"""1.6.4: secret Exodia encounter, five distinct chest relics and colossal sculpted boss."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,a,b):
 p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(name,s): (java/name).write_text(s,encoding='utf-8')
def j(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Exodia>> EXODIA=ENTITIES.register("exodia",()->EntityType.Builder.<Exodia>of(Exodia::new,MobCategory.MONSTER).sized(4.5f,8.8f).clientTrackingRange(16).fireImmune().build(ID+":exodia"));
    public static final java.util.List<RegistryObject<Item>> EXODIA_PARTS=ExodiaRitual.registerParts();
    public static final RegistryObject<Item> EXODIA_SEAL=ITEMS.register("exodia_seal",()->new Item(new Item.Properties().rarity(Rarity.EPIC).stacksTo(1)));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(EXODIA.get(),Exodia.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'for(var part:EXODIA_PARTS)e.accept(part.get());e.accept(EXODIA_SEAL.get());')
write('ExodiaRitual.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.minecraftforge.event.LootTableLoadEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegistryObject;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class ExodiaRitual {
 static final String[] IDS={"head","left_arm","right_arm","left_leg","right_leg"};
 static final String[] NAMES={"Testa","Braccio sinistro","Braccio destro","Gamba sinistra","Gamba destra"};
 static List<RegistryObject<Item>> registerParts(){
  List<RegistryObject<Item>> out=new ArrayList<>();
  for(String id:IDS)out.add(Noctis.ITEMS.register("exodia_"+id,Fragment::new));
  return List.copyOf(out);
 }
 @SubscribeEvent public static void loot(LootTableLoadEvent e){
  String p=e.getName().getPath();
  if(!(p.startsWith("chests/")||p.contains("/chests/")||p.startsWith("chest/")||p.contains("/chest/")))return;
  if(e.getTable().getPool("noctismagic_exodia_fragments")!=null)return;
  var pool=LootPool.lootPool().name("noctismagic_exodia_fragments").setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(.30f));
  for(var part:Noctis.EXODIA_PARTS)pool.add(LootItem.lootTableItem(part.get()));
  e.getTable().addPool(pool.build());
 }
 static class Fragment extends Item{
  Fragment(){super(new Item.Properties().rarity(Rarity.EPIC).stacksTo(16));}
  @Override public boolean isFoil(ItemStack s){return true;}
  @Override public InteractionResultHolder<ItemStack> use(Level level,Player player,InteractionHand hand){
   if(player instanceof ServerPlayer p)invoke(p);
   return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand),level.isClientSide);
  }
  @Override public void appendHoverText(ItemStack stack,Level level,List<Component> tip,TooltipFlag flag){
   tip.add(Component.translatable("item.noctismagic.exodia_fragment.tip").withStyle(ChatFormatting.GOLD));
  }
 }
 static int slot(Player p,Item item){for(int i=0;i<p.getInventory().getContainerSize();i++)if(p.getInventory().getItem(i).is(item))return i;return -1;}
 static void invoke(ServerPlayer p){
  if(!p.isAlive()||p.isSpectator())return;
  ServerLevel l=p.serverLevel();List<String> missing=new ArrayList<>();int[] slots=new int[5];
  for(int i=0;i<5;i++){slots[i]=slot(p,Noctis.EXODIA_PARTS.get(i).get());if(slots[i]<0)missing.add(NAMES[i]);}
  if(!missing.isEmpty()){p.sendSystemMessage(Component.literal("Exodia - Parti mancanti: "+String.join(", ",missing)).withStyle(ChatFormatting.GOLD));return;}
  if(!l.getEntitiesOfClass(Exodia.class,p.getBoundingBox().inflate(160),Exodia::isAlive).isEmpty()){p.sendSystemMessage(Component.literal("Exodia e' gia' presente nelle vicinanze."));return;}
  Exodia boss=Noctis.EXODIA.get().create(l);if(boss==null)return;
  boolean found=false;
  for(int i=0;i<48;i++){
   double a=Math.toRadians(p.getYRot()+90)+(i==0?0:(i%2==0?1:-1)*((i+1)/2)*Math.PI/24);
   int r=12+(i%4)*4,x=p.getBlockX()+(int)Math.round(Math.cos(a)*r),z=p.getBlockZ()+(int)Math.round(Math.sin(a)*r);
   if(!l.hasChunkAt(new BlockPos(x,p.getBlockY(),z)))continue;
   int y=l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
   if(Math.abs(y-p.getBlockY())>12||y+10>=l.getMaxBuildHeight())continue;
   BlockPos q=new BlockPos(x,y,z);boss.moveTo(x+.5,y,z+.5,p.getYRot()+180,0);
   if(l.getWorldBorder().isWithinBounds(boss.getBoundingBox())&&l.noCollision(boss)&&!l.containsAnyLiquid(boss.getBoundingBox())){found=true;break;}
  }
  if(!found){boss.discard();p.sendSystemMessage(Component.literal("Il rituale necessita di una grande area aperta. Le cinque parti non sono state consumate."));return;}
  boss.bind(p);boss.setPersistenceRequired();
  if(!l.addFreshEntity(boss))return;
  for(int i:slots)p.getInventory().getItem(i).shrink(1);
  p.getInventory().setChanged();
  NpcDialogue.say(l,Component.literal("EXODIA, IL PROIBITO! I cinque sigilli sono infranti!").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));
  l.playSound(null,boss.blockPosition(),SoundEvents.WARDEN_ROAR,SoundSource.HOSTILE,4,.65f);
  l.sendParticles(ParticleTypes.TOTEM_OF_UNDYING,boss.getX(),boss.getY()+4,boss.getZ(),180,2.7,4,2.7,.18);
 }
}''')
write('Exodia.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.item.Items;
public class Exodia extends Monster{
 final ServerBossEvent bar=new ServerBossEvent(Component.literal("Exodia - Il Proibito"),BossEvent.BossBarColor.YELLOW,BossEvent.BossBarOverlay.NOTCHED_20);
 UUID summoner;int cooldown=80,phase,cycle,charge,mode,pose,poseMode,absent;Vec3 aim=Vec3.ZERO;
 public Exodia(EntityType<? extends Monster> t,Level l){super(t,l);setNoGravity(true);}
 public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,1500).add(Attributes.ATTACK_DAMAGE,38).add(Attributes.ARMOR,20).add(Attributes.ARMOR_TOUGHNESS,8).add(Attributes.FOLLOW_RANGE,100).add(Attributes.MOVEMENT_SPEED,.29).add(Attributes.KNOCKBACK_RESISTANCE,1);}
 public void bind(ServerPlayer p){summoner=p.getUUID();}
 @Override protected void registerGoals(){}
 @Override public boolean removeWhenFarAway(double d){return false;}
 @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);bar.addPlayer(p);}
 @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
 @Override public void remove(RemovalReason r){bar.removeAllPlayers();super.remove(r);}
 boolean valid(Player p){return p!=null&&p.isAlive()&&!p.isCreative()&&!p.isSpectator()&&distanceTo(p)<100;}
 @Override public void tick(){
  super.tick();if(pose>0)pose--;if(!(level() instanceof ServerLevel l)||!isAlive())return;
  setNoGravity(true);bar.setProgress(getHealth()/getMaxHealth());
  Player t=summoner==null?null:l.getPlayerByUUID(summoner);
  if(!valid(t))t=l.getNearestPlayer(getX(),getY(),getZ(),80,p->p instanceof Player pl&&valid(pl));
  if(!valid(t)){setDeltaMovement(getDeltaMovement().scale(.65));charge=0;return;}
  setTarget(t);
  int next=getHealth()<=getMaxHealth()*.33f?2:getHealth()<=getMaxHealth()*.66f?1:0;
  if(next>phase){phase=next;bar.setColor(phase==2?BossEvent.BossBarColor.RED:BossEvent.BossBarColor.PURPLE);
   NpcDialogue.say(l,Component.literal(phase==1?"Exodia: I sigilli cedono!":"Exodia: OBLITERAZIONE!").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));
   playSound(SoundEvents.WARDEN_ROAR,3,.6f);l.sendParticles(ParticleTypes.FLAME,getX(),getY()+4,getZ(),90,2,3,2,.10);}
  Vec3 diff=t.position().subtract(position());double dist=diff.horizontalDistance();float yaw=(float)(Math.atan2(diff.z,diff.x)*180/Math.PI)-90;setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);
  Vec3 flat=new Vec3(diff.x,0,diff.z);
  Vec3 speed=dist>9&&charge==0?flat.normalize().scale(.24+phase*.08):Vec3.ZERO;
  speed=speed.add(0,Math.max(-.22,Math.min(.22,(t.getY()-getY())*.06)),0);
  if(!l.noCollision(this,getBoundingBox().move(speed))){Vec3 up=new Vec3(0,.26,0);speed=l.noCollision(this,getBoundingBox().move(up))?up:Vec3.ZERO;}
  setDeltaMovement(getDeltaMovement().scale(.35).add(speed.scale(.65)));
  if(tickCount%6==0)l.sendParticles(ParticleTypes.TOTEM_OF_UNDYING,getX(),getY()+3.8,getZ(),4,1.8,2.4,1.8,.015);
  if(charge>0){
   if(charge%4==0){
    double radius=mode==1?5.5:mode==2?7:1.5;
    for(int i=0;i<18;i++){double a=i*Math.PI/9;l.sendParticles(ParticleTypes.FLAME,aim.x+Math.cos(a)*radius,aim.y+.18,aim.z+Math.sin(a)*radius,1,0,0,0,0);}
    if(mode==0){Vec3 start=position().add(0,6.1,0);for(int i=0;i<16;i++){Vec3 q=start.lerp(aim.add(0,1,0),i/15.0);l.sendParticles(ParticleTypes.END_ROD,q.x,q.y,q.z,1,0,0,0,0);}}
   }
   if(--charge==0)strike(l);
   return;
  }
  if(--cooldown>0)return;
  if(distanceTo(t)>32||!hasLineOfSight(t)){cooldown=15;return;}
  mode=cycle++%3;aim=mode==2?position():t.position();charge=mode==0?38:mode==1?30:24;
  cooldown=phase==2?44:phase==1?58:78;
  l.broadcastEntityEvent(this,(byte)(90+mode));
  playSound(SoundEvents.BEACON_POWER_SELECT,2,.65f);
  for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(45),this::valid))p.displayClientMessage(Component.literal(mode==0?"Exodia carica il Raggio dell'Obliterazione!":mode==1?"Sigillo di distruzione: esci dal cerchio!":"Onda delle catene: allontanati!").withStyle(ChatFormatting.GOLD),true);
 }
 void strike(ServerLevel l){
  if(mode==0){
   Vec3 start=position().add(0,6.1,0),end=aim.add(0,1,0),line=end.subtract(start);
   for(int i=0;i<=40;i++){Vec3 q=start.lerp(end,i/40.0);l.sendParticles(ParticleTypes.FLAME,q.x,q.y,q.z,4,.25,.25,.25,.025);l.sendParticles(ParticleTypes.END_ROD,q.x,q.y,q.z,2,.15,.15,.15,.02);}
   for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(40),this::valid)){
    Vec3 pos=p.getEyePosition();double u=Math.max(0,Math.min(1,pos.subtract(start).dot(line)/Math.max(.01,line.lengthSqr())));
    if(pos.distanceTo(start.add(line.scale(u)))<2.0&&hasLineOfSight(p))p.hurt(damageSources().magic(),40+phase*8);
   }
   playSound(SoundEvents.WARDEN_SONIC_BOOM,3,.7f);
  }else{
   double radius=mode==1?5.5:7;for(int i=0;i<48;i++){double a=i*Math.PI/24;l.sendParticles(ParticleTypes.TOTEM_OF_UNDYING,aim.x+Math.cos(a)*radius,aim.y+.5,aim.z+Math.sin(a)*radius,4,.35,.45,.35,.06);}
   for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(45),this::valid)){
    double dx=p.getX()-aim.x,dz=p.getZ()-aim.z;
    if(dx*dx+dz*dz<radius*radius&&Math.abs(p.getY()-aim.y)<4&&hasLineOfSight(p)){
     p.hurt(mode==1?damageSources().magic():damageSources().mobAttack(this),mode==1?30+phase*6:34+phase*7);
     if(mode==1)p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,80,1));
     else p.knockback(2.1,-dx,-dz);
    }
   }
   playSound(SoundEvents.GENERIC_EXPLODE,3,.7f);
  }
  l.broadcastEntityEvent(this,(byte)94);
 }
 @Override public void handleEntityEvent(byte id){if(id>=90&&id<=92){poseMode=id-90;pose=40;return;}if(id==94){pose=12;return;}super.handleEntityEvent(id);}
 public float action(){return pose<=0?0:Math.min(1,pose/8f);}
 public int actionMode(){return poseMode;}
 @Override protected void dropCustomDeathLoot(DamageSource s,int looting,boolean hit){
  super.dropCustomDeathLoot(s,looting,hit);spawnAtLocation(Noctis.EXODIA_SEAL.get());spawnAtLocation(Items.NETHER_STAR);spawnAtLocation(Items.NETHER_STAR);for(int i=0;i<20;i++)spawnAtLocation(Noctis.CRYSTAL.get());
 }
 @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);if(summoner!=null)n.putUUID("Summoner",summoner);n.putInt("Phase",phase);n.putInt("Cycle",cycle);}
 @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);summoner=n.hasUUID("Summoner")?n.getUUID("Summoner"):null;phase=n.getInt("Phase");cycle=n.getInt("Cycle");bar.setColor(phase==2?BossEvent.BossBarColor.RED:phase==1?BossEvent.BossBarColor.PURPLE:BossEvent.BossBarColor.YELLOW);}
}''')
# Custom sculpted Egyptian armor: layered bronze plates, tall crown, broad shoulder pieces,
# articulated fists and hanging broken chains. No shared humanoid face texture.
write('ExodiaClient.java','''package it.noctis.magic;
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
public class ExodiaClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.EXODIA.get(),R::new);}
 static V ring(float a,float b,float w,float h,float r,float u,float v){
  float ca=(float)Math.cos(a),sa=(float)Math.sin(a),cb=(float)Math.cos(b),sb=(float)Math.sin(b);
  return new V((w+r*cb)*ca,(h+r*cb)*sa,r*sb,u,v,ca*cb,sa*cb,sb);
 }
 static void loop(Part p,int tile,float w,float h,float r){
  for(int i=0;i<18;i++)for(int j=0;j<8;j++){
   float a=i*(float)Math.PI/9,A=(i+1)*(float)Math.PI/9,b=j*(float)Math.PI/4,B=(j+1)*(float)Math.PI/4;
   p.faces.add(new Q(ring(a,b,w,h,r,i/18f,j/8f),ring(A,b,w,h,r,(i+1)/18f,j/8f),ring(A,B,w,h,r,(i+1)/18f,(j+1)/8f),ring(a,B,w,h,r,i/18f,(j+1)/8f),tile));
  }
 }
 static class M extends EntityModel<Exodia>{
  final Part root=new Part(0,0,0),body=root.child(0,-.3f,0),head=body.child(0,-2.1f,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shin=new Part[2],skirts=new Part[2];final Part[][] chains=new Part[2][5];
  M(){
   body.loft(0,36,-1.5f,0,0,2.7f,1.9f,-.2f,0,0,5.2f,2.65f,2.6f,0,-.2f,5.5f,3.1f,5.8f,0,0,4.05f,2.4f,9.3f,0,0,3.05f,1.95f,11,0,0,3.9f,2.45f);
   // Massive gold collar and decorated breastplate.
   body.loft(1,40,-1.7f,0,0,1.65f,1.40f,-.8f,0,0,3.0f,2.1f,.35f,0,0,5.1f,2.8f,1.25f,0,-.2f,5.4f,2.9f);
   for(int s:new int[]{-1,1}){
    body.blade(2,s*4.0f,1.0f,-1.65f,s*.35f,5.6f,-2.65f,1.8f);
    body.blade(1,s*3.8f,1.3f,-1.8f,s*.45f,4.6f,-2.90f,.55f);
    for(int j=0;j<3;j++)body.blade(1,s*2.8f,5.4f+j*1.15f,-1.65f,s*.45f,6.3f+j*1.15f,-2.24f,.48f);
   }
   body.oval(1,0,3.65f,-3.05f,1.50f,1.65f,.55f);
   body.oval(3,0,3.65f,-3.47f,1.02f,1.13f,.26f);
   body.oval(12,0,3.65f,-3.68f,.48f,.53f,.16f);
   body.loft(1,32,9.0f,0,0,3.35f,2.10f,10.4f,0,0,3.75f,2.47f);
   body.oval(3,0,9.7f,-2.47f,.84f,.71f,.24f);
   // Rigid mask, narrow glowing eyes and angular gold crown with blue inlays.
   head.loft(4,40,-7.3f,0,.12f,1.45f,1.40f,-6.3f,0,.05f,2.8f,2.35f,-4.2f,0,0,3.05f,2.50f,-2.3f,0,-.12f,2.63f,2.17f,-.35f,0,-.20f,1.28f,1.20f,.2f,0,-.22f,.65f,.65f);
   head.loft(1,32,-10.0f,0,.2f,1.05f,1.15f,-8.85f,0,.14f,2.4f,2.15f,-7.4f,0,.05f,3.0f,2.72f,-6.6f,0,0,3.18f,2.75f);
   head.blade(1,0,-6.8f,-2.8f,0,-11.6f,-.6f,1.7f);
   head.blade(3,0,-7.25f,-2.9f,0,-10.6f,-.8f,.63f);
   head.blade(1,0,-3.4f,-2.45f,0,-1.4f,-2.31f,.70f);
   head.blade(1,0,-.65f,-1.35f,0,1.35f,-.95f,.92f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    Part eye=head.child(s*1.18f,-4.05f,-2.28f);eye.ry=-s*.25f;eye.rz=-s*.17f;
    eye.oval(5,0,0,0,.88f,.40f,.19f);eye.oval(12,0,0,-.14f,.65f,.21f,.11f);
    head.blade(1,s*.45f,-4.75f,-2.57f,s*2.25f,-4.92f,-1.78f,.75f);
    head.blade(1,s*2.40f,-6.95f,-.8f,s*4.7f,-10.7f,.65f,2.3f);
    head.blade(1,s*2.75f,-6.2f,.2f,s*3.75f,-.3f,1.0f,2.1f);
    for(int j=0;j<4;j++)head.blade(3,s*2.9f,-5.9f+j*1.16f,-.42f,s*3.65f,-5.5f+j*1.16f,.35f,.47f);
    arms[i]=body.child(s*5.15f,.3f,0);
    arms[i].loft(0,28,-1.15f,0,0,1.65f,1.68f,.6f,0,0,2.60f,2.33f,2.65f,0,0,2.22f,2.12f,5.4f,0,0,1.52f,1.6f);
    Part shoulder=arms[i].child(s*.55f,-.55f,0);shoulder.rz=-s*.26f;
    shoulder.loft(1,32,-2.8f,0,0,.55f,.63f,-1.8f,0,0,2.0f,2.15f,-.4f,0,0,2.8f,2.7f,1.05f,0,0,2.53f,2.4f,2.15f,0,0,1.9f,2.0f);
    shoulder.blade(1,s*1.1f,-.8f,0,s*4.0f,-3.15f,.15f,2.55f);
    shoulder.oval(3,0,-.3f,-2.47f,.97f,1.10f,.20f);
    fore[i]=arms[i].child(0,5.2f,0);
    fore[i].loft(0,28,-.3f,0,0,1.55f,1.6f,1.4f,0,0,1.98f,1.9f,3.9f,0,0,1.50f,1.45f);
    fore[i].loft(1,32,1.25f,0,0,2.15f,2.02f,2.0f,0,0,2.23f,2.12f,3.15f,0,0,1.85f,1.82f,3.8f,0,0,1.74f,1.72f);
    fore[i].loft(3,32,1.65f,0,0,2.22f,2.1f,2.0f,0,0,2.25f,2.13f);
    fore[i].oval(0,0,4.9f,-.1f,1.46f,1.44f,1.24f);
    for(int j=0;j<4;j++){fore[i].oval(1,-1.02f+j*.68f,5.55f,-.62f,.36f,.75f,.40f);}
    Part prev=fore[i];for(int j=0;j<5;j++){
     Part link=chains[i][j]=prev.child(j==0?s*1.55f:0,j==0?3.0f:1.12f,j==0?.5f:0);
     link.ry=(j%2)*1.50f;loop(link,5,.43f,.75f,.15f);prev=link;
    }
    skirts[i]=body.child(s*1.65f,10.1f,0);skirts[i].rz=-s*.15f;
    skirts[i].loft(1,28,0,0,0,1.9f,2.1f,1.5f,s*.35f,0,2.25f,2.25f,3.75f,s*.7f,.2f,1.9f,2.0f,4.7f,s*.9f,.35f,1.45f,1.8f);
    skirts[i].blade(3,0,.3f,-2.0f,s*.65f,4.6f,-1.85f,.8f);
    legs[i]=root.child(s*2.15f,11.3f,0);
    legs[i].loft(0,28,-.45f,0,0,2.0f,2.05f,2.3f,0,0,1.95f,1.8f,5.6f,0,0,1.36f,1.45f);
    shin[i]=legs[i].child(0,5.45f,0);
    shin[i].oval(1,0,0,-.65f,1.65f,1.42f,1.25f);
    shin[i].loft(1,28,.5f,0,0,1.47f,1.52f,2.1f,0,0,1.62f,1.68f,4.4f,0,0,1.3f,1.39f,5.75f,0,0,1.40f,1.45f);
    shin[i].blade(3,0,.7f,-1.58f,0,5.35f,-1.4f,1.0f);
    shin[i].loft(1,28,5.25f,0,0,1.45f,1.45f,6.5f,0,-.65f,1.76f,2.20f,7.35f,0,-.7f,1.84f,2.36f);
   }
   Part apron=body.child(0,10.0f,-2.0f);apron.blade(3,0,0,0,0,7.5f,.4f,2.4f);apron.blade(1,0,.7f,-.25f,0,7.0f,.22f,.45f);
  }
  @Override public void setupAnim(Exodia e,float limb,float amount,float age,float yaw,float pitch){
   float hit=e.action();int mode=e.actionMode();head.ry=yaw*.009f;head.rx=pitch*.006f-.04f*hit;body.rx=hit*.075f;
   for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.50f+i*Math.PI)*amount;
    arms[i].rx=-w*.32f-hit*(mode==0?1.1f:mode==1?1.55f:.52f);
    arms[i].rz=-s*(.13f+hit*(mode==2?1.15f:.35f));fore[i].rx=-hit*(mode==0?.65f:.30f);
    legs[i].rx=w*.38f;shin[i].rx=Math.max(0,-w)*.18f;skirts[i].rx=w*.08f;
    for(int j=0;j<5;j++){chains[i][j].rx=(float)Math.sin(age*.11f-j*.5f+i)*(.12f+hit*.12f);chains[i][j].rz=(float)Math.cos(age*.08f-j*.65f)*.09f;}
   }
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<Exodia,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),2.15f);}
  @Override protected void scale(Exodia e,PoseStack p,float partial){p.scale(3.8f,3.8f,3.8f);}
  @Override public ResourceLocation getTextureLocation(Exodia e){return new ResourceLocation(Noctis.ID,"textures/entity/exodia.png");}
 }
}''')
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
def png(p,W,H,pix):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+chunk(b'IEND',b''))
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
W,H=1024,512;pix=bytearray(W*H*4)
for m,base in {0:(137,84,43),1:(211,159,68),2:(104,56,29),3:(45,73,131),4:(117,71,47),5:(63,45,40),12:(255,230,108)}.items():
 for y in range(128):
  v=min(1,max(0,(y-3)/121))
  for x in range(128):
   u=min(1,max(0,(x-3)/121))
   c=mix(base,(52,28,23),.18*v+.18*(1-math.sin(u*math.pi)))
   if m in (0,1,2,3):
    c=mix(c,(255,224,145) if m!=3 else (128,171,222),.36*math.exp(-((u-.36)/.16)**2))
    if v<.035 or v>.965:c=mix(c,(76,44,30),.42)
    if m==1 and abs(v-.14)<.015:c=mix(c,(255,230,157),.50)
    if m==0:
     if abs(math.sin(u*math.pi*9+v*3))<.085:c=mix(c,(78,41,25),.30)
   if m==12:c=mix((255,158,48),(255,252,197),.5+.4*math.sin(u*math.pi))
   off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/exodia.png',W,H,pix)
# Unique pixel icons: five pieces on golden sealed plaques; trophy is an open golden eye.
for k,id in enumerate(['head','left_arm','right_arm','left_leg','right_leg','seal']):
 W=H=32;pix=bytearray(W*H*4)
 for y in range(H):
  for x in range(W):
   X=x-15.5;Y=y-15.5;c=None
   if abs(X)<11 and abs(Y)<13 and abs(X)+abs(Y)<21:
    c=(63,36,24) if abs(X)>9 or abs(Y)>11 or abs(X)+abs(Y)>19 else (184,133,52)
    if abs(X)<8 and abs(Y)<10:c=(45,36,50)
   if k==0:
    if abs(X)<5 and -7<Y<5:c=(194,141,69)
    if abs(X)<6 and -9<Y<-4:c=(239,190,78)
    if 1<abs(X)<4 and -2<Y<0:c=(255,240,151)
    if abs(X)<1 and 4<Y<8:c=(235,180,73)
   elif k in (1,2):
    sx=-1 if k==1 else 1
    if abs(X-sx*(2+.27*Y))<2.7 and -9<Y<7:c=(225,174,77)
    if abs(X-sx*3.0)<4 and 4<Y<9:c=(164,112,49)
    if -1<Y<2 and abs(X-sx*2)<4:c=(64,100,161)
   elif k in (3,4):
    sx=-1 if k==3 else 1
    if abs(X-sx*1.4)<3 and -9<Y<7:c=(223,172,73)
    if abs(X-sx*3)<5 and 5<Y<9:c=(237,190,86)
    if 0<Y<2 and abs(X-sx*1.4)<3.8:c=(58,88,154)
   elif (X/10)**2+(Y/6)**2<1:
    c=(245,194,74) if abs(X)>3 else (255,240,170) if abs(X)>1 else (75,43,29)
   if c:pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
 name='exodia_'+id
 png(assets/'textures/item'/f'{name}.png',W,H,pix)
 j(assets/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/'+name}})
for lang in ('it_it','en_us'):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['entity.noctismagic.exodia']='Exodia - Il Proibito' if lang=='it_it' else 'Exodia - The Forbidden One'
 for id,it,en in zip(['head','left_arm','right_arm','left_leg','right_leg'],['Testa','Braccio sinistro','Braccio destro','Gamba sinistra','Gamba destra'],['Head','Left Arm','Right Arm','Left Leg','Right Leg']):
  d['item.noctismagic.exodia_'+id]=('Exodia - '+it) if lang=='it_it' else ('Exodia - '+en)
 d['item.noctismagic.exodia_seal']='Sigillo del Proibito' if lang=='it_it' else 'Seal of the Forbidden One'
 d['item.noctismagic.exodia_fragment.tip']='Riunisci le cinque parti. Clic destro in un luogo aperto.' if lang=='it_it' else 'Collect all five pieces. Right-click in an open area.'
 j(p,d)
for p in (res/'data/forge/tags/entity_types/bosses.json',res/'data/noctismagic/tags/entity_types/vincent_protected.json'):
 d=json.loads(p.read_text()) if p.exists() else {'replace':False,'values':[]}
 if 'noctismagic:exodia' not in d['values']:d['values'].append('noctismagic:exodia')
 j(p,d)
print('Exodia: five rare loot fragments, safe summoning, three telegraphed attacks, 1500 HP and custom golden armor model.')
