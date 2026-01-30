
import time
import pymupdf4llm
import os

PDF_PATH = "data/pdfs/Mainline_Information_Systems_LLC.pdf"
OUTPUT_PATH = "test_mainline_pymupdf.md"

if not os.path.exists(PDF_PATH):
    print(f"File not found: {PDF_PATH}")
    exit(1)

print(f"Starting conversion of {PDF_PATH} using pymupdf4llm...")
start_time = time.time()

try:
    # Convert matches to markdown
    md_text = pymupdf4llm.to_markdown(PDF_PATH)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(md_text)
        
    duration = time.time() - start_time
    print(f"Conversion complete in {duration:.2f} seconds.")
    print(f"Output saved to {OUTPUT_PATH}")
    
    # Preview
    print("-" * 40)
    print(md_text[:500])
    print("-" * 40)
    
    # Check for pipes (tables)
    pipe_count = md_text.count("|")
    print(f"Found {pipe_count} pipe characters (potential table parts).")

except Exception as e:
    print(f"Error: {e}")
