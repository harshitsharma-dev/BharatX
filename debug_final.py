#!/usr/bin/env python3
"""
Final eBay and Snapdeal Debugging
"""

from bs4 import BeautifulSoup
import re

def debug_ebay_final():
    """Final debug of eBay structure"""
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\iPhone 16 Pro Max for sale _ eBay.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    print("=== FINAL eBay DEBUG ===")
    
    # Look for containers
    containers = soup.find_all('div', class_='s-item__wrapper')
    print(f"s-item__wrapper containers: {len(containers)}")
    
    for i, container in enumerate(containers[:5]):
        print(f"\n--- Container {i+1} ---")
        
        # Check for eBay item links
        item_links = container.find_all('a', href=re.compile(r'/itm/\d+'))
        print(f"Item links: {len(item_links)}")
        
        if item_links:
            link = item_links[0]
            print(f"Link href: {link.get('href', '')[:60]}...")
            
            # Look for title in span with role="heading"
            title_span = link.find('span', attrs={'role': 'heading'})
            if title_span:
                title_text = title_span.get_text(strip=True)
                print(f"Title (span role=heading): {title_text[:60]}...")
                
                # Check if it's promotional
                skip_patterns = [
                    "Shop on eBay", "Hot This Week", "Trending", 
                    "Sponsored", "Opens in a new window", "Opens in a new tab"
                ]
                
                is_promotional = any(pattern.lower() in title_text.lower() for pattern in skip_patterns)
                print(f"Is promotional: {is_promotional}")
                
                if not is_promotional and len(title_text) >= 10:
                    print("✅ VALID PRODUCT FOUND")
                else:
                    print("❌ Promotional or too short")
            else:
                print("No span with role=heading found")
                # Check link text
                link_text = link.get_text(strip=True)
                print(f"Link text: {link_text[:60]}...")
        
        # Check for price
        price_elem = container.find('span', class_='s-item__price')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            print(f"Price: {price_text}")

def debug_snapdeal_final():
    """Final debug of Snapdeal structure"""
    html_file = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples\Snapdeal.com - Online shopping India- Discounts - shop Online Perfumes, Watches, sunglasses etc.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    print("\n=== FINAL SNAPDEAL DEBUG ===")
    
    # Look for product links
    product_links = soup.find_all('a', href=re.compile(r'/product/'))
    print(f"Product links found: {len(product_links)}")
    
    for i, link in enumerate(product_links[:5]):
        print(f"\n--- Link {i+1} ---")
        href = link.get('href', '')
        print(f"URL: {href[:60]}...")
        
        # Check for title
        title = link.get('title', '') or link.get_text(strip=True)
        print(f"Title: {title[:60]}...")
        
        if title and len(title) > 5:
            # Look for price near this link
            parent = link.find_parent()
            price_found = False
            
            # Search parent elements for price
            current = link
            for level in range(5):
                if current.parent:
                    parent = current.parent
                    price_texts = parent.find_all(text=re.compile(r'Rs\.?\s*\d+|₹\s*\d+'))
                    if price_texts:
                        print(f"Price found at level {level}: {price_texts[0].strip()}")
                        price_found = True
                        break
                    current = parent
                else:
                    break
            
            if not price_found:
                print("No price found")
            else:
                print("✅ COMPLETE PRODUCT DATA")

if __name__ == "__main__":
    debug_ebay_final()
    debug_snapdeal_final()
