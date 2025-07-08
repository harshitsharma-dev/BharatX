#!/usr/bin/env python3
"""
Multi-Criteria Decision Making (MCDM) for Product Ranking
Implements TOPSIS method for ranking products based on multiple criteria:
1. Search relevance (most important)
2. Price (secondary)
3. Source reliability (tertiary)
"""

import math
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
import re

class MCDMRanker:
    """Multi-Criteria Decision Making ranker for products"""
    
    def __init__(self):
        # Criteria weights (sum should be 1.0)
        self.weights = {
            'relevance': 0.75,    # 75% - Most important: how well does product match search
            'price': 0.20,        # 20% - Secondary: lower price is better
            'source_reliability': 0.05  # 5% - Tertiary: source trustworthiness
        }
        
        # Source reliability scores (0-1, higher is better)
        self.source_reliability = {
            'Amazon.in': 0.95,
            'Flipkart': 0.90,
            'Walmart': 0.95,
            'eBay.com': 0.85,
            'eBay.in': 0.85,
            'Snapdeal': 0.80,
            'Shopsy': 0.75
        }
    
    def calculate_relevance_score(self, product_name: str, search_query: str) -> float:
        """Calculate how relevant the product is to the search query"""
        product_lower = product_name.lower()
        query_lower = search_query.lower()
        
        # Extract key terms from search query
        query_terms = self._extract_key_terms(query_lower)
        
        # Multiple relevance factors
        scores = []
        
        # 1. Fuzzy string similarity (base score)
        fuzzy_score = fuzz.token_sort_ratio(product_lower, query_lower) / 100.0
        scores.append(fuzzy_score * 0.25)  # Reduced further from 0.30
        
        # 2. Exact keyword matches (high importance)
        exact_matches = sum(1 for term in query_terms if term in product_lower)
        exact_score = min(exact_matches / len(query_terms), 1.0) if query_terms else 0
        
        # Strong bonus for exact model/version match
        if self._is_exact_model_match(product_lower, query_lower):
            exact_score = min(exact_score + 0.5, 1.0)  # Increased bonus for exact model
        
        scores.append(exact_score * 0.40)  # Increased weight from 0.35
        
        # 3. Partial keyword matches
        partial_matches = sum(1 for term in query_terms 
                            if any(part in product_lower for part in term.split()))
        partial_score = min(partial_matches / len(query_terms), 1.0) if query_terms else 0
        scores.append(partial_score * 0.10)  # Reduced from 0.15
        
        # 4. Product category/brand alignment (increased weight)
        category_score = self._calculate_category_alignment(product_lower, query_lower)
        scores.append(category_score * 0.25)  # Increased from 0.10 to 0.25
        
        return sum(scores)
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key search terms, removing common words"""
        # Remove common words that don't add search value
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Split and clean terms
        terms = re.findall(r'\w+', query.lower())
        key_terms = [term for term in terms if len(term) > 2 and term not in stop_words]
        
        return key_terms
    
    def _calculate_category_alignment(self, product_name: str, query: str) -> float:
        """Calculate if product matches the general category of search"""
        # Define product categories and their keywords
        categories = {
            'phone': ['iphone', 'phone', 'mobile', 'smartphone', 'galaxy', 'pixel', 'oneplus'],
            'laptop': ['laptop', 'macbook', 'thinkpad', 'notebook', 'computer'],
            'tablet': ['ipad', 'tablet', 'kindle'],
            'audio': ['headphones', 'earbuds', 'speaker', 'airpods'],
            'accessory': ['case', 'cover', 'charger', 'cable', 'screen protector', 'silicon', 'leather']
        }
        
        # Determine query category
        query_category = None
        for category, keywords in categories.items():
            if any(keyword in query for keyword in keywords):
                query_category = category
                break
        
        if not query_category:
            return 0.5  # Neutral if category unclear
        
        # Check if product matches the category
        category_keywords = categories[query_category]
        product_matches_category = any(keyword in product_name for keyword in category_keywords)
        
        # Check if product is an accessory
        accessory_keywords = categories['accessory']
        is_accessory = any(keyword in product_name for keyword in accessory_keywords)
        
        if query_category in ['phone', 'laptop', 'tablet']:
            if is_accessory:
                return 0.1  # Heavy penalty for accessories when searching for main product
            elif product_matches_category:
                return 1.0  # Perfect match for main product
            else:
                return 0.3  # Different category
        
        # For other categories
        if product_matches_category:
            return 1.0
        elif is_accessory and query_category != 'accessory':
            return 0.2
        
        return 0.5  # Neutral
    
    def normalize_price_score(self, prices: List[float]) -> List[float]:
        """Normalize price scores (lower price = higher score)"""
        if not prices or len(set(prices)) == 1:
            return [0.5] * len(prices)  # All equal if no variation
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        # Invert prices (lower price gets higher score)
        normalized = []
        for price in prices:
            if price_range == 0:
                normalized.append(0.5)
            else:
                # Normalize and invert: lowest price gets score 1.0, highest gets 0.0
                score = 1.0 - ((price - min_price) / price_range)
                normalized.append(score)
        
        return normalized
    
    def calculate_mcdm_scores(self, products: List[Dict], search_query: str) -> List[Dict]:
        """Calculate MCDM scores using TOPSIS method with exact model prioritization"""
        if not products:
            return products
        
        # First pass: Calculate basic criteria scores
        criteria_matrix = []
        has_exact_matches = False
        
        for product in products:
            # 1. Relevance score
            relevance = self.calculate_relevance_score(product['productName'], search_query)
            
            # Check if any product has exact model match
            if self._is_exact_model_match(product['productName'].lower(), search_query.lower()):
                has_exact_matches = True
            
            # 2. Source reliability
            source = product.get('source', 'Unknown')
            reliability = self.source_reliability.get(source, 0.5)
            
            criteria_matrix.append({
                'relevance': relevance,
                'price_raw': product['price'],
                'source_reliability': reliability,
                'has_exact_match': self._is_exact_model_match(product['productName'].lower(), search_query.lower()),
                'is_accessory': self._is_accessory_product(product['productName'].lower())
            })
        
        # Second pass: Apply penalties/bonuses based on context
        if has_exact_matches:
            for i, criteria in enumerate(criteria_matrix):
                # Penalize non-exact matches when exact matches exist
                if not criteria['has_exact_match']:
                    criteria['relevance'] *= 0.8  # 20% penalty
                
                # Heavy penalty for accessories when searching for main products
                if criteria['is_accessory'] and not self._is_searching_for_accessory(search_query):
                    criteria['relevance'] *= 0.3  # 70% penalty for accessories
        
        # Normalize price scores
        prices = [criteria['price_raw'] for criteria in criteria_matrix]
        normalized_prices = self.normalize_price_score(prices)
        
        # Calculate weighted scores
        final_scores = []
        for i, criteria in enumerate(criteria_matrix):
            score = (
                criteria['relevance'] * self.weights['relevance'] +
                normalized_prices[i] * self.weights['price'] +
                criteria['source_reliability'] * self.weights['source_reliability']
            )
            final_scores.append(score)
        
        # Add MCDM scores to products and sort
        ranked_products = []
        for i, product in enumerate(products):
            product_copy = product.copy()
            product_copy['mcdm_score'] = final_scores[i]
            product_copy['relevance_score'] = criteria_matrix[i]['relevance']
            ranked_products.append(product_copy)
        
        # Sort by MCDM score (highest first)
        ranked_products.sort(key=lambda x: x['mcdm_score'], reverse=True)
        
        return ranked_products
    
    def _is_accessory_product(self, product_name: str) -> bool:
        """Check if product is an accessory"""
        accessory_keywords = ['case', 'cover', 'charger', 'cable', 'screen protector', 'silicon', 'leather', 'tempered glass']
        return any(keyword in product_name for keyword in accessory_keywords)
    
    def _is_searching_for_accessory(self, query: str) -> bool:
        """Check if user is specifically searching for accessories"""
        accessory_keywords = ['case', 'cover', 'charger', 'cable', 'screen protector']
        return any(keyword in query.lower() for keyword in accessory_keywords)
    
    def filter_low_relevance(self, products: List[Dict], min_relevance: float = 0.3) -> List[Dict]:
        """Filter out products with very low relevance to search query"""
        return [product for product in products if product.get('relevance_score', 0) >= min_relevance]
    
    def _is_exact_model_match(self, product_name: str, query: str) -> bool:
        """Check if product matches the exact model/version in the query"""
        # Look for model numbers and versions
        import re
        
        # Extract model patterns like "16 pro max", "15 pro", "13r", etc.
        model_patterns = [
            r'\b\d+\s*pro\s*max\b',
            r'\b\d+\s*pro\b',
            r'\b\d+\s*plus\b',
            r'\b\d+r\b',
            r'\biphone\s*\d+\b',
            r'\bgalaxy\s*s\d+\b'
        ]
        
        for pattern in model_patterns:
            query_matches = re.findall(pattern, query.lower())
            product_matches = re.findall(pattern, product_name.lower())
            
            if query_matches and product_matches:
                # Check if the exact model appears in both
                for q_match in query_matches:
                    if q_match in product_matches:
                        return True
        
        return False
    
# Example usage and testing
if __name__ == "__main__":
    ranker = MCDMRanker()
    
    # Test with sample products
    sample_products = [
        {
            'productName': 'Apple iPhone 16 Pro Max (Natural Titanium, 256 GB)',
            'price': 135900.0,
            'currency': 'INR',
            'source': 'Amazon.in'
        },
        {
            'productName': 'iPhone 16 Pro Max Case Cover Silicon',
            'price': 499.0,
            'currency': 'INR',
            'source': 'Snapdeal'
        },
        {
            'productName': 'Apple iPhone 15 Pro Max 256GB',
            'price': 120000.0,
            'currency': 'INR',
            'source': 'Flipkart'
        },
        {
            'productName': 'OnePlus 13R Smartphone 256GB',
            'price': 42997.0,
            'currency': 'INR',
            'source': 'Amazon.in'
        }
    ]
    
    search_query = "iPhone 16 Pro Max"
    
    print(f"Search Query: {search_query}")
    print("-" * 60)
    
    ranked = ranker.calculate_mcdm_scores(sample_products, search_query)
    
    for i, product in enumerate(ranked, 1):
        print(f"{i}. {product['productName'][:50]}...")
        print(f"   Price: {product['currency']} {product['price']}")
        print(f"   MCDM Score: {product['mcdm_score']:.3f}")
        print(f"   Relevance: {product['relevance_score']:.3f}")
        print(f"   Source: {product['source']}")
        print()
