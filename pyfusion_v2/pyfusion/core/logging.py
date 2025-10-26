"""
Logging system for PyFusion
"""
import logging
import os
from datetime import datetime
from typing import Optional
from .config import Config

class Logger:
    """Unified logging system"""
    
    _instances = {}
    
    def __new__(cls, name: str = "pyfusion"):
        if name not in cls._instances:
            cls._instances[name] = super(Logger, cls).__new__(cls)
        return cls._instances[name]
    
    def __init__(self, name: str = "pyfusion"):
        if not hasattr(self, '_initialized'):
            self.name = name
            self.config = Config()
            self._setup_logger()
            self._initialized = True
    
    def _setup_logger(self):
        """Setup logger with handlers"""
        self.logger = logging.getLogger(self.name)
        
        # Avoid duplicate handlers
        if self.logger.handlers:
            return
        
        log_level = self.config.get('logging.level', 'INFO')
        log_file = self.config.get('logging.file')
        
        # Set log level
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            try:
                # Create log directory if it doesn't exist
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f"Failed to setup file logging: {e}")
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)

# Global logger instance
log = Logger()