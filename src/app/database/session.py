"""
Database session management utilities.
"""
from sqlalchemy.orm import Session
from typing import Generator, Optional
from contextlib import contextmanager

from .base import SessionLocal


class DatabaseSession:
    """Database session manager with context support."""
    
    def __init__(self):
        self._session: Optional[Session] = None
    
    @property
    def session(self) -> Session:
        """Get current database session."""
        if self._session is None:
            self._session = SessionLocal()
        return self._session
    
    def close(self):
        """Close the database session."""
        if self._session:
            self._session.close()
            self._session = None
    
    def commit(self):
        """Commit the current transaction."""
        if self._session:
            self._session.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        if self._session:
            self._session.rollback()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Yields:
        Generator[Session, None, None]: Database session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session_dependency() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Yields:
        Generator[Session, None, None]: Database session
    """
    with get_db_session() as session:
        yield session
