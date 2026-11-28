# parser/run_eval.py —— 一条命令跑种子回归
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qa_loop import ask

SEED = [
    "学时要求是多少",
    "专家库入库条件",
    "不予受理的情形",
    "科学数据官的职责",
    "创新券的支持开销范围",
    "尖兵领雁支持方式",
    "浙科发才〔2026〕14 号 学时要求是多少",
    "专家库入库条件和基金申报不予受理的情形各是什么",
]

for i, q in enumerate(SEED, 1):
    ans, hits, route = ask(q)
    print()
    print("===== Q%d %s =====" % (i, q))
    print("路:", route)
    for rank, (s, c) in enumerate(hits, 1):
        print("%d. [%.3f] %s %s" % (rank, s, c["doc_no"], c["clause"] or "前言"))
    print()
    print(ans)
print()
print("回归完成: 8/8")