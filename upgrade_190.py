"""1.7.23: angular Code Geass portraits, frequent affection, creative-mode stand defense."""
from pathlib import Path
import sys,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('            int first=head.faces.size();');b=s.index('                arms[i]=root.child(',a)
s=s[:a]+'''            // Planar cheekbones and a tapered angular jaw, with distinct male/female profiles.
            CinnabarClient.Model.angular(head,7,6,6.15f,-7.0f,0,
                -7.0f,0,.18f,2.02f,1.80f,-6.4f,0,.08f,cc?2.83f:2.70f,2.30f,
                -5.0f,0,.01f,cc?2.90f:2.76f,2.42f,-3.65f,0,-.09f,cc?2.72f:2.65f,2.37f,
                -2.15f,0,-.21f,cc?2.21f:2.16f,2.05f,-.75f,0,-.38f,cc?1.48f:1.24f,1.43f,0,0,-.49f,cc?.92f:.74f,.82f);
            CinnabarClient.Model.angular(head,7,7,3,-.35f,1.45f,-.35f,0,.12f,.83f,.84f,1.45f,0,.12f,1.09f,1.04f);
            // Narrow sculpted nose with a distinct bridge and tip.
            head.loft(7,6,-3.95f,0,-2.47f,.10f,.08f,-3.03f,0,-2.63f,.18f,.19f,-2.55f,0,-2.91f,.24f,.25f,-2.28f,0,-2.50f,.15f,.08f);
            for(int side:new int[]{-1,1})head.loft(7,6,-4.35f,side*2.76f,.02f,.14f,.20f,-3.75f,side*2.85f,.05f,.28f,.31f,-3.0f,side*2.70f,.10f,.14f,.16f);
            CinnabarClient.Model.angular(head,8,8,7.1f,-8.35f,-5.90f,
                -8.35f,cc?-.1f:-.46f,.45f,1.25f,1.28f,-7.96f,0,.30f,2.54f,2.15f,
                -7.20f,0,.23f,3.03f,2.65f,-6.12f,0,.36f,3.19f,2.73f,-5.90f,0,.42f,3.10f,2.65f);
            Part cap=head.child(0,-6.75f,1.57f);
            cap.loft(8,8,-.42f,0,0,2.65f,1.34f,1.1f,0,.44f,2.93f,1.48f,3.25f,0,.51f,2.75f,1.34f,5.50f,0,.31f,2.05f,1.04f,cc?6.9f:5.8f,0,.18f,1.29f,.40f);
            // Individual sweeping bangs, deliberately varying in length and direction.
            for(int j=0;j<9;j++){
                float x=-2.66f+j*.66f;Part q=head.child(x,-7.44f+(j%3)*.09f,-2.43f);
                float dx=cc?(j<4?-.32f:.25f):(-.74f+j*.20f);
                float len=cc?1.35f+(j%3)*.38f+(j==4?1.35f:0):2.12f+(j%3)*.48f+(j==2||j==5?1.36f:0);
                q.loft(8,6,-.41f,0,.30f,.47f,.43f,.52f,dx*.32f,-.36f,.58f,.35f,
                    len*.48f,dx*.62f,-.74f,.41f,.23f,len*.76f,dx*.88f,-.86f,.24f,.14f,len,dx,-.66f,.025f,.035f);
            }
            if(!cc){
                for(int j=0;j<7;j++){
                    float x=(j-3)*.73f;Part q=head.child(x,-7.62f,.58f);
                    float dx=(j-3)*.34f;
                    q.loft(8,6,-.35f,0,.15f,.39f,.43f,-.67f,dx*.32f,.64f,.45f,.48f,.19f,dx*.58f,1.25f,.35f,.32f,1.70f,dx,2.23f,.035f,.045f);
                }
            }else for(int j=0;j<13;j++){
                float t=j/12f,spread=(t-.5f)*4.2f;Part q=head.child(-2.76f+t*5.52f,-6.24f,2.11f);hair.add(q);
                float len=22.1f+1.9f*(float)Math.sin(t*Math.PI)+(j%3)*.42f;
                q.loft(j%5==0?11:8,6,-.25f,0,0,.44f,.53f,3,spread*.18f,.40f,.64f,.61f,9,spread*.38f,.88f,.63f,.50f,16,spread*.74f,.66f,.51f,.35f,len,spread,1.60f,.035f,.045f);
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                for(int j=0;j<(cc?4:4);j++){
                    Part lock=head.child(s*(2.83f+j*.12f),-6.66f+j*.35f,-.38f+j*.53f);hair.add(lock);
                    float len=cc?16.4f+j*1.6f:4.35f+j*.42f;
                    lock.loft(8,6,-.25f,0,.14f,.43f,.54f,1.15f,s*.42f,-.25f,.54f,.53f,len*.46f,s*.58f,.06f,.44f,.36f,len*.76f,s*(cc?.58f:.24f),.20f,.27f,.22f,len,s*(cc?.84f:.04f),.45f,.035f,.045f);
                }
'''+s[b:]
# Avoid a straight combed forehead; retain the existing embrace poses and clothing.
s=s.replace('amount*.13f+(float)Math.sin(age*.12+i*.55f)*.025f','amount*.065f+(float)Math.sin(age*.12+i*.55f)*.035f')
p.write_text(s,encoding='utf-8')
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def portrait(u,v,cc,expr):
 f=abs(u-.5);skin=(246,217,194) if cc else (235,202,180)
 def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
 c=mix(skin,(125,84,88),.26*min(1,f*2)+.09*v)
 c=mix(c,(255,239,218),.30*g(.49,.48,.13,.32))
 c=mix(c,(153,91,92),.16*(g(.22,.66,.10,.08)+g(.78,.66,.10,.08)))
 # Directional cast shadow from the fringe over brows and top halves of eyes.
 shadow=.405+.037*math.sin(u*17)+.021*math.sin(u*33) if not cc else .345+.022*math.sin(u*20)
 sh=(1-max(0,min(1,(v-shadow+.04)/.13)))*(.44 if not cc else .22)
 for side in (-1,1):
  ex=.5+side*(.177 if cc else .185);dx=side*(u-ex)/(.132 if cc else .138)
  ey=.465-(.014 if cc else .025)*dx
  half=.081 if cc else .060;dy=(v-ey)/half
  d=abs(dx)**1.75+abs(dy)**1.55
  c=mix(c,(123,78,91),.16*g(ex,.48,.15,.10))
  if expr:
   if abs(dx)<1.04 and abs(v-(ey-.030*(1-dx*dx)))<.010:c=(48,28,41)
   c=mix(c,(214,119,124),.19*g(ex,.63,.10,.07))
  else:
   if d<1.09:c=(45,27,42)
   if d<.85:c=(246,236,224)
   if d<.83 and abs(dx+.035)<.45:
    c=mix((102,59,18) if cc else (58,27,92),(251,200,61) if cc else (174,99,217),(dy+.8)/1.6)
    if abs(dx+.035)<.14:c=(27,20,35)
    if (dx+.17)**2+(dy+.24)**2<.036:c=(255,251,235)
   if abs(dx)<1.05 and abs(v-(ey-.053+.015*dx*dx))<.010:c=(39,25,38)
   if cc and .88<dx<1.10 and abs(v-(ey-.035))<.008:c=(39,25,38)
  brow=.348+(.012 if cc else -.018)*dx-.012*dx*dx
  if abs(dx)<.99 and abs(v-brow)<.010:c=(67,94,42) if cc else (40,28,43)
 c=mix(c,(122,83,97),sh)
 c=mix(c,(158,99,101),.30*g(.53,.653,.035,.035))
 c=mix(c,(255,230,208),.32*g(.485,.61,.020,.065))
 mouth=.77+(.024 if expr else .004)*(1-min(1,f/.105))-(.009 if cc else 0)*(u-.5)
 if f<.105 and abs(v-mouth)<.009:c=(114,53,67)
 c=mix(c,(224,154,143),.19*g(.5,.795,.075,.013))
 return c
for name in ('cc','lelouch'):
 cc=name=='cc'
 for suffix in ('','_soft','_happy'):
  p=assets/'textures/entity'/f'{name}_sculpted{suffix}.png';im=Image.open(p).convert('RGBA')
  for tile in (6,7,8,11):
   for y in range(128):
    v=(y-3)/121
    for x in range(128):
     u=(x-3)/121
     if tile==6:c=portrait(u,v,cc,suffix)
     elif tile==7:c=mix((246,217,194) if cc else (235,202,180),(125,84,88),.13+.12*abs(u-.5)+.04*v)
     else:
      flow=math.sin(u*math.pi*13+v*3+.38*math.sin(v*7))
      base=(91,143,49) if cc else (25,20,39);hi=(167,202,86) if cc else (78,63,100)
      c=mix(base,hi,.22+.24*max(0,flow)**5)
      c=mix(c,(42,79,27) if cc else (9,8,19),.27*max(0,-flow)**5)
      c=mix(c,hi,.32*math.exp(-((v-.31-.07*math.sin(u*5))/.075)**2))
     im.putpixel((tile%8*128+x,tile//8*128+y),(*c,255))
  im.save(p)
# Affection: shorter initial wait, regular opportunities, no need to roll a random chance.
p=java/'DramaGuest.java';s=p.read_text(encoding='utf-8')
for a,b in [('affectionCooldown=900','affectionCooldown=120'),('1000+random.nextInt(1400)','180+random.nextInt(240)'),('tickCount%100!=0||distanceTo(q)>3.4||random.nextInt(3)!=0','tickCount%20!=0||distanceTo(q)>5.0'),('approachTime=65','approachTime=105'),('affectionCooldown=300','affectionCooldown=80')]:
 assert a in s,a;s=s.replace(a,b)
# Most encounters are embraces (including lifted hugs), with occasional kiss.
s=s.replace('int mode=1+random.nextInt(3);','int mode=random.nextInt(5)<2?1:random.nextBoolean()?2:3;',1)
p.write_text(s,encoding='utf-8')
# Creative-mode testing: stand summons, follows and performs visible punches; creative immunity stays intact.
p=java/'JojoMob.java';s=p.read_text(encoding='utf-8')
a='(!(attacker instanceof Player p)||!p.isCreative()&&!p.isSpectator())';assert a in s
s=s.replace(a,'(!(attacker instanceof Player p)||!p.isSpectator())',1)
a='(victim instanceof Player p&&(p.isCreative()||p.isSpectator()))';assert a in s
s=s.replace(a,'(victim instanceof Player p&&p.isSpectator())',1)
a='        if(getTarget()!=victim)setTarget(victim);';assert a in s
s=s.replace(a,'''        if(victim instanceof Player creative&&creative.isCreative()){
            // Normal target goals reject creative players. Follow and demonstrate attacks manually.
            if(getTarget()!=null)setTarget(null);
            getLookControl().setLookAt(creative,35,35);
            double d=distanceToSqr(creative);
            if(d>5.0)getNavigation().moveTo(creative,1.35);
            else{
                getNavigation().stop();
                if(tickCount%12==0){
                    swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                    l.broadcastEntityEvent(this,(byte)82);
                    l.sendParticles(ParticleTypes.CRIT,creative.getX(),creative.getY()+1,creative.getZ(),9,.27,.40,.27,.12);
                    playSound(SoundEvents.PLAYER_ATTACK_STRONG,.8f,1.1f);
                    if(ability<=0){ability=100;NpcDialogue.say(l,Component.literal(variant()==3?"Star Platinum: ORA ORA ORA!":variant()==4?"Sticky Fingers: ARI ARI ARI!":"Gold Experience: MUDA MUDA MUDA!"));}
                }
            }
            return;
        }
'''+a,1)
p.write_text(s,encoding='utf-8')
print('Angular Code Geass heads with cast-shadowed eyes and layered bangs; frequent affection; Stand defense in survival and creative.')
