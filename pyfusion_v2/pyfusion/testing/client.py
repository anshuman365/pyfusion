"""
Test client for PyFusion applications
"""
import requests
from typing import Dict, Any, Optional
from ..core.logging import log

class TestClient:
    """Enhanced test client for API testing"""
    
    def __init__(self, base_url: str = 'http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PyFusion-Test-Client/1.0'
        }
    
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.auth_token = token
        self.default_headers['Authorization'] = f'Bearer {token}'
    
    def clear_auth(self):
        """Clear authentication"""
        self.auth_token = None
        if 'Authorization' in self.default_headers:
            del self.default_headers['Authorization']
    
    def request(self, method: str, endpoint: str, 
               data: Dict[str, Any] = None, 
               headers: Dict[str, str] = None,
               expected_status: int = 200) -> Dict[str, Any]:
        """Make HTTP request with enhanced error handling"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        final_headers = {**self.default_headers, **(headers or {})}
        
        try:
            response = self.session.request(
                method, url, json=data, headers=final_headers
            )
            
            # Check status code
            if response.status_code != expected_status:
                log.warning(f"Unexpected status: {response.status_code} (expected {expected_status})")
            
            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {'text': response.text}
            
            return {
                'status_code': response.status_code,
                'data': response_data,
                'headers': dict(response.headers),
                'success': 200 <= response.status_code < 300
            }
            
        except requests.RequestException as e:
            log.error(f"Request failed: {e}")
            return {
                'status_code': 0,
                'data': {'error': str(e)},
                'headers': {},
                'success': False
            }
    
    def get(self, endpoint: str, headers: Dict[str, str] = None,
            expected_status: int = 200) -> Dict[str, Any]:
        """Make GET request"""
        return self.request('GET', endpoint, headers=headers, expected_status=expected_status)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None,
             headers: Dict[str, str] = None,
             expected_status: int = 201) -> Dict[str, Any]:
        """Make POST request"""
        return self.request('POST', endpoint, data=data, headers=headers, expected_status=expected_status)
    
    def put(self, endpoint: str, data: Dict[str, Any] = None,
            headers: Dict[str, str] = None,
            expected_status: int = 200) -> Dict[str, Any]:
        """Make PUT request"""
        return self.request('PUT', endpoint, data=data, headers=headers, expected_status=expected_status)
    
    def delete(self, endpoint: str, headers: Dict[str, str] = None,
               expected_status: int = 204) -> Dict[str, Any]:
        """Make DELETE request"""
        return self.request('DELETE', endpoint, headers=headers, expected_status=expected_status)
    
    def health_check(self) -> bool:
        """Perform health check"""
        result = self.get('/health')
        return result['success'] and result['data'].get('status') == 'healthy'
    
    def wait_for_server(self, timeout: int = 30, interval: int = 1) -> bool:
        """Wait for server to be ready"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.health_check():
                log.info("Server is ready")
                return True
            log.info("Waiting for server...")
            time.sleep(interval)
        
        log.error("Server did not become ready in time")
        return False