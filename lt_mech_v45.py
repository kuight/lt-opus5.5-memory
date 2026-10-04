# lt_mech_v45.py —— 由 lt_mech_v.py 的成品生成 v4 / v5 两个对照样品
#
# 背景（本轮变化）：加了 §3.9 守卫（lt_root.py）之后，所有生成器输出的根都自带 structure，
#   于是"根无结构"不再是正常产物，只能作为【故意违规的负对照】显式豁免地造出来：
#     v4 = 负对照【根无结构】：取 mech_v2 → 摘掉根 structure（明确豁免）→ 把 doorActivator 段换成
#          advancedDoor 事件门 → 再把最后一处 disableRightClick:0b 改成 1b（门禁落在内层卷帘门上）
#          预期：事件里 children.get(0) 时 children 为空 → IndexOutOfBounds，日志可见
#     v5 = 【根带结构】：现在与 mech_v3 的输出逐字节相同（守卫自动插入的那一份）
#          预期：连接建立，按按钮真的卷帘
import io, os, re, lt_root

D = os.path.dirname(os.path.abspath(__file__))
V2 = "mech_v2_门可右键_有按钮.txt"
V3 = "mech_v3_原版_门禁右键_有按钮.txt"
V4 = "mech_v4_按钮门触发子门_根无结构.txt"
V5 = "mech_v5_根带结构_门禁右键_有按钮.txt"

ACT = 'id:"doorActivator",name:"卷帘按钮",activate:[I;0],activateParent:0b,disableRightClick:0b'
DOOR = ('id:"advancedDoor",name:"按钮门",duration:2,interpolation:3,activateParent:0b,disableRightClick:0b,'
        'axisCenter:[I;20,16,25,21,17,26,16],events:[{id:"child",tick:0,activated:0b,childId:0}]')
DRC0 = 'disableRightClick:0b'
DRC1 = 'disableRightClick:1b'


def rd(n):
    return io.open(os.path.join(D, n), encoding="utf-8").read()


def wr(n, s):
    io.open(os.path.join(D, n), "w", encoding="utf-8").write(s)


def occ(s, p):
    return [m.start() for m in re.finditer(re.escape(p), s)]


old4 = rd(V4) if os.path.exists(os.path.join(D, V4)) else None
old5 = rd(V5) if os.path.exists(os.path.join(D, V5)) else None

s2, s3 = rd(V2), rd(V3)
lt_root.assert_root(s2, V2)          # 守卫产物：v2/v3 必须已带根 structure
lt_root.assert_root(s3, V3)
seg2 = lt_root.seg("测试台")
assert seg2 in s2 and seg2 in s3, "v2/v3 里没有守卫插入的根 structure 段: %s" % seg2

# ---------- v4：故意违规的负对照 ----------
s4 = s2.replace(seg2, "", 1)         # 摘掉根 structure
s4 = lt_root.fix(s4, "测试台", autofix=False, enforce=False, tag=V4,
                 exempt_reason="负对照：故意造【根无结构】，用于验证 §3.9 的失败路径"
                               "（事件触发时 children 为空 → IndexOutOfBounds）")
assert not lt_root.has_root_struct(s4), "v4 应当是根无结构"
assert s4.count(ACT) == 1, "ACT 段出现 %d 次" % s4.count(ACT)
before = occ(s4, DRC0)
s4 = s4.replace(ACT, DOOR)
after = occ(s4, DRC0)
assert len(after) >= 2
last = after[-1]
s4 = s4[:last] + DRC1 + s4[last + len(DRC0):]
p_btn, p_shut, p_lock = s4.find('name:"按钮门"'), s4.find('name:"卷帘门"'), s4.find(DRC1)
assert p_btn < p_shut < p_lock, "1b 没落在内层卷帘门上"
# 可逆校验：反做回去必须逐字节还原（摘掉守卫段后的）v2
back = s4.replace(DRC1, DRC0, 1).replace(DOOR, ACT)
print("v4: 摘根 structure 1 处; ACT->DOOR 1 处; 最后一处 %s@%d -> 1b (改前 0b 位置 %s)" % (DRC0, last, before))
print("v4: 根structure=%s children数=%d; 反做还原(含守卫段)校验=%s"
      % (lt_root.has_root_struct(s4), len(occ(s4, "children:[")), back == s2.replace(seg2, "", 1)))
assert back == s2.replace(seg2, "", 1)
wr(V4, s4)

# ---------- v5：根带结构 ----------
s5 = s3
assert lt_root.has_root_struct(s5)
wr(V5, s5)
print("v5: 由根带结构的 mech_v3 逐字节复制; 与 mech_v3 相同=%s" % (s5 == s3))

print("v4 与上一轮产物逐字节相同:", old4 == s4 if old4 is not None else "（上一轮无产物）")
print("v5 与上一轮产物逐字节相同:", old5 == s5 if old5 is not None else "（上一轮无产物）")
for n, t in ((V4, s4), (V5, s5)):
    rl = lt_root.root_layer(t)
    print("%s: %d 字节; 根层 = %s" % (n, len(t.encode("utf-8")), lt_root.elide(rl)))
print("产物:", os.path.join(D, V4))
print("产物:", os.path.join(D, V5))