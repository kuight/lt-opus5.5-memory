import re
from lt_lib import *
import lt_root

BOX = re.compile(r'\[I;(-?\d+),(-?\d+),(-?\d+),(-?\d+),(-?\d+),(-?\d+)\]')

def load(fn):
    t = open(fn, encoding="utf-8").read()
    i = t.index("tiles:[") + 6
    d = 0
    for j in range(i, len(t)):
        if t[j] == "[": d += 1
        elif t[j] == "]":
            d -= 1
            if d == 0: break
    tiles = t[i:j + 1]
    m = re.search(r'structure:(\{[^{}]*\})', t)
    bs = [list(map(int, b)) for b in BOX.findall(tiles)]
    mn = [min(b[k] for b in bs) for k in range(3)]
    mx = [max(b[k + 3] for b in bs) for k in range(3)]
    return tiles, (m.group(1) if m else None), mn, mx

def place(tiles, mn, to):
    d = [to[k] - mn[k] for k in range(3)]
    return BOX.sub(lambda m: "[I;%d,%d,%d,%d,%d,%d]" % tuple(
        int(m.group(k + 1)) + d[k % 3] for k in range(6)), tiles)

root = LT()
root.box(SM, 0, 0, 0, 48, 2, 48)                    # 地板 3x3 格，2 像素厚
root.box(glow(CYAN), 0, 2, 0, 48, 3, 1)              # 前沿灯线
root.panel(QZ, 0, 2, 40, 16, 34, 44, sx=8)           # 墙段（门左侧）
root.box(QP, 0, 2, 39, 2, 34, 44)

children = []
dt, ds, dmn, dmx = load("lab_door.txt")
door_to = (16, 2, 40)
children.append((place(dt, dmn, door_to), ds))
sz = [dmx[k] - dmn[k] for k in range(3)]
print("门尺寸(1/16):", sz, "结构:", ds)
# 门右侧滑动空间保持空着：root 在那里本来就没东西

ct, cs, cmn, cmx = load("office_chair.txt")
children.append((place(ct, cmn, (16, 2, 12)), cs))
print("椅子尺寸(1/16):", [cmx[k] - cmn[k] for k in range(3)], "结构:", cs)

kids = ",".join("{tiles:%s%s}" % (t, ",structure:" + s if s else "") for t, s in children)
# A：正常写法——根带 structure，守卫直接断言通过
tA = root.save("test_child_A.txt", extra=',structure:{id:"fixed"},children:[%s]' % kids)
lt_root.assert_root(tA, "test_child_A.txt")
# B：负对照——故意造【根无 structure】。必须在这里显式声明豁免：
#    负对照只能靠"明确声明"产生，不能靠"忘了加守卫"产生（否则以后分不清是故意的还是漏的）。
#    与 lt_mech_v45.py 里 v4 的豁免写法保持一致。
tB = root.save("test_child_B.txt", extra=',children:[%s]' % kids)
lt_root.fix(tB, "test_child_B", autofix=False, enforce=False, tag="test_child_B.txt",
            exempt_reason="负对照：故意保持根无 structure，用于验证 §3.9 的失败路径"
                          "（导入后整棵树不建父子连接，触发器静默失效）；对照组为 test_child_A.txt")