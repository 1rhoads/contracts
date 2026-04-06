import os
import json
import concurrent.futures
import time

import pymupdf4llm
from util.hasher import calculate_file_hash

PDF_DIR = "data/pdfs"
OUTPUT_DIR = "data/markdown"
STATE_FILE = "data/pdf_state.json"


def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def convert_pdf_to_md(pdf_path, md_path):
    try:
        title = os.path.basename(pdf_path).replace('.pdf', '').replace('_', ' ')
        chunks = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)

        text_content = [f"# {title}\n"]
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


def process_file(pdf_file):
    p_path = os.path.join(PDF_DIR, pdf_file)
    m_path = os.path.join(OUTPUT_DIR, pdf_file.replace(".pdf", ".md"))
    return convert_pdf_to_md(p_path, m_path)


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(PDF_DIR):
        print(f"PDF directory not found: {PDF_DIR}")
        return

    all_files = sorted(f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf"))
    state = load_state()

    # Filter to only files that changed or are missing their markdown output
    to_process = []
    file_hashes = {}
    for pdf_file in all_files:
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        md_path = os.path.join(OUTPUT_DIR, pdf_file.replace(".pdf", ".md"))
        current_hash = calculate_file_hash(pdf_path)
        file_hashes[pdf_file] = current_hash
        if state.get(pdf_file) == current_hash and os.path.exists(md_path):
            print(f"Skipping {pdf_file} (unchanged)")
        else:
            to_process.append(pdf_file)

    if not to_process:
        print("All PDFs are up to date.")
        return

    print(f"Converting {len(to_process)} PDFs with 4 workers...")
    start_time = time.time()
    successful = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_file, f): f for f in to_process}
        for future, filename in futures.items():
            try:
                if future.result():
                    successful += 1
                    state[filename] = file_hashes[filename]
            except Exception as e:
                print(f"Worker error for {filename}: {e}")

    save_state(state)
    duration = time.time() - start_time
    print(f"\nDone: {successful}/{len(to_process)} converted in {duration:.2f}s.")


if __name__ == "__main__":
    main()
