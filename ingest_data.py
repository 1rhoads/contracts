import sqlite3
import os
import glob
import re

# Configuration
DB_NAME = "data/contracts.db"
MARKDOWN_DIR = "data/markdown"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create main table
    c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        content TEXT
    )
    ''')
    # Create FTS table
    c.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
        title, content, content='documents', content_rowid='id'
    )
    ''')
    
    # Triggers to keep FTS in sync
    c.execute('''
    CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
      INSERT INTO documents_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    ''')
    # (We can add update/delete triggers if needed, but for now specific ingestion is enough)
    
    conn.commit()
    conn.close()
    print("Database initialized.")

def ingest_files():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if we already have data
    files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    print(f"Scanning {len(files)} files...")
    
    new_count = 0
    for filepath in files:
        filename = os.path.basename(filepath)
        
        # Check if file exists in DB
        existing = c.execute("SELECT id FROM documents WHERE filename = ?", (filename,)).fetchone()
        if existing:
            continue
            
        # title is filename without ext and with spaces
        title = filename.replace('.md', '').replace('_', ' ')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        c.execute("INSERT INTO documents (title, filename, content) VALUES (?, ?, ?)", (title, filename, content))
        new_count += 1
        print(f"Imported: {filename}")
        
    conn.commit()
    conn.close()
    if new_count > 0:
        print(f"Ingestion complete. Added {new_count} new documents.")
    else:
        print("No new documents to ingest.")


if __name__ == "__main__":
    init_db()
    ingest_files()
