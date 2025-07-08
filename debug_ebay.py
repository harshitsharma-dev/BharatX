#!/usr/bin/env python3
"""
Debug script to analyze eBay HTML structure and fix selectors
"""

import os
from bs4 import BeautifulSoup
import re

def debug_ebay_parsing():
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\iPhone 16 Pro Max for sale _ eBay.html"
    
    print(f"Reading eBay HTML file: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find different container patterns eBay might use
    container_patterns = [
        ('div.s-item__wrapper', soup.find_all('div', class_='s-item__wrapper')),
        ('div.s-item', soup.find_all('div', class_='s-item')),
        ('div[class*="s-item"]', soup.find_all('div', class_=re.compile(r's-item'))),
        ('div[data-view*="item"]', soup.find_all('div', attrs={'data-view': re.compile(r'item')})),
        ('article', soup.find_all('article')),
        ('div.srp-results', soup.find_all('div', class_='srp-results')),
    ]
    
    print("\n=== CONTAINER ANALYSIS ===")
    for pattern_name, containers in container_patterns:
        print(f"{pattern_name}: {len(containers)} found")
    
    # Use the most promising container pattern
    best_containers = None
    best_pattern = None
    
    for pattern_name, containers in container_patterns:
        if len(containers) > 10:  # Reasonable number for a search results page
            best_containers = containers
            best_pattern = pattern_name
            break
    
    if not best_containers:
        print("No suitable containers found!")
        return
    
    print(f"\nUsing pattern: {best_pattern} ({len(best_containers)} containers)")
    
    # Analyze first 3 containers for structure
    for i, container in enumerate(best_containers[:3]):
        print(f"\n=== CONTAINER {i+1} ANALYSIS ===")
        
        # Look for title/name elements
        title_patterns = [
            ('h3.s-item__title', container.find('h3', class_='s-item__title')),
            ('a.s-item__link', container.find('a', class_='s-item__link')),
            ('h3', container.find('h3')),
            ('a[href*="/itm/"]', container.find('a', href=re.compile(r'/itm/'))),
            ('span.BOLD', container.find('span', class_='BOLD')),
            ('[role="heading"]', container.find(attrs={'role': 'heading'})),
        ]
        
        print("Title/Name Elements:")
        for pattern_name, element in title_patterns:
            if element:
                text = element.get_text(strip=True)[:50]
                print(f"  ✅ {pattern_name}: {text}...")
            else:
                print(f"  ❌ {pattern_name}: Not found")
        
        # Look for price elements
        price_patterns = [
            ('span.s-item__price', container.find('span', class_='s-item__price')),
            ('span.notranslate', container.find('span', class_='notranslate')),
            ('span[data-testid="price"]', container.find('span', attrs={'data-testid': 'price'})),
            ('span.BOLD', container.find('span', class_='BOLD')),
            ('span containing $', container.find('span', string=re.compile(r'\$|\£|€|₹'))),
        ]
        
        print("Price Elements:")
        for pattern_name, element in price_patterns:
            if element:
                text = element.get_text(strip=True)
                print(f"  ✅ {pattern_name}: {text}")
            else:
                print(f"  ❌ {pattern_name}: Not found")
        
        # Look for link elements  
        link_patterns = [
            ('a.s-item__link', container.find('a', class_='s-item__link')),
            ('a[href*="/itm/"]', container.find('a', href=re.compile(r'/itm/'))),
            ('a', container.find('a', href=True)),
        ]
        
        print("Link Elements:")
        for pattern_name, element in link_patterns:
            if element:
                href = element.get('href', '')[:50]
                print(f"  ✅ {pattern_name}: {href}...")
            else:
                print(f"  ❌ {pattern_name}: Not found")
        
        print("-" * 50)
    
    # Look for any text that looks like iPhone prices or names
    print("\n=== SEARCHING FOR iPHONE RELATED CONTENT ===")
    iphone_texts = soup.find_all(string=re.compile(r'iPhone|IPHONE', re.I))
    price_texts = soup.find_all(string=re.compile(r'\$\d+|\$\s*\d+|\d+\.\d+'))
    
    print(f"iPhone-related text found: {len(iphone_texts)}")
    for i, text in enumerate(iphone_texts[:5]):
        print(f"  {i+1}. {text.strip()[:50]}...")
    
    print(f"Price-like text found: {len(price_texts)}")
    for i, text in enumerate(price_texts[:5]):
        print(f"  {i+1}. {text.strip()}")

if __name__ == "__main__":
    debug_ebay_parsing()
