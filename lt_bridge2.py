# -*- coding: utf-8 -*-
# lt_bridge2.py —— 轨道桥二期·原型段（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：E:\work\建筑\ 下 python lt_bridge2.py → bridge2_proto.txt
# 坡道 2px/格（全程可变形盒，逐格一段）；墩距 11/17/13 格；墩型 标准/门式/加固老墩/标准。
# 参考：李子坝轻轨穿楼（坡道+不等跨）、九龙城寨加建加固、流浪地球苏式重工业、香港天桥底空间。
import os, sys, io
sys.path.insert(0, os.getcwd())
import numpy as np
import lt_colors, lt_root, lt_tbox
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("需要 Pillow：停下，不要自己装包")

M = 16
PIERS = [(0, "std", "B-07"), (176, "portal", "B-08"), (448, "hoop", "B-09"), (656, "std", "B-10")]
L = PIERS[-1][0] + 48
Y0 = 168                      # x=0 处梁底
yb = lambda x: Y0 + x // 8    # 2px/格
NX, NY, NZ = L + 2 * M, yb(L) + 64 + M, 104 + 2 * M
PAL = {
    "plinth": ("#1E2329", "solid"), "pier": ("#5C6774", "solid"), "pier2": ("#4F5966", "solid"),
    "pil": ("#6B7685", "solid"), "cap": ("#4A5462", "solid"), "bear": ("#2A3038", "solid"),
    "beam": ("#4A5462", "solid"), "rib": ("#6B7685", "solid"), "groove": ("#2A3038", "solid"),
    "trough": ("#3A424D", "solid"), "ballast": ("#1E2329", "solid"), "rail": ("#9AA3AD", "solid"),
    "cable": ("#15181C", "solid"), "hoop": ("#3A3F45", "solid"), "rust": ("#6B4A3A", "solid"),
    "yellow": ("#E8B00F", "solid"), "black": ("#1A1A1A", "solid"), "white": ("#E6E9EC", "solid"),
    "gold": ("#C9A23A", "solid"), "cyan": ("#00E5FF", "glow"), "amber": ("#FFB347", "glow"),
    "red": ("#FF3B2F", "glow"),
}
MAT = {}
for k, (h, kd) in PAL.items():
    b = lt_colors.fc(h, kd)
    assert isinstance(b, str) and b, "lt_colors.fc 没返回方块名: %s" % k
    MAT[k] = b

def font_path():
    for fn in ("simhei.ttf", "msyh.ttc", "simsun.ttc"):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fn)
        if os.path.exists(p):
            return p
    raise SystemExit("找不到中文字体：停下")
FONT = ImageFont.truetype(font_path(), 16)

CS = {(0,0,0):"WDN",(0,0,1):"WDS",(1,0,0):"EDN",(1,0,1):"EDS",
      (0,1,0):"WUN",(0,1,1):"WUS",(1,1,0):"EUN",(1,1,1):"EUS"}
G = np.zeros((NX, NY, NZ), dtype=np.uint8)
NAMES, TB = [], []
CNT = {"slab": 0, "text": 0, "lantern": 0}

def mid(k):
    b = MAT[k]
    if b not in NAMES:
        NAMES.append(b)
    return NAMES.index(b) + 1

def fill(k, x0, y0, z0, x1, y1, z1):
    X0, X1, Z0, Z1 = x0 + M, x1 + M, z0 + M, z1 + M
    assert 0 <= X0 < X1 <= NX and 0 <= y0 < y1 <= NY and 0 <= Z0 < Z1 <= NZ, "体素越界 %s" % ((x0,y0,z0,x1,y1,z1),)
    G[X0:X1, y0:y1, Z0:Z1] = mid(k)

def paint(k, x, y, z):
    if G[x + M, y, z + M]:
        G[x + M, y, z + M] = mid(k)
        return 1
    return 0

def slab(k, x0, z0, x1, z1, top, bot):
    for d in (top, bot):
        assert d[(0,0)] + d[(1,1)] == d[(1,0)] + d[(0,1)], "四角不共面 %s" % d
    for c in top:
        assert top[c] > bot[c], "板厚 ≤0"
    yhi, ylo = max(top.values()), min(bot.values())
    offs = []
    for (sx, sz) in ((0,0),(1,0),(0,1),(1,1)):
        du, dd = top[(sx,sz)] - yhi, bot[(sx,sz)] - ylo
        assert du <= 0 and dd >= 0, "偏移方向错误（只许向内）"
        if du: offs.append((CS[(sx,1,sz)], "Y", du))
        if dd: offs.append((CS[(sx,0,sz)], "Y", dd))
    if not offs:
        fill(k, x0, ylo, z0, x1, yhi, z1); return
    TB.append((MAT[k], [int(v) for v in lt_tbox.encode([x0+M, ylo, z0+M, x1+M, yhi, z1+M], offs)]))
    CNT["slab"] += 1

flat = lambda v: {(0,0): v, (1,0): v, (0,1): v, (1,1): v}
def ramp(a, b, d0, d1):   # sx: a→b（坡）；sz: d0→d1
    return {(sx, sz): (a if sx == 0 else b) + (d0 if sz == 0 else d1) for sx in (0,1) for sz in (0,1)}

def text(k, s, xc, yc, zl, facing):
    l, t, r, b = FONT.getbbox(s)
    img = Image.new("L", (r - l, b - t), 0)
    ImageDraw.Draw(img).text((-l, -t), s, font=FONT, fill=255)
    m = np.array(img) > 128
    h, w = m.shape
    for j in range(h):
        for i in range(w):
            if m[j, i]:
                x = (xc + w // 2 - 1 - i) if facing == "N" else (xc - w // 2 + i)
                CNT["text"] += paint(k, x, yc + h // 2 - 1 - j, zl)

def stripes(x0, x1, y0, y1, zl):
    for y in range(y0, y1):
        for x in range(x0, x1):
            paint("yellow" if ((x + y) // 6) % 2 == 0 else "black", x, y, zl)

# ===================== 桥面（逐格一段可变形盒）=====================
for x0 in range(0, L, 16):
    a, b = yb(x0), yb(x0 + 16)
    seg = lambda k, z0, z1, bo, to: slab(k, x0, z0, x0 + 16, z1, ramp(a, b, *to), ramp(a, b, *bo))
    for lo, hi in ((0, 16), (16, 32), (32, 48)):
        seg("beam", 28, 68, (lo, lo), (hi, hi))
    seg("beam", 16, 28, (12, 0), (16, 16)); seg("beam", 68, 80, (0, 12), (16, 16))   # 梁底倒角
    for lo, hi in ((16, 32), (32, 48)):
        seg("beam", 16, 28, (lo, lo), (hi, hi)); seg("beam", 68, 80, (lo, lo), (hi, hi))
    for z0, z1 in ((15, 16), (80, 81)):
        seg("cyan", z0, z1, (42, 42), (44, 44))      # 轨道网青色灯带
        seg("groove", z0, z1, (38, 38), (39, 39))
    for z0, z1 in ((16, 18), (78, 80)):
        seg("rib", z0, z1, (48, 48), (60, 60))       # 护墙
        seg("rail", z0, z1, (60, 60), (62, 62))      # 扶手
    seg("trough", 20, 28, (48, 48), (54, 54))        # 电缆槽
    seg("ballast", 30, 66, (48, 48), (52, 52))       # 道床
    seg("rail", 36, 38, (52, 52), (55, 55)); seg("rail", 58, 60, (52, 52), (55, 55))
    if (x0 // 16) % 5 == 2 and not any(ox - 16 <= x0 <= ox + 48 for ox, _k, _l in PIERS):
        seg("amber", 45, 51, (-2, -2), (0, 0))       # 梁底琥珀下照：贴斜梁、避开墩

# ===================== 桥墩 =====================
HANG = []
for ox, kind, label in PIERS:
    yc = yb(ox) - 8                       # 帽梁顶
    fill("plinth", ox, 0, 8, ox + 48, 16, 88)
    if kind == "portal":                  # 门式：腿在桥外，中间留 4 格给店
        for z0 in (0, 80):
            fill("pier2", ox + 8, 16, z0, ox + 40, yc - 32, z0 + 16)
            stripes(ox + 8, ox + 40, 16, 32, z0 if z0 == 0 else z0 + 15)
        fill("cap", ox, yc - 32, 0, ox + 48, yc, 96)
        text("white", label, ox + 24, 80, 0, "N"); text("white", label, ox + 24, 80, 95, "S")
    else:
        fill("pier", ox + 4, 16, 24, ox + 44, yc - 32, 72)
        stripes(ox + 4, ox + 44, 16, 32, 24); stripes(ox + 4, ox + 44, 16, 32, 71)
        fill("cap", ox, yc - 32, 16, ox + 48, yc, 80)
        text("white", label, ox + 24, 76, 24, "N"); text("white", label, ox + 24, 76, 71, "S")
        fill("rail", ox, 16, 34, ox + 4, yc - 32, 36); fill("rail", ox, 16, 44, ox + 4, yc - 32, 46)
        for y in range(22, yc - 34, 6):
            fill("rail", ox + 1, y, 36, ox + 2, y + 1, 44)
        if kind == "hoop":                # 加固老墩：钢箍 + 斜撑 + 锈补丁 + 警示灯
            for y in range(40, yc - 40, 28):
                fill("hoop", ox + 2, y, 22, ox + 46, y + 4, 74)
            for y in range(16, 96, 2):
                d = (96 - y) // 3
                fill("hoop", ox - d - 2, y, 44, ox - d + 2, y + 3, 52)
                fill("hoop", ox + 46 + d, y, 44, ox + 50 + d, y + 3, 52)
            for (px0, py0, pw, ph) in ((8, 100, 14, 10), (26, 130, 10, 18), (12, 58, 12, 8)):
                fill("rust", ox + px0, py0, 23, ox + px0 + pw, py0 + ph, 24)
            fill("amber", ox + 20, yc - 46, 72, ox + 28, yc - 40, 74)
    slab("bear", ox + 8, 26, ox + 40, 70, ramp(yb(ox + 8), yb(ox + 40), 0, 0), flat(yc))
    fill("pil", ox + 44, yc - 20, 6, ox + 48, yc - 14, 16)        # 灯笼缆挂点
    fill("pil", ox, yc - 20, 6, ox + 4, yc - 14, 16)
    HANG.append((ox, yc - 20))

for (xa, ya), (xb, yb2) in zip(HANG, HANG[1:]):               # 北侧灯笼缆（每跨数量不同）
    xa += 48; span = xb - xa; sag = 0.12 * span; low = {}
    for x in range(xa, xb):
        t = (x - xa) / float(span)
        y = int(round(ya + (yb2 - ya) * t - sag * 4 * t * (1 - t)))
        low[x] = y
        fill("cable", x, y, 8, x + 1, y + 2, 10)
    for xc in range(xa + 24, xb - 16, 24):
        y = low[xc]
        fill("cable", xc - 1, y - 3, 8, xc + 1, y, 10)
        fill("gold", xc - 2, y - 4, 7, xc + 2, y - 3, 11)
        fill("red", xc - 2, y - 11, 7, xc + 2, y - 4, 11)
        fill("red", xc - 3, y - 10, 6, xc + 3, y - 5, 12)
        fill("gold", xc - 2, y - 12, 7, xc + 2, y - 11, 11)
        CNT["lantern"] += 1

# ===================== 贪心合并 + 导出 =====================
def greedy():
    out = []
    for mi in range(1, len(NAMES) + 1):
        Rm = (G == mi)
        if not Rm.any(): continue
        xs = np.nonzero(Rm.any(axis=(1, 2)))[0]
        for x in range(int(xs[0]), int(xs[-1]) + 1):
            sl = Rm[x]
            while True:
                y, z = divmod(int(sl.argmax()), NZ)
                if not sl[y, z]: break
                r = sl[y, z:]
                z2 = z + (len(r) if r.all() else int(r.argmin()))
                y2 = y + 1
                while y2 < NY and sl[y2, z:z2].all(): y2 += 1
                x2 = x + 1
                while x2 < NX and Rm[x2, y:y2, z:z2].all(): x2 += 1
                Rm[x:x2, y:y2, z:z2] = False
                out.append((mi, [x, y, z, x2, y2, z2]))
    return out

OUT, NAME = "bridge2_proto.txt", "轨道桥二期_原型段"
if os.path.exists(OUT): os.remove(OUT)
for blk, v in TB:
    x0, y0, z0, x1, y1, z1 = v[:6]
    assert 0 <= x0 < x1 <= NX and 0 <= y0 < y1 <= NY and 0 <= z0 < z1 <= NZ, "可变形盒越界 %s" % v[:6]
    assert not G[x0:x1, y0:y1, z0:z1].any(), "可变形盒与体素重叠 %s" % v[:6]
V = greedy()
W = np.zeros_like(G)
for mi, bx in V: W[bx[0]:bx[3], bx[1]:bx[4], bx[2]:bx[5]] = mi
assert np.array_equal(W, G), "体素贪心合并不无损"
allb = [(NAMES[mi - 1], bx) for mi, bx in V] + TB
lo = [min(bx[i] for _, bx in allb) for i in range(3)]
hi = [max(bx[i + 3] for _, bx in allb) for i in range(3)]
base = [l // 16 * 16 for l in lo]
sh = lambda bx: [bx[i] - base[i % 3] if i < 6 else bx[i] for i in range(len(bx))]
by = {}
for blk, bx in allb:
    by.setdefault(blk, []).append("[I;%s]" % ",".join(map(str, sh(bx))))
parts = [('{bBox:%s,tile:{block:"%s"}}' % (a[0], blk)) if len(a) == 1 else
         ('{boxes:[%s],tile:{block:"%s"}}' % (",".join(a), blk)) for blk, a in by.items()]
mn = [lo[i] - base[i] for i in range(3)]; sz = [hi[i] - lo[i] for i in range(3)]
t = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (",".join(parts), *mn, *sz, len(allb))
t = lt_root.fix(t, NAME, tag=OUT)
io.open(OUT, "w", encoding="utf-8").write(t)
print("== %s（%s）" % (OUT, NAME))
print("  盒子 %d（体素 %d + 可变形 %d），字节 %d" % (len(allb), len(V), len(TB), len(t.encode("utf-8"))))
print("  尺寸 %d×%d×%d px = %.2f×%.2f×%.2f 格；min=%s；文字像素 %d；灯笼 %d" % (
    sz[0], sz[1], sz[2], sz[0]/16.0, sz[1]/16.0, sz[2]/16.0, mn, CNT["text"], CNT["lantern"]))
print("  墩：%s" % "，".join("%s %s x=%d格" % (lb, k, ox // 16) for ox, k, lb in PIERS))
print("  墩距（格）：%s；梁底 %d→%d px（净空 %.1f→%.1f 格）" % (
    [(PIERS[i+1][0] - PIERS[i][0]) // 16 for i in range(3)], yb(0), yb(L), yb(0)/16.0, yb(L)/16.0))
print("== 材质：")
for k, (h, kd) in PAL.items():
    print("  %-8s %s %-5s → %s" % (k, h, kd, MAT[k]))
