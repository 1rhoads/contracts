FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (sqlite3)
RUN apt-get update && apt-get install -y sqlite3 tesseract-ocr libgl1 && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model so it's cached in the image.
# Without this, the first container startup tries to download ~90MB from HuggingFace
# at runtime, which hangs or fails if the host has no outbound internet access.
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Download PDF data during build
# This ensures the files are baked into the image and available without a volume
RUN python3 download_pdfs.py

# Expose the Gunicorn port
EXPOSE 8000

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Run the startup script
CMD ["./start.sh"]
