# HANDOFF —— LittleTiles 1.12.2 天梯城项目（给下一个无记忆的会话）

> 配套：`NOTES.md`（环境/已验证结论/审美偏好/进度/测试记录/1.5.87 基线核对）、`PLAN.md`（天梯城总图 v2，旧版 `PLAN_v1_old.md`）、`DESIGN.md`（设计稿 v2 + 规则 R1~R8）、`FILES.md`（脚本清单）。
> 工作目录 `E:\work\建筑\`（**脚本必须在此目录运行**：`lt_colors.py` 用相对路径读 `flatcoloredblocks.csv`）；记忆仓库 `E:\work\lt-memory\`（远端 `kuight/lt-opus5.5-memory`）。

---

## 0. 会话开场（必做）

1. 先写 `probe.txt` 并用 `dir` 确认；**不要用命令把大段文本打到终端**，用 `read`(offset/limit) / `grep` / `glob` 工具；凡是落盘立刻读回验证。
2. **三条规矩（用户 2026-10-05 明确要求）**
   - (a) **设计任何建筑/功能之前，必须先查资料对照设计目标**（源码 `lt_src_187`、官方 jar 内资源、NOTES/HANDOFF/DESIGN 的既有结论）。**联网搜索 401 期间，只抓用户指定的 URL**，不要自己乱逛。
   - (b) **测试要压缩到 2~3 张截图**：测试清单必须写明拍摄角度/站位，让用户照着拍。
   - (c) **每轮结束更新 NOTES/HANDOFF 并推送，回报完整 SHA**；push 失败**原样贴报错**，不要换别的方式绕过。
3. 工具侧的坑（本会话踩过）
   - PowerShell 的 `Copy-Item`/`Test-Path` 把 `[...]` 当通配符 → mods 里带方括号的 jar 用 `-LiteralPath` 或先 `Get-ChildItem | Where-Object` 拿对象。
   - `java -jar cfr.jar` 传**中文路径**参数会被 ANSI 解码搞坏（`No such jar file E:\work\????\...`）→ jar/输出目录放纯 ASCII 路径，跑完再搬回。
   - `.ps1` 被执行策略挡 → 用 `.bat` 包装（已有 `put.bat`/`put.ps1`，一键把蓝图 JSON 放进剪贴板）。
   - push 到 GitHub 时通时不通（`Recv failure` / `Failed to connect …443`）→ 原样报错，网络好了再推。

---

## 1. 环境（2026-10-05 实测 dir 结果）

`F:\Apply\Release 2.3.0\.minecraft\versions\1.12.2像素小镇\mods\`：

| 状态 | 文件名 | 字节 |
|---|---|---|
| **启用** | `LittleTiles_v1.5.87_mc1.12.2.jar` | 1,994,663 |
| **启用** | `CreativeCore_v1.10.71_mc1.12.2.jar` | 1,321,137 |
| 启用 | `[平滑色块] flatcoloredblocks-mc1.12-6.8.jar` | 139,609 |
| **.disabled** | `[小方块]LittleTiles_v1.5.0-pre199_19_mc1.12.2.jar.disabled` | 1,489,576 |
| **.disabled** | `[小方块][littletiles前置]CreativeCore_v1.10.10_mc1.12.2.jar.disabled` | 1,086,158 |

- 即：**当前跑 1.5.87 + CC1.10.71**；`pre199_19 + CC1.10.10` 是旧线（已禁用，文件带 `[…]` 前缀）。
- 反编译源码：`lt_src\`（pre199）、`lt_src_187\`（1.5.87，438 个 java）、`cc_src\`（CreativeCore）——都不入库。
- 存档 `…\saves\新的世界\`；日志 `…\logs\latest.log`。

---

## 2. 资产清单（脚本 → 产物）

| 脚本 | 产物 | 作用 |
|---|---|---|
| `lt_np.py` | （库） | 街区通用库：`Vol`（numpy 体素 + 贪心合并 + 无损自检 + 打印导入起点）；`export(fn,name,structure=None)` 可把结构挂根层（自动补 `{}`） |
| `lt_root.py` | （库） | 根层守卫：根有 `children` 就必须有 `structure`（缺则插 + 硬断言）；CLI `selftest`/`verify`/`diff` |
| `lt_tree.py` | （库） | 导入文本树/语法校验器：递归解析、查 6 分量与 **7/11 分量可变形盒**、上界排他、count、min/size 全树并集、structure id（含 1.5.87 新 id）、offGrid 陷阱 |
| `lt_probe187.py` | `probe_187.txt` | 1.5.87 探针：A 官方粒子原文 / B 新键粒子 / C 扇叶+stayAnimated / D light15 / E 门→灯 / F 自激灯+总开关 / F10 十盏灯 / H 1/4 圆柱墙(倒角) / I 30° 斜板（间隔 2 格排开） |
| `lt_ramen.py` | `ramen_shop.txt`、`ramen_curtain.txt` | 拉面店外壳（漏光假灯 LEAKFIX）+ 暖帘独立 noclip 导出 |
| `lt_street.py` | `street_0..3.txt` | 主街路面 4 段（**已随 v1 街区作废**，可作 SDF/排版参考） |
| `lt_loop.py` | `loop_fan.txt` | 自转扇叶样品（advancedDoor rotY 0→360 linear 40 tick） |
| `lt_mech.py` / `lt_mech_v.py` / `lt_mech_v45.py` | `mech_test.txt` / `mech_v1..3` / `mech_v4..5` | 机关测试台与对照样品 |
| `lt_colors.py` + `flatcoloredblocks.csv` | （库） | hex → FCB 方块名（solid/trans/glow 最近邻） |
| `put.bat` / `put.ps1` | — | `put.bat probe_187` 把蓝图 JSON 放进剪贴板 |

---

## 3. 当前进度

- **方向已换**：旧 v1 街区（主街/南排店铺）**作废**；新目标 = **天梯城**（见 `DESIGN.md` v2 + `PLAN.md` v2：100×100 范围、4~255 分层、四网一心跳、R1~R8）。
- 拉面店：外壳完成、已实测导入；暖帘已改独立 noclip 文件（`ramen_curtain.txt`，相对店西北角偏移 `(3,2,-1)`，即拉面店导入起点 `+(4,2,1)`）。**下一步要整体改成金属舱体科技版（不保留木质外壳）。**
- 机关：`mech_test.txt` 在 1.5.87 下"都能动"；`/lt-open` 可用；**按钮只能开不能关**（见 §4②）；门禁只挡右键。
- 1.5.87 能力：`light`/`message` 可用，`particle` 未测；信号系统（命名端口 + 表达式连线 + PULSE + 自激）与 `BlockSignalConverter`（红石⇄信号）已就绪未用。
- **`probe_187.txt` 已生成并通过 `lt_root`+`lt_tree`**（9980 B，242 盒，导入起点 (0,0,0)，9 样品按 2 格间隔排开）；测试清单见 §6。

---

## 4. 源码级结论（行号取自 `lt_src_187`，对照 `lt_src`；✔=源码确认，❓=待实测）

### ① 小方块发光：1.5.87 改成"体积加权"，所以 FCB 发光小方块几乎不亮
- 1.5.87 `BlockTile.java:455`：`:465` 属于结构的 tile → `max(light, structure.getLightValue(pos))`（**不缩放**，`LittleLight.java:56`）；`:474` 否则 `ceil(tile.getLightValue(world,pos) * tile.getPercentVolume(context))`（**乘体积比例**）
- pre199 `BlockTile.java:455/464`：`tempLight = tile.getLightValue(state, world, pos)`（**原值，不缩放**）
- ⇒ 1 像素³ 的 tile 占比 ≈ 1/4096 → `ceil(15×1/4096)=1` → 等于不亮 ✔（与"导入后发光弱/不亮"吻合）
- ⇒ **要发光就用 `light` 结构**。❓ 不同体积的亮度曲线、`LittleBox.getPercentVolume` 分母未逐行确认。

### ② 按钮第二次触发不能关门；`disableRightClick` 挡不住关门
- `LittleDoorActivator.openDoor`（`:77-86`）只调 `child.openDoor(...)`（**只有"开"**，从不 `activate`）；`:79` `inMotion = true`，`isInMotion()`（`:120-123`）= 该标志
- `LittleDoor.activate`（`:64-100`）`:95` `opened = !opened`（**activate 才是开关切换**）；`:68-70` 仅 `DoorActivator.RIGHTCLICK` 受 `disableRightClick` 限制
- ⇒ 关门用 `/lt-open`（走 activate=切换）或**信号**（见 ⑤）。

### ③ `stayAnimated:1b` 能消除"变回方块时的闪烁+放置声"；限制是"起点必须对齐"
- 现象根因 `DoorController.java:146-150`：`endTransition()` 里 `if (turnBack != null && …) this.place();`（place=动画实体换回方块）
- `stayAnimated=true` ⇒ `turnBack = null`（`LittleAdvancedDoor.java:284`、`LittleSlidingDoor.java:71`、`LittleAxisDoor.java:215`）⇒ 不 place()、门停成动画实体
- NBT：`stayAnimated:1b`（`LittleDoorBase.java:79/101/115-116`，仅 true 时写）
- 限制："必须整圈"来自 `AnimationKey.java:110`（RotationKey `isAligned = value % 360 == 0`）、`:90`（OffsetKey 须 0）、`AnimationTimeline.java:204-206 isFirstAligned()`、`LittleAdvancedDoor.java:564/697`（未对齐则强制 true、GUI 取消不掉）
- 好处：`LittleDoorBase.java:293-295 isInMotion() = animation != null && controller.isChanging()` ⇒ 停住时 `isInMotion()==false` ⇒ 仍可被反复触发 ✔ ❓ 长期停留对碰撞/光照的影响未测。

### ④ 关门倒放：**中心对称只掩盖停位跳变，不掩盖转向；倒放无不改源码解法；child 事件叠加正转方案待查。**
- 依据：`LittleAdvancedDoor.java:252/258/264`（offX/Y/Z）、`:270/276/282`（rotX/rotY/rotZ）—— **close = `open.invert(duration)`**；`:284` 交给 `DoorController(open, close)`；NBT 只有 `animation:{rot*…/off*…}`，**没有独立关门时间轴** ⇒ 关门必然倒放（`ValueTimeline.java:201-215`）
- `ChildActivateEvent.run`（`:51-72`）：只在服务端、只对 `LittleDoor` 子结构、且**只 `openDoor`（不 activate）** ⇒ 想靠 child 事件"补一次正转开门"来掩盖倒放，目前**没验证过**，待查（事件在关闭回放时会按 `LittleDoorBase.java:169-175` + `AnimationEvent.java:160` 的 `invert(duration)` 镜像触发时刻）。

### ⑤ `particle_emitter` 获取 + NBT（含 g 可变形盒）
- **合成表**（jar 内 `assets/littletiles/recipes/particle_emitter.json`）：图案 `CDC / GRG / CCC`；C=`minecraft:concrete` data15 ×6、D=`minecraft:dispenser` ×1、R=`minecraft:redstone_block` ×1、G=`minecraft:firework_charge` ×2；`type: littletiles:crafting_shaped_premade`
- **给物品（1.12 语法）**：`/give @p littletiles:premade 1 0 {structure:{id:"particle_emitter"}}`（物品注册名 `littletiles:premade`，`LittleTiles.java:252`；NBT 带 `structure:{id:…}`，`LittleStructurePremade.java:62-81`）❓未实测
- **官方预制品原文**（`assets/littletiles/premade/particle_emitter.struct`）用的是**扁平旧键**；`loadSettings`（`LittleParticleEmitter.java:156-162`）确实读扁平键 `tickDelay`/`ticker`/`tickCount`/`speedY`/`spread`，但 **`color/lifetime/texture/size/gravity/growrate` 只在 `settings` 子标签里读**（`:161` `hasKey("settings") ? new ParticleSettings(…) : SMOKE 预设`）⇒ **官方 .struct 里那些键多半被忽略、实际走 SMOKE 预设**
- **新写法键表**：`tickDelay:int, tickCount:int, ticker:int, speedX/Y/Z:float, spread:float`（+圆形扩散 `steps:int`）、`settings:{color,lifetime,lifetimeDeviation,gravity,startSize,endSize,sizeDeviation,randomColor,collision}`（`LittleParticleEmitter.java:169-178`、`:358-381`）、`facing:int`（方向字段，默认 UP=4）、输出端口 `disabled`
- **g 可变形盒（1.5.87 新增）**：`LittleBox.createBox(int[])`（`:1120-1139`）——**6 分量**=普通盒；**7 分量**=`[6 坐标, slice id]`；**11 分量**=`[6 坐标, slice id, 4 个 float 位(startOne,startTwo,endOne,endTwo)]`（`Float.intBitsToFloat`）；187 里 `<0` 的 slice id 走另一套通用编码 ❓。**pre199 有同一套 7/11 编码但走切片盒**（`lt_src/LittleBox.java:1051-1060`），**没有可变形盒** ⇒ 同一文本两版解释不同。

### ☆ 2026-10-06 崩溃事件（probe_187 放置崩）与**待批准**修法

- **异常**：`java.lang.RuntimeException: Invalid id 224` @ `ValueTimeline.getType(ValueTimeline.java:24-28)`；线程 = **Client thread**；时机 = **放置（导入）时**：`Placement.placeTiles(:219)` → `PlacementBlock.place(:516)` → `TileEntityLittleTiles.updateTilesSecretly(:282)` → `PlacementStructurePreview.place(:617)` → `StructureTileList.setStructureNBT(:118)` → `create(:232)` → `LittleStructure.loadFromNBT(:579)` → **`LittleAdvancedDoor.loadFromNBTExtra(:198)`**
- **触发样品 = E**（唯一走"整节点平移"分支的样品）；证据：文件里只有 E 的 `animation.rotY` 首元素是 224（`[224, 4, 0, …]`），其余 8 个样品的结构文本没被平移、时间轴首元素都是 0
- **根因（我的工具 bug，不是 LT 的问题）**：排版用的 `trans()` **盲扫所有 `[I;…]`**，把 `animation` 里的时间轴也按坐标加了偏移 → `[I;0,2,0,0,0,20,…]` → `[I;224,4,0,224,2,20,…]` → `getType(224)` 抛错
- `ValueTimeline.read` 格式（`ValueTimeline.java:39-54`）：`[type(0~3), count, (tick, hi32, lo32)×count] + additional`（Linear 附加 0 个、Hermite 3 个）；`getType` 在 `id < -1 || id >= types.size()` 时抛 `Invalid id`
- **修法（2026-10-06 用户批准 A+C；**已实施**）**：
  - **A（已实施）**：`lt_probe187.py` 重写 —— 样品在**局部坐标**生成，导出后**只对 tiles 段**做一次平移（新函数 `shift_tiles`，带断言：该段只允许出现 6/7/11 分量的盒子数组），**结构文本一律不碰**；旧的 `trans()` 已删除；`axisCenter` 按最终坐标显式计算，且保证落在自家盒子包围盒内。
    ※ 顺带查清：`lt_np.Vol.export` 会把坐标**归一化到内容最小角所在的格**（`lt_np.py:24/41` `base=lo//16*16`），所以"直接生成在最终坐标"必须补这层 tiles 级平移才能与结构里的 `axisCenter` 对齐。
  - **B（不做）**：按用户要求跳过。
  - **C（已实施）**：`lt_tree.py` 新增两道守卫 —— ①**时间轴形态**：`rotX/Y/Z`、`offX/Y/Z` 数组必须 `a[0] ∈ {0,1,2,3}` 且长度 = `2 + 3*a[1]`（hermite id=3 再 +3 个附加）；②**axisCenter 落点**：必须落在**本节点自己的盒子包围盒**内（含边界）。**有问题时 `lt_tree.py` 现在返回 exit 1**。
  - **反例夹具**（入库）：`samples/broken_probe_187_timeline224.txt`、`samples/broken_probe_E_timeline224.txt` —— 两份都必须报错 ✔（已验）
  - **正例**：12 份文件（probe_187 / probe_187_safe / probe_A~I / probe_F10 / probe_j）全部 `lt_root=✓ lt_tree=✓` ✔（已验）
- 同一根因的另外两处（均已定位）：`lt_probe187.py` 的包围盒统计、`lt_probe_split.py` 的 `boxes_of()`（**后者已修**：只在 `bBox:`/`boxes:` 位置取数组）

### ★ 附属评估
- **ALET（A Little Extra Tiles）候选**：见 §7 结论（本轮已评估）。
- **Little Opener 不再需要**：`/lt-open`（命令方块可跑）+ 1.5.87 信号系统已覆盖"远程开关门"的需求，不引入额外前置。

### d. 信号最小 NBT 例（1.5.87）
- 端口状态存放：内部**输出**＝以端口名为键的 COMPOUND（`LittleStructure.java:650/578`），键 `state:int`(位图)/`con:string`/`mode:string`/`delay:int`（`InternalSignalOutput.java:71-82`）；内部**输入**＝以端口名为键的 int（`InternalSignalInput.java:36`）；外部输出处理器＝`signal` TAG_LIST（`:636-641`/`:556-568`）
- 目标表达式：`a<n>`=自己内部输入、`b<n>`=自己内部输出、`i<n>`/`o<n>`=外部输入/输出（指向子结构 single_input/single_output）、`c<n>.…`=下钻子、`p.…`=父（`SignalTarget.java:19-81`；`SignalUtils.java:16-72`）
- 运算符（`SignalLogicOperator.java:13/52/91/130/164/198/232…`）：`+`=or、`V`=xor、`&`=b-and、`|`=b-or、`^`=b-xor、`#`/`-`/`*`/`/`=算术；`!`=not（`SignalInputCondition`）
- **①按钮/doorActivator → light**：灯 `enabled:{state:0,con:"p.b0",mode:"EQUAL",delay:0}`，灯作为按钮的子结构（`p.b0` = 按钮的 `state` 输出）
- **②门 state → light**：同上，灯作为门的子结构（门只有 `addOutput("state")`，无输入）
- **③自引用**：`enabled:{state:0,con:"!b0",mode:"EQUAL",delay:10}`（`b0`=自己）⇒ 自激振荡；再与总开关做与：`con:"!b0&p.b0"`

### e. 门能被信号开/关吗？**能**（虽然没有命名输入）
- `LittleDoor.performInternalOutputChange`（`LittleDoor.java:176-186`）：当端口名 `"state"` 且 `opened != output.getState()[0]` 且不在运动中 → `activate(DoorActivator.SIGNAL, null, null)` ⇒ **信号写门的 state 输出即可开关门**，且 SIGNAL 路径不受 `disableRightClick` 限制 ✔
- ⇒ 这才是"按钮控制开关门"的正解（按钮走 openDoor 只能开，见 ②）

### ★★ 开关门正解（源码推导，**待 J 实测**）
> "把门做成某个开关结构的子结构，门的 `state` 输出写 `con` 引用父的输出" —— 这样**同一个门既能被开也能被关**。

```json
根 fixed → 子0 light(level:0, enabled:{state:0})            // 开关：右键 toggle enabled
             └ 子0 advancedDoor(disableRightClick:1b,
                    state:{state:0, con:"p.b0", mode:"EQUAL", delay:0})
```
- 机制：右键面板 → `LittleLight.onBlockActivated`（`LittleLight.java:61-66`）→ `getOutput(0).toggle()` → 门的 `con` 算式 `p.b0`（`SignalTargetParent`：`structure.getParent().getStructure()` → 父的内部输出 0）重算 → 写门的 `state` 输出 → `LittleDoor.performInternalOutputChange`（`:176-186`）→ `activate(SIGNAL,…)` → **门开/关切换** ✔
- 开关源也可以不用 light：任何有输出的结构都行（门/按钮/`signal_display_16`）；light 的好处是**右键即切换**且不占交互（`disableRightClick` 不写就是 false）

**⚠ 风险注记（已查证，结论：机制成立）**：E/F/J 都依赖"某个结构的输出变化会通知整棵树重算 `con`"。源码路径：
| 环节 | 位置 |
|---|---|
| 组件状态变了 | `ISignalComponent.java:20` `this.changed();` |
| 输出变化出口 | `InternalSignalOutput.changed()`（`InternalSignalOutput.java:37-43`）→ `parent.performInternalOutputChange(this)` + `parent.schedule()` |
| 冒泡到根 | **`LittleStructure.notifyChange()`（`LittleStructure.java:786-798`）**：有父就 `this.parent.getStructure().notifyChange(); return;`（一路上冒）；**只有根（无父）才往下走** |
| 根上递归全树 | **`LittleStructure.processSignalChanges()`（`:800-817`）**：先跑自己的 `externalHandler.update()`（`:802-804`）、再跑自己的 `outputs[i].update()`（`:806-810`，= `InternalSignalOutput.update()` 求值 `con`）、**再递归 `child.getStructure().processSignalChanges()`（`:811-816`）** |
| 调度器入口 | `LittleStructure.changed(ISignalComponent)`（`:839-841`）→ `schedule()`；`ISignalSchedulable.schedule()`（`:29`） |
⇒ **"父（乃至任意节点）的输出变化最终会让全树的 `con` 被重新求值" = 成立**（不是父→子单向，而是"冒泡到根 + 根递归全树"）✔ 因此 E/F/J 的写法在机制上可行，**J 一测就能验证整条链路**。

### g-2. 7/11 分量盒在 187 是"旧切片兼容格式"
- 1.5.87 的 `LittleBox.createBox`（`:1120-1139`）对 7/11 分量的解释**沿用了旧的切片编码**（`slice id` + 4 个 float 位），返回的却是 `LittleTransformableBox`；**原生可变形盒自己的编码格式未知**（`slice id < 0` 走通用构造 `:1128-1129`，含义没读出来 ❓）
- ⇒ **不要凭猜测手写可变形盒**：以游戏内导出为准 —— **测试项 K**（用 LT 的斜面/变形工具做一块斜面，蓝图复制导出，把该 tile 的盒子数组原样贴回来）

### f. child 事件在关门（倒放）时的行为
- `ChildActivateEvent.run`（`:51-72`）：**只 openDoor，不 activate** ⇒ 关门过程中即使事件触发，也只是"再开一次"；若子门已在开态 → `canOpenDoor` 返回 null → 静默不动 ✔

---

## 5. 下一步计划（用户已定，按此顺序）

1. **`lt_np.py` 加接口**：把 `light` / `particle` / `signal`（命名端口、`signal` 列表、`con` 条件、`stayAnimated`、可变形盒）做成可写参数，让后续模块直接产出带机关的蓝图。
2. **拉面店 → 金属舱体科技版**（不保留木质外壳；见 DESIGN 末行设施清单）。
3. **按 `DESIGN.md` + `PLAN.md` v2 铺天梯城**：人造山体 + 峡谷 + 四层竖向分区；**所有可见表面 100% 小方块**（整方块只允许用于完全被包裹的实心内部和临时脚手架，见 DESIGN【精度原则】）；`mass_v0.schematic` 只是规划草图，最终全部替换。

**既有硬约束**：蓝图 min 角落锚点格、体素落点 = `锚点 + floor(坐标/16)`；根有 children 必须有 structure（`lt_root` 拦）；写完必跑 `lt_tree` 到 `[问题] 无`；`Vol.export` 无损必须 True；室外离室内 ≤2 格的装饰灯用同色假灯（1.5.87 下小方块自发光基本无效，直接上 `light` 结构）。

---

## 6. 用户操作说明（探针 + 体块 + 截图/回报清单）

**样品排布**（`probe_187.txt`，从西往东、间隔 2 格、都坐在 2px 底座上）：A 官方粒子 → B 新键粒子 → C 扇叶 → D 灯15 → E 门→灯 → F 自激 → F10 十盏 → H 曲面（209 盒）→ I 斜板；导入起点 (0,0,0)。`probe_j.txt` 是独立的小样品（面板 → 卷帘门），导入起点 (0,0,0)。

**a. 导入探针（先 safe 版，再逐样品，每导入一个之前先存档）**：
1. 先导入 **[probe_187_safe.txt](E:\work\建筑\probe_187_safe.txt)**（A/B/C/D/F/F10/H/I，**已去掉会崩的 E**；9495 B、239 盒、导入起点 (0,0,0)）
2. 嫌疑样品**逐个**导入，**每导入一个之前先存档一次**（顺序 = 风险从低到高，见 §6 e）
3. 全部放在城区外（城区是 x -800~-701 / z 300~399，别放进去；`probe_j.txt` 是独立小样品）
4. ⚠ **`probe_E.txt` 是已确认必崩的样本**（`Invalid id 224`），只在"想复现崩溃"时导入

**e. 单样品文件与推荐导入顺序（风险从低到高，我的建议）**：
| # | 文件 | 内容 | 为什么排这个位置 | 导入起点(格/px) |
|---|---|---|---|---|
| 1 | `probe_H.txt` | 1/4 圆柱曲面（209 盒） | 纯几何，无任何结构机器，最不可能崩；同时看曲面观感 | (36,0,0) / 576px |
| 2 | `probe_D.txt` | light level:15 | light 结构最简单（level + enabled state） | (11,0,0) / 176px |
| 3 | `probe_C.txt` | 扇叶 + stayAnimated:1b | 时间轴合法；风险只在"轴心坐标没随样品平移"（视觉，不崩） | (6,0,0) / 96px |
| 4 | `probe_A.txt` | 官方 particle_emitter 原文 | 探路：先确认 particle_emitter 在本环境能否放置 | (0,0,0) |
| 5 | `probe_B.txt` | 新键名 particle_emitter | 与 A 对照（settings 子标签写法） | (3,0,0) / 48px |
| 6 | `probe_J.txt` | light 右键 → 卷帘门 `con:"p.b0"` | 验证"信号开关门"整条链路；时间轴合法 | (0,0,0) |
| 7 | `probe_F.txt` | 自激灯 + 总开关 | 自引用振荡，可能有卡顿/异常 | (18,0,0) / 296px |
| 8 | `probe_F10.txt` | 10 盏自激灯 | 压测（帧率） | (22,0,0) / 360px |
| 9 | `probe_I.txt` | 30° 斜板（11 分量盒） | 编码**未经验证**，可能崩或形状不对 | (46,0,0) / 736px |
| 10 | `probe_E.txt` | 门 state → 灯 | ★**已确认必崩**（时间轴首元素 224），只用于复现 | (14,0,0) / 224px |

> 与你给的顺序（D→H→C→E→J→B→A→F→F10→I）差别：我把 **E 挪到最后**（已确认必崩，放前面只是白挨一次崩溃），并把 H 放第 1 位（纯几何最保险）。其余相对次序照你的来。

**f. 精度压力样品 `density_test.txt`（6 格宽 × 8 格高 × 2.25 格厚的金属舱壁）**：
2. **再退到 10 格外看一次**：整体观感会不会"糊"、远看是否有起伏层次
3. **两次都记 F3 帧率**（并留意是否卡顿）
4. 参考数据（脚本实测）：**263 个盒子 / 占用 144 个方块格 / 表面 6×8=48 格上 259 个盒子 ≈ 每表面格 5.4 个盒子**；用途 = 按这个密度估算全城规模可行性

**g. 测试项 K 的操作步骤（测 187 原生可变形盒编码）**：
1. 手持 **Little Chisel（小方块凿子）**，切到 **slice（切片）模式**
2. 在任意方块/小方块面上**放一块斜面**（切出斜切面）
3. 用 LT 的**蓝图/复制工具**把该结构**导出成文本**
4. 把该 tile 的**盒子数组原样贴回来**（形如 `[I;…]`，注意看是 6 / 7 / 11 个分量、`slice` 值、以及尾部那几个 int）
   ⇒ 有了它就能确定 187 原生可变形盒的真实编码，再决定 `probe_I`（30° 斜板）怎么写
   **（已解决 2026-10-06：K 已解码并手算验证 —— 见 NOTES 第 22 条 + `lt_tbox.py`；8 分量 = `[6坐标, indicator, word…]`，bit31 标记 / bits24-29 六面 flip / bits0-23 = 哪个角哪个轴存了偏移，word 里 16-bit short 打包，偏移 = 基础角 + 偏移；角序 EUN,EUS,EDN,EDS,WUN,WUS,WDN,WDS）**

**h. 按 2a 结论重做的新探针（2026-10-06，各一份独立文件，导入起点都在 (0,0,0)）**：
> 机制：**门动画会把它的 children 一起搬进动画假世界**（`LittleDoorBase.java:222-223` + `StructureChildToSubWorldConnection`）⇒ 灯**不能**当门的子结构，否则一开门灯就完全不亮（E/F/F10 实测就是这个）。
1. **`probe_E2.txt`**（1024 B，12 盒）：根 fixed → **控制器 light(level:0)** → 子0 卷帘门(offY 上升 2 格, `state.con:"p.b0"`)、子1 灯(level:15, `con:"p.b0"`)＝**互为兄弟** ⇒ 右键控制器：门开关 + 灯跟随亮灭，且门动时灯不灭
2. **`probe_F2.txt`**（560 B，4 盒）：控制器 → 1 盏自激灯 `con:"!b0&p.b0"` delay 10 ⇒ 右键控制器=总开关；开着时灯应自闪、关掉即停
3. **`probe_F2x10.txt`**（2024 B，13 盒）：同上 ×10 盏（看帧率）
4. **`probe_J2.txt`**（884 B，11 盒）：J 的 `stayAnimated:1b` 版（控制器 + offY 门，门禁右键仍在）⇒ 预期**不再闪、无放置声**
5. **`probe_H2.txt` / `probe_H3.txt`**（各 16 盒）：1/4 圆柱墙 R=8 格、高 4 格、壳厚 2px，**16 个原生可变形盒切面（无台阶）**；H2 石英、H3 纯色 FCB 灰（判断条纹是不是贴图拼缝）⇒ 贴近 + 10 格外各看一次，都不该再有台阶感；H2/H3 对比可确认条纹来源
6. **`probe_H2b.txt` / `probe_H3b.txt`**（各 **64 盒** = 16 切面 × 4 段，每段 1 格高）：**只用向内偏移**的版本 —— H2/H3 里有 `+1/-1/-8` 等**向外**偏移，而 `setBounds(:1596-1623)` 会把包围盒夹回 AABB ⇒ 面与记账/切分/碰撞不一致（`lt_tree` 已把它标成 `[问题]`）。**优先看 H2b/H3b**；H2/H3 保留作对照
7. 新规则（已入 NOTES 第 25 条）：**可变形盒角偏移只写"向内或 0"**；跨格时按格拆段（H2b/H3b 已按 1 格高拆 4 段）

**b. 体块模型**：把 `mass_v0.schematic` 放进 `.minecraft/config/worldedit/schematics/`，游戏内 `//schem load mass_v0` → `//paste -o`；若报方块数超限先 `//limit -1`。
⚠ **粘贴会清空 x -800~-701、z 300~399、y3~255 内的一切**（旧 v1 建筑/街道会一起被清掉，用户已同意不备份）。

**c. 截图只要 3 张**：
- **图1**：探针排**南侧**、斜上方约 45° 全景（看 A/B 粒子、D/E 亮度、H 观感、J 门）
- **图2**：贴近 **H（和 I）平视 2 格**（看曲面台阶感/倒角、斜板角度）
- **图3**：体块 —— 飞到 **(-830, 200, 430)** 朝**东北**俯看全城

**d. 文字回报**：
- **C**：还闪不闪？还有没有放置声？
- **E**：开关两次的灯状态（开门亮/关门灭对不对）
- **F**：是否自己闪？大概几秒一次？总开关（那扇小门 `/lt-open`）能不能停它？**F10**：开启前后帧率与卡顿感
- **J**：右键面板能否把门**打开**？再按能否**关上**？（这是"开关门正解"的实测）
- **G**（不用蓝图）：在一盏**原先放着的旧发光建筑**旁边放一个方块再拆掉，看它会不会变暗（验证 §4① 的体积加权光照是否也影响旧建筑）
- **K**：在游戏里用 LT 的斜面/变形工具做一块斜面，用蓝图**复制导出**成文本，把该 tile 的**盒子数组原样贴回来**（§4 g-2：原生可变形盒的编码不要猜，以游戏内导出为准）

---

## 7. 附属评估（ALET / Little Opener）

**ALET = A Little Extra Tiles（候选，未安装）**
- 来源：用户给的三个 URL 之一（Modrinth 项目 `NWquC4YJ` / slug `a-little-extra-tiles`）⇒ 机器可读视图：**`game_versions: ["1.12.2"]`、loader `forge`、当前版本 `1.0.23`、共 18 个已发布版本、许可 LGPL-3.0-only、下载 15397**
- **要求的 LT/CC 版本**（官方 README 正文原文）："The current version of A Little Extra Tiles (ALET) 1.0.23 is compatible with **CreativeCore_v1.10.70** and **LittleTiles_v1.5.58_mc1.12.2**" ⇒ 比我们当前（**1.5.87 + 1.10.71**）**旧**；向上兼容性 **❓未验证**
- 它做什么：**Photo Importer**（图片→LittleTiles 结构，默认上限 **98×98**）、**Typewriter**（文字/字体→结构）、**Tape Measure**（测距，最多 10 组）、以及**新增结构类型（new structure types）**
- ⚠️ **卸载后会不会坏**：README 明确写它 "adds … **new structure types**" ⇒ 一旦生成的结构引用了 ALET 自己的结构类型，**卸载 ALET 后大概率失效/报错**（原版找不到该 id）；图片/文字导入本身产出的应主要是普通 tile（原版/FCB 方块），但**"到底用了哪种结构类型"在不安装的情况下无法确认** ⇒ 标记为**推断 + ❓**
- **抓取情况（如实回报）**：用户给的三个 URL → Modrinth 页面本体是 JS 渲染（只回标题）、CurseForge 页面 **403 Cloudflare**（"Just a moment..."）、GitHub 页面只回导航壳、`raw.githubusercontent` 拉取失败。上述结论数据来自**同三个资源的机器可读视图**（Modrinth API + 官方 README 正文），已注明来源。
- **建议**：**先不动**。要用的话必须①先备份存档；②只用于"生成纹理/文字这类纯 tile"的活；③**不要把 ALET 的结构类型嵌进主体建筑**；等出现 1.5.87 兼容声明再考虑批量用。

**Little Opener：不再需要** —— `/lt-open`（可用命令方块跑）+ 1.5.87 信号系统（门 `state` 输出 → `activate(SIGNAL)`，见 §4e）已覆盖"远程开关门"，不引入额外前置。
