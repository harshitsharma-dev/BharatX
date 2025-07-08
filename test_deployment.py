#!/usr/bin/env python3
"""
Test deployed API with MCDM ranking
"""

import requests
import json
import time

def test_deployed_api(base_url="http://localhost:5000"):
    """Test the deployed API endpoints"""
    
    print(f"Testing API at: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check: PASSED")
        else:
            print(f"❌ Health check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
    
    # Test 2: API info
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ API Info: {info.get('message', 'OK')}")
            print(f"   Supported countries: {len(info.get('supported_countries', []))}")
        else:
            print(f"❌ API Info: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ API Info: ERROR - {e}")
    
    # Test 3: MCDM Search Test (India)
    print("\n📱 Testing MCDM Search - iPhone 16 Pro Max (India)")
    print("-" * 60)
    
    search_data = {
        "country": "IN",
        "query": "iPhone 16 Pro Max",
        "use_local": True,
        "max_results": 10
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/search", json=search_data, timeout=60)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search successful in {response_time:.2f}s")
            print(f"   Total results: {result.get('total_results', 0)}")
            
            # Check MCDM ranking quality
            products = result.get('products', [])
            if products:
                print(f"   Top result: {products[0]['productName'][:50]}...")
                print(f"   Price: {products[0]['currency']} {products[0]['price']}")
                print(f"   Source: {products[0]['source']}")
                
                # Check if MCDM score exists
                if 'mcdm_score' in products[0]:
                    print(f"   MCDM Score: {products[0]['mcdm_score']:.3f}")
                else:
                    print("   MCDM Score: Not available (may be filtered out)")
                
                # Show source breakdown
                if 'source_breakdown' in result:
                    print("   Sources found:")
                    for source, count in result['source_breakdown'].items():
                        print(f"     {source}: {count} products")
            
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test 4: US Search Test
    print("\n🇺🇸 Testing MCDM Search - iPhone 16 Pro Max (US)")
    print("-" * 60)
    
    search_data_us = {
        "country": "US",
        "query": "iPhone 16 Pro Max",
        "use_local": True,
        "max_results": 10
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/search", json=search_data_us, timeout=60)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ US Search successful in {response_time:.2f}s")
            print(f"   Total results: {result.get('total_results', 0)}")
            
            products = result.get('products', [])
            if products:
                print(f"   Top result: {products[0]['productName'][:50]}...")
                print(f"   Price: {products[0]['currency']} {products[0]['price']}")
                print(f"   Source: {products[0]['source']}")
        else:
            print(f"❌ US Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ US Search error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DEPLOYMENT TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    # Test local development server
    test_deployed_api("http://localhost:5000")
    
    # Uncomment to test production deployment
    # test_deployed_api("https://your-app-name.onrender.com")
