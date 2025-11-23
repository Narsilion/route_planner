#!/usr/bin/env bash

set -e  # Exit on any error

# Set environment variables
export FLASK_APP=/app/flaskr
export FLASK_ENV=${FLASK_ENV:-production}

# Ensure data directory exists
mkdir -p /app/data/logs

# Run gunicorn with proper configuration
exec gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  --disable-redirect-access-to-syslog \
  flaskr:app
