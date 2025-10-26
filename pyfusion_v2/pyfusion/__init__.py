"""
PyFusion v2.0 - All-in-One Python Framework
A comprehensive framework bundling web, database, AI, and utility functionalities.
"""

__version__ = "2.0.0"
__author__ = "PyFusion Team"
__license__ = "MIT"

# Import core components for easy access
from .core.config import Config
from .core.logging import Logger, log
from .core.security import Security
from .core.exceptions import *

# Web framework
from .web.server import WebServer
from .web.client import HttpClient
from .web.middleware import Middleware
from .web.rate_limiter import RateLimiter

# Database
from .database.manager import Database
from .database.connection_pool import ConnectionPool

# Authentication
from .auth.manager import AuthManager
from .auth.jwt import JWTManager

# Utilities
from .utils.file_ops import FileManager
from .utils.network import NetworkTools
from .utils.helpers import Validator, Formatter
from .utils.cache import Cache
from .utils.analytics import Analytics

# Tasks
from .tasks.queue import TaskQueue
from .tasks.scheduler import Scheduler

# AI/ML
from .ai.ml import AIModule

# Testing
from .testing.testcase import TestCase
from .testing.client import TestClient

__all__ = [
    # Core
    'Config', 'Logger', 'log', 'Security',
    
    # Web
    'WebServer', 'HttpClient', 'Middleware', 'RateLimiter',
    
    # Database
    'Database', 'ConnectionPool',
    
    # Auth
    'AuthManager', 'JWTManager',
    
    # Utilities
    'FileManager', 'NetworkTools', 'Validator', 'Formatter', 
    'Cache', 'Analytics',
    
    # Tasks
    'TaskQueue', 'Scheduler',
    
    # AI/ML
    'AIModule',
    
    # Testing
    'TestCase', 'TestClient',
]

# Auto-install required dependencies on first import
def _install_dependencies():
    import subprocess
    import sys
    import importlib.util
    
    required_packages = {
        'flask': 'flask>=2.3.0',
        'requests': 'requests>=2.31.0',
        'sqlalchemy': 'sqlalchemy>=2.0.0',
        'jinja2': 'jinja2>=3.1.0',
        'pyjwt': 'pyjwt>=2.8.0',
        'numpy': 'numpy>=1.24.0',
        'pandas': 'pandas>=2.0.0',
    }
    
    for package, install_spec in required_packages.items():
        if importlib.util.find_spec(package) is None:
            print(f"📦 Installing {package}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", install_spec
                ])
                print(f"✅ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                print(f"💡 Please run: pip install {install_spec}")

# Install dependencies on first import
try:
    _install_dependencies()
except Exception as e:
    print(f"⚠️ Dependency installation skipped: {e}")

print(f"🚀 PyFusion v{__version__} loaded successfully!")
print("💡 Available components: WebServer, Database, AuthManager, AIModule, etc.")
print("📚 Documentation: https://pyfusion.readthedocs.io/")