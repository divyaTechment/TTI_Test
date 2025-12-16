"""
Base Pydantic schemas with common functionality.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class IDSchema(BaseSchema):
    """Schema with ID field."""
    
    id: int = Field(..., description="Unique identifier")


class BaseResponseSchema(TimestampSchema, IDSchema):
    """Base response schema with ID and timestamps."""
    pass


class PaginationSchema(BaseSchema):
    """Pagination schema."""
    
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")


class ErrorSchema(BaseSchema):
    """Error response schema."""
    
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    field: Optional[str] = Field(None, description="Field that caused the error")
