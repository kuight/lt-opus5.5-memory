from lt_colors import fc

QZ = "minecraft:quartz_block"
QP = "minecraft:quartz_block:2"
QC = "minecraft:quartz_block:1"
SM = "minecraft:double_stone_slab:8"
DI = "minecraft:stone:4"
IR = "minecraft:iron_block"
AN = "minecraft:stone:6"
PR = "minecraft:prismarine:2"
CYAN = "#7fe9ff"
def glow(h): return fc(h, "glow")
def trans(h): return fc(h, "trans")
def flat(h): return fc(h, "solid")

class LT:
    def __init__(s):
        s.v = {}

    def box(s, blk, x1, y1, z1, x2, y2, z2):
        for x in range(x1, x2):
            for y in range(y1, y2):
                for z in range(z1, z2):
                    if blk is None:
                        s.v.pop((x, y, z), None)
                    else:
                        s.v[(x, y, z)] = blk

    def panel(s, blk, x1, y1, z1, x2, y2, z2, sx=0, sy=0, gap=AN, both=False):
        """带凹缝面板，正面朝 z1；sx/sy 为缝间距；both=True 两面都有缝(厚度>=3)"""
        s.box(blk, x1, y1, z1, x2, y2, z2)
        faces = [((z1, z1 + 1), (z1 + 1, z1 + 2))]
        if both:
            faces.append(((z2 - 1, z2), (z2 - 2, z2 - 1)))
        lines = []
        if sx:
            lines += [(x, y1, x + 1, y2) for x in range(x1 + sx, x2, sx)]
        if sy:
            lines += [(x1, y, x2, y + 1) for y in range(y1 + sy, y2, sy)]
        for (f1, f2), (g1, g2) in faces:
            for a1, b1, a2, b2 in lines:
                s.box(None, a1, b1, f1, a2, b2, f2)
                s.box(gap, a1, b1, g1, a2, b2, g2)

    def save(s, fn, extra=""):
        mats = {}
        for p, b in s.v.items():
            mats.setdefault(b, set()).add(p)
        parts, n = [], 0
        for b, S in mats.items():
            out = []
            for p in sorted(S, key=lambda q: (q[1], q[2], q[0])):
                if p not in S:
                    continue
                x, y, z = p
                x2 = x + 1
                while (x2, y, z) in S:
                    x2 += 1
                z2 = z + 1
                while all((i, y, z2) in S for i in range(x, x2)):
                    z2 += 1
                y2 = y + 1
                while all((i, y2, k) in S for i in range(x, x2) for k in range(z, z2)):
                    y2 += 1
                for i in range(x, x2):
                    for j in range(y, y2):
                        for k in range(z, z2):
                            S.discard((i, j, k))
                out.append("[I;%d,%d,%d,%d,%d,%d]" % (x, y, z, x2, y2, z2))
            n += len(out)
            if len(out) == 1:
                parts.append('{bBox:%s,tile:{block:"%s"}}' % (out[0], b))
            else:
                parts.append('{boxes:[%s],tile:{block:"%s"}}' % (",".join(out), b))
        P = list(s.v)
        mn = [min(p[i] for p in P) for i in range(3)]
        sz = [max(p[i] for p in P) + 1 - mn[i] for i in range(3)]
        txt = "{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d%s}" % (
            ",".join(parts), mn[0], mn[1], mn[2], sz[0], sz[1], sz[2], n, extra)
        open(fn, "w", encoding="utf-8").write(txt)
        print(fn, n, "块", len(txt), "字节", "尺寸", sz)
        return txt