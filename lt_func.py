# lt_func.py  带功能属性的家具（依赖 lt_gen.py 和 lt_items.py）
from lt_gen import export
from lt_items import B, WHITE, GRAY, LGRAY, BLACK, LIME, LANTERN, GLASS

YELLOW = "minecraft:concrete:4"; BLUEGLASS = "minecraft:stained_glass:3"
WOOL_W = "minecraft:wool:0"; WOOL_LB = "minecraft:wool:3"

def with_struct(v, s):
    t = export(v)
    return t[:-1] + ",structure:" + s + "}"

def office_chair():
    b = B(16)
    for box in ((1, 0, 7, 3, 1, 9), (13, 0, 7, 15, 1, 9), (7, 0, 1, 9, 1, 3), (7, 0, 13, 9, 1, 15)):
        b.fill(*box, GRAY)                       # 轮子
    b.fill(1, 1, 7, 15, 2, 9, BLACK)             # 星形脚
    b.fill(7, 1, 1, 9, 2, 15, BLACK)
    b.fill(7, 2, 7, 9, 6, 9, LGRAY)              # 气压杆
    b.fill(2, 6, 2, 14, 7, 14, GRAY)             # 座板
    b.fill(2, 7, 2, 14, 9, 14, BLACK)            # 坐垫
    b.fill(1, 7, 9, 2, 9, 10, LGRAY)             # 扶手支撑
    b.fill(14, 7, 9, 15, 9, 10, LGRAY)
    b.fill(1, 9, 5, 2, 10, 12, LGRAY)            # 扶手
    b.fill(14, 9, 5, 15, 10, 12, LGRAY)
    b.fill(7, 9, 13, 9, 11, 15, LGRAY)           # 靠背支撑
    b.fill(2, 11, 13, 14, 22, 15, BLACK)         # 靠背
    b.fill(7, 12, 12, 9, 21, 13, LANTERN)        # 靠背发光带
    return with_struct(b.v, '{name:"办公椅",id:"chair"}')

def lab_door():
    b = B(16)
    b.fill(0, 0, 7, 16, 32, 9, WHITE)            # 门板
    b.fill(0, 0, 7, 16, 3, 9, BLACK)             # 警示条底色
    for x in range(0, 16, 4):
        b.fill(x, 0, 7, x + 2, 3, 9, YELLOW)     # 黄色斜纹
    b.fill(4, 6, 7, 13, 27, 9, BLUEGLASS)        # 玻璃窗
    b.fill(0, 3, 7, 1, 32, 9, LANTERN)           # 侧边发光带
    b.fill(2, 12, 6, 3, 20, 10, LGRAY)           # 把手（两面）
    b.fill(7, 29, 6, 10, 30, 10, LIME)           # 状态灯
    return with_struct(b.v, '{duration:30,interpolation:0,distance:16,name:"实验室滑门",activateParent:0b,id:"slidingDoor",events:[],disableRightClick:0b,direction:5}')

def med_bed():
    b = B(32)
    b.fill(2, 0, 2, 30, 2, 14, GRAY)             # 底座
    b.fill(2, 1, 1, 30, 2, 2, LANTERN)           # 底座灯带
    b.fill(2, 1, 14, 30, 2, 15, LANTERN)
    b.fill(0, 2, 0, 32, 4, 16, WHITE)            # 床框
    b.fill(1, 4, 1, 31, 6, 15, WOOL_W)           # 床垫
    b.fill(12, 4, 1, 31, 7, 15, WOOL_LB)         # 被子
    b.fill(3, 6, 3, 8, 7, 13, WOOL_W)            # 枕头
    b.fill(0, 4, 0, 1, 15, 16, WHITE)            # 床头板
    b.fill(1, 8, 4, 2, 14, 12, BLACK)            # 心电屏边框
    b.fill(1, 9, 5, 2, 13, 11, LANTERN)          # 屏幕
    b.fill(1, 11, 5, 2, 12, 11, LIME)            # 心电线
    b.fill(1, 12, 7, 2, 13, 8, LIME)
    for z in (0, 15):                            # 两侧护栏
        b.fill(14, 6, z, 15, 9, z + 1, LGRAY)
        b.fill(26, 6, z, 27, 9, z + 1, LGRAY)
        b.fill(14, 8, z, 27, 9, z + 1, LGRAY)
    return with_struct(b.v, '{name:"医疗舱床",id:"bed",direction:3}')

def service_ladder():
    b = B(16)
    b.fill(2, 0, 13, 4, 32, 16, LGRAY)           # 左立轨
    b.fill(12, 0, 13, 14, 32, 16, LGRAY)         # 右立轨
    for y in range(2, 32, 4):
        b.fill(4, y, 14, 12, y + 1, 15, GRAY)    # 横档
    for y in range(3, 32, 8):
        b.fill(2, y, 12, 4, y + 1, 13, LANTERN)  # 指示灯
        b.fill(12, y, 12, 14, y + 1, 13, LANTERN)
    return with_struct(b.v, '{name:"检修梯",id:"ladder"}')

if __name__ == "__main__":
    for name, fn in (("office_chair", office_chair), ("lab_door", lab_door), ("med_bed", med_bed), ("service_ladder", service_ladder)):
        out = fn()
        open(name + ".txt", "w", encoding="utf-8").write(out)
        print("已写出", name + ".txt，长度", len(out), "字符")