"""
Authentication routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict

from ...database.base import get_db
from ...services.auth import AuthService
from ...services.user import UserService
from ...schemas.user import UserLogin, Token, UserResponse, PasswordChange
from ...schemas.base import ErrorSchema

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Current user response
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    user = auth_service.get_current_user(credentials.credentials)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth_service.is_active_user(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return UserResponse.from_orm(user)


def get_current_superuser(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current superuser if exists 
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current superuser response
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


@router.post("/login", response_model=Token, summary="User Login")
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Authenticate user and return access token.
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        Access token
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    token = auth_service.login(user_credentials)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


@router.post("/logout", summary="User Logout")
async def logout() -> Dict[str, str]:
    """
    Logout user (client should discard token).
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse, summary="Get Current User")
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.post("/change-password", summary="Change Password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Change user password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If current password is incorrect
    """
    auth_service = AuthService(db)
    user_service = UserService(db)
    
    # Get user from database
    user = auth_service.user_repo.get(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not auth_service.verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash new password
    new_hashed_password = auth_service.get_password_hash(password_data.new_password)
    
    # Update password
    user_service.user_repo.update(user.id, {"hashed_password": new_hashed_password})
    
    return {"message": "Password changed successfully"}


@router.post("/verify-token", summary="Verify Token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """
    Verify if token is valid.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Token validity status
    """
    auth_service = AuthService(db)
    token_data = auth_service.verify_token(credentials.credentials)
    
    return {"valid": token_data is not None}
