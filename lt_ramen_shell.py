import sys
from collections import deque
X,Y,Z=map(int,sys.argv[1:4])   # 西北角地面方块坐标
W,D,H=9,13,8
F=[]  # (x1,y1,z1,x2,y2,z2,方块,数据,模式)
def f(a,b,c,d,e,g,blk,meta=0,mode=""):F.append((a,b,c,d,e,g,blk,meta,mode))
# 结构
f(0,0,0,8,0,12,"concrete",7)                 # 基础
f(0,1,0,8,7,12,"concrete",15,"hollow")       # 黑色外壳
f(1,1,1,7,1,11,"air")                        # 挖空hollow封住的底面
f(1,0,1,7,0,6,"planks",1)                    # 客区木地板
f(1,0,8,7,0,11,"quartz_block",0)             # 后厨地砖
f(1,6,1,7,6,11,"concrete",7)                 # 吊顶
f(2,6,2,6,6,5,"air")                         # 灯槽凹口
f(2,7,2,6,7,5,"sea_lantern")                 # 槽内光源
f(3,6,9,4,6,10,"air");f(3,7,9,4,7,10,"iron_block")  # 排烟口
# 门面
f(3,1,0,5,3,0,"air")                         # 正门
f(1,2,0,2,4,0,"stained_glass",3);f(6,2,0,7,4,0,"stained_glass",3)
f(0,4,-1,8,4,-1,"concrete",14)               # 雨棚
f(0,5,-1,8,5,-1,"sea_lantern")               # 雨棚灯带
f(0,6,0,8,6,0,"concrete",6)                  # 品红檐线
# 吧台线（占位，下轮换模块）与后门
f(1,1,7,5,1,7,"planks",1)
f(6,1,12,7,3,12,"air")
# ---------- 输出指令 ----------
out=[]
for a,b,c,d,e,g,blk,m,mode in F:
    s=f"/fill {X+a} {Y+b} {Z+c} {X+d} {Y+e} {Z+g} minecraft:{blk} {m}"
    out.append(s+(" "+mode if mode else ""))
open("ramen_shell.txt","w",encoding="utf-8").write("\n".join(out))
print("ramen_shell.txt",len(out),"条指令")
# ---------- 通行检查 ----------
S={}
for a,b,c,d,e,g,blk,m,mode in F:
    for x in range(a,d+1):
        for y in range(b,e+1):
            for z in range(c,g+1):
                edge=x in(a,d) or y in(b,e) or z in(c,g)
                if mode=="hollow" and not edge: S[(x,y,z)]=False
                else: S[(x,y,z)]= blk!="air"
solid=lambda x,y,z: S.get((x,y,z), y<=0 and not(0<=x<=8 and 0<=z<=12) and y==0 or y<0)
def ok(x,z): return solid(x,0,z) and not solid(x,1,z) and not solid(x,2,z)
def path(s,t):
    q=deque([s]);seen={s:None}
    while q:
        c=q.popleft()
        if c==t:
            n=0
            while seen[c]:c=seen[c];n+=1
            return n
        for dx,dz in((1,0),(-1,0),(0,1),(0,-1)):
            n=(c[0]+dx,c[1]+dz)
            if n not in seen and -3<=n[0]<=11 and -3<=n[1]<=15 and ok(*n):
                seen[n]=c;q.append(n)
    return None
routes={"正门→座位":((4,-2),(3,5)),"正门→后厨":((4,-2),(6,10)),"后厨→后门外":((6,10),(7,14))}
allok=True
for k,(s,t) in routes.items():
    r=path(s,t);allok&=r is not None
    print(k, f"通过，步数 {r}" if r is not None else "不通！")
print("通行检查:", "全部通过" if allok else "失败")