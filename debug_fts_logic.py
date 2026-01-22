import sqlite3
import re

DB_NAME = "data/contracts.db"

def run_sql(conn, q):
    try:
        sql = """
        SELECT count(*) 
        FROM documents_fts 
        WHERE documents_fts MATCH ? 
        """
        count = conn.execute(sql, (q,)).fetchone()[0]
        return count
    except Exception as e:
        return f"ERROR: {e}"

def sanitize(query_str):
    # Split by whitespace to handle multiple terms
    # Simple split; doesn't handle existing complex quoting perfectly but good for single terms
    tokens = query_str.split()
    processed = []
    for t in tokens:
        if '-' in t and not (t.startswith('"') and t.endswith('"')):
            processed.append(f'"{t}"')
        else:
            processed.append(t)
    return " ".join(processed)

def fallback(query_str):
    # Replace quotes and hyphens with spaces
    # This relaxes "TAN-CORE" to "TAN CORE" (AND)
    return query_str.replace('"', ' ').replace('-', ' ')

def test_logic(raw_input):
    print(f"User Input: '{raw_input}'")
    conn = sqlite3.connect(DB_NAME)
    
    # Step 1: Sanitize
    s_query = sanitize(raw_input)
    print(f"Sanitized:  '{s_query}'")
    
    res = run_sql(conn, s_query)
    print(f"Result:     {res}")
    
    # Step 2: Fallback if needed
    if res == 0 or isinstance(res, str):
        f_query = fallback(raw_input) # fallback from RAW or Sanitized? From Raw usually better to reset
        # Actually logic in app.py uses query.replace so it starts from raw
        f_query = fallback(raw_input)
        print(f"Fallback:   '{f_query}'")
        res_f = run_sql(conn, f_query)
        print(f"Fb Result:  {res_f}")
        
    conn.close()
    print("-" * 20)

if __name__ == "__main__":
    # Case 1: The working SKU
    test_logic("TAN-CORE-TAAS")
    
    # Case 2: Multi-term
    test_logic("Tanium TAN-CORE-TAAS")
    
    # Case 3: Non-existent SKU (check fallback)
    test_logic("TAN-FAKE-SKU")

    # Case 4: The error case (raw hyphen verified error in previous step)
    # logic() function handles it via sanitize
