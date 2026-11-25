import re, json
from qa_loop import ask

chunks = json.load(open("data/chunks_v0.json", encoding="utf-8"))
norm = lambda s: re.sub(r"\s+", "", s)

for q in ["学时要求是多少", "专家库入库条件"]:
    ans, hits, route = ask(q)
    print("=" * 40)
    print("问:", q, "| 路:", route)
    print(ans)
    print("-- 摘录逐字核对（去空白口径）--")
    ok_n = bad_n = 0
    for line in ans.splitlines():
        s = line.strip()
        if s.startswith("[") and "|" in s:
            parts = [p.strip() for p in s.split("|")]
            clause, quote = parts[1], parts[2].strip("“”\"' ")
            src = next((c for c in chunks if norm(quote) in norm(c["text"])), None)
            if src:
                tag = "PASS" if (src["clause"] or "前言") == clause else "PASS但条款号不符"
                ok_n += 1
            else:
                tag = "FAIL"; bad_n += 1
            print(f"{tag} | {quote[:40]}")
    print(f"合计: {ok_n} 过 / {bad_n} 挂\n")