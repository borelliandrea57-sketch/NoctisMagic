"""1.1.1: tameable Xenomorph, high-resolution Ophanim eyes."""
from pathlib import Path
import sys,math,random,struct,zlib,json
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Xenomorph>> XENOMORPH=ENTITIES.register("xenomorph",()->EntityType.Builder.<Xenomorph>of(Xenomorph::new,MobCategory.CREATURE).sized(.85f,2.4f).clientTrackingRange(10).build(ID+":xenomorph"));
    public static final RegistryObject<Item> XENOMORPH_EGG=ITEMS.register("xenomorph_spawn_egg",()->new ForgeSpawnEggItem(XENOMORPH,0x161b20,0x69825d,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(XENOMORPH.get(),Xenomorph.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'e.accept(XENOMORPH_EGG.get());')
(java/'Xenomorph.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
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
public class Xenomorph extends TamableAnimal{
    private int strike,acid;
    public Xenomorph(EntityType<? extends TamableAnimal> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,100).add(Attributes.ATTACK_DAMAGE,19).add(Attributes.ARMOR,9).add(Attributes.MOVEMENT_SPEED,.35).add(Attributes.FOLLOW_RANGE,32).add(Attributes.KNOCKBACK_RESISTANCE,.6);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));goalSelector.addGoal(2,new MeleeAttackGoal(this,1.3,true));
        goalSelector.addGoal(3,new FollowOwnerGoal(this,1.2,7,2,false));goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(5,new LookAtPlayerGoal(this,Player.class,8));
        targetSelector.addGoal(1,new OwnerHurtByTargetGoal(this));targetSelector.addGoal(2,new OwnerHurtTargetGoal(this));
        targetSelector.addGoal(3,new NearestAttackableTargetGoal<net.minecraft.world.entity.monster.Monster>(this,net.minecraft.world.entity.monster.Monster.class,10,true,false,m->isTame()&&!isOrderedToSit()&&Eclipse.hostile(m)));
    }
    @Override public boolean wantsToAttack(LivingEntity target,LivingEntity owner){return Eclipse.hostile(target);}
    @Override public boolean isFood(ItemStack s){return s.is(Items.RAW_BEEF)||s.is(Items.BEEF)||s.is(Items.CHICKEN)||s.is(Items.PORKCHOP)||s.is(Items.MUTTON)||s.is(Items.ROTTEN_FLESH);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        ItemStack s=p.getItemInHand(h);
        if(!isTame()&&isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);if(random.nextInt(3)==0){tame(p);setPersistenceRequired();setHealth(getMaxHealth());level().broadcastEntityEvent(this,(byte)7);}else level().broadcastEntityEvent(this,(byte)6);}return InteractionResult.sidedSuccess(level().isClientSide);}
        if(isTame()&&isOwnedBy(p)){if(isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);heal(12);}return InteractionResult.sidedSuccess(level().isClientSide);}if(s.isEmpty()){if(!level().isClientSide){setOrderedToSit(!isOrderedToSit());getNavigation().stop();setTarget(null);}return InteractionResult.sidedSuccess(level().isClientSide);}}
        return InteractionResult.PASS;
    }
    @Override public boolean doHurtTarget(Entity e){
        if(!isTame()||!(e instanceof LivingEntity le)||!Eclipse.hostile(le))return false;
        boolean hit=super.doHurtTarget(e);if(hit&&level() instanceof ServerLevel l){l.broadcastEntityEvent(this,(byte)83);playSound(SoundEvents.SPIDER_HURT,.7f,.55f);}return hit;
    }
    @Override public void tick(){super.tick();if(strike>0)strike--;if(acid>0)acid--;if(!(level() instanceof ServerLevel l)||!isTame()||isOrderedToSit())return;
        LivingEntity v=getTarget();if(v==null||!v.isAlive()||!Eclipse.hostile(v)||acid>0||distanceTo(v)>7||!hasLineOfSight(v))return;
        acid=110;Vec3 a=getEyePosition(),b=v.getEyePosition();for(int i=0;i<14;i++){Vec3 q=a.lerp(b,i/13.0);l.sendParticles(ParticleTypes.SNEEZE,q.x,q.y,q.z,2,.12,.12,.12,.03);}
        v.hurt(damageSources().mobAttack(this),8);v.addEffect(new MobEffectInstance(MobEffects.POISON,100,0));l.broadcastEntityEvent(this,(byte)83);
    }
    @Override public void handleEntityEvent(byte id){if(id==83){strike=14;return;}super.handleEntityEvent(id);}
    public float attackPose(){return strike<=0?0:(float)Math.sin(strike*Math.PI/14);}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob a){return null;}
    @Override public boolean canMate(Animal a){return false;}
}'''.replace('s.is(Items.RAW_BEEF)||',''),encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!l.isDay()&&p.getRandom().nextInt(18)==0&&l.getEntitiesOfClass(Xenomorph.class,p.getBoundingBox().inflate(64)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){Xenomorph x=Noctis.XENOMORPH.get().create(l);if(x!=null){x.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(x))l.addFreshEntity(x);}}
        }''')
# Xenomorph mesh: custom UV for each piece, biomechanical silhouette.
N=256;S=4;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((fx,fy,fw,fh,mat,face))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
part('b','r','body',(0,0,0),(.12,0,0),[(-3,-4,-2,6,9,5,'rib'),(-2,5,-1.5,4,5,3,'rib'),(-3,10,-2,6,3,4,'armor')])
part('h','b','head',(0,-4,-1),(-.15,0,0),[(-2.5,-5,-5,5,4,13,'dome'),(-3,-4,-4,6,3,9,'dome'),(-2,-1,-5,4,2,6,'jaw')])
part('jaw','h','jaw',(0,0,-4),(.12,0,0),[(-2,0,-2,4,2,5,'jaw'),(-1.5,-.5,-2.5,3,1,1,'teeth')])
part('inner','jaw','inner',(0,0,-2),(0,0,0),[(-.7,-.5,-3,1,1,4,'jaw'),(-.8,-.6,-3.5,2,1,1,'teeth')])
for i,side in enumerate((-1,1)):
    for n in range(3):part(f'pipe{i}{n}','b',f'pipe{i}{n}',(side*(2+n*.65),-2+n*2,2),(-.7,0,side*.23),[(-.7,-5,-.7,1,6,2,'armor')])
    part('a'+str(i),'b','arm'+str(i),(side*4,-3,0),(0,0,-side*.15),[(-1.5,-1,-1.5,3,7,3,'armor')])
    part('f'+str(i),'a'+str(i),'fore'+str(i),(0,6,0),(-.25,0,0),[(-1,0,-1,2,7,2,'rib')])
    for n in range(3):part(f'claw{i}{n}','f'+str(i),f'claw{n}',(-1+n,7,0),(-.25,0,0),[(-.3,0,-.4,1,3,1,'claw')])
    part('l'+str(i),'r','leg'+str(i),(side*2,12,0),(-.15,0,0),[(-1.5,0,-1.5,3,6,3,'armor')])
    part('s'+str(i),'l'+str(i),'shin'+str(i),(0,6,0),(.45,0,0),[(-1,0,-1,2,5,2,'rib'),(-1.5,5,-3,3,1,4,'claw')])
parent='b'
for i in range(9):
    part('tail'+str(i),parent,'tail'+str(i),(0,10,2.5) if i==0 else (0,0,4),(-.22 if i<4 else .10,0,0),[(-1 if i<5 else -.5,-1 if i<5 else -.5,0,2 if i<5 else 1,2 if i<5 else 1,4,'rib')])
    parent='tail'+str(i)
part('tip',parent,'tip',(0,0,4),(.4,0,0),[(-.5,-.5,0,1,1,4,'claw'),(-.5,-2,2,1,2,2,'claw')])
(java/'XenoClient.java').write_text('''package it.noctis.magic;
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
public class XenoClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"xenomorph"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,XenoClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.XENOMORPH.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<Xenomorph>{
        final ModelPart root,body,head,jaw,inner;final ModelPart[] arms=new ModelPart[2],legs=new ModelPart[2],tail=new ModelPart[9];
        Model(ModelPart r){root=r;body=r.getChild("body");head=body.getChild("head");jaw=head.getChild("jaw");inner=jaw.getChild("inner");for(int i=0;i<2;i++){arms[i]=body.getChild("arm"+i);legs[i]=r.getChild("leg"+i);}ModelPart p=body;for(int i=0;i<9;i++){p=p.getChild("tail"+i);tail[i]=p;}}
        @Override public void setupAnim(Xenomorph e,float limb,float amount,float age,float yaw,float pitch){
            float hit=e.attackPose();boolean sit=e.isInSittingPose();body.xRot=sit?.38f:.12f+hit*.24f;body.y=sit?5:0;head.yRot=yaw*.01745f;head.xRot=-.15f+pitch*.012f;jaw.xRot=.12f+hit*.65f;inner.z=-2-hit*2.8f;
            for(int i=0;i<2;i++){float walk=(float)Math.cos(limb*.65+i*Math.PI)*amount;arms[i].xRot=-walk*.6f-hit*1.0f;legs[i].xRot=sit?-1.25f:walk*.85f;legs[i].getChild("shin"+i).xRot=sit?1.6f:.45f+Math.max(0,-walk)*.4f;}
            for(int i=0;i<9;i++){tail[i].yRot=(float)Math.sin(age*.17-i*.53)*(.16f+amount*.16f);tail[i].xRot=(i<4?-.22f:.1f)+(float)Math.cos(age*.11-i*.4)*.07f-hit*.15f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    }
    static class Renderer extends MobRenderer<Xenomorph,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.45f);}@Override protected void scale(Xenomorph e,PoseStack p,float partial){p.scale(1.24f,1.24f,1.24f);}@Override public ResourceLocation getTextureLocation(Xenomorph e){return new ResourceLocation(Noctis.ID,"textures/entity/xenomorph.png");}}
}''',encoding='utf-8')
def png(path,w,h,pix):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
pix=bytearray(W*W*4)
for x,y,w,h,mat,face in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);shine=math.exp(-((u-.33)/.17)**2);ridge=math.sin(v*math.pi*9)**2
            if mat=='dome':c=(int(12+65*shine),int(18+77*shine),int(23+85*shine))
            elif mat=='teeth':c=(int(130+90*shine),int(145+85*shine),int(143+85*shine))
            elif mat=='claw':c=(int(20+78*shine),int(23+77*shine),int(24+76*shine))
            else:
                k=16+35*shine+(25*ridge if mat=='rib' else 10*math.sin(u*math.pi*5)**2)
                c=(int(k*.86),int(k),int(k*1.12))
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/xenomorph.png',W,W,pix)
# Replace the old low-resolution Ophanim gold and eyes with 2048 x 1024 atlas, same UVs.
W=2048;H=1024;S=16;pix=bytearray(W*H*4)
for y in range(H):
    for x in range(W):
        u=x/S;v=y/S;g=.75+.15*math.sin(u*.65)+.10*math.cos(v*1.5)
        c=(int(190*g),int(141*g),int(52*g));off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
def eye(x,y,w,h,seed):
    for j in range(h*S):
        for i in range(w*S):
            u=(i+.5)/(w*S)*2-1;v=(j+.5)/(h*S)*2-1
            almond=abs(v)/(max(.04,1-u*u)**.6)
            rr=math.sqrt((u/.49)**2+(v/.83)**2);a=math.atan2(v/.83,u/.49)
            c=(92,54,25)
            if almond<.89 and abs(u)<.96:
                c=(int(244-40*abs(u)),int(232-43*abs(u)),int(214-36*abs(u)))
                if abs(v)>.55 and math.sin(u*37+v*15)>.94:c=(181,112,101)
                if rr<1:
                    fib=.5+.5*math.sin(a*45+rr*14+seed)
                    g=.40+.45*fib
                    c=(int(99+145*g),int(48+135*g),int(22+60*g))
                    if rr>.85:c=(80,42,21)
                    if rr<.35:c=(11,9,16)
                    if (u+.13)**2+(v+.26)**2<.017:c=(255,251,233)
                    if (u-.14)**2+(v-.19)**2<.004:c=(255,228,162)
            if .89<=almond<1.10:c=(43,23,23)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*c,255))
for x in (65,72):eye(x,1,6,5,x)
for x in (85,90):eye(x,1,4,4,x)
for x in (1,12):eye(x,23,10,8,x)
png(assets/'textures/entity/ophanim.png',W,H,pix)
p=java/'Client.java';s=p.read_text(encoding='utf-8')
# The existing ring motion stays intact; add staggered blinking to each individual eye.
needle='else if(kind==7){for(int i=0;i<3;i++){ModelPart ring=root.getChild("ring"+i);'
if needle in s:
    s=s.replace(needle,needle+'''for(int j=0;j<12+i*4;j++){ModelPart seg=ring.getChild("segment"+j);float phase=(age+j*13+i*29)%137;float blink=phase<7?.13f+.87f*(float)Math.abs(phase-3.5f)/3.5f:1f;seg.getChild("eye").yScale=blink;seg.getChild("outerEye").yScale=blink;}''',1)
    p.write_text(s,encoding='utf-8')
else:print('Ophanim blink anchor not found; high-resolution eyes retained')
(assets/'models/item/xenomorph_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.xenomorph']='Xenomorfo' if lang=='it_it' else 'Xenomorph';d['item.noctismagic.xenomorph_spawn_egg']='Uovo generatore: Xenomorfo' if lang=='it_it' else 'Xenomorph Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Xenomorph companion and detailed Ophanim eye atlas installed')
