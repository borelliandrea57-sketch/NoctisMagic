"""1.7.16: real chair passengers for players and pastry-shop guests."""
from pathlib import Path
import sys,re
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic'
def edit(n,a,b):
 p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=', '''public static final RegistryObject<EntityType<ChairSeat>> CHAIR_SEAT=ENTITIES.register("chair_seat",()->EntityType.Builder.<ChairSeat>of(ChairSeat::new,MobCategory.MISC).sized(.05f,.05f).clientTrackingRange(8).updateInterval(1).build(ID+":chair_seat"));
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
(java/'ChairSeat.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.chat.Component;
import net.minecraftforge.registries.ForgeRegistries;

public class ChairSeat extends Entity{
 private BlockPos chair=BlockPos.ZERO;
 private int emptyTicks;
 public ChairSeat(EntityType<? extends ChairSeat> type,Level level){super(type,level);noPhysics=true;setNoGravity(true);}
 public static boolean isChair(BlockState s){
  var id=ForgeRegistries.BLOCKS.getKey(s.getBlock());
  if(id==null||!id.getNamespace().equals(Noctis.ID))return false;
  String name=id.getPath();
  return name.endsWith("_chair")||name.equals("lacrimosa_pew")||name.equals("chair");
 }
 public static double height(BlockState s){
  var id=ForgeRegistries.BLOCKS.getKey(s.getBlock());
  String n=id==null?"":id.getPath();
  if(n.equals("swamp_chair"))return 9/16.0;
  if(n.equals("lacrimosa_pew"))return 8/16.0;
  return 10/16.0;
 }
 public static Direction facing(BlockState s){
  return s.hasProperty(Furniture.FurnitureBlock.FACING)?s.getValue(Furniture.FurnitureBlock.FACING):Direction.NORTH;
 }
 public static InteractionResult interact(Level level,BlockPos pos,Player player){
  if(player.isShiftKeyDown()||player.isPassenger())return InteractionResult.PASS;
  if(!level.isClientSide&&level instanceof ServerLevel sl){
   if(!sit(sl,pos,player))player.displayClientMessage(Component.literal("Sedia occupata"),true);
  }
  return InteractionResult.sidedSuccess(level.isClientSide);
 }
 public static boolean sit(ServerLevel l,BlockPos pos,LivingEntity rider){
  BlockState s=l.getBlockState(pos);
  if(!isChair(s)||rider.isPassenger()||!rider.isAlive())return false;
  for(ChairSeat existing:l.getEntitiesOfClass(ChairSeat.class,new AABB(pos).inflate(.25),e->e.chair.equals(pos))){
   if(existing.isVehicle())return false;
   existing.discard();
  }
  ChairSeat e=Noctis.CHAIR_SEAT.get().create(l);if(e==null)return false;
  e.chair=pos.immutable();
  e.setPos(pos.getX()+.5,pos.getY()+height(s),pos.getZ()+.5);
  e.setYRot(facing(s).toYRot());
  e.setXRot(0);
  if(!l.addFreshEntity(e))return false;
  if(!rider.startRiding(e,true)){e.discard();return false;}
  rider.setYRot(e.getYRot());rider.setYHeadRot(e.getYRot());rider.setYBodyRot(e.getYRot());
  if(rider instanceof net.minecraft.world.entity.Mob mob)mob.getNavigation().stop();
  return true;
 }
 @Override protected void defineSynchedData(){}
 @Override protected void readAdditionalSaveData(CompoundTag t){chair=BlockPos.of(t.getLong("Chair"));}
 @Override protected void addAdditionalSaveData(CompoundTag t){t.putLong("Chair",chair.asLong());}
 @Override public void tick(){
  super.tick();setDeltaMovement(Vec3.ZERO);
  if(level().isClientSide)return;
  BlockState s=level().getBlockState(chair);
  if(!isChair(s)){ejectPassengers();discard();return;}
  setPos(chair.getX()+.5,chair.getY()+height(s),chair.getZ()+.5);
  setYRot(facing(s).toYRot());
  if(!isVehicle()){if(++emptyTicks>3)discard();}else emptyTicks=0;
 }
 @Override protected boolean canAddPassenger(Entity e){return !isVehicle()&&e instanceof LivingEntity;}
 @Override protected void positionRider(Entity passenger,Entity.MoveFunction move){
  if(!hasPassenger(passenger))return;
  // Origin is the seat surface. Lower the standing-model origin by the hip height.
  double hip=passenger instanceof CrossoverGuest guest&&guest.kind()==2?.89:.75;
  move.accept(passenger,getX(),getY()-hip,getZ());
  passenger.setDeltaMovement(Vec3.ZERO);
 }
 @Override public Vec3 getDismountLocationForPassenger(LivingEntity e){
  Direction f=facing(level().getBlockState(chair));
  for(Direction dir:new Direction[]{f,f.getClockWise(),f.getCounterClockWise(),f.getOpposite()}){
   BlockPos p=chair.relative(dir);Vec3 v=Vec3.atBottomCenterOf(p);
   if(level().noCollision(e,e.getBoundingBox().move(v.x-e.getX(),v.y-e.getY(),v.z-e.getZ())))return v;
  }
  return Vec3.atBottomCenterOf(chair.above());
 }
}''',encoding='utf-8')
(java/'ChairSeatClient.java').write_text('''package it.noctis.magic;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class ChairSeatClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.CHAIR_SEAT.get(),R::new);}
 static final class R extends EntityRenderer<ChairSeat>{
  R(EntityRendererProvider.Context c){super(c);shadowRadius=0;}
  @Override public ResourceLocation getTextureLocation(ChairSeat e){return new ResourceLocation("minecraft","textures/misc/white.png");}
 }
}''',encoding='utf-8')
p=java/'Furniture.java';s=p.read_text(encoding='utf-8')
a='if(kind==0||kind==1)return InteractionResult.PASS;';assert a in s
s=s.replace(a,'if(ChairSeat.isChair(s))return ChairSeat.interact(l,p,player);\n            '+a,1)
a='if(kind==2)return switch(s.getValue(FACING))';assert a in s
s=s.replace(a,'''if(ChairSeat.isChair(s)){
                double h=ChairSeat.height(s)*16;
                VoxelShape seat=box(1,0,1,15,h,15);
                VoxelShape back=switch(s.getValue(FACING)){
                    case NORTH->box(1,h,13,15,16,15);
                    case SOUTH->box(1,h,1,15,16,3);
                    case EAST->box(1,h,1,3,16,15);
                    default->box(13,h,1,15,16,15);
                };
                return net.minecraft.world.phys.shapes.Shapes.or(seat,back);
            }
            '''+a,1)
p.write_text(s,encoding='utf-8')
# Existing shop guests and new ones find their original chair, rather than standing on it.
p=java/'CrossoverGuest.java';s=p.read_text(encoding='utf-8')
a='public boolean pastrySeated(){return kind()!=0&&level().getBlockState(blockPosition().below()).is(Furniture.SWEET_CHAIR.get());}';assert a in s
s=s.replace(a,'''public boolean pastrySeated(){return kind()!=0&&getVehicle() instanceof ChairSeat;}
    private void tryPastrySeat(){
        if(kind()==0||home==null||isPassenger()||!(level() instanceof ServerLevel l)||tickCount%20!=0)return;
        for(BlockPos candidate:new BlockPos[]{home,home.below(),blockPosition(),blockPosition().below()}){
            if(l.getBlockState(candidate).is(Furniture.SWEET_CHAIR.get())&&distanceToSqr(candidate.getX()+.5,candidate.getY()+.5,candidate.getZ()+.5)<9){
                ChairSeat.sit(l,candidate,this);return;
            }
        }
    }''',1)
a='super.tick();';assert a in s;s=s.replace(a,a+'tryPastrySeat();',1)
s=s.replace('if(home!=null&&tickCount%20==0&&','if(!isPassenger()&&home!=null&&tickCount%20==0&&',1)
p.write_text(s,encoding='utf-8')
# Remove the old render-only vertical offsets that made the attorneys float.
p=java/'CrossoverClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('if(e.pastrySeated())p.translate(0,-1.02,0);','')
p.write_text(s,encoding='utf-8')
p=java/'EdgeworthSculptedClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('if(e.pastrySeated())p.translate(0,-.94,0);','')
p.write_text(s,encoding='utf-8')
print('Functional chair passenger entities; guest seat recovery; no old render offsets; player dismount and occupancy protection.')
