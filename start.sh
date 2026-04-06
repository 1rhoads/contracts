#!/bin/sh

# Sync documents into the database. Content-hash tracking means unchanged files
# are skipped instantly, so this is safe to run on every startup.
echo "Initializing database and syncing documents..."
python3 ingest_data.py
if [ $? -ne 0 ]; then
    echo "WARNING: ingest_data.py failed. The app will start but search data may be stale."
fi

echo "Extracting products..."
python3 extract_products.py
if [ $? -ne 0 ]; then
    echo "WARNING: extract_products.py failed. Product comparison may be unavailable."
fi

# 1 worker: prevents multiple processes each loading torch/sentence-transformers
# timeout 120: allows slow first-request model warm-up without killing the worker
echo "Starting gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --timeout 120 \
    app:app
