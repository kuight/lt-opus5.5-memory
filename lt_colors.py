import csv
PREFIX = "flatcoloredblocks:"   # 先按下面的自检核对，不对就改
KIND_PRE = {"solid": "flatcoloredblock",
            "trans": "flatcoloredblock_transparent0_",
            "glow":  "flatcoloredblock_glowing0_"}   # 发光名需样品确认
_P = {}

def _load(path="flatcoloredblocks.csv"):
    with open(path, encoding="gbk", errors="ignore", newline="") as f:
        rows = list(csv.reader(f))
    for r in rows[1:]:
        if len(r) < 11 or not r[0].strip().isdigit():
            continue
        n, h = int(r[0]), r[2].strip().lstrip("#")
        op, lv = int(r[9]), int(r[10])
        kind = "glow" if lv > 0 else ("trans" if op < 100 else "solid")
        _P.setdefault(kind, []).append(
            (n, int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))

def fc(hexcolor, kind="solid"):
    """输入 '#RRGGBB'，返回最接近的平滑色块方块名"""
    if not _P:
        _load()
    h = hexcolor.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    n = min(_P[kind], key=lambda c: (c[1]-r)**2 + (c[2]-g)**2 + (c[3]-b)**2)[0]
    return f"{PREFIX}{KIND_PRE[kind]}{n // 16}:{n % 16}"

if __name__ == "__main__":
    _load()
    print({k: len(v) for k, v in _P.items()})
    print("自检 trans #7f8d70 ->", fc("#7f8d70", "trans"))
    print("白 ->", fc("#ffffff"), " 黑 ->", fc("#333333"))
    print("发光青 ->", fc("#00ffff", "glow"))