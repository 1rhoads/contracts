
import os
import pdfplumber

PDF_DIR = "data/pdfs"
files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]

print(f"{'Filename':<50} | {'Pages':<5} | {'Size (MB)':<10}")
print("-" * 70)

for f in files:
    path = os.path.join(PDF_DIR, f)
    try:
        with pdfplumber.open(path) as pdf:
            pages = len(pdf.pages)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            if pages > 400: # Threshold 400
                print(f"{f:<50} | {pages:<5} | {size_mb:.2f}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
