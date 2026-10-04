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
| lt_ramen.py | 一番拉面店外壳与门面（唯一带真机通行检查：0.6×1.8 玩家盒） | 无（numpy/PIL 自建） | ramen_shop.txt | 2026-10-05（仅 py_compile + 守卫形状回归；未整跑。根无 children，守卫为预留） |
| lt_ramen_shell.py | 拉面店外壳的 /fill 指令（自带 BFS 通行检查） | 无 | ramen_shell.txt | 未验证 |
| lt_mech.py | 机关测试台：卷帘门+按钮 / 吧台翻板 / 冰柜门 / 穿透暖帘 | 无（自建体素） | mech_test.txt | 2026-10-05（重跑 + 根层逐字节比对一致） |
| lt_mech_v.py | 机关对照样品 v1~v3（门可右键无按钮 / 有按钮 / 门禁右键） | 无（自建体素） | mech_v1_门可右键_无按钮.txt、mech_v2_门可右键_有按钮.txt、mech_v3_原版_门禁右键_有按钮.txt | 2026-10-05（重跑，守卫自动插 structure） |
| lt_mech_v45.py | 由 v2/v3 派生 v4（**豁免**负对照：根无 structure）/ v5（根带 structure） | mech_v2/v3 的 txt | mech_v4_按钮门触发子门_根无结构.txt、mech_v5_根带结构_门禁右键_有按钮.txt | 2026-10-05（重跑 + 反做还原校验） |
| lt_root.py | **根层守卫**：根有 children 就必须有 structure（缺则插入 + 硬断言）；CLI `selftest`/`verify`/`diff` | 根层文本（库） | 无（库；CLI 只打印） | 2026-10-05（selftest 全过 + verify 全部样品） |
| lt_tree.py | 导入文本树/语法校验器：递归解析 tiles/structure/children，查 6 分量、上界排他、count、min/size、structure id、offGrid 陷阱 | 蓝图 txt | 无（只打印） | 2026-10-05（校验 mech_test.txt + mech_v1~v5 共 6 份，全部无问题） |

## 说明
- `nexus_lab.txt` / `neon_tower.txt` / `neon_city.txt` / `ramen_shop.txt` / `cyber_lab.txt` 等大蓝图**不入库**（脚本可重新生成）。
- `lt_src/`、`cc_src/` 反编译源码与各 jar 也不入库（只读参考）。
- 样品（`samples/`）：office_chair.txt（椅子）、med_bed.txt（床）、service_ladder.txt（梯子）、lab_door.txt（推拉门）、mech_test.txt（机关测试台）。