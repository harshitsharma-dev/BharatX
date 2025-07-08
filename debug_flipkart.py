#!/usr/bin/env python3
"""
Debug script to test Flipkart parsing selectors
"""

import os
from bs4 import BeautifulSoup

def debug_flipkart_parsing():
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\Iphone 16 Pro Max- Buy Products Online at Best Price in India - All Categories _ Flipkart.com.html"
    
    print(f"Reading HTML file: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find product containers
    product_containers = soup.find_all('div', class_='yKfJKb')
    print(f"Found {len(product_containers)} yKfJKb containers")
    
    if not product_containers:
        # Alternative container patterns
        product_containers = soup.find_all('div', class_='_1AtVbE')
        print(f"Found {len(product_containers)} _1AtVbE containers")
    
    for i, container in enumerate(product_containers[:3]):  # Test first 3
        print(f"\n=== CONTAINER {i+1} ===")
        
        # Try different title selectors
        title_elem = container.find('div', class_='KzDlHZ')
        print(f"div.KzDlHZ: {title_elem is not None}")
        if title_elem:
            print(f"Title: {title_elem.get_text(strip=True)[:50]}...")
        
        # Try alternative selectors
        alt_title = container.find('div', class_='_4rR01T')
        print(f"div._4rR01T: {alt_title is not None}")
        
        # Try link in container
        link_elem = container.find('a', href=True)
        print(f"a[href] in container: {link_elem is not None}")
        if link_elem:
            print(f"Link: {link_elem.get('href', '')[:50]}...")
        
        # Check parent containers for links
        parent_link = None
        current = container
        for j in range(3):  # Check up to 3 levels up
            if current.parent:
                current = current.parent
                if current.name == 'a' and current.get('href'):
                    parent_link = current
                    print(f"Found link in parent level {j+1}: {current.get('href')[:50]}...")
                    break
                parent_a = current.find('a', href=True, recursive=False)  # Direct child only
                if parent_a:
                    parent_link = parent_a
                    print(f"Found link in parent level {j+1} child: {parent_a.get('href')[:50]}...")
                    break
        
        if not parent_link and not link_elem:
            print("No link found in container or parents")
        
        # Try price selectors
        price_elem = container.find('div', class_='Nx9bqj')
        print(f"div.Nx9bqj: {price_elem is not None}")
        if price_elem:
            print(f"Price: {price_elem.get_text(strip=True)}")
        
        # Try other price classes
        for price_class in ['_30jeq3', '_25b18c', '_1_WHN1']:
            price_elem = container.find('div', class_=price_class)
            print(f"div.{price_class}: {price_elem is not None}")
            if price_elem:
                print(f"Price ({price_class}): {price_elem.get_text(strip=True)}")
                break

if __name__ == "__main__":
    debug_flipkart_parsing()
