#!/bin/sh
set -e

# Auto-initialize database if it doesn't exist
if [ ! -f "instance/contracts.db" ]; then
    echo "Database not found. initializing and ingesting data..."
    python3 ingest_data.py
fi

# Start the application
exec gunicorn -b 0.0.0.0:8000 app:app
