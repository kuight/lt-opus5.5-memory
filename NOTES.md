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
8. 材质：1/16 宽的细线和指示灯用 FCB 平滑色块；超过半格宽的面用原版材质（石英效果最好）；玻璃统一用淡青半透明 FCB；做旧拼色已否决
9. 招牌要从外面看是正向，渲染中文时 MIRROR 要按朝向确认
10. 尺度：1 格 = 1 米；店铺层高 5~6 格，门高 2.5~3 格，柜台 15~16px，楼梯 8px
11. 光照按整格计算，LittleTiles 不挡光：墙外发光件会照亮同格/邻格墙内侧。离室内 ≤2 格的装饰灯一律用同色不发光色块（假灯），由漏光检查自动处理。
12. 门动画不能循环；AnimationEvent 只有 child（childId）和 sound-event（sound/volume/pitch/opening）；
    child 事件只能向下触发直系子门，doorActivator 可被触发；light 结构见 HANDOFF §4。
    长动画方案：一次触发、按 tick 级联子门。
13. pre199 有 /lt-open <x> <y> <z> [结构名...]（OP 权限 2，坐标为绝对坐标，结构名可选、用于过滤）；
    player=null，不受 disableRightClick 限制；循环 = 命令方块 + 时钟反复触发。
    duration 无上限（GUI 的 500 只是滑块范围）；rot 可超过 360，会被拆成多个半圈插值；子结构随父结构一起动。
    pre199 不读红石。本地已启用 1.5.87 + CreativeCore 1.10.71，1.5.87 才有 light/信号/粒子。
14. 1.5.87 有信号转换器 BlockSignalConverter（红石⇄信号互转，源码确认，未实测）。
15. **手写 schematic 的根 TAG_Compound 名字必须写 `Schematic`**（gzip 解压后前 12 字节 = `0A 00 09 53 63 68 65 6D 61 74 69 63`），名字写成空串会被 WE 6.1.10 拒绝：`Tag 'Schematic' does not exist or is not first`；且必须是 **gzip 流（魔数 1f 8b）**，不能是 zlib 裸流。校验工具：`lt_verify_schem.py`（独立读取器，不复用写出代码）。

## 用户审美偏好
- 要极致细节，全程用小方块，不要火柴盒式的造型
- 细节要能看懂、有内涵；乱堆招牌、伪汉字是减分项
- 一步一步做大，先做样板再铺开
- 看得见、按理能交互的东西都要能交互（门、柜、箱盖、井盖、座椅等）
- 街道和店面不允许重复、千篇一律，不要让人审美疲劳；每一处都要经得起细看
- 不做积水（用户自己开雨和光影）
- 赛博朋克味要贯穿侧墙、路面，而不只是门面
- 用户觉得分段做、做得少就是敷衍：每一轮都要拿出足够的量和细节
- 风格偏科幻、高科技；赛博朋克的“旧/乱”用改装、外露线缆、维修痕迹表现，不用日常市井物件（消防栓、共享单车、普通垃圾桶等否决）
- 1.5.87 新光照渲染更有科幻感，保持；用户吐槽“模块化堆砌感、缺曲线斜面过渡微雕、功能贴近现在” → 设计规则 R1~R8 见 DESIGN.md

## 当前进度
- 拉面店外壳完成（灯槽/外墙/暖帘字序字号/风管/橱窗霓虹背板/漏光假灯+门面豁免 均已修）
- 主街路面 v1 完成但被否决：积水椭圆、黑方块要删，需按 DESIGN.md 重做
- 待办：拉面店第二版（科技改造，见 DESIGN.md）；暖帘已改 noclip 独立导出（ramen_curtain.txt，偏移 (4,2,1)）

## 测试记录
- 2026-10-05 mech A（v3+fixed）：按钮能开，右键门打不开 ✔
- 2026-10-05（1.5.87 实测）：旧蓝图能导入，/lt-open 可用，mech 机关都能动
- 卷帘门：按钮能开，但关不上（门是 disableRightClick:1b）
- loop_fan：开 0→360 顺时针，关时倒放成逆时针；回到原位时闪一下并有放置方块的声音
- 导入后发光变弱或不亮（待查）；新版光照渲染变了，用户觉得更有科幻感
- light、message 结构能用；particle 还没测
- 旧蓝图导入后发光弱/不亮，但原先放着的旧建筑亮度正常（原因待测 G）
- **2026-10-06 probe_187 放置崩溃**，原因：**我自己排版脚本的 `trans()` 盲扫所有 `[I;…]` 数组、把 `animation.rotY` 时间轴也当坐标平移了** → `[I;0,2,0,0,0,20,…]` 被改成 `[I;224,4,0,…]`，`ValueTimeline.read` 拿 `array[0]=224` 去 `getType` → `java.lang.RuntimeException: Invalid id 224`（Client thread、**放置时**、`LittleAdvancedDoor.loadFromNBTExtra:198`）。触发样品 = **E**（唯一走"整节点平移"分支的样品）；其余 8 个样品的结构文本未被平移、时间轴首元素仍为 0 ✓。同类缺陷共 3 处（`trans()` / `lt_probe187` 的包围盒 / `lt_probe_split` 的 `boxes_of`），已全部定位，修法见 HANDOFF §4☆。

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