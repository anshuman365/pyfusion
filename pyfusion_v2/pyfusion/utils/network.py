"""
Enhanced network utilities with DNS and advanced connectivity checks
"""
import socket
import requests
import subprocess
import platform
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional, Tuple
from ..core.exceptions import NetworkError
from ..core.logging import log

class NetworkTools:
    """Enhanced network utilities with DNS resolution and advanced checks"""
    
    @staticmethod
    def check_internet(timeout: int = 5, test_url: str = None) -> bool:
        """Check internet connectivity with multiple fallback URLs"""
        test_urls = [
            test_url,
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://www.github.com'
        ]
        
        for url in test_urls:
            if not url:
                continue
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    return True
            except:
                continue
        
        return False
    
    @staticmethod
    def get_local_ip() -> str:
        """Get local IP address that connects to the internet"""
        try:
            # Connect to a remote server to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            try:
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            except:
                return "127.0.0.1"
    
    @staticmethod
    def get_public_ip() -> Optional[str]:
        """Get public IP address using multiple services"""
        services = [
            'https://api.ipify.org',
            'https://ident.me',
            'https://checkip.amazonaws.com'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        
        return None
    
    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if port is open with detailed error reporting"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception as e:
            log.debug(f"Port check failed for {host}:{port}: {e}")
            return False
    
    @staticmethod
    def scan_ports(host: str, ports: List[int], timeout: float = 1.0) -> Dict[int, bool]:
        """Scan multiple ports on a host"""
        results = {}
        for port in ports:
            results[port] = NetworkTools.is_port_open(host, port, timeout)
        return results
    
    @staticmethod
    def validate_url(url: str, check_online: bool = False) -> bool:
        """Validate URL format and optionally check if it's online"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
            
            if check_online:
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    return response.status_code < 400
                except:
                    return False
            
            return True
        except:
            return False
    
    @staticmethod
    def dns_lookup(hostname: str, record_type: str = 'A') -> List[str]:
        """Perform DNS lookup for a hostname"""
        try:
            import dns.resolver
            answers = dns.resolver.resolve(hostname, record_type)
            return [str(rdata) for rdata in answers]
        except ImportError:
            log.warning("dnspython not installed. Install with: pip install dnspython")
            return []
        except Exception as e:
            log.error(f"DNS lookup failed for {hostname}: {e}")
            return []
    
    @staticmethod
    def reverse_dns_lookup(ip: str) -> Optional[str]:
        """Perform reverse DNS lookup for IP address"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Get comprehensive network information"""
        system = platform.system().lower()
        info = {
            'local_ip': NetworkTools.get_local_ip(),
            'public_ip': NetworkTools.get_public_ip(),
            'hostname': socket.gethostname(),
            'internet_connected': NetworkTools.check_internet(),
            'system': system
        }
        
        # Platform-specific network info
        if system == 'windows':
            try:
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
                info['ipconfig'] = result.stdout
            except:
                pass
        elif system in ['linux', 'darwin']:  # Linux or macOS
            try:
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                info['ifconfig'] = result.stdout
            except:
                try:
                    result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
                    info['ip_addr'] = result.stdout
                except:
                    pass
        
        return info
    
    @staticmethod
    def ping_host(host: str, count: int = 4) -> Dict[str, Any]:
        """Ping a host and return results"""
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                cmd = ['ping', '-n', str(count), host]
            else:
                cmd = ['ping', '-c', str(count), host]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                'host': host,
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'host': host,
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def trace_route(host: str) -> Dict[str, Any]:
        """Perform traceroute to host"""
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                cmd = ['tracert', host]
            else:
                cmd = ['traceroute', host]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                'host': host,
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'host': host,
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def check_service_health(url: str, timeout: int = 10) -> Dict[str, Any]:
        """Check health of a web service"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            return {
                'url': url,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_type': response.headers.get('content-type'),
                'server': response.headers.get('server'),
                'success': response.status_code < 400
            }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def get_ssl_cert_info(hostname: str, port: int = 443) -> Optional[Dict[str, Any]]:
        """Get SSL certificate information"""
        try:
            import ssl
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'not_before': cert['notBefore'],
                        'not_after': cert['notAfter'],
                        'serial_number': cert.get('serialNumber'),
                        'version': cert.get('version')
                    }
        except ImportError:
            log.warning("SSL certificate info requires SSL support")
            return None
        except Exception as e:
            log.error(f"Error getting SSL certificate info: {e}")
            return None

# Import time for service health check
import time