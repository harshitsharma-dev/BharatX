# Price Comparison Tool

A modular, Dockerized Python tool that fetches, parses, and ranks product prices from multiple country-relevant e-commerce websites, ensuring high accuracy, broad coverage, and quality results tailored to the user's location and query.

## Features

- **Multi-Country Support**: Supports US, India, UK, Germany, and Canada with country-specific e-commerce sites
- **Parallel Scraping**: Uses asynchronous requests for faster data retrieval
- **Smart Caching**: Implements file-based caching to reduce redundant requests
- **Fuzzy Matching**: Uses advanced text matching to ensure relevant results
- **Duplicate Removal**: Intelligent deduplication based on product similarity
- **RESTful API**: Flask-based API for easy integration
- **Dockerized**: Complete containerization for consistent deployment

## Supported Websites

### United States (US)
- Amazon.com
- eBay.com

### India (IN)
- Amazon.in
- Flipkart
- eBay.in

### United Kingdom (UK)
- Amazon.co.uk
- eBay.co.uk

### Germany (DE)
- Amazon.de
- eBay.de

### Canada (CA)
- Amazon.ca
- eBay.ca

## Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd price-comparison-tool
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. The API will be available at `http://localhost:5000`

### Option 2: Local Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd price-comparison-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## Usage

### API Endpoints

#### Search Products
- **URL**: `POST /search`
- **Content-Type**: `application/json`

**Request Body:**
```json
{
  "country": "US",
  "query": "iPhone 16 Pro 128GB"
}
```

**Response:**
```json
[
  {
    "link": "https://www.amazon.com/product-url",
    "price": 999.0,
    "currency": "USD",
    "productName": "Apple iPhone 16 Pro 128GB"
  },
  {
    "link": "https://www.ebay.com/product-url",
    "price": 1049.0,
    "currency": "USD",
    "productName": "Apple iPhone 16 Pro 128GB"
  }
]
```

#### Health Check
- **URL**: `GET /health`
- **Response**: `{"status": "healthy", "message": "Price comparison tool is running"}`

#### Supported Countries
- **URL**: `GET /supported-countries`
- **Response**: `{"US": "United States", "IN": "India", ...}`

### Command Line Usage

You can also use the tool directly from the command line:

```bash
python test_tool.py
```

## Testing

### Test the Core Functionality
```bash
python test_tool.py
```

### Test the API (requires the Flask app to be running)
```bash
python test_tool.py api
```

### Sample Test Cases

The test script includes several predefined test cases:
- iPhone 16 Pro 128GB in US
- Samsung Galaxy S24 in India
- MacBook Air M2 in US
- OnePlus 12 in India

## Example Usage

### Using cURL

```bash
# Search for iPhone in US
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro 128GB"}'

# Check supported countries
curl http://localhost:5000/supported-countries

# Health check
curl http://localhost:5000/health
```

### Using Python requests

```python
import requests
import json

# Search for products
response = requests.post('http://localhost:5000/search', 
    json={"country": "US", "query": "iPhone 16 Pro 128GB"})

if response.status_code == 200:
    products = response.json()
    for product in products:
        print(f"{product['productName']}: {product['currency']} {product['price']}")
        print(f"Link: {product['link']}\n")
```

## Architecture

### Core Components

1. **PriceComparisonTool**: Main orchestrator class
2. **BaseScraper**: Abstract base class for website scrapers
3. **Specific Scrapers**: Amazon, Flipkart, eBay implementations
4. **CacheManager**: File-based caching system
5. **Flask API**: RESTful web service

### Data Flow

1. **Input Validation**: Validate country code and query
2. **Cache Check**: Look for existing cached results
3. **Parallel Scraping**: Execute multiple scrapers simultaneously
4. **Data Processing**: Parse, filter, and normalize results
5. **Deduplication**: Remove similar products
6. **Sorting**: Sort by price (ascending)
7. **Caching**: Store results for future requests
8. **Response**: Return JSON formatted results

## Configuration

### Environment Variables

- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)
- `LOG_LEVEL`: Logging level (default: INFO)

### Adding New Countries/Websites

To add support for new countries or websites:

1. Create a new scraper class inheriting from `BaseScraper`
2. Implement the required methods: `_build_search_url()` and `_parse_results()`
3. Add the scraper to the country mapping in `PriceComparisonTool._initialize_scrapers()`

Example:
```python
class NewSiteScraper(BaseScraper):
    def __init__(self):
        super().__init__("NewSite", "https://newsite.com", "https://newsite.com/search")
    
    def _build_search_url(self, query: str) -> str:
        return f"{self.search_url}?q={quote_plus(query)}"
    
    def _parse_results(self, html: str, query: str) -> List[Product]:
        # Implementation specific to the website
        pass
```

## Limitations and Considerations

1. **Rate Limiting**: Implements basic delays between requests
2. **Website Changes**: Scrapers may need updates if websites change their structure
3. **Legal Compliance**: Ensure compliance with website terms of service
4. **Currency Conversion**: Currently does not convert between currencies
5. **Geographic Restrictions**: Some websites may block requests from certain regions

## Performance Optimizations

1. **Asynchronous Processing**: All web requests are made concurrently
2. **Intelligent Caching**: Results are cached for 1 hour by default
3. **Duplicate Removal**: Reduces redundant results
4. **Limited Results**: Fetches only top 5 results per site for faster processing
5. **Fuzzy Matching**: Ensures only relevant products are included

## Error Handling

The tool implements comprehensive error handling:
- Network timeouts and connection errors
- HTML parsing errors
- Invalid input validation
- Graceful degradation when some scrapers fail

## Monitoring and Logging

- Structured logging for debugging and monitoring
- Health check endpoint for deployment monitoring
- Error tracking and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational and research purposes. Users are responsible for ensuring compliance with the terms of service of the websites being scraped. The authors are not responsible for any misuse of this tool.
# BharatX
