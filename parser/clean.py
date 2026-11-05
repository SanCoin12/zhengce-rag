# 2、清洗
import json
import re

AGENCIES = ("浙江省科学技术厅", "浙江省财政厅")

# 把已知机关名全部替换成 #
def is_agency_line(s):
    t = re.sub(r"\s+", "", s)
    for name in AGENCIES:
        t = t.replace(name, "#")
    return t.strip("#") == ""

DROPS = [
    r"^[-－]\s*\d+\s*[-－]$",
    r"^[A-Z]{2,}\d*-\d{4}-\d+$",
    r"^\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日(印发)?$",
    r"^.{0,20}办公室$",
]

def clean_text(text):
    keep, removed = [], []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if is_agency_line(s) or any(re.match(p, s) for p in DROPS):
            removed.append(s)
        else:
            keep.append(s)
    return "\n".join(keep), removed

data = json.load(open("data/parsed/one.json", encoding="utf-8"))
pages = data if isinstance(data, list) else data.get("pages", [])

out, removed_all = [], []
before = after = 0
for p in pages:
    before += len(p["text"])
    cleaned, removed = clean_text(p["text"])
    removed_all += removed
    after += len(cleaned)
    if cleaned:
        out.append({"file": p["file"], "page": p["page"], "text": cleaned})

doc_no = re.search(r"[A-Z]{2,}\d*-\d{4}-\d+", pages[0]["text"])

print("清洗前 %d / 清洗后 %d / 削减率 %.1f%%" % (before, after, 100*(1-after/before)))
print("共删 %d 行，样例：" % len(removed_all))
for r in removed_all[:10]:
    print("  [删]", r)
print("政策编号：", doc_no.group() if doc_no else "没抓到")

json.dump({"file": out[0]["file"], "doc_no": doc_no.group() if doc_no else None, "pages": out},
          open("data/parsed/one_clean.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)