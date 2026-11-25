"""1.7.22: standalone angular Cinnabar, flowing ruby locks and liquid-metal combat."""
from pathlib import Path
import sys,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'SculptedGuestsClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.CINNABAR.get(),c->new R<GemGuest>(c,3));'
assert a in s;s=s.replace(a,'e.registerEntityRenderer(Noctis.CINNABAR.get(),CinnabarClient.Renderer::new);',1);p.write_text(s,encoding='utf-8')
(java/'CinnabarClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import java.util.*;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
public final class CinnabarClient{
 static final class Renderer extends MobRenderer<GemGuest,Model>{
  Renderer(EntityRendererProvider.Context c){super(c,new Model(),.36f);}
  @Override public ResourceLocation getTextureLocation(GemGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/cinnabar_rework.png");}
 }
 static final class Model extends EntityModel<GemGuest>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=root.child(0,-1,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shins=new Part[2],orbs=new Part[3];
  final List<Part> locks=new ArrayList<>(),fringe=new ArrayList<>();
  // Rectangular cross sections with small beveled corners: genuinely flat front and side planes.
  static float[][] contour(float w,float d,float b){
   b=Math.min(b,Math.min(w,d)*.80f);
   return new float[][]{{-w+b,-d},{w-b,-d},{w,-d+b},{w,d-b},{w-b,d},{-w+b,d},{-w,d-b},{-w,-d+b}};
  }
  static void angular(Part p,int material,int front,float maxW,float top,float bottom,float... rings){
   int n=rings.length/5;
   for(int k=0;k<n-1;k++){
    int a=k*5,b=(k+1)*5;
    float[][] A=contour(rings[a+3],rings[a+4],.36f),B=contour(rings[b+3],rings[b+4],.36f);
    for(int j=0;j<8;j++){
     int next=(j+1)%8;
     float dx=A[next][0]-A[j][0],dz=A[next][1]-A[j][1],len=(float)Math.hypot(dx,dz);
     float nx=dz/len,nz=-dx/len;boolean face=j==0||j==1||j==7;
     int mat=face?front:material;
     p.faces.add(new Q(vertex(A[j],rings,a,j/8f,face,maxW,top,bottom,nx,nz),vertex(B[j],rings,b,j/8f,face,maxW,top,bottom,nx,nz),vertex(B[next],rings,b,(j+1)/8f,face,maxW,top,bottom,nx,nz),vertex(A[next],rings,a,(j+1)/8f,face,maxW,top,bottom,nx,nz),mat));
    }
   }
   for(int end:new int[]{0,(n-1)*5}){
    float[][] C=contour(rings[end+3],rings[end+4],.36f);float ny=end==0?-1:1;
    V center=new V(rings[end+1],rings[end],rings[end+2],.5f,.5f,0,ny,0);
    for(int j=0;j<8;j++){
     float[] A=C[j],B=C[(j+1)%8];
     V a=new V(A[0]+rings[end+1],rings[end],A[1]+rings[end+2],.15f,.15f,0,ny,0),b=new V(B[0]+rings[end+1],rings[end],B[1]+rings[end+2],.85f,.85f,0,ny,0);
     p.faces.add(end==0?new Q(center,a,b,center,material):new Q(center,b,a,center,material));
    }
   }
  }
  static V vertex(float[] p,float[] r,int i,float u,boolean f,float width,float top,float bottom,float nx,float nz){
   float x=p[0]+r[i+1],y=r[i],z=p[1]+r[i+2];
   return new V(x,y,z,f?Math.max(.02f,Math.min(.98f,.5f+x/width)):u,Math.max(.02f,Math.min(.98f,(y-top)/(bottom-top))),nx,0,nz);
  }
  Model(){
   // Straight-edged tailored jacket, squared shoulders and fitted waist.
   angular(body,10,10,7.4f,-.45f,11, -.45f,0,0,2.35f,1.55f,0,0,0,3.40f,1.72f,2.2f,0,0,3.18f,1.68f,5.8f,0,0,2.42f,1.45f,8.8f,0,0,2.23f,1.36f,11,0,0,2.75f,1.56f);
   // White shirt with actual pointed collar and black tie, not oval chest patches.
   angular(body,11,11,4,-.30f,5.3f,-.30f,0,-1.54f,1.43f,.22f,1.35f,0,-1.71f,1.24f,.16f,4.6f,0,-1.58f,.50f,.08f,5.3f,0,-1.48f,.08f,.04f);
   for(int side:new int[]{-1,1})body.blade(11,side*1.31f,.05f,-1.94f,side*.25f,2.35f,-1.89f,1.02f);
   body.blade(28,0,1.08f,-2.04f,0,5.75f,-1.67f,.73f);
   angular(body,16,16,5.9f,9.5f,10.3f,9.5f,0,0,2.65f,1.56f,10.3f,0,0,2.77f,1.66f);
   body.oval(16,0,9.93f,-1.72f,.45f,.31f,.10f);
   angular(head,17,15,6.25f,-6.75f,0,-6.75f,0,.16f,2.08f,1.74f,-6.14f,0,.09f,2.76f,2.28f,-4.77f,0,0,2.83f,2.40f,-3.02f,0,-.10f,2.60f,2.28f,-1.43f,0,-.20f,2.03f,1.93f,-.35f,0,-.30f,1.26f,1.20f,0,0,-.32f,.95f,.94f);
   angular(head,17,17,3,-.4f,1.4f,-.4f,0,.1f,.88f,.80f,1.4f,0,.1f,1.03f,.96f);
   head.loft(17,6,-3.7f,0,-2.44f,.12f,.09f,-2.92f,0,-2.59f,.19f,.15f,-2.48f,0,-2.78f,.23f,.23f,-2.27f,0,-2.51f,.15f,.08f);
   // Continuous asymmetric crown with deep red faceted crystal planes.
   angular(head,13,13,7,-8.1f,-5.7f,-8.1f,-.43f,.34f,1.31f,1.21f,-7.7f,-.24f,.21f,2.63f,2.28f,-6.92f,0,.23f,3.10f,2.66f,-5.7f,0,.51f,3.02f,2.40f);
   for(int j=0;j<11;j++){
    float x=(j-5)*.56f,side=(j-5)*.22f,len=12.8f+2.2f*(float)Math.sin(j*Math.PI/10)+(j%3)*.49f;
    Part q=head.child(x,-7.4f,2.18f);locks.add(q);
    q.loft(13,6,-.42f,0,.05f,.48f,.53f,1.75f,side*.22f,.49f,.68f,.61f,4.9f,side*.65f,.94f,.59f,.47f,7.7f,side*.82f,.46f,.52f,.37f,10.4f,side*1.09f,.75f,.39f,.29f,len,side*1.55f,1.48f,.035f,.04f);
   }
   for(int side:new int[]{-1,1})for(int j=0;j<4;j++){
    Part q=head.child(side*(2.65f+j*.24f),-6.9f+j*.33f,-.48f+j*.54f);locks.add(q);
    float len=10.5f+j*.77f+(side<0?1.25f:0);
    q.loft(13,6,-.35f,0,0,.41f,.57f,1.7f,side*.65f,-.28f,.61f,.53f,4.1f,side*.81f,.08f,.49f,.40f,7.1f,side*.19f,-.45f,.38f,.27f,len*.84f,side*.42f,-.26f,.25f,.21f,len,side*.92f,.34f,.035f,.04f);
   }
   // Long S-curved fringe in front of the face, deliberately crossing forehead and cheek.
   for(int j=0;j<7;j++){
    float x=-2.56f+j*.75f;Part q=head.child(x,-7.65f,-2.78f);fringe.add(q);
    float len=j==2?8.5f:j==3?6.7f:j==1?5.5f:2.4f+(j%3)*.51f;
    float drift=j<=3?1.60f:-.80f;
    q.loft(13,6,-.34f,0,.11f,.40f,.38f,.62f,drift*.22f,-.23f,.54f,.34f,len*.36f,drift*.64f,-.55f,.45f,.25f,len*.64f,drift*.41f,-.78f,.30f,.18f,len*.83f,drift*.16f,-.87f,.22f,.13f,len,drift*.79f,-.55f,.025f,.035f);
   }
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;Part a=arms[i]=root.child(side*3.48f,.22f,0);
    angular(a,10,10,3.2f,-.45f,3.2f,-.45f,0,0,.98f,1.17f,.05f,side*.13f,0,1.28f,1.34f,2.55f,side*.12f,0,1.10f,1.12f,3.2f,0,0,.94f,.93f);
    angular(a,17,17,2,3.1f,6.3f,3.1f,0,0,.75f,.76f,6.3f,0,0,.68f,.67f);
    Part elbow=fore[i]=a.child(0,6.1f,0);
    angular(elbow,17,17,2,0,4.9f,0,0,0,.70f,.68f,2.7f,0,0,.59f,.61f,4.3f,0,-.08f,.70f,.47f,4.9f,0,-.14f,.48f,.37f);
    for(int j=0;j<4;j++)elbow.blade(17,-.49f+j*.31f,4.2f,-.14f,-.49f+j*.31f,5.22f-(j%2)*.14f,-.18f,.23f);
    Part leg=legs[i]=root.child(side*1.40f,11,0);
    angular(leg,10,10,3,0,4.6f,0,0,0,1.29f,1.35f,4.6f,0,0,1.00f,1.06f);
    angular(leg,17,17,2.2f,4.6f,6.6f,4.6f,0,0,.92f,.95f,6.6f,0,0,.79f,.82f);
    Part shin=shins[i]=leg.child(0,6.6f,0);
    angular(shin,17,17,2.0f,0,4.5f,0,0,0,.79f,.82f,2.2f,0,0,.69f,.70f,4.5f,0,0,.57f,.60f);
    angular(shin,5,5,2.6f,4.35f,6.4f,4.35f,0,0,.77f,.82f,5.25f,0,-.45f,.98f,1.40f,6.4f,0,-.45f,.98f,1.40f);
   }
   for(int i=0;i<3;i++){
    Part q=orbs[i]=root.child(0,0,0);
    q.oval(26,0,0,0,1.28f,1.34f,1.28f);
    q.loft(26,10,1.02f,0,0,.43f,.43f,1.8f,.10f,0,.24f,.25f,2.4f,.20f,0,.035f,.035f);
    q.oval(27,-.45f,-.58f,-1.02f,.29f,.35f,.12f);
   }
  }
  @Override public void setupAnim(GemGuest e,float limb,float amount,float age,float yaw,float pitch){
   float cast=e.metalGesture(),dialog=e.gesture();
   head.ry=yaw*.01745f;head.rx=pitch*.01745f;head.rz=-.035f+(float)Math.sin(age*.055f)*.025f;
   body.ry=-cast*.13f;
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;float walk=(float)Math.cos(limb*.6662f+i*Math.PI)*amount;
    arms[i].rx=-walk*.62f-(i==1?1.28f*cast+.45f*dialog:.42f*cast);
    arms[i].rz=side*(-.07f-.22f*cast);fore[i].rx=i==1?-.65f*cast-.28f*dialog:-.25f*cast;
    legs[i].rx=walk*.58f;shins[i].rx=Math.max(0,-walk*.48f);
   }
   for(int i=0;i<locks.size();i++){Part q=locks.get(i);q.rx=(float)Math.sin(age*.095f+i*.53f)*.045f+amount*.06f+cast*.06f;q.rz=(float)Math.sin(age*.08f+i*.65f)*.028f;}
   for(int i=0;i<fringe.size();i++){Part q=fringe.get(i);q.rx=-(.025f+.022f*(float)Math.sin(age*.13f+i*.55f));q.rz=(float)Math.sin(age*.095f+i*.50f)*.035f;}
   for(int i=0;i<3;i++){
    Part q=orbs[i];float a=age*.115f+i*2.0944f;
    q.x=(6.5f+cast*2.1f)*(float)Math.cos(a);q.z=(5.5f+cast*2.4f)*(float)Math.sin(a);q.y=4.0f+2.5f*(float)Math.sin(a*1.5f)+cast*-2.5f;q.rx=(float)Math.sin(a)*.19f;q.ry=a;
    if(cast<=0&&i>0)q.y=10000;
   }
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
}''',encoding='utf-8')
# Separate atlas, so Phosphophyllite and other shared guests retain their textures.
im=Image.open(assets/'textures/entity/sculpted_guests.png').convert('RGBA')
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for tile in (5,10,11,13,15,16,17,26,27,28):
 for y in range(128):
  v=(y-3)/121
  for x in range(128):
   u=(x-3)/121;f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   if tile==13:
    t=(u*7+v*.95+.29*math.sin(v*9))%1
    c=mix((79,6,27),(209,26,54),.30+.58*t)
    c=mix(c,(255,108,120),.40*math.exp(-((t-.25)/.11)**2))
    c=mix(c,(255,218,183),.72*math.exp(-((t-.24)/.025)**2)*g(.48,.34,.47,.20))
    c=mix(c,(49,3,20),.43*math.exp(-((t-.93)/.075)**2))
   elif tile in (15,17):
    c=mix((247,232,219),(170,127,132),.17*min(1,f*2)+.045*v)
    c=mix(c,(255,241,228),.25*g(.5,.41,.17,.24))
    if tile==15:
     for side in (-1,1):
      ex=.5+side*.177;dx=side*(u-ex)/.128;ey=.467-.012*dx;dy=(v-ey)/.060
      d=abs(dx)**1.7+abs(dy)**1.65
      c=mix(c,(148,82,89),.13*g(ex,.48,.15,.11))
      if d<1.08:c=(71,29,40)
      if d<.86:c=(248,235,222)
      if d<.83 and abs(dx+.035)<.43:
       c=mix((103,16,39),(219,71,80),(dy+.8)/1.6)
       if abs(dx+.035)<.14:c=(40,22,32)
       if (dx+.19)**2+(dy+.25)**2<.043:c=(255,247,235)
      if abs(dx)<1.04 and abs(v-(ey-.05+.012*dx*dx))<.012:c=(66,26,37)
      if abs(dx)<.98 and abs(v-(.352+.022*dx-.008*dx*dx))<.009:c=(113,30,50)
     c=mix(c,(181,118,121),.24*g(.50,.65,.034,.018))
     if f<.077 and abs(v-(.769+.006*(1-f/.077)))<.007:c=(129,66,76)
   elif tile in (26,27):
    c=mix((41,53,70),(225,241,248),.46+.40*math.sin(u*math.pi*2+v*5)**2)
    c=mix(c,(255,255,255),.92*g(.31,.29,.15,.085))
    c=mix(c,(77,102,124),.60*g(.62,.72,.30,.11))
    if tile==27:c=(242,251,255)
   else:
    base={5:(27,28,35),10:(30,34,43),11:(239,236,227),16:(158,170,177),28:(16,19,27)}[tile]
    c=mix(base,(5,9,18),.22*min(1,f*2)+.13*max(0,-math.sin(u*21+v*2))**5)
    c=mix(c,(106,116,131) if tile in (5,10,28) else (255,250,237),.16*g(.34,.35,.18,.4))
    if tile==10 and abs(f-.40)<.008:c=mix(c,(103,112,126),.36)
   im.putpixel((tile%8*128+x,tile//8*128+y),(*c,255))
im.save(assets/'textures/entity/cinnabar_rework.png')
# Server-driven liquid metal attack with a windup, visible travelling globes and splash damage.
p=java/'GemGuest.java';s=p.read_text(encoding='utf-8')
a='public class GemGuest extends PathfinderMob{';assert a in s
s=s.replace(a,a+''' private int metalPose,metalCooldown=40,metalFlight,metalPool;
    private UUID metalTarget;
    private net.minecraft.world.phys.Vec3 metalFrom,metalTo;
''',1)
a='super.tick();';assert a in s
s=s.replace(a,a+'if(metalPose>0)metalPose--;',1)
a='if(!(level() instanceof ServerLevel l))return;';assert a in s
s=s.replace(a,a+'\n        if(!phos())tickLiquidMetal(l);',1)
a='    @Override public void handleEntityEvent(byte id){';assert a in s
s=s.replace(a,'''    public float metalGesture(){return metalPose<=0?0:Math.min(1f,Math.min((36-metalPose)/7f,metalPose/7f));}
    private static final net.minecraft.core.particles.DustParticleOptions CHROME=new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.73f,.84f,.94f),1.25f);
    private static final net.minecraft.core.particles.DustParticleOptions CHROME_DARK=new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.29f,.38f,.48f),1.0f);
    private void tickLiquidMetal(ServerLevel l){
        if(metalCooldown>0)metalCooldown--;
        if(metalFlight>0&&metalFrom!=null&&metalTo!=null){
            int elapsed=36-metalFlight;float t=Math.max(0,Math.min(1,(elapsed-12)/16f));
            if(elapsed<12){
                for(int j=0;j<3;j++){double a=tickCount*.22+j*Math.PI*2/3;l.sendParticles(CHROME,getX()+Math.cos(a)*.58,getY()+1.25+Math.sin(a)*.20,getZ()+Math.sin(a)*.58,3,.08,.08,.08,0);}
            }else if(elapsed<28){
                var v=metalFrom.lerp(metalTo,t).add(0,Math.sin(t*Math.PI)*.55,0);
                for(int j=-1;j<=1;j++){var q=v.add(j*.18,Math.sin(t*6+j)*.12,j*.12);
                    l.sendParticles(CHROME,q.x,q.y,q.z,9,.13,.13,.13,.025);l.sendParticles(CHROME_DARK,q.x,q.y-.16,q.z,3,.09,.15,.09,.02);}
            }else if(elapsed==28){
                l.playSound(null,net.minecraft.core.BlockPos.containing(metalTo),net.minecraft.sounds.SoundEvents.SLIME_SQUISH,net.minecraft.sounds.SoundSource.NEUTRAL,.9f,.55f);
                l.sendParticles(CHROME,metalTo.x,metalTo.y,metalTo.z,45,.48,.22,.48,.09);
                metalPool=44;
                for(net.minecraft.world.entity.LivingEntity v:l.getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class,new net.minecraft.world.phys.AABB(metalTo,metalTo).inflate(1.65,1.5,1.65),this::metalEnemy)){
                    v.hurt(damageSources().mobAttack(this),12f);
                    v.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN,65,1));
                }
            }
            metalFlight--;
        }
        if(metalPool>0&&metalTo!=null){
            metalPool--;
            var ground=metalTo.add(0,-.65,0);
            for(int j=0;j<8;j++){double a=random.nextDouble()*Math.PI*2,r=random.nextDouble()*1.25;
                l.sendParticles(CHROME_DARK,ground.x+Math.cos(a)*r,ground.y+.05,ground.z+Math.sin(a)*r,1,.04,.035,.04,0);}
            if(metalPool%10==0){
                l.sendParticles(CHROME,ground.x,ground.y+.10,ground.z,12,.55,.07,.55,.01);
                for(net.minecraft.world.entity.LivingEntity v:l.getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class,new net.minecraft.world.phys.AABB(ground,ground).inflate(1.35,1.0,1.35),this::metalEnemy)){
                    v.hurt(damageSources().mobAttack(this),2f);
                    v.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.POISON,45,0));
                }
            }
        }
        if(metalCooldown>0||metalFlight>0||metalPool>0||tickCount%5!=0)return;
        net.minecraft.world.entity.LivingEntity target=getLastHurtByMob();
        if(target==null||!metalEnemy(target)||distanceToSqr(target)>81||!hasLineOfSight(target)){
            target=null;double best=81;
            for(net.minecraft.world.entity.monster.Monster m:l.getEntitiesOfClass(net.minecraft.world.entity.monster.Monster.class,getBoundingBox().inflate(9),v->v.isAlive()&&hasLineOfSight(v))){
                double d=distanceToSqr(m);if(d<best){best=d;target=m;}
            }
        }
        if(target==null)return;
        metalTarget=target.getUUID();metalFrom=position().add(0,1.20,0);metalTo=target.position().add(0,.65,0);
        metalFlight=36;metalCooldown=100;getNavigation().stop();getLookControl().setLookAt(target,35,35);
        l.broadcastEntityEvent(this,(byte)114);
    }
    private boolean metalEnemy(net.minecraft.world.entity.LivingEntity v){
        return v!=this&&v.isAlive()&&!(v instanceof GemGuest)&&(v instanceof net.minecraft.world.entity.monster.Monster||v==getLastHurtByMob());
    }
'''+a,1)
s=s.replace('if(id==113){pose=35;return;}','if(id==114){metalPose=36;return;}if(id==113){pose=35;return;}',1)
# Do not interrupt the attack windup with the ordinary companion-follow routine.
s=s.replace('GemGuest q=companion(l);\n        if(q==null)', 'if(!phos()&&metalFlight>24){getNavigation().stop();return;}\n        GemGuest q=companion(l);\n        if(q==null)',1)
p.write_text(s,encoding='utf-8')
print('Cinnabar: dedicated beveled geometry, tailored outfit, S-shaped fringe and independent animated ruby locks; hovering chrome globes, liquid projectile and corrosive puddle.')
