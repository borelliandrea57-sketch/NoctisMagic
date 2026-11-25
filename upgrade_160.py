"""1.6.0: clean planar face UVs and calmer expressions for Jotaro and Bucciarati."""
from pathlib import Path
import sys, math, struct, zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
# Project the eye and mouth artwork on the FRONT of the face rather than wrapping
# it around the circumference. The sides and caps receive only plain skin.
helper='''
    static V faceVertex(V v,boolean front,float width){
        float u=front?.5f+v.x()/width:.035f;
        float z=v.z();
        // Tiny integrated bridge instead of a second intersecting nose mesh.
        if(front&&v.nz()<-.5f){
            float dx=v.x()/.58f,dy=(v.y()+2.65f)/1.10f;
            z-=.23f*(float)Math.exp(-dx*dx-dy*dy);
        }
        return new V(v.x(),v.y(),z,u,v.v(),v.nx(),v.ny(),v.nz());
    }
    static void projectFace(Part p,int tile,float width){
        for(int i=0;i<p.faces.size();i++){
            Q q=p.faces.get(i);if(q.tile()!=tile)continue;
            boolean front=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
            p.faces.set(i,new Q(faceVertex(q.a(),front,width),faceVertex(q.b(),front,width),
                faceVertex(q.c(),front,width),faceVertex(q.d(),front,width),tile));
        }
    }
'''
for name,tile,old in [
 ('JotaroSculptedClient.java',6,'head.loft(2,16,-3.9f,0,-2.6f,.27f,.2f,-2.75f,0,-2.92f,.42f,.55f,-2.15f,0,-2.85f,.45f,.30f);'),
 ('BucciaratiSculptedClient.java',5,'head.loft(6,18,-3.85f,0,-2.48f,.19f,.16f,-2.7f,0,-2.86f,.37f,.41f,-2.1f,0,-2.83f,.31f,.20f);')]:
 p=java/name;s=p.read_text(encoding='utf-8');assert old in s
 s=s.replace(old,'projectFace(head,'+str(tile)+',7.4f);',1)
 a='    static class M extends' if name.startswith('Jotaro') else ' static class M extends'
 assert a in s;s=s.replace(a,helper+a,1)
 a='head.loft(6,32,' if tile==6 else 'head.loft(5,48,'
 assert a in s;s=s.replace(a,'head.loft('+str(tile)+',64,',1)
 if tile==5:
  s=s.replace('-1.5f,0,-.17f,2.20f,2.02f,-.45f,0,-.23f,1.32f,1.35f,0,0,-.26f,.62f,.72f','-1.5f,0,-.17f,2.35f,2.06f,-.45f,0,-.23f,1.50f,1.40f,0,0,-.26f,.82f,.82f',1)
 p.write_text(s,encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
def read(p):
 raw=p.read_bytes();i=8;z=b''
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8];data=raw[i+8:i+8+n];i+=12+n
  if kind==b'IHDR':assert struct.unpack('>IIBBBBB',data)==(W,H,8,6,0,0,0)
  if kind==b'IDAT':z+=data
 rows=zlib.decompress(z);stride=W*4+1
 assert len(rows)==H*stride and all(rows[y*stride]==0 for y in range(H))
 return bytearray(b''.join(rows[y*stride+1:(y+1)*stride] for y in range(H)))
def face(u,v,jotaro):
 base=(220,177,141) if jotaro else (230,184,145)
 f=abs(u-.5)
 # Mild shadows only; no dark cheek lines resembling tears or drooping lips.
 c=mix(base,(154,104,88),.10*clamp((f-.19)*4)+.09*math.exp(-((v-.92)/.15)**2))
 for side in (-1,1):
  ex=.5+side*.161
  dx=(u-ex)/(.104 if jotaro else .103)
  # Both eye corners have similar heights. Jotaro keeps a determined upper lid.
  vv=v-(.475 if jotaro else .485)-side*dx*.008
  if abs(dx)<1.03:
   arch=math.sqrt(max(0,1-min(1,abs(dx)**1.8)))
   top=-(.044 if jotaro else .057)*arch
   bot=(.041 if jotaro else .054)*arch
   if top-.010<vv<bot+.006:
    c=(42,31,32)
    if top+.008<vv<bot-.006 and abs(dx)<.95:
     c=(246,235,216)
     # Irises look straight ahead, with one modest catchlight.
     ix=dx/.40;iy=(vv+.003)/(.043 if jotaro else .050)
     if ix*ix+iy*iy<1:
      c=mix((49,105,99) if jotaro else (55,93,145),(103,157,143) if jotaro else (111,155,197),clamp((iy+.1)*.45))
      if (dx/.19)**2+((vv+.003)/(.034 if jotaro else .040))**2<1:c=(27,29,33)
      if ((dx+.12)/.09)**2+((vv+.016)/.009)**2<1:c=(245,241,232)
   # Almost horizontal brows, not a sad inverted V or a permanent frown.
   brow=.367-.010*(1-dx*dx)+side*dx*(.012 if jotaro else .004)
   if abs(dx)<.94 and abs(v-brow)<(.014 if jotaro else .010):c=(42,34,33)
 # Barely visible nose contour and a relaxed straight mouth with raised corners.
 if f<.020 and .60<v<.68:c=mix(c,(166,110,92),.14)
 if f<.062:
  mouth=.785-(.006 if jotaro else .010)*(f/.062)**2
  if abs(v-mouth)<.008:c=(116,62,58)
  elif f<.035 and mouth+.010<v<mouth+.022:c=mix(c,(170,100,88),.25)
 return c
for name,tile,jotaro in [('jotaro',6,True),('bucciarati',5,False)]:
 p=assets/(name+'_sculpted.png');pix=read(p)
 for y in range(128):
  for x in range(128):
   samples=[face(clamp((x+dx-3)/121),clamp((y+dy-3)/121),jotaro) for dx in (.125,.375,.625,.875) for dy in (.125,.375,.625,.875)]
   rgb=tuple(round(sum(c[k] for c in samples)/len(samples)) for k in range(3))
   off=(y*W+tile*128+x)*4;pix[off:off+4]=bytes((*rgb,255))
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+chunk(b'IEND',b''))
print('Jotaro and Bucciarati: front-projected face UVs, clean eyes, neutral mouth and integrated nose bridge.')
