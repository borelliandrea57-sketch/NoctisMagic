"""0.9.7: a comic scrap thief with recoverable stolen metals."""
from pathlib import Path
import sys,json,struct,zlib,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
edit('Noctis.java',[
('public static final RegistryObject<EntityType<Papi>> PAPI=', '''public static final RegistryObject<EntityType<ScrapThief>> SCRAP_THIEF=ENTITIES.register("scrap_thief",()->EntityType.Builder.<ScrapThief>of(ScrapThief::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(8).build(ID+":scrap_thief"));
    public static final RegistryObject<Item> SCRAP_THIEF_EGG=ITEMS.register("scrap_thief_spawn_egg",()->new ForgeSpawnEggItem(SCRAP_THIEF,0xc72132,0xffffff,new Item.Properties()));
    public static final RegistryObject<EntityType<Papi>> PAPI='''),
('e.put(PAPI.get(),Papi.attributes().build());','e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());e.put(PAPI.get(),Papi.attributes().build());'),
('e.accept(PAPI_EGG.get());','e.accept(PAPI_EGG.get());e.accept(SCRAP_THIEF_EGG.get());')
])
(java/'ScrapThief.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class ScrapThief extends PathfinderMob{
    static final TagKey<Item> INGOTS=TagKey.create(Registries.ITEM,new ResourceLocation("forge","ingots"));
    static final TagKey<Item> NUGGETS=TagKey.create(Registries.ITEM,new ResourceLocation("forge","nuggets"));
    static final TagKey<Item> RAW=TagKey.create(Registries.ITEM,new ResourceLocation("forge","raw_materials"));
    private ItemStack stolen=ItemStack.EMPTY;
    private UUID victim;private boolean alreadyStole=false;private int cooldown=30;
    public ScrapThief(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,26).add(Attributes.MOVEMENT_SPEED,.35).add(Attributes.FOLLOW_RANGE,28);}
    static boolean metal(ItemStack s){return !s.isEmpty()&&(s.is(INGOTS)||s.is(NUGGETS)||s.is(RAW)||s.is(Items.IRON_INGOT)||s.is(Items.GOLD_INGOT)||s.is(Items.COPPER_INGOT)||s.is(Items.NETHERITE_INGOT)||s.is(Items.IRON_NUGGET)||s.is(Items.GOLD_NUGGET)||s.is(Items.RAW_IRON)||s.is(Items.RAW_COPPER)||s.is(Items.RAW_GOLD));}
    static int slot(Player p){for(int i=0;i<p.getInventory().items.size();i++)if(metal(p.getInventory().items.get(i)))return i;return -1;}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new EscapeGoal());goalSelector.addGoal(2,new SnatchGoal());goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(4,new LookAtPlayerGoal(this,Player.class,8));}
    @Override public void tick(){super.tick();if(cooldown>0)cooldown--;}
    @Override public boolean removeWhenFarAway(double d){return stolen.isEmpty()&&super.removeWhenFarAway(d);}
    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource s,int looting,boolean hit){super.dropCustomDeathLoot(s,looting,hit);if(!stolen.isEmpty()){spawnAtLocation(stolen.copy());stolen=ItemStack.EMPTY;}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("Stolen",stolen.save(new CompoundTag()));t.putBoolean("AlreadyStole",alreadyStole);if(victim!=null)t.putUUID("Victim",victim);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);stolen=ItemStack.of(t.getCompound("Stolen"));alreadyStole=t.getBoolean("AlreadyStole");if(t.hasUUID("Victim"))victim=t.getUUID("Victim");}
    class SnatchGoal extends Goal{
        Player p;SnatchGoal(){setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK));}
        @Override public boolean canUse(){if(alreadyStole||cooldown>0)return false;p=level().getNearestPlayer(ScrapThief.this,16);return p!=null&&!p.isCreative()&&!p.isSpectator()&&p.isAlive()&&slot(p)>=0;}
        @Override public boolean canContinueToUse(){return !alreadyStole&&p!=null&&p.isAlive()&&!p.isCreative()&&!p.isSpectator()&&distanceToSqr(p)<400&&slot(p)>=0;}
        @Override public void stop(){getNavigation().stop();p=null;}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        @Override public void tick(){
            if(!(level() instanceof ServerLevel l)||p==null)return;getLookControl().setLookAt(p,30,30);
            if(distanceTo(p)>1.8||!hasLineOfSight(p)){if(tickCount%5==0)getNavigation().moveTo(p,1.15);return;}
            int i=slot(p);if(i<0)return;
            Inventory inv=p.getInventory();ItemStack stack=inv.items.get(i);stolen=stack.split(1);inv.setChanged();p.containerMenu.broadcastChanges();victim=p.getUUID();alreadyStole=true;setPersistenceRequired();
            p.sendSystemMessage(Component.literal("Gennaro: Ue', grazie pe' 'o ").append(stolen.getHoverName()).append("!"));
            playSound(SoundEvents.ITEM_PICKUP,.9f,.7f);l.sendParticles(ParticleTypes.POOF,getX(),getY()+.5,getZ(),8,.25,.3,.25,.05);
            getNavigation().stop();
        }
    }
    class EscapeGoal extends Goal{
        Player p;EscapeGoal(){setFlags(java.util.EnumSet.of(Flag.MOVE));}
        @Override public boolean canUse(){if(stolen.isEmpty()||victim==null)return false;p=level().getPlayerByUUID(victim);return p!=null&&p.isAlive()&&distanceToSqr(p)<625;}
        @Override public boolean canContinueToUse(){return p!=null&&p.isAlive()&&distanceToSqr(p)<900&&!stolen.isEmpty();}
        @Override public void stop(){getNavigation().stop();p=null;}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        @Override public void tick(){
            if(p==null||tickCount%10!=0)return;
            Vec3 away=position().subtract(p.position());if(away.horizontalDistanceSqr()<.01)away=new Vec3(1,0,0);
            Vec3 dir=new Vec3(away.x,0,away.z).normalize();
            for(int j=0;j<8;j++){Vec3 q=position().add(dir.scale(9+random.nextInt(7))).add(random.nextInt(9)-4,random.nextInt(5)-2,random.nextInt(9)-4);BlockPos pos=BlockPos.containing(q);
                if(!level().hasChunkAt(pos))continue;
                var path=getNavigation().createPath(pos,0);if(path!=null&&path.canReach()){getNavigation().moveTo(path,1.65);return;}
            }
        }
    }
}''',encoding='utf-8')
edit('NightGuests.java',[
('if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!p.isCreative()&&p.getRandom().nextInt(16)==0&&l.getEntitiesOfClass(ScrapThief.class,p.getBoundingBox().inflate(64)).isEmpty()){
            BlockPos q=Eclipse.spot(p,9,20);if(q!=null){ScrapThief thief=Noctis.SCRAP_THIEF.get().create(l);if(thief!=null){thief.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(thief))l.addFreshEntity(thief);}}
        }''')
])
(java/'ScrapThiefClient.java').write_text('''package it.noctis.magic;
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
public class ScrapThiefClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"scrap_thief"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,ScrapThiefClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.SCRAP_THIEF.get(),Renderer::new);}
    static LayerDefinition mesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot();r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        r.getChild("head").addOrReplaceChild("cap",CubeListBuilder.create().texOffs(64,0).addBox(-4.5f,-9,-4.5f,9,2.5f,9).texOffs(64,16).addBox(-4,-7,-8,8,1,4),PartPose.ZERO);
        return LayerDefinition.create(m,128,64);
    }
    static class Renderer extends MobRenderer<ScrapThief,HumanoidModel<ScrapThief>>{
        Renderer(EntityRendererProvider.Context c){super(c,new HumanoidModel<>(c.bakeLayer(L)),.42f);}
        @Override public ResourceLocation getTextureLocation(ScrapThief e){return new ResourceLocation(Noctis.ID,"textures/entity/scrap_thief.png");}
    }
}''',encoding='utf-8')
rng=random.Random(97);pix=[[(30,34,48,255) for x in range(128)] for y in range(64)]
def R(x,y,w,h,c,n=0):
    for yy in range(y,min(64,y+h)):
        for xx in range(x,min(128,x+w)):
            d=rng.randint(-n,n);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in c[:3])+(c[3] if len(c)==4 else 255,)
red=(194,28,45);white=(251,245,238);skin=(218,165,123);hair=(50,35,28)
R(0,0,32,16,skin,5);R(32,0,32,16,(0,0,0,0));R(8,0,8,8,hair,5);R(8,8,8,8,skin,4);R(8,8,8,1,hair)
for x in (9,13):R(x,10,2,1,hair);R(x,11,2,1,white)
R(10,11,1,1,hair);R(13,11,1,1,hair);R(10,14,4,1,(96,48,35));R(11,14,2,1,white)
R(16,16,24,16,red,7);R(40,16,16,16,red,5);R(44,24,4,8,skin,4);R(0,16,16,16,(37,46,73),5);R(16,48,32,16,(37,46,73),5)
R(64,0,40,14,red,5);R(64,16,28,7,red,5)
# Compact LETE-like white wordmark across the eight-pixel shirt face;
# high contrast white badge on the cap.
R(20,23,8,4,white);R(21,24,1,2,red);R(23,24,1,2,red);R(25,24,1,2,red);R(27,24,1,2,red)
R(73,10,9,2,white);R(75,10,1,2,red);R(78,10,1,2,red);R(81,10,1,2,red)
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+bytes(v for p in row for v in p) for row in pix)
(assets/'textures/entity/scrap_thief.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,64,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(assets/'models/item/scrap_thief_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.scrap_thief']='Gennaro il rottamaio';d['item.noctismagic.scrap_thief_spawn_egg']='Uovo generatore: Gennaro il rottamaio' if lang=='it_it' else 'Gennaro Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.9.7: scrap thief added')
