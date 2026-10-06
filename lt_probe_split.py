# lt_probe_split.py —— 把 probe_187.txt 切片成单样品文件（probe_A..I、probe_F10）+ 生成 probe_187_safe.txt
# 只做"切片"，**不改任何样品内容**（崩溃元凶 probe_E 原样保留，用于逐个排查）
import io, os, re
import lt_root, lt_tree

SRC = "probe_187.txt"
NAMES = ["A", "B", "C", "D", "E", "F", "F10", "H", "I"]
LABELS = {"A": "官方 particle_emitter 原文", "B": "新键名 particle_emitter", "C": "扇叶 + stayAnimated",
          "D": "light level:15", "E": "门 state → 灯", "F": "自激灯 + 总开关",
          "F10": "F 的 10 盏自激灯", "H": "1/4 圆柱曲面", "I": "30° 斜板（11 分量盒）"}
DANGER = {"E"}          # 已确认崩溃：animation.rotY 首元素被平移到 224 → ValueTimeline.getType(224)


def split_children(src):
    ci = src.index("children:[") + len("children:[")
    kids, depth, start = [], 0, None
    for i in range(ci, len(src)):
        c = src[i]
        if c == "{":
            if depth == 0: start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                kids.append(src[start:i + 1]); start = None
    return kids


def boxes_of(text):
    """只取**盒子位置**的数组（bBox:[I;…] 或 boxes:[[I;…],…],tile:…）
    —— 不能盲扫所有 [I;…]，否则 axisCenter(7 个 int) / 时间轴(8 个 int) 会被当成盒子"""
    out = []
    for m in re.finditer(r'bBox:\[I;([-\d,]+)\]', text):
        out.append([int(x) for x in m.group(1).split(",")][:6])
    for m in re.finditer(r'boxes:\[(.*?)\](?=,tile:)', text, re.S):
        for mm in re.finditer(r'\[I;([-\d,]+)\]', m.group(1)):
            out.append([int(x) for x in mm.group(1).split(",")][:6])
    return out


def timelines_of(text):
    """非盒子的 int 数组（时间轴等）"""
    out = []
    for m in re.finditer(r"\[I;([-\d,]+)\]", text):
        a = [int(x) for x in m.group(1).split(",")]
        if len(a) not in (6, 7, 11):
            out.append(a)
    return out


src = io.open(SRC, encoding="utf-8").read()
kids = split_children(src)
root_tiles = src[len("tiles:"):src.index(',structure:{id:"fixed",name:"probe187"')]
plates = re.findall(r"\[I;[-\d,]+\]", root_tiles)
assert len(kids) == 9 and len(plates) == 9, (len(kids), len(plates))


def emit(fname, kept, label):
    tiles = '[{boxes:[%s],tile:{block:"minecraft:concrete:15"}}]' % ",".join(p for p, k, n in kept)
    kids_txt = ",".join(k for p, k, n in kept)
    b = boxes_of(tiles) + sum([boxes_of(k) for p, k, n in kept], [])
    lo = [min(x[i] for x in b) for i in range(3)]
    hi = [max(x[i + 3] for x in b) for i in range(3)]
    txt = ('{tiles:%s,structure:{id:"fixed",name:"%s"},children:[%s],min:[I;%d,%d,%d],'
           'size:[I;%d,%d,%d],count:%d}'
           % (tiles, label, kids_txt, *lo, *[hi[i] - lo[i] for i in range(3)], len(kept)))
    txt = lt_root.fix(txt, label, tag=fname)
    io.open(fname, "w", encoding="utf-8").write(txt)
    return lo, hi


print("%-22s %-24s %-11s %-9s %s" % ("文件", "样品", "导入起点", "尺寸(格)", "时间轴首元素检查"))
rows = []
for i, nm in enumerate(NAMES):
    fn = "probe_%s.txt" % nm
    lo, hi = emit(fn, [(plates[i], kids[i], "probe_" + nm)], "probe_" + nm)
    tl = timelines_of(kids[i])
    bad = [a for a in tl if a[0] < -1 or a[0] > 3]
    flag = ("★ 非法: %s → 会崩" % bad[0][0]) if bad else ("无时间轴" if not tl else "全部合法(0~3) ✓")
    print("%-22s %-24s (%2d,%2d,%2d) %d×%d×%d  %s" % (fn, LABELS[nm], lo[0] // 16, lo[1] // 16, lo[2] // 16,
          (hi[0] - lo[0]) // 16, (hi[1] - lo[1]) // 16, (hi[2] - lo[2]) // 16, flag))
    rows.append((fn, flag))

keep = [(plates[i], kids[i], NAMES[i]) for i in range(9) if NAMES[i] not in DANGER]
lo, hi = emit("probe_187_safe.txt", keep, "probe187_safe")
print("\nprobe_187_safe.txt: 样品 %s（去掉 %s），导入起点 (%d,%d,%d)，尺寸 %.2f×%.2f×%.2f 格"
      % (",".join(NAMES[i] for i in range(9) if NAMES[i] not in DANGER), ",".join(sorted(DANGER)),
         lo[0] // 16, lo[1] // 16, lo[2] // 16,
         (hi[0] - lo[0]) / 16, (hi[1] - lo[1]) / 16, (hi[2] - lo[2]) / 16))
print("单样品里仍含非法时间轴的：%s" % ([r[0] for r in rows if "非法" in r[1]] or "无"))