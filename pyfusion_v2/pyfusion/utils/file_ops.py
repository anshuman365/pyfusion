"""
Enhanced file operations with additional formats and compression
"""
import os
import json
import csv
import pickle
import zipfile
import tarfile
import shutil
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from ..core.exceptions import PyFusionError
from ..core.logging import log

class FileManager:
    """Enhanced file operations manager with compression support"""
    
    @staticmethod
    def read_json(file_path: str, encoding: str = 'utf-8') -> Optional[Dict[str, Any]]:
        """Read JSON file with enhanced error handling"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Error reading JSON file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_json(file_path: str, data: Any, indent: int = 2, 
                  encoding: str = 'utf-8') -> bool:
        """Write JSON file with pretty printing and backup"""
        try:
            # Create backup if file exists
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup.{int(datetime.now().timestamp())}"
                shutil.copy2(file_path, backup_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            log.error(f"Error writing JSON file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_csv(file_path: str, delimiter: str = ',', 
                encoding: str = 'utf-8') -> Optional[List[Dict[str, Any]]]:
        """Read CSV file with enhanced options"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                return list(reader)
        except Exception as e:
            log.error(f"Error reading CSV file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_csv(file_path: str, data: List[Dict[str, Any]], 
                 fieldnames: List[str] = None, delimiter: str = ',',
                 encoding: str = 'utf-8') -> bool:
        """Write CSV file with automatic field detection"""
        try:
            if not data and not fieldnames:
                log.error("No data and no fieldnames provided for CSV writing")
                return False
            
            if not fieldnames and data:
                fieldnames = list(data[0].keys())
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            log.error(f"Error writing CSV file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read text file with automatic encoding fallback"""
        encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                log.error(f"Error reading file {file_path}: {e}")
                return None
        
        log.error(f"Could not read file {file_path} with any encoding")
        return None
    
    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Write text file with directory creation"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            log.error(f"Error writing file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_pickle(file_path: str) -> Optional[Any]:
        """Read pickle file"""
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            log.error(f"Error reading pickle file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_pickle(file_path: str, data: Any) -> bool:
        """Write pickle file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            log.error(f"Error writing pickle file {file_path}: {e}")
            return False
    
    @staticmethod
    def compress_files(file_paths: List[str], output_path: str, 
                      compression: str = 'zip') -> bool:
        """Compress multiple files"""
        try:
            if compression == 'zip':
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in file_paths:
                        if os.path.isfile(file_path):
                            zipf.write(file_path, os.path.basename(file_path))
                return True
            elif compression == 'tar':
                with tarfile.open(output_path, 'w:gz') as tar:
                    for file_path in file_paths:
                        if os.path.isfile(file_path):
                            tar.add(file_path, arcname=os.path.basename(file_path))
                return True
            else:
                log.error(f"Unsupported compression format: {compression}")
                return False
        except Exception as e:
            log.error(f"Error compressing files: {e}")
            return False
    
    @staticmethod
    def extract_archive(archive_path: str, extract_dir: str) -> bool:
        """Extract archive file"""
        try:
            os.makedirs(extract_dir, exist_ok=True)
            
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(extract_dir)
                return True
            elif archive_path.endswith(('.tar', '.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'r:*') as tar:
                    tar.extractall(extract_dir)
                return True
            else:
                log.error(f"Unsupported archive format: {archive_path}")
                return False
        except Exception as e:
            log.error(f"Error extracting archive: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed file information"""
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'accessed': datetime.fromtimestamp(stat.st_atime),
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path),
                'extension': os.path.splitext(file_path)[1]
            }
        except Exception as e:
            log.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    @staticmethod
    def find_files(directory: str, pattern: str = '*', 
                  recursive: bool = True) -> List[str]:
        """Find files matching pattern"""
        import fnmatch
        matches = []
        
        if recursive:
            for root, dirnames, filenames in os.walk(directory):
                for filename in fnmatch.filter(filenames, pattern):
                    matches.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(directory):
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(directory, filename))
        
        return matches
    
    @staticmethod
    def safe_delete(file_path: str, backup: bool = True) -> bool:
        """Safely delete file with optional backup"""
        try:
            if not os.path.exists(file_path):
                return True
            
            if backup:
                backup_path = f"{file_path}.backup.{int(datetime.now().timestamp())}"
                shutil.copy2(file_path, backup_path)
            
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            
            return True
        except Exception as e:
            log.error(f"Error deleting {file_path}: {e}")
            return False