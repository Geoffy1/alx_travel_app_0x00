# Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /code

# Install system dependencies required for psycopg2 and netcat-traditional
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    musl-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire alx_travel_app application code into the container
COPY alx_travel_app/ /code/alx_travel_app
# Set the working directory inside the container to the Django project root
WORKDIR /code/alx_travel_app

EXPOSE 8000
