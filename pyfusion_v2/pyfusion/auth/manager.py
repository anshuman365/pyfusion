"""
Authentication and authorization manager
"""
import secrets
import time
from typing import Optional, Dict, Any
from ..core.exceptions import AuthenticationError
from ..core.logging import log
from ..core.security import Security
from ..database.manager import Database
from .jwt import JWTManager

class AuthManager:
    """Authentication manager for user management and session handling"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.jwt = JWTManager()
        self.session_timeout = 3600  # 1 hour
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Create new user with password hashing"""
        # Validate inputs
        if not Security.validate_email(email):
            raise AuthenticationError("Invalid email format")
        
        if len(password) < 8:
            raise AuthenticationError("Password must be at least 8 characters")
        
        # Check if user already exists
        existing_user = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        )
        
        if existing_user:
            raise AuthenticationError("Username or email already exists")
        
        # Hash password
        password_hash = Security.hash_password(password)
        
        # Create user
        user_id = self.db.insert('users', {
            'username': username,
            'email': email,
            'password_hash': password_hash
        })
        
        if not user_id:
            raise AuthenticationError("Failed to create user")
        
        log.info(f"User created: {username} ({email})")
        return self.get_user(user_id)
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username/email and password"""
        user = self.db.fetch_one(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = TRUE",
            (username, username)
        )
        
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        if not Security.verify_password(password, user['password_hash']):
            raise AuthenticationError("Invalid credentials")
        
        # Update last login
        self.db.update(
            'users', 
            {'updated_at': 'CURRENT_TIMESTAMP'},
            'id = ?',
            (user['id'],)
        )
        
        log.info(f"User authenticated: {user['username']}")
        return user
    
    def create_session(self, user_id: int) -> str:
        """Create user session and return session token"""
        session_token = secrets.token_urlsafe(32)
        expires_at = time.time() + self.session_timeout
        
        session_id = self.db.insert('sessions', {
            'user_id': user_id,
            'session_token': session_token,
            'expires_at': expires_at
        })
        
        if not session_id:
            raise AuthenticationError("Failed to create session")
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user"""
        session = self.db.fetch_one(
            "SELECT * FROM sessions WHERE session_token = ? AND expires_at > ?",
            (session_token, time.time())
        )
        
        if not session:
            return None
        
        user = self.get_user(session['user_id'])
        return user
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.db.fetch_one(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,)
        )
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.db.fetch_one(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user:
            raise AuthenticationError("User not found")
        
        if not Security.verify_password(old_password, user['password_hash']):
            raise AuthenticationError("Current password is incorrect")
        
        new_hash = Security.hash_password(new_password)
        affected = self.db.update(
            'users',
            {'password_hash': new_hash},
            'id = ?',
            (user_id,)
        )
        
        return affected > 0
    
    def logout(self, session_token: str) -> bool:
        """Invalidate session token"""
        affected = self.db.delete(
            'sessions',
            'session_token = ?',
            (session_token,)
        )
        
        return affected > 0
    
    def create_jwt_token(self, user_id: int, payload: Dict[str, Any] = None) -> str:
        """Create JWT token for user"""
        if payload is None:
            payload = {}
        
        payload['user_id'] = user_id
        return self.jwt.create_token(payload)
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload"""
        return self.jwt.validate_token(token)