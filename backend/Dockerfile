# ============================================================
# Backend Dockerfile - Python FastAPI Application
# ============================================================
# This Dockerfile builds the FastAPI backend container.
#
# How it works:
#   1. Starts from the official Python 3.11 slim image.
#   2. Copies and installs Python dependencies.
#   3. Copies the application source code.
#   4. Runs the FastAPI server with Uvicorn on port 8000.
#
# The backend is NOT exposed publicly. Only Nginx can reach
# it through the Docker internal network.
# ============================================================

FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy only the requirements file first.
# This layer is cached — dependencies are only reinstalled
# when requirements.txt changes, speeding up rebuilds.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code.
COPY ./app ./app

# Expose port 8000 for documentation purposes.
# (This does NOT publish the port to the host.)
EXPOSE 8000

# Start the FastAPI server using Uvicorn.
# --host 0.0.0.0 makes it accessible from other containers.
# --port 8000 is the port Nginx will proxy to.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
