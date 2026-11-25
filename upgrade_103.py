"""1.0.3: custom Sephiroth portrait and individually animated silver hair."""
from pathlib import Path
import sys,math,struct,zlib,re
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
path=assets/'one_winged_angel.png'
data=path.read_bytes();pos=8;comp=b''
while pos<len(data):
    n=struct.unpack('>I',data[pos:pos+4])[0];k=data[pos+4:pos+8];v=data[pos+8:pos+8+n];pos+=12+n
    if k==b'IHDR':ow,oh,depth,ctype,_,_,_=struct.unpack('>IIBBBBB',v);assert (depth,ctype)==(8,6)
    elif k==b'IDAT':comp+=v
raw=zlib.decompress(comp);stride=ow*4+1
assert all(raw[y*stride]==0 for y in range(oh))
# Existing coat/wing/sword UVs are preserved in upper-left quarter.
S=8;W=256*S;pix=bytearray(W*W*4)
for y in range(128*S):
    oy=y*oh//(128*S);row=raw[oy*stride+1:(oy+1)*stride]
    scaled=b''.join(row[(x*ow//(128*S))*4:(x*ow//(128*S))*4+4] for x in range(128*S))
    pix[y*W*4:y*W*4+len(scaled)]=scaled
cx=128;cy=0;rh=0;lines=[]
def clamp(v):return max(0,min(255,round(v)))
def mix(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def shade(mat,u,v,face):
    if mat=='skin':
        # Narrow, severe adult eyes, pale warm skin, softly shaded cheeks.
        c=(209,185,172)
        if face=='front':
            cheek=math.exp(-((abs(u-.5)-.25)/.16)**2-((v-.62)/.20)**2)
            nose=math.exp(-((u-.5)/.075)**2-((v-.55)/.22)**2)
            light=.57+.19*cheek+.18*nose-.18*(abs(u-.5)*2)**2
            c=mix((125,99,98),(246,220,200),max(0,min(1,light)))
            # Dark eye sockets and slanted, narrow eyelids; no rectangular brows.
            for center in (.255,.745):
                s=-1 if center<.5 else 1
                x=(u-center)/.19; yy=(v-(.415-.040*s*x))/.067
                socket=math.exp(-x*x*1.6-((v-.415)/.12)**2)
                c=mix(c,(117,89,91),.26*socket)
                if abs(x)<1 and abs(yy)<(.90-.48*abs(x)):
                    c=(50,42,47)
                    if abs(yy)<(.64-.43*abs(x)):
                        c=(225,218,204)
                        if abs(x+.04*s)<.40:
                            c=(61,145+30*(1-abs(yy)),112)
                            if abs(x+.04*s)<.115:c=(15,46,39)
                            if -.22<yy<.04 and -.29<x<-.12:c=(239,251,228)
                brow=.300-.035*s*x
                if abs(x)<.96 and abs(v-brow)<.018*(1-.45*abs(x)):c=(91,79,79)
            if .46<u<.54 and .45<v<.65:
                c=mix(c,(239,213,192),.22)
            if .39<u<.61 and abs(v-(.778+.018*(abs(u-.5)*7)))<.010:
                c=(102,72,75)
            if .43<u<.57 and .79<v<.81:c=(185,138,131)
            if v>.84:c=mix(c,(141,113,108),min(.42,(v-.84)*2.7))
        elif face in ('left','right'):
            c=mix((145,118,111),(220,190,173),.55+.18*math.sin(v*math.pi))
            ear=((u-.52)/.19)**2+((v-.50)/.24)**2
            if ear<1:c=mix(c,(190,139,125),.55)
            if ear<.40:c=(141,99,93)
        else:c=mix((139,116,113),(224,201,186),.5)
    elif mat=='nose':
        c=mix((155,124,117),(233,206,188),.45+.4*math.sin(u*math.pi))
    elif mat=='hair':
        # Fine silver/platinum fibers, dark roots and cool metallic highlights.
        strand=.5+.5*math.sin(u*math.pi*10+math.sin(v*5)*.28)
        fine=.5+.5*math.sin(u*math.pi*33+v*.75)
        root=.68+.32*min(1,v*4)
        t=(.30+.34*strand+.19*fine+.12*math.sin(u*math.pi))*root
        c=mix((92,85,88),(245,237,229),max(0,min(1,t)))
        if strand>.98:c=mix(c,(253,246,237),.32)
    else:c=(202,184,172)
    f={'top':1.03,'bottom':.87,'left':.96,'right':.98,'front':1,'back':.93}[face]
    return tuple(clamp(x*f) for x in c)
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>256:cx=128;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh)
    assert v+hh<=256,(mat,u,v,ww,hh)
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:
        for j in range(fh*S):
            for i in range(fw*S):
                c=shade(mat,(i+.5)/(fw*S),(j+.5)/(fh*S),face)
                off=((fy*S+j)*W+fx*S+i)*4;pix[off:off+4]=bytes((*c,255))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    shape='CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)
    pose='PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+')'
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",{shape},{pose});')
# Keep standard named head part and an empty hat for HumanoidModel.
part('newHead','r','head',(0,0,0),(0,0,0),[(-4,-8,-4,8,8,8,'skin')])
part('nose','newHead','nose',(0,-3.8,-4),(0,0,0),[(-.45,-.6,-.40,1,2,1,'nose')])
# Hair is built as a rounded stepped crown, rather than a horizontal helmet rim.
part('silver','newHead','silver',(0,0,0),(0,0,0),[(-3.5,-8.9,-2.9,7,2,6,'hair'),(-2.8,-9.5,-2,6,2,4,'hair'),(-4,-7.7,1.5,8,5,3,'hair')])
# Seven articulated main rear locks (existing attack code uses these names).
for i in range(7):
    x=-3.55+i*1.18
    part('strand'+str(i),'silver','strand'+str(i),(x,-7.8,3.8+.35*math.cos(i)),(.06,0,(i-3)*.045),[(-.65,0,-.65,1,12+(i%3),2,'hair'),(-.5,11+(i%3),-.4,1,12+(i%2)*2,1,'hair'),(-.35,22+(i%3),-.3,1,4,1,'hair')])
# Separate surface strands swept from the central part towards the temples.
for i in range(10):
    s=-1 if i<5 else 1;k=i%5
    part('crown'+str(i),'newHead','crown'+str(i),(s*(.5+k*.65),-8.45+.15*k,-2.6+k*.24),(.22,0,-s*(.18+k*.11)),[(-.45,-.4,-.5,1,4+k%2,2,'hair')])
# Side locks preserve the attack animation anchors; lengths reach below waist.
for i,s in enumerate((-1,1)):
    part('lock'+str(i),'newHead','lock'+str(s),(s*3.85,-6.7,-.8),(.08,0,s*.055),[(-.65,-.5,-.6,1,13,2,'hair'),(-.55,12,-.5,1,12,1,'hair'),(-.4,23,-.4,1,4,1,'hair')])
    for j in range(3):
        part('side'+str(i)+str(j),'lock'+str(i),'side'+str(j),(s*(.25+j*.22),-.15+j*.8,-.7+j*.43),(.04,0,s*(j-1)*.055),[(-.45,0,-.4,1,20+j*2,1,'hair'),(-.35,19+j*2,-.3,1,4,1,'hair')])
# Central part: long, fine locks sweep away from eyes and down front of coat.
for i,s in enumerate((-1,1)):
    for j in range(3):
        part('fr'+str(i)+str(j),'newHead','front'+str(i)+str(j),(s*(.55+j*.95),-8.5+.18*j,-3.7-.12*j),(0,0,-s*(.28+j*.12)),[(-.38,0,-.38,1,5+j,1,'hair')])
    part('long'+str(i),'newHead','frontLong'+str(i),(s*3.5,-4.5,-3.45),(.04,0,s*.035),[(-.45,0,-.45,1,13,1,'hair'),(-.35,12,-.35,1,10,1,'hair')])
assert cy+rh<=256
p=java/'FallenClient.java';s=p.read_text(encoding='utf-8')
start=s.index('        h.addOrReplaceChild("silver"')
end=s.index('        PartDefinition wing=',start)
# Existing coat tails remain unchanged.
coat='''        for(int side:new int[]{-1,1})b.addOrReplaceChild("coat"+side,CubeListBuilder.create().texOffs(0,64).addBox(-3,0,-2,6,13,4),PartPose.offsetAndRotation(side*2.5f,10,0,.1f,0,side*.08f));
'''
s=s[:start]+'\n'.join(lines)+'\n'+coat+s[end:]
s=s.replace('LayerDefinition.create(m,128,128)','LayerDefinition.create(m,256,256)',1)
anchor='super.setupAnim(e,swing,amount,age,yaw,pitch);'
assert anchor in s
s=s.replace(anchor,anchor+'''
            head.xScale=.90f;head.yScale=1.075f;head.zScale=.94f;hat.visible=false;
            for(int i=0;i<10;i++){int side=i<5?-1:1,k=i%5;head.getChild("crown"+i).zRot=-side*(.18f+k*.11f)+(float)Math.sin(age*.10f+i*.6f)*.024f;}
            for(int i=0;i<2;i++){int side=i==0?-1:1;
                for(int j=0;j<3;j++)head.getChild("front"+i+j).zRot=-side*(.28f+j*.12f)+(float)Math.sin(age*.16f+j*.4f+i)*.035f;
                head.getChild("frontLong"+i).xRot=.04f+(float)Math.sin(age*.14f+i)*.06f;
            }
''',1)
# Add independent hair reactions after the established attack animation.
anchor='hairBack.xRot=-thrust*.22f;'
assert anchor in s
s=s.replace(anchor,anchor+'''for(int i=0;i<2;i++)head.getChild("frontLong"+i).xRot=-thrust*.32f+(float)Math.sin(age*.17f+i)*.045f;''',1)
p.write_text(s,encoding='utf-8')
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
print('Sephiroth: new portrait UV, individual flowing platinum locks, original combat model preserved')
