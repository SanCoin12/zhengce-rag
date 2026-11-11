import json, os
import chromadb
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ZHIPUAI_API_KEY"],
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

# ① 连库：嵌入式本地库
db = chromadb.PersistentClient(path="data/chroma")

# ② 拿集合（没有就建）。cosine=按夹角算相似度，文本检索的标准姿势
col = db.get_or_create_collection(
    name="zhengce_v0",
    metadata={"hnsw:space": "cosine"},
)

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
print(f"总块数: {len(chunks)} 库里已有: {col.count()}")

BATCH = 8 # ③ 智谱单次最多 64 条

for start in range(0, len(chunks), BATCH):
    batch = chunks[start:start + BATCH]
    texts = [c["text"] for c in batch]

resp = client.embeddings.create(model="embedding-3", input=texts)
vectors = [item.embedding for item in resp.data]

col.upsert( # ④ upsert：同 id 覆盖，脚本可反复重跑不重复入库
    ids=[f"c{start + j:04d}" for j in range(len(batch))],
    embeddings=vectors,
    documents=texts,
    metadatas=[{ # ⑤ 溯源信息挂在每条向量上
        "file": c["file"], "doc_no": c["doc_no"],
        "chapter": c["chapter"] or "", "clause": c["clause"] or "",
        "type": c["type"],
    } for c in batch],
)
print(f"[{start + len(batch)}/{len(chunks)}] 已入库")

print(f"完成 ✓ 库内总数: {col.count()}")