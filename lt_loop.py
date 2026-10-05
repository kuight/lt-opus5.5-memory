# lt_loop.py  pre199 自转扇叶样品：3×3 格 4 片叶 + 青色发光轴，advancedDoor rotY 0→360（linear, 40 tick）
# 关键帧编码依据 ValueTimeline.write()（pre199 lt_src:168-181）+ LinearTimeline.getAdditionalDataSize()=0（:347-350）：
#   线性格式 = [I; 0, 点数, (tick, 值double高32位, 值double低32位) × N ]   —— 没有 hermite 那 3 个尾巴
import struct, lt_np, lt_colors, lt_root

NAME = "扇叶"                      # 结构名：/lt-open 的过滤参数用得上
DUR, SPIN = 40, 360.0              # 40 tick 转满一圈


def F(h, k="solid"): return lt_colors.fc(h, k)


def dbl(v):
    b = struct.unpack(">q", struct.pack(">d", float(v)))[0]; lo = b & 0xFFFFFFFF
    return [b >> 32, lo - (1 << 32) if lo >= 1 << 31 else lo]


def tl_linear(pts):
    a = [0, len(pts)]                       # type 0 = linear
    for t, v in pts: a += [t] + dbl(v)
    return "[I;" + ",".join(map(str, a)) + "]"


# 自检：360.0 的 IEEE754 = 0x4076800000000000 → 高32 = 0x40768000 = 1081507840，低32 = 0
assert tl_linear([(0, 0), (40, 360)]) == "[I;0,2,0,0,0,40,1081507840,0]", tl_linear([(0, 0), (40, 360)])
print("线性关键帧编码自检通过:", tl_linear([(0, 0), (40, 360)]))

V = lt_np.Vol((48, 16, 48), (0, 0, 0), (0, 0, 0))     # 3×3 格 × 1 格高；O=(0,0,0) 合法（16 的倍数）
BL = V.M(F("#3a3a3a"))           # 叶片：FCB 深灰
AX = V.M(F("#40f0ff", "glow"))   # 轴心：FCB 青色发光

# 4 片叶：22px 长 × 4px 宽 × 2px 厚，从轴心 24 向外伸（±X / ±Z）
V.box(BL, 26, 0, 22, 48, 2, 26)          # +X
V.box(BL, 0, 0, 22, 22, 2, 26)           # -X
V.box(BL, 22, 0, 26, 26, 2, 48)          # +Z
V.box(BL, 22, 0, 0, 26, 2, 22)           # -Z
V.box(AX, 23, 0, 23, 25, 3, 25)          # 中心青色发光轴（2×3×2，往上多 1px）

st = ('{id:"advancedDoor",name:"%s",duration:%d,interpolation:0,activateParent:0b,'
      'disableRightClick:0b,axisCenter:[I;23,0,23,25,2,25,16],animation:{rotY:%s}}'
      % (NAME, DUR, tl_linear([(0, 0), (DUR, SPIN)])))
start = V.export("loop_fan.txt", "loop_fan", st)

print("结构: id=advancedDoor name=%s duration=%d interpolation=0(linear) rotY 0→%g" % (NAME, DUR, SPIN))
print("轴心(px) = (24, 1, 24)  → 轴心所在格 = 导入起点 + (1,0,1)")
print("扇叶占 3×3 格，以导入起点为左前下角；叶片任意一格的坐标都能被 /lt-open 命中")
print("---- 命令方块设置（测试用）----")
print("  方块A：循环型(Repeat) + 无条件 + 始终活动，命令：/lt-open <X> <Y> <Z> %s" % NAME)
print("          <X> <Y> <Z> = 任意一片叶片所在格，例：导入起点本身那一格")
print("          门在运动途中 isInMotion → canOpenDoor 否决重复触发；门一停，下一 tick 立刻重新起转 → 看起来是连续自转")
print("  方块B（可选，替代方块A）：任意 20~40 tick 时钟（漏斗钟/中继器环）驱动脉冲命令方块，命令同上")
print("  注意：/lt-open 需要 OP 权限 2（单人开作弊即可）；它用 player=null 触发，不受 disableRightClick 影响")
