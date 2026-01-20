import re
import os

path = "data/markdown/AccessIT_Group_Inc.md"
with open(path, "r") as f:
    content = f.read()

def representation(s):
    return repr(s)

print(f"Content length: {len(content)}")

# Test Regex
regex = r'(^## Page \d+\n)'
page_splits = re.split(regex, content, flags=re.MULTILINE)

print(f"Splits found: {len(page_splits)}")
if len(page_splits) > 10:
   print(f"Sample split[1]: {representation(page_splits[1])}")

page_map = {}
current_page_num = 0

if len(page_splits) > 1:
    for i in range(1, len(page_splits), 2):
        header = page_splits[i].strip() 
        page_content = page_splits[i+1] if i+1 < len(page_splits) else ""
        
        try:
            num_match = re.search(r'(\d+)', header)
            if num_match:
                current_page_num = int(num_match.group(1))
                page_map[current_page_num] = page_content
        except:
            pass

print(f"Pages mapped: {len(page_map)}")
print(f"Page 1 content start: {page_map.get(1, 'None')[:50]}")

# Test Query
query = "Check"
query_terms = ["check"]
matches = []

for p_num, p_text in page_map.items():
    text_lower = p_text.lower()
    if all(term in text_lower for term in query_terms):
        print(f"Match found on page {p_num}")
        matches.append(p_num)

print(f"Total Matches: {len(matches)}")
