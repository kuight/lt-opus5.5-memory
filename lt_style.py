import re, sys, glob, random
from lt_colors import fc

GLASS = {"minecraft:glass", "minecraft:stained_glass"}
LAMP  = {"minecraft:sea_lantern", "minecraft:glowstone"}
GLASS_HEX, LAMP_HEX = "#bdeeff", "#d9f6ff"

# 大面混搭：原方块 -> ([(方块, 权重)...], 拼块格距(1/16), 触发的最小面尺寸)
TEXTURE_MIX = {
    "minecraft:concrete":    ([("minecraft:concrete", 6), ("minecraft:quartz_block", 3)], 8, 6),
    "minecraft:concrete:7":  ([("minecraft:concrete:7", 5), ("minecraft:stone:6", 3), ("minecraft:stone:5", 2)], 8, 6),
    "minecraft:concrete:15": ([("minecraft:concrete:15", 6), ("minecraft:coal_block", 2)], 8, 6),
}
STYLES = {"clean": {}, "texture": TEXTURE_MIX}

ENTRY = re.compile(r'\{(boxes:\[(?:\[I;[-\d,]+\],?)*\]|bBox:\[I;[-\d,]+\]),tile:\{([^{}]*)\}\}')
BOX = re.compile(r'\[I;([-\d,]+)\]')
BLK = re.compile(r'block:"([^"]+)"')
COL = re.compile(r'color:(-?\d+)')

def base(n): return ":".join(n.split(":")[:2])
def mid(b): return sorted([b[3]-b[0], b[4]-b[1], b[5]-b[2]])[1]

def lamp_hex(body):
    m = COL.search(body)
    if m:
        v = int(m.group(1)) & 0xFFFFFF
        r, g, b = v >> 16, (v >> 8) & 255, v & 255
        if max(r, g, b) - min(r, g, b) >= 40:
            return "#%06x" % v, True
    return LAMP_HEX, False

def cuts(a, c, g):
    res, s = [], a
    while s < c:
        e = min(c, (s // g + 1) * g); res.append((s, e)); s = e
    return res

def split(b, g):
    return [[x1, y1, z1, x2, y2, z2]
            for x1, x2 in cuts(b[0], b[3], g)
            for y1, y2 in cuts(b[1], b[4], g)
            for z1, z2 in cuts(b[2], b[5], g)]

def process(text, mix, allow_split, st):
    def sub(m):
        raw, body = m.group(1), m.group(2)
        bm = BLK.search(body)
        if not bm:
            return m.group(0)
        name = bm.group(1); bn = base(name)
        groups = {}
        add = lambda bd, bx: groups.setdefault(bd, []).append(bx)
        for b in [list(map(int, s.split(","))) for s in BOX.findall(raw)]:
            if len(b) != 6:
                add(body, b); continue
            if bn in GLASS:
                add('block:"%s"' % fc(GLASS_HEX, "trans"), b); st["玻璃"] += 1
            elif bn in LAMP:
                hx, colored = lamp_hex(body)
                if colored or mid(b) <= 1:
                    add('block:"%s"' % fc(hx, "glow"), b); st["细灯"] += 1
                else:
                    add(body, b); st["灯面保留"] += 1
            elif name in mix and mid(b) >= mix[name][2]:
                opts, g, _ = mix[name]
                parts = split(b, g) if allow_split else [b]
                st["拆分新增"] += len(parts) - 1; st["混搭"] += 1
                for p in parts:
                    rnd = random.Random(p[0]*73856093 ^ p[1]*19349663 ^ p[2]*83492791)
                    pick = rnd.choices([o[0] for o in opts], [o[1] for o in opts])[0]
                    add(BLK.sub('block:"%s"' % pick, body, count=1), p)
            else:
                add(body, b)
        out = []
        for bd, bxs in groups.items():
            if len(bxs) == 1:
                out.append("{bBox:[I;%s],tile:{%s}}" % (",".join(map(str, bxs[0])), bd))
            else:
                s = ",".join("[I;%s]" % ",".join(map(str, x)) for x in bxs)
                out.append("{boxes:[%s],tile:{%s}}" % (s, bd))
        return ",".join(out)
    return ENTRY.sub(sub, text)

style = sys.argv[1] if len(sys.argv) > 1 else "clean"
mix = STYLES[style]
files = sys.argv[2:] or [f for f in glob.glob("*.txt") if not f.startswith("sample")
                         and not re.search(r'_(fc|clean|texture)\.txt$', f)]
for f in files:
    src = open(f, encoding="utf-8").read()
    ok = "children" not in src and src.count("count:") == 1
    st = {"玻璃": 0, "细灯": 0, "灯面保留": 0, "混搭": 0, "拆分新增": 0}
    out = process(src, mix, ok, st)
    if st["拆分新增"]:
        out = re.sub(r'count:(\d+)', lambda m: "count:%d" % (int(m.group(1)) + st["拆分新增"]), out)
    dst = f[:-4] + "_" + style + ".txt"
    open(dst, "w", encoding="utf-8").write(out)
    print(f, "->", dst, st, "" if ok else "(含子结构，未拆分)")