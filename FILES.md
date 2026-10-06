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
| lt_mass.py | 天梯城体块模型 v0：地形（两山 + 斜穿峡谷 + 台地量化）、天梯（平台/三主塔/环梁/缆束/对接环/发射塔）、4 座穿楼塔、5 条线路（磁浮/连廊/索道/能网/光瀑）；手写 gzip+NBT 出 schematic，自带回读自检 + 俯视高度图 + 对角剖面 + ASCII 高度图 | 无（纯计算） | mass_v0.schematic、mass_v0_top.png、mass_v0_sec.png | 2026-10-06（自检：尺寸一致 ✓ 字节级回读一致 ✓ 非空气 499623 块） |
| lt_verify_schem.py | **独立**校验 .schematic：gzip 魔数、解压后前 12 字节必须 `0A 00 09 "Schematic"`、根标签名、根下全部键与类型、关键键类型/长度、文件是否被完整消费（自带另一套极简 NBT 读取器，**不复用 lt_mass.py 的代码**） | schematic 文件 | 无（只打印） | 2026-10-06（mass_v0.schematic：所有检查通过 ✓，verify_exit=0） |
| lt_probe_split.py | 把 `probe_187.txt` **切片**成单样品文件 `probe_A..I.txt`+`probe_F10.txt`（各带独立根 fixed），并生成去掉嫌疑样品的 `probe_187_safe.txt`；顺带逐样品检查时间轴数组首元素是否 0~3（本次就是靠它+崩溃报告定位到 E） | probe_187.txt | probe_A..I.txt、probe_F10.txt、probe_187_safe.txt | 2026-10-06（10 份全部 lt_root 断言通过 + lt_tree [问题] 无） |
| lt_density.py | **精度压力样品**：6 格宽 × 8 格高 × 2 格厚金属舱壁，表面全细节（2px 面板分缝 4×4 网格 / 288 颗 1px 铆钉 / 3px 圆形截面管线(SDF) / 一组散热格栅 / 2 处 1px 青色 FCB 指示条）；自带报告：盒子数、占用格数、每格盒子数、**每表面格盒子数**、规模估算 | 无（自建体素 + SDF） | density_test.txt | 2026-10-06（lt_root ✓ + lt_tree ✓；263 盒 / 144 格 / 表面 48 格上 261 盒 ≈ 5.4 盒·每表面格） |
| lt_tbox.py | **187 原生可变形盒编解码**（`LittleTransformableBox`）：`decode/encode`、K 样本往返逐位一致；位布局见 NOTES 第 22 条 | `[I;…]` 数组 | 无（库 + CLI `decode`） | 2026-10-06（K 往返 True ✔） |
| lt_probe2.py | 按"门会把 children 搬进动画"结论重做的探针：控制器 light(level:0) 下**并列**放门与灯 ⇒ probe_E2 / F2 / F2x10 / J2 | 无（自建体素） | probe_E2/F2/F2x10/J2.txt | 2026-10-06（4 份 lt_root ✓ + lt_tree ✓） |
| lt_h23.py | 用原生可变形盒做**无台阶**的 1/4 圆柱墙（16 个多边形切面）：H2 石英 / H3 FCB 灰 | lt_tbox | probe_H2.txt、probe_H3.txt | 2026-10-06（各 16 盒，lt_root ✓ + lt_tree ✓） |
| lt_h23b.py | H2b/H3b：**只向内偏移** + 每切面按格高拆 4 段的可变形盒圆柱墙（规避 `setBounds` 夹回 AABB 的风险） | lt_tbox | probe_H2b.txt、probe_H3b.txt | 2026-10-06（各 64 盒，lt_root ✓ + lt_tree ✓） |
| lt_root.py | **根层守卫**：根有 children 就必须有 structure（缺则插入 + 硬断言）；CLI `selftest`/`verify`/`diff` | 根层文本（库） | 无（库；CLI 只打印） | 2026-10-05（selftest 全过 + verify 全部样品） |
| lt_tree.py | 导入文本树/语法校验器：递归解析 tiles/structure/children，查 6 分量与 **7/11 分量可变形盒**、上界排他、count、min/size（全树并集）、structure id（含 1.5.87 新增 id）、advancedDoor 的 offGrid 陷阱；**新增守卫①时间轴形态（首元素 0~3、长度 2+3*count(+hermite 3)）②axisCenter 必须落在本节点盒子包围盒内**；有问题返回 exit 1 | 蓝图 txt | 无（只打印；退出码 0/1） | 2026-10-06（12 份探针全过；2 份反例夹具必须报错 ✔） |

## 说明
- `nexus_lab.txt` / `neon_tower.txt` / `neon_city.txt` / `ramen_shop.txt` / `cyber_lab.txt` 等大蓝图**不入库**（脚本可重新生成）。
- `lt_src/`、`cc_src/` 反编译源码与各 jar 也不入库（只读参考）。
- 样品（`samples/`）：office_chair.txt（椅子）、med_bed.txt（床）、service_ladder.txt（梯子）、lab_door.txt（推拉门）、mech_test.txt（机关测试台）、loop_fan.txt（自转扇叶）、probe_187.txt + probe_187_safe.txt + probe_A~I/probe_F10（1.5.87 探针与单样品切片）、**broken_probe_187_timeline224.txt / broken_probe_E_timeline224.txt（崩溃反例夹具，lt_tree 必须报错）**。
- 文档：`NOTES.md`（环境/结论/审美/进度/测试记录/1.5.87 基线核对）、`HANDOFF.md`（交接 + 源码结论 + 测试清单）、`DESIGN.md`（天梯城设计稿 v2 + R1~R8）、`PLAN.md`（天梯城总图 v2）、`PLAN_v1_old.md`（旧 v1 街区总图，已作废）。