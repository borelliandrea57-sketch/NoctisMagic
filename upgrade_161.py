"""1.6.1: second Code Geass revision, clean front-projected faces and distinct costume silhouettes."""
from pathlib import Path
import sys, math, struct, zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
def edit(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b,1)
edit('import it.noctis.magic.SculptedGuestsClient.Part;','import it.noctis.magic.SculptedGuestsClient.Part;\nimport it.noctis.magic.SculptedGuestsClient.V;\nimport it.noctis.magic.SculptedGuestsClient.Q;')
edit('    static class M extends EntityModel<DramaGuest>{','''    static V faceVertex(V v,boolean front){
        float u=front?.5f+v.x()/7.5f:.035f;
        float z=v.z();
        if(front&&v.nz()<-.5f){
            float dx=v.x()/.52f,dy=(v.y()+2.65f)/1.0f;
            z-=.18f*(float)Math.exp(-dx*dx-dy*dy);
        }
        return new V(v.x(),v.y(),z,u,v.v(),v.nx(),v.ny(),v.nz());
    }
    static void projectFace(Part p){
        for(int i=0;i<p.faces.size();i++){
            Q q=p.faces.get(i);if(q.tile()!=6)continue;
            boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
            p.faces.set(i,new Q(faceVertex(q.a(),f),faceVertex(q.b(),f),faceVertex(q.c(),f),faceVertex(q.d(),f),6));
        }
    }
    static class M extends EntityModel<DramaGuest>{''')
edit('float w=cc?3.35f:3.05f;','float w=cc?3.08f:3.02f;')
edit('head.loft(6,32,','head.loft(6,64,')
edit('cc?2.55f:2.3f,2.25f,-.55f,0,-.25f,cc?1.65f:1.25f,1.45f,0,0,-.3f,.55f,.75f','cc?2.55f:2.45f,2.25f,-.55f,0,-.25f,cc?1.65f:1.52f,1.45f,0,0,-.3f,.80f,.82f')
edit('head.oval(7,0,-2.7f,-2.75f,.30f,.43f,.34f);','projectFace(head);')
edit('head.loft(8,24,-8.7f,0,.1f,.50f,.60f,-8.5f,0,.1f,2.35f,2.25f,-7.5f,0,.2f,3.4f,3.05f,-6.1f,0,.3f,3.55f,3.15f);','''head.loft(8,40,-8.85f,0,.25f,.45f,.55f,-8.55f,0,.15f,2.2f,2.18f,-7.55f,0,.2f,3.28f,3.0f,-6.25f,0,.36f,3.39f,3.04f);''')
edit('float x=cc?-2.9f+i*.83f:-2.8f+i*1.08f;','float x=cc?-2.73f+i*.78f:-2.68f+i*1.04f;')
edit('Part fringe=head.child(x,-7.2f,-2.5f);','Part fringe=head.child(x,-7.65f,-2.12f);')
edit('float d=cc?(i-3.5f)*.19f:-.85f+i*.12f;','float d=cc?(i-3.5f)*.10f:1.12f-i*.13f;')
edit('float end=cc?2.55f+(i%3)*.23f:2.9f+(i%3)*.45f;','float end=cc?2.12f+(i%3)*.17f:2.1f+(i==0||i==5?1.55f:i==1?1.0f:.25f);')
edit('fringe.loft(8,12,-.65f,0,.35f,.76f,.74f,.6f,d*.25f,-.2f,.82f,.55f,1.65f,d*.6f,-.45f,.65f,.38f,end,d,-.4f,.04f,.06f);','''fringe.loft(8,20,-.55f,0,.54f,.55f,.64f,.4f,d*.24f,-.25f,.66f,.59f,1.35f,d*.64f,-.60f,.57f,.39f,end,d,-.38f,.035f,.045f);''')
edit('back.loft(8,24,-.6f,0,0,2.85f,1.6f,2,0,.4f,3.2f,1.65f,6,0,1.2f,3.4f,1.55f,11,0,2.1f,3.7f,1.5f,16,0,2.4f,3.1f,1.1f,20,0,2.6f,2.1f,.35f);','''back.loft(8,36,-.6f,0,0,2.65f,1.42f,2,0,.4f,3.02f,1.48f,6,0,1.2f,3.25f,1.41f,11,0,2.1f,3.6f,1.31f,16,0,2.6f,3.55f,1.10f,22,0,2.9f,2.55f,.35f);''')
edit('q.loft(8,10,0,0,0,.58f,.6f,5,(j-3)*.18f,.4f,.78f,.73f,11,(j-3)*.30f,1.25f,.80f,.65f,17,(j-3)*.45f,1.9f,.65f,.5f,20+(j%3), (j-3)*.5f,1.9f,.04f,.07f);','''q.loft(8,18,0,0,0,.60f,.62f,5,(j-3)*.18f,.4f,.80f,.75f,11,(j-3)*.38f,1.25f,.83f,.65f,17,(j-3)*.52f,2.2f,.75f,.52f,23+(j%3), (j-3)*.60f,2.5f,.035f,.045f);''')
edit('lock.loft(8,12,-.8f,0,0,.74f,1.05f,1.5f,s*.5f,-.3f,.88f,1.12f,cc?7:3.2f,s*.65f,-.2f,.72f,.75f,cc?14.8f:5.7f,s*.35f,.5f,.04f,.07f);','''lock.loft(8,20,-.8f,0,0,.74f,1.05f,1.5f,s*.45f,-.28f,.83f,1.0f,cc?7:3.2f,s*.65f,-.15f,.69f,.72f,cc?16.8f:5.5f,s*.4f,.5f,.035f,.045f);''')
# A fitted tunic and silk cravat instead of an oversized flat chest ornament.
edit('body.blade(3,0,-.3f,-1.8f,0,4.6f,-2.1f,2.9f);','body.blade(3,0,-.35f,-1.92f,0,3.4f,-2.10f,1.65f);')
edit('body.blade(3,-.55f,.7f,-2.0f,-1.0f,4.0f,-2.25f,1.0f);','body.blade(3,-.35f,.4f,-2.0f,-.7f,3.0f,-2.18f,.58f);')
edit('body.blade(3,.55f,.7f,-2.0f,1.0f,4.0f,-2.25f,1.0f);','body.blade(3,.35f,.4f,-2.0f,.7f,3.0f,-2.18f,.58f);')
edit('body.blade(5,s*2.0f,.1f,0,s*4.7f,-5.1f,1.1f,3.0f);','''body.blade(5,s*1.65f,.1f,.2f,s*3.65f,-3.9f,1.25f,2.55f);
                    for(int j=0;j<3;j++)body.oval(4,s*.65f,4.1f+j*1.3f,-1.77f,.19f,.19f,.12f);''')
edit('body.blade(4,s*2.1f,-.1f,-.18f,s*4.65f,-5.15f,.9f,.30f);','body.blade(4,s*1.75f,-.1f,-.02f,s*3.6f,-3.95f,1.05f,.23f);')
edit('body.blade(4,0,-.8f,-1.45f,0,3.2f,-2.0f,.38f);','''body.blade(4,0,-.8f,-1.45f,0,3.2f,-2.0f,.24f);
                body.oval(4,0,.85f,-1.72f,.27f,.29f,.16f);
                for(int t:new int[]{-1,1}){
                    body.blade(1,t*2.0f,7.8f,-1.34f,t*2.45f,11.2f,-1.60f,.68f);
                    body.oval(4,t*1.65f,9.7f,-1.77f,.30f,.25f,.16f);
                }''')
# Elbows and knees articulate separately, keeping a relaxed pose.
edit('final Part[] arms=new Part[2],legs=new Part[2],cape=new Part[2];','final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],knees=new Part[2],cape=new Part[2];')
a=s.index('                if(cc){\n                    arms[i].oval')
b=s.index('                // Broad animated dark cloth',a)
s=s[:a]+'''                fore[i]=arms[i].child(0,4.7f,0);
                if(cc){
                    arms[i].oval(7,0,.7f,0,1.03f,1.26f,1.04f);
                    arms[i].loft(0,24,1.9f,0,0,1.10f,1.09f,2.7f,0,0,.97f,.98f,4.75f,0,0,.77f,.80f);
                    arms[i].loft(4,24,1.8f,0,0,1.13f,1.12f,2.12f,0,0,1.11f,1.10f);
                    fore[i].loft(0,24,-.2f,0,0,.80f,.83f,1.15f,0,0,.93f,.93f,4.05f,0,0,.55f,.58f);
                }else{
                    arms[i].loft(0,24,-.65f,0,0,1.10f,1.18f,.7f,0,0,1.44f,1.35f,2.7f,0,0,1.20f,1.20f,4.8f,0,0,.90f,.93f);
                    fore[i].loft(0,24,-.2f,0,0,.92f,.96f,1.35f,0,0,1.02f,1.02f,4.05f,0,0,.70f,.75f);
                }
                fore[i].loft(4,22,3.75f,0,0,cc?.61f:.77f,cc?.64f:.80f,4.05f,0,0,cc?.60f:.75f,cc?.63f:.79f);
                fore[i].oval(cc?0:7,0,4.98f,-.08f,.67f,.91f,.55f);
                legs[i]=root.child(s*1.51f,11.65f,0);
                legs[i].loft(cc?7:0,24,0,0,0,1.42f,1.42f,2.55f,0,0,1.25f,1.28f,5.6f,0,0,.88f,.92f);
                knees[i]=legs[i].child(0,5.4f,0);
                knees[i].loft(cc?9:0,24,-.3f,0,0,.99f,1.03f,1.25f,0,0,.96f,1.0f,4.5f,0,0,.67f,.74f,5.75f,0,-.15f,.72f,.92f,6.95f,0,-.55f,.88f,1.5f);
                knees[i].blade(4,0,5.6f,-.81f,0,7.0f,-1.8f,.68f);
''' +s[b:]
edit('arms[i].rx=-w*.58f;arms[i].rz=-s*.10f;legs[i].rx=w*.68f;','arms[i].rx=-w*.55f;arms[i].rz=-s*.10f;fore[i].rx=-.06f-Math.max(0,w)*.28f;legs[i].rx=w*.65f;knees[i].rx=Math.max(0,-w)*.24f;')
p.write_text(s,encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
def read(p):
 raw=p.read_bytes();i=8;z=b''
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8];data=raw[i+8:i+8+n];i+=12+n
  if kind==b'IHDR':assert struct.unpack('>IIBBBBB',data)==(W,H,8,6,0,0,0)
  if kind==b'IDAT':z+=data
 rows=zlib.decompress(z);stride=W*4+1
 assert len(rows)==H*stride and all(rows[y*stride]==0 for y in range(H))
 return bytearray(b''.join(rows[y*stride+1:(y+1)*stride] for y in range(H)))
def face(u,v,cc):
 base=(244,209,186) if cc else (238,198,177)
 f=abs(u-.5)
 c=mix(base,(185,130,122),.12*clamp((f-.18)*4)+.08*math.exp(-((v-.92)/.15)**2))
 for side in (-1,1):
  ex=.5+side*.166
  dx=(u-ex)/(.108 if cc else .103)
  vv=v-(.485 if cc else .48)-side*dx*(.009 if cc else .013)
  if abs(dx)<1.04:
   arch=math.sqrt(max(0,1-min(1,abs(dx))**1.8))
   top=-(.064 if cc else .049)*arch
   bot=(.057 if cc else .046)*arch
   if top-.012<vv<bot+.005:
    c=(49,34,40)
    if top+.008<vv<bot-.005 and abs(dx)<.95:
     c=(250,242,230)
     ix=dx/.45;iy=(vv+.003)/(.060 if cc else .047)
     if ix*ix+iy*iy<1:
      c=mix((152,105,36) if cc else (91,47,139),(232,194,92) if cc else (155,96,190),clamp((iy+.15)*.60))
      if (dx/.20)**2+((vv+.003)/(.046 if cc else .036))**2<1:c=(35,27,40)
      if ((dx+.13)/.10)**2+((vv+.021)/.010)**2<1:c=(255,251,241)
   brow=.370-.011*(1-dx*dx)+side*dx*(.006 if cc else .012)
   if abs(dx)<.94 and abs(v-brow)<.009:c=(91,116,51) if cc else (49,36,49)
 if f<.018 and .60<v<.69:c=mix(c,(179,119,110),.14)
 if f<.049 and abs(v-(.785-(.014 if cc else .007)*(f/.049)**2))<.008:c=(143,75,79)
 return c
for cc in (False,True):
 p=assets/(('cc' if cc else 'lelouch')+'_sculpted.png');pix=read(p)
 for y in range(128):
  for x in range(128):
   colors=[face(clamp((x+dx-3)/121),clamp((y+dy-3)/121),cc) for dx in (.125,.375,.625,.875) for dy in (.125,.375,.625,.875)]
   c=tuple(round(sum(t[k] for t in colors)/16) for k in range(3))
   off=(y*W+6*128+x)*4;pix[off:off+4]=bytes((*c,255))
   # Broad soft highlights in the hair, instead of dozens of dark stripes.
   u=clamp((x-3)/121);v=clamp((y-3)/121)
   base=(157,190,84) if cc else (38,28,44)
   c=mix(base,(218,239,145) if cc else (91,72,98),.30*math.exp(-((v-.28)/.15)**2)+.12*math.sin(u*math.pi*6+v*.6)**2)
   c=mix(c,(82,112,44) if cc else (18,15,25),.14*(1-math.sin(u*math.pi)))
   off=((128+y)*W+x)*4;pix[off:off+4]=bytes((*c,255))
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Code Geass revision: front-projected clean faces, separate hair silhouettes, fitted costumes, articulated elbows and knees.')
