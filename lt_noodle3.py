# -*- coding: utf-8 -*-
# lt_noodle3.py —— 合成蛋白面馆 v3：去中式；金属雨棚 / 屋顶设备平台 / 竖挂霓虹招牌 / 夜景轮廓光
# （设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_noodle3.py  → noodle3.txt（需 Pillow + Windows 中文字体渲染招牌字）
# 做法：读入 lt_noodle1.py 原文（须 272a8a4c 开头），按锚点替换 + 插入 v3 代码后执行；一期逻辑不改，只停用飞檐。
# 参考：Blade Runner White Dragon 面摊（雨棚+柜台+霓虹）；香港竖挂招牌（垂直于立面、双面字）；
#       Blade Runner retrofitting（Syd Mead/Ridley Scott，设备外挂、管线外露）；
#       夜景照明"勾勒轮廓、突出重点、分层次"（古建/建筑夜景照明通用手法，取其方法不取其形式）
import io, hashlib

SRC = "lt_noodle1.py"
raw = io.open(SRC, "rb").read()
h = hashlib.sha256(raw).hexdigest().lower()
print("   lt_noodle1.py sha256 = %s" % h.upper())
assert h.startswith("272a8a4c"), "lt_noodle1.py 不是入库版本（应以 272a8a4c 开头），停止"
src = raw.decode("utf-8")


def rep(a, b):
    global src
    n = src.count(a)
    assert n == 1, "替换锚点出现 %d 次（应为 1）：%r" % (n, a)
    src = src.replace(a, b)


rep('OUT = "noodle1.txt"', 'OUT = "noodle3.txt"')
rep('NX, NY, NZ = 256, 256, 240', 'NX, NY, NZ = 256, 320, 240')
rep('"steel": ("#5C6774", "solid")', '"steel": ("#4F5966", "solid")')
rep('"rib": ("#5C6774", "solid")', '"rib": ("#7A8594", "solid")')
rep('"pane": ("#FFB347", "trans")', '"pane": ("#FFB347", "glow")')          # 舱窗改发光，不再像脏玻璃
rep('"roof": ("#4A5462", "solid"),',
    '"roof": ("#4A5462", "solid"), "cyan": ("#00E5FF", "glow"), "magenta": ("#FF2A6D", "glow"), '
    '"red": ("#FF3F3F", "glow"), "white": ("#C8CED4", "solid"), "sign": ("#121519", "solid"),')
rep('def eave_ring(x0, z0, x1, z1, a, t=3):',                               # 停用飞檐（原函数改名保留）
    'def eave_ring(x0, z0, x1, z1, a, t=3):\n    return\n\n\ndef _eave_ring_v1(x0, z0, x1, z1, a, t=3):')
rep('print("   飞檐剖面：出挑 %s px → 高度 %s px（翼角 %+d px）" % (FD, FV, 2 * FV[-1]))',
    'print("   飞檐：已停用（v3 去中式）")')
rep('"合成蛋白面馆_一期"', '"合成蛋白面馆_v3"')
rep('合成蛋白面馆 一期 生成完毕', '合成蛋白面馆 v3 生成完毕')

ADD = r'''
# ===================== v3：金属雨棚 / 屋顶设备平台 / 竖挂霓虹招牌 / 夜景轮廓光 =====================
CNT.update({"canopy": 0})
SIGN = u"合成面馆"


def extent(y, tag, fb=None):
    a = np.argwhere(G[:, y, :] > 0)
    if not len(a):
        assert fb is not None, "扫描 %s y=%d 没找到体素，停止" % (tag, y)
        print("   [回退] 扫描 %s y=%d 为空，用预设 %s" % (tag, y, fb))
        return fb
    x0, z0 = [int(v) - M for v in a.min(0)]
    x1, z1 = [int(v) - M + 1 for v in a.max(0)]
    print("   扫描 %s y=%d：x %d..%d  z %d..%d" % (tag, y, x0, x1, z0, z1))
    return x0, z0, x1, z1


def disk(k, cx, cz, r, y0, y1):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            if (x + 0.5 - cx) ** 2 + (z + 0.5 - cz) ** 2 <= r * r:
                fill(k, x, y0, z, x + 1, y1, z + 1)


def cable(k, A, B, sag, w=2):
    n = int(max(abs(B[i] - A[i]) for i in range(3)) * 3) + 1
    seen = set()
    for i in range(n + 1):
        t = i / float(n)
        p = [A[j] + (B[j] - A[j]) * t for j in range(3)]
        p[1] -= sag * 4 * t * (1 - t)
        q = tuple(int(round(v)) for v in p)
        if q not in seen:
            seen.add(q)
            fill(k, q[0], q[1], q[2], q[0] + w, q[1] + w, q[2] + w)
    return len(seen)


def canopy(x0, z0, x1, z1, a, W=24, D=4, t=3, glow=("amber", "cyan", "cyan", "cyan")):
    """平出挑金属雨棚：四边向外排水坡 D，四角 2D；只用 Y 偏移；棚底外沿 2px 发光条（N/S/W/E）"""
    lo, c2 = a - D, a - 2 * D
    ypiece("eave", x0, z0 - W, x1, z0, {(0, 0): lo, (1, 0): lo, (0, 1): a, (1, 1): a}, t, "canopy")
    ypiece("eave", x0, z1, x1, z1 + W, {(0, 0): a, (1, 0): a, (0, 1): lo, (1, 1): lo}, t, "canopy")
    ypiece("eave", x0 - W, z0, x0, z1, {(0, 0): lo, (0, 1): lo, (1, 0): a, (1, 1): a}, t, "canopy")
    ypiece("eave", x1, z0, x1 + W, z1, {(0, 0): a, (0, 1): a, (1, 0): lo, (1, 1): lo}, t, "canopy")
    ypiece("eave", x0 - W, z0 - W, x0, z0, {(0, 0): c2, (1, 0): lo, (0, 1): lo, (1, 1): a}, t, "canopy")
    ypiece("eave", x1, z0 - W, x1 + W, z0, {(0, 0): lo, (1, 0): c2, (0, 1): a, (1, 1): lo}, t, "canopy")
    ypiece("eave", x0 - W, z1, x0, z1 + W, {(0, 0): lo, (1, 0): a, (0, 1): c2, (1, 1): lo}, t, "canopy")
    ypiece("eave", x1, z1, x1 + W, z1 + W, {(0, 0): a, (1, 0): lo, (0, 1): lo, (1, 1): c2}, t, "canopy")
    yb = lo - t
    fill(glow[0], x0, yb - 2, z0 - W, x1, yb, z0 - W + 2)
    fill(glow[1], x0, yb - 2, z1 + W - 2, x1, yb, z1 + W)
    fill(glow[2], x0 - W, yb - 2, z0, x0 - W + 2, yb, z1)
    fill(glow[3], x1 + W - 2, yb - 2, z0, x1 + W, yb, z1)


def sign_glyphs(text):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise AssertionError("渲染招牌字需要 Pillow（缺失），停止")
    fp = None
    for p in (r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simsun.ttc"):
        if os.path.exists(p):
            fp = p
            break
    assert fp, "找不到中文字体（simhei/msyh/simsun），停止"
    font = ImageFont.truetype(fp, 16)
    out = []
    for ch in text:
        im = Image.new("L", (40, 40), 0)
        ImageDraw.Draw(im).text((10, 10), ch, font=font, fill=255)
        a = np.array(im) >= 128
        ys, xs = np.nonzero(a)
        assert len(xs), "字 %s 渲染为空" % ch
        a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        hh, ww = a.shape
        assert hh <= 16 and ww <= 16, "字 %s 超出 16px：%dx%d" % (ch, ww, hh)
        g = np.zeros((16, 16), dtype=bool)
        oy, ox = (16 - hh) // 2, (16 - ww) // 2
        g[oy:oy + hh, ox:ox + ww] = a
        out.append(g)
    return out, fp


# --- 扫描一期实际楼板范围（不猜坐标）---
PX0, PZ0, PX1, PZ1 = extent(68, "平台")
MX0, MZ0, MX1, MZ1 = extent(140, "中层楼板", (16, 40, 176, 152))
SX0, SZ0, SX1, SZ1 = extent(228, "顶层楼板", (40, 56, 152, 136))

# --- 高凳（同二期a）---
for c in (44, 76, 116, 148):
    fill(None, c - 3, 72, 17, c + 3, 84, 23)
    fill("plinth", c - 4, 72, 16, c + 4, 73, 24)
    fill("steel", c - 1, 73, 19, c + 1, 82, 21)
    fill("steel", c - 3, 77, 18, c + 3, 78, 22)
    fill("top", c - 4, 82, 16, c + 4, 84, 24)

# --- 平台临街轮廓光（洋红）---
fill("magenta", PX0, 66, PZ0 - 1, PX1, 68, PZ0)

# --- 中层金属雨棚：临街一侧棚底琥珀，其余青 ---
canopy(MX0, MZ0, MX1, MZ1, 144, D=3)   # 2026-10-08：D=4 时四角底面 y133 压到腰线带（顶 y134）

# --- 顶层：楼板外沿青色轮廓 + 护栏 ---
fill("cyan", SX0 - 1, 226, SZ0 - 1, SX1 + 1, 228, SZ0)
fill("cyan", SX0 - 1, 226, SZ1, SX1 + 1, 228, SZ1 + 1)
fill("cyan", SX0 - 1, 226, SZ0, SX0, 228, SZ1)
fill("cyan", SX1, 226, SZ0, SX1 + 1, 228, SZ1)
fill("steel", SX0, 232, SZ0, SX1, 238, SZ0 + 2)
fill("steel", SX0, 232, SZ1 - 2, SX1, 238, SZ1)
fill("steel", SX0, 232, SZ0, SX0 + 2, 238, SZ1)
fill("steel", SX1 - 2, 232, SZ0, SX1, 238, SZ1)

# --- 屋顶设备（先断言都落在顶层楼板内）---
for (ax0, az0, ax1, az1, nm) in ((48, 64, 88, 104, "冷凝机组"), (105, 65, 149, 87, "储能罐"),
                                 (132, 120, 152, 124, "桅杆")):
    assert SX0 + 2 <= ax0 and ax1 <= SX1 and SZ0 + 2 <= az0 and az1 <= SZ1 - 2, \
        "%s 超出顶层楼板 %s" % (nm, (SX0, SZ0, SX1, SZ1))
# 冷凝机组（B 白）：百叶朝北、顶部风扇口 + 青色光环
fill("white", 48, 232, 64, 88, 252, 104)
for y in range(235, 250, 4):
    fill("dark", 50, y, 63, 86, y + 2, 64)
disk(None, 68, 84, 14, 244, 252)
disk("dark", 68, 84, 14, 244, 245)
fill("steel", 55, 246, 82, 81, 248, 86)
fill("steel", 66, 246, 71, 70, 248, 97)
disk("steel", 68, 84, 3, 245, 250)
disk("cyan", 68, 84, 15.5, 251, 252)
disk(None, 68, 84, 14, 251, 252)
# 储能罐 ×2（B 白 + 红色发光警示环 + 深色罐顶）
for cx in (116, 138):
    disk("white", cx, 76, 10, 232, 276)
    disk("red", cx, 76, 11, 262, 266)
    disk("white", cx, 76, 10, 262, 266)
    disk("dark", cx, 76, 7, 276, 279)
# 天线桅杆 + 横担 + 航标
fill("steel", 140, 232, 120, 144, 300, 124)
fill("steel", 132, 280, 121, 152, 282, 123)
fill("cyan", 141, 300, 121, 143, 304, 123)
# 管道：机组 → 屋面 → 沿住舱东侧下到露台
fill("steel", 88, 236, 90, SX1 + 6, 240, 94)
fill("steel", SX1 + 2, 144, 90, SX1 + 6, 240, 94)

# --- 竖挂霓虹招牌：独立杆，板面垂直于临街立面，双面字 ---
BX0, BX1, BZ0, BZ1, BY0, BY1 = 202, 206, 0, 38, 148, 284
fill("plinth", 198, 0, 34, 210, 8, 46)
fill("steel", 202, 0, 38, 206, 296, 42)
fill("cyan", 203, 296, 39, 205, 300, 41)
if PX1 < 202:
    fill("steel", PX1, 60, 38, 202, 64, 42)
fill("sign", BX0, BY0, BZ0, BX1, BY1, BZ1)
for (xa, xb) in ((BX0 - 1, BX0), (BX1, BX1 + 1)):
    fill("cyan", xa, BY0, BZ0, xb, BY1, BZ0 + 2)
    fill("cyan", xa, BY0, BZ1 - 2, xb, BY1, BZ1)
    fill("cyan", xa, BY0, BZ0, xb, BY0 + 2, BZ1)
    fill("cyan", xa, BY1 - 2, BZ0, xb, BY1, BZ1)
GL, FP = sign_glyphs(SIGN)
NPX = 0
for i, g in enumerate(GL):
    for r in range(16):
        for c in range(16):
            if not g[r, c]:
                continue
            y = 280 - 32 * i - 2 * (r + 1)
            ze = 33 - 2 * c      # 东面：观察者面朝西，左手 = +z ⇒ 字第 0 列在 z 最大处
            zw = 3 + 2 * c       # 西面：观察者面朝东，左手 = -z ⇒ 字第 0 列在 z 最小处
            fill("magenta", BX1, y, ze, BX1 + 1, y + 2, ze + 2)
            fill("magenta", BX0 - 1, y, zw, BX0, y + 2, zw + 2)
            NPX += 1

# --- 电缆：屋顶桅杆 → 招牌杆顶（悬链线下垂 24px）---
NCAB = cable("plinth", (142, 298, 122), (204, 292, 40), 24)

'''
rep("# ===================== 自检：可变形盒不越界", ADD + "# ===================== 自检：可变形盒不越界")

TAIL = r'''
print("   v3：雨棚斜面件 %d / 招牌字 %s（%d 像素 ×2 面，字体 %s）/ 电缆 %d 点" % (
    CNT["canopy"], SIGN, NPX, FP, NCAB))
seen = {}
for k in PAL:
    seen.setdefault(MAT[k], []).append(k)
same = [(b, ks) for b, ks in seen.items() if len(ks) > 1]
for b, ks in same:
    print("   [同块] %s ← %s" % (b, "/".join(ks)))
print("   同块检查（全部 %d 个调色键）：%s" % (len(PAL), "无" if not same else "%d 组（只提示，不拦截）" % len(same)))
'''
src += TAIL

exec(compile(src, "lt_noodle1+v3", "exec"), {"__name__": "__main__", "__builtins__": __builtins__})