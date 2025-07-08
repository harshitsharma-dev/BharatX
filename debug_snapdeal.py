#!/usr/bin/env python3
"""
Debug script to analyze Snapdeal HTML structure and fix selectors
"""

import os
from bs4 import BeautifulSoup
import re

def debug_snapdeal_parsing():
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\Snapdeal.com - Online shopping India- Discounts - shop Online Perfumes, Watches, sunglasses etc.html"
    
    print(f"Reading Snapdeal HTML file: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find different container patterns Snapdeal might use
    container_patterns = [
        ('div.product-tuple', soup.find_all('div', class_=re.compile(r'product-tuple'))),
        ('div.favDp', soup.find_all('div', class_='favDp')),
        ('div.product-item', soup.find_all('div', class_=re.compile(r'product-item'))),
        ('div[data-js="product-card"]', soup.find_all('div', attrs={'data-js': 'product-card'})),
        ('div.product-desc-rating', soup.find_all('div', class_='product-desc-rating')),
        ('div[class*="product"]', soup.find_all('div', class_=re.compile(r'product'))),
        ('div.dp-widget-link', soup.find_all('div', class_='dp-widget-link')),
    ]
    
    print("\n=== CONTAINER ANALYSIS ===")
    for pattern_name, containers in container_patterns:
        print(f"{pattern_name}: {len(containers)} found")
    
    # Look for actual product information
    print("\n=== SEARCHING FOR PRODUCT CONTENT ===")
    
    # Search for iPhone-related content
    iphone_elements = soup.find_all(string=re.compile(r'iPhone|Apple|APPLE', re.I))
    print(f"iPhone/Apple related text: {len(iphone_elements)}")
    for i, text in enumerate(iphone_elements[:10]):
        clean_text = text.strip()
        if len(clean_text) > 5:
            print(f"  {i+1}. {clean_text[:60]}...")
    
    # Search for price patterns
    price_elements = soup.find_all(string=re.compile(r'₹\s*\d+|Rs\s*\d+|\d+\s*Rs'))
    print(f"\nPrice patterns found: {len(price_elements)}")
    for i, text in enumerate(price_elements[:10]):
        print(f"  {i+1}. {text.strip()}")
    
    # Look for potential product containers with actual content
    print("\n=== ANALYZING POTENTIAL PRODUCT CONTAINERS ===")
    
    # Try different approaches to find product containers
    approaches = [
        ("Links with product info", soup.find_all('a', href=re.compile(r'/product/'))),
        ("Divs with images", soup.find_all('div', class_=re.compile(r'picture|image|img'))),
        ("Elements with prices", soup.find_all(attrs={'data-price': True})),
        ("Product links", soup.find_all('a', title=re.compile(r'iPhone|Apple', re.I))),
    ]
    
    for approach_name, elements in approaches:
        print(f"\n{approach_name}: {len(elements)} found")
        for i, element in enumerate(elements[:3]):
            if hasattr(element, 'get_text'):
                text = element.get_text(strip=True)[:50]
                print(f"  {i+1}. {text}...")
            if hasattr(element, 'get'):
                href = element.get('href', '')
                title = element.get('title', '')
                if href:
                    print(f"     Link: {href[:50]}...")
                if title:
                    print(f"     Title: {title[:50]}...")

if __name__ == "__main__":
    debug_snapdeal_parsing()
