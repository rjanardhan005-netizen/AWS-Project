"""
database.py - Database connection and session management.

Uses SQLAlchemy to connect to PostgreSQL. All connection details
come from environment variables so nothing is hardcoded.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

# Build the database URL from environment variables.
# These are set in docker-compose.yml and read at runtime.
POSTGRES_USER = os.getenv("POSTGRES_USER", "student_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "student_pass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "student_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=int(POSTGRES_PORT),
    database=POSTGRES_DB,
)

# pool_pre_ping=True ensures stale connections are detected and replaced.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal is a factory for creating new database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models.
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI.
    Creates a new database session for each request and closes it afterwards.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
