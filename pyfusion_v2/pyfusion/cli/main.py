"""
Command Line Interface for PyFusion
"""
import argparse
import sys
import os
import shutil
from typing import List, Optional
from ..core.logging import log
from ..core.config import Config
from ..database.manager import Database
from ..database.migrations import MigrationManager
from ..web.server import WebServer

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='PyFusion CLI Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create project command
    create_parser = subparsers.add_parser('create-project', help='Create new project')
    create_parser.add_argument('project_name', help='Name of the project')
    create_parser.add_argument('--template', choices=['basic', 'web', 'api'], 
                              default='basic', help='Project template')
    
    # Run server command
    run_parser = subparsers.add_parser('run-server', help='Run web server')
    run_parser.add_argument('--host', default='localhost', help='Server host')
    run_parser.add_argument('--port', type=int, default=5000, help='Server port')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Database commands
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_subparsers = db_parser.add_subparsers(dest='db_command')
    
    # DB init
    db_init_parser = db_subparsers.add_parser('init', help='Initialize database')
    
    # DB migrate
    db_migrate_parser = db_subparsers.add_parser('migrate', help='Run migrations')
    db_migrate_parser.add_argument('--target', help='Target migration version')
    
    # DB rollback
    db_rollback_parser = db_subparsers.add_parser('rollback', help='Rollback migrations')
    db_rollback_parser.add_argument('--steps', type=int, default=1, help='Number of migrations to rollback')
    
    # DB status
    db_status_parser = db_subparsers.add_parser('status', help='Show migration status')
    
    # Create migration
    db_create_parser = db_subparsers.add_parser('create-migration', help='Create new migration')
    db_create_parser.add_argument('name', help='Migration name')
    db_create_parser.add_argument('--description', help='Migration description')
    
    # Create API command
    api_parser = subparsers.add_parser('create-api', help='Create API endpoint')
    api_parser.add_argument('endpoint_name', help='Name of the API endpoint')
    api_parser.add_argument('--methods', default='GET,POST', help='HTTP methods')
    
    # Version command
    subparsers.add_parser('version', help='Show PyFusion version')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'create-project':
            return create_project(args.project_name, args.template)
        elif args.command == 'run-server':
            return run_server(args.host, args.port, args.debug)
        elif args.command == 'db':
            return handle_db_command(args)
        elif args.command == 'create-api':
            return create_api_endpoint(args.endpoint_name, args.methods)
        elif args.command == 'version':
            return show_version()
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        log.error(f"Command failed: {e}")
        return 1

def create_project(project_name: str, template: str) -> int:
    """Create new PyFusion project"""
    try:
        if os.path.exists(project_name):
            print(f"Error: Directory '{project_name}' already exists")
            return 1
        
        # Create project directory
        os.makedirs(project_name)
        
        # Create project structure based on template
        if template == 'basic':
            create_basic_project(project_name)
        elif template == 'web':
            create_web_project(project_name)
        elif template == 'api':
            create_api_project(project_name)
        
        print(f"✅ Created project: {project_name}")
        print(f"📁 Project structure:")
        print_tree(project_name)
        print(f"\n🚀 Get started:")
        print(f"   cd {project_name}")
        print(f"   python app.py")
        
        return 0
    except Exception as e:
        print(f"Error creating project: {e}")
        return 1

def create_basic_project(project_dir: str):
    """Create basic project structure"""
    # Create main app file
    app_content = '''#!/usr/bin/env python3
"""
Basic PyFusion Application
"""

import pyfusion

# Initialize components
db = pyfusion.Database()
app = pyfusion.WebServer(__name__)

@app.route('/')
def home():
    return {
        "message": "Welcome to PyFusion!",
        "version": pyfusion.__version__,
        "database": "connected" if db else "disconnected"
    }

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    app.run(debug=True)
'''
    
    with open(os.path.join(project_dir, 'app.py'), 'w') as f:
        f.write(app_content)
    
    # Create requirements.txt
    requirements = '''pyfusion>=2.0.0
flask>=2.3.0
'''
    
    with open(os.path.join(project_dir, 'requirements.txt'), 'w') as f:
        f.write(requirements)
    
    # Create README
    readme = f'''# {os.path.basename(project_dir)}

A PyFusion application.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
```

1. Run the application:
   ```bash
   python app.py
   ```
2. Open http://localhost:5000 in your browser
   '''
   with open(os.path.join(project_dir, 'README.md'), 'w') as f:
   f.write(readme)

def create_web_project(project_dir: str):
"""Create web project with templates"""
create_basic_project(project_dir)

<html>
<head>
    <title>{% block title %}PyFusion App{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{% block header %}PyFusion Web App{% endblock %}</h1>
        </div>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
'''

{% block title %}Home - PyFusion App{% endblock %}

{% block header %}Welcome to PyFusion!{% endblock %}

{% block content %}
<h2>Hello World!</h2>
<p>This is your PyFusion web application.</p>
<div>
<a href="/health">Health Check</a> |
<a href="/api/users">Users API</a>
</div>
{%endblock %}
'''

def create_api_project(project_dir: str):
"""Create API-focused project"""
create_basic_project(project_dir)

"""
PyFusion API Application
"""

import pyfusion
from pyfusion.auth.manager import AuthManager

Initialize components

db = pyfusion.Database()
auth= AuthManager(db)
app= pyfusion.WebServer(name)

@app.route('/')
def home():
return {"message": "API Server Running", "version": pyfusion.version}

@app.route('/api/health')
def health():
return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.route('/api/users', methods=['GET'])
def get_users():
users = db.fetch_all("SELECT id, username, email FROM users")
return {"users": users}

@app.route('/api/users', methods=['POST'])
def create_user():
from flask import request

if name == "main":
app.run(debug=True)
'''

def run_server(host: str, port: int, debug: bool) -> int:
"""Run web server"""
try:
# Try to import app from current directory
import importlib.util
spec = importlib.util.spec_from_file_location("app", "app.py")
if spec is None:
print("Error: app.py not found in current directory")
return 1

def handle_db_command(args) -> int:
"""Handle database commands"""
try:
migration_manager = MigrationManager()

def db_init() -> int:
"""Initialize database"""
try:
db = Database()
print("✅ Database initialized")
return 0
except Exception as e:
print(f"Error initializing database: {e}")
return 1

def db_status(migration_manager: MigrationManager) -> int:
"""Show migration status"""
status = migration_manager.status()

def create_api_endpoint(endpoint_name: str, methods: str) -> int:
"""Create API endpoint template"""
try:
endpoint_file = f"api_{endpoint_name}.py"

API Endpoint: {endpoint_name}
Methods:{methods}
"""

import pyfusion
from pyfusion.auth.decorators import requires_auth

Initialize components

db = pyfusion.Database()
app= pyfusion.WebServer(name)

@app.route('/api/{endpoint_name}', methods={method_list})
def handle_{endpoint_name}():
"""
Handle {endpoint_name} endpoint
"""
from flask import request

if name == "main":
# Test the endpoint
app.run(debug=True)
'''

def show_version() -> int:
"""Show PyFusion version"""
import pyfusion
print(f"PyFusion v{pyfusion.version}")
return 0

def print_tree(directory: str, prefix: str = ""):
"""Print directory tree"""
contents = os.listdir(directory)
pointers = ["├── "] * (len(contents) - 1) + ["└── "]

if name == "main":
sys.exit(main())