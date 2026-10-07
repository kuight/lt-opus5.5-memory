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


# ===================== prism / arc_wall（按格裁剪 + 竖边 U/D 同偏移 + 只向内）=====================
CS8 = {("min", "min", "min"): "WDN", ("min", "min", "max"): "WDS", ("max", "min", "min"): "EDN",
       ("max", "min", "max"): "EDS", ("min", "max", "min"): "WUN", ("min", "max", "max"): "WUS",
       ("max", "max", "min"): "EUN", ("max", "max", "max"): "EUS"}


def _clip(poly, axis, value, keep_greater):
    """Sutherland-Hodgman：按 axis=value 半平面裁剪"""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        fa = (a[axis] - value) if keep_greater else (value - a[axis])
        fb = (b[axis] - value) if keep_greater else (value - b[axis])
        if fa >= 0: out.append(a)
        if (fa >= 0) != (fb >= 0):
            t = fa / (fa - fb)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _split_quad(poly):
    """把凸多边形拆成 ≤4 顶点的凸块（超过 4 就用扇形拆）"""
    if len(poly) <= 4: return [poly]
    return [[poly[0], poly[i], poly[i + 1]] for i in range(1, len(poly) - 1)]


def merge_entries(entries):
    """把多个盒子条目按材质合并成【规范形状】{boxes:[…],tile:{block:"…"}}（lt_tree/游戏都吃这个形状）
       ★ 先剥掉条目外层可能带的 [ ]（prism/bevel_edge 逐条生成时带过），再合并；合并结果必须非空"""
    bymat = {}
    s = ""
    for e in entries:
        if not e: continue
        e = e.strip()
        if e.startswith("[") and e.endswith("]"):
            e = e[1:-1]
        s += e + ","
    # 用"数组 + 紧邻的 tile:{block:"…"}"配对（能穿透嵌套花括号）；★ 在整个匹配里找 [I;…]（不要先剥掉方括号）
    for m in re.finditer(r'(?:bBox|boxes):\[.*?\](?=,tile:\{block:"([^"]+)"\})', s, re.S):
        bymat.setdefault(m.group(1), []).extend(re.findall(r'\[I;[-\d,]+\]', m.group(0)))
    out = []
    for blk, arrs in bymat.items():
        if len(arrs) == 1:
            out.append('{bBox:%s,tile:{block:"%s"}}' % (arrs[0], blk))
        else:
            out.append('{boxes:[%s],tile:{block:"%s"}}' % (",".join(arrs), blk))
    merged = ",".join(out)
    assert merged, "merge_entries 合并后为空：条目形状不符合 {bBox|boxes:…,tile:{block:…}}"
    return merged


def prism(poly_xz, y0, y1, block="minecraft:quartz_block", ystep=16, band=None):
    """俯视凸多边形沿 y 拉伸：按方块格裁剪(Sutherland-Hodgman) -> 每块 AABB(floor/ceil 包围盒)
       + 4 条竖边各自对到最近的真顶点(取整)：同竖边的 U/D 偏移完全相同、Y 偏移恒 0、按 ystep 拆段
       + 偏移只朝盒内（min 侧向内=正、max 侧向内=负；旧版一律 min(0,.) 会啃掉内弧 1px）"""
    entries = []
    xs = [q[0] for q in poly_xz]
    zs = [q[1] for q in poly_xz]
    ci0, ci1 = int(math.floor(min(xs) / 16.0)), int(math.floor(max(xs) / 16.0))
    cz0, cz1 = int(math.floor(min(zs) / 16.0)), int(math.floor(max(zs) / 16.0))
    for ci in range(ci0, ci1 + 1):
        for cz in range(cz0, cz1 + 1):
            poly = poly_xz
            poly = _clip(poly, 0, ci * 16, True)
            poly = _clip(poly, 0, (ci + 1) * 16, False)
            poly = _clip(poly, 1, cz * 16, True)
            poly = _clip(poly, 1, (cz + 1) * 16, False)
            if len(poly) < 3:
                continue
            for piece in _split_quad(poly):
                if len(piece) < 3:
                    continue
                vx = [q[0] for q in piece]
                vz = [q[1] for q in piece]
                x0, x1 = int(math.floor(min(vx))), int(math.ceil(max(vx)))
                z0, z1 = int(math.floor(min(vz))), int(math.ceil(max(vz)))
                if x1 <= x0:
                    x1 = x0 + 1
                if z1 <= z0:
                    z1 = z0 + 1
                offs = []
                for sx in ("min", "max"):
                    for sz in ("min", "max"):
                        ax = x0 if sx == "min" else x1
                        az = z0 if sz == "min" else z1
                        tx, tz = min(piece, key=lambda q: (q[0] - ax) ** 2 + (q[1] - az) ** 2)
                        if band is not None:
                            tx, tz = _snap_to_band(tx, tz, band[0], band[1], band[2])
                        else:
                            tx, tz = int(round(tx)), int(round(tz))     # ★ band=None 也要取整（否则 float 进入 encode 报错）
                        dx = tx - ax
                        dz = tz - az
                        dx = min(0, dx) if sx == "max" else max(0, dx)
                        dz = min(0, dz) if sz == "max" else max(0, dz)
                        if dx or dz:
                            for sy in ("min", "max"):
                                c = CS8[(sx, sy, sz)]
                                if dx:
                                    offs.append((c, "X", dx))
                                if dz:
                                    offs.append((c, "Z", dz))
                # ---- 环带钳制：若某竖边角点算完后仍越出目标环带，就在 ±1px 内把它拉回来 ----
                if band is not None:
                    rin, rout, tol = band[0], band[1], band[2]
                    for sx2 in ("min", "max"):
                        for sz2 in ("min", "max"):
                            ax2 = x0 if sx2 == "min" else x1
                            az2 = z0 if sz2 == "min" else z1
                            cur = {(c, a): v for (c, a, v) in offs}
                            for sy2 in ("min", "max"):
                                c2 = CS8[(sx2, sy2, sz2)]
                                cx = ax2 + cur.get((c2, "X"), 0)
                                cz = az2 + cur.get((c2, "Z"), 0)
                                rr = math.hypot(cx, cz)
                                if rr < rin - tol or rr > rout + tol:
                                    best = None
                                    for ddx in (-1, 0, 1):
                                        for ddz in (-1, 0, 1):
                                            nx, nz = cx + ddx, cz + ddz
                                            if not (x0 <= nx <= x1 and z0 <= nz <= z1):
                                                continue
                                            nr = math.hypot(nx, nz)
                                            err = 0.0 if (rin - tol <= nr <= rout + tol) else min(abs(nr - rin), abs(nr - rout))
                                            if best is None or err < best[0]:
                                                best = (err, ddx, ddz)
                                    if best:
                                        _, ddx, ddz = best
                                        if ddx:
                                            offs = [o for o in offs if not (o[0] == c2 and o[1] == "X")]
                                            if cur.get((c2, "X"), 0) + ddx:
                                                offs.append((c2, "X", cur.get((c2, "X"), 0) + ddx))
                                        if ddz:
                                            offs = [o for o in offs if not (o[0] == c2 and o[1] == "Z")]
                                            if cur.get((c2, "Z"), 0) + ddz:
                                                offs.append((c2, "Z", cur.get((c2, "Z"), 0) + ddz))
                for ys in range(y0, y1, ystep):
                    ye = min(ys + ystep, y1)
                    arr = lt_tbox.encode([x0, ys, z0, x1, ye, z1], offs)
                    entries.append('[{%s:[I;%s],tile:{block:"%s"}}]' % ("bBox", ",".join(map(str, arr)), block))
    return merge_entries(entries)


def arc_wall(R=128.0, thick=2.0, a0=0.0, a1=90.0, height=64, seg=16, block="minecraft:quartz_block"):
    """1/4 圆弧壳墙：每段由内外弧上 4 个点组成四边形，交给 prism；返回 tiles 条目串"""
    entries = []
    for k in range(seg):
        t1 = math.radians(a0 + (a1 - a0) * k / seg)
        t2 = math.radians(a0 + (a1 - a0) * (k + 1) / seg)
        ro, ri = R, R - thick
        poly = [(ro * math.cos(t1), ro * math.sin(t1)), (ro * math.cos(t2), ro * math.sin(t2)),
                (ri * math.cos(t2), ri * math.sin(t2)), (ri * math.cos(t1), ri * math.sin(t1))]
        e = prism(poly, 0, height, block=block, band=(R - thick - 0.5, R + 0.5, 0.5))
        if e: entries.append(e)
    return merge_entries([e for e in entries])
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


def bevel_edge(x0, y0, z0, x1, y1, z1, w=2, axis="Y", tile="minecraft:quartz_block", sides="EWNS"):
    """45° 倒角条（真斜切：顶面四边的角同时向内收 w 并下降 w）
       · 属"非竖直拉伸件"（有 Y 偏移），因此不适用"同竖边 U/D 一致"规则；靠共面检查
       · 仍然只向内偏移（X/Z 朝盒内、Y 朝下减小）"""
    out = []
    ylo, yhi = (y0, y1) if axis == "Y" else (z0, z1)
    for s in range(ylo, yhi, 16):
        e = min(s + 16, yhi)
        coords = [x0, s, z0, x1, e, z1] if axis == "Y" else [x0, y0, s, x1, y1, e]
        offs = []
        if "E" in sides:                                   # 东侧两条竖边：顶角 X -w、Y -w
            offs += [("EUN", "X", -w), ("EUN", "Y", -w), ("EUS", "X", -w), ("EUS", "Y", -w)]
        if "W" in sides:
            offs += [("WUN", "X", w), ("WUN", "Y", -w), ("WUS", "X", w), ("WUS", "Y", -w)]
        if "N" in sides:
            offs += [("EUN", "Z", w), ("EUN", "Y", -w), ("WUN", "Z", w), ("WUN", "Y", -w)]
        if "S" in sides:
            offs += [("EUS", "Z", -w), ("EUS", "Y", -w), ("WUS", "Z", -w), ("WUS", "Y", -w)]
        arr = lt_tbox.encode(coords, offs)
        out.append('[{%s:[I;%s],tile:{block:"%s"}}]' % ("bBox", ",".join(map(str, arr)), tile))
    return merge_entries(out)


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

def _snap_to_band(x, z, rin, rout, tol=0.5):
    """把浮点顶点吸附成【落在环带内的整点】（先试最近整点，不行就在 ±2px 邻域里找最近的合规点）"""
    bx, bz = int(round(x)), int(round(z))
    if rin - tol <= math.hypot(bx, bz) <= rout + tol:
        return (bx, bz)
    best = None
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            nx, nz = bx + dx, bz + dz
            r = math.hypot(nx, nz)
            if rin - tol <= r <= rout + tol:
                d = (nx - x) ** 2 + (nz - z) ** 2
                if best is None or d < best[0]:
                    best = (d, nx, nz)
    return (best[1], best[2]) if best else (bx, bz)


def arc_wall_quad(R, thick, a0, a1, height, seg, block="minecraft:quartz_block", yseg=16):
    """H6 思路：每段在俯视图上就是【一个四边形】（内外弧上两端的 4 个点）
       · 顶点吸附到环带内整点，且【相邻段共用同一组顶点】=> 共享边完全重合、无缝
       · 不按水平方块格裁切；只在高度方向每 yseg 分一段"""
    angs = [math.radians(a0 + (a1 - a0) * k / seg) for k in range(seg + 1)]
    outer = [_snap_to_band(R * math.cos(t), R * math.sin(t), R - thick, R) for t in angs]
    inner = [_snap_to_band((R - thick) * math.cos(t), (R - thick) * math.sin(t), R - thick, R) for t in angs]
    entries = []
    for k in range(seg):
        quad = [outer[k], outer[k + 1], inner[k + 1], inner[k]]
        xs = [q[0] for q in quad]
        zs = [q[1] for q in quad]
        x0, x1 = min(xs), max(xs)
        z0, z1 = min(zs), max(zs)
        if x1 <= x0:
            x1 = x0 + 1
        if z1 <= z0:
            z1 = z0 + 1
        offs = []
        for sx in ("min", "max"):
            for sz in ("min", "max"):
                ax = x0 if sx == "min" else x1
                az = z0 if sz == "min" else z1
                tx, tz = min(quad, key=lambda q: (q[0] - ax) ** 2 + (q[1] - az) ** 2)
                dx = tx - ax
                dz = tz - az
                dx = min(0, dx) if sx == "max" else max(0, dx)
                dz = min(0, dz) if sz == "max" else max(0, dz)
                if dx or dz:
                    for sy in ("min", "max"):
                        c = CS8[(sx, sy, sz)]
                        if dx:
                            offs.append((c, "X", dx))
                        if dz:
                            offs.append((c, "Z", dz))
        for ys in range(0, height, yseg):
            ye = min(ys + yseg, height)
            arr = lt_tbox.encode([x0, ys, z0, x1, ye, z1], offs)
            entries.append('[{%s:[I;%s],tile:{block:"%s"}}]' % ("bBox", ",".join(map(str, arr)), block))
    return merge_entries(entries)
