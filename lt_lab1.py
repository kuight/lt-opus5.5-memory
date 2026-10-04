from lt_lib import *

def wall_module():
    m = LT()
    m.panel(QZ, 0, 0, 1, 32, 48, 4, sx=16, sy=16)   # 石英拼缝墙面
    m.box(AN, 0, 0, 0, 32, 3, 4)                     # 踢脚
    m.box(QP, 0, 3, 0, 2, 45, 4)                     # 左侧立柱
    m.box(glow(CYAN), 2, 38, 0, 32, 39, 1)           # 灯带
    m.box(QC, 0, 45, 0, 32, 48, 4)                   # 檐口
    m.save("wall_module.txt")

def lab_bench():
    m = LT()
    m.box(AN, 1, 0, 3, 31, 2, 14)                    # 踢脚凹槽
    m.box(IR, 0, 2, 2, 32, 13, 15)                   # 铁柜体
    for x1, x2 in [(1, 10), (11, 21), (22, 31)]:
        m.box(QZ, x1, 3, 1, x2, 12, 2)               # 柜门
        m.box(flat("#2a2c2e"), x1 + 3, 9, 0, x2 - 3, 10, 1)   # 把手
    m.box(glow(CYAN), 0, 12, 0, 32, 13, 1)           # 台面下灯带
    m.box(SM, 0, 13, 0, 32, 15, 16)                  # 台面
    m.panel(QZ, 0, 15, 13, 32, 26, 16, sx=16)        # 后挡板
    m.box(glow(CYAN), 0, 24, 12, 32, 25, 13)         # 挡板灯带
    # 试管架
    m.box(QC, 3, 15, 4, 13, 16, 8)
    m.box(AN, 3, 16, 5, 4, 20, 7)
    m.box(AN, 12, 16, 5, 13, 20, 7)
    m.box(AN, 3, 19, 5, 13, 20, 7)
    for x, c in [(5, "#39ff88"), (7, "#ff5fd2"), (9, "#ffd23f"), (11, "#5fb8ff")]:
        m.box(trans("#e8fbff"), x, 16, 5, x + 1, 22, 7)
        m.box(glow(c), x, 16, 5, x + 1, 19, 7)
    # 显微镜
    m.box(IR, 20, 15, 4, 27, 16, 10)
    m.box(glow("#fff6d8"), 22, 16, 6, 24, 17, 8)
    m.box(QZ, 21, 17, 5, 25, 18, 9)
    m.box(AN, 25, 16, 6, 27, 23, 8)
    m.box(flat("#2a2c2e"), 22, 18, 6, 24, 21, 8)
    m.box(AN, 21, 21, 5, 26, 23, 9)
    m.box(flat("#2a2c2e"), 23, 23, 6, 24, 25, 7)
    m.save("lab_bench.txt")

if __name__ == "__main__":
    wall_module()
    lab_bench()