# eBay Scraper

This Python program scrapes eBay listings based on user-provided search criteria and calculates price statistics such as the mean, median, lowest, and highest prices of matching items. 

## Features
**Customisable Search** - Search eBay listings using keywords, price range, item condition (new, used, refurbished, or any), and number of pages to scrape.

**Price Statistics** - Calculates and displays:
- Total number of matched products
- Lowest-priced product
- Median-priced product
- Highest-priced product
- Mean price

**Command-Line and Interactive Modes** - Provide input via command-line arguments or interactively through prompts.

## Requirements
- Python 3.6 or higher
- Libraries: requests, beautifulsoup4

Install the required libraries using pip:
```
pip install -r requirements.txt
```

## Usage
**Command-Line Mode**

Run the program with the following arguments: 
```
python ebay_scraper.py [keywords] --min_price [value] --max_price [value] --condition [condition] --pages [number]
```
* keywords: Search terms (e.g., "laptop", "headphones").
* --min_price: Minimum price (optional).
* --max_price: Maximum price (optional).
* --condition: Item condition (new, used, refurbished, or any).
* --pages: Number of pages to scrape (default: 1).

**Interactive Mode**

Run the program without arguments to input parameters interactively:
```
python ebayScraper.py
```
