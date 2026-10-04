from lt_colors import fc

MATS = [
    ("minecraft:quartz_block",        "石英块"),
    ("minecraft:quartz_block:2",      "竖纹石英柱"),
    ("minecraft:quartz_block:1",      "錾制石英"),
    ("minecraft:double_stone_slab:8", "平滑石头"),
    ("minecraft:stone:4",             "磨制闪长岩"),
    ("minecraft:iron_block",          "铁块"),
    ("minecraft:stone:6",             "磨制安山岩"),
    ("minecraft:prismarine:2",        "暗海晶石"),
]
DOT = fc("#26282a", "solid")

parts, n = [], 0
for i, (blk, name) in enumerate(MATS):
    ox = i * 20
    parts.append('{bBox:[I;%d,0,0,%d,32,2],tile:{block:"%s"}}' % (ox, ox + 16, blk))
    n += 1
    dots = ",".join("[I;%d,32,0,%d,33,2]" % (ox + 1 + 2 * k, ox + 2 + 2 * k)
                    for k in range(i + 1))
    if i == 0:
        parts.append('{bBox:%s,tile:{block:"%s"}}' % (dots, DOT))
    else:
        parts.append('{boxes:[%s],tile:{block:"%s"}}' % (dots, DOT))
    n += i + 1
    print(i + 1, name, blk)

out = "{tiles:[%s],min:[I;0,0,0],size:[I;156,33,2],count:%d}" % (",".join(parts), n)
open("mat_palette.txt", "w", encoding="utf-8").write(out)
print("mat_palette.txt", n, "块", len(out), "字节")