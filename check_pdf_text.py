
import fitz # pymupdf

PDF_PATH = "data/pdfs/Mainline_Information_Systems_LLC.pdf"

try:
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    text = page.get_text()
    if text.strip():
        print("PDF has text layer.")
        print(text[:200])
    else:
        print("PDF appears to be scanned/image-only (no text detected on page 1).")
    doc.close()
except Exception as e:
    print(f"Error: {e}")
