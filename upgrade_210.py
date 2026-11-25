"""Johnny's wheelchair survives his death as a persistent player-controlled mount."""
from pathlib import Path
import sys,json
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
 p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
edit('Noctis.java','public static final RegistryObject<EntityType<JohnnyJoestar>> JOHNNY=','''public static final RegistryObject<EntityType<JohnnyWheelchair>> JOHNNY_WHEELCHAIR=ENTITIES.register("johnny_wheelchair",()->EntityType.Builder.<JohnnyWheelchair>of(JohnnyWheelchair::new,MobCategory.MISC).sized(.86f,1.66f).clientTrackingRange(10).build(ID+":johnny_wheelchair"));
    public static final RegistryObject<EntityType<JohnnyJoestar>> JOHNNY=''')
edit('Noctis.java','e.put(JOHNNY.get(),JohnnyJoestar.attributes().build());','e.put(JOHNNY_WHEELCHAIR.get(),JohnnyWheelchair.attributes().build());e.put(JOHNNY.get(),JohnnyJoestar.attributes().build());')
edit('JohnnyJoestar.java',' @Override public void tick()', ''' @Override public void die(net.minecraft.world.damagesource.DamageSource damage){
  if(isAlive()||!getPersistentData().getBoolean("NoctisChairDropped")){
   if(level() instanceof ServerLevel l&&!getPersistentData().getBoolean("NoctisChairDropped")){
    getPersistentData().putBoolean("NoctisChairDropped",true);
    JohnnyWheelchair chair=Noctis.JOHNNY_WHEELCHAIR.get().create(l);
    if(chair!=null){chair.moveTo(getX(),getY(),getZ(),getYRot(),0);chair.setPersistenceRequired();l.addFreshEntity(chair);}
   }
  }
  super.die(damage);
 }
 @Override public void tick()''')
(java/'JohnnyWheelchair.java').write_text('''package it.noctis.magic;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public final class JohnnyWheelchair extends PathfinderMob{
 public JohnnyWheelchair(EntityType<? extends JohnnyWheelchair> type,Level level){
  super(type,level);setPersistenceRequired();setMaxUpStep(.60f);
 }
 public static AttributeSupplier.Builder attributes(){
  return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,30).add(Attributes.ARMOR,4).add(Attributes.MOVEMENT_SPEED,.26);
 }
 @Override protected void registerGoals(){}
 @Override public boolean removeWhenFarAway(double distance){return false;}
 @Override public boolean isPushable(){return !isVehicle();}
 @Override public boolean canBeLeashed(Player player){return false;}
 @Override protected boolean canAddPassenger(Entity passenger){return getPassengers().isEmpty()&&passenger instanceof Player;}
 @Override public LivingEntity getControllingPassenger(){return getFirstPassenger() instanceof Player player?player:null;}
 @Override public double getPassengersRidingOffset(){return .82;}
 @Override protected void positionRider(Entity passenger,Entity.MoveFunction move){
  if(!hasPassenger(passenger))return;
  double yaw=Math.toRadians(getYRot()),front=.035;
  move.accept(passenger,getX()-Math.sin(yaw)*front,getY()+getPassengersRidingOffset()+passenger.getMyRidingOffset(),getZ()+Math.cos(yaw)*front);
 }
 @Override public InteractionResult mobInteract(Player player,InteractionHand hand){
  if(hand!=InteractionHand.MAIN_HAND||player.isShiftKeyDown()||isVehicle())return InteractionResult.PASS;
  if(!level().isClientSide)player.startRiding(this);
  return InteractionResult.sidedSuccess(level().isClientSide);
 }
 @Override public void travel(Vec3 input){
  if(isAlive()&&getControllingPassenger() instanceof Player rider){
   setYRot(rider.getYRot());yBodyRot=getYRot();yHeadRot=getYRot();setXRot(0);
   getNavigation().stop();
   if(isControlledByLocalInstance()){
    setSpeed((float)getAttributeValue(Attributes.MOVEMENT_SPEED));
    float forward=rider.zza<0?rider.zza*.55f:rider.zza;
    super.travel(new Vec3(rider.xxa*.45f,0,forward));
   }
   return;
  }
  super.travel(new Vec3(0,input.y,0));
 }
}''',encoding='utf-8')
# Reuse precisely the chair mesh already visible on Johnny, excluding his body and legs.
s=(java/'JohnnyClient.java').read_text(encoding='utf-8')
a=s.index('  void tube(Part p,');b=s.index('  Model(){',a)
helpers=s[a:b]
a=s.index('   // Wooden high back, seat, padded leather and footrest.');b=s.index('   // Seated torso',a)
mesh=s[a:b]
(java/'JohnnyWheelchairClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.Q;
import it.noctis.magic.SculptedGuestsClient.V;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class JohnnyWheelchairClient{
 @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.JOHNNY_WHEELCHAIR.get(),Renderer::new);}
 static class Renderer extends MobRenderer<JohnnyWheelchair,Model>{
  Renderer(EntityRendererProvider.Context c){super(c,new Model(),.48f);}
  @Override protected void scale(JohnnyWheelchair e,PoseStack p,float partial){p.scale(1.16f,1.16f,1.16f);}
  @Override public ResourceLocation getTextureLocation(JohnnyWheelchair e){return new ResourceLocation(Noctis.ID,"textures/entity/johnny_wheelchair.png");}
 }
 static class Model extends EntityModel<JohnnyWheelchair>{
  final Part root=new Part(0,0,0),chair=root.child(0,0,0);
  final Part[] wheel=new Part[2],caster=new Part[2];
'''+helpers+'''  Model(){
'''+mesh+'''  }
  @Override public void setupAnim(JohnnyWheelchair e,float limb,float amount,float age,float yaw,float pitch){
   for(int i=0;i<2;i++){wheel[i].rx=-limb*.53f;caster[i].rx=-limb*2.4f;}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.drawStyled(p,v,light,overlay,r,g,b,a,8);}
 }
}''',encoding='utf-8')
for lang in ('it_it','en_us'):
 p=assets/('lang/'+lang+'.json');d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.johnny_wheelchair']='Carrozzina di Johnny' if lang=='it_it' else "Johnny's wheelchair";p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Johnny leaves a persistent empty wheelchair, with ride controls and spinning wheels.')
