# -*- coding: utf-8 -*-
# patch_wall2_zo.py —— lt_wall2.py 两处修订（设计方编写）
#   ① ZO 12→11：最外零件 n=11（管卡/法兰）⇒ 墙前沿 z=0，导入起点 (0,0,0)
#   ② 运行前删除旧 std_wall2.txt，避免失败时残留旧文件被误认
# 用法：在 E:\work\建筑\ 下运行 python patch_wall2_zo.py
import io, os
p = os.path.join(os.getcwd(), "lt_wall2.py")
s = io.open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in s else "\n"
R = [("ZO, CX, R0 = 12, 128, 64" + nl, "ZO, CX, R0 = 11, 128, 64" + nl),
     ('OUT = "std_wall2.txt"' + nl,
      'OUT = "std_wall2.txt"' + nl + "if os.path.exists(OUT):" + nl + "    os.remove(OUT)" + nl)]
for a, b in R:
    n = s.count(a)
    if n != 1:
        raise SystemExit("FAIL 锚点出现 %d 次（应为 1）: %r" % (n, a.strip()))
    s = s.replace(a, b)
io.open(p, "w", encoding="utf-8", newline="").write(s)
t = io.open(p, encoding="utf-8").read()
assert "ZO, CX, R0 = 11, 128, 64" in t and "os.remove(OUT)" in t
assert "ZO, CX, R0 = 12" not in t
print("PASS lt_wall2.py 已打补丁：", p)