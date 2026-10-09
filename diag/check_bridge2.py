# -*- coding: utf-8 -*-
# check_bridge2.py —— 三份 bridge2_proto.txt 对照 + 生成器写盘方式（设计方编写，只读）
import hashlib, subprocess, re
def rep(name, raw):
    t = raw.decode("utf-8", "replace")
    print("==", name)
    print("  字节 =", len(raw), " sha256 =", hashlib.sha256(raw).hexdigest()[:16])
    print("  结尾完整 =", t.rstrip().endswith("}"), " {}差 =", t.count("{") - t.count("}"), " []差 =", t.count("[") - t.count("]"))
    print("  light 个数 =", t.count('id:"light"'), " 有 children =", ",children:[" in t, " 有 count: =", ",count:" in t)
    print("  结尾 120 字：", repr(t[-120:]))
rep("工作目录 E:\\work\\建筑\\bridge2_proto.txt", open("bridge2_proto.txt", "rb").read())
rep("仓库 samples", open(r"E:\work\lt-memory\samples\bridge2_proto.txt", "rb").read())
g = subprocess.run(["git", "-C", r"E:\work\lt-memory", "show", "HEAD:samples/bridge2_proto.txt"], capture_output=True)
print("git show exit =", g.returncode)
if g.returncode == 0:
    rep("git HEAD 里的版本", g.stdout)
src = open("lt_bridge2.py", encoding="utf-8").read().split("\n")
for i, s in enumerate(src, 1):
    if re.search(r"open\(|\.write\(|\.close\(", s):
        print("  lt_bridge2.py 第%d行：%s" % (i, s.strip()))
print("PASS")