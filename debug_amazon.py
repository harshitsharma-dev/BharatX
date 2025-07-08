#!/usr/bin/env python3
"""
Debug script to test Amazon parsing selectors
"""

import os
from bs4 import BeautifulSoup

def debug_amazon_parsing():
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\Amazon.in _ iphone 16pro max.html"
    
    print(f"Reading HTML file: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find product containers
    product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
    print(f"Found {len(product_containers)} product containers")
    
    for i, container in enumerate(product_containers[:3]):  # Test first 3
        print(f"\n=== CONTAINER {i+1} ===")
        
        # Try different title selectors
        title_elem = container.find('h2', class_='a-size-medium')
        print(f"h2.a-size-medium: {title_elem is not None}")
        
        if not title_elem:
            title_elem = container.find('h2')
            print(f"h2: {title_elem is not None}")
        
        if title_elem:
            title_link = title_elem.find('a')
            print(f"h2 -> a: {title_link is not None}")
            if title_link:
                print(f"Title: {title_link.get_text(strip=True)[:50]}...")
                print(f"Link: {title_link.get('href', '')[:50]}...")
        
        # Try alternative selector
        alt_title = container.find('a', class_='s-line-clamp-2')
        print(f"a.s-line-clamp-2: {alt_title is not None}")
        
        if not alt_title:
            # Try partial class matching
            alt_title = container.find('a', class_=lambda x: x and 's-line-clamp-2' in x)
            print(f"a[class*='s-line-clamp-2']: {alt_title is not None}")
            
        if alt_title:
            print(f"Alt Title: {alt_title.get_text(strip=True)[:50]}...")
        
        # Try price selectors
        price_elem = container.find('span', class_='a-offscreen')
        print(f"span.a-offscreen: {price_elem is not None}")
        
        if price_elem:
            print(f"Price: {price_elem.get_text(strip=True)}")
        else:
            # Try alternative
            price_elem = container.find('span', class_='a-price-whole')
            print(f"span.a-price-whole: {price_elem is not None}")
            if price_elem:
                print(f"Price (whole): {price_elem.get_text(strip=True)}")

if __name__ == "__main__":
    debug_amazon_parsing()
