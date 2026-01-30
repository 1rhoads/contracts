
import pymupdf4llm
import json

PDF_PATH = "data/pdfs/SGS_Technologie_LLC.pdf"

try:
    chunks = pymupdf4llm.to_markdown(PDF_PATH, page_chunks=True)
    print(f"Type: {type(chunks)}")
    if isinstance(chunks, list) and len(chunks) > 0:
        print(f"First element keys: {chunks[0].keys()}")
        print(f"First element text sample: {chunks[0].get('text', '')[:100]}")
except Exception as e:
    print(f"Error: {e}")
