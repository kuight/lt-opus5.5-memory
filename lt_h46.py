import io, math
import lt_colors, lt_mech2 as M, lt_root, lt_tree

R, TH, H, SEG = 128.0, 2.0, 64, 16
LIGHT = "flatcoloredblocks:flatcoloredblock80:7"
MID = "flatcoloredblocks:flatcoloredblock80:3"


def arrs_of(txt):
    """无正则：扫所有 [I;....] 段"""
    out = []
    i = 0
    while True:
        i = txt.find("[I;", i)
        if i < 0:
            break
        j = txt.find("]", i)
        if j < 0:
            break
        a = [int(x) for x in txt[i + 3:j].split(",")]
        out.append(a)
        i = j + 1
    return out


def rects(txt):
    return [a[:6] for a in arrs_of(txt) if len(a) >= 6]


def build(out, name, entries):
    tiles = "[%s]" % entries
    r = rects(tiles)
    if not r:
        print("!! %s 没有解析到盒子" % out)
        return
    lo = [min(x[i] for x in r) for i in range(3)]
    hi = [max(x[i + 3] for x in r) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (tiles, name, *lo, *[hi[i] - lo[i] for i in range(3)], len(r)))
    txt = lt_root.fix(txt, name, tag=out)
    io.open(out, "w", encoding="utf-8").write(txt)
    print("%-16s 盒子 %3d  字节 %6d  尺寸 %.2f x %.2f x %.2f 格  导入起点 (%d,%d,%d)"
          % (out, len(r), len(txt.encode("utf-8")), (hi[0]-lo[0])/16, (hi[1]-lo[1])/16, (hi[2]-lo[2])/16,
             lo[0]//16, lo[1]//16, lo[2]//16))


print("== H4c / H6 / H5m ==")
build("probe_H4c.txt", "probe_H4c", M.arc_wall(R, TH, 0.0, 90.0, H, SEG, block=LIGHT))
build("probe_H6.txt", "probe_H6", M.arc_wall_quad(R, TH, 0.0, 90.0, H, SEG, block=LIGHT))
build("probe_H5m.txt", "probe_H5m", M.arc_wall_quad(R, TH, 0.0, 90.0, H, SEG, block=MID))
print("   材质：H4c/H6 =", LIGHT, " H5m =", MID)
