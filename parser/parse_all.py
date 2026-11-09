from pathlib import Path
import json
from parse_pdf import parse_pdf
from clean import clean_text
from parse_docx import parse_docx
import re
DOCS = re.compile(r"[A-Z]{2,6}[A-Z0-9]*-\d{4}-\d{3,}|[\u4e00-\u9fa5]{1,12}〔\d{4}〕\s*\d+\s*号")

raw_dir, out_dir = Path("data/raw"), Path("data/parsed")
out_dir.mkdir(parents=True, exist_ok=True)
files = sorted(p for p in raw_dir.iterdir() if p.suffix.lower() in (".pdf", ".docx"))
print(f"找到 {len(files)} 份文件")


ok, failed = [], []
for pdf in files:
    try:
        if pdf.suffix.lower() == ".docx":
            paras = parse_docx(pdf)
            doc_no = ""
            for r in paras:
                if DOCS.fullmatch(r["text"].strip()):
                    doc_no = r["text"].strip()
                    break
            out = out_dir / (pdf.stem + ".json")
            out.write_text(json.dumps({"file": pdf.name, "doc_no": doc_no, "pages": paras}, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"OK {pdf.name}: docx {len(paras)}段 doc_no={doc_no or '—'}")
            ok.append(pdf.name)
            continue
        doc_no = None
        pages = parse_pdf(pdf)
        cleaned = []
        for p in pages:
            result = clean_text(p["text"])
            # 看 return：只返回 str 就直接用；返回 (新文本, 删行列表) 就取 [0]
            new_text = result if isinstance(result, str) else result[0]

            hits = [l.strip() for l in new_text.splitlines() if DOCS.fullmatch(l.strip())]
            doc_no = doc_no or (hits[0] if hits else None)
            new_text = "\n".join(l for l in new_text.splitlines() if not DOCS.fullmatch(l.strip()))

            cleaned.append({**p, "text": new_text})
        
        n_raw = sum(len(p["text"]) for p in pages)
        n_clean = sum(len(p["text"]) for p in cleaned)
        if n_clean < 50:
            failed.append((pdf.name, "empty_text 疑似扫描件")); continue
        rate = 1 - n_clean / n_raw
        out = out_dir / (pdf.stem + ".json") # 用 stem，避免 xxx.pdf.json 双后缀

        out.write_text(json.dumps({"file": pdf.name, "doc_no": doc_no or "", "pages": cleaned}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"OK {pdf.name}: doc_no={doc_no} {len(cleaned)}页 削减率{rate:.1%}" + (" ⚠️超30%需人查" if rate > .30 else ""))
        
        ok.append(pdf.name)
    except Exception as e:
        failed.append((pdf.name, repr(e)))

print(f"成功率 {len(ok)}/{len(files)}")
out_dir.joinpath("failed_list.txt").write_text("\n".join(f"{n} {e}" for n, e in failed), encoding="utf-8")