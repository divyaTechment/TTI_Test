"""
User service for user-related business logic.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.user import User
from ..repositories.user import UserRepository
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from .auth import AuthService


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_service = AuthService(db)
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user response
            
        Raises:
            ValueError: If email or username already exists
        """
        # Check if email already exists
        if self.user_repo.email_exists(user_data.email):
            raise ValueError("Email already registered")
        
        # Check if username already exists
        if self.user_repo.username_exists(user_data.username):
            raise ValueError("Username already taken")
        
        # Hash password
        hashed_password = self.auth_service.get_password_hash(user_data.password)
        
        # Create user data
        user_dict = user_data.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        
        # Create user
        user = self.user_repo.create(user_dict)
        
        return UserResponse.from_orm(user)
    
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User response or None
        """
        user = self.user_repo.get(user_id)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User response or None
        """
        user = self.user_repo.get_by_email(email)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[UserResponse]:
        """
        Get multiple users with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field filters
            
        Returns:
            List of user responses
        """
        users = self.user_repo.get_multi(skip=skip, limit=limit, filters=filters)
        return [UserResponse.from_orm(user) for user in users]
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Update user information.
        
        Args:
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user response or None
            
        Raises:
            ValueError: If email or username already exists
        """
        user = self.user_repo.get(user_id)
        if not user:
            return None
        
        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != user.email:
            if self.user_repo.email_exists(user_data.email):
                raise ValueError("Email already registered")
        
        # Check username uniqueness if username is being updated
        if user_data.username and user_data.username != user.username:
            if self.user_repo.username_exists(user_data.username):
                raise ValueError("Username already taken")
        
        # Update user
        update_data = user_data.dict(exclude_unset=True)
        updated_user = self.user_repo.update(user_id, update_data)
        
        if updated_user:
            return UserResponse.from_orm(updated_user)
        return None
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.user_repo.delete(user_id)
    
    def deactivate_user(self, user_id: int) -> Optional[UserResponse]:
        """
        Deactivate a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user response or None
        """
        user = self.user_repo.deactivate_user(user_id)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def activate_user(self, user_id: int) -> Optional[UserResponse]:
        """
        Activate a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user response or None
        """
        user = self.user_repo.activate_user(user_id)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def verify_user(self, user_id: int) -> Optional[UserResponse]:
        """
        Verify a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user response or None
        """
        user = self.user_repo.verify_user(user_id)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Get active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active user responses
        """
        users = self.user_repo.get_active_users(skip=skip, limit=limit)
        return [UserResponse.from_orm(user) for user in users]
    
    def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Get verified users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of verified user responses
        """
        users = self.user_repo.get_verified_users(skip=skip, limit=limit)
        return [UserResponse.from_orm(user) for user in users]
    
    def count_users(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count users with optional filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching users
        """
        return self.user_repo.count(filters)
