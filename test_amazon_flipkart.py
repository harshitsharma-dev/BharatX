#!/usr/bin/env python3
"""
Test script specifically for Amazon and Flipkart scrapers
"""

import logging
import asyncio
from enhanced_scraping_tool import EnhancedPriceComparisonTool

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

async def test_amazon_flipkart():
    """Test Amazon and Flipkart scrapers specifically"""
    
    local_html_path = r"C:\Users\harsh\OneDrive\Documents\BharatX\webpages_samples"
    
    print("=" * 80)
    print("Testing Amazon and Flipkart scrapers")
    print("=" * 80)
    
    # Test local HTML parsing
    print("\n--- Testing Local HTML Parsing ---")
    tool = EnhancedPriceComparisonTool(local_html_path)
    products = await tool.search_products("IN", "iPhone 16 Pro Max", use_local=True)
    
    print(f"Found {len(products)} products total:")
    
    # Filter by source
    amazon_products = [p for p in products if p['source'] == 'Amazon.in']
    flipkart_products = [p for p in products if p['source'] == 'Flipkart']
    
    print(f"\nAmazon found {len(amazon_products)} products:")
    for i, product in enumerate(amazon_products[:3], 1):
        print(f"{i}. {product['productName'][:60]}...")
        print(f"   Price: {product['currency']} {product['price']}")
        print(f"   Link: {product['link'][:60]}...")
        print()
    
    print(f"\nFlipkart found {len(flipkart_products)} products:")
    for i, product in enumerate(flipkart_products[:3], 1):
        print(f"{i}. {product['productName'][:60]}...")
        print(f"   Price: {product['currency']} {product['price']}")
        print(f"   Link: {product['link'][:60]}...")
        print()
    
    # Test online scraping for just Amazon and Flipkart
    print("\n--- Testing Online Scraping ---")
    tool_online = EnhancedPriceComparisonTool()
    products_online = await tool_online.search_products("IN", "iPhone 16 Pro Max", use_local=False)
    
    amazon_online = [p for p in products_online if p['source'] == 'Amazon.in']
    flipkart_online = [p for p in products_online if p['source'] == 'Flipkart']
    
    print(f"\nAmazon online found {len(amazon_online)} products:")
    for i, product in enumerate(amazon_online[:2], 1):
        print(f"{i}. {product['productName'][:60]}...")
        print(f"   Price: {product['currency']} {product['price']}")
        print()
    
    print(f"\nFlipkart online found {len(flipkart_online)} products:")
    for i, product in enumerate(flipkart_online[:2], 1):
        print(f"{i}. {product['productName'][:60]}...")
        print(f"   Price: {product['currency']} {product['price']}")
        print()

if __name__ == "__main__":
    asyncio.run(test_amazon_flipkart())
