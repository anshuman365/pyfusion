#!/usr/bin/env python3
"""
Example: Full-Stack Application with PyFusion
"""

from pyfusion import WebServer, Database, HttpClient, FileManager

class FullStackApp:
    def __init__(self):
        self.app = WebServer("FullStackApp")
        self.db = Database()
        self.http = HttpClient()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup application routes with unique endpoint names"""
        
        @self.app.route('/')
        def home_page():  # Changed from 'home' to 'home_page'
            return {
                "app": "PyFusion Full-Stack Demo",
                "version": "1.0",
                "endpoints": {
                    "/data": "View application data",
                    "/users": "Manage users", 
                    "/external": "Fetch external data"
                }
            }
        
        @self.app.route('/data')
        def app_data_page():  # Changed from 'app_data'
            # Store some data
            self.db.execute(
                "INSERT OR REPLACE INTO app_data (key, value) VALUES (?, ?)",
                ('last_accessed', '2024-01-01 12:00:00')
            )
            
            # Read data
            data = self.db.fetch_all("SELECT * FROM app_data")
            return {"app_data": data}
        
        @self.app.route('/external')
        def external_data_page():  # Changed from 'external_data'
            # Fetch data from external API
            response = self.http.get('https://jsonplaceholder.typicode.com/posts/1')
            return {
                "external_data": response,
                "cached_at": "2024-01-01 12:00:00"
            }
        
        @self.app.route('/file/read')
        def read_file_page():  # Changed from 'read_file'
            content = FileManager.read_file('README.md')
            return {"file_content": content[:500] + "..." if content else "File not found"}
    
    def run(self):
        """Run the application"""
        print(" Starting Full-Stack PyFusion Application...")
        self.app.run(port=8000)

if __name__ == "__main__":
    full_app = FullStackApp()
    full_app.run()