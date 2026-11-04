""" PyMuPDF 单文件解析 v0 —— PDF -> [{file, page, text}] JSON"""
import json
import sys
from pathlib import Path

import fitz  # PyMuPDF


def parse_pdf(pdf_path: str) -> list[dict]:
    pdf = Path(pdf_path)
    if not pdf.exists():
        sys.exit(f"文件不存在: {pdf}")
    out = []
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            out.append({"file": pdf.name, "page": i, "text": text})
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法: python parser/parse_pdf.py <pdf路径> [输出.json]")
    pdf_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "data/parsed/one.json"
    chunks = parse_pdf(pdf_path)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OK: 共 {len(chunks)} 页 -> {out_path}")
    for c in chunks[:3]:
        preview = c["text"][:60].replace("\n", " ")
        print(f"  第{c['page']}页: {preview}")