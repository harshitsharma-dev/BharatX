#!/usr/bin/env python3
"""
Test all websites with higher limits
"""

import requests
import json
import time

def test_all_websites():
    print("=" * 60)
    print("TESTING ALL WEBSITES WITH HIGH LIMITS")
    print("=" * 60)
    
    # Test US with high limit
    us_data = {
        'country': 'US',
        'query': 'iPhone 16 Pro, 128GB',
        'use_local': True,
        'max_results': 100
    }
    
    print("1. TESTING US (eBay.com + Walmart):")
    try:
        response = requests.post('http://localhost:5000/search', json=us_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Total Results: {result['total_results']}")
            
            if 'source_breakdown' in result:
                print("   Sources found:")
                for source, count in result['source_breakdown'].items():
                    print(f"     {source}: {count} products")
            
            print("\n   Sample products:")
            for i, product in enumerate(result['products'][:3], 1):
                print(f"     {i}. {product['productName'][:50]}...")
                print(f"        Price: {product['currency']} {product['price']}")
                print(f"        Source: {product['source']}")
        else:
            print(f"   Error: {response.status_code}")
            
    except Exception as e:
        print(f"   Connection Error: {e}")
    
    print("\n" + "-" * 60)
    
    # Test India with high limit
    india_data = {
        'country': 'IN',
        'query': 'iPhone 16 Pro Max',
        'use_local': True,
        'max_results': 100
    }
    
    print("2. TESTING INDIA (Amazon.in + Flipkart + eBay.in + Snapdeal + Shopsy):")
    try:
        response = requests.post('http://localhost:5000/search', json=india_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Total Results: {result['total_results']}")
            
            if 'source_breakdown' in result:
                print("   Sources found:")
                for source, count in result['source_breakdown'].items():
                    print(f"     {source}: {count} products")
            
            print("\n   Sample products:")
            for i, product in enumerate(result['products'][:5], 1):
                print(f"     {i}. {product['productName'][:50]}...")
                print(f"        Price: {product['currency']} {product['price']}")
                print(f"        Source: {product['source']}")
        else:
            print(f"   Error: {response.status_code}")
            
    except Exception as e:
        print(f"   Connection Error: {e}")
    
    print("\n" + "=" * 60)
    print("SUMMARY: All websites tested with high limits")
    print("=" * 60)

if __name__ == "__main__":
    test_all_websites()
