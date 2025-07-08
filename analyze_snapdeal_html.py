#!/usr/bin/env python3
"""
Detailed Snapdeal HTML Analysis
"""

import os
import re
from bs4 import BeautifulSoup

def analyze_snapdeal_html():
    html_file = r"c:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\Snapdeal.com - Online shopping India- Discounts - shop Online Perfumes, Watches, sunglasses etc.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find product links
    product_links = soup.find_all('a', href=re.compile(r'/product/'))
    print(f"Found {len(product_links)} product links")
    
    # Analyze first 10 links in detail
    for i, link in enumerate(product_links[:10], 1):
        print(f"\n=== LINK {i} ===")
        href = link.get('href', '')
        print(f"URL: {href}")
        
        # Check link attributes
        print(f"Title attr: '{link.get('title', '')}'")
        print(f"Link text: '{link.get_text(strip=True)}'")
        
        # Check parent structure
        parent = link.find_parent()
        if parent:
            print(f"Parent tag: {parent.name}")
            print(f"Parent class: {parent.get('class', [])}")
            parent_text = parent.get_text(separator=' ', strip=True)
            print(f"Parent text (first 100 chars): '{parent_text[:100]}...'")
            
            # Look for price in parent
            price_match = re.search(r'Rs\.?\s*(\d+(?:,\d+)*)|₹\s*(\d+(?:,\d+)*)', parent_text)
            if price_match:
                print(f"Price found in parent: '{price_match.group(0)}'")
            
            # Check grandparent
            grandparent = parent.find_parent()
            if grandparent:
                gp_text = grandparent.get_text(separator=' ', strip=True)
                price_match = re.search(r'Rs\.?\s*(\d+(?:,\d+)*)|₹\s*(\d+(?:,\d+)*)', gp_text)
                if price_match:
                    print(f"Price found in grandparent: '{price_match.group(0)}'")
                    
                # Show structured text from grandparent
                print(f"Grandparent text structure:")
                all_text_elements = grandparent.find_all(text=True)
                meaningful_texts = [t.strip() for t in all_text_elements if t.strip() and len(t.strip()) > 2]
                for j, text in enumerate(meaningful_texts[:10]):
                    print(f"  {j+1}: '{text}'")

if __name__ == "__main__":
    analyze_snapdeal_html()
