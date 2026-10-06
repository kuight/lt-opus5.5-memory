# lt_mech2.py —— 机关标准写法接口库（不动 lt_np 旧接口）+ 自测
# 规则（NOTES「机关标准写法」）：控制器 light(level:0) 右键 toggle；门/灯/粒子都是它的**兄弟**子结构，con 引用 p.b0；
#   灯永远不挂门下（第 17 条）；门默认 stayAnimated:1b（第 18 条）；可变形盒只向内偏移 + 自动按格拆段（第 25/26 条）。
import io, os, re, struct, math
import lt_colors, lt_np, lt_root, lt_tree, lt_tbox
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
        assert len(a) in (6, 7, 8, 11, 12), "tiles 段出现非盒子 int 数组（%d 分量）" % len(a)
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


def emit(out, kids, plate_box, name):
    tiles = '[{bBox:[I;%s],tile:{block:"minecraft:concrete:15"}}]' % plate_box
    body = "".join(kids)
    bb = [[int(x) for x in m.group(1).split(",")][:6] for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', tiles + body)]
    for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', tiles + body, re.S):
        for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            bb.append([int(x) for x in mm.group(1).split(",")][:6])
    lo = [min(b[i] for b in bb) for i in range(3)]
    hi = [max(b[i + 3] for b in bb) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},children:[%s],min:[I;%d,%d,%d],'
           'size:[I;%d,%d,%d],count:1}' % (tiles, name, body, *lo, *[hi[i] - lo[i] for i in range(3)]))
    txt = lt_root.fix(txt, name, tag=out)
    io.open(out, "w", encoding="utf-8").write(txt)
    return txt


# ===================== 机关 API =====================
def controller(name, xo=0, yo=PLATE):
    p = Part(xo, yo, 16, 20, 3)
    p.box(p.M(F("#2a2d30")), 0, 0, 0, 16, 16, 2)
    p.box(p.M(F("#40f0ff", "glow")), 0, 7, 2, 16, 9, 3)
    return p.tiles(name), 'id:"light",level:0,enabled:{state:0}'


def light(level, con=None, delay=0, xo=24, yo=PLATE, tag="light", mode="EQUAL"):
    p = Part(xo, yo, 8, 8, 8)
    p.box(p.M("minecraft:quartz_block"), 0, 0, 0, 8, 8, 8)
    st = 'id:"light",level:%d,enabled:{state:0%s%s%s}' % (
        level, (',con:"%s"' % con) if con else "", ',mode:"%s"' % mode if con else "", ",delay:%d" % delay if con else "")
    return p.tiles(tag), st


def blink(level, delay=10, phase=0, xo=24, yo=PLATE, tag="blink"):
    """自激闪烁灯：相位用 delay 错开（phase 加到 delay 上）"""
    return light(level, con="!b0&p.b0", delay=delay + phase, xo=xo, yo=yo, tag=tag)


def door_slide(name, xo=24, stay=True, off=32, dur=40, yo=PLATE):
    p = Part(xo, yo, 32, 40, 4)
    p.box(p.M("minecraft:iron_block"), 0, 0, 0, 16, 32, 2)
    for y in range(4, 32, 4):
        p.box(0, 0, y, 0, 16, y + 1, 2)
    ac = [xo, yo, 1, xo, yo + 32, 1, 16]
    st = ('id:"advancedDoor",name:"%s",duration:%d,interpolation:0,activateParent:0b,disableRightClick:1b,'
          '%saxisCenter:[I;%s],animation:{offGrid:16,offY:%s},'
          'state:{state:0,con:"p.b0",mode:"EQUAL",delay:0}'
          % (name, dur, "stayAnimated:1b," if stay else "", ",".join(map(str, ac)), tl_lin([(0, 0), (dur, off)])))
    return p.tiles(name), st


def door_rot(name, xo=24, stay=True, deg=90, dur=20, yo=PLATE):
    p = Part(xo, yo, 24, 40, 16)
    p.box(p.M("minecraft:iron_block"), 0, 0, 8, 16, 32, 10)
    ac = [xo, yo, 9, xo, yo + 32, 9, 16]
    st = ('id:"advancedDoor",name:"%s",duration:%d,interpolation:0,activateParent:0b,disableRightClick:0b,'
          '%saxisCenter:[I;%s],animation:{rotY:%s},'
          'state:{state:0,con:"p.b0",mode:"EQUAL",delay:0}'
          % (name, dur, "stayAnimated:1b," if stay else "", ",".join(map(str, ac)),
             tl_lin([(0, 0), (dur, deg)])))
    return p.tiles(name), st


def particle(facing=1, settings=None, xo=24, yo=PLATE, tag="particle"):
    p = Part(xo, yo, 8, 8, 8)
    p.box(p.M(F("#3a3d40")), 0, 0, 0, 8, 8, 8)
    s = {'color': -1, 'lifetime': 20, 'lifetimeDeviation': 5, 'gravity': 0.0,
         'startSize': 0.4, 'endSize': 0.5, 'sizeDeviation': 0.04, 'randomColor': 0, 'collision': 1}
    s.update(settings or {})
    st = ('tickDelay:10,tickCount:1,ticker:3,speedY:0.1f,speedX:0.0f,speedZ:0.0f,spread:0.0f,facing:%d,'
          'settings:{color:%d,lifetime:%d,lifetimeDeviation:%d,gravity:%.1ff,startSize:%.1ff,endSize:%.1ff,'
          'sizeDeviation:%.2ff,randomColor:%db,collision:%db},id:"particle_emitter"'
          % (facing, s['color'], s['lifetime'], s['lifetimeDeviation'], s['gravity'],
             s['startSize'], s['endSize'], s['sizeDeviation'], s['randomColor'], s['collision']))
    return p.tiles(tag), st


# ===================== 几何 API（只向内 + 自动按格拆段）=====================
def _inward(coords, offsets):
    """强制只向内：越界的偏移按 0 截断（第 25 条）"""
    x0, y0, z0, x1, y1, z1 = coords
    out = []
    for c, ax, v in offsets:
        pos = {"EUN": (1, 1, 0), "EUS": (1, 1, 1), "EDN": (1, 0, 0), "EDS": (1, 0, 1),
               "WUN": (0, 1, 0), "WUS": (0, 1, 1), "WDN": (0, 0, 0), "WDS": (0, 0, 1)}[c]
        p = pos[{"X": 0, "Y": 1, "Z": 2}[ax]]
        if (v > 0 and p) or (v < 0 and not p):
            v = 0
        if v: out.append((c, ax, v))
    return out


def tbox_face(coords, offsets, step=16, axis="Y", tile="minecraft:quartz_block"):
    """斜切面：只向内偏移；按 step 沿 axis 拆段（默认 1 格高）"""
    out = []
    k = {"X": 0, "Y": 1, "Z": 2}[axis]
    a, b = coords[k], coords[k + 3]
    for s in range(a, b, step):
        c = list(coords); c[k] = s; c[k + 3] = min(s + step, b)
        arr = lt_tbox.encode(c, _inward(c, offsets))
        out.append('[{%s:[I;%s],tile:{block:"%s"}}]' % ("bBox", ",".join(map(str, arr)), tile))
    return ",".join(out)


def bevel_edge(x0, y0, z0, x1, y1, z1, w=2, axis="Y", tile="minecraft:quartz_block"):
    """45° 倒角条：沿 axis 拆段，每段把"外缘 4 角"向内收 w（等距 ⇒ 45°）"""
    out = []
    for s in range(y0 if axis == "Y" else z0, (y1 if axis == "Y" else z1), 16):
        e = min(s + 16, y1 if axis == "Y" else z1)
        coords = [x0, s if axis == "Y" else y0, z0, x1, e if axis == "Y" else y1, z1]
        if axis == "Y": coords = [x0, s, z0, x1, e, z1]
        offs = [("EUN", "X", -w), ("EUS", "X", -w), ("EUN", "Z", -w), ("EDN", "Z", -w),
                ("WUN", "X", w), ("WUS", "X", w), ("WUS", "Z", -w), ("WDS", "Z", w)]
        arr = lt_tbox.encode(coords, _inward(coords, offs))
        out.append('[{%s:[I;%s],tile:{block:"%s"}}]' % ("bBox", ",".join(map(str, arr)), tile))
    return ",".join(out)


def _rects(txt):
    """容错取盒：直接按 bBox/boxes 位置抓（不依赖整体解析）"""
    out = []
    for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', txt):
        out.append([int(x) for x in m.group(1).split(",")][:6])
    for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', txt, re.S):
        for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            out.append([int(x) for x in mm.group(1).split(",")][:6])
    return out


def _cmp(a, b):
    """结构等价比较：盒子集合（排序后）+ structure 段键值（去掉 name 差异）"""
    ta = io.open(a, encoding="utf-8").read(); tb = io.open(b, encoding="utf-8").read()

    def boxes(t):
        out = []
        for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', t):
            out.append(tuple(int(x) for x in m.group(1).split(",")))
        for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', t, re.S):
            for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
                out.append(tuple(int(x) for x in mm.group(1).split(",")))
        return sorted(out)

    def structs(t):
        return sorted(re.sub(r'name:"[^"]*"', 'name:"*"', s) for s in re.findall(r'structure:\{(.*?)\}(?=,|$|,children)', t))

    ba, bb = boxes(ta), boxes(tb)
    sa, sb = structs(ta), structs(tb)
    print("   %-14s vs %-16s 盒子集合(排序)=%s(%d/%d)  structure键值=%s"
          % (a, b, "一致" if ba == bb else "不同", len(ba), len(bb),
             "一致" if sa == sb else "不同"))
    if ba != bb:
        da = [x for x in ba if x not in bb][:3]; db = [x for x in bb if x not in ba][:3]
        print("      仅新有:", da, " 仅旧有:", db)
    return ba == bb and sa == sb


if __name__ == "__main__":
    c_t, c_s = controller("E2_控制器", 0)
    d_t, d_s = door_slide("E2_卷帘门", 24, stay=False)
    l_t, l_s = light(15, "p.b0", 0, 60, tag="E2_灯")
    emit("mech2_E2.txt", [node(c_t, c_s, [node(d_t, d_s), node(l_t, l_s)])], "0,0,0,76,2,24", "probe_E2")
    c_t, c_s = controller("F2_总开关", 0)
    b_t, b_s = blink(15, 10, 0, 24, tag="F2_自激灯")
    emit("mech2_F2.txt", [node(c_t, c_s, [node(b_t, b_s)])], "0,0,0,40,2,16", "probe_F2")
    c_t, c_s = controller("J2_开关", 0)
    d_t, d_s = door_slide("J2_卷帘门", 24, stay=True)
    emit("mech2_J2.txt", [node(c_t, c_s, [node(d_t, d_s)])], "0,0,0,40,2,16", "probe_J2")
    # H2b：16 切面 × 4 段（与 lt_h23b 同一取样顺序）
    boxes = []
    SEG = 16
    CS = {("min", "min", "min"): "WDN", ("min", "min", "max"): "WDS", ("max", "min", "min"): "EDN",
          ("max", "min", "max"): "EDS", ("min", "max", "min"): "WUN", ("min", "max", "max"): "WUS",
          ("max", "max", "min"): "EUN", ("max", "max", "max"): "EUS"}
    for k in range(SEG):
        t1, t2 = math.radians(90.0 * k / SEG), math.radians(90.0 * (k + 1) / SEG)
        quad = [(128 * math.cos(t1), 128 * math.sin(t1)), (128 * math.cos(t2), 128 * math.sin(t2)),
                (126 * math.cos(t2), 126 * math.sin(t2)), (126 * math.cos(t1), 126 * math.sin(t1))]
        xs = [p[0] for p in quad]; zs = [p[1] for p in quad]
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
                dx, dz = min(0, int(math.floor(vx + 1e-9)) - px), min(0, int(math.floor(vz + 1e-9)) - pz)
                if dx or dz:
                    for sy in ("min", "max"):
                        c = CS[(sx, sy, sz)]
                        if dx: offs.append((c, "X", dx))
                        if dz: offs.append((c, "Z", dz))
        for y0 in range(0, 64, 16):
            four = lt_tbox.encode([x0, y0, z0, x1, y0 + 16, z1], offs)
            four[1] = four[1]                                # 保持与 lt_h23b 相同的字段顺序
            boxes.append('[{%s:[I;%s],tile:{block:"minecraft:quartz_block"}}]' % ("bBox", ",".join(map(str, four))))
    tiles = "[%s]" % ",".join(boxes)
    rects = _rects(tiles)
    lo = [min(r[i] for r in rects) for i in range(3)]
    hi = [max(r[i + 3] for r in rects) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"probe_H2b"},min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'
           % (tiles, *lo, *[hi[i] - lo[i] for i in range(3)], len(rects)))
    io.open("mech2_H2b.txt", "w", encoding="utf-8").write(lt_root.fix(txt, "probe_H2b", tag="mech2_H2b.txt"))

    print("== lt_mech2 自测：结构等价（盒子集合 + structure 键值）==")
    res = [_cmp("mech2_E2.txt", "probe_E2.txt"), _cmp("mech2_F2.txt", "probe_F2.txt"),
           _cmp("mech2_J2.txt", "probe_J2.txt"), _cmp("mech2_H2b.txt", "probe_H2b.txt")]
    print("   汇总：%s" % ("全部等价 ✔" if all(res) else "有差异（见上）"))