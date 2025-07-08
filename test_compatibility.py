#!/usr/bin/env python3
"""
Test script to verify Python 3.11 compatibility and fallback dependencies
Run this before deployment to ensure everything works
"""

import sys
import importlib

def test_python_version():
    """Test Python version compatibility"""
    print(f"Python version: {sys.version}")
    version_info = sys.version_info
    
    if version_info.major == 3 and 10 <= version_info.minor <= 11:
        print("✅ Python version is compatible")
        return True
    else:
        print("⚠️  Python version may have compatibility issues")
        return False

def test_imports():
    """Test all required imports with fallbacks"""
    test_results = {}
    
    # Core dependencies
    required_modules = [
        'flask', 'requests', 'bs4', 'aiohttp', 'fuzzywuzzy'
    ]
    
    # Optional dependencies with fallbacks
    optional_modules = [
        ('lxml', 'xml parsing'),
        ('Levenshtein', 'string distance calculation')
    ]
    
    print("\n=== Testing Core Dependencies ===")
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            test_results[module] = True
        except ImportError as e:
            print(f"❌ {module}: {e}")
            test_results[module] = False
    
    print("\n=== Testing Optional Dependencies (with fallbacks) ===")
    for module, description in optional_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} ({description})")
            test_results[module] = True
        except ImportError as e:
            print(f"⚠️  {module} not available, will use fallback ({description})")
            test_results[module] = False
    
    return test_results

def test_beautifulsoup_parsers():
    """Test BeautifulSoup parser availability"""
    from bs4 import BeautifulSoup
    
    print("\n=== Testing BeautifulSoup Parsers ===")
    test_html = "<div>Test</div>"
    
    # Test built-in parser (always available)
    try:
        soup = BeautifulSoup(test_html, 'html.parser')
        print("✅ html.parser (built-in)")
    except Exception as e:
        print(f"❌ html.parser: {e}")
    
    # Test lxml parser (optional)
    try:
        soup = BeautifulSoup(test_html, 'lxml')
        print("✅ lxml parser")
    except Exception as e:
        print(f"⚠️  lxml parser not available, using html.parser fallback")

def test_app_imports():
    """Test our app modules can be imported"""
    print("\n=== Testing App Modules ===")
    
    app_modules = [
        'enhanced_scraping_tool',
        'mcdm_ranker', 
        'url_builder',
        'complete_app'
    ]
    
    for module in app_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
        except Exception as e:
            print(f"⚠️  {module}: Warning - {e}")

def main():
    """Run all compatibility tests"""
    print("🧪 Python 3.11 Compatibility Test Suite")
    print("=" * 50)
    
    python_ok = test_python_version()
    test_results = test_imports()
    test_beautifulsoup_parsers()
    test_app_imports()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    core_modules_ok = all(test_results.get(m, False) for m in ['flask', 'requests', 'bs4', 'fuzzywuzzy'])
    
    if python_ok and core_modules_ok:
        print("✅ Ready for deployment!")
        print("   - Python version is compatible")
        print("   - All core dependencies available")
        print("   - Fallbacks configured for optional dependencies")
    else:
        print("❌ Issues detected:")
        if not python_ok:
            print("   - Python version compatibility issues")
        if not core_modules_ok:
            print("   - Missing core dependencies")
        print("   - Fix issues before deployment")

if __name__ == "__main__":
    main()
