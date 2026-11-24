"""Noctis Magic 0.6.0: Sora's secret encounter."""
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
edit(root/'gradle.properties',[('mod_version=0.5.0','mod_version=0.6.0')])
edit(java/'Noctis.java',[
('public static final RegistryObject<EntityType<OneWinged>> FALLEN=', '''public static final RegistryObject<EntityType<Sora>> SORA=ENTITIES.register("sora",()->EntityType.Builder.<Sora>of(Sora::new,MobCategory.CREATURE).sized(.65f,1.8f).clientTrackingRange(8).build(ID+":sora"));
    public static final RegistryObject<EntityType<OneWinged>> FALLEN='''),
('e.put(FALLEN.get(),OneWinged.attributes().build());','e.put(SORA.get(),Sora.attributes().build());e.put(FALLEN.get(),OneWinged.attributes().build());')
])
write('Sora.java','''package it.noctis.magic;
import net.minecraft.network.chat.Component;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.nbt.CompoundTag;
public class Sora extends PathfinderMob {
    public static final String LINE="sta oscurita ha rutt u cazz";
    private int farewell=2400;
    public Sora(EntityType<? extends PathfinderMob> type,Level level){super(type,level);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,40).add(Attributes.MOVEMENT_SPEED,.3).add(Attributes.FOLLOW_RANGE,20);}
    @Override protected void registerGoals(){goalSelector.addGoal(1,new FloatGoal(this));goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,12));goalSelector.addGoal(4,new RandomLookAroundGoal(this));}
    public void speak(Player p){p.sendSystemMessage(Component.literal("Sora: "+LINE));playSound(SoundEvents.NOTE_BLOCK_CHIME.value(),.7f,1.3f);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){if(!level().isClientSide)speak(p);return InteractionResult.sidedSuccess(level().isClientSide);}
    @Override public void tick(){super.tick();if(level() instanceof ServerLevel l){
        if(tickCount%10==0)l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+1,getZ(),2,.35,.65,.35,.02);
        if(--farewell<=0){l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+.8,getZ(),45,.5,.7,.5,.08);discard();}
    }}
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);n.putInt("Farewell",farewell);}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);if(n.contains("Farewell"))farewell=n.getInt("Farewell");}
}''')
write('SoraEncounter.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class SoraEncounter {
    static boolean matches(SignText t){StringBuilder b=new StringBuilder();for(Component line:t.getMessages(false)){String s=line.getString().trim();if(!s.isEmpty()){if(b.length()>0)b.append(" ");b.append(s);}}return b.toString().equalsIgnoreCase("Kingdom Hearts");}
    static boolean spawn(ServerPlayer p,BlockPos origin){
        ServerLevel l=p.serverLevel();
        for(int i=0;i<24;i++){
            BlockPos q=origin.offset(p.getRandom().nextInt(13)-6,p.getRandom().nextInt(5)-2,p.getRandom().nextInt(13)-6);
            if(q.distSqr(p.blockPosition())<9||!l.hasChunkAt(q)||!l.isEmptyBlock(q)||!l.isEmptyBlock(q.above())||!l.getFluidState(q).isEmpty()||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))continue;
            Sora s=Noctis.SORA.get().create(l);if(s==null)return false;s.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,p.getYRot()+180,0);s.setPersistenceRequired();
            if(!l.noCollision(s)||!l.addFreshEntity(s))continue;
            l.sendParticles(ParticleTypes.END_ROD,s.getX(),s.getY()+.9,s.getZ(),42,.5,.75,.5,.07);s.speak(p);return true;
        }return false;
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%40!=0||p.isSpectator())return;
        ServerLevel l=p.serverLevel();if(l.dimension()!=Level.OVERWORLD||!l.getEntitiesOfClass(Sora.class,p.getBoundingBox().inflate(48)).isEmpty())return;
        BlockPos center=p.blockPosition();
        for(BlockPos q:BlockPos.betweenClosed(center.offset(-4,-2,-4),center.offset(4,2,4))){
            if(!l.hasChunkAt(q)||!(l.getBlockEntity(q) instanceof SignBlockEntity sign)||sign.getPersistentData().getBoolean("NoctisSoraSummoned"))continue;
            if((matches(sign.getFrontText())||matches(sign.getBackText()))&&spawn(p,q)){sign.getPersistentData().putBoolean("NoctisSoraSummoned",true);sign.setChanged();return;}
        }
        if(!l.isDay()&&p.tickCount%600==0&&!Noctis.data(p).getBoolean("metSora")&&l.getMaxLocalRawBrightness(center)<=4&&p.getRandom().nextInt(30)==0&&spawn(p,center))Noctis.data(p).putBoolean("metSora",true);
    }
}''')
write('SoraClient.java','''package it.noctis.magic;
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
public class SoraClient {
    static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"sora"),"main");
    static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/sora.png");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(LAYER,SoraClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.SORA.get(),Renderer::new);}
    static LayerDefinition mesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot(),h=r.getChild("head");
        h.addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.5f,-9,-4.5f,9,3,9).texOffs(64,15).addBox(-4,-7,2.6f,8,5,2),PartPose.ZERO);
        for(int i=0;i<7;i++)h.addOrReplaceChild("spike"+i,CubeListBuilder.create().texOffs(96,0).addBox(-1.3f,-4.8f,-1.3f,2.6f,5,2.6f),PartPose.offsetAndRotation(-4+i*1.3f,-8,-1+(i%3)*1.4f,-.4f+(i%3)*.4f,0,(i-3)*.19f));
        r.getChild("body").addOrReplaceChild("hood",CubeListBuilder.create().texOffs(64,28).addBox(-4,-1,1.5f,8,4,2),PartPose.ZERO);
        for(String leg:new String[]{"right_leg","left_leg"})r.getChild(leg).addOrReplaceChild("shoe",CubeListBuilder.create().texOffs(64,38).addBox(-2.6f,8,-4,5.2f,4,6),PartPose.ZERO);
        PartDefinition key=r.getChild("right_arm").addOrReplaceChild("keyblade",CubeListBuilder.create().texOffs(80,64).addBox(-.6f,0,-.6f,1.2f,19,1.2f).texOffs(90,64).addBox(-3,-2,-1,6,2,2).texOffs(90,72).addBox(-3,-7,-1,1.5f,6,2).texOffs(90,72).addBox(1.5f,-7,-1,1.5f,6,2).texOffs(90,64).addBox(-3,-7,-1,6,1.5f,2).texOffs(106,64).addBox(0,14,-.6f,5,2,1.2f).texOffs(106,72).addBox(3,16,-.6f,2,3,1.2f),PartPose.offsetAndRotation(-1,9,0,0,0,-.15f));
        return LayerDefinition.create(m,128,128);
    }
    static class Model extends HumanoidModel<Sora>{
        Model(ModelPart r){super(r);}
        @Override public void setupAnim(Sora e,float s,float a,float age,float yaw,float pitch){super.setupAnim(e,s,a,age,yaw,pitch);rightArm.xRot-=.45f;rightArm.zRot=-.15f;}
    }
    static class Renderer extends MobRenderer<Sora,Model>{
        Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(LAYER)),.4f);}
        @Override public ResourceLocation getTextureLocation(Sora e){return TEX;}
    }
}''')
# Original pixel atlas, with spiky brown hair, blue eyes, red/black clothes, yellow shoes and silver key.
rng=random.Random(606);pix=[[(31,30,40,255) for x in range(128)] for y in range(128)]
def rect(x,y,w,h,col,noise=0):
    for yy in range(max(0,y),min(128,y+h)):
        for xx in range(max(0,x),min(128,x+w)):
            d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col)+(255,)
rect(0,0,32,16,(194,147,106),7);rect(8,8,8,8,(235,186,139),4)
rect(8,8,8,2,(107,64,36),5);rect(9,10,2,2,(245,247,255));rect(13,10,2,2,(245,247,255));rect(10,10,1,2,(38,108,206));rect(13,10,1,2,(38,108,206));rect(11,14,2,1,(125,76,58))
rect(16,16,24,16,(30,29,39),8);rect(20,20,2,12,(171,38,45),7);rect(26,20,2,12,(171,38,45),7);rect(23,20,1,9,(191,188,180));rect(22,27,3,1,(185,164,91))
rect(40,16,16,16,(41,40,48),6);rect(44,20,4,3,(174,40,46),5);rect(44,25,4,4,(222,171,127),6);rect(44,29,4,3,(36,36,42),5)
rect(0,16,16,16,(170,34,45),7);rect(0,25,16,4,(38,37,45),4);rect(16,48,16,16,(170,34,45),7);rect(16,57,16,4,(38,37,45),4);rect(32,48,16,16,(41,40,48),7)
rect(64,0,40,28,(112,67,33),12);rect(96,0,24,14,(120,73,37),13)
for i in range(65,118,4):rect(i,0,1,12,(165,107,54),6)
rect(64,28,30,10,(166,39,46),6);rect(64,38,28,12,(233,176,46),9);rect(64,47,28,2,(45,42,39))
rect(80,64,10,22,(189,197,211),8);rect(90,64,14,18,(228,186,58),7);rect(106,64,16,16,(191,203,217),8)
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+bytes(c for p in row for c in p) for row in pix)
(assets/'textures/entity/sora.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,128,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.sora']='Sora';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.6.0 source patch applied')
