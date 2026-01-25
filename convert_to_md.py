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
            for i, page in enumerate(pdf.pages):
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

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    print(f"Found {len(files)} PDFs to convert.")
    
    for filename in files:
        print(f"Processing: {filename}...")
        pdf_path = os.path.join(PDF_DIR, filename)
        md_filename = filename.replace(".pdf", ".md")
        md_path = os.path.join(OUTPUT_DIR, md_filename)
        
        convert_pdf_to_md(pdf_path, md_path)

if __name__ == "__main__":
    main()
