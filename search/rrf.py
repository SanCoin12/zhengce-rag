# search/rrf.py — RRF 融合：两路榜单只按名次合分，不看原始分
# 为什么不用分数直接加：向量余弦 0~1，BM25 几十上百，量纲不可比
# 为什么 k=60：原论文平滑值，让第1名和第3名差距别太陡

K = 60

def rrf_fuse(list_a, list_b, k=K, topk=5):
    # list_a / list_b: 按分数降序的 (score, chunk) 列表
    score, chunk = {}, {}
    for lst in (list_a, list_b):
        for rank, (s, c) in enumerate(lst, 1):      # rank 从 1 数
            key = c["doc_no"] + "|" + (c["clause"] or "前言")  # 块的身份证
            score[key] = score.get(key, 0) + 1.0 / (k + rank)  # 核心一行
            chunk[key] = c
    top = sorted(score.items(), key=lambda kv: kv[1], reverse=True)[:topk]
    return [(v, chunk[key]) for key, v in top]

if __name__ == "__main__":
    # 自测：两条假榜单各 5 条，Z1 两路都是第 1，Z3 在 a 路第 3、b 路第 5
    fake = lambda no: {"doc_no": no, "clause": "第四条", "text": no + "的正文"}
    a = [(0.9, fake("Z1")), (0.8, fake("Z2")), (0.7, fake("Z3")),
         (0.6, fake("Z4")), (0.5, fake("Z5"))]
    b = [(31.2, fake("Z1")), (28.4, fake("Z9")), (25.0, fake("Z8")),
         (20.1, fake("Z7")), (15.5, fake("Z3"))]
    for s, c in rrf_fuse(a, b):
        print(f"[{s:.4f}] {c['doc_no']} {c['clause']}")