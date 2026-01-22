import os
import sqlite3
import re
from flask import Flask, render_template, request, abort, redirect, url_for
from markdown import markdown # We might need this, but we can display raw text or pre-rendered. 
# Actually, displaying markdown as HTML is better.
# Trying to import markdown, if not available we will just return text.

app = Flask(__name__)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'contracts.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def sanitize_query_fns(q):
    # Split by whitespace to handle multiple terms
    tokens = q.split()
    processed = []
    for t in tokens:
        # If term has hyphen and not already quoted, quote it
        if '-' in t and not (t.startswith('"') and t.endswith('"')):
            processed.append(f'"{t}"')
        else:
            processed.append(t)
    return " ".join(processed)

@app.route('/')
def index():
    query = request.args.get('q', '')
    results = []
    
    if query:
        conn = get_db_connection()
        # Use FTS5 snippet
        # snippet(documents_fts, -1, '<b>', '</b>', '...', 64)
        sql = """
        SELECT d.id, d.title, d.filename, snippet(documents_fts, 1, '<mark>', '</mark>', '...', 64) as snippet 
        FROM documents_fts 
        JOIN documents d ON documents_fts.rowid = d.id
        WHERE documents_fts MATCH ? 
        ORDER BY rank
        LIMIT 50
        """
        # Pass query standard FTS5 syntax. 
        # Spaces imply AND. Quotes imply PHRASE. OR is explicit.
        sanitized_query = sanitize_query_fns(query)
        
        try:
            # Attempt 1: Exact/Standard Query (Sanitized)
            results = conn.execute(sql, (sanitized_query,)).fetchall()
            
            # Attempt 2: Fallback (Relaxed)
            # If no results and query contains space or quotes or hyphens
            if not results:
                # Remove quotes AND replace hyphens with spaces to allow loose matching
                # "TAN-CORE" -> "TAN CORE" (AND)
                relaxed_query = query.replace('"', '').replace('-', ' ')
                
                # Only retry if relaxed is different from original sanitation (avoid redundant query)
                # Compare relaxed vs sanitized is hard because sanitized adds quotes vs relaxed replacing chars
                # Just check if relaxed is different from what we typically query
                if relaxed_query != query:
                     results = conn.execute(sql, (relaxed_query,)).fetchall()
                     
        except sqlite3.OperationalError:
            results = []
            
        conn.close()
        
    return render_template('index.html', query=query, results=results)

@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    conn = get_db_connection()
    doc = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    conn.close()
    
    if doc is None:
        abort(404)
        
    query = request.args.get('q', '')
    page_param = request.args.get('page')
    
    content = doc['content']
    
    # Split content into pages
    # Assumption: pages are separated by "\n## Page X\n" or similar
    # We will look for explicit delimiters inserted by convert_to_md.py
    import re
    
    # Regex to capture page number and content
    # Matches "## Page 1" followed by content until next "## Page" or end of string
    # We use capturing group for page num, and then the content.
    pages = []
    # Note: re.split might be easier, or finditer
    # The format is line: "## Page <num>"
    
    page_splits = re.split(r'(^## Page \d+\n)', content, flags=re.MULTILINE)
    
    # page_splits[0] is strictly preamble (often empty if file starts with page 1, or just the title)
    title_preamble = page_splits[0]
    
    # Then we have pairs: [delimiter, content, delimiter, content...]
    # We can reconstruct a dict map: { 1: "content...", 2: "content..." }
    page_map = {}
    
    current_page_num = 0
    if len(page_splits) > 1:
        for i in range(1, len(page_splits), 2):
            header = page_splits[i].strip() # "## Page 1"
            page_content = page_splits[i+1] if i+1 < len(page_splits) else ""
            
            # Extract number
            try:
                num_match = re.search(r'(\d+)', header)
                if num_match:
                    current_page_num = int(num_match.group(1))
                    page_map[current_page_num] = page_content
            except:
                pass
    else:
        # Fallback if regex didn't trigger (maybe old format), treat whole doc as page 1
        page_map[1] = content

    # --- Case 1: Viewing a specific page ---
    if page_param:
        try:
            target_page = int(page_param)
            if target_page in page_map:
                # Reconstruct just this page's markdown
                # We include the title preamble if it's page 1, strictly speaking title is mostly metadata now
                page_md = f"## Page {target_page}\n{page_map[target_page]}"
                if target_page == 1:
                    page_md = title_preamble + page_md
                
                return render_template('document.html', 
                                     doc=doc, 
                                     content=page_md, 
                                     current_page=target_page, 
                                     total_pages=max(page_map.keys()) if page_map else 1,
                                     query=query)
        except ValueError:
            pass # Invalid page number, fall through
            
    # --- Case 2: Searching (List of Pages) ---
    if query:
        matches = []
        # Parse query logic (loose vs strict) - replicating logic from index()
        normalized_query = query.replace('"', '').lower()
        query_terms = normalized_query.split()
        
        for p_num, p_text in page_map.items():
            text_lower = p_text.lower()
            
            # Check for match (Loose AND: all terms must be present)
            # If query was quoted originally, user might expect phrase, but for page searching
            # "contains all text" is usually a good enough filter.
            if all(term in text_lower for term in query_terms):
                # Generate simple snippet
                # Find first occurrence of first term
                idx = text_lower.find(query_terms[0])
                start = max(0, idx - 50)
                end = min(len(p_text), idx + 150)
                snippet = p_text[start:end]
                
                # Highlight logic handled in frontend or simple replace here
                # Simple crude highlight for the snippet
                for term in query_terms:
                    # distinct case-insensitive replace is hard in pure python without regex
                    # We will leave as text for now, template handles basic display
                    pass
                    
                matches.append({
                    'page_num': p_num,
                    'snippet': snippet
                })
        
        if matches:
            return render_template('document_pages.html', 
                                 doc=doc, 
                                 matches=matches, 
                                 query=query, 
                                 total_matches=len(matches))
                                 
    # --- Case 3: Default View (Full Doc or Page 1) ---
    # User requested "instead of displaying entire document", but if no search query,
    # we probably want to show Page 1? Or just the whole thing as before?
    # Let's show Page 1 by default if we have pages, to be consistent with "Page View" paradigm.
    if page_map:
         return redirect(url_for('view_document', doc_id=doc_id, page=1))
         
    # Fallback to full content
    return render_template('document.html', doc=doc, content=content)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
