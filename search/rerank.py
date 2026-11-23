#  精排：智谱 rerank API，RRF top10 进，top5 出
# 位置：双路召回 → RRF 粗排 → 【这里】→ LLM 生成
import os, requests

URL = "https://open.bigmodel.cn/api/paas/v4/rerank"

def rerank(query, candidates, top_n=5):
    # candidates: [(score, chunk)] 按 RRF 分降序，chunk 含 doc_no/clause/text
    r = requests.post(
        URL,
        headers={"Authorization": f"Bearer {os.environ['ZHIPUAI_API_KEY']}"},
        json={
            "model": "rerank",
            "query": query,
            "top_n": top_n,
            "documents": [c["text"] for _, c in candidates],
        },
    )
    r.raise_for_status()  # 报错不吞
    # results 按分数降序，index 对回传入顺序，找回原 chunk
    return [
        (it["relevance_score"], candidates[it["index"]][1])
        for it in r.json()["results"]
    ]

if __name__ == "__main__":
    # 验收实验：Q1/Q2 两问，RRF top10 → rerank top5，前后对比
    import sys
    sys.path.insert(0, "parser")
    from rrf import rrf_fuse
    from qa_loop import retrieve, bm25, bm25_search, chunks

    key = lambda c: c["doc_no"] + " " + (c["clause"] or "前言")
    for q in ["学时要求是多少", "专家库入库条件"]:
        bm_raw = bm25_search(q, chunks, bm25, topk=10)
        bm = [(s, c) for c, s in bm_raw]               # 对齐 (score, chunk)
        fused = rrf_fuse(retrieve(q, 10), bm, topk=10) # 粗排候选池 top10
        top5 = rerank(q, fused, top_n=5)               # 精排取 5

        print(f"\n=== {q} ===")
        print("--- RRF 粗排 top5 ---")
        for i, (s, c) in enumerate(fused[:5], 1):
            print(f"{i}. [{s:.4f}] {key(c)}")
        print("--- rerank 精排 top5 ---")
        old = {key(c) for _, c in fused[:5]}
        for i, (s, c) in enumerate(top5, 1):
            tag = "" if key(c) in old else "  ←新进"
            print(f"{i}. [{s:.7f}]{tag} {key(c)}")