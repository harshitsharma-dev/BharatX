#!/usr/bin/env python3
"""
Test the Complete Price Comparison API
"""

import requests
import json
import time

def test_api():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("Testing Complete Price Comparison API")
    print("=" * 60)
    
    # Test 1: Home endpoint
    print("\n1. Testing Home Endpoint (GET /)")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data['message']}")
            print(f"Version: {data['version']}")
            print(f"Supported Countries: {data['supported_countries']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
        return
    
    # Test 2: Health check
    print("\n2. Testing Health Check (GET /health)")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"Health Status: {health['status']}")
            print(f"Local HTML Available: {health['local_html_available']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Countries endpoint
    print("\n3. Testing Countries (GET /countries)")
    try:
        response = requests.get(f"{base_url}/countries")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            countries = response.json()
            print(f"Total Countries: {countries['total_countries']}")
            print(f"Total Sites: {countries['total_sites']}")
            for code, info in list(countries['countries'].items())[:3]:
                print(f"  {code}: {info['name']} - {len(info['sites'])} sites")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Sample queries
    print("\n4. Testing Samples (GET /samples)")
    try:
        response = requests.get(f"{base_url}/samples?country=IN")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            samples = response.json()
            print(f"Samples for IN: {samples['samples']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Demo endpoint (GET)
    print("\n5. Testing Demo Info (GET /demo)")
    try:
        response = requests.get(f"{base_url}/demo")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            demo = response.json()
            print(f"Demo Message: {demo['message']}")
            print(f"Example Request: {demo['example_request']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Search endpoint with local HTML
    print("\n6. Testing Search with Local HTML (POST /search)")
    try:
        search_data = {
            "country": "IN",
            "query": "iPhone 16 Pro Max",
            "use_local": True,
            "max_results": 5
        }
        
        print(f"Request: {search_data}")
        response = requests.post(
            f"{base_url}/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Success: {results['success']}")
            print(f"Country: {results['country']}")
            print(f"Total Results: {results['total_results']}")
            print(f"Response Time: {results['response_time_seconds']}s")
            
            if 'price_analysis' in results:
                analysis = results['price_analysis']
                print(f"Price Range: {analysis['currency']} {analysis['min_price']} - {analysis['max_price']}")
                print(f"Average Price: {analysis['currency']} {analysis['avg_price']}")
            
            if 'source_breakdown' in results:
                print("Sources:")
                for source, count in results['source_breakdown'].items():
                    print(f"  {source}: {count} products")
            
            print("\nTop 3 Products:")
            for i, product in enumerate(results['products'][:3], 1):
                print(f"  {i}. {product['productName'][:50]}...")
                print(f"     Price: {product['currency']} {product['price']}")
                print(f"     Source: {product['source']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 7: Demo endpoint (POST)
    print("\n7. Testing Demo Search (POST /demo)")
    try:
        demo_data = {
            "country": "IN",
            "query": "Samsung Galaxy S24",
            "use_local": True,
            "max_results": 3
        }
        
        response = requests.post(
            f"{base_url}/demo",
            json=demo_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Query: {results['query']}")
            print(f"Products Found: {results['total_results']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 8: Cache status
    print("\n8. Testing Cache Status (GET /cache/status)")
    try:
        response = requests.get(f"{base_url}/cache/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            cache = response.json()
            print(f"Cache Directory: {cache['cache_directory']}")
            print(f"Total Files: {cache['total_files']}")
            print(f"Total Size: {cache['total_size_mb']} MB")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("API Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
