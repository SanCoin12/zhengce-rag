import json
from pathlib import Path
from docx import Document
import re
WORD_NOISE = [
    (re.compile(r'^ZJSP05-\d{4}-\d+$'), '政策库编号'),
    (re.compile(r'^[\u4e00-\u9fa5]{1,12}〔\d{4}〕\s*\d+\s*号$'), '发文字号'),
    (re.compile(r'^浙江省科学技术厅(文件)?$'), '机关名'),
    (re.compile(r'^\d{4}年\d{1,2}月\d{1,2}日$'), '成文日期'),
]

def denoise_docx(paras):
    kept, deleted, issued = [], [], ""
    for r in paras:
        s = r["text"].strip()
        kind = next((k for p, k in WORD_NOISE if p.fullmatch(s)), None)
        if kind == '成文日期' and not issued: issued = s
        if kind: deleted.append((kind, s))
        else: kept.append(r)
    return kept, deleted, issued

def parse_docx(path):
    doc = Document(str(path))
    records = []
    for i, p in enumerate(doc.paragraphs, 1):
        t = p.text.strip()
        if t:
            records.append({"file": path.name, "page": i, "text": t})
    return records


def main():
    raw = Path("data/raw")
    out_dir = Path("data/parsed")
    out_dir.mkdir(exist_ok=True)
    ok = 0
    files = sorted(raw.glob("*.docx")) # doc需转为docx
    for f in files:
        try:
            records = parse_docx(f)
            dst = out_dir / (f.stem + ".json")
            dst.write_text(json.dumps({"file": f.name, "doc_no": "", "pages": records}, ensure_ascii=False, indent=2), encoding="utf-8")
            print("OK", f.name, "->", dst.name, len(records), "paras")
            ok += 1
        except Exception as e:
            print("FAIL", f.name, ":", e)
    if files:
        print("docx success", ok, "/", len(files))

if __name__ == "__main__":
    main()
