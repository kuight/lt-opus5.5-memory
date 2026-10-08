# -*- coding: utf-8 -*-
# lt_shop1_exec.py —— 【执行侧尝试 · EXEC ATTEMPT】桥下三档店铺 v1
#   样本 A：B-08 门洞破烂小摊（东西 3 格 × 南北 4 格，高 ~5.6 格）
#   样本 B：B-08~B-09 净跨豪华大店（东西 12 格 + 竖挂招牌，高 ~10 格以内）
# 说明：本文件由「执行侧」自写自跑（设计侧离线期间的能力测试件）。设计侧恢复后可按
#       git tag pre-exec-attempt（= aa9d3a8）整体比对/回退，或直接删除本脚本与其产物。
# 用法：在 E:\work\建筑\ 下运行  python lt_shop1_exec.py  → shop1_exec_A.txt / shop1_exec_B.txt
# 规则自查（常错清单）：#1 每个新件先与已登记 piece AABB 相交断言（撞了直接报是谁撞谁）；
#   #3 不等距/不等高/新旧混排；#7 斜面不落贴地格（一律 16px 基座/柱础托起）；
#   #8 可变形盒只许向内偏移；#16 做旧成片（锈水痕/泥污/掉漆/补板铆钉/外挂线缆/坏灯）。
import os, sys, io, math, random
import numpy as np
import lt_colors, lt_root, lt_tbox
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("需要 Pillow：停下，不要自己装包")

M = 24

def font_path():
    for fn in ("simhei.ttf", "msyh.ttc", "simsun.ttc"):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fn)
        if os.path.exists(p):
            return p
    raise SystemExit("找不到中文字体：停下")
FONT = ImageFont.truetype(font_path(), 16)

PAL = {
    "plinth": ("#1E2329", "solid"), "steel": ("#4F5966", "solid"), "pil": ("#6B7685", "solid"),
    "wall":   ("#3A424D", "solid"), "wall2": ("#4A5462", "solid"), "tin":  ("#6E7884", "solid"),
    "plate":  ("#7D8794", "solid"), "dark":  ("#2A3038", "solid"), "top":  ("#7A8594", "solid"),
    "rust":   ("#6B4A3A", "solid"), "rust2": ("#4A3328", "solid"), "stain": ("#33383F", "solid"),
    "fade":   ("#8E7F4A", "solid"), "sign":  ("#121519", "solid"), "white": ("#E6E9EC", "solid"),
    "gold":   ("#C9A23A", "solid"), "hoop":  ("#3A3F45", "solid"), "cable": ("#15181C", "solid"),
    "pane":   ("#7FD8E8", "trans"), "tarp":  ("#C8CED4", "trans"),
    "cyan":   ("#00E5FF", "glow"), "amber": ("#FFB347", "glow"),
    "magenta": ("#FF2A6D", "glow"), "red": ("#FF3F2F", "glow"),
}
MAT = {}
for _k, (_h, _kd) in PAL.items():
    _b = lt_colors.fc(_h, _kd)
    assert isinstance(_b, str) and _b, "lt_colors.fc 没返回方块名: %s" % _k
    MAT[_k] = _b

CS = {(0, 0, 0): "WDN", (0, 0, 1): "WDS", (1, 0, 0): "EDN", (1, 0, 1): "EDS",
      (0, 1, 0): "WUN", (0, 1, 1): "WUS", (1, 1, 0): "EUN", (1, 1, 1): "EUS"}


class S:
    """一个小方块样品：体素 + 可变形盒斜面 + 相交登记表（常错#1 的机器化保障）"""
    def __init__(self, NX, NY, NZ, tag):
        self.NX, self.NY, self.NZ, self.tag = NX, NY, NZ, tag
        self.G = np.zeros((NX, NY, NZ), dtype=np.uint8)
        self.VOX = np.zeros((NX, NY, NZ), dtype=bool)
        self.NAMES, self.TB, self.OCC = [], [], []
        self.cnt = {"fill": 0, "paint": 0, "slab": 0, "text": 0}
        self.face_src = "sign"

    def mid(self, k):
        b = MAT[k]
        if b not in self.NAMES:
            self.NAMES.append(b)
            assert len(self.NAMES) < 250, "材质过多"
        return self.NAMES.index(b) + 1

    def chk(self, name, box):
        assert 0 <= box[0] < box[3] <= self.NX and 0 <= box[1] < box[4] <= self.NY \
            and 0 <= box[2] < box[5] <= self.NZ, "越界 %s %s" % (name, box)
        for (n2, b2) in self.OCC:
            if box[0] < b2[3] and b2[0] < box[3] and box[1] < b2[4] and b2[1] < box[4] \
               and box[2] < b2[5] and b2[2] < box[5]:
                raise AssertionError("【常错#1】新件 %s %s 与已有件 %s %s 相交" % (name, box, n2, b2))

    def fill(self, k, name, x0, y0, z0, x1, y1, z1):
        box = (x0 + M, y0, z0 + M, x1 + M, y1, z1 + M)
        self.chk(name, box)
        self.OCC.append((name, box))
        self.G[box[0]:box[3], box[1]:box[4], box[2]:box[5]] = self.mid(k)
        self.VOX[box[0]:box[3], box[1]:box[4], box[2]:box[5]] = True
        self.cnt["fill"] += 1

    def paint(self, k, src, name, x0, y0, z0, x1, y1, z1):
        """只在已存在且材质 == src 的体素上换色（做旧 / 灯带 / 文字）：不动几何、不登记相交"""
        box = (x0 + M, y0, z0 + M, x1 + M, y1, z1 + M)
        assert 0 <= box[0] < box[3] <= self.NX and 0 <= box[1] < box[4] <= self.NY \
            and 0 <= box[2] < box[5] <= self.NZ, "paint 越界 %s %s" % (name, box)
        sub = self.G[box[0]:box[3], box[1]:box[4], box[2]:box[5]]
        ms = self.mid(src)
        n = int((sub == ms).sum())
        sub[sub == ms] = self.mid(k)
        self.cnt["paint"] += n
        return n

    def slab(self, k, name, x0, z0, x1, z1, top, bot):
        """Y 偏移斜面/斜顶（可变形盒）：四角共面、板厚 > 0、偏移只许向内"""
        for d in (top, bot):
            assert d[(0, 0)] + d[(1, 1)] == d[(1, 0)] + d[(0, 1)], "四角不共面 %s %s" % (name, d)
        for c in top:
            assert top[c] > bot[c], "板厚 ≤0 %s" % name
        yhi, ylo = max(top.values()), min(bot.values())
        assert x0 < x1 and z0 < z1, "slab 区间非法 %s" % name
        box = (x0 + M, ylo, z0 + M, x1 + M, yhi, z1 + M)
        self.chk(name + "(斜面)", box)
        offs = []
        for (sx, sz) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            du, dd = top[(sx, sz)] - yhi, bot[(sx, sz)] - ylo
            assert du <= 0 and dd >= 0, "偏移方向错误（只许向内）%s" % name
            if du:
                offs.append((CS[(sx, 1, sz)], "Y", du))
            if dd:
                offs.append((CS[(sx, 0, sz)], "Y", dd))
        if not offs:                      # 平板（无偏移）→ 直接落成体素件
            self.OCC.pop()
            self.fill(k, name, x0, ylo, z0, x1, yhi, z1)
            return
        self.OCC.append((name + "(斜面)", box))
        self.TB.append((MAT[k], [int(v) for v in lt_tbox.encode(list(box), offs)]))
        self.cnt["slab"] += 1

    def glyphs(self, text):
        out = []
        for ch in text:
            l, t, r, b = FONT.getbbox(ch)
            assert r > l and b > t, "字 %s 渲染为空" % ch
            im = Image.new("L", (r - l, b - t), 0)
            ImageDraw.Draw(im).text((-l, -t), ch, font=FONT, fill=255)
            a = np.array(im) > 128
            ys, xs = np.nonzero(a)
            a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            assert a.shape[0] <= 16 and a.shape[1] <= 16, "字 %s 超过 16px：%s" % (ch, a.shape)
            out.append(a)
        return out

    def text_n(self, k, s, xc, ytop, zface, gap=4):
        """北面牌横排：观察者面朝南（左手 = +x）⇒ 整串自 x 大往 x 小排，字内第 0 列也在 x 最大处"""
        gs = self.glyphs(s)
        tot = sum(g.shape[1] for g in gs) + gap * (len(gs) - 1)
        cur = xc + tot // 2 - 1
        n0 = self.cnt["paint"]
        for g in gs:
            h, w = g.shape
            for j in range(h):
                for i in range(w):
                    if g[j, i]:
                        xx = cur - i
                        self.paint(k, self.face_src, "字", xx, ytop - 1 - j, zface, xx + 1, ytop - j, zface + 1)
            cur -= w + gap
        self.cnt["text"] += self.cnt["paint"] - n0

    def text_v(self, k, s, xface, ytop, z0, z1, facing, gap=8):
        """竖挂牌：整串自上而下叠排；facing='E'（左手 = +z ⇒ 字第 0 列在 z 最大处）/'W'（左手 = −z）"""
        gs = self.glyphs(s)
        zc = (z0 + z1) // 2
        cur = ytop
        n0 = self.cnt["paint"]
        for g in gs:
            h, w = g.shape
            for j in range(h):
                for i in range(w):
                    if g[j, i]:
                        zz = (zc + w // 2 - 1 - i) if facing == "E" else (zc - w // 2 + i)
                        self.paint(k, self.face_src, "字", xface, cur - 1 - j, zz, xface + 1, cur - j, zz + 1)
            cur -= h + gap
        self.cnt["text"] += self.cnt["paint"] - n0

    def preview(self, prefix):
        """自检用投影图（lt_geom 的 PNG 只画可变形盒，看不清体素外观）"""
        lut = {}
        for k, (h, kd) in PAL.items():
            if MAT[k] in self.NAMES:
                lut[self.NAMES.index(MAT[k]) + 1] = tuple(int(h[1 + j * 2:3 + j * 2], 16) for j in range(3))
        G, NX, NY, NZ = self.G, self.NX, self.NY, self.NZ
        bg = (18, 20, 24)
        front = Image.new("RGB", (NX, NY)); pf = front.load()
        side = Image.new("RGB", (NZ, NY)); ps = side.load()
        top = Image.new("RGB", (NX, NZ)); pt = top.load()
        for x in range(NX):
            for y in range(NY):
                nz = np.nonzero(G[x, y, :])[0]
                # 真实"从北看南"的方向：观察者左手 = +x ⇒ 屏幕上 +x 在左，故列序翻转
                pf[NX - 1 - x, NY - 1 - y] = lut.get(int(G[x, y, nz[0]]), (70, 74, 80)) if len(nz) else bg
        for z in range(NZ):
            for y in range(NY):
                nx = np.nonzero(G[:, y, z])[0]
                ps[z, NY - 1 - y] = lut.get(int(G[nx[0], y, z]), (70, 74, 80)) if len(nx) else bg
        east = Image.new("RGB", (NZ, NY)); pe = east.load()
        for z in range(NZ):
            for y in range(NY):
                nx = np.nonzero(G[:, y, z])[0]
                # 真实"从东看西"：观察者左手 = +z ⇒ 屏幕上 +z 在左，故列序翻转
                pe[NZ - 1 - z, NY - 1 - y] = lut.get(int(G[nx[-1], y, z]), (70, 74, 80)) if len(nx) else bg
        for x in range(NX):
            for z in range(NZ):
                ny = np.nonzero(G[x, :, z])[0]
                if len(ny):
                    c = lut.get(int(G[x, ny[-1], z]), (70, 74, 80))
                    f = 0.55 + 0.45 * (ny[-1] / float(NY))
                    pt[x, z] = tuple(int(v * f) for v in c)
                else:
                    pt[x, z] = bg
        front.save(prefix + "_view_front.png")
        side.save(prefix + "_view_side.png")
        east.save(prefix + "_view_east.png")
        top.save(prefix + "_view_top.png")
        print("   预览图：%s_view_front/ _side/ _east/ _top.png（1px = 1px，仅自检用）" % prefix)

    def greedy(self):
        out = []
        for mi in range(1, len(self.NAMES) + 1):
            Rm = (self.G == mi)
            if not Rm.any():
                continue
            xs = np.nonzero(Rm.any(axis=(1, 2)))[0]
            for x in range(int(xs[0]), int(xs[-1]) + 1):
                sl = Rm[x]
                while True:
                    y, z = divmod(int(sl.argmax()), self.NZ)
                    if not sl[y, z]:
                        break
                    r = sl[y, z:]
                    z2 = z + (len(r) if r.all() else int(r.argmin()))
                    y2 = y + 1
                    while y2 < self.NY and sl[y2, z:z2].all():
                        y2 += 1
                    x2 = x + 1
                    while x2 < self.NX and Rm[x2, y:y2, z:z2].all():
                        x2 += 1
                    Rm[x:x2, y:y2, z:z2] = False
                    out.append((mi, [x, y, z, x2, y2, z2]))
        return out

    def export(self, OUT, NAME):
        if os.path.exists(OUT):
            os.remove(OUT)
        for blk, v in self.TB:
            b = v[:6]
            assert not self.VOX[b[0]:b[3], b[1]:b[4], b[2]:b[5]].any(), "可变形盒与体素重叠 %s" % (b,)
        V = self.greedy()
        W = np.zeros_like(self.G)
        for mi, b in V:
            W[b[0]:b[3], b[1]:b[4], b[2]:b[5]] = mi
        assert np.array_equal(W, self.G), "体素贪心合并不无损"
        allb = [(self.NAMES[mi - 1], b) for mi, b in V] + self.TB
        lo = [min(b[i] for _, b in allb) for i in range(3)]
        hi = [max(b[i + 3] for _, b in allb) for i in range(3)]
        base = [l // 16 * 16 for l in lo]
        sh = lambda b: [b[i] - base[i % 3] if i < 6 else b[i] for i in range(len(b))]
        by = {}
        for blk, b in allb:
            by.setdefault(blk, []).append("[I;%s]" % ",".join(map(str, sh(b))))
        parts = [('{bBox:%s,tile:{block:"%s"}}' % (a[0], blk)) if len(a) == 1 else
                 ('{boxes:[%s],tile:{block:"%s"}}' % (",".join(a), blk)) for blk, a in by.items()]
        mn = [lo[i] - base[i] for i in range(3)]
        sz = [hi[i] - lo[i] for i in range(3)]
        t = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (",".join(parts), *mn, *sz, len(allb))
        t = lt_root.fix(t, NAME, tag=OUT)
        io.open(OUT, "w", encoding="utf-8").write(t)
        nb = len(t.encode("utf-8"))
        print("== %s（%s）" % (OUT, NAME))
        print("   盒子 %d（体素 %d + 可变形斜面 %d），字节 %d" % (len(allb), len(V), len(self.TB), nb))
        print("   尺寸 %d×%d×%d px = %.2f×%.2f×%.2f 格；min=%s" % (
            sz[0], sz[1], sz[2], sz[0] / 16.0, sz[1] / 16.0, sz[2] / 16.0, mn))
        print("   体素件 %d / 换色像素 %d（含文字 %d）/ 斜面 %d" % (
            self.cnt["fill"], self.cnt["paint"], self.cnt["text"], self.cnt["slab"]))
        return nb


# =====================================================================================
# 样本 A：门洞破烂小摊（东西 3 格 × 南北 4 格；临街朝北 = z 小侧）
# =====================================================================================
def build_A():
    A = S(48 + 2 * M, 128, 64 + 2 * M + 24, "A")
    rng = random.Random(20261008)
    A.fill("plinth", "基座16px", -2, 0, -2, 50, 16, 66)
    A.fill("wall", "西墙", 0, 16, 0, 2, 64, 64)
    A.fill("wall", "东墙", 46, 16, 0, 48, 64, 64)
    A.fill("wall", "南墙", 2, 16, 62, 46, 64, 64)
    A.fill("tin", "柜台身", 4, 16, 6, 44, 32, 18)
    A.fill("top", "柜台面", 4, 32, 6, 44, 34, 20)
    A.paint("amber", "tin", "柜台下暖光", 6, 26, 6, 42, 30, 7)
    A.fill("steel", "顶梁N", -2, 64, -2, 50, 68, 0)
    A.fill("steel", "顶梁S", -2, 64, 64, 50, 68, 66)
    A.fill("steel", "顶梁W", -2, 64, 0, 0, 68, 64)
    A.fill("steel", "顶梁E", 48, 64, 0, 50, 68, 64)
    for (n, x0, z0) in (("支杆1", 0, 0), ("支杆2", 46, 0), ("支杆3", 0, 62), ("支杆4", 46, 62)):
        A.fill("steel", n, x0, 68, z0, x0 + 2, 74, z0 + 2)
    A.slab("tin", "顶棚主片", -2, 0, 50, 64, {(0, 0): 76, (1, 0): 76, (0, 1): 84, (1, 1): 84},
           {(0, 0): 74, (1, 0): 74, (0, 1): 82, (1, 1): 82})
    A.slab("tin", "顶棚挑出", -2, -12, 50, 0, {(0, 0): 74, (1, 0): 74, (0, 1): 76, (1, 1): 76},
           {(0, 0): 72, (1, 0): 72, (0, 1): 74, (1, 1): 74})
    A.fill("plinth", "前柱础W", -4, 0, -16, 4, 16, -8)
    A.fill("plinth", "前柱础E", 44, 0, -16, 52, 16, -8)
    A.fill("steel", "前柱W", 0, 16, -14, 2, 72, -12)
    A.fill("steel", "前柱E", 46, 16, -14, 48, 72, -12)
    A.fill("sign", "横匾", 10, 74, -16, 38, 90, -14)
    A.face_src = "sign"
    A.text_n("magenta", "面", 24, 90, -16)
    A.fill("steel", "灯箱支架", 48, 52, 10, 50, 56, 22)
    A.fill("sign", "竖挂灯箱", 50, 44, 8, 52, 76, 24)
    A.face_src = "sign"
    A.text_v("magenta", "面", 51, 76, 8, 24, "E")
    A.text_v("magenta", "面", 50, 76, 8, 24, "W")
    A.fill("steel", "檐下灯座", 2, 70, -13, 46, 72, -11)
    for (x0, x1) in ((4, 14), (20, 30), (36, 46)):
        A.fill("amber", "檐下亮段", x0, 68, -13, x1, 70, -11)
    A.fill("dark", "檐下灭段", 15, 68, -13, 19, 70, -11)
    A.fill("cyan", "摊内灯条", 2, 62, 30, 46, 64, 32)
    A.fill("plate", "东墙补板1", 48, 30, 40, 49, 42, 54)
    A.fill("plate", "东墙补板2", 48, 46, 26, 49, 58, 38)
    for yy in (31, 40, 55):
        A.paint("top", "plate", "补板铆钉", 48, yy, 41, 49, yy + 1, 53)
    A.fill("cable", "外挂电缆1", 49, 16, 4, 51, 62, 6)
    A.fill("cable", "外挂电缆2", 51, 20, 6, 53, 58, 8)
    for yy in (20, 40, 58):
        A.paint("steel", "cable", "卡箍", 49, yy, 4, 51, yy + 2, 6)
    A.fill("tarp", "塑料布", -4, 40, -6, -3, 62, 26)
    A.fill("steel", "塑料布挂杆", -4, 62, -6, -3, 64, 26)
    A.fill("rust", "破桶1", 6, 16, -8, 14, 30, -2)
    A.fill("rust2", "破桶2", 36, 16, -8, 44, 28, -2)
    A.fill("top", "板凳1面", 22, 22, 22, 34, 24, 30)
    A.fill("steel", "板凳1腿1", 23, 16, 23, 25, 22, 25)
    A.fill("steel", "板凳1腿2", 31, 16, 27, 33, 22, 29)
    A.fill("top", "板凳2面", 22, 22, 36, 34, 24, 44)
    A.fill("steel", "板凳2腿1", 23, 16, 37, 25, 22, 39)
    A.fill("steel", "板凳2腿2", 31, 16, 41, 33, 22, 43)
    for y0 in (40, 48, 56):
        A.fill("tin", "蒸笼板", 6, y0, 52, 42, y0 + 2, 62)
    A.fill("steel", "蒸笼柱W", 6, 16, 50, 8, 58, 52)
    A.fill("steel", "蒸笼柱E", 40, 16, 50, 42, 58, 52)
    # ---- 做旧（成片）----
    for (x0, z0, ln) in ((0, 4, 22), (0, 30, 14), (46, 10, 18), (46, 34, 24), (46, 54, 12)):
        w = rng.choice((2, 3, 4))
        for y in range(64 - ln, 64):
            A.paint("rust", "wall", "锈水痕", x0, y, z0, x0 + 1, y + 1, z0 + w)
    A.paint("rust2", "wall", "锈水痕口", 0, 62, 4, 1, 64, 12)
    for x0 in (2, 12, 24, 34, 44):
        hh = rng.randint(6, 24)
        for x in range(x0, min(x0 + 6, 46)):
            hh = max(4, min(26, hh + rng.randint(-3, 3)))
            A.paint("stain", "wall", "墙脚泥污", x, 16, 62, x + 1, 16 + hh, 63)
    for x0 in (0, 46):
        hh = rng.randint(5, 20)
        for z in range(6, 60):
            hh = max(4, min(24, hh + rng.randint(-3, 3)))
            A.paint("stain", "wall", "墙脚泥污侧", x0, 16, z, x0 + 1, 16 + hh, z + 1)
    for x in range(4, 44, 2):
        for y in range(18, 62, 2):
            r = rng.random()
            if r < 0.14:
                A.paint("fade" if r < 0.08 else "rust2", "tin", "掉漆", x, y, 6, x + 2, y + 2, 7)
    A.paint("stain", "tin", "架板污渍", 8, 40, 54, 40, 41, 60)
    A.paint("stain", "plinth", "基座油污", -2, 15, -2, 50, 16, 66)
    return A


# =====================================================================================
# 样本 B：净跨豪华大店（东西 12 格；一层玻璃门面 + 金属雨棚 + 二层 + 竖挂霓虹招牌）
# =====================================================================================
def build_B():
    B = S(224 + 2 * M, 200, 96 + 2 * M, "B")
    rng = random.Random(20261009)
    B.fill("plinth", "基座", -4, 0, -4, 196, 16, 68)
    B.fill("plinth", "台阶下", 20, 0, -20, 172, 8, -12)
    B.fill("plinth", "台阶上", 20, 8, -12, 172, 16, -4)
    for (n, x0) in (("立柱1", 0), ("立柱2", 60), ("立柱3", 128), ("立柱4", 188)):
        B.fill("pil", n, x0, 16, 0, x0 + 4, 96, 4)
    for (n, x0, x1) in (("玻璃1", 4, 60), ("玻璃2", 64, 128), ("玻璃3", 132, 188)):
        B.fill("pane", n, x0, 16, 0, x1, 96, 2)
    B.fill("wall2", "侧墙W", 0, 16, 4, 4, 96, 60)
    B.fill("wall2", "侧墙E", 188, 16, 4, 192, 96, 60)
    B.fill("wall2", "后墙", 0, 16, 60, 192, 96, 64)
    B.fill("wall", "后墙内衬", 4, 20, 58, 188, 92, 60)
    B.fill("steel", "门楣", -2, 96, -2, 194, 104, 4)
    B.paint("cyan", "steel", "门楣灯带", 2, 98, -2, 190, 100, -1)
    for x0 in (1, 61, 129, 189):
        B.paint("cyan", "pil", "立柱竖灯条", x0, 20, 0, x0 + 2, 92, 1)
    B.paint("amber", "plinth", "台阶灯", 20, 8, -4, 172, 10, -3)
    B.slab("steel", "雨棚N", -2, -18, 194, -2, {(0, 0): 104, (1, 0): 104, (0, 1): 104, (1, 1): 104},
           {(0, 0): 100, (1, 0): 100, (0, 1): 100, (1, 1): 100})
    B.slab("steel", "雨棚S", -2, 64, 194, 80, {(0, 0): 104, (1, 0): 104, (0, 1): 104, (1, 1): 104},
           {(0, 0): 100, (1, 0): 100, (0, 1): 100, (1, 1): 100})
    B.slab("steel", "雨棚W", -18, -2, -2, 64, {(0, 0): 104, (1, 0): 104, (0, 1): 104, (1, 1): 104},
           {(0, 0): 100, (1, 0): 100, (0, 1): 100, (1, 1): 100})
    B.slab("steel", "雨棚E", 194, -2, 210, 64, {(0, 0): 104, (1, 0): 104, (0, 1): 104, (1, 1): 104},
           {(0, 0): 100, (1, 0): 100, (0, 1): 100, (1, 1): 100})
    B.slab("steel", "雨棚角NW", -18, -18, -2, -2, {(0, 0): 96, (1, 0): 100, (0, 1): 100, (1, 1): 104},
           {(0, 0): 93, (1, 0): 97, (0, 1): 97, (1, 1): 101})
    B.slab("steel", "雨棚角NE", 194, -18, 210, -2, {(0, 0): 100, (1, 0): 96, (0, 1): 104, (1, 1): 100},
           {(0, 0): 97, (1, 0): 93, (0, 1): 101, (1, 1): 97})
    B.slab("steel", "雨棚角SW", -18, 64, -2, 80, {(0, 0): 100, (1, 0): 104, (0, 1): 96, (1, 1): 100},
           {(0, 0): 97, (1, 0): 101, (0, 1): 93, (1, 1): 97})
    B.slab("steel", "雨棚角SE", 194, 64, 210, 80, {(0, 0): 104, (1, 0): 100, (0, 1): 100, (1, 1): 96},
           {(0, 0): 101, (1, 0): 97, (0, 1): 97, (1, 1): 93})
    B.fill("cyan", "棚底灯带N", -2, 98, -18, 194, 100, -16)
    B.fill("cyan", "棚底灯带S", -2, 98, 78, 194, 100, 80)
    B.fill("amber", "棚下暖光", 20, 98, -13, 170, 99, -11)
    B.fill("cyan", "棚底灯带W", -18, 98, -2, -16, 100, 64)
    B.fill("cyan", "棚底灯带E", 208, 98, -2, 210, 100, 64)
    B.fill("steel", "一层屋面", -2, 104, -2, 194, 112, 66)
    B.fill("sign", "横匾", 30, 104, -4, 160, 130, -2)
    B.face_src = "sign"
    B.text_n("magenta", "合成蛋白", 95, 128, -4)
    B.fill("wall", "二层窗台", 16, 112, 8, 176, 116, 12)
    B.fill("wall", "二层过梁", 16, 134, 8, 176, 140, 12)
    B.fill("wall", "二层垛1", 16, 116, 8, 40, 134, 12)
    B.fill("wall", "二层垛2", 84, 116, 8, 108, 134, 12)
    B.fill("wall", "二层垛3", 152, 116, 8, 176, 134, 12)
    B.fill("pane", "二层窗1", 40, 116, 8, 84, 134, 10)
    B.fill("pane", "二层窗2", 108, 116, 8, 152, 134, 10)
    B.paint("amber", "pane", "窗内暖光1", 42, 118, 8, 82, 122, 9)
    B.paint("amber", "pane", "窗内暖光2", 110, 118, 8, 150, 122, 9)
    B.fill("wall2", "二层墙W", 16, 112, 12, 20, 140, 52)
    B.fill("wall2", "二层墙E", 172, 112, 12, 176, 140, 52)
    B.fill("wall2", "二层墙S", 16, 112, 52, 176, 140, 56)
    B.fill("steel", "女儿墙", 12, 140, 4, 180, 144, 60)
    B.fill("steel", "设备台", 24, 144, 16, 60, 148, 40)
    B.fill("plate", "冷凝机", 26, 148, 18, 58, 160, 38)
    B.fill("dark", "冷凝机百叶", 28, 150, 17, 56, 154, 18)
    B.fill("cyan", "冷凝机状态灯", 56, 150, 16, 58, 156, 18)
    B.fill("steel", "排气管", 62, 144, 24, 66, 168, 28)
    B.fill("cable", "屋顶电缆", 66, 148, 25, 214, 152, 27)
    B.fill("cable", "屋面电缆", 16, 144, 56, 56, 152, 60)
    B.fill("plate", "补板E", 192, 40, 20, 193, 56, 36)
    B.fill("plate", "补板W", -2, 32, 20, -1, 44, 34)
    for yy in (42, 52):
        B.paint("top", "plate", "补板铆钉", 192, yy, 21, 193, yy + 1, 35)
    B.fill("steel", "招牌杆础", 210, 0, 16, 222, 16, 28)
    B.fill("steel", "招牌杆", 214, 16, 20, 218, 164, 24)
    B.fill("cyan", "招牌杆灯条", 218, 16, 21, 219, 94, 23)
    B.fill("steel", "招牌支架", 218, 100, 18, 220, 148, 26)
    B.fill("sign", "竖挂牌", 220, 96, 4, 222, 152, 40)
    B.face_src = "sign"
    B.text_v("magenta", "食堂", 221, 142, 4, 40, "E")
    B.text_v("magenta", "食堂", 220, 142, 4, 40, "W")
    for (x0, z0, ln) in ((0, 20, 26), (0, 44, 18), (188, 30, 22), (188, 12, 16)):
        w = rng.choice((2, 3))
        for y in range(92 - ln, 92):
            B.paint("rust", "wall2", "锈水痕", x0, y, z0, x0 + 2, y + 1, z0 + w)
    for x0 in (20, 70, 120, 160):
        hh = rng.randint(4, 12)
        B.paint("stain", "wall2", "墙脚泥污", x0, 16, 63, x0 + 10, 16 + hh, 64)
    B.paint("stain", "plinth", "基座油污", -4, 15, -4, 196, 16, 68)
    return B


if __name__ == "__main__":
    print("== 【执行侧尝试】桥下三档店铺 v1")
    a = build_A()
    a.export("shop1_exec_A.txt", "桥下店铺_A_门洞破烂小摊")
    a.preview("shop1_exec_A")
    b = build_B()
    b.export("shop1_exec_B.txt", "桥下店铺_B_净跨豪华大店")
    b.preview("shop1_exec_B")
    print("== 材质：")
    for k, (h, kd) in PAL.items():
        print("  %-8s %s %-5s → %s" % (k, h, kd, MAT[k]))
    grp = {}
    for k in PAL:
        grp.setdefault(MAT[k], []).append(k)
    for b, ks in grp.items():
        if len(ks) > 1:
            print("  [同块] %s ← %s（只提示，不拦截）" % (b, "/".join(ks)))
