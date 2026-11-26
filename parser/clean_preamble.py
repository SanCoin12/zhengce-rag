import json, shutil
from pathlib import Path

SRC = Path("data/chunks_v0.json")
AGENCY_TAILS = ("厅", "局", "委员会", "海关", "税务局", "部门", "办公室")

def is_agency(s):  # s 是去掉空格后的整行
    return (2 <= len(s) <= 40 and "《" not in s and "：" not in s
            and s.endswith(AGENCY_TAILS))

def clean_head(text):
    lines = text.split("\n")
    out = []
    i, pos, n = 0, 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.replace(" ", "").replace("\u3000", "")
        # ① 主送行(各开头)或已出 120 字窗口 → 剩余原样保留, 收工
        if line.lstrip().startswith("各") or pos >= 120:
            out.extend(lines[i:])
            break
        # ② 标题串: 从含「印发」的行删到含「的通知」的行(含), 跨行也吃
        if "印发" in line:
            j = i
            while j < n and "的通知" not in lines[j]:
                j += 1
            if j < n:
                for k in range(i, j + 1):
                    pos += len(lines[k]) + 1
                i = j + 1
                continue
            # 找不到「的通知」→ 保守当普通行继续往下判
        if len(s) <= 2:  # 红头竖排单字碎片(杭/州/海/关)
            pos += len(line) + 1
            i += 1
            continue
        # ③ 「文件」独立行 / 机关名+文件 → 整行删
        if s == "文件" or (s.endswith("文件") and is_agency(s[:-2])):
            pos += len(line) + 1
            i += 1
            continue
        # ④ 纯机关名行 → 删
        if is_agency(s):
            pos += len(line) + 1
            i += 1
            continue
        # ⑤ 普通行保留
        out.append(line)
        pos += len(line) + 1
        i += 1
    return "\n".join(out)

# shutil.copy(SRC, "data/chunks_v0.backup_1126.json")  # 先备份再动手
chunks = json.loads(SRC.read_text(encoding="utf-8"))
cnt = 0
for c in chunks:
    if c["type"] == "preamble":
        old = c["text"]
        c["text"] = clean_head(old)
        if c["text"] != old:
            cnt += 1
SRC.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
print("清洗块数:", cnt, "/ 13")
for c in chunks:
    if c["type"] == "preamble":
        print("=" * 40)
        print(c["doc_no"], "| 清洗后长度", len(c["text"]))
        print("头120:", c["text"][:120].replace("\n", " "))