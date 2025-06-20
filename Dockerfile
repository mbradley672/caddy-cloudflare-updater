FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    inotify-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py watcher.py entrypoint.sh ./
COPY crontab.txt /etc/cron.d/updater-cron

# Set up cron job
RUN chmod 0644 /etc/cron.d/updater-cron && \
    crontab /etc/cron.d/updater-cron && \
    chmod +x entrypoint.sh

# Environment variables with defaults
ENV CADDYFILE_PATH=/etc/caddy/Caddyfile
ENV LOG_LEVEL=INFO
ENV RUN_MODE=watcher

# Create log directory
RUN mkdir -p /var/log

# Use entrypoint script for flexibility
CMD ["./entrypoint.sh"]
