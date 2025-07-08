#!/usr/bin/env python3
"""    for i, container in enumerate(product_containers[:10], 1):
        print(f"\n--- Container {i} ---")
        
        # Check for sponsored content - use the new logic
        sponsored_elem = container.find('span', string=re.compile(r'SPONSORED', re.I))
        if sponsored_elem:
            # Only skip if it's a clear sponsored label, not just containing the word
            sponsored_text = sponsored_elem.get_text(strip=True).upper()
            print(f"Found sponsored element: '{sponsored_text}'")
            if sponsored_text == 'SPONSORED' or 'SPONSORED LISTING' in sponsored_text:
                print("❌ SPONSORED - SKIPPED")
                continue
            else:
                print("✅ Contains 'sponsored' but not exact match - CONTINUING")
        else:
            print("✅ NO SPONSORED CONTENT")ific issues with eBay and Snapdeal scrapers
"""

import os
import re
from bs4 import BeautifulSoup

def debug_ebay():
    print("=" * 60)
    print("DEBUGGING EBAY STEP BY STEP")
    print("=" * 60)
    
    html_file = r"c:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\iPhone 16 Pro Max for sale _ eBay.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find product containers
    product_containers = soup.find_all('div', class_='s-item__wrapper')
    if not product_containers:
        product_containers = soup.find_all('div', class_='s-item')
    
    print(f"Found {len(product_containers)} containers")
    
    for i, container in enumerate(product_containers[:5], 1):
        print(f"\n--- Container {i} ---")
        
        # Check for sponsored content - use the new logic
        sponsored_elem = container.find('span', string=re.compile(r'SPONSORED', re.I))
        if sponsored_elem:
            # Only skip if it's a clear sponsored label, not just containing the word
            sponsored_text = sponsored_elem.get_text(strip=True).upper()
            if sponsored_text == 'SPONSORED' or 'SPONSORED LISTING' in sponsored_text:
                print("❌ SPONSORED - SKIPPED")
                continue
        
        # Find item link
        item_link = container.find('a', href=re.compile(r'/itm/\d+'))
        if not item_link:
            print("❌ NO ITEM LINK")
            continue
        else:
            href = item_link.get('href', '')
            print(f"✅ ITEM LINK: {href[:60]}...")
        
        # Test all title extraction strategies
        title_strategies = [
            ("span[role='heading'] inside link", lambda: item_link.find('span', attrs={'role': 'heading'})),
            (".s-item__title in container", lambda: container.find(class_='s-item__title')),
            ("span[role='heading'] in container", lambda: container.find('span', attrs={'role': 'heading'})),
            ("link title attribute", lambda: item_link.get('title')),
            ("link text", lambda: item_link.get_text(strip=True))
        ]
        
        product_name = ""
        for strategy_name, strategy_func in title_strategies:
            try:
                result = strategy_func()
                if result:
                    if hasattr(result, 'get_text'):
                        text = result.get_text(strip=True)
                    else:
                        text = str(result).strip()
                    
                    if len(text) > 10:
                        print(f"✅ {strategy_name}: {text[:50]}...")
                        if not product_name:
                            product_name = text
                    else:
                        print(f"❌ {strategy_name}: Too short - '{text}'")
                else:
                    print(f"❌ {strategy_name}: Not found")
            except Exception as e:
                print(f"❌ {strategy_name}: Error - {e}")
        
        # Test price extraction
        price_elem = container.find('span', class_='s-item__price')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            print(f"✅ PRICE: {price_text}")
        else:
            print("❌ NO PRICE")
        
        print(f"Final product name: {product_name[:50]}..." if product_name else "❌ NO VALID TITLE")

def debug_snapdeal():
    print("\n" + "=" * 60)
    print("DEBUGGING SNAPDEAL STEP BY STEP")
    print("=" * 60)
    
    html_file = r"c:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\Snapdeal.com - Online shopping India- Discounts - shop Online Perfumes, Watches, sunglasses etc.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find product links
    product_links = soup.find_all('a', href=re.compile(r'/product/'))
    print(f"Found {len(product_links)} product links")
    
    for i, link in enumerate(product_links[:5], 1):
        print(f"\n--- Link {i} ---")
        
        href = link.get('href', '')
        print(f"URL: {href[:60]}...")
        
        # Test title extraction strategies
        title_strategies = [
            ("title attribute", lambda: link.get('title', '')),
            ("link text", lambda: link.get_text(strip=True)),
            ("parent title class", lambda: link.find_parent() and link.find_parent().find(class_=re.compile(r'product.*title|title.*product', re.I))),
            ("parent all text", lambda: link.find_parent() and ' '.join(link.find_parent().get_text(separator=' ', strip=True).split()[:10]))
        ]
        
        product_name = ""
        for strategy_name, strategy_func in title_strategies:
            try:
                result = strategy_func()
                if result:
                    if hasattr(result, 'get_text'):
                        text = result.get_text(strip=True)
                    else:
                        text = str(result).strip()
                    
                    if len(text) > 5:
                        print(f"✅ {strategy_name}: {text[:50]}...")
                        if not product_name:
                            product_name = text
                    else:
                        print(f"❌ {strategy_name}: Too short - '{text}'")
                else:
                    print(f"❌ {strategy_name}: Not found")
            except Exception as e:
                print(f"❌ {strategy_name}: Error - {e}")
        
        # Test price extraction strategies
        price_strategies = [
            ("link text price", lambda: re.search(r'Rs\.?\s*(\d+(?:,\d+)*)|₹\s*(\d+(?:,\d+)*)', link.get_text())),
            ("parent text price", lambda: link.find_parent() and re.search(r'Rs\.?\s*(\d+(?:,\d+)*)|₹\s*(\d+(?:,\d+)*)', link.find_parent().get_text())),
            ("price class", lambda: link.find_parent() and link.find_parent().find(['span', 'div'], class_=re.compile(r'price|cost|amount|rs|rupees', re.I)))
        ]
        
        price_text = ""
        for strategy_name, strategy_func in price_strategies:
            try:
                result = strategy_func()
                if result:
                    if hasattr(result, 'group'):  # regex match
                        text = result.group(0)
                    elif hasattr(result, 'get_text'):
                        text = result.get_text(strip=True)
                    else:
                        text = str(result).strip()
                    
                    if 'Rs' in text or '₹' in text:
                        print(f"✅ {strategy_name}: {text}")
                        if not price_text:
                            price_text = text
                    else:
                        print(f"❌ {strategy_name}: No price pattern - '{text[:20]}...'")
                else:
                    print(f"❌ {strategy_name}: Not found")
            except Exception as e:
                print(f"❌ {strategy_name}: Error - {e}")
        
        print(f"Final: Name='{product_name[:30]}...', Price='{price_text}'" if product_name or price_text else "❌ NO COMPLETE DATA")

if __name__ == "__main__":
    debug_ebay()
    debug_snapdeal()
