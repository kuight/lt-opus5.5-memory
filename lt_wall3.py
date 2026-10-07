# -*- coding: utf-8 -*-
# lt_wall3.py —— 风格样品 A/B/C（设计方编写；agent 只保存、运行、贴输出，不改逻辑）
# 用法：在 E:\work\建筑\ 下运行  python lt_wall3.py A|B|C  → std_wall3_A.txt 等
# 做法：读 lt_wall2.py 源码执行，只换材质 + 追加一件悬浮件；几何与 std_wall2 完全相同（门禁口径不变）
# 参考：A=KitBash3D《Creating CyberPunk Interiors》(Shlenov：霓虹只做引导、只放重点)
#       B=《流浪地球2》美术设定(机核 161691)、《三体》水滴/《2001》黑石碑（光滑、不可解读）
#       C=DESIGN 配色 朱砂/鎏金/石青；宫门门钉 → 铆钉改金色
import os, sys, io, math
sys.path.insert(0, os.getcwd())
import lt_colors

VAR = sys.argv[1].upper() if len(sys.argv) > 1 else ""
assert VAR in ("A", "B", "C"), "用法: python lt_wall3.py A|B|C"
if not lt_colors._P:
    lt_colors._load()

S, GL, TR = "solid", "glow", "trans"


def pick(h, kind):
    hh = h.lstrip("#")
    r, g, b = int(hh[0:2], 16), int(hh[2:4], 16), int(hh[4:6], 16)
    assert lt_colors._P.get(kind), "色板缺少类别 %s" % kind
    c = min(lt_colors._P[kind], key=lambda c: (c[1]-r)**2 + (c[2]-g)**2 + (c[3]-b)**2)
    d = math.sqrt((c[1]-r)**2 + (c[2]-g)**2 + (c[3]-b)**2)
    return lt_colors.fc(h, kind), "#%02X%02X%02X" % (c[1], c[2], c[3]), d


def plaque(plate, frame):          # 悬浮板 + 发光边框，n6..7（离板面 6px）
    p, f = pick(*plate)[0], pick(*frame)[0]
    def fn(zo):
        z0, z1 = zo - 7, zo - 6
        return [(p, [58, 24, z0, 80, 40, z1]),
                (f, [57, 23, z0, 58, 41, z1]), (f, [80, 23, z0, 81, 41, z1]),
                (f, [58, 23, z0, 80, 24, z1]), (f, [58, 40, z0, 80, 41, z1])]
    return fn


def monolith(body, seam):          # 悬浮黑碑 n5..8 + 正面发光缝 n8..9
    b, s = pick(*body)[0], pick(*seam)[0]
    def fn(zo):
        return [(b, [62, 20, zo - 8, 76, 44, zo - 5]),
                (s, [68, 20, zo - 9, 70, 44, zo - 8])]
    return fn


VARS = {
    "A": ("赛博朋克：暗底 + 霓虹引导线 + 悬浮全息招牌",
          {"panel": ("#262C34", S), "rib": ("#1A1F26", S), "groove": ("#00E5FF", GL),
           "hi": ("#FF2A6D", GL), "base": ("#121519", S), "under": ("#3A4450", S),
           "door": ("#313843", S), "clamp": ("#4A5260", S), "cyan": ("#00E5FF", GL),
           "red": ("#FF2A6D", GL), "quartz": ("#00E5FF", GL)},
          plaque(("#00E5FF", TR), ("#FF2A6D", GL))),
    "B": ("硬科幻：亮白 + 单条状态灯 + 悬浮黑碑",
          {"panel": ("#EEF1F4", S), "rib": ("#C2C9D1", S), "groove": ("#1E242C", S),
           "hi": ("#F7F9FB", S), "base": ("#4A525C", S), "under": ("#9AA3AD", S),
           "door": ("#DCE1E6", S), "clamp": ("#6E7884", S), "cyan": ("#9FF3FF", GL),
           "red": ("#D13A2A", S), "quartz": ("#F7F9FB", S)},
          monolith(("#0B0D10", S), ("#9FF3FF", GL))),
    "C": ("中式未来：朱砂板 + 鎏金肋 + 门钉 + 悬浮石青匾额",
          {"panel": ("#8E2B22", S), "rib": ("#B8923A", S), "groove": ("#FFB347", GL),
           "hi": ("#FFD27A", GL), "base": ("#23272B", S), "under": ("#C9A24A", S),
           "door": ("#2E6E8E", S), "clamp": ("#3A4450", S), "cyan": ("#3FD0C9", GL),
           "red": ("#FFD27A", GL), "quartz": ("#FFD27A", GL)},
          plaque(("#2E6E8E", TR), ("#FFD27A", GL))),
}
title, spec, extra_fn = VARS[VAR]
VARMAT = {k: pick(h, kd)[0] for k, (h, kd) in spec.items()}

src = io.open("lt_wall2.py", encoding="utf-8").read()


def rep(a, b):
    global src
    assert src.count(a) == 1, "锚点不唯一或不存在: %r" % a
    src = src.replace(a, b)


rep('OUT = "std_wall2.txt"', 'OUT = "std_wall3_%s.txt" % VAR')
rep('MAT["quartz"] = "minecraft:quartz_block"\n',
    'MAT["quartz"] = "minecraft:quartz_block"\nMAT.update(VARMAT)\n')
rep('# ===================== 输出 =====================',
    'EXTRA = EXTRA_FN(ZO)\nT.extend(EXTRA)\n# ===================== 输出 =====================')

g = {"__name__": "__main__", "__file__": "lt_wall2.py",
     "VAR": VAR, "VARMAT": VARMAT, "EXTRA_FN": extra_fn}
exec(compile(src, "lt_wall2.py", "exec"), g)

# 悬浮件不得与任何已有盒子重叠（AABB 保守判定）
EX = g["EXTRA"]
others = g["V"] + g["T"][:len(g["T"]) - len(EX)]
for m, a in EX:
    for m2, b in others:
        bb = b[:6]
        hit = all(a[i] < bb[i + 3] and bb[i] < a[i + 3] for i in range(3))
        assert not hit, "悬浮件与已有盒子重叠 %s / %s" % (a, bb)

allb = g["V"] + g["T"]
nglow = sum(1 for m, _ in allb if "glowing" in m)
print("== 风格 %s：%s" % (VAR, title))
print("   悬浮件 %d 盒，重叠检查 PASS；发光盒 %d / 总 %d" % (len(EX), nglow, len(allb)))
print("   材质映射（目标色 → 方块 → 实际色值，色差>40 标 [偏]）：")
for k, (h, kd) in spec.items():
    n, act, d = pick(h, kd)
    print("     %-7s %s %-5s → %s  实际 %s  色差 %.0f%s" % (k, h, kd, n, act, d, "  [偏]" if d > 40 else ""))
print("   诊断：现版 std_wall2 配色实际落点：")
for k, h in g["PAL"]:
    n, act, d = pick(h, S)
    print("     %-7s %s → %s  实际 %s  色差 %.0f%s" % (k, h, n, act, d, "  [偏]" if d > 40 else ""))