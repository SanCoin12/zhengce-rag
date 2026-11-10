import json, random
chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
random.seed(10)
for c in random.sample(chunks, 10):
    print("=" * 40)
    print(c["file"][:20], "|", c["chapter"], "|", c["clause"] or "(前言)", "| 长度", len(c["text"]))
    print("头:", c["text"][:50].replace("\n", " "))
    print("尾:", c["text"][-50:].replace("\n", " "))