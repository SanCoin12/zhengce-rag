# 哪些能拿「第X条」当刀口切，哪些不能
import glob, json, re

PAT = re.compile(r"第[一二三四五六七八九十百千\d]{1,4}条")
for f in sorted(glob.glob("data/parsed/*.json")):
    doc = json.load(open(f, encoding="utf-8"))
    text = "".join(p["text"] for p in doc["pages"])
    hits = PAT.findall(text)
    print(f.split("/")[-1], "条数=", len(hits), "样例=", hits[:5])