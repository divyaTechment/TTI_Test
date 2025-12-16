"""
User repository for user-related database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base import BaseRepository
from ..models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active users
        """
        return (
            self.db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get verified users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of verified users
        """
        return (
            self.db.query(User)
            .filter(and_(User.is_active == True, User.is_verified == True))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_superusers(self) -> List[User]:
        """
        Get all superusers.
        
        Returns:
            List of superusers
        """
        return (
            self.db.query(User)
            .filter(and_(User.is_active == True, User.is_superuser == True))
            .all()
        )
    
    def update_last_login(self, user_id: int) -> Optional[User]:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None
        """
        from datetime import datetime
        return self.update(user_id, {"last_login": datetime.utcnow()})
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Deactivate a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None
        """
        return self.update(user_id, {"is_active": False})
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """
        Activate a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None
        """
        return self.update(user_id, {"is_active": True})
    
    def verify_user(self, user_id: int) -> Optional[User]:
        """
        Verify a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user instance or None
        """
        return self.update(user_id, {"is_verified": True})
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email exists, False otherwise
        """
        return self.get_by_email(email) is not None
    
    def username_exists(self, username: str) -> bool:
        """
        Check if username already exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if username exists, False otherwise
        """
        return self.get_by_username(username) is not None
