from flask import Flask, request, jsonify
import asyncio
import json
from price_comparison_tool import PriceComparisonTool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
tool = PriceComparisonTool()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Price comparison tool is running"})

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
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/supported-countries', methods=['GET'])
def get_supported_countries():
    """Get list of supported countries"""
    supported_countries = {
        "US": "United States",
        "IN": "India", 
        "UK": "United Kingdom",
        "DE": "Germany",
        "CA": "Canada"
    }
    return jsonify(supported_countries)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
