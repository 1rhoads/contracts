with open("debug_presidio.html", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
    
targets = ["content/download", ".pdf", "Exhibit"]
for t in targets:
    idx = content.find(t)
    if idx != -1:
        print(f"FOUND {t} at index {idx}")
        start = max(0, idx - 100)
        end = min(len(content), idx + 200)
        print(f"Context: {content[start:end]}")
        print("-" * 20)
    else:
        print(f"NOT FOUND: {t}")
