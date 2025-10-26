"""
Enhanced database manager with connection pooling and thread safety
"""
import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple
from ..core.exceptions import DatabaseError
from ..core.logging import log
from ..core.security import Security
from .connection_pool import ConnectionPool

class Database:
    """Enhanced database manager with connection pooling"""
    
    _instances = {}
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = None):
        from ..core.config import Config
        config = Config()
        
        db_path = db_path or config.get('database.path', 'pyfusion_db.sqlite')
        
        with cls._lock:
            if db_path not in cls._instances:
                cls._instances[db_path] = super(Database, cls).__new__(cls)
            return cls._instances[db_path]
    
    def __init__(self, db_path: str = None):
        if not hasattr(self, '_initialized'):
            from ..core.config import Config
            config = Config()
            
            self.db_path = db_path or config.get('database.path', 'pyfusion_db.sqlite')
            self.pool_size = config.get('database.pool_size', 5)
            self.connection_pool = ConnectionPool(self.db_path, self.pool_size)
            self._setup_tables()
            self._initialized = True
    
    def _setup_tables(self):
        """Create default tables with enhanced schema"""
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table with authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # App data table (generic key-value store)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_data (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    data_type TEXT DEFAULT 'text',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    user_id INTEGER,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def execute(self, query: str, params: Tuple = None, 
                sanitize: bool = True) -> Optional[sqlite3.Cursor]:
        """Execute SQL query with enhanced error handling"""
        if sanitize:
            Security.prevent_sql_injection(query, params)
        
        try:
            with self.connection_pool.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            log.error(f"Database error: {e} - Query: {query}")
            raise DatabaseError(f"Database operation failed: {e}")
    
    def fetch_all(self, query: str, params: Tuple = None) -> List[Dict[str, Any]]:
        """Fetch all results with dict factory"""
        cursor = self.execute(query, params)
        if cursor:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return []
    
    def fetch_one(self, query: str, params: Tuple = None) -> Optional[Dict[str, Any]]:
        """Fetch single result"""
        cursor = self.execute(query, params)
        if cursor:
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
        return None
    
    def insert(self, table: str, data: Dict[str, Any], 
               sanitize: bool = True) -> Optional[int]:
        """Insert data into table with sanitization"""
        if sanitize:
            data = Security.sanitize_input(data)
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.execute(query, tuple(data.values()), sanitize=False)
        return cursor.lastrowid if cursor else None
    
    def update(self, table: str, data: Dict[str, Any], 
               where: str, where_params: Tuple = None,
               sanitize: bool = True) -> int:
        """Update data in table"""
        if sanitize:
            data = Security.sanitize_input(data)
        
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        params = tuple(data.values())
        if where_params:
            params += where_params
        
        cursor = self.execute(query, params, sanitize=False)
        return cursor.rowcount if cursor else 0
    
    def delete(self, table: str, where: str, params: Tuple = None) -> int:
        """Delete from table"""
        query = f"DELETE FROM {table} WHERE {where}"
        cursor = self.execute(query, params)
        return cursor.rowcount if cursor else 0
    
    def transaction(self):
        """Context manager for transactions"""
        return self.connection_pool.get_connection()
    
    def close(self):
        """Close all database connections"""
        self.connection_pool.close_all()