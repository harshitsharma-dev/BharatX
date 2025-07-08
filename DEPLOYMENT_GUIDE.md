# Price Comparison API - Deployment Guide

## 🚀 Deploy to Render (Recommended)

### Important: Python Version Compatibility
This application requires **Python 3.11** for optimal compatibility with all dependencies. A `runtime.txt` file is included to specify this.

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Price Comparison API"
   git branch -M main
   git remote add origin https://github.com/yourusername/price-comparison-api.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `price-comparison-api`
     - **Runtime**: Will auto-detect Python from `runtime.txt`
     - **Build Command**: `chmod +x build.sh && ./build.sh`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 complete_app:app`
     - **Instance Type**: `Free` (for testing) or `Starter` (for production)

3. **Environment Variables** (Optional):
   - `FLASK_ENV=production`
   - `MAX_WORKERS=2`
   - `REQUEST_TIMEOUT=120`

### Option 2: Deploy from Local Files

1. **Create a GitHub repository** and push these files:
   ```
   price-comparison-api/
   ├── complete_app.py
   ├── enhanced_scraping_tool.py
   ├── mcdm_ranker.py
   ├── url_builder.py
   ├── requirements-production.txt
   ├── runtime.txt
   ├── Procfile
   ├── build.sh
   ├── webpages_samples/
   └── README.md
   ```

2. **Follow Option 1 steps**

## 🌐 Alternative Deployment Options

### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Heroku
```bash
# Install Heroku CLI and login
heroku create price-comparison-api
git push heroku main
```

### DigitalOcean App Platform
- Upload your repository to GitHub
- Connect to DigitalOcean App Platform
- Use the same configuration as Render

## 📝 Post-Deployment

### Test Your Deployed API
```bash
# Replace YOUR_APP_URL with your actual deployment URL
curl -X POST https://your-app-name.onrender.com/search \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "iPhone 16 Pro Max", "use_local": true}'
```

### API Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /search` - Main search endpoint
- `GET /countries` - Supported countries
- `POST /demo` - Demo endpoint

### Expected Response
```json
{
  "success": true,
  "query": "iPhone 16 Pro Max",
  "country": "IN",
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
  "response_time_seconds": 2.3
}
```

## 🔧 Production Configuration

### Recommended Settings
- **Workers**: 2-4 (depending on instance size)
- **Timeout**: 120 seconds (for web scraping)
- **Memory**: 512MB minimum
- **Disk**: 1GB (for caching)

### Monitoring
- Use Render's built-in monitoring
- Monitor response times and error rates
- Set up alerts for downtime

## 🚨 Important Notes

1. **Rate Limiting**: The scrapers include built-in rate limiting
2. **Caching**: Local HTML samples work for testing
3. **Timeouts**: Web scraping can take 30-60 seconds
4. **Free Tier**: Render free tier sleeps after 15 minutes of inactivity
5. **Scaling**: Use paid plans for production workloads

## 🎯 Quick Start Commands

```bash
# Test locally before deployment
python complete_app.py

# Test production requirements
pip install -r requirements-production.txt
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 complete_app:app

# Deploy to Render
git push origin main  # Triggers automatic deployment
```

## 🛠️ Troubleshooting Common Deployment Issues

### Build Errors with lxml/Levenshtein on Python 3.13

**Problem**: You see errors like:
```
Failed building wheel for lxml
Failed building wheel for python-Levenshtein
```

**Solution**: This is a known issue with Python 3.13 compatibility. The following fixes are included:

1. **runtime.txt** file specifies Python 3.11.9 (compatible version)
2. **requirements-production.txt** uses compatible package versions
3. **Fallback dependencies** are configured in the code

**If build still fails:**
1. Try using `requirements-fallback.txt` instead:
   ```bash
   # In Render dashboard, change build command to:
   pip install -r requirements-fallback.txt && chmod +x build.sh && ./build.sh
   ```

2. The app will gracefully handle missing dependencies:
   - Uses built-in `html.parser` instead of `lxml`
   - Falls back to basic string comparison if `Levenshtein` is unavailable

### Other Common Issues

**Build Timeout**:
- Increase build timeout in Render settings
- Use lighter dependency versions from `requirements-fallback.txt`

**Memory Issues**:
- Upgrade to Starter plan (512MB RAM)
- Reduce number of workers in start command

**Slow Responses**:
- This is normal for web scraping (30-60 seconds)
- Consider upgrading for better performance

**Free Tier Sleep**:
- Render free tier sleeps after 15 minutes
- Upgrade to paid plan for always-on service
