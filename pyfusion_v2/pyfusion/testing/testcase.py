"""
Testing framework for PyFusion applications
"""
import unittest
import tempfile
import os
from typing import Dict, Any, Callable
from ..core.exceptions import PyFusionError
from ..core.logging import log
from ..web.server import WebServer
from ..database.manager import Database

class TestCase(unittest.TestCase):
    """Base test case for PyFusion applications"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self._setup_test_database()
        self._setup_test_server()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if hasattr(self, 'db'):
            self.db.close()
        if hasattr(self, 'server'):
            pass  # Server cleanup if needed
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _setup_test_database(self):
        """Set up test database"""
        db_path = os.path.join(self.test_dir, 'test_db.sqlite')
        self.db = Database(db_path)
    
    def _setup_test_server(self):
        """Set up test web server"""
        self.server = WebServer(__name__ + '_test')
        self.client = self.server.app.test_client()
    
    def assertResponse(self, response, status_code: int = 200, 
                      content_type: str = 'application/json'):
        """Assert response has expected status code and content type"""
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.content_type, content_type)
    
    def assertJsonEqual(self, response, expected: Dict[str, Any]):
        """Assert JSON response matches expected data"""
        data = response.get_json()
        self.assertEqual(data, expected)
    
    def assertJsonContains(self, response, expected: Dict[str, Any]):
        """Assert JSON response contains expected data"""
        data = response.get_json()
        for key, value in expected.items():
            self.assertIn(key, data)
            self.assertEqual(data[key], value)
    
    def create_test_user(self, username: str = 'testuser', 
                        email: str = 'test@example.com',
                        password: str = 'testpass123') -> Dict[str, Any]:
        """Create test user"""
        from ..auth.manager import AuthManager
        auth = AuthManager(self.db)
        return auth.create_user(username, email, password)
    
    def login_test_user(self, client, username: str = 'testuser',
                       password: str = 'testpass123') -> str:
        """Login test user and return session token"""
        from ..auth.manager import AuthManager
        auth = AuthManager(self.db)
        
        user = auth.authenticate(username, password)
        session_token = auth.create_session(user['id'])
        
        return session_token
    
    def mock_database(self, table: str, data: Dict[str, Any]) -> int:
        """Insert mock data into database"""
        return self.db.insert(table, data)
    
    def assertDatabaseHas(self, table: str, where: str, params: tuple = None) -> bool:
        """Assert database has record matching conditions"""
        result = self.db.fetch_one(f"SELECT * FROM {table} WHERE {where}", params)
        self.assertIsNotNone(result, f"No record found in {table} matching {where}")
        return True
    
    def assertDatabaseCount(self, table: str, expected_count: int, 
                          where: str = None, params: tuple = None) -> bool:
        """Assert database table has expected number of records"""
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        result = self.db.fetch_one(query, params)
        actual_count = result['count'] if result else 0
        self.assertEqual(actual_count, expected_count, 
                        f"Expected {expected_count} records in {table}, got {actual_count}")
        return True

class APITestCase(TestCase):
    """Test case specifically for API testing"""
    
    def setUp(self):
        super().setUp()
        self.api_base = '/api/v1'
    
    def get(self, endpoint: str, headers: Dict[str, str] = None):
        """Make GET request to API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        return self.client.get(url, headers=headers)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None, 
             headers: Dict[str, str] = None):
        """Make POST request to API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        return self.client.post(url, json=data, headers=headers)
    
    def put(self, endpoint: str, data: Dict[str, Any] = None,
            headers: Dict[str, str] = None):
        """Make PUT request to API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        return self.client.put(url, json=data, headers=headers)
    
    def delete(self, endpoint: str, headers: Dict[str, str] = None):
        """Make DELETE request to API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        return self.client.delete(url, headers=headers)
    
    def assertApiSuccess(self, response, message: str = None):
        """Assert API response indicates success"""
        self.assertResponse(response, 200)
        data = response.get_json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        if message:
            self.assertIn('message', data)
            self.assertEqual(data['message'], message)
    
    def assertApiError(self, response, status_code: int = 400, 
                      error_type: str = None):
        """Assert API response indicates error"""
        self.assertResponse(response, status_code)
        data = response.get_json()
        self.assertIn('error', data)
        if error_type:
            self.assertEqual(data['error'], error_type)

class DatabaseTestCase(TestCase):
    """Test case specifically for database testing"""
    
    def setUp(self):
        super().setUp()
        self._setup_test_tables()
    
    def _setup_test_tables(self):
        """Set up test-specific tables"""
        # Create additional test tables if needed
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS test_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def assertTableExists(self, table_name: str):
        """Assert that table exists in database"""
        result = self.db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
            (table_name,)
        )
        self.assertIsNotNone(result, f"Table '{table_name}' does not exist")
    
    def assertColumnExists(self, table_name: str, column_name: str):
        """Assert that column exists in table"""
        result = self.db.fetch_all(f"PRAGMA table_info({table_name})")
        columns = [row['name'] for row in result]
        self.assertIn(column_name, columns, 
                     f"Column '{column_name}' not found in table '{table_name}'")