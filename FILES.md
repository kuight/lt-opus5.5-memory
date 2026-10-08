# FILES.md —— 脚本清单（用途 / 输入 / 输出文件名 / 最后验证日期）

日期约定：**2026-10-05** = 该脚本在本次会话中实际跑过或校验过；
**未验证** = 本轮没跑（保留早前产物，未重生成）。改动脚本前先看 NOTES.md「已验证结论」。

| 脚本 | 用途 | 输入 | 输出文件名 | 最后验证日期 |
|---|---|---|---|---|
| lt_colors.py | FCB 最近色查询：hex 颜色 + kind(solid/trans/glow) → FCB 方块名（纯 RGB 平方距离最近邻） | flatcoloredblocks.csv | 无（被 import） | 2026-10-05（间接：lt_mech.py 链路调用） |
| lt_gen.py | 最早的形态库：parse / mesh（贪心合并）/ export；CLI `verify`、`console` | 蓝图 txt 或 build_console() | console.txt、sample_rebuilt.txt（verify 模式） | 未验证 |
| lt_items.py | B(W) 镜像填充助手 + 三种小家具构造 | 无（自建体素） | server_rack.txt、ring_lamp.txt、glass_railing.txt | 未验证 |
| lt_func.py | with_struct() + 带功能家具：办公椅/实验室滑门/医疗舱床/检修梯 | 无（自建体素） | office_chair.txt、lab_door.txt、med_bed.txt、service_ladder.txt | 未验证（产物已收入 samples/） |
| lt_lib.py | 体素 dict + 贪心盒合并 LT.save()；面板凹缝 panel() | 无（被 import） | 由调用者命名 | 2026-10-05（save() 增 return txt，经 lt_child_test.py 跑通） |
| lt_lab1.py | 用 lt_lib 拼实验室构件 | 无（自建体素） | wall_module.txt、lab_bench.txt | 未验证 |
| lt_recolor.py | 批量换名后处理：玻璃→FCB 透明、灯→FCB 发光 | 风格化 txt | *_fc.txt | 未验证 |
| lt_style.py | clean / texture 两种风格后处理 | 蓝图 txt | *_clean.txt、*_texture.txt | 未验证 |
| lt_board.py | 材质对照板（逐材质一格） | flatcoloredblocks.csv 等 | mat_board.txt | 未验证 |
| lt_palette.py | 材质色板/调色板 | 无 | mat_palette.txt | 未验证 |
| lt_room.py | 11×6×11 房间的 /fill 指令（1.12.2 数字+名称 meta 语法） | 无 | room_cmds.txt | 未验证 |
| lt_shell.py | WorldEdit 外壳指令 //pos1/pos2/set/walls | 无 | shell_cmds.txt | 未验证 |
| lt_child_test.py | A/B 单变量测「顶层带 structure」：A 正常断言，B 为**显式声明豁免**的负对照 | lab_door.txt、office_chair.txt | test_child_A.txt、test_child_B.txt | 2026-10-05（重跑 + 守卫校验：A 通过 / B 豁免 exit=1） |
| lt_cyber.py | 赛博实验室生成器（早期版） | 无（自建体素） | **cyber_lab.txt**（本轮改名，原 nexus_lab.txt） | 2026-10-05（仅 py_compile + 守卫形状回归；按用户要求未整跑） |
| lt_nexus.py | NEXUS 实验室大蓝图，含 3 个子结构（滑门 + 2 椅） | lab_door.txt、office_chair.txt | nexus_lab.txt | 2026-10-05（仅 py_compile + 守卫形状回归；未整跑） |
| lt_neon.py | 霓虹塔（GREEBLE 自适应） | 无（自建体素） | neon_tower.txt | 未验证 |
| lt_city.py | 霓虹街区（MIRROR=True 镜像） | 无（自建体素） | neon_city.txt | 未验证 |
| lt_ramen.py | 一番拉面店外壳与门面（唯一带真机通行检查：0.6×1.8 玩家盒）；含漏光假灯 LEAKFIX + 根层守卫 | 无（numpy/PIL 自建） | **ramen_shop.txt、ramen_curtain.txt**（暖帘独立 noclip 结构） | 2026-10-05（重跑：通行检查全通过 / 无损 True / 暖帘偏移 (4,2,1)） |
| lt_ramen_shell.py | 拉面店外壳的 /fill 指令（自带 BFS 通行检查） | 无 | ramen_shell.txt | 未验证 |
| lt_mech.py | 机关测试台：卷帘门+按钮 / 吧台翻板 / 冰柜门 / 穿透暖帘 | 无（自建体素） | mech_test.txt | 2026-10-05（重跑 + 根层逐字节比对一致） |
| lt_mech_v.py | 机关对照样品 v1~v3（门可右键无按钮 / 有按钮 / 门禁右键） | 无（自建体素） | mech_v1_门可右键_无按钮.txt、mech_v2_门可右键_有按钮.txt、mech_v3_原版_门禁右键_有按钮.txt | 2026-10-05（重跑，守卫自动插 structure） |
| lt_mech_v45.py | 由 v2/v3 派生 v4（**豁免**负对照：根无 structure）/ v5（根带 structure） | mech_v2/v3 的 txt | mech_v4_按钮门触发子门_根无结构.txt、mech_v5_根带结构_门禁右键_有按钮.txt | 2026-10-05（重跑 + 反做还原校验） |
| lt_np.py | **街区通用库**（1.5.87 基线）：`Vol` = numpy 体素 + 贪心合并 + 无损自检 + 打印导入起点；`export(fn,name,structure=None)` 把结构挂根层（自动补花括号） | 无（被 import） | 由调用者命名 | 2026-10-05（被 lt_street/lt_loop/lt_probe187 反复调用，全部无损 True） |
| lt_probe187.py | 1.5.87 探针：A 官方 particle_emitter 原文 / B 新键名粒子 / C 扇叶+stayAnimated / D light 亮度15 / E 门 state→灯 / F 自激灯+总开关 / F10 十盏灯 / H 1/4 圆柱墙(R=8格+4px 倒角) / I 30° 斜板(11 分量可变形盒)；样品间隔 2 格排开。**修法 A：样品局部生成 + 只对 tiles 段做带断言的平移（`shift_tiles`），结构文本不碰；`trans()` 已删除** | 无（自建体素 + SDF） | probe_187.txt | 2026-10-06（lt_root ✓ + lt_tree ✓；9986 B / 242 盒 / 导入起点 (0,0,0)；C 轴心 [120,2,24,…]、E [224,2,9,…] 全部落在自家盒子内） |
| lt_street.py | 主街路面 4 段×16 格（**随 v1 街区作废**，留作排版/SDF 参考） | 无（自建体素） | street_0..3.txt | 2026-10-05（4 段无损 True；起点 -800/-784/-768/-752, y=3, z=313） |
| lt_loop.py | 自转扇叶样品：4 叶 + 青色发光轴，advancedDoor rotY 0→360（linear, 40 tick） | 无（自建体素） | loop_fan.txt | 2026-10-05（无损 True + lt_tree [问题] 无；线性关键帧编码有源码自检断言） |
| lt_probe_j.py | 样品 J：light(level:0) 当开关 → 其子结构卷帘门被"信号"开/关（门的 `state` 输出 `con:"p.b0"` 跟父的 enabled） | 无（自建体素） | probe_j.txt | 2026-10-06（lt_root 断言通过 + lt_tree [问题] 无；851 B / 11 盒 / 导入起点 (0,0,0)） |
| lt_mass.py | 天梯城体块模型 v0：地形（两山 + 斜穿峡谷 + 台地量化）、天梯（平台/三主塔/环梁/缆束/对接环/发射塔）、4 座穿楼塔、5 条线路（磁浮/连廊/索道/能网/光瀑）；手写 gzip+NBT 出 schematic，自带回读自检 + 俯视高度图 + 对角剖面 + ASCII 高度图 | 无（纯计算） | mass_v0.schematic、mass_v0_top.png、mass_v0_sec.png | 2026-10-06（自检：尺寸一致 ✓ 字节级回读一致 ✓ 非空气 499623 块）；**已被 lt_mass1 取代，仅作参考（mass_v0 产物亦同）** |

| lt_mass1.py | **天梯城 体块 v1（总图 v3 灰模）**：多地面地形（上台地 y96 / 崖边小台地 y74 / 中台地 y52 / 崖边小台地 y34 / 谷底 y16，边缘正弦曲折）、地下城竖井（剖口 + 4 层地下街 + 街灯）、天梯基座（缆束下段青→中段青玻璃→顶段玻璃渐隐 + 三主塔 + 环梁）、公司塔区 5 座错位外挑塔 + 玻璃连廊、工业谷（冷却塔 ×3 / 碎片熔炉 + 散热鳍片 / 菌丝农场塔 / 取水塔 + 雾网）、巨构住宅 2 栋三段外挑、城寨/桥下市井（随机地块 106 栋 + 违建外挑）、两条轨道（爬坡/拐弯/穿楼/不等墩距）、四网（管线/电缆/人行）；手写 gzip+NBT 出 schematic + 独立回读自检 + 俯视/剖面 PNG + 5 个 /tp 机位；**作者：设计方** | 无（纯计算；需 Pillow） | `mass_v1.schematic`（**不入库**，已复制到 WE `config\worldedit\schematics\`）、`samples/mass_v1_top.png`、`samples/mass_v1_sec.png` | **待用户实测**（2026-10-08：65352 B gzip / 解压 12953820 B；尺寸 160×253×160 = 6476800 格，非空气 **1742827**；WEOrigin (-800, 3, 300) ⇒ 世界 x -800..-641 / y 3..255 / z 300..459；回读自检全部 PASS ✓；1 号线全长 163 格 11 墩梁高 84→100、2 号线 142 格 12 墩梁高 44→104） |
| lt_verify_schem.py | **独立**校验 .schematic：gzip 魔数、解压后前 12 字节必须 `0A 00 09 "Schematic"`、根标签名、根下全部键与类型、关键键类型/长度、文件是否被完整消费（自带另一套极简 NBT 读取器，**不复用 lt_mass.py 的代码**） | schematic 文件 | 无（只打印） | 2026-10-06（mass_v0.schematic：所有检查通过 ✓，verify_exit=0） |
| lt_probe_split.py | 把 `probe_187.txt` **切片**成单样品文件 `probe_A..I.txt`+`probe_F10.txt`（各带独立根 fixed），并生成去掉嫌疑样品的 `probe_187_safe.txt`；顺带逐样品检查时间轴数组首元素是否 0~3（本次就是靠它+崩溃报告定位到 E） | probe_187.txt | probe_A..I.txt、probe_F10.txt、probe_187_safe.txt | 2026-10-06（10 份全部 lt_root 断言通过 + lt_tree [问题] 无） |
| lt_density.py | **精度压力样品**：6 格宽 × 8 格高 × 2 格厚金属舱壁，表面全细节（2px 面板分缝 4×4 网格 / 288 颗 1px 铆钉 / 3px 圆形截面管线(SDF) / 一组散热格栅 / 2 处 1px 青色 FCB 指示条）；自带报告：盒子数、占用格数、每格盒子数、**每表面格盒子数**、规模估算 | 无（自建体素 + SDF） | density_test.txt | 2026-10-06（lt_root ✓ + lt_tree ✓；263 盒 / 144 格 / 表面 48 格上 261 盒 ≈ 5.4 盒·每表面格） |
| lt_tbox.py | **187 原生可变形盒编解码**（`LittleTransformableBox`）：`decode/encode`、K 样本往返逐位一致；位布局见 NOTES 第 22 条 | `[I;…]` 数组 | 无（库 + CLI `decode`） | 2026-10-06（K 往返 True ✔） |
| lt_probe2.py | 按"门会把 children 搬进动画"结论重做的探针：控制器 light(level:0) 下**并列**放门与灯 ⇒ probe_E2 / F2 / F2x10 / J2 | 无（自建体素） | probe_E2/F2/F2x10/J2.txt | 2026-10-06（4 份 lt_root ✓ + lt_tree ✓） |
| lt_h23.py | 用原生可变形盒做**无台阶**的 1/4 圆柱墙（16 个多边形切面）：H2 石英 / H3 FCB 灰 | lt_tbox | probe_H2.txt、probe_H3.txt | 2026-10-06（各 16 盒，lt_root ✓ + lt_tree ✓） |
| lt_h23b.py | H2b/H3b：**只向内偏移** + 每切面按格高拆 4 段的可变形盒圆柱墙（规避 `setBounds` 夹回 AABB 的风险） | lt_tbox | probe_H2b.txt、probe_H3b.txt | 2026-10-06（各 64 盒，lt_root ✓ + lt_tree ✓） |
| lt_mech2.py | **机关标准写法接口库**（不动 lt_np 旧接口）：`controller` / `light` / `blink`(相位用 delay 错开) / `door_slide` / `door_rot` / `particle`(facing 默认 1=UP) / `tbox_face` / `bevel_edge`；只向内偏移 + 自动按格拆段；自带自测（重建 E2/F2/J2/H2b 做结构等价比较） | 无（库 + 自测） | mech2_E2/F2/J2/H2b.txt（自测产物） | 2026-10-06（4 项结构等价 ✔） |
| lt_scale.py | 规模样品：16×16 格舱壁地表（scale_A 带 45° 倒角 / scale_B 不带）；**limit_* 上限填充已按要求删除（Little Importer ≥1MB 实测可用；单文件最大实测约 1MB 可用，更大未测；不设上限，首个大文件导入时顺带观察）** | lt_mech2 | scale_A.txt、scale_B.txt | 2026-10-06（scale_B ✓✓✓；scale_A 待重生成） |
| lt_geom.py | **几何自检**（含可变形盒的文件必过）：解码 8 角点/6 面 → 面不共面(容差 0.01px)、竖边 U/D 偏移一致、与目标弧面 2000 点比对（最大偏差 >1px 报问题）；出 top/front PNG | 蓝图 txt（+可选弧参数） | `<file>_top.png`、`<file>_front.png` | 2026-10-06（反例 probe_H2b 报 232 问题 ✔） |
| lt_h45.py / lt_h46.py / lt_h7.py | 弧墙生成：H4c（按格裁切，反例）/ H6（整段四边形，默认做法）/ H5m（中灰）/ H7·H7b（加墙基） | lt_mech2（arc_wall_quad）/ lt_colors | probe_H4c/H6/H5m/H7/H7b.txt | 2026-10-07（H6/H5m/H7/H7b 三项全过 ✓；H4c 仅作反例） |
| lt_root.py | **根层守卫**：根有 children 就必须有 structure（缺则插入 + 硬断言）；CLI `selftest`/`verify`/`diff` | 根层文本（库） | 无（库；CLI 只打印） | 2026-10-05（selftest 全过 + verify 全部样品） |
| lt_tree.py | 导入文本树/语法校验器：递归解析 tiles/structure/children，查 6 分量与 **7/11 分量可变形盒**、上界排他、count、min/size（全树并集）、structure id（含 1.5.87 新增 id）、advancedDoor 的 offGrid 陷阱；**新增守卫①时间轴形态（首元素 0~3、长度 2+3*count(+hermite 3)）②axisCenter 必须落在本节点盒子包围盒内**；有问题返回 exit 1 | 蓝图 txt | 无（只打印；退出码 0/1） | 2026-10-06（12 份探针全过；2 份反例夹具必须报错 ✔） |

## 交付状态（2026-10-06；门禁 = lt_root + lt_tree + lt_geom（含可变形盒时）三项全过；单文件最大实测约 1MB 可用，更大未测；不设上限，首个大文件导入时顺带观察）

| 文件 | 三项检查 | 交付判定 | 用户测试结果 |
|---|---|---|---|
| probe_I2.txt | ✓✓✓（1 盒，8 分量原生） | **可交付** | **没问题 ✔** |
| scale_B.txt（609 盒） | ✓✓✓（无变形盒） | **可交付** | 开光影 ≈**20fps** / 关光影 ≈**40fps**（**比 density_test 还卡，待排查 §5**） |
| scale_A.txt | ✓✓✓（**已用修复后代码重生成** + 补跑 lt_geom：48 个可变形盒、0 问题） | **可交付** | 待测（与 scale_B 对比倒角观感） |
| probe_C/D/E2/F2/F2x10/J2 | ✓✓✓ | **可交付** | 均 ✔（E2 门灯同步、J2 不闪无声、F2 自闪可停但有 delay 延迟、F2x10 掉帧） |
| probe_A.txt / probe_B.txt | ✓✓（无变形盒） | 可放置 | 黑色圆弧上升 / 白色水平移动（已解释，见 NOTES 21） |
| probe_I.txt | ✓✓⚠（11 分量旧格式→警告） | **移出可交付** | — |
| probe_H/H2/H3/H2b/H3b | H/H2/H3 ✗（越界）；H2b/H3b 几何 ✗（232 问题） | **几何反例夹具（不交付）** | H2b/H3b：鳞片歪墙、曲面没做成 |
| probe_E.txt | ✗（时间轴 224） | **崩溃夹具（不交付）** | — |
| probe_H6.txt / probe_H5m.txt | ✓✓✓（64 盒、3727/3728 B、密采样最大偏差 **1.37px**） | 可交付（已被 H8 取代，留档） | 见 H6/H5m 实测 |
| probe_H8.txt | ✓✓✓（80 盒、4948 B、密采样最大偏差 **1.12px**/平均 0.44；16px 墙基 + 共用内弧顶点 + 双射配对） | **可交付（本轮唯一交付份）** | 用户实测：台阶感不明显、弧形较好、**墙基与墙体无缝隙**，基本够用 ✓ |
| probe_H7.txt / probe_H7b.txt | 三项曾通过；但 **H7b 有墙基顶面缺口** ⇒ **降为参考（不交付）** | 参考 | H7 未解决暗块；H7b 暗块全消失但有缺口 |
| probe_H4c.txt | ✗（按格裁切：错位缺片，用户判失败；越界 0、共享边 0、最大偏差 2.35px） | **反例夹具（不交付）** | — |
| density_test.txt | ✓✓✓ | 可交付 | 开 50 / 关 100+ fps（密度 5.4 盒/格） |
| std_wall2.txt | ✓✓✓（**714 盒 / 30157 B / 12.69×6.00×4.69 格 / 每格 3.74 盒**；平整板面 **42.1%**、倒角翘曲 0.114px；含 1/4 弧转角 + 3 层凹凸 + 3 个设备格间 + 48 颗铆钉；**接缝 `lt_seam` 通过**） | **可交付（标准墙，替代 scale_A / std_wall）** | 待测（见 HANDOFF §6） |
| std_wall.txt | ✓✓✓（**120 盒 / 4763 B / 8.00×6.00×3.12 格 / 每格 2.5 盒**；含 1/4 弧转角 + 3px 45° 倒角 + 16px 墙基；geom 45 变形盒 0 问题） | **可交付（替代 scale_A）** | 待测（见 HANDOFF §6） |

| patch_geom_env.py | 给 `lt_geom` 加 `LT_COPLANAR_TOL` / `LT_GEOM_COMPOSITE` 两个环境变量开关（默认行为不变）；**作者：设计方** | 无 | — | 2026-10-07 原样保存并运行：**PASS** ✓ |
| lt_seam.py | 弧直接缝检查（直段端面是否被弧段起始面盖住 / 角点是否正好在接缝面 / 有无盒子横跨）；**作者：设计方** | 无 | — | 2026-10-07 原样保存（未运行，见下） |
| lt_wall2.py | 标准墙 `std_wall2` 生成器（**作者：设计方**）；自检：平整面 ≥40%、倒角翘曲 ≤1.0px | numpy / lt_tbox / lt_colors | `samples/std_wall2.txt` | **2026-10-07：三项全过 + 接缝通过** ✓ |

| patch_wall2_zo.py | `lt_wall2.py` 修订：ZO 12→11（墙前沿 z=0）+ 运行前先删旧 `std_wall2.txt`；**作者：设计方** | 无 | — | 2026-10-07 原样保存并运行：**PASS** ✓ |
| patch_wall2_fmt.py | `lt_wall2.py` 修订：导出模板 `size` 补 `I;`、`count=根盒子数`；`warp_of` 改为与 `lt_geom` 同一共面口径；**作者：设计方** | 无 | — | 2026-10-07 原样保存并运行：**PASS** ✓ |

| lt_wall3.py | **风格样品 A/B/C**（读 `lt_wall2.py` 源码执行，仅换材质 + 追加一件悬浮件；A 赛博朋克 / B 硬科幻亮白 / C 中式未来）；**作者：设计方** | lt_wall2（源码）/ lt_colors | `samples/std_wall3_A/B/C.txt` | **2026-10-07：A/B/C 各 4 步全过（三项门禁 + 接缝）** ✓；**待用户挑风格** |

| lt_s1.py | **超越技术样品 S1「实体光楼」**（黑色投影基座 + 4 层半透明实体光楼板 + 寄生舱/塔架/电缆 + 青粒子；**作者：设计方**） | lt_np / lt_mech2 / lt_colors | `samples/s1_light.txt` | **2026-10-07：lt_root / lt_tree 通过 ✓（无可变形盒，lt_geom / lt_seam 不适用）**；441 根盒 + 2 粒子子结构 = 443 盒 / 11966 B |

| lt_wall4.py | **加装层样品**，**第 2 参数 `A|B|N`**（缺省 A；`_B`/`_N` 后缀）；**H 为基准密度**；B 警示已改发光红；读 `lt_wall2.py` 源码执行，ZO 11→22，只在直段加 retrofitting；**作者：设计方** | lt_wall2（源码）/ lt_colors | `samples/std_wall4_H.txt`、`std_wall4_H_B.txt`、`std_wall4_H_N.txt`（⚠ `std_wall4_M` / `std_wall4_M_B` **作废：招牌字左右反**） | **待用户实测**（H 1083 盒/38376 B；**H_B 1154 盒/39811 B（发光盒 103）**；H_N 1083 盒/38447 B；四组四项门禁全过 ✓） |

| patch_wall4_b.py | 给 `lt_wall4.py` 加第 2 参数 `A|B`（缺省 A，输出不变；B 亮白硬科幻：检修门/寄生舱 #C8CED4、设备中灰 #7E8893、发光仅青白 #9FF3FF、警示红 #D13A2A 不发光、招牌白底红字）；**作者：设计方** | 无 | — | 2026-10-07 原样保存并运行：**PASS** ✓ |

| patch_wall4_n.py | `lt_wall4.py` 第 3 版补丁：加风格 **N**（民生夜读版）、**修招牌字左右反**（列 c → x=48-c）、**加强 B 警示**（罐带 4px + 檐下 45° 斜纹）；**作者：设计方** | 无 | — | 2026-10-07 原样保存并运行：**PASS** ✓ |

| patch_wall4_glow.py | `lt_wall4.py` 第 4 版补丁：**B 警示改发光红**（`glowm`/`red` solid #D13A2A → glow **#FF3B2F**）+ 修 N 对照组提示（改指 `std_wall3_A`）；**作者：设计方** | 无 | — | 2026-10-07 原样保存并运行：**PASS** ✓ |

| lt_noodle1.py | **合成蛋白面馆 一期待测件**（体块 + 剖面）：吊脚架空层（9 柱 + 6 大梁 + 24 隅撑）/ 中层面摊（临街整面敞开 + 柜台 + 暖光带 + 高凳 ×4 + 腰檐）/ 上层圆角住舱（R=32px 弧墙 ×4 + 腰檐→顶檐）；斜面只用 Y 偏移可变形盒；CLI 无参数，跑完打印盒数/字节/尺寸/占用格/材质表；**作者：设计方** | lt_colors / lt_root / lt_tbox / lt_mech2 | `samples/noodle1.txt`、`noodle1_top.png`、`noodle1_front.png` | **已退役：面馆改为桥下面摊重做，仅作参考**（原状态=待用户实测；2026-10-08：328 盒 = 体素 96 + 可变形 232（弧墙 160 / 飞檐 48 / 隅撑 24），16404 B，14.00×15.00×11.50 格，占用 940 格 / 0.35 盒·每格；lt_root ✓ + lt_tree ✓（[问题] 无）+ lt_geom（`LT_GEOM_COMPOSITE=1`、`LT_COPLANAR_TOL=0.12`）232 盒 0 问题 ✓ —— 三项全过） |

| lt_noodle2.py | **合成蛋白面馆 二期a待测件**（举架屋面 / 瓦垄集热肋 / 檐下散热椽 / 平座勾栏 / 高凳重做 / N 风格分色）：读 `lt_noodle1.py` 原文按 7 个锚点替换（每个必须恰好出现 1 次）+ 插入二期a 代码后 `exec` 执行，一期逻辑不改；**作者：设计方** | `lt_noodle1.py`（原文，须 sha256 以 272a8a4c 开头） | `samples/noodle2.txt`、`noodle2_top.png`、`noodle2_front.png` | **已退役：面馆改为桥下面摊重做，仅作参考**（原为中式方向撤销；2026-10-08：712 盒 = 体素 202 + 可变形 510（一期 232 + 二期a 屋面 6 / 瓦垄 56 / 散热椽 216），34207 B，14.00×17.69×11.50 格，占用 1080 格 / 0.66 盒·每格；举架分步 RZ[56,72,84,92]→RH[234,242,250,261]，坡度 0.5/0.67/1.38；明度分级“全部可分”；lt_root ✓ + lt_tree ✓（[问题] 无）+ lt_geom（`LT_GEOM_COMPOSITE=1`、`LT_COPLANAR_TOL=0.12`）510 盒 0 问题 ✓ —— 三项全过） |

| lt_noodle3.py | **合成蛋白面馆 v3 待测件**（去中式：停用飞檐 `eave_ring` / 金属雨棚（四边排水坡，棚底外沿发光条）/ 屋顶设备平台（冷凝机组 + 储能罐×2 + 桅杆 + 管道 + 电缆）/ 平台与顶层轮廓光 / 竖挂霓虹招牌「合成面馆」双面字（Pillow + simhei）/ 舱窗改发光）；读 `lt_noodle1.py` 原文（须 272a8a4c 开头）按锚点替换 + 插入 v3 代码后 `exec`；**作者：设计方** | `lt_noodle1.py`（原文） | `samples/noodle3.txt`、`noodle3_top.png`、`noodle3_front.png` | **已退役：面馆改为桥下面摊重做，仅作参考**（原状态=已实测：招牌字向正确、屋顶设备可读；夜景灯带不足 → v4；2026-10-08：893 盒 = 体素 701 + 可变形 192（弧墙 160 + 隅撑 24 + 雨棚 8；飞檐 0），30271 B，13.62×19.00×11.06 格，占用 835 格 / 1.07 盒·每格；招牌字 311 像素 ×2 面、电缆 141 点；材质 16 键、[同块] 3 组（deck/roof、rib/top、amber/pane，只提示不拦截）；lt_root ✓ + lt_tree ✓（[问题] 无）+ lt_geom（`LT_GEOM_COMPOSITE=1`、`LT_COPLANAR_TOL=0.12`）192 盒 0 问题 ✓ —— 三项全过） |

| patch_noodle3_d3.py | `lt_noodle3.py` 第 1 版补丁：中层雨棚 `canopy(..., 144)` → `canopy(..., 144, D=3)`（D=4 时四角底面 y133 压到一期腰线带顶 y134）；补丁前后带 sha256 断言 + 写入后读回一致；**作者：设计方** | `lt_noodle3.py` | — | 2026-10-08 原样保存并运行：**PASS** ✓（补丁前 `B18B2505…` → 补丁后 `8B5A2F75…`，10921 字节）；**已退役：面馆改为桥下面摊重做，仅作参考** |

| lt_bridge2.py | **轨道桥二期·原型段待测件**（坡道 2px/格 → 全程逐格可变形盒段；墩距 11/17/13 格不等；4 种墩型：标准 `std` / 门式 `portal`（腿在桥外、中间留 4 格给店）/ 加固老墩 `hoop`（钢箍 + 斜撑 + 锈补丁 + 警示灯）/ 标准；梁底琥珀下照贴斜梁并避开墩；北侧灯笼缆逐跨不同；**作者：设计方** | 无（自建体素；需 Pillow + Windows 中文字体） | `samples/bridge2_proto.txt`、`bridge2_proto_top.png`、`bridge2_proto_front.png` | **待用户实测**（2026-10-08：2806 盒 = 体素 1873 + 可变形 933，94119 B，44.00×19.88×6.00 格，文字 778 像素、灯笼 17；墩距 [11,17,13] 格，梁底 168→256 px（净空 10.5→16.0 格）；lt_root ✓ + lt_tree ✓（[问题] 无）+ lt_geom（`LT_GEOM_COMPOSITE=1`、`LT_COPLANAR_TOL=0.12`）933 盒 0 问题 ✓ —— 三项全过） |

| patch_bridge2_a.py | `lt_bridge2.py` 第 1 版补丁：梁底下照灯由**体素**改为**贴斜梁的可变形盒**（`seg("amber", 45, 51, (-2,-2), (0,0))`）并**避开墩**；补丁前后带 sha256 打印 + 写入读回一致断言；**作者：设计方** | `lt_bridge2.py` | — | 2026-10-08 原样保存并运行：**PASS** ✓（补丁前 `82727bfdad5ce04d…` → 补丁后 `8d92be9d…`（文本模式写盘 ⇒ 实际文件字节哈希 `0f6d516f…`，232 行 CRLF，11638 B） |

| lt_noodle4.py | **合成蛋白面馆 v4 待测件**（夜景灯带加密 + 全息屏）：6 组灯线/灯条/灯环（吊脚柱与大梁、平台轮廓与下照、面摊过梁/墙垛/内凹带/雨棚封檐双线、住舱窗框与舱顶带、屋顶罐条与百叶、招牌杆）+ 平台西/东/南轮廓 + 航空障碍灯（红）+ 全息菜单屏「蛋白面」与露台全息牌「营业中」（半透明 FCB `holo` + 发光边框 + 洋红字）；读 `lt_noodle3.py` 原文（须 8B5A2F75C127F669 开头）按锚点插入 v4 代码后 `exec`；**作者：设计方** | `lt_noodle3.py`（原文） | `samples/noodle4.txt`、`noodle4_top.png`、`noodle4_front.png` | **已退役：面馆改为桥下面摊重做，仅作参考**（原状态=待用户实测；2026-10-08：1105 盒 = 体素 913 + 可变形 192（弧墙 160 + 隅撑 24 + 雨棚 8；飞檐 0），35711 B，13.69×19.00×11.12 格，占用 928 格 / 1.19 盒·每格；**新增发光件 58 处**、全息屏 2 块、屏上字 448 像素；材质 17 键、[同块] 3 组（deck/roof、rib/top、amber/pane，只提示不拦截）；lt_root ✓ + lt_tree ✓（[问题] 无）+ lt_geom（`LT_GEOM_COMPOSITE=1`、`LT_COPLANAR_TOL=0.12`）192 盒 0 问题 ✓ —— 三项全过） |

| lt_bridge1.py | **轨道桥标准件 一期待测件**（桥墩 = 墩座 16px + 40×48 墩柱 + 黄黑警示斜纹 + 东西壁柱 + 区号文字 + 锤头帽梁 + 支座 + 检修梯 + 接线箱 + 灯笼缆挂点；桥面 = 钢箱梁 + 梁底倒角 + 加劲肋 + 护栏 + 电缆槽 + 道床枕木 + 双钢轨 + 接触线 + 网杆 + 南侧 R7 水管与吊架 + 青色轨道网灯带 + 梁底琥珀下照；跨中 = 北侧灯笼缆（悬链，垂度 30px）+ 红灯笼 ×7 + **「轨道一号线」「B-0x」文字**；**作者：设计方** | 无（自建体素；需 Pillow + Windows 中文字体） | `samples/bridge_kit.txt`、`samples/bridge_unit_B04.txt`、`samples/bridge_unit_B05.txt`、`samples/bridge_end_B06.txt`、`samples/bridge_kit_top.png`、`samples/bridge_kit_front.png` | **一期：截面接口参考**（2026-10-08：kit 4366 盒 = 体素 4342 + 可变形 24（梁底倒角 18 / 帽梁斜底 6），107907 B，35.19×16.94×5.88 格，文字 1838 像素、灯笼 14；B04 1676 盒 / 40455 B；B05 1685 盒 / 40655 B；B06 1108 盒 / 25688 B；**4 份 min 一致 = [0,0,6] 拼接自检 PASS**；lt_root + lt_tree 四份全过 ✓ + lt_geom 24 盒 0 问题 ✓） |

## 说明
- `nexus_lab.txt` / `neon_tower.txt` / `neon_city.txt` / `ramen_shop.txt` / `cyber_lab.txt` 等大蓝图**不入库**（脚本可重新生成）。
- `lt_src/`、`cc_src/` 反编译源码与各 jar 也不入库（只读参考）。
- 样品（`samples/`）：office_chair.txt（椅子）、med_bed.txt（床）、service_ladder.txt（梯子）、lab_door.txt（推拉门）、mech_test.txt（机关测试台）、loop_fan.txt（自转扇叶）、probe_187.txt + probe_187_safe.txt + probe_A~I/probe_F10（1.5.87 探针与单样品切片）、**broken_probe_187_timeline224.txt / broken_probe_E_timeline224.txt（崩溃反例夹具，lt_tree 必须报错）**。
- 文档：`NOTES.md`（环境/结论/审美/进度/测试记录/1.5.87 基线核对）、`HANDOFF.md`（交接 + 源码结论 + 测试清单）、`DESIGN.md`（天梯城设计稿 v2 + R1~R8）、`PLAN.md`（天梯城**总图 v3**）、`PLAN_v2_old.md`（旧总图 v2，已作废）、`PLAN_v1_old.md`（旧 v1 街区总图，已作废）。