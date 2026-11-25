"""1.6.6: larger Stand users, custom Giorno, ranged Leon and crouching Xenomorph."""
from pathlib import Path
import sys,re,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
def edit(name,a,b):
 p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a[:100]);p.write_text(s.replace(a,b,1),encoding='utf-8')
# Jotaro's broad tailored coat, metal buttons, reinforced cuffs.
n='JotaroSculptedClient.java'
edit(n,'p.scale(1.02f,1.07f,1.02f);','p.scale(1.21f,1.18f,1.18f);')
edit(n,'4.6f,2.45f,2.5f,0,0,4.55f,2.5f','4.95f,2.60f,2.5f,0,0,4.86f,2.62f')
edit(n,'arm[i]=body.child(s*4.55f,.45f,0);','arm[i]=body.child(s*4.90f,.45f,0);')
edit(n,'fore[i].oval(2,0,5.25f','''fore[i].loft(0,28,3.6f,0,0,1.30f,1.30f,4.42f,0,0,1.20f,1.20f);
                fore[i].loft(3,28,4.15f,0,0,1.22f,1.22f,4.35f,0,0,1.20f,1.20f);
                body.blade(3,s*3.9f,5.6f,-1.60f,s*2.3f,6.7f,-1.95f,.23f);
                body.oval(4,s*2.9f,6.4f,-2.02f,.20f,.20f,.12f);
                fore[i].oval(2,0,5.25f''')
# Bucciarati retains the tailored silhouette and distinct white keyhole fabric.
n='BucciaratiSculptedClient.java'
edit(n,'@Override public ResourceLocation getTextureLocation(JojoMob e)','@Override protected void scale(JojoMob e,PoseStack p,float partial){p.scale(1.13f,1.15f,1.12f);}\n  @Override public ResourceLocation getTextureLocation(JojoMob e)')
edit(n,'3.75f,2.13f,2.4f,0,-.12f,3.65f,2.23f','4.05f,2.25f,2.4f,0,-.12f,3.93f,2.32f')
edit(n,'arm[i]=body.child(s*3.86f,.35f,0);','arm[i]=body.child(s*4.12f,.35f,0);')
edit(n,'fore[i].oval(6,0,5.12f','''fore[i].loft(8,24,3.6f,0,0,.97f,.98f,4.2f,0,0,.94f,.95f);
    fore[i].blade(3,s*.65f,1.7f,-.65f,s*.55f,3.5f,-.70f,.18f);
    for(int j=0;j<5;j++)fore[i].oval(4,s*.60f,1.8f+j*.30f,-.73f,.13f,.08f,.09f);
    Part cuff=fore[i].child(s*.57f,3.5f,-.74f);loop(cuff,.18f,.28f,.075f);
    fore[i].oval(6,0,5.12f''')
# Independent sculpted Giorno rather than the original cuboid model.
edit('JojoClient.java','e.registerEntityRenderer(Noctis.GIORNO.get(),c->new Renderer(c,2));','')
(java/'GiornoSculptedClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class GiornoSculptedClient {
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.GIORNO.get(),R::new);}
 static void curl(Part p,float w,float h){
  for(int i=0;i<28;i++)for(int j=0;j<10;j++){
   float a=i*(float)Math.PI/14,A=(i+1)*(float)Math.PI/14,b=j*(float)Math.PI/5,B=(j+1)*(float)Math.PI/5;
   p.faces.add(new Q(v(a,b,w,h,i/28f,j/10f),v(A,b,w,h,(i+1)/28f,j/10f),v(A,B,w,h,(i+1)/28f,(j+1)/10f),v(a,B,w,h,i/28f,(j+1)/10f),3));
  }
 }
 static V v(float a,float b,float w,float h,float u,float t){
  float ca=(float)Math.cos(a),sa=(float)Math.sin(a),cb=(float)Math.cos(b),sb=(float)Math.sin(b);
  return new V((w+.37f*cb)*ca,(h+.37f*cb)*sa,.37f*sb,u,t,ca*cb,sa*cb,sb);
 }
 static V face(V v,boolean f){return new V(v.x(),v.y(),v.z(),f?.5f+v.x()/7.4f:.035f,v.v(),v.nx(),v.ny(),v.nz());}
 static void project(Part p){for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=5)continue;boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;p.faces.set(i,new Q(face(q.a(),f),face(q.b(),f),face(q.c(),f),face(q.d(),f),5));}}
 static class M extends EntityModel<JojoMob>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1,0);
  final Part[] arm=new Part[2],fore=new Part[2],leg=new Part[2],shin=new Part[2],braid=new Part[6];
  M(){
   body.loft(0,40,-1,0,0,1.75f,1.40f,.15f,0,0,4.12f,2.20f,2.6f,0,-.10f,3.96f,2.28f,5.6f,0,0,3.12f,1.85f,8.6f,0,0,2.55f,1.60f,10.8f,0,0,3.0f,1.85f);
   body.loft(1,24,-1.5f,0,0,1.25f,1.19f,.5f,0,0,1.57f,1.42f);
   // Raised golden edging follows the heart-shaped chest opening.
   for(int s:new int[]{-1,1}){
    body.blade(3,s*.12f,1.75f,-2.26f,s*1.45f,.55f,-1.96f,.30f);
    body.blade(3,s*1.45f,.55f,-1.96f,s*2.0f,2.1f,-2.05f,.30f);
    body.blade(3,s*2.0f,2.1f,-2.05f,s*.95f,5.1f,-2.10f,.30f);
    body.blade(3,s*.95f,5.1f,-2.10f,0,6.6f,-1.80f,.30f);
    body.blade(2,s*3.7f,1.2f,-1.35f,s*2.8f,8.1f,-1.45f,.34f);
    body.blade(3,s*2.75f,7.7f,-1.45f,s*1.75f,9.5f,-1.73f,.18f);
    Part badge=body.child(s*2.40f,3.7f,-1.9f);badge.ry=-s*.32f;
    badge.oval(3,0,0,0,.93f,.99f,.32f);badge.oval(4,0,0,-.30f,.75f,.81f,.22f);
    badge.blade(3,0,-.73f,-.52f,0,.72f,-.52f,.13f);
    for(int j=0;j<3;j++)for(int d:new int[]{-1,1})badge.oval(2,d*.32f,-.43f+j*.42f,-.48f,.12f,.15f,.07f);
   }
   body.oval(3,0,7.7f,-1.76f,.84f,.91f,.32f);body.oval(4,0,7.7f,-2.0f,.65f,.71f,.16f);
   head.loft(5,64,-7.8f,0,.1f,1.4f,1.6f,-7.2f,0,.06f,2.6f,2.4f,-5.5f,0,0,3.12f,2.8f,-3.6f,0,-.1f,3.05f,2.66f,-2,0,-.16f,2.65f,2.32f,-.6f,0,-.24f,1.65f,1.5f,0,0,-.24f,.78f,.8f);
   project(head);
   head.loft(6,32,-9.1f,0,.16f,.5f,.6f,-8.75f,0,.18f,2.55f,2.40f,-7.55f,0,.35f,3.48f,3.10f,-6.1f,0,.5f,3.45f,3.0f);
   for(int j=0;j<3;j++){Part q=head.child(-2.15f+j*2.15f,-6.9f,-2.64f);q.rz=(j-1)*.13f;curl(q,.80f,.95f);q.oval(7,0,0,.06f,.42f,.55f,.20f);}
   Part prev=head;
   for(int j=0;j<6;j++){
    Part q=braid[j]=prev.child(0,j==0?-5.9f:1.65f,j==0?2.6f:.25f);
    q.oval(6,-.46f,.65f,0,1.05f,1.21f,.85f);q.oval(3,.46f,1.10f,.12f,1.0f,1.18f,.83f);prev=q;
   }
   prev.loft(2,18,1.4f,0,0,.85f,.73f,1.85f,0,0,.83f,.71f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    head.oval(1,s*3.0f,-3.25f,.13f,.4f,.82f,.54f);
    head.oval(3,s*3.19f,-2.65f,.02f,.19f,.25f,.18f);
    arm[i]=body.child(s*4.15f,.42f,0);
    arm[i].loft(0,28,-.7f,0,0,1.35f,1.4f,.6f,0,0,1.92f,1.78f,2.65f,0,0,1.62f,1.53f,4.75f,0,0,1.09f,1.1f);
    fore[i]=arm[i].child(0,4.6f,0);
    fore[i].loft(0,24,-.2f,0,0,1.14f,1.15f,1.5f,0,0,1.3f,1.27f,3.9f,0,0,.85f,.89f);
    fore[i].loft(3,24,3.65f,0,0,.94f,.97f,4.08f,0,0,.92f,.95f);
    fore[i].oval(1,0,4.95f,-.12f,.89f,1.1f,.72f);
    for(int j=0;j<3;j++)fore[i].oval(3,s*.87f,1.8f+j*.65f,-.50f,.18f,.18f,.13f);
    leg[i]=root.child(s*1.7f,11.15f,0);
    leg[i].loft(0,26,-.3f,0,0,1.62f,1.6f,2.8f,0,0,1.46f,1.40f,5.6f,0,0,1.04f,1.07f);
    shin[i]=leg[i].child(0,5.4f,0);
    shin[i].loft(0,24,-.25f,0,0,1.1f,1.13f,1.6f,0,0,1.25f,1.22f,4.3f,0,0,.92f,.95f,5.7f,0,0,1.06f,1.08f);
    shin[i].loft(2,24,5.4f,0,0,1.03f,1.08f,6.5f,0,-.58f,1.15f,1.66f,7.4f,0,-.64f,1.16f,1.70f);
    shin[i].blade(3,0,5.6f,-.95f,0,6.9f,-1.65f,.23f);
   }
  }
  @Override public void setupAnim(JojoMob e,float limb,float amount,float age,float yaw,float pitch){
   head.ry=yaw*.01745f;head.rx=pitch*.014f;body.ry=(float)Math.sin(limb*.33f)*amount*.06f;
   float pose=amount<.08f?(float)Math.pow(Math.max(0,Math.sin(age*.028)),8):0;
   for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666f+i*Math.PI)*amount;arm[i].rx=-w*.6f-(i==0?pose*.25f:0);arm[i].rz=-s*.12f+(i==0?pose*.8f:0);fore[i].rx=i==0?-pose*.55f:0;leg[i].rx=w*.65f;shin[i].rx=Math.max(0,-w)*.27f;}
   for(int i=0;i<braid.length;i++){braid[i].rx=(float)Math.sin(age*.12f-i*.5f)*(.06f+amount*.1f);braid[i].rz=(float)Math.sin(age*.1f-i*.5f)*.05f;}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<JojoMob,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.42f);}
  @Override protected void scale(JojoMob e,PoseStack p,float partial){p.scale(1.12f,1.15f,1.10f);}
  @Override public ResourceLocation getTextureLocation(JojoMob e){return new ResourceLocation(Noctis.ID,"textures/entity/giorno_sculpted.png");}
 }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
def clamp(x):return max(0,min(1,x))
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
for m,base in enumerate([(173,38,113),(234,185,145),(89,27,77),(225,183,67),(42,105,158),(234,185,145),(232,188,63),(131,89,36)]):
 for y in range(128):
  v=clamp((y-3)/121)
  for x in range(128):
   u=clamp((x-3)/121);f=abs(u-.5)
   c=mix(base,(52,22,43),.12*v+.13*(1-math.sin(u*math.pi)))
   if m==0:
    c=mix(c,(237,83,151),.24*math.exp(-((u-.36)/.16)**2))
    lim=.19*max(0,1-(v-.29)/.36)
    if .16<v<.65 and f<lim:c=mix((234,185,145),(166,102,87),.12*v)
   if m in (3,6):c=mix(base,(255,233,143),.35*math.sin(u*math.pi)**2)
   if m==5:
    c=mix(base,(170,106,88),.11*clamp((f-.2)*4))
    for side in (-1,1):
     dx=(u-(.5+side*.16))/.10;dy=(v-.49-side*dx*.012)/.065
     d=abs(dx)**1.8+abs(dy)**1.6
     if d<1:c=(48,33,39)
     if d<.75:c=(247,239,220)
     if abs(dx)<.43 and d<.74:c=(63,139,128)
     if abs(dx)<.19 and abs(dy)<.67 and d<.74:c=(24,32,35)
     if ((dx+.13)/.10)**2+((dy+.20)/.15)**2<1:c=(255,253,244)
     if abs(dx)<.92 and abs(v-(.372-.009*(1-dx*dx)))<.012:c=(148,98,42)
    if f<.048 and abs(v-(.79-.007*(f/.048)**2))<.009:c=(137,68,70)
   off=(y*W+m*128+x)*4;pix[off:off+4]=bytes((*c,255))
(assets/'giorno_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
# Leon: enlarged shoulders and biceps, more robust body, retain detailed RE4 coat.
n='LeonSculptedClient.java'
edit(n,'4.0f,2.2f,2.6f,0,0,3.8f,2.15f','4.55f,2.52f,2.6f,0,0,4.25f,2.43f')
edit(n,'arms[i]=body.child(s*4.15f,.45f,0);','arms[i]=body.child(s*4.62f,.45f,0);')
edit(n,'1.78f,1.7f,3.1f,0,0,1.52f,1.49f','2.02f,1.95f,3.1f,0,0,1.76f,1.69f')
edit(n,'1.28f,1.27f,3.8f,0,0,1.02f,1.05f','1.51f,1.45f,3.8f,0,0,1.12f,1.14f')
edit(n,'boolean aiming=e.getTarget()!=null&&!e.level().isDay();','boolean aiming=e.aiming();')
edit(n,'@Override public ResourceLocation getTextureLocation(CrossoverGuest e)','@Override protected void scale(CrossoverGuest e,PoseStack p,float partial){p.scale(1.18f,1.15f,1.15f);}\n        @Override public ResourceLocation getTextureLocation(CrossoverGuest e)')
# Ranged-only hunting. Server refreshes aim pose on clients; no melee navigation overriding the shot.
n='CrossoverGuest.java'
edit(n,'int cooldown=40,speech=0,pose=0,animation=0;','int cooldown=40,speech=0,pose=0,animation=0,aimTicks=0;')
edit(n,'goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.2,true){@Override public boolean canUse(){return kind()==0&&!level().isDay()&&super.canUse();}@Override public boolean canContinueToUse(){return kind()==0&&!level().isDay()&&super.canContinueToUse();}});','goalSelector.addGoal(0,new FloatGoal(this));')
edit(n,'return kind()==0&&super.canUse();','return kind()==0&&getTarget()==null&&super.canUse();')
edit(n,'return kind()==0&&super.canContinueToUse();','return kind()==0&&getTarget()==null&&super.canContinueToUse();')
edit(n,'super.tick();if(pose>0)pose--;','super.tick();if(aimTicks>0)aimTicks--;if(pose>0)pose--;')
edit(n,'if(t instanceof Zombie&&t.isAlive()&&cooldown==0&&distanceTo(t)<18&&hasLineOfSight(t)){','''if(t instanceof Zombie&&t.isAlive()){
                double range=distanceTo(t);boolean sight=hasLineOfSight(t);
                getLookControl().setLookAt(t,45,45);
                if(sight&&range<18){
                    getNavigation().stop();
                    if(tickCount%5==0)l.broadcastEntityEvent(this,(byte)105);
                }else if(tickCount%5==0)getNavigation().moveTo(t,1.20);
            }
            if(t instanceof Zombie&&t.isAlive()&&cooldown==0&&distanceTo(t)<18&&hasLineOfSight(t)){''')
edit(n,'cooldown=30;l.broadcastEntityEvent(this,(byte)104);','cooldown=20;l.broadcastEntityEvent(this,(byte)104);')
edit(n,'Vec3 a=getEyePosition(),b=t.getEyePosition();','''Vec3 b=t.getEyePosition(),dir=b.subtract(getEyePosition()).normalize();
                Vec3 a=getEyePosition().add(dir.scale(.75)).add(0,-.30,0);
                l.sendParticles(ParticleTypes.FLAME,a.x,a.y,a.z,6,.10,.10,.10,.025);
                l.sendParticles(ParticleTypes.SMOKE,a.x,a.y,a.z,4,.07,.07,.07,.012);''')
edit(n,'return kind()==0&&!level().isDay()&&e instanceof Zombie&&super.doHurtTarget(e);','return false;')
edit(n,'if(id>=102&&id<=104){','if(id==105){aimTicks=9;return;}if(id>=102&&id<=104){')
edit(n,'public int animation(){return animation;}','public int animation(){return animation;}\n    public boolean aiming(){return aimTicks>0;}')
# Xenomorph crouches on all fours, hips low, head forward, alternating diagonal gait.
p=java/'XenoClient.java';s=p.read_text(encoding='utf-8')
a=s.index('            float hit=e.attackPose();');b=s.index('\n        }',a)
s=s[:a]+'''            float hit=e.attackPose();boolean sit=e.isInSittingPose();
            float step=limb*1.02f,move=Math.min(1,amount*1.5f);
            float tilt=sit?.38f:1.02f-hit*.24f;
            float hip=sit?17:16.5f+(float)Math.sin(step*2)*move*.28f;
            body.xRot=tilt;body.y=hip-12*(float)Math.cos(tilt);body.z=-12*(float)Math.sin(tilt);
            head.yRot=yaw*.012f;head.xRot=-tilt+pitch*.010f+.10f;
            jaw.xRot=.12f+hit*.65f;inner.z=-2-hit*2.8f;
            for(int i=0;i<2;i++){
                float w=(float)Math.cos(step+i*Math.PI)*move;
                arms[i].xRot=-tilt+.12f-w*.57f-hit*.65f;
                arms[i].zRot=i==0?.23f:-.23f;
                arms[i].getChild("fore"+i).xRot=-.25f-Math.max(0,w)*.53f;
                legs[i].y=hip;legs[i].z=0;
                legs[i].xRot=sit?-1.1f:-.88f+w*.38f;
                legs[i].getChild("shin"+i).xRot=sit?1.50f:1.76f-Math.max(0,w)*.35f;
            }
            for(int i=0;i<9;i++){
                tail[i].yRot=(float)Math.sin(age*.22-i*.52)*(.13f+move*.19f);
                tail[i].xRot=(i==0?-tilt-.08f:i<4?-.10f:.13f)+(float)Math.cos(age*.14-i*.4f)*.08f-hit*.11f;
            }'''+s[b:]
p.write_text(s,encoding='utf-8')
edit('Xenomorph.java','new WaterAvoidingRandomStrollGoal(this,.75)','new WaterAvoidingRandomStrollGoal(this,.95)')
# Align collision sizes with the revised visual proportions.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
for id,w,h in [('jotaro',.88,2.42),('bucciarati',.78,2.28),('giorno',.78,2.28),('leon_kennedy',.80,2.25),('xenomorph',.95,1.45)]:
 pattern=r'(ENTITIES.register\("'+id+r'",[^\n]*?\.sized\()[^)]*(\))'
 s,n=re.subn(pattern,lambda m:m.group(1)+str(w)+'f,'+str(h)+'f'+m.group(2),s,count=1)
 assert n==1,id
p.write_text(s,encoding='utf-8')
print('Stand users enlarged and detailed, custom Giorno, ranged-only Leon, Xenomorph crouched skitter.')


# GitHub Actions: public dependencies should come directly from Maven Central
# rather than the Forge Maven proxy, which has repeatedly returned partial files.
import os
from pathlib import Path
if os.environ.get('GITHUB_ACTIONS')=='true':
    initdir=Path(os.environ.get('GRADLE_USER_HOME',str(Path.home()/'.gradle')))/'init.d'
    initdir.mkdir(parents=True,exist_ok=True)
    (initdir/'noctis-public-repositories.gradle').write_text('''
def configureNoctisRepositories = { repos ->
    repos.mavenCentral()
    repos.configureEach { repo ->
        if (repo instanceof org.gradle.api.artifacts.repositories.MavenArtifactRepository &&
            repo.url?.host == 'maven.minecraftforge.net') {
            repo.content {
                excludeGroup('org.lwjgl')
                excludeGroup('com.google.errorprone')
            }
        }
    }
}
gradle.beforeSettings { settings ->
    configureNoctisRepositories(settings.pluginManagement.repositories)
}
gradle.beforeProject { project ->
    configureNoctisRepositories(project.buildscript.repositories)
    configureNoctisRepositories(project.repositories)
}
''',encoding='utf-8')
    print('CI: Maven Central for LWJGL and Error Prone annotations.')
