# docker-compose.yml
version: '3.8'

services:
  # Web Interface
  web:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    command: streamlit run app.py --server.port=8501 --server.address=0.0.0.0
    restart: unless-stopped

  # API Server
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
      - PORT=5000
    command: python api_server.py
    restart: unless-stopped
    depends_on:
      - web

  # Optional: PostgreSQL for production data storage
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: scraperpro
  #     POSTGRES_USER: scraper
  #     POSTGRES_PASSWORD: your_secure_password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
