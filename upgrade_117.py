"""1.1.7: Joker, Arsene, Phantom Thief calling-card challenge."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Joker>> JOKER=ENTITIES.register("joker",()->EntityType.Builder.<Joker>of(Joker::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(12).build(ID+":joker"));
    public static final RegistryObject<EntityType<Arsene>> ARSENE=ENTITIES.register("arsene",()->EntityType.Builder.<Arsene>of(Arsene::new,MobCategory.CREATURE).sized(1.4f,3.2f).clientTrackingRange(12).build(ID+":arsene"));
    public static final RegistryObject<Item> JOKER_EGG=ITEMS.register("joker_spawn_egg",()->new ForgeSpawnEggItem(JOKER,0x17171e,0xd5122b,new Item.Properties()));
    public static final RegistryObject<Item> CALLING_CARD=ITEMS.register("calling_card",()->new Item(new Item.Properties().stacksTo(1)));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(JOKER.get(),Joker.attributes().build());e.put(ARSENE.get(),Arsene.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'e.accept(JOKER_EGG.get());e.accept(CALLING_CARD.get());')
(java/'Joker.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.effect.*;
import net.minecraft.world.phys.Vec3;
public class Joker extends PathfinderMob{
    private int cd=20,speech,pose;
    private UUID persona;
    public Joker(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,140).add(Attributes.ARMOR,10).add(Attributes.ATTACK_DAMAGE,16).add(Attributes.MOVEMENT_SPEED,.34).add(Attributes.FOLLOW_RANGE,32);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(2,new LookAtPlayerGoal(this,Player.class,10));goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.8));}
    static boolean shadow(LivingEntity e){return e.isAlive()&&Eclipse.hostile(e)&&e.getMaxHealth()<100&&!(e instanceof Cthulhu);}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal("Joker: "+s));}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(!(p instanceof ServerPlayer sp)||!(level() instanceof ServerLevel l))return InteractionResult.SUCCESS;
        if(speech>0)return InteractionResult.CONSUME;speech=60;
        var data=Noctis.data(sp);int quest=data.getInt("PhantomChallenge");
        if(quest==0){
            data.putInt("PhantomChallenge",1);data.putInt("PhantomKills",0);
            ItemStack card=new ItemStack(Noctis.CALLING_CARD.get());if(!p.getInventory().add(card))p.drop(card,false);
            say(l,"Take your time. Elimina cinque Ombre e torna da me.");
        }else if(quest==1&&data.getInt("PhantomKills")>=5){
            data.putInt("PhantomChallenge",2);ItemStack reward=new ItemStack(Noctis.CRYSTAL.get(),4);if(!p.getInventory().add(reward))p.drop(reward,false);
            p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,6000,1));p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,6000,0));
            say(l,"Missione compiuta. Sei uno di noi, Phantom Thief!");
        }else if(quest==1){
            say(l,"Le Ombre non si sconfiggono da sole.");p.displayClientMessage(Component.literal("Calling Card: "+data.getInt("PhantomKills")+"/5"),true);
        }else say(l,"Looking cool! Ci vediamo, Phantom Thief.");
        return InteractionResult.CONSUME;
    }
    @Override public void tick(){
        super.tick();if(cd>0)cd--;if(speech>0)speech--;if(pose>0)pose--;
        if(!(level() instanceof ServerLevel l)||!isAlive()||cd>0)return;
        LivingEntity t=l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(20),Joker::shadow).stream().filter(this::hasLineOfSight).min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
        if(t==null){cd=20;return;}
        cd=75;getNavigation().stop();getLookControl().setLookAt(t,50,50);l.broadcastEntityEvent(this,(byte)90);
        Arsene a=persona==null?null:l.getEntity(persona) instanceof Arsene ar?ar:null;
        if(a==null||!a.isAlive()){
            a=Noctis.ARSENE.get().create(l);
            if(a!=null){a.moveTo(getX(),getY()+.5,getZ(),getYRot(),0);a.bind(this,t);
                if(l.addFreshEntity(a)){persona=a.getUUID();say(l,"Persona! Arsene!");l.sendParticles(ParticleTypes.SOUL_FIRE_FLAME,getX(),getY()+1,getZ(),45,.6,.8,.6,.08);}}
        }else a.bind(this,t);
        // Joker's own quick dagger strike only at close range.
        if(distanceTo(t)<3){t.hurt(damageSources().mobAttack(this),16);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,.8f,1.4f);}
    }
    @Override public void handleEntityEvent(byte id){if(id==90){pose=24;return;}super.handleEntityEvent(id);}
    public float summoning(){return pose<=0?0:(float)Math.sin(pose*Math.PI/24);}
}''',encoding='utf-8')
(java/'Arsene.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Arsene extends PathfinderMob{
    UUID owner,target;long expires;int cd=18,cast;
    public Arsene(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setNoGravity(true);}
    static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,180).add(Attributes.ARMOR,14).add(Attributes.MOVEMENT_SPEED,.35).add(Attributes.FOLLOW_RANGE,40).add(Attributes.KNOCKBACK_RESISTANCE,1);}
    @Override protected void registerGoals(){}
    public void bind(Joker j,LivingEntity t){owner=j.getUUID();target=t.getUUID();expires=j.level().getGameTime()+240;}
    @Override public void tick(){
        super.tick();if(cast>0)cast--;if(cd>0)cd--;
        if(!(level() instanceof ServerLevel l))return;
        if(owner==null||!(l.getEntity(owner) instanceof Joker j)||!j.isAlive()||l.getGameTime()>=expires){discard();return;}
        setNoGravity(true);
        LivingEntity t=target==null?null:l.getEntity(target) instanceof LivingEntity le?le:null;
        Vec3 goal=j.position().add(-Math.sin(Math.toRadians(j.getYRot()))*2,1.2,Math.cos(Math.toRadians(j.getYRot()))*2);
        Vec3 diff=goal.subtract(position());Vec3 v=diff.length()>1?diff.normalize().scale(.32):Vec3.ZERO;
        if(l.noCollision(this,getBoundingBox().move(v)))setDeltaMovement(getDeltaMovement().scale(.4).add(v.scale(.6)));else setDeltaMovement(Vec3.ZERO);
        if(t==null||!Joker.shadow(t)||distanceTo(t)>24||!hasLineOfSight(t)||cd>0)return;
        cd=40;Vec3 delta=t.position().subtract(position());float yaw=(float)(Math.atan2(delta.z,delta.x)*180/Math.PI)-90;setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);
        l.broadcastEntityEvent(this,(byte)91);
        Vec3 a=position().add(0,2.1,0),b=t.getEyePosition();
        for(int i=0;i<28;i++){Vec3 q=a.lerp(b,i/27.0);l.sendParticles(i%3==0?ParticleTypes.SOUL_FIRE_FLAME:ParticleTypes.SQUID_INK,q.x,q.y,q.z,3,.14,.14,.14,.025);}
        t.hurt(damageSources().mobAttack(this),26);t.addEffect(new MobEffectInstance(MobEffects.WITHER,80,0));t.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,100,0));
        playSound(SoundEvents.EVOKER_CAST_SPELL,1,.65f);
    }
    @Override public void handleEntityEvent(byte id){if(id==91){cast=20;return;}super.handleEntityEvent(id);}
    public float casting(){return cast<=0?0:(float)Math.sin(cast*Math.PI/20);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(owner!=null)t.putUUID("Owner",owner);if(target!=null)t.putUUID("Target",target);t.putLong("Expires",expires);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;target=t.hasUUID("Target")?t.getUUID("Target"):null;expires=t.getLong("Expires");}
}''',encoding='utf-8')
(java/'PhantomChallenge.java').write_text('''package it.noctis.magic;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class PhantomChallenge{
    @SubscribeEvent public static void defeat(LivingDeathEvent e){
        if(!(e.getSource().getEntity() instanceof ServerPlayer p)||!Joker.shadowForQuest(e.getEntity()))return;
        var d=Noctis.data(p);if(d.getInt("PhantomChallenge")!=1||d.getInt("PhantomKills")>=5)return;
        int k=d.getInt("PhantomKills")+1;d.putInt("PhantomKills",k);p.displayClientMessage(Component.literal("Calling Card: "+k+"/5"+(k==5?" - torna da Joker!":"")),true);
    }
}''',encoding='utf-8')
edit('Joker.java','    void say(ServerLevel l,String s)', '    static boolean shadowForQuest(LivingEntity e){return Eclipse.hostile(e)&&e.getMaxHealth()<100;}\\n    void say(ServerLevel l,String s)'.replace('\\n','\n'))
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!l.isDay()&&p.getRandom().nextInt(12)==0&&l.getEntitiesOfClass(Joker.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){Joker j=Noctis.JOKER.get().create(l);if(j!=null){j.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(j))l.addFreshEntity(j);}}
        }''')
# Distinct face-specific meshes: black swept hair, mask, red gloves, coat; Arsene top hat, claws, wings.
N=256;S=4;W=N*S;models=[]
def png(path,w,h,pix):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
for ars in (False,True):
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
    part('b','r','body',(0,0,0),(0,0,0),[(-3,-1,-2,6,11,4,'coat'),(-3,8,-2,6,4,4,'coat')])
    part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face')])
    for i,side in enumerate((-1,1)):
        part('arm'+str(i),'r','arm'+str(i),(side*4,0,0),(0,0,-side*.10),[(-1.5,-1,-1.5,3,8,3,'coat'),(-1.3,7,-1.3,3,4,3,'red')])
        part('leg'+str(i),'r','leg'+str(i),(side*2,12,0),(0,0,0),[(-1.5,0,-1.5,3,9,3,'coat'),(-1.5,9,-2.5,3,3,4,'boot')])
        part('tail'+str(i),'b','tail'+str(i),(side*2.2,8,1),(.15,0,side*.12),[(-2,0,-1,4,13,3,'coat' if not ars else 'red')])
        part('collar'+str(i),'b','collar'+str(i),(side*2.7,-1,-1),(0,0,side*.34),[(-.6,-2,-1,2,6,2,'lapel')])
        if ars:
            part('wing'+str(i),'b','wing'+str(i),(side*3,-1,2),(0,side*.22,side*.2),[(0 if side>0 else -12,-3,0,12,2,2,'boot')])
            for j in range(5):part(f'feather{i}{j}','wing'+str(i),f'feather{j}',(side*(3+j*2),-2+j*2,0),(0,side*.1,side*(.1+j*.09)),[(0 if side>0 else -(12-j),0,0,12-j,3+j,1,'wing')])
            for j in range(3):part(f'claw{i}{j}','arm'+str(i),f'claw{j}',(-1+j,11,-.5),(-.2,0,0),[(-.4,0,-.4,1,3,1,'boot')])
        else:
            part('lock'+str(i),'h','lock'+str(i),(side*3.4,-6,0),(0,0,side*.20),[(-1,0,-1,2,6,3,'hair')])
            for j in range(3):part(f'swept{i}{j}','h',f'swept{i}{j}',(side*(1+j),-7+j*.7,-2),(0,side*.2,side*(.45+j*.15)),[(-.7,-1,-1,2,4,3,'hair')])
    if ars:
        part('hat','h','hat',(0,-7,0),(0,0,.05),[(-5,-1,-5,10,1,10,'boot'),(-3,-7,-3,6,6,6,'boot'),(-3,-2,-3,6,1,6,'red')])
    else:
        part('hair','h','hair',(0,-7,0),(0,0,0),[(-4,-1,-3.5,8,2,7,'hair'),(-4,0,2.5,8,5,2,'hair')])
        for j in range(5):part('fringe'+str(j),'h','fringe'+str(j),(-3+j*1.4,-7,-3.5),(0,0,-.35+j*.15),[(-.6,0,-.5,2,2+j%3,1,'hair')])
        part('dagger','arm1','dagger',(0,11,-1),(0,0,.15),[(-.5,0,-.5,1,2,1,'boot'),(-1,2,-.5,2,1,1,'lapel'),(-.5,3,-.5,1,5,1,'lapel')])
    models.append('    static LayerDefinition mesh'+('A' if ars else 'J')+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    pal={'coat':(129,12,36) if ars else (22,24,30),'lapel':(183,182,188),'face':(42,32,39) if ars else (242,211,183),'red':(220,15,37),'boot':(18,16,22),'hair':(21,21,28),'wing':(38,19,34)}
    pix=bytearray(W*W*4)
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[mat];g=.70+.25*math.sin(u*math.pi)+.08*math.cos(v*8)
                c=tuple(int(z*g) for z in base)
                if mat=='hair':c=tuple(int(z*(.8+.8*math.sin(u*31+v*4)**2)) for z in base)
                if mat=='face' and face=='front':
                    for ex in (.27,.73):
                        dx=(u-ex)/.25;dy=(v-.47+(.5-ex)*dx*.22)/.24;d=dx*dx+dy*dy
                        if d<1 and not ars:c=(241,240,233)
                        if abs(dx)<.72 and abs(dy)<.42*(1-abs(dx)*.6):c=(23,20,28)
                        if abs(dx)<.34 and abs(dy)<.39:c=(220,19,40)
                        if abs(dx)<.12 and abs(dy)<.34:c=(20,16,22)
                        if (dx+.1)**2+(dy+.15)**2<.025:c=(255,244,235)
                    if .43<u<.65 and abs(v-.81+(u-.5)*.1)<.02 and not ars:c=(84,37,42)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,z)) for z in c],255))
    png(assets/'textures/entity'/('arsene.png' if ars else 'joker.png'),W,W,pix)
(java/'PhantomClient.java').write_text('''package it.noctis.magic;
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
public class PhantomClient{
    static final ModelLayerLocation J=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"joker"),"main"),A=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"arsene"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(J,PhantomClient::meshJ);e.registerLayerDefinition(A,PhantomClient::meshA);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.JOKER.get(),JRenderer::new);e.registerEntityRenderer(Noctis.ARSENE.get(),ARenderer::new);}
'''+ '\n'.join(models)+'''
    static class Model<T extends net.minecraft.world.entity.LivingEntity> extends EntityModel<T>{
        final ModelPart r,h,b;final boolean ars;
        Model(ModelPart r,boolean ars){this.r=r;this.ars=ars;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(T e,float limb,float amount,float age,float yaw,float pitch){
            float cast=e instanceof Joker j?j.summoning():e instanceof Arsene a?a.casting():0;h.yRot=yaw*.01745f;h.xRot=pitch*.01745f;
            for(int i=0;i<2;i++){int sign=i==0?-1:1;float walk=(float)Math.cos(limb*.6662+i*Math.PI)*amount;r.getChild("leg"+i).xRot=ars?.16f:walk*.7f;r.getChild("arm"+i).xRot=-walk*.7f-(ars?cast*1.3f:i==1?cast*1.8f:0);b.getChild("tail"+i).xRot=.15f+amount*.2f+(float)Math.sin(age*.12+i)*.07f+cast*.25f;if(ars)b.getChild("wing"+i).yRot=sign*(.22f+(float)Math.sin(age*.15)*.25f+cast*.3f);}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class JRenderer extends MobRenderer<Joker,Model<Joker>>{JRenderer(EntityRendererProvider.Context c){super(c,new Model<>(c.bakeLayer(J),false),.35f);}@Override public ResourceLocation getTextureLocation(Joker e){return new ResourceLocation(Noctis.ID,"textures/entity/joker.png");}}
    static class ARenderer extends MobRenderer<Arsene,Model<Arsene>>{ARenderer(EntityRendererProvider.Context c){super(c,new Model<>(c.bakeLayer(A),true),.65f);}@Override protected void scale(Arsene e,PoseStack p,float partial){p.scale(1.45f,1.45f,1.45f);}@Override public ResourceLocation getTextureLocation(Arsene e){return new ResourceLocation(Noctis.ID,"textures/entity/arsene.png");}}
}''',encoding='utf-8')
pix=bytearray(32*32*4)
for y in range(32):
    for x in range(32):
        if not(2<=x<30 and 6<=y<26):continue
        c=(213,17,38) if 4<=x<28 and 8<=y<24 else (20,19,25)
        if 11<=x<=21 and 10<=y<=21 and abs(x-16)+abs(y-15)<7:c=(242,240,226)
        if 12<=x<=20 and y in (14,15):c=(21,20,27)
        pix[(y*32+x)*4:(y*32+x)*4+4]=bytes((*c,255))
png(assets/'textures/item/calling_card.png',32,32,pix)
(assets/'models/item/calling_card.json').write_text('{"parent":"minecraft:item/generated","textures":{"layer0":"noctismagic:item/calling_card"}}')
(assets/'models/item/joker_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.joker']='Joker';d['entity.noctismagic.arsene']='Arsene';d['item.noctismagic.joker_spawn_egg']='Uovo generatore: Joker' if lang=='it_it' else 'Joker Spawn Egg';d['item.noctismagic.calling_card']='Calling Card - Phantom Thieves';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Joker and Arsene, Calling Card challenge installed')
