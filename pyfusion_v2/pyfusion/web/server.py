"""
Enhanced WebServer with middleware support and better routing
"""
from flask import Flask, request, jsonify, render_template_string
import threading
import time
from typing import Callable, Dict, List, Optional
from ..core.exceptions import PyFusionError
from ..core.logging import log
from ..core.security import Security
from .middleware import Middleware

class WebServer:
    """Enhanced web server with middleware and better routing"""
    
    def __init__(self, name: str = __name__):
        self.app = Flask(name)
        self.middleware = Middleware()
        self.routes: Dict[str, str] = {}
        self._request_count = 0
        self._setup_error_handlers()
        self._setup_middleware()
    
    def _setup_error_handlers(self):
        """Setup global error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                "error": "Resource not found",
                "path": request.path,
                "method": request.method
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            log.error(f"Internal server error: {error}")
            return jsonify({
                "error": "Internal server error",
                "message": str(error) if self.app.debug else "Something went wrong"
            }), 500
        
        @self.app.errorhandler(PyFusionError)
        def handle_pyfusion_error(error):
            return jsonify({
                "error": error.__class__.__name__,
                "message": str(error)
            }), 400
    
    def _setup_middleware(self):
        """Setup default middleware"""
        @self.app.before_request
        def before_middleware():
            self.middleware.execute_before(request)
            self._request_count += 1
        
        @self.app.after_request
        def after_middleware(response):
            return self.middleware.execute_after(request, response)
    
    def route(self, path: str, methods: List[str] = None, 
              endpoint: str = None, rate_limit: int = None):
        """Enhanced route decorator with auto endpoint naming"""
        if methods is None:
            methods = ['GET']
        
        def decorator(func: Callable):
            # Generate unique endpoint name if not provided
            if endpoint is None:
                endpoint_name = f"{func.__module__}.{func.__name__}"
            else:
                endpoint_name = endpoint
            
            # Apply rate limiting if specified
            if rate_limit:
                func = self._apply_rate_limit(func, rate_limit)
            
            self.app.route(path, methods=methods, endpoint=endpoint_name)(func)
            self.routes[path] = endpoint_name
            return func
        
        return decorator
    
    def _apply_rate_limit(self, func: Callable, limit: int) -> Callable:
        """Apply rate limiting to function"""
        from .rate_limiter import RateLimiter
        limiter = RateLimiter(limit)
        
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            if not limiter.check_limit(client_ip):
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {limit} requests per minute allowed"
                }), 429
            return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        return wrapper
    
    def add_middleware(self, middleware_func: Callable, position: str = "before"):
        """Add custom middleware"""
        self.middleware.add(middleware_func, position)
    
    def html(self, template: str, route_path: str = "/html"):
        """Serve HTML content with enhanced template support"""
        @self.route(route_path)
        def serve_html():
            return render_template_string(template)
    
    def api(self, path: str, data_func: Callable, methods: List[str] = None):
        """Create API endpoint with automatic JSON response"""
        if methods is None:
            methods = ['GET', 'POST']
        
        @self.route(path, methods=methods)
        def api_endpoint():
            try:
                # Sanitize input data
                sanitized_data = Security.sanitize_input(request.json if request.is_json else request.form)
                result = data_func(request, sanitized_data)
                return jsonify(result)
            except Exception as e:
                log.error(f"API error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def get_routes(self) -> Dict[str, str]:
        """Get all registered routes"""
        return self.routes.copy()
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """Run the web server with configuration support"""
        from ..core.config import Config
        config = Config()
        
        host = host or config.get('server.host', 'localhost')
        port = port or config.get('server.port', 5000)
        debug = debug or config.get('server.debug', False)
        
        log.info(f" PyFusion Server starting at http://{host}:{port}")
        log.info(f" Registered routes: {len(self.routes)}")
        
        self.app.run(host=host, port=port, debug=debug)
    
    def run_background(self, host: str = None, port: int = None):
        """Run server in background thread"""
        def run():
            self.run(host=host, port=port, debug=False)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
        host = host or 'localhost'
        port = port or 5000
        log.info(f" PyFusion Server running in background: http://{host}:{port}")
        return thread