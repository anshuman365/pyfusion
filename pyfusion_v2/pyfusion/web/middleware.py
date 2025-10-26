"""
Middleware support for web server
"""
from typing import Callable, List
from flask import Request, Response
from ..core.logging import log
from ..core.security import Security

class Middleware:
    """Middleware manager for request/response processing"""
    
    def __init__(self):
        self.before_middleware: List[Callable] = []
        self.after_middleware: List[Callable] = []
        self._setup_default_middleware()
    
    def _setup_default_middleware(self):
        """Setup default middleware"""
        self.add(self._security_headers, "after")
        self.add(self._logging_middleware, "before")
    
    def add(self, middleware_func: Callable, position: str = "before"):
        """Add middleware function"""
        if position == "before":
            self.before_middleware.append(middleware_func)
        elif position == "after":
            self.after_middleware.append(middleware_func)
        else:
            raise ValueError("Position must be 'before' or 'after'")
    
    def execute_before(self, request: Request):
        """Execute all before middleware"""
        for middleware in self.before_middleware:
            try:
                middleware(request)
            except Exception as e:
                log.error(f"Middleware error: {e}")
                continue
    
    def execute_after(self, request: Request, response: Response) -> Response:
        """Execute all after middleware"""
        current_response = response
        for middleware in self.after_middleware:
            try:
                result = middleware(request, current_response)
                if result is not None:
                    current_response = result
            except Exception as e:
                log.error(f"Middleware error: {e}")
                continue
        return current_response
    
    def _security_headers(self, request: Request, response: Response) -> Response:
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    def _logging_middleware(self, request: Request):
        """Log request details"""
        log.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")