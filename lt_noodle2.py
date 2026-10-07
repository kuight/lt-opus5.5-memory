# -*- coding: utf-8 -*-
# lt_noodle2.py —— 合成蛋白面馆 二期a：举架屋面 / 瓦垄集热肋 / 檐下散热椽 / 平座勾栏 / 高凳 / N 风格分色
# （设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_noodle2.py  → noodle2.txt
# 做法：读入 lt_noodle1.py 原文，按锚点替换（每个锚点必须恰好出现 1 次）+ 插入二期a 代码后执行；一期逻辑不改。
# 参考：清式举架（五举/六五举/七五举/九举，下缓上陡凹曲面；知乎 610404518、百度百科「举架」、
#       architecturasinica k000224）；清式檐下彩画以青绿冷色为主（广工《清式建筑做法》第八章）；
#       楼阁平座+勾栏；R7：椽 = 散热鳍、鸱吻位 = 传感桅杆
import io, sys, hashlib

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


rep('OUT = "noodle1.txt"', 'OUT = "noodle2.txt"')
rep('NX, NY, NZ = 256, 256, 240', 'NX, NY, NZ = 256, 288, 240')
rep('"steel": ("#5C6774", "solid")', '"steel": ("#4F5966", "solid")')
rep('"rib": ("#5C6774", "solid")', '"rib": ("#7A8594", "solid")')
rep('"roof": ("#4A5462", "solid"),',
    '"roof": ("#2A3038", "solid"), "tile": ("#4A5462", "solid"), '
    '"under": ("#2F4A52", "solid"), "cyan": ("#00E5FF", "glow"),')
rep('"合成蛋白面馆_一期"', '"合成蛋白面馆_二期a"')
rep('合成蛋白面馆 一期 生成完毕', '合成蛋白面馆 二期a 生成完毕')

ADD = r'''
# ===================== 二期a：举架屋面 / 瓦垄集热肋 / 檐下散热椽 / 平座勾栏 / 高凳 =====================
CNT.update({"roof": 0, "tilerib": 0, "fin": 0})


def ytop(k, x0, z0, x1, z1, h, ybot, tag):
    """实心斜顶件：顶面四角高度 h（必须共面），底面平 = ybot；只把顶角向下偏移（向内）"""
    assert h[(0, 0)] + h[(1, 1)] == h[(1, 0)] + h[(0, 1)], "顶面四角不共面 %s" % h
    yhi = max(h.values())
    assert ybot < min(h.values()), "底面不低于顶面 %s / %s" % (h, ybot)
    offs = [(CS[(sx, 1, sz)], "Y", v - yhi) for (sx, sz), v in sorted(h.items()) if v != yhi]
    assert offs, "斜面件没有偏移"
    arr = lt_tbox.encode([x0 + M, ybot, z0 + M, x1 + M, yhi, z1 + M], offs)
    TB.append((MAT[k], [int(v) for v in arr]))
    CNT[tag] += 1


# --- 顶层举架屋面：北坡分步，南坡以 z=96 镜像；檐根比飞檐根高 2px 作连檐线 ---
RZ = [56, 72, 84, 92]
RH = [234, 242, 250, 261]
for i in range(3):
    za, zb, ha, hb = RZ[i], RZ[i + 1], RH[i], RH[i + 1]
    ytop("roof", 40, za, 152, zb, {(0, 0): ha, (1, 0): ha, (0, 1): hb, (1, 1): hb}, 232, "roof")
    ytop("roof", 40, 192 - zb, 152, 192 - za, {(0, 0): hb, (1, 0): hb, (0, 1): ha, (1, 1): ha}, 232, "roof")
    if i < 2:   # 瓦垄 = 集热肋：宽 2px、高 2px、间距 8px，底面贴坡面
        for x in range(44, 150, 8):
            ypiece("tile", x, za, x + 2, zb,
                   {(0, 0): ha + 2, (1, 0): ha + 2, (0, 1): hb + 2, (1, 1): hb + 2}, 2, "tilerib")
            ypiece("tile", x, 192 - zb, x + 2, 192 - za,
                   {(0, 0): hb + 2, (1, 0): hb + 2, (0, 1): ha + 2, (1, 1): ha + 2}, 2, "tilerib")
fill("roof", 40, 232, 92, 152, 261, 100)      # 脊座
fill("rib", 36, 261, 92, 156, 269, 100)       # 正脊（两端各出 4px）
for xa in (36, 150):                          # 鸱吻位 → 传感桅杆 + 青色航标
    fill("steel", xa, 269, 93, xa + 6, 281, 99)
    fill("cyan", xa + 1, 281, 94, xa + 5, 283, 98)
for xa in (38, 152):                          # 悬鱼位 → 山面铭牌（外凸 2px）
    fill("rib", xa, 244, 94, xa + 2, 258, 98)


# --- 檐下散热椽：2px 厚鳍片，顶面贴飞檐底面（反曲），下垂 4px；翼角区不挂 ---
def fins(x0, z0, x1, z1, a, t=3, ft=4, step=8):
    def u(d):
        return a + f(d) - t
    for i in range(2):
        d0, d1 = FD[i], FD[i + 1]
        for x in range(x0 + 4, x1 - 4, step):
            ypiece("under", x, z0 - d1, x + 2, z0 - d0,
                   {(0, 0): u(d1), (1, 0): u(d1), (0, 1): u(d0), (1, 1): u(d0)}, ft, "fin")
            ypiece("under", x, z1 + d0, x + 2, z1 + d1,
                   {(0, 0): u(d0), (1, 0): u(d0), (0, 1): u(d1), (1, 1): u(d1)}, ft, "fin")
        for z in range(z0 + 4, z1 - 4, step):
            ypiece("under", x0 - d1, z, x0 - d0, z + 2,
                   {(0, 0): u(d1), (0, 1): u(d1), (1, 0): u(d0), (1, 1): u(d0)}, ft, "fin")
            ypiece("under", x1 + d0, z, x1 + d1, z + 2,
                   {(0, 0): u(d0), (0, 1): u(d0), (1, 0): u(d1), (1, 1): u(d1)}, ft, "fin")


fins(16, 40, 176, 152, 144)    # 腰檐
fins(40, 56, 152, 136, 232)    # 顶檐

# --- 平座勾栏（中层屋面 = 露台，y144 起）---
for y0, y1 in ((150, 151), (156, 158)):
    fill("steel", 18, y0, 42, 174, y1, 44)
    fill("steel", 18, y0, 148, 174, y1, 150)
    fill("steel", 18, y0, 44, 20, y1, 148)
    fill("steel", 172, y0, 44, 174, y1, 148)
for x in list(range(18, 172, 16)) + [172]:
    fill("steel", x, 144, 42, x + 2, 156, 44)
    fill("steel", x, 144, 148, x + 2, 156, 150)
for z in list(range(42, 148, 16)) + [146]:
    fill("steel", 18, 144, z, 20, 156, z + 2)
    fill("steel", 172, 144, z, 174, 156, z + 2)

# --- 高凳重做：底盘 + 立杆 + 脚踏 + 8px 凳面（位置不变）---
for c in (44, 76, 116, 148):
    fill(None, c - 3, 72, 17, c + 3, 84, 23)
    fill("plinth", c - 4, 72, 16, c + 4, 73, 24)
    fill("steel", c - 1, 73, 19, c + 1, 82, 21)
    fill("steel", c - 3, 77, 18, c + 3, 78, 22)
    fill("top", c - 4, 82, 16, c + 4, 84, 24)

'''
rep("# ===================== 自检：可变形盒不越界", ADD + "# ===================== 自检：可变形盒不越界")

TAIL = r'''
print("   二期a：举架屋面 %d / 瓦垄集热肋 %d / 檐下散热椽 %d" % (CNT["roof"], CNT["tilerib"], CNT["fin"]))
print("   举架：分步 %s → 高 %s，坡度 %s" % (RZ, RH,
      [round((RH[i + 1] - RH[i]) / float(RZ[i + 1] - RZ[i]), 2) for i in range(3)]))
seen = {}
for k in ("panel", "rib", "steel", "eave", "roof", "tile", "under"):
    seen.setdefault(MAT[k], []).append(k)
same = [(b, ks) for b, ks in seen.items() if len(ks) > 1]
for b, ks in same:
    print("   [同块] %s ← %s" % (b, "/".join(ks)))
print("   明度分级：%s" % ("全部可分" if not same else "有 %d 组同块（只提示，不拦截）" % len(same)))
'''
src += TAIL

exec(compile(src, "lt_noodle1+2a", "exec"), {"__name__": "__main__", "__builtins__": __builtins__})