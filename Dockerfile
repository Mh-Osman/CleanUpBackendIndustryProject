# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create folder for static files
# RUN mkdir -p /app/staticfiles

# Collect static files
# RUN python manage.py collectstatic --noinput

# Command to run Gunicorn with Uvicorn workers
CMD ["gunicorn", "Talkfusion.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]