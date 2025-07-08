#!/usr/bin/env python3
"""
eBay Search API Implementation
"""

import aiohttp
import json
from typing import List, Dict
import urllib.parse

class EbayAPIClient:
    """eBay Search API Client"""
    
    def __init__(self, app_id: str, client_secret: str, environment: str = "production"):
        self.app_id = app_id
        self.client_secret = client_secret
        self.environment = environment
        
        if environment == "sandbox":
            self.base_url = "https://api.sandbox.ebay.com"
        else:
            self.base_url = "https://api.ebay.com"
    
    async def get_access_token(self, session: aiohttp.ClientSession) -> str:
        """Get OAuth access token for eBay API"""
        
        url = f"{self.base_url}/identity/v1/oauth2/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self._get_basic_auth()}'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        try:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return token_data.get('access_token', '')
                else:
                    print(f"eBay Token Error: {response.status}")
                    return ''
        except Exception as e:
            print(f"eBay Token Exception: {e}")
            return ''
    
    def _get_basic_auth(self) -> str:
        """Generate basic auth string for eBay API"""
        import base64
        credentials = f"{self.app_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()
    
    async def search_products(self, session: aiohttp.ClientSession, query: str, marketplace_id: str = "EBAY_US") -> List[Dict]:
        """Search for products using eBay Browse API"""
        
        # Get access token
        access_token = await self.get_access_token(session)
        if not access_token:
            return []
        
        url = f"{self.base_url}/buy/browse/v1/item_summary/search"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-EBAY-C-MARKETPLACE-ID': marketplace_id,
            'X-EBAY-C-ENDUSERCTX': f'affiliateCampaignId={self.app_id}'
        }
        
        params = {
            'q': query,
            'limit': 10,
            'sort': 'price',
            'filter': 'buyingOptions:{FIXED_PRICE|AUCTION}'
        }
        
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_response(data)
                else:
                    print(f"eBay Search Error: {response.status}")
                    return []
        except Exception as e:
            print(f"eBay Search Exception: {e}")
            return []
    
    def _parse_search_response(self, data: Dict) -> List[Dict]:
        """Parse eBay search response"""
        products = []
        
        items = data.get('itemSummaries', [])
        
        for item in items:
            try:
                # Extract product details
                title = item.get('title', '')
                item_web_url = item.get('itemWebUrl', '')
                price_info = item.get('price', {})
                
                if title and item_web_url and price_info:
                    product = {
                        'productName': title,
                        'link': item_web_url,
                        'price': float(price_info.get('value', 0)),
                        'currency': price_info.get('currency', 'USD')
                    }
                    products.append(product)
                    
            except Exception as e:
                print(f"Error parsing eBay item: {e}")
                continue
                
        return products


# Configuration template
EBAY_CONFIG = {
    "US": {
        "app_id": "YOUR_APP_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "marketplace_id": "EBAY_US"
    },
    "IN": {
        "app_id": "YOUR_APP_ID", 
        "client_secret": "YOUR_CLIENT_SECRET",
        "marketplace_id": "EBAY_IN"
    },
    "UK": {
        "app_id": "YOUR_APP_ID",
        "client_secret": "YOUR_CLIENT_SECRET", 
        "marketplace_id": "EBAY_GB"
    }
}
