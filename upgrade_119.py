"""1.1.9: six rideable friendship ponies, pegasus and alicorn flight."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
ids=['twilight_sparkle','rainbow_dash','fluttershy','rarity','applejack','pinkie_pie']
labels=['Twilight Sparkle','Rainbow Dash','Fluttershy','Rarity','Applejack','Pinkie Pie']
regs=[n.upper() for n in ids]
palettes=[((160,112,200),(44,36,89),(229,73,164),(110,44,153)),((106,190,235),(232,60,61),(246,211,48),(192,59,135)),((249,225,130),(245,158,192),(250,192,216),(37,148,153)),((241,240,246),(93,44,146),(145,86,184),(50,105,206)),((238,157,67),(247,218,101),(255,239,158),(52,143,65)),((246,148,189),(224,42,127),(245,77,156),(54,147,213))]
decl=''
for n,r,(body,mane,accent,eye) in zip(ids,regs,palettes):
    a='0x%02x%02x%02x'%body;b='0x%02x%02x%02x'%mane
    decl+=f'public static final RegistryObject<EntityType<FriendshipPony>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<FriendshipPony>of(FriendshipPony::new,MobCategory.CREATURE).sized(1.05f,1.65f).clientTrackingRange(10).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{a},{b},new Item.Properties()));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG=';edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,''.join(f'e.put({r}.get(),FriendshipPony.attributes().build());' for r in regs)+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({r}_EGG.get());' for r in regs))
(java/'FriendshipPony.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class FriendshipPony extends TamableAnimal{
    private int speech,magic,pose;
    public FriendshipPony(EntityType<? extends TamableAnimal> t,Level l){super(t,l);setMaxUpStep(1f);}
    public int kind(){var t=getType();return t==Noctis.TWILIGHT_SPARKLE.get()?0:t==Noctis.RAINBOW_DASH.get()?1:t==Noctis.FLUTTERSHY.get()?2:t==Noctis.RARITY.get()?3:t==Noctis.APPLEJACK.get()?4:5;}
    public boolean winged(){return kind()<=2;}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,60).add(Attributes.MOVEMENT_SPEED,.32).add(Attributes.FOLLOW_RANGE,32);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));
        goalSelector.addGoal(2,new FollowOwnerGoal(this,1.1,6,2,false){@Override public boolean canUse(){return !isVehicle()&&super.canUse();}@Override public boolean canContinueToUse(){return !isVehicle()&&super.canContinueToUse();}});
        goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.75){@Override public boolean canUse(){return !isVehicle()&&super.canUse();}@Override public boolean canContinueToUse(){return !isVehicle()&&super.canContinueToUse();}});
        goalSelector.addGoal(4,new LookAtPlayerGoal(this,Player.class,8));
    }
    @Override public boolean isFood(ItemStack s){return s.is(Items.APPLE)||s.is(Items.CARROT)||s.is(Items.SUGAR);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        ItemStack s=p.getItemInHand(h);
        if(!isTame()&&isFood(s)){if(level() instanceof ServerLevel l){if(!p.getAbilities().instabuild)s.shrink(1);if(random.nextInt(3)==0||p.getAbilities().instabuild){tame(p);setPersistenceRequired();setHealth(getMaxHealth());l.broadcastEntityEvent(this,(byte)7);NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": Da oggi siamo amici!"));}else l.broadcastEntityEvent(this,(byte)6);}return InteractionResult.sidedSuccess(level().isClientSide);}
        if(isTame()&&isOwnedBy(p)){
            if(isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);heal(8);}return InteractionResult.sidedSuccess(level().isClientSide);}
            if(s.isEmpty()&&h==InteractionHand.MAIN_HAND){
                if(level() instanceof ServerLevel l){
                    if(p.isShiftKeyDown()){setOrderedToSit(!isOrderedToSit());getNavigation().stop();if(speech==0){speech=80;NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+(isOrderedToSit()?"Ti aspetto qui!":"Andiamo!")));}}
                    else{setOrderedToSit(false);setInSittingPose(false);getNavigation().stop();p.startRiding(this);if(speech==0){speech=80;String[] lines={"L'amicizia e' magia!","Pronto per un volo a tutta velocita'?","Oh... andiamo piano, per favore.","Che avventura deliziosa!","Su, abbiamo un sacco da fare!","Evviva! Una nuova avventura!"};NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+lines[kind()]));}}
                }return InteractionResult.sidedSuccess(level().isClientSide);
            }
        }return InteractionResult.PASS;
    }
    @Override public LivingEntity getControllingPassenger(){return getFirstPassenger() instanceof Player p&&isOwnedBy(p)?p:null;}
    @Override public double getPassengersRidingOffset(){return 1.10;}
    @Override public boolean causeFallDamage(float a,float b,net.minecraft.world.damagesource.DamageSource d){return !winged()&&super.causeFallDamage(a,b,d);}
    @Override public void travel(Vec3 v){
        if(isAlive()&&getControllingPassenger() instanceof Player rider){
            setYRot(rider.getYRot());yBodyRot=getYRot();yHeadRot=getYRot();setXRot(0);getNavigation().stop();
            if(winged()){
                setNoGravity(true);
                if(isControlledByLocalInstance()){
                    double yaw=Math.toRadians(rider.getYRot()),pitch=Math.toRadians(rider.getXRot()),f=rider.zza,side=rider.xxa;
                    Vec3 motion=new Vec3(-Math.sin(yaw)*Math.cos(pitch)*f+Math.cos(yaw)*side*.65,-Math.sin(pitch)*f,Math.cos(yaw)*Math.cos(pitch)*f+Math.sin(yaw)*side*.65);
                    if(motion.lengthSqr()>1)motion=motion.normalize();
                    setDeltaMovement(getDeltaMovement().scale(.70).add(motion.scale(kind()==1?.34:kind()==2?.19:.25)));
                    if(getDeltaMovement().lengthSqr()<.0002)setDeltaMovement(Vec3.ZERO);
                    move(MoverType.SELF,getDeltaMovement());calculateEntityAnimation(false);
                }else setDeltaMovement(Vec3.ZERO);
            }else{
                setNoGravity(false);setSpeed(kind()==4?.37f:.31f);
                if(isControlledByLocalInstance())super.travel(new Vec3(rider.xxa*.6,0,rider.zza<0?rider.zza*.5:rider.zza));else setDeltaMovement(Vec3.ZERO);
            }return;
        }
        if(isNoGravity())setNoGravity(false);
        super.travel(v);
    }
    @Override public void tick(){super.tick();if(speech>0)speech--;if(magic>0)magic--;if(pose>0)pose--;
        if(!(level() instanceof ServerLevel l)||!isTame()||isOrderedToSit())return;
        if(winged()&&!isVehicle()&&getOwner()!=null&&getOwner().getY()-getY()>3&&distanceTo(getOwner())<32){Vec3 v=getOwner().position().subtract(position()).normalize().scale(.28);if(l.noCollision(this,getBoundingBox().move(v)))setDeltaMovement(v);}
        if(kind()==1&&isVehicle()&&!onGround()&&tickCount%3==0)l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+.7,getZ(),3,.35,.2,.35,.015);
        if(kind()==2&&tickCount%80==0&&getOwner()!=null&&distanceTo(getOwner())<4&&getOwner().getHealth()<getOwner().getMaxHealth()){getOwner().heal(2);l.sendParticles(ParticleTypes.HEART,getX(),getY()+1,getZ(),3,.2,.2,.2,.01);}
    }
    public void power(ServerLevel l,Player p){
        if(magic>0||!isOwnedBy(p)||isOrderedToSit())return;magic=240;l.broadcastEntityEvent(this,(byte)93);
        switch(kind()){
            case 0->{for(LivingEntity e:l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(7),e->Eclipse.hostile(e)&&e.getMaxHealth()<100)){e.hurt(damageSources().magic(),12);e.addEffect(new MobEffectInstance(MobEffects.GLOWING,100,0));}p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,160,0));}
            case 1->p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,300,2));
            case 2->{p.heal(10);p.addEffect(new MobEffectInstance(MobEffects.REGENERATION,120,1));}
            case 3->{p.addEffect(new MobEffectInstance(MobEffects.LUCK,600,1));p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,600,0));}
            case 4->{p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,300,1));p.addEffect(new MobEffectInstance(MobEffects.SATURATION,20,0));}
            default->{p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,300,0));p.addEffect(new MobEffectInstance(MobEffects.JUMP,300,1));}
        }
        l.sendParticles(kind()==5?ParticleTypes.HAPPY_VILLAGER:kind()==2?ParticleTypes.HEART:ParticleTypes.END_ROD,getX(),getY()+1,getZ(),40,.6,.6,.6,.06);playSound(SoundEvents.AMETHYST_BLOCK_CHIME,1,1.3f);
    }
    @Override public void handleEntityEvent(byte id){if(id==93){pose=24;return;}super.handleEntityEvent(id);}
    public float casting(){return pose<=0?0:(float)Math.sin(pose*Math.PI/24);}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob a){return null;}
    @Override public boolean canMate(Animal a){return false;}
}''',encoding='utf-8')
(java/'PonyEvents.java').write_text('''package it.noctis.magic;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Items;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class PonyEvents{
    @SubscribeEvent public static void power(PlayerInteractEvent.RightClickItem e){
        if(e.getEntity() instanceof ServerPlayer p&&e.getItemStack().is(Items.BLAZE_ROD)&&p.getVehicle() instanceof FriendshipPony pony)pony.power(p.serverLevel(),p);
    }
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(l.isDay()&&p.getRandom().nextInt(18)==0&&l.getEntitiesOfClass(FriendshipPony.class,p.getBoundingBox().inflate(64)).size()<2){
            BlockPos q=Eclipse.spot(p,10,22);if(q!=null){int k=p.getRandom().nextInt(6);
                FriendshipPony pony=(switch(k){case 0->Noctis.TWILIGHT_SPARKLE.get();case 1->Noctis.RAINBOW_DASH.get();case 2->Noctis.FLUTTERSHY.get();case 3->Noctis.RARITY.get();case 4->Noctis.APPLEJACK.get();default->Noctis.PINKIE_PIE.get();}).create(l);
                if(pony!=null){pony.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(pony))l.addFreshEntity(pony);}
            }
        }''')
# Six individually sculpted cartoon pony silhouettes; no humanoid base.
N=256;S=4;W=N*S;models=[]
for k in range(6):
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
    part('b','r','body',(0,12,0),(0,0,0),[(-4,-4,-6,8,8,13,'body'),(-3,-7,-7,6,7,5,'body')])
    part('h','r','head',(0,4,-6),(0,0,0),[(-4,-6,-5,8,9,8,'face'),(-3,0,-7,6,4,4,'muzzle')])
    for i,side in enumerate((-1,1)):
        part('ear'+str(i),'h','ear'+str(i),(side*3,-5,0),(0,0,side*.20),[(-1,-4,-1,2,4,2,'body'),(-.5,-3,-1.2,1,2,1,'inner')])
        for j,z in enumerate((-4,5)):
            part(f'leg{i}{j}','r',f'leg{i}{j}',(side*2.7,15,z),(0,0,0),[(-1.4,-1,-1.4,3,5,3,'body'),(-1.6,4,-1.7,3,5,4,'hoof')])
        if k<=2:
            part('wing'+str(i),'b','wing'+str(i),(side*4,-2,0),(0,0,side*.2),[(0 if side>0 else -6,-1,-2,6,2,5,'body')])
            for j in range(5):
                length=7-j
                part(f'feather{i}{j}','wing'+str(i),f'feather{j}',(side*(2+j*.6),0,-2+j*1.5),(0,side*(.15+j*.09),side*.15),[(0 if side>0 else -length,-.4,0,length,1,2,'feather')])
    if k in (0,3):part('horn','h','horn',(0,-6,-3),(-.16,0,0),[(-1,-3,-1,2,3,2,'body'),(-.5,-5,-.5,1,2,1,'body')])
    if k==4:part('hat','h','hat',(0,-6,0),(0,0,.08),[(-5,-1,-5,10,1,9,'hat'),(-3,-4,-3,6,3,6,'hat'),(-3,-1.7,-3,6,1,6,'accent')])
    # Mane and tail silhouettes: straight, swept, flowing, curled, tied or fluffy.
    for j in range(5):
        lengths=[5,4,9,6,7,4];length=lengths[k]+(j%2)*2
        part('mane'+str(j),'h','mane'+str(j),(-3+j*1.45,-6,-1),(0,0,(j-2)*(.12 if k!=5 else .3)),[(-.8,-1,-2,2,3,5,'mane'+str(j)),(-.8,1,1,2,length,2,'mane'+str(j))])
    if k in (2,3,5):
        part('sideMane','h','sideMane',(3.5,-4,-1),(0,0,-.18),[(-1,0,-1,2,9 if k==2 else 6,3,'mane2'),(-1,6,0,3,3,3,'mane3')])
    part('tail','b','tail',(0,-1,7),(-.35,0,0),[(-2,-1,0,4,4,5,'mane0')])
    part('tip','tail','tip',(0,1,4),(.55,0,0),[(-2,-1,0,4,4,6,'mane2'),(-1.5,1,5,3,4,3,'mane4')])
    if k==4:part('tie','tail','tie',(0,1,5),(0,0,0),[(-2,-1,-1,4,3,1,'accent')])
    models.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    body,mane,accent,eye=palettes[k];pix=bytearray(W*W*4)
    rainbow=[(234,67,67),(250,152,56),(252,218,55),(80,183,106),(71,119,226),(158,82,195)]
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=body
                if mat.startswith('mane'):base=rainbow[(int(mat[-1])+int(u*2))%6] if k==1 else accent if k==0 and (.27<u<.44 or .60<u<.67) else accent if k in (2,3,5) and .25<u<.42 else mane
                elif mat=='accent':base=accent
                elif mat=='hat':base=(131,83,43)
                elif mat=='inner':base=tuple(int(a*.82) for a in body)
                elif mat=='hoof':base=tuple(int(a*.91) for a in body)
                g=.80+.17*math.sin(u*math.pi)+.04*math.cos(v*5)
                c=tuple(int(a*g) for a in base)
                if mat=='face' and face in ('front','left','right'):
                    centers=(.24,.76) if face=='front' else (.45,)
                    for ex in centers:
                        dx=(u-ex)/(.22 if face=='front' else .39);dy=(v-.57)/.35;d=dx*dx+dy*dy
                        if d<1:c=(45,32,54)
                        if d<.88:c=(255,253,250)
                        if d<.81 and abs(dx)<.52:c=eye
                        if d<.73 and abs(dx)<.24:c=(30,22,43)
                        if (dx+.16)**2+(dy+.34)**2<.09:c=(255,255,255)
                        if (dx-.19)**2+(dy-.31)**2<.025:c=(255,255,255)
                if mat=='muzzle' and face=='front' and .72<v<.78 and abs(u-.5)<.20:c=tuple(int(a*.54) for a in body)
                # Cutie marks on both flanks of the main body, small colored symbols.
                if mat=='body' and w==13 and h==8 and face in ('left','right'):
                    a=(u-.76)*3.8;b=(v-.59)*3.5
                    if abs(a)<.65 and abs(b)<.65:
                        if k==0 and (abs(a)<.15 or abs(b)<.15 or abs(abs(a)-abs(b))<.12):c=(216,58,150)
                        if k==1 and abs(a+.35*b)<.25 and abs(b)<.6:c=(235,61,49) if b<0 else (246,217,48)
                        if k in (2,4,5):
                            for ax,by in ((-.30,-.28),(.30,-.28),(0,.27)):
                                if (a-ax)**2+(b-by)**2<.065:c=(221,65,126) if k==2 else (218,47,46) if k==4 else (66,158,222)
                        if k==3 and abs(a)+abs(b)<.56:c=(70,160,235)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,z)) for z in c],255))
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
    (assets/'textures/entity'/f'{ids[k]}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(java/'PonyClient.java').write_text('''package it.noctis.magic;
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
public class PonyClient{
    static final String[] N={'''+','.join(json.dumps(n) for n in ids)+'''};
    static final ModelLayerLocation[] L=new ModelLayerLocation[6];
    static{for(int i=0;i<6;i++)L[i]=new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[i]),"main");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){'''+''.join(f'e.registerLayerDefinition(L[{i}],PonyClient::mesh{i});' for i in range(6))+'''}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){'''+''.join(f'e.registerEntityRenderer(Noctis.{r}.get(),c->new Renderer(c,{i}));' for i,r in enumerate(regs))+'''}
'''+ '\n'.join(models)+'''
    static class Model extends EntityModel<FriendshipPony>{
        final ModelPart r,h,b,tail;final int k;
        Model(ModelPart r,int k){this.r=r;this.k=k;h=r.getChild("head");b=r.getChild("body");tail=b.getChild("tail");}
        @Override public void setupAnim(FriendshipPony e,float limb,float amount,float age,float yaw,float pitch){
            boolean flight=e.winged()&&!e.onGround(),sit=e.isInSittingPose();h.yRot=yaw*.012f;h.xRot=pitch*.009f-e.casting()*.15f;h.y=sit?7:4;b.y=sit?15:12;tail.yRot=(float)Math.sin(age*.13)*.24f+amount*.14f;tail.xRot=-.35f-amount*.2f;
            for(int j=0;j<5;j++)h.getChild("mane"+j).xRot=(float)Math.sin(age*.10+j*.6)*.065f+amount*.11f;
            for(int i=0;i<2;i++){int sign=i==0?-1:1;h.getChild("ear"+i).zRot=sign*(.20f+(float)Math.sin(age*.11+i)*.06f);
                for(int j=0;j<2;j++){ModelPart leg=r.getChild("leg"+i+j);leg.xRot=sit?(j==0?-.6f:1.0f):flight?.35f:(float)Math.cos(limb*.66+(i+j)*Math.PI)*amount*.75f;}
                if(k<=2){ModelPart w=b.getChild("wing"+i);w.zRot=sign*(flight?(float)Math.sin(age*.35)*.75f:.85f);w.yRot=sign*(flight?.1f:.65f);}
            }
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<FriendshipPony,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.48f);this.k=k;}@Override public ResourceLocation getTextureLocation(FriendshipPony e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''',encoding='utf-8')
for n in ids:(assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in zip(ids,labels):
        d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Six Friendship Ponies, three flying mounts and six special powers installed')
