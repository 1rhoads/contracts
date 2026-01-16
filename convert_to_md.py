import os
import fitz  # PyMuPDF

PDF_DIR = "pdfs"
MD_DIR = "markdown"

def convert_pdf_to_md(pdf_path, md_path):
    try:
        doc = fitz.open(pdf_path)
        text_content = []
        
        # Add Title based on filename
        title = os.path.basename(pdf_path).replace('.pdf', '').replace('_', ' ')
        text_content.append(f"# {title}\n")
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text_content.append(f"## Page {page_num + 1}\n")
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
    if not os.path.exists(MD_DIR):
        os.makedirs(MD_DIR)
        
    files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    print(f"Found {len(files)} PDFs to convert.")
    
    for filename in files:
        pdf_path = os.path.join(PDF_DIR, filename)
        md_filename = filename.replace(".pdf", ".md")
        md_path = os.path.join(MD_DIR, md_filename)
        
        convert_pdf_to_md(pdf_path, md_path)

if __name__ == "__main__":
    main()
