"""
Enhanced HTTP client with retry mechanism and better error handling
"""
import requests
import json
import time
import os
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
from ..core.exceptions import NetworkError
from ..core.logging import log

class HttpClient:
    """Enhanced HTTP client with retry mechanism and session management"""
    
    def __init__(self, base_url: str = None, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.default_headers = {
            'User-Agent': 'PyFusion-HTTP-Client/2.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Setup retry strategy
        self._setup_retry_strategy()
    
    def _setup_retry_strategy(self):
        """Setup retry strategy for HTTP requests"""
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def set_auth_token(self, token: str, auth_type: str = 'Bearer'):
        """Set authentication token"""
        self.default_headers['Authorization'] = f'{auth_type} {token}'
    
    def set_base_headers(self, headers: Dict[str, str]):
        """Set base headers for all requests"""
        self.default_headers.update(headers)
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, 
            headers: Dict[str, str] = None, timeout: int = None) -> Dict[str, Any]:
        """Enhanced HTTP GET request with retry"""
        return self._request('GET', endpoint, params=params, headers=headers, timeout=timeout)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None,
             headers: Dict[str, str] = None, timeout: int = None) -> Dict[str, Any]:
        """Enhanced HTTP POST request with retry"""
        return self._request('POST', endpoint, data=data, headers=headers, timeout=timeout)
    
    def put(self, endpoint: str, data: Dict[str, Any] = None,
            headers: Dict[str, str] = None, timeout: int = None) -> Dict[str, Any]:
        """Enhanced HTTP PUT request with retry"""
        return self._request('PUT', endpoint, data=data, headers=headers, timeout=timeout)
    
    def patch(self, endpoint: str, data: Dict[str, Any] = None,
              headers: Dict[str, str] = None, timeout: int = None) -> Dict[str, Any]:
        """Enhanced HTTP PATCH request with retry"""
        return self._request('PATCH', endpoint, data=data, headers=headers, timeout=timeout)
    
    def delete(self, endpoint: str, headers: Dict[str, str] = None,
               timeout: int = None) -> Dict[str, Any]:
        """Enhanced HTTP DELETE request with retry"""
        return self._request('DELETE', endpoint, headers=headers, timeout=timeout)
    
    def _request(self, method: str, endpoint: str, data: Dict[str, Any] = None,
                 params: Dict[str, Any] = None, headers: Dict[str, str] = None,
                 timeout: int = None) -> Dict[str, Any]:
        """Execute HTTP request with enhanced error handling and retry"""
        url = self._build_url(endpoint)
        final_headers = {**self.default_headers, **(headers or {})}
        final_timeout = timeout or self.timeout
        
        # Track request for logging
        request_id = f"{method}_{endpoint}_{int(time.time())}"
        log.debug(f"HTTP Request [{request_id}]: {method} {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=final_headers,
                timeout=final_timeout,
                allow_redirects=True
            )
            
            return self._process_response(response, request_id)
            
        except requests.exceptions.Timeout:
            log.error(f"Request [{request_id}] timed out after {final_timeout}s")
            return {
                "error": "Request timeout",
                "status_code": 408,
                "success": False,
                "request_id": request_id
            }
        except requests.exceptions.ConnectionError:
            log.error(f"Request [{request_id}] connection error")
            return {
                "error": "Connection error",
                "status_code": 503,
                "success": False,
                "request_id": request_id
            }
        except requests.exceptions.RequestException as e:
            log.error(f"Request [{request_id}] failed: {e}")
            return {
                "error": str(e),
                "status_code": 500,
                "success": False,
                "request_id": request_id
            }
    
    def _build_url(self, endpoint: str) -> str:
        """Build complete URL"""
        if self.base_url:
            return urljoin(self.base_url, endpoint)
        return endpoint
    
    def _process_response(self, response: requests.Response, request_id: str) -> Dict[str, Any]:
        """Process HTTP response with enhanced information"""
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = response.text
        
        # Log response for debugging
        log.debug(f"HTTP Response [{request_id}]: {response.status_code}")
        
        result = {
            "status_code": response.status_code,
            "data": response_data,
            "headers": dict(response.headers),
            "success": 200 <= response.status_code < 300,
            "request_id": request_id,
            "elapsed_time": response.elapsed.total_seconds()
        }
        
        # Add rate limit information if available
        if 'X-RateLimit-Limit' in response.headers:
            result['rate_limit'] = {
                'limit': response.headers.get('X-RateLimit-Limit'),
                'remaining': response.headers.get('X-RateLimit-Remaining'),
                'reset': response.headers.get('X-RateLimit-Reset')
            }
        
        return result
    
    def download_file(self, endpoint: str, save_path: str,
                     headers: Dict[str, str] = None) -> bool:
        """Download file from URL"""
        url = self._build_url(endpoint)
        final_headers = {**self.default_headers, **(headers or {})}
        
        try:
            response = self.session.get(url, headers=final_headers, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            log.info(f"File downloaded successfully: {save_path}")
            return True
            
        except Exception as e:
            log.error(f"File download failed: {e}")
            return False
    
    def upload_file(self, endpoint: str, file_path: str, 
                   field_name: str = 'file',
                   additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Upload file to server"""
        url = self._build_url(endpoint)
        
        try:
            with open(file_path, 'rb') as f:
                files = {field_name: (os.path.basename(file_path), f)}
                data = additional_data or {}
                
                response = self.session.post(url, files=files, data=data)
                return self._process_response(response, f"UPLOAD_{os.path.basename(file_path)}")
                
        except Exception as e:
            log.error(f"File upload failed: {e}")
            return {
                "error": str(e),
                "status_code": 500,
                "success": False
            }
    
    def health_check(self, endpoint: str = '/health') -> bool:
        """Perform health check"""
        result = self.get(endpoint)
        return result.get('success', False) and result.get('status_code') == 200
    
    def close(self):
        """Close HTTP session"""
        self.session.close()

# Async HTTP Client (for future async support)
class AsyncHttpClient:
    """Async HTTP client (placeholder for future implementation)"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url
        log.warning("AsyncHttpClient is a placeholder. Use HttpClient for now.")
    
    async def get(self, endpoint: str, **kwargs):
        """Async GET request"""
        raise NotImplementedError("Async support coming in future version")
    
    async def post(self, endpoint: str, **kwargs):
        """Async POST request"""
        raise NotImplementedError("Async support coming in future version")