#!/usr/bin/env python3
"""
Debug Snapdeal scraper specifically
"""

import os
import re
import logging
from bs4 import BeautifulSoup
from enhanced_scraping_tool import EnhancedSnapdealScraper
from fuzzywuzzy import fuzz

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_snapdeal_scraper():
    print("=" * 60)
    print("DEBUGGING SNAPDEAL SCRAPER")
    print("=" * 60)
    
    # Create scraper
    scraper = EnhancedSnapdealScraper(local_html_path="webpages_samples")
    
    # Read HTML file
    html_file = os.path.join("webpages_samples", "Snapdeal.com - Online shopping India- Discounts - shop Online Perfumes, Watches, sunglasses etc.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Parse results with debug output
    query = "iPhone 16 Pro Max"
    products = scraper._parse_results(html, query)
    
    print(f"\nFinal Results: {len(products)} products found")
    for i, product in enumerate(products, 1):
        print(f"  {i}. {product.product_name}")
        print(f"     Price: {product.currency} {product.price}")
        print(f"     Link: {product.link}")

if __name__ == "__main__":
    debug_snapdeal_scraper()
