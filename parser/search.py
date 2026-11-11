import json, os
import numpy as np
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ZHIPUAI_API_KEY"],
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
store = np.load("data/vec_store_v0.npz")["vectors"]    # 237×2048 矩阵
print(f"弹药库就位: {store.shape[0]} 条 / {store.shape[1]} 维\n")

while True:
    q = input("问点啥（q 退出）: ")
    if q.strip().lower() in ("q", "quit", "exit", ""):
        break
    qv = np.array(client.embeddings.create(model="embedding-3", input=[q]).data[0].embedding, dtype=np.float32)

    # 余弦相似度：夹角越小=语义越近。分子点积，分母模长归一
    scores = (store @ qv) / (np.linalg.norm(store, axis=1) * np.linalg.norm(qv))
    top5 = np.argsort(scores)[::-1][:5]

    print()
    for rank, i in enumerate(top5, 1):
        c = chunks[i]
        print(f"{rank}. [{scores[i]:.3f}] {c['doc_no']} {c['clause'] or '前言'}")
        print("   " + c["text"][:100].replace("\n", " "))
    print()