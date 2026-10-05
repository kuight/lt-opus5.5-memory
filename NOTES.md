# LittleTiles 1.12.2 建筑项目备忘

## 环境
- MC 1.12.2 Forge，LittleTiles pre199_19，FlatColoredBlocks，Little Importer，WorldEdit
- 存档：超平坦；工作目录 E:\work\建筑\
- 执行 agent：DeepSeek harness 上的 DeepSeek V4.1 Flash；每次会话先写 probe.txt 并用 dir 确认
- 脚本必须在 E:\work\建筑\ 下运行（lt_colors.py 用相对路径读 CSV）

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

## 用户审美偏好
- 要极致细节，全程用小方块，不要火柴盒式的造型
- 细节要能看懂、有内涵；乱堆招牌、伪汉字是减分项
- 一步一步做大，先做样板再铺开

## 当前进度
- 拉面店外壳（ramen_shop.txt）已通过；待改：灯槽太亮、东西外墙空、暖帘“拉”字、屋顶风管、室内左墙发亮方块
- 机关已验证：卷帘门+按钮、翻板、冰柜门、穿透暖帘
- 下一轮：木格推拉门、L 形吧台、调料架、吧台凳、食券机、煮面炉、排烟罩、门面卷帘

## 测试记录
- 2026-10-05 mech A（v3+fixed）：按钮能开，右键门打不开 ✔