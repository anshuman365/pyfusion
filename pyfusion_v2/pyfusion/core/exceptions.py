"""
Custom exceptions for PyFusion framework
"""

class PyFusionError(Exception):
    """Base exception for all PyFusion errors"""
    pass

class DatabaseError(PyFusionError):
    """Database related errors"""
    pass

class ValidationError(PyFusionError):
    """Data validation errors"""
    pass

class AuthenticationError(PyFusionError):
    """Authentication related errors"""
    pass

class ConfigurationError(PyFusionError):
    """Configuration errors"""
    pass

class NetworkError(PyFusionError):
    """Network related errors"""
    pass

class SecurityError(PyFusionError):
    """Security related errors"""
    pass