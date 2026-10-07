# -*- coding: utf-8 -*-
# patch_wall4_b.py —— 给 lt_wall4.py 加第 2 参数 A|B（设计方编写；agent 只保存、运行、贴输出）
# 用法：在 E:\work\建筑\ 下运行 python patch_wall4_b.py
# 默认 A：输出文件与补丁前逐字节一致；B：亮白硬科幻（同 lt_wall3 B），输出 std_wall4_M_B.txt 等
# B 改动：检修门/寄生舱 #C8CED4（上轮 B 检修门与板面同块融合）；设备中灰 #7E8893；
#         发光只有青白 #9FF3FF；警示红 #D13A2A 不发光（喷涂标识），招牌白底红字
import io, sys
P = "lt_wall4.py"
s = io.open(P, encoding="utf-8").read()
assert "STYLE" not in s, "已打过补丁，停止"


def rep(a, b):
    global s
    n = s.count(a)
    assert n == 1, "锚点出现 %d 次: %r" % (n, a)
    s = s.replace(a, b)


rep('assert VAR in ("M", "H"), "用法: python lt_wall4.py M|H"',
    'assert VAR in ("M", "H"), "用法: python lt_wall4.py M|H [A|B]"\n'
    'STYLE = sys.argv[2].upper() if len(sys.argv) > 2 else "A"\n'
    'assert STYLE in ("A", "B"), "用法: python lt_wall4.py M|H [A|B]"\n'
    'SUF = "" if STYLE == "A" else "_B"')

B_SPEC = '''if STYLE == "B":   # 风格 B 亮白硬科幻
    SPEC = {
        "panel": ("#EEF1F4", S), "rib": ("#C2C9D1", S), "groove": ("#1E242C", S),
        "hi": ("#F7F9FB", S), "base": ("#4A525C", S), "under": ("#9AA3AD", S),
        "door": ("#C8CED4", S), "clamp": ("#6E7884", S), "cyan": ("#9FF3FF", GL),
        "red": ("#D13A2A", S), "quartz": ("#F7F9FB", S),
        "equip": ("#7E8893", S), "cable": ("#1E242C", S), "signbd": ("#F7F9FB", S),
        "glowc": ("#9FF3FF", GL), "glowm": ("#D13A2A", S), "pane": ("#9FF3FF", TR),
    }
'''
rep('VARMAT = {k: pick(h, kd)[0] for k, (h, kd) in SPEC.items()}',
    B_SPEC + 'VARMAT = {k: pick(h, kd)[0] for k, (h, kd) in SPEC.items()}')

rep(r"""rep('OUT = "std_wall2.txt"', 'OUT = "std_wall4_%s.txt" % VAR')""",
    r"""rep('OUT = "std_wall2.txt"', 'OUT = "std_wall4_%s%s.txt"' % (VAR, SUF))""")

rep('print("== 加装层 %s：%s" % (VAR, "中密度" if VAR == "M" else "高密度"))',
    'print("== 加装层 %s%s：%s，风格 %s" % (VAR, SUF, "中密度" if VAR == "M" else "高密度", STYLE))')

rep('print("   墙面在 z=%d（ZO 11→%d，外挑空间 %dpx）；对照组 = samples/std_wall3_A.txt" % (NMAX, NMAX, NMAX))',
    'print("   墙面在 z=%d（ZO 11→%d，外挑空间 %dpx）；风格 %s；对照组 = samples/std_wall3_%s.txt" % (NMAX, NMAX, NMAX, STYLE, STYLE))')

TAIL = '''print("   全部材质映射（风格 %s）：" % STYLE)
for _k, (_h, _kd) in SPEC.items():
    _n, _act, _d = pick(_h, _kd)
    print("     %-7s %s %-5s → %s  实际 %s  色差 %.0f%s" % (_k, _h, _kd, _n, _act, _d, "  [偏]" if _d > 40 else ""))
_seen = {}
for _k, _v in VARMAT.items():
    _seen.setdefault(_v, []).append(_k)
for _v, _ks in sorted(_seen.items()):
    if len(_ks) > 1:
        print("   [同块] %s → %s（信息，不算错）" % ("/".join(sorted(_ks)), _v))
'''
s = s.rstrip("\n") + "\n" + TAIL
compile(s, P, "exec")
io.open(P, "w", encoding="utf-8").write(s)
print("PASS：lt_wall4.py 已加第 2 参数 A|B（默认 A，输出不变）")