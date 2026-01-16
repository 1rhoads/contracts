import sqlite3
import os
import glob
import re

DB_NAME = "contracts.db"
MD_DIR = "markdown"

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
    c.execute("SELECT COUNT(*) FROM documents")
    if c.fetchone()[0] > 0:
        print("Database already populated. Skipping ingestion (delete db to re-ingest).")
        conn.close()
        return

    files = glob.glob(os.path.join(MD_DIR, "*.md"))
    print(f"Ingesting {len(files)} files...")
    
    for filepath in files:
        filename = os.path.basename(filepath)
        # title is filename without ext and with spaces
        title = filename.replace('.md', '').replace('_', ' ')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        c.execute("INSERT INTO documents (title, filename, content) VALUES (?, ?, ?)", (title, filename, content))
        
    conn.commit()
    conn.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    init_db()
    ingest_files()
