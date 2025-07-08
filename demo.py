#!/usr/bin/env python3
"""
Demo script with mock data for the price comparison tool
This demonstrates the expected output format and functionality
"""

import json
import asyncio
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Product:
    """Data class for product information"""
    link: str
    price: float
    currency: str
    product_name: str
    
    def to_dict(self) -> Dict:
        return {
            "link": self.link,
            "price": self.price,
            "currency": self.currency,
            "productName": self.product_name
        }

class MockPriceComparisonTool:
    """Mock version of the price comparison tool with sample data"""
    
    def __init__(self):
        self.mock_data = {
            "US": {
                "iPhone 16 Pro 128GB": [
                    Product("https://www.amazon.com/dp/B0DHJXS9CY", 999.0, "USD", "Apple iPhone 16 Pro 128GB - Natural Titanium"),
                    Product("https://www.bestbuy.com/site/iphone-16-pro", 999.0, "USD", "Apple - iPhone 16 Pro 128GB - Natural Titanium"),
                    Product("https://www.ebay.com/itm/iphone16pro", 1049.99, "USD", "iPhone 16 Pro 128GB Unlocked - Natural Titanium"),
                    Product("https://www.target.com/p/iphone-16-pro", 999.0, "USD", "Apple iPhone 16 Pro 128GB"),
                    Product("https://www.walmart.com/ip/iphone-16", 1020.0, "USD", "Apple iPhone 16 Pro 128GB Natural Titanium")
                ],
                "MacBook Air M2": [
                    Product("https://www.amazon.com/dp/B0B3C2R8MP", 999.0, "USD", "Apple MacBook Air 13-inch M2 Chip 8GB RAM 256GB SSD"),
                    Product("https://www.bestbuy.com/site/macbook-air-m2", 999.0, "USD", "Apple - MacBook Air 13.6-inch M2 chip - 8GB Memory - 256GB SSD"),
                    Product("https://www.apple.com/shop/buy-mac/macbook-air", 1199.0, "USD", "MacBook Air 13-inch M2"),
                    Product("https://www.costco.com/macbook-air-m2", 949.99, "USD", "Apple MacBook Air M2 13-inch"),
                    Product("https://www.ebay.com/itm/macbook-air-m2", 899.0, "USD", "Apple MacBook Air M2 13-inch 8GB 256GB")
                ]
            },
            "IN": {
                "iPhone 16 Pro 128GB": [
                    Product("https://www.amazon.in/dp/B0DHJXS9CY", 134900.0, "INR", "Apple iPhone 16 Pro 128GB - Natural Titanium"),
                    Product("https://www.flipkart.com/iphone-16-pro", 134900.0, "INR", "Apple iPhone 16 Pro (Natural Titanium, 128 GB)"),
                    Product("https://www.sangeethamobiles.com/iphone16pro", 129999.0, "INR", "iPhone 16 Pro 128GB Natural Titanium"),
                    Product("https://www.croma.com/iphone-16-pro", 134900.0, "INR", "Apple iPhone 16 Pro 128GB"),
                    Product("https://www.reliancedigital.in/iphone-16", 139900.0, "INR", "Apple iPhone 16 Pro 128GB Natural Titanium")
                ],
                "Samsung Galaxy S24": [
                    Product("https://www.amazon.in/dp/S24", 74999.0, "INR", "Samsung Galaxy S24 5G (Marble Grey, 8GB, 128GB Storage)"),
                    Product("https://www.flipkart.com/samsung-galaxy-s24", 72999.0, "INR", "Samsung Galaxy S24 5G (Marble Grey, 8GB RAM, 128GB Storage)"),
                    Product("https://www.samsung.com/in/smartphones/galaxy-s24", 79999.0, "INR", "Galaxy S24 5G 128GB"),
                    Product("https://www.vijaysales.com/galaxy-s24", 74500.0, "INR", "Samsung Galaxy S24 5G 128GB"),
                    Product("https://www.croma.com/samsung-galaxy-s24", 76999.0, "INR", "Samsung Galaxy S24 5G 128GB Marble Grey")
                ],
                "OnePlus 12": [
                    Product("https://www.amazon.in/dp/OnePlus12", 64999.0, "INR", "OnePlus 12 5G (Flowy Emerald, 12GB RAM, 256GB Storage)"),
                    Product("https://www.flipkart.com/oneplus-12", 64999.0, "INR", "OnePlus 12 5G (Flowy Emerald, 12GB RAM, 256GB Storage)"),
                    Product("https://www.oneplus.in/12", 69999.0, "INR", "OnePlus 12 256GB Flowy Emerald"),
                    Product("https://www.amazon.in/dp/OnePlus12-alt", 62999.0, "INR", "OnePlus 12 5G Smartphone 256GB"),
                    Product("https://www.poorvika.com/oneplus-12", 63500.0, "INR", "OnePlus 12 5G 256GB Flowy Emerald")
                ]
            }
        }
    
    async def search_products(self, country: str, query: str) -> List[Dict]:
        """Mock search that returns sample data"""
        print(f"Searching for '{query}' in {country}...")
        
        # Simulate network delay
        await asyncio.sleep(1)
        
        country_data = self.mock_data.get(country.upper(), {})
        
        # Find matching products based on query
        for product_key, products in country_data.items():
            if any(word.lower() in product_key.lower() for word in query.split()):
                # Sort by price (ascending)
                sorted_products = sorted(products, key=lambda x: x.price)
                return [product.to_dict() for product in sorted_products]
        
        # If no exact match, return empty list
        return []

async def demo_search(country: str, query: str):
    """Demonstrate the search functionality with mock data"""
    print(f"\n{'='*60}")
    print(f"Demo: Searching for '{query}' in {country}")
    print(f"{'='*60}")
    
    tool = MockPriceComparisonTool()
    
    try:
        results = await tool.search_products(country, query)
        
        if results:
            print(f"Found {len(results)} products (sorted by price):")
            print(json.dumps(results, indent=2))
            
            # Show price comparison summary
            print(f"\nPrice Summary:")
            print(f"Lowest Price: {results[0]['currency']} {results[0]['price']}")
            print(f"Highest Price: {results[-1]['currency']} {results[-1]['price']}")
            if len(results) > 1:
                savings = results[-1]['price'] - results[0]['price']
                print(f"Potential Savings: {results[0]['currency']} {savings:.2f}")
        else:
            print("No products found for this query")
            
    except Exception as e:
        print(f"Error during search: {e}")

async def run_demo():
    """Run demonstration with multiple test cases"""
    print("Price Comparison Tool - Mock Demo")
    print("This demonstrates the expected functionality with sample data")
    
    test_cases = [
        {"country": "US", "query": "iPhone 16 Pro 128GB"},
        {"country": "IN", "query": "iPhone 16 Pro 128GB"},
        {"country": "US", "query": "MacBook Air M2"},
        {"country": "IN", "query": "Samsung Galaxy S24"},
        {"country": "IN", "query": "OnePlus 12"},
        {"country": "US", "query": "Unknown Product"},  # Test case with no results
    ]
    
    for test_case in test_cases:
        await demo_search(test_case["country"], test_case["query"])
        await asyncio.sleep(0.5)  # Small delay between tests

def show_api_examples():
    """Show examples of how to use the API"""
    print(f"\n{'='*60}")
    print("API Usage Examples")
    print(f"{'='*60}")
    
    print("\n1. Using cURL:")
    print("""
curl -X POST http://localhost:5000/search \\
  -H "Content-Type: application/json" \\
  -d '{"country": "US", "query": "iPhone 16 Pro 128GB"}'
""")
    
    print("\n2. Using Python requests:")
    print("""
import requests

response = requests.post('http://localhost:5000/search', 
    json={"country": "US", "query": "iPhone 16 Pro 128GB"})

if response.status_code == 200:
    products = response.json()
    for product in products:
        print(f"{product['productName']}: {product['currency']} {product['price']}")
""")
    
    print("\n3. Expected Response Format:")
    print("""
[
  {
    "link": "https://www.amazon.com/dp/B0DHJXS9CY",
    "price": 999.0,
    "currency": "USD",
    "productName": "Apple iPhone 16 Pro 128GB - Natural Titanium"
  },
  {
    "link": "https://www.bestbuy.com/site/iphone-16-pro",
    "price": 999.0,
    "currency": "USD", 
    "productName": "Apple - iPhone 16 Pro 128GB - Natural Titanium"
  }
]
""")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_demo())
    
    # Show API examples
    show_api_examples()
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print("1. Run 'python app.py' to start the Flask API server")
    print("2. Test the API endpoints using the examples above")
    print("3. Build and run with Docker: 'docker-compose up --build'")
    print(f"{'='*60}")
