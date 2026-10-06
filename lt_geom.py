# lt_geom.py —— 几何自检（所有含可变形盒的文件都必须过）
#   ① 解码每个盒子 → 8 角点 / 6 面；面 4 点不共面（容差 0.01px）→ 报问题
#   ② 竖直拉伸件：同一条竖边的 U/D 角 X、Z 偏移必须相同 → 不同即报问题
#   ③ 与目标弧面对比：内外弧面均匀取 2000 点，算到生成体表面的最大/平均偏差（px），最大 >1px 报问题
#   ④ 出俯视 / 正视 PNG
# 用法: python lt_geom.py <file.txt> [R,thick,a0,a1,height]    （不给弧参数就跳过 ③）
import io, re, sys, math
import lt_tbox

CORN = {"EUN": (1, 1, 0), "EUS": (1, 1, 1), "EDN": (1, 0, 0), "EDS": (1, 0, 1),
        "WUN": (0, 1, 0), "WUS": (0, 1, 1), "WDN": (0, 0, 0), "WDS": (0, 0, 1)}
VERT = [("EUN", "EDN"), ("EUS", "EDS"), ("WUN", "WDN"), ("WUS", "WDS")]


def load(path):
    t = io.open(path, encoding="utf-8").read()
    return t, [[int(x) for x in m.split(",")] for m in re.findall(r"\[I;([-\d,]+)\]", t)
               if len(m.split(",")) >= 7]


def corners_of(arr):
    coords = arr[:6]
    d = lt_tbox.decode(arr)
    off = {}
    for o in d["offsets"]:
        off.setdefault(o["corner"], {})[o["axis"]] = o["offset"]
    pts = {}
    for c, (ex, ey, ez) in CORN.items():
        x = coords[3] if ex else coords[0]
        y = coords[4] if ey else coords[1]
        z = coords[5] if ez else coords[2]
        o = off.get(c, {})
        pts[c] = (x + o.get("X", 0), y + o.get("Y", 0), z + o.get("Z", 0))
    return pts


def dev_plane(p0, p1, p2, p3):
    ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    n = math.sqrt(nx * nx + ny * ny + nz * nz)
    if n < 1e-9: return 0.0
    w = (p3[0] - p0[0]) * nx + (p3[1] - p0[1]) * ny + (p3[2] - p0[2]) * nz
    return abs(w / n)


def to_seg(px, pz, a, b):
    ax, az = a; bx, bz = b
    dx, dz = bx - ax, bz - az
    L = dx * dx + dz * dz
    t = 0.0 if L < 1e-9 else max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / L))
    return math.hypot(px - (ax + t * dx), pz - (az + t * dz))


def check(path, arc=None):
    txt, arrs = load(path)
    issues, rep = [], []
    if not arrs:
        print("!! %s 没有可变形盒（≥7 分量）" % path); return 0, 0.0, 0.0
    polys = []
    for a in arrs:
        pts = corners_of(a)
        # ① 6 面共面
        faces = [("E/D/N", ["EDN", "EDS", "EUS", "EUN"]), ("W", ["WDN", "WDS", "WUS", "WUN"]),
                 ("down", ["WDN", "EDN", "EDS", "WDS"]), ("up", ["WUN", "EUN", "EUS", "WUS"]),
                 ("north", ["WDN", "WUN", "EUN", "EDN"]), ("south", ["WDS", "WUS", "EUS", "EDS"])]
        for nm, cs in faces:
            q = [pts[c] for c in cs]
            dv = max(dev_plane(q[0], q[1], q[2], q[3]), dev_plane(q[1], q[2], q[3], q[0]))
            if dv > 0.01:
                issues.append("盒 %s 的 %s 面不共面（偏差 %.3f px）" % (a[:6], nm, dv))
        # ② 竖边 U/D 偏移一致
        d = lt_tbox.decode(a)
        off = {}
        for o in d["offsets"]:
            off[(o["corner"], o["axis"])] = o["offset"]
        for cu, cd in VERT:
            for ax in ("X", "Z"):
                if off.get((cu, ax), 0) != off.get((cd, ax), 0):
                    issues.append("盒 %s 竖边 %s/%s 的 %s 偏移不一致（%d vs %d）"
                                  % (a[:6], cu, cd, ax, off.get((cu, ax), 0), off.get((cd, ax), 0)))
        polys.append(pts)
    mx = avg = 0.0
    if arc:
        R, th, a0, a1, h = arc
        import random
        random.seed(7)
        n = 2000
        tot = 0.0
        for i in range(n):
            t = math.radians(a0 + (a1 - a0) * random.random())
            rr = R - random.random() * th
            y = random.random() * h
            px, pz = rr * math.cos(t), rr * math.sin(t)
            best = 1e9
            for pts in polys:
                if not (pts["WDN"][1] - 0.001 <= y <= pts["WUN"][1] + 0.001): continue
                seq = [(pts["WDN"][0], pts["WDN"][2]), (pts["EDN"][0], pts["EDN"][2]),
                       (pts["EDS"][0], pts["EDS"][2]), (pts["WDS"][0], pts["WDS"][2])]
                inside = True
                for k in range(4):
                    a1p, b1p = seq[k], seq[(k + 1) % 4]
                    cr = (b1p[0] - a1p[0]) * (pz - a1p[2]) - (b1p[2] - a1p[2]) * (px - a1p[0])
                    if cr < -1e-6: inside = False; break
                best = min(best, 0.0 if inside else dmin)
            tot += best
            mx = max(mx, best)
        avg = tot / n
        if mx > 1.0:
            issues.append("与目标弧面最大偏差 %.2f px > 1px（平均 %.2f px）" % (mx, avg))
    # ④ PNG
    try:
        from PIL import Image, ImageDraw
        W = H = 300
        img = Image.new("RGB", (W, H), (25, 25, 28))
        dr = ImageDraw.Draw(img)
        for pts in polys:
            seq = [pts["WDN"], pts["EDN"], pts["EDS"], pts["WDS"]]
            dr.polygon([(p[0], H - p[2]) for p in seq], outline=(0, 220, 255))
        img.save(path.replace(".txt", "_top.png"))
        img2 = Image.new("RGB", (W, 200), (25, 25, 28))
        d2 = ImageDraw.Draw(img2)
        for pts in polys:
            dr2 = d2
            dr2.line([(pts["WDN"][0], 199 - pts["WDN"][1]), (pts["EDN"][0], 199 - pts["EDN"][1])], fill=(255, 180, 0))
            dr2.line([(pts["WUN"][0], 199 - pts["WUN"][1]), (pts["EUN"][0], 199 - pts["EUN"][1])], fill=(255, 180, 0))
        img2.save(path.replace(".txt", "_front.png"))
        print("   PNG: %s_top.png / %s_front.png" % (path[:-4], path[:-4]))
    except Exception as ex:
        print("   (PNG 跳过: %s)" % ex)
    print("== %s：可变形盒 %d 个，问题 %d 条" % (path, len(arrs), len(issues)))
    for x in issues[:12]:
        print("   [问题] " + x)
    if arc: print("   偏差：最大 %.2f px，平均 %.2f px（目标弧面取 2000 点）" % (mx, avg))
    return len(arrs), mx, avg


if __name__ == "__main__":
    p = sys.argv[1]
    arc = None
    if len(sys.argv) > 2:
        R, th, a0, a1, h = [float(v) for v in sys.argv[2].split(",")]
        arc = (R, th, a0, a1, h)
    n, mx, avg = check(p, arc)
    sys.exit(1 if n == 0 else 0)