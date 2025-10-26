"""
Rate limiting implementation
"""
import time
from typing import Dict
from ..core.logging import log

class RateLimiter:
    """Rate limiter for API endpoints"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def check_limit(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove requests older than 1 minute
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < 60
        ]
        
        # Check if within limit
        if len(self.requests[client_id]) < self.requests_per_minute:
            self.requests[client_id].append(current_time)
            return True
        
        log.warning(f"Rate limit exceeded for client: {client_id}")
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        current_time = time.time()
        
        if client_id not in self.requests:
            return self.requests_per_minute
        
        # Count requests in last minute
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < 60
        ]
        
        return max(0, self.requests_per_minute - len(recent_requests))