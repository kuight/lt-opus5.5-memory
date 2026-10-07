# -*- coding: utf-8 -*-
# patch_geom_env.py —— 给 lt_geom.py 加两个环境变量开关（默认行为不变）
#   LT_COPLANAR_TOL：共面容差，默认 0.01
#   LT_GEOM_COMPOSITE=1：组合件模式，关闭"同一竖线各段必须首尾相接"（管道/管卡等本来就分段）
# 用法：在 E:\work\建筑\ 下运行 python patch_geom_env.py
import io, os
p = os.path.join(os.getcwd(), "lt_geom.py")
s = io.open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in s else "\n"
R = [("import io, re, sys, math" + nl, "import io, re, sys, math, os" + nl),
     ("            if dv > 0.01:" + nl,
      '            if dv > float(os.environ.get("LT_COPLANAR_TOL", "0.01")):' + nl),
     ("            if abs(segs[i][1] - segs[i + 1][0]) > 0.01:" + nl,
      '            if os.environ.get("LT_GEOM_COMPOSITE") != "1" and abs(segs[i][1] - segs[i + 1][0]) > 0.01:' + nl)]
for a, b in R:
    n = s.count(a)
    if n != 1:
        raise SystemExit("FAIL 锚点出现 %d 次（应为 1）: %r" % (n, a.strip()))
    s = s.replace(a, b)
io.open(p, "w", encoding="utf-8", newline="").write(s)
t = io.open(p, encoding="utf-8").read()
assert "LT_COPLANAR_TOL" in t and "LT_GEOM_COMPOSITE" in t
print("PASS lt_geom.py 已打补丁：", p)