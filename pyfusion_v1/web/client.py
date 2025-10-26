import requests
import json

class HttpClient:
    """Built-in HTTP client with requests integration"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.default_headers = {
            'User-Agent': 'PyFusion-HTTP-Client/1.0',
            'Content-Type': 'application/json'
        }
    
    def get(self, endpoint, params=None, headers=None):
        """HTTP GET request"""
        url = self._build_url(endpoint)
        final_headers = {**self.default_headers, **(headers or {})}
        
        try:
            response = self.session.get(url, params=params, headers=final_headers)
            return self._process_response(response)
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    def post(self, endpoint, data=None, headers=None):
        """HTTP POST request"""
        url = self._build_url(endpoint)
        final_headers = {**self.default_headers, **(headers or {})}
        
        try:
            response = self.session.post(url, json=data, headers=final_headers)
            return self._process_response(response)
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    def _build_url(self, endpoint):
        """Build complete URL"""
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return endpoint
    
    def _process_response(self, response):
        """Process HTTP response"""
        try:
            return {
                "status_code": response.status_code,
                "data": response.json(),
                "headers": dict(response.headers),
                "success": 200 <= response.status_code < 300
            }
        except json.JSONDecodeError:
            return {
                "status_code": response.status_code,
                "data": response.text,
                "headers": dict(response.headers),
                "success": 200 <= response.status_code < 300
            }