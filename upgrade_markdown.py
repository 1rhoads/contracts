import os
import re

MD_DIR = "data/markdown"

def normalize_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check if file has Bento-style separators (---) and lacks proper headers
    if "## Page" not in content and "---" in content:
        print(f"Normalizing {filepath}...")
        
        # Split by separator
        # Bento uses "---" typically on its own line
        # Regex to capture it even if whitespace surrounds
        chunks = re.split(r'^\s*---\s*$', content, flags=re.MULTILINE)
        
        new_content = []
        # First chunk is Page 1
        page_num = 1
        
        for chunk in chunks:
            # Skip empty chunks if any (start/end)
            if not chunk.strip():
                continue
                
            new_content.append(f"## Page {page_num}\n")
            new_content.append(chunk.strip())
            new_content.append("\n\n")
            page_num += 1
            
        final_text = "\n".join(new_content)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_text)
            
    else:
        print(f"Skipping {filepath} (already normalized or incompatible format)")

def main():
    files = [f for f in os.listdir(MD_DIR) if f.endswith(".md")]
    for filename in files:
        normalize_file(os.path.join(MD_DIR, filename))
        
if __name__ == "__main__":
    main()
