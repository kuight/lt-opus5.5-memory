# -*- coding: utf-8 -*-
# patch_bridge2_a.py —— 梁底下照灯：体素→贴斜梁可变形盒，并避开墩（设计方编写）
import hashlib, io
P = "lt_bridge2.py"
src = io.open(P, encoding="utf-8").read()
print("补丁前 sha256 =", hashlib.sha256(src.encode("utf-8")).hexdigest())
OLD = '''    if (x0 // 16) % 5 == 2:                          # 梁底琥珀下照
        fill("amber", x0 + 5, a - 2, 45, x0 + 11, a, 51)
'''
NEW = '''    if (x0 // 16) % 5 == 2 and not any(ox - 16 <= x0 <= ox + 48 for ox, _k, _l in PIERS):
        seg("amber", 45, 51, (-2, -2), (0, 0))       # 梁底琥珀下照：贴斜梁、避开墩
'''
assert src.count(OLD) == 1, "锚点没找到或不唯一：停下"
out = src.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8").write(out)
back = io.open(P, encoding="utf-8").read()
assert back == out and back.count(NEW) == 1, "写入读回不一致"
print("补丁后 sha256 =", hashlib.sha256(back.encode("utf-8")).hexdigest())
print("PASS")
