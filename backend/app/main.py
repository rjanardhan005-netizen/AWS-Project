"""
main.py - FastAPI application entry point.

This is the core of the backend. It defines:
  - Health check endpoint (/api/health)
  - CRUD endpoints for student records (/api/students)
  - Database table creation on startup
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from .database import engine, get_db, Base
from .models import Student
from .schemas import StudentCreate, StudentResponse, HealthResponse

# Create the FastAPI application instance.
app = FastAPI(
    title="Student Records API",
    description="A simple API for managing student records - Project 16",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

@app.on_event("startup")
def on_startup():
    """
    Runs when the application starts.
    Creates all database tables if they don't already exist.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    Verifies the API is running and can connect to PostgreSQL.
    Returns HTTP 200 if healthy, HTTP 503 if the database is unreachable.
    """
    try:
        # Try a simple query to verify the database connection.
        db.execute(text("SELECT 1"))
    except Exception:
        # Database is unreachable — report unhealthy with 503.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )

    return HealthResponse(
        status="healthy",
        service="student-records-api",
        database="connected",
        version="1.0.0",
    )


# ──────────────────────────────────────────────
# Student CRUD Endpoints
# ──────────────────────────────────────────────

@app.get("/api/students", response_model=List[StudentResponse], tags=["Students"])
def list_students(db: Session = Depends(get_db)):
    """Retrieve all student records, newest first."""
    students = db.query(Student).order_by(Student.created_at.desc()).all()
    return students


@app.post(
    "/api/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student record.
    Returns 400 if a student with the same email already exists.
    """
    # Check for duplicate email.
    existing = db.query(Student).filter(Student.email == student.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with email '{student.email}' already exists.",
        )

    new_student = Student(
        name=student.name,
        email=student.email,
        course=student.course,
    )
    db.add(new_student)
    try:
        db.commit()
    except IntegrityError:
        # The unique constraint handles concurrent duplicate requests.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with email '{student.email}' already exists.",
        )
    db.refresh(new_student)
    return new_student


@app.get("/api/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Retrieve a single student by ID. Returns 404 if not found."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found.",
        )
    return student


@app.delete("/api/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student by ID. Returns 404 if not found."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found.",
        )
    db.delete(student)
    db.commit()
