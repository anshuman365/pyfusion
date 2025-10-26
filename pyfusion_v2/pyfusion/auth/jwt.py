"""
JWT token management
"""
import jwt
import time
from typing import Optional, Dict, Any
from ..core.exceptions import AuthenticationError
from ..core.config import Config

class JWTManager:
    """JWT token creation and validation"""
    
    def __init__(self):
        self.config = Config()
        self.secret_key = self.config.get('security.secret_key')
        self.algorithm = 'HS256'
        self.expiration = 3600  # 1 hour
    
    def create_token(self, payload: Dict[str, Any]) -> str:
        """Create JWT token"""
        if not self.secret_key:
            raise AuthenticationError("JWT secret key not configured")
        
        payload = payload.copy()
        payload['exp'] = time.time() + self.expiration
        payload['iat'] = time.time()
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload"""
        if not self.secret_key:
            raise AuthenticationError("JWT secret key not configured")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    def refresh_token(self, token: str) -> str:
        """Refresh JWT token"""
        payload = self.validate_token(token)
        if 'exp' in payload:
            del payload['exp']
        if 'iat' in payload:
            del payload['iat']
        
        return self.create_token(payload)