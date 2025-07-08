#!/usr/bin/env python3
"""
Complete Price Comparison API Application
Combines enhanced scraping, Flask API, caching, and comprehensive error handling
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

# Import our enhanced scraping tool
from enhanced_scraping_tool import EnhancedPriceComparisonTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('price_comparison.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
class Config:
    """Application configuration"""
    # Cache settings
    CACHE_TTL_SECONDS = 3600  # 1 hour
    CACHE_DIR = "api_cache"
    
    # API settings
    MAX_RESULTS_PER_SCRAPER = 20  # Increased from 10 to allow more results per source
    REQUEST_TIMEOUT = 30
    MAX_CONCURRENT_REQUESTS = 5
    
    # Supported countries and their details
    SUPPORTED_COUNTRIES = {
        "US": {
            "name": "United States",
            "currency": "USD",
            "sites": ["eBay.com", "Walmart"]
        },
        "IN": {
            "name": "India", 
            "currency": "INR",
            "sites": ["Amazon.in", "Flipkart", "eBay.in", "Snapdeal", "Shopsy"]
        },
        "UK": {
            "name": "United Kingdom",
            "currency": "GBP", 
            "sites": ["eBay.co.uk"]
        },
        "DE": {
            "name": "Germany",
            "currency": "EUR",
            "sites": ["eBay.de"]
        },
        "CA": {
            "name": "Canada",
            "currency": "CAD",
            "sites": ["eBay.ca"]
        }
    }
    
    # Sample queries for demonstration
    SAMPLE_QUERIES = {
        "US": ["iPhone 16 Pro Max", "Samsung Galaxy S24", "MacBook Pro", "AirPods Pro"],
        "IN": ["iPhone 16 Pro Max", "Samsung Galaxy S24", "OnePlus 12", "Nothing Phone 2"],
        "UK": ["iPhone 16 Pro Max", "Samsung Galaxy S24", "Google Pixel 8"],
        "DE": ["iPhone 16 Pro Max", "Samsung Galaxy S24", "Xiaomi 14"],
        "CA": ["iPhone 16 Pro Max", "Samsung Galaxy S24", "MacBook Air"]
    }

# Global variables
config = Config()
price_tool = None
executor = ThreadPoolExecutor(max_workers=config.MAX_CONCURRENT_REQUESTS)

def create_price_tool():
    """Create and return price comparison tool instance - Always fresh instance"""
    # Always create fresh instance to pick up code changes
    local_html_path = "webpages_samples"
    if os.path.exists(local_html_path):
        tool = EnhancedPriceComparisonTool(local_html_path)
        logger.info("Price tool initialized with local HTML samples")
    else:
        tool = EnhancedPriceComparisonTool()
        logger.info("Price tool initialized for online scraping")
    return tool

def run_async_search(country: str, query: str, use_local: bool = False) -> List[Dict]:
    """Run async search in a new event loop"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tool = create_price_tool()
        result = loop.run_until_complete(
            tool.search_products(country, query, use_local=use_local)
        )
        
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in async search: {e}")
        return []

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Price Comparison API",
        "version": "2.0.0",
        "description": "Compare prices across multiple e-commerce platforms",
        "endpoints": {
            "/": "This help message",
            "/health": "Health check",
            "/search": "Search for products (POST)",
            "/countries": "Get supported countries",
            "/samples": "Get sample queries by country"
        },
        "supported_countries": list(config.SUPPORTED_COUNTRIES.keys()),
        "total_sites": sum(len(info["sites"]) for info in config.SUPPORTED_COUNTRIES.values())
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test if we can create the price tool
        tool = create_price_tool()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cache_dir_exists": os.path.exists(config.CACHE_DIR),
            "local_html_available": os.path.exists("webpages_samples"),
            "supported_countries": len(config.SUPPORTED_COUNTRIES)
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/countries')
def get_supported_countries():
    """Get list of supported countries with details"""
    return jsonify({
        "countries": config.SUPPORTED_COUNTRIES,
        "total_countries": len(config.SUPPORTED_COUNTRIES),
        "total_sites": sum(len(info["sites"]) for info in config.SUPPORTED_COUNTRIES.values())
    })

@app.route('/samples')
def get_sample_queries():
    """Get sample queries for testing"""
    country = request.args.get('country', '').upper()
    
    if country and country in config.SAMPLE_QUERIES:
        return jsonify({
            "country": country,
            "samples": config.SAMPLE_QUERIES[country]
        })
    else:
        return jsonify({
            "all_samples": config.SAMPLE_QUERIES,
            "usage": "Add ?country=US to get samples for a specific country"
        })

def process_search_request(data: Dict) -> tuple:
    """Process search request data and return response"""
    start_time = time.time()
    
    try:
        # Validate required fields
        country = data.get('country', '').upper()
        query = data.get('query', '').strip()
        
        if not country:
            return jsonify({"error": "Country is required"}), 400
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Validate country support
        if country not in config.SUPPORTED_COUNTRIES:
            return jsonify({
                "error": f"Country '{country}' not supported",
                "supported_countries": list(config.SUPPORTED_COUNTRIES.keys())
            }), 400
        
        # Optional parameters
        use_local = data.get('use_local', False)  # For testing with local HTML
        max_results = min(data.get('max_results', 50), 100)  # Cap at 100, default 50
        
        logger.info(f"Search request: {query} in {country} (local: {use_local})")
        
        # Run search in thread pool to avoid blocking
        future = executor.submit(run_async_search, country, query, use_local)
        products = future.result(timeout=config.REQUEST_TIMEOUT)
        
        # Limit results
        products = products[:max_results]
        
        # Calculate response time
        response_time = round(time.time() - start_time, 2)
        
        # Prepare response
        response = {
            "success": True,
            "query": query,
            "country": country,
            "country_info": config.SUPPORTED_COUNTRIES[country],
            "products": products,
            "total_results": len(products),
            "response_time_seconds": response_time,
            "timestamp": datetime.now().isoformat(),
            "use_local": use_local
        }
        
        # Add summary statistics
        if products:
            prices = [p["price"] for p in products]
            currency = products[0]["currency"]
            
            response["price_analysis"] = {
                "currency": currency,
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": round(sum(prices) / len(prices), 2),
                "price_range": max(prices) - min(prices)
            }
            
            # Group by source
            sources = {}
            for product in products:
                source = product["source"]
                if source not in sources:
                    sources[source] = 0
                sources[source] += 1
            
            response["source_breakdown"] = sources
        
        logger.info(f"Search completed: {len(products)} products in {response_time}s")
        return jsonify(response), 200
        
    except asyncio.TimeoutError:
        logger.error("Search request timed out")
        return jsonify({
            "error": "Search request timed out",
            "suggestion": "Try a more specific query or try again later"
        }), 408
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/search', methods=['POST'])
def search_products():
    """Main search endpoint"""
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        return process_search_request(data)
        
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        return jsonify({
            "error": "Failed to process request",
            "message": str(e)
        }), 500

@app.route('/demo', methods=['GET', 'POST'])
def demo_endpoint():
    """Demo endpoint for quick testing"""
    if request.method == 'GET':
        # Show demo form
        return jsonify({
            "message": "Demo endpoint - POST to this URL to test the API",
            "example_request": {
                "country": "IN",
                "query": "iPhone 16 Pro Max",
                "use_local": True,
                "max_results": 10
            },
            "sample_curl": 'curl -X POST -H "Content-Type: application/json" -d \'{"country":"IN","query":"iPhone 16 Pro Max","use_local":true}\' http://localhost:5000/demo'
        })
    
    # For POST requests, use default demo data if not provided
    try:
        data = request.get_json() or {}
        
        # Use defaults for demo
        demo_request = {
            "country": data.get("country", "IN"),
            "query": data.get("query", "iPhone 16 Pro Max"), 
            "use_local": data.get("use_local", True),
            "max_results": data.get("max_results", 10)
        }
        
        logger.info(f"Demo request: {demo_request}")
        
        # Process demo request directly
        response, status_code = process_search_request(demo_request)
        return response, status_code
        
    except Exception as e:
        return jsonify({
            "error": "Demo error",
            "message": str(e)
        }), 500

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear application cache"""
    try:
        cache_dir = config.CACHE_DIR
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
        
        return jsonify({
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({
            "error": "Failed to clear cache",
            "message": str(e)
        }), 500

@app.route('/cache/status')
def cache_status():
    """Get cache status information"""
    try:
        cache_dir = config.CACHE_DIR
        cache_files = []
        total_size = 0
        
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                filepath = os.path.join(cache_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    modified = os.path.getmtime(filepath)
                    cache_files.append({
                        "filename": filename,
                        "size_bytes": size,
                        "modified": datetime.fromtimestamp(modified).isoformat()
                    })
                    total_size += size
        
        return jsonify({
            "cache_directory": cache_dir,
            "cache_exists": os.path.exists(cache_dir),
            "total_files": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "ttl_seconds": config.CACHE_TTL_SECONDS,
            "files": cache_files[:10]  # Show first 10 files
        })
    except Exception as e:
        return jsonify({
            "error": "Failed to get cache status",
            "message": str(e)
        }), 500

@app.route('/debug', methods=['POST'])
def debug_endpoint():
    """Debug endpoint to see detailed scraping logs"""
    try:
        data = request.get_json() or {}
        
        # Use defaults for debug
        country = data.get("country", "IN")
        query = data.get("query", "iPhone 16 Pro Max")
        use_local = data.get("use_local", True)
        
        logger.info(f"Debug request: {query} in {country} (local: {use_local})")
        
        # Enable verbose logging temporarily
        logging.getLogger('enhanced_scraping_tool').setLevel(logging.DEBUG)
        
        # Run search with detailed logging
        future = executor.submit(run_async_search, country, query, use_local)
        products = future.result(timeout=config.REQUEST_TIMEOUT)
        
        # Group by source for debugging
        sources = {}
        for product in products:
            source = product["source"]
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        return jsonify({
            "debug": True,
            "query": query,
            "country": country,
            "products_found": len(products),
            "sources": sources,
            "raw_products": products[:10]  # First 10 for inspection
        }), 200
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested URL was not found on the server",
        "available_endpoints": [
            "/", "/health", "/search", "/countries", 
            "/samples", "/demo", "/cache/status", "/cache/clear"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now().isoformat()
    }), 500

def create_app():
    """Application factory function"""
    # Ensure cache directory exists
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    
    # Initialize price tool
    create_price_tool()
    
    logger.info("Complete Price Comparison API initialized")
    return app

if __name__ == '__main__':
    # Create the app
    complete_app = create_app()
    
    # Run the Flask development server
    logger.info("Starting Complete Price Comparison API server...")
    logger.info("Available endpoints:")
    logger.info("  GET  /              - API information")
    logger.info("  GET  /health        - Health check")
    logger.info("  GET  /countries     - Supported countries")
    logger.info("  GET  /samples       - Sample queries")
    logger.info("  POST /search        - Search products")
    logger.info("  GET|POST /demo      - Demo endpoint")
    logger.info("  GET  /cache/status  - Cache information")
    logger.info("  POST /cache/clear   - Clear cache")
    
    complete_app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to False for production
        threaded=True
    )
