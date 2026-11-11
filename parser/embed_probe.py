import json, os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ZHIPUAI_API_KEY"], # 不跟 DeepSeek 那个全局变量串台
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
print(f"总块数: {len(chunks)}")

texts = [c["text"] for c in chunks[:3]] # 拿前 3 块试水（1 块前言 + 2 块条款）

resp = client.embeddings.create(model="embedding-3", input=texts)

for i, item in enumerate(resp.data):
    v = item.embedding
    print(f"第{i+1}块 维度={len(v)} 前5个数={v[:5]}")
    print(f" 出自: {chunks[i]['doc_no']} {chunks[i]['clause'] or '前言'}")