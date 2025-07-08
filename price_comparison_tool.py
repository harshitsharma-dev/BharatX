#!/usr/bin/env python3
"""
Price Comparison Tool
A modular tool for fetching and comparing product prices across multiple e-commerce websites
based on user's country and query.
"""

import asyncio
import aiohttp
import json
import re
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup
import logging
from fuzzywuzzy import fuzz
import hashlib
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
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

class CacheManager:
    """Simple file-based cache manager for storing search results"""
    
    def __init__(self, cache_dir: str = "cache", ttl_seconds: int = 3600):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, country: str, query: str) -> str:
        """Generate cache key from country and query"""
        key_string = f"{country}:{query}".lower()
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, country: str, query: str) -> Optional[List[Product]]:
        """Get cached results if they exist and are not expired"""
        cache_key = self._get_cache_key(country, query)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                
            # Check if cache is expired
            if time.time() - cached_data['timestamp'] > self.ttl_seconds:
                os.remove(cache_file)
                return None
                
            return cached_data['products']
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set(self, country: str, query: str, products: List[Product]):
        """Cache the search results"""
        cache_key = self._get_cache_key(country, query)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        try:
            cached_data = {
                'timestamp': time.time(),
                'products': products
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")

class BaseScraper:
    """Base class for website scrapers"""
    
    def __init__(self, name: str, base_url: str, search_url: str):
        self.name = name
        self.base_url = base_url
        self.search_url = search_url
    
    async def search(self, session: aiohttp.ClientSession, query: str) -> List[Product]:
        """Search for products on the website"""
        try:
            search_url = self._build_search_url(query)
            headers = self._get_headers()
            
            async with session.get(search_url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_results(html, query)
                else:
                    logger.warning(f"{self.name}: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error scraping {self.name}: {e}")
            return []
    
    def _build_search_url(self, query: str) -> str:
        """Build search URL for the query"""
        raise NotImplementedError
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        """Parse HTML and extract product information"""
        raise NotImplementedError

class AmazonScraper(BaseScraper):
    """Amazon scraper implementation"""
    
    def __init__(self, domain: str = "com"):
        base_url = f"https://www.amazon.{domain}"
        search_url = f"{base_url}/s"
        super().__init__(f"Amazon.{domain}", base_url, search_url)
        self.domain = domain
    
    def _build_search_url(self, query: str) -> str:
        params = {"k": query, "ref": "sr_pg_1"}
        return f"{self.search_url}?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for container in product_containers[:5]:  # Limit to top 5 results
            try:
                # Product name
                title_elem = container.find('h2')
                if not title_elem:
                    continue
                title_link = title_elem.find('a')
                if not title_link:
                    continue
                    
                product_name = title_link.get_text(strip=True)
                product_link = self.base_url + title_link.get('href', '')
                
                # Price
                price_elem = container.find('span', class_='a-price-whole')
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True).replace(',', '')
                price = float(re.findall(r'\d+', price_text)[0])
                
                # Currency
                currency = "USD" if self.domain == "com" else "INR" if self.domain == "in" else "USD"
                
                # Fuzzy match to ensure relevance
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 60:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency=currency,
                        product_name=product_name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Amazon product: {e}")
                continue
        
        return products

class FlipkartScraper(BaseScraper):
    """Flipkart scraper implementation"""
    
    def __init__(self):
        super().__init__("Flipkart", "https://www.flipkart.com", "https://www.flipkart.com/search")
    
    def _build_search_url(self, query: str) -> str:
        params = {"q": query}
        return f"{self.search_url}?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', class_='_1AtVbE')
        
        for container in product_containers[:5]:  # Limit to top 5 results
            try:
                # Product name
                title_elem = container.find('div', class_='_4rR01T')
                if not title_elem:
                    continue
                product_name = title_elem.get_text(strip=True)
                
                # Product link
                link_elem = container.find('a')
                if not link_elem:
                    continue
                product_link = self.base_url + link_elem.get('href', '')
                
                # Price
                price_elem = container.find('div', class_='_30jeq3')
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True).replace('₹', '').replace(',', '')
                price = float(re.findall(r'\d+', price_text)[0])
                
                # Fuzzy match to ensure relevance
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 60:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="INR",
                        product_name=product_name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Flipkart product: {e}")
                continue
        
        return products

class EbayScraper(BaseScraper):
    """eBay scraper implementation"""
    
    def __init__(self, domain: str = "com"):
        base_url = f"https://www.ebay.{domain}"
        search_url = f"{base_url}/sch/i.html"
        super().__init__(f"eBay.{domain}", base_url, search_url)
        self.domain = domain
    
    def _build_search_url(self, query: str) -> str:
        params = {"_nkw": query, "_sacat": "0"}
        return f"{self.search_url}?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', class_='s-item__info')
        
        for container in product_containers[:5]:  # Limit to top 5 results
            try:
                # Product name
                title_elem = container.find('h3', class_='s-item__title')
                if not title_elem:
                    continue
                product_name = title_elem.get_text(strip=True)
                
                # Product link
                link_elem = container.find('a')
                if not link_elem:
                    continue
                product_link = link_elem.get('href', '')
                
                # Price
                price_elem = container.find('span', class_='s-item__price')
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price_numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if not price_numbers:
                    continue
                price = float(price_numbers[0])
                
                # Currency
                currency = "USD" if self.domain == "com" else "INR" if self.domain == "in" else "USD"
                
                # Fuzzy match to ensure relevance
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 60:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency=currency,
                        product_name=product_name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing eBay product: {e}")
                continue
        
        return products

class PriceComparisonTool:
    """Main price comparison tool"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> Dict[str, List[BaseScraper]]:
        """Initialize scrapers for different countries"""
        return {
            "US": [
                AmazonScraper("com"),
                EbayScraper("com"),
            ],
            "IN": [
                AmazonScraper("in"),
                FlipkartScraper(),
                EbayScraper("in"),
            ],
            "UK": [
                AmazonScraper("co.uk"),
                EbayScraper("co.uk"),
            ],
            "DE": [
                AmazonScraper("de"),
                EbayScraper("de"),
            ],
            "CA": [
                AmazonScraper("ca"),
                EbayScraper("ca"),
            ]
        }
    
    async def search_products(self, country: str, query: str) -> List[Dict]:
        """Search for products across multiple websites"""
        # Check cache first
        cached_results = self.cache.get(country, query)
        if cached_results:
            logger.info("Using cached results")
            return [product.to_dict() for product in cached_results]
        
        # Get scrapers for the country
        country_scrapers = self.scrapers.get(country.upper(), self.scrapers.get("US", []))
        if not country_scrapers:
            logger.warning(f"No scrapers available for country: {country}")
            return []
        
        # Create aiohttp session
        async with aiohttp.ClientSession() as session:
            # Execute searches in parallel
            tasks = [scraper.search(session, query) for scraper in country_scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and filter results
        all_products = []
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraper error: {result}")
        
        # Remove duplicates and sort by price
        unique_products = self._remove_duplicates(all_products)
        sorted_products = sorted(unique_products, key=lambda x: x.price)
        
        # Cache results
        self.cache.set(country, query, sorted_products)
        
        # Convert to dictionary format
        return [product.to_dict() for product in sorted_products]
    
    def _remove_duplicates(self, products: List[Product]) -> List[Product]:
        """Remove duplicate products based on similarity"""
        unique_products = []
        
        for product in products:
            is_duplicate = False
            for existing in unique_products:
                # Check if products are similar (same name and similar price)
                name_similarity = fuzz.ratio(product.product_name.lower(), existing.product_name.lower())
                price_diff = abs(product.price - existing.price) / max(product.price, existing.price)
                
                if name_similarity > 80 and price_diff < 0.1:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_products.append(product)
        
        return unique_products

async def main():
    """Main function for testing"""
    tool = PriceComparisonTool()
    
    # Test with sample input
    test_input = {
        "country": "US",
        "query": "iPhone 16 Pro, 128GB"
    }
    
    logger.info(f"Searching for: {test_input['query']} in {test_input['country']}")
    
    results = await tool.search_products(test_input["country"], test_input["query"])
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
