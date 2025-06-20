FROM python:3.11-slim

RUN apt update && apt install -y cron inotify-tools \
 && pip install --no-cache-dir requests caddyparser watchdog

WORKDIR /app
COPY . .

# Install cron job
COPY crontab.txt /etc/cron.d/updater-cron
RUN chmod 0644 /etc/cron.d/updater-cron && crontab /etc/cron.d/updater-cron

CMD ["sh", "-c", "cron && python watcher.py"]
