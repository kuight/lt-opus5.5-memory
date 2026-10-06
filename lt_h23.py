# lt_h23.py —— H2/H3：用 187 原生可变形盒（8+ 分量）做"多边形切面"的 1/4 圆柱墙（切面之间无台阶）
#   H2 = 石英；H3 = 纯色 FCB 灰（判断"条纹"是不是贴图拼缝造成的）
#   做法：每 1/16 圆周一个切面（90°/16 = 5.625°），每个切面 = 一个可变形盒：
#         6 分量取该切面 4 个竖边角点的 XZ 包围盒（y 0..64 贯穿），再把 8 个角的 X/Z 偏移到真正的角点
import io, math, re
import lt_tbox, lt_root, lt_tree

RO, RI, HH, SEG = 128.0, 126.0, 64, 16        # 外半径 / 内半径（壳厚 2px）/ 高 4 格 / 16 个切面
CORNER = {("min", "min", "min"): "WDN", ("min", "min", "max"): "WDS",
          ("max", "min", "min"): "EDN", ("max", "min", "max"): "EDS",
          ("min", "max", "min"): "WUN", ("min", "max", "max"): "WUS",
          ("max", "max", "min"): "EUN", ("max", "max", "max"): "EUS"}


def facet(t1, t2):
    """返回该切面的盒子数组（8+ 分量）"""
    def pt(r, a): return (r * math.cos(a), r * math.sin(a))
    quad = [pt(RO, t1), pt(RO, t2), pt(RI, t2), pt(RI, t1)]
    xs = [p[0] for p in quad]; zs = [p[1] for p in quad]
    x0, x1, z0, z1 = int(round(min(xs))), int(round(max(xs))), int(round(min(zs))), int(round(max(zs)))
    if x1 <= x0: x1 = x0 + 1
    if z1 <= z0: z1 = z0 + 1
    offs = []
    for sx in ("min", "max"):
        for sz in ("min", "max"):
            px = x0 if sx == "min" else x1
            pz = z0 if sz == "min" else z1
            vx, vz = min(quad, key=lambda p: (p[0] - px) ** 2 + (p[1] - pz) ** 2)
            dx, dz = int(round(vx)) - px, int(round(vz)) - pz
            if dx or dz:
                for sy in ("min", "max"):
                    c = CORNER[(sx, sy, sz)]
                    if dx: offs.append((c, "X", dx))
                    if dz: offs.append((c, "Z", dz))
    return lt_tbox.encode([x0, 0, z0, x1, HH, z1], offs)


def build(out, block, name):
    boxes = []
    for k in range(SEG):
        t1 = math.radians(90.0 * k / SEG)
        t2 = math.radians(90.0 * (k + 1) / SEG)
        boxes.append("[I;" + ",".join(map(str, facet(t1, t2))) + "]")
    tiles = '[{boxes:[%s],tile:{block:"%s"}}]' % (",".join(boxes), block)
    txt = tiles
    lo = [min(int(b) for b in []) if False else 0]      # 占位，下面按解析结果算
    ent = lt_tree.entries(tiles)
    rects = [r for _, rs, _ in ent for r in rs]
    lo = [min(r[i] for r in rects) for i in range(3)]
    hi = [max(r[i + 3] for r in rects) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (tiles, name, *lo, *[hi[i] - lo[i] for i in range(3)], len(rects)))
    txt = lt_root.fix(txt, name, tag=out)
    io.open(out, "w", encoding="utf-8").write(txt)
    print("%-14s %5d 字节  盒子 %d  尺寸 %.2f×%.2f×%.2f 格  导入起点 (%d,%d,%d)"
          % (out, len(txt.encode("utf-8")), len(rects),
             (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16, (hi[2] - lo[2]) / 16,
             lo[0] // 16, lo[1] // 16, lo[2] // 16))


print("== H2/H3：1/4 圆柱墙 R=8格(128px) 高 4 格 壳厚 2px，%d 个多边形切面 ==" % SEG)
build("probe_H2.txt", "minecraft:quartz_block", "probe_H2")
build("probe_H3.txt", "flatcoloredblocks:flatcoloredblock70:0", "probe_H3")
print("\n示例切面数组 = [I;%s]" % ",".join(map(str, facet(0.0, math.radians(90.0 / SEG)))))