import os
import fitz  # Directories

PDF_DIR = "data/pdfs"
OUTPUT_DIR = "data/markdown"

import pdfplumber

def convert_pdf_to_md(pdf_path, md_path):
    try:
        text_content = []
        
        # Add Title based on filename
        title = os.path.basename(pdf_path).replace('.pdf', '').replace('_', ' ')
        text_content.append(f"# {title}\n")
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            if total_pages > 500:
                print(f"Skipping {pdf_path}: Too many pages ({total_pages}) for bulk processing.")
                text_content.append(f"> **Note**: This document has {total_pages} pages and was skipped during bulk conversion to save resources.\n")
                # Create a placeholder file so we don't retry it every time
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(text_content))
                return True

            for i, page in enumerate(pdf.pages):
                # print(f"  Processing page {i + 1}/{total_pages}...", end='\r', flush=True)
                text_content.append(f"## Page {i + 1}\n")
                
                # Extract tables first
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        # Convert table to markdown
                        if not table: continue
                        
                        # Filter out empty rows/None
                        cleaned_table = [[cell if cell else "" for cell in row] for row in table]
                        
                        # Markdown table formatting
                        if cleaned_table:
                             # Header
                            header = cleaned_table[0]
                            text_content.append("| " + " | ".join(header) + " |")
                            text_content.append("| " + " | ".join(["---"] * len(header)) + " |")
                            # Rows
                            for row in cleaned_table[1:]:
                                text_content.append("| " + " | ".join(row) + " |")
                            text_content.append("\n")
                
                # Extract text (filtering out text inside tables is hard, so we just dump text too)
                # Ideally we deduct table bboxes, but for V1 let's append text below
                text = page.extract_text()
                if text:
                    text_content.append(text)
                
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
    
    if os.path.exists(m_path):
        # Optional: Check size > 0?
        # print(f"Skipping existing: {pdf_file}")
        return True
        
    if "Mainline_Information_Systems_LLC.pdf" in pdf_file:
        print(f"Skipping large file: {pdf_file}")
        return False

    # print(f"Starting: {pdf_file}") # Optional: reduce clutter
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
