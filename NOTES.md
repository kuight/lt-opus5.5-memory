# LittleTiles 1.12.2 建筑项目备忘

## 环境
- MC 1.12.2 Forge；**当前** LittleTiles 1.5.87 + CreativeCore 1.10.71；**旧线** pre199_19 + CC 1.10.10。另有 FlatColoredBlocks、WorldEdit
- 存档：超平坦；工作目录 E:\work\建筑\
- 执行 agent：DeepSeek harness 上的 DeepSeek V4.1 Flash；每次会话先写 probe.txt 并用 dir 确认
- 脚本必须在 E:\work\建筑\ 下运行（lt_colors.py 用相对路径读 CSV）
- 游戏已实跑 LittleTiles 1.5.87 + CreativeCore 1.10.71（2026-10-05 用户启用，旧存档已备份，旧建筑和旧机关正常）

## 已验证结论（改动前必须遵守）
1. 蓝图文本：坐标 [I;x1,y1,z1,x2,y2,z2]，单位 1/16 格；单盒用 bBox，多盒用 boxes；数据值写 "minecraft:wool:14"
2. 输入框上限 256 字符，大蓝图一律走 Little Importer 剪贴板导入
3. **根有 children 就必须有 structure**（用 fixed 包一层），否则导入时不会建立父子连接，按钮静默失效。由 lt_root.py 强制检查
4. 穿透结构 id = noclip，web:0b 表示不减速（默认 1b 会像蛛网一样减速）
5. 高级门有 6 个通道 rotX/rotY/rotZ/offX/offY/offZ；旋转单位是度，位移单位是 1/offGrid 格，时间单位是 tick
   - 写了 offX/Y/Z 就必须同时写 offGrid，否则位移被静默忽略
   - hermite 关键帧格式：[3,2,起点,值,终点,值,...,1,0,0]
   - rotZ +90：+X→+Y；rotY +90：+X→−Z
6. doorActivator 的 activate:[I;n] 指向 children 下标；门设 disableRightClick:1b 后按钮仍能打开（已在游戏中验证）
7. 子结构可以独立运作；方式 a 破坏会整个拆掉，方式 b 按小方块逐个破坏
8. 材质：1/16 宽的细线和指示灯用 FCB 平滑色块；**大面材质 = FCB 纯色**（2026-10-06 定案）；玻璃统一用淡青半透明 FCB；做旧拼色已否决。
   ※ 石英贴图**每 1 格重复**，会暴露 1 米网格 ⇒ 只用于**小面积收边**。（H5 拍摄时在背光面偏深，"是否中灰"下次朝阳时再确认。）
9. 招牌要从外面看是正向，渲染中文时 MIRROR 要按朝向确认
10. 尺度：1 格 = 1 米；店铺层高 5~6 格，门高 2.5~3 格，柜台 15~16px，楼梯 8px
11. 已退役，见第 23 条。
12. 门动画不能循环；AnimationEvent 只有 child（childId）和 sound-event（sound/volume/pitch/opening）；
    child 事件只能向下触发直系子门，doorActivator 可被触发；light 结构见 HANDOFF §4。
    长动画方案：一次触发、按 tick 级联子门。
13. pre199 有 /lt-open <x> <y> <z> [结构名...]（OP 权限 2，坐标为绝对坐标，结构名可选、用于过滤）；
    player=null，不受 disableRightClick 限制；循环 = 命令方块 + 时钟反复触发。
    duration 无上限（GUI 的 500 只是滑块范围）；rot 可超过 360，会被拆成多个半圈插值；子结构随父结构一起动。
    pre199 不读红石。本地已启用 1.5.87 + CreativeCore 1.10.71，1.5.87 才有 light/信号/粒子。
14. 1.5.87 有信号转换器 BlockSignalConverter（红石⇄信号互转，源码确认，未实测）。
15. **手写 schematic 的根 TAG_Compound 名字必须写 `Schematic`**（gzip 解压后前 12 字节 = `0A 00 09 53 63 68 65 6D 61 74 69 63`），名字写成空串会被 WE 6.1.10 拒绝：`Tag 'Schematic' does not exist or is not first`；且必须是 **gzip 流（魔数 1f 8b）**，不能是 zlib 裸流。校验工具：`lt_verify_schem.py`（独立读取器，不复用写出代码）。
16. **生成器禁止用正则盲改 int 数组**（2026-10-06 血的教训）。`[I;…]` 在蓝图文本里有三种身份：①盒子坐标（6）②可变形盒（7/11）③**非坐标数组**（`axisCenter` 7 个、`animation` 时间轴 8+ 个）。任何"扫所有 `[I;…]` 就加偏移"的做法都会毁掉 ③ → 时间轴首元素被加成 224 ⇒ 游戏里放置时 `ValueTimeline.getType(224)` 抛 `RuntimeException: Invalid id 224`（**直接崩客户端**）。合规做法：**只对 tiles 段做平移**（该段只允许 6/7/11，`lt_probe187.shift_tiles` 带断言），结构文本一律不碰；取盒子也必须在 `bBox:`/`boxes:` 位置取（不能按分量数猜）。另注：`lt_np.Vol.export` 会把坐标归一化到内容最小角所在的格（`lt_np.py:24/41`），所以"生成在最终坐标"必须补这一层 tiles 级平移才能与结构里的 axisCenter 对齐。

## 用户审美偏好
- 要极致细节，全程用小方块，不要火柴盒式的造型
- 细节要能看懂、有内涵；乱堆招牌、伪汉字是减分项
- 一步一步做大，先做样板再铺开
- 看得见、按理能交互的东西都要能交互（门、柜、箱盖、井盖、座椅等）
- 街道和店面不允许重复、千篇一律，不要让人审美疲劳；每一处都要经得起细看
- 不做积水（用户自己开雨和光影）
- 赛博朋克味要贯穿侧墙、路面，而不只是门面
- 用户觉得分段做、做得少就是敷衍：每一轮都要拿出足够的量和细节
- **用户否决"外圈低精城市海"**：低精部分会拉低整体精度感，要求"整座城都是小方块"的观感（见 DESIGN.md【精度原则】）
- 风格偏科幻、高科技；赛博朋克的“旧/乱”用改装、外露线缆、维修痕迹表现，不用日常市井物件（消防栓、共享单车、普通垃圾桶等否决）
- 1.5.87 新光照渲染更有科幻感，保持；用户吐槽“模块化堆砌感、缺曲线斜面过渡微雕、功能贴近现在” → 设计规则 R1~R8 见 DESIGN.md

## 当前进度
- 旧拉面店与 v1 街道已随 **mass_v0 粘贴清除**（用户同意不备份）。
- **当前阶段 = 几何与机关基础件验证**：曲面墙 **H4/H5 待修+待测**（残余锯齿未清零）、**scale_B 帧率已降级**（静止高、移动/转身卡，暂不排查）。
- 之后：**合成蛋白面馆设计稿**（第一栋精细建筑，用来定**中式科幻设计语言**）→ 定**全城细节密度标准** → **体块 v1**（按 DESIGN「高度感与体块 v1 方向」）。

## 测试记录
- 2026-10-05 mech A（v3+fixed）：按钮能开，右键门打不开 ✔
- 2026-10-05（1.5.87 实测）：旧蓝图能导入，/lt-open 可用，mech 机关都能动
- 卷帘门：按钮能开，但关不上（门是 disableRightClick:1b）
- loop_fan：开 0→360 顺时针，关时倒放成逆时针；回到原位时闪一下并有放置方块的声音
- 导入后发光变弱或不亮（待查）；新版光照渲染变了，用户觉得更有科幻感
- light、message 结构能用；particle 还没测
- **2026-10-06 用户实测第二批（原话）**：
  - H：仍有台阶感，离远了条纹更怪
  - D：周围亮，亮度 15 ✔
  - C（stayAnimated:1b）：不闪、无声 ✔
  - A：黑色粒子，圆弧形上升；B：白色粒子，水平移动
  - J：右键开、再按关 ✔，但仍闪且有放置声
  - E、F、F10：灯完全不亮，F10 帧率无变化
- **2026-10-06 用户实测第三批（原话）**：E2 **门和灯同步 ✔**；J2 **不闪、无声 ✔**；F2 会自己一亮一灭、**周期不到 1 秒**、能停，但**不是一右键马上停**，要等当前这次亮灭做完才停；F2x10 十盏同时开或关时**掉一下帧（几十帧）**，平时体感不明显；**H3（旧版、角向外偏移）形状扭曲、有"反过来"的感觉**（印证第 25 条）；density_test 贴近 **50fps**、10 格外 **70**、平时 70~80。
- F2"停止有延迟"的原因：**输出条件排队后无法取消** —— 排程用的是普通队列 `SignalTicker.java:27/32-33`（`List<SignalScheduleTicket>`，搜不到 cancel/remove 取消路径），而 `InternalSignalOutput.update():90-108` 每次只把**新的**状态 `handler.schedule(outputState)` 入队 ⇒ 总开关关掉时**已排队的那次翻转仍会到期执行**，所以必须等当前这次亮/灭走完。（高置信推断，未通读 ticker 全部代码）
- **2026-10-06 用户实测第四批（原话）**：**H2b/H3b：每格一块歪斜的平行四边形 + 三角形明暗，整面墙像鳞片并且往一边倒，曲面没做成**；H3b 显示**近乎黑色**。
- **2026-10-06 用户实测第五批（原话）**：
  - **H4/H5 弧墙**：平视时**台阶消失**，比纯小方块阶梯好很多；但**俯视时墙顶有一整排三角形锯齿**（用户截图），并不平滑。
  - **大面材质定为 FCB 纯色**（第 8 条已改）；石英贴图每 1 格重复会暴露 1 米网格，只用于小面积收边；H5 拍摄在背光面偏深，是否中灰下次朝阳再确认。
  - **scale_A vs scale_B**：2 格距离上 **45° 倒角几乎看不出来**；看着"模块化"的原因是 ①板块尺寸一样 ②铆钉等距排满成了花纹 ③只有框和板两层深度；**暗板颜色太黑太闷**。
  - **帧率**：**移动和转身时卡、站着不动时高，忽高忽低，没有稳定数值**。
- **光影对帧率的影响（重要结论）**：开光影时贴近 **50fps**；**关光影时贴近 100+** ⇒ **小方块密度不是瓶颈，帧率主要被光影吃掉**。以后测帧率**一律记"开光影 / 关光影"两个数**。
- 旧蓝图导入后发光弱/不亮，但原先放着的旧建筑亮度正常（已确认，见第 23 条）
- **2026-10-06 probe_187 放置崩溃**，原因：**我自己排版脚本的 `trans()` 盲扫所有 `[I;…]` 数组、把 `animation.rotY` 时间轴也当坐标平移了** → `[I;0,2,0,0,0,20,…]` 被改成 `[I;224,4,0,…]`，`ValueTimeline.read` 拿 `array[0]=224` 去 `getType` → `java.lang.RuntimeException: Invalid id 224`（Client thread、**放置时**、`LittleAdvancedDoor.loadFromNBTExtra:198`）。触发样品 = **E**（唯一走"整节点平移"分支的样品）；其余 8 个样品的结构文本未被平移、时间轴首元素仍为 0 ✓。同类缺陷共 3 处（`trans()` / `lt_probe187` 的包围盒 / `lt_probe_split` 的 `boxes_of`），已全部定位，修法见 HANDOFF §4☆。
- **G 结果（2026-10-06）**：在原先放着的**旧发光小方块**旁边放置/破坏方块后，该格光照被重算并**变暗**；小方块外观仍然发光，但**不再照亮周围方块**（已确认，见第 23 条）。

## 1.5.87 基线核对（源码只读核对，未改代码；行号取自 lt_src_187）
| NOTES 条目 | 1.5.87 | 证据 |
|---|---|---|
| 1 蓝图文本（[I;…] / bBox / boxes / "block:meta"，单位 1/16 格） | ✔ | `LittleTile.java:316/354/374-380`、`LittlePreview.java:266/275-279`、`LittlePreviews.java:395` |
| 1 grid 默认 16 | ✔ | `LittleTilesConfig.java:111`、`LittleTiles.java:228`、`LittleGridContext.java:21` |
| 3 根有 children 就必须有 structure | ✔（机制同，调用点搬到 Placement） | `Placement.java:230-235`（仅 origin.isStructure() 才 notifyStructurePlaced）、`:236` + `:264-273` updateRelations（父子双方 getStructure() 非空才建连接） |
| 4 noclip web:0b 不减速 | ✔ | `LittleNoClipStructure.java:33`（默认 true）/`:41/46` |
| 5 高级门 6 通道（rot/off）+ 位移换算 offGrid | ✔ | `LittleAdvancedDoor.java:248-264`、`:168-169/197-198/219-220` |
| 5 写 offX/Y/Z 就必须写 offGrid | ✔ | `LittleAdvancedDoor.java:248-252`：有 `if(offX!=null)` 守卫，但守卫内直接解引用 `offGrid` → 缺 offGrid 会在此处出错（pre199 记的是"静默忽略"，实际现象待实测） |
| 5 关键帧格式与插值表（linear/cosine/cubic/hermite） | ✔ | `ValueTimeline.java:17/167-168/225-228/347-350` |
| 6 doorActivator activate:[I;n] → children 下标 | ✔ | `LittleDoorActivator.java:55/62` |
| 6 门禁只挡右键、按钮仍能开 | ✔ | `LittleDoor.java:68`（仅 RIGHTCLICK 路径检查）、`LittleDoorActivator.java:221` |
| 12 门动画不能循环 | ✔ | `AnimationGuiHandler.java:31/68-71/118`（loop 仅 GUI 预览） |
| 12 AnimationEvent 只有 child / sound-event | ✔ | `AnimationEvent.java:170/208` |
| 12「没有 light 结构」 | **✘** | `LittleStructureRegistry.java:153`（1.5.87 有 light，带 enabled 输出） |

**蓝图格式改动点（只列，不改代码）**
- 新增结构 id：light / message / item_holder / particle_emitter / blankomatic / single_cable1|4|16 / single_input1|4|16 / single_output1|4|16 / signal_display_16 / structure_builder（`LittleStructureRegistry.java:153-155`、`LittleDoorBase.java:313-316`、`LittleStructurePremade.java:170-185`）
- 结构类型新增**命名输入/输出端口**（`LittleStructureType.java:82/87`）：各门新增 output `state`；noclip 新增 input `players`/`entities`
- 结构 NBT 新增：内部输出＝以**端口名为键的 COMPOUND**（`state`/`con`/`mode`/`delay`，`LittleStructure.java:650` 写、`:578` 读）；内部输入＝以端口名为键的 **int**（`InternalSignalInput.java:36`）；外部输出处理器＝**`signal` TAG_LIST**（`LittleStructure.java:636-641`、`:556-568`）
- 旧格式兼容仍在：`LittlePreview.java:73-74`（bBoxminX）、`LittlePreviews.java:411-413`（紧凑 tiles 整数分支）

**信号/自激（源码级结论）**
- 目标表达式：`a<n>`=本结构内部输入、`b<n>`=本结构内部输出、`i<n>`/`o<n>`=外部输入/输出（指向子结构 single_input/single_output）、`c<n>.…`=下钻子结构、`p.…`=父结构、`d<n>`=索引变量（`SignalTarget.java:19-81`；`SignalUtils.java:16-72`；`SignalTargetParent.java:382-392`；`SignalTargetNested.java:435`）
- **能自激**：输出条件 `con` 可引用自身输出 `b<n>`；`SignalInputCondition.calculateDelay()`（`:135/243/275`）保证反馈 ≥1 tick，`InternalSignalOutput.load():64-66` 用 `max(ceil(calculateDelay()), delay)` 抬高延迟 → 可做无外部触发的振荡（稳定性待游戏内实测）
- 周期性：`SignalMode.PULSE`（delay+length）+ `SignalTicker` 调度（`SignalMode.java:152/678-736`、`SignalTicker.java:25`）
- **1.5.87 新增红石转换方块**：`BlockSignalConverter.java:11/95`、`TESignalConverter.java:33`（pre199 完全没有红石代码）

17. **门动画会把它的 children 一起搬进动画实体**：`LittleDoorBase.java:222-223`（`new EntityAnimation(...)` 之后 `newDoor.transferChildrenToAnimation(animation)`），子连接被换成 `StructureChildToSubWorldConnection`（`StructureChildToSubWorldConnection.java:19-46`：世界取 `animation.fakeWorld`、`isLinkToAnotherWorld()=true`）；门的 tiles 也放进 `SubWorld.createFakeWorld`（`:253-259`）并从原 TE `remove()`（`:265-270`）。⇒ **"门为父、灯为子" ⇒ 灯被搬走 ⇒ 世界里完全不亮**（E/F/F10 实测"灯完全不亮"的根因）。反过来 **"灯/控制器为父、门为子" 则灯留在世界**（J 能联动成功）。
18. **C（stayAnimated:1b）实测不闪、无声** ✔ ⇒ 旋转/位移门用 `stayAnimated:1b` 可消除"回到方块"那一下闪烁与放置声（`DoorController.java:146-150` 的 `place()`）。
19. `/lt-open` 走 **`DoorActivator.COMMAND`**（`OpenCommand.java:82`）→ `LittleDoor.activate`（`:95` 翻转 `opened`；`:96-98` **非 SIGNAL** 时 `getOutput(0).toggle()`）⇒ `getOutput(0)` 就是 `state`，**会被 toggle**（SIGNAL 触发时不 toggle，避免自激）。
20. **信号可以写兄弟节点**：`SignalTarget.parseTarget` 是递归的（`:61-67` 处理 `c<n>.`、`:68-73` 处理 `p.`）⇒ `p.c1.b0` 合法（= 父结构第 1 个子节点的内部输出 0）。
21. **particle_emitter 的速度在 facing 局部系里**：`LittleParticleEmitter.java:111-138`（`speed = spread.generate()`，再按 facing 旋转 pos/speed；`:145-148` 在动画世界里还会转到世界系）。`EnumFacing` 序 = DOWN,UP,NORTH,SOUTH,WEST,EAST ⇒ **`facing:4` 是 WEST**，想竖直上升要 **`facing:1`(UP)**。解释实测：A 的扁平键被忽略 → 走 **SMOKE 预设**（黑 + 环形扩散 = 黑色圆弧上升）；B 的 `settings` 生效（`color:-1` = 白），但 facing=WEST 把 +Y 转成水平 ⇒ 白色水平移动。
22. **K 解码（187 原生可变形盒）**：数组 = `[x1,y1,z1,x2,y2,z2, indicator, word…]`。`indicator`：bit31 = 可变形标记（所以 `LittleBox.createBox:1127-1129` 用 `array[6] < 0` 判分支）；bits24-29 = 六面 `flipped`（`LittleTransformableBox.java:228-244`）；**bits0-23 = `bit(i*3+a)` 标记"角 i 的轴 a 存了偏移"**（`:274-285`）。`word`：每 2 个 16-bit 有符号 short 打包进一个 int（偶索引取高 16、奇索引取低 16，`:251-263`）；偏移含义 = 该角该轴坐标 = **基础角坐标 + 偏移**（`:860`）。角序 = `EUN,EUS,EDN,EDS,WUN,WUS,WDN,WDS`（`cc_src/com/creativemd/creativecore/common/utils/math/box/BoxUtils.java:221-229`）。K 样本 `[2,0,0,14,7,11,-2147418096,-393223]` ⇒ indicator `0x80010010`（bit4=(角1,Y)、bit16=(角5,Y)）+ word `0xFFF9FFF9`（高/低 16 都是 −7）⇒ **角 EUS（槽0）与 角5 WUS（槽1）的 Y 各 −7px**（是 **Y** 轴，不是别的轴——2026-10-06 笔误更正）。工具：`lt_tbox.py`（decode/encode，**对 K 往返逐位一致 ✔**）。

23. **FCB 发光小方块 = 只发光不照明、不漏光**（2026-10-06 用户截图确认：FCB 发光细条贴墙，**墙面未被照亮**）⇒ **照明一律用 `light` 结构**；`lt_ramen.py` 的 **LEAKFIX 退役**（代码先保留，但**不再要求漏光检查**）。旁证：1.5.87 对小方块自发光做体积加权（`*= getPercentVolume`），1px 级亮度≈1。
24. facing 序 = DOWN0 UP1 NORTH2 SOUTH3 WEST4 EAST5；粒子默认 `facing:1`。
25. **可变形盒的角偏移"越出声明 AABB"有风险**：`LittleTransformableBox.setBounds(:1596-1623)` 会把几何包围盒**夹回**声明范围（`minX = max(minX, oldMinX)`、`maxX = min(maxX, oldMaxX)`）；保存时 6 坐标就是该 AABB（`:481-490`），`getBox` 也只按 AABB 建碰撞盒（`:216-221`）⇒ 面可能画到 AABB 外，而**记账/按格切分/碰撞只认 AABB** ⇒ 不一致。**规则：角偏移只写"向内或 0"**（`lt_tree` 已加检查，越界报 `[问题]`）。H2/H3（有 +1/-1/-8 等向外偏移）现已被标为问题，改用 **H2b/H3b**。
26. **水平方向不拆**：整段四边形（H6 已实测，墙顶平滑）；按格裁切的 H4c 实测**错位缺片**，**禁用**。跨格时只按高度分段。

## 2026-10-06 设计方对话归档（本轮新增，全部入库）

### 测试记录追加（用户原话）
- **I2（30° 原生 8 分量斜坡，1 盒）：没问题 ✔** ⇒ 已验证结论新增：**原生 8 分量可变形盒可用**（K 格式，`lt_tbox` 生成）。
- **scale_B（609 盒，无可变形盒）：开光影贴近约 20fps，关光影约 40fps** —— 比 density_test（开 50 / 关 100+）**还卡**，但盒子密度更低（约 **2.4 盒/格**，density_test 约 **5.4**）⇒ **疑点不在墙本身，待排查（见 HANDOFF §5）**。用户原话："之前会话做了很多完全由小方块搭建的建筑都没这么卡。"
- **mass_v0 体块（用户看图 3）**：视距不拉大还好，拉大了感觉也就那样。

### 审美 / 设计偏好追加（用户意见）
- **中式 × 未来是用户主动提出的，认为更酷**；下层川渝吊脚楼市井、上层官式斗拱飞檐；配色 **朱砂红 / 鎏金 / 石青 / 冷白** —— 用户已同意。
- 规模**起码 100×100**；**60 格太矮，要多层次**（参考重庆）；城市要"**活**"，建筑之间要有关联（线缆、轨道等）。
- **精细与宏大要兼得**。
- 用户批评设计出的未来产物**不够未来**，要求**多学习科幻作品**（三体、星际穿越等）。
- **【硬约束】设计任何建筑/功能/物件之前，必须搜索学习相关资料**（科幻作品、建筑案例、工程原理），尽量贴合设计目标，**设计稿里写明参考来源**。
- 吐槽原文：强烈的"**模块化**"与"**堆砌感**"——凑近看主体依然是方块垂直堆叠，**缺乏异形曲线、斜面过渡和微雕细节**；功能过于贴近目前的生活，**没有未来感**。
- **曲面**：1/16 素体阶梯在任何距离都有台阶感，远看合并拼缝成条纹更怪 ⇒ **曲面一律用可变形盒做"多边形切面"**（像舰船外壳那种有意的棱面），**禁用素体阶梯**。

### 规则 / 经验追加
- **帧率规则（2026-10-06 改）**：**不再报具体 fps**，只描述"**静止时高不高 / 移动转身卡不卡**"——实测数值忽高忽低、没有稳定值；光影仍是主要影响因素（开/关光影的差异依然记录）。
- **闪烁候选规则（未测）**：只需要"看起来闪"的地方，用 **FCB 发光小块常亮 + 小门/遮板动画开合**，避免 light 翻转触发光照重算；真正要照明才用 light 并错开相位。注意：**大量 stayAnimated 动画实体本身的开销未测**。
- **细节手法（设计方评审 density_test 得出）**：细节靠**深度层次**（面板不同凹凸深度、检修舱位内凹、管线压进槽里），不要只在平面上画分缝；**铆钉不要均匀铺满**（像噪点），只放在**受力点/接缝处**；**45° 倒角是消除方块感的主要手段**。

## 写入不稳定问题（2026-10-07 查清，结论：不是路径问题）
- **对照测试**：写文件工具分别写 `E:\work\建筑\_wtest1.txt`（中文路径）/ `E:\work\lt-memory\_wtest2.txt` / `E:\work\ascii_test\_wtest3.txt` —— **三个全部落盘** ✓ ⇒ **中文路径没问题**，**不需要建 junction** ✗（测试文件已删）。
- **真正原因两条**：① 我在前面几轮用 `Remove-Item "_*"` / `tmp_*` **自己删掉了那些临时脚本**（`_diag_h4.py` 一直健在 ✓）；② 有几次是**把"写文件"和"验证"放在同一条消息里**，两个调用并发执行 → 验证先跑、看不到刚写的文件 ✓✓（`lt_geom_luna.py`、`tmp_chk.py` 都是这种）。
- **规避规则（重要）**：**写文件与验证必须分两条消息**；批量改脚本时用"同一条命令里 python 改写 + 立刻校验"的方式（本轮全程验证有效 ✓）。
- **附带证据**：`E:\work` 下同时存在 `末日狂徒优化记录` 与乱码目录 `鏈棩鐙傚緬浼樺寲璁板綍`（UTF-8 字节被按 GBK 解释）⇒ 历史上确有某些调用用错代码页建过目录（该乱码目录**是空的**，与本轮丢文件无关）；**建议**：新建中文目录不要在错误代码页下用 cmd/PS 建 ✓。

## H4 弧墙本轮结论（2026-10-07）
- **诊断**（不靠肉眼）：修复前 208 盒里 **160 盒**角点越出环带；根因 = `prism` 的"只向内"写成**对所有角一律 `min(0, delta)`** ✗（min 侧向内应为正）⇒ 内弧被啃进去、顶面露出三角缺口。
- **修复后数字（唯一可信一组，probe_H4，sha256 `095D454A…`、12524 B）**：**208 盒 / 越界 8 盒 = 32 角点（口径 C 实测 角点/盒 = 4.0 ✓ 两个数字自洽）/ 最大偏差 2.35px / 平均 0.40px**。
- **两版新弧墙（参数同 H4：R=8 格、壳厚 2px、1/4 圆、16 段、高 4 格、FCB 浅灰 `flatcoloredblock80:7`）**：
  | 版本 | 盒数 | 字节 | 越界角点 | 共享边问题 | 最大/平均偏差 | 判定 |
  |---|---|---|---|---|---|---|
  | **probe_H4c**（按格裁切 + 环带吸附） | 208 | 12525 | 0 ✓ | 0 ✓ | **2.35 / 0.40 px** ✗ | **不合格** |
  | **probe_H6**（整段四边形、共享整点顶点、不按格裁切） | **64** | 3727 | 0 ✓ | 0 ✓ | **1.36 / 0.41 px** ✗ | **不合格（只差偏差一项）** |
  | **probe_H5m**（= H6 做法 + FCB 中灰 `80:3`） | 64 | 3728 | 0 ✓ | 0 ✓ | 1.36 / 0.41 px ✗ | 同上 |
- **卡点判断**：整数角点**无法贴合真圆**——吸附到整点必然带来 ≤0.7px 的径向误差，16 段的弦高差再叠加 0.15px，所以**"最大偏差 ≤1px"这个门槛对整数网格弧墙偏严**；H6 已经比 H4c 好 1px（且盒数只有 1/3、无缝、共享边检查 0 条 ✓）。**请设计方定**：是放宽到 ≤1.5px、还是改用更细网格/允许非整数角(需要另想办法)、还是接受 H6 + 加厚壳到 3~4px 让误差相对减小。
- `lt_geom` 本轮已补：**纯边界距离度量**（能测出弦-弧差，不再出现假的 0.00）、**角点环带检查**、**`check_shared_edges`**（同竖线上高度段首尾相接 + 相邻盒竖线必须完全重合；同段去重避免误报 ✓）。

27. **可变形盒斜面贴地时会出"对齐格线的硬边暗块"**（2026-10-07 用户实测）：H6/H5m 最下面一格有偏深竖长方形暗块、边界对齐方块格线，开不开光影都有；**关平滑光照→消失**，**悬空放置→也消失**。成因（源码）：LT 的平滑光照走 Forge 的 vanilla AO 管线（`RenderingThread.java:254-286` → `cc_src/.../CreativeModelPipeline.java:86-118`）：`:86-94` 反射构造原版 `BlockModelRenderer$AmbientOcclusionFace`（该类还被 LT coremod 改写，`LittleTilesTransformer.java:412-419`），`:109-116` 用 vanilla `VertexLighterSmoothAo` 并 `setWorld/setState/setBlockPos(pos)/updateBlockInfo()`（**按方块位置 + 按面朝向**取 AO），并强制"非满块"。⇒ 可变形盒**跨格时每格各自算一次 AO**、相邻格之间不混合 ⇒ 贴地处由地面方块产生的遮蔽变成**硬边暗块**。
28. **更细网格**：grid 尺寸表由 `LittleGridContext.loadGrid(min, defaultGrid, scale, multiplier)`（`LittleGridContext.java:35-50`）生成，尺寸序列 = `min × multiplier^n`（n < scale）；`get(int)`（`:61-70`）**只认表内尺寸，否则抛异常**；蓝图 `grid` 键经 `get(NBTTagCompound)`（`:76-81`）读取，缺省回落 16（`:83-87` getOverall）。默认 `defaultSize = 16`（`LittleTilesConfig.java:111`、`LittleTiles.java:228` 配置范围 1..MAX）。⇒ **1/32 只要配置表里有 32 就能用**（如 min=1, multiplier=2, scale≥6）；**可变形盒的角偏移是 grid 单位的 short** ⇒ 网格变细后偏移自动变细；**与 1/16 混放由 LT 的上下文转换支持**（`LittleActionPlaceAbsolute.java:129/175`、`LittleActionSaw.java:70/93`、`LittleActionDestroyBoxes.java:162/223` 都在比较 `context.size` 后转换）。
- **门槛调整（2026-10-07 设计方定）**：整数网格弧墙的弧面偏差门槛改为 **≤1.5px**，最终以**游戏观感**为准 ⇒ **H6 / H5m 达标 ✓**。
- **H6 的 1.36px 出现在哪**：细化采样（4 万点）实测 **最大 1.474px**，位置 = **角度 44.33°（第 7 段、段内 88%）内弧**，盒 #28 `[89,0,80,99,16,91]`，其角偏移达 **±8/9px** ⇒ **薄片在"最近顶点映射"上配错**（把面拉歪）；误差构成 = 弦高差 **0.154px**（16 段 R=128 的理论值）+ 顶点吸附 ≤0.7px + **该薄片的映射错配**（主因，最大 ~1.3px）。
- **H7 / H7b（墙基方案）**：H6 弧墙 + 沿弧线、外凸 2px 的正交墙基（深色 FCB **`flatcoloredblocks:flatcoloredblock80:1`**），墙基高 **4px**(H7) / **16px**(H7b)，弧墙从墙基顶面起。两份**三项门禁全过** ✓（80 盒、4708/4741 B、最大偏差 1.36px）。等用户实测哪个高度能消掉/减轻墙根暗块。
## 操作记录
- **mass_v0 体块粘贴法**（原先写在 HANDOFF §6，本轮移到此处）：把 `mass_v0.schematic` 放进 `.minecraft/config/worldedit/schematics/` → 游戏内 `//schem load mass_v0` → `//paste -o`；若报方块数超限先 `//limit -1`。⚠ **会清空 x -800~-701、z 300~399、y3~255 内的一切**（旧 v1 建筑随之清除，用户已同意不备份）。

## 蓝图体积规则（2026-10-06 起，硬性）
- **Little Importer 单次导入 ≥1MB 已实测可用**（早前会话验证）。
- **单个蓝图 ≤ 1MB**；建筑**按模块拆分导入**（外壳 / 门面 / 内饰 / 机关），**每个模块一个文件**。
- **生成器导出时必须打印字节数**：> **900KB 报警告**，> **1MB 报问题并拒绝交付**（配合"任何文件没过 lt_root + lt_tree + 几何自检一律不交付"）。

## 机关标准写法（2026-10-06 起）
- **控制器模式**：根 `fixed` → **控制器 `light`(level:0，右键 toggle)** → 门 / 灯 / 粒子**全部作为它的兄弟子结构**，各自 `con` 引用 `p.b0`（= 控制器的 `enabled`）。**灯永远不能挂在门下面**（门动画会把 children 搬进动画假世界 ⇒ 灯不亮，见第 17 条）。
- **门默认 `stayAnimated:1b`**（起点必须"对齐"：旋转 360 的整数倍、位移 0，见第 18 条与 §3.5），否则关门结束会把方块放回去 ⇒ 闪一下 + 放置声。
- **自激闪烁**：`con:"!b0&p.b0"` + `delay`（`b0`=自己、`p.b0`=控制器）；会闪的 light **少用 + 相位错开**（`blink(level, delay, phase)` 用不同 delay 错开相位），因为每次翻转都会重算光照 → 掉帧。
- **闪烁候选规则（未测）**：只需要"看起来闪"的地方，用 **FCB 发光小块常亮 + 小门/遮板动画开合**，避免 light 翻转触发光照重算；真正要照明才用 light 并错开相位（大量 stayAnimated 动画实体本身的开销未测）。