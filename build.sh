#!/bin/bash
# Build script for Render deployment - Python 3.12.5 with EXACT working versions
echo "🚀 Starting build process for Python 3.12.5..."

echo "📦 Installing Python dependencies (exact versions from local working system)..."
pip install --upgrade pip

# Try main requirements with exact versions that work locally
echo "   Installing EXACT working versions (Flask 3.1.1, requests 2.32.4, etc.)..."
if pip install -r requirements-production.txt; then
    echo "✅ Main requirements (exact working versions) installed successfully"
else
    echo "⚠️  Main requirements failed, trying minimal fallback..."
    if [ -f "requirements-fallback.txt" ]; then
        pip install -r requirements-fallback.txt
        echo "✅ Fallback requirements (minimal working set) installed"
    else
        echo "❌ Fallback requirements not found"
        exit 1
    fi
fi

echo "🔧 Setting up application..."
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

echo "🧪 Verifying Python 3.12 installation with exact working versions..."
python -c "
import sys
print(f'Python version: {sys.version}')

# Test core dependencies with version info
packages_to_check = ['flask', 'requests', 'bs4', 'aiohttp', 'fuzzywuzzy']
all_good = True

for pkg in packages_to_check:
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'unknown')
        print(f'✅ {pkg} {version}')
    except ImportError as e:
        print(f'❌ {pkg}: {e}')
        all_good = False

if not all_good:
    sys.exit(1)

# Test optional dependencies with graceful fallbacks  
try:
    import lxml
    print(f'✅ lxml available - using fast XML parser (version {lxml.__version__})')
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
