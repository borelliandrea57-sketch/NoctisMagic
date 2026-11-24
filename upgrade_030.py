"""Apply Noctis Magic 0.3.0 additions to the original, compiled 0.2.0 source."""
from pathlib import Path
import sys, json, random, math, struct, zlib
root=Path(sys.argv[1])
java=root/'src/main/java/it/noctis/magic'
res=root/'src/main/resources'
assets=res/'assets/noctismagic'
def edit(p, pairs):
    s=p.read_text(encoding='utf-8')
    for old,new in pairs:
        if old not in s: raise ValueError(f'Missing patch anchor {p.name}: {old[:120]}')
        s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')
def write(name,s):
    (java/name).write_text(s,encoding='utf-8')
edit(root/'gradle.properties',[('mod_version=0.2.0','mod_version=0.3.0')])
edit(java/'Noctis.java',[
('public static final RegistryObject<EntityType<Tentacle>> TENTACLE=', '''public static final RegistryObject<EntityType<Angel>> ANGEL=ENTITIES.register("ophanim",()->EntityType.Builder.<Angel>of(Angel::new,MobCategory.MONSTER).sized(1.8f,1.8f).clientTrackingRange(12).build(ID+":ophanim"));
    public static final RegistryObject<EntityType<Demon>> DEMON=ENTITIES.register("demon",()->EntityType.Builder.<Demon>of(Demon::new,MobCategory.CREATURE).sized(.8f,2.2f).fireImmune().clientTrackingRange(8).build(ID+":demon"));
    public static final RegistryObject<Item> ANGEL_EGG=ITEMS.register("ophanim_spawn_egg",()->new ForgeSpawnEggItem(ANGEL,0xf0cd76,0xf9f6e9,new Item.Properties()));
    public static final RegistryObject<Item> DEMON_EGG=ITEMS.register("demon_spawn_egg",()->new ForgeSpawnEggItem(DEMON,0x35212d,0xf2a96b,new Item.Properties()));
    public static final RegistryObject<EntityType<Tentacle>> TENTACLE='''),
('ITEMS.register("cigarette",()->new Item(new Item.Properties()))','ITEMS.register("cigarette",SmokeItem::new)'),
('e.put(UMBREON.get(),Familiar.attributes(40,7).build());','e.put(ANGEL.get(),Angel.attributes().build());e.put(DEMON.get(),Demon.attributes().build());e.put(UMBREON.get(),Familiar.attributes(40,7).build());'),
('FRIENDLY.get(),SpawnPlacements.Type.ON_GROUND,net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,Monster::checkMonsterSpawnRules','FRIENDLY.get(),SpawnPlacements.Type.ON_GROUND,net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,Vampire.Friendly::canVisit'),
('e.accept(UMBREON_EGG.get());','e.accept(ANGEL_EGG.get());e.accept(DEMON_EGG.get());e.accept(UMBREON_EGG.get());'),
('CompoundTag d=data(p);for(String k:new String[]{"cooldown","shield","flight"})','Encounter.tick(p);CompoundTag d=data(p);for(String k:new String[]{"cooldown","shield","flight"})'),
('static void stopFlight(ServerPlayer p)', '''@SubscribeEvent public void invite(net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock e){
        if(!(e.getEntity() instanceof ServerPlayer p)||!(p.level().getBlockState(e.getPos()).getBlock() instanceof net.minecraft.world.level.block.DoorBlock))return;
        for(Vampire.Friendly v:p.serverLevel().getEntitiesOfClass(Vampire.Friendly.class,new AABB(e.getPos()).inflate(3)))if(v.inviteAt(p,e.getPos()))break;
    }
    static void stopFlight(ServerPlayer p)''')])
write('SmokeItem.java','''package it.noctis.magic;
import net.minecraft.world.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.effect.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
public class SmokeItem extends Item {
    public SmokeItem(){super(new Item.Properties().stacksTo(16));}
    @Override public UseAnim getUseAnimation(ItemStack s){return UseAnim.DRINK;}
    @Override public int getUseDuration(ItemStack s){return 48;}
    @Override public InteractionResultHolder<ItemStack> use(Level l,Player p,InteractionHand h){p.startUsingItem(h);return InteractionResultHolder.consume(p.getItemInHand(h));}
    @Override public ItemStack finishUsingItem(ItemStack s,Level l,LivingEntity e){
        if(l instanceof ServerLevel sl && e instanceof Player p){
            MobEffect[] effects={MobEffects.NIGHT_VISION,MobEffects.MOVEMENT_SPEED,MobEffects.REGENERATION,MobEffects.DAMAGE_RESISTANCE,MobEffects.DIG_SPEED,MobEffects.LUCK};
            MobEffect effect=effects[p.getRandom().nextInt(effects.length)];
            p.addEffect(new MobEffectInstance(effect, effect==MobEffects.REGENERATION?160:900,0));
            sl.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE,p.getX(),p.getEyeY(),p.getZ(),12,.13,.17,.13,.015);
            p.sendSystemMessage(Component.literal("Fumo incantato: ").append(Component.translatable(effect.getDescriptionId())));
            p.getCooldowns().addCooldown(this,200);
            if(!p.getAbilities().instabuild)s.shrink(1);
        }return s;
    }
}''')
write('Angel.java','''package it.noctis.magic;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.Vec3;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
public class Angel extends Monster {
    private int shot=40;
    public Angel(EntityType<? extends Monster> t,Level l){super(t,l);setNoGravity(true);}
    public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,65).add(Attributes.ATTACK_DAMAGE,8).add(Attributes.FOLLOW_RANGE,32).add(Attributes.MOVEMENT_SPEED,.3);}
    @Override public boolean causeFallDamage(float d,float m,net.minecraft.world.damagesource.DamageSource s){return false;}
    @Override public void tick(){super.tick();if(!(level() instanceof ServerLevel l))return;
        if(!l.isDay()||l.dimension()!=Level.OVERWORLD){l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+.8,getZ(),36,.8,.8,.8,.05);discard();return;}
        setNoGravity(true);Player p=l.getNearestPlayer(this,32);
        if(p!=null&&!p.isCreative()&&!p.isSpectator()&&p.isAlive()){
            Vec3 dest=p.position().add(0,5,0), diff=dest.subtract(position());
            Vec3 vel=diff.length()>1.2?diff.normalize().scale(.21):Vec3.ZERO;
            setDeltaMovement(getDeltaMovement().scale(.65).add(vel.scale(.35)));
            if(--shot<=0&&distanceTo(p)<18&&hasLineOfSight(p)){
                shot=55;Vec3 start=position().add(0,.9,0), end=p.getEyePosition();
                for(int i=0;i<=16;i++){Vec3 q=start.lerp(end,i/16.0);l.sendParticles(ParticleTypes.END_ROD,q.x,q.y,q.z,1,0,0,0,0);}
                p.hurt(damageSources().mobAttack(this),8);playSound(SoundEvents.BLAZE_SHOOT,.8f,1.5f);
            }
        }else setDeltaMovement(getDeltaMovement().scale(.85));
        if(tickCount%5==0)l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+.8,getZ(),3,.55,.55,.55,.01);
    }
}''')
write('Demon.java','''package it.noctis.magic;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
public class Demon extends PathfinderMob {
    private boolean gifted; private int dialogue;
    private static final String[] LINES={"Non giudicarmi dalle corna, mortale.","Il Nether non e' una prigione per tutti.","Ho conosciuto angeli molto meno gentili di me.","Se senti un ghast, resta vicino.","Le anime piu' luminose si incontrano nei luoghi piu' oscuri.","Porta i miei saluti al mondo di sopra."};
    public Demon(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,52).add(Attributes.MOVEMENT_SPEED,.30).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void registerGoals(){goalSelector.addGoal(1,new FloatGoal(this));goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,1));goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,10));goalSelector.addGoal(4,new RandomLookAroundGoal(this));}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){if(!level().isClientSide){
        if(!gifted){gifted=true;Item[] gifts={Items.GOLD_INGOT,Items.QUARTZ,Items.MAGMA_CREAM,Noctis.CRYSTAL.get()};ItemStack s=new ItemStack(gifts[random.nextInt(gifts.length)],2);if(!p.getInventory().add(s))p.drop(s,false);p.sendSystemMessage(Component.literal("Demone: Non temere. Accetta questo dono."));}
        else p.sendSystemMessage(Component.literal("Demone: "+LINES[(dialogue++)%LINES.length]));
    }return InteractionResult.sidedSuccess(level().isClientSide);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putBoolean("Gifted",gifted);t.putInt("Dialogue",dialogue);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);gifted=t.getBoolean("Gifted");dialogue=t.getInt("Dialogue");}
}''')
write('Encounter.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
public class Encounter {
    static void tick(ServerPlayer p){
        if(p.isSpectator()||p.tickCount%200!=0)return;
        ServerLevel l=p.serverLevel();
        if(l.dimension()==Level.OVERWORLD&&l.isDay()&&p.getRandom().nextInt(3)==0&&l.getEntitiesOfClass(Angel.class,p.getBoundingBox().inflate(64)).isEmpty()){
            if(l.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL)return;
            int x=p.getBlockX()+p.getRandom().nextInt(31)-15,z=p.getBlockZ()+p.getRandom().nextInt(31)-15;
            BlockPos ground=l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING,xz(x,z));
            BlockPos pos=new BlockPos(x,Math.max(ground.getY()+12,p.getBlockY()+10),z);
            if(pos.getY()<l.getMaxBuildHeight()-3&&l.hasChunkAt(pos)&&l.canSeeSky(pos)){
                Angel a=Noctis.ANGEL.get().create(l);if(a!=null){a.moveTo(x+.5,pos.getY(),z+.5);if(l.noCollision(a))l.addFreshEntity(a);}
            }
        }
        if(l.dimension()==Level.NETHER&&p.getRandom().nextInt(3)==0&&l.getEntitiesOfClass(Demon.class,p.getBoundingBox().inflate(48)).size()<2){
            for(int i=0;i<12;i++){int x=p.getBlockX()+p.getRandom().nextInt(35)-17,z=p.getBlockZ()+p.getRandom().nextInt(35)-17;
                BlockPos pos=new BlockPos(x,p.getBlockY()+p.getRandom().nextInt(13)-6,z);
                if(!l.hasChunkAt(pos)||!l.getBlockState(pos.below()).isFaceSturdy(l,pos.below(),Direction.UP)||!l.getFluidState(pos).isEmpty()||!l.getBlockState(pos).isAir()||!l.getBlockState(pos.above()).isAir())continue;
                Demon d=Noctis.DEMON.get().create(l);if(d!=null){d.moveTo(x+.5,pos.getY(),z+.5);if(l.noCollision(d)){l.addFreshEntity(d);break;}}
            }
        }
    }
    static BlockPos xz(int x,int z){return new BlockPos(x,0,z);}
}''')
edit(java/'Familiar.java',[
('tame(p);setPersistenceRequired();setHealth(getMaxHealth());level().broadcastEntityEvent(this,(byte)7);','tame(p);setPersistenceRequired();setHealth(getMaxHealth());level().broadcastEntityEvent(this,(byte)7);if(octopus())p.sendSystemMessage(net.minecraft.network.chat.Component.literal("SirPiovra: Incantato, mio caro! Da oggi siamo soci."));'),
('if(isFood(s)&&getHealth()<getMaxHealth())','if(octopus()&&s.isEmpty()&&p.isShiftKeyDown()){String[] lines={"Permettetemi di presentarmi: SirPiovra, al vostro servizio.","Il frac e\\u0027 impeccabile, naturalmente.","Un pesce per il pensiero, mio caro?","Otto tentacoli e una sola parola: eleganza."};p.sendSystemMessage(net.minecraft.network.chat.Component.literal("SirPiovra: "+lines[random.nextInt(lines.length)]));}else if(isFood(s)&&getHealth()<getMaxHealth())'),
('return super.mobInteract(p,h);','if(octopus()&&s.isEmpty()){if(!level().isClientSide)p.sendSystemMessage(net.minecraft.network.chat.Component.literal("SirPiovra: Mi chiamo SirPiovra. Gradirei del merluzzo o del salmone crudo."));return InteractionResult.sidedSuccess(level().isClientSide);}return super.mobInteract(p,h);'),
('if(eternal()){\\n','if(eternal()){\\n') if False else ('if(getHealth()<getMaxHealth())setHealth(getMaxHealth());clearFire();','if(getHealth()<getMaxHealth())setHealth(getMaxHealth());clearFire();if(getType()==Noctis.FROST_FAMILIAR.get()&&tickCount%5==0&&level() instanceof ServerLevel l)l.sendParticles(net.minecraft.core.particles.ParticleTypes.SNOWFLAKE,getX(),getY()+.6,getZ(),5,.32,.45,.32,.02);')
])
edit(java/'Vampire.java',[
('private boolean gifted=false;', '''private boolean gifted=false;
        private net.minecraft.core.BlockPos waitingDoor;
        private java.util.UUID guest;
        private int invitedTicks=0;
        private boolean asked=false;
        public static boolean canVisit(EntityType<Friendly> t,net.minecraft.world.level.ServerLevelAccessor l,MobSpawnType reason,net.minecraft.core.BlockPos pos,net.minecraft.util.RandomSource r){
            return !l.getLevel().isDay()&&MonsterRules(t,l,reason,pos,r);
        }
        private static boolean MonsterRules(EntityType<Friendly> t,net.minecraft.world.level.ServerLevelAccessor l,MobSpawnType reason,net.minecraft.core.BlockPos pos,net.minecraft.util.RandomSource r){
            return net.minecraft.world.entity.monster.Monster.checkMonsterSpawnRules(t,l,reason,pos,r);
        }
        public boolean inviteAt(Player p,net.minecraft.core.BlockPos pos){
            if(waitingDoor==null||waitingDoor.distSqr(pos)>2||guest==null||!guest.equals(p.getUUID()))return false;
            waitingDoor=null;invitedTicks=400;asked=false;p.sendSystemMessage(Component.literal("Vampiro: Vi ringrazio dell'invito. Permesso!"));return true;
        }
        @Override public void tick(){super.tick();if(!(level() instanceof net.minecraft.server.level.ServerLevel l))return;
            if(invitedTicks>0){invitedTicks--;Player p=guest==null?null:l.getPlayerByUUID(guest);if(p!=null&&tickCount%10==0&&distanceTo(p)>2)getNavigation().moveTo(p,1.0);return;}
            if(l.isDay()){waitingDoor=null;asked=false;return;}
            if(tickCount%40!=0)return;
            Player p=l.getNearestPlayer(this,20);if(p==null||p.isSpectator())return;
            if(waitingDoor==null){
                net.minecraft.core.BlockPos center=p.blockPosition(),best=null;double dist=Double.MAX_VALUE;
                for(net.minecraft.core.BlockPos q:net.minecraft.core.BlockPos.betweenClosed(center.offset(-6,-2,-6),center.offset(6,2,6))){
                    var s=l.getBlockState(q);if(s.getBlock() instanceof net.minecraft.world.level.block.DoorBlock&&s.getValue(net.minecraft.world.level.block.DoorBlock.HALF)==net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER){
                        double d=q.distSqr(blockPosition());if(d<dist){dist=d;best=q.immutable();}}
                }
                if(best!=null){waitingDoor=best;guest=p.getUUID();asked=false;}
            }
            if(waitingDoor!=null){
                if(!(l.getBlockState(waitingDoor).getBlock() instanceof net.minecraft.world.level.block.DoorBlock)){waitingDoor=null;return;}
                if(waitingDoor.distSqr(blockPosition())>5){
                    net.minecraft.core.BlockPos best=null;double dist=Double.MAX_VALUE;
                    for(net.minecraft.core.Direction dir:net.minecraft.core.Direction.Plane.HORIZONTAL){
                        var q=waitingDoor.relative(dir);if(!l.getBlockState(q).isAir()||!l.getBlockState(q.above()).isAir())continue;
                        double d=q.distSqr(blockPosition());if(d<dist){dist=d;best=q;}}
                    if(best!=null)getNavigation().moveTo(best.getX()+.5,best.getY(),best.getZ()+.5,1.05);
                }else{getNavigation().stop();if(!asked){asked=true;p.sendSystemMessage(Component.literal("Vampiro: Buonasera... posso entrare? Aprite la porta, se lo desiderate."));}}
            }
        }'''),
('ItemStack s=p.getItemInHand(h);if(!gifted)','ItemStack s=p.getItemInHand(h);if(waitingDoor!=null&&inviteAt(p,waitingDoor))return InteractionResult.CONSUME;if(!gifted)')
])
# Geometry: keep animated base rig, add individual silhouettes and accessories.
edit(java/'Client.java',[
('IMP=layer("imp"),VAMPIRE','IMP=layer("imp"),DEVIL=layer("devil"),FROST=layer("frost"),NIGHT=layer("night"),ANGEL=layer("ophanim"),DEMON=layer("demon"),VAMPIRE'),
('e.registerLayerDefinition(IMP,()->ShapeModel.mesh(3));','e.registerLayerDefinition(IMP,()->ShapeModel.mesh(3));e.registerLayerDefinition(DEVIL,()->ShapeModel.mesh(4));e.registerLayerDefinition(FROST,()->ShapeModel.mesh(5));e.registerLayerDefinition(NIGHT,()->ShapeModel.mesh(6));e.registerLayerDefinition(ANGEL,()->ShapeModel.mesh(7));e.registerLayerDefinition(DEMON,Client::demonMesh);'),
('new FamiliarRenderer(c,IMP,"devil")','new FamiliarRenderer(c,DEVIL,"devil")'),
('new FamiliarRenderer(c,IMP,"night_familiar")','new FamiliarRenderer(c,NIGHT,"night_familiar")'),
('new FamiliarRenderer(c,IMP,"frost_familiar")','new FamiliarRenderer(c,FROST,"frost_familiar")'),
('e.registerEntityRenderer(Noctis.TENTACLE.get()','e.registerEntityRenderer(Noctis.ANGEL.get(),AngelRenderer::new);e.registerEntityRenderer(Noctis.DEMON.get(),DemonRenderer::new);e.registerEntityRenderer(Noctis.TENTACLE.get()'),
('l==OCTOPUS?1:l==IMP?3:0','l==OCTOPUS?1:l==IMP?3:l==DEVIL?4:l==FROST?5:l==NIGHT?6:0'),
('static class TentacleRenderer', '''static class AngelRenderer extends MobRenderer<Angel,ShapeModel<Angel>>{
        AngelRenderer(EntityRendererProvider.Context c){super(c,new ShapeModel<>(c.bakeLayer(ANGEL),7),.0f);}
        @Override public ResourceLocation getTextureLocation(Angel e){return tex("ophanim");}
    }
    static class DemonRenderer extends MobRenderer<Demon,HumanoidModel<Demon>>{
        DemonRenderer(EntityRendererProvider.Context c){super(c,new HumanoidModel<>(c.bakeLayer(DEMON)),.5f);}
        @Override public ResourceLocation getTextureLocation(Demon e){return tex("demon");}
    }
    static LayerDefinition demonMesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);
        PartDefinition h=m.getRoot().getChild("head"),b=m.getRoot().getChild("body");
        for(int s:new int[]{-1,1}){
            h.addOrReplaceChild("horn"+s,CubeListBuilder.create().texOffs(64,0).addBox(-1.5f,-5,-1.5f,3,5,3).texOffs(78,0).addBox(-1,-8,0,2,4,2),PartPose.offsetAndRotation(s*3,-6,0,-.25f,0,s*.38f));
            b.addOrReplaceChild("bat"+s,CubeListBuilder.create().texOffs(64,32).addBox(s<0?-10:0,-2,0,10,9,1).texOffs(88,32).addBox(s<0?-13:0,-3,0,13,2,1),PartPose.offsetAndRotation(s*3,2,2,0,s*.55f,0));
        }
        b.addOrReplaceChild("tail",CubeListBuilder.create().texOffs(96,0).addBox(-1,0,0,2,2,10).texOffs(96,14).addBox(-1,-4,8,2,5,2),PartPose.offsetAndRotation(0,10,2,-.3f,0,.2f));
        return LayerDefinition.create(m,128,64);
    }
    static class TentacleRenderer'''),
('for(int i=0;i<8;i++){double a=i*Math.PI/4;','''PartDefinition body=r.getChild("body");
                body.addOrReplaceChild("hat",CubeListBuilder.create().texOffs(56,28).addBox(-5,-13,-5,10,1,10).texOffs(76,0).addBox(-3.5f,-18,-3.5f,7,5,7).texOffs(76,16).addBox(-4,-14,-4,8,1,8),PartPose.ZERO);
                body.addOrReplaceChild("monocle",CubeListBuilder.create().texOffs(106,0).addBox(1,-8,-6.3f,4,1,.5f).texOffs(106,0).addBox(1,-5,-6.3f,4,1,.5f).texOffs(106,0).addBox(1,-7,-6.3f,1,2,.5f).texOffs(106,0).addBox(4,-7,-6.3f,1,2,.5f).texOffs(106,0).addBox(4,-4,-6.3f,.5f,4,.5f),PartPose.ZERO);
                body.addOrReplaceChild("bowtie",CubeListBuilder.create().texOffs(112,16).addBox(-3,-3,-6.4f,6,2,.8f),PartPose.ZERO);
                for(int i=0;i<8;i++){double a=i*Math.PI/4;'''),
('}else{\\n                r.addOrReplaceChild("body",CubeListBuilder.create().texOffs(0,0).addBox(-3,-7,-2,6,7,4)', '''}else if(k==7){
                r.addOrReplaceChild("body",CubeListBuilder.create().texOffs(0,0).addBox(-4,-4,-4,8,8,8),PartPose.offset(0,12,0));
                for(int ring=0;ring<3;ring++){
                    PartDefinition band=r.addOrReplaceChild("ring"+ring,CubeListBuilder.create(),PartPose.offsetAndRotation(0,12,0,ring==1?1.05f:0,ring==2?1.05f:0,ring==0?.3f:ring==1?-.5f:1.0f));
                    for(int i=0;i<12;i++){float a=(float)(i*Math.PI/6);float rad=9+ring*2;
                        PartDefinition seg=band.addOrReplaceChild("seg"+i,CubeListBuilder.create().texOffs(40,0).addBox(-2.9f,-1.3f,-1.3f,5.8f,2.6f,2.6f).texOffs(64,0).addBox(-1.5f,-1.8f,-2.1f,3,3,1),PartPose.offsetAndRotation((float)Math.sin(a)*rad,(float)Math.cos(a)*rad,0,0,0,-a));
                    }
                }
            }else{
                r.addOrReplaceChild("body",CubeListBuilder.create().texOffs(0,0).addBox(-3,-7,-2,6,7,4)'''.replace('\\n','\n')),
('return LayerDefinition.create(mesh,128,64);','''if(k>=3&&k<=6){
                PartDefinition head=r.getChild("head"),body=r.getChild("body");
                if(k==3){
                    for(int s:new int[]{-1,1})head.addOrReplaceChild("flamehorn"+s,CubeListBuilder.create().texOffs(96,0).addBox(-1,-4,-1,2,4,2).texOffs(96,8).addBox(-.5f,-6,-.5f,1,3,1),PartPose.offsetAndRotation(s*3,-8,0,0,0,s*.3f));
                    body.addOrReplaceChild("ember",CubeListBuilder.create().texOffs(96,24).addBox(-1.5f,-5,-2.3f,3,3,.7f),PartPose.ZERO);
                }else if(k==4){
                    for(int s:new int[]{-1,1}){
                        head.addOrReplaceChild("devilhorn"+s,CubeListBuilder.create().texOffs(96,0).addBox(-1.6f,-5,-1.6f,3,5,3).texOffs(96,10).addBox(-1,-9,0,2,5,2),PartPose.offsetAndRotation(s*3,-7,0,-.3f,0,s*.5f));
                        r.getChild("wing"+(s<0?0:1)).addOrReplaceChild("blade",CubeListBuilder.create().texOffs(96,32).addBox(s<0?-11:0,-3,0,11,2,1).texOffs(96,40).addBox(s<0?-9:5,0,0,4,5,1),PartPose.ZERO);
                    }
                    body.addOrReplaceChild("armor",CubeListBuilder.create().texOffs(96,24).addBox(-4,-6,-2.7f,8,3,1).texOffs(96,24).addBox(-2,-3,-2.7f,4,3,1),PartPose.ZERO);
                }else if(k==5){
                    for(int i=0;i<5;i++)head.addOrReplaceChild("ice"+i,CubeListBuilder.create().texOffs(96,0).addBox(-1.3f,-5-(i%2)*2,-1.3f,2.6f,5+(i%2)*2,2.6f).texOffs(96,12).addBox(-.6f,-7-(i%2)*2,-.6f,1.2f,2,1.2f),PartPose.offsetAndRotation(-4+i*2,-6,0,.15f,0,(i-2)*.22f));
                    for(int s:new int[]{-1,1})r.getChild("wing"+(s<0?0:1)).addOrReplaceChild("shard",CubeListBuilder.create().texOffs(96,32).addBox(s<0?-10:0,-6,0,10,2,1).texOffs(96,40).addBox(s<0?-8:5,-4,0,3,9,1),PartPose.ZERO);
                    body.addOrReplaceChild("gem",CubeListBuilder.create().texOffs(96,24).addBox(-2,-5,-2.6f,4,4,1),PartPose.offsetAndRotation(0,-1,0,0,0,.65f));
                }else{
                    head.addOrReplaceChild("hood",CubeListBuilder.create().texOffs(96,0).addBox(-5,-8,-4,10,3,8).texOffs(96,12).addBox(-5,-5,1,10,6,3),PartPose.ZERO);
                    body.addOrReplaceChild("rune",CubeListBuilder.create().texOffs(96,24).addBox(-2,-5,-2.5f,4,4,1),PartPose.ZERO);
                }
            }
            return LayerDefinition.create(mesh,128,64);'''),
('else if(kind==3){','else if(kind==7){for(int i=0;i<3;i++){ModelPart ring=root.getChild("ring"+i);ring.xRot=(float)(age*.045*(i+1)+i*.8);ring.yRot=(float)(age*.025*(i%2==0?1:-1));ring.zRot=(float)(age*.03+i*.9);}}\\n            else if(kind>=3&&kind<=6){'.replace('\\n','\n'))
])
# Draw detailed block-style texture atlases without nonstandard dependencies.
def png(name,pix):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(c for p in row for c in (*p,255)) for row in pix)
    path=assets/'textures/entity'/f'{name}.png'
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,64,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
def atlas(name,base,trim,bright,dark,mode):
    rng=random.Random(name)
    pix=[[base for x in range(128)] for y in range(64)]
    def rect(x,y,w,h,col,noise=0):
        for yy in range(max(0,y),min(64,y+h)):
            for xx in range(max(0,x),min(128,x+w)):
                d=rng.randint(-noise,noise)
                pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col)
    def box(x,y,w,d,h,col,edge):
        rect(x+d,y,w,d,col,10);rect(x+d+w,y,w,d,edge,9)
        for xx,ww,shade in [(x,d,edge),(x+d,w,col),(x+d+w,d,edge),(x+2*d+w,w,col)]:
            rect(xx,y+d,ww,h,shade,12);rect(xx,y+d,ww,1,trim,7)
    rect(0,0,128,64,base,12)
    if mode=='pet':
        box(0,0,6,4,7,base,dark);box(0,16,8,6,6,base,dark)
        rect(6,23,8,1,dark);rect(7,24,2,2,bright);rect(11,24,2,2,bright);rect(8,27,4,1,dark);rect(8,27,1,1,(249,238,214));rect(11,27,1,1,(249,238,214))
        rect(4,5,6,2,trim);rect(6,7,2,3,bright);rect(4,10,6,1,trim)
        rect(32,16,12,12,trim,13);rect(42,16,12,8,base,10)
        rect(40,40,25,12,dark,12);rect(40,43,24,1,trim);rect(48,46,1,5,trim);rect(57,46,1,5,trim);rect(60,40,22,5,trim,10)
        rect(80,0,16,20,base,12);rect(96,0,32,23,trim,10);rect(96,24,24,8,bright,8);rect(96,32,32,26,trim,12)
        if name=='frost_familiar':
            for i in range(25):
                x=rng.randrange(96,126);y=rng.randrange(1,60);rect(x,y,1,2,bright,3)
            rect(7,24,2,2,(236,255,255));rect(11,24,2,2,(236,255,255))
        if name=='devil':
            rect(6,22,3,1,dark);rect(11,22,3,1,dark);rect(7,23,2,1,bright);rect(11,23,2,1,bright);rect(7,26,6,1,dark)
    elif mode=='octo':
        box(0,0,12,12,10,base,dark);rect(12,12,12,10,(48,36,54),8);rect(13,12,10,5,base,10)
        rect(14,14,2,2,(248,236,197));rect(20,14,2,2,(248,236,197));rect(15,14,1,1,dark);rect(21,14,1,1,dark)
        rect(17,17,2,4,(232,226,214));rect(16,17,1,2,trim);rect(19,17,1,2,trim);rect(17,18,2,1,(128,28,53))
        box(0,28,3,7,3,dark,base);box(24,28,2,5,2,dark,base)
        for x in range(8,23,3):rect(x,37,1,1,bright)
        rect(56,28,28,21,dark,5);rect(76,0,30,25,dark,7);rect(76,16,31,8,trim,6);rect(106,0,12,12,trim,8);rect(112,16,15,8,(156,34,52),5)
    elif mode=='angel':
        rect(0,0,34,26,trim,12);rect(8,8,8,8,(246,237,208));rect(10,10,4,4,(65,36,24));rect(11,11,2,2,(12,9,18));rect(11,10,1,1,(255,255,255))
        rect(40,0,23,11,trim,10);rect(42,3,6,2,bright);rect(64,0,13,9,(244,241,216),5);rect(65,1,3,3,(239,181,78));rect(66,2,1,1,(20,15,32));rect(66,1,1,1,(255,255,255))
    else:
        rect(0,0,32,16,base,11);rect(8,8,8,8,base,7);rect(9,10,2,1,bright);rect(13,10,2,1,bright);rect(10,13,4,1,dark);rect(10,13,1,1,(245,230,211));rect(13,13,1,1,(245,230,211))
        rect(16,16,24,16,dark,9);rect(20,20,8,8,base,9);rect(22,20,4,8,trim,10);rect(40,16,16,16,base,10);rect(0,16,16,16,dark,8);rect(16,48,32,16,base,8);rect(64,0,32,24,dark,10);rect(64,32,40,22,(93,31,49),12);rect(96,0,32,24,base,10)
    png(name,pix)
atlas('imp',(155,64,42),(224,117,40),(255,214,99),(67,29,32),'pet')
atlas('devil',(105,31,53),(202,80,77),(255,188,91),(34,17,34),'pet')
atlas('frost_familiar',(82,156,210),(132,219,244),(231,255,255),(32,68,122),'pet')
atlas('night_familiar',(56,42,92),(111,71,159),(205,151,255),(19,16,40),'pet')
atlas('octopus',(133,80,141),(217,179,83),(228,155,179),(31,24,43),'octo')
atlas('ophanim',(171,125,47),(215,169,63),(255,241,177),(80,54,24),'angel')
atlas('demon',(124,57,63),(188,92,61),(255,203,100),(38,26,39),'demon')
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for id,name in [('ophanim','Ofan - Ruota celeste' if lang=='it_it' else 'Ophanim - Celestial Wheel'),('demon','Demone del Nether' if lang=='it_it' else 'Nether Demon')]:
        d['entity.noctismagic.'+id]=name;d['item.noctismagic.'+id+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+name
    d['entity.noctismagic.octopus']='SirPiovra';d['item.noctismagic.octopus_spawn_egg']='Uovo generatore: SirPiovra' if lang=='it_it' else 'SirPiovra Spawn Egg'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
for id in ['ophanim','demon']:
    (assets/'models/item'/f'{id}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}',encoding='utf-8')
print('Noctis 0.3.0 source patch applied')
