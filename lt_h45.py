# lt_h45.py —— H4/H5/I2（用 lt_mech2.arc_wall / lt_tbox 原生写法）
#   H4：R=8格、高4格、壳厚2px、1/4 圆、16 段，石英
#   H5：同 H4，FCB 中灰（hex≈#808080，报实际选到的名字与颜色）
#   I2：3×3 格 30° 斜坡，参照 K 的原生写法（把上方两个角的 Y 降下来）
import io, math
import lt_colors, lt_mech2 as M, lt_root, lt_tree, lt_tbox
from lt_colors import fc

SEG, R, TH, H = 16, 128.0, 2.0, 64


def rects(txt):
    out = []
    for m in re.finditer_all(txt) if False else []:
        pass
    for m in __import__("re").finditer(r'bBox:\[I;([-\d,]+)\]', txt):
        out.append([int(x) for x in m.group(1).split(",")][:6])
    for m in __import__("re").finditer(r'boxes:\[(.*?)\](?=,tile:)', txt, __import__("re").S):
        for mm in __import__("re").finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            out.append([int(x) for x in mm.group(1).split(",")][:6])
    return out


def build(out, name, entries):
    tiles = "[%s]" % entries
    r = rects(tiles)
    lo = [min(x[i] for x in r) for i in range(3)]
    hi = [max(x[i + 3] for x in r) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (tiles, name, *lo, *[hi[i] - lo[i] for i in range(3)], len(r)))
    txt = lt_root.fix(txt, name, tag=out)
    io.open(out, "w", encoding="utf-8").write(txt)
    print("%-12s 盒子 %3d  字节 %5d  尺寸 %.1f×%.1f×%.1f 格  导入起点 (%d,%d,%d)"
          % (out, len(r), len(txt.encode("utf-8")), (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16,
             (hi[2] - lo[2]) / 16, lo[0] // 16, lo[1] // 16, lo[2] // 16))
    return out


print("== H4（石英）/ H5（FCB 中灰）==")
build("probe_H4.txt", "probe_H4", M.arc_wall(R, TH, 0.0, 90.0, H, SEG, block=lt_colors.fc("#c8c8c8")))
gray = fc("#808080")
print("   H5 选色：lt_colors.fc('#808080') = %s" % (gray,))
build("probe_H5.txt", "probe_H5", M.arc_wall(R, TH, 0.0, 90.0, H, SEG, block=gray))

print("\n== I2（3×3 格 30° 斜坡，参照 K 的原生写法：降上方两角 Y）==")
coords = [0, 0, 0, 48, 32, 48]
drop = int(round(math.tan(math.radians(30.0)) * 48))       # 27.7 → 28px
offs = [("EUS", "Y", -drop), ("WUS", "Y", -drop)]          # 上方(UP)+南侧(SOUTH)两角下降 → 30° 斜坡
arr = lt_tbox.encode(coords, offs)
print("   I2 盒 = [I;%s]   （drop=%dpx，48px 宽 → %.1f°）" % (",".join(map(str, arr)), drop,
                                                              math.degrees(math.atan2(drop, 48))))
build("probe_I2.txt", "probe_I2",
      '{bBox:[I;%s],tile:{block:"flatcoloredblocks:flatcoloredblock_glowing0_27:9"}}' % ",".join(map(str, arr)))
print("   （I2 材质沿用 K 样本的 %s）" % "flatcoloredblocks:flatcoloredblock_glowing0_27:9")