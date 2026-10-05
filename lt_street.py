# lt_street.py  主街路面：4 段×16 格，每段一个蓝图；只占世界 y=3 一层（人行道顶=地面，车道低 2 像素）
from lt_np import Vol, F
WX,WY,WZ=-800,3,313
SEGS,L,D=4,256,176
C1,C2=136,184                       # 斑马线（全局像素 x），正对拉面店东侧小巷
PUDDLE=[(40,100,14,7),(300,70,20,8),(520,112,12,6),(700,60,18,9),(930,96,15,7)]
PATCH=[(200,48,40,24),(610,96,32,30)]
DRAIN=[g for g in range(32,SEGS*L,128) if not (C1-24<g<C2+8)]

def seg(i):
    x0=i*L; E=x0+L; v=Vol((L,16,D),(0,0,0),(WX+i*16,WY,WZ)); M=v.M
    ASP=M("minecraft:concrete:7"); BK=M("minecraft:concrete:15"); WALK=M("minecraft:concrete:8")
    CURB=M("minecraft:double_stone_slab:8"); IR=M("minecraft:iron_block"); WH=M("minecraft:concrete")
    YL=M(F("#e8c020")); YLD=M(F("#a08414")); WET=M(F("#6f8fb8","trans"))
    def B(m,g1,y1,z1,g2,y2,z2):
        a,b=max(g1-x0,0),min(g2-x0,L)
        if a<b: v.box(m,a,y1,z1,b,y2,z2)
    def P(m,g,y,z): B(m,g,y,z,g+1,y+1,z+1)
    # 1 基层：人行道 / 路缘石 / 车道 / 边沟
    B(WALK,x0,0,0,E,16,29); B(WALK,x0,0,147,E,16,D)
    B(CURB,x0,0,29,E,16,32); B(CURB,x0,0,144,E,16,147)
    B(ASP,x0,0,32,E,14,144)
    B(CURB,x0,13,32,E,14,36); B(CURB,x0,13,140,E,14,144)
    # 2 人行道砖缝（凹 1 像素，缝底深灰）
    def groove(g1,z1,g2,z2): B(0,g1,15,z1,g2,16,z2); B(ASP,g1,14,z1,g2,15,z2)
    for g in range(x0,E,8): groove(g,0,g+1,29); groove(g,147,g+1,D)
    for z in (0,8,16,24,152,160,168): groove(x0,z,E,z+1)
    # 3 盲道：导向条 + 点状提示
    def bars(z1,z2,yt):
        B(0,x0,yt-1,z1,E,yt,z2); B(YLD,x0,yt-2,z1,E,yt-1,z2)
        for z in range(z1,z2,2): B(YL,x0,yt-1,z,E,yt,z+1)
        for g in range(x0,E,8): B(YLD,g,yt-1,z1,g+1,yt,z2)
    def dots(g1,g2,z1,z2,yt):
        B(0,g1,yt-1,z1,g2,yt,z2); B(YLD,g1,yt-2,z1,g2,yt-1,z2)
        for g in range(g1,g2):
            if g%3==1:
                for z in range(z1,z2):
                    if (z-z1)%3==1: P(YL,g,yt-1,z)
    bars(9,16,16); bars(161,168,16)
    # 4 斑马线两端：两级路缘坡道 + 提示砖
    B(0,C1,15,17,C2,16,32); B(0,C1,14,24,C2,15,32)
    B(0,C1,15,144,C2,16,160); B(0,C1,14,144,C2,15,153)
    dots(C1,C2,9,16,16); dots(C1,C2,161,168,16); dots(C1,C2,24,31,14); dots(C1,C2,145,152,14)
    # 5 沥青补丁 → 标线 → 斑马线/停止线
    for g,z,l,w in PATCH: B(BK,g,13,z,g+l,14,z+w)
    B(WH,x0,13,40,E,14,42); B(WH,x0,13,134,E,14,136)
    for g in range(0,SEGS*L,80):
        if g+48<=C1-8 or g>=C2+8: B(WH,g,13,87,g+48,14,89)
    B(ASP,C1,13,40,C2,14,42); B(ASP,C1,13,134,C2,14,136)
    for z in range(44,132,16): B(WH,C1+4,13,z,C2-4,14,z+8)
    B(WH,C1-12,13,42,C1-9,14,88); B(WH,C2+9,13,88,C2+12,14,134)
    # 6 积水（两个椭圆叠成不规则形）
    for cx,cz,rx,rz in PUDDLE:
        for ex,ez,ax_,az_ in ((cx,cz,rx,rz),(cx+rx*.6,cz+rz*.4,rx*.6,rz*.7)):
            for g in range(int(ex-ax_)-1,int(ex+ax_)+2):
                if not x0<=g<E: continue
                for z in range(int(ez-az_)-1,int(ez+az_)+2):
                    if 36<=z<140 and ((g+.5-ex)/ax_)**2+((z+.5-ez)/az_)**2<=1: P(WET,g,13,z)
    # 7 井盖（外圈缝 + 十字 + 内环，凹 1 像素）
    cx,cz=x0+208,(64 if i%2==0 else 112)
    for g in range(cx-12,cx+12):
        for z in range(cz-12,cz+12):
            d=((g+.5-cx)**2+(z+.5-cz)**2)**.5
            if d>11.5: continue
            B(IR,g,11,z,g+1,14,z+1)
            if 9.5<d<=10.5: P(0,g,13,z); P(BK,g,12,z)
            elif abs(g+.5-cx)<1 or abs(z+.5-cz)<1 or 5.5<d<=6.5: P(0,g,13,z)
    # 8 雨水箅子 + 路缘进水口
    for g in DRAIN:
        for z1 in (32,136):
            B(IR,g,12,z1,g+16,14,z1+8); B(BK,g+1,9,z1+1,g+15,12,z1+7)
            for k in range(g+2,g+14,3): B(0,k,12,z1+1,k+1,14,z1+7)
        B(0,g+2,14,30,g+14,15,32); B(BK,g+2,14,29,g+14,15,30)
        B(0,g+2,14,144,g+14,15,146); B(BK,g+2,14,146,g+14,15,147)
    return v.export(f"street_{i}.txt",f"street_{i}")

for i in range(SEGS): seg(i)