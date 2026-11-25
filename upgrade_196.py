"""Sticky Fingers: custom armor and spatial zipper ambush."""
from pathlib import Path
import sys,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'JojoClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.STICKY_FINGERS.get(),c->new Renderer(c,4));';assert a in s
s=s.replace(a,'e.registerEntityRenderer(Noctis.STICKY_FINGERS.get(),StickyFingersClient.Renderer::new);',1);p.write_text(s,encoding='utf-8')
(java/'StickyFingersClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import it.noctis.magic.SculptedGuestsClient.Part;
public final class StickyFingersClient{
 static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/sticky_fingers_spirit.png");
 static final class Renderer extends MobRenderer<JojoMob,Model>{
  Renderer(EntityRendererProvider.Context c){super(c,new Model(),0);}
  @Override public ResourceLocation getTextureLocation(JojoMob e){return TEX;}
  @Override protected void scale(JojoMob e,PoseStack p,float partial){p.scale(1.13f,1.13f,1.13f);}
 }
 static final class Model extends EntityModel<JojoMob>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-.4f,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shins=new Part[2],energy=new Part[6];
  final Part aura=new Part(0,0,0);
  float glow,opacity=1;
  void shell(Part p,int m,float... r){CinnabarClient.Model.angular(p,m,m,8,r[0],r[r.length-5],r);}
  void blade(Part p,int m,float x,float y,float z,float X,float Y,float Z,float w){p.blade(m,x,y,z,X,Y,Z,w);}
  void tooth(Part p,int m,float x,float y,float z,float w,float h){
   shell(p,m,y-h/2,x,z,w/2,.13f,y+h/2,x,z,w/2,.13f);
  }
  void pull(Part p,float x,float y,float z,float size){
   Part q=p.child(x,y,z);
   for(int j=0;j<8;j++){
    double a=j*Math.PI/4,b=(j+1)*Math.PI/4;
    blade(q,4,(float)Math.cos(a)*size*.48f,(float)Math.sin(a)*size*.66f,0,(float)Math.cos(b)*size*.48f,(float)Math.sin(b)*size*.66f,0,size*.23f);
   }
   blade(q,4,0,-size*.95f,0,0,-size*.59f,0,size*.46f);
  }
  void zip(Part p,float x,float y,float z,float len,float scale){
   blade(p,3,x,y,z,x,y+len,z,.48f*scale);
   blade(p,4,x,y,z-.18f,x,y+len,z-.18f,.11f*scale);
   for(int j=0;j<(int)(len/(.42f*scale));j++){
    float yy=y+.16f+j*.42f*scale;
    tooth(p,2,x+(j%2==0?-.14f:.14f)*scale,yy,z-.23f,.42f*scale,.19f*scale);
   }
   pull(p,x,y+len*.21f,z-.48f,.72f*scale);
  }
  Model(){super(RenderType::entityTranslucent);
   shell(body,0,-.4f,0,0,2.65f,1.65f,.7f,0,0,3.65f,2.05f,3.0f,0,0,3.35f,1.96f,5.3f,0,0,2.62f,1.64f,8.0f,0,0,1.98f,1.36f,10.1f,0,0,2.39f,1.55f,11.2f,0,0,2.73f,1.64f);
   for(int s:new int[]{-1,1}){
    blade(body,1,s*.43f,.65f,-1.91f,s*2.74f,2.73f,-1.85f,2.6f);
    blade(body,2,s*2.75f,.65f,-1.5f,s*2.60f,4.0f,-1.63f,.50f);
    blade(body,1,s*.75f,3.70f,-1.88f,s*1.06f,5.7f,-1.65f,1.45f);
    blade(body,1,s*.77f,5.78f,-1.71f,s*.80f,7.65f,-1.43f,1.15f);
    blade(body,3,s*2.6f,3.24f,-1.62f,s*1.78f,8.65f,-1.21f,.52f);
    blade(body,1,s*1.8f,9.2f,-1.53f,s*2.44f,10.9f,-1.50f,1.42f);
   }
   zip(body,0,.7f,-2.26f,8.7f,1);
   // Ring collar with separated silver plates, not a flat hat or human head.
   shell(body,3,-1.4f,0,0,.82f,.80f,0,0,0,1.08f,1.03f);
   for(int i=0;i<12;i++){
    double a=i*Math.PI/6;Part q=body.child((float)Math.cos(a)*1.45f,-.2f,(float)Math.sin(a)*1.16f);q.ry=-(float)a;
    shell(q,1,-.5f,0,0,.46f,.40f,.35f,0,0,.50f,.43f);
   }
   // Tapered jaw and lower white mask; the blue helmet covers the eyes completely.
   shell(head,1,-5.55f,0,0,1.30f,1.30f,-4.8f,0,-.05f,2.04f,1.85f,-3.3f,0,-.11f,2.03f,1.77f,-1.6f,0,-.28f,1.38f,1.35f,-.45f,0,-.36f,.69f,.80f);
   shell(head,0,-8.2f,0,.20f,.55f,.64f,-7.8f,0,.15f,1.42f,1.35f,-6.9f,0,.08f,2.35f,2.0f,-5.2f,0,.03f,2.62f,2.30f,-3.95f,0,.16f,2.45f,2.12f);
   for(int s:new int[]{-1,1}){
    blade(head,2,s*.60f,-7.35f,-1.38f,s*1.95f,-4.22f,-1.80f,1.1f);
    blade(head,0,s*2.13f,-6.15f,-.64f,s*2.05f,-3.22f,-.68f,1.18f);
    blade(head,3,s*1.82f,-3.65f,-1.54f,s*.42f,-3.14f,-1.91f,.46f);
    blade(head,2,s*.64f,-2.88f,-1.77f,s*1.04f,-1.93f,-1.42f,.40f);
   }
   zip(head,0,-7.95f,-2.30f,4.05f,.82f);
   blade(head,3,-.43f,-1.55f,-1.64f,.43f,-1.55f,-1.64f,.14f);
   blade(head,4,-.30f,-1.35f,-1.57f,.30f,-1.35f,-1.57f,.18f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;Part a=arms[i]=body.child(s*3.45f,.6f,0);
    shell(a,0,-.85f,0,0,1.22f,1.25f,.05f,s*.14f,0,1.65f,1.54f,1.7f,s*.09f,0,1.46f,1.40f,3.5f,0,0,1.03f,1.06f,5.9f,0,0,.79f,.81f);
    for(int j=0;j<4;j++){
     float y=-.45f+j*.83f;
     blade(a,1,s*.95f,y,-.9f,s*1.1f,y+.65f,1.02f,.80f);
     blade(a,2,s*.35f,y+.15f,-1.50f,s*1.35f,y+.48f,-1.19f,.74f);
    }
    blade(a,2,0,2.6f,-1.20f,0,5.65f,-.81f,1.24f);
    Part f=fore[i]=a.child(0,5.75f,0);
    shell(f,0,-.3f,0,0,.81f,.87f,.70f,0,0,1.20f,1.13f,2.4f,0,0,1.04f,1.06f,3.75f,0,0,.65f,.74f,4.2f,0,0,.68f,.71f);
    for(int j=0;j<4;j++){
     float y=.35f+j*.79f;blade(f,1,-.86f,y,-1.01f,.86f,y+.16f,-1.01f,.73f);
    }
    zip(f,s*.62f,.20f,-1.02f,3.9f,.72f);
    shell(f,1,4.02f,0,0,.64f,.70f,4.62f,0,-.1f,.84f,.67f,5.36f,0,-.22f,.78f,.56f,5.62f,0,-.23f,.47f,.41f);
    for(int j=0;j<3;j++)blade(f,3,-.38f+j*.38f,4.85f,-.82f,-.38f+j*.38f,5.4f,-.76f,.09f);
    Part l=legs[i]=root.child(s*1.43f,11,0);
    shell(l,0,-.45f,0,0,1.4f,1.54f,1.12f,s*.11f,0,1.49f,1.51f,3.25f,0,0,1.18f,1.27f,5.65f,0,0,.87f,.91f,6.10f,0,0,.86f,.89f);
    blade(l,1,0,.35f,-1.53f,0,5.61f,-.97f,1.70f);
    blade(l,2,s*1.13f,.55f,-.95f,s*.72f,5.52f,-.61f,.73f);
    zip(l,s*1.16f,.10f,-1.12f,4.6f,.73f);
    Part sh=shins[i]=l.child(0,6.05f,0);
    shell(sh,0,-.30f,0,0,.89f,.94f,.65f,0,0,1.09f,1.13f,2.4f,0,0,.98f,1.08f,4.9f,0,0,.67f,.76f,6.0f,0,0,.61f,.67f);
    blade(sh,1,0,-.12f,-1.09f,0,1.62f,-1.18f,1.72f);
    blade(sh,2,0,1.44f,-1.12f,0,5.75f,-.76f,1.27f);
    zip(sh,s*.47f,1.56f,-1.04f,4.1f,.65f);
    shell(sh,1,5.83f,0,-.12f,.65f,.75f,6.43f,0,-.48f,.87f,1.37f,7.22f,0,-.60f,.83f,1.51f,7.46f,0,-.55f,.59f,1.29f);
   }
   for(int i=0;i<6;i++){
    double a=i*Math.PI/3;Part q=energy[i]=aura.child((float)Math.cos(a)*5.1f,0,(float)Math.sin(a)*5.1f);q.ry=(float)a;
    for(int j=0;j<5;j++){
     float y=22-j*6.3f;
     blade(q,7,(float)Math.sin(j*.9+i)*.75f,y,0,(float)Math.sin((j+1)*.9+i)*.75f,y-6.3f,0,.68f);
    }
   }
  }
  @Override public void setupAnim(JojoMob e,float limb,float amount,float age,float yaw,float pitch){
   float h=e.punchPose(),z=e.zipperPose();
   opacity=1-.70f*z;glow=.55f+.23f*(float)Math.sin(age*.17f);
   root.y=-1.15f+(float)Math.sin(age*.14f)*.52f;
   body.ry=-.10f+h*.27f*(float)Math.sin(age*1.8f);
   head.ry=yaw*.01745f;head.rx=pitch*.01745f;head.rz=-.07f;
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;float hit=h*(.5f+.5f*(float)Math.sin(age*2+i*Math.PI));
    arms[i].rx=-.48f-hit*1.75f-z*.8f;arms[i].rz=-s*(.25f+.30f*z);
    fore[i].rx=-1.32f*(1-hit)*(1-z*.8f);fore[i].rz=-s*.22f*(1-hit);
    legs[i].rx=s*.16f;legs[i].rz=-s*.08f;shins[i].rx=i==0?.21f:.38f;
   }
   aura.y=root.y;aura.ry=age*.021f;
   for(int i=0;i<6;i++)energy[i].y=(float)Math.sin(age*.12+i)*1.3f;
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){
   root.draw(p,v,LightTexture.pack(Math.max(10,LightTexture.block(light)),Math.max(10,LightTexture.sky(light))),overlay,r,g,b,a*.88f*opacity);
   aura.draw(p,v,LightTexture.FULL_BRIGHT,overlay,.67f,.86f,1,a*glow);
  }
 }
}''',encoding='utf-8')
im=Image.new('RGBA',(1024,512))
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for m in (0,1,2,3,4,7):
 for y in range(128):
  v=max(0,min(1,(y-3)/121))
  for x in range(128):
   u=max(0,min(1,(x-3)/121));f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   alpha=255
   if m in (0,2):
    c=mix((17,48,103) if m==0 else (38,107,185),(4,14,42),.48*f+.20*v)
    c=mix(c,(109,196,254),.62*g(.30,.35,.17,.52))
    c=mix(c,(195,231,255),.45*g(.23,.29,.035,.35))
   elif m==1:
    c=mix((222,230,231),(95,110,128),.45*f+.24*v)
    c=mix(c,(255,255,248),.45*g(.34,.3,.22,.47))
   elif m==3:c=mix((12,19,32),(63,76,98),.25*math.sin(u*math.pi)**2)
   elif m==4:
    c=mix((150,96,27),(252,213,108),.28+.55*math.sin(u*math.pi)**2)
    c=mix(c,(255,247,183),.5*g(.26,.27,.12,.33))
   else:
    c=mix((53,127,242),(216,251,255),max(0,1-f*2))
    alpha=round(140*max(0,1-f*2)**2*max(0,math.sin(v*math.pi)))
   im.putpixel((m%8*128+x,m//8*128+y),(*c,alpha))
im.save(assets/'textures/entity/sticky_fingers_spirit.png')
p=java/'JojoMob.java';s=p.read_text(encoding='utf-8')
a='private int punch,ability,dialogue;';assert a in s
s=s.replace(a,a+''' private int zipperCooldown=24,zipperTicks,zipperVisual;
    private Vec3 zipperExit;
''',1)
a='super.tick();if(punch>0)punch--;';assert a in s
s=s.replace(a,'super.tick();if(zipperVisual>0)zipperVisual--;if(punch>0)punch--;',1)
a='        if(victim instanceof Player creative&&creative.isCreative()){';assert a in s
s=s.replace(a,'        if(variant()==4&&zipperAmbush(l,victim))return;\\n'+a,1).replace('return;\\n        if(victim instanceof Player','return;\\n        if(victim instanceof Player') if False else s.replace(a,'        if(variant()==4&&zipperAmbush(l,victim))return;\n'+a,1)
a='    @Override public void handleEntityEvent(byte id){';assert a in s
s=s.replace(a,'''    public float zipperPose(){return zipperVisual<=0?0:Math.min(1f,zipperVisual/5f);}
    private static final net.minecraft.core.particles.DustParticleOptions ZIP_GOLD=new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(1f,.73f,.23f),1.1f);
    private static final net.minecraft.core.particles.DustParticleOptions ZIP_DARK=new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.045f,.075f,.15f),1.35f);
    private static final net.minecraft.core.particles.DustParticleOptions ZIP_BLUE=new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.25f,.64f,1f),.75f);
    private void zipperFrame(ServerLevel l,Vec3 at,LivingEntity target,float open){
        Vec3 side=new Vec3(target.getZ()-at.z,0,at.x-target.getX()).normalize();
        if(side.lengthSqr()<.01)side=new Vec3(1,0,0);
        for(int i=0;i<=22;i++){
            double y=.12+i*.13,spread=.09+.65*Math.sin(Math.PI*i/22)*open;
            for(int sign:new int[]{-1,1}){
                Vec3 t=at.add(side.scale(sign*spread)).add(0,y,0);
                l.sendParticles(ZIP_GOLD,t.x,t.y,t.z,1,0,0,0,0);
                Vec3 tooth=t.add(side.scale(-sign*.10));
                l.sendParticles(ZIP_GOLD,tooth.x,tooth.y,tooth.z,1,0,0,0,0);
            }
            if(open>.15f){
                Vec3 v=at.add(0,y,0);l.sendParticles(ZIP_DARK,v.x,v.y,v.z,2,Math.abs(side.x)*spread*.28,.02,Math.abs(side.z)*spread*.28,0);
            }
        }
        Vec3 v=at.add(0,2.65-open*1.95,0);
        for(int j=0;j<8;j++){
            double a=j*Math.PI/4;Vec3 q=v.add(side.scale(.23*Math.cos(a))).add(0,.30*Math.sin(a),0);
            l.sendParticles(ZIP_GOLD,q.x,q.y,q.z,1,0,0,0,0);
        }
        l.sendParticles(ZIP_BLUE,at.x,at.y+1.3,at.z,7,.44,.70,.44,.01);
    }
    private boolean zipSafe(ServerLevel l,Vec3 p){
        var b=net.minecraft.core.BlockPos.containing(p);
        return l.hasChunkAt(b)&&!l.isOutsideBuildHeight(b)&&l.getWorldBorder().isWithinBounds(b)
          &&l.getBlockState(b.below()).isFaceSturdy(l,b.below(),net.minecraft.core.Direction.UP)
          &&l.getFluidState(b).isEmpty()&&l.noCollision(this,getBoundingBox().move(p.subtract(position())));
    }
    private boolean zipperAmbush(ServerLevel l,LivingEntity victim){
        if(zipperCooldown>0)zipperCooldown--;
        if(zipperTicks>0){
            getNavigation().stop();setDeltaMovement(0,getDeltaMovement().y,0);
            getLookControl().setLookAt(victim,35,35);
            int step=--zipperTicks;
            if(step>=7&&step%2==0)zipperFrame(l,position(),victim,(14-step)/7f);
            if(step==6){
                if(zipperExit!=null&&zipSafe(l,zipperExit)){
                    teleportTo(zipperExit.x,zipperExit.y,zipperExit.z);
                    l.broadcastEntityEvent(this,(byte)115);
                    zipperFrame(l,position(),victim,1);
                    l.playSound(null,blockPosition(),SoundEvents.ENDERMAN_TELEPORT,net.minecraft.sounds.SoundSource.HOSTILE,.75f,1.65f);
                }else{zipperTicks=0;zipperExit=null;return false;}
            }
            if(step<6&&step%2==0)zipperFrame(l,position(),victim,step/6f);
            if(step==0&&distanceToSqr(victim)<12){
                swing(net.minecraft.world.InteractionHand.MAIN_HAND);l.broadcastEntityEvent(this,(byte)82);
                if(!(victim instanceof Player p&&p.isCreative())){
                    victim.hurt(damageSources().mobAttack(this),20f);
                    victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,1));
                }
                l.sendParticles(ParticleTypes.CRIT,victim.getX(),victim.getY()+1,victim.getZ(),18,.35,.55,.35,.12);
                playSound(SoundEvents.PLAYER_ATTACK_STRONG,1,1.2f);
            }
            return true;
        }
        if(zipperCooldown>0||distanceToSqr(victim)>400)return false;
        Vec3 look=victim.getLookAngle().multiply(1,0,1).normalize();
        if(look.lengthSqr()<.01)look=new Vec3(0,0,1);
        Vec3 side=new Vec3(-look.z,0,look.x);
        Vec3[] spots={victim.position().subtract(look.scale(2.1)),victim.position().add(side.scale(2.3)),victim.position().subtract(side.scale(2.3))};
        for(Vec3 base:spots)for(int dy:new int[]{0,1,-1,2,-2}){
            Vec3 dest=base.add(0,dy,0);
            if(!zipSafe(l,dest)||dest.distanceToSqr(position())<2.25)continue;
            zipperExit=dest;zipperTicks=14;zipperCooldown=85+random.nextInt(40);
            l.broadcastEntityEvent(this,(byte)115);zipperFrame(l,position(),victim,.18f);
            l.playSound(null,blockPosition(),SoundEvents.CHAIN_PLACE,net.minecraft.sounds.SoundSource.HOSTILE,1,.85f);
            return true;
        }
        zipperCooldown=20;return false;
    }
'''+a,1)
s=s.replace(a,a+'if(id==115){zipperVisual=12;return;}',1)
p.write_text(s,encoding='utf-8')
print('Sticky Fingers: armored spectral model and safe zipper teleport ambush, including creative mode.')
