"""Noctis 0.9.5: eclipse, Guts, Gabumon, and nocturnal Elvis."""
from pathlib import Path
import sys,json,struct,zlib,random,math,wave,array,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
def j(path,d):
    p=res/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
edit('Noctis.java',[
('public static final RegistryObject<EntityType<Shenron>> SHENRON=', '''public static final RegistryObject<EntityType<Guts>> GUTS=ENTITIES.register("guts",()->EntityType.Builder.<Guts>of(Guts::new,MobCategory.MISC).sized(.8f,2.1f).clientTrackingRange(10).build(ID+":guts"));
    public static final RegistryObject<EntityType<Gabumon>> GABUMON=ENTITIES.register("gabumon",()->EntityType.Builder.<Gabumon>of(Gabumon::new,MobCategory.CREATURE).sized(.8f,1.35f).clientTrackingRange(8).build(ID+":gabumon"));
    public static final RegistryObject<EntityType<Elvis>> ELVIS=ENTITIES.register("elvis",()->EntityType.Builder.<Elvis>of(Elvis::new,MobCategory.MONSTER).sized(.65f,1.95f).clientTrackingRange(8).build(ID+":elvis"));
    public static final RegistryObject<Item> GABUMON_EGG=ITEMS.register("gabumon_spawn_egg",()->new ForgeSpawnEggItem(GABUMON,0xd5d1ad,0x4068c5,new Item.Properties()));
    public static final RegistryObject<Item> ELVIS_EGG=ITEMS.register("elvis_spawn_egg",()->new ForgeSpawnEggItem(ELVIS,0xf4eedb,0xd9ab43,new Item.Properties()));
    public static final RegistryObject<EntityType<Shenron>> SHENRON='''),
('e.put(SHENRON.get(),Shenron.attributes().build());','e.put(GUTS.get(),Guts.attributes().build());e.put(GABUMON.get(),Gabumon.attributes().build());e.put(ELVIS.get(),Elvis.attributes().build());e.put(SHENRON.get(),Shenron.attributes().build());'),
('e.accept(VINCENT_EGG.get());','e.accept(GABUMON_EGG.get());e.accept(ELVIS_EGG.get());e.accept(VINCENT_EGG.get());')
])
edit('FallenEncounter.java',[
('static final RegistryObject<SoundEvent> THEME=','static final RegistryObject<SoundEvent> ELVIS_SONG=SOUNDS.register("elvis_song",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"elvis_song")));\n    static final RegistryObject<SoundEvent> THEME=')
])
write('Eclipse.java','''package it.noctis.magic;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.Difficulty;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.monster.*;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class Eclipse {
    static long day(Level l){return Math.floorDiv(l.getDayTime(),24000L);}
    public static boolean active(Level l){long d=day(l);return l.dimension()==Level.OVERWORLD&&d>0&&d%7==0&&Math.floorMod(l.getDayTime(),24000L)<6000L&&l.getDifficulty()!=Difficulty.PEACEFUL;}
    static boolean hostile(LivingEntity e){return e instanceof Enemy&&!(e instanceof Vampire.Friendly)&&!(e instanceof OneWinged)&&!(e instanceof NeutralMob);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.isSpectator()||!p.isAlive()||p.tickCount%20!=0)return;
        ServerLevel l=p.serverLevel();var data=Noctis.data(p);
        boolean active=active(l);
        if(!active){if(data.getBoolean("eclipseSeen")){data.putBoolean("eclipseSeen",false);if(l.dimension()==Level.OVERWORLD)p.sendSystemMessage(Component.literal("L'Eclissi e' finita. Il sole torna a splendere."));}return;}
        long day=day(l);
        if(!data.getBoolean("eclipseSeen")||data.getLong("eclipseDay")!=day){
            data.putBoolean("eclipseSeen",true);data.putLong("eclipseDay",day);
            p.sendSystemMessage(Component.literal("L'ECLISSI - Il sole viene divorato. Le creature delle tenebre si risvegliano.").withStyle(net.minecraft.ChatFormatting.DARK_RED));
            p.playSound(SoundEvents.WITHER_SPAWN,.75f,.6f);
        }
        if(p.isCreative())return;
        if(data.getLong("gutsDay")!=day){
            BlockPos q=spot(p,3,7);
            if(q!=null){Guts g=Noctis.GUTS.get().create(l);if(g!=null){g.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);g.tame(p);g.setEclipseDay(day);if(l.noCollision(g)&&l.addFreshEntity(g)){data.putLong("gutsDay",day);p.sendSystemMessage(Component.literal("Guts: Non stare fermo. Combatti."));}}}
        }
        if(p.tickCount%240!=0)return;
        int nearby=l.getEntitiesOfClass(Mob.class,p.getBoundingBox().inflate(48),m->m.getPersistentData().getBoolean("NoctisEclipseMob")).size();
        int count=Math.min(5,Math.max(0,20-nearby));
        EntityType<?>[] types={EntityType.HUSK,EntityType.SPIDER,EntityType.CREEPER,EntityType.STRAY,EntityType.VINDICATOR,EntityType.ZOMBIE,EntityType.SKELETON};
        for(int i=0;i<count;i++){
            BlockPos q=spot(p,12,30);if(q==null)continue;
            Entity ent=types[p.getRandom().nextInt(types.length)].create(l);
            if(!(ent instanceof Mob m))continue;
            m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);
            if(!l.noCollision(m))continue;
            boost(m,Attributes.MAX_HEALTH,2);boost(m,Attributes.ATTACK_DAMAGE,1.6);boost(m,Attributes.MOVEMENT_SPEED,1.2);
            m.setHealth(m.getMaxHealth());m.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE,6600,0,false,false));
            m.getPersistentData().putBoolean("NoctisEclipseMob",true);
            m.setTarget(p);
            if(l.addFreshEntity(m))l.sendParticles(ParticleTypes.SMOKE,m.getX(),m.getY()+.8,m.getZ(),12,.35,.6,.35,.03);
        }
    }
    static void boost(Mob m,Attribute a,double multiplier){AttributeInstance attr=m.getAttribute(a);if(attr!=null)attr.setBaseValue(attr.getBaseValue()*multiplier);}
    static BlockPos spot(ServerPlayer p,int min,int max){
        ServerLevel l=p.serverLevel();BlockPos center=p.blockPosition();
        for(int i=0;i<30;i++){
            double angle=p.getRandom().nextDouble()*Math.PI*2;int radius=min+p.getRandom().nextInt(max-min+1);
            int x=center.getX()+(int)Math.round(Math.cos(angle)*radius),z=center.getZ()+(int)Math.round(Math.sin(angle)*radius);
            BlockPos column=new BlockPos(x,center.getY(),z);if(!l.hasChunkAt(column))continue;
            int y=l.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
            if(Math.abs(y-center.getY())>12)continue;
            BlockPos q=new BlockPos(x,y,z);
            if(l.getWorldBorder().isWithinBounds(q)&&l.isEmptyBlock(q)&&l.isEmptyBlock(q.above())&&l.isEmptyBlock(q.above(2))&&l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))return q;
        }return null;
    }
}''')
write('Guts.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.animal.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
public class Guts extends TamableAnimal{
    private long eclipseDay=-1;private int swing=0;
    public Guts(EntityType<? extends TamableAnimal> t,Level l){super(t,l);setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,200).add(Attributes.ARMOR,16).add(Attributes.ATTACK_DAMAGE,36).add(Attributes.MOVEMENT_SPEED,.36).add(Attributes.FOLLOW_RANGE,36).add(Attributes.KNOCKBACK_RESISTANCE,.85);}
    public void setEclipseDay(long day){eclipseDay=day;}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.35,true));goalSelector.addGoal(2,new FollowOwnerGoal(this,1.2,7,3,false));goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));
        targetSelector.addGoal(1,new NearestAttackableTargetGoal<Mob>(this,Mob.class,5,true,false,e->Eclipse.hostile(e)&&getOwner()!=null&&e.distanceToSqr(getOwner())<1024));
    }
    @Override public boolean doHurtTarget(Entity e){
        if(!(e instanceof LivingEntity le)||!Eclipse.hostile(le))return false;
        boolean hit=super.doHurtTarget(e);
        if(hit&&level() instanceof ServerLevel l){
            l.broadcastEntityEvent(this,(byte)76);
            l.sendParticles(ParticleTypes.SWEEP_ATTACK,e.getX(),e.getY()+e.getBbHeight()*.6,e.getZ(),3,.5,.25,.5,0);
            l.sendParticles(ParticleTypes.CRIT,e.getX(),e.getY()+.8,e.getZ(),10,.4,.5,.4,.06);
            playSound(SoundEvents.PLAYER_ATTACK_SWEEP,1.3f,.55f);
            for(Mob other:l.getEntitiesOfClass(Mob.class,e.getBoundingBox().inflate(2),m->m!=e&&Eclipse.hostile(m)&&distanceToSqr(m)<25&&hasLineOfSight(m)))other.hurt(damageSources().mobAttack(this),18);
        }return hit;
    }
    @Override public void handleEntityEvent(byte id){if(id==76){swing=12;return;}super.handleEntityEvent(id);}
    public float swingPose(float partial){return swing<=0?0:(float)Math.sin(Math.PI*(1-Math.max(0,swing-partial)/12f));}
    @Override public void tick(){super.tick();if(swing>0)swing--;if(level() instanceof ServerLevel l){
        if(!Eclipse.active(l)||Eclipse.day(l)!=eclipseDay){l.sendParticles(ParticleTypes.SMOKE,getX(),getY()+1,getZ(),20,.35,.7,.35,.02);discard();return;}
        if(tickCount%100==0&&getHealth()<getMaxHealth())heal(3);
    }}
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float amount){if(source.getEntity() instanceof Player)return false;return super.hurt(source,amount);}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob p){return null;}
    @Override public boolean canMate(Animal a){return false;}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putLong("EclipseDay",eclipseDay);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);eclipseDay=t.getLong("EclipseDay");}
}''')
write('Gabumon.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.animal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.effect.*;
import net.minecraft.network.chat.Component;
public class Gabumon extends TamableAnimal {
    private int breath=0,attackCooldown=0;
    public Gabumon(EntityType<? extends TamableAnimal> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,60).add(Attributes.ATTACK_DAMAGE,11).add(Attributes.ARMOR,3).add(Attributes.MOVEMENT_SPEED,.3).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));goalSelector.addGoal(2,new MeleeAttackGoal(this,1.15,true));goalSelector.addGoal(3,new FollowOwnerGoal(this,1.1,6,2,false));goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.7));goalSelector.addGoal(5,new LookAtPlayerGoal(this,Player.class,8));
        targetSelector.addGoal(1,new OwnerHurtByTargetGoal(this));targetSelector.addGoal(2,new OwnerHurtTargetGoal(this));
    }
    @Override public boolean wantsToAttack(LivingEntity target,LivingEntity owner){return Eclipse.hostile(target);}
    @Override public boolean isFood(ItemStack s){return s.is(Items.COOKED_BEEF)||s.is(Items.COOKED_CHICKEN)||s.is(Items.COOKED_PORKCHOP);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        ItemStack s=p.getItemInHand(h);
        if(!isTame()&&isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);if(random.nextInt(3)==0){tame(p);setPersistenceRequired();setHealth(getMaxHealth());level().broadcastEntityEvent(this,(byte)7);p.sendSystemMessage(Component.literal("Gabumon: Da oggi siamo amici!"));}else level().broadcastEntityEvent(this,(byte)6);}return InteractionResult.sidedSuccess(level().isClientSide);}
        if(isTame()&&isOwnedBy(p)){if(isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);heal(8);}return InteractionResult.sidedSuccess(level().isClientSide);}if(s.isEmpty()){if(!level().isClientSide){setOrderedToSit(!isOrderedToSit());getNavigation().stop();setTarget(null);}return InteractionResult.sidedSuccess(level().isClientSide);}}
        return InteractionResult.PASS;
    }
    @Override public boolean doHurtTarget(Entity e){return e instanceof LivingEntity le&&Eclipse.hostile(le)&&super.doHurtTarget(e);}
    @Override public void tick(){super.tick();if(breath>0)breath--;if(attackCooldown>0)attackCooldown--;if(!(level() instanceof ServerLevel l)||!isTame()||isOrderedToSit())return;
        LivingEntity e=getTarget();if(e==null||!e.isAlive()||!Eclipse.hostile(e)||attackCooldown>0||distanceTo(e)>9||!hasLineOfSight(e))return;
        attackCooldown=100;l.broadcastEntityEvent(this,(byte)77);Vec3 start=getEyePosition(),end=e.getEyePosition();
        for(int i=0;i<16;i++){Vec3 v=start.lerp(end,i/15.0);l.sendParticles(ParticleTypes.SOUL_FIRE_FLAME,v.x,v.y,v.z,3,.12,.12,.12,.02);}
        e.hurt(damageSources().mobAttack(this),12);e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,50,0));playSound(SoundEvents.BLAZE_SHOOT,.7f,1.45f);
    }
    @Override public void handleEntityEvent(byte id){if(id==77){breath=20;return;}super.handleEntityEvent(id);}
    public float breathPose(float partial){return breath<=0?0:(float)Math.sin(Math.PI*(1-Math.max(0,breath-partial)/20f));}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob a){return null;}
    @Override public boolean canMate(Animal a){return false;}
}''')
write('Elvis.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Elvis extends Monster{
    private int cooldown=35,perform=0;
    public Elvis(EntityType<? extends Monster> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,45).add(Attributes.ATTACK_DAMAGE,7).add(Attributes.MOVEMENT_SPEED,.27).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SingGoal());goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.8));goalSelector.addGoal(4,new LookAtPlayerGoal(this,Player.class,10));targetSelector.addGoal(1,new NearestAttackableTargetGoal<Player>(this,Player.class,true));}
    @Override public void tick(){super.tick();if(perform>0)perform--;if(cooldown>0)cooldown--;if(level() instanceof ServerLevel l&&l.dimension()==Level.OVERWORLD&&l.isDay()){l.sendParticles(ParticleTypes.NOTE,getX(),getY()+1,getZ(),8,.3,.6,.3,0);discard();}}
    @Override public void handleEntityEvent(byte id){if(id==78){perform=40;return;}super.handleEntityEvent(id);}
    public float singing(){return perform>0?1:0;}
    class SingGoal extends Goal{
        SingGoal(){setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK));}
        @Override public boolean canUse(){return getTarget()!=null&&getTarget().isAlive();}
        @Override public boolean canContinueToUse(){return canUse();}
        @Override public void stop(){getNavigation().stop();}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        @Override public void tick(){
            if(!(level() instanceof ServerLevel l))return;LivingEntity t=getTarget();if(t==null)return;
            getLookControl().setLookAt(t,40,40);
            if(distanceTo(t)>10||!hasLineOfSight(t)){if(tickCount%5==0)getNavigation().moveTo(t,1.1);return;}
            getNavigation().stop();if(cooldown>0)return;cooldown=65;
            l.broadcastEntityEvent(Elvis.this,(byte)78);playSound(FallenEncounter.ELVIS_SONG.get(),1.2f,1);
            Vec3 a=getEyePosition(),b=t.getEyePosition();for(int i=1;i<=16;i++){Vec3 v=a.lerp(b,i/16.0);l.sendParticles(ParticleTypes.NOTE,v.x,v.y,v.z,1,0,0,0,1);l.sendParticles(ParticleTypes.SONIC_BOOM,v.x,v.y,v.z,i==8?1:0,0,0,0,0);}
            t.hurt(damageSources().mobAttack(Elvis.this),7);t.knockback(.7,getX()-t.getX(),getZ()-t.getZ());
            if(t instanceof Player p)p.displayClientMessage(Component.literal("Elvis: Rock'n'roll, baby!"),true);
        }
    }
}''')
write('NightGuests.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.*;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class NightGuests{
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.isSpectator()||p.tickCount%400!=0)return;
        ServerLevel l=p.serverLevel();if(l.dimension()!=Level.OVERWORLD)return;
        if(p.getRandom().nextInt(10)==0&&l.getEntitiesOfClass(Gabumon.class,p.getBoundingBox().inflate(60)).size()<2){
            BlockPos q=Eclipse.spot(p,8,20);if(q!=null){Gabumon g=Noctis.GABUMON.get().create(l);if(g!=null){g.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(g))l.addFreshEntity(g);}}
        }
        if(!l.isDay()&&l.getDifficulty()!=Difficulty.PEACEFUL&&p.getRandom().nextInt(5)==0&&l.getEntitiesOfClass(Elvis.class,p.getBoundingBox().inflate(48)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){Elvis v=Noctis.ELVIS.get().create(l);if(v!=null){v.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(v)){v.setTarget(p);l.addFreshEntity(v);}}}
        }
    }
}''')
write('EclipseVisuals.java','''package it.noctis.magic;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.world.level.material.FogType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
public class EclipseVisuals{
    static boolean active(){var l=Minecraft.getInstance().level;return l!=null&&Eclipse.active(l);}
    @SubscribeEvent public static void fog(ViewportEvent.ComputeFogColor e){if(active()&&e.getCamera().getFluidInCamera()==FogType.NONE){e.setRed(e.getRed()*.35f+.12f);e.setGreen(e.getGreen()*.12f+.025f);e.setBlue(e.getBlue()*.18f+.035f);}}
    static void v(BufferBuilder b,Matrix4f m,float x,float y,float z,int r,int g,int bl,int a){b.vertex(m,x,y,z).color(r,g,bl,a).endVertex();}
    @SubscribeEvent public static void sky(RenderLevelStageEvent e){
        if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_SKY||!active()||e.getCamera().getFluidInCamera()!=FogType.NONE)return;
        var level=Minecraft.getInstance().level;PoseStack pose=e.getPoseStack();pose.pushPose();
        RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.disableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);RenderSystem.setShaderColor(1,1,1,1);
        try{
            pose.mulPose(Axis.YP.rotationDegrees(-90));pose.mulPose(Axis.XP.rotationDegrees(level.getTimeOfDay(e.getPartialTick())*360));
            Matrix4f m=pose.last().pose();BufferBuilder b=Tesselator.getInstance().getBuilder();b.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);
            for(int i=0;i<64;i++){
                double a=i*Math.PI/32,c=(i+1)*Math.PI/32;float ax=(float)Math.cos(a),az=(float)Math.sin(a),cx=(float)Math.cos(c),cz=(float)Math.sin(c);
                v(b,m,0,99,0,8,3,10,255);v(b,m,ax*35,99,az*35,8,3,10,255);v(b,m,cx*35,99,cz*35,8,3,10,255);
                v(b,m,ax*35,99,az*35,255,105,51,255);v(b,m,cx*35,99,cz*35,255,105,51,255);v(b,m,cx*48,99,cz*48,156,9,22,0);
                v(b,m,ax*35,99,az*35,255,105,51,255);v(b,m,cx*48,99,cz*48,156,9,22,0);v(b,m,ax*48,99,az*48,156,9,22,0);
            }BufferUploader.drawWithShader(b.end());
        }finally{pose.popPose();RenderSystem.setShaderColor(1,1,1,1);RenderSystem.enableCull();RenderSystem.depthMask(true);RenderSystem.enableDepthTest();RenderSystem.disableBlend();}
    }
    @SubscribeEvent public static void hud(RenderGuiEvent.Post e){
        if(!active()||Minecraft.getInstance().options.hideGui)return;
        var g=e.getGuiGraphics();int w=Minecraft.getInstance().getWindow().getGuiScaledWidth();
        g.drawCenteredString(Minecraft.getInstance().font,"L'ECLISSI",w/2,39,0xE65A54);
    }
}''')
write('EclipseGuestsClient.java','''package it.noctis.magic;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class EclipseGuestsClient{
    static final ModelLayerLocation G=layer("guts"),B=layer("gabumon"),E=layer("elvis");
    static ModelLayerLocation layer(String n){return new ModelLayerLocation(new ResourceLocation(Noctis.ID,n),"main");}
    static ResourceLocation tex(String n){return new ResourceLocation(Noctis.ID,"textures/entity/"+n+".png");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(G,()->mesh(0));e.registerLayerDefinition(B,()->mesh(1));e.registerLayerDefinition(E,()->mesh(2));}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.GUTS.get(),GRenderer::new);e.registerEntityRenderer(Noctis.GABUMON.get(),BRenderer::new);e.registerEntityRenderer(Noctis.ELVIS.get(),ERenderer::new);}
    static CubeListBuilder c(int u,int v){return CubeListBuilder.create().texOffs(u,v);}
    static LayerDefinition mesh(int k){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot(),h=r.getChild("head"),b=r.getChild("body");r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        if(k==1){
            h.addOrReplaceChild("pelt",c(64,0).addBox(-4.5f,-9,-4.5f,9,2,9).texOffs(64,14).addBox(-4.5f,-7,3,9,10,2),PartPose.ZERO);
            h.addOrReplaceChild("muzzle",c(64,30).addBox(-3,-3,-7,6,4,4),PartPose.ZERO);
            h.addOrReplaceChild("horn",c(96,0).addBox(-1.3f,-5,-1.3f,2.6f,5,2.6f).texOffs(108,0).addBox(-.65f,-7,-.65f,1.3f,2,1.3f),PartPose.offsetAndRotation(0,-7,-2,-.25f,0,0));
            for(int s:new int[]{-1,1})h.addOrReplaceChild("ear"+s,c(96,14).addBox(-1.2f,-5,-1.2f,2.4f,5,2.4f),PartPose.offsetAndRotation(s*4,-6,1,0,0,s*.65f));
            b.addOrReplaceChild("tail",c(64,48).addBox(-1.3f,-1.3f,0,2.6f,2.6f,9),PartPose.offsetAndRotation(0,9,2,-.25f,0,0));
            b.addOrReplaceChild("belly",c(0,64).addBox(-3,-1,-2.7f,6,10,1.5f),PartPose.ZERO);
            for(String n:new String[]{"right_arm","left_arm","right_leg","left_leg"}){PartDefinition part=r.getChild(n);part.addOrReplaceChild("claws",c(96,40).addBox(-2,8,-3,4,2,2),PartPose.ZERO);}
        }else if(k==0){
            h.addOrReplaceChild("hair",c(64,0).addBox(-4.3f,-9,-4.3f,8.6f,2,8.6f),PartPose.ZERO);
            for(int i=0;i<5;i++)h.addOrReplaceChild("spike"+i,c(92,0).addBox(-.8f,-3,-.8f,1.6f,3,1.6f),PartPose.offsetAndRotation(-3+i*1.5f,-8,0,-.45f,0,(i-2)*.15f));
            b.addOrReplaceChild("armor",c(0,64).addBox(-4.8f,0,-3,9.6f,8,5.5f),PartPose.ZERO);
            b.addOrReplaceChild("cape",c(36,64).addBox(-5,0,0,10,20,1),PartPose.offsetAndRotation(0,1,3,-.12f,0,0));
            for(String n:new String[]{"right_arm","left_arm"}){PartDefinition a=r.getChild(n);a.addOrReplaceChild("shoulder",c(64,40).addBox(-3,-3,-2.8f,6,4,5.6f),PartPose.ZERO);a.addOrReplaceChild("bracer",c(64,54).addBox(-2.5f,4,-2.5f,5,7,5),PartPose.ZERO);}
            r.getChild("right_arm").addOrReplaceChild("dragonslayer",c(80,84).addBox(-2.5f,0,-.7f,5,30,1.4f).texOffs(96,84).addBox(-1.5f,30,-.7f,3,3,1.4f).texOffs(108,84).addBox(-4,-1,-1,8,1,2).texOffs(108,92).addBox(-.8f,-7,-.8f,1.6f,6,1.6f),PartPose.offsetAndRotation(-1,8,0,0,0,-.14f));
        }else{
            h.addOrReplaceChild("quiff",c(64,0).addBox(-4.5f,-10,-4.5f,9,3,9).texOffs(96,0).addBox(-4,-12,-4,8,3,5),PartPose.offsetAndRotation(0,0,0,-.1f,0,.05f));
            for(int s:new int[]{-1,1})h.addOrReplaceChild("sideburn"+s,c(96,14).addBox(-.5f,0,-1.5f,1,4,3),PartPose.offset(s*4,-5,-1));
            b.addOrReplaceChild("collar",c(0,64).addBox(-4.5f,-2,-2.5f,9,4,5),PartPose.ZERO);
            r.getChild("right_arm").addOrReplaceChild("mic",c(80,84).addBox(-.65f,-4,-.65f,1.3f,6,1.3f).texOffs(92,84).addBox(-1.1f,-6,-1.1f,2.2f,2,2.2f),PartPose.offsetAndRotation(-1,8,-1,0,0,.25f));
        }
        return LayerDefinition.create(m,128,128);
    }
    static class GM extends HumanoidModel<Guts>{
        final ModelPart cape;GM(ModelPart r){super(r);cape=body.getChild("cape");}
        @Override public void setupAnim(Guts e,float limb,float amount,float age,float yaw,float pitch){super.setupAnim(e,limb,amount,age,yaw,pitch);float s=e.swingPose(age-e.tickCount);rightArm.xRot=-.6f-s*1.65f;rightArm.zRot=-.17f-s*.95f;leftArm.xRot-=s*.65f;body.yRot=s*.55f;cape.xRot=-.15f-amount*.4f-s*.3f+(float)Math.sin(age*.16)*.07f;}
    }
    static class BM extends HumanoidModel<Gabumon>{
        final ModelPart tail;BM(ModelPart r){super(r);tail=body.getChild("tail");}
        @Override public void setupAnim(Gabumon e,float limb,float amount,float age,float yaw,float pitch){super.setupAnim(e,limb,amount,age,yaw,pitch);tail.yRot=(float)Math.sin(age*.19)*.35f;head.xRot-=e.breathPose(age-e.tickCount)*.35f;rightArm.zRot=.1f;leftArm.zRot=-.1f;if(e.isInSittingPose()){rightLeg.xRot=-1.25f;leftLeg.xRot=-1.25f;}}
    }
    static class EM extends HumanoidModel<Elvis>{
        EM(ModelPart r){super(r);}
        @Override public void setupAnim(Elvis e,float limb,float amount,float age,float yaw,float pitch){super.setupAnim(e,limb,amount,age,yaw,pitch);if(e.singing()>0){rightArm.xRot=-2.05f;rightArm.zRot=-.23f;leftArm.xRot=-.5f+(float)Math.sin(age*.3)*.4f;body.yRot=(float)Math.sin(age*.3)*.18f;head.zRot=(float)Math.sin(age*.3)*.1f;}else{body.yRot=0;head.zRot=0;}}
    }
    static class GRenderer extends MobRenderer<Guts,GM>{GRenderer(EntityRendererProvider.Context c){super(c,new GM(c.bakeLayer(G)),.5f);}@Override public ResourceLocation getTextureLocation(Guts e){return tex("guts");}@Override protected void scale(Guts e,com.mojang.blaze3d.vertex.PoseStack p,float f){p.scale(1.12f,1.12f,1.12f);}}
    static class BRenderer extends MobRenderer<Gabumon,BM>{BRenderer(EntityRendererProvider.Context c){super(c,new BM(c.bakeLayer(B)),.4f);}@Override public ResourceLocation getTextureLocation(Gabumon e){return tex("gabumon");}@Override protected void scale(Gabumon e,com.mojang.blaze3d.vertex.PoseStack p,float f){p.scale(.76f,.76f,.76f);}}
    static class ERenderer extends MobRenderer<Elvis,EM>{ERenderer(EntityRendererProvider.Context c){super(c,new EM(c.bakeLayer(E)),.45f);}@Override public ResourceLocation getTextureLocation(Elvis e){return tex("elvis");}}
}''')
def png(name,k):
    rng=random.Random(name)
    skin,hair,cloth,trim=[((198,155,124),(26,24,29),(39,40,49),(129,137,149)),((242,202,100),(225,225,208),(218,220,202),(45,89,174)),((218,168,130),(30,24,23),(238,231,212),(202,151,50))][k]
    pix=[[(*cloth,255) for x in range(128)] for y in range(128)]
    def R(x,y,w,h,col,noise=0):
        for yy in range(max(0,y),min(128,y+h)):
            for xx in range(max(0,x),min(128,x+w)):
                d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col[:3])+(col[3] if len(col)==4 else 255,)
    R(0,0,32,16,skin,5);R(32,0,32,16,(0,0,0,0));R(8,0,8,8,hair,5)
    for x in (0,16,24):R(x,8,8,8,hair,6)
    R(8,8,8,8,skin,3);R(8,8,8,1,hair)
    for x in (9,13):
        R(x,10,2,1,(54,34,31));R(x,11,2,1,(250,241,218));R(x+(1 if x==9 else 0),11,1,1,(28,21,26) if k!=1 else (171,38,40))
    R(11,14,2,1,(100,62,49));R(16,16,24,16,cloth,8);R(40,16,16,16,cloth,8);R(0,16,16,16,cloth,6);R(16,48,32,16,cloth,7)
    R(64,0,64,28,hair,7)
    if k==0:
        R(13,11,2,1,(87,45,43));R(0,64,35,20,(62,67,79),9);R(36,64,24,25,(23,25,32),5);R(64,40,28,32,(82,88,102),10)
        for x in range(3,30,5):R(x,67,2,8,trim,6)
        R(80,84,16,38,(153,159,170),10);R(82,86,1,32,(226,232,240));R(96,84,12,12,(179,184,195),8);R(108,84,16,18,(54,43,34),8)
    elif k==1:
        for y in range(16,64,6):
            R(0,y,16,2,trim,4);R(40,y,16,2,trim,5);R(16,y,16,2,trim,4)
        R(64,30,22,12,skin,7);R(69,34,2,1,(90,50,39));R(73,34,2,1,(90,50,39));R(96,0,22,14,(237,219,161),7)
        R(96,14,20,12,trim,6);R(64,48,24,13,cloth,6)
        for x in range(67,85,5):R(x,48,2,12,trim,5)
        R(0,64,20,14,skin,6);R(96,40,16,10,(232,229,217),5)
        for x in (65,76,86):R(x,3,3,20,trim,6)
        R(8,9,1,5,trim);R(15,9,1,5,trim)
    else:
        R(8,9,1,4,hair);R(15,9,1,4,hair);R(20,20,8,12,(238,230,208),4)
        for x,y in [(21,21),(26,21),(21,24),(26,24),(23,26),(24,28)]:R(x,y,1,1,trim)
        R(20,29,8,2,(174,134,47),5);R(0,64,30,13,cloth,4);R(80,84,24,12,(80,81,87),7);R(92,84,10,5,(179,184,190),7)
    def chunk(tag,b):return struct.pack('>I',len(b))+tag+b+struct.pack('>I',zlib.crc32(tag+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for px in row for v in px) for row in pix)
    (assets/'textures/entity'/f'{name}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,128,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
for k,n in enumerate(['guts','gabumon','elvis']):png(n,k)
for n in ['gabumon','elvis']:j(f'assets/noctismagic/models/item/{n}_spawn_egg.json',{"parent":"minecraft:item/template_spawn_egg"})
# Original rockabilly vocal-like melody, no sampled music or imitation of a specific recording.
rate=22050;length=2.4;pcm=array.array('h');phase=0
notes=[52,55,57,55,59,57,52,50]
for i in range(int(rate*length)):
    t=i/rate;n=min(7,int(t/.3));local=t-n*.3;f=440*2**((notes[n]-69)/12)*(1+.018*math.sin(t*37));phase+=2*math.pi*f/rate
    env=min(1,local/.035)*min(1,(.3-local)/.05)
    vocal=sum(math.sin(phase*h)*math.exp(-((f*h-(650 if n%2==0 else 420))/270)**2)/math.sqrt(h) for h in range(1,12))
    bass=math.sin(2*math.pi*(82.4 if n%2==0 else 110)*t)*math.exp(-local*10)
    click=math.sin(2*math.pi*180*t)*math.exp(-local*40)
    pcm.append(int(max(-.95,min(.95,.32*vocal*env+.13*bass+.055*click))*32767))
sounds=assets/'sounds';wav=sounds/'elvis_song.wav'
with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm.tobytes())
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(sounds/'elvis_song.ogg')],check=True);wav.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['elvis_song']={"sounds":[{"name":"noctismagic:elvis_song"}]};p.write_text(json.dumps(d),encoding='utf-8')
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
    for n,label in [('guts','Guts'),('gabumon','Gabumon'),('elvis','Elvis Presley')]:
        d['entity.noctismagic.'+n]=label
        if n!='guts':d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: '+label) if it else label+' Spawn Egg'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.9.5: eclipse, Guts, Gabumon and Elvis installed')
