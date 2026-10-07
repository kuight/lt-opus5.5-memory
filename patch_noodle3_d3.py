# -*- coding: utf-8 -*-
# patch_noodle3_d3.py —— 修 lt_noodle3.py 雨棚四角与一期腰线带重叠（设计方编写；agent 只保存、运行、贴输出）
# 原因：canopy 默认 D=4，四角顶面降 2D=8px、再减板厚 3px ⇒ 角块底面 y133，压到腰线带（y126..134，外凸到 x14/z38）
# 改法：中层雨棚 D=3 ⇒ 四角底面 y135、边板底面 y138，与腰线带留 1px
import io, hashlib

P = "lt_noodle3.py"
raw = io.open(P, "rb").read()
h0 = hashlib.sha256(raw).hexdigest().upper()
print("   补丁前 %s sha256 = %s" % (P, h0))
assert h0.startswith("B18B2505484F22E1"), "lt_noodle3.py 不是上轮保存的版本，停止"
s = raw.decode("utf-8")
A = "canopy(MX0, MZ0, MX1, MZ1, 144)"
B = "canopy(MX0, MZ0, MX1, MZ1, 144, D=3)   # 2026-10-08：D=4 时四角底面 y133 压到腰线带（顶 y134）"
assert s.count(A) == 1, "锚点出现 %d 次（应为 1）" % s.count(A)
s = s.replace(A, B)
out = s.encode("utf-8")
io.open(P, "wb").write(out)
chk = io.open(P, "rb").read()
assert chk == out and chk.decode("utf-8").count(B) == 1, "写入后读回不一致"
print("   补丁后 %s sha256 = %s（%d 字节）" % (P, hashlib.sha256(chk).hexdigest().upper(), len(chk)))
print("PASS")