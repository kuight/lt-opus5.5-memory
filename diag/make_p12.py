# -*- coding: utf-8 -*-
# make_p12.py —— 卡顿二分第2步（设计方编写）
# P1 = 只有 B-09(hoop) 墩号发光；P2 = 只有 B-09 墩号不发光。两者都无 light、都保留随机配色
import io, hashlib, shutil, os
def sha(b): return hashlib.sha256(b).hexdigest()[:16]
P = "bridge2_proto.txt"
BAK = "bridge2_proto.bak_p12"
shutil.copyfile(P, BAK)
before = sha(open(P, "rb").read())
base = io.open("lt_bridge2.py", encoding="utf-8").read()
W = 'io.open(OUT, "w", encoding="utf-8").write(t)'
T = '"{tiles:[%s],children:[%s],min:'
E = '# ===================== 贪心合并 + 导出 ====================='
for k in (W, T, E):
    assert base.count(k) == 1, "锚点数量不符：停下 → " + k[:40]
INJ = '''
_LB, _WH = mid("label"), mid("white")
_NEW = [mid(_k) for _k in ("rust3", "ochre", "soot", "moss", "chalk")]
_CEN = [(_o + 24, _k, _l) for _o, _k, _l in PIERS]
def _near(_xf):
    return min(_CEN, key=lambda _c: abs(_c[0] - _xf))
_lab = np.argwhere(G == _LB)
_new = np.argwhere(np.isin(G, _NEW))
_cn = {tuple(((_p - M) // 16).tolist()) for _p in _new}
_stat = {}
for _p in _lab:
    _c = _near(int(_p[0]) - M)
    _s = _stat.setdefault(str(_c[2]), [0, set(), _c[1]])
    _s[0] += 1
    _s[1].add(tuple(((_p - M) // 16).tolist()))
for _l, (_n0, _cs, _k) in sorted(_stat.items()):
    print("  [诊断] 墩号 %s(%s) 发光像素 %d 占格 %d 与随机配色同格 %d" % (_l, _k, _n0, len(_cs), len(_cs & _cn)))
print("  [诊断] 随机配色共占格 %d" % len(_cn))
_n1 = 0
for _p in _lab:
    if _near(int(_p[0]) - M)[1] not in KEEP:
        G[tuple(_p)] = _WH
        _n1 += 1
print("  [变体] 保留发光的墩型 %s；改白像素 %d" % (sorted(KEEP), _n1))
'''
def run(name, keep):
    src = base.replace(W, 'io.open(%r, "w", encoding="utf-8", newline="").write(t)' % name)
    src = src.replace(T, '"{tiles:[%s]%.0s,min:')
    src = src.replace(E, "KEEP = %r\n" % (keep,) + INJ + E)
    print("=====", name)
    exec(compile(src, "lt_bridge2_" + name, "exec"), {"__name__": "__main__"})
    s = io.open(name, encoding="utf-8", newline="").read()
    print(name, "字节 =", len(s.encode("utf-8")), " 结尾完整 =", s.endswith("}"),
          " light 个数 =", s.count('id:"light"'), " sha256 =", sha(s.encode("utf-8")))
    assert s.endswith("}") and s.count('id:"light"') == 0, name + " 不对：停下"
try:
    run("test_P1_only09.txt", {"hoop"})
    run("test_P2_no09.txt", {"std", "portal"})
finally:
    if (not os.path.exists(P)) or sha(open(P, "rb").read()) != before:
        shutil.copyfile(BAK, P)
        print("原文件被生成器删除或改动，已从备份恢复（预期内）")
    assert sha(open(P, "rb").read()) == before, "原文件恢复失败：停下"
    os.remove(BAK)
    print("原文件未动", before)
print("PASS")