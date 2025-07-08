#!/usr/bin/env python3
"""
Test script for the price comparison tool
"""

import asyncio
import json
import sys
from price_comparison_tool import PriceComparisonTool

async def test_search(country: str, query: str):
    """Test the search functionality"""
    print(f"\n{'='*60}")
    print(f"Testing search for: '{query}' in {country}")
    print(f"{'='*60}")
    
    tool = PriceComparisonTool()
    
    try:
        results = await tool.search_products(country, query)
        
        if results:
            print(f"Found {len(results)} products:")
            print(json.dumps(results, indent=2))
        else:
            print("No products found")
            
    except Exception as e:
        print(f"Error during search: {e}")

async def run_tests():
    """Run multiple test cases"""
    test_cases = [
        {"country": "US", "query": "iPhone 16 Pro 128GB"},
        {"country": "IN", "query": "Samsung Galaxy S24"},
        {"country": "US", "query": "MacBook Air M2"},
        {"country": "IN", "query": "OnePlus 12"},
    ]
    
    for test_case in test_cases:
        await test_search(test_case["country"], test_case["query"])
        await asyncio.sleep(2)  # Rate limiting

def test_api():
    """Test the Flask API"""
    import requests
    
    print(f"\n{'='*60}")
    print("Testing Flask API")
    print(f"{'='*60}")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test search endpoint
    test_data = {
        "country": "US",
        "query": "iPhone 16 Pro 128GB"
    }
    
    try:
        response = requests.post(f"{base_url}/search", json=test_data)
        print(f"Search API: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Found {len(results)} products")
            print(json.dumps(results[:2], indent=2))  # Show first 2 results
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Search API failed: {e}")
    
    # Test supported countries endpoint
    try:
        response = requests.get(f"{base_url}/supported-countries")
        print(f"Supported countries: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Supported countries failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        test_api()
    else:
        asyncio.run(run_tests())
