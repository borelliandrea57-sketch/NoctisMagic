"""Noctis 0.9.3: affectionate companions and a temporary Raiden spell."""
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
('public static final RegistryObject<EntityType<Familiar>> UMBREON=', '''public static final RegistryObject<EntityType<Admirer>> WAIFU=ENTITIES.register("waifu",()->EntityType.Builder.<Admirer>of(Admirer::new,MobCategory.CREATURE).sized(.75f,1.95f).clientTrackingRange(8).build(ID+":waifu"));
    public static final RegistryObject<EntityType<Admirer>> OGRE=ENTITIES.register("glamour_ogre",()->EntityType.Builder.<Admirer>of(Admirer::new,MobCategory.CREATURE).sized(.95f,2.2f).clientTrackingRange(8).build(ID+":glamour_ogre"));
    public static final RegistryObject<EntityType<Admirer>> SLIME_LADY=ENTITIES.register("slime_lady",()->EntityType.Builder.<Admirer>of(Admirer::new,MobCategory.CREATURE).sized(.8f,1.85f).clientTrackingRange(8).build(ID+":slime_lady"));
    public static final RegistryObject<EntityType<Raiden>> RAIDEN=ENTITIES.register("raiden",()->EntityType.Builder.<Raiden>of(Raiden::new,MobCategory.MISC).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":raiden"));
    public static final RegistryObject<Item> WAIFU_EGG=ITEMS.register("waifu_spawn_egg",()->new ForgeSpawnEggItem(WAIFU,0x774563,0xf6a9bd,new Item.Properties()));
    public static final RegistryObject<Item> OGRE_EGG=ITEMS.register("glamour_ogre_spawn_egg",()->new ForgeSpawnEggItem(OGRE,0x687e3e,0xdb4988,new Item.Properties()));
    public static final RegistryObject<Item> SLIME_LADY_EGG=ITEMS.register("slime_lady_spawn_egg",()->new ForgeSpawnEggItem(SLIME_LADY,0x55b7a3,0xf6a3ca,new Item.Properties()));
    public static final RegistryObject<EntityType<Familiar>> UMBREON='''),
('e.put(UMBREON.get(),Familiar.attributes(40,7).build());','e.put(WAIFU.get(),Admirer.attributes(30).build());e.put(OGRE.get(),Admirer.attributes(48).build());e.put(SLIME_LADY.get(),Admirer.attributes(34).build());e.put(RAIDEN.get(),Raiden.attributes().build());e.put(UMBREON.get(),Familiar.attributes(40,7).build());'),
('e.accept(VINCENT_EGG.get());','e.accept(WAIFU_EGG.get());e.accept(OGRE_EGG.get());e.accept(SLIME_LADY_EGG.get());e.accept(VINCENT_EGG.get());'),
('STORM("Tempesta oscura",10,120);','STORM("Tempesta oscura",10,120),RAIDEN("Evoca Raiden",7,85);'),
('case FIRE -> {','case RAIDEN -> {if(!Raiden.summon(p)){tell(p,"Raiden e ancora in missione, oppure manca spazio.");return;}}\n            case FIRE -> {')
])
# Screen has an unused tenth spell slot; no layout change is needed.
write('Admirer.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.animal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.network.chat.Component;
public class Admirer extends TamableAnimal {
    public Admirer(EntityType<? extends TamableAnimal> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(double hp){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,hp).add(Attributes.MOVEMENT_SPEED,.29).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));goalSelector.addGoal(2,new FollowOwnerGoal(this,1.1,5,2,false));goalSelector.addGoal(3,new AdmireGoal());goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.7));goalSelector.addGoal(5,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(6,new RandomLookAroundGoal(this));
    }
    @Override public boolean isFood(ItemStack s){return s.isEdible();}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        ItemStack s=p.getItemInHand(h);
        if(!isTame()&&isFood(s)){
            if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);if(random.nextInt(3)==0){tame(p);setPersistenceRequired();setHealth(getMaxHealth());level().broadcastEntityEvent(this,(byte)7);p.sendSystemMessage(Component.literal(getDisplayName().getString()+": Ti voglio bene!"));}else{level().broadcastEntityEvent(this,(byte)7);}}
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if(isTame()&&isOwnedBy(p)){
            if(!level().isClientSide){if(isFood(s)){if(!p.getAbilities().instabuild)s.shrink(1);heal(6);level().broadcastEntityEvent(this,(byte)7);}else if(s.isEmpty()){setOrderedToSit(!isOrderedToSit());getNavigation().stop();}}
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        return InteractionResult.PASS;
    }
    @Override public void tick(){super.tick();if(level() instanceof ServerLevel l&&tickCount%65==0&&!isOrderedToSit()){
        Player p=l.getNearestPlayer(this,5);if(p!=null&&!p.isSpectator())l.sendParticles(ParticleTypes.HEART,getX(),getY()+getBbHeight()+.15,getZ(),2,.22,.2,.22,.01);
    }}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob partner){return null;}
    @Override public boolean canMate(Animal a){return false;}
    @Override public boolean removeWhenFarAway(double d){return !isTame()&&d>128*128;}
    class AdmireGoal extends Goal {
        Player p;
        AdmireGoal(){setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK));}
        @Override public boolean canUse(){if(isTame()||isOrderedToSit())return false;p=level().getNearestPlayer(Admirer.this,14);return p!=null&&!p.isSpectator();}
        @Override public boolean canContinueToUse(){return !isTame()&&p!=null&&p.isAlive()&&!p.isSpectator()&&distanceToSqr(p)<256;}
        @Override public void stop(){getNavigation().stop();p=null;}
        @Override public void tick(){if(p==null)return;getLookControl().setLookAt(p,25,25);if(distanceTo(p)>2.6)getNavigation().moveTo(p,1);else getNavigation().stop();}
    }
}''')
write('AdmirerEncounter.java','''package it.noctis.magic;
import net.minecraft.core.*;
import net.minecraft.server.level.*;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class AdmirerEncounter{
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.isSpectator()||p.tickCount%600!=0)return;
        ServerLevel l=p.serverLevel();if(l.dimension()!=Level.OVERWORLD||p.getRandom().nextInt(6)!=0||l.getEntitiesOfClass(Admirer.class,p.getBoundingBox().inflate(64)).size()>=2)return;
        for(int i=0;i<20;i++){BlockPos q=p.blockPosition().offset(p.getRandom().nextInt(29)-14,p.getRandom().nextInt(5)-2,p.getRandom().nextInt(29)-14);
            if(q.distSqr(p.blockPosition())<49||!l.hasChunkAt(q)||!l.isEmptyBlock(q)||!l.isEmptyBlock(q.above())||!l.isEmptyBlock(q.above(2))||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))continue;
            int variant=p.getRandom().nextInt(3);Admirer a=(variant==0?Noctis.WAIFU.get():variant==1?Noctis.OGRE.get():Noctis.SLIME_LADY.get()).create(l);
            if(a!=null){a.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(a)&&l.addFreshEntity(a))return;}
        }
    }
}''')
write('Raiden.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.animal.*;
import net.minecraft.world.entity.monster.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
public class Raiden extends TamableAnimal {
    private long expires;private int slash=0;
    public Raiden(EntityType<? extends TamableAnimal> t,Level l){super(t,l);setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,140).add(Attributes.ARMOR,16).add(Attributes.ATTACK_DAMAGE,28).add(Attributes.MOVEMENT_SPEED,.43).add(Attributes.FOLLOW_RANGE,32).add(Attributes.KNOCKBACK_RESISTANCE,.75);}
    private static boolean hostile(LivingEntity e){return e instanceof Monster&&!(e instanceof Vampire.Friendly);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.45,true));goalSelector.addGoal(2,new FollowOwnerGoal(this,1.3,6,2,false));goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));
        targetSelector.addGoal(1,new NearestAttackableTargetGoal<Monster>(this,Monster.class,10,true,false,e->hostile(e)&&isTame()&&getOwner()!=null&&e.distanceToSqr(getOwner())<576));
    }
    @Override public boolean doHurtTarget(Entity e){
        if(!(e instanceof LivingEntity le)||!hostile(le))return false;
        boolean hit=super.doHurtTarget(e);if(hit&&level() instanceof ServerLevel l){l.broadcastEntityEvent(this,(byte)75);l.sendParticles(ParticleTypes.SWEEP_ATTACK,e.getX(),e.getY()+e.getBbHeight()*.6,e.getZ(),2,.3,.25,.3,0);l.sendParticles(ParticleTypes.ELECTRIC_SPARK,e.getX(),e.getY()+.8,e.getZ(),12,.4,.5,.4,.07);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,1,.8f);}return hit;
    }
    @Override public void handleEntityEvent(byte id){if(id==75){slash=10;return;}super.handleEntityEvent(id);}
    public float slashPose(float partial){return slash<=0?0:(float)Math.sin(Math.PI*(1-Math.max(0,slash-partial)/10f));}
    @Override public void tick(){super.tick();if(slash>0)slash--;if(level() instanceof ServerLevel l){
        if(expires<=0||l.getGameTime()>=expires){l.sendParticles(ParticleTypes.ELECTRIC_SPARK,getX(),getY()+1,getZ(),45,.6,.7,.6,.06);discard();}
    }}
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource s,float damage){if(s.getEntity() instanceof Player)return false;return super.hurt(s,damage);}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob p){return null;}
    @Override public boolean canMate(Animal a){return false;}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putLong("Expires",expires);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);expires=t.getLong("Expires");}
    static boolean summon(ServerPlayer p){
        ServerLevel l=p.serverLevel();CompoundTag d=Noctis.data(p);long now=l.getGameTime();
        if(d.getLong("raidenUntil")>now)return false;
        for(int i=0;i<18;i++){
            BlockPos q=p.blockPosition().offset(p.getRandom().nextInt(7)-3,0,p.getRandom().nextInt(7)-3);
            if(q.distSqr(p.blockPosition())<2||!l.hasChunkAt(q)||!l.isEmptyBlock(q)||!l.isEmptyBlock(q.above())||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),net.minecraft.core.Direction.UP))continue;
            Raiden r=Noctis.RAIDEN.get().create(l);if(r==null)return false;r.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);r.tame(p);r.expires=now+1800;
            if(!l.noCollision(r)||!l.addFreshEntity(r))continue;d.putLong("raidenUntil",now+1800);
            l.sendParticles(ParticleTypes.ELECTRIC_SPARK,r.getX(),r.getY()+1,r.getZ(),60,.6,.8,.6,.08);p.sendSystemMessage(Component.literal("Raiden: Lascia fare a me."));return true;
        }return false;
    }
}''')
write('GlamourClient.java','''package it.noctis.magic;
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
public class GlamourClient {
    static final ModelLayerLocation[] LAYERS={layer("waifu"),layer("glamour_ogre"),layer("slime_lady"),layer("raiden")};
    static ModelLayerLocation layer(String n){return new ModelLayerLocation(new ResourceLocation(Noctis.ID,n),"main");}
    static ResourceLocation tex(String n){return new ResourceLocation(Noctis.ID,"textures/entity/"+n+".png");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){for(int i=0;i<4;i++){final int k=i;e.registerLayerDefinition(LAYERS[i],()->mesh(k));}}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
        e.registerEntityRenderer(Noctis.WAIFU.get(),c->new LadyRenderer(c,0,"waifu"));
        e.registerEntityRenderer(Noctis.OGRE.get(),c->new LadyRenderer(c,1,"glamour_ogre"));
        e.registerEntityRenderer(Noctis.SLIME_LADY.get(),c->new LadyRenderer(c,2,"slime_lady"));
        e.registerEntityRenderer(Noctis.RAIDEN.get(),RRenderer::new);
    }
    static CubeListBuilder c(int u,int v){return CubeListBuilder.create().texOffs(u,v);}
    static PartDefinition add(PartDefinition p,String n,CubeListBuilder b,float x,float y,float z){return p.addOrReplaceChild(n,b,PartPose.offset(x,y,z));}
    static LayerDefinition mesh(int k){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot(),h=r.getChild("head"),b=r.getChild("body");
        r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        add(h,"hair",c(64,0).addBox(-4.5f,-9,-4.5f,9,2,9).texOffs(64,14).addBox(-4,-7,3.2f,8,k==3?7:15,2),0,0,0);
        if(k<3){
            // Cartoon hourglass silhouette, fully clothed, exaggerated bust and hip tailoring.
            add(b,"bodice",c(0,64).addBox(-4.7f,1,-4.5f,9.4f,5,4.5f),0,0,0);
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                add(b,"bust"+i,c(32,64).addBox(-2.4f,-2,-2.3f,4.8f,4,3.5f),s*2.3f,3,-2.3f);
                add(b,"hip"+i,c(56,64).addBox(-2.9f,0,-2.7f,5.8f,4,5.4f),s*2.3f,9,0);
                PartDefinition lock=h.addOrReplaceChild("lock"+i,c(96,0).addBox(-1.1f,0,-1,2.2f,10,2.5f),PartPose.offsetAndRotation(s*4.4f,-7,0,0,0,s*.08f));
                PartDefinition arm=r.getChild(i==0?"right_arm":"left_arm");add(arm,"cuff",c(96,40).addBox(-2.2f,6,-2.2f,4.4f,2,4.4f),0,0,0);
                if(k==1){h.addOrReplaceChild("horn"+i,c(96,16).addBox(-1,-5,-1,2,5,2),PartPose.offsetAndRotation(s*3,-7,0,0,0,s*.4f));add(h,"tusk"+i,c(112,16).addBox(-.5f,-2,-.5f,1,2,1),s*2,0,-4.2f);}
                if(k==2)add(h,"jelly"+i,c(96,28).addBox(-1.4f,-3,-1.2f,2.8f,4,2.4f),s*3.4f,-7,0);
            }
            add(b,"skirt",c(0,82).addBox(-5,10,-3.2f,10,5,6.4f),0,0,0);
        }else{
            for(int i=0;i<6;i++)h.addOrReplaceChild("spike"+i,c(96,0).addBox(-1,-4,-1,2,4,2),PartPose.offsetAndRotation(-3.5f+i*1.4f,-8,i%2,-.5f,0,(i-2.5f)*.2f));
            add(h,"visor",c(96,16).addBox(-4,-4.8f,-4.4f,8,1.7f,.8f),0,0,0);
            add(b,"plate",c(0,64).addBox(-4.4f,0,-3,8.8f,7,1.8f),0,0,0);
            for(int i=0;i<2;i++){PartDefinition arm=r.getChild(i==0?"right_arm":"left_arm");add(arm,"armor",c(64,40).addBox(-2.5f,-2,-2.5f,5,4,5),0,0,0);add(arm,"gauntlet",c(64,54).addBox(-2.4f,4,-2.4f,4.8f,7,4.8f),0,0,0);}
            add(r.getChild("right_arm"),"blade",c(80,90).addBox(-.6f,1,-.5f,1.2f,24,1).texOffs(96,90).addBox(-2.5f,0,-1,5,1,2).texOffs(96,98).addBox(-.8f,-5,-.8f,1.6f,5,1.6f),-1,8,0);
        }
        return LayerDefinition.create(m,128,128);
    }
    static class LadyModel extends HumanoidModel<Admirer>{
        final ModelPart l,r;LadyModel(ModelPart root){super(root);l=head.getChild("lock0");r=head.getChild("lock1");}
        @Override public void setupAnim(Admirer e,float limb,float amount,float age,float yaw,float pitch){
            super.setupAnim(e,limb,amount,age,yaw,pitch);hat.visible=false;float sway=(float)Math.sin(age*.11)*.065f;
            l.zRot=-.08f+sway;r.zRot=.08f+sway;body.zRot=amount*.045f*(float)Math.sin(limb*.7);
            if(e.isInSittingPose()){rightLeg.xRot=-1.35f;leftLeg.xRot=-1.35f;body.xRot=-.08f;}else body.xRot=0;
        }
    }
    static class LadyRenderer extends MobRenderer<Admirer,LadyModel>{
        final ResourceLocation texture;final int k;
        LadyRenderer(EntityRendererProvider.Context c,int k,String n){super(c,new LadyModel(c.bakeLayer(LAYERS[k])),.45f);this.k=k;texture=tex(n);}
        @Override public ResourceLocation getTextureLocation(Admirer e){return texture;}
        @Override protected void scale(Admirer e,PoseStackAliasNotUsed p,float f){}
    }
    static class RModel extends HumanoidModel<Raiden>{
        RModel(ModelPart r){super(r);}
        @Override public void setupAnim(Raiden e,float limb,float amount,float age,float yaw,float pitch){
            super.setupAnim(e,limb,amount,age,yaw,pitch);hat.visible=false;float slash=e.slashPose(age-e.tickCount);rightArm.xRot=-.35f-slash*1.6f;rightArm.zRot=-.2f-slash*.9f;body.yRot=slash*.45f;leftArm.xRot-=slash*.35f;
        }
    }
    static class RRenderer extends MobRenderer<Raiden,RModel>{
        RRenderer(EntityRendererProvider.Context c){super(c,new RModel(c.bakeLayer(LAYERS[3])),.45f);}
        @Override public ResourceLocation getTextureLocation(Raiden e){return tex("raiden");}
    }
}'''.replace('@Override protected void scale(Admirer e,PoseStackAliasNotUsed p,float f){}','@Override protected void scale(Admirer e,com.mojang.blaze3d.vertex.PoseStack p,float f){if(k==1)p.scale(1.13f,1.13f,1.13f);else if(k==2)p.scale(1.02f,.98f,1.02f);}'))
# Four separate atlases, with readable face UVs and transparent head overlay.
def png(name,skin,hair,cloth,trim,k):
    rng=random.Random(name);pix=[[(*cloth,255) for x in range(128)] for y in range(128)]
    def R(x,y,w,h,col,noise=0):
        for yy in range(max(0,y),min(128,y+h)):
            for xx in range(max(0,x),min(128,x+w)):
                d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col[:3])+(col[3] if len(col)==4 else 255,)
    R(0,0,32,16,skin,5);R(32,0,32,16,(0,0,0,0))
    R(8,0,8,8,hair,6)
    for x in (0,16,24):R(x,8,8,8,hair,6)
    R(8,8,8,8,skin,3);R(8,8,8,1,hair);R(8,9,1,2,hair)
    for x in (9,13):
        R(x,10,2,1,(49,24,40));R(x,11,2,1,(245,235,239));R(x+(1 if x==9 else 0),11,1,1,trim)
    R(11,14,2,1,(192,23,82) if k<3 else (105,86,91));R(10,14,1,1,(147,22,63) if k<3 else skin);R(13,14,1,1,(147,22,63) if k<3 else skin)
    if k<3:R(9,13,1,1,(217,108,133));R(14,13,1,1,(217,108,133))
    R(16,16,24,16,cloth,8);R(20,20,8,12,cloth,6);R(20,20,8,1,trim);R(23,22,2,1,trim)
    R(40,16,16,16,cloth,8);R(44,25,4,5,skin,4);R(0,16,16,16,cloth,7);R(16,48,32,16,cloth,7)
    R(64,0,64,38,hair,8)
    for x in range(65,125,4):R(x,1,1,30,tuple(min(255,v+35) for v in hair),5)
    R(96,40,24,12,trim,8)
    R(0,64,80,18,cloth,8)
    for x in (4,16,34,46,58,70):R(x,67,2,8,trim,5)
    R(0,82,36,14,cloth,7);R(0,92,36,2,trim,7)
    if k==1:R(96,16,24,12,(88,66,58),8)
    if k==2:R(96,28,24,10,(113,236,200),9)
    if k==3:
        R(0,64,28,14,(116,133,152),12);R(4,68,14,1,(213,227,239));R(64,40,26,14,(98,113,132),8);R(64,54,28,18,(48,56,70),9);R(96,16,22,6,(156,36,48),5);R(80,90,10,30,(182,204,225),9);R(82,92,1,23,(245,251,255));R(96,90,16,16,(47,44,54),8)
    def chunk(tag,b):return struct.pack('>I',len(b))+tag+b+struct.pack('>I',zlib.crc32(tag+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for px in row for v in px) for row in pix)
    (assets/'textures/entity'/f'{name}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,128,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
png('waifu',(233,182,167),(62,29,48),(98,34,71),(235,130,170),0)
png('glamour_ogre',(128,160,87),(39,42,29),(88,42,59),(225,166,75),1)
png('slime_lady',(104,200,167),(39,132,115),(48,92,112),(245,153,206),2)
png('raiden',(213,190,183),(180,189,205),(31,36,49),(175,46,57),3)
for id in ('waifu','glamour_ogre','slime_lady'):j('assets/noctismagic/models/item/'+id+'_spawn_egg.json',{"parent":"minecraft:item/template_spawn_egg"})
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
    for id,label in [('waifu','Waifu'),('glamour_ogre','Orchessa glamour' if it else 'Glamour Ogre'),('slime_lady','Dama di slime' if it else 'Slime Lady'),('raiden','Raiden')]:
        d['entity.noctismagic.'+id]=label
        if id!='raiden':d['item.noctismagic.'+id+'_spawn_egg']=('Uovo generatore: '+label) if it else label+' Spawn Egg'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.9.3: admirers and Raiden summon applied')
