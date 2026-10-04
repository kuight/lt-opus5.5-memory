import re, math
from lt_colors import fc
import lt_root
ROOT_NAME="cyber_lab"   # 根层 structure 的 name

def T(b): return b if b is None or b.startswith("block:") else 'block:"%s"' % b
def G(h): return T(fc(h, "glow"))
def F(h): return T(fc(h, "solid"))
def GL(h): return T(fc(h, "trans"))
QZ, QP, SM, IR, AN = [T("minecraft:" + b) for b in
    ("quartz_block", "quartz_block:2", "double_stone_slab:8", "iron_block", "stone:6")]
CY, MG, WH, RD = G("#3ff0ff"), G("#ff2bd6"), G("#e6f4ff"), G("#ff3030")
DK, DK2, SEAM, BLK = F("#1c1f26"), F("#2a2d33"), F("#0b0c10"), F("#121418")
GLASS, FLUID = GL("#1a3050"), GL("#3cff9a")

V = {}
def box(b, x1, y1, z1, x2, y2, z2):
    b = T(b)
    for x in range(x1, x2):
        for y in range(y1, y2):
            for z in range(z1, z2):
                if b is None: V.pop((x, y, z), None)
                else: V[(x, y, z)] = b
def put(b, x, y, z): V[(x, y, z)] = b

# ---------- 平面轮廓（切角） ----------
X0, X1, Z0, Z1, CH = 16, 208, 32, 176, 16
def inside(x, z, i):
    if not (X0 + i <= x < X1 - i and Z0 + i <= z < Z1 - i): return False
    return min(x - X0, X1 - 1 - x) + min(z - Z0, Z1 - 1 - z) >= CH + i * 1.414
def layer(x, z):
    if not inside(x, z, 0): return None
    for i, n in ((2, "out"), (6, "core"), (8, "in")):
        if not inside(x, z, i): return n
    return "room"

def wall_mat(L, y, t, diag):
    if y < 10: return BLK if L == "out" else (AN if L == "in" else DK2)
    if y == 10 and L == "out": return MG
    if 26 <= y < 50:
        if t % 24 < 2: return CY if L == "out" else DK
        return GLASS
    if y == 50 and L == "out": return CY
    if L == "out":
        if diag: return SEAM if y % 8 == 0 else MG
        return SEAM if (t % 32 == 0 or y in (18, 60)) else DK
    if L == "in":
        if y == 62: return MG
        return AN if t % 32 == 0 else QZ
    return DK2

TX, TZ = 112, 96
# ---------- 基座与入口步道 ----------
box(F("#23262c"), 0, 0, 0, 224, 3, 192)
box(CY, 0, 2, 0, 224, 3, 1); box(CY, 0, 2, 191, 224, 3, 192)
box(CY, 0, 2, 0, 1, 3, 192); box(CY, 223, 2, 0, 224, 3, 192)
box(SM, 88, 3, 0, 120, 4, 32)
box(CY, 88, 3, 0, 89, 4, 32); box(CY, 119, 3, 0, 120, 4, 32)
for x in range(89, 119):
    for z in range(22, 30):
        put(G("#ffd400") if (x + z) % 8 < 4 else BLK, x, 3, z)

# ---------- 墙体 / 地板 / 屋顶 / 檐口 / 女儿墙 ----------
for x in range(0, 224):
    for z in range(0, 192):
        L = layer(x, z)
        if L is None and not inside(x, z, -6): continue
        t = x + z
        diag = min(x - X0, X1 - 1 - x) < CH and min(z - Z0, Z1 - 1 - z) < CH
        if L in ("out", "core", "in"):
            for y in range(3, 70): V[(x, y, z)] = wall_mat(L, y, t, diag)
        if L == "room":
            for y in range(3, 6):
                V[(x, y, z)] = AN if (y == 5 and (x % 16 == 0 or z % 16 == 0)) else SM
            if (x in (104, 119) and z < 64): V[(x, 5, z)] = CY
            V[(x, 68, z)] = AN; V[(x, 69, z)] = AN
        if L is not None:
            for y in range(70, 78): V[(x, y, z)] = DK2
        else:
            for y in range(72, 78): V[(x, y, z)] = DK
            if not inside(x, z, -5): V[(x, 72, z)] = MG
        if not inside(x, z, -2):
            for y in range(78, 86): V[(x, y, z)] = DK
            V[(x, 85, z)] = CY

# ---------- 入口：雨棚 + 招牌 ----------
box(DK, 64, 54, 6, 160, 58, 32)
for x in range(64, 160):
    for z in range(6, 32):
        if x % 16 == 0 or z % 8 == 6: put(WH, x, 54, z)
box(MG, 64, 54, 6, 160, 58, 7)
FONT = {"N": ["101", "111", "111", "111", "101"], "E": ["111", "100", "111", "100", "111"],
        "X": ["101", "101", "010", "101", "101"], "U": ["101", "101", "101", "101", "111"],
        "S": ["111", "100", "111", "001", "111"], "-": ["000", "000", "111", "000", "000"],
        "L": ["100", "100", "100", "100", "111"], "A": ["010", "101", "111", "101", "101"],
        "B": ["110", "101", "110", "101", "110"]}
txt = "NEXUS-LAB"; x0 = 112 + len(txt) * 4
for i, ch in enumerate(txt):
    for r, row in enumerate(FONT[ch]):
        for c, bit in enumerate(row):
            if bit == "1":
                x = x0 - (i * 8 + c * 2) - 2; y = 68 - (r + 1) * 2
                box(MG, x, y, 30, x + 2, y + 2, 32)

# ---------- 东墙管道 + 空调外机 ----------
for pz in (60, 68):
    box(IR, 208, 6, pz, 212, 78, pz + 4)
    for y in range(14, 78, 16):
        box(IR, 207, y, pz - 1, 213, y + 2, pz + 5)
        box(CY, 212, y + 8, pz, 213, y + 9, pz + 4)
box(IR, 208, 6, 110, 222, 30, 150)
box(MG, 208, 30, 110, 222, 31, 150)
for fz in (120, 140):
    for y in range(9, 28):
        for z in range(fz - 9, fz + 10):
            r = math.hypot(y + 0.5 - 18.5, z + 0.5 - fz)
            if r < 9:
                put(BLK if (r > 7.5 or (abs(y - 18) < 1 or abs(z - fz) < 1)) else DK2, 222, y, z)
    put(CY, 222, 18, fz)

# ---------- 西墙全息广告牌 ----------
box(BLK, 14, 28, 70, 16, 72, 138)
box(CY, 13, 28, 70, 14, 72, 138)
box(GL("#ff3fd0"), 13, 30, 72, 14, 70, 136)
for y in range(32, 70, 6): box(CY, 13, y, 74, 14, y + 1, 134)

# ---------- 屋顶设备 ----------
box(IR, 56, 78, 140, 58, 124, 142)
for y in (96, 110): box(IR, 50, y, 140, 64, y + 1, 142); box(IR, 56, y, 134, 58, y + 1, 148)
box(RD, 55, 124, 139, 59, 127, 143)
box(IR, 149, 78, 139, 151, 86, 141)
for dx in range(-14, 15):
    for dz in range(-14, 15):
        d2 = dx * dx + dz * dz
        if d2 <= 196: put(QZ, 150 + dx, 86 + d2 // 28, 140 + dz)
box(IR, 150, 87, 140, 151, 98, 141); put(CY, 150, 98, 140)
for (lx, lz) in ((30, 50), (108, 50), (30, 94), (108, 94)):
    box(IR, lx, 78, lz, lx + 2, 82, lz + 2)
for x in range(30, 110):
    for z in range(50, 96):
        put(F("#c0c8d8") if (x % 10 == 0 or z % 10 == 0) else F("#1d2f66"), x, 82, z)
box(DK2, 130, 78, 50, 176, 90, 84)
box(MG, 130, 84, 50, 176, 85, 84)
for fx in (142, 164):
    for x in range(fx - 9, fx + 10):
        for z in range(58, 77):
            r = math.hypot(x + 0.5 - fx, z + 0.5 - 67)
            if r < 9: put(BLK if r > 7.5 or abs(x - fx) < 1 or abs(z - 67) < 1 else SEAM, x, 90, z)
    put(CY, fx, 91, 67)

# ---------- 中央培养舱 ----------
for x in range(TX - 32, TX + 33):
    for z in range(TZ - 32, TZ + 33):
        r = math.hypot(x + 0.5 - TX, z + 0.5 - TZ)
        if 29 <= r < 30.5: put(CY, x, 5, z)
        if r < 26:
            for y in range(6, 12): put(IR, x, y, z)
            if 23 <= r < 24.5: put(CY, x, 11, z)
        if r < 22:
            for y in range(12, 54): put(GLASS if r >= 20 else FLUID, x, y, z)
        if r < 24:
            for y in range(54, 60): put(IR, x, y, z)
        if r < 4: put(CY, x, 60, z)
        if 30 <= r < 32 and inside(x, z, 8): put(MG, x, 67, z)
for x in range(TX - 7, TX + 8):
    for y in range(26, 41):
        for z in range(TZ - 7, TZ + 8):
            if math.dist((x + .5, y + .5, z + .5), (TX, 33.5, TZ)) < 7: put(MG, x, y, z)
for k in range(6):
    a = k * math.pi / 3
    bx, bz = int(TX + 13 * math.cos(a)), int(TZ + 13 * math.sin(a))
    for y in range(14, 52, 5): put(WH, bx, y, bz)
for dx, dz in ((0, -22), (0, 21), (-22, 0), (21, 0)):
    box(IR, TX + dx, 12, TZ + dz, TX + dx + 1, 54, TZ + dz + 1)
for px, pz in ((TX - 14, TZ - 1), (TX + 12, TZ - 1), (TX - 1, TZ - 14), (TX - 1, TZ + 12)):
    box(IR, px, 60, pz, px + 2, 68, pz + 2)
    box(CY, px - 1, 64, pz - 1, px + 3, 65, pz + 3)

# ---------- 天花板灯盘 ----------
for cx in range(32, 192, 32):
    for cz in range(48, 160, 32):
        if abs(cx + 16 - TX) < 36 and abs(cz + 16 - TZ) < 36: continue
        box(IR, cx + 2, 66, cz + 2, cx + 30, 68, cz + 30)
        box(WH, cx + 4, 66, cz + 4, cx + 28, 67, cz + 28)

# ---------- 南墙数据屏 ----------
box(F("#07080b"), 48, 22, 164, 176, 62, 166)
box(IR, 47, 21, 163, 177, 22, 166); box(IR, 47, 62, 163, 177, 63, 166)
box(IR, 47, 21, 163, 48, 63, 166); box(IR, 176, 21, 163, 177, 63, 166)
for x in range(50, 174, 12): box(F("#1a2a3a"), x, 24, 163, x + 1, 60, 164)
for x in range(50, 118): put(CY, x, 42 + int(round(9 * math.sin(x / 8.0))), 163)
for k, h in enumerate([8, 14, 10, 18, 12, 16, 6, 20, 11, 15]):
    box(MG, 122 + k * 5, 24, 163, 125 + k * 5, 24 + h, 164)
box(CY, 52, 58, 163, 90, 59, 164)

# ---------- 电缆桥架 ----------
box(IR, 184, 62, 54, 198, 63, 154)
for i, c in enumerate(("#ffb000", "#3ff0ff", "#ff2bd6")):
    box(F(c), 186 + i * 4, 63, 54, 188 + i * 4, 64, 154)

# ---------- 载入家具 ----------
BOXRE = re.compile(r'\[I;(-?\d+),(-?\d+),(-?\d+),(-?\d+),(-?\d+),(-?\d+)\]')
ENT = re.compile(r'\{(?:boxes:\[((?:\[I;[-\d,]+\],?)*)\]|bBox:(\[I;[-\d,]+\])),tile:\{([^{}]*)\}\}')
def norm(v):
    mn = [min(p[i] for p in v) for i in range(3)]
    return {(p[0] - mn[0], p[1] - mn[1], p[2] - mn[2]): b for p, b in v.items()}
def dims(v): return [max(p[i] for p in v) + 1 for i in range(3)]
def load(fn):
    t = open(fn, encoding="utf-8").read(); v = {}
    for m in ENT.finditer(t):
        for b in BOXRE.findall(m.group(1) or m.group(2)):
            x1, y1, z1, x2, y2, z2 = map(int, b)
            for x in range(x1, x2):
                for y in range(y1, y2):
                    for z in range(z1, z2): v[(x, y, z)] = m.group(3)
    s = re.search(r'structure:(\{[^{}]*\})', t)
    return norm(v), (s.group(1) if s else None)
def rot(v, k):   # 0朝北 1朝东 2朝南 3朝西
    for _ in range(k % 4):
        D = dims(v)[2]
        v = norm({(D - 1 - p[2], p[1], p[0]): b for p, b in v.items()})
    return v
def stamp(v, ox, oy, oz, name):
    hit = 0
    for p, b in v.items():
        q = (p[0] + ox, p[1] + oy, p[2] + oz)
        if q in V: hit += 1
        V[q] = b
    print("  %-14s @(%d,%d,%d) 尺寸%s 覆盖%d" % (name, ox, oy, oz, dims(v), hit))

def merge(vox):
    mats = {}
    for p, b in vox.items(): mats.setdefault(b, set()).add(p)
    parts, n = [], 0
    for b, S in mats.items():
        out = []
        for p in sorted(S, key=lambda q: (q[1], q[2], q[0])):
            if p not in S: continue
            x, y, z = p; x2 = x + 1
            while (x2, y, z) in S: x2 += 1
            z2 = z + 1
            while all((i, y, z2) in S for i in range(x, x2)): z2 += 1
            y2 = y + 1
            while all((i, y2, k) in S for i in range(x, x2) for k in range(z, z2)): y2 += 1
            for i in range(x, x2):
                for j in range(y, y2):
                    for k in range(z, z2): S.discard((i, j, k))
            out.append("[I;%d,%d,%d,%d,%d,%d]" % (x, y, z, x2, y2, z2))
        n += len(out)
        if len(out) == 1: parts.append("{bBox:%s,tile:{%s}}" % (out[0], b))
        else: parts.append("{boxes:[%s],tile:{%s}}" % (",".join(out), b))
    return "[%s]" % ",".join(parts), n

KIDS = []
def child(v, st, ox, oy, oz, name):
    cut, sh = 0, {}
    for p, b in v.items():
        q = (p[0] + ox, p[1] + oy, p[2] + oz)
        if V.pop(q, None) is not None: cut += 1
        sh[q] = b
    t, n = merge(sh)
    KIDS.append("{tiles:%s%s}" % (t, ",structure:" + st if st else ""))
    print("  [子结构] %-8s @(%d,%d,%d) %d块 清让%d 结构:%s" % (name, ox, oy, oz, n, cut, st))

print("== 家具 ==")
door, dst = load("lab_door.txt"); dw, dh, dd = dims(door)
dz0 = 36 - dd // 2
box(None, 96, 6, Z0, 96 + dw, 6 + dh, Z0 + 8)                    # 门洞
box(None, 96 + dw, 6, dz0, 96 + 2 * dw, 6 + dh, dz0 + dd)         # 门袋
box(CY, 94, 6, 30, 96, 8 + dh, 32); box(CY, 96 + dw, 6, 30, 98 + dw, 8 + dh, 32)
box(CY, 94, 6 + dh, 30, 98 + dw, 8 + dh, 32)
if dd > 4: print("  注意：门厚", dd, "像素 > 4，门袋会切穿墙皮")
bench = rot(load("lab_bench.txt")[0], 1)
for z in (58, 90, 122): stamp(bench, 24, 6, z, "lab_bench")
rack = rot(load("server_rack_clean.txt")[0], 3)
for z in range(56, 152, 16): stamp(rack, 200 - dims(rack)[0], 6, z, "server_rack")
con = load("console_clean.txt")[0]; cw, ch_, cd = dims(con)
chair, cst = load("office_chair.txt"); chair = rot(chair, 2); hw, hh, hd = dims(chair)
for cx in (80, 144):
    cz = 162 - cd
    stamp(con, cx - cw // 2, 6, cz, "console")
    child(chair, cst, cx - hw // 2, 6, cz - hd - 2, "chair")
child(door, dst, 96, 6, dz0, "door")

# ---------- 输出 ----------
t, n = merge(V)
P = list(V)
mn = [min(p[i] for p in P) for i in range(3)]
sz = [max(p[i] for p in P) + 1 - mn[i] for i in range(3)]
out = "{tiles:%s,min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d,children:[%s]}" % (
    t, mn[0], mn[1], mn[2], sz[0], sz[1], sz[2], n, ",".join(KIDS))
# 根有 children ⇒ 根必须有 structure（§3.9）；缺了在此自动插入，断言不过直接报错退出
out = lt_root.fix(out, ROOT_NAME, tag="cyber_lab.txt")
open("cyber_lab.txt", "w", encoding="utf-8").write(out)
print("cyber_lab.txt 根结构", n, "块，体素", len(V), "，", len(out), "字节，尺寸", sz)