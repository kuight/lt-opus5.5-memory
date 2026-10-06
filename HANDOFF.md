# HANDOFF —— LittleTiles 1.12.2 天梯城项目（给下一个无记忆的会话）

> 配套：`NOTES.md`（环境/已验证结论/审美偏好/进度/测试记录/1.5.87 基线核对）、`PLAN.md`（天梯城总图 v2，旧版 `PLAN_v1_old.md`）、`DESIGN.md`（设计稿 v2 + 规则 R1~R8）、`FILES.md`（脚本清单）。
> 工作目录 `E:\work\建筑\`（**脚本必须在此目录运行**：`lt_colors.py` 用相对路径读 `flatcoloredblocks.csv`）；记忆仓库 `E:\work\lt-memory\`（远端 `kuight/lt-opus5.5-memory`）。

---

## 0. 会话开场（必做）

1. 先写 `probe.txt` 并用 `dir` 确认；**不要用命令把大段文本打到终端**，用 `read`(offset/limit) / `grep` / `glob` 工具；凡是落盘立刻读回验证。
2. **三条规矩（用户 2026-10-05 明确要求）**
   - (a) **设计建筑/功能/物件之前，必须先搜索科幻作品、建筑案例、工程原理**，尽量贴合设计目标，**设计稿里写明参考来源**；**技术问题查 `lt_src_187` 源码**（不是只看笔记）。
   - (b) **测试要压缩到 2~3 张截图**：测试清单必须写明拍摄角度/站位，让用户照着拍。
   - (c) **每轮结束更新 NOTES/HANDOFF 并推送，回报完整 SHA**；push 失败**原样贴报错**，不要换别的方式绕过。
3. 工具侧的坑（本会话踩过）
   - PowerShell 的 `Copy-Item`/`Test-Path` 把 `[...]` 当通配符 → mods 里带方括号的 jar 用 `-LiteralPath` 或先 `Get-ChildItem | Where-Object` 拿对象。
   - `java -jar cfr.jar` 传**中文路径**参数会被 ANSI 解码搞坏（`No such jar file E:\work\????\...`）→ jar/输出目录放纯 ASCII 路径，跑完再搬回。
   - `.ps1` 被执行策略挡 → 用 `.bat` 包装（已有 `put.bat`/`put.ps1`，一键把蓝图 JSON 放进剪贴板）。
   - push 到 GitHub 时通时不通 → **已在 git 设全局代理**：`http.proxy` / `https.proxy` = **`http://127.0.0.1:7897`**（Clash Verge / verge-mihomo 的系统代理端口）。**Clash 没开时 push 会失败**，先确认代理在运行；失败时原样贴报错，不换别的方式绕。

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

- 旧拉面店与 v1 街道已随 **mass_v0 粘贴清除**（用户同意不备份）。
- **当前阶段 = 几何与机关基础件验证**：曲面墙 **H4/H5 待修+待测**、**scale_B 帧率已降级**（静止高、移动/转身卡，暂不排查）。
- 之后：**合成蛋白面馆设计稿**（第一栋精细建筑，用来定**中式科幻设计语言**）→ 定**全城细节密度标准** → **体块 v1**（按 DESIGN「高度感与体块 v1 方向」）。

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
- **新写法键表**：`tickDelay:int, tickCount:int, ticker:int, speedX/Y/Z:float, spread:float`（+圆形扩散 `steps:int`）、`settings:{color,lifetime,lifetimeDeviation,gravity,startSize,endSize,sizeDeviation,randomColor,collision}`（`LittleParticleEmitter.java:169-178`、`:358-381`）、`facing:int`（**默认 UP=1**；序 = DOWN0 UP1 NORTH2 SOUTH3 WEST4 EAST5）、输出端口 `disabled`
- **g 可变形盒（1.5.87 新增）**：`LittleBox.createBox(int[])`（`:1120-1139`）——**6 分量**=普通盒；**7 分量**=`[6 坐标, slice id]`；**11 分量**=`[6 坐标, slice id, 4 个 float 位(startOne,startTwo,endOne,endTwo)]`（`Float.intBitsToFloat`）；187 里 `<0` 的 slice id 走另一套通用编码 ❓。**pre199 有同一套 7/11 编码但走切片盒**（`lt_src/LittleBox.java:1051-1060`），**没有可变形盒** ⇒ 同一文本两版解释不同。

### ☆ 2026-10-06 崩溃事件（probe_187 放置崩）与**已实施**修法

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
- **②门 state → light**：**灯不能挂在门下，必须做控制器的兄弟节点（NOTES 17）** —— 门动画会把 children 搬进动画假世界 ⇒ 灯不亮
- **③自引用**：`enabled:{state:0,con:"!b0",mode:"EQUAL",delay:10}`（`b0`=自己）⇒ 自激振荡；再与总开关做与：`con:"!b0&p.b0"`

### e. 门能被信号开/关吗？**能**（虽然没有命名输入）
- `LittleDoor.performInternalOutputChange`（`LittleDoor.java:176-186`）：当端口名 `"state"` 且 `opened != output.getState()[0]` 且不在运动中 → `activate(DoorActivator.SIGNAL, null, null)` ⇒ **信号写门的 state 输出即可开关门**，且 SIGNAL 路径不受 `disableRightClick` 限制 ✔
- ⇒ 这才是"按钮控制开关门"的正解（按钮走 openDoor 只能开，见 ②）

### ★★ 开关门正解（源码推导；**J / J2 / E2 已实测通过**）
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

### g-2. 7/11 分量盒 / 原生可变形盒
- **原生编码已解码**：见 **NOTES 第 22 条 + `lt_tbox.py`**（`[6坐标, indicator, word…]`，bit31 标记 / bits24-29 六面 flip / bits0-23 掩码，word 里 16-bit short 打包，偏移 = 基础角 + 偏移；角序 EUN,EUS,EDN,EDS,WUN,WUS,WDN,WDS）；K 样本往返**逐位一致 ✔**。
- **7 / 11 分量为旧格式**（`LittleSlice` 编码），`lt_tree` 只报 **`[警告]`**，不再当问题。
### f. child 事件在关门（倒放）时的行为
- `ChildActivateEvent.run`（`:51-72`）：**只 openDoor，不 activate** ⇒ 关门过程中即使事件触发，也只是"再开一次"；若子门已在开态 → `canOpenDoor` 返回 null → 静默不动 ✔

---

## 5. 下一步（**按顺序**，2026-10-06 设计方对话后重排）

1. ~~merge_entries / H4·H5 / scale_A~~ → **已完成（a7fb541）**；本轮又做了：`prism` 内方向 bug 修复（min 侧向内=正）、`lt_geom` 度量改为纯边界距离 + 角点环带检查。**但 H4/H5 仍未达标**（32 角点越环带、最大偏差 2.35px）⇒ 见第 3 条。
2. **scale_B 帧率排查 → 已降级**：静止时帧率高，卡顿只在**移动/转身**时出现，暂不排查（规则：不再报具体 fps，只描述"静止高不高 / 移动转身卡不卡"）。
3. **H4/H5 曲面墙收尾（下一步第一件事）**：① 消除残余锯齿 —— 段 7/8 处三角形薄片的 bbox 角点对到了错的顶点，需在 `prism` 里把"环带钳制"真正跑通（±1px 内拉回环带）或改用"取整后的真顶点当包围盒"；② 造一个**真的** 2px 偏移反例（上轮写失败，退化成 H4 副本）；③ 三项门禁全过后才可交付。
4. **合成蛋白面馆设计稿（先查资料）** → 用来定**全城细节密度标准**。
5. **体块 v1**（按 DESIGN「高度感与体块 v1 方向」）。

**交付门禁（重申）**：`lt_root` + `lt_tree` + `lt_geom`（含可变形盒时）**三项全过**才能交付；**单个文件 ≤1MB**。

**给设计方（Claude）的接续说明**：新会话先读**最新 SHA 的** HANDOFF → NOTES → DESIGN → PLAN → FILES；用户每轮会转发 agent 报告和完整 SHA；**设计方说法若与仓库结论矛盾，以仓库为准**，回仓库核对。

**用户协作习惯**：截图数量有限 → 测试压缩到 **2~3 张**并写明拍摄角度，给回报模板；agent 联网搜索 **401（待用户换 key）**，期间只直接抓指定 URL。

## 6. 待测清单
**已完成、见 NOTES 测试记录**：探针导入（safe 版/风险顺序/density/K 操作步骤/各样品回报项）、E2/F2/F2x10/J2/H2b/H3b、density_test、scale_B、K 解码 + `lt_tbox` 回归。
**待测**：**`probe_H4.txt` / `probe_H5.txt`**（等几何修好后：贴近看曲面是否还有台阶/锯齿、H4 浅灰 FCB `flatcoloredblock80:7` 与 H5 中灰 `flatcoloredblock80:3` 哪个当大面材质）；**`scale_A.txt`**（真 45° 倒角宽 1px，2 格距离看不出，看更大距离/更近距离是否需要加宽）。
**帧率一律只记"静止高不高 / 移动转身卡不卡"**（不再记具体 fps）。
**几何自检**：`python lt_geom.py <文件> [R,壳厚,起角,终角,高]`；反例夹具 `samples/jagged_probe_H4_16seg.txt`、`samples/bad_probe_H4_offset2px.txt`（**注意：后者上轮写失败，目前是 H4 副本，需重造**）。

**既有硬约束**：蓝图 min 角落锚点格、体素落点 = `锚点 + floor(坐标/16)`；根有 children 必须有 structure（`lt_root` 拦）；写完必跑 `lt_tree` 到 `[问题] 无` +（含可变形盒时）跑 `lt_geom`；`Vol.export` 无损必须 True。

---

**已完成归档**：探针导入（`probe_187_safe` / 风险顺序表 / `density_test` / K 操作步骤 / 各样品回报项）、E2/F2/F2x10/J2/H2b/H3b、scale_B、K 解码与 `lt_tbox` 回归 —— **见 NOTES 测试记录**；体块粘贴法见 **NOTES 操作记录**。

**b/c/d（体块粘贴、3 张截图、C/E/F/J/G/K 回报项）已完成，见 NOTES 测试记录；体块粘贴法见 NOTES 操作记录。**

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
