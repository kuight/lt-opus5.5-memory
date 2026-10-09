# -*- coding: utf-8 -*-
# make_split.py —— 桥身(无结构) + 灯(独立小 light 树) 拆成两个文件（设计方编写，纯文本处理，不跑生成器）
import io, re, hashlib
def sha(b): return hashlib.sha256(b).hexdigest()[:16]
def rd(n): return io.open(n, encoding="utf-8", newline="").read()
def save(name, s):
    io.open(name, "w", encoding="utf-8", newline="").write(s)
    assert rd(name) == s, "读回不一致：" + name
    print(name, "字节 =", len(s.encode("utf-8")), " 结尾完整 =", s.endswith("}"),
          " structure: 次数 =", s.count("structure:"), " light 个数 =", s.count('id:"light"'),
          " sha256 =", sha(s.encode("utf-8")))
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
P = "bridge2_proto.txt"
t = rd(P); before = sha(t.encode("utf-8"))
body = rd("test_K_noroot.txt")
assert sha(body.encode("utf-8")) == "53b50e1507509657", "桥身底稿不是测过不卡的 K_noroot：停下"
assert "structure:" not in body, "桥身里有结构：停下"
K = ",children:["
assert t.count(K) == 1, "children 锚点不符：停下"
a = t.find(K); b = match(t, a + len(K) - 1)
kids = top_split(t[a + len(K):b])
assert len(kids) == 2, "light 个数不是 2：停下"
E = re.compile(r'\{(?:bBox:(\[I;[-\d,]+\])|boxes:\[((?:\[I;[-\d,]+\],?)+)\]),tile:\{block:"([^"]+)"\}\}')
lamps, cnt = [], {}
for k in kids:
    nm = re.search(r'name:"([^"]*)"', k).group(1)
    lv = int(re.search(r"level:(\d+)", k).group(1))
    st = re.search(r"enabled:\{state:(\d)\}", k).group(1)
    for m in E.finditer(k):
        arrs = [m.group(1)] if m.group(1) else re.findall(r"\[I;[-\d,]+\]", m.group(2))
        for s in arrs:
            cnt[nm] = cnt.get(nm, 0) + 1
            lamps.append(("%s%d" % (nm, cnt[nm]), lv, st, m.group(3), s))
print("灯盒 =", len(lamps), "（对照 10）", "；".join("%s×%d" % kv for kv in cnt.items()))
assert len(lamps) == 10, "灯盒数不符：停下"
V = [list(map(int, s[3:-1].split(",")))[:6] for _n, _l, _s, _b, s in lamps]
lo = [min(v[i] for v in V) for i in range(3)]
hi = [max(v[i + 3] for v in V) for i in range(3)]
def stc(nm, lv, st):
    return 'structure:{id:"light",name:"%s",level:%d,disableRightClick:0b,enabled:{state:%s}}' % (nm, lv, st)
def tl(s, blk):
    return '[{bBox:%s,tile:{block:"%s"}}]' % (s, blk)
for nm, lv, st, blk, s in lamps:
    print("  %s 亮度%d 开关%s 盒%s" % (nm, lv, st, s[3:-1].split(",")[:6]))
r = lamps[0]
ch = ["{tiles:%s,%s}" % (tl(s, blk), stc(nm, lv, st)) for nm, lv, st, blk, s in lamps[1:]]
L = "{tiles:%s,%s,children:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:1}" % (
    tl(r[4], r[3]), stc(r[0], r[1], r[2]), ",".join(ch), lo[0], lo[1], lo[2],
    hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
save("bridge2_body.txt", body)
save("bridge2_lights.txt", L)
print("灯文件 最小角 px =", lo, " 尺寸 px =", [hi[i] - lo[i] for i in range(3)])
print("灯文件放置点 = 桥放置点 + (x %+d, y %+d, z %+d) 格" % (lo[0] // 16, lo[1] // 16, lo[2] // 16))
assert sha(rd(P).encode("utf-8")) == before, "原文件被改动：停下"
print("原文件未动", before)
print("PASS")