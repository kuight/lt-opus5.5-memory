# -*- coding: utf-8 -*-
# lt_wall2.py —— 标准墙 std_wall2 生成器（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_wall2.py
# 坐标：单位 px。直段沿 +x（x 0..128），板面 n=0，向外 n>0；直段 z = ZO - n（外侧朝北）。
#   弧段 16 段：P(k,n) = (CX+(R0+n)sinθk, CZ-(R0+n)cosθk)，θk=90°·k/16。
#   k=0 时 P=(128, ZO-n) 与直段端面逐点相同 ⇒ 接缝共用顶点。
# 剖面（n 向外 / y 向上）：墙基 y0..16 外凸5、顶部45°倒角3；板面 y16..80；加强带 y46..50 凸2；
#   挑檐 y80..94 外挑4、下沿45°倒角3；石英收边 y94..96；肋框凸4；管道 n5..9；管卡 n4..10。
import os, sys, io, math
sys.path.insert(0, os.getcwd())
import numpy as np
import lt_tbox, lt_colors

OUT = "std_wall2.txt"
ZO, CX, R0 = 10, 128, 64
CZ = ZO + R0
NSEG, H = 16, 96
NX, NY, NZ = 128, 96, 27
XS0 = 3                       # x<3 为左端竖向倒角柱（可变形盒）

PAL = [("panel", "#D8DEE4"), ("rib", "#AEB6BE"), ("groove", "#3A4450"), ("hi", "#F0F4F7"),
       ("base", "#4A5562"), ("under", "#8E98A2"), ("door", "#C4CCD4"), ("clamp", "#6E7884"),
       ("cyan", "#2E6E8E"), ("red", "#C8372D")]
MAT = {}
for k, h in PAL:
    b = lt_colors.fc(h, "solid")
    assert isinstance(b, str) and b, "lt_colors.fc 没返回方块名: %s" % h
    MAT[k] = b
MAT["iron"] = "minecraft:iron_block"
MAT["quartz"] = "minecraft:quartz_block"

RIBS_S = [(0, 6), (44, 50), (88, 94)]
RIBS_A = {0, 7, 15}
CLAMP_A = {7, 15}
PIPES = [57, 63, 69]
CLAMP_Y = [(55, 57), (61, 63), (67, 69), (73, 75)]

# ===================== 直段：体素 + 每格内贪心合并 =====================
names = []
G = np.zeros((NX, NY, NZ), dtype=np.uint8)


def mid(k):
    b = MAT[k]
    if b not in names:
        names.append(b)
    return names.index(b) + 1


def fill(k, x0, x1, y0, y1, n0, n1):
    x0 = max(x0, XS0)
    if x1 <= x0:
        return
    z0, z1 = ZO - n1, ZO - n0
    G[x0:x1, y0:y1, z0:z1] = 0 if k is None else mid(k)


# 大形
fill("base", 0, 128, 0, 13, -16, 5)
fill("base", 0, 128, 13, 16, -16, 2)
fill("panel", 0, 128, 16, 80, -16, 0)
fill("under", 0, 128, 80, 83, -16, 1)
fill("rib", 0, 128, 83, 94, -16, 4)
fill("quartz", 0, 128, 94, 96, -16, 4)
# 中形
fill("rib", 0, 128, 46, 50, 0, 2)
for a, b in RIBS_S:
    fill("rib", a, b, 16, 80, 0, 4)
fill("cyan", 46, 48, 16, 80, 4, 5)                  # 石青数据线沿 44..50 肋框
# 检修口（x6..44 格间）
fill(None, 11, 39, 22, 42, -4, 0)
fill("groove", 11, 39, 22, 42, -5, -4)
fill("door", 13, 37, 24, 40, -4, -1)
for i in range(13, 37, 4):
    fill("red", i, min(i + 2, 37), 38, 40, -2, -1)
fill("iron", 32, 34, 29, 35, -1, 0)
# 通风格栅（x94..128 格间）
fill(None, 99, 123, 20, 42, -6, 0)
fill("groove", 99, 123, 20, 42, -7, -6)
for y in range(21, 41, 3):
    fill("rib", 99, 123, y, y + 1, -5, -1)
fill("rib", 110, 112, 20, 42, -6, -1)
# 管束（法兰 → 管卡 → 拐进弧段）
fill("clamp", 50, 52, 55, 75, 4, 10)
fill("clamp", 89, 93, 55, 75, 4, 10)
for b in PIPES:
    fill("iron", 52, 128, b + 1, b + 3, 5, 9)
    fill("iron", 52, 128, b, b + 1, 6, 8)
    fill("iron", 52, 128, b + 3, b + 4, 6, 8)
# 铆钉：只沿肋框两侧，离肋边 2px，竖向间距 5px
RIV = []


def busy(x, y):
    if 45 <= y < 51: return True
    if 54 <= y < 76 and x >= 48: return True
    if 10 <= x < 40 and 21 <= y < 43: return True
    if 98 <= x < 124 and 19 <= y < 43: return True
    return False


for a, b in RIBS_S:
    for x in ([a - 3] if a >= 3 else []) + [b + 2]:
        for y in range(19, 79, 5):
            if busy(x, y):
                continue
            fill("under", x, x + 1, y, y + 1, 0, 1)
            RIV.append((x, y))

# 楔形区域必须留空（由可变形盒占据）
assert not G[XS0:128, 13:16, ZO - 5:ZO - 2].any(), "墙基倒角区被体素占用"
assert not G[XS0:128, 80:83, ZO - 4:ZO - 1].any(), "挑檐倒角区被体素占用"
assert not G[0:XS0].any(), "左端倒角柱区被体素占用"


def greedy():
    out = []
    done = np.zeros(G.shape, dtype=bool)
    for cx in range(0, NX, 16):
        for cy in range(0, NY, 16):
            for cz in range(0, NZ, 16):
                X1, Y1, Z1 = min(cx + 16, NX), min(cy + 16, NY), min(cz + 16, NZ)
                for y in range(cy, Y1):
                    for z in range(cz, Z1):
                        for x in range(cx, X1):
                            m = G[x, y, z]
                            if m == 0 or done[x, y, z]:
                                continue
                            x2 = x
                            while x2 < X1 and G[x2, y, z] == m and not done[x2, y, z]:
                                x2 += 1
                            z2 = z + 1
                            while z2 < Z1 and np.all(G[x:x2, y, z2] == m) and not done[x:x2, y, z2].any():
                                z2 += 1
                            y2 = y + 1
                            while y2 < Y1 and np.all(G[x:x2, y2, z:z2] == m) and not done[x:x2, y2, z:z2].any():
                                y2 += 1
                            done[x:x2, y:y2, z:z2] = True
                            out.append((names[m - 1], [x, y, z, x2, y2, z2]))
    return out


# ===================== 可变形盒 =====================
def rnd(v):
    return int(math.floor(v + 0.5))


def P(k, n):
    t = math.radians(90.0 * k / NSEG)
    r = R0 + n
    return (rnd(CX + r * math.sin(t)), rnd(CZ - r * math.cos(t)))


def Qs(xa, xb, lo, hi):
    return [(xa, ZO - lo), (xa, ZO - hi), (xb, ZO - hi), (xb, ZO - lo)]


def area2(q):
    return sum(q[i][0] * q[(i + 1) % 4][1] - q[(i + 1) % 4][0] * q[i][1] for i in range(4))


def convex(q):
    sgn = 0
    for i in range(4):
        a, b, c = q[i], q[(i + 1) % 4], q[(i + 2) % 4]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if cr:
            s = 1 if cr > 0 else -1
            if sgn and s != sgn:
                return False
            sgn = s
    return True


def dev(p0, p1, p2, p3):
    ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    n = math.sqrt(nx * nx + ny * ny + nz * nz)
    if n < 1e-9:
        return 0.0
    return abs(((p3[0] - p0[0]) * nx + (p3[1] - p0[1]) * ny + (p3[2] - p0[2]) * nz) / n)


BOXC = [("W", "N"), ("E", "N"), ("E", "S"), ("W", "S")]
STAT = {"tbox": 0, "warp": 0.0}


def tbox(q, y0, y1, mat, tag, ymove=None):
    """q=俯视四边形 [v0(lo,起), v1(hi,起), v2(hi,止), v3(lo,止)]，竖直拉伸 y0..y1。
       四角按极角双射配对；偏移全部朝内。ymove=('U',-h)：外侧(v1,v2)上角下压 ⇒ 顶部 45° 倒角；
       ('D',+h)：外侧下角上抬 ⇒ 底部 45° 倒角。"""
    assert len(set(q)) == 4 and area2(q) != 0, "退化四边形 %s %s" % (tag, q)
    assert convex(q), "非凸四边形 %s %s" % (tag, q)
    x0 = min(p[0] for p in q); x1 = max(p[0] for p in q)
    z0 = min(p[1] for p in q); z1 = max(p[1] for p in q)
    box = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    idx = [0, 1, 2, 3] if (area2(q) > 0) == (area2(box) > 0) else [0, 3, 2, 1]
    best = None
    for sh in range(4):
        od = [idx[(i + sh) % 4] for i in range(4)]
        cost = sum((q[od[i]][0] - box[i][0]) ** 2 + (q[od[i]][1] - box[i][1]) ** 2 for i in range(4))
        if best is None or cost < best[0]:
            best = (cost, od)
    od = best[1]
    offs = []
    for i, (ex, sz) in enumerate(BOXC):
        tx, tz = q[od[i]]
        bx = x0 if ex == "W" else x1
        bz = z0 if sz == "N" else z1
        for lv in ("D", "U"):
            nm = ex + lv + sz
            if tx != bx: offs.append((nm, "X", tx - bx))
            if tz != bz: offs.append((nm, "Z", tz - bz))
            if ymove and lv == ymove[0] and od[i] in (1, 2):
                offs.append((nm, "Y", ymove[1]))
    if ymove:
        assert abs(ymove[1]) == y1 - y0, "倒角高度必须等于盒高 %s" % tag
        if ymove[0] == "U":
            f = [(q[0], y1), (q[1], y0), (q[2], y0), (q[3], y1)]
        else:
            f = [(q[0], y0), (q[1], y1), (q[2], y1), (q[3], y0)]
        p3 = [(p[0], yy, p[1]) for p, yy in f]
        STAT["warp"] = max(STAT["warp"], dev(*p3), dev(p3[1], p3[2], p3[3], p3[0]))
    coords = [x0, y0, z0, x1, y1, z1]
    if not offs:
        return (MAT[mat], coords)
    STAT["tbox"] += 1
    return (MAT[mat], lt_tbox.encode(coords, offs))


def ysplit(y0, y1):
    cuts = sorted(set([y0, y1] + [c for c in range(16, H, 16) if y0 < c < y1]))
    return list(zip(cuts[:-1], cuts[1:]))


T = []
# 直段倒角楔（按 16px 分段）
xs = [XS0] + list(range(16, 128, 16)) + [128]
for xa, xb in zip(xs[:-1], xs[1:]):
    T.append(tbox(Qs(xa, xb, 2, 5), 13, 16, "hi", "直段墙基倒角", ("U", -3)))
    T.append(tbox(Qs(xa, xb, 1, 4), 80, 83, "under", "直段挑檐倒角", ("D", 3)))
# 左端竖向 3px 倒角柱
for y0, y1, no, m in [(0, 16, 5, "base"), (16, 32, 4, "rib"), (32, 48, 4, "rib"), (48, 64, 4, "rib"),
                      (64, 80, 4, "rib"), (80, 94, 4, "rib"), (94, 96, 4, "quartz")]:
    zo = ZO - no
    T.append(tbox([(0, 26), (0, zo + 3), (3, zo), (3, 26)], y0, y1, m, "左端倒角柱"))


def arc_elems(k):
    E = []

    def R(lo, hi, y0, y1, m, ym=None):
        for a, b in ([(y0, y1)] if ym else ysplit(y0, y1)):
            E.append((lo, hi, a, b, m, ym))
    R(-16, 5, 0, 13, "base")
    R(-16, 2, 13, 16, "base")
    R(2, 5, 13, 16, "hi", ("U", -3))
    R(-16, 1, 80, 83, "under")
    R(1, 4, 80, 83, "under", ("D", 3))
    R(-16, 4, 83, 94, "rib")
    R(-16, 4, 94, 96, "quartz")
    R(-16, 0, 16, 80, "panel")
    if k in RIBS_A:
        R(0, 4, 16, 80, "rib")
        if k in CLAMP_A:
            for a, b in CLAMP_Y:
                R(4, 10, a, b, "clamp")
    else:
        R(0, 2, 46, 50, "rib")
    for b in PIPES:
        R(5, 9, b + 1, b + 3, "iron")
        R(6, 8, b, b + 1, "iron")
        R(6, 8, b + 3, b + 4, "iron")
    for i in range(len(E)):
        for j in range(i + 1, len(E)):
            a, c = E[i], E[j]
            if a[0] < c[1] and c[0] < a[1] and a[2] < c[3] and c[2] < a[3]:
                raise AssertionError("弧段 %d 元素重叠 %s / %s" % (k, a, c))
    return E


for k in range(NSEG):
    for lo, hi, y0, y1, m, ym in arc_elems(k):
        q = [P(k, lo), P(k, hi), P(k + 1, hi), P(k + 1, lo)]
        T.append(tbox(q, y0, y1, m, "弧段 k=%d n%d..%d y%d..%d" % (k, lo, hi, y0, y1), ym))

# ===================== 输出 =====================
V = greedy()
allb = V + T
groups, order = {}, []
for m, a in allb:
    if m not in groups:
        groups[m] = []; order.append(m)
    groups[m].append("[I;" + ",".join(str(int(v)) for v in a) + "]")
ents = []
for m in order:
    g = groups[m]
    ents.append(('{bBox:%s,tile:{block:"%s"}}' % (g[0], m)) if len(g) == 1
                else ('{boxes:[%s],tile:{block:"%s"}}' % (",".join(g), m)))
lo = [min(a[i] for _, a in allb) for i in range(3)]
hi = [max(a[i + 3] for _, a in allb) for i in range(3)]
txt = "{tiles:[%s],min:[I;%d,%d,%d],size:[%d,%d,%d],count:1}" % (
    ",".join(ents), lo[0], lo[1], lo[2], hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
io.open(OUT, "w", encoding="utf-8").write(txt)
back = io.open(OUT, encoding="utf-8").read()
assert back == txt, "读回不一致"
nbytes = len(back.encode("utf-8"))
assert nbytes <= 1024 * 1024, "超过 1MB，拒绝交付"

cells = set()
for _, a in allb:
    for cx in range(a[0] // 16, (a[3] - 1) // 16 + 1):
        for cy in range(a[1] // 16, (a[4] - 1) // 16 + 1):
            for cz in range(a[2] // 16, (a[5] - 1) // 16 + 1):
                cells.add((cx, cy, cz))

tot = flat = 0
hist = {}
pid = names.index(MAT["panel"]) + 1
for x in range(XS0, NX):
    for y in range(NY):
        nz = np.nonzero(G[x, y, :])[0]
        if len(nz) == 0:
            continue
        z = int(nz[0]); n = ZO - z
        tot += 1; hist[n] = hist.get(n, 0) + 1
        if n == 0 and G[x, y, z] == pid:
            flat += 1

print("== std_wall2 生成完毕：%s" % OUT)
print("   盒子 %d（体素 %d + 可变形 %d），字节 %d%s" % (len(allb), len(V), STAT["tbox"], nbytes,
      "  [警告] >900KB" if nbytes > 900 * 1024 else ""))
print("   尺寸 %d×%d×%d px = %.2f×%.2f×%.2f 格；导入起点 (%d,%d,%d)" % (
    hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2],
    (hi[0] - lo[0]) / 16.0, (hi[1] - lo[1]) / 16.0, (hi[2] - lo[2]) / 16.0, lo[0], lo[1], lo[2]))
print("   占用格 %d，每格平均 %.2f 盒" % (len(cells), len(allb) / float(len(cells))))
print("   直段正视：平整板面占比 %.1f%%（要求 ≥40%%）" % (100.0 * flat / tot))
print("   直段正视各层深度(n px → 格数)：%s" % ", ".join("%+d→%d" % (k, hist[k]) for k in sorted(hist)))
print("   铆钉 %d 颗，竖向间距 5px，离肋边 2px" % len(RIV))
print("   弧段倒角斜面最大翘曲 %.3f px；建议 LT_COPLANAR_TOL=%.2f（必须 ≤1.0）" % (
    STAT["warp"], math.ceil((STAT["warp"] + 0.005) * 100) / 100.0))
assert STAT["warp"] <= 1.0, "翘曲超过 1px，停止交付"
print("   接缝：x=128，弧段 k=0 顶点 = 直段端面（共用顶点）")
print("   配色实际方块：")
for k, h in PAL:
    print("     %-7s %s → %s" % (k, h, MAT[k]))
print("     iron    → minecraft:iron_block（管道、把手）；quartz → minecraft:quartz_block（顶部收边）")