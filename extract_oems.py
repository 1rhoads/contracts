import os
import re
import csv
import glob
import sys

def extract_oems(data_dir):
    """
    Extracts unique OEMs from markdown files in the specified directory.
    """
    oems = set()
    markdown_files = glob.glob(os.path.join(data_dir, "*.md"))

    print(f"Found {len(markdown_files)} markdown files.", flush=True)

    patterns = [
        r"(?i)Solution Proposed:\s*(.*)",
        r"(?i)Manufacturer:\s*(.*)",
        r"(?i)Product:\s*(.*)",
        r"(?i)OEM:\s*(.*)"
    ]

    for i, file_path in enumerate(markdown_files):
        try:
            filename = os.path.basename(file_path)
            # print(f"Processing {filename}...", flush=True)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Process line by line to avoid memory issues with large files
                # and to match patterns per line
                for line in f:
                    # Quick check if line contains keywords before regex
                    if "Solution Proposed" in line or "Manufacturer" in line or "Product" in line or "OEM" in line:
                         for pattern in patterns:
                            match = re.search(pattern, line)
                            if match:
                                raw_val = match.group(1)
                                clean_val = clean_oem_name(raw_val)
                                if clean_val:
                                    oems.add(clean_val)
                                    # print(f"  Found: {clean_val}", flush=True)

        except Exception as e:
            print(f"Error reading {file_path}: {e}", flush=True)

        # Progress indicator
        if (i + 1) % 5 == 0:
            print(f"Processed {i + 1}/{len(markdown_files)} files.", flush=True)

    return sorted(list(oems))

def clean_oem_name(raw_name):
    """
    Cleans and normalizes OEM names.
    """
    name = raw_name.strip()
    
    # Remove leading/trailing underscores/dashes/stars
    name = re.sub(r"^[\W_]+|[\W_]+$", "", name)
    
    # Remove "Inc.", "LLC" etc.
    # strict removal might be dangerous, let's just strip trailing punctuation
    
    if len(name) > 80:
        return None
        
    if not name:
        return None

    return name

def main():
    data_dir = "data/markdown"
    output_file = "unique_oems.csv"
    
    if not os.path.exists(data_dir):
        print(f"Directory not found: {data_dir}")
        return

    oems = extract_oems(data_dir)
    
    print(f"Extracted {len(oems)} unique potential OEMs.", flush=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["OEM / Solution"])
        for oem in oems:
            writer.writerow([oem])
            
    print(f"Saved to {output_file}", flush=True)

if __name__ == "__main__":
    main()
