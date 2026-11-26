import json

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
targets = [c for c in chunks
           if c["type"] == "preamble"
           or (c["type"] == "section" and ("前言" in (c["chapter"] or "") or "前言" in (c["clause"] or "")))]
for c in targets:
    print("=" * 40)
    print(c["file"][:20], "|", c["chapter"], "|", c["clause"] or "(前言)", "| 长度", len(c["text"]))
    print("头120:", c["text"][:120].replace("\n", " "))
    print("尾50:", c["text"][-50:].replace("\n", " "))
print("共", len(targets), "块")