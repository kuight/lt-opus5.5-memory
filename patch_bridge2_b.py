# -*- coding: utf-8 -*-
# patch_bridge2_b.py —— 二期b：加光条（梁侧/梁底/墩身/帽梁/承台）+ B-09 成片做旧（设计方编写）
import hashlib, io
P = "lt_bridge2.py"
raw = open(P, "rb").read()
h0 = hashlib.sha256(raw).hexdigest()
print("补丁前 文件 sha256 =", h0)
assert h0.startswith("0f6d516f3f7e4c37"), "补丁前哈希不符：停下"
src = raw.decode("utf-8").replace("\r\n", "\n")

O1 = '"rust": ("#6B4A3A", "solid"),'
N1 = O1 + ' "rust2": ("#4A3328", "solid"), "stain": ("#33383F", "solid"),\n    "fade": ("#8E7F4A", "solid"), "plate": ("#7D8794", "solid"),'

O2 = '''    if (x0 // 16) % 5 == 2 and not any(ox - 16 <= x0 <= ox + 48 for ox, _k, _l in PIERS):
        seg("amber", 45, 51, (-2, -2), (0, 0))'''
N2 = '''    clear = not any(ox - 16 <= x0 <= ox + 48 for ox, _k, _l in PIERS)
    if clear:
        seg("cyan", 28, 30, (-1, -1), (0, 0)); seg("cyan", 66, 68, (-1, -1), (0, 0))   # 梁底双青线
    for z0, z1 in ((15, 16), (80, 81)):
        seg("cyan", z0, z1, (20, 20), (22, 22))      # 梁侧第二道青线
    if (x0 // 16) % 3 == 1 and clear:
        seg("amber", 45, 51, (-2, -2), (0, 0))'''

O3 = 'for (xa, ya), (xb, yb2) in zip(HANG, HANG[1:]):'
N3 = '''# ===================== 二期b：墩身光条 + B-09 成片做旧（patch_bridge2_b）=====================
import random
RND = random.Random(20261008)
CNT["plight"] = 0
CNT["rust"] = 0

def paint_if(k, src, x, y, z):
    if G[x + M, y, z + M] == mid(src):
        G[x + M, y, z + M] = mid(k)
        return 1
    return 0

def vstrip(k, src, xs, zs, y0, y1, broken=False, skip=(64, 92)):
    n = 0
    for y in range(y0, y1):
        if skip[0] <= y < skip[1] or (broken and (y // 9) % 4 == 2):
            continue
        for x in xs:
            for z in zs:
                n += paint_if(k, src, x, y, z)
    return n

for ox, kind, label in PIERS:
    yc = yb(ox) - 8
    top = yc - 32
    for zf in (8, 87):                                   # 承台顶沿琥珀光边
        for x in range(ox, ox + 48):
            for y in (14, 15):
                CNT["plight"] += paint_if("amber", "plinth", x, y, zf)
    if kind == "portal":
        for zf in (0, 15, 80, 95):                       # 腿外面 + 朝店内面竖光条
            for xs in ((ox + 10, ox + 11), (ox + 37, ox + 38)):
                CNT["plight"] += vstrip("cyan", "pier2", xs, (zf,), 34, top - 4)
        for z0 in (18, 76):                              # 门洞顶灯条：照亮将来的小摊
            fill("cyan", ox + 4, top - 2, z0, ox + 44, top, z0 + 2)
        continue
    old = kind == "hoop"
    lk = "amber" if old else "cyan"
    for zf in (24, 71):                                  # 南北面竖光条
        for xs in ((ox + 6, ox + 7), (ox + 40, ox + 41)):
            CNT["plight"] += vstrip(lk, "pier", xs, (zf,), 34, top - 4, broken=old)
    for xf in (ox + 4, ox + 43):                         # 东西面竖光条
        for zs in ((30, 31), (64, 65)):
            CNT["plight"] += vstrip(lk, "pier", (xf,), zs, 34, top - 4, broken=old)
    for z0 in (16, 78):                                  # 帽梁悬挑下沿灯条（老墩缺几截）
        for xs in range(ox + 2, ox + 46, 8):
            if old and RND.random() < 0.4:
                continue
            fill(lk, xs, top - 2, z0, min(xs + (6 if old else 8), ox + 46), top, z0 + 2)
    if not old:
        continue
    bands = list(range(40, yc - 40, 28))
    # ① 剥落露筋（先挖，只挖墩身色）
    for (fx, fy, fw, fh, zf, dz) in ((ox + 10, 48, 10, 7, 24, 1), (ox + 28, 108, 8, 12, 24, 1),
                                     (ox + 14, 138, 12, 8, 71, -1), (ox + 29, 56, 9, 9, 71, -1)):
        for x in range(fx, fx + fw):
            for y in range(fy, fy + fh):
                for d in (0, 1):
                    if G[x + M, y, zf + d * dz + M] == mid("pier"):
                        G[x + M, y, zf + d * dz + M] = 0
                paint_if("stain", "pier", x, y, zf + 2 * dz)
        for y in (fy + 2, fy + fh - 3):
            for x in range(fx, fx + fw):
                paint_if("rust", "stain", x, y, zf + 2 * dz)
    # ② 锈水痕：从帽梁底和每道钢箍下沿往下淌，长短宽窄不一
    for ys in [top] + bands:
        for zf in (24, 71):
            for _ in range(5):
                x, w, ln = ox + RND.randint(5, 41), RND.choice((1, 2, 2, 3)), RND.randint(8, 30)
                for y in range(max(33, ys - ln), ys):
                    for xx in range(x, min(x + w, ox + 44)):
                        CNT["rust"] += paint_if("rust2" if y >= ys - 3 else "rust", "pier", xx, y, zf)
        for xf in (ox + 4, ox + 43):
            for _ in range(3):
                z, w, ln = RND.randint(25, 69), RND.choice((1, 2, 2)), RND.randint(6, 22)
                for y in range(max(33, ys - ln), ys):
                    for zz in range(z, min(z + w, 72)):
                        CNT["rust"] += paint_if("rust", "pier", xf, y, zz)
    # ③ 墩脚泥污：上沿随机游走
    for zf in (24, 71):
        h = 14
        for x in range(ox + 4, ox + 44):
            h = max(4, min(26, h + RND.randint(-3, 3)))
            for y in range(33, 33 + h):
                paint_if("stain", "pier", x, y, zf)
    for xf in (ox + 4, ox + 43):
        h = 14
        for z in range(24, 72):
            h = max(4, min(26, h + RND.randint(-3, 3)))
            for y in range(33, 33 + h):
                paint_if("stain", "pier", xf, y, z)
    # ④ 警示纹褪色掉漆（2×2 一块）
    for zf in (24, 71):
        for x in range(ox + 4, ox + 44, 2):
            for y in range(16, 32, 2):
                r = RND.random()
                k2 = "fade" if r < 0.3 else ("rust2" if r < 0.42 else None)
                if k2:
                    for dx in (0, 1):
                        for dy in (0, 1):
                            paint_if(k2, "yellow", x + dx, y + dy, zf)
    # ⑤ 东面补板 + 铆钉
    for (py, ph, pz, pw) in ((104, 12, 44, 14), (132, 16, 46, 12)):
        fill("plate", ox + 44, py, pz, ox + 45, py + ph, pz + pw)
        for y in (py + 1, py + ph - 2):
            for z in range(pz + 1, pz + pw - 1, 4):
                paint_if("rail", "plate", ox + 44, y, z)
    # ⑥ 外挂线缆两根 + 卡箍 + 接线盒（红灯）
    for z0 in (34, 38):
        fill("cable", ox + 44, 16, z0, ox + 46, top, z0 + 2)
    for y in range(30, top - 6, 18):
        fill("hoop", ox + 44, y, 33, ox + 47, y + 2, 41)
    fill("plate", ox + 44, 60, 46, ox + 48, 72, 56)
    fill("red", ox + 48, 68, 48, ox + 49, 70, 50)
    # ⑦ 帽梁水渍
    for zf in (16, 79):
        for _ in range(6):
            x, ln = ox + RND.randint(2, 45), RND.randint(5, 20)
            for y in range(yc - ln, yc):
                paint_if("stain", "cap", x, y, zf)
    # ⑧ 斜撑脚墩（修：原斜撑脚悬空）
    fill("plinth", ox - 32, 0, 40, ox - 20, 16, 56)
    fill("plinth", ox + 68, 0, 40, ox + 80, 16, 56)

''' + O3

O4 = 'print("== 材质：")'
N4 = 'print("  二期b：墩身/承台光条像素 %d；B-09 锈痕像素 %d；剥落 4 处、补板 2 块、线缆 2 根、斜撑脚墩 2 个" % (CNT["plight"], CNT["rust"]))\n' + O4

for o, n in ((O1, N1), (O2, N2), (O3, N3), (O4, N4)):
    assert src.count(o) == 1, "锚点没找到或不唯一：停下 → %r" % o[:50]
    src = src.replace(o, n)
io.open(P, "w", encoding="utf-8", newline="").write(src)
back = open(P, "rb").read()
assert back == src.encode("utf-8"), "写入读回不一致"
print("补丁后 文件 sha256 =", hashlib.sha256(back).hexdigest())
print("PASS")
