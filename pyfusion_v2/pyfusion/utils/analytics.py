"""
Usage analytics and performance tracking
"""
import time
from typing import Dict, List, Any
from datetime import datetime
from ..core.logging import log
from ..database.manager import Database

class Analytics:
    """Usage analytics and performance tracking"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self._start_time = time.time()
        self._request_times: List[float] = []
        self._feature_usage: Dict[str, int] = {}
    
    def track_request(self, method: str, path: str, duration: float):
        """Track HTTP request"""
        self._request_times.append(duration)
        
        # Keep only last 1000 requests for performance
        if len(self._request_times) > 1000:
            self._request_times.pop(0)
        
        # Log to database if available
        try:
            self.db.insert('audit_log', {
                'action': f'{method} {path}',
                'details': f'Duration: {duration:.3f}s',
                'ip_address': '127.0.0.1',  # Would come from request in real scenario
                'user_agent': 'PyFusion Analytics'
            })
        except Exception as e:
            log.debug(f"Analytics tracking failed: {e}")
    
    def track_feature(self, feature_name: str):
        """Track feature usage"""
        self._feature_usage[feature_name] = self._feature_usage.get(feature_name, 0) + 1
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self._request_times:
            return {}
        
        return {
            'total_requests': len(self._request_times),
            'average_response_time': sum(self._request_times) / len(self._request_times),
            'max_response_time': max(self._request_times),
            'min_response_time': min(self._request_times),
            'uptime': time.time() - self._start_time
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'feature_usage': self._feature_usage,
            'total_features_used': len(self._feature_usage),
            'most_used_feature': max(self._feature_usage.items(), key=lambda x: x[1]) if self._feature_usage else None
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        performance = self.get_performance_metrics()
        usage = self.get_usage_stats()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'performance': performance,
            'usage': usage,
            'system': {
                'python_version': '3.8+',  # Would be dynamic in real implementation
                'framework_version': '2.0.0'
            }
        }