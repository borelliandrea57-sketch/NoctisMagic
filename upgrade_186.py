"""1.7.19: Giorno's compact adult portrait and coherent golden swept hair."""
from pathlib import Path
import sys,math,re
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'GiornoSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   VoxelPortrait.head(head,5,1,');b=s.index('   Part prev=head;',a)
s=s[:a]+'''   // A compact adult skull; broader jaw and gently beveled cheekbones.
   int faceStart=head.faces.size();
   head.loft(5,16,-6.80f,0,.12f,1.55f,1.50f,-6.30f,0,.08f,2.57f,2.36f,
      -5.40f,0,0,2.98f,2.58f,-4.20f,0,-.04f,2.94f,2.61f,
      -3.00f,0,-.12f,2.78f,2.49f,-1.80f,0,-.21f,2.35f,2.19f,
      -.68f,0,-.31f,1.62f,1.52f,0,0,-.34f,1.10f,1.06f);
   for(int i=faceStart;i<head.faces.size();i++){
    Q q=head.faces.get(i);
    boolean front=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.08f;
    head.faces.set(i,new Q(portrait(q.a(),front),portrait(q.b(),front),portrait(q.c(),front),portrait(q.d(),front),front?5:1));
   }
   head.loft(1,8,-.40f,0,.06f,.89f,.86f,.55f,0,.06f,1.13f,1.04f,1.40f,0,.06f,1.30f,1.19f);
   head.loft(1,8,-3.72f,0,-2.54f,.10f,.075f,-3.05f,0,-2.67f,.17f,.16f,-2.65f,0,-2.79f,.27f,.19f,-2.40f,0,-2.53f,.16f,.10f);
   // Crown shell overlaps the skull internally, without a tall cluster of spikes.
   head.loft(6,12,-8.04f,0,.22f,.82f,.84f,-7.74f,0,.23f,2.00f,1.91f,
      -7.18f,0,.24f,2.83f,2.58f,-6.35f,0,.28f,3.25f,2.85f,-5.78f,0,.43f,3.18f,2.64f);
   // Continuous rear and temple hair, clear of the eyes.
   Part rear=head.child(0,-6.02f,1.63f);
   rear.loft(6,12,-.52f,0,0,2.75f,1.16f,1.18f,0,.23f,3.04f,1.37f,
      2.90f,0,.34f,2.72f,1.28f,4.80f,0,.48f,2.17f,.94f,5.54f,0,.64f,1.30f,.67f);
   for(int side:new int[]{-1,1}){
    for(int j=0;j<5;j++){
     Part q=head.child(side*(2.72f+j*.035f),-6.52f+j*.16f,-.83f+j*.64f);
     q.loft(6,8,-.35f,side*.06f,0,.44f,.53f,.55f,side*.40f,.25f,.52f,.62f,
       1.84f,side*.34f,.52f,.45f,.54f,3.55f,side*.11f,1.02f,.28f,.32f,4.33f,0,1.22f,.045f,.06f);
    }
   }
   // Low, backward-swept sculpted ridges.
   for(int j=0;j<9;j++){
    float x=(j-4)*.64f;
    Part q=head.child(x,-7.17f,-.92f);
    q.loft(6,8,-.56f,0,.30f,.39f,.45f,-.86f,x*.07f,1.10f,.48f,.58f,
       -.14f,x*.04f,2.25f,.39f,.52f,1.26f,-x*.12f,3.0f,.075f,.12f);
   }
   // Three open-front rolled curls, with real recessed centres and sculpted golden rims.
   for(int j=0;j<3;j++){
    Part q=head.child((j-1)*1.87f,-6.23f+(j==1?-.20f:0),-2.67f);
    q.rz=(j-1)*.06f;
    roll(q,.66f,.76f);
    q.oval(7,0,0,.21f,.47f,.55f,.10f);
    for(int k=0;k<9;k++){
     float t=k*(float)Math.PI/4.5f;
     float x=(float)Math.cos(t)*.66f,y=(float)Math.sin(t)*.76f;
     q.blade(9,x,y,-.32f,x*.91f,y*.91f,-.33f,.12f);
    }
   }
'''+s[b:]
# The torus has a thinner tube than the original bulbous rolls.
a=' static class M extends EntityModel<JojoMob>{'
assert a in s
s=s.replace(a,''' static V portrait(V v,boolean f){
  return new V(v.x(),v.y(),v.z(),f?clamp(.5f+v.x()/6.45f):.025f,clamp((v.y()+6.80f)/6.80f),v.nx(),v.ny(),v.nz());
 }
 static V rollV(float a,float b,float w,float h,float u,float t){
  float ca=(float)Math.cos(a),sa=(float)Math.sin(a),cb=(float)Math.cos(b),sb=(float)Math.sin(b);
  return new V((w+.25f*cb)*ca,(h+.25f*cb)*sa,.32f*sb,u,t,ca*cb,sa*cb,sb);
 }
 static void roll(Part p,float w,float h){
  for(int i=0;i<24;i++)for(int j=0;j<8;j++){
   float a=i*(float)Math.PI/12,A=(i+1)*(float)Math.PI/12,b=j*(float)Math.PI/4,B=(j+1)*(float)Math.PI/4;
   p.faces.add(new Q(rollV(a,b,w,h,i/24f,j/8f),rollV(A,b,w,h,(i+1)/24f,j/8f),rollV(A,B,w,h,(i+1)/24f,(j+1)/8f),rollV(a,B,w,h,i/24f,(j+1)/8f),6));
  }
 }
'''+a,1)
s,n=re.subn(r'prev\.child\([^;]+?\);','prev.child(j==0?0:j%2==0?.12f:-.12f,j==0?-1.95f:1.48f,j==0?2.48f:.15f);',s,count=1)
assert n==1
# Eliminate the old high-relief brow blades and excessive shoulder-side head ornaments.
s=re.sub(r'head\.oval\(1,s\*[^;]+;', 'head.oval(1,s*2.82f,-3.03f,.22f,.32f,.65f,.40f);',s,count=1)
s=re.sub(r'head\.oval\(3,s\*[^;]+;', 'head.oval(3,s*2.99f,-2.52f,.12f,.14f,.19f,.12f);',s,count=1)
p.write_text(s,encoding='utf-8')
# Redraw the facial tile and gold hair materials without touching the purple suit.
p=assets/'textures/entity/giorno_sculpted.png';im=Image.open(p).convert('RGBA')
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for tile in (1,5,6,7,9):
 for y in range(128):
  v=max(0,min(1,(y-3)/121))
  for x in range(128):
   u=max(0,min(1,(x-3)/121));f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   if tile in (1,5):
    c=mix((236,184,147),(155,99,92),.14*v+.16*f)
    c=mix(c,(251,215,179),.26*g(.5,.44,.16,.27))
    if tile==5:
     for side in (-1,1):
      ex=.5+side*.175;dx=side*(u-ex)/.132;ey=.474-.020*dx;dy=(v-ey)/.066
      d=abs(dx)**1.85+abs(dy)**1.55
      c=mix(c,(149,91,80),.15*g(ex,.52,.15,.11))
      if d<1.08:c=(49,32,39)
      if d<.88:c=(245,234,217)
      if d<.85 and abs(dx+.04)<.49:
       c=mix((33,82,74),(104,181,140),(dy+.8)/1.6)
       if abs(dx+.04)<.17:c=(24,30,35)
       if (dx+.18)**2+(dy+.30)**2<.049:c=(255,250,237)
      if abs(dx)<1.02 and abs(v-(ey-.059+.013*dx*dx))<.010:c=(54,34,35)
      if abs(dx)<.96 and abs(v-(.353-.015*dx-.015*dx*dx))<.012:c=(125,88,34)
     c=mix(c,(165,98,87),.30*g(.5,.651,.045,.023))
     if f<.092 and abs(v-(.776-.011*(1-f/.092)))<.010:c=(117,57,65)
     c=mix(c,(211,134,119),.27*g(.5,.796,.065,.014))
   elif tile==7:c=mix((113,68,24),(168,113,40),.45*math.sin(u*math.pi)**2)
   else:
    wave=math.sin(u*math.pi*11+v*.9)
    c=mix((177,119,37),(246,209,91),.40+.29*math.sin(u*math.pi)**2)
    c=mix(c,(116,74,25),.30*max(0,-wave)**4)
    c=mix(c,(255,237,155),.36*max(0,wave)**4)
    if tile==9:c=mix(c,(255,229,138),.42)
   im.putpixel((tile%8*128+x,tile//8*128+y),(*c,255))
im.save(p)
print('Giorno: compact skull, complete temple hair and nape, low swept crown, three recessed rolls and refined portrait. Body and animated braid preserved.')
