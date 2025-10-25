# Base image - Python 3.10 on a lightweight Linux distribution
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Django project into the container
COPY credit_approval/ /app/

# Expose port 8000 (Django's default development server port)
EXPOSE 8000

# Command to run when container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
