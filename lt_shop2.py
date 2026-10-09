# -*- coding: utf-8 -*-
# lt_shop2.py —— 桥下第一批店铺（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 记忆典当行（B-08~B-09 净跨，可进入）+ 落星零件摊（B-08 门洞）
# 坐标 = bridge2_body.txt 同一原点（px，16px=1格）；输出 pawn_lights / stall_lights / pawn_body / stall_body
# 规则：本体不套结构（常错20）；新件不压桥身/桥灯（常错1）；屋顶距梁底 >=2 格；灯 = 独立 light、每盏在 1 格内
import os, sys, io, re, math, random, hashlib
sys.path.insert(0, os.getcwd())
import numpy as np
import lt_colors
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("需要 Pillow：停下，不要自己装包")

def sha(b): return hashlib.sha256(b).hexdigest()[:16]
def rd(n): return io.open(n, encoding="utf-8", newline="").read()
BODY, BLT = "bridge2_body.txt", "bridge2_lights.txt"
assert sha(rd(BODY).encode("utf-8")) == "53b50e1507509657", "桥身不是已实测版本：停下"
assert sha(rd(BLT).encode("utf-8")) == "466a73593bec83d7", "桥灯不是已实测版本：停下"

NX, NY, NZ = 720, 336, 192
yb = lambda x: 168 + x // 8                       # 梁底，与 lt_bridge2.py 相同

def arrays(t):
    for m in re.finditer(r"\[I;([-\d,]+)\]", t):
        v = [int(a) for a in m.group(1).split(",")]
        if len(v) >= 6:
            yield v[:6]
OCC = np.zeros((NX, NY, NZ), bool)
nb = 0
for n in (BODY, BLT):
    for v in arrays(rd(n)):
        assert min(v[:3]) >= 0 and v[3] <= NX and v[4] <= NY and v[5] <= NZ, "桥盒越界 %s" % v
        OCC[v[0]:v[3], v[1]:v[4], v[2]:v[5]] = True
        nb += 1
print("桥身+桥灯 盒 =", nb, "（对照 4351；可变形盒按外包盒计）")
assert nb == 4351, "桥盒数不符：停下"

NAMES = []
def mid(h, kind="solid"):
    b = lt_colors.fc(h, kind)
    assert isinstance(b, str) and b, "lt_colors.fc 没返回方块名 %s" % h
    if b not in NAMES:
        NAMES.append(b)
    return NAMES.index(b) + 1
C = dict(
    floor=("#2A3038",), shell=("#E6E9EC",), dark=("#1E2329",), steel=("#4F5966",), cab=("#3A424D",),
    louver=("#7A8594",), glass=("#9FE8FF", "trans"), cyan=("#00E5FF", "glow"), mag=("#FF2A6D", "glow"),
    red=("#FF3B2F", "glow"), ledw=("#CFF8FF", "glow"), warm=("#FFC24A", "glow"), amber=("#FFB347", "glow"),
    tin=("#7D8794",), tin2=("#5C6774",), rust=("#6B4A3A",), rust2=("#4A3328",), rust3=("#8A5A2B",),
    ochre=("#A0743A",), soot=("#24201D",), pipe=("#9AA3AD",), cell=("#1B2A6B",), cellg=("#2E3F8A",),
    dish=("#B8BEC4",), olive=("#4A5536",), yellow=("#E8B00F",), black=("#15181C",), orange=("#C8641E",),
    chalk=("#A8A496",),
)
K = {k: mid(*v) for k, v in C.items()}

GP = np.zeros((NX, NY, NZ), np.uint8)             # 典当行本体
GS = np.zeros((NX, NY, NZ), np.uint8)             # 零件摊本体
EX = np.zeros((NX, NY, NZ), bool)                 # 净空豁免（接梁/接墩的线缆）
LAMPS = {"pawn": [], "stall": []}
def box(G, k, x0, y0, z0, x1, y1, z1, ex=False):
    assert 0 <= x0 < x1 <= NX and 0 <= y0 < y1 <= NY and 0 <= z0 < z1 <= NZ, "越界 %s" % ((x0, y0, z0, x1, y1, z1),)
    G[x0:x1, y0:y1, z0:z1] = K[k] if k else 0
    if ex:
        EX[x0:x1, y0:y1, z0:z1] = True
def lamp(grp, name, lv, k, on, v):
    LAMPS[grp].append((name, lv, k, on, v))
def cable(G, k, p0, p1, sag=0, w=2, ex=False):
    n = 2 * max(abs(p1[i] - p0[i]) for i in range(3)) + 1
    pts = []
    for s in range(n + 1):
        u = s / n
        x = int(round(p0[0] + (p1[0] - p0[0]) * u))
        y = int(round(p0[1] + (p1[1] - p0[1]) * u - sag * 4 * u * (1 - u)))
        z = int(round(p0[2] + (p1[2] - p0[2]) * u))
        box(G, k, x, y, z, x + w, y + w, z + w, ex)
        pts.append((x, y, z))
    return pts

def font_path():
    for fn in ("simhei.ttf", "msyh.ttc", "simsun.ttc"):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fn)
        if os.path.exists(p):
            return p
    raise SystemExit("找不到中文字体：停下")
FP = font_path()
def glyph(s, size, rot=0):
    f = ImageFont.truetype(FP, size)
    l, t, r, b = f.getbbox(s)
    img = Image.new("L", (r - l + 4, b - t + 4), 0)
    ImageDraw.Draw(img).text((2 - l, 2 - t), s, font=f, fill=255)
    if rot:
        img = img.rotate(rot, expand=True, fillcolor=0)
    m = np.array(img) > 128
    ys, xs = np.nonzero(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
def fit(s, hmax, wmax, rot=0, smin=6):
    for size in range(24, smin - 1, -1):
        m = glyph(s, size, rot)
        if m.shape[0] <= hmax and m.shape[1] <= wmax:
            return m
    raise AssertionError("字放不下：%s" % s)
def put(G, k, m, o, U):
    """m 行=从上到下、列=观者从左到右；o=观者左下角像素；U=观者右手方向"""
    h, w = m.shape
    for j in range(h):
        for i in range(w):
            if m[j, i]:
                x, y, z = o[0] + U[0] * i, o[1] + h - 1 - j, o[2] + U[2] * i
                assert 0 <= x < NX and 0 <= y < NY and 0 <= z < NZ, "字越界"
                G[x, y, z] = K[k]

# ===================== 记忆典当行 =====================
G = GP
X0, X1, Z0, Z1 = 240, 400, 20, 144
box(G, "floor", X0, 0, Z0, X1, 4, Z1)
box(G, "shell", X0, 4, Z0, X1, 68, Z0 + 4)
box(G, "shell", X0, 4, Z0, X0 + 4, 68, Z1)
box(G, "shell", X1 - 4, 4, Z0, X1, 68, Z1)
box(G, "shell", X0, 68, Z0, X1, 76, Z1)                                   # 一二层楼板
SEG = [(240, 296, 144), (296, 352, 152), (352, 400, 160)]                 # 三段爬坡屋顶
for a, b, top in SEG:
    box(G, "shell", a, top - 8, Z0, b, top, Z1)
    box(G, "shell", a, 76, Z0, b, top - 8, Z0 + 4)
box(G, "shell", X0, 76, Z0, X0 + 4, 136, Z1)
box(G, "shell", X1 - 4, 76, Z0, X1, 152, Z1)
for a, b, top in ((240, 296, 144), (296, 330, 152)):
    box(G, "shell", a, 76, 140, b, top - 8, 144)                          # 二层南墙（西段）
box(G, "shell", 330, 68, 144, 400, 76, 160)                               # 东段外挑 1 格
for a, b, top in ((330, 352, 152), (352, 400, 160)):
    box(G, "shell", a, top - 8, 144, b, top, 160)
    box(G, "shell", a, 76, 156, b, top - 8, 160)
box(G, "shell", 330, 76, 144, 334, 144, 160)
box(G, "shell", 396, 76, 144, 400, 152, 160)
for bx0 in (336, 390):                                                    # 外挑托架
    for t in range(16):
        box(G, "steel", bx0, 36 + 2 * t, 144 + t, bx0 + 4, 39 + 2 * t, 145 + t)
box(G, None, 240, 76, 20, 272, 145, 52)                                   # 西北缺角
box(G, "shell", 272, 76, 20, 276, 136, 52)
box(G, "shell", 240, 76, 52, 272, 136, 56)
box(G, "shell", 240, 76, 20, 242, 80, 52); box(G, "shell", 240, 76, 20, 272, 80, 22)
for a, b in ((240, 248), (276, 280), (312, 316), (336, 340), (366, 370), (390, 400)):
    box(G, "shell", a, 4, 140, b, 68, 144)                                # 一层南立面柱
for a, b in ((248, 276), (316, 336), (340, 366), (370, 390)):
    box(G, "shell", a, 4, 140, b, 10, 144)
    box(G, "glass", a, 10, 141, b, 62, 143)
    box(G, "shell", a, 62, 140, b, 68, 144)
box(G, "shell", 280, 48, 140, 312, 68, 144)                               # 南门 x280~312 y4~48
box(G, "cyan", 278, 4, 144, 280, 48, 145); box(G, "cyan", 312, 4, 144, 314, 48, 145)
box(G, "cyan", 278, 48, 144, 314, 50, 145)
box(G, "shell", 240, 60, 144, 400, 64, 154)                               # 雨棚
box(G, "cyan", 240, 59, 150, 400, 60, 152)
box(G, "dark", 240, 50, 154, 400, 64, 156)                                # 横招牌带
box(G, "cyan", 240, 49, 154, 400, 50, 156)
m = fit("意识备份·抵押·赎回", 12, 152); put(G, "mag", m, (320 - m.shape[1] // 2, 51, 156), (1, 0, 0))
box(G, None, 248, 92, 140, 326, 112, 144); box(G, "glass", 248, 92, 141, 326, 112, 143)
box(G, None, 334, 92, 156, 392, 112, 160); box(G, "glass", 334, 92, 157, 392, 112, 159)
for y in (90, 113):
    box(G, "cyan", 248, y, 144, 326, y + 1, 145); box(G, "cyan", 334, y, 160, 392, y + 1, 161)
box(G, "dark", 278, 76, 144, 318, 89, 145)                                # 门牌
m = fit("B-08/09", 10, 38); put(G, "cyan", m, (298 - m.shape[1] // 2, 78, 145), (1, 0, 0))
box(G, "dark", 244, 72, 144, 248, 142, 174)                               # 西端竖招牌（双面）
box(G, "cyan", 244, 141, 144, 248, 142, 174); box(G, "cyan", 244, 72, 144, 248, 73, 174)
box(G, "cyan", 244, 72, 173, 248, 142, 174)
for k, ch in enumerate("记忆典当"):
    m = fit(ch, 15, 26); h, w = m.shape
    oy = 139 - 17 * k - h + 1
    put(G, "mag", m, (243, oy, 159 - w // 2), (0, 0, 1))                  # 西面：右手 +z
    put(G, "mag", m, (248, oy, 159 + (w - w // 2) - 1), (0, 0, -1))       # 东面：右手 -z
box(G, "cyan", 240, 142, 144, 296, 144, 145); box(G, "cyan", 296, 150, 144, 330, 152, 145)
box(G, "cyan", 330, 150, 160, 352, 152, 161); box(G, "cyan", 352, 158, 160, 400, 160, 161)
box(G, "cyan", 240, 4, 144, 241, 60, 145); box(G, "cyan", 399, 4, 144, 400, 60, 145)
box(G, "cyan", 248, 3, 120, 392, 4, 121)                                  # 大厅地面青线
box(G, "dark", 248, 4, 96, 392, 18, 104); box(G, "shell", 248, 18, 96, 392, 20, 104)   # 柜台
box(G, "cyan", 248, 19, 104, 392, 20, 105)
box(G, "glass", 248, 20, 96, 392, 56, 97); box(G, "cyan", 248, 56, 96, 392, 57, 97)
for a, b in ((248, 288), (290, 318), (320, 348), (350, 392)):
    box(G, None, a + 6, 20, 96, b - 6, 27, 97)                            # 递物口
for x in (288, 318, 348):
    box(G, "glass", x, 20, 96, x + 2, 56, 104)
for cx in (266, 302, 332, 370):                                           # 柜内凳
    box(G, "dark", cx - 3, 4, 84, cx + 3, 16, 90); box(G, "shell", cx - 4, 16, 83, cx + 4, 18, 91)
for k in range(6):                                                        # 抵押舱
    x0 = 250 + 24 * k
    box(G, "dark", x0, 4, 26, x0 + 20, 10, 58)
    box(G, "shell", x0, 10, 26, x0 + 20, 22, 58)
    box(G, None, x0 + 2, 10, 28, x0 + 18, 22, 56)
    box(G, "glass", x0 + 2, 20, 28, x0 + 18, 22, 56)
    for c in ((x0, 21, 26, x0 + 20, 22, 27), (x0, 21, 57, x0 + 20, 22, 58),
              (x0, 21, 26, x0 + 1, 22, 58), (x0 + 19, 21, 26, x0 + 20, 22, 58)):
        box(G, None, *c)
    box(G, "steel", x0 + 6, 4, 24, x0 + 14, 30, 26); box(G, "cyan", x0 + 9, 24, 26, x0 + 11, 26, 27)
    box(G, "cyan", x0 + 2, 9, 58, x0 + 18, 10, 59)
    lamp("pawn", "典当行抵押舱灯%d" % (k + 1), 10, "ledw", k not in (1, 4), [x0 + 8, 11, 40, x0 + 12, 13, 44])
for i, x in enumerate((260, 324, 372)):
    lamp("pawn", "典当行大厅灯%d" % (i + 1), 14, "ledw", True, [x, 64, 118, x + 6, 68, 124])
lamp("pawn", "典当行柜内灯", 12, "ledw", True, [324, 64, 72, 330, 68, 78])
lamp("pawn", "典当行评估室灯", 12, "ledw", True, [324, 138, 72, 330, 142, 78])
for i, x in enumerate((288, 352)):
    lamp("pawn", "典当行雨棚灯%d" % (i + 1), 13, "ledw", True, [x, 56, 146, x + 6, 60, 150])
RP = random.Random(20261011)
for cx in list(range(252, 320, 18)) + list(range(340, 392, 18)):          # 二层数据柜
    box(G, "cab", cx, 76, 100, cx + 14, 124, 116)
    for y in range(80, 122, 5):
        for x in range(cx + 2, cx + 12, 3):
            if RP.random() < 0.6:
                box(G, "cyan" if RP.random() < 0.8 else "mag", x, y, 116, x + 1, y + 1, 117)
box(G, "steel", 252, 144, 64, 288, 146, 100)                              # 冷凝机组底座（屋顶第 1 段）
box(G, "louver", 254, 146, 66, 286, 162, 98)
for x in range(256, 286, 3):
    box(G, "dark", x, 148, 98, x + 1, 160, 99)                            # 百叶
for cx in (262, 278):                                                     # 风扇口青色光环
    box(G, "dark", cx - 5, 162, 77, cx + 5, 163, 87)
    box(G, "cyan", cx - 6, 162, 76, cx + 6, 163, 77); box(G, "cyan", cx - 6, 162, 87, cx + 6, 163, 88)
box(G, "steel", 380, 160, 100, 384, 180, 104)                             # 天线桅杆（屋顶第 3 段）
box(G, "steel", 372, 174, 101, 392, 176, 103); box(G, "red", 381, 180, 101, 383, 182, 103)
cable(G, "cyan", (381, 182, 101), (381, 212, 40), ex=True)                # 数据线上梁、接轨道网青线
box(G, None, 372, 4, 96, 396, 57, 105)                                    # 柜台东头留员工通道

# ===================== 落星零件摊（B-08 门洞，x176~224 / z16~80，地面 = 承台顶 y16）=====================
G = GS
RS = random.Random(20261012)
for z in range(16, 80, 4):                                                # 斜铁皮棚：北高南低，钉在北腿上
    y = 84 - (z - 16) // 4
    for x in range(172, 228, 4):
        box(G, "tin" if (x // 4) % 2 else "tin2", x, y, z, x + 4, y + 2, z + 4)
box(G, "steel", 184, 80, 16, 216, 86, 18)                                 # 铆接角钢
for x in range(188, 214, 6):
    box(G, "pipe", x, 84, 18, x + 2, 86, 19)
for px in (172, 226):                                                     # 歪钢管撑（落在承台外的地面）
    for y in range(0, 70, 4):
        d = y // 18 * (1 if px == 172 else -1)
        box(G, "pipe", px + d, y, 74, px + d + 2, y + 4, 76)
box(G, "cab", 186, 16, 16, 214, 56, 24)                                   # 分格零件柜（靠北腿）
for gx in range(188, 212, 6):
    for gy in range(18, 54, 6):
        box(G, None, gx, gy, 22, gx + 4, gy + 4, 24)
        box(G, RS.choice(("pipe", "orange", "cellg", "dish", "rust3")), gx + 1, gy, 22, gx + 3, gy + 2, 23)
        box(G, "chalk", gx, gy + 4, 23, gx + 4, gy + 5, 24)               # 手写标签
for lx, lz in ((192, 42), (214, 42), (192, 60), (214, 60)):               # 折叠桌
    box(G, "steel", lx, 16, lz, lx + 2, 28, lz + 2)
box(G, "tin2", 190, 28, 40, 218, 30, 64)
for x0, z0, w, d, h in ((193, 43, 10, 8, 1), (204, 45, 11, 7, 2), (196, 53, 9, 9, 1)):   # 烧焦太阳能板
    box(G, "cell", x0, 30, z0, x0 + w, 30 + h, z0 + d)
    for x in range(x0, x0 + w, 3):
        box(G, "cellg", x, 30 + h - 1, z0, x + 1, 30 + h, z0 + d)
    box(G, "soot", x0, 30, z0, x0 + 2, 30 + h, z0 + d); box(G, "soot", x0, 30, z0 + d - 1, x0 + w, 30 + h, z0 + d)
for dy in range(15):                                                      # 半个天线锅（斜靠西侧）
    for dz in range(-14, 15):
        if dy * dy + dz * dz <= 196:
            x = 178 + (dy * dy + dz * dz) // 50
            box(G, "dish", x, 16 + dy, 34 + dz, x + 2, 17 + dy, 35 + dz)
box(G, "steel", 183, 16, 33, 185, 26, 35)
for i, (r, k) in enumerate(((7, "orange"), (6, "black"), (5, "orange"), (4, "black"))):   # 断缆绳头
    for a in range(0, 360, 15):
        x = int(204 + r * math.cos(math.radians(a))); z = int(70 + r * math.sin(math.radians(a)))
        box(G, k, x, 16 + i * 2, z, x + 2, 18 + i * 2, z + 2)
for lx, lz in ((214, 28), (220, 28), (214, 36), (220, 36)):               # 旧折叠椅
    box(G, "olive", lx, 16, lz, lx + 2, 26, lz + 2)
box(G, "olive", 213, 26, 27, 223, 28, 39); box(G, "olive", 221, 28, 27, 223, 40, 39)
box(G, "tin2", 150, 0, 30, 174, 20, 54); box(G, None, 152, 4, 32, 172, 20, 52)   # 撬开的残骸货箱（门洞西侧）
box(G, "cell", 154, 4, 34, 170, 12, 50); box(G, "tin", 146, 0, 28, 148, 22, 56)
m = fit("待熔", 12, 22); put(G, "yellow", m, (162 - m.shape[1] // 2, 5, 54), (1, 0, 0))
box(G, "tin2", 222, 38, 24, 224, 66, 72)                                  # 招牌（朝东：右手 -z）
box(G, "black", 222, 66, 26, 224, 72, 28); box(G, "black", 222, 66, 68, 224, 70, 70)
m = fit("落星零件", 13, 44, rot=4); put(G, "warm", m, (224, 50, 48 + m.shape[1] // 2), (0, 0, -1))
m = fit("熔前价", 8, 30, rot=-3); put(G, "warm", m, (224, 40, 48 + m.shape[1] // 2), (0, 0, -1))
lamp("stall", "落星零件摊灯", 11, "warm", True, [200, 58, 50, 204, 62, 54])
box(G, "black", 201, 62, 51, 203, 78, 53)                                 # 吊灯线
box(G, "steel", 185, 108, 16, 189, 114, 18)                               # 偷电：从北腿光条旁私接
cable(G, "black", (186, 110, 17), (201, 76, 52), sag=8)
pal = [K[k] for k in ("tin", "tin2", "rust", "rust3", "ochre", "soot", "rust2")]
cell = {}
for x, y, z in np.argwhere(np.isin(G, (K["tin"], K["tin2"]))):            # 铁皮随机做旧（3x4 斑块）
    key = (x // 3, y // 4, z // 3)
    if key not in cell:
        cell[key] = RS.choice(pal) if RS.random() < 0.45 else int(G[x, y, z])
    G[x, y, z] = cell[key]

# ===================== 门禁 =====================
for nm, G_ in (("典当行", GP), ("零件摊", GS)):
    hit = np.argwhere((G_ > 0) & OCC)
    assert len(hit) == 0, "%s 与桥重叠 %d 处，例 %s：停下" % (nm, len(hit), hit[:3].tolist())
both = np.argwhere((GP > 0) & (GS > 0))
assert len(both) == 0, "两店互相重叠：停下 %s" % both[:3].tolist()
mask = (GP > 0) & ~EX
gap = 999
for x in range(NX):
    ys = np.nonzero(mask[x].any(axis=1))[0]
    if len(ys):
        g = yb(x) - (int(ys.max()) + 1)
        gap = min(gap, g)
        assert g >= 32, "典当行 x=%d 距梁底只有 %dpx（<2 格）：停下" % (x, g)
print("典当行 距梁底最小净空 = %dpx = %.2f 格" % (gap, gap / 16))
sy = int(np.nonzero((GS > 0).any(axis=(0, 2)))[0].max()) + 1
assert sy <= 120, "零件摊过高 y=%d：停下" % sy
print("零件摊 最高 y = %dpx（门洞灯条在 148）" % sy)
ALL = OCC | (GP > 0) | (GS > 0)
LO = np.zeros_like(OCC)
for grp in LAMPS:
    for nm, lv, k, on, v in LAMPS[grp]:
        assert all(v[i] // 16 == (v[i + 3] - 1) // 16 for i in range(3)), "灯跨格：停下 %s" % nm
        s = (slice(v[0], v[3]), slice(v[1], v[4]), slice(v[2], v[5]))
        assert not ALL[s].any(), "灯与实体重叠：停下 %s" % nm
        assert not LO[s].any(), "灯互相重叠：停下 %s" % nm
        LO[s] = True

# ===================== 导出 =====================
def merge(G_):
    parts, cnt, W = [], 0, np.zeros_like(G_)
    for mi in range(1, len(NAMES) + 1):
        R = (G_ == mi)
        if not R.any():
            continue
        bx = []
        xs = np.nonzero(R.any(axis=(1, 2)))[0]
        for x in range(int(xs[0]), int(xs[-1]) + 1):
            sl = R[x]
            while sl.any():
                y, z = divmod(int(sl.argmax()), NZ)
                r = sl[y, z:]; z2 = z + (len(r) if r.all() else int(r.argmin()))
                y2 = y + 1
                while y2 < NY and sl[y2, z:z2].all():
                    y2 += 1
                x2 = x + 1
                while x2 < NX and R[x2, y:y2, z:z2].all():
                    x2 += 1
                R[x:x2, y:y2, z:z2] = False; W[x:x2, y:y2, z:z2] = mi
                bx.append((x, y, z, x2, y2, z2))
        cnt += len(bx)
        b = ",".join("[I;%d,%d,%d,%d,%d,%d]" % t for t in bx)
        parts.append(('{bBox:%s,tile:{block:"%s"}}' if len(bx) == 1 else '{boxes:[%s],tile:{block:"%s"}}') % (b, NAMES[mi - 1]))
    assert np.array_equal(W, G_), "无损校验失败：停下"
    nz = np.nonzero(G_)
    lo = [int(a.min()) for a in nz]; hi = [int(a.max()) + 1 for a in nz]
    t = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (",".join(parts), *lo, *[hi[i] - lo[i] for i in range(3)], cnt)
    assert "structure:" not in t, "本体出现结构：停下（常错20）"
    return t, cnt, lo, hi
def lights(lst):
    def one(nm, lv, k, on, v):
        return ('[{bBox:[I;%s],tile:{block:"%s"}}]' % (",".join(map(str, v)), NAMES[K[k] - 1]),
                'structure:{id:"light",name:"%s",level:%d,disableRightClick:0b,enabled:{state:%d}}' % (nm, lv, 1 if on else 0))
    lo = [min(l[4][i] for l in lst) for i in range(3)]; hi = [max(l[4][i + 3] for l in lst) for i in range(3)]
    tr, sr = one(*lst[0])
    ch = ",".join("{tiles:%s,%s}" % one(*l) for l in lst[1:])
    return "{tiles:%s,%s%s,min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:1}" % (
        tr, sr, (",children:[%s]" % ch) if ch else "", *lo, *[hi[i] - lo[i] for i in range(3)])
def save(name, s):
    io.open(name, "w", encoding="utf-8", newline="").write(s)
    assert rd(name) == s, "读回不一致：" + name
    print("  %-17s 字节 %7d 结尾完整 %s structure: %2d light %2d sha256 %s" % (
        name, len(s.encode("utf-8")), s.endswith("}"), s.count("structure:"), s.count('id:"light"'), sha(s.encode("utf-8"))))
print("== 输出")
for fn, G_ in (("pawn_body.txt", GP), ("stall_body.txt", GS)):
    t, cnt, lo, hi = merge(G_)
    print("  %s 盒 %d min %s 尺寸 %s 格" % (fn, cnt, lo, [(hi[i] - lo[i]) / 16 for i in range(3)]))
    save(fn, t)
for grp, fn in (("pawn", "pawn_lights.txt"), ("stall", "stall_lights.txt")):
    save(fn, lights(LAMPS[grp]))
    for nm, lv, k, on, v in LAMPS[grp]:
        print("    %s 亮度%d %s 盒%s" % (nm, lv, "开" if on else "关", v))
print("材质 %d 种：%s" % (len(NAMES), "，".join("%s=%s" % (k, NAMES[K[k] - 1]) for k in C)))
print("放置（全程潜行、同一格）：stall_lights → pawn_lights → stall_body → pawn_body → bridge2_lights → bridge2_body")
print("PASS")
