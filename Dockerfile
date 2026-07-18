# JARVIS-X Global Sentient Mirror Deployment
FROM python:3.11-slim

# Avoid writing .pyc files & buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for audio/opencv if needed (minimized for cloud)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port (default 8080 for Fly.io/Render)
EXPOSE 8080

# Start the FastAPI sentience hub
CMD ["python", "server.py"]
