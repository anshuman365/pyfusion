import sqlite3
import json
import os
from datetime import datetime

class Database:
    """Built-in database manager with SQLite integration"""
    
    def __init__(self, db_path='pyfusion_db.sqlite'):
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._setup_tables()
    
    def _connect(self):
        """Connect to SQLite database"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
    
    def _setup_tables(self):
        """Create default tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # App data table (generic key-value store)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_data (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
    
    def execute(self, query, params=None):
        """Execute SQL query"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """Fetch all results"""
        cursor = self.execute(query, params)
        if cursor:
            return [dict(row) for row in cursor.fetchall()]
        return []
    
    def fetch_one(self, query, params=None):
        """Fetch single result"""
        cursor = self.execute(query, params)
        if cursor:
            result = cursor.fetchone()
            return dict(result) if result else None
        return None
    
    def insert(self, table, data):
        """Insert data into table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.execute(query, list(data.values()))
        return cursor.lastrowid if cursor else None
    
    def update(self, table, data, where):
        """Update data in table"""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        cursor = self.execute(query, list(data.values()))
        return cursor.rowcount if cursor else 0
    
    def delete(self, table, where, params=None):
        """Delete from table"""
        query = f"DELETE FROM {table} WHERE {where}"
        cursor = self.execute(query, params)
        return cursor.rowcount if cursor else 0
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()