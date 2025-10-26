#!/usr/bin/env python3
"""
Example: Simple Web Application using PyFusion
"""

import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyfusion import WebServer, Database

def create_app():
    # Initialize components
    app = WebServer("MyApp")
    db = Database()

    @app.route('/users')
    def get_users():
        """Get all users"""
        users = db.fetch_all("SELECT * FROM users")
        return {"users": users, "count": len(users)}

    @app.route('/users/add', methods=['POST'])
    def add_user():
        """Add new user"""
        from flask import request
        data = request.json
        
        if not data or 'username' not in data or 'email' not in data:
            return {"error": "Missing username or email"}, 400
        
        user_id = db.insert('users', {
            'username': data['username'],
            'email': data['email']
        })
        
        return {"message": "User added", "user_id": user_id}

    @app.route('/hello/<name>')
    def hello_name(name):
        """Personalized greeting"""
        return {"message": f"Hello, {name}! Welcome to PyFusion!"}

    return app

if __name__ == "__main__":
    app = create_app()
    print(" PyFusion Web Application Starting...")
    app.run(host='0.0.0.0', port=8080, debug=True)  # Changed port to 8081