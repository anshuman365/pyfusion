from flask import Flask, request, jsonify, render_template_string
import threading
import os

class WebServer:
    """Built-in web server with Flask integration"""
    
    def __init__(self, name=__name__):
        self.app = Flask(name)
        self.routes = {}
        self._setup_default_routes()
    
    def _setup_default_routes(self):
        """Setup default routes"""
        @self.app.route('/')
        def home():
            return jsonify({
                "message": "PyFusion Server Running",
                "status": "active",
                "framework": "PyFusion"
            })
        
        @self.app.route('/health')
        def health():
            return jsonify({"status": "healthy"})
    
    def route(self, path, methods=['GET']):
        """Decorator to add routes"""
        def decorator(func):
            self.app.route(path, methods=methods)(func)
            self.routes[path] = func.__name__
            return func
        return decorator
    
    def html(self, template):
        """Serve HTML content"""
        @self.app.route('/html')
        def serve_html():
            return render_template_string(template)
    
    def api(self, path, data_func):
        """Create API endpoint"""
        @self.app.route(path, methods=['GET', 'POST'])
        def api_endpoint():
            return jsonify(data_func(request))
    
    def run(self, host='localhost', port=5000, debug=False):
        """Run the web server"""
        print(f"🚀 PyFusion Server starting at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def run_background(self, host='localhost', port=5000):
        """Run server in background thread"""
        def run():
            self.app.run(host=host, port=port, debug=False, use_reloader=False)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        print(f"🔄 PyFusion Server running in background: http://{host}:{port}")
        return thread