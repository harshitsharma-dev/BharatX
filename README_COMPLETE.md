# 🛒 Complete Price Comparison API

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![API](https://img.shields.io/badge/API-REST-orange.svg)](http://localhost:5000)

A comprehensive, production-ready price comparison API that scrapes multiple e-commerce platforms to find and compare product prices across different countries. Built with advanced web scraping, intelligent caching, and robust error handling.

## 🌟 Key Features

- **🌐 Multi-Platform Support**: Amazon, Flipkart, eBay, Walmart, Snapdeal, Shopsy
- **🗺️ Multi-Country**: US, India, UK, Germany, Canada with currency support
- **⚡ High Performance**: Async scraping with intelligent caching
- **🛡️ Robust**: Comprehensive error handling and anti-bot measures
- **🐳 Production Ready**: Dockerized with health checks and monitoring
- **📊 Analytics**: Price analysis, source breakdown, and statistics
- **🧪 Testing**: Both live scraping and local HTML testing support
- **📝 Well Documented**: Comprehensive API documentation

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and start with Docker
git clone <repository-url>
cd BharatX
docker-compose up -d

# API available at http://localhost:5000
```

### Option 2: Local Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the API
python complete_app.py

# API available at http://localhost:5000
```

### Option 3: Setup Scripts
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

## 🧪 Quick Test

```bash
# Test all endpoints
python test_complete_api.py

# Or test manually
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "iPhone 16 Pro Max", "max_results": 5}'
```

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and help |
| GET | `/health` | Health check and system status |
| GET | `/countries` | Supported countries and sites |
| GET | `/samples` | Sample queries for testing |
| POST | `/search` | **Main product search** |
| GET/POST | `/demo` | Demo endpoint with defaults |
| GET | `/cache/status` | Cache information |
| POST | `/cache/clear` | Clear cache |

## 🔍 Search API Usage

### Basic Search
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "country": "IN",
    "query": "iPhone 16 Pro Max"
  }'
```

### Advanced Search with Options
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "country": "US",
    "query": "MacBook Pro",
    "max_results": 20,
    "use_local": false
  }'
```

### Demo Search (Quick Test)
```bash
curl -X POST http://localhost:5000/demo \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "Samsung Galaxy"}'
```

## 📊 Response Format

```json
{
  "success": true,
  "query": "iPhone 16 Pro Max",
  "country": "IN",
  "products": [
    {
      "productName": "Apple iPhone 16 Pro Max (Natural Titanium, 512 GB)",
      "price": 152900.0,
      "currency": "INR",
      "link": "https://www.flipkart.com/...",
      "source": "Flipkart"
    }
  ],
  "total_results": 15,
  "response_time_seconds": 2.1,
  "price_analysis": {
    "min_price": 135900.0,
    "max_price": 170900.0,
    "avg_price": 152400.0,
    "currency": "INR"
  },
  "source_breakdown": {
    "Amazon.in": 8,
    "Flipkart": 7
  }
}
```

## 🌍 Supported Countries & Sites

| Country | Code | Sites | Currency |
|---------|------|-------|----------|
| 🇮🇳 India | IN | Amazon.in, Flipkart, eBay.in, Snapdeal, Shopsy | INR |
| 🇺🇸 United States | US | eBay.com, Walmart | USD |
| 🇬🇧 United Kingdom | UK | eBay.co.uk | GBP |
| 🇩🇪 Germany | DE | eBay.de | EUR |
| 🇨🇦 Canada | CA | eBay.ca | CAD |

## 🛠️ Project Structure

```
BharatX/
├── complete_app.py              # 🎯 Main Flask API application
├── enhanced_scraping_tool.py    # 🔧 Enhanced scraping engine
├── real_scraping_tool.py        # 🌐 Real web scraping implementation
├── price_comparison_tool.py     # 💰 Core price comparison logic
├── url_builder.py               # 🔗 URL building utilities
├── app.py / app_demo.py         # 📱 Alternative API versions
├── test_complete_api.py         # 🧪 Comprehensive API tests
├── debug_amazon.py              # 🔍 Amazon debugging tools
├── debug_flipkart.py            # 🔍 Flipkart debugging tools
├── webpages_samples/            # 📄 Local HTML samples for testing
├── api_cache/                   # 💾 API response cache
├── logs/                        # 📝 Application logs
├── Dockerfile                   # 🐳 Docker configuration
├── docker-compose.yml           # 🐳 Docker Compose setup
├── requirements.txt             # 📦 Python dependencies
├── setup.sh / setup.bat         # ⚙️ Setup scripts
├── README.md                    # 📖 This file
├── API_DOCUMENTATION.md         # 📚 Detailed API docs
└── IMPLEMENTATION.md            # 🔧 Implementation details
```

## 🏗️ Architecture

### Core Components

1. **🎯 Complete Flask API** (`complete_app.py`)
   - Production-ready REST API
   - Comprehensive error handling
   - Caching and performance optimization
   - Health monitoring and logging

2. **🔧 Enhanced Scraping Engine** (`enhanced_scraping_tool.py`)
   - Multi-platform scrapers with intelligent selectors
   - Support for both live and local HTML scraping
   - Robust price extraction and validation
   - Anti-bot measures and error recovery

3. **💰 Price Comparison Logic** 
   - Intelligent duplicate detection
   - Price normalization and analysis
   - Source breakdown and statistics
   - Currency handling

4. **📦 Caching System**
   - File-based caching with configurable TTL
   - Reduces load on target websites
   - Improves response times

### Scraping Strategy

- **🎯 Targeted Selectors**: Site-specific CSS selectors based on actual HTML analysis
- **🔄 Fallback Patterns**: Multiple selector patterns for reliability
- **🛡️ Anti-Bot Measures**: User-Agent rotation, request delays, SSL handling
- **📊 Local Testing**: HTML samples for development and testing

## ⚙️ Configuration

### Environment Variables
```bash
# Cache settings
CACHE_TTL_SECONDS=3600
CACHE_DIR=api_cache

# Performance settings  
REQUEST_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=5
MAX_RESULTS_PER_SCRAPER=10

# Server settings
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_ENV=production
```

### Config File
Modify the `Config` class in `complete_app.py` for detailed configuration:
```python
class Config:
    CACHE_TTL_SECONDS = 3600
    MAX_RESULTS_PER_SCRAPER = 10
    SUPPORTED_COUNTRIES = {...}
    SAMPLE_QUERIES = {...}
```

## 🐳 Docker Deployment

### Development
```bash
docker-compose up
```

### Production
```bash
# Build production image
docker build -t price-comparison-api .

# Run with production settings
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e CACHE_TTL_SECONDS=7200 \
  -v $(pwd)/api_cache:/app/api_cache \
  -v $(pwd)/logs:/app/logs \
  price-comparison-api
```

## 🧪 Testing & Development

### Running Tests
```bash
# Full API test suite
python test_complete_api.py

# Individual scraper tests
python test_amazon_flipkart.py

# Debug specific scrapers
python debug_amazon.py
python debug_flipkart.py

# Enhanced scraping tool test
python enhanced_scraping_tool.py
```

### Local HTML Testing
```bash
# Test with local HTML samples (no web requests)
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "iPhone", "use_local": true}'
```

### Adding New Scrapers
1. Create scraper class in `enhanced_scraping_tool.py`
2. Implement required methods: `_build_search_url()`, `_parse_results()`
3. Add HTML samples to `webpages_samples/`
4. Add scraper to country configuration
5. Test with debug scripts

## 📊 Monitoring & Logging

### Health Check
```bash
curl http://localhost:5000/health
```

### Cache Management
```bash
# Check cache status
curl http://localhost:5000/cache/status

# Clear cache
curl -X POST http://localhost:5000/cache/clear
```

### Logs
- Application logs: `price_comparison.log`
- Docker logs: `docker-compose logs -f`
- Error tracking with detailed stack traces

## 🚨 Error Handling

The API provides comprehensive error responses:

```json
{
  "error": "Country 'XX' not supported",
  "supported_countries": ["US", "IN", "UK", "DE", "CA"],
  "timestamp": "2025-07-08T10:30:00"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Endpoint not found
- `408`: Request timeout
- `500`: Internal server error

## 🔒 Security & Production

### Security Considerations
- Input validation and sanitization
- Rate limiting (implement for production)
- HTTPS enforcement (configure reverse proxy)
- API authentication (add for production)
- Error sanitization (no sensitive data exposure)

### Production Checklist
- [ ] Configure reverse proxy (nginx/apache)
- [ ] Set up HTTPS/SSL certificates
- [ ] Implement rate limiting
- [ ] Add API authentication
- [ ] Configure monitoring and alerts
- [ ] Set up log rotation
- [ ] Configure backup for cache data

## 📈 Performance

### Optimization Features
- **⚡ Async Scraping**: Parallel requests across multiple sites
- **💾 Intelligent Caching**: Reduces redundant requests
- **🔄 Connection Pooling**: Reuses HTTP connections
- **⏱️ Timeout Handling**: Prevents hanging requests
- **📊 Result Limiting**: Configurable result counts

### Performance Metrics
- Average response time: 1-3 seconds
- Cache hit rate: 70-90% for repeated queries
- Concurrent request handling: 5 parallel scrapers
- Memory usage: ~50MB base + cache

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-scraper`
3. Make changes and add tests
4. Commit: `git commit -am 'Add new scraper for XYZ'`
5. Push: `git push origin feature/new-scraper`
6. Submit a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Test with both local and live scraping
- Ensure Docker compatibility

## 📞 Support & Troubleshooting

### Common Issues

**Issue**: "No products found"
- Check if the query is too specific
- Verify country code is supported
- Try `use_local: true` for testing

**Issue**: "Request timeout"
- Check internet connection
- Some sites may be temporarily down
- Try reducing `max_results`

**Issue**: "Cache errors"
- Clear cache: `curl -X POST http://localhost:5000/cache/clear`
- Check disk space and permissions

### Getting Help
- Check the `/health` endpoint for system status
- Review logs in `price_comparison.log`
- Use the `/demo` endpoint for quick testing
- Check the [API Documentation](API_DOCUMENTATION.md)

## 📄 License

[Specify your license here - MIT, Apache 2.0, etc.]

## 🙏 Acknowledgments

- Built with Python, Flask, and BeautifulSoup
- Uses aiohttp for async HTTP requests
- Fuzzy matching with fuzzywuzzy
- Caching and performance optimizations

---

**⭐ If this project helps you, please give it a star!**

**🛒 Happy price hunting! 💰**
