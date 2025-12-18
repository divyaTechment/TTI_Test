"""
Base repository class with common database operations.
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def getTesting(self, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        var=56
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field filters
            order_by: Field to order by
            
        Returns:
            List of model instances
        """
        query = self.db.query(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, field).in_(value))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            obj_in: Dictionary of field values
            
        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update a record.
        
        Args:
            id: Record ID
            obj_in: Dictionary of field values to update
            
        Returns:
            Updated model instance or None
        """
        db_obj = self.get(id)
        if db_obj:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """
        Delete a record.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching records
        """
        query = self.db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, field).in_(value))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
    
    def exists(self, id: int) -> bool:
        """
        Check if a record exists.
        
        Args:
            id: Record ID
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
    
    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """
        Get a record by a specific field value.
        
        Args:
            field: Field name
            value: Field value
            
        Returns:
            Model instance or None
        """
        if hasattr(self.model, field):
            return self.db.query(self.model).filter(getattr(self.model, field) == value).first()
        return None
