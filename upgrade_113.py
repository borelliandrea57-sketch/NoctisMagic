"""1.1.3: two rideable Synchro dragons, flight, distinct combat magic and custom models."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<SynchroDragon>> BLACK_ROSE=ENTITIES.register("black_rose_dragon",()->EntityType.Builder.<SynchroDragon>of(SynchroDragon::new,MobCategory.CREATURE).sized(2.6f,3.6f).clientTrackingRange(12).build(ID+":black_rose_dragon"));
    public static final RegistryObject<EntityType<SynchroDragon>> STARDUST=ENTITIES.register("stardust_dragon",()->EntityType.Builder.<SynchroDragon>of(SynchroDragon::new,MobCategory.CREATURE).sized(2.6f,3.6f).clientTrackingRange(12).build(ID+":stardust_dragon"));
    public static final RegistryObject<Item> BLACK_ROSE_EGG=ITEMS.register("black_rose_dragon_spawn_egg",()->new ForgeSpawnEggItem(BLACK_ROSE,0xa71949,0x24212e,new Item.Properties()));
    public static final RegistryObject<Item> STARDUST_EGG=ITEMS.register("stardust_dragon_spawn_egg",()->new ForgeSpawnEggItem(STARDUST,0xc8dce9,0x54488a,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(BLACK_ROSE.get(),SynchroDragon.attributes().build());e.put(STARDUST.get(),SynchroDragon.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'e.accept(BLACK_ROSE_EGG.get());e.accept(STARDUST_EGG.get());')
(java/'SynchroDragon.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class SynchroDragon extends TamableAnimal{
    private int magicCooldown=0,castPose=0;
    public SynchroDragon(EntityType<? extends TamableAnimal> t,Level l){super(t,l);setMaxUpStep(1f);}
    public boolean rose(){return getType()==Noctis.BLACK_ROSE.get();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,180).add(Attributes.ARMOR,12).add(Attributes.ATTACK_DAMAGE,25).add(Attributes.MOVEMENT_SPEED,.35).add(Attributes.FOLLOW_RANGE,48).add(Attributes.KNOCKBACK_RESISTANCE,.8);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));
        goalSelector.addGoal(2,new MeleeAttackGoal(this,1.2,true){@Override public boolean canUse(){return !isVehicle()&&super.canUse();}@Override public boolean canContinueToUse(){return !isVehicle()&&super.canContinueToUse();}});
        goalSelector.addGoal(3,new FollowOwnerGoal(this,1.1,8,3,false){@Override public boolean canUse(){return !isVehicle()&&super.canUse();}@Override public boolean canContinueToUse(){return !isVehicle()&&super.canContinueToUse();}});
        goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.7){@Override public boolean canUse(){return !isVehicle()&&super.canUse();}});goalSelector.addGoal(5,new LookAtPlayerGoal(this,Player.class,10));
        targetSelector.addGoal(1,new OwnerHurtByTargetGoal(this));targetSelector.addGoal(2,new OwnerHurtTargetGoal(this));
    }
    @Override public boolean isFood(ItemStack s){return s.is(Items.COOKED_BEEF)||s.is(Items.COOKED_PORKCHOP)||s.is(Items.COOKED_CHICKEN);}
    private boolean offering(ItemStack s){return rose()?s.is(Items.WITHER_ROSE):s.is(Items.AMETHYST_SHARD);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        ItemStack s=p.getItemInHand(h);
        if(!isTame()&&offering(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);if(random.nextInt(3)==0||p.getAbilities().instabuild){tame(p);setPersistenceRequired();setHealth(getMaxHealth());level().broadcastEntityEvent(this,(byte)7);}else level().broadcastEntityEvent(this,(byte)6);}return InteractionResult.sidedSuccess(level().isClientSide);}
        if(isTame()&&isOwnedBy(p)){
            if(isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);heal(16);}return InteractionResult.sidedSuccess(level().isClientSide);}
            if(s.isEmpty()&&h==InteractionHand.MAIN_HAND){if(!level().isClientSide){
                if(p.isShiftKeyDown()){setOrderedToSit(!isOrderedToSit());getNavigation().stop();setTarget(null);}
                else{setOrderedToSit(false);setInSittingPose(false);getNavigation().stop();setTarget(null);p.startRiding(this);p.displayClientMessage(Component.literal("WASD per volare; guarda in alto/basso per salire/scendere; bacchetta di Blaze per il potere."),false);}
            }return InteractionResult.sidedSuccess(level().isClientSide);}
        }return InteractionResult.PASS;
    }
    @Override public LivingEntity getControllingPassenger(){return getFirstPassenger() instanceof Player p&&isOwnedBy(p)?p:null;}
    @Override public double getPassengersRidingOffset(){return 2.45;}
    @Override public boolean causeFallDamage(float a,float b,net.minecraft.world.damagesource.DamageSource d){return false;}
    @Override public void travel(Vec3 v){
        if(isAlive()&&getControllingPassenger() instanceof Player rider){
            setYRot(rider.getYRot());yBodyRot=getYRot();yHeadRot=getYRot();setXRot(0);
            setNoGravity(true);getNavigation().stop();
            if(isControlledByLocalInstance()){
                double yaw=Math.toRadians(rider.getYRot()),pitch=Math.toRadians(rider.getXRot());
                double f=rider.zza,side=rider.xxa;
                Vec3 motion=new Vec3(-Math.sin(yaw)*Math.cos(pitch)*f+Math.cos(yaw)*side*.65,-Math.sin(pitch)*f,Math.cos(yaw)*Math.cos(pitch)*f+Math.sin(yaw)*side*.65);
                if(motion.lengthSqr()>1)motion=motion.normalize();
                setDeltaMovement(getDeltaMovement().scale(.72).add(motion.scale(rose()?.24:.28)));
                if(getDeltaMovement().lengthSqr()<.0002)setDeltaMovement(Vec3.ZERO);
                move(MoverType.SELF,getDeltaMovement());calculateEntityAnimation(false);
            }else setDeltaMovement(Vec3.ZERO);
            return;
        }
        if(isNoGravity())setNoGravity(false);
        super.travel(v);
    }
    @Override public boolean wantsToAttack(LivingEntity target,LivingEntity owner){return Eclipse.hostile(target);}
    @Override public boolean doHurtTarget(Entity e){return isTame()&&e instanceof LivingEntity le&&Eclipse.hostile(le)&&super.doHurtTarget(e);}
    @Override public void tick(){
        super.tick();if(magicCooldown>0)magicCooldown--;if(castPose>0)castPose--;
        if(!(level() instanceof ServerLevel l)||!isTame()||isOrderedToSit())return;
        if(!isVehicle()&&getTarget()!=null&&getTarget().isAlive()&&distanceTo(getTarget())<15&&hasLineOfSight(getTarget()))cast(l,getTarget());
        if(!isVehicle()&&getTarget()==null&&getOwner()!=null&&getOwner().getY()-getY()>4&&distanceTo(getOwner())<45){
            Vec3 v=getOwner().position().subtract(position()).normalize().scale(.38);
            if(l.noCollision(this,getBoundingBox().move(v))){setDeltaMovement(v);resetFallDistance();}
        }
        if(tickCount%5==0&&!onGround())l.sendParticles(rose()?ParticleTypes.CRIMSON_SPORE:ParticleTypes.END_ROD,getX(),getY()+1,getZ(),3,1.2,.4,1.2,.02);
    }
    public void cast(ServerLevel l,LivingEntity target){
        if(magicCooldown>0||!isTame()||isOrderedToSit())return;
        if(rose()&&target==null)return;
        magicCooldown=rose()?120:180;l.broadcastEntityEvent(this,(byte)85);
        if(rose()){
            Vec3 a=position().add(0,2.7,0),b=target.getEyePosition();
            for(int i=0;i<28;i++){Vec3 q=a.lerp(b,i/27.0);l.sendParticles(ParticleTypes.CRIMSON_SPORE,q.x,q.y,q.z,4,.35,.35,.35,.05);}
            for(LivingEntity e:l.getEntitiesOfClass(LivingEntity.class,target.getBoundingBox().inflate(5),e->e.isAlive()&&Eclipse.hostile(e)&&!isAlliedTo(e))){e.hurt(damageSources().mobAttack(this),24);e.addEffect(new MobEffectInstance(MobEffects.WITHER,100,0));e.knockback(1.5,getX()-e.getX(),getZ()-e.getZ());}
            playSound(SoundEvents.ENDER_DRAGON_SHOOT,1.4f,.75f);
        }else{
            addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,160,1));heal(12);
            if(getOwner()!=null){getOwner().addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,160,1));getOwner().addEffect(new MobEffectInstance(MobEffects.ABSORPTION,240,1));getOwner().heal(8);}
            for(int i=0;i<40;i++){double a=i*Math.PI/20;l.sendParticles(ParticleTypes.END_ROD,getX()+Math.cos(a)*3,getY()+1.4,getZ()+Math.sin(a)*3,2,.1,.4,.1,.025);}
            if(target!=null&&Eclipse.hostile(target)){Vec3 a=position().add(0,2.7,0),b=target.getEyePosition();for(int i=0;i<24;i++){Vec3 q=a.lerp(b,i/23.0);l.sendParticles(ParticleTypes.END_ROD,q.x,q.y,q.z,3,.12,.12,.12,.02);}target.hurt(damageSources().mobAttack(this),20);}
            playSound(SoundEvents.BEACON_ACTIVATE,1.4f,1.2f);
        }
    }
    @Override public void handleEntityEvent(byte id){if(id==85){castPose=24;return;}super.handleEntityEvent(id);}
    public float casting(){return castPose<=0?0:(float)Math.sin(castPose*Math.PI/24);}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob a){return null;}
    @Override public boolean canMate(Animal a){return false;}
}''',encoding='utf-8')
(java/'DragonMountEvents.java').write_text('''package it.noctis.magic;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class DragonMountEvents{
    @SubscribeEvent public static void power(PlayerInteractEvent.RightClickItem e){
        if(!e.getItemStack().is(Items.BLAZE_ROD)||!(e.getEntity() instanceof ServerPlayer p)||!(p.getVehicle() instanceof SynchroDragon d)||!d.isOwnedBy(p))return;
        Vec3 eye=p.getEyePosition(),look=p.getLookAngle();LivingEntity best=null;double score=Double.MAX_VALUE;
        for(LivingEntity x:p.serverLevel().getEntitiesOfClass(LivingEntity.class,p.getBoundingBox().inflate(30),x->x.isAlive()&&Eclipse.hostile(x)&&!d.isAlliedTo(x))){
            Vec3 v=x.getEyePosition().subtract(eye);double len=v.length();if(len>30||len<.1||look.dot(v.normalize())<.80||!p.hasLineOfSight(x))continue;
            double cost=len+(1-look.dot(v.normalize()))*30;if(cost<score){best=x;score=cost;}
        }
        d.cast(p.serverLevel(),best);
    }
}''',encoding='utf-8')
# Encounter rarity: both can be found, not just spawned from eggs.
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(p.getRandom().nextInt(48)==0&&l.getEntitiesOfClass(SynchroDragon.class,p.getBoundingBox().inflate(96)).isEmpty()){
            BlockPos q=Eclipse.spot(p,18,30);if(q!=null){SynchroDragon d=(p.getRandom().nextBoolean()?Noctis.BLACK_ROSE.get():Noctis.STARDUST.get()).create(l);if(d!=null){d.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(d))l.addFreshEntity(d);}}
        }''')
# Two independent models with stepped petal blades vs silver crystalline fins.
N=256;S=4;W=N*S;models=[]
for rose in (True,False):
    cx=cy=rh=0;islands=[];lines=[]
    def cube(x,y,z,w,h,d,mat):
        global cx,cy,rh
        ww=2*(w+d);hh=h+d
        if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
        u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N,(mat,u,v)
        for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((fx,fy,fw,fh,mat,face))
        return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
    def part(var,parent,name,pos,rot,boxes):
        lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
    part('b','r','body',(0,9,0),(0,0,0),[(-5,-5,-7,10,9,15,'armor'),(-4,-4,-9,8,8,6,'plate')])
    parent='b'
    for i in range(5):
        part('neck'+str(i),parent,'neck'+str(i),(0,-3,-7) if i==0 else (0,0,-4),(-.34 if i<3 else .05,0,0),[(-2.5,-3,-5,5,6,6,'armor'),(-3,-3.5,-3,6,1,3,'plate')]);parent='neck'+str(i)
    part('h',parent,'head',(0,0,-4),(.35,0,0),[(-3,-3,-5,6,6,7,'armor'),(-2,-1,-9,4,3,6,'plate')])
    part('jaw','h','jaw',(0,1,-4),(0,0,0),[(-2,0,-5,4,2,5,'armor'),(-1.5,-1,-5,3,1,4,'claw')])
    for i,sign in enumerate((-1,1)):
        part('eye'+str(i),'h','eye'+str(i),(sign*2.8,-1.6,-3.7),(0,sign*.30,0),[(-.5,-.5,-1,1,1,2,'eye')])
        part('horn'+str(i),'h','horn'+str(i),(sign*2.6,-2,1),(-.8,0,sign*.35),[(-.5,-5,-.5,1,6,1,'plate')])
        part('wing'+str(i),'b','wing'+str(i),(sign*5,-3,0),(0,sign*.12,sign*.12),[(0 if sign>0 else -12,-1,-1,12,2,2,'armor')])
        for n in range(6):
            # separate overlapping blade panels taper at their ends
            length=12+n*2
            part(f'blade{i}{n}','wing'+str(i),f'blade{n}',(sign*(4+n*2),0,1+n*2),(0,sign*(n*.17-.25),sign*(.12+n*.045)),[(0 if sign>0 else -length,-1,0,length,2,5,'petal'),(sign*(length-3) if sign>0 else -length,-.5,1,3,1,3,'plate')])
        for n in range(3):
            part(f'petal{i}{n}','b',f'petal{i}{n}',(sign*(3+n*.7),-4+n*2,2+n*2),(0,sign*.4,sign*.5),[(0 if sign>0 else -6,-1,-2,6,2,5,'petal')])
        for j,z in enumerate((-6,6)):
            part(f'leg{i}{j}','b',f'leg{i}{j}',(sign*4,3,z),(0,0,sign*.12),[(-1.5,0,-1.5,3,6,3,'armor'),(-2,6,-3,4,2,5,'plate')])
            for n in range(3):part(f'claw{i}{j}{n}',f'leg{i}{j}',f'claw{n}',(-1+n,7,-3),(0,0,0),[(-.4,0,-2,1,1,3,'claw')])
    parent='b'
    for i in range(9):
        part('tail'+str(i),parent,'tail'+str(i),(0,0,7) if i==0 else (0,0,5),(.05,0,0),[(-1.5,-1.5,0,3 if i<5 else 2,3 if i<5 else 2,5,'armor'),(-2,-2,1,4,1,3,'plate')]);parent='tail'+str(i)
    part('tip',parent,'tip',(0,0,5),(0,0,0),[(-3,-1,0,6,2,6,'petal')])
    models.append('    static LayerDefinition mesh'+('0' if rose else '1')+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    palette={'armor':(40,24,38),'plate':(169,30,67),'petal':(193,31,76),'eye':(252,220,92),'claw':(113,83,111)} if rose else {'armor':(88,139,167),'plate':(207,229,238),'petal':(177,211,235),'eye':(148,65,220),'claw':(215,237,245)}
    pix=bytearray(W*W*4)
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=palette[mat];edge=min(u,v,1-u,1-v)
                g=.64+.34*math.sin(v*math.pi)+.12*math.sin(u*math.pi)
                if mat=='petal':g*=.7+.3*math.sin(v*math.pi);g+=.12*math.sin(u*22+v*5)**2
                if mat in ('armor','plate') and edge<.075:g*=.48
                if mat=='petal' and edge<.055:g*=.48
                if mat=='eye':g=1.25
                c=tuple(max(0,min(255,int(b*g))) for b in base)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*c,255))
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
    (assets/'textures/entity'/('black_rose_dragon.png' if rose else 'stardust_dragon.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(java/'SynchroClient.java').write_text('''package it.noctis.magic;
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
public class SynchroClient{
    static final ModelLayerLocation R=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"black_rose_dragon"),"main"),S=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"stardust_dragon"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(R,SynchroClient::mesh0);e.registerLayerDefinition(S,SynchroClient::mesh1);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.BLACK_ROSE.get(),c->new Renderer(c,true));e.registerEntityRenderer(Noctis.STARDUST.get(),c->new Renderer(c,false));}
'''+ '\n'.join(models)+'''
    static class Model extends EntityModel<SynchroDragon>{
        final ModelPart root,body,head,jaw;final ModelPart[] wings=new ModelPart[2],tail=new ModelPart[9],neck=new ModelPart[5];
        Model(ModelPart r){root=r;body=r.getChild("body");for(int i=0;i<2;i++)wings[i]=body.getChild("wing"+i);ModelPart p=body;for(int i=0;i<9;i++){p=p.getChild("tail"+i);tail[i]=p;}p=body;for(int i=0;i<5;i++){p=p.getChild("neck"+i);neck[i]=p;}head=p.getChild("head");jaw=head.getChild("jaw");}
        @Override public void setupAnim(SynchroDragon e,float limb,float amount,float age,float yaw,float pitch){
            boolean flying=!e.onGround()||e.isVehicle();float cast=e.casting(),flap=(float)Math.sin(age*(flying?.28:.10))*(flying?.58f:.12f);
            for(int i=0;i<2;i++){int sign=i==0?-1:1;wings[i].zRot=sign*(flap+(flying?.13f:.45f));for(int n=0;n<6;n++)wings[i].getChild("blade"+n).zRot=sign*(.12f+n*.045f+flap*.12f);
                for(int j=0;j<2;j++)body.getChild("leg"+i+j).xRot=flying?.45f:(float)Math.cos(limb*.65+(i+j)*Math.PI)*amount*.65f;}
            for(int i=0;i<5;i++){neck[i].xRot=(i<3?-.34f:.05f)-cast*.12f;neck[i].yRot=yaw*.003f;}
            head.xRot=.35f+pitch*.007f;jaw.xRot=cast*.55f;
            for(int i=0;i<9;i++){tail[i].yRot=(float)Math.sin(age*.11-i*.5)*.14f;tail[i].xRot=.05f+(float)Math.cos(age*.09-i*.5)*.07f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    }
    static class Renderer extends MobRenderer<SynchroDragon,Model>{final boolean rose;Renderer(EntityRendererProvider.Context c,boolean rose){super(c,new Model(c.bakeLayer(rose?R:S)),1.2f);this.rose=rose;}@Override protected void scale(SynchroDragon e,PoseStack p,float partial){p.scale(2.15f,2.15f,2.15f);}@Override public ResourceLocation getTextureLocation(SynchroDragon e){return new ResourceLocation(Noctis.ID,"textures/entity/"+(rose?"black_rose_dragon":"stardust_dragon")+".png");}}
}''',encoding='utf-8')
for n in ('black_rose_dragon','stardust_dragon'):(assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in [('black_rose_dragon','Drago Rosa Nera al Chiaro di Luna' if lang=='it_it' else 'Black Rose Moonlight Dragon'),('stardust_dragon','Drago Polvere di Stelle' if lang=='it_it' else 'Stardust Dragon')]:
        d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Two rideable flying Synchro dragons installed')
