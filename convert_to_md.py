import os
import fitz  # Directories

PDF_DIR = "data/pdfs"
OUTPUT_DIR = "data/markdown"


import pymupdf4llm

def convert_pdf_to_md(pdf_path, md_path):
    try:
        # Get title from filename
        title = os.path.basename(pdf_path).replace('.pdf', '').replace('_', ' ')
        
        # Use pymupdf4llm for high-quality Markdown conversion
        # It handles tables, headers, and multi-column layouts automatically
        chunks = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
        
        text_content = []
        text_content.append(f"# {title}\n")
        
        for i, chunk in enumerate(chunks):
            text_content.append(f"## Page {i + 1}\n")
            text_content.append(chunk.get('text', ''))
            text_content.append("\n---\n")
            
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(text_content))
            
        print(f"Converted: {md_path}")
        return True
    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")
        return False

# Helper for process pool must be top-level
def process_file(pdf_file):
    p_path = os.path.join(PDF_DIR, pdf_file)
    m_path = os.path.join(OUTPUT_DIR, pdf_file.replace(".pdf", ".md"))
    
    # Always re-convert to ensure standardization across all files
    # if os.path.exists(m_path):
    #    return True

    if convert_pdf_to_md(p_path, m_path):
        return True
    return False

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    # Sort files: Process small files first by size?
    # Simple alphabetic sort is fine, or sort by size if we want quick wins.
    # files.sort(key=lambda x: os.path.getsize(os.path.join(PDF_DIR, x))) # Optional
    files.sort()
    
    print(f"Found {len(files)} PDFs. Resuming conversion with 4 workers...")
    
    import concurrent.futures
    import time
    
    start_time = time.time()
    successful = 0
    
    # Use fewer workers to avoid OOM on large PDFs
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(process_file, files)
        for res in results:
            if res:
                successful += 1

    duration = time.time() - start_time
    print(f"\nBatch complete: {successful}/{len(files)} files checked/converted in {duration:.2f}s.")

if __name__ == "__main__":
    main()
