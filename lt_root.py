# lt_root.py —— 根层文本的统一出口 + 不变量守卫（依据交接文档 §3.9）
#
# 规则：根有 children 就必须有 structure。
#   根无 structure ⇒ LittlePreviews.getStructure() 返回 null ⇒ placedStructure() 不执行
#   ⇒ 整棵树的 children/parent 一个都不连（每个结构照旧落地，但彼此没有层级 → 按了没反应）。
# 所以：任何脚本拼根层文本时，只要根有 children 却没有 structure，
#   就在 tiles:[...] 的闭合 ] 后面自动插入 structure:{id:"fixed",name:"<名字>"}，
#   并立即断言；断言不通过就报错退出（exit 1）。
#
# 脚本内用法：
#   import lt_root
#   ROOT_NAME = "测试台"
#   s = lt_root.fix(s, ROOT_NAME, tag="mech_test.txt")
#
# 命令行用法：
#   python lt_root.py verify <file.txt> [...]                  校验不变量并打印根层
#   python lt_root.py diff <before.txt> <after.txt> <name>     只允许"插入 structure 段"的逐字节比对
#   python lt_root.py selftest                                 纯字符串自测（不碰磁盘）
import io, os, sys

CH = "children:["          # 根层 children 的起始标记
CLOSE_ERR = "tiles 的 ] 不配对"


def tiles_end(t):
    """返回根 tiles:[...] 闭合 ] 之后的下标（括号/引号感知）"""
    i = t.index("[")
    depth, instr = 0, False
    while i < len(t):
        c = t[i]
        if instr:
            if c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError(CLOSE_ERR)


def first_children(t):
    return t.find(CH)


def has_root_struct(t):
    """根自己的 structure 必须出现在第一个 children:[ 之前；否则那是子节点的 structure"""
    i = first_children(t)
    if i < 0:
        j = t.find(",min:")
        i = j if j >= 0 else len(t)
    return t.rfind("structure:{", 0, i) >= 0


def seg(name, sid="fixed"):
    return ',structure:{id:"%s",name:"%s"}' % (sid, name)


def root_layer(t):
    """根层文本：从开头到第一个 children:[ 为止"""
    i = first_children(t)
    return t[:i + len(CH)] if i >= 0 else t


def elide(t):
    """把 tiles:[...] 的内容换成 [...]，便于人眼看根层"""
    k = tiles_end(t)
    return "{tiles:[...]" + t[k:]


def assert_root(t, tag="根层"):
    i = first_children(t)
    if i < 0:
        return t
    assert t.rfind("structure:{", 0, i) >= 0, (
        "%s: 根有 children 却没有 structure → LittlePreviews.getStructure() 返回 null，"
        "整棵树不会建立 children/parent 连接（§3.9）。修法：在 tiles:[...] 后接 "
        'structure:{id:"fixed",name:"<名字>"},' % tag)
    return t


def fix(t, name, sid="fixed", autofix=True, enforce=True, tag=None, exempt_reason=None):
    """根有 children 却无 structure 时自动插入；并按需断言。assert 失败直接抛错（脚本非 0 退出）"""
    tag = tag or name
    if first_children(t) >= 0 and not has_root_struct(t):
        if autofix:
            k = tiles_end(t)
            t = t[:k] + seg(name, sid) + t[k:]
            print("[根层] %s 自动插入 structure:{id:%s,name:%s}" % (tag, sid, name))
        elif exempt_reason:
            print("[豁免] %s 故意保持【根无 structure】: %s" % (tag, exempt_reason))
    if enforce:
        assert_root(t, tag)
    return t


def selftest():
    ok = 'fixed'
    a = '{tiles:[{bBox:[I;0,0,0,1,1,1],tile:{block:"x:"}}],children:[{tiles:[],structure:{id:"fixed"}}],min:[I;0,0,0],size:[I;1,1,1],count:1}'
    r = fix(a, "测试台", tag="自测A")
    assert r == a[:tiles_end(a)] + seg("测试台") + a[tiles_end(a):]
    assert r.startswith(ok and '{tiles:[{bBox:[I;0,0,0,1,1,1],tile:{block:"x:"}}],structure:{id:"fixed",name:"测试台"},children:[')
    assert has_root_struct(r) and first_children(r) > r.find("structure:{")
    # 已带根 structure 的不重复插
    assert fix(r, "测试台", tag="自测B") == r
    # 无 children 的不动
    b = '{tiles:[],min:[I;0,0,0],size:[I;1,1,1],count:0}'
    assert fix(b, "空", tag="自测C") == b
    # 缺 structure 时断言必须炸
    try:
        fix(a, "x", autofix=False, enforce=True, tag="自测D")
        raise SystemExit("自测D 未按预期报错")
    except AssertionError as ex:
        assert "§3.9" in str(ex)
    # 子节点有 structure 而根没有 → 仍应判为"根无 structure"（假阳性回归测试）
    c = '{tiles:[],children:[{tiles:[],structure:{id:"fixed"}}],min:[I;0,0,0],size:[I;1,1,1],count:0}'
    assert not has_root_struct(c)
    # 三个真实脚本的根层形状回归：lt_nexus(children 在 min 前) / lt_cyber(children 在最后) / lt_ramen(无 children)
    nex = ('{tiles:[{bBox:[I;0,0,0,1,1,1],tile:{block:"a"}}],children:[{tiles:[],structure:{id:"chair"}}],'
           'min:[I;0,0,0],size:[I;1,1,1],count:1}')
    rn = fix(nex, "nexus_lab", tag="形状:nexus")
    assert rn == nex[:tiles_end(nex)] + seg("nexus_lab") + nex[tiles_end(nex):]
    assert rn.index('structure:{id:"fixed"') < rn.index("children:[")
    cyb = ('{tiles:[{bBox:[I;0,0,0,1,1,1],tile:{block:"a"}}],min:[I;0,0,0],size:[I;1,1,1],count:1,'
           'children:[{tiles:[],structure:{id:"chair"}}]}')
    rc = fix(cyb, "nexus_lab", tag="形状:cyber")
    assert rc.index(',structure:{id:"fixed"') == tiles_end(cyb)     # 紧跟 tiles 的 ]
    assert rc.index('structure:{id:"fixed"') < rc.index("children:[")
    assert rc.index("min:[I;") > tiles_end(cyb)
    ram = '{tiles:[{bBox:[I;0,0,0,1,1,1],tile:{block:"a"}}],min:[I;0,0,0],size:[I;1,1,1],count:1}'
    assert fix(ram, "ramen_shop", tag="形状:ramen") == ram
    print("selftest 全部通过")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "verify":
        bad = 0
        for f in sys.argv[2:]:
            t = io.open(f, encoding="utf-8").read()
            try:
                assert_root(t, os.path.basename(f))
                v = "通过"
            except AssertionError as ex:
                v = "失败: %s" % ex
                bad += 1
            i = first_children(t)
            print("%s: 有children=%s 根structure=%s 断言=%s" %
                  (os.path.basename(f), i >= 0, has_root_struct(t), v))
            if i >= 0:
                rl = root_layer(t)
                print("   根层(到第一个 children:[) = %s   [%d 字节]" % (elide(rl), len(rl.encode("utf-8"))))
        sys.exit(1 if bad else 0)
    elif cmd == "diff":
        b = io.open(sys.argv[2], encoding="utf-8").read()
        a = io.open(sys.argv[3], encoding="utf-8").read()
        nm = sys.argv[4]
        k = tiles_end(b)                      # 插入点 = 改前 tiles 闭合 ] 之后
        exp = b[:k] + seg(nm) + b[k:]
        target = "{tiles:[...]" + seg(nm) + "," + CH   # 目标文本：tiles 省略 + 插入段 + 原有 ,children:[
        la, lb = root_layer(a), root_layer(b)
        print("唯一允许的差值段: %s" % seg(nm))
        print("插入点偏移 %d，改前该处起始文本 = %r" % (k, b[k:k + len(CH)]))
        print("改后文本 == 改前文本 + 插入段 (逐字节): %s" % (a == exp))
        if a != exp:
            for x in range(min(len(a), len(exp))):
                if a[x] != exp[x]:
                    print("   首个不同处: 偏移 %d 改后=%r 期望=%r" % (x, a[x], exp[x]))
                    break
        print("根层(改后, 到第一个 children:[) = %s   [%d 字节]" % (elide(la), len(la.encode("utf-8"))))
        print("根层(改前, 到第一个 children:[) = %s   [%d 字节]" % (elide(lb), len(lb.encode("utf-8"))))
        print("根层 == 目标文本 %s : %s" % (target, elide(la) == target))
        print("tiles:[...] 段逐字节相同: %s" % (a[:tiles_end(a)] == b[:tiles_end(b)]))
        print("第一个 children:[ 之后逐字节相同: %s" % (a[a.find(CH):] == b[b.find(CH):]))
        print("整串字节数: 改前 %d → 改后 %d (%+d)" %
              (len(b.encode("utf-8")), len(a.encode("utf-8")),
               len(a.encode("utf-8")) - len(b.encode("utf-8"))))
    elif cmd == "selftest":
        selftest()
    else:
        print(__doc__ or "usage: python lt_root.py verify|diff|selftest ...")