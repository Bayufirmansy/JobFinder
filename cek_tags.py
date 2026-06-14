import json
from collections import Counter

with open("data_bersih.json") as f:
    data = json.load(f)

semua_tags = []
for loker in data:
    tags = loker.get("tags", "")
    for t in tags.split(","):
        t = t.strip()
        if t:
            semua_tags.append(t)

print("TOP 20 TAG:")
for tag, jumlah in Counter(semua_tags).most_common(20):
    print(f"  {tag}: {jumlah}")