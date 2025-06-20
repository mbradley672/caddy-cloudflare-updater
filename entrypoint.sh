#!/bin/bash

# entrypoint.sh - Flexible entrypoint for different run modes

set -e

# Function to run one-time sync
run_once() {
    echo "Running one-time DNS sync..."
    python /app/main.py
}

# Function to run with file watcher
run_watcher() {
    echo "Starting file watcher mode..."
    python /app/watcher.py
}

# Function to run with cron
run_cron() {
    echo "Starting cron mode..."
    # Start cron daemon
    cron
    echo "Cron daemon started"
    # Keep container running and show logs
    tail -f /var/log/caddy-updater.log
}

# Function to run cron + watcher (hybrid mode)
run_hybrid() {
    echo "Starting hybrid mode (cron + watcher)..."
    # Start cron daemon
    cron
    echo "Cron daemon started"
    # Start watcher in background and show logs
    python /app/watcher.py &
    echo "File watcher started"
    # Keep container running and show logs
    tail -f /var/log/caddy-updater.log
}

# Validate required environment variables
check_env() {
    if [ -z "$CF_API_TOKEN" ]; then
        echo "ERROR: CF_API_TOKEN environment variable is required"
        exit 1
    fi
    if [ -z "$CF_ZONE_ID" ]; then
        echo "ERROR: CF_ZONE_ID environment variable is required"
        exit 1
    fi
    if [ -z "$CF_DOMAIN" ]; then
        echo "ERROR: CF_DOMAIN environment variable is required"
        exit 1
    fi
}

# Check if Caddyfile exists
check_caddyfile() {
    if [ ! -f "$CADDYFILE_PATH" ]; then
        echo "WARNING: Caddyfile not found at $CADDYFILE_PATH"
        echo "Make sure to mount your Caddyfile to the container"
        echo "Example: -v /path/to/Caddyfile:$CADDYFILE_PATH:ro"
    fi
}

# Main execution
echo "=== Caddy Cloudflare DNS Updater ==="
echo "Run mode: $RUN_MODE"
echo "Caddyfile path: $CADDYFILE_PATH"
echo "Log level: $LOG_LEVEL"

# Validate environment
check_env
check_caddyfile

# Create log file if it doesn't exist
touch /var/log/caddy-updater.log

# Run based on mode
case "$RUN_MODE" in
    "once")
        run_once
        ;;
    "watcher")
        run_watcher
        ;;
    "cron")
        run_cron
        ;;
    "hybrid")
        run_hybrid
        ;;
    *)
        echo "ERROR: Invalid RUN_MODE. Must be one of: once, watcher, cron, hybrid"
        echo "Defaulting to watcher mode..."
        run_watcher
        ;;
esac
