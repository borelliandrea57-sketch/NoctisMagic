"""Metal Sonic: metallic loot, electrical retaliation, storms and amplified Neo form."""
from pathlib import Path
import sys
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic'
p=java/'SonicGuest.java';s=p.read_text(encoding='utf-8')
old='horizontal.normalize().scale(neo()?.27:.21)'
assert old in s
s=s.replace(old,'horizontal.normalize().scale(neo()?.52:.25)',1)
# The hover controller must not override the improved movement speed.
s=s.replace('Math.sin(angle)*.065,dy,Math.cos(angle)*.065','Math.sin(angle)*(neo()?.135:.065),dy,Math.cos(angle)*(neo()?.135:.065)',1)
p.write_text(s,encoding='utf-8')
(java/'MetalSonicStorm.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class MetalSonicStorm {
 private static final String BOOST="NoctisNeoStormStats",STRIKE="NoctisMetalStrikeAt",WEATHER="NoctisMetalStormAt";
 private static int form(LivingEntity e){
  ResourceLocation id=ForgeRegistries.ENTITY_TYPES.getKey(e.getType());
  if(id==null||!Noctis.ID.equals(id.getNamespace()))return 0;
  return id.getPath().equals("neo_metal_sonic")?2:id.getPath().equals("metal_sonic")?1:0;
 }
 private static void boost(LivingEntity e,Attribute attr,double min,double factor){
  AttributeInstance a=e.getAttribute(attr);
  if(a!=null)a.setBaseValue(Math.max(min,a.getBaseValue()*factor));
 }
 private static void ensureStats(LivingEntity e){
  if(form(e)!=2||e.getPersistentData().getBoolean(BOOST))return;
  float hp=e.getHealth(),oldMax=e.getMaxHealth();
  e.getPersistentData().putBoolean(BOOST,true);
  boost(e,Attributes.MAX_HEALTH,240,2.5);
  boost(e,Attributes.ATTACK_DAMAGE,22,2.2);
  boost(e,Attributes.MOVEMENT_SPEED,.46,1.65);
  boost(e,Attributes.ARMOR,14,1.6);
  boost(e,Attributes.KNOCKBACK_RESISTANCE,.70,1.0);
  e.setHealth(Math.min(e.getMaxHealth(),e.getMaxHealth()*hp/Math.max(1,oldMax)));
 }
 @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent event){
  LivingEntity e=event.getEntity();
  if(!(e instanceof SonicGuest)||!(e.level() instanceof ServerLevel l))return;
  int f=form(e);if(f==0)return;
  ensureStats(e);
  if(f==2&&e.tickCount%5==0){
   l.sendParticles(ParticleTypes.ELECTRIC_SPARK,e.getX(),e.getY()+1.0,e.getZ(),4,.46,.58,.46,.035);
  }
 }
 @SubscribeEvent public static void retaliation(LivingHurtEvent event){
  LivingEntity e=event.getEntity();
  if(!(e instanceof SonicGuest)||!(e.level() instanceof ServerLevel l))return;
  int f=form(e);if(f==0)return;
  ensureStats(e);
  if(event.getSource().is(DamageTypes.LIGHTNING_BOLT)){event.setAmount(0);return;}
  if(event.getAmount()<=0||!(event.getSource().getEntity() instanceof LivingEntity attacker)||attacker==e||!attacker.isAlive()||attacker.distanceTo(e)>24)return;
  if(attacker instanceof Player p&&(p.isCreative()||p.isSpectator()))return;
  if(form(attacker)>0)return;
  long now=l.getGameTime();
  if(now<e.getPersistentData().getLong(STRIKE))return;
  e.getPersistentData().putLong(STRIKE,now+(f==2?65:160));
  LightningBolt bolt=EntityType.LIGHTNING_BOLT.create(l);
  if(bolt!=null){bolt.moveTo(attacker.getX(),attacker.getY(),attacker.getZ());l.addFreshEntity(bolt);}
  if(f==2)attacker.hurt(l.damageSources().magic(),7);
  l.sendParticles(ParticleTypes.ELECTRIC_SPARK,e.getX(),e.getY()+1,e.getZ(),24,.5,.6,.5,.16);
  e.playSound(SoundEvents.LIGHTNING_BOLT_THUNDER,.6f,1.3f);
  if(l.dimension()==Level.OVERWORLD&&l.getGameRules().getBoolean(GameRules.RULE_WEATHER_CYCLE)&&now>=e.getPersistentData().getLong(WEATHER)){
   e.getPersistentData().putLong(WEATHER,now+1200);
   // Normal form summons rain; Neo always brings a thunderstorm.
   boolean thunder=f==2||e.getRandom().nextInt(3)==0;
   l.setWeatherParameters(0,thunder?4800:2400,true,thunder);
  }
 }
 private static void drop(LivingDropsEvent event,Item item,int count){
  if(count<=0)return;
  LivingEntity e=event.getEntity();
  ItemEntity entity=new ItemEntity(e.level(),e.getX(),e.getY()+.3,e.getZ(),new ItemStack(item,count));
  entity.setDefaultPickUpDelay();event.getDrops().add(entity);
 }
 @SubscribeEvent public static void loot(LivingDropsEvent event){
  LivingEntity e=event.getEntity();if(!(e instanceof SonicGuest))return;
  int f=form(e);if(f==0)return;
  int bonus=Math.max(0,Math.min(3,event.getLootingLevel()));
  drop(event,Items.IRON_INGOT,(f==2?10:4)+e.getRandom().nextInt(f==2?7:4)+bonus);
  drop(event,Items.COPPER_INGOT,(f==2?7:3)+e.getRandom().nextInt(5)+bonus);
  drop(event,Items.GOLD_INGOT,(f==2?3:1)+e.getRandom().nextInt(f==2?4:2));
  drop(event,Items.REDSTONE,(f==2?8:3)+e.getRandom().nextInt(5));
  if(f==2&&e.getRandom().nextInt(4)==0)drop(event,Items.NETHERITE_SCRAP,1);
 }
}''',encoding='utf-8')
print('Metal Sonic storm retaliation and metal loot; Neo improved health, armor, attack and hover velocity.')
