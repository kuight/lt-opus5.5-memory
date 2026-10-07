# lt_h7.py -- H7 / H7b：H6 弧墙 + 墙基（正交盒，沿弧线，比墙外凸 2px），看能否消掉墙根 AO 暗块
import io, math
import lt_colors, lt_mech2 as M, lt_root

R, TH, H, SEG = 128.0, 2.0, 64, 16
LIGHT = "flatcoloredblocks:flatcoloredblock80:7"
DARK = lt_colors.fc("#4a4d50")
EXT = 2          # 墙基外凸


def arrs(t):
    out = []
    i = 0
    while True:
        i = t.find("[I;", i)
        if i < 0:
            break
        j = t.find("]", i)
        out.append((i, j + 1, [int(x) for x in t[i + 3:j].split(",")]))
        i = j + 1
    return out


def shift_y(t, d):
    out = t
    for (i, j, a) in reversed(arrs(t)):
        if len(a) >= 6:
            a[1] += d
            a[4] += d
            out = out[:i] + "[I;" + ",".join(map(str, a)) + "]" + out[j:]
    return out


def build(out, name, base_h):
    wall = M.arc_wall_quad(R, TH, 0.0, 90.0, H, SEG, block=LIGHT)
    wall = shift_y(wall, base_h)                                  # 弧墙抬到墙基顶面
    base = M.arc_wall_quad(R + EXT, TH + EXT, 0.0, 90.0, base_h, SEG, block=DARK)
    tiles = "[%s]" % (base + "," + wall)
    r = [a[:6] for (_, _, a) in arrs(tiles) if len(a) >= 6]
    lo = [min(x[i] for x in r) for i in range(3)]
    hi = [max(x[i + 3] for x in r) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (tiles, name, *lo, *[hi[i] - lo[i] for i in range(3)], len(r)))
    io.open(out, "w", encoding="utf-8").write(lt_root.fix(txt, name, tag=out))
    print("%-14s 盒子 %3d  字节 %6d  尺寸 %.2f x %.2f x %.2f 格  导入起点 (%d,%d,%d)"
          % (out, len(r), len(txt.encode("utf-8")), (hi[0]-lo[0])/16, (hi[1]-lo[1])/16, (hi[2]-lo[2])/16,
             lo[0]//16, lo[1]//16, lo[2]//16))


print("== H7 / H7b（墙基外凸 %dpx，深色 FCB = %s）==" % (EXT, DARK))
build("probe_H7.txt", "probe_H7", 4)
build("probe_H7b.txt", "probe_H7b", 16)
