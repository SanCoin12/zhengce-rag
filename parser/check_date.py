import json
chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
for c in chunks:
    if c["doc_no"].replace(" ", "") == "浙科发才〔2026〕14号" and c["clause"] == "第四条":
        print(c["text"])
        print("含18学时:", "18学时" in c["text"].replace(" ", ""))
        print("含60学时:", "60学时" in c["text"].replace(" ", ""))
        print("含其中:", "其中" in c["text"])
# 顺手看学时相关的块到底切成了几块
for c in chunks:
    if c["doc_no"].replace(" ", "") == "浙科发才〔2026〕14号" and ("学时" in c["text"]):
        print("块:", c["clause"] or "前言", "| 字数:", len(c["text"]))