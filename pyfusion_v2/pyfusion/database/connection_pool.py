"""
Database connection pooling for thread safety
"""
import sqlite3
import threading
from typing import List
from queue import Queue, Empty
from ..core.exceptions import DatabaseError
from ..core.logging import log

class ConnectionPool:
    """Thread-safe database connection pool"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self._pool.put(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create new database connection"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create database connection: {e}")
    
    def get_connection(self) -> 'PooledConnection':
        """Get connection from pool"""
        try:
            conn = self._pool.get(timeout=10)
            return PooledConnection(conn, self)
        except Empty:
            raise DatabaseError("No database connections available")
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        try:
            # Rollback any uncommitted changes
            conn.rollback()
            self._pool.put(conn)
        except Exception as e:
            log.error(f"Error returning connection to pool: {e}")
            # Create new connection to replace broken one
            new_conn = self._create_connection()
            self._pool.put(new_conn)
    
    def close_all(self):
        """Close all connections in pool"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except Empty:
                break

class PooledConnection:
    """Context manager for pooled connections"""
    
    def __init__(self, conn: sqlite3.Connection, pool: ConnectionPool):
        self.conn = conn
        self.pool = pool
    
    def __enter__(self) -> sqlite3.Connection:
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.return_connection(self.conn)