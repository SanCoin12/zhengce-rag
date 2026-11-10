# 
import glob, json, re, os

CLAUSE = re.compile(r"(?m)^\s{0,4}(第[一二三四五六七八九十百千零]{1,6}条)")
CHAPTER = re.compile(r"(?m)^\s{0,4}(第[一二三四五六七八九十百]{1,3}章)\s*(.*)$")

all_chunks = []
for f in sorted(glob.glob("data/parsed/*.json")):
    doc = json.load(open(f, encoding="utf-8"))
    text = "\n".join(p["text"] for p in doc["pages"])
    cms = list(CHAPTER.finditer(text))
    vms = list(CLAUSE.finditer(text))
    title = os.path.splitext(os.path.basename(f))[0]
    print(os.path.basename(f)[:30], "章数=", len(cms), "条数=", len(vms))

    if len(vms) < 3: print(" → 非条款式，v0 跳过，fallback 明天做"); continue
    if vms[0].start() > 0: all_chunks.append({"file": title, "doc_no": doc.get("doc_no", ""), "chapter": "", "clause": "", "type": "preamble", "text": text[:vms[0].start()].strip()})

    for i, m in enumerate(vms):
        end = vms[i+1].start() if i+1 < len(vms) else len(text)
        chs = [c.group(1) + (c.group(2) or "") for c in cms if c.start() < m.start()]
        all_chunks.append({"file": title, "doc_no": doc.get("doc_no", ""), "chapter": chs[-1].strip() if chs else "", "clause": m.group(1), "type": "clause", "text": text[m.start():end].strip()})
        json.dump(all_chunks, open("data/chunks_v0.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("总 chunks =", len(all_chunks), "| 平均长 =", sum(len(c["text"]) for c in all_chunks) // len(all_chunks), "| 最长 =", max(len(c["text"]) for c in all_chunks))