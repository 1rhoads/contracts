import sqlite3
import re
import os

DB_NAME = "data/contracts.db"

def clean_title(filename):
    # Base: removal of extension
    title = filename.replace('.md', '').replace('.pdf', '')
    
    # 1. Replace underscores with spaces
    title = title.replace('_', ' ')
    
    # 2. Remove common prefixes (case insensitive)
    # "Exhibit B - ", "Exhibit B", "DMS Attachment ... "
    # Regex is best here.
    
    # Look for "Exhibit B" followed by optional space, hyphen, space
    title = re.sub(r'Exhibit\s+B\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
    
    # Look for "DMS Attachment X"
    title = re.sub(r'DMS\s+Attachment\s+[A-Z0-9]+\s*[-–]?\s*', '', title, flags=re.IGNORECASE)
    
    # Look for "Price Sheet"
    title = re.sub(r'Price\s+Sheet\s*[-–]?\s*', '', title, flags=re.IGNORECASE)

    # 3. Clean up generic terms if they are at the start
    # e.g. " - Presidio" -> "Presidio"
    title = re.sub(r'^\s*[-–]\s*', '', title)
    
    # 4. Title Case (but preserve generic acronyms if possible? Title() is usually fine)
    title = title.title()
    
    # 5. Collapse multiple spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def migrate_db():
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    rows = c.execute("SELECT id, filename, title FROM documents").fetchall()
    
    print(f"Checking {len(rows)} documents...")
    
    updates = 0
    for row in rows:
        doc_id, filename, old_title = row
        
        # Use filename as source of truth for "clean" generation, 
        # or use old_title? Filename is usually safer if old_title was just filename.replace.
        # Let's use filename to be fresh.
        new_title = clean_title(filename)
        
        if new_title != old_title:
            c.execute("UPDATE documents SET title = ? WHERE id = ?", (new_title, doc_id))
            print(f"  [UPDATE] '{old_title}' -> '{new_title}'")
            updates += 1
            
    conn.commit()
    conn.close()
    print(f"Migration complete. Updated {updates} titles.")

if __name__ == "__main__":
    migrate_db()
