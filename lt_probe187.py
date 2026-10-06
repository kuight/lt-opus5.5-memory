# lt_probe187.py —— LittleTiles 1.5.87 探针：样品一字排开（间隔 2 格）→ probe_187.txt
# 样品：A 官方 particle_emitter 原文 | B 同 A 但新键名写法 | C 扇叶+stayAnimated | D light 亮度15
#       E 门 state → 灯 | F 自激灯+总开关 | F10 F 的 10 盏灯 | H 1/4 圆柱墙(顶部 4px 倒角) | I 30° 斜板
# 不改 lt_np 主体：只把它当好用的体素阵 + 精简导出器（导到临时文件再抠 tiles）
import io, os, re, struct, math
import numpy as np
import lt_colors, lt_np, lt_root, lt_tree
from lt_colors import fc

OUT = "probe_187.txt"
GAP = 2 * 16          # 样品间隔 2 格
PLATE = 2             # 底座厚 2px


def F(h, k="solid"): return fc(h, k)


def dbl(v):
    b = struct.unpack(">q", struct.pack(">d", float(v)))[0]; lo = b & 0xFFFFFFFF
    return [b >> 32, lo - (1 << 32) if lo >= 1 << 31 else lo]


def tl_lin(pts):      # 线性关键帧：type 0，无附加数据（ValueTimeline.write + LinearTimeline.getAdditionalDataSize=0）
    a = [0, len(pts)]
    for t, v in pts: a += [t] + dbl(v)
    return "[I;" + ",".join(map(str, a)) + "]"


def fbits(x):         # float → int 位模式（11 分量盒尾部 4 个 int 就是 float 位）
    return struct.unpack(">i", struct.pack(">f", float(x)))[0]


def vol(sx=256, sy=96, sz=256):
    return lt_np.Vol((sx, sy, sz), (0, 0, 0), (0, 0, 0))


def grab(v, tag, st):
    """用 Vol.export 导到临时文件，抠出 tiles:[...]（子节点不能带 min/size/count）"""
    fn = "_tmp_%s.txt" % re.sub(r"[^0-9A-Za-z_]", "", tag)
    v.export(fn, tag, st)
    t = io.open(fn, encoding="utf-8").read(); os.remove(fn)
    k = lt_root.tiles_end(t)
    tiles = t[t.index("tiles:") + 6:k]
    d, _ = lt_tree.parse_obj(t, 0)
    return tiles, lt_tree.ivec(d["size"])


def trans(tiles, dx, dy, dz):
    """平移：只改前 6 个分量（7/11 分量盒的切片 id 与 float 尾原样保留）"""
    def r(m):
        a = [int(x) for x in m.group(1).split(",")]
        for i, d in enumerate((dx, dy, dz)):
            a[i] += d; a[i + 3] += d
        return "[I;" + ",".join(map(str, a)) + "]"
    return re.sub(r"\[I;([-\d,]+)\]", r, tiles)


def node(tiles, st, kids=()):
    s = "{tiles:%s,structure:{%s}" % (tiles, st)
    if kids: s += ",children:[%s]" % ",".join(kids)
    return s + "}"


# ===================== 样品内容 =====================

# A 官方 particle_emitter 原文（assets/littletiles/premade/particle_emitter.struct 照抄）
A_T = '[{bBox:[I;0,0,0,1,1,1],tile:{color:-13619152,block:"littletiles:ltcoloredblock"}}]'
A_S = ('ticker:3,speedZ:0.0f,color:-1,speedY:0.1f,speedX:0.0f,texture:"smoke",lifetime:20,facing:4,'
       'tickDelay:10,spread:0.0f,size:0.4f,gravity:0b,growrate:1.0f,id:"particle_emitter",state:0')

# B 同 A，改"新键名写法"（settings 子标签；texture 省略走默认，避免枚举名不合规）
B_S = ('tickDelay:10,tickCount:1,ticker:3,speedY:0.1f,speedX:0.0f,speedZ:0.0f,spread:0.0f,facing:4,'
       'settings:{color:-1,lifetime:20,lifetimeDeviation:5,gravity:0.0f,startSize:0.4f,endSize:0.5f,'
       'sizeDeviation:0.04f,randomColor:0b,collision:1b},id:"particle_emitter"')

# C 扇叶 + stayAnimated:1b
_vc = vol(); _BL = _vc.M(F("#3a3a3a")); _AX = _vc.M(F("#40f0ff", "glow"))
_vc.box(_BL, 26, 0, 22, 48, 2, 26); _vc.box(_BL, 0, 0, 22, 22, 2, 26)
_vc.box(_BL, 22, 0, 26, 26, 2, 48); _vc.box(_BL, 22, 0, 0, 26, 2, 22)
_vc.box(_AX, 23, 0, 23, 25, 3, 25)
C_S = ('id:"advancedDoor",name:"探针C_扇叶",duration:40,interpolation:0,activateParent:0b,'
       'disableRightClick:0b,stayAnimated:1b,axisCenter:[I;23,0,23,25,2,25,16],animation:{rotY:%s}'
       % tl_lin([(0, 0), (40, 360)]))
C_T, C_SZ = grab(_vc, "probeC_fan", C_S)

# D light 结构，亮度 15
_vd = vol(); _QZ = _vd.M("minecraft:quartz_block")
_vd.box(_QZ, 0, 0, 0, 16, 16, 16)
D_S = 'id:"light",level:15,disableRightClick:0b,enabled:{state:1}'
D_T, D_SZ = grab(_vd, "probeD_light", D_S)

# E 门 state 输出 → 灯（灯是门的子结构；灯的 con 用 p.b0 = 父的第 0 号内部输出 = 门的 state）
_ve = vol(); _IR = _ve.M("minecraft:iron_block")
_ve.box(_IR, 0, 0, 8, 16, 32, 10)
E_S = ('id:"advancedDoor",name:"探针E_门",duration:20,interpolation:0,activateParent:0b,'
       'disableRightClick:0b,axisCenter:[I;0,0,8,0,40,10,16],animation:{rotY:%s}'
       % tl_lin([(0, 0), (20, 90)]))
E_T, E_SZ = grab(_ve, "probeE_door", E_S)
_vl = vol(); _QZ2 = _vl.M("minecraft:quartz_block")
_vl.box(_QZ2, 0, 0, 0, 8, 8, 8)
E_L_S = 'id:"light",level:15,disableRightClick:0b,enabled:{state:0,con:"p.b0",mode:"EQUAL",delay:0}'
E_LT, E_LSZ = grab(_vl, "probeE_lamp", E_L_S)
E_NODE = node(E_T, E_S, [node(trans(E_LT, 24, 0, 8), E_L_S)])   # 灯摆在门的东侧 1.5 格、同深度

# F 自激灯 + 总开关（开关=一扇小门，用 /lt-open 切换它的 state；灯 con = !自己 & 父.state）
F_L_S = 'id:"light",level:15,disableRightClick:0b,enabled:{state:0,con:"!b0&p.b0",mode:"EQUAL",delay:10}'


def sw(name):
    v = vol(); S = v.M("minecraft:iron_block")
    v.box(S, 0, 0, 0, 8, 24, 2)
    st = ('id:"advancedDoor",name:"%s",duration:10,interpolation:0,activateParent:0b,'
          'disableRightClick:0b,axisCenter:[I;0,0,0,0,32,2,16],animation:{rotY:%s}'
          % (name, tl_lin([(0, 0), (10, 90)])))
    t, sz = grab(v, name, st)
    return t, st, sz


FS_T, FS_S, FS_SZ = sw("probeF_switch")
_vl2 = vol(); _QZ3 = _vl2.M("minecraft:quartz_block")
_vl2.box(_QZ3, 0, 0, 0, 8, 8, 8)
FL_T, FL_SZ = grab(_vl2, "probeF_lamp", F_L_S)
F_NODE = node(FS_T, FS_S, [node(FL_T, F_L_S)])
F10_NODE = node(FS_T, FS_S, [node(FL_T, F_L_S) for _ in range(10)])

# H 1/4 圆柱墙：R=8 格(128px)、高 4 格(64px)、壳厚 2px、石英、顶部 R=4px 倒角
_vh = vol(256, 96, 256); _QZH = _vh.M("minecraft:quartz_block")
R_OUT, R_IN, HH = 128, 126, 64
for _x in range(R_OUT + 1):
    for _z in range(R_OUT + 1):
        _d = math.hypot(_x + 0.5, _z + 0.5)
        for _y in range(HH):
            if _y < HH - 4:
                _rout = R_OUT
            else:
                _t = (_y - (HH - 4)) + 0.5
                _rout = (R_OUT - 4) + math.sqrt(max(0.0, 16.0 - _t * _t))
            if R_IN <= _d <= _rout:
                _vh.px(_QZH, _x, _y, _z)
H_S = 'id:"fixed",name:"探针H_曲面"'
H_T, H_SZ = grab(_vh, "probeH_curved", H_S)
H_BOXES = sum(len(rs) for _, rs, _ in lt_tree.entries(H_T))

# I 3×3 格 30° 斜板：11 分量可变形盒 = [6 坐标, slice id, 4 个 float 位(startOne,startTwo,endOne,endTwo)]
SLICE_ID = 24
_tan30 = math.tan(math.radians(30.0)) * 48.0
I_T = ('[{bBox:[I;0,0,0,48,2,48,%d,%d,%d,%d,%d],tile:{block:"minecraft:quartz_block"}}]'
       % (SLICE_ID, fbits(0.0), fbits(0.0), fbits(48.0), fbits(_tan30)))
I_S = 'id:"fixed",name:"探针I_斜板"'

# ===================== 排版：一字排开 =====================
# (标签, 节点模板, 自身宽px, 深px, 子节点要额外右移的px)
LAYOUT = [
    ("A 官方粒子", ('tiles', A_T, A_S, []), 16, 16),
    ("B 新键粒子", ('tiles', A_T, B_S, []), 16, 16),
    ("C 扇叶", ('tiles', C_T, C_S, []), C_SZ[0], C_SZ[2]),
    ("D 灯15", ('tiles', D_T, D_S, []), D_SZ[0], D_SZ[2]),
    ("E 门→灯", ('node', E_NODE, None, []), 40, max(E_SZ[2], 24)),
    ("F 自激", ('tiles', FS_T, FS_S, [(FL_T, F_L_S)]), FS_SZ[0] + 16 + FL_SZ[0], max(FS_SZ[2], 16)),
    ("F10 十盏", ('tiles', FS_T, FS_S, [(FL_T, F_L_S)] * 10), FS_SZ[0] + 16 + 10 * (FL_SZ[0] + 8), max(FS_SZ[2], 16)),
    ("H 曲面", ('tiles', H_T, H_S, []), H_SZ[0], H_SZ[2]),
    ("I 斜板", ('tiles', I_T, I_S, []), 48, 48),
]

cursor = 0
kids_out, plates, table = [], [], []
for lab, spec, w, d in LAYOUT:
    kind, t, st, kl = spec
    if kind == 'node':                      # t 已是完整节点（含自己的 children）
        nt = trans(t, cursor, PLATE, 0)
    else:
        kids = []
        for i, (kt, kst) in enumerate(kl):
            dx = FS_SZ[0] + 16 + (i * (FL_SZ[0] + 8) if len(kl) > 1 else 0)
            kids.append(node(trans(kt, cursor + dx, PLATE, 0), kst))
        nt = node(trans(t, cursor, PLATE, 0), st, kids)
    kids_out.append(nt)
    plates.append("[I;%d,0,0,%d,%d,%d]" % (cursor, cursor + w, PLATE, d))
    table.append((lab, cursor, cursor // 16, w, d))
    cursor += w + GAP
total_w = cursor - GAP
depth = max(p[4] for p in table)

ROOT_T = '[{boxes:[%s],tile:{block:"minecraft:concrete:15"}}]' % ",".join(plates)
all_txt = ROOT_T + "".join(kids_out)
allbox = [[int(v) for v in m.split(",")][:6] for m in re.findall(r"\[I;([-\d,]+)\]", all_txt)
          if len(m.split(",")) in (6, 7, 11)]     # 只认盒子，排除关键帧等 8 分量数组
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
print("根盒子数 %d（底座板）  样品 %d 个  间隔 %d 格  底座深 %dpx" % (n_root, len(LAYOUT), GAP // 16, depth))
print("H 曲面：SDF 体素化 + 贪心合并后盒子数 = %d" % H_BOXES)
print("I 斜板：11 分量盒 slice=%d，float位=(%d,%d,%d,%d) 即 (0.0, 0.0, 48.0, %.2f)"
      % (SLICE_ID, fbits(0.0), fbits(0.0), fbits(48.0), fbits(_tan30), _tan30))
print("--- 样品排布（从西往东）---")
for lab, xpx, xcell, w, d in table:
    print("   %-10s x=%5dpx (%4d格) 宽%4dpx 深%4dpx" % (lab, xpx, xcell, w, d))
