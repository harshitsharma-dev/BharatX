#!/bin/bash

# Price Comparison Tool Setup Script
# This script helps set up and run the price comparison tool

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Price Comparison Tool Setup${NC}"
echo "================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists pip; then
    echo -e "${RED}pip is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 and pip are available${NC}"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create cache directory
echo -e "${YELLOW}Creating cache directory...${NC}"
mkdir -p cache
echo -e "${GREEN}✓ Cache directory created${NC}"

# Run tests
echo -e "${YELLOW}Running basic tests...${NC}"
python test_tool.py

echo -e "${GREEN}✓ Basic tests completed${NC}"

# Instructions for running
echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To run the application:"
echo "  python app.py"
echo ""
echo "To test the tool:"
echo "  python test_tool.py"
echo ""
echo "To run with Docker:"
echo "  docker-compose up --build"
echo ""
echo "API will be available at: http://localhost:5000"
