#!/usr/bin/env python3
"""
Test MCDM ranking with debug output
"""

from mcdm_ranker import MCDMRanker

def test_mcdm_detailed():
    ranker = MCDMRanker()
    
    # Test products
    products = [
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
        }
    ]
    
    query = "iPhone 16 Pro Max"
    
    print(f"Search Query: {query}")
    print("=" * 80)
    
    # Debug each product's scoring
    for i, product in enumerate(products):
        print(f"\nProduct {i+1}: {product['productName']}")
        
        # Test relevance components
        relevance = ranker.calculate_relevance_score(product['productName'], query)
        print(f"  Overall Relevance: {relevance:.3f}")
        
        # Test category alignment
        category_score = ranker._calculate_category_alignment(product['productName'].lower(), query.lower())
        print(f"  Category Alignment: {category_score:.3f}")
        
        # Test exact model match
        exact_match = ranker._is_exact_model_match(product['productName'].lower(), query.lower())
        print(f"  Exact Model Match: {exact_match}")
        
        print(f"  Price: {product['currency']} {product['price']}")
        print(f"  Source: {product['source']}")
    
    print("\n" + "=" * 80)
    print("FINAL RANKING:")
    print("=" * 80)
    
    ranked = ranker.calculate_mcdm_scores(products, query)
    
    for i, product in enumerate(ranked, 1):
        print(f"{i}. {product['productName']}")
        print(f"   MCDM Score: {product['mcdm_score']:.3f}")
        print(f"   Relevance: {product['relevance_score']:.3f}")
        print(f"   Price: {product['currency']} {product['price']}")
        print()

if __name__ == "__main__":
    test_mcdm_detailed()
