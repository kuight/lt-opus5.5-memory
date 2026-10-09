# -*- coding: utf-8 -*-
# make_km.py —— 卡顿对照（设计方编写，只读 bridge2_proto.txt）
# K = 去掉两个 light 子结构；M = 每盏灯独立 light、1 灯 1 格、不与桥身同格（照旧探针成功写法）
import io, re, hashlib
def sha(b): return hashlib.sha256(b).hexdigest()[:16]
P = "bridge2_proto.txt"
t = io.open(P, encoding="utf-8", newline="").read()
before = sha(t.encode("utf-8"))
def match(s, i):
    d = 0
    for j in range(i, len(s)):
        if s[j] in "[{": d += 1
        elif s[j] in "]}":
            d -= 1
            if d == 0: return j
    raise AssertionError("括号不配对：停下")
def top_split(s):
    out, d, k = [], 0, 0
    for j, c in enumerate(s):
        if c in "[{": d += 1
        elif c in "]}": d -= 1
        elif c == "," and d == 0: out.append(s[k:j]); k = j + 1
    out.append(s[k:]); return out
def cellset(v):
    return {(x, y, z) for x in range(v[0] // 16, (v[3] - 1) // 16 + 1)
            for y in range(v[1] // 16, (v[4] - 1) // 16 + 1)
            for z in range(v[2] // 16, (v[5] - 1) // 16 + 1)}
def cuts(lo, hi):
    p = [lo] + list(range((lo // 16 + 1) * 16, hi, 16)) + [hi]
    return list(zip(p[:-1], p[1:]))
K = ",children:["
assert t.count(K) == 1, "children 锚点不符：停下"
a = t.find(K); b = match(t, a + len(K) - 1)
kids = top_split(t[a + len(K):b])
body = t[:a] + t[b + 1:]
i = body.find("structure:{")
print("children 个数 =", len(kids), " 根部结构：", body[i:i + 50] if i >= 0 else "无")
assert len(kids) == 2, "light 个数不是 2：停下"
cells, nb = set(), 0
for m in re.finditer(r"\[I;([-\d,]+)\]", body):
    v = list(map(int, m.group(1).split(",")))
    if len(v) < 6: continue
    nb += 1; cells |= cellset(v)
print("主体盒 =", nb, "（对照 4341） 主体占用格 =", len(cells))
assert nb > 4000, "主体盒数异常：停下"
E = re.compile(r'\{(?:bBox:(\[I;[-\d,]+\])|boxes:\[((?:\[I;[-\d,]+\],?)+)\]),tile:\{block:"([^"]+)"\}\}')
lamps = []
for k in kids:
    nm = re.search(r'name:"([^"]*)"', k).group(1)
    lv = int(re.search(r"level:(\d+)", k).group(1))
    st = re.search(r"enabled:\{state:(\d)\}", k).group(1)
    for m in E.finditer(k):
        arrs = [m.group(1)] if m.group(1) else re.findall(r"\[I;[-\d,]+\]", m.group(2))
        for s in arrs:
            lamps.append((nm, lv, st, m.group(3), list(map(int, s[3:-1].split(",")))))
print("灯盒 =", len(lamps), "（对照 10）")
assert len(lamps) == 10, "灯盒数不符：停下"
pieces = []
for nm, lv, st, blk, v in lamps:
    if len(v) == 6:
        for xa, xb in cuts(v[0], v[3]):
            for ya, yb in cuts(v[1], v[4]):
                for za, zb in cuts(v[2], v[5]):
                    pieces.append((nm, lv, st, blk, [xa, ya, za, xb, yb, zb]))
    else:
        pieces.append((nm, lv, st, blk, v))
used, nk, multi = set(), [], 0
for j, (nm, lv, st, blk, v) in enumerate(pieces, 1):
    for k in range(0, 320):
        w = v[:]; w[1] -= k; w[4] -= k
        assert w[1] >= 0, "下移到底仍无空格：停下 %s" % v[:6]
        cs = cellset(w)
        if not (cs & cells) and not (cs & used): break
    used |= cs; multi += len(cs) > 1
    print("  %s%d 原盒%s 下移 %dpx 占 %d 格 分量 %d" % (nm, j, v[:6], k, len(cs), len(v)))
    nk.append('{tiles:[{bBox:[I;%s],tile:{block:"%s"}}],structure:{id:"light",name:"%s%d",level:%d,'
              'disableRightClick:0b,enabled:{state:%s}}}' % (",".join(map(str, w)), blk, nm, j, lv, st))
print("M 版 light 结构 =", len(nk), " 其中跨多格 =", multi)
def save(name, s):
    io.open(name, "w", encoding="utf-8", newline="").write(s)
    back = io.open(name, encoding="utf-8", newline="").read()
    assert back == s, "读回不一致：" + name
    print(name, "字节 =", len(s.encode("utf-8")), " 结尾完整 =", s.endswith("}"),
          " light 个数 =", s.count('id:"light"'), " sha256 =", sha(s.encode("utf-8")))
save("test_K_nolight.txt", t[:a] + t[b + 1:])
save("test_M_split.txt", t[:a] + K + ",".join(nk) + t[b:])
after = sha(io.open(P, encoding="utf-8", newline="").read().encode("utf-8"))
assert before == after, "原文件被改动：停下"
print("原文件未动", after)
print("PASS")