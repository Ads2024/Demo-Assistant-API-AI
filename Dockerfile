# Use Python 3.11.5 as base image
FROM python:3.11.5-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501 \
    PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies in stages
COPY requirements.txt .

# Stage 1: Install core dependencies
RUN pip install --no-cache-dir \
    "typing-extensions==4.11.0" \
    "PyYAML==6.0.2" \
    "openai==1.55.0" \
    "python-dotenv==1.0.1" \
    "streamlit==1.38.0" \
    "streamlit-chat==0.1.1"

# Stage 2: Install data processing dependencies
RUN pip install --no-cache-dir \
    "pandas==2.1.3" \
    "numpy>=1.24.0" \
    "scipy==1.14.1" \
    "scikit_learn==1.5.2" \
    "matplotlib==3.9.3" \
    "plotly==5.24.1" \
    "bokeh==3.6.2"

# Stage 3: Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*

# Copy project files
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p /app/src /app/assets /app/.streamlit

# Set Streamlit configurations for docker
RUN echo '\
[server]\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
' > /app/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to run the application
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]