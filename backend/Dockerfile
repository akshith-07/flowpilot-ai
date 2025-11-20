FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt /app/requirements/base.txt
COPY requirements/development.txt /app/requirements/development.txt
RUN pip install --upgrade pip
RUN pip install -r requirements/development.txt

# Copy project
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Run migrations and collect static files
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
