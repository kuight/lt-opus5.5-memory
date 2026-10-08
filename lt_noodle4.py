# -*- coding: utf-8 -*-
# lt_noodle4.py —— 合成蛋白面馆 v4：夜景灯带加密 + 全息菜单屏 / 露台全息牌（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_noodle4.py  → noodle4.txt
# 做法：读入 lt_noodle3.py 原文（须 8B5A2F75C127F669 开头），按锚点插入 v4 代码后执行；一期/v3 逻辑不改。
# 参考：建筑夜景照明"勾勒结构线、分层次、突出重点"；Blade Runner 街区（每层都有光源、屏幕、招牌）；
#       Ghost in the Shell(2017) 半透明全息屏；航空障碍灯（红）
import io, hashlib

P = "lt_noodle3.py"
raw = io.open(P, "rb").read()
h = hashlib.sha256(raw).hexdigest().upper()
print("   lt_noodle3.py sha256 = %s" % h)
assert h.startswith("8B5A2F75C127F669"), "lt_noodle3.py 不是补丁后入库版本（应以 8B5A2F75C127F669 开头），停止"
src = raw.decode("utf-8")


def rep(a, b):
    global src
    n = src.count(a)
    assert n == 1, "替换锚点出现 %d 次（应为 1）：%r" % (n, a)
    src = src.replace(a, b)


ADD4 = r"""
# ===================== v4：夜景灯带加密 + 全息屏 =====================
NL = {"n": 0, "txt": 0}


def glow(k, x0, y0, z0, x1, y1, z1):
    fill(k, x0, y0, z0, x1, y1, z1)
    NL["n"] += 1


def holo_text(text, xr, ytop, zf, k="magenta"):
    # 朝北面：观察者面朝南，左手 = +x ⇒ 第 0 字、第 0 列在 x 最大处；第 0 行在最上
    gl, _ = sign_glyphs(text)
    for i, g in enumerate(gl):
        for r in range(16):
            for c in range(16):
                if g[r, c]:
                    x, y = xr - 20 * i - c, ytop - r
                    fill(k, x, y, zf, x + 1, y + 1, zf + 1)
                    NL["txt"] += 1


# --- 1 吊脚层 ---
for cx in COLX:
    glow("cyan", cx + 3, 16, 7, cx + 5, 48, 8)            # 北排柱竖向灯条
glow("cyan", 4, 55, 7, 188, 57, 8)                         # 北面大梁灯线
for cx in COLX:
    for cz in COLZ:                                        # 柱础光环 1px
        fill("cyan", cx - 5, 12, cz - 5, cx + 13, 13, cz + 13)
        fill("plinth", cx - 4, 12, cz - 4, cx + 12, 13, cz + 12)
        NL["n"] += 1
glow("amber", 16, 62, 44, 176, 64, 46)                     # 平台底下照灯线
glow("amber", 16, 62, 112, 176, 64, 114)
glow("cyan", PX0 - 1, 66, PZ0, PX0, 68, PZ1)               # 平台西/东/南轮廓
glow("cyan", PX1, 66, PZ0, PX1 + 1, 68, PZ1)
glow("cyan", PX0, 66, PZ1, PX1, 68, PZ1 + 1)

# --- 2 面摊层 ---
glow("cyan", 24, 120, 39, 168, 122, 40)                    # 过梁底边
glow("cyan", 19, 76, 39, 21, 120, 40)                      # 墙垛竖条
glow("cyan", 171, 76, 39, 173, 120, 40)
glow("cyan", 15, 100, 40, 16, 102, 152)                    # 三面墙肋间内凹灯带
glow("cyan", 176, 100, 40, 177, 102, 152)
glow("cyan", 16, 100, 152, 176, 102, 153)
glow("cyan", MX0, 139, MZ0 - 25, MX1, 141, MZ0 - 24)       # 雨棚封檐外侧（与棚底灯带成双线）
glow("cyan", MX0, 139, MZ1 + 24, MX1, 141, MZ1 + 25)
glow("cyan", MX0 - 25, 139, MZ0, MX0 - 24, 141, MZ1)
glow("cyan", MX1 + 24, 139, MZ0, MX1 + 25, 141, MZ1)
# 全息菜单屏（柜台上方，吊在过梁下）
fill("holo", 56, 96, 41, 136, 118, 42)
for b in ((55, 95, 41, 137, 96, 42), (55, 118, 41, 137, 119, 42), (55, 96, 41, 56, 118, 42), (136, 96, 41, 137, 118, 42)):
    glow("cyan", *b)
fill("steel", 60, 119, 41, 62, 120, 42)
fill("steel", 130, 119, 41, 132, 120, 42)
holo_text(u"蛋白面", 125, 115, 40)
glow("amber", 72, 98, 40, 124, 99, 41)

# --- 3 露台全息牌「营业中」---
fill("holo", 52, 152, 44, 140, 172, 45)
for b in ((51, 151, 44, 141, 152, 45), (51, 172, 44, 141, 173, 45), (51, 152, 44, 52, 172, 45), (140, 152, 44, 141, 172, 45)):
    glow("cyan", *b)
fill("steel", 60, 144, 44, 62, 151, 45)
fill("steel", 130, 144, 44, 132, 151, 45)
holo_text(u"营业中", 127, 169, 43)

# --- 4 住舱 ---
for zf in (55, 136):                                       # 南北窗框 + 舱顶下横向灯带
    glow("cyan", 78, 176, zf, 80, 210, zf + 1)
    glow("cyan", 112, 176, zf, 114, 210, zf + 1)
    glow("cyan", 78, 208, zf, 114, 210, zf + 1)
    glow("cyan", 73, 218, zf, 119, 220, zf + 1)
glow("cyan", 152, 162, 95, 153, 222, 97)                   # 东墙竖条
glow("cyan", 42, 160, 89, 43, 200, 91)                     # 西门框（门洞内侧）
glow("cyan", 42, 160, 101, 43, 200, 103)
glow("cyan", 42, 198, 91, 43, 200, 101)

# --- 5 屋顶 ---
for cx in (116, 138):
    glow("cyan", cx - 1, 236, 65, cx + 1, 260, 66)         # 储能罐竖向灯条
for y in (239, 247):
    glow("cyan", 50, y, 63, 86, y + 2, 64)                 # 冷凝机组进风口发光百叶
glow("cyan", 88, 240, 68, 89, 248, 76)                     # 机组东侧状态屏
glow("amber", 88, 244, 70, 89, 245, 72)
glow("red", 132, 282, 121, 134, 284, 123)                  # 航空障碍灯
glow("red", 150, 282, 121, 152, 284, 123)

# --- 6 招牌杆竖向灯条 ---
glow("cyan", 203, 8, 37, 205, 146, 38)

print("   v4：新增发光件 %d 处；全息屏 2（菜单「蛋白面」/ 露台「营业中」），屏上字 %d 像素" % (NL["n"], NL["txt"]))
"""

rep('OUT = "noodle3.txt"', 'OUT = "noodle4.txt"')
rep('"合成蛋白面馆_v3"', '"合成蛋白面馆_v4"')
rep('合成蛋白面馆 v3 生成完毕', '合成蛋白面馆 v4 生成完毕')
rep('"sign": ("#121519", "solid"),\'', '"sign": ("#121519", "solid"), "holo": ("#00E5FF", "trans"),\'')
A = 'NCAB = cable("plinth", (142, 298, 122), (204, 292, 40), 24)'
rep(A, A + "\n" + ADD4)

exec(compile(src, "lt_noodle3+v4", "exec"), {"__name__": "__main__", "__builtins__": __builtins__})