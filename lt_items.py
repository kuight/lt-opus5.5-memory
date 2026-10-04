# lt_items.py  建筑配件库（依赖 lt_gen.py）
from lt_gen import export

class B:
    """设计坐标：面朝正面（z=0 一侧）看，x 从左到右，y 向上，z 向里"""
    def __init__(s, W):
        s.W = W; s.v = {}
    def fill(s, x1, y1, z1, x2, y2, z2, block, color=None):
        for x in range(s.W - x2, s.W - x1):
            for y in range(y1, y2):
                for z in range(z1, z2):
                    if block is None:
                        s.v.pop((x, y, z), None)
                    else:
                        s.v[(x, y, z)] = (block, color)

WHITE = "minecraft:concrete"; GRAY = "minecraft:concrete:7"; LGRAY = "minecraft:concrete:8"
BLACK = "minecraft:concrete:15"; LIME = "minecraft:concrete:5"; ORANGE = "minecraft:concrete:1"
LANTERN = "minecraft:sea_lantern"; GLASS = "minecraft:glass"

def server_rack():
    b = B(16)
    b.fill(0, 0, 0, 16, 32, 16, BLACK)          # 柜体
    b.fill(1, 2, 0, 15, 30, 2, None)            # 前面挖出放设备的空间
    for i in range(9):                          # 9 层服务器
        y = 3 + i * 3
        b.fill(2, y, 1, 14, y + 2, 2, GRAY)
        b.fill(3, y + 1, 1, 4, y + 2, 2, LIME)
        b.fill(5, y + 1, 1, 6, y + 2, 2, ORANGE if i % 3 == 1 else LIME)
        b.fill(8, y, 1, 13, y + 1, 2, BLACK)    # 散热槽
    b.fill(1, 2, 0, 15, 30, 1, GLASS)           # 玻璃门
    b.fill(0, 1, 0, 1, 31, 1, LANTERN)          # 左侧光边
    b.fill(15, 1, 0, 16, 31, 1, LANTERN)        # 右侧光边
    return b.v

def ring_lamp():
    b = B(16)
    b.fill(5, 15, 5, 11, 16, 11, GRAY)          # 吸顶底座
    b.fill(7, 6, 7, 9, 15, 9, LGRAY)            # 吊杆
    b.fill(1, 5, 7, 15, 6, 9, LGRAY)            # 十字支撑
    b.fill(7, 5, 1, 9, 6, 15, LGRAY)
    for x in range(16):
        for z in range(16):
            d = (x + 0.5 - 8) ** 2 + (z + 0.5 - 8) ** 2
            if 30.25 <= d <= 56.25:
                b.fill(x, 5, z, x + 1, 7, z + 1, WHITE)    # 灯环外壳
                b.fill(x, 4, z, x + 1, 5, z + 1, LANTERN)  # 灯环发光底面
    b.fill(6, 4, 6, 10, 5, 10, LANTERN)         # 中心灯片
    return b.v

def glass_railing():
    b = B(16)
    b.fill(0, 0, 7, 16, 2, 9, GRAY)             # 底座
    b.fill(0, 2, 7, 16, 12, 9, GLASS)           # 玻璃
    b.fill(0, 12, 7, 16, 13, 9, LANTERN)        # 隐藏灯带
    b.fill(0, 13, 6, 16, 15, 10, WHITE)         # 扶手
    b.fill(0, 0, 6, 2, 15, 10, LGRAY)           # 左侧立柱
    return b.v

if __name__ == "__main__":
    for name, fn in (("server_rack", server_rack), ("ring_lamp", ring_lamp), ("glass_railing", glass_railing)):
        out = export(fn())
        open(name + ".txt", "w", encoding="utf-8").write(out)
        print("已写出", name + ".txt，长度", len(out), "字符")