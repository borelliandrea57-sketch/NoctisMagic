"""1.7.20: oversized Rebellion mesh and detailed Dante-only material atlas."""
from pathlib import Path
import sys,math,json
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'WitchHunterClient.java';s=p.read_text(encoding='utf-8')
a=s.index(' static Part rebellion(){');b=s.index(' static V faceVertex(',a)
s=s[:a]+''' // A diamond-section blade with distinct bevel and fuller surfaces.
 static void swordBlade(Part p){
  float[][] rings={{2.65f,1.13f,.30f},{4.25f,2.03f,.48f},{7.0f,1.93f,.43f},{21.5f,1.74f,.37f},{28.5f,1.45f,.29f},{32.2f,.78f,.18f},{35.2f,.012f,.012f}};
  for(int k=0;k<rings.length-1;k++){
   float[] a=rings[k],b=rings[k+1];
   for(int j=0;j<4;j++){
    int n=(j+1)%4;
    float[][] A={{0,a[0],-a[2]},{a[1],a[0],0},{0,a[0],a[2]},{-a[1],a[0],0}};
    float[][] B={{0,b[0],-b[2]},{b[1],b[0],0},{0,b[0],b[2]},{-b[1],b[0],0}};
    float dx=A[n][0]-A[j][0],dz=A[n][2]-A[j][2],l=(float)Math.hypot(dx,dz);
    float nx=dz/l,nz=-dx/l;
    int m=j%2==0?11:4;
    p.faces.add(new Q(swordV(A[j],0,k/6f,nx,nz),swordV(B[j],0,(k+1)/6f,nx,nz),swordV(B[n],1,(k+1)/6f,nx,nz),swordV(A[n],1,k/6f,nx,nz),m));
   }
  }
 }
 static V swordV(float[] a,float u,float v,float nx,float nz){return new V(a[0],a[1],a[2],u,v,nx,0,nz);}
 static Part rebellion(){
  Part p=new Part(0,5.1f,-.5f);p.rx=-.95f;
  p.loft(3,8,-4.4f,0,0,.43f,.44f,-.55f,0,0,.48f,.49f,.45f,0,0,.40f,.43f);
  for(int j=0;j<9;j++){
   float y=-4.22f+j*.40f;
   p.loft(9,8,y,0,0,.49f,.50f,y+.15f,0,0,.49f,.50f);
  }
  p.loft(4,8,-5.20f,0,0,.34f,.35f,-4.98f,0,0,.74f,.65f,-4.62f,0,0,.77f,.66f,-4.32f,0,0,.43f,.45f);
  // Detailed skull, recessed sockets, nasal hole, teeth and swept skeletal quillons.
  p.loft(11,12,.05f,0,0,.78f,.67f,.60f,0,0,1.06f,.77f,1.40f,0,-.05f,1.02f,.69f,2.12f,0,-.09f,.68f,.50f,2.58f,0,-.08f,.49f,.34f);
  for(int side:new int[]{-1,1}){
   p.oval(3,side*.40f,.84f,-.75f,.27f,.34f,.11f);
   p.blade(11,side*.10f,.42f,-.74f,side*.83f,.62f,-.71f,.21f);
   p.blade(4,side*.81f,.94f,-.10f,side*3.60f,-.76f,.15f,1.08f);
   p.blade(11,side*1.65f,.48f,-.34f,side*3.57f,-.72f,-.08f,.23f);
   p.blade(4,side*.84f,1.59f,.04f,side*3.77f,3.43f,.20f,1.13f);
   p.blade(11,side*1.17f,1.71f,-.18f,side*3.66f,3.37f,-.09f,.30f);
   p.blade(4,side*.68f,2.13f,.04f,side*2.67f,5.08f,.12f,.83f);
   p.blade(9,side*1.05f,2.00f,-.25f,side*2.26f,4.66f,-.10f,.25f);
  }
  p.oval(3,0,1.56f,-.69f,.18f,.25f,.09f);
  for(int j=0;j<7;j++)p.blade(11,-.54f+j*.18f,1.96f,-.58f,-.54f+j*.18f,2.35f,-.43f,.12f);
  swordBlade(p);
  // Thin dark channels beside the spine, tapering before the tip.
  for(int side:new int[]{-1,1}){
   p.blade(9,side*.30f,5.35f,-.419f,side*.24f,27.9f,-.257f,.13f);
   p.blade(9,side*.30f,5.35f,.419f,side*.24f,27.9f,.257f,.13f);
  }
  return p;
 }
'''+s[b:]
# The back sheath is kept a little smaller to avoid excessive ground clipping.
old='backSword=rebellion();backSword.x='
assert old in s
s=s.replace(old,'backSword=rebellion();VoxelPortrait.enlarge(backSword,.83f,.83f,.83f);backSword.x=',1)
p.write_text(s,encoding='utf-8')
# Standalone 3D item model. Native Minecraft element bounds -16..32, with distinct metallic surfaces.
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')
textures={'steel':(148,159,177),'edge':(229,235,239),'ridge':(91,101,120),'bone':(183,180,169),'socket':(37,32,39),'leather':(45,34,39)}
for n,base in textures.items():
 im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
 for y in range(64):
  for x in range(64):
   u=x/63;v=y/63
   light=.82+.23*math.sin(u*math.pi)**2+.035*math.sin(v*55+u*9)
   if n=='leather':light*=.78+.30*math.sin(v*math.pi*8)**2
   if n=='bone':light*=.88+.15*math.sin(u*6+v*3)**2
   im.putpixel((x,y),(*[max(0,min(255,round(q*light))) for q in base],255))
 if n=='steel':
  for x in (5,58):d.line((x,0,x,63),fill=(212,218,228),width=1)
 if n=='leather':
  for y in range(0,64,8):d.line((0,y,63,y+4),fill=(89,75,75),width=1)
 f=assets/'textures/item'/f'rebellion_{n}.png';f.parent.mkdir(parents=True,exist_ok=True);im.save(f)
els=[]
def box(x,y,z,X,Y,Z,m,rotation=None):
 if not(x<X and y<Y and z<Z):return
 e={'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}}
 if rotation:e['rotation']=rotation
 els.append(e)
# Handle, pommel, wrapped grip.
box(7.30,-10,7.30,8.70,-2.1,8.70,'leather')
box(6.85,-11,6.85,9.15,-9.8,9.15,'bone')
for j in range(9):
 y=-9.65+j*.77;box(7.1,y,7.1,8.9,y+.22,8.9,'ridge')
# Skull jaw and eye sockets on both faces.
box(6.2,-2.1,6.85,9.8,.75,9.15,'bone')
box(6.6,.75,7.05,9.4,2.3,8.95,'bone')
for z,Z in ((6.68,6.85),(9.15,9.32)):
 for x in (6.65,8.45):box(x,-.9,z,x+.9,-.1,Z,'socket')
 box(7.75,.05,z,8.25,.62,Z,'socket')
 for j in range(6):box(6.85+j*.42,.9,z,7.12+j*.42,1.8,Z,'bone')
# Curved stepped quillons and skeletal fingers.
for side in (-1,1):
 def sidebox(a,b,y,Y,z,Z,m):
  box(8+a if side>0 else 8-b,y,z,8+b if side>0 else 8-a,Y,Z,m)
 for a,b,y,Y in ((1.4,2.7,-1.2,.4),(2.7,3.8,-1.6,-.15),(3.8,4.9,-2.5,-.7),(4.9,5.5,-3.2,-1.8),(1.4,2.9,.45,1.65),(2.9,4.0,1.1,2.5),(4.0,5.0,2.0,3.2),(1.0,2.2,1.7,3.0),(2.2,3.3,2.75,4.4)):
  sidebox(a,b,y,Y,7.25,8.75,'bone')
  sidebox(a+.10,b-.10,y+.16,Y-.16,7.02,7.25,'ridge')
# Blade: progressively thinner layers meet at a fine cutting edge and taper to a point.
for y,Y,width in ((2.1,4.2,1.25),(4.2,7.5,2.1),(7.5,18,1.98),(18,24,1.72),(24,27,1.42),(27,29,1.04),(29,30.3,.62),(30.3,31.25,.27),(31.25,31.9,.085)):
 box(8-width,y,7.94,8+width,Y,8.06,'edge')
 box(8-width*.78,y,7.77,8+width*.78,Y,8.23,'steel')
 box(8-width*.35,y,7.57,8+width*.35,Y,8.43,'steel')
 if y<27:
  box(7.96,y,7.52,8.04,Y,7.57,'edge')
  box(7.96,y,8.43,8.04,Y,8.48,'edge')
  for sign in (-1,1):
   x=8+sign*width*.20;box(x-.035,y,7.51,x+.035,Y,7.57,'ridge')
model={'parent':'minecraft:item/handheld','gui_light':'front','textures':{**{k:'noctismagic:item/rebellion_'+k for k in textures},'particle':'noctismagic:item/rebellion_steel'},'elements':els,
'display':{'gui':{'rotation':[15,0,-42],'translation':[0,-2,0],'scale':[.37,.37,.37]},'ground':{'rotation':[0,0,0],'translation':[0,4,0],'scale':[.42,.42,.42]},'fixed':{'rotation':[0,0,-35],'translation':[0,-3,0],'scale':[.45,.45,.45]},'firstperson_righthand':{'rotation':[0,-90,23],'translation':[1.5,1.5,1.5],'scale':[1.12,1.12,1.12]},'firstperson_lefthand':{'rotation':[0,90,-23],'translation':[1.5,1.5,1.5],'scale':[1.12,1.12,1.12]},'thirdperson_righthand':{'rotation':[0,-90,45],'translation':[0,2.5,1],'scale':[1.30,1.30,1.30]},'thirdperson_lefthand':{'rotation':[0,90,-45],'translation':[0,2.5,1],'scale':[1.30,1.30,1.30]}}}
dump(assets/'models/item/rebellion.json',model)
# Dante only: detailed red leather, charcoal fabric, silver-white hair and stubble.
p=assets/'textures/entity/dante_sculpted.png';im=Image.open(p).convert('RGBA')
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for tile in (0,1,2,3,5,6,7,8,9,10,11):
 for y in range(128):
  v=max(0,min(1,(y-3)/121))
  for x in range(128):
   u=max(0,min(1,(x-3)/121));f=abs(u-.5);xx=tile%8*128+x;yy=tile//8*128+y;c=im.getpixel((xx,yy))[:3]
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   grain=math.sin(x*2.17+y*.61)*math.sin(y*1.93-x*.39)
   if tile in (0,10):
    c=mix(c,(45,12,23),.24*min(1,f*1.9)+.22*max(0,-math.sin(u*19+v*4))**7)
    c=mix(c,(224,95,94),.27*g(.34,.35,.19,.45)+.13*max(0,math.sin(u*25+v*5))**6)
    c=tuple(max(0,min(255,round(k+grain*4))) for k in c)
    # Fine double stitching on the leather panels.
    if abs(f-.39)<.007 and y%6<3:c=mix(c,(205,128,108),.65)
   elif tile in (1,2,3):
    c=mix(c,(12,15,22),.15*min(1,f*2)+.10*max(0,math.cos(u*25+v*5))**5)
    c=mix(c,(111,119,132),.12*g(.31,.35,.16,.52))
    c=tuple(max(0,min(255,round(k+grain*3))) for k in c)
   elif tile in (7,8):
    flow=math.sin(u*math.pi*19+v*4+.7*math.sin(v*8))
    c=mix((118,130,152),(245,243,236),.64+.23*max(0,flow)**4)
    c=mix(c,(82,95,116),.27*max(0,-flow)**6)
    c=mix(c,(255,253,242),.22*g(.40,.33,.20,.26))
   elif tile==5:
    # Preserve eye and brow artwork; add facial plane shading outside those features.
    if v>.60 or v<.29:
     c=mix(c,(109,68,68),.19*min(1,f*2)+.12*g(.50,.69,.09,.06))
     c=mix(c,(248,212,186),.15*g(.50,.31,.16,.15))
    if .74<v<.96 and f<.32 and (x*17+y*31)%13<3:c=mix(c,(93,81,82),.23)
   elif tile==6:
    c=mix(c,(134,91,82),.10*min(1,f*2)+.06*v)
   elif tile in (9,11):
    c=mix(c,(236,240,247) if tile==11 else (75,85,106),.22*math.sin(math.pi*u)**2)
   im.putpixel((xx,yy),(*c,255))
im.save(p)
print('Rebellion: oversized diamond-section NPC blade, sculpted skull guard, matching 3D player item and Dante-only leather, hair and skin shading.')
