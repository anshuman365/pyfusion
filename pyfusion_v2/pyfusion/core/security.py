"""
Security utilities and middleware
"""
import re
import html
from typing import Any, Dict, List
from .exceptions import SecurityError

class Security:
    """Security utilities for input sanitization and validation"""
    
    @staticmethod
    def sanitize_input(data: Any) -> Any:
        """Sanitize input data to prevent XSS"""
        if isinstance(data, str):
            return html.escape(data.strip())
        elif isinstance(data, dict):
            return {key: Security.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [Security.sanitize_input(item) for item in data]
        return data
    
    @staticmethod
    def prevent_sql_injection(query: str, params: tuple = None) -> bool:
        """Basic SQL injection prevention"""
        if not params:
            return True
            
        sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER']
        query_upper = query.upper()
        
        # Check for suspicious patterns
        for keyword in sql_keywords:
            if f' {keyword} ' in query_upper and '?' not in query:
                raise SecurityError(f"Potential SQL injection detected: {keyword}")
        
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Enhanced email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Enhanced phone validation"""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        import secrets
        return secrets.token_hex(32)
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()