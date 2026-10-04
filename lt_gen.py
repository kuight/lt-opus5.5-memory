# lt_gen.py  LittleTiles 1.12.2 导入文本生成器（grid=16）
import re, sys
from collections import defaultdict

def parse(text):
    vox = {}
    for kind, boxes, tile in re.findall(r'\{(boxes|bBox):(.*?),tile:\{(.*?)\}\}', text):
        cm = re.search(r'color:(-?\d+)', tile)
        color = int(cm.group(1)) if cm else None
        block = re.search(r'block:"([^"]+)"', tile).group(1)
        for nums in re.findall(r'\[I;([-\d,]+)\]', boxes):
            x1, y1, z1, x2, y2, z2 = map(int, nums.split(','))
            for x in range(x1, x2):
                for y in range(y1, y2):
                    for z in range(z1, z2):
                        vox[(x, y, z)] = (block, color)
    return vox

def mesh(vox):
    rem = dict(vox)
    out = []
    for key in sorted(vox, key=lambda p: (p[1], p[2], p[0])):
        if key not in rem:
            continue
        m = rem[key]
        x0, y0, z0 = key
        x1 = x0 + 1
        while rem.get((x1, y0, z0)) == m:
            x1 += 1
        z1 = z0 + 1
        while all(rem.get((x, y0, z1)) == m for x in range(x0, x1)):
            z1 += 1
        y1 = y0 + 1
        while all(rem.get((x, y1, z)) == m for x in range(x0, x1) for z in range(z0, z1)):
            y1 += 1
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    del rem[(x, y, z)]
        out.append((m, (x0, y0, z0, x1, y1, z1)))
    return out

def export(vox):
    mx = min(p[0] for p in vox); my = min(p[1] for p in vox); mz = min(p[2] for p in vox)
    vox = {(x - mx, y - my, z - mz): m for (x, y, z), m in vox.items()}
    groups = defaultdict(list)
    for m, b in mesh(vox):
        groups[m].append(b)
    parts, n = [], 0
    for (block, color), bl in groups.items():
        tile = ('{color:%d,block:"%s"}' % (color, block)) if color is not None else ('{block:"%s"}' % block)
        n += len(bl)
        if len(bl) == 1:
            parts.append('{bBox:[I;%s],tile:%s}' % (','.join(map(str, bl[0])), tile))
        else:
            bs = ','.join('[I;%s]' % ','.join(map(str, b)) for b in bl)
            parts.append('{boxes:[%s],tile:%s}' % (bs, tile))
    sx = max(p[0] for p in vox) + 1; sy = max(p[1] for p in vox) + 1; sz = max(p[2] for p in vox) + 1
    return '{tiles:[%s],min:[I;0,0,0],size:[I;%d,%d,%d],count:%d}' % (','.join(parts), sx, sy, sz, n)

def build_console():
    v = {}
    def fill(x1, y1, z1, x2, y2, z2, block, color=None):
        for x in range(x1, x2):
            for y in range(y1, y2):
                for z in range(z1, z2):
                    if block is None:
                        v.pop((x, y, z), None)
                    else:
                        v[(x, y, z)] = (block, color)
    WHITE = "minecraft:concrete"; GRAY = "minecraft:concrete:7"; LGRAY = "minecraft:concrete:8"
    BLACK = "minecraft:concrete:15"; LIME = "minecraft:concrete:5"; ORANGE = "minecraft:concrete:1"
    LANTERN = "minecraft:sea_lantern"; GLASS = "minecraft:glass"; GLOW = "minecraft:glowstone"
    RED = "minecraft:wool:14"; GREEN = "minecraft:wool:5"
    # 柜体（正面朝 z=0 一侧）
    fill(1, 0, 2, 31, 2, 15, BLACK)            # 内缩踢脚
    fill(0, 2, 1, 32, 12, 16, WHITE)           # 柜体
    fill(0, 2, 1, 1, 12, 16, GRAY)             # 左侧板
    fill(31, 2, 1, 32, 12, 16, GRAY)           # 右侧板
    for y in (4, 6, 8):                        # 散热格栅
        fill(3, y, 1, 13, y + 1, 2, BLACK)
        fill(19, y, 1, 29, y + 1, 2, BLACK)
    fill(15, 3, 1, 17, 11, 2, LANTERN)         # 正面中央光带
    fill(0, 12, 0, 32, 13, 16, LGRAY)          # 台面（前沿外挑）
    fill(1, 11, 0, 31, 12, 1, LANTERN)         # 台面下沿灯带
    # 键盘
    fill(6, 13, 2, 27, 14, 7, BLACK)
    for x in range(7, 26, 2):
        for z in (3, 5):
            fill(x, 14, z, x + 1, 15, z + 1, WHITE)
    fill(28, 13, 3, 30, 14, 5, RED)            # 红色按钮
    fill(28, 13, 6, 30, 14, 8, GREEN)          # 绿色按钮
    # 显示器
    fill(3, 13, 10, 29, 27, 15, BLACK)         # 外壳和边框
    fill(5, 15, 11, 27, 25, 12, LANTERN)       # 发光屏幕
    fill(5, 15, 10, 27, 25, 11, GLASS)         # 屏幕玻璃
    for i, h in enumerate((3, 6, 4, 8, 5)):    # 柱状图
        x = 7 + i * 3
        fill(x, 16, 11, x + 2, 16 + h, 12, LIME)
    fill(23, 22, 11, 26, 23, 12, RED)          # 右侧数据条
    fill(23, 19, 11, 26, 20, 12, ORANGE)
    fill(23, 16, 11, 25, 17, 12, LIME)
    fill(25, 27, 13, 26, 28, 14, GLOW)         # 顶部状态灯
    return v

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "verify":
        text = open(sys.argv[2], encoding="utf-8").read()
        v1 = parse(text)
        out = export(v1)
        v2 = parse(out)
        print("原样品体素数:", len(v1), " 重建后体素数:", len(v2), " 完全一致:", v1 == v2)
        open("sample_rebuilt.txt", "w", encoding="utf-8").write(out)
        print("已写出 sample_rebuilt.txt")
    elif cmd == "console":
        out = export(build_console())
        open("console.txt", "w", encoding="utf-8").write(out)
        print("已写出 console.txt，长度", len(out), "字符")