#!/bin/bash
# Build script for Render deployment - Python 3.12.5 optimized
echo "🚀 Starting build process for Python 3.12.5..."

echo "📦 Installing Python dependencies..."
pip install --upgrade pip

# Try main requirements optimized for Python 3.12
echo "   Installing Python 3.12 optimized requirements..."
if pip install -r requirements-production.txt; then
    echo "✅ Main requirements installed successfully"
else
    echo "⚠️  Main requirements failed, trying fallback..."
    if [ -f "requirements-fallback.txt" ]; then
        pip install -r requirements-fallback.txt
        echo "✅ Fallback requirements installed"
    else
        echo "❌ Fallback requirements not found"
        exit 1
    fi
fi

echo "🔧 Setting up application..."
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

echo "🧪 Verifying Python 3.12 installation..."
python -c "
import sys
print(f'Python version: {sys.version}')

# Test core dependencies
try:
    import flask, requests, bs4, aiohttp, fuzzywuzzy
    print('✅ Core dependencies OK')
except ImportError as e:
    print(f'❌ Core dependency missing: {e}')
    sys.exit(1)

# Test optional dependencies with graceful fallbacks  
try:
    import lxml
    print('✅ lxml available - using fast XML parser')
except ImportError:
    print('⚠️  lxml not available, using html.parser fallback')

try:
    import Levenshtein
    print('✅ Levenshtein available - using fast string matching')
except ImportError:
    print('⚠️  Levenshtein not available, using basic string comparison fallback')

print('🎉 Python 3.12 build verification complete!')
"

echo "✅ Build completed successfully!"
