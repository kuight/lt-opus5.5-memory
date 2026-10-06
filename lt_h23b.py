# lt_h23b.py —— H2b/H3b：**只向内偏移** + 每个切面按格高拆成 4 段（规避 AABB 越界风险）
#   依据：LittleTransformableBox.setBounds(:1596-1623) 会把几何包围盒 **夹回声明范围**
#         （minX = max(minX, oldMinX)、maxX = min(maxX, oldMaxX)）⇒ 角若被移到 AABB 外，
#         真实面与"AABB 记账/切分/碰撞"就不一致 ⇒ 统一改成"盒子取 ceil 包围盒、只往内收"
import io, math
import lt_tbox, lt_root, lt_tree

RO, RI, SEG, HSTEP = 128.0, 126.0, 16, 16          # 外/内半径；16 个切面；每段高 16px（1 格）
CORNER = {("min", "min", "min"): "WDN", ("min", "min", "max"): "WDS",
          ("max", "min", "min"): "EDN", ("max", "min", "max"): "EDS",
          ("min", "max", "min"): "WUN", ("min", "max", "max"): "WUS",
          ("max", "max", "min"): "EUN", ("max", "max", "max"): "EUS"}


def facet(t1, t2, y0, y1):
    def pt(r, a): return (r * math.cos(a), r * math.sin(a))
    quad = [pt(RO, t1), pt(RO, t2), pt(RI, t2), pt(RI, t1)]
    xs = [p[0] for p in quad]; zs = [p[1] for p in quad]
    # ★ 只向内：盒子取"能装下该切面"的 ceil 包围盒
    x0, x1 = int(math.floor(min(xs))), int(math.ceil(max(xs)))
    z0, z1 = int(math.floor(min(zs))), int(math.ceil(max(zs)))
    if x1 <= x0: x1 = x0 + 1
    if z1 <= z0: z1 = z0 + 1
    offs = []
    for sx in ("min", "max"):
        for sz in ("min", "max"):
            px = x0 if sx == "min" else x1
            pz = z0 if sz == "min" else z1
            vx, vz = min(quad, key=lambda p: (p[0] - px) ** 2 + (p[1] - pz) ** 2)
            dx, dz = int(math.floor(vx + 1e-9)) - px, int(math.floor(vz + 1e-9)) - pz
            dx, dz = min(0, dx), min(0, dz)          # ★ 只向内（负数或 0）——由 ceil 包围盒保证
            if dx or dz:
                for sy in ("min", "max"):
                    c = CORNER[(sx, sy, sz)]
                    if dx: offs.append((c, "X", dx))
                    if dz: offs.append((c, "Z", dz))
    return lt_tbox.encode([x0, y0, z0, x1, y1, z1], offs)


def build(out, block, name):
    boxes = []
    for k in range(SEG):
        t1, t2 = math.radians(90.0 * k / SEG), math.radians(90.0 * (k + 1) / SEG)
        for y0 in range(0, 64, HSTEP):
            boxes.append("[I;" + ",".join(map(str, facet(t1, t2, y0, y0 + HSTEP))) + "]")
    tiles = '[{boxes:[%s],tile:{block:"%s"}}]' % (",".join(boxes), block)
    rects = [r for _, rs, _ in lt_tree.entries(tiles) for r in rs]
    lo = [min(r[i] for r in rects) for i in range(3)]
    hi = [max(r[i + 3] for r in rects) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (tiles, name, *lo, *[hi[i] - lo[i] for i in range(3)], len(rects)))
    txt = lt_root.fix(txt, name, tag=out)
    io.open(out, "w", encoding="utf-8").write(txt)
    print("%-15s %5d 字节  盒子 %d  尺寸 %.2f×%.2f×%.2f 格  导入起点 (%d,%d,%d)"
          % (out, len(txt.encode("utf-8")), len(rects),
             (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16, (hi[2] - lo[2]) / 16,
             lo[0] // 16, lo[1] // 16, lo[2] // 16))


print("== H2b/H3b：%d 切面 × %d 段（每段 1 格高）= %d 盒；只向内偏移 ==" % (SEG, 64 // HSTEP, SEG * 64 // HSTEP))
build("probe_H2b.txt", "minecraft:quartz_block", "probe_H2b")
build("probe_H3b.txt", "flatcoloredblocks:flatcoloredblock70:0", "probe_H3b")