#!/usr/bin/env python3
"""
Basic PyFusion v2.0 Example
"""

import pyfusion
from pyfusion.core.config import Config

# Initialize configuration
config = Config()
config.set('app.name', 'PyFusion Demo App')

# Create web server
app = pyfusion.WebServer(__name__)

@app.route('/')
def home():
    return {
        "message": "Welcome to PyFusion v2.0!",
        "version": pyfusion.__version__,
        "app": config.get('app.name')
    }

@app.route('/users')
def get_users():
    db = pyfusion.Database()
    users = db.fetch_all("SELECT * FROM users")
    return {"users": users}

@app.route('/health')
def health_check():
    analytics = pyfusion.Analytics()
    return {
        "status": "healthy",
        "performance": analytics.get_performance_metrics()
    }

if __name__ == "__main__":
    app.run(port=8000, debug=True)