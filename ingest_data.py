import sqlite3
import os
import glob
import re
import json
import hashlib
from util.categories import extract_categories

try:
    from util.llm import get_embedding
    HAS_EMBEDDINGS = True
except ImportError:
    print("Warning: numpy or util.llm not found. Embeddings will be skipped.")
    HAS_EMBEDDINGS = False

# Configuration
DB_NAME = "instance/contracts.db"
MARKDOWN_DIR = "data/markdown"


def content_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def init_db():
    if not os.path.exists('instance'):
        os.makedirs('instance')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        vendor TEXT,
        categories TEXT,
        content TEXT,
        content_hash TEXT
    )
    ''')
    # Add content_hash column to existing databases that predate this schema
    try:
        c.execute("ALTER TABLE documents ADD COLUMN content_hash TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    c.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
        title, content, content='documents', content_rowid='id'
    )
    ''')
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
    c.execute('''
    CREATE TABLE IF NOT EXISTS product_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        vendor TEXT,
        oem TEXT,
        sku TEXT,
        description TEXT,
        price TEXT,
        unit TEXT,
        raw_line TEXT,
        FOREIGN KEY(document_id) REFERENCES documents(id)
    )
    ''')
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


def insert_chunk(cursor, doc_id, page_num, text):
    if not text.strip():
        return
    try:
        emb = get_embedding(text)
        cursor.execute(
            "INSERT INTO chunks (document_id, page_number, content, embedding) VALUES (?, ?, ?, ?)",
            (doc_id, page_num, text, emb.tobytes())
        )
    except Exception as e:
        print(f"  Error embedding page {page_num}: {e}")


def generate_chunks(cursor, doc_id, content):
    page_splits = re.split(r'(^## Page \d+\n)', content, flags=re.MULTILINE)
    if len(page_splits) > 1:
        for i in range(1, len(page_splits), 2):
            header = page_splits[i].strip()
            page_content = page_splits[i + 1] if i + 1 < len(page_splits) else ""
            num_match = re.search(r'(\d+)', header)
            page_num = int(num_match.group(1)) if num_match else i // 2 + 1
            insert_chunk(cursor, doc_id, page_num, f"{header}\n{page_content}")
    else:
        insert_chunk(cursor, doc_id, 1, content)


def ingest_files():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    files = sorted(glob.glob(os.path.join(MARKDOWN_DIR, "*.md")))
    print(f"Scanning {len(files)} files...")

    new_count = 0
    updated_count = 0
    skipped_count = 0

    for filepath in files:
        filename = os.path.basename(filepath)

        title = filename.replace('.md', '').replace('.pdf', '')
        title = title.replace('_', ' ')
        title = re.sub(r'Exhibit\s+B\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'DMS\s+Attachment\s+[A-Z0-9]+\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'Price\s+Sheet\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^\s*[-–]\s*', '', title)
        title = title.title()
        title = re.sub(r'\s+', ' ', title).strip()

        vendor = title

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_hash = content_hash(content)
        cats = extract_categories(content)
        cats_json = json.dumps(cats)

        existing = c.execute(
            "SELECT id, content_hash FROM documents WHERE filename = ?", (filename,)
        ).fetchone()

        if existing:
            doc_id, stored_hash = existing
            if stored_hash == new_hash:
                skipped_count += 1
                continue  # Content unchanged — nothing to do

            c.execute(
                "UPDATE documents SET title=?, vendor=?, categories=?, content=?, content_hash=? WHERE id=?",
                (title, vendor, cats_json, content, new_hash, doc_id)
            )
            updated_count += 1
            print(f"Updated: {filename} (Cats: {len(cats)})")

            if HAS_EMBEDDINGS:
                c.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))
                print(f"  Re-generating embeddings for {filename}...")
                generate_chunks(c, doc_id, content)
        else:
            c.execute(
                "INSERT INTO documents (title, filename, vendor, categories, content, content_hash) VALUES (?, ?, ?, ?, ?, ?)",
                (title, filename, vendor, cats_json, content, new_hash)
            )
            doc_id = c.lastrowid
            new_count += 1
            print(f"Imported: {filename} (Cats: {len(cats)})")

            if HAS_EMBEDDINGS:
                print(f"  Generating embeddings for {filename}...")
                generate_chunks(c, doc_id, content)
            else:
                print(f"  Skipping embeddings (missing dependencies)")

    conn.commit()
    conn.close()
    print(f"Ingestion complete. Added {new_count} new, updated {updated_count}, skipped {skipped_count} unchanged.")


if __name__ == "__main__":
    init_db()
    ingest_files()
