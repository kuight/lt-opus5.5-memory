# -*- coding: utf-8 -*-
# lt_wall4.py —— 加装层样品 M/H（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_wall4.py M|H  → std_wall4_M.txt / std_wall4_H.txt
# 做法：读 lt_wall2.py 源码执行（同 lt_wall3 方式），风格 A 配色；ZO 11→22 给加装层留 22px 外挑；
#   只在直段 x3..124 加"加装层"（retrofitting），弧段/接缝几何不变（整数平移，顶点相对位置不变）。
# 参考：Ridley Scott / Syd Mead《Blade Runner》retrofitting（American Cinematographer，theasc.com）
#   M：大气冷凝机组（散热鳍+托架+出水管）+ 竖挂招牌"中电" + 悬垂电缆 1 条
#   H：M + 储能罐×2 + 寄生舱（发光窗/百叶/斜撑/霓虹边）+ 第二条电缆 + 下垂引线 + 接线盒
import os, sys, io, math
sys.path.insert(0, os.getcwd())
import lt_colors

VAR = sys.argv[1].upper() if len(sys.argv) > 1 else ""
assert VAR in ("M", "H"), "用法: python lt_wall4.py M|H"
if not lt_colors._P:
    lt_colors._load()
S, GL, TR = "solid", "glow", "trans"
NMAX = 22                                   # 加装层最外 n（= 新 ZO，电缆/挂钩正好贴到 z=0）


def pick(h, kind):
    hh = h.lstrip("#")
    r, g, b = int(hh[0:2], 16), int(hh[2:4], 16), int(hh[4:6], 16)
    assert lt_colors._P.get(kind), "色板缺少类别 %s" % kind
    c = min(lt_colors._P[kind], key=lambda c: (c[1]-r)**2 + (c[2]-g)**2 + (c[3]-b)**2)
    d = math.sqrt((c[1]-r)**2 + (c[2]-g)**2 + (c[3]-b)**2)
    return lt_colors.fc(h, kind), "#%02X%02X%02X" % (c[1], c[2], c[3]), d


SPEC = {  # 风格 A（与 lt_wall3 A 相同）+ 加装层新材质
    "panel": ("#262C34", S), "rib": ("#1A1F26", S), "groove": ("#00E5FF", GL),
    "hi": ("#FF2A6D", GL), "base": ("#121519", S), "under": ("#3A4450", S),
    "door": ("#313843", S), "clamp": ("#4A5260", S), "cyan": ("#00E5FF", GL),
    "red": ("#FF2A6D", GL), "quartz": ("#00E5FF", GL),
    "equip": ("#2A3038", S), "cable": ("#0E1013", S), "signbd": ("#15181C", S),
    "glowc": ("#00E5FF", GL), "glowm": ("#FF2A6D", GL), "pane": ("#00E5FF", TR),
}
VARMAT = {k: pick(h, kd)[0] for k, (h, kd) in SPEC.items()}

ZHONG = ["...#...", "#######", "#..#..#", "#..#..#", "#######",
         "...#...", "...#...", "...#...", "...#..."]
DIAN = ["...#...", "#######", "#..#..#", "#######", "#..#..#",
        "#######", "...#...", "...#..#", "...####"]
PARTS = []


def catenary(fill, xa, xb, yh, sag, n0):
    L = float(xb - xa); xm = (xa + xb) / 2.0; ys = {}
    for x in range(xa, xb):
        t = (x + 0.5 - xm) / (L / 2.0)
        yc = int(round(yh - sag * (1 - t * t)))
        fill("cable", x, x + 1, yc - 1, yc + 1, n0, n0 + 2)
        ys[x] = yc
    return ys


def hook(fill, x, yh, n1):
    fill("iron", x - 1, x + 1, yh - 1, yh + 1, 0, n1)


def disc(fill, mat, cx, cn, r, y0, y1):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for n in range(int(cn - r) - 1, int(cn + r) + 2):
            if (x + 0.5 - cx) ** 2 + (n + 0.5 - cn) ** 2 <= r * r:
                fill(mat, x, x + 1, y0, y1, n, n + 1)


def retro(fill):
    # ---------- M ----------
    # 大气冷凝机组（左格间 x6..44，加强带之上）：托架 → 机身 → 散热鳍 → 状态灯 → 出水管弯进检修口上方
    fill("iron", 12, 14, 52, 54, 0, 14); fill("iron", 36, 38, 52, 54, 0, 14)
    fill("equip", 10, 40, 54, 76, 4, 14)
    fill("equip", 10, 11, 54, 76, 14, 16); fill("equip", 39, 40, 54, 76, 14, 16)
    for y in range(55, 76, 2):
        fill("clamp", 11, 39, y, y + 1, 14, 16)
    fill("glowc", 36, 38, 73, 74, 16, 17); fill("glowm", 32, 34, 73, 74, 16, 17)
    fill("iron", 24, 26, 44, 54, 6, 8); fill("iron", 24, 26, 42, 44, 0, 8)
    PARTS.append("冷凝机组（散热鳍 11 条、托架 2、出水管、状态灯 2）")
    # 竖挂招牌"中电"：两根悬臂从 44..50 肋框伸出，板 n16..18，字与边框 n18..19
    fill("iron", 44, 46, 32, 34, 5, 16); fill("iron", 44, 46, 50, 52, 5, 16)
    fill("signbd", 40, 51, 30, 55, 16, 18)
    for x0, x1, y0, y1 in [(40, 51, 54, 55), (40, 51, 30, 31), (40, 41, 30, 55), (50, 51, 30, 55)]:
        fill("glowc", x0, x1, y0, y1, 18, 19)
    for ytop, gl in [(53, ZHONG), (41, DIAN)]:
        for r, row in enumerate(gl):
            for c, ch in enumerate(row):
                if ch == "#":
                    fill("glowm", 42 + c, 43 + c, ytop - 1 - r, ytop - r, 18, 19)
    PARTS.append("竖挂招牌 中电（板 11×25px，字 7×9px，青色边框）")
    # 悬垂电缆 1：挂钩 x9 / x89，y78，下垂 8px，n20..22
    catenary(fill, 9, 89, 78, 8, 20)
    hook(fill, 9, 78, NMAX); hook(fill, 89, 78, NMAX)
    PARTS.append("悬垂电缆 1（x9→x89，下垂 8px）+ 挂钩 2")
    if VAR == "M":
        return
    # ---------- H ----------
    # 储能罐 ×2（中格间下部）：底座 → 罐体 r5 → 箍环 r6 ×2 → 发光警示环 → 顶盖 → 通进寄生舱的管
    fill("clamp", 53, 83, 16, 18, 0, 15)
    for cx in (60, 76):
        disc(fill, "equip", cx, 9, 5.0, 18, 44)
        disc(fill, "iron", cx, 9, 6.0, 24, 26)
        disc(fill, "iron", cx, 9, 6.0, 36, 38)
        disc(fill, "glowm", cx, 9, 5.4, 31, 32)
        disc(fill, "equip", cx, 9, 3.5, 44, 46)
        fill("iron", cx - 1, cx + 1, 46, 52, 8, 10)
    PARTS.append("储能罐 2（箍环 4、警示环 2、顶管 2）")
    # 寄生舱（中格间上部）：舱体 → 窗（内发光 + 半透明青玻璃 + 百叶）→ 檐口 → 霓虹边 → 斜撑
    fill("door", 54, 84, 52, 76, 0, 12)
    fill(None, 60, 78, 58, 70, 9, 12)
    fill("glowc", 60, 78, 58, 70, 8, 9)
    fill("pane", 60, 78, 58, 70, 9, 10)
    for y in (61, 64, 67):
        fill("clamp", 59, 79, y, y + 1, 11, 12)
    fill("rib", 53, 85, 76, 78, 0, 13)
    fill("glowm", 54, 84, 74, 75, 12, 13)
    for x in (52, 84):
        for i in range(12):
            fill("clamp", x, x + 2, 40 + i, 42 + i, i, i + 2)
    PARTS.append("寄生舱（发光窗+百叶 3 条、檐口、霓虹边、斜撑 2）")
    # 电缆 2 + 下垂引线 + 接线盒 → 通进通风格栅
    ys2 = catenary(fill, 51, 123, 54, 6, 18)
    hook(fill, 51, 54, 20); hook(fill, 123, 54, 20)
    fill("cable", 110, 112, 32, ys2[110] - 1, 18, 20)
    fill("equip", 106, 116, 24, 32, 14, 22)
    fill("glowc", 113, 115, 29, 30, 21, 22)
    fill("cable", 110, 112, 26, 28, 0, 14)
    PARTS.append("电缆 2（x51→x123，下垂 6px）+ 引线 + 接线盒 → 格栅")


src = io.open("lt_wall2.py", encoding="utf-8").read()


def rep(a, b):
    global src
    assert src.count(a) == 1, "锚点不唯一或不存在: %r" % a
    src = src.replace(a, b)


rep('OUT = "std_wall2.txt"', 'OUT = "std_wall4_%s.txt" % VAR')
rep('ZO, CX, R0 = 11, 128, 64', 'ZO, CX, R0 = %d, 128, 64' % NMAX)
rep('MAT["quartz"] = "minecraft:quartz_block"\n',
    'MAT["quartz"] = "minecraft:quartz_block"\nMAT.update(VARMAT)\n')
rep('# 楔形区域必须留空（由可变形盒占据）', 'RETRO(fill)\n# 楔形区域必须留空（由可变形盒占据）')
rep('assert flat_pct >= 40.0, "平整板面占比不足 40%，停止交付"',
    'print("   [加装层样品] 平整面门禁本样品暂停（本身就在测密度），实测 %.1f%%" % flat_pct)')

g = {"__name__": "__main__", "__file__": "lt_wall2.py", "VAR": VAR,
     "VARMAT": VARMAT, "RETRO": retro}
exec(compile(src, "lt_wall2.py", "exec"), g)

allb = g["allb"]
nglow = sum(1 for m, _ in allb if "glowing" in m)
ntrans = sum(1 for m, _ in allb if "transparent" in m or "trans" in m.split(":")[-1])
print("== 加装层 %s：%s" % (VAR, "中密度" if VAR == "M" else "高密度"))
for p in PARTS:
    print("   + " + p)
print("   盒子 %d，发光盒 %d，半透明盒 %d，字节 %d" % (len(allb), nglow, ntrans, g["nbytes"]))
print("   墙面在 z=%d（ZO 11→%d，外挑空间 %dpx）；对照组 = samples/std_wall3_A.txt" % (NMAX, NMAX, NMAX))
print("   材质映射（目标色 → 方块 → 实际色值，色差>40 标 [偏]）：")
for k in ("equip", "cable", "signbd", "glowc", "glowm", "pane"):
    h, kd = SPEC[k]
    n, act, d = pick(h, kd)
    print("     %-7s %s %-5s → %s  实际 %s  色差 %.0f%s" % (k, h, kd, n, act, d, "  [偏]" if d > 40 else ""))