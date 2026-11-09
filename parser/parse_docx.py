import json
from pathlib import Path
from docx import Document

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
