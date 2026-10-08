# -*- coding: utf-8 -*-
# lt_mass1.py —— 天梯城 体块 v1（总图 v3 灰模；设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_mass1.py  → mass_v1.schematic + mass_v1_top.png + mass_v1_sec.png
# 局部坐标（格）：x 东、y 上、z 南；WEOrigin = (-800, 3, 300)，//schem load mass_v1 + //paste -o 贴回原位。
# 只是规划灰模（原版方块按片区上色），不是成品；成品一律小方块。
# 参考：重庆"一半贴地一半悬空、多层入口"（新京报）；来福士横向连廊；Night City 巨构住宅三段外挑（Cyberpunk Wiki / Reddit）；
#       九龙城寨高密度互相遮挡（ArcGIS StoryMaps）；流浪地球地下城 + 通地表电梯（archcollege 43399）；李子坝轻轨穿楼。
import os, io, gzip, struct, math, random
import numpy as np
try:
    from PIL import Image
except ImportError:
    raise SystemExit("需要 Pillow：停下，不要自己装包")

OUT = "mass_v1.schematic"
W, H, L = 160, 253, 160
ORIGIN = (-800, 3, 300)
BLK = np.zeros((W, H, L), dtype=np.uint8)
DAT = np.zeros((W, H, L), dtype=np.uint8)

MAT = {  # key: (id, data, 说明, 预览色)
    "rock":   (1, 0, "石头：山体", (125, 125, 125)),
    "up":     (251, 8, "淡灰混凝土：上台地地面", (155, 155, 148)),
    "mid":    (251, 7, "灰混凝土：中台地地面", (110, 110, 102)),
    "val":    (172, 0, "硬化粘土：谷底地面", (150, 92, 66)),
    "ledge":  (251, 12, "棕混凝土：崖边小台地 / 地下城楼板", (96, 60, 32)),
    "corp":   (251, 0, "白混凝土：公司塔区", (207, 213, 214)),
    "elev":   (155, 0, "石英块：天梯基座与主塔", (235, 229, 222)),
    "res":    (251, 3, "淡蓝混凝土：巨构住宅", (36, 137, 199)),
    "mkt1":   (251, 2, "品红混凝土：城寨 / 桥下市井", (169, 48, 159)),
    "mkt2":   (251, 6, "粉混凝土：城寨 / 桥下市井", (214, 101, 143)),
    "ind":    (251, 1, "橙混凝土：工业谷（冷却塔、熔炉、取水塔）", (224, 97, 1)),
    "farm":   (251, 5, "黄绿混凝土：菌丝农场塔", (94, 169, 24)),
    "rail":   (251, 15, "黑混凝土：轨道桥与墩", (8, 10, 15)),
    "pipe":   (251, 4, "黄混凝土：管线网（水 / 蛋白）", (241, 175, 21)),
    "cable":  (251, 9, "青混凝土：电缆网 / 缆束下段", (21, 119, 136)),
    "walk":   (251, 13, "绿混凝土：扶梯 / 人行连廊", (73, 91, 36)),
    "glass":  (95, 3, "淡蓝染色玻璃：公司连廊 / 电梯井", (102, 153, 216)),
    "cglass": (95, 9, "青染色玻璃：缆束中段", (76, 127, 153)),
    "clear":  (20, 0, "玻璃：缆束顶段", (220, 240, 255)),
    "net":    (95, 0, "白染色玻璃：取水塔雾网", (250, 250, 250)),
    "lamp":   (169, 0, "海晶灯：地下街灯", (170, 210, 200)),
}

def _clip(x0, x1, y0, y1, z0, z1):
    x0, x1 = max(0, int(math.floor(x0))), min(W, int(math.floor(x1)))
    y0, y1 = max(0, int(math.floor(y0))), min(H, int(math.floor(y1)))
    z0, z1 = max(0, int(math.floor(z0))), min(L, int(math.floor(z1)))
    return x0, x1, y0, y1, z0, z1

def put(k, x0, x1, y0, y1, z0, z1):
    x0, x1, y0, y1, z0, z1 = _clip(x0, x1, y0, y1, z0, z1)
    if x0 < x1 and y0 < y1 and z0 < z1:
        BLK[x0:x1, y0:y1, z0:z1] = MAT[k][0]
        DAT[x0:x1, y0:y1, z0:z1] = MAT[k][1]

def air(x0, x1, y0, y1, z0, z1):
    x0, x1, y0, y1, z0, z1 = _clip(x0, x1, y0, y1, z0, z1)
    if x0 < x1 and y0 < y1 and z0 < z1:
        BLK[x0:x1, y0:y1, z0:z1] = 0
        DAT[x0:x1, y0:y1, z0:z1] = 0

XX, ZZ = np.meshgrid(np.arange(W) + 0.5, np.arange(L) + 0.5, indexing="ij")
def disc(cx, cz, r):
    return (XX - cx) ** 2 + (ZZ - cz) ** 2 <= r * r
def ring(cx, cz, ro, ri):
    d2 = (XX - cx) ** 2 + (ZZ - cz) ** 2
    return (d2 <= ro * ro) & (d2 > ri * ri)
def putm(k, mask, y0, y1):
    for y in range(max(0, int(y0)), min(H, int(y1))):
        BLK[:, y, :][mask] = MAT[k][0]
        DAT[:, y, :][mask] = MAT[k][1]
def airm(mask, y0, y1):
    for y in range(max(0, int(y0)), min(H, int(y1))):
        BLK[:, y, :][mask] = 0
        DAT[:, y, :][mask] = 0

def line3(k, p0, p1, r=0, sag=0.0):
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)) * 3) + 1
    for i in range(n + 1):
        t = i / float(n)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t - sag * 4 * t * (1 - t)
        z = z0 + (z1 - z0) * t
        xi, yi, zi = int(math.floor(x)), int(math.floor(y)), int(math.floor(z))
        put(k, xi - r, xi + r + 1, yi - r, yi + r + 1, zi - r, zi + r + 1)

# ===================== 地形：三级地面 + 崖边小台地（不做同心圆）=====================
U, MH, V = 96, 52, 16
xs = np.arange(W)
zU = 62 + 6 * np.sin(xs / 13.0) + 3 * np.sin(xs / 5.3 + 1)      # 上台地南缘
zM = 116 + 7 * np.sin(xs / 17.0 + 2) + 3 * np.sin(xs / 6.1)      # 中台地南缘
HM = np.full((W, L), V, dtype=np.int32)
for x in range(W):
    for z in range(L):
        HM[x, z] = U if z < zU[x] else (MH if z < zM[x] else V)
for x in list(range(0, 40)) + list(range(75, 100)):
    for z in range(L):
        if zU[x] <= z < zU[x] + 5:
            HM[x, z] = 74
for x in range(20, 60):
    for z in range(L):
        if zM[x] <= z < zM[x] + 4:
            HM[x, z] = 34
for y in range(U):
    BLK[:, y, :][HM > y] = 1
for h, k in ((U, "up"), (74, "ledge"), (MH, "mid"), (34, "ledge"), (V, "val")):
    putm(k, HM == h, h - 1, h)

# ===================== 地下城竖井（流浪地球式：剖开地面看见地下几层）=====================
SX, SZ, SR = 62, 92, 9
assert (HM[disc(SX, SZ, SR + 1)] == MH).all(), "竖井不在中台地"
airm(disc(SX, SZ, SR), 4, MH)
putm("ledge", disc(SX, SZ, SR), 3, 4)
LV = [6, 18, 30, 42]
nlamp = 0
for lv in LV:
    putm("ledge", ring(SX, SZ, SR, 6.5), lv - 1, lv)
    for dx, dz in ((1, 0), (0, 1), (-1, 0)):
        for s in range(8, 20):
            cx, cz = SX + dx * s, SZ + dz * s
            if dx:
                xa, xb, za, zb = cx, cx + 1, SZ - 2, SZ + 2
            else:
                xa, xb, za, zb = SX - 2, SX + 2, cz, cz + 1
            air(xa, xb, lv, lv + 5, za, zb)
            put("ledge", xa, xb, lv - 1, lv, za, zb)
            if s % 4 == 0:
                put("lamp", xa, xb, lv + 4, lv + 5, za, zb)
                nlamp += 1
putm("glass", disc(SX, SZ, 1.6), 4, MH + 10)
putm("rail", disc(SX, SZ, 2.6), MH + 10, MH + 11)

# ===================== 天梯基座（全城唯一冲天）=====================
EX, EZ = 118, 30
assert (HM[disc(EX, EZ, 21)] == U).all(), "天梯平台不在上台地"
putm("elev", disc(EX, EZ, 20), U, U + 6)
put("elev", 100, 108, U + 6, U + 14, 22, 38)            # 货运站
put("elev", 128, 136, U + 6, U + 11, 40, 47)            # 候梯厅
for a in (90, 210, 330):
    tx, tz = EX + 10 * math.cos(math.radians(a)), EZ + 10 * math.sin(math.radians(a))
    putm("elev", disc(tx, tz, 2.5), U + 6, 232)
putm("cable", disc(EX, EZ, 2.2), U + 6, 150)
putm("cglass", disc(EX, EZ, 2.2), 150, 200)
putm("clear", disc(EX, EZ, 2.2), 200, H)
putm("elev", ring(EX, EZ, 14.5, 12), 139, 142)
putm("elev", ring(EX, EZ, 9, 7), 204, 206)

# ===================== 公司塔区（错位 / 外挑，不做直筒）=====================
GROW, OFF = [0, 2, -1, 3, 1, -2], [0, 1, -2, 2, -1, 0]
def tower(cx, cz, w, d, ytop, seed):
    hw, hd = (max(w, d) + 3) // 2 + 2, (max(w, d) + 3) // 2 + 2
    assert (HM[cx - hw:cx + hw, cz - hd:cz + hd] == U).all(), "塔不在上台地 %s" % ((cx, cz),)
    y, i = U, 0
    while y < ytop:
        sh = min(14 + (seed * 7 + i * 5) % 10, ytop - y)
        g = GROW[(seed + i) % 6]
        ox, oz = OFF[(seed * 3 + i) % 6], OFF[(seed + 2 * i) % 6]
        ww, dd = max(5, w + g), max(5, d + g)
        x0, z0 = cx + ox - ww // 2, cz + oz - dd // 2
        put("corp", x0, x0 + ww, y, y + sh, z0, z0 + dd)
        y += sh
        i += 1
    put("corp", cx, cx + 1, ytop, ytop + 12, cz, cz + 1)
    return i
TW = {"T1": (28, 22, 12, 12, 200, 1), "T2": (50, 36, 10, 13, 178, 2), "T3": (74, 18, 9, 10, 160, 3),
      "T4": (16, 44, 9, 9, 146, 4), "T5": (88, 40, 8, 8, 132, 5)}
nsec = sum(tower(*v) for v in TW.values())
for a, b, y in (("T1", "T2", 150), ("T2", "T3", 128), ("T1", "T4", 118), ("T3", "T5", 112)):
    line3("glass", (TW[a][0], y, TW[a][1]), (TW[b][0], y - 4, TW[b][1]), r=1)
line3("glass", (88, 112, 40), (106, 103, 36), r=1)

# ===================== 工业谷 =====================
CT = [(20, 140, 6.0, 50), (42, 146, 5.0, 42), (64, 140, 6.0, 48)]
for cx, cz, r0, h in CT:
    yw, c = V + 0.7 * h, 0.7 * h / 1.333
    for y in range(V, V + h):
        r = r0 * math.sqrt(1 + ((y - yw) / c) ** 2)
        putm("ind", ring(cx, cz, r, r - 1.2), y, y + 1)
put("ind", 81, 99, V, V + 20, 132, 147)                   # 碎片熔炉
for i in range(6):
    put("ind", 83 + 3 * i, 84 + 3 * i, V + 20, V + 28, 134, 145)   # 散热鳍片
putm("ind", disc(96, 135, 1.5), V + 20, V + 45)
putm("farm", disc(106, 152, 5), V, V + 100)               # 菌丝农场塔
for y in range(V + 10, V + 100, 12):
    putm("farm", disc(106, 152, 6.5), y, y + 1)
putm("ind", disc(56, 124, 1.5), V, V + 72)                # 取水塔
putm("net", disc(56, 124, 6), V + 72, V + 73)
putm("ind", ring(56, 124, 6.5, 5.5), V + 71, V + 74)

# ===================== 巨构住宅（三段外挑，底在谷底、中段接中台地）=====================
def mega(cx, cz, core, widths, ys, seed):
    c0 = core // 2
    assert (HM[cx - c0:cx - c0 + core, cz - c0:cz - c0 + core] == V).all(), "住宅底不在谷底"
    put("res", cx - c0, cx - c0 + core, ys[0], ys[1], cz - c0, cz - c0 + core)
    for i, w in enumerate(widths):
        ox = (1, -1, 2)[(seed + i) % 3]
        x0, z0 = cx - w // 2 + ox, cz - w // 2 - ox
        put("res", x0, x0 + w, ys[i + 1], ys[i + 2], z0, z0 + w)
        air(x0, x0 + w, ys[i + 1], ys[i + 1] + 2, z0, z0 + w)            # 段间收腰平台
        put("res", x0 + 2, x0 + w - 2, ys[i + 1], ys[i + 1] + 2, z0 + 2, z0 + w - 2)
    put("res", cx, cx + 1, ys[-1], ys[-1] + 10, cz, cz + 1)
mega(124, 142, 8, [14, 18, 22], [V, 50, 88, 122, 150], 0)
mega(147, 140, 7, [12, 16, 20], [V, 44, 76, 106, 130], 1)
line3("walk", (124, 60, 131), (124, 53, 115), r=1)
line3("walk", (147, 58, 129), (147, 53, 103), r=1)

# ===================== 城寨 / 桥下市井（随机地块、窄巷、违建外挑）=====================
rng = random.Random(20261008)
nbld, x = 0, 2
while x < W - 4:
    w = rng.randint(4, 9)
    z = int(zU[x:x + w].max()) + 6
    while z < L:
        d = rng.randint(4, 8)
        x1, z1 = min(W, x + w), min(L, z + d)
        lot = HM[x:x1, z:z1]
        if lot.size and (lot == MH).all() and math.hypot(x + w / 2.0 - SX, z + d / 2.0 - SZ) > SR + 5:
            h = rng.choice([6, 8, 10, 12, 14, 16, 20, 24, 30, 36])
            k = "mkt1" if rng.random() < 0.55 else "mkt2"
            put(k, x, x1, MH, MH + h, z, z1)
            if h >= 12 and rng.random() < 0.6:
                ox, oz = rng.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                put(k, x + ox, x1 + ox, MH + h, MH + h + rng.randint(3, 8), z + oz, z1 + oz)
            nbld += 1
        z += d + rng.choice([1, 1, 2])
    x += w + rng.choice([1, 1, 2])

# ===================== 轨道（爬坡、拐弯、不等墩距；点 = (x, y, z)）=====================
def rail(name, pts, spans):
    s_next, si, total, npier = 3.0, 0, 0.0, 0
    for (x0, y0, z0), (x1, y1, z1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, z1 - z0)
        n = int(seg / 0.25) + 1
        for i in range(n):
            t = i / float(n)
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            y = int(round(y0 + (y1 - y0) * t))
            put("rail", x - 1, x + 2, y - 1, y + 1, z - 1, z + 2)
            if total + seg * t >= s_next:
                xi, zi = int(x), int(z)
                if 0 <= xi < W - 1 and 0 <= zi < L - 1 and math.hypot(xi + 1 - SX, zi + 1 - SZ) > SR + 1:
                    put("rail", xi, xi + 2, HM[xi, zi], y - 1, zi, zi + 2)
                    npier += 1
                s_next += spans[si % len(spans)]
                si += 1
        total += seg
    print("   %s：全长 %.0f 格，墩 %d 根，梁高 %d→%d" % (name, total, npier, pts[0][1], pts[-1][1]))
print("== 轨道")
rail("1号线（中层，西→东爬坡，x66 处拐弯，穿楼）",
     [(0, 84, 98), (38, 86, 96), (66, 89, 86), (100, 94, 80), (130, 98, 86), (159, 100, 92)],
     [11, 17, 13, 9, 15, 12, 19, 10])
rail("2号线（谷底→天梯平台，约在 x85 z83 上跨 1 号线）",
     [(4, 44, 128), (36, 64, 120), (74, 98, 104), (96, 104, 62), (106, 104, 44)],
     [14, 9, 16, 12, 10])

# ===================== 四网：管线 / 电缆 / 人行 =====================
for a, b in (((106, 70, 146), (100, 64, 124)), ((100, 64, 124), (86, 60, 112)), ((86, 60, 112), (60, 58, 106)),
             ((56, 88, 124), (48, 70, 104)), ((48, 70, 104), (30, 64, 98)), ((98, 30, 138), (113, 40, 140))):
    line3("pipe", a, b, r=1)
for x in range(4, W, 9):                                  # 上崖竖管
    z = int(math.ceil(zU[x]))
    put("pipe", x, x + 1, HM[x, z], U, z, z + 1)
for x in range(6, 108, 11):                               # 下崖竖管
    z = int(math.ceil(zM[x]))
    put("pipe", x, x + 1, V, MH, z, z + 1)
for tgt in ((40, 80, 96), (124, 151, 142), (62, 60, 84), (90, 37, 138), (28, 170, 22)):
    p0 = (EX, 160, EZ)
    ln = math.sqrt(sum((tgt[i] - p0[i]) ** 2 for i in range(3)))
    line3("cable", p0, tgt, r=0, sag=0.08 * ln)
line3("walk", (30, 52, 96), (30, 74, 73), r=1)             # 扶梯：中台地 → 崖边小台地
putm("glass", disc(36, 70, 1.2), 74, 100)                 # 竖井电梯：小台地 → 上台地
line3("walk", (36, 99, 70), (36, 97, 64), r=1)
line3("walk", (4, 16, 158), (4, 52, 122), r=1)             # 扶梯：谷底 → 中台地
putm("glass", disc(40, 117, 1.2), V, 58)                  # 竖井电梯：谷底 → 中台地
line3("walk", (40, 57, 117), (40, 53, 109), r=1)

# ===================== 写 schematic（根名 Schematic，gzip）=====================
def tn(t, name):
    nb = name.encode("utf-8")
    return bytes([t]) + struct.pack(">H", len(nb)) + nb
def t_short(n, v): return tn(2, n) + struct.pack(">h", v)
def t_int(n, v): return tn(3, n) + struct.pack(">i", v)
def t_str(n, s):
    b = s.encode("utf-8")
    return tn(8, n) + struct.pack(">H", len(b)) + b
def t_barr(n, b): return tn(7, n) + struct.pack(">i", len(b)) + b
def t_elist(n): return tn(9, n) + bytes([10]) + struct.pack(">i", 0)
blocks = BLK.transpose(1, 2, 0).tobytes()
datas = DAT.transpose(1, 2, 0).tobytes()
body = (t_short("Width", W) + t_short("Height", H) + t_short("Length", L) + t_str("Materials", "Alpha")
        + t_barr("Blocks", blocks) + t_barr("Data", datas) + t_elist("Entities") + t_elist("TileEntities")
        + t_int("WEOriginX", ORIGIN[0]) + t_int("WEOriginY", ORIGIN[1]) + t_int("WEOriginZ", ORIGIN[2])
        + t_int("WEOffsetX", 0) + t_int("WEOffsetY", 0) + t_int("WEOffsetZ", 0))
raw = tn(10, "Schematic") + body + b"\x00"
if os.path.exists(OUT):
    os.remove(OUT)
with gzip.open(OUT, "wb") as f:
    f.write(raw)

# ===================== 独立回读自检 =====================
def parse(buf, p, t):
    if t == 1: return buf[p], p + 1
    if t == 2: return struct.unpack_from(">h", buf, p)[0], p + 2
    if t == 3: return struct.unpack_from(">i", buf, p)[0], p + 4
    if t == 4: return struct.unpack_from(">q", buf, p)[0], p + 8
    if t == 5: return struct.unpack_from(">f", buf, p)[0], p + 4
    if t == 6: return struct.unpack_from(">d", buf, p)[0], p + 8
    if t == 7:
        n = struct.unpack_from(">i", buf, p)[0]
        return buf[p + 4:p + 4 + n], p + 4 + n
    if t == 8:
        n = struct.unpack_from(">H", buf, p)[0]
        return buf[p + 2:p + 2 + n].decode("utf-8"), p + 2 + n
    if t == 9:
        et, n = buf[p], struct.unpack_from(">i", buf, p + 1)[0]
        p += 5
        out = []
        for _ in range(n):
            v, p = parse(buf, p, et)
            out.append(v)
        return out, p
    if t == 10:
        d = {}
        while True:
            tt = buf[p]; p += 1
            if tt == 0: return d, p
            n = struct.unpack_from(">H", buf, p)[0]
            nm = buf[p + 2:p + 2 + n].decode("utf-8"); p += 2 + n
            d[nm], p = parse(buf, p, tt)
    raise ValueError("未知标签 %d" % t)
with gzip.open(OUT, "rb") as f:
    rb = f.read()
assert rb[:12] == bytes.fromhex("0A0009536368656D61746963"), "根标签不是 Schematic"
root, end = parse(rb, 12, 10)
assert end == len(rb), "NBT 末尾有多余字节"
assert (root["Width"], root["Height"], root["Length"]) == (W, H, L)
assert root["Materials"] == "Alpha"
assert len(root["Blocks"]) == len(root["Data"]) == W * H * L
assert root["Blocks"] == blocks and root["Data"] == datas, "回读数组与写入不一致"
assert (root["WEOriginX"], root["WEOriginY"], root["WEOriginZ"]) == ORIGIN

# ===================== 统计 + 预览图 =====================
nz = int((BLK != 0).sum())
print("== %s：%d 字节（gzip），解压 %d 字节；回读自检全部 PASS" % (OUT, os.path.getsize(OUT), len(rb)))
print("   尺寸 %d×%d×%d = %d 格，非空气 %d" % (W, H, L, W * H * L, nz))
print("   世界范围 x %d..%d  y %d..%d  z %d..%d（//paste -o 贴回原位）" % (
    ORIGIN[0], ORIGIN[0] + W - 1, ORIGIN[1], ORIGIN[1] + H - 1, ORIGIN[2], ORIGIN[2] + L - 1))
print("   地面：上台地 y%d / 崖边小台地 y74 / 中台地 y%d / 崖边小台地 y34 / 谷底 y%d（局部，世界 +3）" % (U, MH, V))
print("   公司塔 %d 座 %d 段；市井楼 %d 栋；地下街 %d 层×3 条，街灯 %d；冷却塔 %d 座；巨构住宅 2 栋" % (
    len(TW), nsec, nbld, len(LV), nlamp, len(CT)))
print("== 材质（片区配色）")
lut = {}
for k, (bid, dv, desc, rgb) in MAT.items():
    m = (BLK == bid) & (DAT == dv)
    print("   %-6s %3d:%-2d %8d  %s" % (k, bid, dv, int(m.sum()), desc))
    lut[(bid, dv)] = rgb
def wc(x, y, z): return "(%d, %d, %d)" % (ORIGIN[0] + x, ORIGIN[1] + y, ORIGIN[2] + z)
print("== 机位（/tp 世界坐标）")
print("   A 东南外全景 %s 朝西北" % wc(200, 150, 210))
print("   B 竖井边     %s 朝南看井（头顶是 1 号线）" % wc(62, 53, 80))
print("   C 两线交叉下 %s 朝北仰视（可能在楼里，飞起来找空位）" % wc(85, 56, 90))
print("   D 天梯平台   %s 2 号线终点" % wc(104, 103, 44))
print("   E 谷底仰望   %s 朝北看两道崖" % wc(80, 17, 155))

S = 4
top = Image.new("RGB", (W * S, L * S))
px = top.load()
rev = BLK[:, ::-1, :] != 0
ytop = H - 1 - rev.argmax(axis=1)
for x in range(W):
    for z in range(L):
        y = int(ytop[x, z])
        rgb = lut.get((int(BLK[x, y, z]), int(DAT[x, y, z])), (128, 128, 128))
        f = 0.45 + 0.55 * y / float(H)
        c = tuple(int(v * f) for v in rgb)
        for i in range(S):
            for j in range(S):
                px[x * S + i, z * S + j] = c
top.save("mass_v1_top.png")
S2 = 3
sec = Image.new("RGB", (L * S2 * 2 + 12, H * S2), (40, 44, 52))
ps = sec.load()
for n, sx in enumerate((SX, EX)):
    for z in range(L):
        for y in range(H):
            b = int(BLK[sx, y, z])
            if b:
                c = lut.get((b, int(DAT[sx, y, z])), (128, 128, 128))
                for i in range(S2):
                    for j in range(S2):
                        ps[n * (L * S2 + 12) + z * S2 + i, (H - 1 - y) * S2 + j] = c
sec.save("mass_v1_sec.png")
print("   PNG：mass_v1_top.png（俯视，越亮越高）/ mass_v1_sec.png（左 x=%d 竖井剖面、右 x=%d 天梯剖面；北在左）" % (SX, EX))
