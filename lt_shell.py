import sys
X, Y, Z = map(int, sys.argv[1:4])
C = []
def sel(x1, y1, z1, x2, y2, z2):
    C.append("//pos1 %d,%d,%d" % (X+x1, Y+y1, Z+z1))
    C.append("//pos2 %d,%d,%d" % (X+x2, Y+y2, Z+z2))
def s(b, *r): sel(*r); C.append("//set " + b)
def w(b, *r): sel(*r); C.append("//walls " + b)

QZ, QP, BLK, WHT, GRY = "155:0", "155:2", "251:15", "251:0", "251:7"
GLASS, LAMP, IRON = "95:15", "169", "42"

# 1 地面光环 + 基座
w(LAMP, -2, 0, -2, 12, 0, 12)
w(GRY,  -1, 0, -1, 11, 0, 11)
# 2 墙体：黑勒脚 + 黑玻璃窗带 + 窗棂 + 角柱
w(BLK,   0, 1, 0, 10, 1, 10)
w(GLASS, 0, 2, 0, 10, 3, 10)
for i in (2, 4, 6, 8):
    s(QP, i, 2, 0, i, 3, 0);  s(QP, i, 2, 10, i, 3, 10)
    s(QP, 0, 2, i, 0, 3, i);  s(QP, 10, 2, i, 10, 3, i)
for x in (0, 10):
    for z in (0, 10):
        s(QP, x, 1, z, x, 4, z)
# 3 檐口：发光带 + 黑檐板 + 石英女儿墙
w(LAMP, -1, 4, -1, 11, 4, 11)
w(BLK,  -1, 5, -1, 11, 5, 11)
w(QZ,   -1, 6, -1, 11, 6, 11)
# 4 入口：门框 + 发光门楣 + 门洞 + 雨棚 + 步道
s(IRON, 4, 1, 0, 6, 3, 0)
s(LAMP, 5, 3, 0, 5, 3, 0)
s("0",  5, 1, 0, 5, 2, 0)
s(WHT,  3, 4, -3, 7, 4, -1)
s(LAMP, 3, 4, -3, 7, 4, -3)
s("43:8", 4, 0, -4, 6, 0, -1)
s(LAMP, 5, 0, -4, 5, 0, -1)
# 5 屋顶设备
s(IRON,   1, 6, 5, 5, 6, 9)
s("151",  1, 7, 5, 5, 7, 9)
s(GRY,    7, 6, 6, 9, 7, 9)
s("101",  7, 6, 5, 9, 7, 5)
s(IRON,   8, 6, 2, 8, 6, 2)
s("101",  8, 7, 2, 8, 10, 2)
s("198:1", 8, 11, 2, 8, 11, 2)

open("shell_cmds.txt", "w", encoding="utf-8").write("\n".join(C))
print("shell_cmds.txt", len(C), "条指令")