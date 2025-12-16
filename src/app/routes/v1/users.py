"""
User management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...database.base import get_db
from ...services.user import UserService
from ...services.auth import AuthService
from ...schemas.user import UserCreate, UserUpdate, UserResponse
from ...schemas.base import PaginationSchema
from .auth import get_current_user, get_current_superuser

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create User")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        db: Database session
        
    Returns:
        Created user response
        
    Raises:
        HTTPException: If email or username already exists
    """
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[UserResponse], summary="Get Users")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[UserResponse]:
    """
    Get users with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        is_verified: Filter by verified status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of user responses
    """
    user_service = UserService(db)
    
    # Build filters
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if is_verified is not None:
        filters["is_verified"] = is_verified
    
    users = user_service.get_users(skip=skip, limit=limit, filters=filters)
    return users


@router.get("/me", response_model=UserResponse, summary="Get Current User Profile")
async def get_my_profile(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user profile
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse, summary="Get User by ID")
async def get_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User response
        
    Raises:
        HTTPException: If user not found or access denied
    """
    user_service = UserService(db)
    
    # Users can only view their own profile unless they're superusers
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/me", response_model=UserResponse, summary="Update Current User")
async def update_my_profile(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update current user's profile.
    
    Args:
        user_data: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user response
        
    Raises:
        HTTPException: If update fails
    """
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_user(current_user.id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse, summary="Update User")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update user by ID (superuser only).
    
    Args:
        user_id: User ID
        user_data: User update data
        current_user: Current superuser
        db: Database session
        
    Returns:
        Updated user response
        
    Raises:
        HTTPException: If user not found or update fails
    """
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_user(user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", summary="Delete User")
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete user by ID (superuser only).
    
    Args:
        user_id: User ID
        current_user: Current superuser
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    
    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/activate", response_model=UserResponse, summary="Activate User")
async def activate_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Activate user by ID (superuser only).
    
    Args:
        user_id: User ID
        current_user: Current superuser
        db: Database session
        
    Returns:
        Updated user response
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    
    user = user_service.activate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse, summary="Deactivate User")
async def deactivate_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Deactivate user by ID (superuser only).
    
    Args:
        user_id: User ID
        current_user: Current superuser
        db: Database session
        
    Returns:
        Updated user response
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    
    # Prevent self-deactivation
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = user_service.deactivate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/{user_id}/verify", response_model=UserResponse, summary="Verify User")
async def verify_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Verify user by ID (superuser only).
    
    Args:
        user_id: User ID
        current_user: Current superuser
        db: Database session
        
    Returns:
        Updated user response
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    
    user = user_service.verify_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
