import sqlite3
import os
import glob
import re
from normalize_oems import normalize_name

# Configuration
DB_NAME = "instance/contracts.db"
MARKDOWN_DIR = "data/markdown"

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def extract_products():
    print("Starting product extraction...")
    conn = get_db_connection()
    c = conn.cursor()
    
    # Clear existing products to avoid duplicates during re-runs
    c.execute("DELETE FROM product_lines")
    conn.commit()
    
    # Get map of filename -> document_id
    doc_map = {}
    rows = c.execute("SELECT id, filename, vendor FROM documents").fetchall()
    for r in rows:
        doc_map[r[1]] = {'id': r[0], 'vendor': r[2]}
        
    files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    total_products = 0
    
    for filepath in files:
        filename = os.path.basename(filepath)
        if filename not in doc_map:
            print(f"Skipping {filename} (not in DB)")
            continue
            
        doc_id = doc_map[filename]['id']
        vendor = doc_map[filename]['vendor']
        
        # Heuristic: Vendor is usually correct in DB, but sometimes we might want to extract it from "Respondent: ..." 
        # inside the file if the DB vendor is generic. For now relying on DB vendor is fine.

        current_oem = None
        products_found = 0
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Regex patterns
        oem_patterns = [
            r"(?i)Solution Proposed:\s*(.*)",
            r"(?i)Manufacturer:\s*(.*)",
            r"(?i)Product:\s*(.*)",
            r"(?i)OEM:\s*(.*)"
        ]
        
        # State machine for table parsing
        in_table = False
        table_headers = []
        header_map = {} # {'sku': index, 'price': index, ...}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 1. Detect OEM context
            for pattern in oem_patterns:
                match = re.search(pattern, line)
                if match:
                    raw_oem = match.group(1)
                    norm_oem = normalize_name(raw_oem)
                    if norm_oem:
                        current_oem = norm_oem
                        # print(f"  [Context] OEM set to: {current_oem}")
            
            # 2. Detect Table Start (Header row)
            if line.startswith('|') and '---' not in line:
                # Potential header row
                # Check duplicate separator row next
                if i + 1 < len(lines) and '---' in lines[i+1]:
                    # likely a header
                    headers = [h.strip() for h in line.strip('|').split('|')]
                    
                    # Map headers to our fields
                    header_map = {}
                    for idx, h in enumerate(headers):
                        h_lower = h.lower()
                        if 'sku' in h_lower or 'part number' in h_lower or 'tier' in h_lower or 'product code' in h_lower or 'name' in h_lower:
                             # Prioritize actual SKU columns over just "Name" if both exist?
                             # For now, simplistic mapping.
                             if 'sku' not in header_map: # First match
                                 header_map['sku'] = idx
                        
                        if 'description' in h_lower:
                            header_map['description'] = idx
                            
                        if 'price' in h_lower or 'cost' in h_lower:
                             header_map['price'] = idx
                             
                        if 'unit' in h_lower:
                             header_map['unit'] = idx
                    
                    if 'price' in header_map and ('sku' in header_map or 'description' in header_map):
                        in_table = True
                        table_headers = headers
                        # print(f"  [Table] Found table with headers: {headers}")
                        continue
            
            # 3. Detect Table Separator
            if line.startswith('|') and '---' in line:
                continue
                
            # 4. Process Table Row
            if in_table and line.startswith('|'):
                cols = [c.strip() for c in line.strip('|').split('|')]
                
                # Check if this row looks like a valid data row (matched len typically)
                # Markdown tables can be messy.
                if len(cols) != len(table_headers):
                    # Try to align? Or just skip?
                    # Be lenient if close
                    pass
                
                # Extract data
                sku = cols[header_map['sku']] if 'sku' in header_map and len(cols) > header_map['sku'] else None
                desc = cols[header_map['description']] if 'description' in header_map and len(cols) > header_map['description'] else None
                price = cols[header_map['price']] if 'price' in header_map and len(cols) > header_map['price'] else None
                unit = cols[header_map['unit']] if 'unit' in header_map and len(cols) > header_map['unit'] else None
                
                # Fallback: if no SKU col, use Description as SKU/Name
                if not sku and desc:
                    sku = desc
                    
                # Cleanup Price
                if price:
                    # If price is empty or just "$", skip
                    if not re.search(r'\d', price):
                        continue
                        
                if sku and price and current_oem:
                    # Insert
                    # Remove markdown formatting from content
                    sku = re.sub(r"~~.*~~", "", sku).replace("*", "").strip()
                    if desc: desc = re.sub(r"~~.*~~", "", desc).replace("*", "").strip()
                    price = re.sub(r"~~.*~~", "", price).replace("*", "").strip()
                    
                    if not sku: continue # Skip if empty after cleaning

                    c.execute("""
                        INSERT INTO product_lines (document_id, vendor, oem, sku, description, price, unit, raw_line)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (doc_id, vendor, current_oem, sku, desc, price, unit, line))
                    products_found += 1
                    total_products += 1
            
            # 5. End Table
            if in_table and not line.startswith('|'):
                in_table = False
                
        # print(f"  Extracted {products_found} products from {filename}")

    conn.commit()
    conn.close()
    print(f"Extraction complete. Total products: {total_products}")

if __name__ == "__main__":
    extract_products()
