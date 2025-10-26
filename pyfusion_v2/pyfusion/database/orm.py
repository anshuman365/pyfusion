"""
Object-Relational Mapping (ORM) system for PyFusion
"""
from typing import Any, Dict, List, Optional, Type, TypeVar
from ..core.exceptions import DatabaseError
from ..core.logging import log
from .manager import Database

T = TypeVar('T', bound='Model')

class Field:
    """Base field for ORM"""
    
    def __init__(self, field_type: str, primary_key: bool = False, 
                 auto_increment: bool = False, nullable: bool = True,
                 default: Any = None, unique: bool = False):
        self.field_type = field_type
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.nullable = nullable
        self.default = default
        self.unique = unique

class IntegerField(Field):
    """Integer field"""
    
    def __init__(self, primary_key: bool = False, auto_increment: bool = False,
                 nullable: bool = True, default: int = None, unique: bool = False):
        super().__init__('INTEGER', primary_key, auto_increment, nullable, default, unique)

class StringField(Field):
    """String field"""
    
    def __init__(self, max_length: int = 255, nullable: bool = True,
                 default: str = None, unique: bool = False):
        super().__init__(f'VARCHAR({max_length})', False, False, nullable, default, unique)
        self.max_length = max_length

class TextField(Field):
    """Text field"""
    
    def __init__(self, nullable: bool = True, default: str = None):
        super().__init__('TEXT', False, False, nullable, default, False)

class BooleanField(Field):
    """Boolean field"""
    
    def __init__(self, nullable: bool = True, default: bool = None):
        super().__init__('BOOLEAN', False, False, nullable, default, False)

class DateTimeField(Field):
    """DateTime field"""
    
    def __init__(self, nullable: bool = True, default: str = None):
        super().__init__('TIMESTAMP', False, False, nullable, default, False)

class ModelMeta(type):
    """Metaclass for Model to collect field information"""
    
    def __new__(cls, name, bases, attrs):
        # Collect fields from class attributes
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                fields[key] = value
                attrs.pop(key)
        
        attrs['_fields'] = fields
        attrs['_table_name'] = attrs.get('__tablename__', name.lower() + 's')
        
        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=ModelMeta):
    """Base Model class for ORM"""
    
    def __init__(self, **kwargs):
        self._db = Database()
        self._is_new = True
        
        # Set field values from kwargs
        for field_name in self._fields:
            value = kwargs.get(field_name, None)
            setattr(self, field_name, value)
    
    def save(self) -> bool:
        """Save model to database"""
        try:
            data = {}
            for field_name, field in self._fields.items():
                value = getattr(self, field_name, None)
                
                # Use default value if None and default is specified
                if value is None and field.default is not None:
                    value = field.default
                
                # Handle auto-increment primary key
                if field.primary_key and field.auto_increment and value is None:
                    continue
                
                data[field_name] = value
            
            if self._is_new:
                # Insert new record
                row_id = self._db.insert(self._table_name, data)
                if row_id:
                    # Set the auto-increment ID
                    for field_name, field in self._fields.items():
                        if field.primary_key and field.auto_increment:
                            setattr(self, field_name, row_id)
                    self._is_new = False
                    return True
            else:
                # Update existing record
                primary_key = self._get_primary_key()
                if primary_key:
                    where = f"{primary_key[0]} = ?"
                    affected = self._db.update(
                        self._table_name, data, where, (getattr(self, primary_key[0]),)
                    )
                    return affected > 0
            
            return False
        except Exception as e:
            log.error(f"Error saving model: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete model from database"""
        primary_key = self._get_primary_key()
        if not primary_key or self._is_new:
            return False
        
        where = f"{primary_key[0]} = ?"
        affected = self._db.delete(
            self._table_name, where, (getattr(self, primary_key[0]),)
        )
        
        if affected > 0:
            self._is_new = True
            return True
        return False
    
    def _get_primary_key(self) -> Optional[tuple]:
        """Get primary key field name and value"""
        for field_name, field in self._fields.items():
            if field.primary_key:
                return (field_name, getattr(self, field_name, None))
        return None
    
    @classmethod
    def objects(cls: Type[T]) -> 'QuerySet[T]':
        """Get query set for model"""
        return QuerySet(cls)
    
    @classmethod
    def create_table(cls) -> bool:
        """Create table for model"""
        try:
            db = Database()
            
            # Build CREATE TABLE query
            fields_sql = []
            for field_name, field in cls._fields.items():
                field_sql = f"{field_name} {field.field_type}"
                
                if field.primary_key:
                    field_sql += " PRIMARY KEY"
                if field.auto_increment:
                    field_sql += " AUTOINCREMENT"
                if not field.nullable:
                    field_sql += " NOT NULL"
                if field.unique:
                    field_sql += " UNIQUE"
                if field.default is not None:
                    field_sql += f" DEFAULT {repr(field.default)}"
                
                fields_sql.append(field_sql)
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {cls._table_name} ({', '.join(fields_sql)})"
            db.execute(create_sql)
            return True
        except Exception as e:
            log.error(f"Error creating table: {e}")
            return False

class QuerySet:
    """Query set for database operations"""
    
    def __init__(self, model_class: Type[Model]):
        self.model_class = model_class
        self._db = Database()
        self._where = []
        self._params = []
        self._limit = None
        self._offset = None
        self._order_by = []
    
    def filter(self, **kwargs) -> 'QuerySet':
        """Add filter conditions"""
        for key, value in kwargs.items():
            self._where.append(f"{key} = ?")
            self._params.append(value)
        return self
    
    def limit(self, count: int) -> 'QuerySet':
        """Set limit"""
        self._limit = count
        return self
    
    def offset(self, count: int) -> 'QuerySet':
        """Set offset"""
        self._offset = count
        return self
    
    def order_by(self, *fields: str) -> 'QuerySet':
        """Set order by fields"""
        for field in fields:
            if field.startswith('-'):
                self._order_by.append(f"{field[1:]} DESC")
            else:
                self._order_by.append(field)
        return self
    
    def all(self) -> List[Model]:
        """Get all objects"""
        return self._execute_query()
    
    def first(self) -> Optional[Model]:
        """Get first object"""
        results = self.limit(1)._execute_query()
        return results[0] if results else None
    
    def get(self, **kwargs) -> Optional[Model]:
        """Get single object by filters"""
        return self.filter(**kwargs).first()
    
    def count(self) -> int:
        """Get count of objects"""
        query = f"SELECT COUNT(*) as count FROM {self.model_class._table_name}"
        
        if self._where:
            query += f" WHERE {' AND '.join(self._where)}"
        
        result = self._db.fetch_one(query, tuple(self._params))
        return result['count'] if result else 0
    
    def delete(self) -> int:
        """Delete objects"""
        query = f"DELETE FROM {self.model_class._table_name}"
        
        if self._where:
            query += f" WHERE {' AND '.join(self._where)}"
        
        cursor = self._db.execute(query, tuple(self._params))
        return cursor.rowcount if cursor else 0
    
    def _execute_query(self) -> List[Model]:
        """Execute query and return model instances"""
        query = f"SELECT * FROM {self.model_class._table_name}"
        
        if self._where:
            query += f" WHERE {' AND '.join(self._where)}"
        
        if self._order_by:
            query += f" ORDER BY {', '.join(self._order_by)}"
        
        if self._limit is not None:
            query += f" LIMIT {self._limit}"
        
        if self._offset is not None:
            query += f" OFFSET {self._offset}"
        
        results = self._db.fetch_all(query, tuple(self._params))
        objects = []
        
        for row in results:
            obj = self.model_class(**dict(row))
            obj._is_new = False
            objects.append(obj)
        
        return objects

# Example model classes
class User(Model):
    """User model example"""
    __tablename__ = 'users'
    
    id = IntegerField(primary_key=True, auto_increment=True)
    username = StringField(unique=True, max_length=50)
    email = StringField(unique=True, max_length=100)
    age = IntegerField(nullable=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default='CURRENT_TIMESTAMP')

class Product(Model):
    """Product model example"""
    __tablename__ = 'products'
    
    id = IntegerField(primary_key=True, auto_increment=True)
    name = StringField(max_length=100)
    price = IntegerField()  # in cents
    description = TextField(nullable=True)
    in_stock = BooleanField(default=True)
    created_at = DateTimeField(default='CURRENT_TIMESTAMP')