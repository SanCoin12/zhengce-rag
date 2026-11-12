import json, os
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.environ["ZHIPUAI_API_KEY"],
                base_url="https://open.bigmodel.cn/api/paas/v4/")

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
store = np.load("data/vec_store_v0.npz")["vectors"]
print(f"弹药库就位: {store.shape[0]} 条 / {store.shape[1]} 维")

def retrieve(question, k=5):
    qv = np.array(client.embeddings.create(model="embedding-3", input=[question])
                  .data[0].embedding, dtype=np.float32)
    scores = (store @ qv) / (np.linalg.norm(store, axis=1) * np.linalg.norm(qv))
    top = np.argsort(scores)[::-1][:k]
    return [(float(scores[i]), chunks[i]) for i in top]

def build_prompt(question, hits):
    ctx = "\n\n".join(f"【{c['doc_no']} {c['clause'] or '前言'}】{c['text']}" for _, c in hits)
    return [
        {"role": "system", "content": "你是政务政策问答助手。只依据下面的检索条款回答；没有依据就回答'所给资料中未找到依据'，禁止编造。"},
        {"role": "user", "content": f"检索到的条款：\n{ctx}\n\n问题：{question}"}]

def ask(question, k=5):
    hits = retrieve(question, k)
    resp = client.chat.completions.create(model="glm-4-flash",
        messages=build_prompt(question, hits), temperature=0.1, max_tokens=500)
    return resp.choices[0].message.content, hits

if __name__ == "__main__":
    while True:
        q = input("问（q 退出）: ")
        if q.strip().lower() in ("q", "quit", "exit", ""):
            break
        ans, hits = ask(q)
        for rank, (s, c) in enumerate(hits, 1):
            print(f"{rank}. [{s:.3f}] {c['doc_no']} {c['clause'] or '前言'}")
        print(f"\n答：{ans}\n")