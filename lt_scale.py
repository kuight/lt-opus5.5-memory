# lt_scale.py —— 规模测试样品（用 lt_mech2 的几何接口）+ 导入上限填充文本
#   scale_A：16×16 格舱壁地表，密度同 density_test，**面板边缘全 45° 倒角**，2 层凹凸深度 + 检修舱口凹陷
#   scale_B：同上但**不加倒角**（对比）
#   limit_32k/128k/512k：纯填充（棋盘 1px 点阵，按目标字节数截断），用来测 Little Importer 的单次导入上限
import io, math, re
import lt_colors, lt_mech2 as M, lt_root, lt_tree
from lt_colors import fc

W = H = 256                      # 16 格 × 16 格（px）
FRONT = 1                        # 表面层 z=1（板厚 2px：z 0..2）


def _rects(txt):
    out = []
    for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', txt):
        out.append([int(x) for x in m.group(1).split(",")][:6])
    for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', txt, re.S):
        for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            out.append([int(x) for x in mm.group(1).split(",")][:6])
    return out


def build(out, name, bevel=True):
    v = M.Part(0, 0, W, H, 8)
    BASE = v.M("minecraft:iron_block"); DARK = v.M(fc("#33363a")); LIT = v.M(fc("#b9bec4")); RUB = v.M(fc("#1b1d1f"))
    v.box(BASE, 0, 0, 0, W, H, 2)                          # 2px 厚地表板
    # 4×4 面板（每块 4 格），2px 分缝
    for s in (64, 128, 192):
        v.box(DARK, s - 1, 0, 0, s + 1, H, 2)
        v.box(DARK, 0, s - 1, 0, W, s + 1, 2)
    # 2 层凹凸深度：外圈 1px、内场 2px（用不同深浅表现层次）
    for x0 in (0, 64, 128, 192):
        for y0 in (0, 64, 128, 192):
            v.box(RUB, x0 + 6, y0 + 6, FRONT, x0 + 58, y0 + 58, 2)      # 内场凹 1px
    # 铆钉阵列（每面板边框内缩 4px、间距 8px、凸出 1px）
    for x0 in (0, 64, 128, 192):
        for y0 in (0, 64, 128, 192):
            for x in range(x0 + 4, x0 + 62, 8):
                v.box(LIT, x, y0 + 3, 2, x + 1, y0 + 4, 3)
                v.box(LIT, x, y0 + 60, 2, x + 1, y0 + 61, 3)
            for y in range(y0 + 4, y0 + 62, 8):
                v.box(LIT, x0 + 3, y, 2, x0 + 4, y + 1, 3)
                v.box(LIT, x0 + 60, y, 2, x0 + 61, y + 1, 3)
    # 检修舱口凹陷（128..176 × 128..176，凹 2px + 四角螺栓 + 一圈框）
    v.box(RUB, 128, 128, 0, 176, 176, 1)
    v.box(DARK, 126, 126, FRONT, 178, 178, 2)
    v.box(RUB, 130, 130, FRONT, 174, 174, 1)
    for cx in (130, 172):
        for cy in (130, 172):
            v.box(LIT, cx, cy, 2, cx + 2, cy + 2, 3)
    # 散热格栅（两块面板）
    for (gx0, gy0) in ((70, 20), (198, 132)):
        v.box(RUB, gx0, gy0, FRONT, gx0 + 40, gy0 + 30, 2)
        for y in range(gy0 + 2, gy0 + 30, 4):
            v.box(LIT, gx0 + 2, y, 2, gx0 + 38, y + 1, 3)
    tiles = v.tiles("scale")
    extra = ""
    if bevel:                                              # 面板竖边 45° 倒角（只向内 + 按格拆段）
        strips = []
        for s in (64, 128, 192):
            strips.append(M.bevel_edge(s - 2, 0, 0, s + 2, H, 2, w=1, axis="Y"))
        extra = ",".join([s for s in strips if s])
    # tiles = Part 导出的条目 + 倒角条目
    all_tiles = "[%s%s]" % (tiles[tiles.index("[") + 1:tiles.rindex("]")],
                            ("," + extra) if extra else "")
    rects = _rects(all_tiles)
    lo = [min(r[i] for r in rects) for i in range(3)]
    hi = [max(r[i + 3] for r in rects) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (all_tiles, name, *lo, *[hi[i] - lo[i] for i in range(3)], len(rects)))
    txt = lt_root.fix(txt, name, tag=out)
    io.open(out, "w", encoding="utf-8").write(txt)
    print("%-14s 字节 %6d  盒子 %5d  尺寸 %.1f×%.1f×%.1f 格  导入起点 (%d,%d,%d)"
          % (out, len(txt.encode("utf-8")), len(rects),
             (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16, (hi[2] - lo[2]) / 16,
             lo[0] // 16, lo[1] // 16, lo[2] // 16))


def filler(out, target):
    """棋盘 1px 点阵填充，按目标字节数截断 → 用来测导入上限"""
    boxes, n = [], 0
    for y in range(0, 256, 2):
        for x in range(0, 256, 2):
            boxes.append('[{%s:[I;%d,%d,0,%d,%d,1],tile:{block:"minecraft:iron_block"}}]'
                         % ("bBox", x, y, x + 1, y + 1))
            n += 1
            if n % 512 == 0:
                tiles = "[%s]" % ",".join(boxes)
                if len(tiles.encode("utf-8")) >= target:
                    break
        else:
            continue
        break
    tiles = "[%s]" % ",".join(boxes)
    rects = _rects(tiles)
    lo = [min(r[i] for r in rects) for i in range(3)]
    hi = [max(r[i + 3] for r in rects) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (tiles, "limit", *lo, *[hi[i] - lo[i] for i in range(3)], len(rects)))
    io.open(out, "w", encoding="utf-8").write(lt_root.fix(txt, "limit", tag=out))
    print("%-20s 目标 %6d B → 实得 %6d B  盒子 %5d" % (out, target, len(txt.encode("utf-8")), len(rects)))


print("== scale 规模样品（16×16 格 = 256×256 px）==")
build("scale_A.txt", "scale_A", bevel=True)
build("scale_B.txt", "scale_B", bevel=False)
print("\n== 导入上限填充（Little Importer 单次上限未知，做三份给用户试）==")
for t in (32768, 131072, 524288):
    filler("limit_%dk.txt" % (t // 1024), t)