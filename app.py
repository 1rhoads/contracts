import os
import sqlite3
import re
from flask import Flask, render_template, request, abort, redirect, url_for
from markdown import markdown # We might need this, but we can display raw text or pre-rendered. 
# Actually, displaying markdown as HTML is better.
# Trying to import markdown, if not available we will just return text.

app = Flask(__name__)

def get_db_connection():
    # Use instance folder for persistence
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'contracts.db')
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

def get_sidebar_data():
    conn = get_db_connection()
    # Get all distinct vendors
    vendors = [r['vendor'] for r in conn.execute("SELECT DISTINCT vendor FROM documents WHERE vendor IS NOT NULL ORDER BY vendor").fetchall()]
    
    # Get all categories
    # Since categories are stored as JSON list strings, we need to flatten them
    import json
    cats_rows = conn.execute("SELECT categories FROM documents WHERE categories IS NOT NULL").fetchall()
    unique_cats = set()
    for row in cats_rows:
        try:
            clist = json.loads(row['categories'])
            for c in clist:
                unique_cats.add(c)
        except:
            pass
            
    # Sort categories naturally (Number first)
    # They usually come as "1. Name", so sorting by string works decently or better logic needed
    def natural_keys(text):
        try:
           return int(text.split('.')[0])
        except:
           return 999
           
    sorted_cats = sorted(list(unique_cats), key=natural_keys)
    
    conn.close()
    return vendors, sorted_cats

@app.route('/')
def index():
    query = request.args.get('q', '')
    selected_vendor = request.args.get('vendor')
    selected_category = request.args.get('category')
    
    results = []
    
    conn = get_db_connection()
    
    # Base Query
    # We need to construct dynamic WHERE clauses
    sql_parts = ["""
        SELECT d.id, d.title, d.filename, d.content, d.vendor, d.categories,
               snippet(documents_fts, 1, '<mark>', '</mark>', '...', 64) as snippet
        FROM documents_fts 
        JOIN documents d ON documents_fts.rowid = d.id
    """]
    
    where_clauses = []
    params = []
    
    # 1. Search Query
    if query:
        where_clauses.append("documents_fts MATCH ?")
        params.append(sanitize_query_fns(query))
        
    # 2. Vendor Filter
    if selected_vendor:
        where_clauses.append("d.vendor = ?")
        params.append(selected_vendor)
        
    # 3. Category Filter
    # Categories are JSON list. We check if the JSON string contains the category substring.
    # Simple workaround for SQLite without JSON extension
    if selected_category:
        where_clauses.append("d.categories LIKE ?")
        params.append(f"%{selected_category}%")
        
    if where_clauses:
        sql_parts.append("WHERE " + " AND ".join(where_clauses))
        
    sql_parts.append("ORDER BY rank LIMIT 50" if query else "ORDER BY d.title")
    # If no query, we might want to paginate or limit? Let's show all for browsing
    
    full_sql = " ".join(sql_parts)
    
    try:
        rows = conn.execute(full_sql, params).fetchall()
        
        # If no results with strict query, try relaxed (only if search was involved)
        if not rows and query:
             relaxed_query = query.replace('"', '').replace('-', ' ')
             if relaxed_query != query:
                 # Rebuild params with relaxed query
                 # Params order: [query, vendor?, category?]
                 new_params = [relaxed_query]
                 if selected_vendor: new_params.append(selected_vendor)
                 if selected_category: new_params.append(f"%{selected_category}%")
                 
                 rows = conn.execute(full_sql, new_params).fetchall()
                 
        # Process rows
        count_terms = query.replace('"', '').lower().split() if query else []
        
        for row in rows:
            matches = 0
            if query and row['content']:
                text_lower = row['content'].lower()
                for term in count_terms:
                    matches += text_lower.count(term)
                    
            # Load cats for display
            import json
            try:
                display_cats = json.loads(row['categories'])
            except:
                display_cats = []
            
            results.append({
                'id': row['id'],
                'title': row['title'],
                'filename': row['filename'],
                'vendor': row['vendor'],
                'categories': display_cats,
                'snippet': row['snippet'] if query else row['content'][:200] + "...", 
                'match_count': matches
            })
            
    except sqlite3.OperationalError as e:
        print(f"SQL Error: {e}")
        # Possibly fallback to empty
        
    conn.close()
    
    # Get Sidebar Data
    vendors, categories = get_sidebar_data()
        
    return render_template('index.html', 
                         query=query, 
                         results=results,
                         all_vendors=vendors,
                         all_categories=categories,
                         selected_vendor=selected_vendor,
                         selected_category=selected_category)

@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    import sys
    print(f"Entered view_document: {doc_id}", file=sys.stderr)
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

            
    
    # --- Identify Matching Pages (Pre-calculation) ---
    matching_page_numbers = []
    if query:
        # Parse query logic (loose vs strict) - replicating logic from index()
        normalized_query = query.replace('"', '').lower()
        query_terms = normalized_query.split()
        
        for p_num, p_text in page_map.items():
            text_lower = p_text.lower()
            if all(term in text_lower for term in query_terms):
                matching_page_numbers.append(p_num)
    
    matching_page_numbers.sort()

    # --- Case 1: Viewing a specific page ---
    if page_param:
        try:
            target_page = int(page_param)
            if target_page in page_map:
                # Reconstruct just this page's markdown
                page_md = f"## Page {target_page}\n{page_map[target_page]}"
                if target_page == 1:
                    page_md = title_preamble + page_md
                
                # Calculate Page Navigation
                total_pages = max(page_map.keys()) if page_map else 1
                prev_page = target_page - 1 if target_page > 1 else None
                next_page = target_page + 1 if target_page < total_pages else None
                
                # Calculate Result Navigation
                prev_result = None
                next_result = None
                
                if matching_page_numbers:
                    # Find matches relative to current page
                    lower_matches = [p for p in matching_page_numbers if p < target_page]
                    higher_matches = [p for p in matching_page_numbers if p > target_page]
                    
                    if lower_matches:
                        prev_result = max(lower_matches)
                    if higher_matches:
                        next_result = min(higher_matches)

                return render_template('document.html', 
                                     doc=doc, 
                                     content=page_md, 
                                     current_page=target_page, 
                                     total_pages=total_pages,
                                     query=query,
                                     prev_page=prev_page,
                                     next_page=next_page,
                                     prev_result=prev_result,
                                     next_result=next_result)
        except ValueError:
            pass # Invalid page number, fall through
            
    # --- Case 2: Searching (List of Pages) ---
    if query and matching_page_numbers:
        matches = []
        # Re-using pre-calculated list
        normalized_query = query.replace('"', '').lower()
        query_terms = normalized_query.split()
        
        for p_num in matching_page_numbers:
            p_text = page_map[p_num]
            text_lower = p_text.lower()
            
            # Snippet generation logic (same as before)
            idx = text_lower.find(query_terms[0])
            start = max(0, idx - 50)
            end = min(len(p_text), idx + 150)
            snippet = p_text[start:end]
            
            matches.append({
                'page_num': p_num,
                'snippet': snippet
            })
        
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

@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    from flask import send_from_directory
    pdf_dir = os.path.join(os.path.dirname(__file__), 'data', 'pdfs')
    return send_from_directory(pdf_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
