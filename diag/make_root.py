# -*- coding: utf-8 -*-
# make_root.py —— 单变量：只加/去根部 fixed 外壳（设计方编写，纯文本替换，不跑生成器）
import io, hashlib
def sha(b): return hashlib.sha256(b).hexdigest()[:16]
RS = ',structure:{id:"fixed",name:"轨道桥二期_原型段"}'
def rd(n): return io.open(n, encoding="utf-8", newline="").read()
def save(name, s):
    io.open(name, "w", encoding="utf-8", newline="").write(s)
    assert rd(name) == s, "读回不一致：" + name
    print(name, "字节 =", len(s.encode("utf-8")), " 结尾完整 =", s.endswith("}"),
          " 有外壳 =", RS in s, " light 个数 =", s.count('id:"light"'), " sha256 =", sha(s.encode("utf-8")))
src = {n: rd(n) for n in ("test_K_nolight.txt", "test_V2_no_recolor.txt", "test_B_old.txt", "bridge2_proto.txt")}
before = {n: sha(s.encode("utf-8")) for n, s in src.items()}
for n, s in src.items():
    print("原", n, "外壳出现次数 =", s.count(RS), " structure: 出现次数 =", s.count("structure:"))
k = src["test_K_nolight.txt"]
assert k.count(RS) == 1 and k.count("structure:") == 1, "K 外壳锚点不符：停下"
save("test_K_noroot.txt", k.replace(RS, ""))
for n, out in (("test_V2_no_recolor.txt", "test_V2_root.txt"), ("test_B_old.txt", "test_B_root.txt")):
    s = src[n]
    assert "structure:" not in s, n + " 已有结构：停下"
    i = s.rfind(",min:[I;")
    assert i > 0 and s.startswith("{tiles:["), n + " 锚点不符：停下"
    save(out, s[:i] + RS + s[i:])
for n in src:
    assert sha(rd(n).encode("utf-8")) == before[n], "原文件被改动：停下 " + n
print("原文件全部未动")
print("PASS")