# -*- coding: utf-8 -*-
# lt_s1.py —— 超越技术样品 S1「实体光楼」（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_s1.py  → s1_light.txt
# R8 新版（超越技术 7 : 人类寄生 3）：
#   超越层：黑色投影基座（无缝矩形 + 1px 发光缝）→ 4 束 1px 光束 → 4 层悬空错位的半透明"实体光"楼板
#           （全厚 1px 发光描边 + 顶面虚线数据纹）+ 伸出楼外的光桥；楼板之间无任何支撑
#   寄生层（风格 A）：两间蹲在光板上的铁皮舱 + 一间吊在光板下的舱（品红/青招牌、门洞、亮窗、空调）；
#           人造钢塔架够到光桥末端；近似悬链线（抛物线）电缆连舱、塔架与光板；地面电缆接基座
#   粒子：基座顶两个发射器，青色粒子上升穿过楼板
# 参考：Ash Thorp《Ghost in the Shell》Solograms；《三体》水滴/"完美矩形"；Vermette《降临》
import os, sys, io, re, math
sys.path.insert(0, os.getcwd())
import numpy as np
import lt_colors, lt_np, lt_root, lt_mech2

OUT = "s1_light.txt"
NAME = "S1_实体光楼"
if os.path.exists(OUT):
    os.remove(OUT)
if not lt_colors._P:
    lt_colors._load()

NX, NY, NZ = 192, 192, 128
V = lt_np.Vol((NX, NY, NZ), (0, 0, 0), (0, 0, 0))
G = np.zeros((NX, NY, NZ), dtype=np.uint8)          # 1 = 超越层，2 = 寄生层（只用于统计比例）

PAL = [("ped", "#0E1114", "solid"), ("slit", "#7FF6FF", "glow"), ("beam", "#BFFBFF", "glow"),
       ("slab", "#3FD8FF", "trans"), ("edge", "#DFFFFF", "glow"), ("data", "#00E5FF", "glow"),
       ("hull", "#262C34", "solid"), ("dark", "#121519", "solid"), ("rib", "#1A1F26", "solid"),
       ("mag", "#FF2A6D", "glow"), ("cyan", "#00E5FF", "glow"),
       ("iron", "minecraft:iron_block", "vanilla")]
SUPER = {"ped", "slit", "beam", "slab", "edge", "data"}


def pick(h, kind):
    hh = h.lstrip("#")
    r, g, b = int(hh[0:2], 16), int(hh[2:4], 16), int(hh[4:6], 16)
    assert lt_colors._P.get(kind), "色板缺少类别 %s" % kind
    c = min(lt_colors._P[kind], key=lambda c: (c[1]-r)**2 + (c[2]-g)**2 + (c[3]-b)**2)
    d = math.sqrt((c[1]-r)**2 + (c[2]-g)**2 + (c[3]-b)**2)
    return lt_colors.fc(h, kind), "#%02X%02X%02X" % (c[1], c[2], c[3]), d


MAT, INFO = {}, []
for k, h, kd in PAL:
    if kd == "vanilla":
        n, act, d = h, "-", 0.0
    else:
        n, act, d = pick(h, kd)
    MAT[k] = V.M(n)
    INFO.append((k, h, kd, n, act, d))


def B(k, x0, y0, z0, x1, y1, z1):
    assert 0 <= x0 < x1 <= NX and 0 <= y0 < y1 <= NY and 0 <= z0 < z1 <= NZ, \
        "越界 %s %s" % (k, (x0, y0, z0, x1, y1, z1))
    V.box(MAT[k], x0, y0, z0, x1, y1, z1)
    G[x0:x1, y0:y1, z0:z1] = 1 if k in SUPER else 2


def CLR(x0, y0, z0, x1, y1, z1):
    V.box(0, x0, y0, z0, x1, y1, z1)
    G[x0:x1, y0:y1, z0:z1] = 0


def cable(p0, p1, sag, k="rib"):
    L = math.sqrt(sum((p1[i] - p0[i]) ** 2 for i in range(3)))
    n = int(L * 3) + 2
    for i in range(n + 1):
        t = i / float(n)
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t - sag * 4 * t * (1 - t)
        z = p0[2] + (p1[2] - p0[2]) * t
        xi, yi, zi = int(round(x)), int(round(y)), int(round(z))
        if 0 <= xi < NX and 0 <= yi < NY and 0 <= zi < NZ:
            B(k, xi, yi, zi, xi + 1, yi + 1, zi + 1)


def cabin(x0, y0, z0, w, h, d, sign, hang_to=None):
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    B("hull", x0, y0, z0, x1, y1, z1)
    dx = x0 + 4                                            # 门洞：凹 2px + 发光门框
    CLR(dx, y0 + 1, z0, dx + 8, y0 + 15, z0 + 2)
    B("dark", dx, y0 + 1, z0 + 2, dx + 8, y0 + 15, z0 + 3)
    B(sign, dx - 1, y0 + 15, z0, dx + 9, y0 + 16, z0 + 1)
    B(sign, dx - 1, y0 + 1, z0, dx, y0 + 15, z0 + 1)
    B(sign, dx + 8, y0 + 1, z0, dx + 9, y0 + 15, z0 + 1)
    CLR(dx + 12, y0 + 8, z0, x1 - 3, y0 + 13, z0 + 1)      # 亮窗：凹 1px
    B("cyan", dx + 12, y0 + 8, z0 + 1, x1 - 3, y0 + 13, z0 + 2)
    B(sign, x0 + 2, y1 - 6, z0 - 1, x1 - 2, y1 - 4, z0)    # 招牌：外凸 1px
    B("rib", x0 - 1, y1, z0 - 2, x1 + 1, y1 + 2, z1 + 1)   # 屋顶挑出
    B("iron", x1, y0 + h // 2, z0 + 4, x1 + 4, y0 + h // 2 + 5, z0 + 10)   # 空调
    if hang_to:
        for hx in (x0 + 2, x1 - 3):
            for hz in (z0 + 2, z1 - 3):
                B("iron", hx, y1 + 2, hz, hx + 1, hang_to, hz + 1)


def slab(x0, z0, x1, z1, y, t=3):
    B("slab", x0, y, z0, x1, y + t, z1)
    B("edge", x0, y, z0, x1, y + t, z0 + 1); B("edge", x0, y, z1 - 1, x1, y + t, z1)
    B("edge", x0, y, z0, x0 + 1, y + t, z1); B("edge", x1 - 1, y, z0, x1, y + t, z1)
    for x in range(x0 + 12, x1 - 4, 24):
        for z in range(z0 + 4, z1 - 4, 16):
            B("data", x, y + t - 1, z, x + 1, y + t, min(z + 8, z1 - 4))


# ---------- 寄生层（先画，超越层后画覆盖）----------
cable((172, 79, 46), (124, 68, 22), 6)
cable((96, 64, 24), (49, 62, 30), 8)
cable((93, 135, 110), (106, 159, 106), 2)
B("rib", 88, 0, 46, 176, 1, 48)                            # 地面电缆
for lx, lz in ((176, 38), (187, 38), (176, 53), (187, 53)):
    B("rib", lx, 0, lz, lx + 3, 77, lz + 3)                # 塔架四腿
for y in (24, 48, 72):
    B("rib", 176, y, 38, 190, y + 2, 41); B("rib", 176, y, 53, 190, y + 2, 56)
    B("rib", 176, y, 38, 179, y + 2, 56); B("rib", 187, y, 38, 190, y + 2, 56)
B("hull", 172, 77, 34, 192, 81, 58)                        # 塔顶平台
B("mag", 172, 77, 34, 192, 78, 35)                         # 平台警示条
cabin(16, 43, 26, 32, 22, 22, "mag")                       # 蹲在光板 a 上
cabin(68, 123, 96, 24, 18, 22, "cyan")                     # 蹲在光板 c 上
cabin(96, 56, 14, 24, 18, 18, "mag", hang_to=80)           # 吊在光板 b 下

# ---------- 超越层 ----------
slab(8, 16, 104, 112, 40)
slab(24, 4, 124, 92, 80)
slab(4, 36, 96, 124, 120)
slab(30, 30, 110, 110, 160)
B("slab", 124, 81, 40, 176, 82, 52)                        # 光桥
B("edge", 124, 81, 40, 176, 82, 41); B("edge", 124, 81, 51, 176, 82, 52)
B("ped", 40, 0, 40, 88, 10, 88)                            # 投影基座
B("slit", 40, 6, 40, 88, 7, 41); B("slit", 40, 6, 87, 88, 7, 88)
B("slit", 40, 6, 40, 41, 7, 88); B("slit", 87, 6, 40, 88, 7, 88)
B("slit", 58, 10, 58, 70, 11, 70)                          # 投影镜面
for bx, bz in ((60, 60), (67, 60), (60, 67), (67, 67)):
    B("beam", bx, 11, bz, bx + 1, 176, bz + 1)             # 光束穿过楼板
B("edge", 58, 176, 58, 70, 178, 70)                        # 顶部光节点

# ---------- 导出根层 ----------
nzax = [np.nonzero(V.V.any(axis=tuple(j for j in range(3) if j != i)))[0] for i in range(3)]
base = [int(a[0]) // 16 * 16 for a in nzax]
TMP = "_s1_root.txt"
V.export(TMP, NAME)
t = io.open(TMP, encoding="utf-8").read()
os.remove(TMP)
root_tiles = t[t.index("tiles:") + 6:lt_root.tiles_end(t)]

# ---------- 粒子子结构 ----------
PSET = {"color": -12525313, "lifetime": 60, "lifetimeDeviation": 10, "gravity": 0.0,
        "startSize": 0.3, "endSize": 0.0, "collision": 0}
kids = []
for i, (px, pz) in enumerate(((44, 44), (76, 76))):
    assert not V.V[px:px + 8, 10:18, pz:pz + 8].any(), "粒子发射器位置被占用"
    pt, ps = lt_mech2.particle(facing=1, settings=PSET, xo=px - base[0], yo=10 - base[1],
                               tag="S1_p%d" % (i + 1))
    pt = lt_mech2.shift_tiles(pt, 0, 0, pz - base[2])
    kids.append(lt_mech2.node(pt, ps))

rects = lt_mech2._rects(root_tiles + "".join(kids))
lo = [min(r[i] for r in rects) for i in range(3)]
hi = [max(r[i + 3] for r in rects) for i in range(3)]
count = len(re.findall(r"\[I;", root_tiles))
txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},children:[%s],min:[I;%d,%d,%d],'
       'size:[I;%d,%d,%d],count:%d}' % (root_tiles, NAME, ",".join(kids), lo[0], lo[1], lo[2],
                                       hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], count))
txt = lt_root.fix(txt, NAME, tag=OUT)
io.open(OUT, "w", encoding="utf-8").write(txt)
nbytes = len(txt.encode("utf-8"))

ns, nh = int((G == 1).sum()), int((G == 2).sum())
print("== S1 实体光楼 生成完毕：%s" % OUT)
print("   根盒子 %d + 粒子子结构 %d；全树盒子 %d；字节 %d" % (count, len(kids), len(rects), nbytes))
print("   尺寸 %d×%d×%d px = %.2f×%.2f×%.2f 格；导入起点基准 %s" % (
    hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2],
    (hi[0] - lo[0]) / 16.0, (hi[1] - lo[1]) / 16.0, (hi[2] - lo[2]) / 16.0, base))
print("   体素比 超越:寄生 = %d:%d（%.0f%% : %.0f%%，按体积，基座占大头，仅供参考）" % (
    ns, nh, 100.0 * ns / (ns + nh), 100.0 * nh / (ns + nh)))
print("   材质映射（目标色 → 方块 → 实际色值，色差>40 标 [偏]）：")
for k, h, kd, n, act, d in INFO:
    print("     %-5s %-22s %-7s → %s  实际 %s  色差 %.0f%s" % (k, h, kd, n, act, d, "  [偏]" if d > 40 else ""))
assert nbytes <= 1024 * 1024, "超过 1MB，停止交付"