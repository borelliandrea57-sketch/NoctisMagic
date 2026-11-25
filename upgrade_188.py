"""1.7.21: Dante's expressive combat and idle poses, taller hitbox, stronger Rebellion."""
from pathlib import Path
import sys,re,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
s,n=re.subn(r'(EntityType\.Builder\.<Dante>of\(Dante::new,MobCategory\.MISC\)\.sized\()[^)]*\)',r'\g<1>.86f,2.35f)',s,count=1);assert n==1
s,n=re.subn(r'(REBELLION=ITEMS\.register\("rebellion",\(\)->new net\.minecraft\.world\.item\.SwordItem\(net\.minecraft\.world\.item\.Tiers\.NETHERITE,)\d+,',r'\g<1>30,',s,count=1);assert n==1
p.write_text(s,encoding='utf-8')
p=java/'Dante.java';s=p.read_text(encoding='utf-8')
s=s.replace('int attack,pose,mode,cd=40;','int attack,pose,mode,cd=40; private int styleTicks,styleMode;',1)
assert 'private int styleTicks,styleMode;' in s
s=s.replace('add(Attributes.ATTACK_DAMAGE,28)','add(Attributes.ATTACK_DAMAGE,40)',1).replace('getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(32)','getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(46)',1).replace('duel?24:18','duel?42:34',1)
s=s.replace('super.tick();if(pose>0)pose--;if(cd>0)cd--;','super.tick();if(pose>0)pose--;if(styleTicks>0)styleTicks--;if(cd>0)cd--;',1)
a='LivingEntity t=getTarget();if(t==null||!t.isAlive()||!hasLineOfSight(t))return;'
assert a in s
s=s.replace(a,'''LivingEntity t=getTarget();
        if(!duel&&(t==null||!t.isAlive())&&owner!=null&&distanceTo(owner)<8&&getDeltaMovement().horizontalDistanceSqr()<.003&&tickCount%160==0){
            l.broadcastEntityEvent(this,(byte)(102+random.nextInt(3)));
        }
        if(t==null||!t.isAlive()||!hasLineOfSight(t))return;''',1)
a='if(id==100||id==101){pose=18;mode=id-100;return;}'
assert a in s
s=s.replace(a,'if(id==100||id==101){pose=18;mode=id-100;styleTicks=0;return;}if(id>=102&&id<=104){styleMode=id-101;styleTicks=60;return;}',1)
a='    public int mode(){return mode;}';assert a in s
s=s.replace(a,a+'''
    public int styleMode(){return styleTicks>0?styleMode:0;}
    public float styleAmount(){return styleTicks<=0?0:Math.min(1f,Math.min((60-styleTicks)/9f,styleTicks/10f));}
    public String faceStyle(){
        if(hurtTime>0)return "_grimace";
        if(action()>.05f)return mode==1?"_focus":"_rage";
        if(styleMode()!=0)return "_smirk";
        return (tickCount+getId()*13)%97<4?"_blink":"";
    }''',1)
p.write_text(s,encoding='utf-8')
p=java/'WitchHunterClient.java';s=p.read_text(encoding='utf-8')
s,n=re.subn(r'else p\.scale\([0-9.]+f,[0-9.]+f,[0-9.]+f\);','else p.scale(1.14f,1.25f,1.14f);',s,count=1);assert n==1
a='   show(fore[1],sword,!witch&&!shoot&&casting);show(body,backSword,!witch&&(!casting||shoot));'
assert a in s
s=s.replace(a,'''   if(!witch){
    Dante d=(Dante)e;
    float f=d.styleAmount()*(1-Math.min(1f,walk*4));
    body.rx=0;body.rz=0;head.rz=0;
    if(casting){
     float sweep=(float)Math.sin(a*Math.PI);
     body.ry=shoot?.25f*a:(.55f*a-.20f*sweep);
     body.rx=shoot?-.06f*a:.18f*a;
     head.rz=-.07f*a;
     if(!shoot){
      arms[1].rx=-2.35f*a;arms[1].rz=-.32f*a;fore[1].rx=-.48f*a;
      arms[0].rx=-.35f*a;arms[0].rz=.36f*a;
      legs[0].rx-=.18f*a;legs[1].rx+=.20f*a;
      cloth[0].rz+=.30f*a;cloth[1].rz-=.30f*a;
     }else{
      arms[0].rx=-1.70f*a;arms[1].rx=-1.53f*a;
      arms[0].rz=.38f*a;arms[1].rz=-.32f*a;
      fore[0].rx=-.24f*a;fore[1].rx=-.14f*a;
     }
    }else if(f>.01f){
     body.ry=.18f*f;body.rz=-.055f*f;head.rz=.12f*f;head.rx-=.075f*f;
     if(d.styleMode()==1){
      // Cocky arms folded across chest.
      arms[0].rx=-.82f*f;arms[1].rx=-.82f*f;
      arms[0].rz=.36f*f;arms[1].rz=-.36f*f;
      fore[0].rx=-1.22f*f;fore[1].rx=-1.28f*f;
     }else if(d.styleMode()==2){
      // Dramatic one-handed weapon flourish.
      arms[1].rx=-1.88f*f;arms[1].rz=-.28f*f;fore[1].rx=-.54f*f;
      arms[0].rx=-.25f*f;arms[0].rz=.38f*f;
     }else{
      // Two-finger salute silhouette, hand beside forehead.
      arms[1].rx=-1.40f*f;arms[1].rz=-.38f*f;fore[1].rx=-1.42f*f;
      arms[0].rz=.31f*f;
     }
    }
    boolean flourish=!casting&&d.styleMode()==2&&f>.18f;
    show(fore[1],sword,(!shoot&&casting)||flourish);show(body,backSword,(!casting||shoot)&&!flourish);
   }else{
    show(fore[1],sword,false);show(body,backSword,false);
   }''',1)
a='(witch?"bayonetta":"dante")+"_sculpted.png"';assert a in s
s=s.replace(a,'(witch?"bayonetta_sculpted":"dante_sculpted"+((Dante)e).faceStyle())+".png"',1)
p.write_text(s,encoding='utf-8')
# Expression atlases retain the existing costume, weapon and hair shading.
base=Image.open(assets/'textures/entity/dante_sculpted.png').convert('RGBA')
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for expr in ('smirk','focus','rage','grimace','blink'):
 im=base.copy()
 for y in range(128):
  v=(y-3)/121
  for x in range(128):
   u=(x-3)/121;f=abs(u-.5);c=im.getpixel((640+x,y))[:3]
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   for side in (-1,1):
    ex=.5+side*.181;dx=side*(u-ex)/.118
    if abs(dx)<1.35 and .325<v<.57:
     skin=mix((229,187,161),(135,83,78),.24*max(0,min(1,(f-.18)*4))+.09*v)
     c=mix(c,skin,.99)
     ey=.47-(.045 if expr in ('rage','grimace') else .015)*dx
     half=.061 if expr=='rage' else .044 if expr=='focus' else .038 if expr=='smirk' else .032
     dy=(v-ey)/half;d=abs(dx)**1.7+abs(dy)**1.5
     if expr in ('blink','grimace'):
      if abs(dx)<1.03 and abs(v-(ey-.012*(1-dx*dx)))<.011:c=(51,31,37)
     else:
      if d<1.13:c=(48,29,35)
      if d<.84:c=(242,234,225)
      if d<.81 and abs(dx)<.40:c=mix((46,71,89),(130,185,220),(dy+.7)/1.4)
      if d<.78 and abs(dx)<.15:c=(22,24,33)
      if (dx+.14)**2+(dy+.25)**2<.045:c=(255,251,240)
     brow=.365-(.055 if expr in ('rage','grimace') else .024)*dx-(.025 if expr=='smirk' and side==1 else 0)
     if abs(dx)<1.08 and abs(v-brow)<.013:c=(114,106,104)
   if .73<v<.87 and f<.18:
    c=mix(c,(225,177,151),.88)
    if expr=='smirk':
     m=.786-.035*(u-.5)/.14
     if f<.13 and abs(v-m)<.013:c=(94,43,49)
     if f<.095 and m-.012<v<m-.003:c=(239,225,207)
    elif expr in ('rage','grimace'):
     m=.785+.012*math.cos((u-.5)*12)
     if f<.13 and abs(v-m)<.028*(1-f/.14):c=(61,28,34)
     if f<.10 and m-.015<v<m+.005:c=(240,224,209)
    else:
     if f<.09 and abs(v-.78)<.009:c=(103,51,54)
   im.putpixel((640+x,y),(*c,255))
 im.save(assets/'textures/entity'/f'dante_sculpted_{expr}.png')
print('Dante: taller mesh and hitbox, stronger sword, expressive face variants, three idle poses and enhanced combat animation.')
