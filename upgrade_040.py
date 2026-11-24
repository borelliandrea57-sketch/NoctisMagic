"""Noctis Magic 0.4.0: vampire bonds, bat form, glowberry bushes and Nether amethyst."""
from pathlib import Path
import json,sys,struct,zlib,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(p,pairs):
    s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s: raise ValueError(f'Missing anchor {p.name}: {a[:100]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
def write(name,s): (java/name).write_text(s,encoding='utf-8')
def j(path,data):
    p=res/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
edit(root/'gradle.properties',[('mod_version=0.3.0','mod_version=0.4.0')])
edit(java/'Noctis.java',[
('ITEMS.register(bus);ENTITIES.register(bus);','ITEMS.register(bus);ENTITIES.register(bus);VampireLife.register(bus);'),
('Encounter.tick(p);CompoundTag d=data(p);','Encounter.tick(p);VampireLife.tick(p);CompoundTag d=data(p);'),
('if(id<0||id>=Spell.values().length','if(id==-1){VampireLife.toggleBat(p);return;}if(id<0||id>=Spell.values().length'),
('static void stopFlight(ServerPlayer p){CompoundTag d=data(p);','static void stopFlight(ServerPlayer p){CompoundTag d=data(p);if(d.getBoolean("batForm")){d.putInt("flight",0);return;}'),
('if(e.getEntity() instanceof ServerPlayer p){stopFlight(p);sync(p);}','if(e.getEntity() instanceof ServerPlayer p){VampireLife.leaveBat(p);stopFlight(p);sync(p);}'),
('if(e.getEntity() instanceof ServerPlayer p)stopFlight(p);if(e.getEntity() instanceof Monster','if(e.getEntity() instanceof ServerPlayer p){VampireLife.leaveBat(p);stopFlight(p);}if(e.getEntity() instanceof Monster'),
('if(e.getEntity() instanceof ServerPlayer p)stopFlight(p);}','if(e.getEntity() instanceof ServerPlayer p){VampireLife.leaveBat(p);stopFlight(p);}}'),
('copy.putInt("flight",0);','copy.putBoolean("batForm",false);copy.putBoolean("batGrantedFlight",false);copy.putBoolean("grantedFlight",false);copy.putInt("flight",0);'),
('e.accept(CRYSTAL.get());','e.accept(VampireLife.BLOOD.get());e.accept(VampireLife.ORE_ITEM.get());e.accept(CRYSTAL.get());'),
('if(e.getTabKey()==CreativeModeTabs.SPAWN_EGGS)','if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)e.accept(VampireLife.ORE_ITEM.get());if(e.getTabKey()==CreativeModeTabs.SPAWN_EGGS)'),
('if(!p.getAbilities().mayfly){d.putBoolean("grantedFlight",true);p.getAbilities().mayfly=true;}','if(!p.getAbilities().mayfly||d.getBoolean("batGrantedFlight")){d.putBoolean("grantedFlight",true);p.getAbilities().mayfly=true;}')
])
write('VampireLife.java','''package it.noctis.magic;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.animal.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.*;
import java.util.UUID;

@Mod.EventBusSubscriber(modid=Noctis.ID)
public class VampireLife {
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Noctis.ID);
    public static final DeferredRegister<MobEffect> EFFECTS=DeferredRegister.create(ForgeRegistries.MOB_EFFECTS,Noctis.ID);
    public static final RegistryObject<Block> BUSH=BLOCKS.register("glowberry_bush",GlowBush::new);
    public static final RegistryObject<Block> ORE=BLOCKS.register("nether_amethyst_ore",()->new Block(BlockBehaviour.Properties.copy(Blocks.NETHER_QUARTZ_ORE)));
    public static final RegistryObject<Item> ORE_ITEM=Noctis.ITEMS.register("nether_amethyst_ore",()->new BlockItem(ORE.get(),new Item.Properties()));
    public static final RegistryObject<Item> BLOOD=Noctis.ITEMS.register("blood_bucket",()->new Item(new Item.Properties().stacksTo(1)));
    public static final RegistryObject<MobEffect> VAMPIRISM=EFFECTS.register("vampirism",()->new MobEffect(MobEffectCategory.NEUTRAL,0x702335){});
    public static final RegistryObject<MobEffect> BAT=EFFECTS.register("bat_form",()->new MobEffect(MobEffectCategory.NEUTRAL,0x47334f){});
    private static final UUID SPEED=UUID.fromString("a001a7b0-3866-4d88-9a40-01971dfe0010"),POWER=UUID.fromString("a001a7b0-3866-4d88-9a40-01971dfe0011");
    public static void register(IEventBus bus){BLOCKS.register(bus);EFFECTS.register(bus);}
    public static boolean night(ServerPlayer p){return p.serverLevel().dimension()==Level.OVERWORLD&&!p.serverLevel().isDay();}
    public static boolean isVampire(ServerPlayer p){return Noctis.data(p).getBoolean("vampire");}
    static void marker(ServerPlayer p,MobEffect e){if(!p.hasEffect(e))p.addEffect(new MobEffectInstance(e,-1,0,false,false,false));}
    public static void turn(ServerPlayer p){
        if(isVampire(p))return;
        Noctis.data(p).putBoolean("vampire",true);marker(p,VAMPIRISM.get());
        p.serverLevel().sendParticles(ParticleTypes.HEART,p.getX(),p.getY()+1.5,p.getZ(),18,.5,.5,.5,.05);
        p.sendSystemMessage(Component.literal("Il patto di sangue e' compiuto. Di notte premi B per assumere la forma di pipistrello."));
    }
    static void attr(ServerPlayer p,Attribute type,UUID id,double amount,AttributeModifier.Operation op,boolean on){
        AttributeInstance a=p.getAttribute(type);if(a==null)return;
        if(on&&a.getModifier(id)==null)a.addTransientModifier(new AttributeModifier(id,"Noctis blood blessing",amount,op));
        if(!on&&a.getModifier(id)!=null)a.removeModifier(id);
    }
    static void tick(ServerPlayer p){
        boolean vampire=isVampire(p),night=vampire&&night(p);
        if(vampire)marker(p,VAMPIRISM.get());
        if(p.tickCount%10==0){
            attr(p,Attributes.MOVEMENT_SPEED,SPEED,.25,AttributeModifier.Operation.MULTIPLY_TOTAL,night);
            attr(p,Attributes.ATTACK_DAMAGE,POWER,3,AttributeModifier.Operation.ADDITION,night);
        }
        if(Noctis.data(p).getBoolean("batForm")){
            if(!night||p.isSpectator()||!p.isAlive()){leaveBat(p);return;}
            marker(p,BAT.get());p.resetFallDistance();
        }
    }
    static void toggleBat(ServerPlayer p){
        if(Noctis.data(p).getBoolean("batForm")){leaveBat(p);return;}
        if(!isVampire(p)||!night(p)||p.isSpectator()||!p.isAlive()){Noctis.tell(p,"La forma di pipistrello richiede il vampirismo e la notte.");return;}
        CompoundTag d=Noctis.data(p);d.putBoolean("batForm",true);
        d.putBoolean("batGrantedFlight",!p.getAbilities().mayfly||d.getBoolean("grantedFlight"));
        p.getAbilities().mayfly=true;p.getAbilities().flying=true;p.onUpdateAbilities();
        marker(p,BAT.get());p.resetFallDistance();Noctis.tell(p,"Forma di pipistrello attiva. B per tornare umano.");
    }
    static void leaveBat(ServerPlayer p){
        CompoundTag d=Noctis.data(p);
        if(d.getBoolean("batGrantedFlight")&&!p.isCreative()&&!p.isSpectator()&&d.getInt("flight")<=0){p.getAbilities().mayfly=false;p.getAbilities().flying=false;p.onUpdateAbilities();d.putBoolean("grantedFlight",false);}
        if(d.getBoolean("batForm")&&!p.onGround()&&p.isAlive())p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING,160,0,false,false));d.putBoolean("batForm",false);d.putBoolean("batGrantedFlight",false);p.removeEffect(BAT.get());p.resetFallDistance();
    }
    @SubscribeEvent public static void collect(LivingDeathEvent e){
        if(!(e.getSource().getEntity() instanceof ServerPlayer p))return;
        LivingEntity victim=e.getEntity();
        if(!(victim instanceof Cow||victim instanceof Sheep||victim instanceof Pig||victim instanceof net.minecraft.world.entity.animal.camel.Camel))return;
        for(InteractionHand h:InteractionHand.values()){ItemStack s=p.getItemInHand(h);if(!s.is(Items.BUCKET))continue;
            if(!p.getAbilities().instabuild)s.shrink(1);ItemStack filled=new ItemStack(BLOOD.get());
            if(s.isEmpty())p.setItemInHand(h,filled);else if(!p.getInventory().add(filled))p.drop(filled,false);
            Noctis.tell(p,"Hai raccolto un secchio di sangue.");break;
        }
    }
    @SubscribeEvent public static void plant(PlayerInteractEvent.RightClickBlock e){
        if(e.getFace()!=Direction.UP||!e.getItemStack().is(Items.GLOW_BERRIES))return;
        Level l=e.getLevel();BlockPos pos=e.getPos().above();PlayerGuard: {
            if(!l.isEmptyBlock(pos)||!BUSH.get().defaultBlockState().canSurvive(l,pos)||!e.getEntity().mayUseItemAt(pos,e.getFace(),e.getItemStack()))break PlayerGuard;
            if(l instanceof ServerLevel sl){l.setBlockAndUpdate(pos,BUSH.get().defaultBlockState());sl.scheduleTick(pos,BUSH.get(),2400);if(!e.getEntity().getAbilities().instabuild)e.getItemStack().shrink(1);}
            e.setCancellationResult(InteractionResult.sidedSuccess(l.isClientSide));e.setCanceled(true);
        }
    }
}''')
write('GlowBush.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.*;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;
public class GlowBush extends BushBlock {
    public static final BooleanProperty RIPE=BooleanProperty.create("ripe");
    public GlowBush(){super(BlockBehaviour.Properties.copy(Blocks.SWEET_BERRY_BUSH).lightLevel(s->s.getValue(RIPE)?9:0));registerDefaultState(stateDefinition.any().setValue(RIPE,false));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(RIPE);}
    @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return Block.box(2,0,2,14,13,14);}
    @Override public void tick(BlockState s,ServerLevel l,BlockPos p,RandomSource r){if(s.canSurvive(l,p)&&!s.getValue(RIPE))l.setBlockAndUpdate(p,s.setValue(RIPE,true));}
    @Override public void randomTick(BlockState s,ServerLevel l,BlockPos p,RandomSource r){}
    @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player player,InteractionHand h,BlockHitResult hit){
        if(!s.getValue(RIPE))return InteractionResult.PASS;
        if(l instanceof ServerLevel sl){popResource(l,p,new ItemStack(Items.GLOW_BERRIES,2+l.random.nextInt(3)));l.setBlockAndUpdate(p,s.setValue(RIPE,false));sl.scheduleTick(p,this,2400);}
        return InteractionResult.sidedSuccess(l.isClientSide);
    }
}''')
write('VampireSpacing.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class VampireSpacing extends SavedData {
    final Map<UUID,BlockPos> locations=new HashMap<>();
    static VampireSpacing load(CompoundTag t){
        VampireSpacing d=new VampireSpacing();ListTag list=t.getList("Visitors",10);
        for(int i=0;i<list.size();i++){CompoundTag n=list.getCompound(i);if(n.hasUUID("Id"))d.locations.put(n.getUUID("Id"),BlockPos.of(n.getLong("Pos")));}return d;
    }
    @Override public CompoundTag save(CompoundTag t){ListTag list=new ListTag();for(var e:locations.entrySet()){CompoundTag n=new CompoundTag();n.putUUID("Id",e.getKey());n.putLong("Pos",e.getValue().asLong());list.add(n);}t.put("Visitors",list);return t;}
    static VampireSpacing get(ServerLevel l){return l.getDataStorage().computeIfAbsent(VampireSpacing::load,VampireSpacing::new,"noctis_vampire_spacing");}
    static boolean available(ServerLevel l,BlockPos p,UUID except){for(var e:get(l).locations.entrySet()){if(e.getKey().equals(except))continue;long x=(long)e.getValue().getX()-p.getX(),z=(long)e.getValue().getZ()-p.getZ();if(x*x+z*z<1000000)return false;}return true;}
    static void track(Vampire.Friendly v){if(!(v.level() instanceof ServerLevel l))return;VampireSpacing d=get(l);BlockPos pos=v.blockPosition();BlockPos old=d.locations.get(v.getUUID());if(old==null||old.distSqr(pos)>16){d.locations.put(v.getUUID(),pos);d.setDirty();}}
    @SubscribeEvent public static void join(EntityJoinLevelEvent e){
        if(!(e.getLevel() instanceof ServerLevel l)||!(e.getEntity() instanceof Vampire.Friendly v))return;
        if(!e.loadedFromDisk()&&!available(l,v.blockPosition(),v.getUUID())){e.setCanceled(true);return;}track(v);
    }
    @SubscribeEvent public static void death(LivingDeathEvent e){if(e.getEntity() instanceof Vampire.Friendly v&&v.level() instanceof ServerLevel l){VampireSpacing d=get(l);d.locations.remove(v.getUUID());d.setDirty();}}
}''')
edit(java/'Encounter.java',[
('&&l.getEntitiesOfClass(Vampire.Friendly.class,p.getBoundingBox().inflate(40)).isEmpty())','&&VampireSpacing.available(l,p.blockPosition(),null))'),
('if(l.noCollision(v)){l.addFreshEntity(v);break;}','if(l.noCollision(v)&&VampireSpacing.available(l,pos,null)){v.setPersistenceRequired();if(l.addFreshEntity(v))break;}')])
edit(java/'Vampire.java',[
('private boolean gifted=false;','''private boolean gifted=false;
        private CompoundTag friendship=new CompoundTag();
        @Override protected net.minecraft.sounds.SoundEvent getAmbientSound(){return net.minecraft.sounds.SoundEvents.WANDERING_TRADER_AMBIENT;}
        @Override protected net.minecraft.sounds.SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource s){return net.minecraft.sounds.SoundEvents.VILLAGER_HURT;}
        @Override protected net.minecraft.sounds.SoundEvent getDeathSound(){return net.minecraft.sounds.SoundEvents.VILLAGER_DEATH;}
        @Override public boolean shouldDespawnInPeaceful(){return false;}
        private String friendKey(Player p){return p.getUUID().toString();}
        private void offer(net.minecraft.server.level.ServerPlayer p){p.sendSystemMessage(Component.literal("Vampiro: Ti considero ormai uno di noi. Vuoi diventare un vampiro? Shift + tasto destro a mano vuota per accettare; tasto destro normale per rifiutare."));}
        private boolean bond(Player player,ItemStack s){
            if(!(player instanceof net.minecraft.server.level.ServerPlayer p))return false;
            String key=friendKey(p);int points=friendship.getInt(key);
            if(s.is(VampireLife.BLOOD.get())){
                if(points>=10){if(!VampireLife.isVampire(p))offer(p);else p.sendSystemMessage(Component.literal("Vampiro: Il nostro legame e' eterno."));return true;}
                if(!p.getAbilities().instabuild){s.shrink(1);ItemStack bucket=new ItemStack(Items.BUCKET);if(!p.getInventory().add(bucket))p.drop(bucket,false);}
                friendship.putInt(key,++points);p.serverLevel().sendParticles(net.minecraft.core.particles.ParticleTypes.HEART,getX(),getY()+1.8,getZ(),8,.3,.4,.3,.03);
                playSound(net.minecraft.sounds.SoundEvents.VILLAGER_YES,.7f,.85f);
                p.sendSystemMessage(Component.literal("Vampiro: Un dono prezioso, grazie. Amicizia "+points+"/10"));
                if(points==10&&!VampireLife.isVampire(p)){friendship.putBoolean(key+"_offer",true);offer(p);}return true;
            }
            if(points>=10&&!VampireLife.isVampire(p)&&s.isEmpty()){
                if(p.isShiftKeyDown()){VampireLife.turn(p);friendship.putBoolean(key+"_offer",false);}
                else if(friendship.getBoolean(key+"_offer")){friendship.putBoolean(key+"_offer",false);p.sendSystemMessage(Component.literal("Vampiro: Come desideri. La nostra amicizia non cambia. Potrai ripensarci."));}
                else{friendship.putBoolean(key+"_offer",true);offer(p);}return true;
            }
            return false;
        }'''),
('return !l.getLevel().isDay()&&MonsterRules(t,l,reason,pos,r);','return !l.getLevel().isDay()&&VampireSpacing.available(l.getLevel(),pos,null)&&MonsterRules(t,l,reason,pos,r);'),
('if(!(level() instanceof net.minecraft.server.level.ServerLevel l))return;','if(!(level() instanceof net.minecraft.server.level.ServerLevel l))return;if(tickCount%100==0){setPersistenceRequired();VampireSpacing.track(this);}'),
('ItemStack s=p.getItemInHand(h);if(waitingDoor!=null','ItemStack s=p.getItemInHand(h);if(bond(p,s))return InteractionResult.CONSUME;if(waitingDoor!=null'),
('t.putBoolean("Gifted",gifted);','t.putBoolean("Gifted",gifted);t.put("Friendship",friendship.copy());'),
('gifted=t.getBoolean("Gifted");','gifted=t.getBoolean("Gifted");friendship=t.getCompound("Friendship");')
])
# Client: separate synced effect markers let other players also see fangs and bat form.
edit(java/'Client.java',[
('static int selected=0;','static final KeyMapping BAT_KEY=new KeyMapping("key.noctismagic.bat",InputConstants.Type.KEYSYM,GLFW.GLFW_KEY_B,"key.categories.noctismagic");\n    static int selected=0;'),
('e.register(MENU);e.register(CAST);','e.register(MENU);e.register(CAST);e.register(BAT_KEY);'),
('while(CAST.consumeClick())Noctis.NET.sendToServer(new Noctis.Cast(selected));','while(CAST.consumeClick())Noctis.NET.sendToServer(new Noctis.Cast(selected));while(BAT_KEY.consumeClick())Noctis.NET.sendToServer(new Noctis.Cast(-1));')
])
write('VampireVisuals.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ambient.Bat;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class VampireVisuals {
    static final ModelLayerLocation FANGS=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"fangs"),"main");
    static final ResourceLocation WHITE=new ResourceLocation(Noctis.ID,"textures/entity/fangs.png");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(FANGS,()->{
        MeshDefinition m=new MeshDefinition();m.getRoot().addOrReplaceChild("teeth",CubeListBuilder.create().texOffs(0,0).addBox(-2,-1.9f,-4.2f,.75f,1.5f,.45f).texOffs(4,0).addBox(1.25f,-1.9f,-4.2f,.75f,1.5f,.45f),PartPose.ZERO);return LayerDefinition.create(m,16,16);
    });}
    @SubscribeEvent public static void add(EntityRenderersEvent.AddLayers e){for(String name:e.getSkins()){PlayerRenderer renderer=e.getSkin(name);if(renderer!=null)renderer.addLayer(new Fangs(renderer,e.getEntityModels().bakeLayer(FANGS)));}}
    static class Fangs extends RenderLayer<AbstractClientPlayer,PlayerModel<AbstractClientPlayer>>{
        final ModelPart teeth;
        Fangs(PlayerRenderer r,ModelPart m){super(r);teeth=m;}
        @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,AbstractClientPlayer p,float limb,float amount,float partial,float age,float yaw,float pitch){
            if(!p.hasEffect(VampireLife.VAMPIRISM.get())||p.isInvisible())return;
            pose.pushPose();getParentModel().head.translateAndRotate(pose);teeth.render(pose,buffers.getBuffer(RenderType.entityCutoutNoCull(WHITE)),light,OverlayTexture.NO_OVERLAY);pose.popPose();
        }
    }
    @Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
    public static class Render {
        private static Bat previewBat;
        @SubscribeEvent public static void bat(RenderPlayerEvent.Pre e){
            if(!e.getEntity().hasEffect(VampireLife.BAT.get())||e.getEntity().isInvisible())return;
            if(previewBat==null||previewBat.level()!=e.getEntity().level())previewBat=EntityType.BAT.create(e.getEntity().level());Bat b=previewBat;if(b==null)return; b.setPos(e.getEntity().getX(),e.getEntity().getY(),e.getEntity().getZ());
            b.setResting(false);b.tickCount=e.getEntity().tickCount;b.setYRot(e.getEntity().getYRot());b.yRotO=b.getYRot();b.yBodyRot=b.getYRot();b.yBodyRotO=b.yBodyRot;
            b.setXRot(e.getEntity().getXRot());b.xRotO=b.getXRot();b.setYHeadRot(b.getYRot());
            e.setCanceled(true);e.getPoseStack().pushPose();e.getPoseStack().translate(0,.4,0);
            Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(b).render(b,b.getYRot(),e.getPartialTick(),e.getPoseStack(),e.getMultiBufferSource(),e.getPackedLight());e.getPoseStack().popPose();
        }
        @SubscribeEvent public static void hand(RenderHandEvent e){var p=Minecraft.getInstance().player;if(p!=null&&p.hasEffect(VampireLife.BAT.get()))e.setCanceled(true);}
    }
}''')
# Assets, loot and world generation.
def png(path,w,h,fn):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    data=b''.join(b'\0'+bytes(v for x in range(w) for v in fn(x,y)) for y in range(h))
    p=assets/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(data))+chunk(b'IEND',b''))
png('textures/entity/fangs.png',16,16,lambda x,y:(255,245,229,255))
def blood(x,y):
    if 3<=x<=12 and 5<=y<=13 and (y<11 or 5<=x<=10):
        if y in (5,6):return (142,20,40,255)
        if x in (3,12) or y==13:return (74,77,88,255)
        return (155+((x+y)%3)*13,160+((x+y)%3)*13,173+((x+y)%3)*10,255) if y>7 else (187,32,49,255)
    if y in (2,3,4) and (x in (4,11) or y==2 and 4<=x<=11):return (140,150,160,255)
    return (0,0,0,0)
png('textures/item/blood_bucket.png',16,16,blood)
rng=random.Random(24);ore=[]
for y in range(16):
    for x in range(16):
        d=rng.randint(-15,15);col=(100+d,39+d//2,45+d//2,255)
        for cx,cy in [(4,4),(12,6),(7,12),(1,10)]:
            if abs(x-cx)+abs(y-cy)<=2:col=(156+d,87+d,218+d,255) if x>=cx else (222+d,165+d,242,255)
        ore.append(col)
png('textures/block/nether_amethyst_ore.png',16,16,lambda x,y:ore[y*16+x])
def bush(x,y,ripe):
    berries=[(3,8),(7,4),(12,9),(8,12)]
    if ripe and any(abs(x-a)+abs(y-b)<=1 for a,b in berries):return (255,196,38,255) if (x+y)%2 else (255,237,130,255)
    if (abs(x-7)<=1 and y>3) or (y>5 and abs(x-7)<=max(2,6-abs(y-9)) and (x*3+y*7)%5!=0):
        return (44+(x+y)%3*14,115+(x*y)%4*17,42+(x+y)%4*8,255)
    return (0,0,0,0)
for ripe in (False,True):png('textures/block/glowberry_bush_'+str(ripe).lower()+'.png',16,16,lambda x,y,ripe=ripe:bush(x,y,ripe))
for name,col in [('vampirism',(190,32,57)),('bat_form',(103,69,149))]:
    png('textures/mob_effect/'+name+'.png',18,18,lambda x,y,col=col:(*col,255) if abs(x-8)+abs(y-8)<7 else (0,0,0,0))
j('assets/noctismagic/models/item/blood_bucket.json',{"parent":"minecraft:item/generated","textures":{"layer0":"noctismagic:item/blood_bucket"}})
j('assets/noctismagic/blockstates/nether_amethyst_ore.json',{"variants":{"":{"model":"noctismagic:block/nether_amethyst_ore"}}})
j('assets/noctismagic/models/block/nether_amethyst_ore.json',{"parent":"minecraft:block/cube_all","textures":{"all":"noctismagic:block/nether_amethyst_ore"}})
j('assets/noctismagic/models/item/nether_amethyst_ore.json',{"parent":"noctismagic:block/nether_amethyst_ore"})
j('assets/noctismagic/blockstates/glowberry_bush.json',{"variants":{f"ripe={b}":{"model":f"noctismagic:block/glowberry_bush_{b}"} for b in ["false","true"]}})
for b in ["false","true"]:j(f'assets/noctismagic/models/block/glowberry_bush_{b}.json',{"parent":"minecraft:block/cross","render_type":"minecraft:cutout","textures":{"cross":f"noctismagic:block/glowberry_bush_{b}"}})
j('data/noctismagic/loot_tables/blocks/glowberry_bush.json',{"type":"minecraft:block","pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":"minecraft:glow_berries"}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
j('data/noctismagic/loot_tables/blocks/nether_amethyst_ore.json',{"type":"minecraft:block","pools":[{"rolls":1,"entries":[{"type":"minecraft:alternatives","children":[{"type":"minecraft:item","name":"noctismagic:nether_amethyst_ore","conditions":[{"condition":"minecraft:match_tool","predicate":{"enchantments":[{"enchantment":"minecraft:silk_touch","levels":{"min":1}}]}}]},{"type":"minecraft:item","name":"minecraft:amethyst_shard","functions":[{"function":"minecraft:set_count","count":{"type":"minecraft:uniform","min":2,"max":4}},{"function":"minecraft:apply_bonus","enchantment":"minecraft:fortune","formula":"minecraft:ore_drops"},{"function":"minecraft:explosion_decay"}]}]}]}]})
j('data/minecraft/tags/blocks/mineable/pickaxe.json',{"replace":False,"values":["noctismagic:nether_amethyst_ore"]})
j('data/noctismagic/worldgen/configured_feature/nether_amethyst.json',{"type":"minecraft:ore","config":{"size":7,"discard_chance_on_air_exposure":0.0,"targets":[{"target":{"predicate_type":"minecraft:tag_match","tag":"minecraft:base_stone_nether"},"state":{"Name":"noctismagic:nether_amethyst_ore"}}]}})
j('data/noctismagic/worldgen/placed_feature/nether_amethyst.json',{"feature":"noctismagic:nether_amethyst","placement":[{"type":"minecraft:count","count":7},{"type":"minecraft:in_square"},{"type":"minecraft:height_range","height":{"type":"minecraft:uniform","min_inclusive":{"absolute":12},"max_inclusive":{"absolute":110}}},{"type":"minecraft:biome"}]})
j('data/noctismagic/forge/biome_modifier/nether_amethyst.json',{"type":"forge:add_features","biomes":"#minecraft:is_nether","features":"noctismagic:nether_amethyst","step":"underground_ores"})
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
    d.update({'item.noctismagic.blood_bucket':'Secchio di sangue' if it else 'Blood Bucket','block.noctismagic.glowberry_bush':'Cespuglio di bacche luminose' if it else 'Glowberry Bush','block.noctismagic.nether_amethyst_ore':'Minerale di ametista del Nether' if it else 'Nether Amethyst Ore','effect.noctismagic.vampirism':'Vampirismo' if it else 'Vampirism','effect.noctismagic.bat_form':'Forma di pipistrello' if it else 'Bat Form','key.noctismagic.bat':'Trasformazione in pipistrello' if it else 'Bat Transformation'})
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.4.0 source patch applied')
