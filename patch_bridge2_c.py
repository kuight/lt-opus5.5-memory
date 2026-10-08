# -*- coding: utf-8 -*-
# patch_bridge2_c.py —— 二期c：墩号发光 + B-09 做旧色彩随机 + 门洞灯/梁底下照灯改为真 light 子结构（设计方编写）
import hashlib, io
P = "lt_bridge2.py"
raw = open(P, "rb").read()
h0 = hashlib.sha256(raw).hexdigest()
print("补丁前 文件 sha256 =", h0)
assert h0.startswith("75396f318476b739"), "补丁前哈希不符：停下"
src = raw.decode("utf-8").replace("\r\n", "\n")
REP = []

O = '"plate": ("#7D8794", "solid"),'
REP.append((O, O + '\n    "label": ("#CFF8FF", "glow"), "rust3": ("#8A5A2B", "solid"), "ochre": ("#A0743A", "solid"),'
               '\n    "soot": ("#24201D", "solid"), "moss": ("#4A5536", "solid"), "chalk": ("#A8A496", "solid"),', 1))

REP.append(('text("white", label,', 'text("label", label,', 4))

O = 'RND = random.Random(20261008)'
REP.append((O, O + '\nLIGHTS = []   # (名字, 亮度, 方块, 盒数组[G 坐标]) —— 真 light 子结构（FCB 发光不照亮邻块）', 1))

REP.append(('fill("cyan", ox + 4, top - 2, z0, ox + 44, top, z0 + 2)',
            'LIGHTS.append(("B-08门洞灯", 15, MAT["cyan"], [ox + 4 + M, top - 2, z0 + M, ox + 44 + M, top, z0 + 2 + M]))', 1))

O = '# ===================== 贪心合并 + 导出 ====================='
REP.append((O, '''# ===================== 二期c：B-09 做旧色彩随机（3×4px 斑块，patch_bridge2_c）=====================
RC = random.Random(20261009)
ox9 = [ox for ox, k, _l in PIERS if k == "hoop"][0]
xa, xb = ox9 - 40 + M, ox9 + 90 + M
m_r = (mid("rust"), mid("rust2"))
m_s = mid("stain")
pal_r = [mid(k) for k in ("rust", "rust2", "rust3", "ochre", "rust3")]
pal_sl = [mid(k) for k in ("stain", "moss", "moss", "soot")]
pal_sh = [mid(k) for k in ("stain", "soot", "chalk", "stain")]
cell = {}
CNT["recolor"] = 0
for x, y, z in np.argwhere(np.isin(G[xa:xb], m_r + (m_s,))):
    X = int(x) + xa
    v = int(G[X, y, z])
    key = (v == m_s, X // 3, int(y) // 4, int(z) // 3)
    if key not in cell:
        cell[key] = RC.choice((pal_sl if y < 48 else pal_sh) if v == m_s else pal_r)
    G[X, y, z] = cell[key]
    CNT["recolor"] += 1

''' + O, 1))

O = 'for blk, v in TB:'
REP.append((O, '''for i in range(len(TB) - 1, -1, -1):          # 梁底下照灯 → light 子结构
    if TB[i][0] == MAT["amber"]:
        LIGHTS.append(("梁底下照灯", 12, TB[i][0], TB[i][1]))
        del TB[i]
assert LIGHTS, "没有 light 子结构"
for _n, _lv, _b, a in LIGHTS:
    assert 0 <= a[0] < a[3] <= NX and 0 <= a[1] < a[4] <= NY and 0 <= a[2] < a[5] <= NZ, "light 越界 %s" % a[:6]
    assert not G[a[0]:a[3], a[1]:a[4], a[2]:a[5]].any(), "light 子结构与体素重叠 %s" % a[:6]
''' + O, 1))

O = 't = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (",".join(parts), *mn, *sz, len(allb))'
REP.append((O, '''kids = {}
for _n, _lv, _b, a in LIGHTS:
    for i in range(3):
        assert lo[i] <= a[i] and a[i + 3] <= hi[i], "light 超出主体并集 %s" % a[:6]
    kids.setdefault((_n, _lv), {}).setdefault(_b, []).append("[I;%s]" % ",".join(map(str, sh(a))))
cl = []
for (nm, lv), byb in kids.items():
    tp = [('{bBox:%s,tile:{block:"%s"}}' % (v[0], b)) if len(v) == 1 else
          ('{boxes:[%s],tile:{block:"%s"}}' % (",".join(v), b)) for b, v in byb.items()]
    cl.append('{tiles:[%s],structure:{id:"light",name:"%s",level:%d,disableRightClick:0b,enabled:{state:1}}}' % (",".join(tp), nm, lv))
NLIGHT = sum(len(v) for byb in kids.values() for v in byb.values())
t = "{tiles:[%s],children:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (",".join(parts), ",".join(cl), *mn, *sz, len(allb))''', 1))

O = 'print("== 材质：")'
REP.append((O, 'print("  二期c：发光墩号 4 处；B-09 重新着色像素 %d；light 子结构 %d 个（盒 %d）：%s" % (CNT["recolor"], len(kids), NLIGHT, "，".join("%s 亮度%d" % k for k in kids)))\n' + O, 1))

for o, n, c in REP:
    assert src.count(o) == c, "锚点数量不符（要 %d 实 %d）：停下 → %r" % (c, src.count(o), o[:50])
    src = src.replace(o, n)
io.open(P, "w", encoding="utf-8", newline="").write(src)
back = open(P, "rb").read()
assert back == src.encode("utf-8"), "写入读回不一致"
print("补丁后 文件 sha256 =", hashlib.sha256(back).hexdigest())
print("PASS")