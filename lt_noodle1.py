# -*- coding: utf-8 -*-
# lt_noodle1.py —— 合成蛋白面馆 一期：体块 + 剖面（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_noodle1.py  → noodle1.txt
# 坐标 px：x 东、y 上、z 南；临街面朝北（z 小）。局部坐标 + 边距 M 落进体素数组，导出时整体按 16 对齐归零。
# 参考：Blade Runner White Dragon 面摊（临街柜台+高凳+雨棚）；香港大排档（向外加棚/向上加层）；
#       重庆洪崖洞吊脚楼（架空层+层层出挑）；清式翼角起翘（檐口反曲、角部高于正身）
# 斜面一律只用 Y 偏移的可变形盒：侧面都落在坐标面上 ⇒ 天然共面；顶/底面四角高度满足 h00+h11=h10+h01 ⇒ 平面。
import os, sys, io, re, math
sys.path.insert(0, os.getcwd())
import numpy as np
import lt_colors, lt_root, lt_tbox, lt_mech2

OUT = "noodle1.txt"
if os.path.exists(OUT):
    os.remove(OUT)
M = 32
NX, NY, NZ = 256, 256, 240

PAL = {  # 风格 N 基础色（一期只定体块与剖面）
    "steel": ("#5C6774", "solid"), "plinth": ("#1E2329", "solid"), "deck": ("#4A5462", "solid"),
    "panel": ("#3A424D", "solid"), "rib": ("#5C6774", "solid"), "dark": ("#2A3038", "solid"),
    "top": ("#7A8594", "solid"), "amber": ("#FFB347", "glow"), "pane": ("#FFB347", "trans"),
    "eave": ("#5C6774", "solid"), "roof": ("#4A5462", "solid"),
}
MAT = {}
for k, (h, kd) in PAL.items():
    b = lt_colors.fc(h, kd)
    assert isinstance(b, str) and b, "lt_colors.fc 没返回方块名: %s %s" % (h, kd)
    MAT[k] = b

names = []
G = np.zeros((NX, NY, NZ), dtype=np.uint8)
TB = []                       # (block, 数组) 可变形盒，体素坐标
CNT = {"arc": 0, "eave": 0, "brace": 0}


def mid(k):
    b = MAT[k]
    if b not in names:
        names.append(b)
        assert len(names) < 255, "材质过多"
    return names.index(b) + 1


def fill(k, x0, y0, z0, x1, y1, z1):
    X0, X1, Z0, Z1 = x0 + M, x1 + M, z0 + M, z1 + M
    assert 0 <= X0 < X1 <= NX and 0 <= y0 < y1 <= NY and 0 <= Z0 < Z1 <= NZ, \
        "体素越界 %s" % ((k, x0, y0, z0, x1, y1, z1),)
    G[X0:X1, y0:y1, Z0:Z1] = 0 if k is None else mid(k)


CS = {(0, 0, 0): "WDN", (0, 0, 1): "WDS", (1, 0, 0): "EDN", (1, 0, 1): "EDS",
      (0, 1, 0): "WUN", (0, 1, 1): "WUS", (1, 1, 0): "EUN", (1, 1, 1): "EUS"}


def ypiece(k, x0, z0, x1, z1, h, t, tag):
    """顶面四角高度 h[(sx,sz)]（0=min 侧 / 1=max 侧），竖向板厚 t；只用 Y 偏移，全部朝盒内"""
    assert h[(0, 0)] + h[(1, 1)] == h[(1, 0)] + h[(0, 1)], "顶面四角不共面 %s" % h
    yhi = max(h.values())
    ylo = min(h.values()) - t
    assert ylo < yhi
    offs = []
    for (sx, sz), v in h.items():
        du, dd = v - yhi, v - t - ylo
        assert du <= 0 and dd >= 0, "偏移方向错误"
        if du:
            offs.append((CS[(sx, 1, sz)], "Y", du))
        if dd:
            offs.append((CS[(sx, 0, sz)], "Y", dd))
    assert offs, "斜面件没有偏移"
    arr = lt_tbox.encode([x0 + M, ylo, z0 + M, x1 + M, yhi, z1 + M], offs)
    TB.append((MAT[k], [int(v) for v in arr]))
    CNT[tag] += 1


# ===================== 飞檐：反曲 + 翼角起翘 =====================
FD = [0, 16, 32]              # 出挑距离 px
FV = [0, -3, 4]               # 相对檐根的高度：先压 3px，再翘到 +4px；翼角 = 两向相加 ⇒ +8px


def f(d):
    return FV[FD.index(d)]


def eave_ring(x0, z0, x1, z1, a, t=3):
    for i in range(2):
        d0, d1 = FD[i], FD[i + 1]
        ypiece("eave", x0, z0 - d1, x1, z0 - d0,
               {(0, 0): a + f(d1), (1, 0): a + f(d1), (0, 1): a + f(d0), (1, 1): a + f(d0)}, t, "eave")
        ypiece("eave", x0, z1 + d0, x1, z1 + d1,
               {(0, 0): a + f(d0), (1, 0): a + f(d0), (0, 1): a + f(d1), (1, 1): a + f(d1)}, t, "eave")
        ypiece("eave", x0 - d1, z0, x0 - d0, z1,
               {(0, 0): a + f(d1), (0, 1): a + f(d1), (1, 0): a + f(d0), (1, 1): a + f(d0)}, t, "eave")
        ypiece("eave", x1 + d0, z0, x1 + d1, z1,
               {(0, 0): a + f(d0), (0, 1): a + f(d0), (1, 0): a + f(d1), (1, 1): a + f(d1)}, t, "eave")
    for i in range(2):
        for j in range(2):
            du0, du1, dv0, dv1 = FD[i], FD[i + 1], FD[j], FD[j + 1]
            for cxs in (0, 1):
                for czs in (0, 1):
                    if cxs == 0:
                        X0, X1, dux = x0 - du1, x0 - du0, {0: du1, 1: du0}
                    else:
                        X0, X1, dux = x1 + du0, x1 + du1, {0: du0, 1: du1}
                    if czs == 0:
                        Z0, Z1, dvz = z0 - dv1, z0 - dv0, {0: dv1, 1: dv0}
                    else:
                        Z0, Z1, dvz = z1 + dv0, z1 + dv1, {0: dv0, 1: dv1}
                    h = {(sx, sz): a + f(dux[sx]) + f(dvz[sz]) for sx in (0, 1) for sz in (0, 1)}
                    ypiece("eave", X0, Z0, X1, Z1, h, t, "eave")


# ===================== 吊脚架空层 =====================
COLX, COLZ, CW, BH = (8, 92, 176), (8, 76, 144), 8, 5
for cx in COLX:
    for cz in COLZ:
        fill("plinth", cx - 4, 0, cz - 4, cx + 12, 16, cz + 12)     # 柱础 16px
        fill("steel", cx, 16, cz, cx + CW, 48, cz + CW)             # 钢柱
for cz in COLZ:
    fill("steel", 4, 48, cz, 188, 64, cz + CW)                      # 大梁（x 向）
for cx in COLX:
    fill("steel", cx, 48, 4, cx + CW, 64, 156)                      # 大梁（z 向）
fill("deck", 0, 64, 0, 192, 72, 160)                                # 平台


def brace(x0, z0, x1, z1, axis, rise_pos):
    """隅撑：柱面 y32 起、梁底 y48 止；低端贴柱，高端贴梁"""
    def ht(s):
        return 48 if (s == 1) == rise_pos else 32 + BH
    if axis == "x":
        h = {(sx, sz): ht(sx) for sx in (0, 1) for sz in (0, 1)}
    else:
        h = {(sx, sz): ht(sz) for sx in (0, 1) for sz in (0, 1)}
    ypiece("steel", x0, z0, x1, z1, h, BH, "brace")


for i, cx in enumerate(COLX):
    for j, cz in enumerate(COLZ):
        if i < len(COLX) - 1:
            brace(cx + CW, cz + 2, cx + CW + 16, cz + 6, "x", True)
        if i > 0:
            brace(cx - 16, cz + 2, cx, cz + 6, "x", False)
        if j < len(COLZ) - 1:
            brace(cx + 2, cz + CW, cx + 6, cz + CW + 16, "z", True)
        if j > 0:
            brace(cx + 2, cz - 16, cx + 6, cz, "z", False)

# ===================== 中层面摊（y72..136，外轮廓 x16..176 / z40..152）=====================
fill("panel", 16, 72, 40, 20, 136, 152)            # 西墙
fill("panel", 172, 72, 40, 176, 136, 152)          # 东墙
fill("panel", 16, 72, 148, 176, 136, 152)          # 南墙
fill("panel", 16, 72, 40, 24, 136, 44)             # 北面两端墙垛
fill("panel", 168, 72, 40, 176, 136, 44)
fill("panel", 24, 120, 40, 168, 136, 44)           # 北面过梁（临街整面敞开）
fill("dark", 20, 72, 146, 172, 136, 148)           # 厨房后墙深色内衬
fill("plinth", 14, 72, 40, 16, 76, 152)            # 踢脚（外凸 2px）
fill("plinth", 176, 72, 40, 178, 76, 152)
fill("plinth", 14, 72, 152, 178, 76, 154)
fill("rib", 14, 126, 38, 178, 134, 40)             # 腰线带（外凸 2px，顶 y134 给檐底留 1px）
fill("rib", 14, 126, 40, 16, 134, 152)
fill("rib", 176, 126, 40, 178, 134, 152)
fill("rib", 14, 126, 152, 178, 134, 154)
for z0, z1 in ((40, 46), (93, 99), (146, 152)):    # 竖肋
    fill("rib", 14, 76, z0, 16, 126, z1)
    fill("rib", 176, 76, z0, 178, 126, z1)
for x0, x1 in ((16, 22), (66, 72), (120, 126), (170, 176)):
    fill("rib", x0, 76, 152, x1, 126, 154)
fill("dark", 24, 72, 36, 168, 84, 56)              # 柜台身（高 1 格）
fill("top", 22, 84, 32, 170, 88, 58)               # 柜台面
fill("amber", 24, 80, 35, 168, 82, 36)             # 柜台暖光带
for c in (44, 76, 116, 148):                       # 高凳 ×4（凳面高 0.75 格）
    fill("plinth", c - 1, 72, 19, c + 1, 82, 21)
    fill("top", c - 3, 82, 17, c + 3, 84, 23)
fill("roof", 16, 136, 40, 176, 144, 152)           # 中层屋面 = 上层露台
eave_ring(16, 40, 176, 152, 144)                   # 腰檐

# ===================== 上层圆角住舱（外轮廓 x40..152 / z56..136，R=2 格）=====================
R, TH, SEG, Y_CAB, WALLH = 32, 4, 8, 144, 64
fill("panel", 72, 160, 56, 120, 224, 60)           # 北直墙
fill("plinth", 72, 144, 54, 120, 160, 60)
fill("panel", 72, 160, 132, 120, 224, 136)         # 南直墙
fill("plinth", 72, 144, 132, 120, 160, 138)
fill("panel", 40, 160, 88, 44, 224, 104)           # 西直墙
fill("plinth", 38, 144, 88, 44, 160, 104)
fill("panel", 148, 160, 88, 152, 224, 104)         # 东直墙
fill("plinth", 148, 144, 88, 154, 160, 104)
for zw, zp, zs0, zs1 in ((56, 59, 54, 56), (132, 132, 136, 138)):   # 南北琥珀窗 + 窗台
    fill(None, 80, 176, zw, 112, 208, zw + 4)
    fill("pane", 80, 176, zp, 112, 208, zp + 1)
    fill("top", 78, 174, zs0, 114, 176, zs1)
fill(None, 40, 160, 88, 44, 200, 104)              # 西门洞（通露台）
fill("dark", 43, 160, 88, 44, 200, 104)
fill("roof", 40, 224, 56, 152, 232, 136)           # 舱顶
eave_ring(40, 56, 152, 136, 232)                   # 顶檐


def add_arc(cx, cz, a0, a1):
    s = lt_mech2.arc_wall_with_base(R, TH, a0, a1, WALLH, SEG, baseH=16, extend=2,
                                    wall_block=MAT["panel"], base_block=MAT["plinth"], yseg=16)
    for m in re.finditer(r'(?:bBox|boxes):\[.*?\](?=,tile:\{block:"([^"]+)"\})', s, re.S):
        blk = m.group(1)
        for a in re.findall(r'\[I;([-\d,]+)\]', m.group(0)):
            v = [int(x) for x in a.split(",")]
            assert len(v) >= 6, "弧墙数组分量不足"
            for i, d in enumerate((cx + M, Y_CAB, cz + M)):
                v[i] += d
                v[i + 3] += d
            TB.append((blk, v))
            CNT["arc"] += 1


add_arc(72, 88, 180, 270)      # 西北
add_arc(120, 88, 270, 360)     # 东北
add_arc(120, 104, 0, 90)       # 东南
add_arc(72, 104, 90, 180)      # 西南

# ===================== 自检：可变形盒不越界、不与体素重叠 =====================
for blk, v in TB:
    x0, y0, z0, x1, y1, z1 = v[:6]
    assert 0 <= x0 < x1 <= NX and 0 <= y0 < y1 <= NY and 0 <= z0 < z1 <= NZ, "可变形盒越界 %s" % v[:6]
    assert not G[x0:x1, y0:y1, z0:z1].any(), "可变形盒与体素重叠 %s" % v[:6]


# ===================== 体素贪心合并（无损自检）=====================
def greedy():
    out = []
    for mi in range(1, len(names) + 1):
        Rm = (G == mi)
        if not Rm.any():
            continue
        xs = np.nonzero(Rm.any(axis=(1, 2)))[0]
        for x in range(int(xs[0]), int(xs[-1]) + 1):
            sl = Rm[x]
            while True:
                y, z = divmod(int(sl.argmax()), NZ)
                if not sl[y, z]:
                    break
                r = sl[y, z:]
                z2 = z + (len(r) if r.all() else int(r.argmin()))
                y2 = y + 1
                while y2 < NY and sl[y2, z:z2].all():
                    y2 += 1
                x2 = x + 1
                while x2 < NX and Rm[x2, y:y2, z:z2].all():
                    x2 += 1
                Rm[x:x2, y:y2, z:z2] = False
                out.append((mi, [x, y, z, x2, y2, z2]))
    return out


V = greedy()
Wv = np.zeros_like(G)
for mi, b in V:
    Wv[b[0]:b[3], b[1]:b[4], b[2]:b[5]] = mi
assert np.array_equal(Wv, G), "体素贪心合并不无损"

# ===================== 导出 =====================
allb = [(names[mi - 1], b) for mi, b in V] + TB
lo = [min(b[i] for _, b in allb) for i in range(3)]
hi = [max(b[i + 3] for _, b in allb) for i in range(3)]
base = [l // 16 * 16 for l in lo]


def sh(b):
    return [b[i] - base[i % 3] if i < 6 else b[i] for i in range(len(b))]


by = {}
for blk, b in allb:
    by.setdefault(blk, []).append("[I;%s]" % ",".join(map(str, sh(b))))
parts = []
for blk, arrs in by.items():
    if len(arrs) == 1:
        parts.append('{bBox:%s,tile:{block:"%s"}}' % (arrs[0], blk))
    else:
        parts.append('{boxes:[%s],tile:{block:"%s"}}' % (",".join(arrs), blk))
t = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (
    ",".join(parts), *[lo[i] - base[i] for i in range(3)], *[hi[i] - lo[i] for i in range(3)], len(allb))
t = lt_root.fix(t, "合成蛋白面馆_一期", tag=OUT)
io.open(OUT, "w", encoding="utf-8").write(t)
nbytes = len(t.encode("utf-8"))

cells = set()
for _, b in allb:
    for cx in range(b[0] // 16, (b[3] - 1) // 16 + 1):
        for cy in range(b[1] // 16, (b[4] - 1) // 16 + 1):
            for cz in range(b[2] // 16, (b[5] - 1) // 16 + 1):
                cells.add((cx, cy, cz))

print("== 合成蛋白面馆 一期 生成完毕：%s" % OUT)
print("   盒子 %d（体素 %d + 可变形 %d：弧墙 %d / 飞檐 %d / 隅撑 %d），字节 %d" % (
    len(allb), len(V), len(TB), CNT["arc"], CNT["eave"], CNT["brace"], nbytes))
print("   尺寸 %d×%d×%d px = %.2f×%.2f×%.2f 格；导入起点 (0,0,0)" % (
    hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2],
    (hi[0] - lo[0]) / 16.0, (hi[1] - lo[1]) / 16.0, (hi[2] - lo[2]) / 16.0))
print("   占用格 %d，每格平均 %.2f 盒" % (len(cells), len(allb) / float(len(cells))))
print("   分层：架空 y0..64（柱 9、大梁 6、隅撑 %d）/ 平台 y64..72 / 面摊 y72..136 / 腰檐 a=144 /"
      " 住舱 y144..224（R=32px 圆角 ×4）/ 顶檐 a=232" % CNT["brace"])
print("   飞檐剖面：出挑 %s px → 高度 %s px（翼角 %+d px）" % (FD, FV, 2 * FV[-1]))
print("   自检：可变形盒不越界 / 不与体素重叠 / 顶面共面断言 / 体素无损 —— 全部 PASS")
print("   材质：")
for k, (h, kd) in PAL.items():
    print("     %-7s %s %-5s → %s" % (k, h, kd, MAT[k]))
assert nbytes <= 1024 * 1024, "超过 1MB，停止交付"