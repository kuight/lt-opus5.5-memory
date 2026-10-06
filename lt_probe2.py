# lt_probe2.py —— 按 2a 结论重做的探针：灯/控制器**不能**当门的子结构（会被搬进动画假世界 → 不发光）
#   正确结构 = 根 fixed → 控制器 light(level:0，右键切换 enabled) → 里面并列放【门】和【灯】（互为兄弟）
#     · 门自己 con:"p.b0"（跟控制器的 enabled）
#     · 灯 con:"p.b0"（E2）或 con:"!b0&p.b0"（F2 自激 + 总开关）
#   E2 / F2 / F2x10 / J2 各出一份独立文件（每份独立根 fixed），全部过 lt_root + lt_tree
import io, os, re, struct, math
import numpy as np
import lt_colors, lt_np, lt_root, lt_tree
from lt_colors import fc

PLATE = 2


def F(h, k="solid"): return fc(h, k)


def dbl(v):
    b = struct.unpack(">q", struct.pack(">d", float(v)))[0]; lo = b & 0xFFFFFFFF
    return [b >> 32, lo - (1 << 32) if lo >= 1 << 31 else lo]


def tl_lin(pts):
    a = [0, len(pts)]
    for t, v in pts: a += [t] + dbl(v)
    return "[I;" + ",".join(map(str, a)) + "]"


def shift_tiles(tiles, dx, dy, dz):
    def r(m):
        a = [int(x) for x in m.group(1).split(",")]
        assert len(a) in (6, 7, 11), "tiles 段出现非盒子 int 数组（%d 分量）: %s" % (len(a), a)
        for i, dd in enumerate((dx, dy, dz)):
            a[i] += dd; a[i + 3] += dd
        return "[I;" + ",".join(map(str, a)) + "]"
    return re.sub(r"\[I;([-\d,]+)\]", r, tiles)


class Part:
    def __init__(self, xo, yo, w, h, d):
        self.v = lt_np.Vol((w + 8, h + 8, d + 8), (0, 0, 0), (0, 0, 0))
        self.xo, self.yo = xo, yo
    def M(self, b): return self.v.M(b)
    def box(self, m, x1, y1, z1, x2, y2, z2): self.v.box(m, x1, y1, z1, x2, y2, z2)
    def tiles(self, tag):
        fn = "_tmp_%s.txt" % re.sub(r"[^0-9A-Za-z_]", "", tag)
        self.v.export(fn, tag)
        t = io.open(fn, encoding="utf-8").read(); os.remove(fn)
        return shift_tiles(t[t.index("tiles:") + 6:lt_root.tiles_end(t)], self.xo, self.yo, 0)


def node(tiles, st, kids=()):
    s = "{tiles:%s,structure:{%s}" % (tiles, st)
    if kids: s += ",children:[%s]" % ",".join(kids)
    return s + "}"


def write(out, kids, plate_box, name):
    tiles = '[{bBox:[I;%s],tile:{block:"minecraft:concrete:15"}}]' % plate_box
    body = "".join(kids)
    bb = []
    for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', tiles + body):
        bb.append([int(x) for x in m.group(1).split(",")][:6])
    for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', tiles + body, re.S):
        for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            bb.append([int(x) for x in mm.group(1).split(",")][:6])
    lo = [min(b[i] for b in bb) for i in range(3)]
    hi = [max(b[i + 3] for b in bb) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},children:[%s],min:[I;%d,%d,%d],'
           'size:[I;%d,%d,%d],count:1}' % (tiles, name, body, *lo,
                                            *[hi[i] - lo[i] for i in range(3)]))
    txt = lt_root.fix(txt, name, tag=out)
    io.open(out, "w", encoding="utf-8").write(txt)
    print("%-18s %5d 字节  导入起点 (%d,%d,%d)  尺寸 %.2f×%.2f×%.2f 格"
          % (out, len(txt.encode("utf-8")), lo[0] // 16, lo[1] // 16, lo[2] // 16,
             (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16, (hi[2] - lo[2]) / 16))


# ---------- 部件工厂 ----------
def controller(xo, tag):                       # 控制器：light level:0（右键切换 enabled）
    p = Part(xo, PLATE, 16, 20, 3)
    p.box(p.M(F("#2a2d30")), 0, 0, 0, 16, 16, 2)
    p.box(p.M(F("#40f0ff", "glow")), 0, 7, 2, 16, 9, 3)     # 青色指示条
    return p.tiles(tag), 'id:"light",level:0,enabled:{state:0}'


def door(xo, tag, stay=False):                 # 卷帘门：1 格宽 × 2 格高，offY 上升 2 格
    p = Part(xo, PLATE, 32, 40, 4)
    p.box(p.M("minecraft:iron_block"), 0, 0, 0, 16, 32, 2)
    for y in range(4, 32, 4):
        p.box(0, 0, y, 0, 16, y + 1, 2)        # 1px 横向分缝
    ac = [xo, PLATE, 1, xo, PLATE + 32, 1, 16]
    st = ('id:"advancedDoor",name:"%s",duration:40,interpolation:0,activateParent:0b,'
          'disableRightClick:1b,%saxisCenter:[I;%s],animation:{offGrid:16,offY:%s},'
          'state:{state:0,con:"p.b0",mode:"EQUAL",delay:0}'
          % (tag, "stayAnimated:1b," if stay else "", ",".join(map(str, ac)),
             tl_lin([(0, 0), (40, 32)])))
    return p.tiles(tag), st


def lamp(xo, tag, con, level=15):
    p = Part(xo, PLATE, 8, 8, 8)
    p.box(p.M("minecraft:quartz_block"), 0, 0, 0, 8, 8, 8)
    return p.tiles(tag), 'id:"light",level:%d,enabled:{state:0,con:"%s",mode:"EQUAL",delay:%d}' % (
        level, con, 10 if con.startswith("!") else 0)


# ---------- E2：控制器 → 子0 门、子1 灯（兄弟，门动时灯留在世界）----------
E2_T, E2_S = controller(0, "E2_控制器")
E2_D_T, E2_D_S = door(24, "E2_卷帘门")
E2_L_T, E2_L_S = lamp(60, "E2_灯", "p.b0")
write("probe_E2.txt", [node(E2_T, E2_S, [node(E2_D_T, E2_D_S), node(E2_L_T, E2_L_S)])],
      "0,0,0,%d,%d,%d" % (76, PLATE, 24), "probe_E2")

# ---------- F2：控制器 → 1 盏自激灯（con = !自己 & 父.enabled）----------
F2_T, F2_S = controller(0, "F2_总开关")
F2_L_T, F2_L_S = lamp(24, "F2_自激灯", "!b0&p.b0")
write("probe_F2.txt", [node(F2_T, F2_S, [node(F2_L_T, F2_L_S)])],
      "0,0,0,%d,%d,%d" % (40, PLATE, 16), "probe_F2")

# ---------- F2x10：控制器 → 10 盏自激灯 ----------
F2X_T, F2X_S = controller(0, "F2x10_总开关")
kids = []
for i in range(10):
    t, s = lamp(24 + i * 16, "F2x10_灯%d" % i, "!b0&p.b0")
    kids.append(node(t, s))
write("probe_F2x10.txt", [node(F2X_T, F2X_S, kids)],
      "0,0,0,%d,%d,%d" % (24 + 10 * 16, PLATE, 16), "probe_F2x10")

# ---------- J2：J（灯为父、门为子）加 stayAnimated:1b ----------
J2_CT, J2_CS = controller(0, "J2_开关")
J2_D_T, J2_D_S = door(24, "J2_卷帘门", stay=True)
write("probe_J2.txt", [node(J2_CT, J2_CS, [node(J2_D_T, J2_D_S)])],
      "0,0,0,%d,%d,%d" % (40, PLATE, 16), "probe_J2")
print("\n说明：E2 用 offY 位移门（不是 J 那种）；J2 才是 J 的 stayAnimated 版（灯/控制器都不在门里）")