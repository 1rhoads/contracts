import sqlite3
import os

DB_NAME = "data/contracts.db"

def test_query(query_str):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    print(f"--- Testing Query: '{query_str}' ---")
    
    sql = """
    SELECT d.id, d.title, snippet(documents_fts, 1, '[', ']', '...', 64) as snippet 
    FROM documents_fts 
    JOIN documents d ON documents_fts.rowid = d.id
    WHERE documents_fts MATCH ? 
    LIMIT 5
    """
    
    try:
        rows = c.execute(sql, (query_str,)).fetchall()
        print(f"Result Count: {len(rows)}")
        for r in rows:
            print(f"Match: {r['title']}")
            print(f"Snippet: {r['snippet']}")
    except Exception as e:
        print(f"ERROR: {e}")
        
    conn.close()
    print("\n")

if __name__ == "__main__":
    # Test 1: Raw SKU as typically entered
    test_query("TAN-CORE-TAAS")
    
    # Test 2: Quoted SKU
    test_query('"TAN-CORE-TAAS"')
    
    # Test 3: Replaced hyphen with space (implicit AND)
    test_query("TAN CORE TAAS")
    
    # Test 4: Replaced hyphen with OR?
    test_query("TAN OR CORE OR TAAS")
