# -*- coding: utf-8 -*-
# patch_wall4_n.py —— lt_wall4.py 第三版补丁（设计方编写；agent 只保存、运行、贴输出）
# 用法：在 E:\work\建筑\ 下运行 python patch_wall4_n.py
# ① 修"中电"左右反：朝北墙观察者面朝南，+x 在左手 ⇒ 列 c → x = 48 - c（所有风格）
# ② 新风格 N（民生夜读版）：A 提亮一档、肋框比板面亮、浅灰散热鳍/百叶、暖琥珀窗与高光
# ③ B 警示加强：罐警示带 1px → 4px；檐下 45° 红/深灰斜纹 30×5px（不发光）
# 新材质键 glowa（窗内发光）：A/B 默认同 glowc，输出不受影响
import io
P = "lt_wall4.py"
s = io.open(P, encoding="utf-8").read()
assert "STYLE" in s, "缺少 patch_wall4_b 补丁，停止"
assert "glowa" not in s, "已打过本补丁，停止"


def rep(a, b):
    global s
    n = s.count(a)
    assert n == 1, "锚点出现 %d 次: %r" % (n, a)
    s = s.replace(a, b)


rep('assert STYLE in ("A", "B"),', 'assert STYLE in ("A", "B", "N"),')
rep('SUF = "" if STYLE == "A" else "_B"', 'SUF = "" if STYLE == "A" else "_" + STYLE')

N_SPEC = '''if STYLE == "N":   # 风格 N 民生夜读版（A 提亮一档 + 暖窗）
    SPEC = {
        "panel": ("#3A424D", S), "rib": ("#5C6774", S), "groove": ("#00E5FF", GL),
        "hi": ("#FFB347", GL), "base": ("#1E2329", S), "under": ("#4A5462", S),
        "door": ("#2A3038", S), "clamp": ("#7A8594", S), "cyan": ("#00E5FF", GL),
        "red": ("#FF2A6D", GL), "quartz": ("#00E5FF", GL),
        "equip": ("#4E5864", S), "cable": ("#0E1013", S), "signbd": ("#15181C", S),
        "glowc": ("#00E5FF", GL), "glowm": ("#FF2A6D", GL), "pane": ("#FFB347", TR),
        "glowa": ("#FFB347", GL),
    }
SPEC.setdefault("glowa", SPEC["glowc"])
'''
rep('VARMAT = {k: pick(h, kd)[0] for k, (h, kd) in SPEC.items()}',
    N_SPEC + 'VARMAT = {k: pick(h, kd)[0] for k, (h, kd) in SPEC.items()}')

rep('fill("glowm", 42 + c, 43 + c, ytop - 1 - r, ytop - r, 18, 19)',
    'fill("glowm", 48 - c, 49 - c, ytop - 1 - r, ytop - r, 18, 19)')

rep('disc(fill, "glowm", cx, 9, 5.4, 31, 32)',
    'disc(fill, "glowm", cx, 9, 5.4, 30 if STYLE == "B" else 31, 34 if STYLE == "B" else 32)')

rep('    fill("glowc", 60, 78, 58, 70, 8, 9)', '    fill("glowa", 60, 78, 58, 70, 8, 9)')

rep('    fill("glowm", 54, 84, 74, 75, 12, 13)\n',
    '    if STYLE == "B":   # 警示斜纹 30x5px：红/深灰，45 度，条宽 3px，不发光\n'
    '        for x in range(54, 84):\n'
    '            for y in range(71, 76):\n'
    '                fill("glowm" if ((x + y) // 3) % 2 == 0 else "groove", x, x + 1, y, y + 1, 12, 13)\n'
    '    else:\n'
    '        fill("glowm", 54, 84, 74, 75, 12, 13)\n')

compile(s, P, "exec")
io.open(P, "w", encoding="utf-8").write(s)
print("PASS：lt_wall4.py 已加风格 N、修招牌字方向、加强 B 警示")