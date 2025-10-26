import os
import json
import csv
import pickle

class FileManager:
    """Built-in file operations manager"""
    
    @staticmethod
    def read_json(file_path):
        """Read JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading JSON: {e}")
            return None
    
    @staticmethod
    def write_json(file_path, data):
        """Write JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing JSON: {e}")
            return False
    
    @staticmethod
    def read_csv(file_path, delimiter=','):
        """Read CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f, delimiter=delimiter))
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return None
    
    @staticmethod
    def write_csv(file_path, data, fieldnames=None):
        """Write CSV file"""
        try:
            if not fieldnames and data:
                fieldnames = data[0].keys()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error writing CSV: {e}")
            return False
    
    @staticmethod
    def read_file(file_path):
        """Read text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    @staticmethod
    def write_file(file_path, content):
        """Write text file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False