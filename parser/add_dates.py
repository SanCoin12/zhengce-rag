import json
from pathlib import Path

SRC = Path("data/chunks_v0.json")
DOC_DATES = {
    "浙科发才〔2026〕14 号": "2026年4月9日",
    "浙科发重〔2026〕24 号": "2026年6月18日",
    "浙科发金〔2026〕29 号": "2026年7月6日",
    "浙科发基〔2026〕32 号": "2026年8月25日",
    "浙科发外〔2026〕21 号": "2026年6月9日",
    "浙科发外〔2026〕22 号": "2026年6月9日",
    "ZJSP05-2023-0009": "2023年8月30日",
    "浙科发政〔2026〕39 号": "2026年9月11日",
    "ZJSP05-2026-0010": "2026年7月27日",
    "浙科发重〔2026〕23 号": "2026年6月10日",
    "浙科发重〔2026〕30 号": "2026年7月13日",
    "浙科发基〔2026〕31 号": "2026年7月22日",
    "ZJSP05-2026-0001": "2026年3月27日",
}

chunks = json.loads(SRC.read_text(encoding="utf-8"))
missed = []
for c in chunks:
    d = DOC_DATES.get(c["doc_no"])
    if d is None:
        missed.append(c["doc_no"])
    c["date"] = d or ""

SRC.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

filled = sum(1 for c in chunks if c["date"])
distinct = len(set(c["date"] for c in chunks if c["date"]))
print("补上 date 的块数:", filled, "/", len(chunks))
print("不同日期值种数:", distinct, "(应为13)")
if missed:
    print("⚠️ 没匹配上的 doc_no:", set(missed))
else:
    print("doc_no 全部精确匹配 ✓")