import chromadb
col = chromadb.Client().get_or_create_collection("hello")
col.add(ids=[str(i) for i in range(10)],
documents=[f"政策测试条目{i}" for i in range(10)],
embeddings=[[float(i)] * 8 for i in range(10)])
r = col.query(query_embeddings=[[1.0] * 8], n_results=3)
print("查回：", r["documents"])