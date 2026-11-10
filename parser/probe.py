import json, re, glob
PAT = re.compile(r"第[一二三四五六七八九十百千零\d]{1,6}条")
for name in ["浙江省自然科学基金", "国际联合实验室", "行政处罚"]:
    f = [x for x in glob.glob("data/parsed/*.json") if name in x][0]
    doc = json.load(open(f, encoding="utf-8"))
    text = "\n".join(p["text"] for p in doc["pages"])
    hits = list(PAT.finditer(text))
    print("=====", name, "hits=", len(hits))
    for m in hits[:4]: print(repr(text[max(0, m.start()-20):m.end()+8]))