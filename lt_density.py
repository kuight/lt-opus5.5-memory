# lt_density.py —— 精度压力样品：6 格宽 × 8 格高 × 2 格厚的金属舱壁，表面全细节 → density_test.txt
# 表面：2px 面板分缝（4×4 面板网格）/ 1px 铆钉阵列（沿面板边框，凸出 1px）/ 3px 外露管线（圆截面 SDF）
#       / 一组散热格栅（凹 1px + 每 4px 一道亮条）/ 2 处 1px 青色 FCB 发光指示条
# 报告：盒子总数、占用的方块格数、平均每格盒子数（用于估算全城规模可行性）
import io, math, re
import numpy as np
import lt_colors, lt_np, lt_root, lt_tree
from lt_colors import fc

OUT = "density_test.txt"
WPX, HPX, DPX = 96, 128, 32          # 6 格宽 × 8 格高 × 2 格厚
FRONT = DPX - 1                      # 正面（+z 侧）最外一层像素
PROUD = DPX                          # 凸出 1px 的层


def F(h, k="solid"): return fc(h, k)


v = lt_np.Vol((WPX + 16, HPX + 16, DPX + 16), (0, 0, 0), (0, 0, 0))
BASE = v.M("minecraft:iron_block")          # 主金属（整格材质做舱体底）
DARK = v.M(F("#33363a"))                    # 分缝 / 支架（深色 FCB）
LIT = v.M(F("#b9bec4"))                     # 亮金属：铆钉 / 管线 / 格栅亮条
RUB = v.M(F("#1b1d1f"))                     # 格栅凹底
CY = v.M(F("#40f0ff", "glow"))              # 青色 FCB 发光指示条

# ---------- 1) 舱壁主体（2 格厚实心）----------
v.box(BASE, 0, 0, 0, WPX, HPX, DPX)

# ---------- 2) 2px 面板分缝：4×4 面板网格（往内 2px 深的深色带）----------
for sx in (24, 48, 72):
    v.box(DARK, sx - 1, 0, FRONT - 1, sx + 1, HPX, DPX)
for sy in (32, 64, 96):
    v.box(DARK, 0, sy - 1, FRONT - 1, WPX, sy + 1, DPX)

# ---------- 3) 1px 铆钉阵列：沿每个面板边框内缩 4px，间距 8px，凸出 1px ----------
xs_panels = [(0, 24), (25, 48), (49, 72), (73, 96)]
ys_panels = [(0, 32), (33, 64), (65, 96), (97, 128)]
rivets = 0
for x0, x1 in xs_panels:
    for y0, y1 in ys_panels:
        rx = list(range(x0 + 4, x1 - 2, 8)) + [x1 - 4]
        ry = list(range(y0 + 4, y1 - 2, 8)) + [y1 - 4]
        for x in rx:
            for y in (y0 + 4, y1 - 4):
                v.px(LIT, x, y, PROUD); rivets += 1
        for y in ry:
            for x in (x0 + 4, x1 - 4):
                v.px(LIT, x, y, PROUD); rivets += 1

# ---------- 4) 一组散热格栅（面板 x25..48 / y33..64 内）----------
GX0, GX1, GY0, GY1 = 28, 45, 36, 61
v.box(RUB, GX0, GY0, FRONT, GX1, GY1, DPX)              # 凹 1px 的深底
for y in range(GY0 + 1, GY1, 4):
    v.box(LIT, GX0 + 1, y, FRONT, GX1 - 1, y + 1, DPX)  # 每 4px 一道亮条
v.box(DARK, GX0 - 2, GY0 - 2, FRONT, GX1 + 2, GY0, DPX)  # 格栅上沿边框
v.box(DARK, GX0 - 2, GY1, FRONT, GX1 + 2, GY1 + 2, DPX)  # 格栅下沿边框

# ---------- 5) 3px 外露管线（圆截面 SDF：半径 1.5px，落在 x=84、z 中心 33.5）----------
PX0, PZ0, PR = 84.0, 33.5, 1.5
pipe_px = 0
for x in range(int(PX0 - PR - 1), int(PX0 + PR + 2)):
    for z in range(int(PZ0 - PR - 1), int(PZ0 + PR + 2)):
        if (x - PX0) ** 2 + (z - PZ0) ** 2 <= PR ** 2:
            for y in range(0, HPX):
                v.px(LIT, x, y, z); pipe_px += 1
for yc in (16, 48, 80, 112):                             # 管卡：每 32px 一道
    v.box(DARK, 81, yc, FRONT, 88, yc + 2, DPX + 3)

# ---------- 6) 2 处 1px 青色 FCB 发光指示条（凸出 1px）----------
v.box(CY, 40, 68, PROUD, 41, 92, PROUD + 1)
v.box(CY, 64, 4, PROUD, 65, 28, PROUD + 1)

# ---------- 导出 ----------
start = v.export(OUT, "density_test", 'id:"fixed",name:"精度压力样_舱壁"')

# ---------- 统计 ----------
txt = io.open(OUT, encoding="utf-8").read()
nbox = sum(len(rs) for _, rs, _ in lt_tree.entries(txt[txt.index("tiles:") + 6:lt_root.tiles_end(txt)]))
V = v.V
xs, ys, zs = np.nonzero(V)
cells = len(set(zip((xs // 16).tolist(), (ys // 16).tolist(), (zs // 16).tolist())))
pxs = len(xs)
print("\n=== density_test 精度压力样品 ===")
print("尺寸：%d × %d × %d px = %.1f × %.1f × %.1f 格（%d 格宽的舱壁）"
      % (WPX, HPX, DPX + 4, WPX / 16, HPX / 16, (DPX + 4) / 16, WPX // 16))
print("盒子总数 = %d" % nbox)
print("占用的方块格数 = %d" % cells)
print("平均每格盒子数 = %.2f（注意：2 格厚的实心内部只占 1 个盒子，会把均值拉低）" % (nbox / cells))
# 表面密度（更贴近"精度观感"的指标）
boxes = [r for _, rs, _ in lt_tree.entries(txt[txt.index("tiles:") + 6:lt_root.tiles_end(txt)]) for r in rs]
surf = [b for b in boxes if b[5] > FRONT - 1]
surf_cells = len(set((x // 16, y // 16) for x in range(WPX) for y in range(HPX)))
print("表面盒子数（碰到 z≥%d 的层的盒子）= %d ；表面格数 = %d（%d 格宽 × %d 格高）"
      % (FRONT, len(surf), surf_cells, WPX // 16, HPX // 16))
print("→ 每个【表面格】平均 %d 个盒子（这才是精度观感的密度）" % round(len(surf) / surf_cells))
print("实心像素 = %d（其中管线 %d；铆钉 %d 颗）" % (pxs, pipe_px, rivets))
print("材质 %d 种：主金属 / 深色分缝支架 / 亮金属 / 格栅底 / 青色发光" % (len(v.MATS) - 1))
print("导入起点 = %s" % (start,))
print("规模估算：若天梯城可见表面 X 格，按本密度需 %.1f×X 个盒子（供可行性判断）"
      % (len(surf) / surf_cells))