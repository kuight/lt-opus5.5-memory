import re, glob, sys
from lt_colors import fc

# 主题色，可随时改
GLASS_HEX = "#bdeeff"   # 玻璃 → 淡青半透明
LAMP_HEX  = "#d9f6ff"   # 无色/灰色灯 → 冷白发光

GLASS = {"minecraft:glass", "minecraft:stained_glass"}
LAMP  = {"minecraft:sea_lantern", "minecraft:glowstone"}
TILE  = re.compile(r'tile:\{([^{}]*)\}')

def base_name(b):
    return b.rsplit(":", 1)[0] if b.count(":") == 2 else b

def argb_hex(c):
    v = int(c) & 0xFFFFFF
    r, g, b = v >> 16, (v >> 8) & 255, v & 255
    return "#%06x" % v, max(r, g, b) - min(r, g, b)

def recolor(text, log):
    def sub(m):
        body = m.group(1)
        bm = re.search(r'block:"([^"]+)"', body)
        if not bm:
            return m.group(0)
        blk = base_name(bm.group(1))
        cm = re.search(r'color:(-?\d+)', body)
        if blk in GLASS:
            new = fc(GLASS_HEX, "trans")
        elif blk in LAMP:
            h = LAMP_HEX
            if cm:
                hx, spread = argb_hex(cm.group(1))
                if spread >= 40:      # 有明显颜色才保留
                    h = hx
            new = fc(h, "glow")
        else:
            return m.group(0)
        log.append(f"  {bm.group(1)}{' color:'+cm.group(1) if cm else ''} -> {new}")
        return 'tile:{block:"%s"}' % new
    return TILE.sub(sub, text)

files = sys.argv[1:] or [f for f in glob.glob("*.txt")
        if not f.endswith("_fc.txt") and not f.startswith("sample")]
for f in files:
    src = open(f, encoding="utf-8").read()
    log = []
    out = recolor(src, log)
    if log:
        dst = f[:-4] + "_fc.txt"
        open(dst, "w", encoding="utf-8").write(out)
        print(f"{f} -> {dst}  替换 {len(log)} 处")
        print("\n".join(log))
    else:
        print(f"{f}  无需替换")