# -*- coding: utf-8 -*-
# patch_wall4_glow.py —— lt_wall4.py 第四版补丁（设计方编写；agent 只保存、运行、贴输出）
# ① B 警示红改发光（用户：不发光不显眼）：glowm/red 由 solid #D13A2A → glow #FF3B2F
# ② 修提示文字：风格 N 的对照组写成 std_wall3_A（std_wall3_N 不存在）
# A/N 输出不受影响
import io
P = "lt_wall4.py"
s = io.open(P, encoding="utf-8").read()
assert "glowa" in s, "缺少 patch_wall4_n 补丁，停止"
assert "#FF3B2F" not in s, "已打过本补丁，停止"


def rep(a, b):
    global s
    n = s.count(a)
    assert n == 1, "锚点出现 %d 次: %r" % (n, a)
    s = s.replace(a, b)


rep('"glowm": ("#D13A2A", S)', '"glowm": ("#FF3B2F", GL)')
rep('"red": ("#D13A2A", S)', '"red": ("#FF3B2F", GL)')
rep('STYLE, STYLE))', 'STYLE, "A" if STYLE == "N" else STYLE))')
compile(s, P, "exec")
io.open(P, "w", encoding="utf-8").write(s)
print("PASS：B 警示改发光红、修 N 对照组提示")