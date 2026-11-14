import glob, json, re, os, sys

RE_SEC = re.compile(r'^[一二三四五六七八九十]+、')
RE_MID = re.compile(r'^（[一二三四五六七八九十]+）')
RE_NUM = re.compile(r'^\d+[、\.]')
WRITE = '--write' in sys.argv

old = json.load(open('data/chunks_v0.json', encoding='utf-8'))
done = set(c['file'] for c in old) # 已处理好的
new_chunks = []
for f in sorted(glob.glob('data/parsed/*.json')):
    doc = json.load(open(f, encoding='utf-8'))
    title = os.path.basename(f)[:-5]
    if title in done:
        continue
    full = '\n'.join((p.get('text') or '') for p in doc.get('pages', [])) # 跨页拼接
    lines = [l.strip() for l in full.split('\n')] # 段落切割
    sec_idx = [i for i, l in enumerate(lines) if RE_SEC.match(l)]
    if not sec_idx:
        print('!! 无大项结构,跳过:', title[:30]); continue
    if sec_idx[0] > 0 and len(''.join(lines[:sec_idx[0]])) > 50: # 第一个刀口之前有没有东西
        new_chunks.append({'file': title, 'doc_no': doc.get('doc_no', ''), 'chapter': '', 'clause': '', 'type': 'preamble', 'text': '\n'.join(lines[:sec_idx[0]])})
    bounds = sec_idx + [len(lines)]
    for a, b in zip(bounds, bounds[1:]):
        sec_lines = lines[a:b]
        chapter = sec_lines[0]
        mid_idx = [i for i, l in enumerate(sec_lines[1:], 1) if RE_MID.match(l)]
        cut = RE_MID if len(mid_idx) >= 2 else RE_NUM
        sub_idx = [i for i, l in enumerate(sec_lines[1:], 1) if cut.match(l)]
        if not sub_idx:
            new_chunks.append({'file': title, 'doc_no': doc.get('doc_no', ''), 'chapter': chapter, 'clause': '', 'type': 'section', 'text': '\n'.join(sec_lines)}); continue
        if sub_idx and sub_idx[0] == 1 and len(sec_lines[0]) < 40:
            sub_idx = sub_idx[1:]
        sb = [0] + sub_idx + [len(sec_lines)]
        for x, y in zip(sb, sb[1:]):
            blk = sec_lines[x:y]
            clause = blk[0][:12]
            if sum(len(l) for l in blk) > 1500 and cut is RE_MID:
                nb = [i for i, l in enumerate(blk) if RE_NUM.match(l)]
                nb2 = [0] + nb + [len(blk)] if nb else [0, len(blk)]
                for p, q in zip(nb2, nb2[1:]):
                    sub = blk[p:q]
                    if sub: new_chunks.append({'file': title, 'doc_no': doc.get('doc_no', ''), 'chapter': chapter, 'clause': sub[0][:12], 'type': 'section', 'text': '\n'.join(sub)})
            else:
                new_chunks.append({'file': title, 'doc_no': doc.get('doc_no', ''), 'chapter': chapter, 'clause': clause, 'type': 'section', 'text': '\n'.join(blk)})

print(f'新增 {len(new_chunks)} 块;各文件块数:')

from collections import Counter

for k, v in Counter(c['file'][:20] for c in new_chunks).items(): print(' ', v, k)
mx = max(new_chunks, key=lambda c: len(c['text'])) if new_chunks else None
if mx: print('最大块字数:', len(mx['text']), mx['file'][:20], mx['clause'])
for c in new_chunks[:8]: print(' 样例:', c['clause'], '|', c['text'][:36].replace('\n', ' '))
if WRITE:
    cp = 'data/chunks_v0.json.bak'
    if not os.path.exists(cp): open(cp, 'w', encoding='utf-8').write(json.dumps(old, ensure_ascii=False))
    json.dump(old + new_chunks, open('data/chunks_v0.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('已写回 chunks_v0.json(备份 .bak),总块数', len(old) + len(new_chunks))
else:
    print('DRY-RUN 未落盘,确认样例后加 --write 重跑')