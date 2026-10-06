# lt_verify_schem.py —— 独立校验 .schematic（**不与 lt_mass.py 共用任何代码**，重写一套极简 NBT 读取器）
# 用法: python lt_verify_schem.py mass_v0.schematic
# 检查: gzip 魔数 / 解压后前 12 字节 / 根标签名 / 根下全部键与类型 / 关键键的类型与长度 / 文件是否被完整消费
import gzip, struct, sys

TYPES = {0: "TAG_End", 1: "TAG_Byte", 2: "TAG_Short", 3: "TAG_Int", 4: "TAG_Long",
         5: "TAG_Float", 6: "TAG_Double", 7: "TAG_Byte_Array", 8: "TAG_String",
         9: "TAG_List", 10: "TAG_Compound", 11: "TAG_Int_Array"}


class R:
    def __init__(self, b): self.b, self.p = b, 0

    def u1(self): v = self.b[self.p]; self.p += 1; return v
    def i2(self): v = struct.unpack_from(">h", self.b, self.p)[0]; self.p += 2; return v
    def u2(self): v = struct.unpack_from(">H", self.b, self.p)[0]; self.p += 2; return v
    def i4(self): v = struct.unpack_from(">i", self.b, self.p)[0]; self.p += 4; return v
    def s(self): n = self.u2(); v = self.b[self.p:self.p + n].decode("utf-8", "replace"); self.p += n; return v

    def payload(self, t):
        if t == 1:
            v = self.u1(); return v - 256 if v > 127 else v
        if t == 2: return self.i2()
        if t == 3: return self.i4()
        if t == 4: v = struct.unpack_from(">q", self.b, self.p)[0]; self.p += 8; return v
        if t == 5: v = struct.unpack_from(">f", self.b, self.p)[0]; self.p += 4; return v
        if t == 6: v = struct.unpack_from(">d", self.b, self.p)[0]; self.p += 8; return v
        if t == 7:
            n = self.i4(); d = self.b[self.p:self.p + n]; self.p += n; return ("byte_array", n, d)
        if t == 8: return self.s()
        if t == 9:
            et = self.u1(); n = self.i4()
            return ("list", et, n, [self.payload(et) for _ in range(n)])
        if t == 10:
            out = []
            while True:
                tt = self.u1()
                if tt == 0: break
                nm = self.s(); out.append((nm, tt, self.payload(tt)))
            return out
        if t == 11:
            n = self.i4(); return ("int_array", n, [struct.unpack_from(">i", self.b, self.p + 4 * i)[0] for i in range(n)])
        raise ValueError("未知 tag id %d（偏移 %d）" % (t, self.p))


def brief(t, v):
    if t == 7: return "长度 %d 字节（%d..%d）" % (v[1], min(v[2]) if v[1] else 0, max(v[2]) if v[1] else 0)
    if t == 8: return repr(v)
    if t == 9: return "元素类型 %s × %d" % (TYPES.get(v[1], v[1]), v[2])
    if t == 10: return "%d 个键" % len(v)
    if t == 11: return "长度 %d" % v[1]
    return repr(v)


def main(path):
    raw = open(path, "rb").read()
    print("== %s  %d 字节 ==" % (path, len(raw)))
    magic = raw[:2]
    print("gzip 魔数 1f 8b（不是 zlib 裸流）: %s  [%s]" % (magic == b"\x1f\x8b", magic.hex(" ")))
    data = gzip.decompress(raw)                     # 若不是 gzip 流，这里会直接抛错
    first12 = data[:12]
    want = bytes([0x0A, 0x00, 0x09]) + b"Schematic"
    print("解压后 %d 字节；前 12 字节: %s" % (len(data), first12.hex(" ").upper()))
    print("  期望值              : %s   → %s" % (want.hex(" ").upper(), "一致 ✓" if first12 == want else "不一致 ✗"))

    r = R(data)
    tid = r.u1()
    assert tid == 10, "根不是 TAG_Compound（id=%d）" % tid
    name = r.s()
    print("根标签: type=0x%02X(%s) name=%r  → %s"
          % (tid, TYPES[tid], name, "✓ 正确" if name == "Schematic" else "✗ 必须叫 Schematic"))

    keys = []
    while True:
        t = r.u1()
        if t == 0: break
        nm = r.s(); v = r.payload(t)
        keys.append((nm, t, v))
    print("根下共 %d 个键（文件顺序）:" % len(keys))
    for nm, t, v in keys:
        print("   %-13s type=0x%02X %-15s %s" % (nm, t, TYPES[t], brief(t, v)))
    print("文件被完整消费: %s（读指针 %d / 总长 %d）" % (r.p == len(data), r.p, len(data)))

    d = {nm: (t, v) for nm, t, v in keys}
    exp = [("Width", 2), ("Height", 2), ("Length", 2), ("Materials", 8),
           ("Blocks", 7), ("Data", 7), ("Entities", 9), ("TileEntities", 9),
           ("WEOriginX", 3), ("WEOriginY", 3), ("WEOriginZ", 3),
           ("WEOffsetX", 3), ("WEOffsetY", 3), ("WEOffsetZ", 3)]
    bad = []
    for nm, t in exp:
        if nm not in d: bad.append("%s 缺失" % nm)
        elif d[nm][0] != t: bad.append("%s 类型应为 %s，实际 %s" % (nm, TYPES[t], TYPES[d[nm][0]]))
    if d.get("Materials", (0, ""))[1] != "Alpha": bad.append("Materials 必须是 \"Alpha\"")
    W, H, L = d["Width"][1], d["Height"][1], d["Length"][1]
    if d["Blocks"][1][1] != W * H * L: bad.append("Blocks 长度 %d ≠ %d×%d×%d" % (d["Blocks"][1][1], W, H, L))
    if d["Data"][1][1] != W * H * L: bad.append("Data 长度不符")
    if d["Entities"][1][2] != 0 or d["TileEntities"][1][2] != 0: bad.append("Entities/TileEntities 应为空")
    print("关键键校验: %s" % ("全部通过 ✓" if not bad else "✗ " + "；".join(bad)))
    print("摘要: W=%d H=%d L=%d；Origin=(%d,%d,%d) Offset=(%d,%d,%d)；非空气方块=%d"
          % (W, H, L, d["WEOriginX"][1], d["WEOriginY"][1], d["WEOriginZ"][1],
             d["WEOffsetX"][1], d["WEOffsetY"][1], d["WEOffsetZ"][1],
             sum(1 for x in d["Blocks"][1][2] if x)))
    return 0 if (not bad and r.p == len(data) and name == "Schematic" and first12 == want) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "mass_v0.schematic"))