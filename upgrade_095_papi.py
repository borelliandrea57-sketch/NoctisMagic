"""Noctis 0.9.5: Enrico Papi comedic sonic attacker."""
from pathlib import Path
import sys,json,struct,zlib,subprocess,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
edit('Noctis.java',[
('public static final RegistryObject<EntityType<Shenron>> SHENRON=', '''public static final RegistryObject<EntityType<Papi>> PAPI=ENTITIES.register("papi",()->EntityType.Builder.<Papi>of(Papi::new,MobCategory.MONSTER).sized(.65f,1.95f).clientTrackingRange(8).build(ID+":papi"));
    public static final RegistryObject<Item> PAPI_EGG=ITEMS.register("papi_spawn_egg",()->new ForgeSpawnEggItem(PAPI,0x28334a,0xe7c6a4,new Item.Properties()));
    public static final RegistryObject<EntityType<Shenron>> SHENRON='''),
('e.put(SHENRON.get(),Shenron.attributes().build());','e.put(PAPI.get(),Papi.attributes().build());e.put(SHENRON.get(),Shenron.attributes().build());'),
('e.accept(ELVIS_EGG.get());','e.accept(ELVIS_EGG.get());e.accept(PAPI_EGG.get());')
])
edit('FallenEncounter.java',[('static final RegistryObject<SoundEvent> THEME=','static final RegistryObject<SoundEvent> PAPI_SHOUT=SOUNDS.register("papi_shout",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"papi_shout")));\n    static final RegistryObject<SoundEvent> THEME=')])
(java/'Papi.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Papi extends Monster {
    private int cooldown=30,shout=0;
    public Papi(EntityType<? extends Monster> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,40).add(Attributes.ATTACK_DAMAGE,6).add(Attributes.MOVEMENT_SPEED,.29).add(Attributes.FOLLOW_RANGE,25);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new ShoutGoal());goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.8));goalSelector.addGoal(4,new LookAtPlayerGoal(this,Player.class,10));targetSelector.addGoal(1,new NearestAttackableTargetGoal<Player>(this,Player.class,true));}
    @Override public void tick(){super.tick();if(cooldown>0)cooldown--;if(shout>0)shout--;}
    @Override public void handleEntityEvent(byte id){if(id==79){shout=45;return;}super.handleEntityEvent(id);}
    public boolean shouting(){return shout>0;}
    class ShoutGoal extends Goal {
        ShoutGoal(){setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK));}
        @Override public boolean canUse(){return getTarget()!=null&&getTarget().isAlive();}
        @Override public boolean canContinueToUse(){return canUse();}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        @Override public void stop(){getNavigation().stop();}
        @Override public void tick(){
            if(!(level() instanceof ServerLevel l))return;
            LivingEntity t=getTarget();if(t==null)return;getLookControl().setLookAt(t,40,40);
            if(distanceTo(t)>9||!hasLineOfSight(t)){if(tickCount%5==0)getNavigation().moveTo(t,1.15);return;}
            getNavigation().stop();if(cooldown>0)return;cooldown=100;
            l.broadcastEntityEvent(Papi.this,(byte)79);playSound(FallenEncounter.PAPI_SHOUT.get(),1.2f,1f);
            if(t instanceof Player p)p.sendSystemMessage(Component.literal("Enrico Papi: vuoi sapere quanto vale la tua auto?"));
            Vec3 a=getEyePosition(),b=t.getEyePosition();
            for(int i=1;i<=12;i++){Vec3 q=a.lerp(b,i/12.0);l.sendParticles(ParticleTypes.NOTE,q.x,q.y,q.z,1,0,0,0,1);}
            l.sendParticles(ParticleTypes.SONIC_BOOM,b.x,b.y,b.z,1,0,0,0,0);
            t.hurt(damageSources().mobAttack(Papi.this),6);t.knockback(.8,getX()-t.getX(),getZ()-t.getZ());
        }
    }
}''',encoding='utf-8')
edit('NightGuests.java',[
('if(!l.isDay()&&l.getDifficulty()!=Difficulty.PEACEFUL&&p.getRandom().nextInt(5)==0', '''if(l.getDifficulty()!=Difficulty.PEACEFUL&&p.getRandom().nextInt(14)==0&&l.getEntitiesOfClass(Papi.class,p.getBoundingBox().inflate(64)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){Papi v=Noctis.PAPI.get().create(l);if(v!=null){v.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(v)){v.setTarget(p);l.addFreshEntity(v);}}}
        }
        if(!l.isDay()&&l.getDifficulty()!=Difficulty.PEACEFUL&&p.getRandom().nextInt(5)==0''')
])
(java/'PapiClient.java').write_text('''package it.noctis.magic;
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
public class PapiClient {
    static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"papi"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(LAYER,PapiClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.PAPI.get(),Renderer::new);}
    static LayerDefinition mesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot();
        r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        r.getChild("head").addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.3f,-9,-4.3f,8.6f,2,8.6f),PartPose.ZERO);
        r.getChild("right_arm").addOrReplaceChild("mic",CubeListBuilder.create().texOffs(80,40).addBox(-.7f,-4,-.7f,1.4f,6,1.4f).texOffs(90,40).addBox(-1.2f,-6,-1.2f,2.4f,2,2.4f),PartPose.offsetAndRotation(-1,8,-1,0,0,.2f));
        return LayerDefinition.create(m,128,64);
    }
    static class Model extends HumanoidModel<Papi>{
        Model(ModelPart p){super(p);}
        @Override public void setupAnim(Papi e,float limb,float amount,float age,float yaw,float pitch){super.setupAnim(e,limb,amount,age,yaw,pitch);if(e.shouting()){rightArm.xRot=-2f;leftArm.xRot=-1f;leftArm.zRot=.6f;head.xRot+=(float)Math.sin(age*.7)*.08f;}}
    }
    static class Renderer extends MobRenderer<Papi,Model>{
        Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(LAYER)),.4f);}
        @Override public ResourceLocation getTextureLocation(Papi e){return new ResourceLocation(Noctis.ID,"textures/entity/papi.png");}
    }
}''',encoding='utf-8')
pix=[[(33,42,58,255) for x in range(128)] for y in range(64)]
rng=random.Random(701)
def R(x,y,w,h,col,noise=0):
    for yy in range(y,min(y+h,64)):
        for xx in range(x,min(x+w,128)):
            n=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,c+n)) for c in col[:3])+(col[3] if len(col)==4 else 255,)
R(0,0,32,16,(207,161,128),4);R(32,0,32,16,(0,0,0,0));R(8,0,8,8,(77,53,36),6);R(8,8,8,8,(221,176,140),3)
R(8,8,8,1,(82,55,38));R(9,10,2,1,(83,53,37));R(13,10,2,1,(83,53,37));R(9,11,2,1,(250,241,226));R(13,11,2,1,(250,241,226));R(10,11,1,1,(66,47,34));R(13,11,1,1,(66,47,34));R(10,14,4,1,(117,68,53));R(11,14,2,1,(239,228,215))
R(64,0,38,12,(77,54,38),8);R(16,16,24,16,(37,46,64),6);R(22,20,4,9,(233,231,223),3);R(23,21,2,7,(149,49,56),3)
R(40,16,16,16,(37,46,64),6);R(44,26,4,6,(215,169,135),3);R(0,16,16,16,(30,38,52),5);R(16,48,32,16,(30,38,52),5)
R(80,40,10,10,(42,43,50),4);R(90,40,13,7,(174,180,188),9)
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+bytes(v for p in row for v in p) for row in pix)
(assets/'textures/entity/papi.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,64,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
p=assets/'models/item/papi_spawn_egg.json';p.write_text('{"parent":"minecraft:item/template_spawn_egg"}',encoding='utf-8')
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.papi']='Enrico Papi';d['item.noctismagic.papi_spawn_egg']='Uovo generatore: Enrico Papi' if lang=='it_it' else 'Enrico Papi Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
sounds=assets/'sounds'
sounds.mkdir(parents=True,exist_ok=True)
audio=Path(__file__).resolve().parent/'enrico_papi.mp3'
assert audio.is_file() and audio.stat().st_size>0, 'Missing enrico_papi.mp3 in repository'
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(audio),'-map','0:a:0','-vn','-ac','1','-ar','44100','-c:a','libvorbis','-q:a','5',str(sounds/'papi_shout.ogg')],check=True)
assert (sounds/'papi_shout.ogg').stat().st_size>0
print('Papi: repository voice converted to Vorbis; no speech synthesis')
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['papi_shout']={"sounds":[{"name":"noctismagic:papi_shout"}]};p.write_text(json.dumps(d),encoding='utf-8')
print('Noctis: Papi encounter added')
