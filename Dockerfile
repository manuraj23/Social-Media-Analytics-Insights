# Use slim image with Python 3.11+
FROM python:3.11-slim

# System deps (build tools + fonts for matplotlib if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy requirement first for better layer cache
COPY requirements.txt /app/requirements.txt

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and assets
COPY . /app

# Streamlit config to run in container
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

# Expose app port
EXPOSE 8501

# Optional: avoid Streamlit opening the browser
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
