# -*- coding: utf-8 -*-
# lt_seam.py —— 弧直接缝检查（设计方编写）
# 用法：python lt_seam.py <file.txt> <X>
#   直段 = AABB 完全在 x<=X 的盒；弧段 = 完全在 x>=X 的盒。
#   取各盒落在平面 x=X 上的角点围成的面，按 1px 网格栅格化（z,y）。
#   问题：①直段端面有格子没被弧段起始面盖住（= 缝/错位）②有角点距 X 在 (0,1.5]px（差一点没对齐）
#        ③有盒子横跨接缝 ④任一侧在接缝处没有面
#   弧段多出来的面（如肋框侧面）只报信息，不算问题。
import io, re, sys, math, os
sys.path.insert(0, os.getcwd())
import lt_tbox

CORN = {"EUN": (1, 1, 0), "EUS": (1, 1, 1), "EDN": (1, 0, 0), "EDS": (1, 0, 1),
        "WUN": (0, 1, 0), "WUS": (0, 1, 1), "WDN": (0, 0, 0), "WDS": (0, 0, 1)}


def boxes_of(t):
    out = []
    for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', t):
        out.append([int(v) for v in m.group(1).split(",")])
    for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', t, re.S):
        for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            out.append([int(v) for v in mm.group(1).split(",")])
    return out


def corners(a):
    x0, y0, z0, x1, y1, z1 = a[:6]
    off = {}
    if len(a) > 6:
        for o in lt_tbox.decode(a)["offsets"]:
            off.setdefault(o["corner"], {})[o["axis"]] = o["offset"]
    pts = []
    for c, (ex, ey, ez) in CORN.items():
        o = off.get(c, {})
        pts.append(((x1 if ex else x0) + o.get("X", 0),
                    (y1 if ey else y0) + o.get("Y", 0),
                    (z1 if ez else z0) + o.get("Z", 0)))
    return pts


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def cells_in(h):
    if len(h) < 3:
        return set()
    zs = [p[0] for p in h]; ys = [p[1] for p in h]
    out = set()
    for z in range(int(math.floor(min(zs))), int(math.ceil(max(zs)))):
        for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys)))):
            pz, py = z + 0.5, y + 0.5
            ok = True
            for i in range(len(h)):
                a, b = h[i], h[(i + 1) % len(h)]
                if (b[0] - a[0]) * (py - a[1]) - (b[1] - a[1]) * (pz - a[0]) < -1e-9:
                    ok = False; break
            if ok:
                out.add((z, y))
    return out


def main():
    path, X = sys.argv[1], int(sys.argv[2])
    t = io.open(path, encoding="utf-8").read()
    A, B = set(), set()
    near = cross = na = nb = 0
    allb = [a for a in boxes_of(t) if len(a) >= 6]
    for a in allb:
        pts = corners(a)
        near += sum(1 for p in pts if 0 < abs(p[0] - X) <= 1.5)
        if a[0] < X < a[3]:
            cross += 1
            continue
        on = [(p[2], p[1]) for p in pts if p[0] == X]
        if len(set(on)) < 3:
            continue
        c = cells_in(hull(on))
        if a[3] <= X:
            A |= c; na += 1
        elif a[0] >= X:
            B |= c; nb += 1
    probs = []
    if not A: probs.append("直段在 x=%d 处没有端面" % X)
    if not B: probs.append("弧段在 x=%d 处没有起始面" % X)
    miss = A - B
    if miss: probs.append("直段端面有 %d 个 1px 格没被弧段盖住（缝/错位），例：%s" % (len(miss), sorted(miss)[:8]))
    if near: probs.append("有 %d 个角点距接缝面 (0,1.5]px（差一点没对齐）" % near)
    if cross: probs.append("有 %d 个盒子横跨接缝面" % cross)
    print("== %s  接缝 x=%d：盒子 %d 个；直段贴缝盒 %d、弧段贴缝盒 %d；直段端面 %d 格、弧段起始面 %d 格"
          % (path, X, len(allb), na, nb, len(A), len(B)))
    print("   信息：弧段多出（外露侧面，非问题）%d 格" % len(B - A))
    for p in probs:
        print("   [问题] " + p)
    print("   结论：%s" % ("通过" if not probs else "不通过"))
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()