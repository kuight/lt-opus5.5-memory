# -*- coding: utf-8 -*-
# lt_bridge1.py —— 轨道桥标准件 一期（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_bridge1.py
# 输出：bridge_kit.txt（两跨 + 端墩，B-01..B-03）、bridge_unit_B04.txt、bridge_unit_B05.txt、bridge_end_B06.txt
# 坐标 px：x 东、y 上、z 南；桥沿 x 方向。标准跨 = 256px（16 格），墩在跨的西端 x0..48。
# 参考：流浪地球概念设计（苏联重工业基调、开放支撑）、香港天桥底空间、李子坝轻轨穿楼、Blade Runner 面摊。
# 斜面只用 Y 偏移可变形盒（只向内），顶/底四角满足 h00+h11=h10+h01；不放贴地格。
import os, sys, io
sys.path.insert(0, os.getcwd())
import numpy as np
import lt_colors, lt_root, lt_tbox
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("需要 Pillow：停下，不要自己装包")

M = 16
UNIT, PIER = 256, 48
NY = 288
NZ = 104 + 2 * M

PAL = {
    "plinth": ("#1E2329", "solid"), "pier": ("#5C6774", "solid"), "pil": ("#6B7685", "solid"),
    "cap": ("#4A5462", "solid"), "bear": ("#2A3038", "solid"), "beam": ("#4A5462", "solid"),
    "rib": ("#6B7685", "solid"), "groove": ("#2A3038", "solid"), "trough": ("#3A424D", "solid"),
    "ballast": ("#1E2329", "solid"), "sleeper": ("#3A3F45", "solid"), "rail": ("#9AA3AD", "solid"),
    "mast": ("#7A8594", "solid"), "insul": ("#DDE2E6", "solid"), "wire": ("#15181C", "solid"),
    "cable": ("#15181C", "solid"), "pipe": ("#8A939E", "solid"), "jbox": ("#3A424D", "solid"),
    "yellow": ("#E8B00F", "solid"), "black": ("#1A1A1A", "solid"), "white": ("#E6E9EC", "solid"),
    "gold": ("#C9A23A", "solid"),
    "cyan": ("#00E5FF", "glow"), "amber": ("#FFB347", "glow"), "red": ("#FF3B2F", "glow"),
}
MAT = {}
for k, (h, kd) in PAL.items():
    b = lt_colors.fc(h, kd)
    assert isinstance(b, str) and b, "lt_colors.fc 没返回方块名: %s %s" % (h, kd)
    MAT[k] = b

def font_path():
    for fn in ("simhei.ttf", "msyh.ttc", "simsun.ttc"):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fn)
        if os.path.exists(p):
            return p
    raise SystemExit("找不到中文字体：停下")
FONT = font_path()
_FC = {}
def text_mask(s, size):
    if size not in _FC:
        _FC[size] = ImageFont.truetype(FONT, size)
    f = _FC[size]
    l, t, r, b = f.getbbox(s)
    img = Image.new("L", (r - l, b - t), 0)
    ImageDraw.Draw(img).text((-l, -t), s, font=f, fill=255)
    return np.array(img) > 128

CS = {(0, 0, 0): "WDN", (0, 0, 1): "WDS", (1, 0, 0): "EDN", (1, 0, 1): "EDS",
      (0, 1, 0): "WUN", (0, 1, 1): "WUS", (1, 1, 0): "EUN", (1, 1, 1): "EUS"}

class Scene:
    def __init__(self, L):
        self.NX = L + 2 * M
        self.G = np.zeros((self.NX, NY, NZ), dtype=np.uint8)
        self.names, self.TB = [], []
        self.cnt = {"chamfer": 0, "cap": 0, "text": 0, "lantern": 0}
    def mid(self, k):
        b = MAT[k]
        if b not in self.names:
            self.names.append(b)
            assert len(self.names) < 255, "材质过多"
        return self.names.index(b) + 1
    def _r(self, x0, y0, z0, x1, y1, z1):
        X0, X1, Z0, Z1 = x0 + M, x1 + M, z0 + M, z1 + M
        assert 0 <= X0 < X1 <= self.NX and 0 <= y0 < y1 <= NY and 0 <= Z0 < Z1 <= NZ, \
            "体素越界 %s" % ((x0, y0, z0, x1, y1, z1),)
        return X0, X1, Z0, Z1
    def fill(self, k, x0, y0, z0, x1, y1, z1):
        X0, X1, Z0, Z1 = self._r(x0, y0, z0, x1, y1, z1)
        self.G[X0:X1, y0:y1, Z0:Z1] = self.mid(k)
    def paint(self, k, x0, y0, z0, x1, y1, z1):
        X0, X1, Z0, Z1 = self._r(x0, y0, z0, x1, y1, z1)
        sub = self.G[X0:X1, y0:y1, Z0:Z1]
        sub[sub != 0] = self.mid(k)
    def px(self, k, x, y, z):
        if self.G[x + M, y, z + M]:
            self.G[x + M, y, z + M] = self.mid(k)
            return 1
        return 0
    def slab(self, k, x0, z0, x1, z1, top, bot, tag):
        for d in (top, bot):
            assert d[(0, 0)] + d[(1, 1)] == d[(1, 0)] + d[(0, 1)], "四角不共面 %s" % d
        for c in top:
            assert top[c] > bot[c], "板厚 ≤0"
        yhi, ylo = max(top.values()), min(bot.values())
        offs = []
        for (sx, sz) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            du, dd = top[(sx, sz)] - yhi, bot[(sx, sz)] - ylo
            assert du <= 0 and dd >= 0, "偏移方向错误"
            if du: offs.append((CS[(sx, 1, sz)], "Y", du))
            if dd: offs.append((CS[(sx, 0, sz)], "Y", dd))
        assert offs, "斜面件没有偏移"
        arr = lt_tbox.encode([x0 + M, ylo, z0 + M, x1 + M, yhi, z1 + M], offs)
        self.TB.append((MAT[k], [int(v) for v in arr]))
        self.cnt[tag] += 1
    def text(self, k, s, size, xc, yc, zl, facing):
        m = text_mask(s, size)
        h, w = m.shape
        ytop, n = yc + h // 2, 0
        for j in range(h):
            for i in range(w):
                if m[j, i]:
                    x = (xc + w // 2 - 1 - i) if facing == "N" else (xc - w // 2 + i)
                    n += self.px(k, x, ytop - 1 - j, zl)
        self.cnt["text"] += n

def flat(v):
    return {(0, 0): v, (1, 0): v, (0, 1): v, (1, 1): v}
def zramp(v0, v1):  # sz=0（z 小侧）取 v0，sz=1 取 v1
    return {(0, 0): v0, (1, 0): v0, (0, 1): v1, (1, 1): v1}

def stripes_xy(S, x0, x1, y0, y1, zl, ox):
    for y in range(y0, y1):
        for x in range(x0, x1):
            S.paint("yellow" if ((x - ox + y) // 6) % 2 == 0 else "black", x, y, zl, x + 1, y + 1, zl + 1)

# ===================== 桥墩（x ox..ox+48）=====================
def pier(S, ox, label):
    S.fill("plinth", ox, 0, 8, ox + 48, 16, 88)                     # 墩座 16px（防贴地 AO）
    S.fill("pier", ox + 4, 16, 24, ox + 44, 120, 72)                 # 墩柱 40×48
    stripes_xy(S, ox + 4, ox + 44, 16, 32, 24, ox)                    # 警示斜纹（北/南）
    stripes_xy(S, ox + 4, ox + 44, 16, 32, 71, ox)
    for y in range(16, 32):                                           # 警示斜纹（西/东）
        for z in range(24, 72):
            k = "yellow" if ((z + y) // 6) % 2 == 0 else "black"
            S.paint(k, ox + 4, y, z, ox + 5, y + 1, z + 1)
            S.paint(k, ox + 43, y, z, ox + 44, y + 1, z + 1)
    for gy in (56, 88):                                               # 分缝
        S.paint("groove", ox + 4, gy, 24, ox + 44, gy + 1, 25)
        S.paint("groove", ox + 4, gy, 71, ox + 44, gy + 1, 72)
        S.paint("groove", ox + 4, gy, 24, ox + 5, gy + 1, 72)
        S.paint("groove", ox + 43, gy, 24, ox + 44, gy + 1, 72)
    for z0 in (24, 68):                                               # 东西面壁柱
        S.fill("pil", ox + 2, 32, z0, ox + 4, 120, z0 + 4)
        S.fill("pil", ox + 44, 32, z0, ox + 46, 120, z0 + 4)
    S.text("white", label, 16, ox + 24, 76, 24, "N")                  # 区号（北面：字向 x 递减）
    S.text("white", label, 16, ox + 24, 76, 71, "S")                  # 区号（南面：字向 x 递增）
    S.fill("cap", ox, 120, 24, ox + 48, 136, 72)                      # 锤头帽梁
    S.fill("cap", ox, 136, 16, ox + 48, 152, 80)
    S.slab("cap", ox, 16, ox + 48, 24, flat(136), zramp(132, 120), "cap")
    S.slab("cap", ox, 72, ox + 48, 80, flat(136), zramp(120, 132), "cap")
    stripes_xy(S, ox, ox + 48, 140, 148, 16, ox)                      # 帽梁警示带
    stripes_xy(S, ox, ox + 48, 140, 148, 79, ox)
    S.fill("bear", ox + 8, 152, 26, ox + 40, 160, 38)                 # 支座
    S.fill("bear", ox + 8, 152, 58, ox + 40, 160, 70)
    S.fill("rail", ox, 16, 34, ox + 4, 120, 36)                       # 西面检修梯
    S.fill("rail", ox, 16, 44, ox + 4, 120, 46)
    for y in range(22, 118, 6):
        S.fill("rail", ox + 1, y, 36, ox + 2, y + 1, 44)
    S.fill("jbox", ox + 44, 40, 40, ox + 50, 56, 56)                  # 东面接线箱
    S.fill("cyan", ox + 50, 49, 46, ox + 51, 53, 50)
    S.fill("cable", ox + 44, 56, 47, ox + 46, 120, 49)
    S.fill("pil", ox, 140, 6, ox + 4, 146, 16)                        # 灯笼缆挂点（西/东）
    S.fill("pil", ox + 44, 140, 6, ox + 48, 146, 16)

# ===================== 梁 + 桥面（x ox..ox+L）=====================
def deck(S, ox, L):
    S.fill("beam", ox, 176, 16, ox + L, 208, 80)                      # 钢箱梁腹板段
    S.fill("beam", ox, 160, 28, ox + L, 176, 68)                      # 梁底芯
    for x0 in range(0, L, 64):                                        # 梁底倒角（每 64px 一件）
        x1 = min(x0 + 64, L)
        S.slab("beam", ox + x0, 16, ox + x1, 28, flat(176), zramp(172, 160), "chamfer")
        S.slab("beam", ox + x0, 68, ox + x1, 80, flat(176), zramp(160, 172), "chamfer")
    for zl in (16, 79):
        S.paint("cyan", ox, 204, zl, ox + L, 206, zl + 1)             # 轨道网青色灯带
        S.paint("groove", ox, 200, zl, ox + L, 201, zl + 1)
    for rx in (0, 44, 60, 192):                                       # 加劲肋
        if rx + 4 <= L:
            S.fill("rib", ox + rx, 176, 14, ox + rx + 4, 204, 16)
            S.fill("rib", ox + rx, 176, 80, ox + rx + 4, 204, 82)
    S.fill("rib", ox, 208, 16, ox + L, 220, 18)                       # 护栏
    S.fill("rib", ox, 208, 78, ox + L, 220, 80)
    for p in range(0, L, 32):
        S.fill("mast", ox + p, 220, 16, ox + p + 2, 226, 18)
        S.fill("mast", ox + p, 220, 78, ox + p + 2, 226, 80)
    S.fill("rail", ox, 226, 16, ox + L, 228, 18)
    S.fill("rail", ox, 226, 78, ox + L, 228, 80)
    stripes_xy(S, ox, ox + min(48, L), 208, 220, 16, ox)              # 墩位护栏警示
    stripes_xy(S, ox, ox + min(48, L), 208, 220, 79, ox)
    S.fill("trough", ox, 208, 20, ox + L, 214, 28)                    # 电缆槽
    S.fill("ballast", ox, 208, 30, ox + L, 212, 66)                   # 道床
    for sx in range(0, L, 8):
        S.fill("sleeper", ox + sx + 2, 212, 32, ox + sx + 5, 214, 64)
    S.fill("rail", ox, 214, 36, ox + L, 217, 38)                      # 钢轨
    S.fill("rail", ox, 214, 58, ox + L, 217, 60)
    S.fill("wire", ox, 246, 47, ox + L, 247, 48)                      # 接触线
    R, cy, cz = 7, 168, 92                                            # 南侧水管
    for dy in range(-R - 1, R + 1):
        for dz in range(-R - 1, R + 1):
            d2 = (dy + 0.5) ** 2 + (dz + 0.5) ** 2
            if d2 <= R * R:
                S.fill("pipe", ox, cy + dy, cz + dz, ox + L, cy + dy + 1, cz + dz + 1)
            elif d2 <= (R + 1) ** 2 and L > 130:
                S.fill("cyan", ox + 128, cy + dy, cz + dz, ox + 130, cy + dy + 1, cz + dz + 1)
    for hx in (16, 72, 184, 240):                                     # 水管吊架
        if hx + 3 <= L:
            S.fill("mast", ox + hx, 178, 80, ox + hx + 3, 182, 93)
            S.fill("mast", ox + hx, 175, 91, ox + hx + 3, 178, 93)

# ===================== 跨中件（只在标准跨）=====================
def span_mid(S, ox):
    S.text("white", "轨道一号线", 16, ox + 128, 188, 16, "N")
    S.text("white", "轨道一号线", 16, ox + 128, 188, 79, "S")
    for dx in (96, 160):                                              # 梁底琥珀下照
        S.fill("amber", ox + dx - 3, 158, 45, ox + dx + 3, 160, 51)
    S.fill("mast", ox + 224, 180, 80, ox + 228, 268, 84)              # 接触网杆
    for yb in (186, 198):
        S.fill("pil", ox + 223, yb, 80, ox + 229, yb + 4, 85)
    S.fill("mast", ox + 225, 256, 46, ox + 227, 260, 84)
    S.fill("insul", ox + 224, 255, 70, ox + 228, 261, 74)
    S.fill("wire", ox + 225, 247, 47, ox + 226, 256, 48)
    S.fill("red", ox + 224, 268, 80, ox + 228, 271, 84)
    xa, xb, ya, sag = 48, 256, 141, 30                                # 北侧灯笼缆（墩到墩）
    xm, half = (xa + xb) / 2.0, (xb - xa) / 2.0
    yf = lambda x: ya - sag * (1 - ((x - xm) / half) ** 2)
    low = {}
    for x in range(xa, xb):
        y0, y1 = int(round(yf(x))), int(round(yf(x + 1)))
        low[x] = min(y0, y1)
        S.fill("cable", ox + x, low[x], 8, ox + x + 1, max(y0, y1) + 2, 10)
    for xc in range(72, 240, 24):                                     # 红灯笼 ×7
        yc = low[xc]
        S.fill("cable", ox + xc - 1, yc - 3, 8, ox + xc + 1, yc, 10)
        S.fill("gold", ox + xc - 2, yc - 4, 7, ox + xc + 2, yc - 3, 11)
        S.fill("red", ox + xc - 2, yc - 11, 7, ox + xc + 2, yc - 4, 11)
        S.fill("red", ox + xc - 3, yc - 10, 6, ox + xc + 3, yc - 5, 12)
        S.fill("gold", ox + xc - 2, yc - 12, 7, ox + xc + 2, yc - 11, 11)
        S.fill("red", ox + xc - 1, yc - 15, 8, ox + xc + 1, yc - 12, 10)
        S.cnt["lantern"] += 1

# ===================== 自检 + 贪心合并 + 导出 =====================
def greedy(S):
    G, out = S.G, []
    for mi in range(1, len(S.names) + 1):
        Rm = (G == mi)
        if not Rm.any():
            continue
        xs = np.nonzero(Rm.any(axis=(1, 2)))[0]
        for x in range(int(xs[0]), int(xs[-1]) + 1):
            sl = Rm[x]
            while True:
                y, z = divmod(int(sl.argmax()), NZ)
                if not sl[y, z]:
                    break
                r = sl[y, z:]
                z2 = z + (len(r) if r.all() else int(r.argmin()))
                y2 = y + 1
                while y2 < NY and sl[y2, z:z2].all():
                    y2 += 1
                x2 = x + 1
                while x2 < S.NX and Rm[x2, y:y2, z:z2].all():
                    x2 += 1
                Rm[x:x2, y:y2, z:z2] = False
                out.append((mi, [x, y, z, x2, y2, z2]))
    return out

def export(S, OUT, NAME):
    if os.path.exists(OUT):
        os.remove(OUT)
    for blk, v in S.TB:
        x0, y0, z0, x1, y1, z1 = v[:6]
        assert 0 <= x0 < x1 <= S.NX and 0 <= y0 < y1 <= NY and 0 <= z0 < z1 <= NZ, "可变形盒越界 %s" % v[:6]
        assert not S.G[x0:x1, y0:y1, z0:z1].any(), "可变形盒与体素重叠 %s" % v[:6]
    V = greedy(S)
    W = np.zeros_like(S.G)
    for mi, b in V:
        W[b[0]:b[3], b[1]:b[4], b[2]:b[5]] = mi
    assert np.array_equal(W, S.G), "体素贪心合并不无损"
    allb = [(S.names[mi - 1], b) for mi, b in V] + S.TB
    lo = [min(b[i] for _, b in allb) for i in range(3)]
    hi = [max(b[i + 3] for _, b in allb) for i in range(3)]
    base = [l // 16 * 16 for l in lo]
    sh = lambda b: [b[i] - base[i % 3] if i < 6 else b[i] for i in range(len(b))]
    by = {}
    for blk, b in allb:
        by.setdefault(blk, []).append("[I;%s]" % ",".join(map(str, sh(b))))
    parts = []
    for blk, arrs in by.items():
        if len(arrs) == 1:
            parts.append('{bBox:%s,tile:{block:"%s"}}' % (arrs[0], blk))
        else:
            parts.append('{boxes:[%s],tile:{block:"%s"}}' % (",".join(arrs), blk))
    mn = [lo[i] - base[i] for i in range(3)]
    sz = [hi[i] - lo[i] for i in range(3)]
    t = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (",".join(parts), *mn, *sz, len(allb))
    t = lt_root.fix(t, NAME, tag=OUT)
    io.open(OUT, "w", encoding="utf-8").write(t)
    nbytes = len(t.encode("utf-8"))
    print("== %s（%s）" % (OUT, NAME))
    print("   盒子 %d（体素 %d + 可变形 %d：梁底倒角 %d / 帽梁斜底 %d），字节 %d" % (
        len(allb), len(V), len(S.TB), S.cnt["chamfer"], S.cnt["cap"], nbytes))
    print("   尺寸 %d×%d×%d px = %.2f×%.2f×%.2f 格；min=%s；文字像素 %d；灯笼 %d" % (
        sz[0], sz[1], sz[2], sz[0] / 16.0, sz[1] / 16.0, sz[2] / 16.0, mn, S.cnt["text"], S.cnt["lantern"]))
    return mn

def build(parts):
    L = sum(256 if p[0] == "unit" else 48 for p in parts)
    S, ox = Scene(L), 0
    for kind, label in parts:
        pier(S, ox, label)
        if kind == "unit":
            deck(S, ox, UNIT); span_mid(S, ox); ox += UNIT
        else:
            deck(S, ox, PIER); ox += PIER
    return S

MN = {}
MN["kit"] = export(build([("unit", "B-01"), ("unit", "B-02"), ("end", "B-03")]), "bridge_kit.txt", "轨道桥_试装段")
MN["u4"] = export(build([("unit", "B-04")]), "bridge_unit_B04.txt", "轨道桥_标准跨_B04")
MN["u5"] = export(build([("unit", "B-05")]), "bridge_unit_B05.txt", "轨道桥_标准跨_B05")
MN["e6"] = export(build([("end", "B-06")]), "bridge_end_B06.txt", "轨道桥_端墩_B06")
assert len(set(tuple(v) for v in MN.values())) == 1, "各文件 min 不一致，拼接会错位：%s" % MN
print("   拼接原点自检：4 个文件 min 一致 = %s —— PASS" % MN["kit"])
print("== 接口（标准跨局部坐标，px；16px=1格）")
print("   模数：标准跨 256（16 格）沿 x；墩占 x0..48（跨西端）；端墩件 48；拼接 = 每份东移 16 格")
print("   桥宽 z16..80（4 格），中线 z48；北侧挂件区 z0..16，南侧挂件区 z80..104")
print("   墩座 y0..16 / 墩柱 y16..120 / 帽梁 y120..152 / 支座 y152..160 / 梁底 y160 / 梁顶 y208")
print("   轨顶 y217，轨距中心 z37 与 z59；护栏扶手 y226..228；接触线 y246 z47；网杆在 x224 南侧")
print("   桥下净空 160px = 10 格；灯笼缆 z8..10，墩挂点 y140..146，垂度 30px")
print("   水管中心 (y168, z92) R7，吊架 x16/72/184/240；灯带 y204..206（梁两侧，轨道网=青）")
print("== 材质：")
for k, (h, kd) in PAL.items():
    print("   %-8s %s %-5s → %s" % (k, h, kd, MAT[k]))
grp = {}
for k in PAL:
    grp.setdefault(MAT[k], []).append(k)
for b, ks in grp.items():
    if len(ks) > 1:
        print("   [同块] %s ← %s（只提示，不拦截）" % (b, "/".join(ks)))
