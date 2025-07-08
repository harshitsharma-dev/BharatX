# Complete Price Comparison API

A comprehensive, production-ready price comparison API that scrapes multiple e-commerce platforms to find and compare product prices across different countries.

## 🚀 Features

- **Multi-Platform Scraping**: Amazon, Flipkart, eBay, Walmart, Snapdeal, Shopsy
- **Multi-Country Support**: US, India, UK, Germany, Canada
- **Intelligent Caching**: File-based caching with configurable TTL
- **Real & Local Scraping**: Support for both live web scraping and local HTML testing
- **RESTful API**: Clean, well-documented REST endpoints
- **Price Analysis**: Automatic price statistics and source breakdown
- **Robust Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Cross-origin resource sharing enabled
- **Production Ready**: Dockerized with comprehensive logging

## 📋 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repo-url>
cd BharatX

# Install dependencies
pip install -r requirements.txt

# Or use the setup script
./setup.sh  # Linux/Mac
setup.bat   # Windows
```

### 2. Running the API

```bash
# Start the API server
python complete_app.py

# The API will be available at:
# http://localhost:5000
```

### 3. Quick Test

```bash
# Test the API
python test_complete_api.py
```

## 🔧 API Endpoints

### Home & Information
- `GET /` - API information and available endpoints
- `GET /health` - Health check and system status
- `GET /countries` - List supported countries and sites
- `GET /samples` - Get sample queries for testing

### Product Search
- `POST /search` - Main product search endpoint
- `GET /demo` - Demo endpoint information
- `POST /demo` - Quick demo search with defaults

### Cache Management
- `GET /cache/status` - View cache information
- `POST /cache/clear` - Clear all cached data

## 📖 API Usage Examples

### Basic Product Search

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "country": "IN",
    "query": "iPhone 16 Pro Max",
    "max_results": 10
  }'
```

### Demo Search
```bash
curl -X POST http://localhost:5000/demo \
  -H "Content-Type: application/json" \
  -d '{
    "country": "US",
    "query": "MacBook Pro",
    "use_local": false
  }'
```

### Get Supported Countries
```bash
curl http://localhost:5000/countries
```

## 📊 Response Format

### Search Response
```json
{
  "success": true,
  "query": "iPhone 16 Pro Max",
  "country": "IN",
  "country_info": {
    "name": "India",
    "currency": "INR",
    "sites": ["Amazon.in", "Flipkart", "eBay.in", "Snapdeal", "Shopsy"]
  },
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
  "response_time_seconds": 2.34,
  "timestamp": "2025-07-08T10:30:00",
  "price_analysis": {
    "currency": "INR",
    "min_price": 60200.0,
    "max_price": 170900.0,
    "avg_price": 128450.5,
    "price_range": 110700.0
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
| India | IN | Amazon.in, Flipkart, eBay.in, Snapdeal, Shopsy | INR |
| United States | US | eBay.com, Walmart | USD |
| United Kingdom | UK | eBay.co.uk | GBP |
| Germany | DE | eBay.de | EUR |
| Canada | CA | eBay.ca | CAD |

## ⚙️ Configuration

### Environment Variables
```bash
# Cache settings
CACHE_TTL_SECONDS=3600        # Cache duration (default: 1 hour)
CACHE_DIR=api_cache           # Cache directory

# API settings
MAX_RESULTS_PER_SCRAPER=10    # Max results per site
REQUEST_TIMEOUT=30            # Request timeout in seconds
MAX_CONCURRENT_REQUESTS=5     # Max parallel requests

# Server settings
FLASK_HOST=0.0.0.0           # Server host
FLASK_PORT=5000              # Server port
FLASK_DEBUG=false            # Debug mode
```

### Config Class (complete_app.py)
```python
class Config:
    CACHE_TTL_SECONDS = 3600
    CACHE_DIR = "api_cache"
    MAX_RESULTS_PER_SCRAPER = 10
    REQUEST_TIMEOUT = 30
    MAX_CONCURRENT_REQUESTS = 5
    # ... more settings
```

## 🐳 Docker Deployment

### Build and Run with Docker
```bash
# Build the image
docker build -t price-comparison-api .

# Run the container
docker run -p 5000:5000 -d price-comparison-api
```

### Docker Compose
```bash
# Start with docker-compose
docker-compose up -d

# Stop
docker-compose down
```

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive API tests
python test_complete_api.py

# Test individual scrapers
python test_amazon_flipkart.py

# Debug specific sites
python debug_amazon.py
python debug_flipkart.py
```

### Manual Testing
```bash
# Test with local HTML samples
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "iPhone", "use_local": true}'

# Test live scraping
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "iPhone", "use_local": false}'
```

## 📝 Development & Extensibility

### Adding New Scrapers
1. Create a new scraper class inheriting from `EnhancedBaseScraper`
2. Implement required methods: `_build_search_url()`, `_parse_results()`
3. Add to the scrapers dictionary in `enhanced_scraping_tool.py`
4. Test with local HTML samples

### Adding New Countries
1. Add country configuration to `SUPPORTED_COUNTRIES`
2. Add sample queries to `SAMPLE_QUERIES`
3. Configure appropriate scrapers for the country

### Local HTML Testing
- Place HTML samples in `webpages_samples/` directory
- Use `use_local: true` in API requests
- Useful for development and anti-bot testing

## 🚨 Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input data
- **404 Not Found**: Endpoint not found
- **408 Request Timeout**: Search took too long
- **500 Internal Server Error**: Server-side errors

Example error response:
```json
{
  "error": "Country 'XX' not supported",
  "supported_countries": ["US", "IN", "UK", "DE", "CA"],
  "timestamp": "2025-07-08T10:30:00"
}
```

## 📊 Monitoring & Logging

### Logging
- All requests and responses logged
- Error tracking with stack traces
- Performance metrics (response times)
- Cache hit/miss statistics

### Log Files
- `price_comparison.log` - Application logs
- Console output for development

### Health Monitoring
Use the `/health` endpoint for monitoring:
```bash
curl http://localhost:5000/health
```

## 🔒 Security Considerations

- **Rate Limiting**: Implement rate limiting for production
- **API Keys**: Add authentication for production use
- **HTTPS**: Use HTTPS in production
- **Input Validation**: All inputs validated and sanitized
- **Error Sanitization**: Sensitive information not exposed in errors

## 📈 Performance Optimization

- **Async Scraping**: Parallel scraping across multiple sites
- **Intelligent Caching**: Reduces redundant requests
- **Request Pooling**: Connection reuse and pooling
- **Result Limiting**: Configurable result limits
- **Timeout Handling**: Prevents hanging requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Submit a pull request

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check the logs in `price_comparison.log`
- Use the `/health` endpoint to verify system status

## 📄 License

[Add your license information here]

---

**Built with ❤️ for accurate price comparisons across the web**
