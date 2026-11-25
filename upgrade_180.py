"""1.7.13: sculpt Faputa's facial volumes and asymmetric hair crown, without altering her body."""
from pathlib import Path
import sys,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'FaputaSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   VoxelPortrait.head(head,5,0,');b=s.index('   // A head-attached neck',a)
s=s[:a]+'''   // A faceted but fully volumetric skull. The forehead, cheekbones, muzzle and jaw have separate depth profiles.
   head.loft(5,20,-7.20f,0,.22f,1.62f,1.68f,-6.72f,0,.15f,2.65f,2.45f,
     -5.78f,0,.03f,3.03f,2.83f,-4.78f,0,-.06f,3.10f,2.82f,
     -3.74f,0,-.18f,2.98f,2.75f,-2.85f,0,-.25f,2.76f,2.67f,
     -1.86f,0,-.34f,2.39f,2.42f,-.92f,0,-.43f,1.84f,1.90f,
     -.25f,0,-.52f,1.10f,1.18f,0,0,-.52f,.81f,.89f);
   projectFace(head);
'''+s[b:]
# Face curvature must not distort the UV placement of the eyes.
s=s.replace('v.x()/6.4f','v.x()/6.65f',1).replace('(v.y()+6.9f)/6.9f','(v.y()+7.2f)/7.2f',1)
a='   head.loft(0,8,-2.74f,0,-2.40f,.16f,.11f,-2.35f,0,-2.57f,.24f,.19f,-2.08f,0,-2.36f,.15f,.09f);'
assert a in s
s=s.replace(a,'''   // Sculpted small feline bridge, nose tip and lower lip; cheek shadows follow the curved mesh.
   head.loft(0,12,-3.66f,0,-2.82f,.12f,.08f,-3.00f,0,-2.94f,.20f,.16f,-2.37f,0,-3.04f,.30f,.28f,-2.08f,0,-2.87f,.20f,.14f);
   head.oval(0,0,-1.41f,-2.36f,.43f,.12f,.18f);''',1)
s=s.replace('head.blade(0,side*.60f,-3.78f,-2.54f,side*1.92f,-4.34f,-2.50f,.20f);','head.blade(0,side*.57f,-4.02f,-2.80f,side*1.98f,-4.60f,-2.29f,.22f);',1)
# Lift the crown into an asymmetric, peaked silhouette instead of a flat lid.
a=s.index('   head.loft(1,12,-8.45f');b=s.index('   Part rear=',a)
s=s[:a]+'''   head.loft(1,16,-9.25f,-.38f,.48f,.46f,.55f,-8.93f,-.24f,.36f,1.46f,1.59f,-8.40f,-.10f,.30f,2.55f,2.47f,-7.54f,0,.20f,3.32f,2.98f,-6.46f,0,.30f,3.56f,3.12f,-5.92f,0,.35f,3.53f,3.06f);
   for(int j=0;j<7;j++){
    float x=(j-3)*.70f;
    Part tuft=head.child(x,-7.85f,.44f);
    float h=1.3f+(1-Math.abs(j-3)/3f)*.65f;
    tuft.loft(1,8,-h,-.22f,.34f,.03f,.04f,-h*.70f,-.14f,.28f,.29f,.33f,-.37f,0,.13f,.55f,.60f,.35f,0,0,.56f,.55f);
   }
'''+s[b:]
a=s.index('   for(int j=0;j<11;j++){\n    float x=(j-5)*.52f');b=s.index('   for(int j=0;j<11;j++){',a+8)
s=s[:a]+'''   // Individual swept locks; three distinct ruby markings on the ivory fringe.
   for(int j=0;j<11;j++){
    float x=(j-5)*.54f,dx=(j-5)*.15f;
    Part q=head.child(x,-7.65f,-2.13f);locks.add(q);
    float len=1.60f+1.06f*(float)Math.sin(j*Math.PI/10)+(j%3)*.18f;
    if(j==5)len=2.88f;
    q.loft(1,10,-.64f,0,.64f,.42f,.49f,.22f,dx*.16f,-.40f,.56f,.43f,len*.62f,dx*.55f,-.70f,.37f,.28f,len,dx,-.46f,.025f,.04f);
    if(j==2||j==5||j==8){
     Part mark=q.child(0,.36f,-.82f);
     mark.loft(7,6,-.28f,0,.07f,.035f,.035f,.17f,0,-.05f,.24f,.11f,.74f,dx*.25f,-.15f,.20f,.09f,1.15f,dx*.44f,-.08f,.025f,.03f);
    }
   }
   for(int side:new int[]{-1,1}){
    for(int j=0;j<3;j++){
     Part lock=head.child(side*(2.78f+j*.13f),-6.1f+j*.54f,-.70f+j*.22f);locks.add(lock);
     lock.loft(1,8,-.4f,0,.12f,.45f,.58f,1.0f,side*.22f,-.28f,.62f,.44f,2.8f,side*.46f,-.18f,.36f,.28f,4.25f,side*.70f,.08f,.035f,.04f);
    }
   }
'''+s[b:]
p.write_text(s,encoding='utf-8')
# Repaint the same facial material in both normal and enraged atlases, retain every other material.
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for rage in (False,True):
 p=assets/'textures/entity'/('faputa_rage.png' if rage else 'faputa_sculpted.png');im=Image.open(p).convert('RGBA')
 for y in range(128):
  v=(y-3)/121
  for x in range(128):
   u=(x-3)/121;f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   c=mix((134,100,76),(60,40,40),.32*min(1,f*1.7)+.12*v)
   c=mix(c,(184,139,96),.27*g(.5,.39,.12,.23))
   c=mix(c,(167,119,86),.16*g(.5,.71,.15,.13))
   for side in (-1,1):
    ex=.5+side*.182;dx=side*(u-ex)/.127
    ey=.493-(.055 if rage else .032)*dx
    dy=(v-ey)/(.087 if rage else .100)
    d=abs(dx)**1.65+abs(dy)**1.65
    c=mix(c,(59,36,34),.46*g(ex,.49,.15,.13))
    c=mix(c,(191,136,95),.26*g(.5+side*.24,.64,.09,.074))
    if d<1.15:c=(40,24,26)
    if d<.89:c=(223,205,170)
    if d<.85 and abs(dx+.03)<.57:
     c=mix((139,27,25) if rage else (139,82,14),(255,154,62) if rage else (255,210,65),(dy+1)/2)
     if abs(dx+.03)<(.10 if rage else .14):c=(25,17,20)
     if (dx+.20)**2+(dy+.33)**2<.060:c=(255,248,222)
     if (dx-.21)**2+(dy-.31)**2<.021:c=(253,217,125)
    if abs(dx)<1.06 and abs(v-(ey-.064))<.017:c=(43,24,24)
    if abs(dx)<1.07 and abs(v-(.355-(.057 if rage else .036)*dx))<.014:c=(70,43,37)
    if abs(dx)<.95 and abs(v-(ey+.094))<.008:c=mix(c,(76,45,41),.62)
   c=mix(c,(65,38,34),.45*g(.50,.668,.044,.018))
   mouth=.778-(.017 if not rage else .030)*(1-min(1,f/.12))+.015*(u-.5)
   if f<.112 and abs(v-mouth)<(.024 if rage else .010):c=(54,26,28)
   if rage and .045<f<.080 and mouth-.012<v<mouth+.013:c=(238,224,198)
   c=mix(c,(174,114,83),.30*g(.5,.81,.07,.013))
   im.putpixel((640+x,y),(*c,255))
 im.save(p)
print('Faputa: volumetric face, sculpted cheeks and muzzle, peaked layered ivory crown and larger golden eyes. Body unchanged.')
