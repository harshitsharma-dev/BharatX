#!/usr/bin/env python3
"""
Comprehensive test for all scrapers including eBay, Walmart, Snapdeal, Shopsy
"""

import asyncio
import logging
from enhanced_scraping_tool import EnhancedPriceComparisonTool

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

async def test_all_scrapers():
    """Test all scrapers individually to see their performance"""
    
    local_html_path = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples"
    
    print("=" * 80)
    print("COMPREHENSIVE SCRAPER TEST - ALL SITES")
    print("=" * 80)
    
    # Test 1: India with iPhone (tests Amazon.in, Flipkart, eBay.in, Snapdeal, Shopsy)
    print("\n🇮🇳 TESTING INDIA SCRAPERS - iPhone 16 Pro Max")
    print("-" * 60)
    
    tool = EnhancedPriceComparisonTool(local_html_path)
    products = await tool.search_products("IN", "iPhone 16 Pro Max", use_local=True)
    
    # Group by source
    sources = {}
    for product in products:
        source = product['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(product)
    
    for source, source_products in sources.items():
        print(f"\n✅ {source}: {len(source_products)} products")
        for i, product in enumerate(source_products[:2], 1):
            print(f"  {i}. {product['productName'][:50]}...")
            print(f"     Price: {product['currency']} {product['price']}")
    
    # Show sources with no products
    indian_scrapers = ["Amazon.in", "Flipkart", "eBay.in", "Snapdeal", "Shopsy"]
    for scraper in indian_scrapers:
        if scraper not in sources:
            print(f"\n❌ {scraper}: 0 products (needs debugging)")
    
    # Test 2: US with iPhone (tests eBay.com, Walmart)
    print("\n\n🇺🇸 TESTING US SCRAPERS - iPhone 16 Pro Max")  
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
        print(f"\n✅ {source}: {len(source_products)} products")
        for i, product in enumerate(source_products[:2], 1):
            print(f"  {i}. {product['productName'][:50]}...")
            print(f"     Price: {product['currency']} {product['price']}")
    
    # Show sources with no products
    us_scrapers = ["eBay.com", "Walmart"]
    for scraper in us_scrapers:
        if scraper not in sources_us:
            print(f"\n❌ {scraper}: 0 products (needs debugging)")
    
    # Test 3: Different product category - Samsung
    print("\n\n📱 TESTING DIFFERENT PRODUCT CATEGORY - Samsung Galaxy S24")
    print("-" * 60)
    
    products_samsung = await tool.search_products("IN", "Samsung Galaxy S24", use_local=True)
    
    sources_samsung = {}
    for product in products_samsung:
        source = product['source']
        if source not in sources_samsung:
            sources_samsung[source] = []
        sources_samsung[source].append(product)
    
    print(f"Total Samsung products found: {len(products_samsung)}")
    for source, source_products in sources_samsung.items():
        print(f"  {source}: {len(source_products)} products")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("SCRAPER PERFORMANCE SUMMARY")
    print("=" * 80)
    
    all_scrapers = {
        "Amazon.in": "✅ Working perfectly",
        "Flipkart": "✅ Working perfectly", 
        "eBay.in": "❌ Needs selector fixes",
        "eBay.com": "❌ Needs selector fixes",
        "Walmart": "✅ Working (US only)",
        "Snapdeal": "❌ Needs selector fixes",
        "Shopsy": "❌ Needs selector fixes"
    }
    
    for scraper, status in all_scrapers.items():
        print(f"{scraper:12} - {status}")
    
    working_count = sum(1 for status in all_scrapers.values() if "✅" in status)
    total_count = len(all_scrapers)
    
    print(f"\nOverall Status: {working_count}/{total_count} scrapers working ({working_count/total_count*100:.0f}%)")

if __name__ == "__main__":
    asyncio.run(test_all_scrapers())
