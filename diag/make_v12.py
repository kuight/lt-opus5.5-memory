# -*- coding: utf-8 -*-
# make_v12.py —— 卡顿二分（设计方编写）：V1=墩号改回白色；V2=去掉B-09随机配色；B=二期b原文件。三者都无 light
import io, hashlib, subprocess, shutil, os
def sha(b): return hashlib.sha256(b).hexdigest()[:16]
P = "bridge2_proto.txt"
BAK = "bridge2_proto.bak_v12"
shutil.copyfile(P, BAK)
before = sha(open(P, "rb").read())
base = io.open("lt_bridge2.py", encoding="utf-8").read()
W = 'io.open(OUT, "w", encoding="utf-8").write(t)'
T = '"{tiles:[%s],children:[%s],min:'
L = 'text("label", label,'
S = '# ===================== 二期c：B-09 做旧色彩随机'
E = '# ===================== 贪心合并 + 导出 ====================='
for k, n in ((W, 1), (T, 1), (L, 4), (S, 1), (E, 1)):
    assert base.count(k) == n, "锚点数量不符（要 %d 实 %d）：停下 → %s" % (n, base.count(k), k[:40])
def run(name, src):
    src = src.replace(W, 'io.open(%r, "w", encoding="utf-8", newline="").write(t)' % name)
    src = src.replace(T, '"{tiles:[%s]%.0s,min:')
    print("=====", name)
    exec(compile(src, "lt_bridge2_" + name, "exec"), {"__name__": "__main__"})
    s = io.open(name, encoding="utf-8", newline="").read()
    print(name, "字节 =", len(s.encode("utf-8")), " 结尾完整 =", s.endswith("}"),
          " light 个数 =", s.count('id:"light"'), " sha256 =", sha(s.encode("utf-8")))
    assert s.endswith("}") and s.count('id:"light"') == 0, name + " 不对：停下"
try:
    run("test_V1_white_label.txt", base.replace(L, 'text("white", label,'))
    i, j = base.find(S), base.find(E)
    assert 0 < i < j, "配色段定位失败：停下"
    run("test_V2_no_recolor.txt", base[:i] + 'CNT["recolor"] = 0\n' + base[j:])
    g = subprocess.run(["git", "-C", r"E:\work\lt-memory", "show",
                        "aa9d3a829d24d8586e99e658196d836a3b51e7f8:samples/bridge2_proto.txt"], capture_output=True)
    assert g.returncode == 0, "git show 失败：停下"
    open("test_B_old.txt", "wb").write(g.stdout)
    print("test_B_old.txt 字节 =", len(g.stdout), "（应为 127406） sha256 =", sha(g.stdout))
    assert len(g.stdout) == 127406, "二期b 字节不符：停下"
finally:
    if sha(open(P, "rb").read()) != before:
        shutil.copyfile(BAK, P)
        print("！原文件曾被改动，已从备份恢复")
    assert sha(open(P, "rb").read()) == before, "原文件恢复失败：停下"
    os.remove(BAK)
    print("原文件未动", before)
print("PASS")