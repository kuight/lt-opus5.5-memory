from lt_colors import fc

tiles = {}
def put(block, x1, y1, z1, x2, y2, z2):
    if x2 > x1 and y2 > y1 and z2 > z1:
        tiles.setdefault(block, []).append((x1, y1, z1, x2, y2, z2))
def S(h): return fc(h, "solid")

W, H = 16, 32
BASE, BASE2 = "#e6e6e2", "#dcdbd5"

# 1 纯色平滑色块
put(S(BASE), 0, 0, 0, W, H, 2)

# 2 原版石英整面
put("minecraft:quartz_block", 20, 0, 0, 20 + W, H, 2)

# 3 拼缝面板
ox = 40
put(S("#5c5f63"), ox, 0, 1, ox + W, H, 2)
xs, ys = [(0, 7), (8, 16)], [(0, 15), (16, 32)]
for i, (x1, x2) in enumerate(xs):
    for j, (y1, y2) in enumerate(ys):
        put(S(BASE if (i + j) % 2 == 0 else BASE2), ox + x1, y1, 0, ox + x2, y2, 1)
put(S("#5c5f63"), ox + 7, 0, 0, ox + 8, H, 1)
put(S("#5c5f63"), ox, 15, 0, ox + 7, 16, 1)
put(S("#5c5f63"), ox + 8, 15, 0, ox + W, 16, 1)

# 4 渐变做旧
ox = 60
for y1, y2, h in [(0, 2, "#8f8a80"), (2, 4, "#b3aea4"), (4, 7, "#cfcbc2"), (7, 18, BASE)]:
    put(S(h), ox, y1, 0, ox + W, y2, 2)
for y1, y2, sh in [(18, 21, "#d6d3cc"), (21, 24, "#c4c0b7")]:
    for x1, x2, h in [(0, 5, BASE), (5, 6, sh), (6, 10, BASE), (10, 11, sh), (11, 16, BASE)]:
        put(S(h), ox + x1, y1, 0, ox + x2, y2, 2)
put(S(BASE), ox, 24, 0, ox + 4, 26, 2)
put(S("#26282a"), ox + 4, 24, 0, ox + 12, 26, 2)
put(S(BASE), ox + 12, 24, 0, ox + W, 26, 2)
put(S(BASE), ox, 26, 0, ox + W, H, 2)

# 5 原版白混凝土整面
put("minecraft:concrete", 80, 0, 0, 80 + W, H, 2)

parts, n = [], 0
for blk, bxs in tiles.items():
    n += len(bxs)
    fmt = lambda b: "[I;%s]" % ",".join(map(str, b))
    if len(bxs) == 1:
        parts.append('{bBox:%s,tile:{block:"%s"}}' % (fmt(bxs[0]), blk))
    else:
        parts.append('{boxes:[%s],tile:{block:"%s"}}' % (",".join(map(fmt, bxs)), blk))
out = "{tiles:[%s],min:[I;0,0,0],size:[I;96,32,2],count:%d}" % (",".join(parts), n)
open("mat_board.txt", "w", encoding="utf-8").write(out)
print("mat_board.txt", n, "块", len(out), "字节")