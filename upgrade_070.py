"""Noctis Magic 0.7.0: chat-triggered miracle and comedic lightning."""
from pathlib import Path
import sys,json,struct,zlib,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(path,pairs):
    s=path.read_text(encoding='utf-8')
    for old,new in pairs:
        if old not in s:raise ValueError(f'Missing anchor {path.name}: {old[:100]}')
        s=s.replace(old,new,1)
    path.write_text(s,encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
def j(path,data):
    p=res/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
edit(root/'gradle.properties',[('mod_version=0.6.0','mod_version=0.7.0')])
edit(java/'Noctis.java',[
('public static final RegistryObject<EntityType<Sora>> SORA=', '''public static final RegistryObject<EntityType<MiracleVisitor>> JESUS=ENTITIES.register("jesus",()->EntityType.Builder.<MiracleVisitor>of(MiracleVisitor::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(8).build(ID+":jesus"));
    public static final RegistryObject<EntityType<Sora>> SORA='''),
('VampireLife.register(bus);','VampireLife.register(bus);MiracleLiquid.register(bus);'),
('e.put(SORA.get(),Sora.attributes().build());','e.put(JESUS.get(),MiracleVisitor.attributes().build());e.put(SORA.get(),Sora.attributes().build());'),
('e.accept(VampireLife.BLOOD.get());','e.accept(VampireLife.BLOOD.get());e.accept(MiracleLiquid.BUCKET.get());')
])
write('MiracleLiquid.java','''package it.noctis.magic;
import java.util.function.Consumer;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.*;
import net.minecraftforge.client.extensions.common.IClientFluidTypeExtensions;
import net.minecraftforge.common.SoundActions;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fluids.*;
import net.minecraftforge.registries.*;
public class MiracleLiquid {
    static final DeferredRegister<FluidType> TYPES=DeferredRegister.create(ForgeRegistries.Keys.FLUID_TYPES,Noctis.ID);
    static final DeferredRegister<Fluid> FLUIDS=DeferredRegister.create(ForgeRegistries.FLUIDS,Noctis.ID);
    static final RegistryObject<FluidType> TYPE=TYPES.register("miracle_liquid",()->new FluidType(FluidType.Properties.create().density(1050).viscosity(1100).canConvertToSource(false).sound(SoundActions.BUCKET_FILL,SoundEvents.BUCKET_FILL).sound(SoundActions.BUCKET_EMPTY,SoundEvents.BUCKET_EMPTY)){
        @Override public void initializeClient(Consumer<IClientFluidTypeExtensions> c){
            c.accept(new IClientFluidTypeExtensions(){
                @Override public ResourceLocation getStillTexture(){return new ResourceLocation("minecraft","block/water_still");}
                @Override public ResourceLocation getFlowingTexture(){return new ResourceLocation("minecraft","block/water_flow");}
                @Override public int getTintColor(){return 0xFFAC39D4;}
            });
        }
    });
    static final RegistryObject<FlowingFluid> SOURCE=FLUIDS.register("miracle_liquid",()->new ForgeFlowingFluid.Source(properties()){
        @Override public void tick(Level l,BlockPos p,FluidState s){}
    });
    static final RegistryObject<FlowingFluid> FLOWING=FLUIDS.register("flowing_miracle_liquid",()->new ForgeFlowingFluid.Flowing(properties()){
        @Override public void tick(Level l,BlockPos p,FluidState s){}
    });
    static final RegistryObject<LiquidBlock> BLOCK=VampireLife.BLOCKS.register("miracle_liquid",()->new LiquidBlock(SOURCE,BlockBehaviour.Properties.copy(Blocks.WATER)));
    static final RegistryObject<Item> BUCKET=Noctis.ITEMS.register("miracle_liquid_bucket",()->new BucketItem(SOURCE,new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));
    static ForgeFlowingFluid.Properties properties(){return new ForgeFlowingFluid.Properties(TYPE,SOURCE,FLOWING).bucket(BUCKET).block(BLOCK);}
    static void register(IEventBus bus){TYPES.register(bus);FLUIDS.register(bus);}
}''')
write('MiracleEncounter.java','''package it.noctis.magic;
import java.text.Normalizer;
import java.util.Locale;
import java.util.regex.Pattern;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.event.ServerChatEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class MiracleEncounter {
    static final Pattern CURSE=Pattern.compile("(?:^| )(?:porco (?:dio|gesu)|(?:dio|gesu) (?:cane|porco|maiale|merda|bastardo|stronzo)|(?:dio|gesu) di merda|porca madonna|madonna (?:puttana|troia))(?: |$)");
    static String normalize(String s){return Normalizer.normalize(s,Normalizer.Form.NFD).replaceAll("\\\\p{M}+","").toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+"," ").trim();}
    @SubscribeEvent public static void chat(ServerChatEvent e){
        ServerPlayer p=e.getPlayer();if(p.isSpectator()||!p.isAlive())return;
        ServerLevel l=p.serverLevel();String s=normalize(e.getRawText());long now=l.getGameTime();var d=Noctis.data(p);
        if(s.equals("gesu aiutami")){
            if(d.contains("miracleAt")&&now-d.getLong("miracleAt")<1200){p.sendSystemMessage(Component.literal("Gesu: Nu poco 'e pacienza, figlio mio."));return;}
            if(!l.getEntitiesOfClass(MiracleVisitor.class,p.getBoundingBox().inflate(12)).isEmpty())return;
            BlockPos origin=p.blockPosition();
            for(int i=0;i<40;i++){
                BlockPos q=origin.offset(p.getRandom().nextInt(9)-4,p.getRandom().nextInt(5)-2,p.getRandom().nextInt(9)-4);
                if(q.distSqr(origin)<4||!l.hasChunkAt(q)||!l.isEmptyBlock(q)||!l.isEmptyBlock(q.above())||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))continue;
                MiracleVisitor v=Noctis.JESUS.get().create(l);if(v==null)return;
                v.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,p.getYRot()+180,0);v.setRecipient(p);
                if(!l.noCollision(v)||!l.addFreshEntity(v))continue;
                d.putLong("miracleAt",now);l.sendParticles(ParticleTypes.END_ROD,v.getX(),v.getY()+1,v.getZ(),55,.6,1,.6,.04);
                p.sendSystemMessage(Component.literal("Gesu: Eccomi, figlio mio. Mo ce penzo io."));return;
            }
            p.sendSystemMessage(Component.literal("Gesu: Fammi nu poco 'e spazio, e richiamami."));return;
        }
        if(!CURSE.matcher(s).find())return;
        if(d.contains("smiteAt")&&now-d.getLong("smiteAt")<200)return;
        d.putLong("smiteAt",now);
        LightningBolt bolt=EntityType.LIGHTNING_BOLT.create(l);
        if(bolt!=null){bolt.moveTo(p.getX(),p.getY(),p.getZ());bolt.setVisualOnly(true);l.addFreshEntity(bolt);}
        if(!p.isCreative())p.hurt(p.damageSources().lightningBolt(),Math.min(6f,Math.max(0f,p.getHealth()-1f)));
        String[] lines={"Ue, ma si' scemo? Tieni 'stu fulmine!","Mannaggia a te, impara a parlare!","Ma che sfaccimma staje dicenno?","Mo te faccio arrivare 'a bolletta d''a luce!"};
        p.sendSystemMessage(Component.literal("Gesu: "+lines[p.getRandom().nextInt(lines.length)]));
    }
    static int changeWater(ServerPlayer p){
        ServerLevel l=p.serverLevel();BlockPos center=p.blockPosition();int n=0;
        for(BlockPos q:BlockPos.betweenClosed(center.offset(-5,-3,-5),center.offset(5,3,5))){
            if(n>=64)break;
            if(l.hasChunkAt(q)&&l.getBlockState(q).is(Blocks.WATER)&&l.getFluidState(q).isSource()){
                l.setBlockAndUpdate(q,MiracleLiquid.BLOCK.get().defaultBlockState());n++;
                l.sendParticles(ParticleTypes.WITCH,q.getX()+.5,q.getY()+.7,q.getZ()+.5,4,.3,.2,.3,.01);
            }
        }return n;
    }
}''')
write('MiracleVisitor.java','''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
public class MiracleVisitor extends PathfinderMob {
    private UUID recipient;
    private int visit=0;
    public MiracleVisitor(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,40).add(Attributes.MOVEMENT_SPEED,.26).add(Attributes.FOLLOW_RANGE,20);}
    public void setRecipient(ServerPlayer p){recipient=p.getUUID();}
    @Override protected void registerGoals(){}
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource d,float a){return false;}
    @Override public void tick(){super.tick();if(!(level() instanceof ServerLevel l))return;
        ServerPlayer p=recipient==null?null:l.getServer().getPlayerList().getPlayer(recipient);visit++;
        if(p!=null&&p.level()==l){
            getLookControl().setLookAt(p,30,30);
            if(visit<35&&distanceTo(p)>2.2&&visit%5==0)getNavigation().moveTo(p,.8);
            if(visit==35){getNavigation().stop();int n=MiracleEncounter.changeWater(p);
                ItemStack bread=new ItemStack(Items.BREAD,8),fish=new ItemStack(Items.COOKED_COD,8);
                if(!p.getInventory().add(bread))p.drop(bread,false);if(!p.getInventory().add(fish))p.drop(fish,false);
                p.sendSystemMessage(Component.literal(n>0?"Gesu: L'acqua s'e fatta viola. Tieni pane e pesce, e statte buono.":"Gesu: Acqua nun ne veco, ma pane e pesce nun te mancano."));
                playSound(SoundEvents.NOTE_BLOCK_CHIME.value(),1,1);
            }
        }
        if(visit%8==0)l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+1.2,getZ(),3,.35,.7,.35,.01);
        if(visit>=105){l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+1,getZ(),60,.7,1,.7,.06);discard();}
    }
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);if(recipient!=null)n.putUUID("Recipient",recipient);n.putInt("Visit",visit);}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);if(n.hasUUID("Recipient"))recipient=n.getUUID("Recipient");visit=n.getInt("Visit");}
}''')
write('MiracleClient.java','''package it.noctis.magic;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class MiracleClient {
    static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"jesus"),"main");
    static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/jesus.png");
    @SubscribeEvent public static void init(FMLClientSetupEvent e){e.enqueueWork(()->{ItemBlockRenderTypes.setRenderLayer(MiracleLiquid.SOURCE.get(),RenderType.translucent());ItemBlockRenderTypes.setRenderLayer(MiracleLiquid.FLOWING.get(),RenderType.translucent());});}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(LAYER,MiracleClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.JESUS.get(),Renderer::new);}
    static LayerDefinition mesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot(),h=r.getChild("head"),b=r.getChild("body");
        h.addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.4f,-8.7f,-4.3f,8.8f,2.5f,8.6f).texOffs(64,14).addBox(-4,-7,3,8,12,2),PartPose.ZERO);
        for(int s:new int[]{-1,1})h.addOrReplaceChild("lock"+s,CubeListBuilder.create().texOffs(96,0).addBox(-1,-1,-1,2,10,3),PartPose.offset(s*4,-6,1));
        h.addOrReplaceChild("beard",CubeListBuilder.create().texOffs(96,16).addBox(-3,-1.9f,-4.25f,6,3,1.4f),PartPose.ZERO);
        b.addOrReplaceChild("robe",CubeListBuilder.create().texOffs(0,64).addBox(-4.5f,10,-2.7f,9,10,5.4f),PartPose.ZERO);
        return LayerDefinition.create(m,128,128);
    }
    static class Renderer extends MobRenderer<MiracleVisitor,HumanoidModel<MiracleVisitor>>{
        Renderer(EntityRendererProvider.Context c){super(c,new HumanoidModel<>(c.bakeLayer(LAYER)),.45f);}
        @Override public ResourceLocation getTextureLocation(MiracleVisitor e){return TEX;}
    }
}''')
def png(path,w,h,fn):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for x in range(w) for v in fn(x,y)) for y in range(h))
    p=assets/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
rng=random.Random(707);pix=[[(235,225,206,255) for x in range(128)] for y in range(128)]
def rect(x,y,w,h,col,noise=0):
    for yy in range(max(0,y),min(128,y+h)):
        for xx in range(max(0,x),min(128,x+w)):
            d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col)+(255,)
rect(0,0,32,16,(175,124,85),8);rect(8,8,8,8,(213,163,117),5)
rect(8,8,8,1,(101,59,33));rect(9,10,2,1,(245,239,220));rect(13,10,2,1,(245,239,220));rect(10,10,1,1,(60,38,25));rect(13,10,1,1,(60,38,25));rect(10,13,4,2,(111,67,39))
rect(16,16,24,16,(239,230,212),7)
for y in range(20,32):rect(20+(y-20)//3,y,3,1,(161,49,52),5)
rect(20,28,8,1,(155,111,65));rect(40,16,16,16,(231,222,204),7);rect(44,27,4,5,(213,163,117),5)
rect(0,16,16,16,(216,206,185),7);rect(16,48,32,16,(227,217,196),7);rect(4,29,8,3,(114,77,48),5)
rect(64,0,48,38,(100,62,36),10)
for x in range(65,112,4):rect(x,0,1,31,(140,87,48),6)
rect(96,16,18,8,(107,62,35),7);rect(0,64,32,20,(236,225,205),8)
for x in range(3,32,6):rect(x,70,1,13,(211,200,179),5)
png('textures/entity/jesus.png',128,128,lambda x,y:pix[y][x])
def bucket(x,y):
    if y in (3,4) and (x in (4,11) or y==3 and 4<=x<=11):return (155,166,178,255)
    if 3<=x<=12 and 5<=y<=13 and (y<11 or 5<=x<=10):
        if y<=7:return (170,54,212,255) if (x+y)%3 else (225,136,250,255)
        if x in (3,12) or y==13:return (76,81,94,255)
        return (156+(x%3)*20,163+(x%3)*20,176+(x%3)*20,255)
    return (0,0,0,0)
png('textures/item/miracle_liquid_bucket.png',16,16,bucket)
j('assets/noctismagic/models/item/miracle_liquid_bucket.json',{"parent":"minecraft:item/generated","textures":{"layer0":"noctismagic:item/miracle_liquid_bucket"}})
j('assets/noctismagic/blockstates/miracle_liquid.json',{"variants":{"":{"model":"noctismagic:block/miracle_liquid"}}})
j('assets/noctismagic/models/block/miracle_liquid.json',{"textures":{"particle":"minecraft:block/water_still"}})
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
    d.update({'entity.noctismagic.jesus':'Gesù' if it else 'Jesus','item.noctismagic.miracle_liquid_bucket':'Secchio di liquido miracoloso' if it else 'Miracle Liquid Bucket','block.noctismagic.miracle_liquid':'Liquido miracoloso' if it else 'Miracle Liquid','fluid_type.noctismagic.miracle_liquid':'Liquido miracoloso' if it else 'Miracle Liquid'})
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.7.0 source patch applied')
