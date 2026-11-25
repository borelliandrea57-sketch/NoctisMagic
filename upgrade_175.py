"""1.7.5: Moon guardian hair and wand, faceted gemstone twins, broad Arsene."""
from pathlib import Path
import sys,math,re
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'MoonFoxClient.java';s=p.read_text(encoding='utf-8')
a=s.index('static LayerDefinition meshM()');b=s.index('return LayerDefinition.create(m,256,256);',a);m=s[a:b]
mat={'hair':(0,128),'shade':(64,128),'gold':(128,128),'pink':(192,128),'ruby':(0,192),'crystal':(64,192)}
def f(n):return str(float(n))+'f'
def part(var,parent,name,pos,rot,boxes):
 def cube(q):
  x,y,z,w,h,d,c=q;u,v=mat[c]
  return f'.texOffs({u},{v}).addBox('+','.join(map(f,(x,y,z,w,h,d)))+')'
 return f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(q) for q in boxes)+',PartPose.offsetAndRotation('+','.join(map(f,(*pos,*rot)))+'));'
def replace(var,line):
 global m
 m,n=re.subn(r'(?m)^\s*PartDefinition '+re.escape(var)+r'=.*?;[ \t]*$',lambda _:line,m,count=1);assert n==1,var
replace('hair',part('hair','h','hair',(0,-7,0),(0,0,0),[(-3.6,-1.15,-3.6,7.2,1.8,7.1,'hair'),(-3,-1.7,-3.05,6,.85,6.1,'hair'),(-3.75,.3,2.35,7.5,4.7,1.35,'shade'),(-3.55,4.65,2.65,7.1,1.55,.92,'hair'),(-3.75,.35,-2.1,1,3.5,4.65,'hair'),(2.75,.35,-2.1,1,3.5,4.65,'hair')]))
for i,side in enumerate((-1,1)):
 bun='bun'+str(i);lock='lock'+str(i);tip='locktip'+str(i);bang='bang'+str(i)
 lines=[part(bun,'h',bun,(side*3.05,-7.25,.35),(0,0,side*.14),[(-1.75,-2.15,-1.6,3.5,3.15,3.2,'hair'),(-1.37,-2.78,-1.27,2.74,.78,2.54,'hair'),(-1.39,-2,-2.04,2.78,2.55,.66,'shade'),(-1.3,-1.7,-2.19,2.6,1.85,.25,'gold'),(-.73,-1.35,-2.43,1.46,1.13,.42,'ruby'),(-.43,-1.19,-2.63,.86,.78,.2,'ruby')])]
 for j in range(9):
  ang=2*math.pi*j/9;lines.append(part(f'bunRib{i}_{j}',bun,f'rib{j}',(1.58*math.cos(ang),-.63,1.48*math.sin(ang)),(0,-ang,0),[(-.18,-1.38,-.22,.36,2.3,.48,'hair')]))
 replace(bun,'\n'.join(lines))
 lines=[part(lock,'h',lock,(side*3.75,-6.10,.85),(0,0,side*.1),[(-1.02,0,-.94,2.04,3.8,1.88,'hair'),(-1.12,3.25,-1.04,2.24,3.5,2.08,'hair'),(-1.02,6,-.91,2.04,3.6,1.82,'hair'),(-.66,.7,-1.12,.4,8.2,.25,'shade')])]
 for j in range(5):lines.append(part(f'lockRib{i}_{j}',lock,f'rib{j}',((j-2)*.38,.35,.95 if j%2 else -.91),(0,0,(j-2)*.022),[(-.16,0,-.22,.32,9,.44,'hair')]))
 replace(lock,'\n'.join(lines))
 lines=[part(tip,lock,'tip',(0,8.75,0),(0,0,side*.12),[(-1.05,-.25,-.92,2.1,4.8,1.84,'hair'),(-.98,4,-.88,1.96,4.3,1.76,'hair'),(-.81,7.9,-.73,1.62,3.6,1.46,'hair'),(-.55,11,-.55,1.1,2.3,1.1,'hair'),(-.24,13,-.28,.48,1.3,.56,'hair')])]
 for j in range(5):lines.append(part(f'tailRib{i}_{j}',tip,f'rib{j}',((j-2)*.32,0,-.89),(0,0,(2-j)*.018),[(-.14,0,-.18,.28,11-abs(j-2),.36,'shade' if j%2 else 'hair')]))
 replace(tip,'\n'.join(lines))
 lines=[part(bang,'h',bang,(side*1.55,-7.35,-3.42),(0,0,-side*.33),[(-.85,-.3,-.44,1.7,2.35,.85,'hair'),(-.55,1.8,-.38,1.10,1.35,.72,'hair'),(-.24,2.9,-.29,.48,.55,.45,'hair')])]
 for j in range(3):lines.append(part(f'fringe{i}_{j}',bang,f'fringe{j}',(side*(j*.62-.4),-.15,-.39),(0,0,-side*(.13+j*.13)),[(-.27,0,-.17,.54,2.7-j*.42,.48,'hair')]))
 replace(bang,'\n'.join(lines))
# Open gold crescent with tapering ends, crystal and pink grip.
lines=[part('wand','arm1','wand',(0,10.15,-.7),(0,0,.10),[(-.38,-4,-.38,.76,8.2,.76,'pink'),(-.53,3.75,-.53,1.06,.85,1.06,'gold'),(-.55,-4.45,-.55,1.1,.75,1.1,'gold'),(-.64,-5.2,-.64,1.28,.95,1.28,'pink'),(-.8,-5.65,-.5,1.6,.6,1,'gold')])]
for j in range(21):
 ang=math.radians(160+220*j/20);x=1.85*math.cos(ang);y=-7.35-1.85*math.sin(ang)
 thickness=.27+.22*math.sin(math.pi*j/20)
 lines.append(part(f'arc{j}','wand',f'arc{j}',(x,y,0),(0,0,ang-math.pi/2),[(-thickness,-.30,-.40,2*thickness,.64,.80,'gold')]))
lines.append(part('gem','wand','crystal',(0,-7.35,-.06),(0,0,math.pi/4),[(-.53,-.53,-.5,1.06,1.06,1,'crystal')]))
replace('wand','\n'.join(lines));s=s[:a]+m+s[b:];p.write_text(s,encoding='utf-8')
p=assets/'textures/entity/sailor_moon.png';im=Image.open(p).convert('RGBA');S=im.width//256
pal={'hair':(244,205,65),'shade':(206,151,35),'gold':(252,196,62),'pink':(232,105,161),'ruby':(191,31,65),'crystal':(234,249,255)}
for name,(x,y) in mat.items():
 for j in range(64*S):
  v=j/(64*S)
  for i in range(64*S):
   u=i/(64*S);t=.85+.15*math.sin(u*math.pi)**2+.08*math.sin(u*math.pi*22+v*3)**2 if name in ('hair','shade') else .78+.32*math.sin(u*math.pi)**2
   im.putpixel((x*S+i,y*S+j),(*[max(0,min(255,int(z*t))) for z in pal[name]],255))
im.save(p)
# Gem twins: preserve all other models in the shared renderer.
p=java/'SculptedGuestsClient.java';s=p.read_text(encoding='utf-8')
a='head.loft(face,24,-7.2f';i=s.index(a);j=s.index(';',i)+1
old=s[i:j]
s=s[:i]+'''if(gem){
                    VoxelPortrait.head(head,face,17,6.4f,7.2f,
                     -7.2f,2.45f,2.10f,.10f,.32f,-6.5f,3.02f,2.55f,.04f,.37f,
                     -4.65f,3.08f,2.60f,0,.44f,-2.8f,2.86f,2.42f,-.08f,.43f,
                     -1.1f,2.22f,1.92f,-.18f,.37f,0,1.40f,1.30f,-.22f,.29f);
                    head.loft(17,8,-.35f,0,.05f,.87f,.85f,.8f,0,.05f,1.13f,1.05f);
                }else '''+old+s[j:]
a='body.loft(suit,16,-1';i=s.index(a);j=s.index(';',i)+1;old=s[i:j]
s=s[:i]+'''if(gem)body.loft(suit,8,-1,0,0,2.3f,1.65f,0,0,0,4.10f,2.14f,1.4f,0,0,4.05f,2.20f,4.8f,0,0,3.10f,1.72f,8.6f,0,0,2.68f,1.62f,11,0,0,3.40f,1.92f);
            else '''+old+s[j:]
match=re.search(r'Part\s+a\s*=\s*arms\[i\]\s*=\s*root\.child\([^;]+;',s)
a=match.group(0) if match else ''
if a:s=s.replace(a,'''Part a=arms[i]=root.child(s*(gem?4.35f:4),0,0);
                if(gem){
                    a.loft(suit,4,-.55f,0,0,1.34f,1.34f,.1f,0,0,1.80f,1.66f,1.75f,0,0,1.66f,1.50f,3.15f,0,0,1.36f,1.24f);
                    a.blade(11,0,2.70f,-1.35f,0,3.05f,-1.33f,2.05f);
                }''',1)
# More crystalline hair faces with independent irregular locks, not a round cap alone.
a='if(k==3)for(int i=0;i<4;i++)'
if a in s:s=s.replace(a,'''                if(gem)for(int j=0;j<11;j++){
                    float x=(j-5)*.52f;
                    Part crystal=head.child(x,-7.9f,.45f+(j%3)*.40f);
                    crystal.loft(h,4,-.45f,0,0,.42f,.52f,.25f,0,0,.66f,.58f,1.2f,x*.17f,-.22f,.50f,.43f,2.3f,x*.30f,-.45f,.04f,.06f);
                    head.blade(h,x,-7.62f,-2.17f,x+(k==2?-.56f:.40f),-4.90f-(j%3)*.35f,-2.45f,.53f);
                }
'''+a,1)
# Small idle head movements supplement dialogue.
a='head.rz=k==2?cast*.10f:k==3?-cast*.04f:0;'
if a in s:s=s.replace(a,'head.rz=k==2?cast*.10f+(float)Math.sin(age*.065f)*.045f:k==3?-cast*.04f+(float)Math.sin(age*.05f)*.025f:0;',1)
p.write_text(s,encoding='utf-8')
p=assets/'textures/entity/sculpted_guests.png';im=Image.open(p).convert('RGBA')
def mix(a,b,t):return tuple(int(x+(y-x)*max(0,min(1,t))) for x,y in zip(a,b))
for tile in (12,13,14,15):
 for y in range(128):
  v=(y+.5)/128
  for x in range(128):
   u=(x+.5)/128;ox=tile%8*128+x;oy=tile//8*128+y
   if tile in (12,13):
    base=(69,208,177) if tile==12 else (162,25,53);highlight=(188,255,225) if tile==12 else (255,116,145)
    seg=(int(u*12)+int((v+u*.45)*8))%4;c=mix(base,highlight,.12+seg*.19)
    if (u*12)%1<.09 or ((v+u*.45)*8)%1<.06:c=mix(c,(255,247,245),.60)
   else:
    skin=(246,234,216);c=mix(skin,(167,139,137),.16*abs(u-.5)*2+.07*v)
    for side in (-1,1):
     ex=.5+side*.19;dx=side*(u-ex)/.142;dy=(v-(.47-(.026 if tile==14 else .065)*dx))/(.077 if tile==14 else .059)
     d=abs(dx)**1.55+abs(dy)**1.6
     if d<1.13:c=(39,35,48)
     if d<.79:c=(255,250,235)
     if d<.78 and abs(dx+.04)<.49:
      c=mix((36,88,83) if tile==14 else (103,20,45),(108,238,207) if tile==14 else (236,85,107),(dy+1)/2)
      if abs(dx+.04)<.17:c=(27,28,39)
      if (dx+.20)**2+(dy+.25)**2<.065:c=(255,255,248)
     if abs(dx)<1.0 and abs(v-(.345-(.018 if tile==14 else .055)*dx))<.015:c=(42,104,92) if tile==14 else (109,23,48)
    if abs(u-.5)<.037 and abs(v-.65)<.011:c=(184,152,145)
    if abs(u-.5)<.10 and abs(v-(.76-(.025 if tile==14 else -.018)*(1-abs(u-.5)*10)))<.011:c=(134,79,91)
   im.putpixel((ox,oy),(*c,255))
im.save(p)
# Arsene: scale the mask and crown together, add faceted plates and shoulder armour.
p=java/'ArseneDetailedClient.java';s=p.read_text(encoding='utf-8')
a='   // Central raised nose/forehead ridge';assert a in s
s=s.replace(a,'''   for(int side:new int[]{-1,1}){
    head.blade(14,side*1.88f,-5.72f,-.86f,side*2.24f,-4.20f,-.64f,.52f);
    head.blade(1,side*2.13f,-4.30f,-.71f,side*1.12f,-2.35f,-1.59f,.48f);
    head.blade(13,side*1.86f,-5.80f,-1.12f,side*.47f,-5.42f,-1.82f,.085f);
    for(int j=0;j<4;j++)head.blade(14,side*(1.79f-j*.23f),-4.12f+j*.60f,-1.22f,side*(1.42f-j*.22f),-3.78f+j*.60f,-1.52f,.105f);
   }
'''+a,1)
a='   for(int i=0;i<2;i++){';i=s.index(a,s.index('// Central raised nose/forehead ridge'))
s=s[:i]+'''   VoxelPortrait.enlarge(head,1.34f,1.12f,1.29f);
   for(int side:new int[]{-1,1}){
    body.loft(0,4,-.55f,side*2.75f,0,1.25f,1.52f,.16f,side*3.05f,0,1.63f,1.70f,1.25f,side*3.07f,0,1.36f,1.45f);
    body.blade(1,side*1.74f,-.32f,-1.22f,side*4.35f,.06f,-1.13f,.62f);
    body.blade(14,side*2.05f,-.50f,-1.61f,side*4.18f,-.20f,-1.49f,.15f);
   }
'''+s[i:]
s,n=re.subn(r'body\.loft\(0,20,-\.9f,[^;]+;', 'body.loft(0,8,-.9f,0,0,1.5f,1.16f,.15f,0,0,3.92f,1.95f,2,0,-.10f,3.45f,1.88f,4.3f,0,0,2.10f,1.28f,7.1f,0,0,1.48f,1.03f,9.2f,0,0,1.94f,1.30f,10.7f,0,0,2.15f,1.39f);',s,count=1)
s,n2=re.subn(r'arms\[i\]=body\.child\(side\*[^;]+;', 'arms[i]=body.child(side*4.15f,.15f,0);',s,count=1);assert n2==1
s=re.sub(r'arms\[i\]\.loft\(0,\d+,[^;]+;', 'arms[i].loft(0,8,-.35f,0,0,1.24f,1.28f,.45f,0,0,1.55f,1.44f,2.2f,0,0,1.20f,1.17f,5.05f,0,0,.78f,.79f);',s,count=1)
p.write_text(s,encoding='utf-8')
print('Moon Stick and layered hair; Phos/Cinnabar voxel faces and crystalline hair; Arsene enlarged mask and angular shoulders.')
