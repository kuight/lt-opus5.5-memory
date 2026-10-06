# lt_probe_j.py —— 样品 J：light(level:0) 当开关 → 它的子结构卷帘门被"信号"开/关
# 结构链：根 fixed "probe_j" → 子0 light(面板, 右键 toggle enabled) → 其子0 advancedDoor(卷帘门, offY 上升 2 格)
#   门的 state 输出写 con:"p.b0" ⇒ 跟父(light)的 enabled 走 ⇒ 右键面板 = 门开/关（LittleDoor.java:176-186 的 SIGNAL 路径）
import io, os, re, math, struct
import numpy as np
import lt_colors, lt_np, lt_root, lt_tree
from lt_colors import fc

OUT = "probe_j.txt"


def F(h, k="solid"): return fc(h, k)


def dbl(v):
    b = struct.unpack(">q", struct.pack(">d", float(v)))[0]; lo = b & 0xFFFFFFFF
    return [b >> 32, lo - (1 << 32) if lo >= 1 << 31 else lo]


def tl_lin(pts):
    a = [0, len(pts)]
    for t, v in pts: a += [t] + dbl(v)
    return "[I;" + ",".join(map(str, a)) + "]"


def vol(sx=128, sy=96, sz=32):
    return lt_np.Vol((sx, sy, sz), (0, 0, 0), (0, 0, 0))


def grab(v, tag, st):
    fn = "_tmp_%s.txt" % re.sub(r"[^0-9A-Za-z_]", "", tag)
    v.export(fn, tag, st)
    t = io.open(fn, encoding="utf-8").read(); os.remove(fn)
    k = lt_root.tiles_end(t)
    tiles = t[t.index("tiles:") + 6:k]
    d, _ = lt_tree.parse_obj(t, 0)
    return tiles, lt_tree.ivec(d["size"])


def node(tiles, st, kids=()):
    s = "{tiles:%s,structure:{%s}" % (tiles, st)
    if kids: s += ",children:[%s]" % ",".join(kids)
    return s + "}"


def trans(tiles, dx, dy, dz):
    """平移：只改前 6 个分量（子结构共用同一绝对空间，必须错开，否则体素重叠）"""
    def r(m):
        a = [int(x) for x in m.group(1).split(",")]
        for i, d in enumerate((dx, dy, dz)):
            a[i] += d; a[i + 3] += d
        return "[I;" + ",".join(map(str, a)) + "]"
    return re.sub(r"\[I;([-\d,]+)\]", r, tiles)

# ---------- 面板（light 开关）：1×1 格、2px 厚，表面 2px 青色 FCB 指示条 ----------
vp = vol(); QZ = vp.M("minecraft:quartz_block"); CY = vp.M(F("#40f0ff", "glow"))
vp.box(QZ, 0, 0, 0, 16, 16, 2)                 # 面板 16×16px（1 格）× 2px 厚
vp.box(CY, 0, 7, 2, 16, 9, 3)                  # 表面 2px 青色指示条（16×2px，贴在 z=2 外侧 1px）
P_T, P_SZ = grab(vp, "probeJ_panel",
                 'id:"light",level:0,enabled:{state:0}')   # 不写 disableRightClick（=默认 false，可右键）

# ---------- 卷帘门：2 格宽 × 2 格高，石英 + 1px 横向分缝 ----------
vd = vol(); QZ2 = vd.M("minecraft:quartz_block")
vd.box(QZ2, 0, 0, 0, 32, 32, 2)                # 门板 32×32px（2×2 格）× 2px 厚
for y in range(4, 32, 4):                      # 每 4px 一道 1px 横向分缝
    vd.box(0, 0, y, 0, 32, y + 1, 2)           # 挖空（=空气）
D_ST = ('id:"advancedDoor",name:"J_卷帘门",duration:40,interpolation:0,activateParent:0b,'
        'disableRightClick:1b,axisCenter:[I;40,16,0,40,16,2,16],'
        'animation:{offGrid:16,offY:%s},'
        'state:{state:0,con:"p.b0",mode:"EQUAL",delay:0}' % tl_lin([(0, 0), (40, 32)]))
D_T, D_SZ = grab(vd, "probeJ_door", D_ST)

# ---------- 组装：根 fixed → light(面板, 也带指示条 at z=2..3) → 门 ----------
LIGHT_KIDS = [node(trans(D_T, 24, 2, 0), D_ST)]   # 门平移 +24px（1.5 格）与 +2px（坐到底座上）
LIGHT_NODE = node(trans(P_T, 0, 2, 0), 'id:"light",level:0,enabled:{state:0}', LIGHT_KIDS)  # 面板也 +2px

node_txt = LIGHT_NODE
ROOT_T = '[{bBox:[I;0,0,0,56,2,3],tile:{block:"minecraft:concrete:15"}}]'   # 根自带 2px 底座（避免空 tiles）
all_txt = ROOT_T + node_txt
b = [[int(v) for v in m.split(",")][:6] for m in re.findall(r"\[I;([-\d,]+)\]", all_txt)
     if len(m.split(",")) in (6, 7, 11)]          # 只认盒子（6/7/11 分量），排除关键帧等 }8 分量数组
lo = [min(x[i] for x in b) for i in range(3)]
hi = [max(x[i + 3] for x in b) for i in range(3)]
# 根 tiles 空列表（所有几何都在子结构里）；count = 根盒子数 = 0
txt = ('{tiles:%s,structure:{id:"fixed",name:"probe_j"},children:[%s],min:[I;%d,%d,%d],'
       'size:[I;%d,%d,%d],count:1}' % (ROOT_T, node_txt, *lo, *[hi[i] - lo[i] for i in range(3)]))
txt = lt_root.fix(txt, "probe_j", tag=OUT)
io.open(OUT, "w", encoding="utf-8").write(txt)

print("已写出 %s：%d 字节" % (OUT, len(txt.encode("utf-8"))))
print("导入起点（根 min 角所在格）= (%d, %d, %d)   总体尺寸 = %.2f × %.2f × %.2f 格"
      % (lo[0] // 16, lo[1] // 16, lo[2] // 16,
         (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16, (hi[2] - lo[2]) / 16))
print("面板 %s  门 %s   门 offY 0→+32px（=上升 2 格，offGrid:16）" % (P_SZ, D_SZ))
print("门的位置：x %d..%d px（面板东侧 %.1f 格起）" % (24, 24 + 32, 24 / 16))
print("用法：右键面板 → light.enabled 翻转 → 门的 state(con 跟 p.b0) 变化 → activate(SIGNAL) → 门开/关；门本身 disableRightClick:1b 右键无效")
