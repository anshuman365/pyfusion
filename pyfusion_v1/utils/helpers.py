import re
from datetime import datetime
import hashlib

class Validator:
    """Data validation utilities"""
    
    @staticmethod
    def is_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_phone(phone):
        """Validate phone number (basic)"""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def is_strong_password(password):
        """Check password strength"""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True

class Formatter:
    """Data formatting utilities"""
    
    @staticmethod
    def format_date(date_string, input_format='%Y-%m-%d', output_format='%d/%m/%Y'):
        """Format date string"""
        try:
            date_obj = datetime.strptime(date_string, input_format)
            return date_obj.strftime(output_format)
        except:
            return date_string
    
    @staticmethod
    def format_currency(amount, currency='₹'):
        """Format currency"""
        return f"{currency}{amount:,.2f}"
    
    @staticmethod
    def hash_data(data, algorithm='sha256'):
        """Hash data"""
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        else:
            return hashlib.sha256(data.encode()).hexdigest()