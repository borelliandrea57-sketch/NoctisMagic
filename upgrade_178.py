"""1.7.8: Fallomorph, a grotesque comic hopping hostile creature."""
from pathlib import Path
import sys,json,math,random
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
 p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Fallomorph>> FALLOMORPH=ENTITIES.register("fallomorph",()->EntityType.Builder.<Fallomorph>of(Fallomorph::new,MobCategory.MONSTER).sized(1.05f,1.65f).clientTrackingRange(8).build(ID+":fallomorph"));
    public static final RegistryObject<Item> FALLOMORPH_EGG=ITEMS.register("fallomorph_spawn_egg",()->new ForgeSpawnEggItem(FALLOMORPH,0x7c364e,0xd5a26f,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(FALLOMORPH.get(),Fallomorph.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'e.accept(FALLOMORPH_EGG.get());')
(java/'Fallomorph.java').write_text('''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraft.util.Mth;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid=Noctis.ID,bus=Mod.EventBusSubscriber.Bus.MOD)
public class Fallomorph extends Monster{
 private int delay=14,attackWindow=0,pose=0,windup=0;
 private boolean airborne=false;
 public Fallomorph(EntityType<? extends Monster> type,Level level){super(type,level);xpReward=7;}
 public static AttributeSupplier.Builder attributes(){
  return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,38).add(Attributes.ATTACK_DAMAGE,7).add(Attributes.MOVEMENT_SPEED,.24).add(Attributes.FOLLOW_RANGE,24).add(Attributes.KNOCKBACK_RESISTANCE,.2);
 }
 @SubscribeEvent public static void placements(SpawnPlacementRegisterEvent e){
  e.register(Noctis.FALLOMORPH.get(),SpawnPlacements.Type.ON_GROUND,Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,Monster::checkMonsterSpawnRules,SpawnPlacementRegisterEvent.Operation.REPLACE);
 }
 @Override protected void registerGoals(){
  goalSelector.addGoal(0,new FloatGoal(this));
  targetSelector.addGoal(1,new HurtByTargetGoal(this));
  targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));
 }
 @Override public void tick(){
  super.tick();
  if(pose>0)pose--;if(windup>0)windup--;
  if(!(level() instanceof ServerLevel l)||!isAlive())return;
  LivingEntity t=getTarget();
  boolean chase=t!=null&&t.isAlive()&&distanceToSqr(t)<576;
  if(attackWindow>0){
   attackWindow--;
   if(chase&&getBoundingBox().inflate(.42,.16,.42).intersects(t.getBoundingBox())&&hasLineOfSight(t)){
    if(doHurtTarget(t)){playSound(SoundEvents.SLIME_ATTACK,.9f,.65f);l.sendParticles(ParticleTypes.CRIT,t.getX(),t.getY()+.8,t.getZ(),8,.25,.3,.25,.12);}
    attackWindow=0;
   }
  }
  if(!onGround()){airborne=true;return;}
  if(airborne){
   airborne=false;
   l.broadcastEntityEvent(this,(byte)91);
   l.sendParticles(ParticleTypes.POOF,getX(),getY()+.08,getZ(),6,.32,.06,.32,.025);
   playSound(SoundEvents.SLIME_SQUISH,.8f,.70f);
  }
  if(isInWater()||isInLava())return;
  if(chase){
   float angle=(float)(Math.atan2(t.getZ()-getZ(),t.getX()-getX())*180/Math.PI)-90f;
   setYRot(angle);yBodyRot=angle;yHeadRot=angle;
  }
  if(--delay==5)l.broadcastEntityEvent(this,(byte)92);
  if(delay>0)return;
  delay=chase?12+random.nextInt(7):30+random.nextInt(25);
  double vx,vz;
  if(chase){
   Vec3 d=t.position().subtract(position());double len=Math.sqrt(d.x*d.x+d.z*d.z);
   double speed=Mth.clamp(len*.13,.19,.59);
   vx=len>.02?d.x/len*speed:0;vz=len>.02?d.z/len*speed:0;
   attackWindow=22;
  }else{
   float a=random.nextFloat()*360;setYRot(a);yBodyRot=a;yHeadRot=a;
   vx=-Math.sin(Math.toRadians(a))*.19;vz=Math.cos(Math.toRadians(a))*.19;
  }
  setDeltaMovement(vx,chase?.53:.38,vz);
  hasImpulse=true;l.broadcastEntityEvent(this,(byte)90);
  playSound(SoundEvents.SLIME_JUMP,.85f,.65f+random.nextFloat()*.22f);
 }
 @Override public void handleEntityEvent(byte id){
  if(id==90){pose=12;windup=0;return;}
  if(id==91){pose=-0;windup=5;return;}
  if(id==92){windup=5;return;}
  super.handleEntityEvent(id);
 }
 public float stretch(){return pose/12f;}
 public float compression(){return windup/5f;}
 @Override protected SoundEvent getAmbientSound(){return SoundEvents.SLIME_SQUISH;}
 @Override protected SoundEvent getHurtSound(DamageSource s){return SoundEvents.SLIME_HURT;}
 @Override protected SoundEvent getDeathSound(){return SoundEvents.SLIME_DEATH;}
}
''',encoding='utf-8')
# Sculpted, stepped silhouette; each mesh cuboid has its own UV island.
N=256;S=2;cursorX=cursorY=rowH=0;islands=[];lines=[]
def cube(b):
 global cursorX,cursorY,rowH
 x,y,z,w,h,d,mat=b
 uW=2*(w+d)+2;uH=h+d+2
 if cursorX+uW>N:cursorX=0;cursorY+=rowH;rowH=0
 u,v=cursorX,cursorY;cursorX+=uW;rowH=max(rowH,uH)
 assert v+uH<=N
 for xx,yy,ww,hh,face in [(u+d,v,w,d,'up'),(u+d+w,v,w,d,'down'),(u,v+d,d,h,'left'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'right'),(u+2*d+w,v+d,w,h,'back')]:
  islands.append((xx,yy,ww,hh,mat,face))
 return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
 lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
part('b','r','body',(0,24,0),(0,0,0),[(-4,-21,-4,8,16,8,'flesh'),(-5,-17,-3,10,10,6,'flesh'),(-3,-24,-3,6,5,6,'flesh'),(-4,-7,-4,8,6,8,'dark')])
part('h','b','crown',(0,-20,0),(0,0,0),[(-6,-5,-5,12,6,10,'crown'),(-5,-7,-4,10,2,8,'crown'),(-3,-8,-3,6,1,6,'crown'),(-6,0,-5,12,2,10,'rim'),(-4,-4,-6,8,4,1,'face')])
for i,side in enumerate((-1,1)):
 part('l'+str(i),'b','lobe'+str(i),(side*4,-3,0),(0,0,side*.12),[(-4,-4,-4,8,6,8,'dark'),(-3,-6,-3,6,2,6,'flesh'),(-3,2,-3,6,1,6,'dark')])
 part('ridge'+str(i),'b','ridge'+str(i),(side*3,-10,-3),(0,0,side*.12),[(-1,-8,-1,2,13,2,'vein')])
 for j in range(3):
  part(f'claw{i}_{j}','l'+str(i),f'claw{j}',(float(j*2-2),1,-4),(0,0,side*.05),[(-1,-1,-2,2,2,3,'horn'),(-1,0,-3,2,1,1,'horn')])
part('jaw','h','jaw',(0,0,-5),(0,0,0),[(-4,0,-1,8,2,2,'mouth'),(-3,2,-1,6,1,2,'dark')])
for i in range(4):
 part(f'tooth{i}','jaw',f'tooth{i}',(i*2-3,0,-1),(0,0,0),[(-.5,0,-.5,1,1,1,'horn')])
(java/'FallomorphClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class FallomorphClient{
 static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"fallomorph"),"main");
 @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,FallomorphClient::mesh);}
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.FALLOMORPH.get(),Renderer::new);}
 static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
 return LayerDefinition.create(m,256,256);}
 static class Model extends EntityModel<Fallomorph>{
  final ModelPart r,b,h,jaw;Model(ModelPart r){this.r=r;b=r.getChild("body");h=b.getChild("crown");jaw=h.getChild("jaw");}
  @Override public void setupAnim(Fallomorph e,float limb,float amount,float age,float yaw,float pitch){
   float s=e.stretch(),c=e.compression();
   b.yScale=1+.14f*s-.22f*c;b.xScale=1-.07f*s+.13f*c;b.zScale=b.xScale;
   b.xRot=-.13f*s+.07f*c;h.xRot=-b.xRot*.55f;h.zRot=(float)Math.sin(age*.16)*.045f;
   jaw.xRot=.14f+.55f*s+.07f*(float)Math.sin(age*.22);
   for(int i=0;i<2;i++){b.getChild("lobe"+i).zRot=(i==0?-1:1)*(.10f+.13f*c-.06f*s);}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float red,float green,float blue,float alpha){r.render(p,v,light,overlay,red,green,blue,alpha);}
 }
 static class Renderer extends MobRenderer<Fallomorph,Model>{
  Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.48f);}
  @Override public ResourceLocation getTextureLocation(Fallomorph e){return new ResourceLocation(Noctis.ID,"textures/entity/fallomorph.png");}
 }
}''',encoding='utf-8')
im=Image.new('RGBA',(N*S,N*S),(89,43,58,255))
pal={'flesh':(159,79,94),'dark':(111,49,72),'crown':(184,94,115),'rim':(119,45,70),'face':(173,81,104),'vein':(95,45,74),'mouth':(38,19,31),'horn':(222,196,145)}
for x,y,w,h,mat,face in islands:
 rng=random.Random(f'{x},{y}')
 for j in range(h*S):
  v=(j+.5)/(h*S)
  for i in range(w*S):
   u=(i+.5)/(w*S)
   shade=.75+.24*math.sin(math.pi*u)+.06*math.sin(v*13)+rng.uniform(-.035,.035)
   c=tuple(max(0,min(255,int(q*shade))) for q in pal[mat])
   if mat in ('flesh','dark','crown') and abs(math.sin(u*17+v*5+math.sin(v*16)*.3))>.98:c=tuple(int(q*.72) for q in c)
   if mat=='face' and face=='front':
    for ex in (.24,.76):
     dx=(u-ex)/.21;dy=(v-.52)/.30
     if abs(dx)+abs(dy)<1.1:c=(49,18,35)
     if abs(dx)+abs(dy)<.8:c=(250,193,76)
     if abs(dx)<.15 and abs(dy)<.63:c=(38,15,27)
   im.putpixel((x*S+i,y*S+j),(*c,255))
p=assets/'textures/entity/fallomorph.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
dump(assets/'models/item/fallomorph_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
dump(res/'data/noctismagic/forge/biome_modifier/fallomorph_spawns.json',{'type':'forge:add_spawns','biomes':'#minecraft:is_overworld','spawners':{'type':'noctismagic:fallomorph','weight':12,'minCount':1,'maxCount':1}})
dump(res/'data/noctismagic/loot_tables/entities/fallomorph.json',{'type':'minecraft:entity','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'minecraft:slime_ball','functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':2}}]}]}]})
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.fallomorph']='Fallomorfo' if loc=='it_it' else 'Fallomorph';d['item.noctismagic.fallomorph_spawn_egg']='Uovo generatore: Fallomorfo' if loc=='it_it' else 'Fallomorph Spawn Egg';dump(p,d)
print('Fallomorph: detailed custom voxel model, animated squash/stretch, leap attacks, low-frequency hostile spawns and spawn egg.')
