#!/bin/bash
# Build script for Render deployment with fallback handling
echo "🚀 Starting build process..."

echo "📦 Installing Python dependencies..."
pip install --upgrade pip

# Try main requirements first
echo "   Attempting to install main requirements..."
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

echo "🧪 Verifying installation..."
python -c "
import sys
print(f'Python version: {sys.version}')

# Test core dependencies
try:
    import flask, requests, bs4, aiohttp
    print('✅ Core dependencies OK')
except ImportError as e:
    print(f'❌ Core dependency missing: {e}')
    sys.exit(1)

# Test optional dependencies with fallbacks  
try:
    import lxml
    print('✅ lxml available')
except ImportError:
    print('⚠️  lxml not available, using html.parser fallback')

try:
    import Levenshtein
    print('✅ Levenshtein available')
except ImportError:
    print('⚠️  Levenshtein not available, using basic string comparison fallback')

print('🎉 Build verification complete!')
"

echo "✅ Build completed successfully!"
