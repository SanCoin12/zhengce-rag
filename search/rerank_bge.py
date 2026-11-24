import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import json, time

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder
        _model = CrossEncoder("BAAI/bge-reranker-base")
    return _model

def rerank(query, candidates):
    """candidates: [(score, chunk)] → 精排后 [(score, chunk)]，分数降序"""
    model = get_model()
    pairs = [(query, c["text"][:512]) for _, c in candidates]
    scores = model.predict(pairs)
    ranked = sorted(zip(scores, [c for _, c in candidates]), key=lambda x: -x[0])
    return [(float(s), c) for s, c in ranked]

if __name__ == "__main__":
    chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
    query = "专业技术人员继续教育学时要求"
    model = get_model()

    pairs = [(query, c["text"][:512]) for c in chunks[:10]]
    t0 = time.time()
    model.predict(pairs)
    print(f"10 对推理耗时: {time.time()-t0:.2f}s")

    def pick(kw_doc, kw_clause):
        for c in chunks:
            if kw_doc in c["doc_no"].replace(" ", "") and kw_clause in str(c["clause"]).replace(" ", ""):
                return c

    cands = [c for c in (pick("浙科发才", "第四条"), pick("浙科才", "第六条"),
                         pick("浙科发金", "第十六条"), pick("0009", "第五条")) if c]
    for c, s in zip(cands, model.predict([(query, c["text"][:512]) for c in cands])):
        print(f"{s:.4f}  {c['doc_no']} {c['clause']}")