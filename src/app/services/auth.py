"""
Authentication service for user authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.user import User
from ..repositories.user import UserRepository
from ..schemas.user import Token, TokenData, UserLogin

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and authorization."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a password.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User instance if authenticated, None otherwise
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Token payload data
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: int = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                return None
            
            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from token.
        
        Args:
            token: JWT token string
            
        Returns:
            User instance if valid, None otherwise
        """
        token_data = self.verify_token(token)
        if token_data is None:
            return None
        
        user = self.user_repo.get(token_data.user_id)
        if user is None:
            return None
        
        return user
    
    def login(self, user_credentials: UserLogin) -> Optional[Token]:
        """
        Authenticate user and return access token.
        
        Args:
            user_credentials: User login credentials
            
        Returns:
            Token if authentication successful, None otherwise
        """
        user = self.authenticate_user(user_credentials.email, user_credentials.password)
        if not user:
            return None
        
        # Update last login
        self.user_repo.update_last_login(user.id)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    def is_active_user(self, user: User) -> bool:
        """
        Check if user is active.
        
        Args:
            user: User instance
            
        Returns:
            True if user is active, False otherwise
        """
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """
        Check if user is a superuser.
        
        Args:
            user: User instance
            
        Returns:
            True if user is superuser, False otherwise
        """
        return user.is_superuser and user.is_active
