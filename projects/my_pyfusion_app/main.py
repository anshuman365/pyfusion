#!/usr/bin/env python3
"""
PyFusion Demo Application
A comprehensive demo showing all PyFusion features
"""

import pyfusion
import json
import os
from datetime import datetime

class PyFusionDemo:
    def __init__(self):
        # Initialize components
        self.config = self.load_config()
        self.db = pyfusion.Database(self.config['database'])
        self.server = pyfusion.WebServer(__name__)
        self.http_client = pyfusion.HttpClient()
        self.setup_routes()
        
    def load_config(self):
        """Load application configuration"""
        if os.path.exists('config.json'):
            return pyfusion.FileManager.read_json('config.json')
        return {
            'app_name': 'PyFusion Demo',
            'database': 'demo_db.sqlite',
            'server': {'host': 'localhost', 'port': 8080}
        }
    
    def setup_routes(self):
        """Setup web server routes"""
        
        # Use different endpoint names to avoid conflicts
        @self.server.route('/dashboard')
        def dashboard():
            """Main dashboard"""
            network_status = "Connected" if pyfusion.NetworkTools.check_internet() else "Offline"
            local_ip = pyfusion.NetworkTools.get_local_ip()
            
            html_template = pyfusion.FileManager.read_file('templates/dashboard.html')
            if html_template:
                return html_template.replace('{{ app_name }}', self.config['app_name'])\
                                   .replace('{{ local_ip }}', local_ip)\
                                   .replace('{{ internet_status }}', network_status)\
                                   .replace('{{ server_port }}', str(self.config['server']['port']))
            return f"<h1>{self.config['app_name']}</h1><p>Local IP: {local_ip}</p>"
        
        @self.server.route('/app_health')
        def app_health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "database": "connected",
                    "internet": pyfusion.NetworkTools.check_internet(),
                    "local_ip": pyfusion.NetworkTools.get_local_ip()
                }
            }
        
        @self.server.route('/users')
        def list_users():
            """List all users from database"""
            users = self.db.fetch_all("SELECT * FROM users ORDER BY created_at DESC")
            return {
                "count": len(users),
                "users": users
            }
        
        @self.server.route('/add_user', methods=['POST'])
        def add_user():
            """Add new user via form"""
            from flask import request
            
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            
            # Validate input
            if not username or not email:
                return {"error": "Username and email are required"}, 400
            
            if not pyfusion.Validator.is_email(email):
                return {"error": "Invalid email format"}, 400
            
            # Check if user already exists
            existing = self.db.fetch_one(
                "SELECT id FROM users WHERE username = ? OR email = ?", 
                (username, email)
            )
            
            if existing:
                return {"error": "Username or email already exists"}, 400
            
            # Insert new user
            user_id = self.db.insert('users', {
                'username': username,
                'email': email
            })
            
            return {
                "message": "User created successfully",
                "user_id": user_id,
                "username": username,
                "email": email
            }
        
        @self.server.route('/demo/validation')
        def demo_validation():
            """Demo validation utilities"""
            test_data = {
                "email": "test@example.com",
                "phone": "+1234567890",
                "password": "StrongPass123"
            }
            
            return {
                "email_valid": pyfusion.Validator.is_email(test_data["email"]),
                "phone_valid": pyfusion.Validator.is_phone(test_data["phone"]),
                "password_strong": pyfusion.Validator.is_strong_password(test_data["password"]),
                "test_data": test_data
            }
        
        @self.server.route('/demo/formatting')
        def demo_formatting():
            """Demo formatting utilities"""
            return {
                "date_formatted": pyfusion.Formatter.format_date("2024-01-15"),
                "currency_formatted": pyfusion.Formatter.format_currency(1234.56),
                "data_hash": pyfusion.Formatter.hash_data("hello world")
            }
        
        @self.server.route('/demo/files')
        def demo_files():
            """Demo file operations"""
            # Read CSV file
            csv_data = pyfusion.FileManager.read_csv('data/sample_data.csv')
            
            # Create sample JSON file
            sample_json = {
                "app": "PyFusion Demo",
                "timestamp": datetime.now().isoformat(),
                "data": [{"id": i, "value": f"item_{i}"} for i in range(3)]
            }
            pyfusion.FileManager.write_json('data/sample_output.json', sample_json)
            
            return {
                "csv_data": csv_data,
                "json_created": True,
                "file_contents": pyfusion.FileManager.read_file('data/sample_output.json')
            }
        
        @self.server.route('/demo/network')
        def demo_network():
            """Demo network utilities"""
            return {
                "internet_available": pyfusion.NetworkTools.check_internet(),
                "local_ip": pyfusion.NetworkTools.get_local_ip(),
                "google_dns_available": pyfusion.NetworkTools.is_port_open('8.8.8.8', 53),
                "localhost_ssh": pyfusion.NetworkTools.is_port_open('localhost', 22)
            }
    
    def initialize_database(self):
        """Initialize database with sample data"""
        # Create additional tables if needed
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add sample task if table is empty
        existing_tasks = self.db.fetch_all("SELECT COUNT(*) as count FROM tasks")
        if existing_tasks[0]['count'] == 0:
            self.db.insert('tasks', {
                'title': 'Explore PyFusion',
                'description': 'Learn all the features of PyFusion framework',
                'completed': False
            })
    
    def run(self):
        """Run the application"""
        print(f"🚀 Starting {self.config['app_name']}")
        print("📊 Initializing database...")
        self.initialize_database()
        
        print("🌐 Starting web server...")
        server_config = self.config['server']
        
        print(f"📊 Available routes:")
        print(f"   • http://{server_config['host']}:{server_config['port']}/ (default PyFusion route)")
        print(f"   • http://{server_config['host']}:{server_config['port']}/dashboard (main application)")
        print(f"   • http://{server_config['host']}:{server_config['port']}/app_health (health check)")
        print(f"   • http://{server_config['host']}:{server_config['port']}/users (user list)")
        print(f"   • http://{server_config['host']}:{server_config['port']}/demo/validation (validation demo)")
        print(f"   • http://{server_config['host']}:{server_config['port']}/demo/formatting (formatting demo)")
        
        self.server.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=True
        )

def quick_demo():
    """Quick demonstration of PyFusion features"""
    print("\n" + "="*50)
    print("🚀 PYFUSION QUICK DEMO")
    print("="*50)
    
    # Demo validation
    print("\n📧 VALIDATION DEMO:")
    print(f"Email valid: {pyfusion.Validator.is_email('test@example.com')}")
    print(f"Phone valid: {pyfusion.Validator.is_phone('+1234567890')}")
    print(f"Strong password: {pyfusion.Validator.is_strong_password('StrongPass123')}")
    
    # Demo formatting
    print("\n🎨 FORMATTING DEMO:")
    print(f"Date: {pyfusion.Formatter.format_date('2024-01-15')}")
    print(f"Currency: {pyfusion.Formatter.format_currency(1234.56)}")
    print(f"Hash: {pyfusion.Formatter.hash_data('hello')}")
    
    # Demo network
    print("\n🌐 NETWORK DEMO:")
    print(f"Internet: {pyfusion.NetworkTools.check_internet()}")
    print(f"Local IP: {pyfusion.NetworkTools.get_local_ip()}")
    
    # Demo file operations
    print("\n📁 FILE OPERATIONS DEMO:")
    sample_data = [{"name": "Test", "value": 123}]
    pyfusion.FileManager.write_json('demo_data.json', sample_data)
    print("Created demo_data.json")
    
    print("\n✅ Demo completed! Starting web application...")

if __name__ == "__main__":
    # Run quick demo
    quick_demo()
    
    # Start the main application
    app = PyFusionDemo()
    app.run()