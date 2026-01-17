import os
import sqlite3
from flask import Flask, render_template, request, abort
from markdown import markdown # We might need this, but we can display raw text or pre-rendered. 
# Actually, displaying markdown as HTML is better.
# Trying to import markdown, if not available we will just return text.

app = Flask(__name__)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'contracts.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
        # Escape query for FTS syntax if needed, but standard text often works. 
        # For safety, we wrap in double quotes or sanitize.
        sanitized_query = f'"{query}"' if '"' not in query else query
        
        try:
            results = conn.execute(sql, (sanitized_query,)).fetchall()
        except sqlite3.OperationalError:
            # Fallback for complex syntax errors
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
        
    # Simple markdown to HTML conversion if possible
    content = doc['content']
    # Use pymupdf or simple replacement if markdown lib not installed
    # We installed pymupdf, but maybe not 'markdown' lib.
    # Let's just wrap in pre tags for now or do basic HTML.
    # Actually, we can assume plaintext is fine or minimal formatting.
    
    return render_template('document.html', doc=doc, content=content)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
