# 🛍️ Price Comparison API

**Intelligent multi-site price comparison tool with MCDM ranking**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🚀 Features

- **6 E-commerce Sites**: Amazon, Flipkart, eBay, Walmart, Snapdeal, Shopsy
- **MCDM Ranking**: Smart search relevance prioritization over just price
- **Multi-Country Support**: US, India, UK, Canada, Germany
- **REST API**: Production-ready with monitoring and caching
- **Docker Ready**: Complete containerization support

## 📊 MCDM Intelligence

Our Multi-Criteria Decision Making system prioritizes:
- **75% Search Relevance** - Exact model matches rank higher
- **20% Price** - Competitive pricing consideration  
- **5% Source Reliability** - Trusted marketplace preference

**Example**: Searching "iPhone 16 Pro Max" returns iPhone 16 Pro Max products first, not just the cheapest accessories.

## 🔧 Quick Deploy

### Deploy to Render (1-click)
1. Fork this repository
2. Connect to [Render](https://render.com)
3. Deploy as Web Service
4. Use: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 complete_app:app`

### Local Development
```bash
git clone https://github.com/yourusername/price-comparison-api.git
cd price-comparison-api
pip install -r requirements-production.txt
python complete_app.py
```

## 📡 API Usage

### Search Products
```bash
curl -X POST https://your-app.onrender.com/search \
  -H "Content-Type: application/json" \
  -d '{
    "country": "IN",
    "query": "iPhone 16 Pro Max",
    "max_results": 10
  }'
```

### Response
```json
{
  "success": true,
  "products": [
    {
      "productName": "Apple iPhone 16 Pro Max (Natural Titanium, 256 GB)",
      "price": 135900.0,
      "currency": "INR", 
      "link": "https://amazon.in/...",
      "source": "Amazon.in"
    }
  ],
  "total_results": 15,
  "mcdm_ranked": true
}
```

## 🌍 Supported Countries & Sites

| Country | Sites |
|---------|-------|
| 🇮🇳 India | Amazon.in, Flipkart, eBay.in, Snapdeal, Shopsy |
| 🇺🇸 USA | eBay.com, Walmart |
| 🇬🇧 UK | eBay.co.uk, Amazon.co.uk |
| 🇨🇦 Canada | eBay.ca, Amazon.ca |
| 🇩🇪 Germany | eBay.de, Amazon.de |

## 🛠️ Tech Stack

- **Backend**: Python, Flask, AsyncIO
- **Scraping**: BeautifulSoup, aiohttp
- **Intelligence**: MCDM/TOPSIS ranking, FuzzyWuzzy
- **Production**: Gunicorn, Docker
- **Deployment**: Render, Railway, Heroku compatible

## 📈 Performance

- **Response Time**: 2-5 seconds average
- **Concurrent Requests**: 2-4 workers
- **Success Rate**: 86% scraper reliability
- **Smart Filtering**: Removes low-relevance results

## 🔗 Endpoints

- `GET /` - API information
- `GET /health` - Health check  
- `POST /search` - Main search endpoint
- `GET /countries` - Supported countries
- `POST /demo` - Demo with sample data

## 📝 Environment Variables

```env
FLASK_ENV=production
MAX_WORKERS=2
REQUEST_TIMEOUT=120
```

## 🐳 Docker

```bash
docker build -t price-comparison-api .
docker run -p 5000:5000 price-comparison-api
```

## 🧪 Testing

```bash
python test_deployment.py  # Test all endpoints
python test_all_scrapers_fixed.py  # Test individual scrapers
```

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Project Overview](PROJECT_COMPLETE.md)

## 🤝 Contributing

1. Fork the repository
2. Add new scrapers in `enhanced_scraping_tool.py`
3. Update country configs in `url_builder.py`
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ for intelligent price comparison**
