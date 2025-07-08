from flask import Flask, request, jsonify
import json
import time
from demo import MockPriceComparisonTool
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
tool = MockPriceComparisonTool()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Price comparison tool is running",
        "timestamp": int(time.time()),
        "version": "1.0.0"
    })

@app.route('/search', methods=['POST'])
def search_products():
    """Search for products endpoint"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        country = data.get('country')
        query = data.get('query')
        
        if not country or not query:
            return jsonify({"error": "Both 'country' and 'query' are required"}), 400
        
        # Validate country format
        if len(country) != 2:
            return jsonify({"error": "Country should be a 2-letter country code (e.g., 'US', 'IN')"}), 400
        
        logger.info(f"Searching for '{query}' in country '{country}'")
        
        # Run async search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(tool.search_products(country, query))
        loop.close()
        
        response_data = {
            "country": country,
            "query": query,
            "results_count": len(results),
            "products": results,
            "timestamp": int(time.time())
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/supported-countries', methods=['GET'])
def get_supported_countries():
    """Get list of supported countries"""
    supported_countries = {
        "US": {
            "name": "United States",
            "currency": "USD",
            "supported_sites": ["Amazon.com", "Best Buy", "eBay.com", "Target", "Walmart"]
        },
        "IN": {
            "name": "India",
            "currency": "INR", 
            "supported_sites": ["Amazon.in", "Flipkart", "eBay.in", "Croma", "Reliance Digital"]
        },
        "UK": {
            "name": "United Kingdom",
            "currency": "GBP",
            "supported_sites": ["Amazon.co.uk", "eBay.co.uk"]
        },
        "DE": {
            "name": "Germany",
            "currency": "EUR",
            "supported_sites": ["Amazon.de", "eBay.de"]
        },
        "CA": {
            "name": "Canada",
            "currency": "CAD",
            "supported_sites": ["Amazon.ca", "eBay.ca"]
        }
    }
    return jsonify(supported_countries)

@app.route('/sample-queries', methods=['GET'])
def get_sample_queries():
    """Get sample queries for testing"""
    sample_queries = {
        "US": [
            "iPhone 16 Pro 128GB",
            "MacBook Air M2",
            "Samsung Galaxy S24",
            "PlayStation 5",
            "iPad Pro"
        ],
        "IN": [
            "iPhone 16 Pro 128GB", 
            "Samsung Galaxy S24",
            "OnePlus 12",
            "MacBook Air",
            "iPad"
        ]
    }
    return jsonify(sample_queries)

@app.route('/', methods=['GET'])
def home():
    """Home page with API documentation"""
    documentation = {
        "name": "Price Comparison Tool API",
        "version": "1.0.0",
        "description": "Compare product prices across multiple e-commerce websites",
        "endpoints": {
            "GET /health": "Health check",
            "POST /search": "Search for products",
            "GET /supported-countries": "Get supported countries",
            "GET /sample-queries": "Get sample queries for testing"
        },
        "search_example": {
            "url": "/search",
            "method": "POST",
            "body": {
                "country": "US",
                "query": "iPhone 16 Pro 128GB"
            }
        },
        "demo_note": "This is a demo version using mock data. The actual implementation would scrape real e-commerce websites."
    }
    return jsonify(documentation)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "available_endpoints": ["/", "/health", "/search", "/supported-countries", "/sample-queries"]}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting Price Comparison Tool API...")
    print("Demo mode: Using mock data for demonstration")
    print("Available at: http://localhost:5000")
    print("\nTry these endpoints:")
    print("- GET  http://localhost:5000/health")
    print("- GET  http://localhost:5000/supported-countries")
    print("- POST http://localhost:5000/search")
    print("  Body: {\"country\": \"US\", \"query\": \"iPhone 16 Pro 128GB\"}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
