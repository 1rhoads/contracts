import sqlite3
import os
import glob
import re
import json
import numpy as np
import io
from util.categories import extract_categories
from util.llm import get_embedding

# Configuration
DB_NAME = "instance/contracts.db"
MARKDOWN_DIR = "data/markdown"

def init_db():
    if not os.path.exists('instance'):
        os.makedirs('instance')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create main table
    c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        vendor TEXT,
        categories TEXT,
        content TEXT
    )
    ''')
    # Create FTS table
    c.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
        title, content, content='documents', content_rowid='id'
    )
    ''')

    # Create Chunks table for RAG
    c.execute('''
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        page_number INTEGER,
        content TEXT,
        embedding BLOB,
        FOREIGN KEY(document_id) REFERENCES documents(id)
    )
    ''')
    
    # Triggers to keep FTS in sync
    c.execute('''
    CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
      INSERT INTO documents_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    ''')
    c.execute('''
    CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
      INSERT INTO documents_fts(documents_fts, rowid, content) VALUES('delete', old.id, old.content);
    END;
    ''')
    c.execute('''
    CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
      INSERT INTO documents_fts(documents_fts, rowid, content) VALUES('delete', old.id, old.content);
      INSERT INTO documents_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

def ingest_files():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if we already have data
    files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    # Sort files to ensure consistent order if possible, though updates won't change ID
    files.sort()
    
    print(f"Scanning {len(files)} files...")
    
    new_count = 0
    updated_count = 0
    
    for filepath in files:
        filename = os.path.basename(filepath)
        
        # title cleaning logic
        title = filename.replace('.md', '').replace('.pdf', '')
        title = title.replace('_', ' ')
        title = re.sub(r'Exhibit\s+B\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'DMS\s+Attachment\s+[A-Z0-9]+\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'Price\s+Sheet\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^\s*[-–]\s*', '', title)
        title = title.title()
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Vendor is essentially the cleaned title for now, or we can use the filename stem
        vendor = title 
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract Categories
        cats = extract_categories(content)
        cats_json = json.dumps(cats)

        # Check if file exists in DB
        existing = c.execute("SELECT id FROM documents WHERE filename = ?", (filename,)).fetchone()
        if existing:
            # Update content
            # Only update if changed? For now, force update to get new metadata
            c.execute("UPDATE documents SET title=?, vendor=?, categories=?, content=? WHERE id=?", 
                      (title, vendor, cats_json, content, existing[0]))
            updated_count += 1
            print(f"Updated: {filename} (Cats: {len(cats)})")
        else:
            c.execute("INSERT INTO documents (title, filename, vendor, categories, content) VALUES (?, ?, ?, ?, ?)", 
                      (title, filename, vendor, cats_json, content))
            doc_id = c.lastrowid
            new_count += 1
            print(f"Imported: {filename} (Cats: {len(cats)})")

            # --- RAG: Chunking & Embedding ---
            print(f"  generating embeddings for {filename}...")
            # Split by pages
            page_splits = re.split(r'(^## Page \d+\n)', content, flags=re.MULTILINE)
            current_page = 1
            
            # Helper to insert chunk
            def insert_chunk(doc_id, page_num, text):
                if not text.strip(): return
                try:
                    emb = get_embedding(text)
                    # Convert numpy dict to bytes
                    emb_blob = emb.tobytes()
                    c.execute("INSERT INTO chunks (document_id, page_number, content, embedding) VALUES (?, ?, ?, ?)",
                              (doc_id, page_num, text, emb_blob))
                except Exception as e:
                    print(f"Error embedding page {page_num}: {e}")

            if len(page_splits) > 1:
                for i in range(1, len(page_splits), 2):
                    header = page_splits[i].strip()
                    page_content = page_splits[i+1]
                    try:
                        num_match = re.search(r'(\d+)', header)
                        if num_match:
                            current_page = int(num_match.group(1))
                    except:
                        pass
                    
                    full_chunk_text = f"{header}\n{page_content}"
                    insert_chunk(doc_id, current_page, full_chunk_text)
            else:
                # Single chunk
                insert_chunk(doc_id, 1, content)
        
    conn.commit()
    conn.close()
    print(f"Ingestion complete. Added {new_count} new, Updated {updated_count} existing documents.")


if __name__ == "__main__":
    init_db()
    ingest_files()
