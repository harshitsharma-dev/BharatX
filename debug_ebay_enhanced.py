#!/usr/bin/env python3
"""
Enhanced eBay HTML Structure Analyzer
"""

from bs4 import BeautifulSoup
import re

def analyze_ebay_structure():
    """Analyze eBay HTML to find the correct product selectors"""
    
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\iPhone 16 Pro Max for sale _ eBay.html"
    
    print("=== ENHANCED EBAY STRUCTURE ANALYSIS ===")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Look for actual product containers - not promotional ones
    print("\n1. IDENTIFYING REAL PRODUCT CONTAINERS:")
    containers = soup.find_all('div', class_='s-item__wrapper')
    print(f"Total s-item__wrapper containers: {len(containers)}")
    
    real_product_count = 0
    for i, container in enumerate(containers[:10]):  # Check first 10
        # Look for links with actual eBay item URLs
        item_links = container.find_all('a', href=re.compile(r'/itm/\d+'))
        
        if item_links:
            # Check if this is a real product (not promotional)
            title_text = ""
            for link in item_links:
                text = link.get_text(strip=True)
                if text and 'Shop on eBay' not in text and len(text) > 10:
                    title_text = text
                    break
            
            if title_text:
                real_product_count += 1
                print(f"\n✅ Container {i+1}: REAL PRODUCT")
                print(f"   Title: {title_text[:60]}...")
                
                # Check price
                price_elem = container.find('span', class_='s-item__price')
                if price_elem:
                    print(f"   Price: {price_elem.get_text(strip=True)}")
                
                # Check link
                print(f"   Link: {item_links[0]['href'][:60]}...")
            else:
                print(f"\n❌ Container {i+1}: PROMOTIONAL")
        else:
            print(f"\n❌ Container {i+1}: NO ITEM LINKS")
    
    print(f"\nReal products found in first 10: {real_product_count}")
    
    # Look for better selectors
    print("\n2. ANALYZING PRODUCT TITLE SELECTORS:")
    potential_titles = []
    
    # Try different title selectors
    selectors_to_try = [
        'h3.s-item__title a',
        'a.s-item__link span[role="heading"]',
        '.s-item__title-link',
        'a[href*="/itm/"] span[role="heading"]',
        '.s-item__link .s-item__title',
        'span[role="heading"]'
    ]
    
    for selector in selectors_to_try:
        elements = soup.select(selector)
        if elements:
            # Filter out promotional content
            valid_titles = []
            for elem in elements[:5]:
                text = elem.get_text(strip=True)
                if (text and 'Shop on eBay' not in text and 
                    'Opens in a new window' not in text and 
                    len(text) > 10):
                    valid_titles.append(text[:40] + "...")
            
            if valid_titles:
                print(f"   {selector}: {len(valid_titles)} valid titles")
                for title in valid_titles[:3]:
                    print(f"      - {title}")
                potential_titles.extend(valid_titles)
    
    print(f"\nTotal potential product titles found: {len(potential_titles)}")
    
    # Analyze price structure
    print("\n3. ANALYZING PRICE STRUCTURE:")
    price_containers = soup.find_all('span', class_='s-item__price')
    print(f"Price containers found: {len(price_containers)}")
    
    valid_prices = []
    for price in price_containers[:10]:
        price_text = price.get_text(strip=True)
        if re.search(r'\$\d+', price_text):
            valid_prices.append(price_text)
    
    print(f"Valid prices found: {len(valid_prices)}")
    for price in valid_prices[:5]:
        print(f"   - {price}")

if __name__ == "__main__":
    analyze_ebay_structure()
