# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs output data/clients data/configs

# Expose ports
EXPOSE 8501 5000

# Default command (can be overridden)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

