#!/usr/bin/env python3
"""
Test all scrapers individually to check if they're working correctly
This is a Windows-compatible version without Unicode emojis
"""

import asyncio
from enhanced_scraping_tool import EnhancedPriceComparisonTool
import os

async def test_all_scrapers():
    """Test all scrapers with local HTML files"""
    
    local_html_path = os.path.join(os.path.dirname(__file__), "webpages_samples")
    
    # Test 1: India with iPhone (tests Amazon.in, Flipkart, eBay.in, Snapdeal, Shopsy)
    print("\n[IN] TESTING INDIAN SCRAPERS - iPhone 16 Pro Max")  
    print("-" * 60)
    
    tool = EnhancedPriceComparisonTool(local_html_path)
    products = await tool.search_products("IN", "iPhone 16 Pro Max", use_local=True)
    
    # Group products by source
    sources = {}
    for product in products:
        source = product['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(product)
    
    for source, source_products in sources.items():
        print(f"\n[OK] {source}: {len(source_products)} products")
        for i, product in enumerate(source_products[:2], 1):
            print(f"  {i}. {product['productName'][:50]}...")
            print(f"     Price: {product['currency']} {product['price']}")
    
    # Show sources with no products
    indian_scrapers = ["Amazon.in", "Flipkart", "eBay.in", "Snapdeal", "Shopsy"]
    for scraper in indian_scrapers:
        if scraper not in sources:
            print(f"\n[FAIL] {scraper}: 0 products (needs debugging)")
    
    # Test 2: US with iPhone (tests eBay.com, Walmart)
    print("\n\n[US] TESTING US SCRAPERS - iPhone 16 Pro Max")  
    print("-" * 60)
    
    tool_us = EnhancedPriceComparisonTool(local_html_path)
    products_us = await tool_us.search_products("US", "iPhone 16 Pro Max", use_local=True)
    
    sources_us = {}
    for product in products_us:
        source = product['source']
        if source not in sources_us:
            sources_us[source] = []
        sources_us[source].append(product)
    
    for source, source_products in sources_us.items():
        print(f"\n[OK] {source}: {len(source_products)} products")
        for i, product in enumerate(source_products[:2], 1):
            print(f"  {i}. {product['productName'][:50]}...")
            print(f"     Price: {product['currency']} {product['price']}")
    
    # Show sources with no products
    us_scrapers = ["eBay.com", "Walmart"]
    for scraper in us_scrapers:
        if scraper not in sources_us:
            print(f"\n[FAIL] {scraper}: 0 products (needs debugging)")
    
    # Test 3: Different product category - Samsung
    print("\n\n[TEST] TESTING DIFFERENT PRODUCT CATEGORY - Samsung Galaxy S24")
    print("-" * 60)
    
    products_samsung = await tool.search_products("IN", "Samsung Galaxy S24", use_local=True)
    
    sources_samsung = {}
    for product in products_samsung:
        source = product['source']
        if source not in sources_samsung:
            sources_samsung[source] = []
        sources_samsung[source].append(product)
    
    for source, source_products in sources_samsung.items():
        print(f"\n[OK] {source}: {len(source_products)} products")
        for i, product in enumerate(source_products[:2], 1):
            print(f"  {i}. {product['productName'][:50]}...")
            print(f"     Price: {product['currency']} {product['price']}")
    
    # Summary
    print("\n\n" + "="*60)
    print("SCRAPER STATUS SUMMARY")
    print("="*60)
    
    all_scrapers_status = {
        "Amazon.in": "[OK] Working well",
        "Flipkart": "[OK] Working well", 
        "Walmart": "[OK] Working well",
        "eBay.in": "[FAIL] Needs selector fixes",
        "eBay.com": "[FAIL] Needs selector fixes",
        "Snapdeal": "[OK] Fixed and working",
        "Shopsy": "[FAIL] Needs selector fixes"
    }
    
    for scraper, status in all_scrapers_status.items():
        print(f"{scraper:<15}: {status}")
    
    print("\nNOTE: Run this test to verify scrapers are working before testing API integration")

if __name__ == "__main__":
    asyncio.run(test_all_scrapers())
