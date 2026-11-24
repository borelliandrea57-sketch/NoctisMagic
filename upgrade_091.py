"""Noctis Magic 0.9.1: Vincent, a rare protective vampire."""
from pathlib import Path
import sys,json,struct,zlib,random
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
('public static final RegistryObject<EntityType<Sora>> SORA=', '''public static final RegistryObject<EntityType<Vincent>> VINCENT=ENTITIES.register("vincent",()->EntityType.Builder.<Vincent>of(Vincent::new,MobCategory.CREATURE).sized(.7f,2.05f).clientTrackingRange(10).build(ID+":vincent"));
    public static final RegistryObject<Item> VINCENT_EGG=ITEMS.register("vincent_spawn_egg",()->new ForgeSpawnEggItem(VINCENT,0x25222a,0xa33345,new Item.Properties()));
    public static final RegistryObject<EntityType<Sora>> SORA='''),
('e.put(SORA.get(),Sora.attributes().build());','e.put(VINCENT.get(),Vincent.attributes().build());e.put(SORA.get(),Sora.attributes().build());'),
('e.accept(FALLEN_EGG.get());','e.accept(VINCENT_EGG.get());e.accept(FALLEN_EGG.get());')
])
write('Vincent.java','''package it.noctis.magic;
import java.util.Comparator;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.monster.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraft.nbt.CompoundTag;
import org.joml.Vector3f;
public class Vincent extends PathfinderMob {
    private static final TagKey<EntityType<?>> BOSSES=TagKey.create(Registries.ENTITY_TYPE,new ResourceLocation("forge","bosses"));
    private static final TagKey<EntityType<?>> EXCLUDED=TagKey.create(Registries.ENTITY_TYPE,new ResourceLocation(Noctis.ID,"vincent_protected"));
    private static final DustParticleOptions CRIMSON=new DustParticleOptions(new Vector3f(.68f,.035f,.12f),.9f);
    private int cooldown=0,speech=0,visualTicks=0;private boolean engaged;
    public Vincent(EntityType<? extends PathfinderMob> type,Level l){super(type,l);setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,100).add(Attributes.ARMOR,14).add(Attributes.ATTACK_DAMAGE,30).add(Attributes.MOVEMENT_SPEED,.34).add(Attributes.FOLLOW_RANGE,32).add(Attributes.KNOCKBACK_RESISTANCE,.5);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new GuardGoal());goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,10));goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.65));goalSelector.addGoal(5,new RandomLookAroundGoal(this));}
    private boolean eligible(Mob m,Player p){
        if(m==this||!m.isAlive()||m instanceof Vampire.Friendly||m instanceof Familiar||m instanceof OneWinged||m instanceof WitherBoss||m instanceof Warden||m.getType().is(BOSSES)||m.getType().is(EXCLUDED)||m.getMaxHealth()>=100||m instanceof OwnableEntity)return false;
        if(!(m instanceof Enemy)&&m.getType().getCategory()!=MobCategory.MONSTER)return false;
        if(m instanceof NeutralMob&&m.getTarget()!=p&&m.getTarget()!=this)return false;
        return m.distanceToSqr(p)<=196&&m.distanceToSqr(this)<=576;
    }
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override protected net.minecraft.sounds.SoundEvent getAmbientSound(){return null;}
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float amount){if(source.getEntity() instanceof Player)return false;return super.hurt(source,amount);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand hand){
        if(!level().isClientSide&&speech<=0){String[] lines={"...","Resta dietro di me.","Non sono qui per parlare.","Non temere la notte."};p.sendSystemMessage(Component.literal("Vincent: "+lines[random.nextInt(lines.length)]));speech=100;}
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==73){visualTicks=16;return;}super.handleEntityEvent(id);}
    public float attackPose(float partial){return visualTicks<=0?0:(float)Math.sin(Math.PI*(1-Math.max(0,visualTicks-partial)/16f));}
    @Override public void tick(){super.tick();if(visualTicks>0)visualTicks--;if(speech>0)speech--;if(cooldown>0)cooldown--;if(!level().isClientSide&&tickCount%120==0&&getHealth()<getMaxHealth())heal(2);}
    class GuardGoal extends Goal {
        Player protectedPlayer;Mob enemy;
        GuardGoal(){setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK));}
        Player nearest(){return level().getNearestPlayer(Vincent.this,18);}
        Mob choose(Player p){return level().getEntitiesOfClass(Mob.class,getBoundingBox().inflate(24),m->eligible(m,p)).stream().min(Comparator.comparingDouble(m->m.distanceToSqr(p))).orElse(null);}
        @Override public boolean canUse(){protectedPlayer=nearest();if(protectedPlayer==null||protectedPlayer.isSpectator())return false;enemy=choose(protectedPlayer);return enemy!=null;}
        @Override public boolean canContinueToUse(){return protectedPlayer!=null&&protectedPlayer.isAlive()&&!protectedPlayer.isSpectator()&&distanceToSqr(protectedPlayer)<484&&enemy!=null&&eligible(enemy,protectedPlayer);}
        @Override public void start(){if(!engaged&&speech<=0){protectedPlayer.sendSystemMessage(Component.literal("Vincent: Resta dietro di me."));speech=180;}engaged=true;}
        @Override public void stop(){getNavigation().stop();protectedPlayer=null;enemy=null;engaged=false;}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        @Override public void tick(){
            if(!(level() instanceof ServerLevel l)||enemy==null)return;
            getLookControl().setLookAt(enemy,45,45);
            double distance=distanceTo(enemy);
            if(distance>10||!hasLineOfSight(enemy)){if(tickCount%5==0)getNavigation().moveTo(enemy,1.25);return;}
            getNavigation().stop();
            if(cooldown>0)return;cooldown=22;
            l.broadcastEntityEvent(Vincent.this,(byte)73);
            Vec3 from=getEyePosition().add(0,-.35,0),to=enemy.getEyePosition().add(0,-.25,0);
            for(int i=0;i<=12;i++){Vec3 q=from.lerp(to,i/12.0);l.sendParticles(CRIMSON,q.x,q.y,q.z,2,.06,.06,.06,0);}
            l.sendParticles(ParticleTypes.CRIT,to.x,to.y,to.z,8,.25,.25,.25,.12);
            enemy.hurt(damageSources().mobAttack(Vincent.this),32);
            playSound(SoundEvents.PLAYER_ATTACK_STRONG,.65f,.65f);
        }
    }
}'''.replace('import net.minecraft.world.entity.monster.*;','import net.minecraft.world.entity.monster.*;\nimport net.minecraft.world.entity.boss.wither.WitherBoss;'))
write('VincentEncounter.java','''package it.noctis.magic;
import net.minecraft.core.*;
import net.minecraft.server.level.*;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class VincentEncounter {
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.isSpectator()||p.tickCount%600!=0)return;
        ServerLevel l=p.serverLevel();
        if(l.dimension()!=Level.OVERWORLD||l.isDay()||Noctis.data(p).getBoolean("metVincent")||p.getRandom().nextInt(12)!=0||!l.getEntitiesOfClass(Vincent.class,p.getBoundingBox().inflate(96)).isEmpty())return;
        BlockPos center=p.blockPosition();
        for(int i=0;i<28;i++){
            BlockPos q=center.offset(p.getRandom().nextInt(25)-12,p.getRandom().nextInt(5)-2,p.getRandom().nextInt(25)-12);
            if(q.distSqr(center)<36||!l.hasChunkAt(q)||!l.isEmptyBlock(q)||!l.isEmptyBlock(q.above())||!l.isEmptyBlock(q.above(2))||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))continue;
            Vincent v=Noctis.VINCENT.get().create(l);if(v==null)return;
            double dx=p.getX()-q.getX(),dz=p.getZ()-q.getZ();
            v.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,(float)(Math.atan2(dz,dx)*180/Math.PI)-90,0);
            if(l.noCollision(v)&&l.addFreshEntity(v)){Noctis.data(p).putBoolean("metVincent",true);return;}
        }
    }
}''')
write('VincentClient.java','''package it.noctis.magic;
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
public class VincentClient {
    static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"vincent"),"main");
    static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/vincent.png");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(LAYER,VincentClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.VINCENT.get(),Renderer::new);}
    static CubeListBuilder c(int u,int v){return CubeListBuilder.create().texOffs(u,v);}
    static LayerDefinition mesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot(),h=r.getChild("head"),b=r.getChild("body");
        r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        h.addOrReplaceChild("hair",c(64,0).addBox(-4.5f,-9,-4.5f,9,2,9).texOffs(64,14).addBox(-4,-7,3.2f,8,13,2),PartPose.ZERO);
        for(int i=0;i<6;i++)h.addOrReplaceChild("spike"+i,c(96,0).addBox(-1,-4,-1,2,5,2),PartPose.offsetAndRotation(-3.7f+i*1.45f,-8,-.3f+(i%3),-.55f,0,(i-2.5f)*.19f));
        h.addOrReplaceChild("fringe",c(96,14).addBox(-.8f,0,-.6f,1.6f,5,1.2f),PartPose.offsetAndRotation(1.9f,-8,-4.25f,0,0,-.22f));
        b.addOrReplaceChild("chest",c(0,64).addBox(-4.4f,0,-2.7f,8.8f,6,1.2f).texOffs(24,64).addBox(-3.6f,6,-2.55f,7.2f,5,1),PartPose.ZERO);
        b.addOrReplaceChild("collar",c(48,64).addBox(-4.8f,-2,1,9.6f,5,2),PartPose.ZERO);
        for(int i=0;i<2;i++){
            int s=i==0?-1:1;String armName=i==0?"right_arm":"left_arm",legName=i==0?"right_leg":"left_leg";
            PartDefinition arm=r.getChild(armName),leg=r.getChild(legName);
            arm.addOrReplaceChild("pauldron",c(64,40).addBox(-2.8f,-3,-2.6f,5.6f,4,5.2f),PartPose.ZERO);
            arm.addOrReplaceChild("point",c(90,40).addBox(-1,-4,-1,2,5,2),PartPose.offsetAndRotation(s*2,-2,0,0,0,s*.55f));
            arm.addOrReplaceChild("gauntlet",c(64,54).addBox(-2.5f,4,-2.5f,5,7,5),PartPose.ZERO);
            leg.addOrReplaceChild("knee",c(92,54).addBox(-2.2f,3,-2.5f,4.4f,4,1.2f),PartPose.ZERO);
            b.addOrReplaceChild("waist"+i,c(96,74).addBox(-2,0,-.6f,4,7,1.2f),PartPose.offsetAndRotation(s*2,10,-1.9f,.18f,0,s*.14f));
        }
        return LayerDefinition.create(m,128,128);
    }
    static class Model extends HumanoidModel<Vincent>{
        final ModelPart fringe,hair;
        Model(ModelPart r){super(r);fringe=head.getChild("fringe");hair=head.getChild("hair");}
        @Override public void setupAnim(Vincent e,float limb,float amount,float age,float yaw,float pitch){
            super.setupAnim(e,limb,amount,age,yaw,pitch);hat.visible=false;
            float power=e.attackPose(age-e.tickCount);rightArm.xRot-=power*1.5f;rightArm.zRot=-.12f-power*.12f;leftArm.xRot-=power*.35f;
            body.yRot=power*.14f;hair.xRot=(float)Math.sin(age*.12)*.035f-power*.08f;fringe.zRot=-.22f+(float)Math.sin(age*.15)*.025f;
        }
    }
    static class Renderer extends MobRenderer<Vincent,Model>{
        Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(LAYER)),.45f);}
        @Override public ResourceLocation getTextureLocation(Vincent e){return TEX;}
        @Override protected void scale(Vincent e,com.mojang.blaze3d.vertex.PoseStack p,float partial){p.scale(1.08f,1.08f,1.08f);}
    }
}''')
# Custom pixel atlas with pale face, red eyes, layered dark hair and silver armor with red seams.
rng=random.Random(910);pix=[[(23,23,30,255) for x in range(128)] for y in range(128)]
def R(x,y,w,h,c,noise=0):
    for yy in range(max(y,0),min(y+h,128)):
        for xx in range(max(x,0),min(x+w,128)):
            d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in c[:3])+(c[3] if len(c)==4 else 255,)
R(0,0,32,16,(193,172,170),5);R(32,0,32,16,(0,0,0,0))
for x in (0,16,24):R(x,8,8,8,(22,21,28),5)
R(8,0,8,8,(20,19,26),5);R(16,0,8,8,(178,152,155),4)
R(8,8,8,8,(210,187,183),3);R(8,8,8,1,(24,23,31));R(8,9,1,4,(29,25,33));R(15,9,1,3,(26,24,31))
R(9,10,2,1,(57,41,48));R(13,10,2,1,(57,41,48));R(9,11,2,1,(235,225,223));R(13,11,2,1,(235,225,223));R(10,11,1,1,(193,35,56));R(13,11,1,1,(193,35,56));R(12,12,1,2,(170,140,145));R(11,14,2,1,(101,64,75));R(9,15,6,1,(161,132,139))
R(16,16,24,16,(28,29,37),6);R(20,20,8,12,(124,134,146),9);R(20,20,8,1,(191,204,214))
for y in range(21,31):R(20+(y-20)//3,y,1,1,(35,35,44));R(27-(y-20)//3,y,1,1,(35,35,44))
R(40,16,16,16,(32,33,43),8);R(0,16,16,16,(29,28,36),8);R(16,48,32,16,(31,30,39),8)
R(64,0,60,34,(21,20,28),6)
for x in range(65,124,3):R(x,0,1,31,(48,46,57),4)
R(0,64,24,12,(117,127,142),8);R(1,65,18,1,(196,209,220));R(5,67,3,3,(60,63,75));R(12,67,3,3,(60,63,75))
R(24,64,22,12,(85,91,106),7);R(27,68,1,5,(199,72,86));R(39,68,1,5,(199,72,86))
R(48,64,26,12,(17,18,25),7);R(64,40,25,14,(100,113,130),9);R(66,42,15,1,(188,201,217));R(71,45,2,3,(177,50,69))
R(90,40,14,10,(142,155,171),8);R(64,54,28,18,(29,31,42),7);R(68,60,10,2,(141,150,167));R(69,64,8,1,(194,53,75));R(92,54,20,11,(90,100,115),6);R(96,74,20,12,(30,30,41),6);R(99,78,1,5,(183,54,73));R(108,78,1,5,(183,54,73))
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+bytes(v for p in row for v in p) for row in pix)
(assets/'textures/entity/vincent.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,128,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
j('assets/noctismagic/models/item/vincent_spawn_egg.json',{"parent":"minecraft:item/template_spawn_egg"})
j('data/noctismagic/tags/entity_types/vincent_protected.json',{"replace":False,"values":["minecraft:ender_dragon","minecraft:wither","minecraft:warden","noctismagic:one_winged_angel"]})
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.vincent']='Vincent Valentine';d['item.noctismagic.vincent_spawn_egg']='Uovo generatore: Vincent Valentine' if lang=='it_it' else 'Vincent Valentine Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.9.1: Vincent guardian installed')
