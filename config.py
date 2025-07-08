#!/usr/bin/env python3
"""
Configuration management for API credentials
"""

import os
from typing import Dict, Optional

class APIConfig:
    """Centralized API configuration management"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from environment variables or config file"""
        return {
            "amazon": {
                "US": {
                    "access_key": os.getenv("AMAZON_US_ACCESS_KEY", ""),
                    "secret_key": os.getenv("AMAZON_US_SECRET_KEY", ""),
                    "associate_tag": os.getenv("AMAZON_US_ASSOCIATE_TAG", ""),
                    "marketplace": "webservices.amazon.com"
                },
                "IN": {
                    "access_key": os.getenv("AMAZON_IN_ACCESS_KEY", ""),
                    "secret_key": os.getenv("AMAZON_IN_SECRET_KEY", ""),
                    "associate_tag": os.getenv("AMAZON_IN_ASSOCIATE_TAG", ""),
                    "marketplace": "webservices.amazon.in"
                }
            },
            "ebay": {
                "app_id": os.getenv("EBAY_APP_ID", ""),
                "client_secret": os.getenv("EBAY_CLIENT_SECRET", ""),
                "marketplaces": {
                    "US": "EBAY_US",
                    "IN": "EBAY_IN", 
                    "UK": "EBAY_GB",
                    "DE": "EBAY_DE",
                    "CA": "EBAY_CA"
                }
            },
            "walmart": {
                "api_key": os.getenv("WALMART_API_KEY", "")
            },
            "flipkart": {
                "api_url": os.getenv("FLIPKART_API_URL", "http://localhost:8080")
            }
        }
    
    def get_amazon_config(self, country: str) -> Optional[Dict]:
        """Get Amazon configuration for country"""
        return self.config.get("amazon", {}).get(country.upper())
    
    def get_ebay_config(self) -> Dict:
        """Get eBay configuration"""
        return self.config.get("ebay", {})
    
    def get_walmart_config(self) -> Dict:
        """Get Walmart configuration"""
        return self.config.get("walmart", {})
    
    def get_flipkart_config(self) -> Dict:
        """Get Flipkart API configuration"""
        return self.config.get("flipkart", {})
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate that required API keys are present"""
        validation = {
            "amazon_us": bool(self.config["amazon"]["US"]["access_key"]),
            "amazon_in": bool(self.config["amazon"]["IN"]["access_key"]),
            "ebay": bool(self.config["ebay"]["app_id"]),
            "walmart": bool(self.config["walmart"]["api_key"]),
            "flipkart": bool(self.config["flipkart"]["api_url"])
        }
        return validation


# Create sample environment file
def create_env_template():
    """Create a template .env file"""
    template = """# Amazon Product Advertising API
AMAZON_US_ACCESS_KEY=your_amazon_us_access_key
AMAZON_US_SECRET_KEY=your_amazon_us_secret_key
AMAZON_US_ASSOCIATE_TAG=your_amazon_us_associate_tag

AMAZON_IN_ACCESS_KEY=your_amazon_in_access_key
AMAZON_IN_SECRET_KEY=your_amazon_in_secret_key
AMAZON_IN_ASSOCIATE_TAG=your_amazon_in_associate_tag

# eBay API
EBAY_APP_ID=your_ebay_app_id
EBAY_CLIENT_SECRET=your_ebay_client_secret

# Walmart API
WALMART_API_KEY=your_walmart_api_key

# Flipkart Scraper API URL
FLIPKART_API_URL=http://localhost:8080
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    
    print("Created .env.template file. Copy to .env and add your API keys.")

if __name__ == "__main__":
    create_env_template()
