#!/usr/bin/env python3
"""
Production-ready Flask application for Render deployment
"""

import os
import logging
from flask import Flask
from complete_app import app, logger

# Configure for production
if __name__ == "__main__":
    # Get port from environment variable or default to 10000 (Render's default)
    port = int(os.environ.get("PORT", 10000))
    
    # Configure logging for production
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting Price Comparison API on port {port}")
    logger.info("Production mode: Ready for deployment")
    
    # Run the app
    app.run(
        host="0.0.0.0",  # Listen on all interfaces
        port=port,       # Use environment port or default
        debug=False,     # Never debug in production
        threaded=True    # Handle multiple requests
    )
