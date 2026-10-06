# lt_tree.py —— LittleTiles 导入文本的树/语法校验器（递归解析 tiles / structure / children）
# 依据交接文档 §3.1~§3.6、§3.13 的实证规则：
#   tiles 条目形状 / 坐标 6 分量且上界排他 / 根 count = 根盒子数 / min,size = 【全树】并集包围盒
#   structure id 必须在注册表内 / advancedDoor 写了 offX|offY|offZ 就必须要同一容器里有 offGrid（§3.6 陷阱）
#   子节点不得带根专属键（min/size/count）
# 用法: python lt_tree.py <文件.txt> [文件2.txt ...]
import re, sys, io, os

REG = {"fixed", "ladder", "bed", "chair", "storage", "noclip", "door", "slidingDoor",
       "advancedDoor", "doorActivator",
       # ↓ 仅 1.5.87 有（pre199 无）：见 NOTES 1.5.87 基线核对
       "light", "message", "item_holder", "particle_emitter", "blankomatic",
       "single_cable1", "single_cable4", "single_cable16",
       "single_input1", "single_input4", "single_input16",
       "single_output1", "single_output4", "single_output16",
       "signal_display_16", "structure_builder"}
ROOT_KEYS = ("tiles", "structure", "children", "min", "size", "count")
NODE_KEYS = ("tiles", "structure", "children")


def match(s, i):
    op = s[i]
    if op not in "{[":
        raise ValueError("期望 { 或 [，实际是 %r（偏移 %d，附近文本: %r）" % (op, i, s[max(0, i - 40):i + 40]))
    cl = {"{": "}", "[": "]"}[op]
    depth, instr, j = 0, False, i
    while j < len(s):
        c = s[j]
        if instr:
            if c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == op:
            depth += 1
        elif c == cl:
            depth -= 1
            if depth == 0:
                return s[i:j + 1], j + 1
        j += 1
    raise ValueError("括号不配对 @%d" % i)


def split_top(t):
    out, depth, instr, cur = [], 0, False, []
    for c in t:
        if instr:
            cur.append(c)
            if c == '"':
                instr = False
            continue
        if c == '"':
            instr = True
        elif c in "{[(":
            depth += 1
        elif c in "}])":
            depth -= 1
        if c == "," and depth == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        out.append("".join(cur))
    return out


def parse_obj(s, i):
    body, ni = match(s, i)
    d = {}
    for p in split_top(body[1:-1]):
        k, _, v = p.partition(":")
        d[k.strip()] = v.strip()
    return d, ni


def unq(v):
    return v[1:-1] if v and v[0] == '"' else v


def ivec(v):
    return [int(x) for x in re.findall(r"-?\d+", v[3:-1])]


def entries(tiles_text):
    out = []
    for e in split_top(match(tiles_text, 0)[0][1:-1]):
        d, _ = parse_obj(e, 0)
        if "bBox" in d:
            rects = [ivec(d["bBox"])]
        elif "boxes" in d:
            rects = [[int(x) for x in m.split(",")]
                     for m in re.findall(r"\[I;([-\d,]+)\]", match(d["boxes"], 0)[0])]
        else:
            rects = []
        blk = re.search(r'block:"([^"]+)"', d.get("tile", ""))
        out.append((unq(blk.group(1)) if blk else "?", rects, sorted(d.keys())))
    return out


def walk(s, i, depth, path, rep, st):
    d, _ = parse_obj(s, i)
    allowed = ROOT_KEYS if depth == 0 else NODE_KEYS
    extra = [k for k in d if k not in allowed]
    if extra:
        st["issues"].append("%s 出现不该有的键 %s" % (path, extra))
    if depth == 0:
        st["min"], st["size"], st["count"] = d.get("min"), d.get("size"), d.get("count")

    sid = sname = "-"
    if "structure" in d:
        sd, _ = parse_obj(d["structure"], 0)
        sid, sname = unq(sd.get("id")), unq(sd.get("name"))
        if sid not in REG:
            st["issues"].append("%s structure id 不在注册表: %s" % (path, sid))
        if sid == "doorActivator" and "activate" not in sd:
            st["issues"].append("%s doorActivator 缺 activate(§3.13)" % path)
        if sid == "advancedDoor":
            # §3.6 陷阱：offX/Y/Z 与 offGrid 必须在【同一容器】里（新格式在 animation 块内）
            box, tag = sd, "顶层"
            if "animation" in sd:
                box, tag = parse_obj(sd["animation"], 0)[0], "animation"
            off = [k for k in ("offX", "offY", "offZ") if k in box]
            rot = [k for k in ("rotX", "rotY", "rotZ") if k in box]
            grid = "offGrid" in box
            if off and not grid:
                st["issues"].append("%s advancedDoor 有 %s 但同容器缺 offGrid → 静默忽略(§3.6)" % (path, off))
            rep.append("%sadvancedDoor 帧: 容器=%s off=%s rot=%s offGrid=%s 总时长字段=%s"
                       % ("  " * depth, tag, off, rot, grid, "duration" in sd))
        if sid == "fixed" and "name" not in sd:
            st["issues"].append("%s fixed 无 name（命名可以省略，仅提示）" % path)

    els = entries(d["tiles"]) if "tiles" in d else []
    if "tiles" not in d:
        st["issues"].append("%s 缺 tiles(§3.2)" % path)
    nbox = sum(len(rs) for _, rs, _ in els)
    if depth == 0:
        st["rootboxes"] = nbox
    for blk, rs, keys in els:
        for r in rs:
            st["acc"].append(r[:6])
            if len(r) == 6:
                if not (r[0] < r[3] and r[1] < r[4] and r[2] < r[5]):
                    st["issues"].append("%s 盒上界非排他: %s" % (path, r))
            elif len(r) >= 7 and r[6] < 0:
                # 187 **原生可变形盒**（8 分量起；见 lt_tbox.py 的位级解码）
                try:
                    import lt_tbox
                    dd = lt_tbox.decode(r)
                    if not dd["marker"]:
                        st["issues"].append("%s 可变形盒缺 bit31 标记: %s" % (path, r))
                    for o in dd["offsets"]:
                        if abs(o["offset"]) > 512:
                            st["issues"].append("%s 可变形盒角偏移异常(>512px): %s" % (path, o))
                    rep.append("%s可变形盒(原生 8+ 分量): 6坐标%s；%d 个角偏移 [%s]；面翻转=%s"
                               % ("  " * depth, r[:6], len(dd["offsets"]),
                                  ", ".join("%s.%s%+d" % (o["corner"], o["axis"], o["offset"]) for o in dd["offsets"]),
                                  dd["flips"] or "无"))
                except Exception as ex:
                    st["issues"].append("%s 可变形盒解析失败: %s" % (path, ex))
            elif len(r) in (7, 11):
                rep.append("%s★警告：%d 分量“手写切片盒”（旧 LittleSlice 编码，非原生可变形盒）6坐标%s slice=%d 附加=%s"
                           % ("  " * depth, len(r), r[:6], r[6], r[7:]))
                st["warns"].append("%s %d 分量手写切片盒（旧编码，建议改用 8 分量原生盒）: %s" % (path, len(r), r))
            else:
                st["issues"].append("%s 盒分量数 %d 非法: %s" % (path, len(r), r))
            if not blk or blk == "?":
                st["issues"].append("%s 有条目缺 tile.block" % path)

    # ===== 守卫①：时间轴数组形态 / 守卫②：axisCenter 落点（2026-10-06 新增；依据 "Invalid id 224" 崩溃）=====
    # 教训：生成器**禁止用正则盲改 int 数组**。旧版 trans() 把 animation.rotY 也当坐标平移 →
    #      首元素变成 224 → 游戏里 ValueTimeline.getType(224) 抛 RuntimeException: Invalid id 224（放置时崩）。
    if "structure" in d:
        sdg, _ = parse_obj(d["structure"], 0)
        scopes = [("顶层", sdg)]
        if "animation" in sdg:
            scopes.append(("animation", parse_obj(sdg["animation"], 0)[0]))
        for scope_name, scope in scopes:
            for key in ("rotX", "rotY", "rotZ", "offX", "offY", "offZ"):
                if key not in scope:
                    continue
                arr = ivec(scope[key])
                where = "%s.%s" % (scope_name, key)
                if len(arr) < 2:
                    st["issues"].append("%s 时间轴 %s 太短: %s" % (path, where, arr))
                    continue
                t, cnt = arr[0], arr[1]
                base, add = 2 + 3 * cnt, (3 if arr[0] == 3 else 0)
                if t not in (0, 1, 2, 3):
                    st["issues"].append(
                        "%s 时间轴 %s 首元素=%d 非法（必须 0~3；游戏里 ValueTimeline.getType 会抛 "
                        "RuntimeException: Invalid id %d）: %s" % (path, where, t, t, arr))
                if len(arr) not in (base, base + add):
                    st["issues"].append(
                        "%s 时间轴 %s 长度=%d 与 count=%d 不符（应为 %d%s）: %s"
                        % (path, where, len(arr), cnt, base,
                           ("或 %d（hermite 附加 3）" % (base + add)) if add else "", arr))
                rep.append("%s时间轴 %s = %s（type=%d count=%d）" % ("  " * depth, where, arr, t, cnt))
        if "axisCenter" in sdg:
            ac = ivec(sdg["axisCenter"])
            rep.append("%saxisCenter = %s" % ("  " * depth, ac))
            own = [r[:6] for _, rs, _ in els for r in rs]
            if len(ac) >= 6 and own:
                albo = [min(r[k] for r in own) for k in range(3)]
                ahib = [max(r[k + 3] for r in own) for k in range(3)]
                for k, ax in enumerate("XYZ"):
                    a1, a2 = sorted((ac[k], ac[k + 3]))
                    if a1 < albo[k] or a2 > ahib[k]:
                        st["issues"].append("%s axisCenter 的 %s 段 [%d,%d] 超出本节点盒子范围 [%d,%d]"
                                            % (path, ax, a1, a2, albo[k], ahib[k]))
            elif len(ac) >= 6:
                rep.append("%s[提示] 有 axisCenter 但本节点无自己的盒子，跳过落点校验" % ("  " * depth))

    kids = split_top(match(d["children"], 0)[0][1:-1]) if "children" in d else []
    rep.append("%s[%s] id=%s name=%s 条目=%d 盒=%d 子=%d"
               % ("  " * depth, path, sid, sname, len(els), nbox, len(kids)))
    for k, c in enumerate(kids):
        walk(c, 0, depth + 1, "%s.%d" % (path, k), rep, st)


def report(fn):
    s = io.open(fn, encoding="utf-8").read()
    rep, st = [], {"acc": [], "issues": [], "warns": []}
    try:
        walk(s, 0, 0, "根", rep, st)
    except Exception as ex:
        print("!! %s 解析失败: %s" % (os.path.basename(fn), ex))
        return 1
    acc = st["acc"]
    lo = [min(r[k] for r in acc) for k in range(3)]
    hi = [max(r[k + 3] for r in acc) for k in range(3)]
    if st["count"] is not None and int(st["count"]) != st["rootboxes"]:
        st["issues"].append("根 count=%s 但根盒子数=%d(§3.1: count=盒子个数)" % (st["count"], st["rootboxes"]))
    if st["min"] is not None and ivec(st["min"]) != lo:
        st["issues"].append("根 min=%s 与全树并集 %s 不符" % (ivec(st["min"]), lo))
    if st["size"] is not None and ivec(st["size"]) != [hi[k] - lo[k] for k in range(3)]:
        st["issues"].append("根 size=%s 与全树并集 %s 不符" % (ivec(st["size"]), [hi[k] - lo[k] for k in range(3)]))
    print("== %s  (%d 字节, 全树 %d 盒, 并集 min=%s size=%s, count=%s)"
          % (os.path.basename(fn), len(s.encode("utf-8")), len(acc), lo,
             [hi[k] - lo[k] for k in range(3)], st["count"]))
    if st["issues"]:
        for x in st["issues"]:
            print("   [问题] " + x)
    else:
        print("   [问题] 无")
    for x in st.get("warns", []):
        print("   [警告] " + x)
    for line in rep:
        print("   " + line)
    return 1 if st["issues"] else 0


if __name__ == "__main__":
    n = 0
    for f in sys.argv[1:]:
        n += report(f)
    sys.exit(1 if n else 0)