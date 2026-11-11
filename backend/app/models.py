"""
models.py - SQLAlchemy ORM models.

Defines the database tables as Python classes.
Each class maps to a PostgreSQL table.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Student(Base):
    """
    Student model - represents the 'students' table in PostgreSQL.

    Columns:
        id       - Auto-incrementing primary key
        name     - Student's full name (required)
        email    - Student's email address (required, unique)
        course   - Course the student is enrolled in (required)
        created_at - Timestamp when the record was created (auto-set)
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    course = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
