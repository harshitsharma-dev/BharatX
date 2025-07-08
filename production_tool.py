#!/usr/bin/env python3
"""
Production Price Comparison Tool with Real APIs
"""

import asyncio
import aiohttp
import json
from typing import List, Dict
from dataclasses import dataclass
import logging

from amazon_api_client import AmazonPAAPIClient
from ebay_api_client import EbayAPIClient
from walmart_api_client import WalmartAPIClient
from config import APIConfig

logger = logging.getLogger(__name__)

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

class ProductionPriceComparisonTool:
    """Production price comparison tool with real APIs"""
    
    def __init__(self):
        self.config = APIConfig()
        self.validation = self.config.validate_config()
    
    async def search_products(self, country: str, query: str) -> List[Dict]:
        """Search for products using real APIs"""
        
        # Check API availability
        logger.info(f"API Status: {self.validation}")
        
        all_products = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Amazon API
            if self.validation.get("amazon_us") and country.upper() == "US":
                amazon_config = self.config.get_amazon_config("US")
                amazon_client = AmazonPAAPIClient(**amazon_config)
                tasks.append(self._search_amazon(session, amazon_client, query))
            
            elif self.validation.get("amazon_in") and country.upper() == "IN":
                amazon_config = self.config.get_amazon_config("IN")
                amazon_client = AmazonPAAPIClient(**amazon_config)
                tasks.append(self._search_amazon(session, amazon_client, query))
            
            # eBay API
            if self.validation.get("ebay"):
                ebay_config = self.config.get_ebay_config()
                ebay_client = EbayAPIClient(ebay_config["app_id"], ebay_config["client_secret"])
                marketplace_id = ebay_config["marketplaces"].get(country.upper(), "EBAY_US")
                tasks.append(self._search_ebay(session, ebay_client, query, marketplace_id))
            
            # Walmart API (US only)
            if self.validation.get("walmart") and country.upper() == "US":
                walmart_config = self.config.get_walmart_config()
                walmart_client = WalmartAPIClient(walmart_config["api_key"])
                tasks.append(self._search_walmart(session, walmart_client, query))
            
            # Flipkart API (India only)
            if self.validation.get("flipkart") and country.upper() == "IN":
                flipkart_config = self.config.get_flipkart_config()
                tasks.append(self._search_flipkart(session, flipkart_config["api_url"], query))
            
            # Execute all API calls in parallel
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, list):
                        all_products.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"API Error: {result}")
            else:
                logger.warning("No APIs configured or available for this request")
        
        # Remove duplicates and sort by price
        unique_products = self._remove_duplicates(all_products)
        sorted_products = sorted(unique_products, key=lambda x: x.price)
        
        return [product.to_dict() for product in sorted_products]
    
    async def _search_amazon(self, session: aiohttp.ClientSession, client: AmazonPAAPIClient, query: str) -> List[Product]:
        """Search Amazon using PA API"""
        try:
            results = await client.search_products(session, query)
            products = []
            for result in results:
                products.append(Product(
                    link=result["link"],
                    price=result["price"],
                    currency=result["currency"],
                    product_name=result["productName"]
                ))
            return products
        except Exception as e:
            logger.error(f"Amazon search error: {e}")
            return []
    
    async def _search_ebay(self, session: aiohttp.ClientSession, client: EbayAPIClient, query: str, marketplace_id: str) -> List[Product]:
        """Search eBay using Browse API"""
        try:
            results = await client.search_products(session, query, marketplace_id)
            products = []
            for result in results:
                products.append(Product(
                    link=result["link"],
                    price=result["price"],
                    currency=result["currency"],
                    product_name=result["productName"]
                ))
            return products
        except Exception as e:
            logger.error(f"eBay search error: {e}")
            return []
    
    async def _search_walmart(self, session: aiohttp.ClientSession, client: WalmartAPIClient, query: str) -> List[Product]:
        """Search Walmart using Search API"""
        try:
            results = await client.search_products(session, query)
            products = []
            for result in results:
                products.append(Product(
                    link=result["link"],
                    price=result["price"],
                    currency=result["currency"],
                    product_name=result["productName"]
                ))
            return products
        except Exception as e:
            logger.error(f"Walmart search error: {e}")
            return []
    
    async def _search_flipkart(self, session: aiohttp.ClientSession, api_url: str, query: str) -> List[Product]:
        """Search Flipkart using community scraper API"""
        try:
            url = f"{api_url}/search"
            params = {"query": query}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    products = []
                    
                    for item in data.get("products", []):
                        products.append(Product(
                            link=item.get("link", ""),
                            price=float(item.get("current_price", 0)),
                            currency="INR",
                            product_name=item.get("name", "")
                        ))
                    
                    return products
                else:
                    logger.error(f"Flipkart API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Flipkart search error: {e}")
            return []
    
    def _remove_duplicates(self, products: List[Product]) -> List[Product]:
        """Remove duplicate products based on similarity"""
        from fuzzywuzzy import fuzz
        
        unique_products = []
        
        for product in products:
            is_duplicate = False
            for existing in unique_products:
                # Check if products are similar
                name_similarity = fuzz.ratio(product.product_name.lower(), existing.product_name.lower())
                price_diff = abs(product.price - existing.price) / max(product.price, existing.price)
                
                if name_similarity > 80 and price_diff < 0.1:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_products.append(product)
        
        return unique_products


async def main():
    """Test the production tool"""
    tool = ProductionPriceComparisonTool()
    
    # Test search
    results = await tool.search_products("US", "iPhone 16 Pro 128GB")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
