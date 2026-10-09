# -*- coding: utf-8 -*-
# make_k.py —— 卡顿排查：K=去掉 light 子结构的二期c；B=上一版（不卡的基准）（设计方编写）
import io, hashlib, os, subprocess
def sha(b): return hashlib.sha256(b).hexdigest()[:16]
base = io.open("lt_bridge2.py", encoding="utf-8").read()
W = 'io.open(OUT, "w", encoding="utf-8").write(t)'
T = '"{tiles:[%s],children:[%s],min:'
assert base.count(W) == 1, "写盘锚点不符：停下"
assert base.count(T) == 1, "children 锚点不符：停下"
before = sha(open("bridge2_proto.txt", "rb").read())
src = base.replace(W, 'io.open("test_K_nolight.txt", "w", encoding="utf-8", newline="").write(t)')
src = src.replace(T, '"{tiles:[%s]%.0s,min:')
exec(compile(src, "lt_bridge2_K", "exec"), {"__name__": "__main__"})
s = io.open("test_K_nolight.txt", encoding="utf-8").read()
print("test_K_nolight.txt 字节 =", os.path.getsize("test_K_nolight.txt"), " 结尾完整 =", s.endswith("}"),
      " light 个数 =", s.count('id:"light"'), " sha256 =", sha(s.encode("utf-8")))
assert s.endswith("}") and s.count('id:"light"') == 0, "K 版不对：停下"
g = subprocess.run(["git", "-C", r"E:\work\lt-memory", "show",
                    "aa9d3a829d24d8586e99e658196d836a3b51e7f8:samples/bridge2_proto.txt"], capture_output=True)
assert g.returncode == 0, "git show 失败：停下"
open("test_B_old.txt", "wb").write(g.stdout)
print("test_B_old.txt 字节 =", len(g.stdout), "（应为 127406） sha256 =", sha(g.stdout))
after = sha(open("bridge2_proto.txt", "rb").read())
assert before == after, "原文件被改动：停下"
print("原文件未动", after)
print("PASS")