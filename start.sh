#!/bin/sh
set -e

# Always initialize DB schema (idempotent) and sync any new/changed markdown files.
# The content-hash check in ingest_data.py makes this fast on restarts — unchanged
# documents are skipped in milliseconds, so there's no penalty for running every time.
echo "Initializing database and syncing documents..."
python3 ingest_data.py

echo "Extracting products..."
python3 extract_products.py

# Start the application
exec gunicorn -b 0.0.0.0:8000 app:app
