# lt_probe187.py —— LittleTiles 1.5.87 探针：样品一字排开（间隔 2 格）→ probe_187.txt
# ★ 修法 A（修正版）：样品在**局部坐标**生成，导出后**只对 tiles 段**做一次平移（tiles 里只可能有
#   6/7/11 分量的盒子数组，且带断言）；**structure 文本一律不碰** ⇒ 时间轴 / axisCenter 不再被污染。
#   旧版 trans() 会盲改整节点里所有 [I;…] → animation.rotY 首元素被加成 224 → 游戏内
#   RuntimeException: Invalid id 224（放置时崩）。该函数已删除，且 lt_tree 现在有守卫能拦住。
# 注意：lt_np.Vol.export 会把坐标归一化到【内容最小角所在的格】(lt_np.py:24/41 base=lo//16*16)，
#   所以"直接生成在最终坐标"必须补这一步 tiles 级平移才能与结构里的 axisCenter 对齐。
# 样品：A 官方 particle_emitter | B 新键名粒子 | C 扇叶+stayAnimated | D light15 | E 门 state→灯
#       F 自激灯+总开关 | F10 十盏灯 | H 1/4 圆柱曲面(209 盒) | I 30° 斜板(11 分量盒)
import io, os, re, struct, math
import numpy as np
import lt_colors, lt_np, lt_root, lt_tree
from lt_colors import fc

OUT = "probe_187.txt"
GAP = 32              # 样品间隔 2 格
PLATE = 2             # 底座厚 2px

LAYOUT = [("A", "官方 particle_emitter 原文", 16, 16, 16),
          ("B", "新键名 particle_emitter", 16, 16, 16),
          ("C", "扇叶 + stayAnimated:1b", 48, 48, 8),
          ("D", "light level:15", 16, 16, 16),
          ("E", "门 state → 灯", 40, 24, 40),
          ("F", "自激灯 + 总开关", 32, 16, 30),
          ("F10", "F 的 10 盏自激灯", 184, 16, 30),
          ("H", "1/4 圆柱曲面", 128, 128, 70),
          ("I", "30° 斜板（11 分量盒）", 48, 48, 8)]


def F(h, k="solid"): return fc(h, k)


def dbl(v):
    b = struct.unpack(">q", struct.pack(">d", float(v)))[0]; lo = b & 0xFFFFFFFF
    return [b >> 32, lo - (1 << 32) if lo >= 1 << 31 else lo]


def tl_lin(pts):      # 线性关键帧：type=0，附加 0 个 → [0, count, (tick,hi32,lo32)×count]
    a = [0, len(pts)]
    for t, v in pts: a += [t] + dbl(v)
    return "[I;" + ",".join(map(str, a)) + "]"


def fbits(x):
    return struct.unpack(">i", struct.pack(">f", float(x)))[0]


def shift_tiles(tiles, dx, dy, dz):
    """只平移 **tiles 段**（该段只允许出现 6/7/11 分量的盒子数组；出现别的 int 数组立刻断言失败）。
    —— 这就是"禁止盲改 int 数组"的合规做法：作用域被限定 + 有断言保护。"""
    def r(m):
        a = [int(x) for x in m.group(1).split(",")]
        assert len(a) in (6, 7, 11), "tiles 段出现非盒子 int 数组（%d 分量）: %s" % (len(a), a)
        for i, dd in enumerate((dx, dy, dz)):
            a[i] += dd; a[i + 3] += dd
        return "[I;" + ",".join(map(str, a)) + "]"
    return re.sub(r"\[I;([-\d,]+)\]", r, tiles)


class Part:
    """局部坐标生成；tiles() 导出后按 (xo,yo,0) 精确落位（结构文本不参与平移）"""
    def __init__(self, xo, yo, w, h, d):
        self.v = lt_np.Vol((w + 8, h + 8, d + 8), (0, 0, 0), (0, 0, 0))
        self.xo, self.yo = xo, yo
    def M(self, b): return self.v.M(b)
    def box(self, m, x1, y1, z1, x2, y2, z2): self.v.box(m, x1, y1, z1, x2, y2, z2)
    def px(self, m, x, y, z): self.v.px(m, x, y, z)
    def tiles(self, tag, st):
        fn = "_tmp_%s.txt" % re.sub(r"[^0-9A-Za-z_]", "", tag)
        self.v.export(fn, tag, st)
        t = io.open(fn, encoding="utf-8").read(); os.remove(fn)
        k = lt_root.tiles_end(t)
        return shift_tiles(t[t.index("tiles:") + 6:k], self.xo, self.yo, 0)


def node(tiles, st, kids=()):
    s = "{tiles:%s,structure:{%s}" % (tiles, st)
    if kids: s += ",children:[%s]" % ",".join(kids)
    return s + "}"


# ===================== 排版（先算每样品 xo）=====================
X = {}
cur = 0
for nm, lab, w, d, h in LAYOUT:
    X[nm] = cur
    cur += w + GAP
TOTAL = cur - GAP
XO, YO = X, {nm: PLATE for nm, *_ in LAYOUT}

# ===================== A / B：particle_emitter =====================
AB_T = '[{bBox:[I;%d,%d,0,%d,%d,1],tile:{color:-13619152,block:"littletiles:ltcoloredblock"}}]'
A_T = AB_T % (0, 0, 1, 1)
B_T = AB_T % (0, 0, 1, 1)                      # 局部坐标，稍后用 shift_tiles 落位
A_S = ('ticker:3,speedZ:0.0f,color:-1,speedY:0.1f,speedX:0.0f,texture:"smoke",lifetime:20,facing:4,'
       'tickDelay:10,spread:0.0f,size:0.4f,gravity:0b,growrate:1.0f,id:"particle_emitter",state:0')
B_S = ('tickDelay:10,tickCount:1,ticker:3,speedY:0.1f,speedX:0.0f,speedZ:0.0f,spread:0.0f,facing:4,'
       'settings:{color:-1,lifetime:20,lifetimeDeviation:5,gravity:0.0f,startSize:0.4f,endSize:0.5f,'
       'sizeDeviation:0.04f,randomColor:0b,collision:1b},id:"particle_emitter"')
A_T = shift_tiles(A_T, XO["A"], PLATE, 0)
B_T = shift_tiles(B_T, XO["B"], PLATE, 0)

# ===================== C：扇叶 + stayAnimated =====================
c = Part(XO["C"], PLATE, 48, 8, 48)
BL, AX = c.M(F("#3a3a3a")), c.M(F("#40f0ff", "glow"))
c.box(BL, 26, 0, 22, 48, 2, 26); c.box(BL, 0, 0, 22, 22, 2, 26)
c.box(BL, 22, 0, 26, 26, 2, 48); c.box(BL, 22, 0, 0, 26, 2, 22)
c.box(AX, 23, 0, 23, 25, 3, 25)
C_AC = [XO["C"] + 24, PLATE, 24, XO["C"] + 24, PLATE + 2, 24, 16]      # 竖轴：x/z 0 宽、y 2px(偶)
C_S = ('id:"advancedDoor",name:"探针C_扇叶",duration:40,interpolation:0,activateParent:0b,'
       'disableRightClick:0b,stayAnimated:1b,axisCenter:[I;%s],animation:{rotY:%s}'
       % (",".join(map(str, C_AC)), tl_lin([(0, 0), (40, 360)])))
C_T = c.tiles("probeC_fan", C_S)

# ===================== D：light level:15 =====================
d = Part(XO["D"], PLATE, 16, 16, 16)
d.box(d.M("minecraft:quartz_block"), 0, 0, 0, 16, 16, 16)
D_S = 'id:"light",level:15,disableRightClick:0b,enabled:{state:1}'
D_T = d.tiles("probeD_light", D_S)

# ===================== E：门 state → 灯 =====================
e = Part(XO["E"], PLATE, 40, 40, 24)
e.box(e.M("minecraft:iron_block"), 0, 0, 8, 16, 32, 10)                 # 门板 1 格宽 × 2 格高
E_AC = [XO["E"], PLATE, 9, XO["E"], PLATE + 32, 9, 16]                  # 铰链 = 左边缘竖线
E_S = ('id:"advancedDoor",name:"探针E_门",duration:20,interpolation:0,activateParent:0b,'
       'disableRightClick:0b,axisCenter:[I;%s],animation:{rotY:%s}'
       % (",".join(map(str, E_AC)), tl_lin([(0, 0), (20, 90)])))
E_T = e.tiles("probeE_door", E_S)
el = Part(XO["E"] + 24, PLATE, 8, 8, 8)
el.box(el.M("minecraft:quartz_block"), 0, 0, 0, 8, 8, 8)
E_L_S = 'id:"light",level:15,disableRightClick:0b,enabled:{state:0,con:"p.b0",mode:"EQUAL",delay:0}'
E_L_T = el.tiles("probeE_lamp", E_L_S)
E_NODE = node(E_T, E_S, [node(E_L_T, E_L_S)])

# ===================== F / F10 =====================
F_L_S = 'id:"light",level:15,disableRightClick:0b,enabled:{state:0,con:"!b0&p.b0",mode:"EQUAL",delay:10}'


def make_switch(xo, tag):
    s = Part(xo, PLATE, 8, 30, 2)
    s.box(s.M("minecraft:iron_block"), 0, 0, 0, 8, 24, 2)
    ac = [xo, PLATE, 1, xo, PLATE + 24, 1, 16]
    st = ('id:"advancedDoor",name:"%s",duration:10,interpolation:0,activateParent:0b,'
          'disableRightClick:0b,axisCenter:[I;%s],animation:{rotY:%s}'
          % (tag, ",".join(map(str, ac)), tl_lin([(0, 0), (10, 90)])))
    return s.tiles(tag, st), st


def make_lamp(xo, tag):
    l = Part(xo, PLATE, 8, 8, 8)
    l.box(l.M("minecraft:quartz_block"), 0, 0, 0, 8, 8, 8)
    return l.tiles(tag, F_L_S)


F_S_T, F_S_S = make_switch(XO["F"], "probeF_switch")
F10_S_T, F10_S_S = make_switch(XO["F10"], "probeF10_switch")
F_NODE = node(F_S_T, F_S_S, [node(make_lamp(XO["F"] + 24, "probeF_lamp"), F_L_S)])
F10_NODE = node(F10_S_T, F10_S_S,
                [node(make_lamp(XO["F10"] + 24 + i * 16, "probeF10_lamp%d" % i), F_L_S) for i in range(10)])

# ===================== H：1/4 圆柱曲面 =====================
h = Part(XO["H"], PLATE, 128, 70, 128)
QZH = h.M("minecraft:quartz_block")
R_OUT, R_IN, HH = 128, 126, 64
for _x in range(R_OUT + 1):
    for _z in range(R_OUT + 1):
        _dd = math.hypot(_x + 0.5, _z + 0.5)
        for _y in range(HH):
            if _y < HH - 4:
                _rout = R_OUT
            else:
                _t = (_y - (HH - 4)) + 0.5
                _rout = (R_OUT - 4) + math.sqrt(max(0.0, 16.0 - _t * _t))
            if R_IN <= _dd <= _rout:
                h.px(QZH, _x, _y, _z)
H_S = 'id:"fixed",name:"探针H_曲面"'
H_T = h.tiles("probeH_curved", H_S)
H_BOXES = sum(len(rs) for _, rs, _ in lt_tree.entries(H_T))

# ===================== I：30° 斜板（11 分量盒）=====================
SLICE_ID = 24
_tan30 = math.tan(math.radians(30.0)) * 48.0
I_T = ('[{bBox:[I;%d,%d,0,%d,%d,48,%d,%d,%d,%d,%d],tile:{block:"minecraft:quartz_block"}}]'
       % (0, 0, 48, 2, SLICE_ID, fbits(0.0), fbits(0.0), fbits(48.0), fbits(_tan30)))
I_T = shift_tiles(I_T, XO["I"], PLATE, 0)
I_S = 'id:"fixed",name:"探针I_斜板"'

# ===================== 组装根（底座板按 LAYOUT 顺序生成）=====================
SAMP = {"A": node(A_T, A_S), "B": node(B_T, B_S), "C": node(C_T, C_S), "D": node(D_T, D_S),
        "E": E_NODE, "F": F_NODE, "F10": F10_NODE, "H": node(H_T, H_S), "I": node(I_T, I_S)}
ORDER = [nm for nm, *_ in LAYOUT]
kids_out = [SAMP[nm] for nm in ORDER]
plates = ["[I;%d,0,0,%d,%d,%d]" % (X[nm], X[nm] + w, PLATE, dd) for nm, lab, w, dd, hh in LAYOUT]
ROOT_T = '[{boxes:[%s],tile:{block:"minecraft:concrete:15"}}]' % ",".join(plates)


def collect_boxes(text):
    """只在 bBox:/boxes: 位置取数组（不盲扫 [I;…]）"""
    out = []
    for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', text):
        out.append([int(x) for x in m.group(1).split(",")][:6])
    for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', text, re.S):
        for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            out.append([int(x) for x in mm.group(1).split(",")][:6])
    return out


all_txt = ROOT_T + "".join(kids_out)
allbox = collect_boxes(all_txt)
lo = [min(b[i] for b in allbox) for i in range(3)]
hi = [max(b[i + 3] for b in allbox) for i in range(3)]
n_root = sum(len(rs) for _, rs, _ in lt_tree.entries(ROOT_T))
txt = ('{tiles:%s,structure:{id:"fixed",name:"probe187"},children:[%s],min:[I;%d,%d,%d],'
       'size:[I;%d,%d,%d],count:%d}'
       % (ROOT_T, ",".join(kids_out), *lo, *[hi[i] - lo[i] for i in range(3)], n_root))
txt = lt_root.fix(txt, "probe187", tag=OUT)
io.open(OUT, "w", encoding="utf-8").write(txt)

print("已写出 %s：%d 字节" % (OUT, len(txt.encode("utf-8"))))
print("导入起点（根 min 角所在格）= (%d, %d, %d)   总体尺寸 = %.2f × %.2f × %.2f 格"
      % (lo[0] // 16, lo[1] // 16, lo[2] // 16,
         (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16, (hi[2] - lo[2]) / 16))
print("根底座 %d 块地板；样品 %d 个；H 曲面盒数 %d" % (n_root, len(ORDER), H_BOXES))
print("\n--- 排版 / 关键数组数值（供复核）---")
print("%-4s %-24s %-8s %-26s %s" % ("样品", "内容", "xo(px)", "axisCenter", "时间轴"))
for nm, lab, w, dd, hh in LAYOUT:
    body = SAMP[nm]
    ac = re.search(r'axisCenter:\[I;([-\d,]+)\]', body)
    tls = [(m.group(1), m.group(2)) for m in re.finditer(r'(rot[XYZ]|off[XYZ]):\[I;([-\d,]+)\]', body)]
    print("%-4s %-24s %-8d %-26s %s" % (nm, lab, X[nm],
          ("[" + ac.group(1) + "]") if ac else "—",
          "；".join("%s=[%s]" % (k, v) for k, v in tls) if tls else "—"))