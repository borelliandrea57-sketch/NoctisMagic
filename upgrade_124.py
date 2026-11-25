"""1.2.4: Spider-Man affected by a fictional spider-sense curse, hostile encounters."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<SpiderHero>> SPIDER_HERO=ENTITIES.register("spider_man",()->EntityType.Builder.<SpiderHero>of(SpiderHero::new,MobCategory.MONSTER).sized(.65f,1.85f).clientTrackingRange(10).build(ID+":spider_man"));
    public static final RegistryObject<Item> SPIDER_HERO_EGG=ITEMS.register("spider_man_spawn_egg",()->new ForgeSpawnEggItem(SPIDER_HERO,0xb92136,0x243a87,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(SPIDER_HERO.get(),SpiderHero.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(SPIDER_HERO_EGG.get());')
(java/'SpiderHero.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class SpiderHero extends Monster{
    static final EntityDataAccessor<Boolean> CLIMBING=SynchedEntityData.defineId(SpiderHero.class,EntityDataSerializers.BOOLEAN);
    int webCooldown=45,leapCooldown=40,speech,pose;
    public SpiderHero(EntityType<? extends Monster> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,140).add(Attributes.ARMOR,8).add(Attributes.ATTACK_DAMAGE,15).add(Attributes.MOVEMENT_SPEED,.35).add(Attributes.FOLLOW_RANGE,28).add(Attributes.KNOCKBACK_RESISTANCE,.3);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(CLIMBING,false);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.2,true));goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(4,new RandomLookAroundGoal(this));}
    @Override public boolean onClimbable(){return entityData.get(CLIMBING)||super.onClimbable();}
    @Override public boolean causeFallDamage(float a,float b,net.minecraft.world.damagesource.DamageSource s){return false;}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal("Spider-Man: "+s));}
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(webCooldown>0)webCooldown--;if(leapCooldown>0)leapCooldown--;if(speech>0)speech--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        LivingEntity t=getTarget();
        if(t!=null&&(!t.isAlive()||distanceTo(t)>24||t instanceof Player p&&(p.isCreative()||p.isSpectator()))){setTarget(null);t=null;}
        if(t==null&&tickCount%10==0){
            // His corrupted spider-sense identifies movement, not faces; crouching quietly avoids detection.
            t=l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(18),p->p.isAlive()&&!p.isCreative()&&!p.isSpectator()&&(!p.isShiftKeyDown()||p.distanceTo(this)<2.5)).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
            if(t!=null){setTarget(t);if(speech==0){speech=160;say(l,"Il mio senso di ragno non sbaglia mai! ...Aspetta, chi sei?");}}
        }
        entityData.set(CLIMBING,horizontalCollision&&t!=null);
        if(t==null)return;
        if(onClimbable()&&horizontalCollision){Vec3 v=getDeltaMovement();setDeltaMovement(v.x,Math.max(v.y,.18),v.z);}
        double d=distanceTo(t);
        if(onGround()&&leapCooldown==0&&d>3&&d<9&&hasLineOfSight(t)){
            Vec3 v=t.position().subtract(position());Vec3 h=new Vec3(v.x,0,v.z).normalize().scale(.65);
            setDeltaMovement(h.x,.55,h.z);leapCooldown=65;l.broadcastEntityEvent(this,(byte)96);
        }
        if(webCooldown==0&&d<16&&hasLineOfSight(t)){
            webCooldown=90;l.broadcastEntityEvent(this,(byte)96);
            Vec3 a=getEyePosition(),b=t.getEyePosition();
            for(int i=0;i<24;i++){Vec3 q=a.lerp(b,i/23.0);l.sendParticles(ParticleTypes.CLOUD,q.x,q.y,q.z,1,.025,.025,.025,0);}
            t.hurt(damageSources().mobAttack(this),7);t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,80,2));
            playSound(SoundEvents.SNOWBALL_THROW,1,.75f);
            if(speech==0){speech=160;say(l,"Preso! ...Spero di aver preso quello giusto.");}
        }
    }
    @Override public boolean doHurtTarget(Entity e){boolean hit=super.doHurtTarget(e);if(hit&&level() instanceof ServerLevel l)l.broadcastEntityEvent(this,(byte)96);return hit;}
    @Override public void handleEntityEvent(byte id){if(id==96){pose=18;return;}super.handleEntityEvent(id);}
    public float action(){return pose<=0?0:(float)Math.sin(pose*Math.PI/18);}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!l.isDay()&&l.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL&&p.getRandom().nextInt(24)==0&&l.getEntitiesOfClass(SpiderHero.class,p.getBoundingBox().inflate(64)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){SpiderHero hero=Noctis.SPIDER_HERO.get().create(l);if(hero!=null){hero.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(hero))l.addFreshEntity(hero);}}
        }''')
(java/'SpiderHeroClient.java').write_text('''package it.noctis.magic;
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
public class SpiderHeroClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"spider_man"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,()->{
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot();
        r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        return LayerDefinition.create(m,64,64);
    });}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.SPIDER_HERO.get(),Renderer::new);}
    static class Model extends HumanoidModel<SpiderHero>{
        Model(ModelPart p){super(p);}
        @Override public void setupAnim(SpiderHero e,float limb,float amount,float age,float yaw,float pitch){
            super.setupAnim(e,limb,amount,age,yaw,pitch);float a=e.action();
            if(e.onClimbable()){rightArm.xRot=-1.9f+(float)Math.sin(age*.4)*.45f;leftArm.xRot=-1.9f-(float)Math.sin(age*.4)*.45f;}
            if(a>0){rightArm.xRot=-1.65f*a;rightArm.zRot=.15f*a;leftArm.xRot=-.7f*a;body.yRot=a*.12f;}
            else{rightArm.zRot=0;body.yRot=0;}
        }
    }
    static class Renderer extends MobRenderer<SpiderHero,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.35f);}@Override public ResourceLocation getTextureLocation(SpiderHero e){return new ResourceLocation(Noctis.ID,"textures/entity/spider_man.png");}}
}''',encoding='utf-8')
# High resolution classic red/blue suit with web lines, almond mask lenses and chest spider.
S=8;W=64*S;pix=bytearray(W*W*4)
def face(x,y,w,h,red,kind=''):
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);g=.72+.28*math.sin(u*math.pi);base=(199,25,42) if red else (33,54,119)
            c=tuple(int(a*g) for a in base)
            if red:
                if abs(math.sin((u-.5)*math.pi*5))<.12 or abs(math.sin((v+.12*math.cos(u*math.pi*2))*math.pi*6))<.105:c=(48,27,40)
            if kind=='mask':
                for ex in (.25,.75):
                    dx=(u-ex)/.225;dy=(v-.52+(.5-ex)*dx*.36)/.32
                    if abs(dx)<1 and abs(dy)<(1-abs(dx))**.58:c=(20,19,26)
                    if abs(dx)<.82 and abs(dy)<.81*(1-abs(dx)/.9)**.55:c=(229,237,245)
            if kind=='chest':
                dx=u-.5;dy=v-.44
                if (dx/.065)**2+(dy/.13)**2<1 or (.075<abs(dx)<.28 and abs(dy-(abs(dx)-.075)*(.9 if dy>0 else -.9))<.055):c=(22,20,27)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*c,255))
def uv(u,v,w,h,d,red,kind=''):
    for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:
        face(X,Y,A,B,red,kind if f=='front' else '')
uv(0,0,8,8,8,True,'mask')
uv(16,16,8,12,4,True,'chest')
uv(40,16,4,12,4,True)
uv(32,48,4,12,4,True)
uv(0,16,4,12,4,False)
uv(16,48,4,12,4,False)
# Red boots and gloves by repainting bottom six texels of the relevant side faces.
for u,v in [(0,16),(16,48)]:
    for x in (u,u+4,u+8,u+12):face(x,v+4+7,4,5,True)
for u,v in [(40,16),(32,48)]:
    for x in (u,u+4,u+8,u+12):face(x,v+4+3,4,4,False)
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'textures/entity/spider_man.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))))+ch(b'IEND',b''))
(assets/'models/item/spider_man_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.spider_man']='Spider-Man';d['item.noctismagic.spider_man_spawn_egg']='Uovo generatore: Spider-Man' if lang=='it_it' else 'Spider-Man Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Spider-Man: corrupted spider-sense, wall climb, acrobatics and web attacks')
