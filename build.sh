#!/bin/bash
# Build script for Render deployment
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-production.txt

echo "Setting up application..."
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

echo "Verifying installation..."
python -c "import flask, requests, bs4, aiohttp; print('All dependencies installed successfully')"

echo "Build completed successfully!"
