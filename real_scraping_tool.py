#!/usr/bin/env python3
"""
Updated Price Comparison Tool with Real Web Scraping
Based on actual HTML structure from the provided sample pages
"""

import asyncio
import aiohttp
import json
import re
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlencode, quote_plus, urlparse
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
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
    
    async def search(self, session: aiohttp.ClientSession, query: str) -> List[Product]:
        """Search for products on the website"""
        try:
            search_url = self._build_search_url(query)
            headers = self._get_headers()
            
            logger.info(f"Scraping {self.name}: {search_url}")
            
            async with session.get(search_url, headers=headers, timeout=15) as response:
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        """Parse HTML and extract product information"""
        raise NotImplementedError
    
    def _clean_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        try:
            # Remove currency symbols and commas
            clean_price = re.sub(r'[^\d.,]', '', price_text)
            clean_price = clean_price.replace(',', '')
            
            # Handle different decimal formats
            if '.' in clean_price:
                return float(clean_price)
            else:
                return float(clean_price)
        except:
            return None
    
    def _build_absolute_url(self, relative_url: str) -> str:
        """Convert relative URL to absolute URL"""
        if relative_url.startswith('http'):
            return relative_url
        elif relative_url.startswith('//'):
            return 'https:' + relative_url
        elif relative_url.startswith('/'):
            return self.base_url + relative_url
        else:
            return self.base_url + '/' + relative_url

class AmazonInScraper(BaseScraper):
    """Amazon India scraper implementation"""
    
    def __init__(self):
        super().__init__("Amazon.in", "https://www.amazon.in")
    
    def _build_search_url(self, query: str) -> str:
        # Clean up the query to match expected format
        clean_query = query.replace(' ', '+')
        return f"{self.base_url}/s?k={clean_query}&ref=nb_sb_noss"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers with the specific attribute
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        logger.info(f"Found {len(product_containers)} product containers on Amazon.in")
        
        for container in product_containers[:8]:  # Limit to top 8 results
            try:
                # Extract product title
                title_elem = container.find('h2')
                if not title_elem:
                    continue
                
                title_link = title_elem.find('a')
                if not title_link:
                    continue
                
                product_name = title_link.get_text(strip=True)
                product_link = self._build_absolute_url(title_link.get('href', ''))
                
                # Extract price - look for the price container
                price_elem = container.find('span', class_='a-price-whole')
                if not price_elem:
                    # Try alternative price selectors
                    price_elem = container.find('span', class_='a-price')
                    if price_elem:
                        price_elem = price_elem.find('span', class_='a-offscreen')
                
                if not price_elem:
                    logger.debug(f"No price found for: {product_name}")
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    logger.debug(f"Could not parse price '{price_text}' for: {product_name}")
                    continue
                
                # Check relevance
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 40:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="INR",
                        product_name=product_name
                    ))
                    logger.debug(f"Added: {product_name} - ₹{price}")
                    
            except Exception as e:
                logger.debug(f"Error parsing Amazon product: {e}")
                continue
        
        logger.info(f"Amazon.in: Found {len(products)} valid products")
        return products

class EbayScraper(BaseScraper):
    """eBay scraper implementation"""
    
    def __init__(self, domain: str = "com"):
        base_url = f"https://www.ebay.{domain}"
        super().__init__(f"eBay.{domain}", base_url)
        self.domain = domain
    
    def _build_search_url(self, query: str) -> str:
        params = {"_nkw": query, "_sacat": "0"}
        return f"{self.base_url}/sch/i.html?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', class_='s-item__wrapper')
        if not product_containers:
            product_containers = soup.find_all('div', class_='s-item')
        
        logger.info(f"Found {len(product_containers)} product containers on eBay.{self.domain}")
        
        for container in product_containers[:8]:  # Limit to top 8 results
            try:
                # Product title
                title_elem = container.find('h3', class_='s-item__title')
                if not title_elem:
                    title_elem = container.find('a', class_='s-item__link')
                
                if not title_elem:
                    continue
                
                product_name = title_elem.get_text(strip=True)
                
                # Product link
                link_elem = container.find('a', class_='s-item__link')
                if not link_elem:
                    continue
                product_link = link_elem.get('href', '')
                
                # Price
                price_elem = container.find('span', class_='s-item__price')
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    continue
                
                # Currency detection
                currency = "USD" if self.domain == "com" else "INR" if self.domain == "in" else "USD"
                if "₹" in price_text:
                    currency = "INR"
                elif "$" in price_text:
                    currency = "USD"
                elif "£" in price_text:
                    currency = "GBP"
                
                # Relevance check
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 40:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency=currency,
                        product_name=product_name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing eBay product: {e}")
                continue
        
        logger.info(f"eBay.{self.domain}: Found {len(products)} valid products")
        return products

class FlipkartScraper(BaseScraper):
    """Flipkart scraper implementation"""
    
    def __init__(self):
        super().__init__("Flipkart", "https://www.flipkart.com")
    
    def _build_search_url(self, query: str) -> str:
        params = {"q": query}
        return f"{self.base_url}/search?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers - Flipkart uses different selectors
        product_containers = soup.find_all('div', class_='_1AtVbE')
        if not product_containers:
            product_containers = soup.find_all('div', class_='_13oc-S')
        if not product_containers:
            product_containers = soup.find_all('div', attrs={'data-id': True})
        
        logger.info(f"Found {len(product_containers)} product containers on Flipkart")
        
        for container in product_containers[:8]:  # Limit to top 8 results
            try:
                # Product title
                title_elem = container.find('div', class_='_4rR01T')
                if not title_elem:
                    title_elem = container.find('a', class_='_1fQZEK')
                if not title_elem:
                    title_elem = container.find('div', class_='_2WkVRV')
                
                if not title_elem:
                    continue
                
                product_name = title_elem.get_text(strip=True)
                
                # Product link
                link_elem = container.find('a')
                if not link_elem:
                    continue
                product_link = self._build_absolute_url(link_elem.get('href', ''))
                
                # Price
                price_elem = container.find('div', class_='_30jeq3')
                if not price_elem:
                    price_elem = container.find('div', class_='_25b18c')
                if not price_elem:
                    price_elem = container.find('div', class_='_1_WHN1')
                
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    continue
                
                # Relevance check
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 40:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="INR",
                        product_name=product_name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Flipkart product: {e}")
                continue
        
        logger.info(f"Flipkart: Found {len(products)} valid products")
        return products

class WalmartScraper(BaseScraper):
    """Walmart scraper implementation"""
    
    def __init__(self):
        super().__init__("Walmart", "https://www.walmart.com")
    
    def _build_search_url(self, query: str) -> str:
        params = {"q": query}
        return f"{self.base_url}/search?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', attrs={'data-item-id': True})
        if not product_containers:
            product_containers = soup.find_all('div', class_='mb0')
        
        logger.info(f"Found {len(product_containers)} product containers on Walmart")
        
        for container in product_containers[:8]:  # Limit to top 8 results
            try:
                # Product title
                title_elem = container.find('span', attrs={'data-automation-id': 'product-title'})
                if not title_elem:
                    title_elem = container.find('a', attrs={'data-testid': 'product-title'})
                
                if not title_elem:
                    continue
                
                product_name = title_elem.get_text(strip=True)
                
                # Product link
                link_elem = container.find('a')
                if not link_elem:
                    continue
                product_link = self._build_absolute_url(link_elem.get('href', ''))
                
                # Price
                price_elem = container.find('span', attrs={'itemprop': 'price'})
                if not price_elem:
                    price_elem = container.find('div', class_='lh-copy')
                
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    continue
                
                # Relevance check
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 40:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="USD",
                        product_name=product_name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Walmart product: {e}")
                continue
        
        logger.info(f"Walmart: Found {len(products)} valid products")
        return products

class SnapdealScraper(BaseScraper):
    """Scraper for Snapdeal India"""
    
    def __init__(self):
        super().__init__("Snapdeal", "https://www.snapdeal.com")
    
    def _build_search_url(self, query: str) -> str:
        params = {"keyword": query, "noOfResults": "20"}
        return f"{self.base_url}/search?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Try to find products in the product grid
        product_containers = soup.find_all('div', class_=re.compile(r'product-tuple|favDp|product-item'))
        
        if not product_containers:
            # Alternative selectors
            product_containers = soup.find_all('div', {'data-js': 'product-card'})
        
        logger.info(f"Found {len(product_containers)} product containers on Snapdeal")
        
        for container in product_containers[:8]:  # Limit to top 8 results
            try:
                # Look for product name
                name_elem = container.find('p', class_='product-title')
                if not name_elem:
                    name_elem = container.find('a', title=True)
                if not name_elem:
                    name_elem = container.find('div', class_='product-desc-rating')
                
                if not name_elem:
                    continue
                    
                product_name = name_elem.get('title', '') or name_elem.get_text(strip=True)
                if not product_name:
                    continue
                
                # Look for price
                price_elem = container.find('span', class_=re.compile(r'lfloat.*product-price|price'))
                if not price_elem:
                    price_elem = container.find('div', class_='product-price')
                if not price_elem:
                    price_elem = container.find('span', string=re.compile(r'₹|Rs'))
                    
                if not price_elem:
                    continue
                    
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    continue
                
                # Look for link
                link_elem = container.find('a', href=True)
                product_link = "https://www.snapdeal.com"
                if link_elem and link_elem.get('href'):
                    product_link = self._build_absolute_url(link_elem['href'])
                
                # Relevance check
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 40:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="INR",
                        product_name=product_name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Snapdeal product: {e}")
                continue
        
        # Fallback: Look for hidden input data
        if not products:
            data_inputs = soup.find_all('input', {'class': 'dp-info-collect'})
            for data_input in data_inputs:
                try:
                    data_value = data_input.get('value', '')
                    if data_value and data_value.startswith('['):
                        import ast
                        product_data = ast.literal_eval(data_value)
                        for item in product_data[:5]:  # Limit to first 5
                            if isinstance(item, dict):
                                name = item.get('k4', '').strip()
                                price_text = item.get('k5', '0')
                                link_data = item.get('k2', '')
                                
                                if name and price_text:
                                    price = self._clean_price(str(price_text))
                                    if price is not None and price > 0:
                                        product_url = f"https://www.snapdeal.com/{link_data}" if link_data else "https://www.snapdeal.com"
                                        if fuzz.partial_ratio(query.lower(), name.lower()) > 40:
                                            products.append(Product(
                                                link=product_url,
                                                price=price,
                                                currency="INR",
                                                product_name=name
                                            ))
                except Exception as e:
                    logger.debug(f"Error parsing Snapdeal data input: {e}")
                    continue
        
        logger.info(f"Snapdeal: Found {len(products)} valid products")
        return products

class ShopsyScraper(BaseScraper):
    """Scraper for Shopsy (Flipkart's social commerce platform)"""
    
    def __init__(self):
        super().__init__("Shopsy", "https://www.shopsy.in")
    
    def _build_search_url(self, query: str) -> str:
        params = {"q": query}
        return f"{self.base_url}/search?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Shopsy uses React and loads data via JSON in script tags
        script_tags = soup.find_all('script', {'id': '__NEXT_DATA__'})
        
        for script in script_tags:
            if script.string:
                try:
                    data = json.loads(script.string)
                    
                    # Navigate through Shopsy's data structure
                    page_props = data.get('props', {}).get('pageProps', {})
                    initial_state = page_props.get('initialState', {})
                    page_data = initial_state.get('pageData', {})
                    response_data = page_data.get('RESPONSE', {})
                    page_data_inner = response_data.get('pageData', {})
                    slots = page_data_inner.get('slots', [])
                    
                    for slot in slots:
                        widget = slot.get('widget', {})
                        if widget.get('type') == 'PRODUCT_SUMMARY':
                            widget_data = widget.get('data', {})
                            product_list = widget_data.get('products', [])
                            
                            for product_info in product_list[:8]:  # Limit to first 8
                                try:
                                    product_data = product_info.get('productInfo', {}).get('value', {})
                                    
                                    # Extract product name
                                    titles = product_data.get('titles', {})
                                    name = titles.get('title', '') or titles.get('newTitle', '')
                                    if not name:
                                        continue
                                    
                                    # Extract price
                                    pricing = product_data.get('pricing', {})
                                    final_price = pricing.get('finalPrice', {})
                                    price = final_price.get('value', 0)
                                    
                                    if price <= 0:
                                        continue
                                    
                                    # Build product URL
                                    base_url = product_data.get('baseUrl', '')
                                    product_url = f"https://www.shopsy.in{base_url}" if base_url else "https://www.shopsy.in"
                                    
                                    # Relevance check
                                    if fuzz.partial_ratio(query.lower(), name.lower()) > 40:
                                        products.append(Product(
                                            link=product_url,
                                            price=float(price),
                                            currency="INR",
                                            product_name=name
                                        ))
                                        
                                except Exception as e:
                                    logger.debug(f"Error parsing Shopsy product: {e}")
                                    continue
                                    
                except json.JSONDecodeError:
                    continue
        
        # Fallback: Try to extract from HTML structure
        if not products:
            product_containers = soup.find_all('div', class_=re.compile(r'css-175oi2r.*product|item'))
            
            for container in product_containers[:8]:
                try:
                    # Look for product name (multiple possible selectors)
                    name_elem = container.find('div', class_='bkNEtl')  # Based on HTML sample
                    if not name_elem:
                        name_elem = container.find('div', string=re.compile(r'iPhone|Apple|Samsung'))
                    if not name_elem:
                        name_elem = container.find('span', string=re.compile(r'iPhone|Apple|Samsung'))
                    
                    if not name_elem:
                        continue
                        
                    product_name = name_elem.get_text(strip=True)
                    if not product_name:
                        continue
                    
                    # Look for price
                    price_elem = container.find('div', string=re.compile(r'₹\d+'))
                    if not price_elem:
                        # Try other price selectors
                        price_spans = container.find_all('div', string=re.compile(r'\d+'))
                        for span in price_spans:
                            text = span.get_text()
                            if '₹' in text or (text.replace(',', '').isdigit() and len(text) > 2):
                                price_elem = span
                                break
                                
                    if not price_elem:
                        continue
                        
                    price_text = price_elem.get_text(strip=True)
                    price = self._clean_price(price_text)
                    
                    if price is None:
                        continue
                    
                    # Look for link
                    link_elem = container.find('a', href=True)
                    product_link = "https://www.shopsy.in"
                    if link_elem and link_elem.get('href'):
                        product_link = self._build_absolute_url(link_elem['href'])
                    
                    # Relevance check
                    if fuzz.partial_ratio(query.lower(), product_name.lower()) > 40:
                        products.append(Product(
                            link=product_link,
                            price=price,
                            currency="INR",
                            product_name=product_name
                        ))
                        
                except Exception as e:
                    logger.debug(f"Error parsing Shopsy container: {e}")
                    continue
        
        logger.info(f"Shopsy: Found {len(products)} valid products")
        return products

class RealPriceComparisonTool:
    """Main price comparison tool with real web scraping"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> Dict[str, List[BaseScraper]]:
        """Initialize scrapers for different countries"""
        return {
            "US": [
                EbayScraper("com"),
                WalmartScraper(),
            ],
            "IN": [
                AmazonInScraper(),
                FlipkartScraper(),
                EbayScraper("in"),
                SnapdealScraper(),
                ShopsyScraper(),
            ],
            "UK": [
                EbayScraper("co.uk"),
            ],
            "DE": [
                EbayScraper("de"),
            ],
            "CA": [
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
        
        # Create aiohttp session with SSL disabled for testing
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Execute searches in parallel
            tasks = [scraper.search(session, query) for scraper in country_scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and filter results
        all_products = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_products.extend(result)
                logger.info(f"Scraper {i+1}: Found {len(result)} products")
            elif isinstance(result, Exception):
                logger.error(f"Scraper {i+1} error: {result}")
        
        # Remove duplicates and sort by price
        unique_products = self._remove_duplicates(all_products)
        sorted_products = sorted(unique_products, key=lambda x: x.price)
        
        logger.info(f"Total unique products found: {len(sorted_products)}")
        
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
                
                # For price comparison, normalize to same currency if possible
                if product.currency == existing.currency:
                    price_diff = abs(product.price - existing.price) / max(product.price, existing.price, 1)
                    if name_similarity > 75 and price_diff < 0.15:
                        is_duplicate = True
                        break
                elif name_similarity > 85:
                    # Very similar names, likely duplicate even with different currency
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_products.append(product)
        
        return unique_products

async def main():
    """Main function for testing real scraping"""
    tool = RealPriceComparisonTool()
    
    # Test cases
    test_cases = [
        {"country": "IN", "query": "iPhone 16 Pro Max"},
        {"country": "US", "query": "iPhone 16 Pro Max"},
        {"country": "IN", "query": "Samsung Galaxy S24"},
    ]
    
    for test_case in test_cases:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing real scraping: {test_case['query']} in {test_case['country']}")
        logger.info(f"{'='*60}")
        
        try:
            results = await tool.search_products(test_case["country"], test_case["query"])
            
            if results:
                print(f"Found {len(results)} products:")
                for i, product in enumerate(results, 1):
                    print(f"{i}. {product['productName']}")
                    print(f"   Price: {product['currency']} {product['price']}")
                    print(f"   Link: {product['link'][:80]}...")
                    print()
            else:
                print("No products found")
                
        except Exception as e:
            logger.error(f"Error during search: {e}")
        
        # Small delay between tests
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
