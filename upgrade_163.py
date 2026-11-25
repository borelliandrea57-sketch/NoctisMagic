"""1.6.3: differentiated adult silhouettes and clean face UVs for Dante and Bayonetta."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'WitchHunterClient.java';s=p.read_text(encoding='utf-8')
changes=json.loads("[[\"body.loft(0,40,-1,0,0,1.42f,1.16f,.1f,0,0,3.10f,1.65f,2.4f,0,-.10f,2.91f,1.96f,4.2f,0,0,2.44f,1.55f,7.4f,0,0,1.70f,1.18f,9.8f,0,.10f,2.35f,1.55f,11.05f,0,.12f,2.79f,1.80f);\",\"body.loft(0,64,-1,0,0,1.50f,1.22f,.1f,0,0,3.55f,1.85f,1.2f,0,-.14f,3.46f,2.03f,2.1f,0,-.24f,3.45f,2.28f,2.8f,0,-.30f,3.43f,2.35f,3.5f,0,-.22f,3.25f,2.21f,4.4f,0,0,2.82f,1.80f,5.5f,0,.05f,2.47f,1.57f,7.0f,0,.12f,2.12f,1.44f,8.1f,0,.14f,2.53f,1.70f,9.4f,0,.19f,3.28f,2.09f,10.4f,0,.25f,3.60f,2.26f,11.25f,0,.19f,3.37f,2.03f);\\n    sculptBust(body);\\n    body.blade(10,0,4.4f,-1.87f,0,7.0f,-1.36f,.26f);\\n    for(int s:new int[]{-1,1}){\\n      body.blade(4,s*2.50f,4.0f,-1.50f,s*1.97f,7.0f,-.83f,.19f);\\n      body.blade(4,s*1.97f,7.0f,-.83f,s*2.90f,10.3f,-1.25f,.20f);\\n    }\"],[\"body.oval(4,0,2.9f,-2.04f,1.13f,1.15f,.29f);\",\"body.oval(4,0,1.25f,-2.23f,.91f,.91f,.25f);\"],[\"body.oval(3,0,2.9f,-2.26f,.86f,.87f,.15f);\",\"body.oval(3,0,1.25f,-2.45f,.70f,.70f,.12f);\"],[\"Part med=body.child(0,2.9f,-2.4f);loop(med,4,.84f,.85f,.095f);\",\"Part med=body.child(0,1.25f,-2.59f);loop(med,4,.69f,.70f,.075f);\"],[\"body.loft(0,32,-1,0,0,1.95f,1.42f,.15f,0,0,4.15f,2.2f,2.65f,0,-.12f,3.95f,2.35f,5.2f,0,0,3.18f,1.95f,8.5f,0,0,2.68f,1.7f,10.7f,0,0,3.10f,1.95f);\",\"body.loft(0,40,-1,0,0,2.0f,1.52f,-.1f,0,0,4.45f,2.30f,.8f,0,0,4.70f,2.43f,2.65f,0,-.12f,4.38f,2.58f,4.0f,0,-.04f,3.95f,2.34f,5.2f,0,0,3.53f,2.11f,8.5f,0,0,2.88f,1.85f,10.7f,0,0,3.29f,2.08f);\\n    squareTorso(body);\"],[\"body.oval(1,0,3.7f,-2.04f,2.14f,3.73f,.50f);\",\"body.loft(1,32,.1f,0,-1.9f,1.78f,.40f,1.0f,0,-2.05f,2.34f,.59f,3.3f,0,-2.17f,2.06f,.44f,5.5f,0,-1.77f,1.70f,.38f,8.3f,0,-1.43f,1.31f,.28f);\"],[\"float w=witch?2.95f:3.24f;\",\"float w=witch?2.95f:3.10f;\"],[\"witch?2.30f:2.72f,2.36f,-.75f,0,-.20f,witch?1.36f:1.76f,1.65f,0,0,-.25f,.65f,.85f\",\"witch?2.30f:2.85f,2.36f,-.75f,0,-.20f,witch?1.36f:2.12f,1.65f,0,0,-.25f,witch?.65f:1.15f,.85f\"],[\"head.loft(6,20,-3.8f,0,-2.55f,.22f,.17f,-2.6f,0,-2.93f,.39f,.46f,-2.04f,0,-2.82f,.32f,.24f);\",\"projectFace(head,witch);\"],[\"glasses.ry=-s*.22f;glasses.rz=-s*.12f;loop(glasses,3,1.14f,.58f,.108f);\",\"glasses.ry=-s*.16f;glasses.rz=-s*.07f;loop(glasses,3,1.12f,.46f,.085f);\"],[\"for(int j=0;j<7;j++){Part q=head.child(-2.45f+j*.73f,-7.8f,-2.0f);\",\"for(int j=0;j<7;j++){Part q=head.child(-2.45f+j*.73f,-8.0f,-2.0f);\"],[\"2.45f+j*.10f,1.05f,-.45f,.035f,.06f\",\"2.10f+j*.10f,1.15f,-.45f,.035f,.06f\"],[\"s*(witch?3.25f:4.05f)\",\"s*(witch?3.72f:4.75f)\"],[\"witch?.91f:1.34f,witch?.98f:1.4f\",\"witch?1.10f:1.62f,witch?1.11f:1.63f\"],[\"witch?1.24f:1.91f,witch?1.22f:1.79f\",\"witch?1.43f:2.05f,witch?1.41f:1.98f\"],[\"witch?1.01f:1.77f,witch?1.02f:1.64f\",\"witch?1.20f:1.85f,witch?1.20f:1.81f\"],[\"witch?.69f:1.12f,witch?.72f:1.18f\",\"witch?.84f:1.23f,witch?.87f:1.28f\"],[\"witch?.94f:1.4f,witch?.92f:1.34f\",\"witch?1.09f:1.53f,witch?1.06f:1.49f\"],[\"s*(witch?1.38f:1.77f)\",\"s*(witch?1.71f:1.84f)\"],[\"witch?1.41f:1.62f,witch?1.43f:1.60f\",\"witch?1.75f:1.78f,witch?1.83f:1.73f\"],[\"witch?1.18f:1.54f,witch?1.24f:1.45f\",\"witch?1.60f:1.66f,witch?1.60f:1.60f\"],[\"witch?.73f:1.08f,witch?.78f:1.12f\",\"witch?1.05f:1.18f,witch?1.07f:1.23f\"],[\"witch?.81f:1.18f,witch?.83f:1.2f\",\"witch?1.07f:1.24f,witch?1.09f:1.27f\"],[\"witch?.94f:1.27f,witch?.95f:1.23f\",\"witch?1.26f:1.39f,witch?1.29f:1.36f\"],[\"witch?.56f:.90f,witch?.59f:.93f\",\"witch?.79f:1.02f,witch?.81f:1.04f\"],[\"if(witch){\\n     Part heel=\",\"if(witch){\\n     // Sleeve hair drapery flares behind the elbows, with a separate tapered silhouette.\\n     Part drape=fore[i].child(s*.38f,.1f,1.0f);\\n     drape.loft(7,32,-.2f,0,0,.45f,.55f,2.4f,s*.50f,1.1f,1.60f,.92f,5.8f,s*1.12f,2.15f,2.50f,1.04f,9.7f,s*1.45f,3.0f,2.05f,.69f,12.3f,s*.95f,3.35f,.05f,.08f);\\n     locks.add(drape);\\n     Part heel=\"],[\"legs[i].loft(3,24,3.1f,0,0,1.47f,1.39f,3.7f,0,0,1.41f,1.34f);\",\"legs[i].loft(3,24,3.1f,0,0,1.65f,1.57f,3.7f,0,0,1.59f,1.49f);\"],[\"if(witch)p.scale(.99f,1.15f,.99f);else p.scale(1.02f,1.02f,1.02f);\",\"if(witch)p.scale(1.13f,1.13f,1.13f);else p.scale(1.17f,1.15f,1.17f);\"],[\"arms[i].rz=-s*(.12f+(shoot?a*.23f:0));\",\"arms[i].rz=-s*((witch?.19f:.14f)+(shoot?a*.23f:0));\"],[\"show(fore[i],guns[i],shoot&&casting);\",\"show(fore[i],guns[i],witch||shoot&&casting);\"],[\" static class M<T extends Mob> extends EntityModel<T>{\",\" static V faceVertex(V v,boolean front,boolean witch){\\n  float u=front?.5f+v.x()/7.3f:.035f,z=v.z();\\n  if(front&&v.nz()<-.55f){float dx=v.x()/.52f,dy=(v.y()+2.65f)/1.1f;z-=(witch?.20f:.27f)*(float)Math.exp(-dx*dx-dy*dy);}\\n  return new V(v.x(),v.y(),z,u,v.v(),v.nx(),v.ny(),v.nz());\\n }\\n static void projectFace(Part p,boolean witch){\\n  for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=5)continue;\\n   boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;\\n   p.faces.set(i,new Q(faceVertex(q.a(),f,witch),faceVertex(q.b(),f,witch),faceVertex(q.c(),f,witch),faceVertex(q.d(),f,witch),5));}\\n }\\n static V bustVertex(V v){\\n  if(v.nz()>=0||v.y()<.3f||v.y()>5.2f)return v;\\n  float x=v.x(),y=v.y(),dx=(Math.abs(x)-1.45f)/1.28f,dy=(y-2.65f)/1.28f;\\n  float d=.78f*(float)Math.exp(-dx*dx-dy*dy)*Math.max(0,-v.nz());\\n  float nx=v.nx()+d*dx*(x<0?-1:1),ny=v.ny()+d*dy,nz=v.nz();\\n  float len=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);\\n  return new V(x,y,v.z()-d,v.u(),v.v(),nx/len,ny/len,nz/len);\\n }\\n static void sculptBust(Part p){\\n  for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()==0)p.faces.set(i,new Q(bustVertex(q.a()),bustVertex(q.b()),bustVertex(q.c()),bustVertex(q.d()),0));}\\n }\\n static V squareVertex(V v){\\n  if(Math.abs(v.ny())>.5f)return v;\\n  float x=v.x(),z=v.z(),nx=v.nx(),nz=v.nz();\\n  return new V(x*(1+.17f*Math.abs(nz)),v.y(),z*(1+.13f*Math.abs(nx)),v.u(),v.v(),nx,v.ny(),nz);\\n }\\n static void squareTorso(Part p){\\n  for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()==0)p.faces.set(i,new Q(squareVertex(q.a()),squareVertex(q.b()),squareVertex(q.c()),squareVertex(q.d()),0));}\\n }\\n static class M<T extends Mob> extends EntityModel<T>{\"]]")
for a,b in changes:
 assert a in s,a
 s=s.replace(a,b,1)
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
def face(u,v,witch):
 base=(241,198,174) if witch else (233,191,164);f=abs(u-.5)
 c=mix(base,(164,112,102),.10*clamp((f-.20)*4)+.08*math.exp(-((v-.93)/.13)**2))
 for side in (-1,1):
  ex=.5+side*.164;dx=(u-ex)/(.105 if witch else .106)
  vv=v-.486-side*dx*.012
  if abs(dx)<1.04:
   arch=math.sqrt(max(0,1-min(1,abs(dx))**1.8))
   top=-(.052 if witch else .041)*arch;bot=(.043 if witch else .038)*arch
   if top-.010<vv<bot+.005:
    c=(38,25,34)
    if top+.009<vv<bot-.005 and abs(dx)<.95:
     c=(249,238,227);ix=dx/.42;iy=(vv+.002)/(.047 if witch else .039)
     if ix*ix+iy*iy<1:
      c=mix((88,103,112) if witch else (52,94,145),(145,171,178) if witch else (117,162,194),clamp((iy+.2)*.5))
      if (dx/.19)**2+((vv+.002)/.032)**2<1:c=(25,24,34)
      if ((dx+.13)/.10)**2+((vv+.015)/.009)**2<1:c=(255,252,241)
   brow=.372-.009*(1-dx*dx)+side*dx*.01
   if abs(dx)<.94 and abs(v-brow)<.010:c=(37,26,36) if witch else (119,111,123)
  if witch and abs(dx)<1.16 and abs(v-(.427+side*dx*.018))<.008:c=mix(c,(88,48,82),.45)
 if f<.055 and abs(v-(.790-.010*(f/.055)**2))<.009:c=(116,32,46) if witch else (133,73,69)
 if witch and f<.043 and .800<v<.822:c=mix(c,(180,53,71),.65)
 if witch and ((u-.572)/.005)**2+((v-.851)/.007)**2<1:c=(52,31,33)
 return c
for witch in (True,False):
 p=assets/(('bayonetta' if witch else 'dante')+'_sculpted.png');pix=read(p)
 for y in range(128):
  for x in range(128):
   colors=[face(clamp((x+dx-3)/121),clamp((y+dy-3)/121),witch) for dx in (.125,.375,.625,.875) for dy in (.125,.375,.625,.875)]
   c=tuple(round(sum(t[k] for t in colors)/16) for k in range(3))
   off=(y*W+5*128+x)*4;pix[off:off+4]=bytes((*c,255))
   u=clamp((x-3)/121);v=clamp((y-3)/121)
   if witch:
    # Satin fabric with long highlights and subdued longitudinal panel seams.
    c=mix((23,25,34),(104,111,130),.35*math.exp(-((u-.38)/.10)**2)+.25*math.exp(-((u-.62)/.10)**2))
    if abs(u-.5)<.006 or abs(u-.31)<.004 or abs(u-.69)<.004:c=mix(c,(129,135,150),.31)
   else:
    # Red leather, with visible broad creases rather than a shiny rounded tube.
    c=mix((135,25,38),(198,62,65),.36*math.exp(-((u-.35)/.18)**2))
    c=mix(c,(60,13,26),.19*math.exp(-((v-.70-.10*math.sin(u*9))/.037)**2))
    if abs(u-.29)<.006 or abs(u-.71)<.006:c=mix(c,(63,18,28),.45)
   off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
   # tile 10 is a silver seam detail on the black suit.
   off=((128+y)*W+2*128+x)*4;pix[off:off+4]=bytes((110,116,130,255))
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+chunk(b'IEND',b''))
print('Dante and Bayonetta: distinct stronger silhouettes, corrected face projection and costume materials')
