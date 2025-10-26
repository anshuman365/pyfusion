# PyFusion - All-in-One Python Framework 🚀

![PyFusion Logo](https://raw.githubusercontent.com/anshuman365/pyfusion/refs/heads/main/pyfusion_v1/assets/logo.jpg)

[![PyPI version](https://img.shields.io/pypi/v/pyfusion-v1.svg)](https://pypi.org/project/pyfusion-v1/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyfusion-v1.svg)](https://pypi.org/project/pyfusion-v1/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/pyfusion-v1.svg)](https://pypi.org/project/pyfusion-v1/)

A comprehensive Python framework that bundles web development, database operations, and utility functions into a single, easy-to-use package.

## ✨ Features

### 🌐 Web Framework
- **Built-in Web Server** - Flask-based web framework with easy routing
- **HTTP Client** - Robust HTTP client for API interactions
- **Background Server** - Run servers in background threads
- **API Endpoints** - Easy creation of RESTful APIs
- **HTML Templates** - Serve dynamic HTML content

### 💾 Database Management
- **SQLite Integration** - Built-in database manager with ORM-like interface
- **CRUD Operations** - Simple insert, update, delete, and query methods
- **Key-Value Store** - Generic app data storage
- **Auto-setup** - Automatic table creation and connection management
- **Transaction Support** - Safe database operations

### 🔧 Utilities
- **File Operations** - JSON, CSV, and text file handling
- **Network Tools** - Internet connectivity checks, port scanning, IP detection
- **Data Validation** - Email, phone, password strength validation
- **Data Formatting** - Date, currency, and hashing utilities
- **Security** - Data hashing and input sanitization

### ⚡ Easy to Use
- **Auto-dependency Installation** - Automatically installs required packages
- **Simple Import** - Single import for all components
- **Comprehensive Examples** - Ready-to-run demo code
- **Production Ready** - Well-tested and documented
- **Zero Configuration** - Works out of the box

## 🚀 Quick Installation

```bash
pip install pyfusion-v1
```

📖 Quick Start

Web Server Example

```python
from pyfusion_v1 import WebServer

# Create and configure server
app = WebServer()

@app.route('/hello')
def hello():
    return {"message": "Hello from PyFusion!", "status": "success"}

@app.route('/users', methods=['POST'])
def create_user():
    return {"message": "User created", "method": "POST"}

# Run server
app.run(host='localhost', port=5000)
```

Database Operations

```python
from pyfusion_v1 import Database

# Initialize database
db = Database('my_app.db')

# Insert data
user_id = db.insert('users', {
    'username': 'john_doe',
    'email': 'john@example.com'
})

# Query data
users = db.fetch_all('SELECT * FROM users')
user = db.fetch_one('SELECT * FROM users WHERE id = ?', [1])

# Update data
db.update('users', {'username': 'john_updated'}, 'id = 1')

# Delete data
db.delete('users', 'id = ?', [1])
```

HTTP Client

```python
from pyfusion_v1 import HttpClient

# Create client
client = HttpClient('https://api.example.com')

# Make requests
response = client.get('/users')
response = client.post('/users', {'name': 'John', 'email': 'john@example.com'})
```

File Operations

```python
from pyfusion_v1 import FileManager

# Read/write JSON
data = FileManager.read_json('config.json')
FileManager.write_json('output.json', data)

# Read/write CSV
csv_data = FileManager.read_csv('data.csv')
FileManager.write_csv('output.csv', csv_data)

# Text files
content = FileManager.read_file('README.md')
FileManager.write_file('copy.txt', content)
```

Utilities

```python
from pyfusion_v1 import Validator, Formatter, NetworkTools

# Validation
print(Validator.is_email('test@example.com'))  # True
print(Validator.is_strong_password('Secure123!'))  # True

# Formatting
print(Formatter.format_date('2024-01-15'))  # 15/01/2024
print(Formatter.format_currency(1500.75))   # ₹1,500.75

# Network
print(NetworkTools.check_internet())  # True
print(NetworkTools.get_local_ip())    # 192.168.1.100
```

🏗️ Project Structure

```
pyfusion_v1/
├── __init__.py              # Main package initialization
├── assets/
│   └── logo.jpg            # Project logo
├── web/
│   ├── __init__.py
│   ├── server.py           # WebServer class
│   └── client.py           # HttpClient class
├── database/
│   ├── __init__.py
│   └── manager.py          # Database class
└── utils/
    ├── __init__.py
    ├── file_ops.py         # FileManager class
    ├── network.py          # NetworkTools class
    └── helpers.py          # Validator & Formatter classes
```

📚 Examples

Check the examples/ directory for complete working examples:

· web_app.py - Full web application example
· database_demo.py - Database operations demo
· full_stack.py - Complete full-stack application

Running Examples:

```bash
# Clone the repository
git clone https://github.com/anshuman365/pyfusion.git
cd pyfusion

# Run web application example
python examples/web_app.py

# Run database demo
python examples/database_demo.py

# Run full-stack example
python examples/full_stack.py
```

🔧 Requirements

· Python 3.6 or higher
· Dependencies (automatically installed):
  · Flask >= 2.0.0
  · Requests >= 2.25.0
  · SQLAlchemy >= 1.4.0
  · Jinja2 >= 3.0.0

🎯 Use Cases

· Rapid Prototyping - Quickly build MVP applications
· Learning Tool - Perfect for beginners learning web development
· Internal Tools - Build admin panels and internal dashboards
· API Development - Create RESTful APIs with minimal setup
· Full-Stack Apps - End-to-end web applications
· Scripting - Enhanced scripting with database and web capabilities

🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

Development Setup:

```bash
git clone https://github.com/anshuman365/pyfusion.git
cd pyfusion
pip install -e .
```

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🐛 Bug Reports

If you encounter any bugs or have suggestions, please open an issue.

❓ FAQ

Q: Is PyFusion suitable for production use?
A: Yes! PyFusion is built with production-ready components and includes proper error handling.

Q: Can I use PyFusion with other databases?
A: Currently PyFusion uses SQLite, but you can extend it to support other databases.

Q: How is this different from Flask/Django?
A: PyFusion provides an all-in-one solution with built-in database, HTTP client, and utilities, reducing setup time.

Q: Is there documentation?
A: Comprehensive documentation is available in the README and code examples.

🔗 Links

· PyPI: https://pypi.org/project/pyfusion-v1/
· GitHub: https://github.com/anshuman365/pyfusion
· Issue Tracker: https://github.com/anshuman365/pyfusion/issues

📞 Support

If you need help or have questions:

1. Check the examples directory
2. Open an issue on GitHub
3. Review the source code documentation

---

Made with ❤️ by PyFusion Team

Simplifying Python development, one line at a time.
