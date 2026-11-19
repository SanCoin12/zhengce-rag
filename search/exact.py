import re
import json

# 中文发文字号：机关代字〔年份〕序号号，如 浙科发金〔2026〕29号
P_CN = re.compile(r'[\u4e00-\u9fa5]{1,12}〔\d{4}〕\s?\d{1,4}\s?号?')
# 政策库统一编号：如 ZJSP05-2023-0009
P_ZJ = re.compile(r'[A-Z]+\d{0,3}-\d{4}-\d{4}')

def extract_doc_no(query):
    m = P_ZJ.search(query) or P_CN.search(query)
    return m.group(0) if m else None

def load_chunks(path="data/chunks_v0.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def exact_search(query, chunks):
    no = extract_doc_no(query)
    if not no:
        return None, []
    key = no.replace(" ", "") # 空格归零再比，防「29 号」vs「29号」miss
    hits = [c for c in chunks if c.get("doc_no", "").replace(" ", "") == key]
    return no, hits

if __name__ == "__main__":
    chunks = load_chunks()
    print("总块数:", len(chunks))
    print("样例块:", json.dumps(chunks[0], ensure_ascii=False)[:200])
    for q in ["浙科发金〔2026〕29号", "ZJSP05-2023-0009 的入库条件", "学时要求"]:
        no, hits = exact_search(q, chunks)
        print(q, "| 抽到:", no, "| 捞到块数:", len(hits))