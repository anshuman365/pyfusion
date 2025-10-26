"""
Authentication decorators for PyFusion
"""
from functools import wraps
from flask import request, jsonify
from typing import Callable, Any
from .manager import AuthManager
from .permissions import requires_permission, requires_role
from ..core.exceptions import AuthenticationError
from ..core.logging import log

def login_required(f: Callable) -> Callable:
    """Decorator to require login for route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                "error": "Authentication required",
                "message": "Bearer token missing"
            }), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            auth = AuthManager()
            user = auth.validate_jwt_token(token)
            
            if not user:
                return jsonify({
                    "error": "Invalid token",
                    "message": "Token is invalid or expired"
                }), 401
            
            # Add user to request context for use in route
            request.user = user
            return f(*args, **kwargs)
            
        except AuthenticationError as e:
            return jsonify({
                "error": "Authentication failed",
                "message": str(e)
            }), 401
    
    return decorated_function

def session_required(f: Callable) -> Callable:
    """Decorator to require session for route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('X-Session-Token') or \
                       request.cookies.get('session_token')
        
        if not session_token:
            return jsonify({
                "error": "Session required",
                "message": "Session token missing"
            }), 401
        
        try:
            auth = AuthManager()
            user = auth.validate_session(session_token)
            
            if not user:
                return jsonify({
                    "error": "Invalid session",
                    "message": "Session is invalid or expired"
                }), 401
            
            # Add user to request context
            request.user = user
            return f(*args, **kwargs)
            
        except AuthenticationError as e:
            return jsonify({
                "error": "Session validation failed",
                "message": str(e)
            }), 401
    
    return decorated_function

def admin_required(f: Callable) -> Callable:
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'user') or not request.user:
            return jsonify({
                "error": "Authentication required"
            }), 401
        
        # Check if user has admin role (simplified)
        user_roles = request.user.get('roles', [])
        if 'admin' not in user_roles:
            return jsonify({
                "error": "Admin access required",
                "message": "Insufficient permissions"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# Export permission decorators from permissions module
__all__ = [
    'login_required',
    'session_required', 
    'admin_required',
    'requires_permission',
    'requires_role'
]