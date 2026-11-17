# search/bm25.py — BM25 检索 v0：jieba 分词 + rank_bm25
import json
from pathlib import Path

import jieba
from rank_bm25 import BM25Okapi # BM25 按词匹配，不按整串匹配

CHUNKS = Path("data/chunks_v0.json")


def tokenize(text):
    # v0 简易去噪：只留长度>=2 的词，拦掉"的/了/和"这类单字虚词
    return [t for t in jieba.lcut(text) if len(t.strip()) >= 2]


def load_chunks():
    return json.loads(CHUNKS.read_text(encoding="utf-8"))


def build_index(chunks):
    return BM25Okapi([tokenize(c["text"]) for c in chunks])


def search(query, chunks, bm25, topk=5):
    scores = bm25.get_scores(tokenize(query))
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:topk]
    return [(chunks[i], scores[i]) for i in top if scores[i] > 0]


def show(query, chunks, bm25):
    print(f"\n=== query: {query} ===")
    hits = search(query, chunks, bm25)
    if not hits:
        print("（无命中）")
        return
    for c, s in hits:
        tag = c["type"] + "/" + c["clause"] if c.get("clause") else c["type"]
        print(f"[{s:7.2f}] {tag} | {c['file'][:20]} | {c['text'][:44]} | {c['text'].count(query)}")


if __name__ == "__main__":
    chunks = load_chunks()
    bm25 = build_index(chunks)
    print(f"索引块数: {len(chunks)}")
    for q in ["学时", "入库条件", "不予受理"]:
        show(q, chunks, bm25)