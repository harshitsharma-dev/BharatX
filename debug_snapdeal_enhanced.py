#!/usr/bin/env python3
"""
Enhanced Snapdeal HTML Structure Analyzer
"""

from bs4 import BeautifulSoup
import re

def analyze_snapdeal_structure():
    """Analyze Snapdeal HTML to find the correct product selectors"""
    
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\Snapdeal.com - Online shopping India- Discounts - shop Online Perfumes, Watches, sunglasses etc.html"
    
    print("=== ENHANCED SNAPDEAL STRUCTURE ANALYSIS ===")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Look for actual product containers
    print("\n1. ANALYZING PRODUCT CONTAINERS:")
    containers = soup.find_all('div', class_='product-tuple')
    print(f"Total product-tuple containers: {len(containers)}")
    
    # Analyze first few containers
    real_products = 0
    for i, container in enumerate(containers[:10]):
        print(f"\n--- Container {i+1} ---")
        
        # Look for product title
        title_selectors = [
            'p.product-title',
            '.product-title',
            'p[title]',
            'a[title]',
            '.dp-widget-link p',
            'p.product-desc'
        ]
        
        title_found = None
        for selector in title_selectors:
            title_elem = container.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if title_text and len(title_text) > 5:
                    title_found = title_text
                    print(f"   Title ({selector}): {title_text[:50]}...")
                    break
        
        # Look for price
        price_selectors = [
            'span.product-price',
            '.product-price',
            'span.payBlkBig',
            '.payBlkBig',
            'span[class*="price"]',
            '.price'
        ]
        
        price_found = None
        for selector in price_selectors:
            price_elem = container.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                if price_text and ('Rs' in price_text or '₹' in price_text):
                    price_found = price_text
                    print(f"   Price ({selector}): {price_text}")
                    break
        
        # Look for link
        link_selectors = [
            'a.dp-widget-link',
            '.dp-widget-link',
            'a[href*="/product/"]',
            'a[href*="snapdeal.com"]'
        ]
        
        link_found = None
        for selector in link_selectors:
            link_elem = container.select_one(selector)
            if link_elem and link_elem.get('href'):
                link_found = link_elem['href']
                print(f"   Link ({selector}): {link_found[:60]}...")
                break
        
        if title_found and price_found and link_found:
            real_products += 1
            print(f"   ✅ VALID PRODUCT")
        else:
            print(f"   ❌ INCOMPLETE DATA - Title: {bool(title_found)}, Price: {bool(price_found)}, Link: {bool(link_found)}")
    
    print(f"\nReal products found in first 10: {real_products}")
    
    # Search for all potential product information
    print("\n2. SEARCHING FOR PRODUCT INFORMATION PATTERNS:")
    
    # Find all elements with product-like text
    all_text_elements = soup.find_all(string=re.compile(r'iPhone|Apple|Samsung|Mobile', re.IGNORECASE))
    print(f"Elements with product keywords: {len(all_text_elements)}")
    
    # Find elements with price patterns
    price_elements = soup.find_all(string=re.compile(r'Rs\.?\s*\d+|₹\s*\d+'))
    print(f"Elements with price patterns: {len(price_elements)}")
    
    # Find product links
    product_links = soup.find_all('a', href=re.compile(r'/product/'))
    print(f"Product links found: {len(product_links)}")
    
    # Show sample product links with their container structure
    print("\n3. SAMPLE PRODUCT LINK ANALYSIS:")
    for i, link in enumerate(product_links[:5]):
        print(f"\nLink {i+1}:")
        print(f"   URL: {link.get('href', '')[:60]}...")
        print(f"   Text: {link.get_text(strip=True)[:50]}...")
        
        # Find parent container
        parent = link.find_parent('div', class_='product-tuple')
        if parent:
            print(f"   Parent: product-tuple container found")
            # Look for title in this container
            title_elem = parent.find('p', attrs={'title': True})
            if title_elem:
                print(f"   Container title: {title_elem.get('title', '')[:50]}...")
        else:
            print(f"   Parent: No product-tuple container")

if __name__ == "__main__":
    analyze_snapdeal_structure()
