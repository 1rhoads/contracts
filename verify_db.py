import sqlite3

DB_NAME = "contracts.db"

def verify():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check documents count
    try:
        c.execute("SELECT COUNT(*) FROM documents")
        count = c.fetchone()[0]
        print(f"Documents count: {count}")
    except Exception as e:
        print(f"Error checking documents: {e}")
        
    # Check FTS count
    try:
        c.execute("SELECT COUNT(*) FROM documents_fts")
        fts_count = c.fetchone()[0]
        print(f"FTS documents count: {fts_count}")
    except Exception as e:
        print(f"Error checking FTS: {e}")
        
    # Try search
    query = "tanium"
    try:
        sql = """
        SELECT d.id, d.title, d.filename, snippet(documents_fts, 1, '<mark>', '</mark>', '...', 64) as snippet 
        FROM documents_fts 
        JOIN documents d ON documents_fts.rowid = d.id
        WHERE documents_fts MATCH ? 
        ORDER BY rank
        LIMIT 50
        """
        results = c.execute(sql, (f'"{query}"',)).fetchall()
        print(f"Search for '{query}' returned {len(results)} results")
        if len(results) > 0:
            print("First resulting snippet:")
            print(results[0][3]) # snippet is the 4th column (index 3)
    except Exception as e:
        print(f"Error searching: {e}")

    conn.close()

if __name__ == "__main__":
    verify()
