# lt_mass.py —— 天梯城 体块模型 v0 → mass_v0.schematic（MCEdit/Alpha：gzip 压缩 NBT，手写 struct+gzip）
#   坐标：i=x+800 (0..99)，k=z-300 (0..99)，y=3..255 → Width=100(X) Height=253 Length=100(Z)
#   下标 (y*Length + z)*Width + x；Materials="Alpha"；空气=0（//paste 用于清场）
#   另出 mass_v0_top.png（俯视高度图+网格）、mass_v0_sec.png（i=k 对角线立面剖面）、25×25 ASCII 高度图
import gzip, io, math, struct
import numpy as np
from PIL import Image, ImageDraw

W = L = 100
Y0, Y1 = 3, 255
HGT = Y1 - Y0 + 1
OY = Y0

AIR, STONE, GRASS, GLASS, CONCRETE, GOLD = 0, 1, 2, 95, 251, 41
def C(d): return (CONCRETE, d)
SGL = lambda d: (GLASS, d)

blocks = np.zeros((HGT, L, W), np.uint8)      # [y-Y0, k, i]
mdata = np.zeros((HGT, L, W), np.uint8)


def setb(i, y, k, bd):
    if 0 <= i < W and 0 <= k < L and Y0 <= y <= Y1:
        blocks[y - OY, k, i], mdata[y - OY, k, i] = bd


def carve(i, y, k):
    setb(i, y, k, (AIR, 0))


def box(i1, y1, k1, i2, y2, k2, bd):
    for i in range(max(0, i1), min(W, i2 + 1)):
        for k in range(max(0, k1), min(L, k2 + 1)):
            for y in range(max(Y0, y1), min(Y1, y2) + 1):
                setb(i, y, k, bd)


# ---------------- 地形 ----------------
def terrain(i, k):
    s = (i - k) / math.sqrt(2)
    d = (i + k - 99) / math.sqrt(2) - 4 * math.sin(2 * math.pi * s / 70)
    d1, d2 = math.hypot(i - 33, k - 33), math.hypot(i - 66, k - 66)
    cx, cz, peak = (33, 33, 110) if d1 <= d2 else (66, 66, 100)
    r = min(d1, d2)
    th = math.atan2(k - cz, i - cx)
    R = 46 * (1 + 0.15 * math.sin(3 * th) + 0.08 * math.sin(5 * th + 1))
    hm = 3 if r > R else 3 + (peak - 3) * (1 - (r / R) ** 2)
    hc = 30.0 if abs(d) <= 6 else 30 + (abs(d) - 6) * 8
    h = min(hm, hc)
    if h < 30:
        return h
    return 30 + 10 * math.floor((h - 30) / 10)


hh = np.zeros((L, W))
for k in range(L):
    for i in range(W):
        hh[k, i] = terrain(i, k)

for k in range(L):
    for i in range(W):
        h = int(hh[k, i])
        for y in range(Y0, h + 1):
            setb(i, y, k, (STONE, 0))
        if h == 3:
            setb(i, h, k, (GRASS, 0))
        else:
            setb(i, h, k, C(8))
        cliff = False
        for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nk = i + di, k + dk
            if 0 <= ni < W and 0 <= nk < L and abs(h - int(hh[nk, ni])) >= 5:
                cliff = True
                for y in range(min(h, int(hh[nk, ni])) + 1, h + 1):
                    setb(i, y, k, C(7))
        if cliff and h > 3:
            setb(i, h, k, C(7))

# ---------------- 天梯（中心 i=65,k=65）----------------
CX = CZ = 65.0
box(51, 100, 51, 79, 102, 79, C(0))                       # 山顶平台 半径14 圆盘（先铺方，再削圆）
for i in range(51, 80):
    for k in range(51, 80):
        if math.hypot(i - CX, k - CZ) > 14:
            for y in range(100, 103): carve(i, y, k)
for y in range(102, Y1 + 1):                              # 三主塔
    rad = 3 + (1.5 - 3) * (y - 102) / (Y1 - 102)
    for az in (90, 210, 330):
        a = math.radians(az)
        px, pz = CX + 9 * math.cos(a), CZ + 9 * math.sin(a)
        for i in range(int(px - 4), int(px + 5)):
            for k in range(int(pz - 4), int(pz + 5)):
                if math.hypot(i - px, k - pz) <= rad:
                    setb(i, y, k, C(0))
for y in (140, 170, 200, 230):                            # 环梁 环半径9 管半径1
    for i in range(int(CX - 11), int(CX + 12)):
        for k in range(int(CZ - 11), int(CZ + 12)):
            if abs(math.hypot(i - CX, k - CZ) - 9) <= 1:
                setb(i, y, k, C(0))
for y in range(102, Y1 + 1):                              # 中心缆束 半径1.5，交替 concrete:0 / stained_glass:9
    bd = C(0) if y % 2 == 0 else SGL(9)
    for i in range(int(CX - 2), int(CX + 3)):
        for k in range(int(CZ - 2), int(CZ + 3)):
            if math.hypot(i - CX, k - CZ) <= 1.5:
                setb(i, y, k, bd)
for i in range(int(CX - 15), int(CX + 16)):               # 对接环占位 y=200 环半径13 管半径1.5
    for k in range(int(CZ - 15), int(CZ + 16)):
        if abs(math.hypot(i - CX, k - CZ) - 13) <= 1.5:
            setb(i, 200, k, C(4))
for n in range(6):                                        # 发射塔 6 根 半径1 y102~140
    a = math.radians(30 + 60 * n)
    px, pz = CX + 13 * math.cos(a), CZ + 13 * math.sin(a)
    for i in range(int(px - 2), int(px + 3)):
        for k in range(int(pz - 2), int(pz + 3)):
            if math.hypot(i - px, k - pz) <= 1:
                for y in range(102, 141): setb(i, y, k, C(7))

# ---------------- 民城山穿楼塔（圆角方形 |u/a|^4+|v/a|^4≤1，a=5，每 20 格 a-=0.7）----------------
TOWERS = [((25, 20), 170), ((40, 35), 150), ((15, 45), 160), ((52, 14), 145)]
for (ti, tk), top in TOWERS:
    base = int(hh[tk, ti])
    for y in range(base, top + 1):
        a = 5 - 0.7 * ((y - base) // 20)
        if a <= 0.5: break
        for i in range(ti - 6, ti + 7):
            for k in range(tk - 6, tk + 7):
                u, v = abs((i - ti) / a), abs((k - tk) / a)
                if u ** 4 + v ** 4 <= 1:
                    setb(i, y, k, C(0))

# ---------------- 线路 ----------------
def seg_dist(i, k, p, q):
    (x1, z1), (x2, z2) = p, q
    dx, dz = x2 - x1, z2 - z1
    t = ((i - x1) * dx + (k - z1) * dz) / max(1e-9, dx * dx + dz * dz)
    t = max(0.0, min(1.0, t))
    return math.hypot(i - (x1 + t * dx), k - (z1 + t * dz)), t


MAGLEV = [((56, 58), (40, 35)), ((40, 35), (15, 45))]     # 磁浮：3宽×2高梁 y=120，concrete:4
for i in range(W):
    for k in range(L):
        dmin = min(seg_dist(i, k, p, q)[0] for p, q in MAGLEV)
        if dmin <= 1.5:
            for y in (120, 121): setb(i, y, k, C(4))
# 穿塔通道：在 (40,35) 塔身里挖 5×4
for i in range(W):
    for k in range(L):
        d = seg_dist(i, k, (56, 58), (40, 35))[0]
        if d <= 2.5 and math.hypot(i - 40, k - 35) <= 7:
            for y in range(119, 123): carve(i, y, k)

CORR = [(25, 20), (15, 45)]                               # 水晶连廊 y=140，3宽×3高：玻璃壳 + concrete:0 地板
for i in range(W):
    for k in range(L):
        if seg_dist(i, k, CORR[0], CORR[1])[0] <= 1.5:
            for di in (-1, 0, 1):
                for dk in (-1, 0, 1):
                    if di == 0 and dk == 0: continue           # 中心留空（通道）
                    for y in range(140, 143):
                        setb(i + di, y, k + dk, C(0) if y == 140 else SGL(0))

SROPE = ((30, 50, 70), (72, 40, 80))
for i in range(W):
    for k in range(L):
        d, t = seg_dist(i, k, (SROPE[0][0], SROPE[0][1]), (SROPE[1][0], SROPE[1][1]))
        if d <= 0.6:
            yy = int(round(SROPE[0][2] + (SROPE[1][2] - SROPE[0][2]) * t - 6 * 4 * t * (1 - t)))
            setb(i, yy, k, C(4))                              # 索道 concrete:4

def canyon_walls(s0):
    """在 i-k=s0 处，沿 (1,1) 方向（垂直于峡谷中线）找两侧崖壁：|d|>6.5 的第一列"""
    out = []
    base = ((s0 + 99) / 2.0, (99 - s0) / 2.0)             # i+k=99, i-k=s0
    for sign in (1, -1):
        for step in range(1, 40):
            i = int(round(base[0] + sign * step / math.sqrt(2)))
            k = int(round(base[1] + sign * step / math.sqrt(2)))
            if 0 <= i < W and 0 <= k < L:
                s = (i - k) / math.sqrt(2)
                d = (i + k - 99) / math.sqrt(2) - 4 * math.sin(2 * math.pi * s / 70)
                if abs(d) > 6.5:
                    out.append((i, k)); break
    return out

for s0 in (-12, 0, 12):                                   # 能网：y60 三根悬链线跨峡谷（下垂 4）
    w = canyon_walls(s0)
    if len(w) == 2:
        for i in range(W):
            for k in range(L):
                d, t = seg_dist(i, k, w[0], w[1])
                if d <= 0.6:
                    setb(i, int(round(60 - 4 * 4 * t * (1 - t))), k, C(14))
for i, k in canyon_walls(0):                              # 能网：两侧崖壁 2×2 立柱 y30~80
    for di in (0, 1):
        for dk in (0, 1):
            for y in range(30, 81): setb(i + di, y, k + dk, C(14))
for s0 in range(-48, 49, 4):                              # 光瀑：崖壁外表面每 4 格一根 1 格粗竖线
    w = canyon_walls(s0)
    for i, k in w:
        h = int(hh[k, i])
        for y in range(30, h + 1): setb(i, y, k, SGL(9))

# ---------------- 写 schematic（MCEdit Alpha）----------------
def nbt_str(s):
    b = s.encode("utf-8"); return struct.pack(">H", len(b)) + b
def tag_short(n, v): return b"\x02" + nbt_str(n) + struct.pack(">h", v)
def tag_int(n, v): return b"\x03" + nbt_str(n) + struct.pack(">i", v)
def tag_str(n, v): return b"\x08" + nbt_str(n) + nbt_str(v)
def tag_byte_array(n, arr):
    b = bytes(int(x) & 0xFF for x in arr)
    return b"\x07" + nbt_str(n) + struct.pack(">i", len(b)) + b
def tag_empty_list(n): return b"\x09" + nbt_str(n) + b"\x0a" + struct.pack(">i", 0)

bl = blocks.transpose(0, 1, 2).reshape(-1)                # (y,k,i) → 顺序即 (y*Length + z)*Width + x
dt = mdata.transpose(0, 1, 2).reshape(-1)
body = (tag_short("Width", W) + tag_short("Height", HGT) + tag_short("Length", L) +
        tag_str("Materials", "Alpha") + tag_byte_array("Blocks", bl) + tag_byte_array("Data", dt) +
        tag_empty_list("Entities") + tag_empty_list("TileEntities") +
        tag_int("WEOriginX", -800) + tag_int("WEOriginY", Y0) + tag_int("WEOriginZ", 300) +
        tag_int("WEOffsetX", 0) + tag_int("WEOffsetY", 0) + tag_int("WEOffsetZ", 0))
nbt = b"\x0a" + nbt_str("Schematic") + body + b"\x00"   # ★ WE 要求根 TAG_Compound 名字必须是 "Schematic"
with gzip.open("mass_v0.schematic", "wb") as f:
    f.write(nbt)

# ---------------- 自检：读回 ----------------
def read_nbt(buf, pos=0):
    def rs(p):
        n = struct.unpack(">H", buf[p:p + 2])[0]; return buf[p + 2:p + 2 + n].decode("utf-8"), p + 2 + n
    t = buf[pos]; name, p = rs(pos + 1); out = {}
    if t == 10:
        while buf[p] != 0:
            v, p = read_nbt(buf, p); out[v[0]] = v[1]
        p += 1
    elif t == 2: out = (name, struct.unpack(">h", buf[p:p + 2])[0]); p += 2
    elif t == 3: out = (name, struct.unpack(">i", buf[p:p + 4])[0]); p += 4
    elif t == 7:
        n = struct.unpack(">i", buf[p:p + 4])[0]; p += 4
        out = (name, np.frombuffer(buf[p:p + n], np.uint8).copy()); p += n
    elif t == 8: out = (name, rs(p)[0]); p = rs(p)[1]
    elif t == 9:
        et = buf[p]; n = struct.unpack(">i", buf[p + 1:p + 5])[0]; p += 5
        out = (name, []); 
        for _ in range(n):
            pass
    else: raise ValueError("tag %d 未处理" % t)
    return (name, out) if t == 10 else out, p

with gzip.open("mass_v0.schematic", "rb") as f:
    raw = f.read()
root, _ = read_nbt(raw)
r = root[1] if isinstance(root, tuple) else root
print("=== 自检：读回 mass_v0.schematic（%d 字节 gzip）===" % len(raw))
print("  Width=%d Height=%d Length=%d Materials=%s" % (r["Width"], r["Height"], r["Length"], r["Materials"]))
rb = r["Blocks"]
print("  尺寸一致: %s ；Blocks 元素数 %d（应为 %d）" % (rb.size == W * HGT * L, rb.size, W * HGT * L))
print("  与写出前逐字节一致: %s" % bool(np.array_equal(rb.reshape(HGT, L, W), blocks)))
print("  非空气方块总数 = %d" % int((rb > 0).sum()))
cnt = {}
for bid in np.unique(rb[rb > 0]):
    cnt[int(bid)] = int((rb == bid).sum())
print("  各材质计数（id: 数量）: %s" % cnt)

# ---------------- 出图 ----------------
def hcolor(y):                                            # 高度色带（3..255）
    t = max(0.0, min(1.0, (y - 3) / 252.0))
    return (int(20 + 90 * t), int(90 + 120 * (1 - abs(t - 0.45) * 2)), int(180 - 150 * t))

top = np.zeros((L, W, 3), np.uint8)
hh2 = np.zeros((L, W))
for k in range(L):
    for i in range(W):
        col = np.nonzero(blocks[:, k, i])[0]
        if not len(col):
            top[k, i] = (30, 30, 30); continue
        yy = col[-1]; bid, md = int(blocks[yy, k, i]), int(mdata[yy, k, i])
        hh2[k, i] = yy + OY
        if bid == 251 and md == 0: top[k, i] = (255, 255, 255)        # 天梯主结构 冷白
        elif bid == 251 and md == 4: top[k, i] = (255, 40, 40)        # 磁浮 朱红系
        elif bid == 251 and md == 14: top[k, i] = (255, 0, 255)       # 能网 品红
        elif bid == 95: top[k, i] = (0, 220, 255)                     # 玻璃 青
        elif bid == 2: top[k, i] = (60, 160, 60)                      # 草地
        else: top[k, i] = hcolor(yy + OY)                             # 其余按高度上色
img = Image.fromarray(top, "RGB").resize((W * 6, L * 6), Image.NEAREST)
d = ImageDraw.Draw(img)
for g in range(0, W + 1, 10):
    d.line([(g * 6, 0), (g * 6, L * 6)], fill=(0, 0, 0), width=1)
    d.line([(0, g * 6), (W * 6, g * 6)], fill=(0, 0, 0), width=1)
    d.text((g * 6 + 2, 2), str(g), fill=(255, 255, 0))
    d.text((2, g * 6 + 2), str(g), fill=(255, 255, 0))
img.save("mass_v0_top.png")
print("=== 高度统计（俯视图用）===")
print("  h: min=%d max=%d 中位=%d ；台地分布(取少数) %s"
      % (hh2.min(), hh2.max(), int(np.median(hh2)),
         {int(v): int((hh2 == v).sum()) for v in np.unique(hh2)[-6:]}))

sec = np.zeros((HGT, W, 3), np.uint8)
for s in range(W):
    for yy in range(HGT):
        bid, md = int(blocks[yy, s, s]), int(mdata[yy, s, s])
        sec[HGT - 1 - yy, s] = (60, 60, 60) if bid == 0 else ((150, 150, 150) if bid == 1 else
                     (90, 200, 90) if bid == 2 else (240, 240, 240) if bid == 251 else
                     (255, 60, 60) if bid == 251 and md == 14 else (120, 120, 255))
Image.fromarray(sec, "RGB").resize((W * 6, HGT * 3), Image.NEAREST).save("mass_v0_sec.png")

print("=== 25×25 ASCII 高度图（每 4 格取样，数字 = floor(h/10)）===")
for k in range(0, L, 4):
    print("  " + "".join("%X" % max(0, min(15, int(hh[k, i] // 10))) for i in range(0, W, 4)))
