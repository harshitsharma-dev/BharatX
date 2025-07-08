#!/usr/bin/env python3
"""
Amazon Product Advertising API Implementation
"""

import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime
import aiohttp
import xml.etree.ElementTree as ET
from typing import List, Dict

class AmazonPAAPIClient:
    """Amazon Product Advertising API Client"""
    
    def __init__(self, access_key: str, secret_key: str, associate_tag: str, marketplace: str = "webservices.amazon.com"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.marketplace = marketplace
        self.endpoint = f"https://{marketplace}/onca/xml"
    
    def _generate_signature(self, params: Dict[str, str]) -> str:
        """Generate AWS signature for the request"""
        # Sort parameters
        sorted_params = sorted(params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        
        # Create string to sign
        string_to_sign = f"GET\n{self.marketplace}\n/onca/xml\n{query_string}"
        
        # Generate signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    async def search_products(self, session: aiohttp.ClientSession, query: str, search_index: str = "All") -> List[Dict]:
        """Search for products using Amazon PA API"""
        
        # Base parameters
        params = {
            'Service': 'AWSECommerceService',
            'Operation': 'ItemSearch',
            'AWSAccessKeyId': self.access_key,
            'AssociateTag': self.associate_tag,
            'SearchIndex': search_index,
            'Keywords': query,
            'ResponseGroup': 'ItemAttributes,Offers,Images',
            'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'Version': '2013-08-01'
        }
        
        # Generate signature
        signature = self._generate_signature(params)
        params['Signature'] = signature
        
        try:
            async with session.get(self.endpoint, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self._parse_xml_response(xml_content)
                else:
                    print(f"Amazon API Error: {response.status}")
                    return []
        except Exception as e:
            print(f"Amazon API Exception: {e}")
            return []
    
    def _parse_xml_response(self, xml_content: str) -> List[Dict]:
        """Parse XML response from Amazon API"""
        products = []
        
        try:
            root = ET.fromstring(xml_content)
            items = root.findall('.//Item')
            
            for item in items:
                try:
                    # Extract product details
                    title = item.find('.//Title')
                    detail_url = item.find('.//DetailPageURL')
                    price = item.find('.//LowestNewPrice/Amount')
                    currency = item.find('.//LowestNewPrice/CurrencyCode')
                    
                    if title is not None and detail_url is not None and price is not None:
                        product = {
                            'productName': title.text,
                            'link': detail_url.text,
                            'price': float(price.text) / 100,  # Amazon returns price in cents
                            'currency': currency.text if currency is not None else 'USD'
                        }
                        products.append(product)
                        
                except Exception as e:
                    print(f"Error parsing Amazon item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error parsing Amazon XML: {e}")
            
        return products


# Configuration template
AMAZON_CONFIG = {
    "US": {
        "access_key": "YOUR_ACCESS_KEY",
        "secret_key": "YOUR_SECRET_KEY", 
        "associate_tag": "YOUR_ASSOCIATE_TAG",
        "marketplace": "webservices.amazon.com"
    },
    "IN": {
        "access_key": "YOUR_ACCESS_KEY",
        "secret_key": "YOUR_SECRET_KEY",
        "associate_tag": "YOUR_ASSOCIATE_TAG", 
        "marketplace": "webservices.amazon.in"
    }
}
