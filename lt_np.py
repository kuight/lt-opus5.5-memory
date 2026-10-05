# lt_np.py  街区模块通用库：numpy 体素 + 贪心合并导出（1像素=1/16格）
import numpy as np
import lt_colors, lt_root
def F(h,k="solid"): return lt_colors.fc(h,k)

class Vol:
    """V[下标] = 局部像素 + O；局部像素 (0,0,0) 所在格 = 世界格 W"""
    def __init__(s,size,O,W):
        assert all(o%16==0 for o in O),"O 必须是 16 的倍数"
        s.V=np.zeros(size,np.uint8); s.O=O; s.W=W; s.MATS=[None]; s.MID={}
    def M(s,n):
        if n not in s.MID:
            s.MID[n]=len(s.MATS); s.MATS.append(n)
            assert len(s.MATS)<256,"材质超过 255 种"
        return s.MID[n]
    def box(s,m,x1,y1,z1,x2,y2,z2):
        a,b,c=s.O
        assert min(x1+a,y1+b,z1+c)>=0,"坐标越界（负下标会回绕）"
        s.V[x1+a:x2+a,y1+b:y2+b,z1+c:z2+c]=m
    def px(s,m,x,y,z): s.box(m,x,y,z,x+1,y+1,z+1)
    def export(s,fn,name,structure=None):
        V=s.V; SX,SY,SZ=V.shape
        ax=[np.nonzero(V.any(axis=tuple(j for j in range(3) if j!=i)))[0] for i in range(3)]
        lo=[int(a[0]) for a in ax]; hi=[int(a[-1])+1 for a in ax]; base=[l//16*16 for l in lo]
        parts=[]; cnt=0; Wv=np.zeros_like(V)
        for mi in range(1,len(s.MATS)):
            R=(V==mi)
            if not R.any(): continue
            bx=[]
            for x in range(lo[0],hi[0]):
                sl=R[x]
                while True:
                    y,z=divmod(int(sl.argmax()),SZ)
                    if not sl[y,z]: break
                    r=sl[y,z:]; z2=z+(len(r) if r.all() else int(r.argmin()))
                    y2=y+1
                    while y2<SY and sl[y2,z:z2].all(): y2+=1
                    x2=x+1
                    while x2<SX and R[x2,y:y2,z:z2].all(): x2+=1
                    R[x:x2,y:y2,z:z2]=False; Wv[x:x2,y:y2,z:z2]=mi
                    bx.append((x-base[0],y-base[1],z-base[2],x2-base[0],y2-base[1],z2-base[2]))
            cnt+=len(bx); b=",".join("[I;%d,%d,%d,%d,%d,%d]"%t for t in bx)
            parts.append(('{bBox:%s,tile:{block:"%s"}}' if len(bx)==1 else '{boxes:[%s],tile:{block:"%s"}}')%(b,s.MATS[mi]))
        t="{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}"%(",".join(parts),
            *[lo[i]-base[i] for i in range(3)],*[hi[i]-lo[i] for i in range(3)],cnt)
        if structure:                                   # 根层直接挂结构（如 noclip 暖帘 / advancedDoor 扇叶）
            if not structure.startswith("{"):            # 允许传 id:"x",name:"y" 这种不带花括号的写法
                structure = "{" + structure + "}"
            k=lt_root.tiles_end(t); t=t[:k]+",structure:"+structure+t[k:]
        t=lt_root.fix(t,name,tag=fn)
        open(fn,"w",encoding="utf-8").write(t)
        start=tuple(s.W[i]+(base[i]-s.O[i])//16 for i in range(3))
        ok=np.array_equal(Wv,V)
        print(fn,f"{len(t.encode())/1024:.0f} KB | 小块 {cnt} | 材质 {len(parts)} | 尺寸 {[(hi[i]-lo[i])/16 for i in range(3)]} 格 | 无损 {ok} | 导入起点 {start}")
        assert ok,"无损校验失败"
        return start