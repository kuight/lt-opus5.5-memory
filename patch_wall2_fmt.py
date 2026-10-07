# -*- coding: utf-8 -*-
# patch_wall2_fmt.py —— lt_wall2.py 两处修订（设计方编写）
#   ① 导出模板：size 补 I; 前缀；count = 根盒子数（§3.1）
#   ② warp_of：4 个点各自到另三点平面的距离取最大（与 lt_geom 口径一致，不受角点起始顺序影响）
# 用法：在 E:\work\建筑\ 下运行 python patch_wall2_fmt.py
import io, os
p = os.path.join(os.getcwd(), "lt_wall2.py")
s = io.open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in s else "\n"
R = [('txt = "{tiles:[%s],min:[I;%d,%d,%d],size:[%d,%d,%d],count:1}" % (' + nl +
      '    ",".join(ents), lo[0], lo[1], lo[2], hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])' + nl,
      'txt = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}" % (' + nl +
      '    ",".join(ents), lo[0], lo[1], lo[2], hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], len(allb))' + nl),
     ("    return max(dev(*p), dev(p[1], p[2], p[3], p[0]))" + nl,
      "    return max(dev(p[i % 4], p[(i + 1) % 4], p[(i + 2) % 4], p[(i + 3) % 4]) for i in range(4))" + nl)]
for a, b in R:
    n = s.count(a)
    if n != 1:
        raise SystemExit("FAIL 锚点出现 %d 次（应为 1）: %r" % (n, a.strip()[:60]))
    s = s.replace(a, b)
io.open(p, "w", encoding="utf-8", newline="").write(s)
t = io.open(p, encoding="utf-8").read()
assert "size:[I;%d,%d,%d],count:%d}" in t and "len(allb))" in t
assert "for i in range(4))" in t and "count:1}" not in t
print("PASS lt_wall2.py 已打补丁：", p)