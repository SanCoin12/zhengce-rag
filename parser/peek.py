# 1、侦察
import json

data = json.load(open("data/parsed/one.json", encoding="utf-8"))
pages = data if isinstance(data, list) else data.get("pages", [])

for p in pages:
    lines = [x.strip() for x in p["text"].splitlines() if x.strip()]
    print(f'--- 第{p["page"]}页 ---')
    print("\n".join(lines[:3]))
    print("  ......")
    print("\n".join(lines[-2:]))