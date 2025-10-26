"""
Database migration system
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from ..core.exceptions import DatabaseError
from ..core.logging import log
from .manager import Database

class Migration:
    """Migration base class"""
    
    def __init__(self):
        self.version = self.__class__.__name__
        self.description = "No description"
    
    def up(self, db: Database) -> bool:
        """Apply migration"""
        raise NotImplementedError
    
    def down(self, db: Database) -> bool:
        """Revert migration"""
        raise NotImplementedError

class MigrationManager:
    """Database migration manager"""
    
    def __init__(self, db: Database = None, migrations_dir: str = "migrations"):
        self.db = db or Database()
        self.migrations_dir = migrations_dir
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations table if it doesn't exist"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def create_migration(self, name: str, description: str = "") -> str:
        """Create new migration file"""
        # Ensure migrations directory exists
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{name}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        template = f'''"""
Migration: {name}
Description: {description}
"""

import pyfusion
from pyfusion.database.migrations import Migration

class {timestamp}_{name.capitalize()}(Migration):
    """{description}"""
    
    def __init__(self):
        super().__init__()
        self.version = "{timestamp}_{name}"
        self.description = "{description}"
    
    def up(self, db):
        """Apply migration"""
        # Add your migration code here
        # Example:
        # db.execute("ALTER TABLE users ADD COLUMN new_column TEXT")
        return True
    
    def down(self, db):
        """Revert migration"""
        # Add your revert code here
        # Example:
        # db.execute("ALTER TABLE users DROP COLUMN new_column")
        return True
'''
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        log.info(f"Created migration: {filepath}")
        return filepath
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        results = self.db.fetch_all("SELECT version FROM migrations ORDER BY applied_at")
        return [row['version'] for row in results]
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        if not os.path.exists(self.migrations_dir):
            return []
        
        applied = set(self.get_applied_migrations())
        pending = []
        
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                migration_name = filename[:-3]  # Remove .py extension
                if migration_name not in applied:
                    pending.append(migration_name)
        
        return sorted(pending)
    
    def migrate(self, target_version: str = None) -> bool:
        """Apply pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            log.info("No pending migrations")
            return True
        
        if target_version:
            # Migrate only up to target version
            pending = [m for m in pending if m <= target_version]
        
        for migration_name in pending:
            if not self._apply_migration(migration_name):
                log.error(f"Failed to apply migration: {migration_name}")
                return False
        
        log.info(f"Applied {len(pending)} migration(s)")
        return True
    
    def rollback(self, steps: int = 1) -> bool:
        """Rollback migrations"""
        applied = self.get_applied_migrations()
        
        if not applied:
            log.info("No migrations to rollback")
            return True
        
        # Get migrations to rollback
        to_rollback = applied[-steps:]
        
        for migration_name in reversed(to_rollback):
            if not self._revert_migration(migration_name):
                log.error(f"Failed to revert migration: {migration_name}")
                return False
        
        log.info(f"Reverted {len(to_rollback)} migration(s)")
        return True
    
    def _apply_migration(self, migration_name: str) -> bool:
        """Apply specific migration"""
        try:
            # Import migration module
            import importlib.util
            filepath = os.path.join(self.migrations_dir, f"{migration_name}.py")
            
            spec = importlib.util.spec_from_file_location(migration_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find migration class
            migration_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Migration) and 
                    attr != Migration):
                    migration_class = attr
                    break
            
            if not migration_class:
                log.error(f"Migration class not found in {migration_name}")
                return False
            
            # Apply migration
            migration = migration_class()
            if migration.up(self.db):
                # Record migration
                self.db.insert('migrations', {
                    'version': migration_name,
                    'description': migration.description
                })
                log.info(f"Applied migration: {migration_name}")
                return True
            else:
                log.error(f"Migration failed: {migration_name}")
                return False
                
        except Exception as e:
            log.error(f"Error applying migration {migration_name}: {e}")
            return False
    
    def _revert_migration(self, migration_name: str) -> bool:
        """Revert specific migration"""
        try:
            # Import migration module
            import importlib.util
            filepath = os.path.join(self.migrations_dir, f"{migration_name}.py")
            
            spec = importlib.util.spec_from_file_location(migration_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find migration class
            migration_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Migration) and 
                    attr != Migration):
                    migration_class = attr
                    break
            
            if not migration_class:
                log.error(f"Migration class not found in {migration_name}")
                return False
            
            # Revert migration
            migration = migration_class()
            if migration.down(self.db):
                # Remove migration record
                self.db.delete('migrations', 'version = ?', (migration_name,))
                log.info(f"Reverted migration: {migration_name}")
                return True
            else:
                log.error(f"Migration revert failed: {migration_name}")
                return False
                
        except Exception as e:
            log.error(f"Error reverting migration {migration_name}: {e}")
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get migration status"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'applied': applied,
            'pending': pending,
            'total_applied': len(applied),
            'total_pending': len(pending),
            'current_version': applied[-1] if applied else None
        }