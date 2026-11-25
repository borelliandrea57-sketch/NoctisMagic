"""Divine arrival cinematics and distinct adult cabaret costumes."""
from pathlib import Path
import sys,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
 p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
(java/'DivineArrival.java').write_text('''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.particles.*;
import net.minecraft.network.chat.Component;
import net.minecraft.ChatFormatting;
import net.minecraft.server.level.*;
import net.minecraft.sounds.*;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class DivineArrival{
 record Arrival(ServerLevel level,Vec3 origin,UUID viewer,boolean exodia,int age){}
 static final List<Arrival> active=new ArrayList<>();
 public static void start(ServerPlayer p,Entity mob,boolean ex){begin(p,mob.position(),ex);}
 public static void begin(ServerPlayer p,Vec3 pos,boolean ex){
  ServerLevel l=p.serverLevel();
  active.add(new Arrival(l,pos,p.getUUID(),ex,0));
  p.displayClientMessage(Component.literal(ex?"LE CINQUE RELIQUIE SONO RIUNITE":"UNA LUCE DISCENDE DAL CIELO").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD),true);
  l.playSound(null,pos.x,pos.y,pos.z,ex?SoundEvents.ENDER_DRAGON_GROWL:SoundEvents.BEACON_ACTIVATE,SoundSource.AMBIENT,1.4f,ex?.70f:1.15f);
 }
 static void ring(ServerLevel l,Vec3 p,double radius,double y,int n,double phase,ParticleOptions particle){
  for(int i=0;i<n;i++){double a=2*Math.PI*i/n+phase;l.sendParticles(particle,p.x+radius*Math.cos(a),p.y+y,p.z+radius*Math.sin(a),1,0,0,0,0);}
 }
 @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){
  if(e.phase!=TickEvent.Phase.END)return;
  for(int i=active.size()-1;i>=0;i--){
   Arrival a=active.get(i);ServerLevel l=a.level();Vec3 p=a.origin();int t=a.age();boolean ex=a.exodia();
   if(t%5==0){
    double r=(ex?6:3)+Math.sin(t*.12)*(ex?1.5:.45);
    ring(l,p,r,.13,40,t*.035,ParticleTypes.TOTEM_OF_UNDYING);
    ring(l,p,r*.65,ex?3.8:1.2,24,-t*.06,ex?ParticleTypes.SOUL_FIRE_FLAME:ParticleTypes.END_ROD);
    for(int j=0;j<5;j++){double angle=j*2*Math.PI/5+t*.06;l.sendParticles(ex?ParticleTypes.REVERSE_PORTAL:ParticleTypes.END_ROD,p.x+Math.cos(angle)*r*.6,p.y+1+t*.10,p.z+Math.sin(angle)*r*.6,3,.05,.12,.05,.025);}
    l.sendParticles(ParticleTypes.END_ROD,p.x,p.y+(ex?6:2),p.z,12,.25,ex?4:3,.25,.035);
   }
   if(t==20||t==55){
    l.sendParticles(ex?ParticleTypes.EXPLOSION:ParticleTypes.FLASH,p.x,p.y+(ex?5:2),p.z,1,0,0,0,0);
    l.playSound(null,p.x,p.y,p.z,ex?SoundEvents.WITHER_SPAWN:SoundEvents.AMETHYST_BLOCK_CHIME,SoundSource.AMBIENT,1,ex?.80f:1.05f);
    if(ex)l.sendParticles(ParticleTypes.LARGE_SMOKE,p.x,p.y+2,p.z,45,3,1,3,.06);
    else ring(l,p,4.5,2.8,48,t*.02,ParticleTypes.END_ROD);
   }
   if(t>=100){
    active.remove(i);
    ServerPlayer viewer=l.getServer().getPlayerList().getPlayer(a.viewer());
    if(ex&&viewer!=null&&viewer.serverLevel()==l)viewer.connection.disconnect(Component.literal("Hai vinto il duello.").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));
   }else active.set(i,new Arrival(l,p,a.viewer(),ex,t+1));
  }
 }
 @SubscribeEvent public static void stop(ServerStoppedEvent e){active.clear();}
}
''',encoding='utf-8')
for n in ('ExodiaRitual.java','ExodiaEgg.java'):
 edit(n,'p.connection.disconnect(Component.literal("Hai vinto il duello.").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));','DivineArrival.start(p,boss,true);')
edit('MiracleEncounter.java','if(!l.noCollision(v)||!l.addFreshEntity(v))continue;','if(!l.noCollision(v)||!l.addFreshEntity(v))continue;\n                DivineArrival.start(p,v,false);')
edit('DivineRexJudgment.java','if(rex.isEmpty())return false;','if(rex.isEmpty())return false;\n  DivineArrival.begin(p,p.position(),false);')
for name,skin,hair,eye,lip,metal,cloth in [
 ('cabaret_noir',(174,115,91),(25,20,33),(186,94,206),(118,23,75),(197,151,221),(48,20,70)),
 ('cabaret_luna',(229,199,180),(217,188,126),(68,149,224),(179,40,83),(229,231,251),(37,74,139))]:
 p=assets/'textures/entity'/f'{name}.png';im=Image.open(p).convert('RGBA');S=im.width//128
 def mix(a,b,t):return tuple(round(x+(y-x)*max(0,min(1,t))) for x,y in zip(a,b))
 for j in range(7*S):
  v=(j+.5)/(7*S)
  for i in range(7*S):
   u=(i+.5)/(7*S);f=abs(u-.5)
   c=mix(skin,(92,47,55),.19*max(0,(f-.20)*4)+.06*v)
   c=mix(c,(255,220,202),.18*math.exp(-((u-.50)/.16)**2-((v-.50)/.32)**2))
   for side in (-1,1):
    ex=.5+side*.21;dx=side*(u-ex)/.18;dy=(v-(.43-.08*dx))/.088;d=abs(dx)**1.6+abs(dy)**1.5
    c=mix(c,lip,.16*math.exp(-((u-ex)/.16)**2-((v-.57)/.10)**2))
    if d<1.22:c=(42,23,39)
    if d<.76:c=(247,233,229)
    if d<.74 and abs(dx+.06)<.42:
     c=mix((48,30,75),eye,(dy+1)/2)
     if abs(dx+.06)<.17:c=(24,18,31)
     if (dx+.2)**2+(dy+.24)**2<.055:c=(255,247,237)
    if abs(dx)<1.14 and abs(v-(.295-.06*dx))<.020:c=hair
    if .75<dx<1.25 and abs(v-(.385-.12*dx))<.025:c=(35,20,32)
   if f<.035 and abs(v-.63)<.022:c=mix(skin,lip,.30)
   smile=.755+.16*(u-.5)-.018*math.cos((u-.5)*10)
   if f<.126 and abs(v-smile)<.033:c=lip
   if f<.08 and abs(v-smile-.018)<.011:c=mix(lip,(245,159,187),.7)
   if name=='cabaret_noir' and .74<u<.78 and .66<v<.70:c=(58,31,39)
   im.putpixel((42*S+i,23*S+j),(*c,255))
 for y in range(112*S,128*S):
  for x in range(32*S):
   u=x/S;v=y/S;c=mix(cloth,metal,.14+.18*math.sin(u*2.3)**2)
   if abs((u+v)%5-2.5)<.32 or abs((u-v)%5-2.5)<.32:c=mix(cloth,metal,.54)
   im.putpixel((x,y),(*c,255))
 im.save(p)
p=java/'CabaretClient.java';s=p.read_text(encoding='utf-8');a='        return LayerDefinition.create(m,128,128);';assert a in s
s=s.replace(a,'''        if(k!=0){
            b.addOrReplaceChild("corsetBodice",CubeListBuilder.create().texOffs(0,112).addBox(-3.65f,0,-2.95f,7.3f,5.1f,5.1f),PartPose.offset(0,.6f,-.22f));
            for(int i=0;i<2;i++){
                int side=i==0?-1:1;
                b.addOrReplaceChild("satinPanel"+i,CubeListBuilder.create().texOffs(0,112).addBox(-1.5f,0,-.45f,3.0f,3.0f,.9f),PartPose.offsetAndRotation(side*1.5f,.8f,-3.10f,0,0,side*.15f));
                sk.addOrReplaceChild("ruffle"+i,CubeListBuilder.create().texOffs(0,112).addBox(-2.05f,0,-2.1f,4.1f,1.25f,4.2f),PartPose.offsetAndRotation(side*2.8f,2.6f,-.65f,0,0,-side*.12f));
                PartDefinition arm=r.getChild("arm"+i);
                arm.addOrReplaceChild("operaGlove",CubeListBuilder.create().texOffs(0,112).addBox(-1.06f,3.9f,-1.06f,2.12f,5.3f,2.12f),PartPose.ZERO);
                h.addOrReplaceChild("layeredLock"+i,CubeListBuilder.create().texOffs(96,112).addBox(-.6f,0,-.65f,1.2f,k==1?6.1f:8.2f,1.3f),PartPose.offsetAndRotation(side*3.6f,-6.4f,1.0f,0,0,side*.14f));
            }
            b.addOrReplaceChild("waistBrooch",CubeListBuilder.create().texOffs(116,112).addBox(-.64f,-.45f,-.35f,1.28f,.9f,.7f),PartPose.offset(0,7.5f,-2.30f));
        }
'''+a,1)
s=s.replace('head.zRot=g*.12f;','head.zRot=g*.12f;if(e.variant()!=0)head.zRot+=(float)Math.sin(age*.045f)*.07f;',1)
p.write_text(s,encoding='utf-8')
print('Five-second divine arrivals, cabaret costume and face refinement.')
