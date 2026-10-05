# HANDOFF —— LittleTiles 1.12.2 像素小镇·街区项目（给下一个无记忆的会话）

> 配套文档：`NOTES.md`（环境/已验证结论/审美偏好/进度/测试记录/1.5.87 基线核对）、`PLAN.md`（街区总图与坐标）、`DESIGN.md`（科幻赛博朋克设计稿）、`FILES.md`（脚本清单）。
> 工作目录 `E:\work\建筑\`（**所有脚本必须在此目录运行**：`lt_colors.py` 用相对路径读 `flatcoloredblocks.csv`）；记忆仓库 `E:\work\lt-memory\`（远端 GitHub `kuight/lt-opus5.5-memory`）。

---

## 0. 会话开场三件事（别跳）

1. **先写 `probe.txt` 并用 `dir` 确认**（用户要求的工作惯例）。
2. **不要用命令把大段文本打到终端**：用 `read`(带 offset/limit) / `grep` / `glob` 工具精读。大蓝图单行上百 KB，`grep` 命中会返回整行 —— 慎用。
3. **凡是"落盘"立刻读回验证**；改 `.py` 后跑 `python -m py_compile` 或直接重跑生成器。

**工具侧的坑（本会话踩过）**：
- PowerShell 的 `Copy-Item`/`Test-Path` 会把 `[...]` 当通配符 —— mods 里那些 `[小方块]…jar` 必须用 `-LiteralPath`，或先用 `Get-ChildItem | Where-Object` 拿到对象再复制。
- `java -jar cfr.jar` 传**中文路径**参数会被 JVM 用 ANSI 码页解码而失效（报 `No such jar file E:\work\????\...`）→ 把 jar/输出目录放**纯 ASCII 路径**，跑完再搬回中文目录。
- `Set-Clipboard` 可用（会话里做过）；`.ps1` 被执行策略挡，用 `.bat`（`powershell -NoProfile -ExecutionPolicy Bypass -File`）包装，已有 `put.bat` / `put.ps1` 一键把蓝图 JSON 塞进剪贴板。
- **push 到 GitHub 时通时不通**（`Recv failure: Connection was reset` / `Failed to connect ... 443`）。用户要求：**失败就原样贴报错，不要换别的方式绕过**；网络恢复后 `git push origin main` 即可。

---

## 1. 环境（当前实况）

- MC 1.12.2 Forge；**游戏已实跑 LittleTiles 1.5.87 + CreativeCore 1.10.71**（2026-10-05 用户启用，旧存档已备份，旧建筑与旧机关正常）。
- 原版 1.12.2 线（旧记录）：`LittleTiles_v1.5.0-pre199_19` + `CreativeCore_v1.10.10`（两个 jar 都还在 mods 里，`.disabled` 的是新版）。
- 其它：FlatColoredBlocks `mc1.12-6.8`、WorldEdit `6.1.10`。
- 反编译源码：`lt_src\`（pre199）、`lt_src_187\`（1.5.87，438 个 java）；`cc_src\`（CreativeCore）。三个目录都**不入库**。
- 存档：`F:\Apply\Release 2.3.0\.minecraft\versions\1.12.2像素小镇\saves\新的世界\`；日志 `…\logs\latest.log`。

---

## 2. 资产清单（脚本 → 产物）

| 脚本 | 产物 | 作用 |
|---|---|---|
| `lt_np.py` | （库存） | **街区通用库**：`Vol`（numpy 体素 + 贪心合并导出 + 无损自检 + 导入起点打印）；`export(fn,name,structure=None)` 可把结构直接挂根层（自动补 `{}`） |
| `lt_root.py` | （库存） | **根层守卫**：根有 `children` 就必须有 `structure`（缺则插入 + 硬断言）；CLI `selftest` / `verify` / `diff` |
| `lt_tree.py` | （库存） | **导入文本树/语法校验器**：递归解析 tiles/structure/children，查 6 分量、上界排他、count、min/size 全树并集、structure id、advancedDoor 的 offGrid 陷阱 |
| `lt_ramen.py` | `ramen_shop.txt` + `ramen_curtain.txt` | 拉面店外壳 + 门面 + 漏光假灯（LEAKFIX）+ 暖帘独立 noclip 导出 |
| `lt_street.py` | `street_0..3.txt` | 主街路面 4 段×16 格（导入起点 -800/-784/-768/-752, y=3, z=313） |
| `lt_loop.py` | `loop_fan.txt` | 自转扇叶样品（advancedDoor rotY 0→360, linear, 40 tick） |
| `lt_mech.py` / `lt_mech_v.py` / `lt_mech_v45.py` | `mech_test.txt` / `mech_v1..3` / `mech_v4..5` | 机关测试台与对照样品（卷帘门+按钮/翻板/冰柜门/暖帘；A/B 负对照） |
| `lt_colors.py` + `flatcoloredblocks.csv` | （库存） | hex → FCB 方块名（solid/trans/glow 三类最近邻） |
| `put.bat` / `put.ps1` | — | `put.bat street_0` 把该蓝图 JSON 放进剪贴板（Little Importer 导入用） |

---

## 3. 当前进度

- **拉面店**：外壳完成并已实测导入（灯槽/外墙/暖帘字序字号/风管/橱窗霓虹背板/漏光假灯+门面豁免）。暖帘已改成独立 `noclip` 结构文件（`ramen_curtain.txt`，偏移 `(4,2,1)`，相对店西北角 = `+ (3,2,-1)`）。
- **主街路面 v1**：已否决（积水椭圆、黑方块删除后仍不合方向），要按 `DESIGN.md` 重做成科幻赛博朋克版。
- **机关**：`mech_test.txt` 在 1.5.87 下实测"都能动"；`/lt-open` 可用；按钮只能开不能关（见 §4②）。
- **1.5.87 新增能力**：`light` / `message` 结构能用；`particle` 未测；信号系统（命名端口 + 表达式连线 + PULSE）与红石转换方块已就绪未用。

---

## 4. ①②③④⑤ 结论（源码级，行号取自 `lt_src_187`；✔=实测/源码确认，❓=待实测）

### ① 小方块发光：1.5.87 改成了"体积加权"，所以 FCB 发光小方块几乎不亮
- **1.5.87** `BlockTile.java:455` `getLightValue(state,world,pos)`：
  - `:465` tile 属于结构时 → `light = Math.max(light, list.getStructure().getLightValue(pos))`（**结构光照，不缩放**；`LittleLight.java:56` 走这条）
  - `:474` 否则 → `tempLight = (int)Math.ceil(tile.getLightValue(world,pos) * tile.getPercentVolume(context))`（**按体积比例缩放**）
- **pre199** `BlockTile.java:455/464`：`tempLight = tile.getLightValue(state, world, pos)` —— **原亮度，无缩放**
- `getPercentVolume` = 该 tile 占整格的体积比例（`LittleTile.java:196-198` → `LittleBox.java:183`）
⇒ **FCB 发光块放进小方块后仍然"能放"，但亮度被压**：1 像素³ 的 tile 占比 ≈ 1/4096 → `ceil(15 × 1/4096) = 1` → 看起来等于不亮 ✔（与实测"发光变弱或不亮"一致）
⇒ **实操：1.5.87 里要发光，用 `light` 结构；别指望 FCB 发光小方块**。❓ 不同体积下的亮度数值没实测；`LittleBox.getPercentVolume` 的分母（整格体积）按 `:183` 理解，未逐行读全。

### ② 按钮第二次触发不能关门；`disableRightClick` 也挡不住关门
- `LittleDoorActivator.openDoor`（`LittleDoorActivator.java:77-86`）：只对 `toActivate` 里的子门调 `child.openDoor(...)` —— **只有"开"这一个方向，从不调 `activate`** ⇒ 按钮开不了"关"，门已开时 `canOpenDoor` 返回 null → 静默跳过 ✔（与实测"按钮能开但关不上"一致）
- `LittleDoor.activate`（`LittleDoor.java:64-100`）：`:95` `this.opened = !this.opened` → **activate 才是开/关切换**；`:68-70` `if (activator == DoorActivator.RIGHTCLICK && this.disableRightClick) throw ...Hidden("Door is locked!")` → **门禁只挡"右键"这一条路径** ⇒ **`disableRightClick:1b` 不影响关门** ✔
- `:96-98`：非 SIGNAL 触发时 `getOutput(0).toggle()` → 门的 `state` 输出每次切换都翻转（可驱动灯/信号）
⇒ **关门手段**：`/lt-open <x> <y> <z> [结构名]`（走 `activate` → 切换，实测可用）或命令方块时钟反复跑它；1.5.87 还可用红石转换方块+门 `state` 输出做联动。

### ③ `stayAnimated:1b` 能消除"变回方块时闪一下 + 放置声"，但有"起点必须对齐"的限制
- 现象根因：`DoorController.java:146-150`（187）`endTransition()` → `if (turnBack != null && turnBack == (state==opened)) this.place();` —— **`place()` 就是把动画实体换回方块**（闪烁+放置声）
- `stayAnimated=true` ⇒ 构造 controller 时 `turnBack = null`（`LittleAdvancedDoor.java:284`、`LittleSlidingDoor.java:71`、`LittleAxisDoor.java:215`）⇒ **`place()` 不执行，门保持在动画态** ✔
- **NBT 写法**：`stayAnimated:1b`（`LittleDoorBase.java:79` 字段、`:101` 读 `getBoolean("stayAnimated")`、`:115-116` **仅 true 时写**）
- **限制（"必须整圈"的来源）**：
  - `LittleAdvancedDoor.java:697`：任一时间轴"未对齐"→ **强制 `stayAnimated=true`**（GUI 里取消不掉）
  - `AnimationKey.java:110`（RotationKey）`isAligned = value % 360.0 == 0.0`；`:90`（OffsetKey）位移必须为 0
  - `AnimationTimeline.java:204-206 isFirstAligned()` + `LittleAdvancedDoor.java:564` `settings.stayAnimatedPossible = animation.isFirstAligned()`
  ⇒ **起点 rotY=0（360 的整数倍）就满足**，我们 `loop_fan` 的起点正是 0 ⇒ **可以直接加 `stayAnimated:1b`** ✔
- 副作用（好）：`LittleDoorBase.java:293-295 isInMotion() = animation != null && controller.isChanging()` ⇒ **停在动画态、不在过渡中时 `isInMotion()==false`** ⇒ 仍可被命令方块反复触发 ✔
- ❓ 动画实体长期停留对碰撞/光照/存档的影响没实测。

### ④ 关门一定"倒放"，没有独立关门时间轴
- `LittleAdvancedDoor.java:252/258/264`（offX/offY/offZ）+ `:270/276/282`（rotX/rotY/rotZ）：**close 时间轴 = `open.invert(duration)` 逐通道生成**；`:284` 把它交给 `DoorController(open, close)`
- NBT 里只存在一个 `animation:{rotX/rotY/rotZ/offX/offY/offZ}`（`:168-169` 等）⇒ **没有"关门时间轴"字段** ⇒ 关门必然倒放（`ValueTimeline.invert(duration)`，`ValueTimeline.java:201-215`）
- 变通（不改源码）：① 把扇叶做成**中心对称**（4 叶 90° 对称或 2 叶 180° 对称）→ 倒放看不出来；② 只追求"关掉时别闪/别响" → 用 ③ 的 `stayAnimated:1b`；③ 真要"关门也正转"只能改源码加字段。

### ⑤ `particle_emitter` 怎么获得 + NBT 范本
- **有合成表**：`assets/littletiles/recipes/particle_emitter.json`（jar 内实测）
  ```
  图案:  C D C        C = minecraft:concrete (data 15 黑色混凝土) ×6
         G R G        D = minecraft:dispenser (发射器)  ×1  ← 顶部中间
         C C C        R = minecraft:redstone_block (红石块) ×1
                      G = minecraft:firework_charge (烟火之星) ×2
  "type": "littletiles:crafting_shaped_premade", "result": {"item":"littletiles:premade","structure":"particle_emitter"}
  ```
- 也可 `/give`：预制品物品注册名 = `littletiles:premade`（`LittleTiles.java:252` `new ItemPremadeStructure().setRegistryName("premade")`），物品 NBT 里带 `structure:{id:"particle_emitter"}`（`LittleStructurePremade.java:62-81` 的装载逻辑）⇒ `/give @p littletiles:premade{structure:{id:"particle_emitter"}}` ❓(按源码推导，未实测)
- **官方预制品原文**（`assets/littletiles/premade/particle_emitter.struct`，可直接当模板）：
  ```json
  {tiles:[{bBox:[I;0,0,0,1,1,1],tile:{color:-13619152,block:"littletiles:ltcoloredblock"}}],
   min:[I;0,0,0],size:[I;1,1,1],grid:16,count:1,
   structure:{ticker:3,speedZ:0.0f,color:-1,speedY:0.1f,speedX:0.0f,texture:"smoke",lifetime:20,
              facing:4,tickDelay:10,spread:0.0f,size:0.4f,gravity:0b,growrate:1.0f,id:"particle_emitter",state:0}}
  ```
  ❓ 该 .struct 用的是**扁平旧键**，而反编译出的写侧用 `ParticleSettings` 的键（`color`/`lifetime`/`lifetimeDeviation`/`texture`/`randomColor`/`collision`，`LittleParticleEmitter.java:358-381`）+ `tickDelay`/`tickCount`/`ticker`（`:156-173`）+ spread `steps`（`:211`）——**新写文件该照哪套键名，未确认**（以官方 .struct 能加载为准，但可能只是兼容旧键）。

---

## 5. 下一步计划（用户已定）

1. **`lt_np.py` 扩展**：加 `light` / `particle` / `signal` 的接口（把命名端口、`signal` 列表、`stayAnimated`、条件表达式 `con` 都做成可写参数），让后续所有模块都能直接产出带机关的蓝图。
2. **拉面店整体改成"金属舱体科技版"**（保留木质外壳做对比 → 见 `DESIGN.md` 末行）：全息菜单、神经支付环、机械臂煮面、低温冷柜、能源电池柜、散热风扇、无人机投递口、线缆槽。
3. **按 `DESIGN.md` 铺街道**：S1 光栅人行横道 / S2 悬浮舱停靠站 / S3 能源管廊 / S4 交通控制塔路口（每段主题不同，机关清单见 DESIGN.md；同类元素相邻 3 段不重复）。

**做这三件事时的既有约束**：
- 坐标：`PLAN.md` 为总图（西北角 x=-800,z=300；主街 y=3 一层，建筑从 y=4 起；南排 拉面店 -800~-792 / 小巷 -791~-790 / 便利店 -789~-778 / 居酒屋 -777~-769 / 公寓楼梯间 -768~-761 / 电玩店 -760~-749）。
- 导入锚点：**蓝图 min 角落在锚点格上**，体素落点 = `锚点 + floor(蓝图坐标/16)`；脚本会自动打印"导入起点"，别手算。
- 硬规则：根有 `children` 必须有 `structure`（`lt_root` 会拦）；写完必跑 `lt_tree.py` 复核 `[问题] 无`；`Vol.export` 的无损自检必须 True。
- 审美：偏科幻高科技；赛博朋克的"旧/乱"用改装/外露线缆/维修痕迹表现，**不用日常市井物件**（消防栓、共享单车、普通垃圾桶否决）；不做积水；看得见的东西都要能交互；每轮要拿出足够的量与细节。
- 光照：1.5.87 下小方块自身发光被体积加权压掉 → **用 `light` 结构**；室外离室内 ≤2 格的装饰灯用同色不发光假灯（`lt_ramen.py` 的 LEAKFIX 是参考实现）。
