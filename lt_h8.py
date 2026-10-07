# lt_h8.py -- probe_H8：16px 墙基 + 弧墙（角点双射配对、密采样检查）
import io, lt_colors, lt_mech2 as M, lt_root
R, TH, H, SEG = 128.0, 2.0, 64, 16
LIGHT = "flatcoloredblocks:flatcoloredblock80:7"
DARK = lt_colors.fc("#4a4d50")          # 墙基深色


def arrs(t):
    o = []; i = 0
    while True:
        i = t.find("[I;", i)
        if i < 0: break
        j = t.find("]", i); o.append([int(x) for x in t[i+3:j].split(",")]); i = j + 1
    return o


tiles = M.arc_wall_with_base(R, TH, 0.0, 90.0, H, SEG, baseH=16, extend=2,
                             wall_block=LIGHT, base_block=DARK)
r = [a[:6] for a in arrs(tiles) if len(a) >= 6]
lo = [min(x[i] for x in r) for i in range(3)]
hi = [max(x[i+3] for x in r) for i in range(3)]
txt = ('{tiles:[%s],structure:{id:"fixed",name:"probe_H8"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
       % (tiles, *lo, *[hi[i]-lo[i] for i in range(3)], len(r)))
io.open("probe_H8.txt", "w", encoding="utf-8").write(lt_root.fix(txt, "probe_H8", tag="probe_H8"))
print("probe_H8.txt 盒子 %d 字节 %d 墙基色 %s" % (len(r), len(txt.encode()), DARK))
