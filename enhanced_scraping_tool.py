#!/usr/bin/env python3
"""
Enhanced Price Comparison Tool with Real Web Scraping and Local HTML Parsing
Supports both live scraping and parsing local HTML files for testing/development
"""

import asyncio
import aiohttp
import json
import re
import time
import os
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from urllib.parse import urlencode, quote_plus, urlparse
from bs4 import BeautifulSoup
import logging
from fuzzywuzzy import fuzz
import hashlib
import pickle

# Handle missing dependencies gracefully for cloud deployment
try:
    from Levenshtein import distance as levenshtein_distance
    HAS_LEVENSHTEIN = True
except ImportError:
    # Fallback to basic string comparison
    HAS_LEVENSHTEIN = False
    def levenshtein_distance(s1, s2):
        """Simple fallback implementation"""
        return abs(len(s1) - len(s2))
from mcdm_ranker import MCDMRanker

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
    source: str  # Which website/scraper found this
    
    def to_dict(self) -> Dict:
        return {
            "link": self.link,
            "price": self.price,
            "currency": self.currency,
            "productName": self.product_name,
            "source": self.source
        }

class EnhancedBaseScraper:
    """Enhanced base class for website scrapers with local HTML support"""
    
    def __init__(self, name: str, base_url: str, local_html_file: Optional[str] = None):
        self.name = name
        self.base_url = base_url
        self.local_html_file = local_html_file
    
    async def search(self, session: aiohttp.ClientSession, query: str, use_local: bool = False) -> List[Product]:
        """Search for products on the website or parse local HTML"""
        try:
            if use_local and self.local_html_file:
                return self._parse_local_html(query)
            else:
                return await self._search_online(session, query)
        except Exception as e:
            logger.error(f"Error in {self.name} search: {e}")
            return []
    
    async def _search_online(self, session: aiohttp.ClientSession, query: str) -> List[Product]:
        """Search online"""
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
    
    def _parse_local_html(self, query: str) -> List[Product]:
        """Parse local HTML file"""
        if not self.local_html_file or not os.path.exists(self.local_html_file):
            logger.warning(f"Local HTML file not found: {self.local_html_file}")
            return []
        
        logger.info(f"Parsing local HTML: {self.local_html_file}")
        
        try:
            with open(self.local_html_file, 'r', encoding='utf-8') as f:
                html = f.read()
            return self._parse_results(html, query)
        except Exception as e:
            logger.error(f"Error reading local HTML file: {e}")
            return []
    
    def _build_search_url(self, query: str) -> str:
        """Build search URL for the query"""
        raise NotImplementedError
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        """Parse HTML and extract product information"""
        raise NotImplementedError
    
    def _clean_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text - Enhanced for Indian formats"""
        try:
            # Remove currency symbols and extra characters, but be more careful with dots
            # First remove currency symbols and spaces
            clean_price = re.sub(r'[₹Rs\s]', '', price_text)
            # Then remove any remaining non-digit characters except commas and decimal points
            clean_price = re.sub(r'[^\d.,]', '', clean_price)
            
            # Remove leading/trailing dots
            clean_price = clean_price.strip('.')
            
            if not clean_price:
                return None
            
            # Handle Indian price formats (e.g., 1,34,900 or 1,34,900.00)
            if ',' in clean_price:
                # Remove commas (Indian number formatting)
                clean_price = clean_price.replace(',', '')
            
            # Handle different decimal formats
            if '.' in clean_price:
                # Split by decimal point and take the main number
                parts = clean_price.split('.')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Valid decimal format
                    return float(clean_price)
                else:
                    # Multiple dots or invalid format, take only the integer part
                    return float(parts[0])
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

class EnhancedAmazonInScraper(EnhancedBaseScraper):
    """Enhanced Amazon India scraper with local HTML support"""
    
    def __init__(self, local_html_path: Optional[str] = None):
        local_file = os.path.join(local_html_path, "Amazon.in _ iphone 16pro max.html") if local_html_path else None
        super().__init__("Amazon.in", "https://www.amazon.in", local_file)
    
    def _build_search_url(self, query: str) -> str:
        # Use the URL pattern from your provided links
        clean_query = query.replace(' ', '+')
        return f"{self.base_url}/s?k={clean_query}&ref=nb_sb_noss"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers with the specific attribute
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        logger.info(f"Found {len(product_containers)} product containers on Amazon.in")
        
        for container in product_containers[:20]:  # Limit to top 20 results
            try:
                # Extract product title - Based on debug findings
                title_elem = container.find('a', class_=lambda x: x and 's-line-clamp-2' in x)
                
                if not title_elem:
                    # Alternative: look for h2 with embedded span text
                    h2_elem = container.find('h2', class_='a-size-medium')
                    if h2_elem:
                        span_elem = h2_elem.find('span')
                        if span_elem:
                            title_elem = h2_elem
                    
                if not title_elem:
                    continue
                
                # Get title text and link
                if title_elem.name == 'a':
                    product_name = title_elem.get_text(strip=True)
                    product_link = self._build_absolute_url(title_elem.get('href', ''))
                else:
                    # h2 element case
                    span_elem = title_elem.find('span')
                    if not span_elem:
                        continue
                    product_name = span_elem.get_text(strip=True)
                    # Find the link separately
                    link_elem = container.find('a', href=True)
                    if not link_elem:
                        continue
                    product_link = self._build_absolute_url(link_elem.get('href', ''))
                
                # Extract price - Use the most reliable selector first
                price_elem = container.find('span', class_='a-offscreen')
                
                if not price_elem:
                    # Try alternative price selectors
                    price_elem = container.find('span', class_='a-price-whole')
                    if price_elem:
                        # Get the full price including decimals if any
                        price_container = price_elem.find_parent('span', class_='a-price')
                        if price_container:
                            offscreen = price_container.find('span', class_='a-offscreen')
                            if offscreen:
                                price_elem = offscreen
                
                if not price_elem:
                    logger.debug(f"No price found for: {product_name}")
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    logger.debug(f"Could not parse price '{price_text}' for: {product_name}")
                    continue
                
                # Check relevance
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 30:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="INR",
                        product_name=product_name,
                        source=self.name
                    ))
                    logger.debug(f"Added: {product_name} - ₹{price}")
                    
            except Exception as e:
                logger.debug(f"Error parsing Amazon product: {e}")
                continue
        
        logger.info(f"Amazon.in: Found {len(products)} valid products")
        return products

class EnhancedEbayScraper(EnhancedBaseScraper):
    """Enhanced eBay scraper with local HTML support"""
    
    def __init__(self, domain: str = "com", local_html_path: Optional[str] = None):
        base_url = f"https://www.ebay.{domain}"
        local_file = os.path.join(local_html_path, "iPhone 16 Pro Max for sale _ eBay.html") if local_html_path else None
        super().__init__(f"eBay.{domain}", base_url, local_file)
        self.domain = domain
    
    def _build_search_url(self, query: str) -> str:
        # Use the URL pattern from your provided links
        params = {"_nkw": query, "_sacat": "0", "_from": "R40"}
        return f"{self.base_url}/sch/i.html?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', class_='s-item__wrapper')
        if not product_containers:
            product_containers = soup.find_all('div', class_='s-item')
        
        logger.info(f"Found {len(product_containers)} product containers on eBay.{self.domain}")
        
        for container in product_containers[:20]:  # Limit to top 20 results
            try:
                # TODO: Re-enable smarter sponsored filtering later
                # For now, disable to ensure eBay works
                
                # First check if this container has a valid eBay item link
                item_link = container.find('a', href=re.compile(r'/itm/\d+'))
                if not item_link:
                    continue  # Skip containers without actual product links
                
                # Product title - Use multiple fallback strategies
                title_elem = None
                product_name = ""
                
                # Strategy 1: span with role="heading" inside the link
                title_elem = item_link.find('span', attrs={'role': 'heading'})
                if title_elem:
                    product_name = title_elem.get_text(strip=True)
                
                # Strategy 2: Look for .s-item__title within the container
                if not product_name:
                    title_elem = container.find(class_='s-item__title')
                    if title_elem:
                        product_name = title_elem.get_text(strip=True)
                
                # Strategy 3: Look for span[role="heading"] anywhere in container
                if not product_name:
                    title_elem = container.find('span', attrs={'role': 'heading'})
                    if title_elem:
                        product_name = title_elem.get_text(strip=True)
                
                # Strategy 4: Use the link's title attribute or text
                if not product_name:
                    product_name = item_link.get('title', '') or item_link.get_text(strip=True)
                
                # Strategy 5: Look for any text within the link that looks like a title
                if not product_name or len(product_name) < 10:
                    for child in item_link.find_all(text=True):
                        text = child.strip()
                        if len(text) > 10 and not text.lower().startswith(('shop', 'sponsored')):
                            product_name = text
                            break
                
                if not product_name or len(product_name) < 5:
                    continue
                
                # Skip eBay promotional entries and generic content
                skip_patterns = [
                    "Shop on eBay", "Hot This Week", "Trending", 
                    "Sponsored", "Opens in a new window", "Opens in a new tab"
                ]
                
                # Skip if title contains promotional patterns
                if any(pattern.lower() in product_name.lower() for pattern in skip_patterns):
                    continue
                    
                # Skip very short or empty titles
                if len(product_name) < 10:
                    continue
                
                # Clean up common eBay prefixes but keep them for relevance
                original_name = product_name
                for pattern in ["New Listing", "Hot This Week", "Trending price"]:
                    if product_name.startswith(pattern):
                        product_name = product_name.replace(pattern, "").strip()
                
                # Skip if after cleaning, title is too short
                if len(product_name) < 10:
                    continue
                
                # Product link - Use the item link we already found
                product_link = item_link.get('href', '')
                if not product_link:
                    continue
                
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
                
                # Relevance check - be more lenient for eBay
                relevance_score = fuzz.partial_ratio(query.lower(), product_name.lower())
                if relevance_score > 25 or any(word.lower() in product_name.lower() for word in query.lower().split() if len(word) > 2):
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency=currency,
                        product_name=product_name,
                        source=self.name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing eBay product: {e}")
                continue
        
        logger.info(f"eBay.{self.domain}: Found {len(products)} valid products")
        return products

class EnhancedFlipkartScraper(EnhancedBaseScraper):
    """Enhanced Flipkart scraper with local HTML support"""
    
    def __init__(self, local_html_path: Optional[str] = None):
        local_file = os.path.join(local_html_path, "Iphone 16 Pro Max- Buy Products Online at Best Price in India - All Categories _ Flipkart.com.html") if local_html_path else None
        super().__init__("Flipkart", "https://www.flipkart.com", local_file)
    
    def _build_search_url(self, query: str) -> str:
        # Use the URL pattern from your provided links
        params = {
            "q": query,
            "otracker": "search",
            "otracker1": "search",
            "marketplace": "FLIPKART",
            "as-show": "on",
            "as": "off"
        }
        return f"{self.base_url}/search?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Flipkart uses specific class structures - Updated based on actual HTML
        product_containers = soup.find_all('div', class_='yKfJKb')
        if not product_containers:
            # Alternative container patterns
            product_containers = soup.find_all('div', class_='_1AtVbE')
        if not product_containers:
            product_containers = soup.find_all('div', class_='_13oc-S')
        if not product_containers:
            product_containers = soup.find_all('div', attrs={'data-id': True})
        
        logger.info(f"Found {len(product_containers)} product containers on Flipkart")
        
        for container in product_containers[:10]:  # Limit to top 10 results
            try:
                # Product title - Updated to match actual HTML structure
                title_elem = container.find('div', class_='KzDlHZ')
                if not title_elem:
                    # Try alternative selectors
                    title_elem = container.find('div', class_='_4rR01T')
                if not title_elem:
                    title_elem = container.find('a', class_='_1fQZEK')
                if not title_elem:
                    title_elem = container.find('div', class_='_2WkVRV')
                if not title_elem:
                    title_elem = container.find('a', title=True)
                
                if not title_elem:
                    continue
                
                product_name = title_elem.get('title', '') or title_elem.get_text(strip=True)
                
                # Product link - first check in container, then in parent containers
                link_elem = container.find('a', href=True)
                product_link = ""
                
                if link_elem:
                    product_link = self._build_absolute_url(link_elem.get('href', ''))
                else:
                    # Check parent containers for links (Flipkart structure)
                    current = container
                    for level in range(3):  # Check up to 3 levels up
                        if current.parent:
                            current = current.parent
                            if current.name == 'a' and current.get('href'):
                                product_link = self._build_absolute_url(current.get('href', ''))
                                break
                            parent_a = current.find('a', href=True, recursive=False)  # Direct child only
                            if parent_a:
                                product_link = self._build_absolute_url(parent_a.get('href', ''))
                                break
                
                if not product_link:
                    continue
                
                # Price - Updated selectors based on actual HTML structure
                price_elem = container.find('div', class_='Nx9bqj')  # Common Flipkart price class
                if not price_elem:
                    price_elem = container.find('div', class_='_30jeq3')
                if not price_elem:
                    price_elem = container.find('div', class_='_25b18c')
                if not price_elem:
                    price_elem = container.find('div', class_='_1_WHN1')
                if not price_elem:
                    # Look for any element with price-like text
                    price_elem = container.find(text=re.compile(r'₹\s*[\d,]+'))
                    if price_elem:
                        price_elem = price_elem.parent
                
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    continue
                
                # Relevance check
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 30:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="INR",
                        product_name=product_name,
                        source=self.name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Flipkart product: {e}")
                continue
        
        logger.info(f"Flipkart: Found {len(products)} valid products")
        return products

class EnhancedWalmartScraper(EnhancedBaseScraper):
    """Enhanced Walmart scraper with local HTML support"""
    
    def __init__(self, local_html_path: Optional[str] = None):
        local_file = os.path.join(local_html_path, "iphone 16 pro max - Walmart.com.html") if local_html_path else None
        super().__init__("Walmart", "https://www.walmart.com", local_file)
    
    def _build_search_url(self, query: str) -> str:
        # Use the URL pattern from your provided links
        params = {"q": query, "typeahead": query.replace(' ', '%20')}
        return f"{self.base_url}/search?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        product_containers = soup.find_all('div', attrs={'data-item-id': True})
        if not product_containers:
            product_containers = soup.find_all('div', class_='mb0')
        if not product_containers:
            # Look for broader patterns
            product_containers = soup.find_all('div', class_=re.compile(r'.*product.*|.*item.*'))
        
        logger.info(f"Found {len(product_containers)} product containers on Walmart")
        
        for container in product_containers[:10]:  # Limit to top 10 results
            try:
                # Product title
                title_elem = container.find('span', attrs={'data-automation-id': 'product-title'})
                if not title_elem:
                    title_elem = container.find('a', attrs={'data-testid': 'product-title'})
                if not title_elem:
                    title_elem = container.find('h3')
                if not title_elem:
                    title_elem = container.find('a', title=True)
                
                if not title_elem:
                    continue
                
                product_name = title_elem.get('title', '') or title_elem.get_text(strip=True)
                
                # Product link
                link_elem = container.find('a', href=True)
                if not link_elem:
                    continue
                product_link = self._build_absolute_url(link_elem.get('href', ''))
                
                # Price
                price_elem = container.find('span', attrs={'itemprop': 'price'})
                if not price_elem:
                    price_elem = container.find('div', class_='lh-copy')
                if not price_elem:
                    # Look for any element with price-like text
                    price_elem = container.find(text=re.compile(r'\$\s*\d+'))
                    if price_elem:
                        price_elem = price_elem.parent
                
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                
                if price is None:
                    continue
                
                # Relevance check
                if fuzz.partial_ratio(query.lower(), product_name.lower()) > 30:
                    products.append(Product(
                        link=product_link,
                        price=price,
                        currency="USD",
                        product_name=product_name,
                        source=self.name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Walmart product: {e}")
                continue
        
        logger.info(f"Walmart: Found {len(products)} valid products")
        return products

class EnhancedSnapdealScraper(EnhancedBaseScraper):
    """Enhanced Snapdeal scraper with local HTML support"""
    
    def __init__(self, local_html_path: Optional[str] = None):
        local_file = os.path.join(local_html_path, "Snapdeal.com - Online shopping India- Discounts - shop Online Perfumes, Watches, sunglasses etc.html") if local_html_path else None
        super().__init__("Snapdeal", "https://www.snapdeal.com", local_file)
    
    def _build_search_url(self, query: str) -> str:
        # Use the URL pattern from your provided links
        params = {
            "keyword": query,
            "santizedKeyword": "",
            "catId": "",
            "categoryId": "0",
            "suggested": "false",
            "vertical": "",
            "noOfResults": "20",
            "searchState": "",
            "clickSrc": "go_header",
            "sort": "rlvncy"
        }
        return f"{self.base_url}/search?{urlencode(params)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product links
        product_links = soup.find_all('a', href=re.compile(r'/product/'))
        
        if not product_links:
            logger.info("No product links found on Snapdeal")
            return products
        
        logger.info(f"Found {len(product_links)} product containers on Snapdeal")
        
        processed_links = set()
        
        for i, link in enumerate(product_links[:15]):  # Process more links
            try:
                href = link.get('href', '')
                if href in processed_links or not href:
                    continue
                processed_links.add(href)
                
                # Get product name with multiple strategies
                product_name = ""
                
                # Strategy 1: title attribute
                product_name = link.get('title', '').strip()
                if product_name and len(product_name) > 10:
                    pass  # Got name from title
                
                # Strategy 2: link text (but skip generic ones and clean prices)
                if not product_name:
                    link_text = link.get_text(strip=True)
                    if link_text and len(link_text) > 5 and not link_text.lower().startswith(('quick view', '...', 'view')):
                        # Remove price information from link text
                        clean_text = re.sub(r'Rs\.?\s*\d+[,\d]*|₹\s*\d+[,\d]*|\d+%\s*Off', '', link_text)
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                        if len(clean_text) > 10:
                            product_name = clean_text
                
                # Strategy 3: Look in grandparent structure (where the full product data is)
                if not product_name or len(product_name) < 15:
                    grandparent = link.find_parent()
                    if grandparent:
                        grandparent = grandparent.find_parent()
                        if grandparent:
                            # Find all text elements in grandparent
                            all_texts = grandparent.find_all(string=True)
                            for text_elem in all_texts:
                                text = text_elem.strip()
                                # Look for text that looks like a product name (long, contains relevant words)
                                if (len(text) > 20 and 
                                    not text.lower().startswith(('quick view', 'rs.', '₹', 'left!')) and
                                    not re.match(r'^\d+%?\s*(off|left)', text.lower()) and
                                    ('iphone' in text.lower() or 'case' in text.lower() or 'cover' in text.lower() or len(text) > 30)):
                                    product_name = text
                                    break
                
                if not product_name or len(product_name) < 10:
                    continue
                
                # Look for price with multiple strategies
                price_text = ""
                
                # Strategy 1: In link text
                link_text = link.get_text()
                price_match = re.search(r'Rs\.?\s*(\d+(?:,\d+)*)|₹\s*(\d+(?:,\d+)*)', link_text)
                if price_match:
                    price_text = price_match.group(0)
                
                # Strategy 2: In parent elements
                if not price_text:
                    parent = link.find_parent()
                    if parent:
                        parent_text = parent.get_text()
                        price_match = re.search(r'Rs\.?\s*(\d+(?:,\d+)*)|₹\s*(\d+(?:,\d+)*)', parent_text)
                        if price_match:
                            price_text = price_match.group(0)
                
                # Strategy 3: Look in grandparent or wider area
                if not price_text:
                    grandparent = link.find_parent()
                    if grandparent:
                        grandparent = grandparent.find_parent()
                        if grandparent:
                            gp_text = grandparent.get_text()
                            price_match = re.search(r'Rs\.?\s*(\d+(?:,\d+)*)|₹\s*(\d+(?:,\d+)*)', gp_text)
                            if price_match:
                                price_text = price_match.group(0)
                
                if not price_text:
                    continue
                
                # Clean and validate price
                price = self._clean_price(price_text)
                if not price:
                    continue
                
                # Skip irrelevant products (very lenient check)
                relevance_score = fuzz.partial_ratio(query.lower(), product_name.lower())
                query_words = [w.lower() for w in query.split() if len(w) > 2]
                has_keyword = any(word in product_name.lower() for word in query_words)
                
                if relevance_score > 15 or has_keyword:
                    products.append(Product(
                        link=self._build_absolute_url(href),
                        price=price,
                        currency="INR",
                        product_name=product_name,
                        source=self.name
                    ))
                    
            except Exception as e:
                logger.debug(f"Error parsing Snapdeal product: {e}")
                continue
        
        logger.info(f"Snapdeal: Found {len(products)} valid products")
        return products
    
    def _elements_are_related(self, elem1, elem2, max_depth=5):
        """Check if two elements are related within max_depth levels"""
        try:
            # Find common ancestor
            parents1 = []
            current = elem1
            for _ in range(max_depth):
                if current.parent:
                    parents1.append(current.parent)
                    current = current.parent
                else:
                    break
            
            current = elem2
            for _ in range(max_depth):
                if current.parent:
                    if current.parent in parents1:
                        return True
                    current = current.parent
                else:
                    break
            
            return False
        except:
            return False

class EnhancedShopsyScraper(EnhancedBaseScraper):
    """Enhanced Shopsy scraper with local HTML support"""
    
    def __init__(self, local_html_path: Optional[str] = None):
        local_file = os.path.join(local_html_path, "Iphone 16 Pro Max- Buy Products Online at Best Price in India - All Categories _ shopsy.in.html") if local_html_path else None
        super().__init__("Shopsy", "https://www.shopsy.in", local_file)
    
    def _build_search_url(self, query: str) -> str:
        # Use the URL pattern from your provided links
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
                            
                            for product_info in product_list[:10]:  # Limit to first 10
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
                                    if fuzz.partial_ratio(query.lower(), name.lower()) > 30:
                                        products.append(Product(
                                            link=product_url,
                                            price=float(price),
                                            currency="INR",
                                            product_name=name,
                                            source=self.name
                                        ))
                                        
                                except Exception as e:
                                    logger.debug(f"Error parsing Shopsy product: {e}")
                                    continue
                                    
                except json.JSONDecodeError:
                    continue
        
        # Fallback: Try to extract from HTML structure
        if not products:
            product_containers = soup.find_all('div', class_=re.compile(r'css-175oi2r.*product|item'))
            
            for container in product_containers[:10]:
                try:
                    # Look for product name (multiple possible selectors)
                    name_elem = container.find('div', class_='bkNEtl')  # Based on HTML sample
                    if not name_elem:
                        name_elem = container.find(text=re.compile(r'iPhone|Apple|Samsung', re.I))
                        if name_elem:
                            name_elem = name_elem.parent
                    
                    if not name_elem:
                        continue
                        
                    product_name = name_elem.get_text(strip=True)
                    if not product_name:
                        continue
                    
                    # Look for price
                    price_elem = container.find(text=re.compile(r'₹\d+'))
                    if not price_elem:
                        # Try other price selectors
                        price_spans = container.find_all('div', text=re.compile(r'\d+'))
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
                    if fuzz.partial_ratio(query.lower(), product_name.lower()) > 30:
                        products.append(Product(
                            link=product_link,
                            price=price,
                            currency="INR",
                            product_name=product_name,
                            source=self.name
                        ))
                        
                except Exception as e:
                    logger.debug(f"Error parsing Shopsy container: {e}")
                    continue
        
        logger.info(f"Shopsy: Found {len(products)} valid products")
        return products

class EnhancedPriceComparisonTool:
    """Enhanced price comparison tool supporting both online and local HTML parsing"""
    
    def __init__(self, local_html_path: Optional[str] = None):
        self.local_html_path = local_html_path
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> Dict[str, List[EnhancedBaseScraper]]:
        """Initialize scrapers for different countries"""
        return {
            "US": [
                EnhancedEbayScraper("com", self.local_html_path),
                EnhancedWalmartScraper(self.local_html_path),
            ],
            "IN": [
                EnhancedAmazonInScraper(self.local_html_path),
                EnhancedFlipkartScraper(self.local_html_path),
                EnhancedEbayScraper("in", self.local_html_path),
                EnhancedSnapdealScraper(self.local_html_path),
                EnhancedShopsyScraper(self.local_html_path),
            ],
            "UK": [
                EnhancedEbayScraper("co.uk", self.local_html_path),
            ],
            "DE": [
                EnhancedEbayScraper("de", self.local_html_path),
            ],
            "CA": [
                EnhancedEbayScraper("ca", self.local_html_path),
            ]
        }
    
    async def search_products(self, country: str, query: str, use_local: bool = False) -> List[Dict]:
        """Search for products across multiple websites"""
        # Get scrapers for the country
        country_scrapers = self.scrapers.get(country.upper(), self.scrapers.get("US", []))
        if not country_scrapers:
            logger.warning(f"No scrapers available for country: {country}")
            return []
        
        # Create aiohttp session with SSL verification disabled for testing
        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Execute searches in parallel
            tasks = [scraper.search(session, query, use_local) for scraper in country_scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and filter results
        all_products = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_products.extend(result)
                logger.info(f"Scraper {country_scrapers[i].name}: Found {len(result)} products")
            elif isinstance(result, Exception):
                logger.error(f"Scraper {i+1} error: {result}")
        
        # Remove duplicates and apply MCDM ranking
        unique_products = self._remove_duplicates(all_products)
        
        # Apply MCDM ranking for intelligent search relevance + price optimization
        mcdm_ranker = MCDMRanker()
        product_dicts = [product.to_dict() for product in unique_products]
        ranked_products = mcdm_ranker.calculate_mcdm_scores(product_dicts, query)
        
        # Filter out low relevance products
        filtered_products = mcdm_ranker.filter_low_relevance(ranked_products, min_relevance=0.2)
        
        logger.info(f"Total unique products found: {len(unique_products)}")
        logger.info(f"After MCDM ranking and filtering: {len(filtered_products)}")
        
        return filtered_products
    
    def _remove_duplicates(self, products: List[Product]) -> List[Product]:
        """Remove duplicate products based on similarity - Less aggressive to preserve diverse results"""
        unique_products = []
        
        for product in products:
            is_duplicate = False
            for existing in unique_products:
                # Only consider exact or very close matches as duplicates
                name_similarity = fuzz.ratio(product.product_name.lower(), existing.product_name.lower())
                
                # More strict criteria for duplicates to preserve diverse results
                if product.currency == existing.currency:
                    price_diff = abs(product.price - existing.price) / max(product.price, existing.price, 1)
                    # Increased thresholds: only remove if very similar name AND very similar price
                    if name_similarity > 90 and price_diff < 0.05:
                        is_duplicate = True
                        break
                elif name_similarity > 95:
                    # Only remove if almost identical names across currencies
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_products.append(product)
        
        return unique_products

async def main():
    """Main function for testing enhanced scraping"""
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_samples_path = os.path.join(current_dir, "webpages_samples")
    
    # Create tool instance
    tool = EnhancedPriceComparisonTool(html_samples_path)
    
    # Test cases
    test_cases = [
        {"country": "IN", "query": "iPhone 16 Pro Max", "use_local": True},
        {"country": "IN", "query": "iPhone 16 Pro Max", "use_local": False},
        {"country": "US", "query": "iPhone 16 Pro Max", "use_local": True},
    ]
    
    for test_case in test_cases:
        logger.info(f"\n{'='*80}")
        mode = "LOCAL HTML" if test_case['use_local'] else "ONLINE SCRAPING"
        logger.info(f"Testing {mode}: {test_case['query']} in {test_case['country']}")
        logger.info(f"{'='*80}")
        
        try:
            results = await tool.search_products(
                test_case["country"], 
                test_case["query"], 
                test_case['use_local']
            )
            
            if results:
                print(f"Found {len(results)} products:")
                for i, product in enumerate(results, 1):
                    print(f"{i}. {product['productName'][:60]}...")
                    print(f"   Price: {product['currency']} {product['price']}")
                    print(f"   Source: {product['source']}")
                    print(f"   Link: {product['link'][:80]}...")
                    print()
            else:
                print("No products found")
                
        except Exception as e:
            logger.error(f"Error during search: {e}")
        
        # Small delay between tests
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
