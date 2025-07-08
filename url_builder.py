#!/usr/bin/env python3
"""
URL Builder and Search Tool for Enhanced Price Comparison
Handles the specific URL patterns from the provided search links
"""

from urllib.parse import urlencode, quote_plus
from typing import Dict, List, Any
import re

class SearchURLBuilder:
    """Builds search URLs that match the patterns from the provided links"""
    
    @staticmethod
    def amazon_in_url(query: str) -> str:
        """Build Amazon India search URL matching the provided pattern"""
        # Original: https://www.amazon.in/s?k=iphone+16pro+max&crid=7HN8Y295XVCV&sprefix=iphone+%2Caps%2C791&ref=nb_sb_ss_mvt-t11-ranker_1_7
        clean_query = query.replace(' ', '+')
        
        # Generate a realistic sprefix (first part of query + some extra)
        query_parts = query.lower().split()
        sprefix = query_parts[0] if query_parts else query.lower()[:6]
        
        params = {
            'k': clean_query,
            'crid': '7HN8Y295XVCV',  # This can be static or generated
            'sprefix': f"{sprefix}+",
            'ref': 'nb_sb_ss_mvt-t11-ranker_1_7'
        }
        
        return f"https://www.amazon.in/s?{urlencode(params, safe='+')}"
    
    @staticmethod
    def ebay_com_url(query: str) -> str:
        """Build eBay.com search URL matching the provided pattern"""
        # Original: https://www.ebay.com/sch/i.html?_nkw=iphone+16+pro+max&_sacat=0&_from=R40&_trksid=p4432023.m570.l1311
        params = {
            '_nkw': query,
            '_sacat': '0',
            '_from': 'R40',
            '_trksid': 'p4432023.m570.l1311'
        }
        
        return f"https://www.ebay.com/sch/i.html?{urlencode(params)}"
    
    @staticmethod
    def flipkart_url(query: str) -> str:
        """Build Flipkart search URL matching the provided pattern"""
        # Original: https://www.flipkart.com/search?q=iphone+16+pro+max&sid=tyy%2C4io&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_7_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_7_na_na_na&as-pos=1&as-type=RECENT&suggestionId=iphone+16+pro+max%7CMobiles&requestId=8d16d1ae-a3c5-48f2-8f6b-7cd1e6a12a04&as-backfill=on
        params = {
            'q': query,
            'sid': 'tyy,4io',
            'as': 'on',
            'as-show': 'on',
            'otracker': 'AS_QueryStore_OrganicAutoSuggest_1_7_na_na_na',
            'otracker1': 'AS_QueryStore_OrganicAutoSuggest_1_7_na_na_na',
            'as-pos': '1',
            'as-type': 'RECENT',
            'suggestionId': f'{query}|Mobiles',
            'requestId': '8d16d1ae-a3c5-48f2-8f6b-7cd1e6a12a04',
            'as-backfill': 'on'
        }
        
        return f"https://www.flipkart.com/search?{urlencode(params)}"
    
    @staticmethod
    def walmart_url(query: str) -> str:
        """Build Walmart search URL matching the provided pattern"""
        # Original: https://www.walmart.com/search?q=iphone%2016%20pro%20max&typeahead=iphone%2016
        # Extract typeahead (first part of query)
        query_parts = query.split()
        typeahead = ' '.join(query_parts[:2]) if len(query_parts) >= 2 else query
        
        params = {
            'q': query,
            'typeahead': typeahead
        }
        
        return f"https://www.walmart.com/search?{urlencode(params)}"
    
    @staticmethod
    def snapdeal_url(query: str) -> str:
        """Build Snapdeal search URL matching the provided pattern"""
        # Original: https://www.snapdeal.com/search?keyword=IPHONE%2016%20PRO%20MAX&santizedKeyword=&catId=&categoryId=0&suggested=false&vertical=&noOfResults=20&searchState=&clickSrc=go_header&lastKeyword=&prodCatId=&changeBackToAll=false&foundInAll=false&categoryIdSearched=&cityPageUrl=&categoryUrl=&url=&utmContent=&dealDetail=&sort=rlvncy
        params = {
            'keyword': query.upper(),
            'santizedKeyword': '',
            'catId': '',
            'categoryId': '0',
            'suggested': 'false',
            'vertical': '',
            'noOfResults': '20',
            'searchState': '',
            'clickSrc': 'go_header',
            'lastKeyword': '',
            'prodCatId': '',
            'changeBackToAll': 'false',
            'foundInAll': 'false',
            'categoryIdSearched': '',
            'cityPageUrl': '',
            'categoryUrl': '',
            'url': '',
            'utmContent': '',
            'dealDetail': '',
            'sort': 'rlvncy'
        }
        
        return f"https://www.snapdeal.com/search?{urlencode(params)}"
    
    @staticmethod
    def shopsy_url(query: str) -> str:
        """Build Shopsy search URL matching the provided pattern"""
        # Original: https://www.shopsy.in/search?q=iphone%2016%20pro%20max
        params = {
            'q': query
        }
        
        return f"https://www.shopsy.in/search?{urlencode(params)}"

class URLMatcher:
    """Matches and parses URLs to extract search queries and site information"""
    
    @staticmethod
    def extract_query_from_url(url: str) -> Dict[str, str]:
        """Extract search query and site from URL"""
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        query_params = parse_qs(parsed.query)
        
        # Determine site and extract query
        if 'amazon.in' in domain:
            query = query_params.get('k', [''])[0].replace('+', ' ')
            return {'site': 'amazon_in', 'query': query, 'country': 'IN'}
        
        elif 'ebay.com' in domain:
            query = query_params.get('_nkw', [''])[0]
            return {'site': 'ebay_com', 'query': query, 'country': 'US'}
        
        elif 'flipkart.com' in domain:
            query = query_params.get('q', [''])[0]
            return {'site': 'flipkart', 'query': query, 'country': 'IN'}
        
        elif 'walmart.com' in domain:
            query = query_params.get('q', [''])[0]
            return {'site': 'walmart', 'query': query, 'country': 'US'}
        
        elif 'snapdeal.com' in domain:
            query = query_params.get('keyword', [''])[0]
            return {'site': 'snapdeal', 'query': query, 'country': 'IN'}
        
        elif 'shopsy.in' in domain:
            query = query_params.get('q', [''])[0]
            return {'site': 'shopsy', 'query': query, 'country': 'IN'}
        
        return {'site': 'unknown', 'query': '', 'country': 'US'}

class EnhancedSearchTool:
    """Enhanced search tool that can work with the provided URL patterns"""
    
    def __init__(self):
        self.url_builder = SearchURLBuilder()
        self.url_matcher = URLMatcher()
    
    def build_search_urls(self, query: str, country: str = "IN") -> Dict[str, str]:
        """Build search URLs for all supported sites"""
        urls = {}
        
        if country.upper() == "IN":
            urls['Amazon.in'] = self.url_builder.amazon_in_url(query)
            urls['Flipkart'] = self.url_builder.flipkart_url(query)
            urls['Snapdeal'] = self.url_builder.snapdeal_url(query)
            urls['Shopsy'] = self.url_builder.shopsy_url(query)
            # eBay India can also be added
        
        if country.upper() == "US":
            urls['eBay.com'] = self.url_builder.ebay_com_url(query)
            urls['Walmart'] = self.url_builder.walmart_url(query)
        
        return urls
    
    def parse_provided_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """Parse the provided URLs to extract query and site information"""
        parsed_urls = []
        
        for url in urls:
            result = self.url_matcher.extract_query_from_url(url)
            result['original_url'] = url
            parsed_urls.append(result)
        
        return parsed_urls
    
    def get_search_info_from_links(self, url_text: str) -> Dict[str, Any]:
        """Extract search information from the provided links"""
        lines = url_text.strip().split('\n')
        urls = [line.strip() for line in lines if line.strip().startswith('http')]
        
        parsed_urls = self.parse_provided_urls(urls)
        
        # Extract common query (most frequent)
        queries = [item['query'] for item in parsed_urls if item['query']]
        most_common_query = max(set(queries), key=queries.count) if queries else ""
        
        # Determine countries involved
        countries = list(set([item['country'] for item in parsed_urls]))
        
        return {
            'query': most_common_query,
            'countries': countries,
            'sites': [item['site'] for item in parsed_urls],
            'parsed_urls': parsed_urls
        }

# Test the URL building and parsing
if __name__ == "__main__":
    search_tool = EnhancedSearchTool()
    
    # Test URL building
    print("=== Testing URL Building ===")
    query = "iPhone 16 Pro Max"
    
    print(f"Query: {query}")
    print("\nGenerated URLs:")
    
    in_urls = search_tool.build_search_urls(query, "IN")
    for site, url in in_urls.items():
        print(f"{site}: {url}")
    
    print("\n" + "="*80)
    
    # Test URL parsing with provided links
    provided_urls = """
https://www.amazon.in/s?k=iphone+16pro+max&crid=7HN8Y295XVCV&sprefix=iphone+%2Caps%2C791&ref=nb_sb_ss_mvt-t11-ranker_1_7
https://www.ebay.com/sch/i.html?_nkw=iphone+16+pro+max&_sacat=0&_from=R40&_trksid=p4432023.m570.l1311
https://www.flipkart.com/search?q=iphone+16+pro+max&sid=tyy%2C4io&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_7_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_7_na_na_na&as-pos=1&as-type=RECENT&suggestionId=iphone+16+pro+max%7CMobiles&requestId=8d16d1ae-a3c5-48f2-8f6b-7cd1e6a12a04&as-backfill=on
https://www.walmart.com/search?q=iphone%2016%20pro%20max&typeahead=iphone%2016
https://www.snapdeal.com/search?keyword=IPHONE%2016%20PRO%20MAX&santizedKeyword=&catId=&categoryId=0&suggested=false&vertical=&noOfResults=20&searchState=&clickSrc=go_header&lastKeyword=&prodCatId=&changeBackToAll=false&foundInAll=false&categoryIdSearched=&cityPageUrl=&categoryUrl=&url=&utmContent=&dealDetail=&sort=rlvncy
https://www.shopsy.in/search?q=iphone%2016%20pro%20max
"""
    
    print("=== Testing URL Parsing ===")
    search_info = search_tool.get_search_info_from_links(provided_urls)
    
    print(f"Extracted Query: {search_info['query']}")
    print(f"Countries: {search_info['countries']}")
    print(f"Sites: {search_info['sites']}")
    
    print("\nParsed URLs:")
    for item in search_info['parsed_urls']:
        print(f"- {item['site']}: {item['query']} ({item['country']})")
