import requests
from bs4 import BeautifulSoup
import re
import argparse

def construct_ebay_url(keywords, min_price, max_price, condition, page_number):
    base_url = "https://www.ebay.co.uk/sch/i.html"

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

    # Join multiple keywords with spaces
    main_keyword = "%20".join(keywords)

    params = {
        '_from': 'R40',
        '_nkw': main_keyword,
        '_sacat': '0',
        '_fsrp': '1',
        'LH_Complete': '1',
        'LH_Sold': '1',
        '_pgn': str(page_number),
        'rt': 'nc'
    }

    if item_condition_value:
        params['LH_ItemCondition'] = item_condition_value

    if min_price:
        params['_udlo'] = min_price
    if max_price:
        params['_udhi'] = max_price

    query_string = '&'.join(
        [f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}"


def calculate_price_stats(search_terms, base_url, num_pages):
    if not isinstance(search_terms, list) or not all(isinstance(term, str) for term in search_terms):
        raise ValueError('search_terms should be a list of strings.')

    search_terms_lower = [term.lower() for term in search_terms]

    matched_products = []

    for page in range(1, num_pages + 1):
        url = base_url.format(page_number=page)
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        product_elements = soup.select('.s-item')

        for product in product_elements:
            title_element = product.select_one('.s-item__title span')
            price_element = product.select_one('.s-item__price .POSITIVE')

            if title_element and price_element:
                product_name = title_element.text.strip().lower()
                product_price = price_element.text.strip()

                if any(term in product_name for term in search_terms_lower):
                    # Remove any currency symbols and commas
                    price_value = float(re.sub(r'[^\d\.]', '', product_price))
                    matched_products.append(
                        (title_element.text.strip(), price_value))

    matched_products.sort(key=lambda x: x[1])

    num_products = len(matched_products)
    if num_products == 0:
        return {'num_products': 0}

    mean_price = sum(price for _, price in matched_products) / num_products
    median_index = num_products // 2
    if num_products % 2 == 1:
        median_product = matched_products[median_index]
    else:
        median_price = (matched_products[median_index - 1][1] + matched_products[median_index][1]) / 2
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


def run_search():
    parser = argparse.ArgumentParser(
        description="Calculate price statistics from eBay search results.")
    parser.add_argument("keywords", nargs='*',
                        help="Main search keywords (one or more)")
    parser.add_argument("--min_price", default='',
                        help="Minimum price (optional)")
    parser.add_argument("--max_price", default='',
                        help="Maximum price (optional)")
    parser.add_argument("--condition",
                        help="Item condition (new, used, refurbished, or any)")
    parser.add_argument("--pages", type=int,
                        help="Number of pages to search (default is 1)")

    args = parser.parse_args()

    # Check if the script is being run with arguments
    if args.keywords:
        search_terms = args.keywords
    else:
        # Interactive mode if required arguments are missing
        keywords_input = input("Enter keywords (separated by spaces): ")
        search_terms = [kw.strip() for kw in keywords_input.split(' ')]

    if args.condition is None:
        args.condition = input(
            "Enter the item condition (new, used, refurbished, or any) [any]: ") or 'any'

    if not args.min_price:
        args.min_price = input("Enter the minimum price (optional): ")

    if not args.max_price:
        args.max_price = input("Enter the maximum price (optional): ")

    if args.pages is None:
        args.pages = input("Enter the number of pages to search (default 1): ")
        args.pages = int(args.pages) if args.pages else 1

    # Construct the base URL without the page number
    base_url_template = construct_ebay_url(
        search_terms, args.min_price, args.max_price, args.condition, "{page_number}")

    # Display the provided arguments
    print("\nSearch Parameters:")
    print("=================")
    print(f"Keywords: {', '.join(search_terms)}")
    print(f"Condition: {args.condition.capitalize()}")
    if args.min_price:
        print(f"Minimum Price: £{args.min_price}")
    if args.max_price:
        print(f"Maximum Price: £{args.max_price}")
    print(f"Number of Pages: {args.pages}")

    # Calculate and display the statistics
    stats = calculate_price_stats(search_terms, base_url_template, args.pages)

    print(f"\nProducts matched: {stats['num_products']}")
    print("=================")
    if stats['num_products'] > 0:
        print(
            f"Lowest price: £{stats['lowest_price_product'][1]:.2f} - {stats['lowest_price_product'][0]}")
        print(
            f"Median price: £{stats['median_product'][1]:.2f} - {stats['median_product'][0]}")
        print(
            f"Highest price: £{stats['highest_price_product'][1]:.2f} - {stats['highest_price_product'][0]}")
        print(f"Mean (average) price: £{stats['mean_price']:.2f}")
        print("\nBase URL (for first page): ", base_url_template.format(page_number=1))
    else:
        print("No matching product found.")
        print("\nBase URL (for first page): ", base_url_template.format(page_number=1))


def main():
    while True:
        run_search()
        user_input = input(
            "\nWould you like to start another search? (y/n): ").strip().lower()
        if user_input != 'y':
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
