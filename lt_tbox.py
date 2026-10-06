# lt_tbox.py —— 187 可变形盒 LittleTransformableBox 的编码/解码（依据 lt_src_187 逐行反推）
#
# 数组格式（`[I;…]`，长度 ≥ 7）：[x1,y1,z1,x2,y2,z2, indicator, word1, word2, …]
#   · indicator（有符号 int，**负数** ⇒ LittleBox.createBox(:1127-1129) 走 `new LittleTransformableBox(array)`）
#       bit31      = 可变形标记（写出时 `Integer.MIN_VALUE | 0xBF000000 & …`，见 :1681-1683）
#       bits24-29  = 六个面的 flipped 标志（:228-244，24+facing.ordinal()；facing 序=DOWN,UP,NORTH,SOUTH,WEST,EAST）
#       bits0-23   = “哪个角的哪个轴存了偏移”掩码：bit(i*3+a)，i=角序 0..7、a=轴 0..2（:274-285 的读取顺序）
#   · word1… = 连续 16-bit 有符号 short 打包：第 k 个偏移 → word[k/2 + 1]，k 偶→高 16 位、k 奇→低 16 位（:251-263）
#   · 偏移含义：该角的对应轴坐标 = 基础角坐标 + 偏移（:860 `getData(activeBits) + this.get(corner.x)`）
# 角序（cc_src BoxUtils.BoxCorner:221-229）：0 EUN 1 EUS 2 EDN 3 EDS 4 WUN 5 WUS 6 WDN 7 WDS
import sys

CORNERS = ["EUN", "EUS", "EDN", "EDS", "WUN", "WUS", "WDN", "WDS"]
FACINGS = ["DOWN", "UP", "NORTH", "SOUTH", "WEST", "EAST"]      # EnumFacing.ordinal()
MARKER = 0x80000000


def _s32(x):
    return x - (1 << 32) if x >= (1 << 31) else x


def _s16(x):
    return x - (1 << 16) if x >= (1 << 15) else x


def decode(arr):
    """arr = 完整盒子数组（≥7 个 int）→ 结构化描述"""
    coords = [int(x) for x in arr[:6]]
    data = [int(x) & 0xFFFFFFFF for x in arr[6:]]
    ind = data[0]
    mask = ind & 0xFFFFFF
    slots = [(i // 3, i % 3) for i in range(24) if (mask >> i) & 1]

    def slot(k):
        w = data[k // 2 + 1]
        v = ((w >> 16) & 0xFFFF) if k % 2 == 0 else (w & 0xFFFF)
        return _s16(v)

    offs = []
    for k, (c, a) in enumerate(slots):
        offs.append(dict(corner=CORNERS[c], cornerIndex=c, axis="XYZ"[a], axisIndex=a,
                         offset=slot(k), slotIndex=k))
    return dict(coords=coords, indicator=_s32(ind), marker=bool(ind >> 31),
                flips=[FACINGS[i] for i in range(6) if (ind >> (24 + i)) & 1],
                mask=mask, offsets=offs, words=len(data) - 1,
                raw=data)


def encode(coords, offsets, flips=()):
    """offsets: {"EUN:X": 3, …} 或 [("EUN","X",3), …]；flips: ["UP", …] → 数组（list[int]，已带符号）"""
    if isinstance(offsets, dict):
        items = [(k.split(":")[0], k.split(":")[1], v) for k, v in offsets.items()]
    else:
        items = []
        for o in offsets:
            if isinstance(o, dict):
                items.append((o["corner"], o["axis"], o["offset"]))
            else:
                items.append(tuple(o))
    # ★ 同一 (角,轴) 只保留最后一个值（去重），否则掩码位与槽位会错配
    dedup = {}
    for cname, ax, v in items:
        dedup[(cname, ax)] = v
    items = sorted([(c, a, v) for (c, a), v in dedup.items()],
                   key=lambda t: CORNERS.index(t[0]) * 3 + "XYZ".index(t[1]))
    mask, slots = 0, []
    for cname, ax, v in items:
        if v == 0: continue
        i, a = CORNERS.index(cname), "XYZ".index(ax)
        mask |= 1 << (i * 3 + a); slots.append(_s16(v) & 0xFFFF)
    ind = MARKER | mask
    for f in flips:
        ind |= 1 << (24 + FACINGS.index(f))
    nwords = max(1, (len(slots) + 1) // 2)
    words = [0] * nwords
    for k, v in enumerate(slots):
        words[k // 2] |= (v << 16) if k % 2 == 0 else v
    return [int(x) for x in coords] + [_s32(ind)] + [_s32(w) for w in words]


def show(arr, tag=""):
    d = decode(arr)
    print("== %s  %s" % (tag, arr))
    print("   坐标 6 分量 = %s" % (d["coords"],))
    print("   indicator = %d (0x%08X)：可变形标记=%s  面翻转=%s"
          % (d["indicator"], d["raw"][0], d["marker"], d["flips"] or "无"))
    print("   掩码 bits0-23 = 0b%s（%d 个偏移槽）  数据字 %d 个"
          % (bin(d["mask"])[2:].zfill(24), len(d["offsets"]), d["words"]))
    for o in d["offsets"]:
        print("     槽%d：角 %s(%d) 的 %s 轴偏移 = %+d px"
              % (o["slotIndex"], o["corner"], o["cornerIndex"], o["axis"], o["offset"]))
    return d


def parse_text(t):
    """从 '[I;1,2,3,…]' 解析成 int 列表"""
    return [int(x) for x in t.strip().lstrip("[I;").rstrip("]").split(",")]


if __name__ == "__main__":
    # K 样本（用户在游戏内导出的原生斜面）
    K = [2, 0, 0, 14, 7, 11, -2147418096, -393223]
    d = show(K, "K 原生斜面样本")
    back = encode(d["coords"], [dict(corner=o["corner"], axis=o["axis"], offset=o["offset"])
                                for o in d["offsets"]], d["flips"])
    print("   解码→再编码 = %s" % back)
    print("   逐位一致（与 K 完全相同）= %s" % (back == K))
    # 手算校验
    print("\n   手算校验：indicator=0x80010010 → bit4=(角1, Y)、bit16=(角5, Y) 两个槽；")
    print("             word=0xFFF9FFF9 → 高16=0xFFF9=-7、低16=0xFFF9=-7 ⇒ 角1(EUS)Y 与 角5(WUS)Y 各 −7px")
    if len(sys.argv) > 1 and sys.argv[1] == "decode":
        show(parse_text(sys.argv[2]), sys.argv[2])