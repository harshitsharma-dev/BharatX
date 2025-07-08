#!/usr/bin/env python3
"""
Debug API integration - Test exactly what the API does
"""

import asyncio
import os
import sys
from enhanced_scraping_tool import EnhancedPriceComparisonTool

async def test_api_method():
    """Test exactly what the API does to find the issue"""
    
    local_html_path = os.path.join(os.path.dirname(__file__), "webpages_samples")
    print(f"Local HTML path: {local_html_path}")
    print(f"Path exists: {os.path.exists(local_html_path)}")
    
    # Create tool exactly like the API does
    if os.path.exists(local_html_path):
        price_tool = EnhancedPriceComparisonTool(local_html_path)
        print("Price tool initialized with local HTML samples")
    else:
        price_tool = EnhancedPriceComparisonTool()
        print("Price tool initialized for online scraping")
    
    # Test India (should get Amazon.in, Flipkart, eBay.in, Snapdeal, Shopsy)
    print("\n" + "="*60)
    print("TESTING INDIA - iPhone 16 Pro Max")
    print("="*60)
    
    products = await price_tool.search_products("IN", "iPhone 16 Pro Max", use_local=True)
    
    print(f"Total products returned: {len(products)}")
    
    # Group by source
    sources = {}
    for product in products:
        source = product['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(product)
    
    print(f"\nSources found: {list(sources.keys())}")
    
    for source, source_products in sources.items():
        print(f"\n{source}: {len(source_products)} products")
        for i, product in enumerate(source_products[:2], 1):
            print(f"  {i}. {product['productName'][:50]}...")
            print(f"     Price: {product['currency']} {product['price']}")
    
    # Test US (should get eBay.com, Walmart)
    print("\n" + "="*60)
    print("TESTING US - iPhone 16 Pro Max")
    print("="*60)
    
    products_us = await price_tool.search_products("US", "iPhone 16 Pro Max", use_local=True)
    
    print(f"Total products returned: {len(products_us)}")
    
    # Group by source
    sources_us = {}
    for product in products_us:
        source = product['source']
        if source not in sources_us:
            sources_us[source] = []
        sources_us[source].append(product)
    
    print(f"\nSources found: {list(sources_us.keys())}")
    
    for source, source_products in sources_us.items():
        print(f"\n{source}: {len(source_products)} products")
        for i, product in enumerate(source_products[:2], 1):
            print(f"  {i}. {product['productName'][:50]}...")
            print(f"     Price: {product['currency']} {product['price']}")

if __name__ == "__main__":
    asyncio.run(test_api_method())
