import socket
import requests
from urllib.parse import urlparse

class NetworkTools:
    """Built-in network utilities"""
    
    @staticmethod
    def check_internet():
        """Check internet connectivity"""
        try:
            requests.get('https://www.google.com', timeout=5)
            return True
        except:
            return False
    
    @staticmethod
    def get_local_ip():
        """Get local IP address"""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "127.0.0.1"
    
    @staticmethod
    def is_port_open(host, port):
        """Check if port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    @staticmethod
    def validate_url(url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False