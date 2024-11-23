# Use Python 3.11.5 as base image
FROM python:3.11.5-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p /app/src /app/assets /app/.streamlit

# Expose port
EXPOSE 8501

# Set Streamlit configurations for docker
RUN echo '\
[server]\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
' > /app/.streamlit/config.toml

# Command to run the application
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]