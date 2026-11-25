"""1.7.4: sculpted Faputa fur, angular muscular Giorno and taller Bayonetta."""
from pathlib import Path
import sys,re,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'FaputaSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   // Cream crown');b=s.index('   for(int i=0;i<2;i++){',a)
s=s[:a]+'''   // Complete ivory crown with layered asymmetrical fringe and long rear mane.
   head.loft(1,12,-8.45f,0,.12f,1.35f,1.52f,-8.05f,0,.10f,2.60f,2.42f,-7.12f,0,.15f,3.52f,3.02f,-5.95f,0,.35f,3.65f,3.10f);
   Part rear=head.child(0,-6.60f,1.65f);
   rear.loft(1,12,-.5f,0,0,2.75f,1.35f,1.2f,0,.36f,3.16f,1.54f,4.1f,0,.8f,3.04f,1.39f,7.2f,0,1.5f,2.3f,.74f,9.5f,0,2.1f,.35f,.19f);
   for(int j=0;j<11;j++){
    float x=(j-5)*.52f,dx=(j-5)*.12f;
    Part q=head.child(x,-7.7f,-2.04f);locks.add(q);
    float len=1.8f+1.12f*(float)Math.sin(j*Math.PI/10);if(j==5)len=3.28f;
    q.loft(j==2||j==5||j==8?7:1,8,-.48f,0,.46f,.48f,.56f,.55f,dx*.2f,-.22f,.63f,.48f,len*.63f,dx*.55f,-.40f,.41f,.29f,len,dx,-.12f,.035f,.05f);
    q.blade(1,-.2f,.2f,-.47f,dx*.8f,len*.82f,-.29f,.20f);
   }
   for(int j=0;j<11;j++){
    float x=(j-5)*.54f;Part q=head.child(x,-6.5f,2.25f);locks.add(q);
    float spread=(j-5)*.31f,len=10.2f+2.2f*(float)Math.sin(j*Math.PI/10);
    q.loft(1,8,-.4f,0,0,.57f,.64f,2,spread*.18f,.24f,.73f,.63f,5,spread*.53f,.91f,.63f,.47f,len*.8f,spread,1.60f,.40f,.26f,len,spread*1.4f,2.12f,.04f,.05f);
   }
'''+s[b:]
a='    // Thick furred haunches';assert a in s
s=s.replace(a,'''    // Layered ears, inner folds and pointed cheek silhouettes.
    for(int j=0;j<5;j++){
     float t=.55f+j*.84f;
     ears[i].blade(1,s*.71f,t,.53f,s*(1.31f-j*.14f),t+1.12f,.72f,.56f);
     ears[i].blade(2,-s*.32f,t,-1.15f,-s*.25f,t+.78f,-1.22f,.17f);
    }
    for(int j=0;j<2;j++){
     int k=i*2+j;Part paw=fore[k];
     float end=(j==0?5.0f:4.25f)*1.14f;
     for(int n=0;n<5;n++){
      float y=.9f+n*.65f;
      paw.blade(1,-s*1.1f,y,-.68f,-s*1.75f,y+1.30f,-.25f,.87f);
      paw.blade(1,s*1.15f,y,-.37f,s*1.78f,y+1.25f,.22f,.78f);
     }
     for(int n=0;n<3;n++){
      float x=(n-1)*.70f;
      Part knuckle=paw.child(x,end-.62f,-.54f);
      knuckle.loft(1,8,-.3f,0,0,.45f,.44f,.35f,0,-.07f,.48f,.41f,.95f,0,-.10f,.25f,.27f);
      paw.blade(6,x,end+.18f,-.57f,x,end+1.80f,-1.11f,.39f);
     }
    }
    // Thick furred haunches''',1)
a='   // Three individually animated';assert a in s
s=s.replace(a,'''   // Golden gear ornaments and a visible harness over the upper body.
   for(int side:new int[]{-1,1}){
    body.blade(3,side*1.76f,-.18f,-2.1f,side*1.92f,-1.84f,-.50f,.36f);
    body.blade(4,side*1.98f,-1.78f,-.45f,side*1.58f,-2.0f,.97f,.31f);
    Part gear=body.child(side*1.62f,.05f,-2.10f);
    gear.oval(3,0,0,0,1.24f,1.24f,.26f);
    gear.oval(4,0,0,-.24f,.91f,.91f,.13f);
    for(int n=0;n<10;n++){
     float a=n*(float)Math.PI/5;Part tooth=gear.child((float)Math.sin(a)*1.13f,(float)Math.cos(a)*1.13f,-.09f);tooth.rz=-a;
     tooth.loft(3,4,-.27f,0,0,.22f,.20f,.28f,0,0,.22f,.20f);
    }
    for(int n=0;n<6;n++){
     float a=n*(float)Math.PI/3;gear.blade(3,0,0,-.40f,(float)Math.cos(a)*.80f,(float)Math.sin(a)*.80f,-.40f,.19f);
    }
    gear.oval(3,0,0,-.46f,.25f,.25f,.12f);
   }
   // Three individually animated''',1)
a='    t.loft(1,32,';i=s.index(a);j=s.index(';',i)+1
s=s[:i]+'''    t.loft(1,12,-.65f,0,0,.66f,.84f,1.5f,0,0,1.82f,1.42f,3.8f,0,.5f,2.65f,1.82f,6.0f,.15f,.92f,2.30f,1.32f,len-1.2f,.35f,1.05f,1.09f,.72f,len,.54f,.8f,.035f,.05f);
    for(int k=0;k<8;k++){
     float y=1.25f+k*(len-2.1f)/8f,w=(float)Math.sin(k*Math.PI/9)*1.45f+.63f;
     for(int side:new int[]{-1,1})t.blade(1,side*w,y,.46f,side*(w+.78f),y+1.30f,.83f,.92f);
     t.blade(1,0,y,1.11f,.42f,y+1.20f,1.64f,.62f);
    }'''+s[j:]
# More ear/leg texture and longer rear silhouette; preserve 4 independent animated limbs.
p.write_text(s,encoding='utf-8')
for fn in ('faputa_sculpted.png','faputa_rage.png'):
 p=assets/'textures/entity'/fn;im=Image.open(p).convert('RGBA')
 for tile in (1,2,3,4,6,7):
  for y in range(128):
   v=y/127
   for x in range(128):
    u=x/127;ox=tile*128+x;old=im.getpixel((ox,y));c=old[:3]
    if tile==1:
     flow=math.sin(u*math.pi*32+v*5+.8*math.sin(v*9))
     tuft=.78+.19*max(0,flow)**3+.10*math.sin((u+v*.17)*math.pi*8)**2
     c=tuple(int(max(0,min(255,a*tuft+14))) for a in c)
    elif tile==2:
     c=tuple(int(max(0,min(255,a*(.88+.15*math.sin(u*math.pi))))) for a in c)
    elif tile in (3,4):
     v0=.72+.40*math.sin(u*math.pi)**3+.13*math.cos(v*math.pi*5)**6
     c=tuple(int(max(0,min(255,a*v0))) for a in c)
    elif tile==6:
     c=(int(119+103*math.sin(u*math.pi)**2),int(16+37*math.sin(u*math.pi)**2),int(27+49*math.sin(u*math.pi)**2))
    im.putpixel((ox,y),(*c,255))
 im.save(p)
# Giorno: faceted square jaw, substantial shoulders and geometric gold hair.
p=java/'GiornoSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   head.loft(5,32,');b=s.index('   project(head,5,false);',a)
s=s[:a]+'''   VoxelPortrait.head(head,5,1,6.2f,7.85f,
      -7.85f,2.26f,2.08f,.10f,.36f,-7.18f,2.93f,2.51f,.04f,.42f,
      -5.45f,3.03f,2.60f,0,.44f,-3.55f,2.90f,2.46f,-.10f,.46f,
      -1.50f,2.42f,2.04f,-.16f,.42f,-.38f,1.81f,1.55f,-.25f,.34f,0,1.38f,1.23f,-.25f,.29f);
   head.loft(1,8,-.45f,0,.06f,.90f,.87f,.55f,0,.06f,1.15f,1.04f,1.45f,0,.06f,1.32f,1.20f);
'''+s[b+len('   project(head,5,false);'):]
s=s.replace('AngularHeads.apply(head,5,.86f,.97f,.93f,.15f);','',1)
# Faceted torso rather than smooth oval; widen top and keep a tapered waist.
s,n=re.subn(r'body\.loft\(8,64,[^;]+;', 'body.loft(8,8,-1,0,0,1.9f,1.53f,.15f,0,0,5.05f,2.60f,1.7f,0,-.10f,4.92f,2.75f,3.2f,0,-.10f,4.52f,2.75f,5.6f,0,0,3.54f,2.12f,8.6f,0,0,2.77f,1.79f,10.8f,0,0,3.28f,2.03f);',s,count=1)
assert n==1
# Update shoulders on the animated arms and add structured fabric shoulder panels.
s,n=re.subn(r'arm\[i\]=body\.child\([^;]+;', 'arm[i]=body.child(s*5.0f,.42f,0);',s,count=1);assert n==1
s,n=re.subn(r'arm\[i\]\.loft\(0,\d+,[^;]+;', '''arm[i].loft(0,8,-.75f,0,0,1.62f,1.70f,.25f,0,0,2.20f,2.05f,1.9f,0,0,2.04f,1.91f,3.2f,0,0,1.72f,1.63f,4.75f,0,0,1.26f,1.26f);
    arm[i].loft(0,4,-.55f,0,0,1.82f,1.79f,.30f,s*.19f,0,2.33f,1.98f,1.14f,s*.12f,0,2.15f,1.83f);
    arm[i].blade(3,-s*1.54f,.10f,-1.31f,s*1.58f,.15f,-1.31f,.16f);
    arm[i].blade(2,s*1.35f,1.22f,-1.50f,s*.80f,3.60f,-1.24f,.33f);''',s,count=1);assert n==1
# Keep the three signature hair rolls open, add raised outer rim and swept-back cap.
s=s.replace('q.oval(6,0,0,.10f,.44f,.49f,.21f);','q.oval(7,0,0,.28f,.31f,.38f,.12f);',1)
s=s.replace('curl(q,.68f,.78f);','curl(q,.88f,1.03f);',1)
s=s.replace('for(int i=0;i<28;i++)for(int j=0;j<10;j++)','for(int i=0;i<28;i++)for(int j=0;j<10;j++)',1)
s=re.sub(r'head\.loft\(6,24,[^;]+;', 'head.loft(6,8,-9.1f,0,.25f,1.72f,1.64f,-8.65f,0,.20f,2.64f,2.49f,-7.55f,0,.31f,3.30f,2.95f,-6.1f,0,.50f,3.29f,2.88f);',s,count=1)
a='   Part prev=head;';assert a in s
s=s.replace(a,'''   // Additional sharp swept hair layers across the back and around the braid.
   for(int j=0;j<11;j++){
    float x=(j-5)*.54f;
    head.blade(6,x,-7.45f,1.15f,x*.80f,-9.70f,2.78f,.80f);
    head.blade(9,x-.10f,-7.65f,1.04f,x*.80f,-9.60f,2.69f,.16f);
    head.blade(6,x,-6.45f,2.45f,x*.58f,-3.2f,2.70f,.77f);
   }
'''+a,1)
s=re.sub(r'p\.scale\([0-9.]+f,[0-9.]+f,[0-9.]+f\);','p.scale(1.24f,1.19f,1.16f);',s,count=1)
p.write_text(s,encoding='utf-8')
# Bayonetta: body scaling only; leave Dante unchanged.
p=java/'WitchHunterClient.java';s=p.read_text(encoding='utf-8')
s,n=re.subn(r'if\(witch\)p\.scale\([^)]+\);','if(witch)p.scale(1.24f,1.40f,1.21f);',s,count=1);assert n==1
p.write_text(s,encoding='utf-8')
print('Faputa fur layers, claw and gear detail; broad angular Giorno; taller Bayonetta.')
