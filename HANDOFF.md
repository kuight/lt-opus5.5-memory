# HANDOFF —— LittleTiles 1.12.2 天梯城项目（给下一个无记忆的会话）

> 配套：`NOTES.md`（环境/已验证结论/审美偏好/进度/测试记录/1.5.87 基线核对）、`PLAN.md`（天梯城**总图 v3**，旧版 `PLAN_v2_old.md` / `PLAN_v1_old.md`）、`DESIGN.md`（设计稿 v2 + 规则 R1~R8）、`FILES.md`（脚本清单）。
> 工作目录 `E:\work\建筑\`（**脚本必须在此目录运行**：`lt_colors.py` 用相对路径读 `flatcoloredblocks.csv`）；记忆仓库 `E:\work\lt-memory\`（远端 `kuight/lt-opus5.5-memory`）。

---

## 0. 会话开场（必做）

### 常犯错误清单（设计方与 agent 共用，每轮开工前对照）
1. 新增件不核对已有件位置 → 重叠断言失败（noodle3 雨棚压腰线、bridge2 下照灯压支座）。写生成器时，每个新件都要对照它附近所有 fill/slab 的区间。
2. 方向变了只给旧骨架打补丁（撤中式后 noodle3/4 换零件不换体块）→ 方向一变先回体块重做。
3. 太规整：等距、同高、同尺寸、同心圆 → 默认不等距、不等高、店铺大小新旧都不同；秩序靠标准截面，复杂靠加建。
4. 招牌文字左右反 → 东面看左手=+z，西面看左手=−z，北面看字要从 x 大往 x 小排。
5. 自设体积上限（1MB）→ 不设上限，只观察导入是否异常。
6. 凭感觉说"上下文快满"就停手 → 不凭估计停工，只在 push 失败时按规矩停。
7. 斜面放在贴地格 → 最底一格用 16px 墙基托起。
8. 可变形盒只许向内偏移；弧墙水平方向不拆格，只按高度分段。
9. 帧率报数字会误导 → 只描述静止时高不高、移动转身卡不卡。
10. 没读回就说"已生效/已不再触发" → 一切以读回、实际 exit 为准。
11. 设计前不查资料 → 设计稿必须写参考来源。
12. 远景用低精度（大方块"外城海"）→ 被否；可见面全部小方块，大方块只当实心芯或脚手架。
13. 夜景太暗、灯太少 → 每个成品都要有足量发光件，夜景单独验收。
14. 用户测试项只写给用户、没进任务书 → 任务书里凡是说"换成下面的…"，正文必须附在同一份任务书里。
15. 补丁用文本模式写盘 → 行尾变 CRLF，打印的哈希和文件实际哈希不一致。补丁一律用 io.open(P, "w", encoding="utf-8", newline="") 写盘，并对文件字节重新算哈希。
16. 做旧只放几块小补丁 → 3 格外看不出。做旧要成片：锈水痕、泥污、褪色掉漆、剥落露筋、补板铆钉、外挂线缆，坏灯也算做旧。
17. 要照亮周围却用 FCB 发光块（只自亮、不照亮邻块）→ 照明必须用 light 子结构；做灯之前先读 NOTES「机关标准写法」。
18. 编号、标识、招牌默认做成发光件，夜里才看得见，也更合理。
19. 生成前不先算坐标极值 → 边距 M 取小了就"越界"（B 的 z=-20 越界）。**先算 min/max 再定边距**；另外**多字串要推进游标**（"合成蛋白"四个字曾叠在一起），**自检图要看真实朝向**（否则镜像会骗自己）。
20. 大件套了根结构（生成器见到子结构就自动给整座桥包 fixed）→ 约 1762 格连成一个结构，一靠近 chunk updates 狂跳、背对不卡、TPS 正常。**大件本体不套任何结构**；灯/门等结构做成独立小件文件，与本体同一放置点。生成器要断言：本体文件 structure: 次数 = 0。
21. 借用生成器生成对照件时，它会先删掉 OUT → 恢复备份前先判断文件是否存在。
22. 对照件之间有没解释的字节差（两份 K 差 56 字节被当成无关）→ 每个对照件都要和基准逐字节比对，差异全部讲清楚再拿去测；新写法验收必看 chunk updates。

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
- **每轮推送前的固定动作（2026-10-08 起）**：必须更新 ① HANDOFF **§3 当前进度** ② HANDOFF **§5 下一步** ③ **常犯错误清单**（有新错就加）④ NOTES 末尾**「设计方决定日志」**（有新决定就加）；**汇报里必须报清这四处各改了几行**。
- **分工规则（2026-10-07 设计方定）**：**生成器与检查器由设计方编写**；执行 agent **只负责原样保存、运行、贴完整输出、更新文档、推送**，**不修改脚本逻辑**；**运行报错就原样贴 traceback 并停下，等设计方改**。
- **写入/验证必须分两条消息**（2026-10-07 查清）：中文路径**没问题**（对照测试三个路径全部落盘 ✓）；之前"文件丢失"的真实原因是**我自己 `Remove-Item "_*"` 删掉了临时脚本**＋**把写文件与验证放在同一条消息里导致并发竞态**。批量改脚本时用"同一条命令里 python 改写 + 立刻校验"。**若整条命令被吞、脚本没落盘**：用 `$code | python -` **管道运行、不落脚本文件**（已验证稳定）。另注：`E:\work` 下存在乱码目录 `鏈棩鐙傚緬浼樺寲璁板綍`（UTF-8 被当 GBK 解），说明历史上某些调用用错代码页建过目录（该目录是空的）。
- **git 提交被吞（2026-10-08）**：长 git commit/push 命令及同回合的写文件会被 harness 丢弃（无输出、无副作用，写工具报成功但文件不存在），只读短命令正常。已试无效：`$code | python -` 包装、写 message 文件 + commit -F、Set-Content。对策：① 提交信息一律短英文 -m；② 写文件、提交、推送分成不同消息；③ 同一回合连续两次被吞 ⇒ 停下，请用户本地手动提交或开新会话。

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
- **几何基础件验证完成**：`arc_wall_with_base`（16px 墙基 + 共用内弧顶点）三项门禁全过、实测无缝隙 ⇒ 弧墙默认用它；**H4/H5 已由 H6→H8 取代**。
- **面馆线（noodle1~4）全部退役**：一期体块+剖面 ✓、二期a 中式方向已撤、v3/v4 造型被用户否决 ⇒ 面馆改为**桥下面摊**，在**轨道桥**下重做。
- **mass_v1 灰模已实测**：用户「**开始吧，感觉还可以**」⇒ **布局通过，作为脚手架保留**（成品仍要一块块换成小方块）。
- **轨道桥标准件 一期已实测**（酷、很像、不卡；「B-0x」与「轨道一号线」文字清楚、方向正确；桥下净空基本够）⇒ 一期仅作**截面接口参考**。
- **轨道桥二期·原型段已实测**（坡道「**平滑，完全ok**」⇒ **可变形盒坡道可用**；「不等墩距 + 多种墩型」思路成立；但**灯不够**、**B-09 做旧没做好**）。
- **轨道桥二期b 已实测**（「**差不多了**」；灯够了、做旧有了）⇒ 仍要改三条：**①桥墩标号改发光 ②做旧颜色更丰富随机 ④照明必须用真 `light` 子结构**（FCB 发光不照亮邻块）。
- **轨道桥二期c 卡顿已定位并修复**：**根 fixed 外壳**是元凶（整座桥约 1762 格连成一个结构 ⇒ 靠近时 chunk updates 狂跳、背对不卡、TPS 正常）；**发光墩号 / B-09 随机配色 / light 子结构本身都不卡**。⇒ 已拆成 **`samples/bridge2_body.txt`（桥身，无结构，已实测不卡）** + **`samples/bridge2_lights.txt`（10 盏 light，同一放置点、先放）**；**二期c 原版 `samples/bridge2_proto.txt` 已停用**（保留归档）。
- **之后**：**桥下三档店铺**（**B-08~B-09 净跨约 12~14 格放豪华大店；B-08 门洞 南北 4 格 × 东西 3 格 塞破烂小摊**）→ **列车（门动画）+ light / 粒子** → 各片区逐个细化；**mass_v1 是脚手架，成品一块块用小方块替换上去**。
- **样品测试地点 = 城东 x≈-600、z≈300**；**城区 x -800~-641 / z 300~459 内不再放样品**（那里是 mass_v1 城区，会被覆盖）。
- **【执行侧尝试·可整体删除】桥下三档店铺 v1 已出样品**：`samples/shop1_exec_A.txt`（门洞破烂小摊 473 盒）+ `shop1_exec_B.txt`（净跨豪华大店 441 盒），三项门禁全过；脚本由**执行侧自写自跑**（`lt_shop1_exec.py`），说明与回退方法见 `EXEC_ATTEMPT.md`（锚点 tag `pre-exec-attempt`）。

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

## 5. 下一步（按顺序）

1. **轨道桥二期c 拆分件（桥身 + 灯，两文件）已入库、门禁全过 ⇒ 待用户实测**：`samples/bridge2_body.txt`（136155 B，**无结构**，已实测不卡）+ `samples/bridge2_lights.txt`（2271 B，10 盏 light）；**先放灯、再放本体，两文件点同一格**；**测试项见 §6**。（二期c 原版 `bridge2_proto.txt` **会卡、已停用**）
2. **桥下三档店铺**（**B-08~B-09 净跨约 12~14 格 → 豪华大店**；**B-08 门洞 南北 4 格 × 东西 3 格 → 破烂小摊**；面摊在桥墩与梁底挂载，红灯笼 + 竖挂霓虹招牌 + `light` / 粒子）——**起点 = 城寨市井两线交叉口**。
3. **列车（门动画）+ light / 粒子** → 之后各片区逐个细化；**mass_v1 已实测通过（布局通过，作脚手架保留）**，与 bridge 一期一起只当脚手架 / 截面接口参考，**成品一块块用小方块替换上去**。
4. **【执行侧尝试·可删】桥下三档店铺 v1 样品待实测**：`shop1_exec_A`（门洞破烂小摊，放进 B-08 门洞）+ `shop1_exec_B`（净跨豪华大店，放 B-08~B-09 净跨）；门禁已过，测法与风险见 `EXEC_ATTEMPT.md`。


**交付门禁（重申）**：`lt_root` + `lt_tree` + `lt_geom`（含可变形盒时）**三项全过**才能交付。**单文件最大实测约 1MB 可用，更大未测；不设上限，首个大文件导入时顺带观察**。

**给设计方（Claude）的接续说明**：新会话先读**最新 SHA 的** HANDOFF → NOTES → DESIGN → PLAN → FILES；用户每轮会转发 agent 报告和完整 SHA；**设计方说法若与仓库结论矛盾，以仓库为准**，回仓库核对。

**用户协作习惯**：截图数量有限 → 测试压缩到 **2~3 张**并写明拍摄角度，给回报模板；agent 联网搜索 **401（待用户换 key）**，期间只直接抓指定 URL。
- **执行 agent 的上下文由用户管理**。**"上下文快满就停手"只是设计方自己的规则**；执行 agent **只在 push 失败时停下**。
- **用户回报以截图为主**；**设计方只追问图里看不出来的东西**。
- **2026-10-07 试过 GPT-6 Luna（免费档）**：中途中断，留下**半成品 `lt_geom`**（含空壳 `check_shared_edges`），后来已 `git checkout` 恢复。**结论：免费额度扛不住长任务** —— 以后再试就用**付费 API**，并且**先用短任务试探**。执行 agent 目前仍是 **NVIDIA NIM 上的 DeepSeek**；速度慢的原因是**免费档约 40 RPM 的限速**。
- **接手的执行者如果没有记忆，开场必须清点现场**：`git status` / `git diff`，**先把半成品存成补丁**（`git diff > xxx.patch`，不入库），再决定保留还是恢复。**这次处理 Luna 的流程可以当模板**。

## 6. 待用户实测：B-08~B-09 桥下大店 / B-08 门洞小摊（下一轮任务书给出）
放置：全程潜行；先放灯/门等小件，再放 bridge2_body.txt，全部点同一格（城东 x≈-600、z≈300、y=4）。
每个新件必报：靠近卡不卡、chunk updates 跳不跳。


## 7. 附属评估（ALET / Little Opener）

**ALET = A Little Extra Tiles（候选，未安装）**
- 来源：用户给的三个 URL 之一（Modrinth 项目 `NWquC4YJ` / slug `a-little-extra-tiles`）⇒ 机器可读视图：**`game_versions: ["1.12.2"]`、loader `forge`、当前版本 `1.0.23`、共 18 个已发布版本、许可 LGPL-3.0-only、下载 15397**
- **要求的 LT/CC 版本**（官方 README 正文原文）："The current version of A Little Extra Tiles (ALET) 1.0.23 is compatible with **CreativeCore_v1.10.70** and **LittleTiles_v1.5.58_mc1.12.2**" ⇒ 比我们当前（**1.5.87 + 1.10.71**）**旧**；向上兼容性 **❓未验证**
- 它做什么：**Photo Importer**（图片→LittleTiles 结构，默认上限 **98×98**）、**Typewriter**（文字/字体→结构）、**Tape Measure**（测距，最多 10 组）、以及**新增结构类型（new structure types）**
- ⚠️ **卸载后会不会坏**：README 明确写它 "adds … **new structure types**" ⇒ 一旦生成的结构引用了 ALET 自己的结构类型，**卸载 ALET 后大概率失效/报错**（原版找不到该 id）；图片/文字导入本身产出的应主要是普通 tile（原版/FCB 方块），但**"到底用了哪种结构类型"在不安装的情况下无法确认** ⇒ 标记为**推断 + ❓**
- **抓取情况（如实回报）**：用户给的三个 URL → Modrinth 页面本体是 JS 渲染（只回标题）、CurseForge 页面 **403 Cloudflare**（"Just a moment..."）、GitHub 页面只回导航壳、`raw.githubusercontent` 拉取失败。上述结论数据来自**同三个资源的机器可读视图**（Modrinth API + 官方 README 正文），已注明来源。
- **建议**：**先不动**。要用的话必须①先备份存档；②只用于"生成纹理/文字这类纯 tile"的活；③**不要把 ALET 的结构类型嵌进主体建筑**；等出现 1.5.87 兼容声明再考虑批量用。

**Little Opener：不再需要** —— `/lt-open`（可用命令方块跑）+ 1.5.87 信号系统（门 `state` 输出 → `activate(SIGNAL)`，见 §4e）已覆盖"远程开关门"，不引入额外前置。
