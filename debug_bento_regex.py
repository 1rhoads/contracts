import re

filepath = "data/markdown/Optiv_Security_Inc.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)}")
print(f"First 50 chars: {repr(content[:50])}")

# Current Regex in app.py
regex = r'(^## Page \d+\n)'
splits = re.split(regex, content, flags=re.MULTILINE)

print(f"Splits count: {len(splits)}")

page_map = {}
if len(splits) > 1:
    for i in range(1, len(splits), 2):
        header = splits[i].strip()
        body = splits[i+1] if i+1 < len(splits) else ""
        print(f"Found Header: '{header}'")
        print(f"Body start: {repr(body[:30])}")
        
        # Verify simple search
        if "price" in body.lower():
            print(f"MATCH 'price' in {header}")
else:
    print("NO SPLITS FOUND")
