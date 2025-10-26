"""
PyFusion - All-in-One Python Framework
A comprehensive framework bundling web, database, and utility functionalities.
"""

__version__ = "1.0.1"
__author__ = "PyFusion Team"

# Import core components for easy access
from .web.server import WebServer
from .web.client import HttpClient
from .database.manager import Database
from .utils.file_ops import FileManager
from .utils.network import NetworkTools
from .utils.helpers import Validator, Formatter

__all__ = [
    'WebServer',
    'HttpClient', 
    'Database',
    'FileManager',
    'NetworkTools',
    'Validator',
    'Formatter',
]

# Auto-install required dependencies on first import
def _install_dependencies():
    import subprocess
    import sys
    import importlib.util
    
    required_packages = {
        'flask': 'flask>=2.0.0',
        'requests': 'requests>=2.25.0',
        'sqlalchemy': 'sqlalchemy>=1.4.0', 
        'jinja2': 'jinja2>=3.0.0'
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
_install_dependencies()

print(f"🚀 PyFusion v{__version__} loaded successfully!")
print("💡 Available components: WebServer, Database, HttpClient, FileManager, etc.")