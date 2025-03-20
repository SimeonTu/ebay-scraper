import requests
from bs4 import BeautifulSoup
import re
import argparse

# Constructs an eBay URL with specified search parameters


def construct_ebay_url(keywords, min_price, max_price, condition, page_number):
    base_url = "https://www.ebay.co.uk/sch/i.html"

    # Determine the item condition code based on user input
    if condition and condition.lower() == 'new':
        item_condition_value = '1000'
    elif condition and condition.lower() == 'used':
        item_condition_value = '3000'
    elif condition and condition.lower() == 'refurbished':
        item_condition_value = '2000'
    elif condition and condition.lower() == 'any':
        item_condition_value = None  # No condition filter
    else:
        item_condition_value = None  # Default to any condition if not specified

    # Join multiple keywords with spaces for the search query
    main_keyword = "%20".join(keywords)

    # Construct query parameters for the URL
    params = {
        '_from': 'R40',
        '_nkw': main_keyword,
        '_sacat': '0',
        '_fsrp': '1',
        'LH_Complete': '1',  # Search for completed listings
        'LH_Sold': '1',      # Search for sold items only
        '_pgn': str(page_number),
        'rt': 'nc'
    }

    if item_condition_value:
        params['LH_ItemCondition'] = item_condition_value

    if min_price:
        params['_udlo'] = min_price
    if max_price:
        params['_udhi'] = max_price

    # Convert parameters to a query string
    query_string = '&'.join(
        [f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}"


# Calculates price statistics for products from eBay search results
def calculate_price_stats(search_terms, base_url, num_pages):
    if not isinstance(search_terms, list) or not all(isinstance(term, str) for term in search_terms):
        raise ValueError('search_terms should be a list of strings.')

    search_terms_lower = [term.lower() for term in search_terms]
    matched_products = []

    # Iterate through pages of search results
    for page in range(1, num_pages + 1):
        url = base_url.format(page_number=page)
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        product_elements = soup.select('.s-item')

        # Extract product details from each product element
        for product in product_elements:
            title_element = product.select_one('.s-item__title span')
            price_element = product.select_one('.s-item__price .POSITIVE')

            if title_element and price_element:
                product_name = title_element.text.strip().lower()
                product_price = price_element.text.strip()

                # Check if product matches search terms
                if any(term in product_name for term in search_terms_lower):
                    # Remove currency symbols and commas, then convert to float
                    price_value = float(re.sub(r'[^\d\.]', '', product_price))
                    matched_products.append(
                        (title_element.text.strip(), price_value))

    matched_products.sort(key=lambda x: x[1])
    num_products = len(matched_products)

    if num_products == 0:
        return {'num_products': 0}

    # Calculate mean, median, and identify highest and lowest prices
    mean_price = sum(price for _, price in matched_products) / num_products
    median_index = num_products // 2

    if num_products % 2 == 1:
        median_product = matched_products[median_index]
    else:
        median_price = (
            matched_products[median_index - 1][1] + matched_products[median_index][1]) / 2
        median_product = (matched_products[median_index][0], median_price)

    lowest_price_product = matched_products[0]
    highest_price_product = matched_products[-1]

    return {
        'num_products': num_products,
        'mean_price': mean_price,
        'median_product': median_product,
        'lowest_price_product': lowest_price_product,
        'highest_price_product': highest_price_product,
        'matched_products': matched_products
    }


# Handles user input and search execution
def run_search():
    parser = argparse.ArgumentParser(
        description="Calculate price statistics from eBay search results.")
    parser.add_argument("keywords", nargs='*',
                        help="Main search keywords (one or more)")
    parser.add_argument("--min_price", default='',
                        help="Minimum price (optional)")
    parser.add_argument("--max_price", default='',
                        help="Maximum price (optional)")
    parser.add_argument(
        "--condition", help="Item condition (new, used, refurbished, or any)")
    parser.add_argument("--pages", type=int,
                        help="Number of pages to search (default is 1)")

    args = parser.parse_args()

    # Collect missing arguments from user input
    if not args.keywords:
        keywords_input = input("Enter keywords (separated by spaces): ")
        args.keywords = [kw.strip() for kw in keywords_input.split(' ')]

    args.condition = args.condition or input(
        "Enter the item condition (new, used, refurbished, or any) [any]: ") or 'any'
    args.min_price = args.min_price or input(
        "Enter the minimum price (optional): ")
    args.max_price = args.max_price or input(
        "Enter the maximum price (optional): ")
    args.pages = args.pages or int(
        input("Enter the number of pages to search (default 1): ") or 1)

    # Generate the base eBay URL
    base_url_template = construct_ebay_url(
        args.keywords, args.min_price, args.max_price, args.condition, "{page_number}")

    # Calculate and print the search statistics
    stats = calculate_price_stats(args.keywords, base_url_template, args.pages)
    print(f"\nProducts matched: {stats['num_products']}")

    if stats['num_products'] > 0:
        print(
            f"Lowest price: £{stats['lowest_price_product'][1]:.2f} - {stats['lowest_price_product'][0]}")
        print(
            f"Median price: £{stats['median_product'][1]:.2f} - {stats['median_product'][0]}")
        print(
            f"Highest price: £{stats['highest_price_product'][1]:.2f} - {stats['highest_price_product'][0]}")
        print(f"Mean (average) price: £{stats['mean_price']:.2f}")


# Entry point to start the program
def main():
    while True:
        run_search()
        if input("\nWould you like to start another search? (y/n): ").strip().lower() != 'y':
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
