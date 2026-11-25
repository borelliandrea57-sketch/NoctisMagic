"""1.1.8: Morgana name-tag dialogue, motorcycle Shadow and weather-evolving Metal Sonic."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<SonicGuest>> SHADOW=ENTITIES.register("shadow",()->EntityType.Builder.<SonicGuest>of(SonicGuest::new,MobCategory.CREATURE).sized(1.15f,1.65f).clientTrackingRange(10).build(ID+":shadow"));
    public static final RegistryObject<EntityType<SonicGuest>> METAL_SONIC=ENTITIES.register("metal_sonic",()->EntityType.Builder.<SonicGuest>of(SonicGuest::new,MobCategory.CREATURE).sized(.7f,1.65f).clientTrackingRange(10).build(ID+":metal_sonic"));
    public static final RegistryObject<Item> SHADOW_EGG=ITEMS.register("shadow_spawn_egg",()->new ForgeSpawnEggItem(SHADOW,0x1b1b20,0xc51e32,new Item.Properties()));
    public static final RegistryObject<Item> METAL_SONIC_EGG=ITEMS.register("metal_sonic_spawn_egg",()->new ForgeSpawnEggItem(METAL_SONIC,0x2149b9,0xf1cd48,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(SHADOW.get(),SonicGuest.attributes().build());e.put(METAL_SONIC.get(),SonicGuest.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(SHADOW_EGG.get());e.accept(METAL_SONIC_EGG.get());')
(java/'Morgana.java').write_text('''package it.noctis.magic;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.animal.Cat;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class Morgana{
    static boolean named(Cat c){return c.hasCustomName()&&c.getCustomName().getString().trim().equalsIgnoreCase("Morgana");}
    static void say(Cat c,ServerPlayer p,boolean night){
        ServerLevel l=p.serverLevel();var d=c.getPersistentData();long now=l.getGameTime();
        if(d.getLong("MorganaTalkUntil")>now||p.getPersistentData().getLong("MorganaReminderUntil")>now)return;
        d.putLong("MorganaTalkUntil",now+1200);p.getPersistentData().putLong("MorganaReminderUntil",now+1200);
        String[] lines=night?new String[]{"E' tardi. Dovresti andare a dormire!","Oggi hai fatto abbastanza. A letto!","Niente altre avventure stanotte, vai a dormire!"}:new String[]{"Non sono un gatto!","Mi chiamo Morgana, ricordalo.","Riposa un po', ti servira' energia."};
        NpcDialogue.say(l,Component.literal("Morgana: "+lines[c.getRandom().nextInt(lines.length)]));
    }
    @SubscribeEvent public static void interact(PlayerInteractEvent.EntityInteract e){
        if(e.getHand()==InteractionHand.MAIN_HAND&&e.getEntity() instanceof ServerPlayer p&&e.getTarget() instanceof Cat c&&named(c)&&e.getItemStack().isEmpty())say(c,p,!p.serverLevel().isDay());
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent e){
        if(!(e.getEntity() instanceof Cat c)||!(c.level() instanceof ServerLevel l)||c.tickCount%100!=0||!named(c)||l.dimension()!=Level.OVERWORLD||l.isDay())return;
        if(c.isTame()&&c.getOwner() instanceof ServerPlayer p&&p.distanceTo(c)<16&&!p.isSleeping())say(c,p,true);
        else if(!c.isTame()&&l.getNearestPlayer(c,8) instanceof ServerPlayer p&&!p.isSleeping())say(c,p,true);
    }
}''',encoding='utf-8')
(java/'SonicGuest.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
public class SonicGuest extends PathfinderMob{
    static final EntityDataAccessor<Boolean> NEO=SynchedEntityData.defineId(SonicGuest.class,EntityDataSerializers.BOOLEAN);
    int speech,hit;
    public SonicGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setMaxUpStep(1);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(NEO,false);}
    public boolean shadow(){return getType()==Noctis.SHADOW.get();}
    public boolean neo(){return !shadow()&&entityData.get(NEO);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,100).add(Attributes.ARMOR,9).add(Attributes.ATTACK_DAMAGE,12).add(Attributes.MOVEMENT_SPEED,.34).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.15,true));goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,1.0));goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(4,new RandomLookAroundGoal(this));targetSelector.addGoal(1,new HurtByTargetGoal(this));}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l&&speech==0){speech=100;String[] lines=shadow()?new String[]{"Non ho fretta. Sto solo facendo un giro.","Chaos Control? Oggi no.","Bella moto, vero?"}:neo()?new String[]{"Forma Neo attiva. Nessuna ostilita' rilevata.","Energia atmosferica acquisita."}:new String[]{"...","Diagnostica completata. Nessuna minaccia.","Modalita' riposo."};
            NpcDialogue.say(l,Component.literal((shadow()?"Shadow":neo()?"Neo Metal Sonic":"Metal Sonic")+": "+lines[random.nextInt(lines.length)]));}
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void tick(){
        super.tick();if(speech>0)speech--;if(hit>0)hit--;
        if(!(level() instanceof ServerLevel l)||tickCount%20!=0)return;
        if(!shadow()){
            boolean storm=l.dimension()==Level.OVERWORLD&&(l.isRaining()||l.isThundering());
            if(storm!=neo()){
                entityData.set(NEO,storm);getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(storm?23:12);getAttribute(Attributes.ARMOR).setBaseValue(storm?16:9);getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(storm?.40:.34);
                l.sendParticles(ParticleTypes.ELECTRIC_SPARK,getX(),getY()+1,getZ(),45,.6,.9,.6,.12);playSound(SoundEvents.BEACON_ACTIVATE,.8f,storm?.65f:1.3f);
                NpcDialogue.say(l,Component.literal(storm?"Metal Sonic: Energia atmosferica assorbita. NEO METAL SONIC!":"Metal Sonic: Ritorno alla forma standard."));
            }
        }
        if(getTarget()!=null&&(!getTarget().isAlive()||distanceTo(getTarget())>20)){setTarget(null);getNavigation().stop();}
        if(shadow()&&getDeltaMovement().horizontalDistanceSqr()>.01)l.sendParticles(ParticleTypes.SMOKE,getX(),getY()+.25,getZ(),2,.15,.1,.15,.015);
    }
    @Override public boolean doHurtTarget(Entity e){boolean ok=super.doHurtTarget(e);if(ok&&level() instanceof ServerLevel l){l.broadcastEntityEvent(this,(byte)92);l.sendParticles(neo()?ParticleTypes.ELECTRIC_SPARK:ParticleTypes.CRIT,e.getX(),e.getY()+.8,e.getZ(),12,.2,.3,.2,.05);}return ok;}
    @Override public void handleEntityEvent(byte id){if(id==92){hit=12;return;}super.handleEntityEvent(id);}
    public float attacking(){return hit<=0?0:(float)Math.sin(hit*Math.PI/12);}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(p.getRandom().nextInt(20)==0&&l.getEntitiesOfClass(SonicGuest.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){SonicGuest m=(p.getRandom().nextBoolean()?Noctis.SHADOW.get():Noctis.METAL_SONIC.get()).create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }''')
# Three independent meshes, same common limb names for animation. Shadow's motorcycle is part of his model.
N=256;S=4;W=N*S;models=[]
for k in range(3):
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
    part('body','r','body',(0,5 if k else 2,0),(0,0,0),[(-3,-1,-2,6,7,5,'shell'),(-2,0,-2.7,4,4,1,'core')])
    part('head','body','head',(0,-1,0),(0,0,0),[(-4,-8,-4,8,7,8,'face'),(-3,-9,-3,6,2,6,'shell'),(-4,-3,-5,8,3,3,'muzzle')])
    if k==0:part('nose','head','nose',(0,-3,-6.3),(0,0,0),[(-.8,-.7,-.4,2,1,1,'dark')])
    for i,side in enumerate((-1,1)):
        part('ear'+str(i),'head','ear'+str(i),(side*3,-7,0),(0,0,side*.25),[(-1,-3,-1,2,4,2,'shell'),(-.7,-2,-1.2,1,2,1,'inner')])
        for j in range(3):
            length=(7+j*2 if k==2 else 5+j)
            part(f'spike{i}{j}','head',f'spike{i}{j}',(side*(2.7+j*.5),-6+j*2,2),( -.25-j*.14,side*.32,side*(.32+j*.17)),[(-1.5,-2,0,3,4,length,'stripe'),(-.8,-1,length-1,2,2,3,'shell')])
        part('arm'+str(i),'body','arm'+str(i),(side*3.3,0,0),(0,0,side*-.12),[(-.8,0,-.8,2,5,2,'joint'),(-1.3,4,-1.3,3,3,3,'shell'),(-1.5,6,-1.5,3,1,3,'gold'),(-1.5,7,-1.5,3,3,3,'glove')])
        if k: 
            for j in range(3):part(f'claw{i}{j}','arm'+str(i),f'claw{j}',(-1+j,9,-.5),(-.3,0,0),[(-.4,0,-.4,1,2,1,'joint')])
        part('leg'+str(i),'body','leg'+str(i),(side*1.8,6,0),(0,0,0),[(-.8,0,-.8,2,6,2,'joint'),(-1.6,5,-1.4,3,3,3,'shell'),(-1.8,7,-2,4,1,4,'gold'),(-2,8,-4,4,3,6,'shoe')])
        if k==2:
            part('coat'+str(i),'body','coat'+str(i),(side*2,3,1),(.15,0,side*.22),[(-2,0,-1,4,12,3,'cape'),(-2,10,-1.5,4,2,4,'silver')])
            part('cuff'+str(i),'arm'+str(i),'cuff',(0,4,0),(0,0,0),[(-2,-1,-2,4,3,4,'cape')])
    if k==2:part('crest','head','crest',(0,-8,1),(-.2,0,0),[(-1.5,-8,-1,3,9,3,'stripe'),(-.5,-12,0,1,5,1,'silver')])
    if k==0:
        part('bike','r','bike',(0,19,0),(0,0,0),[(-2,-3,-7,4,4,15,'dark'),(-3,-6,-3,6,4,7,'shell'),(-2,-7,2,4,2,6,'dark'),(-3,-4,-7,6,2,5,'shoe'),(-2,-3,5,4,2,6,'silver')])
        part('bars','bike','bars',(0,-6,-5),(-.3,0,0),[(-.5,-5,-.5,1,5,1,'silver'),(-5,-5,-.5,10,1,1,'dark')])
        part('lamp','bike','lamp',(0,-4,-8),(0,0,0),[(-2,-2,-.5,4,3,1,'silver')])
        for i,z in enumerate((-7,8)):
            part('wheel'+str(i),'bike','wheel'+str(i),(0,1,z),(0,0,0),[(-2,-3,-3,4,6,6,'tire'),(-2.2,-2,-2,1,4,4,'silver'),(1.2,-2,-2,1,4,4,'silver')])
    models.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    blue=(35,67,169) if k==1 else (32,38,106)
    pal={'shell':(25,24,30) if not k else blue,'face':(28,27,34) if not k else blue,'stripe':(28,27,34) if not k else blue,'core':(236,235,228) if not k else (234,194,35),'muzzle':(222,160,82) if not k else (166,175,185),'inner':(224,166,76) if k<2 else (197,27,40),'joint':(30,28,34) if not k else (153,166,178),'gold':(224,183,43),'glove':(239,237,233) if not k else (156,167,178),'shoe':(203,24,36),'dark':(23,22,27),'silver':(192,199,211),'cape':(27,29,67),'tire':(19,19,21)}
    pix=bytearray(W*W*4)
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[mat];g=.68+.32*math.sin(u*math.pi)+.10*math.exp(-((u-.25)/.12)**2)
                c=tuple(int(z*g) for z in base)
                if mat=='stripe' and (abs(u-.5)<.13 or face=='top' and abs(u-.5)<.23):c=(218,24,37) if not k else (225,231,242) if k==2 else c
                if mat=='face' and face=='front':
                    if not k and abs(u-.5)<.13 and v<.4:c=(210,26,40)
                    for ex in (.26,.74):
                        dx=(u-ex)/.23;dy=(v-.68+(ex-.5)*dx*.28)/.27;d=dx*dx+dy*dy
                        if d<1:c=(240,237,230) if not k else (8,9,17)
                        if d<.8 and abs(dx)<.35:c=(224,29,39) if k!=1 else (247,113,18)
                        if d<.65 and abs(dx)<.16:c=(17,12,20)
                        if (dx+.12)**2+(dy+.25)**2<.04:c=(255,242,231)
                if mat=='core':
                    d=(u-.5)**2+(v-.5)**2
                    if k and d<.075:c=(15,17,24)
                if mat=='shoe' and face=='top' and .18<u<.82 and .18<v<.8:c=(228,230,235)
                if mat=='cape' and min(u,1-u,v,1-v)<.10:c=(198,208,220)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,z)) for z in c],255))
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
    (assets/'textures/entity'/(['shadow','metal_sonic','neo_metal_sonic'][k]+'.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(java/'SonicGuestClient.java').write_text('''package it.noctis.magic;
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
public class SonicGuestClient{
    static final String[] N={"shadow","metal_sonic","neo_metal_sonic"};
    static final ModelLayerLocation[] L=new ModelLayerLocation[3];
    static{for(int i=0;i<3;i++)L[i]=new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[i]),"main");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],SonicGuestClient::mesh0);e.registerLayerDefinition(L[1],SonicGuestClient::mesh1);e.registerLayerDefinition(L[2],SonicGuestClient::mesh2);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.SHADOW.get(),c->new Renderer(c,true));e.registerEntityRenderer(Noctis.METAL_SONIC.get(),c->new Renderer(c,false));}
'''+ '\n'.join(models)+'''
    static class Model extends EntityModel<SonicGuest>{
        final ModelPart r,b,h;final int k;
        Model(ModelPart r,int k){this.r=r;this.k=k;b=r.getChild("body");h=b.getChild("head");}
        @Override public void setupAnim(SonicGuest e,float limb,float amount,float age,float yaw,float pitch){
            h.yRot=yaw*.012f;h.xRot=pitch*.012f;float hit=e.attacking();
            for(int i=0;i<2;i++){float walk=(float)Math.cos(limb*.67+i*Math.PI)*amount;ModelPart arm=b.getChild("arm"+i),leg=b.getChild("leg"+i);
                arm.xRot=k==0?-1.25f-hit*.5f:-walk*.7f-hit*1.4f;leg.xRot=k==0?-.80f:walk*.7f;leg.zRot=k==0?(i==0?-.38f:.38f):0;
                if(k==2)b.getChild("coat"+i).xRot=.15f+amount*.25f+(float)Math.sin(age*.13+i)*.09f;
            }
            if(k==0){for(int i=0;i<2;i++)r.getChild("bike").getChild("wheel"+i).xRot=limb*1.3f;b.xRot=.18f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<SonicGuest,Model>{
        final Model normal,neo;final boolean shadow;
        Renderer(EntityRendererProvider.Context c,boolean shadow){super(c,new Model(c.bakeLayer(L[shadow?0:1]),shadow?0:1),.55f);this.shadow=shadow;normal=model;neo=shadow?normal:new Model(c.bakeLayer(L[2]),2);}
        @Override public void render(SonicGuest e,float yaw,float partial,PoseStack p,net.minecraft.client.renderer.MultiBufferSource b,int light){model=e.neo()?neo:normal;super.render(e,yaw,partial,p,b,light);}
        @Override protected void scale(SonicGuest e,PoseStack p,float partial){float a=e.neo()?1.20f:1f;p.scale(a,a,a);}
        @Override public ResourceLocation getTextureLocation(SonicGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[shadow?0:e.neo()?2:1]+".png");}
    }
}''',encoding='utf-8')
for n in ('shadow','metal_sonic'):(assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in [('shadow','Shadow the Hedgehog'),('metal_sonic','Metal Sonic')]:
        d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Morgana dialogue and neutral Sonic guests installed')
