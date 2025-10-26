"""
Permission and role-based access control system
"""
from typing import List, Set, Callable, Any
from ..core.exceptions import AuthenticationError
from ..core.logging import log

class Permission:
    """Permission class for access control"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        if isinstance(other, Permission):
            return self.name == other.name
        return self.name == other

class Role:
    """Role with associated permissions"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.permissions: Set[Permission] = set()
    
    def add_permission(self, permission: Permission):
        """Add permission to role"""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission):
        """Remove permission from role"""
        self.permissions.discard(permission)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has permission"""
        return permission in self.permissions
    
    def __str__(self):
        return self.name

class PermissionManager:
    """Manager for roles and permissions"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self._setup_default_roles()
    
    def _setup_default_roles(self):
        """Setup default roles and permissions"""
        # Default permissions
        self.create_permission('user:read', 'Read user data')
        self.create_permission('user:write', 'Write user data')
        self.create_permission('user:delete', 'Delete users')
        self.create_permission('admin:access', 'Access admin panel')
        
        # Default roles
        admin_role = self.create_role('admin', 'Administrator')
        admin_role.add_permission(self.get_permission('user:read'))
        admin_role.add_permission(self.get_permission('user:write'))
        admin_role.add_permission(self.get_permission('user:delete'))
        admin_role.add_permission(self.get_permission('admin:access'))
        
        user_role = self.create_role('user', 'Regular user')
        user_role.add_permission(self.get_permission('user:read'))
    
    def create_permission(self, name: str, description: str = "") -> Permission:
        """Create new permission"""
        permission = Permission(name, description)
        self.permissions[name] = permission
        return permission
    
    def get_permission(self, name: str) -> Permission:
        """Get permission by name"""
        if name not in self.permissions:
            raise AuthenticationError(f"Permission not found: {name}")
        return self.permissions[name]
    
    def create_role(self, name: str, description: str = "") -> Role:
        """Create new role"""
        role = Role(name, description)
        self.roles[name] = role
        return role
    
    def get_role(self, name: str) -> Role:
        """Get role by name"""
        if name not in self.roles:
            raise AuthenticationError(f"Role not found: {name}")
        return self.roles[name]
    
    def user_has_permission(self, user_roles: List[str], permission: Permission) -> bool:
        """Check if user has permission through roles"""
        for role_name in user_roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                if role.has_permission(permission):
                    return True
        return False

def requires_permission(permission_name: str):
    """Decorator to require permission for route access"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Get user from session (simplified - would come from auth system)
            user_roles = getattr(request, 'user_roles', [])
            
            permission_manager = PermissionManager()
            permission = permission_manager.get_permission(permission_name)
            
            if not permission_manager.user_has_permission(user_roles, permission):
                return jsonify({
                    "error": "Permission denied",
                    "message": f"Required permission: {permission_name}"
                }), 403
            
            return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

def requires_role(role_name: str):
    """Decorator to require role for route access"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Get user from session (simplified - would come from auth system)
            user_roles = getattr(request, 'user_roles', [])
            
            if role_name not in user_roles:
                return jsonify({
                    "error": "Access denied",
                    "message": f"Required role: {role_name}"
                }), 403
            
            return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator