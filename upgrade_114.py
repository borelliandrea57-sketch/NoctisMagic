"""1.1.4: cuddly Fennekin and lunar guardian Sailor Moon."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Fennekin>> FENNEKIN=ENTITIES.register("fennekin",()->EntityType.Builder.<Fennekin>of(Fennekin::new,MobCategory.CREATURE).sized(.65f,.85f).clientTrackingRange(8).build(ID+":fennekin"));
    public static final RegistryObject<EntityType<MoonGuardian>> SAILOR_MOON=ENTITIES.register("sailor_moon",()->EntityType.Builder.<MoonGuardian>of(MoonGuardian::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":sailor_moon"));
    public static final RegistryObject<Item> FENNEKIN_EGG=ITEMS.register("fennekin_spawn_egg",()->new ForgeSpawnEggItem(FENNEKIN,0xffdf75,0xf46a39,new Item.Properties()));
    public static final RegistryObject<Item> SAILOR_MOON_EGG=ITEMS.register("sailor_moon_spawn_egg",()->new ForgeSpawnEggItem(SAILOR_MOON,0xeee4b3,0x273caa,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(FENNEKIN.get(),Fennekin.attributes().build());e.put(SAILOR_MOON.get(),MoonGuardian.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'e.accept(FENNEKIN_EGG.get());e.accept(SAILOR_MOON_EGG.get());')
a='public static final RegistryObject<Block> BUSH='
edit('VampireLife.java',a,'''public static final RegistryObject<Block> MOON_LIGHT=BLOCKS.register("moon_light",()->new MoonLightBlock());
    '''+a)
(java/'MoonLightBlock.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
public class MoonLightBlock extends Block{
    public MoonLightBlock(){super(BlockBehaviour.Properties.of().noCollission().noOcclusion().noLootTable().replaceable().lightLevel(s->15).strength(0));}
    @Override public RenderShape getRenderShape(BlockState s){return RenderShape.INVISIBLE;}
    @Override public void tick(BlockState s,ServerLevel l,BlockPos p,RandomSource r){
        if(l.getEntitiesOfClass(MoonGuardian.class,new net.minecraft.world.phys.AABB(p).inflate(2),MoonGuardian::shining).isEmpty())l.removeBlock(p,false);
        else l.scheduleTick(p,this,20);
    }
}''',encoding='utf-8')
(java/'Fennekin.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
public class Fennekin extends TamableAnimal{
    private int cuddle,flame,fireCooldown;
    public Fennekin(EntityType<? extends TamableAnimal> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,32).add(Attributes.ATTACK_DAMAGE,5).add(Attributes.MOVEMENT_SPEED,.32).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));goalSelector.addGoal(2,new MeleeAttackGoal(this,1.15,true));goalSelector.addGoal(3,new FollowOwnerGoal(this,1.2,4,1.5f,false));goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(5,new LookAtPlayerGoal(this,Player.class,8));targetSelector.addGoal(1,new OwnerHurtByTargetGoal(this));targetSelector.addGoal(2,new OwnerHurtTargetGoal(this));
    }
    @Override public boolean isFood(ItemStack s){return s.is(Items.SWEET_BERRIES)||s.is(Items.GLOW_BERRIES)||s.is(Items.COOKED_CHICKEN);}
    @Override public boolean wantsToAttack(LivingEntity target,LivingEntity owner){return Eclipse.hostile(target);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        ItemStack s=p.getItemInHand(h);
        if(!isTame()&&isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);if(random.nextInt(3)==0||p.getAbilities().instabuild){tame(p);setPersistenceRequired();setHealth(getMaxHealth());level().broadcastEntityEvent(this,(byte)7);}else level().broadcastEntityEvent(this,(byte)6);}return InteractionResult.sidedSuccess(level().isClientSide);}
        if(isTame()&&isOwnedBy(p)){if(isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);heal(6);}return InteractionResult.sidedSuccess(level().isClientSide);}
            if(s.isEmpty()&&h==InteractionHand.MAIN_HAND){if(level() instanceof ServerLevel l){if(p.isShiftKeyDown()){setOrderedToSit(!isOrderedToSit());getNavigation().stop();setTarget(null);}else if(cuddle==0){cuddle=35;l.broadcastEntityEvent(this,(byte)86);l.sendParticles(ParticleTypes.HEART,getX(),getY()+.8,getZ(),8,.3,.2,.3,.02);playSound(SoundEvents.FOX_AMBIENT,.65f,1.5f);}}return InteractionResult.sidedSuccess(level().isClientSide);}}
        return InteractionResult.PASS;
    }
    @Override public boolean doHurtTarget(Entity e){return e instanceof LivingEntity le&&Eclipse.hostile(le)&&super.doHurtTarget(e);}
    @Override public void tick(){super.tick();if(cuddle>0)cuddle--;if(flame>0)flame--;if(fireCooldown>0)fireCooldown--;
        if(!(level() instanceof ServerLevel l)||!isTame()||isOrderedToSit())return;
        if(getTarget()==null&&getOwner()!=null&&distanceTo(getOwner())<2&&tickCount%160==0&&random.nextInt(3)==0){cuddle=35;l.broadcastEntityEvent(this,(byte)86);l.sendParticles(ParticleTypes.HEART,getX(),getY()+.7,getZ(),3,.2,.15,.2,.01);}
        LivingEntity t=getTarget();if(t==null||!t.isAlive()||!Eclipse.hostile(t)||fireCooldown>0||distanceTo(t)>8||!hasLineOfSight(t))return;
        fireCooldown=100;l.broadcastEntityEvent(this,(byte)87);var a=getEyePosition();var b=t.getEyePosition();for(int i=0;i<16;i++){var v=a.lerp(b,i/15.0);l.sendParticles(ParticleTypes.SMALL_FLAME,v.x,v.y,v.z,3,.10,.10,.10,.02);}t.hurt(damageSources().mobAttack(this),7);t.setSecondsOnFire(3);playSound(SoundEvents.BLAZE_SHOOT,.5f,1.7f);
    }
    @Override public void handleEntityEvent(byte id){if(id==86){cuddle=35;return;}if(id==87){flame=20;return;}super.handleEntityEvent(id);}
    public float cuddling(){return cuddle<=0?0:(float)Math.sin(cuddle*Math.PI/35);}
    public float flaming(){return flame<=0?0:(float)Math.sin(flame*Math.PI/20);}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob a){return null;}
    @Override public boolean canMate(Animal a){return false;}
}''',encoding='utf-8')
(java/'MoonGuardian.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class MoonGuardian extends PathfinderMob{
    private int beam,cd,speech;
    public MoonGuardian(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,80).add(Attributes.ARMOR,6).add(Attributes.MOVEMENT_SPEED,.29).add(Attributes.FOLLOW_RANGE,32);}
    public boolean shining(){return level().dimension()==Level.OVERWORLD&&!level().isDay()&&level().getMoonPhase()==0&&isAlive();}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(2,new LookAtPlayerGoal(this,Player.class,10));goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(4,new RandomLookAroundGoal(this));}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){if(h==InteractionHand.MAIN_HAND&&p.getItemInHand(h).isEmpty()){if(level() instanceof ServerLevel l&&speech<=0){speech=100;NpcDialogue.say(l,Component.literal("Sailor Moon: Nel nome della Luna, ti proteggero!"));}return InteractionResult.sidedSuccess(level().isClientSide);}return super.mobInteract(p,h);}
    @Override public void tick(){
        super.tick();if(beam>0)beam--;if(cd>0)cd--;if(speech>0)speech--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        if(shining()&&tickCount%5==0){
            BlockPos p=blockPosition().above();
            if(l.isEmptyBlock(p)){l.setBlock(p,VampireLife.MOON_LIGHT.get().defaultBlockState(),3);l.scheduleTick(p,VampireLife.MOON_LIGHT.get(),20);}
            l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+1,getZ(),5,.45,.8,.45,.015);
        }
        if(cd>0||l.isDay())return;
        LivingEntity t=l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(18),e->e!=this&&e.isAlive()&&Eclipse.hostile(e)&&hasLineOfSight(e)).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
        if(t==null)return;
        cd=shining()?55:100;getNavigation().stop();getLookControl().setLookAt(t,60,60);l.broadcastEntityEvent(this,(byte)88);
        Vec3 a=getEyePosition(),b=t.getEyePosition();for(int i=0;i<28;i++){Vec3 v=a.lerp(b,i/27.0);l.sendParticles(ParticleTypes.END_ROD,v.x,v.y,v.z,3,.07,.07,.07,.015);if(i%3==0)l.sendParticles(ParticleTypes.ELECTRIC_SPARK,v.x,v.y,v.z,3,.15,.15,.15,.03);}
        t.hurt(damageSources().mobAttack(this),shining()?20:12);t.addEffect(new MobEffectInstance(MobEffects.GLOWING,100,0));t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,1));playSound(SoundEvents.BEACON_ACTIVATE,.9f,1.5f);
        if(speech<=0){speech=180;NpcDialogue.say(l,Component.literal("Sailor Moon: Potere del cristallo di luna!"));}
    }
    @Override public void handleEntityEvent(byte id){if(id==88){beam=25;return;}super.handleEntityEvent(id);}
    public float casting(){return beam<=0?0:(float)Math.sin(beam*Math.PI/25);}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(l.isDay()&&p.getRandom().nextInt(12)==0&&l.getEntitiesOfClass(Fennekin.class,p.getBoundingBox().inflate(64)).size()<2){
            BlockPos q=Eclipse.spot(p,8,20);if(q!=null){Fennekin f=Noctis.FENNEKIN.get().create(l);if(f!=null){f.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(f))l.addFreshEntity(f);}}
        }
        if(!l.isDay()&&l.getMoonPhase()==0&&p.getRandom().nextInt(4)==0&&l.getEntitiesOfClass(MoonGuardian.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){MoonGuardian m=Noctis.SAILOR_MOON.get().create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }''')
# Custom geometry + UV atlas, distinct quadruped and humanoid models.
N=256;S=4;W=N*S;models=[]
for fox in (True,False):
    cx=cy=rh=0;islands=[];lines=[]
    def cube(x,y,z,w,h,d,mat):
        global cx,cy,rh
        ww=2*(w+d);hh=h+d
        if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
        u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
        for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((fx,fy,fw,fh,mat,face))
        return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
    def part(var,parent,name,pos,rot,boxes):
        lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
    if fox:
        part('b','r','body',(0,17,1),(0,0,0),[(-3,-3,-5,6,6,10,'fur'),(-2,-2,-6,4,5,3,'cream')])
        part('h','r','head',(0,15,-5),(0,0,0),[(-4,-5,-4,8,7,7,'face'),(-3,0,-6,6,3,4,'cream'),(-1,.5,-6.5,2,1,1,'nose')])
        for i,side in enumerate((-1,1)):
            part('ear'+str(i),'h','ear'+str(i),(side*3,-4,0),(0,0,side*.40),[(-2,-10,-1,4,9,3,'fur'),(-1.5,-12,-.8,3,3,2,'fur'),(-1,-8,-1.6,3,7,1,'orange')])
            for j in range(3):part(f'tuft{i}{j}','ear'+str(i),f'tuft{j}',(side*(1+j*.4),-3-j*2,-1.4),(0,0,side*.4),[(-.6,-3,-.4,2,4,1,'orange')])
            part('cheek'+str(i),'h','cheek'+str(i),(side*3,0,-2),(0,0,side*.25),[(-1,-1,-2,4,3,4,'cream'),(0,-2,0,3,2,3,'cream')])
            for j,z in enumerate((-3,5)):part(f'leg{i}{j}','r',f'leg{i}{j}',(side*2,19,z),(0,0,0),[(-1,0,-1,2,4,2,'fur'),(-1,4,-2,2,1,3,'fur')])
        part('tail','b','tail',(0,-1,5),(-.8,0,0),[(-2,-2,0,4,4,6,'fur'),(-3,-3,4,6,6,6,'fur')])
        part('tip','tail','tip',(0,0,9),(-.28,0,0),[(-2.5,-2.5,0,5,5,4,'orange'),(-1.5,-1.5,3,3,3,3,'orange')])
    else:
        part('b','r','body',(0,0,0),(0,0,0),[(-3,-1,-2,6,11,4,'white'),(-3,8,-2.5,6,3,5,'blue')])
        part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face')])
        part('hair','h','hair',(0,-7,0),(0,0,0),[(-4,-1,-3.5,8,2,7,'gold'),(-4,0,2,8,6,2,'gold')])
        part('tiara','h','tiara',(0,-5.3,-3.6),(0,0,0),[(-3,0,-.5,6,1,1,'gold'),(-.5,0,-1,1,1,1,'red')])
        part('skirt','b','skirt',(0,10,0),(0,0,0),[(-4,0,-3,8,3,6,'blue'),(-5,2,-3.5,10,1,7,'blue')])
        part('collar','b','collar',(0,0,0),(0,0,0),[(-3.5,-.5,-2.2,7,2,1,'blue'),(-3.5,-.5,1.7,7,3,1,'blue')])
        for i,side in enumerate((-1,1)):
            part('bun'+str(i),'h','bun'+str(i),(side*3.5,-7,0),(0,0,0),[(-1.5,-2,-1.5,3,3,3,'gold'),(-.5,-1,-2,1,2,1,'red')])
            part('lock'+str(i),'h','lock'+str(i),(side*3.7,-5,1),(0,0,side*.1),[(-1,0,-1,2,9,2,'gold')])
            part('locktip'+str(i),'lock'+str(i),'tip',(0,8,0),(0,0,side*.12),[(-.8,0,-1,2,13,2,'gold')])
            part('bang'+str(i),'h','bang'+str(i),(side*1.5,-7,-3.5),(0,0,-side*.36),[(-1,0,-.5,2,3,1,'gold')])
            part('arm'+str(i),'r','arm'+str(i),(side*4,0,0),(0,0,-side*.10),[(-1.5,-1,-1.5,3,3,3,'white'),(-1,2,-1,2,4,2,'skin'),(-1,6,-1,2,5,2,'white'),(-1,6,-1,2,1,2,'red')])
            part('leg'+str(i),'r','leg'+str(i),(side*2,12,0),(0,0,0),[(-1.5,0,-1.5,3,6,3,'skin'),(-1.5,6,-1.5,3,6,3,'red'),(-1.5,10,-2.5,3,2,4,'red')])
            part('bow'+str(i),'b','bow'+str(i),(side*1.2,3,-2.5),(0,0,side*.45),[(-1.5,-1,-.5,3,2,1,'red')])
        part('brooch','b','brooch',(0,3,-3),(0,0,0),[(-.6,-.6,-.5,1,1,1,'gold')])
        part('wand','arm1','wand',(0,10,-1),(0,0,.15),[(-.4,-4,-.4,1,8,1,'gold'),(-1.4,-6,-.4,3,2,1,'gold'),(-.5,-7,-.4,1,1,1,'white')])
    models.append('    static LayerDefinition mesh'+('F' if fox else 'M')+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    pal={'fur':(255,222,111),'cream':(255,249,226),'face':(255,228,125),'nose':(48,44,53),'orange':(243,96,47)} if fox else {'face':(241,201,177),'skin':(240,196,169),'gold':(241,206,67),'blue':(44,68,171),'white':(247,245,240),'red':(205,38,74)}
    pix=bytearray(W*W*4)
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[mat];g=.78+.19*math.sin(u*math.pi)+.05*math.cos(v*7)
                c=tuple(int(b*g) for b in base)
                if mat=='face' and face=='front':
                    for ex in (.25,.75):
                        dx=(u-ex)/(.22 if fox else .19);dy=(v-.50)/(.25 if fox else .17);d=dx*dx+dy*dy
                        if d<1:c=(49,29,32)
                        if d<.81:c=(255,252,245)
                        if d<.75 and abs(dx)<.55:c=(232,92,42) if fox else (63,135,221)
                        if d<.65 and abs(dx)<.20:c=(39,25,38)
                        if (dx+.18)**2+(dy+.35)**2<.07:c=(255,255,255)
                    if not fox and .39<u<.61 and abs(v-.80)<.025:c=(172,64,79)
                if not fox and mat=='gold':c=tuple(int(b*(.72+.26*math.sin(u*29+v*2)**2)) for b in base)
                if not fox and mat=='blue' and v>.85:c=(233,232,238)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,z)) for z in c],255))
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
    (assets/'textures/entity'/('fennekin.png' if fox else 'sailor_moon.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(java/'MoonFoxClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class MoonFoxClient{
    static final ModelLayerLocation F=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"fennekin"),"main"),M=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"sailor_moon"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(F,MoonFoxClient::meshF);e.registerLayerDefinition(M,MoonFoxClient::meshM);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.FENNEKIN.get(),FoxRenderer::new);e.registerEntityRenderer(Noctis.SAILOR_MOON.get(),MoonRenderer::new);}
'''+ '\n'.join(models)+'''
    static class FoxModel extends EntityModel<Fennekin>{
        final ModelPart r,h,b,tail;FoxModel(ModelPart r){this.r=r;h=r.getChild("head");b=r.getChild("body");tail=b.getChild("tail");}
        @Override public void setupAnim(Fennekin e,float limb,float amount,float age,float yaw,float pitch){float c=e.cuddling(),fire=e.flaming();boolean sit=e.isInSittingPose();h.yRot=yaw*.01745f;h.xRot=pitch*.015f-c*.16f-fire*.14f;h.zRot=c*(float)Math.sin(age*.25)*.25f;b.xRot=sit?-.25f:0;b.y=sit?19:17;tail.yRot=(float)Math.sin(age*(c>0?.55:.18))*(c>0?.65f:.24f);tail.xRot=-.8f+c*.25f;
            for(int i=0;i<2;i++){h.getChild("ear"+i).zRot=(i==0?-1:1)*(.40f+(float)Math.sin(age*.14+i)*.08f+c*.14f);for(int j=0;j<2;j++)r.getChild("leg"+i+j).xRot=sit?(j==0?0:1.15f):(float)Math.cos(limb*.67+(i+j)*Math.PI)*amount*.8f;}}
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class MoonModel extends EntityModel<MoonGuardian>{
        final ModelPart r,h,b;MoonModel(ModelPart r){this.r=r;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(MoonGuardian e,float limb,float amount,float age,float yaw,float pitch){float cast=e.casting();h.yRot=yaw*.01745f;h.xRot=pitch*.01745f;for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.6662+i*Math.PI)*amount;r.getChild("leg"+i).xRot=w*.7f;r.getChild("arm"+i).xRot=-w*.7f-(i==1?cast*1.8f:0);ModelPart lock=h.getChild("lock"+i);lock.xRot=amount*.28f+(float)Math.sin(age*.13+i)*.08f;lock.zRot=(i==0?-1:1)*(.10f+(float)Math.sin(age*.15+i)*.09f);lock.getChild("tip").xRot=(float)Math.sin(age*.14+i)*.13f+amount*.2f;}b.getChild("skirt").zRot=(float)Math.sin(limb*.66)*amount*.06f;}
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class FoxRenderer extends MobRenderer<Fennekin,FoxModel>{FoxRenderer(EntityRendererProvider.Context c){super(c,new FoxModel(c.bakeLayer(F)),.3f);}@Override protected void scale(Fennekin e,PoseStack p,float partial){p.scale(.85f,.85f,.85f);}@Override public ResourceLocation getTextureLocation(Fennekin e){return new ResourceLocation(Noctis.ID,"textures/entity/fennekin.png");}}
    static class MoonRenderer extends MobRenderer<MoonGuardian,MoonModel>{MoonRenderer(EntityRendererProvider.Context c){super(c,new MoonModel(c.bakeLayer(M)),.35f);}@Override protected int getBlockLightLevel(MoonGuardian e,net.minecraft.core.BlockPos p){return e.shining()?15:super.getBlockLightLevel(e,p);}@Override public ResourceLocation getTextureLocation(MoonGuardian e){return new ResourceLocation(Noctis.ID,"textures/entity/sailor_moon.png");}}
}''',encoding='utf-8')
for n in ('fennekin','sailor_moon'):(assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
(assets/'blockstates/moon_light.json').write_text('{"variants":{"":{"model":"noctismagic:block/moon_light"}}}')
(assets/'models/block/moon_light.json').write_text('{"parent":"minecraft:block/block","textures":{"particle":"minecraft:block/white_stained_glass"}}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in [('fennekin','Fennekin'),('sailor_moon','Sailor Moon')]:
        d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Fennekin and Sailor Moon with full moon dynamic light installed')
