import json, os
import numpy as np
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ZHIPUAI_API_KEY"],
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

def embed_texts(texts):
    """撞 400 自动对半劈重试；单条还超就截前 2000 字"""
    if len(texts) == 1:
        try:
            return [e.embedding for e in client.embeddings.create(model="embedding-3", input=texts).data]
        except Exception:
            return [e.embedding for e in client.embeddings.create(model="embedding-3", input=[texts[0][:2000]]).data]
    try:
        return [e.embedding for e in client.embeddings.create(model="embedding-3", input=texts).data]
    except Exception:
        mid = len(texts) // 2
        return embed_texts(texts[:mid]) + embed_texts(texts[mid:])

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
print(f"总块数: {len(chunks)}")

BATCH = 16
all_vecs = []
for start in range(0, len(chunks), BATCH):
    all_vecs.extend(embed_texts([c["text"] for c in chunks[start:start + BATCH]]))
    print(f"[{min(start + BATCH, len(chunks))}/{len(chunks)}] 已向量化")

vecs = np.array(all_vecs, dtype=np.float32)
np.savez_compressed("data/vec_store_v0.npz", vectors=vecs)
print(f"完成 ✓ 形状 {vecs.shape}，存到 data/vec_store_v0.npz")