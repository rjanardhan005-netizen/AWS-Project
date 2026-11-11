"""
schemas.py - Pydantic models for request/response validation.

These schemas define the shape of data going in and out of the API.
Pydantic validates all incoming data automatically.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class StudentCreate(BaseModel):
    """Schema for creating a new student (request body)."""
    name: str = Field(..., min_length=1, max_length=100, examples=["John Doe"])
    email: EmailStr = Field(..., max_length=100, examples=["john@example.com"])
    course: str = Field(..., min_length=1, max_length=100, examples=["Computer Science"])


class StudentResponse(BaseModel):
    """Schema for returning student data (response body)."""
    id: int
    name: str
    email: str
    course: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    service: str
    database: str
    version: str
