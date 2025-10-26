# PyFusion - All-in-One Python Framework

A comprehensive Python framework that bundles web development, database operations, and utility functions into a single, easy-to-use package.

## Features

- **Built-in Web Server** - Flask-based web framework
- **HTTP Client** - Easy API requests
- **Database Manager** - SQLite database operations
- **File Operations** - JSON, CSV, text file handling
- **Network Utilities** - Connectivity checks, validations
- **Data Helpers** - Validation, formatting, hashing

## Quick Start

```python
from pyfusion import WebServer, Database

# Create web server
app = WebServer()
db = Database()

@app.route('/hello')
def hello():
    return {"message": "Hello from PyFusion!"}

app.run(port=5000)