import sys
X, Y, Z = map(int, sys.argv[1:4])
cmds = []
def f(x1, y1, z1, x2, y2, z2, blk):
    cmds.append("/fill %d %d %d %d %d %d %s" % (X+x1, Y+y1, Z+z1, X+x2, Y+y2, Z+z2, blk))

f(0, 0, 0, 10, 5, 10, "quartz_block 0 hollow")   # 外壳（内部清空）
f(0, 0, 0, 10, 0, 10, "double_stone_slab 8")     # 地板
f(0, 5, 0, 10, 5, 10, "stone 6")                 # 天花板
for x in (0, 10):
    for z in (0, 10):
        f(x, 1, z, x, 4, z, "quartz_block 2")    # 角柱
f(4, 3, 0, 6, 3, 0, "quartz_block 1")            # 门楣
f(5, 1, 0, 5, 2, 0, "air")                       # 门洞

open("room_cmds.txt", "w", encoding="utf-8").write("\n".join(cmds))
print("room_cmds.txt", len(cmds), "条指令")
print("\n".join(cmds))

def p(name, x, y, z, rot):
    print("  %-14s %d %d %d   %s" % (name, X+x, Y+y, Z+z, rot))
print("\n=== 小方块摆放坐标（结构左下前角所在方块）===")
p("lab_door", 5, 1, 1, "原朝向；右侧 6,1,1 要留空给滑门")
for x in (1, 3, 6, 8):
    p("lab_bench", x, 1, 9, "原朝向（面朝北）")
p("server_rack", 5, 1, 9, "原朝向")
for z in (1, 3, 5, 7):
    p("wall_module", 1, 1, z, "转向面朝东，贴西墙")
for z in (3, 4, 5, 6, 7):
    p("server_rack", 9, 1, z, "转向面朝西，贴东墙")
for x in (3, 6):
    p("console", x, 1, 5, "原朝向（面朝北）")
    p("office_chair", x, 1, 4, "转向面朝南，对着控制台")
for x, z in [(3, 3), (7, 3), (3, 7), (7, 7)]:
    p("ring_lamp", x, 4, z, "贴天花板")