import json, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "search"))
import numpy as np
from openai import OpenAI
from exact import exact_search
from bm25 import build_index, search as bm25_search
from rrf import rrf_fuse
import os
RERANK = os.environ.get("RERANK", "off")   # off / api / bge

client = OpenAI(api_key=os.environ["ZHIPUAI_API_KEY"],
                base_url="https://open.bigmodel.cn/api/paas/v4/")

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
store = np.load("data/vec_store_v0.npz")["vectors"]
print(f"弹药库就位: {store.shape[0]} 条 / {store.shape[1]} 维")
bm25 = build_index(chunks)
print(f"BM25 索引就位: {len(chunks)} 块")

def retrieve(question, k=5):
    qv = np.array(client.embeddings.create(model="embedding-3", input=[question])
                  .data[0].embedding, dtype=np.float32)
    scores = (store @ qv) / (np.linalg.norm(store, axis=1) * np.linalg.norm(qv))
    top = np.argsort(scores)[::-1][:k]
    return [(float(scores[i]), chunks[i]) for i in top]

def build_prompt(question, hits):
    ctx = "\n\n".join(f"[{i}]【{c['doc_no']} {c['clause'] or '前言'}】{c['text']}" for i, (_, c) in enumerate(hits, 1))
    system = (
        "你是政务政策问答助手。只依据下面的检索条款回答；"
        "没有依据就回答'所给资料中未找到依据'，禁止编造。"
    )
    fmt = (
        "输出格式（必须严格遵守）：\n"
        "1. 先给答案，每条要点结尾标依据编号，如 [1] 或 [2][5]；无依据不标。\n"
        "2. 答完另起一行输出【引用】，只列答案标注过的编号，每行格式：[编号] “摘录”\n"
        "3. 摘录必须从对应编号条款原文逐字复制，禁止改写缩写，每条不超60字。\n"
        "示例：\n"
        "答：申请单位应当是在浙江省内注册的法人机构 [1]。\n"
        "【引用】\n"
        "[1] “申请单位应当是在浙江省内注册”"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"检索到的条款：\n{ctx}\n\n问题：{question}\n\n{fmt}"}]

def ask(question, k=5):
    no, exact_hits = exact_search(question, chunks)
    if no and exact_hits:
        hits = [(1.0, c) for c in exact_hits]
        route = f"精确({len(exact_hits)}块)"
    else:
        vec_hits = retrieve(question, 10)
        bm_raw = bm25_search(question, chunks, bm25, topk=10)
        bm_hits = [(s, c) for c, s in bm_raw]
        fused10 = rrf_fuse(vec_hits, bm_hits, topk=10)      # 候选池扩到10
        route = f"RRF(向{len(vec_hits)}+BM{len(bm_hits)})|排:{RERANK}"
        if RERANK == "bge":
            from rerank_bge import rerank as do_rerank      # 懒加载：进分支才import
            hits = do_rerank(question, fused10)[:5]
        elif RERANK == "api":
            from rerank import rerank as do_rerank
            hits = do_rerank(question, fused10)[:5]
        else:
            hits = fused10[:5]

    resp = client.chat.completions.create(model="glm-4-flash", messages=build_prompt(question, hits), temperature=0.1, max_tokens=900)
    ans = resp.choices[0].message.content
    return assemble_citations(ans, hits), hits, route

def assemble_citations(ans, hits):
    out, in_cite = [], False
    for line in ans.splitlines():
        if "【引用】" in line:
            in_cite = True
            out.append(line)
            continue
        if in_cite:
            m = re.match(r"\s*\[(\d+)\]\s*[“\"]?(.*?)[”\"]?\s*$", line)
            if m:
                n = int(m.group(1))
                quote = re.sub(r"[；。，、！？!?.,“”\"' ]+$", "", m.group(2).strip())
                if 1 <= n <= len(hits):
                    _, c = hits[n - 1]
                    out.append(f"[{n}] {c['doc_no']} | {c['clause'] or '前言'} | “{quote}”")
            # 不匹配的行直接丢弃
        else:
            out.append(line)
    return "\n".join(out)

if __name__ == "__main__":
    while True:
        q = input("问（q 退出）: ")
        if q.strip().lower() in ("q", "quit", "exit", ""):
            break
        ans, hits, route = ask(q)
        print("路:", route)
        for rank, (s, c) in enumerate(hits, 1):
            print(f"{rank}. [{s:.3f}] {c['doc_no']} {c['clause'] or '前言'}")
        print(f"\n{ans}\n")