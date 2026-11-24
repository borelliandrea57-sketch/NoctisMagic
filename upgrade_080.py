"""Noctis 0.8.0: polished familiars and eyes, wine, unique boss, smoking and vampire audio."""
from pathlib import Path
import sys,json,struct,zlib,random,math,wave,array,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(path,pairs):
    s=path.read_text(encoding='utf-8')
    for old,new in pairs:
        if old not in s:raise ValueError(f'Missing anchor {path.name}: {old[:120]}')
        s=s.replace(old,new,1)
    path.write_text(s,encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
def j(path,data):
    p=res/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
edit(root/'gradle.properties',[('mod_version=0.7.0','mod_version=0.8.0')])
edit(java/'Noctis.java',[
('public static final RegistryObject<EntityType<Angel>> ANGEL=', '''public static final RegistryObject<Item> FALLEN_EGG=ITEMS.register("one_winged_angel_spawn_egg",()->new ForgeSpawnEggItem(FALLEN,0x191820,0xc8c8d8,new Item.Properties()));
    public static final RegistryObject<Item> SORA_EGG=ITEMS.register("sora_spawn_egg",()->new ForgeSpawnEggItem(SORA,0xae342d,0xeac74d,new Item.Properties()));
    public static final RegistryObject<EntityType<Angel>> ANGEL='''),
('e.accept(ANGEL_EGG.get());','e.accept(FALLEN_EGG.get());e.accept(SORA_EGG.get());e.accept(ANGEL_EGG.get());'),
('e.accept(MiracleLiquid.BUCKET.get());','e.accept(MiracleLiquid.BUCKET.get());e.accept(WineItem.WINE.get());')
])
# Register wine during the main mod class initialization, not after item registration.
edit(java/'Noctis.java',[('public static final RegistryObject<Item> FALLEN_EGG=', 'public static final RegistryObject<Item> WINE=WineItem.WINE;\n    public static final RegistryObject<Item> FALLEN_EGG=')])
write('WineItem.java','''package it.noctis.magic;
import net.minecraft.network.chat.Component;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegistryObject;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class WineItem extends Item {
    public static final RegistryObject<Item> WINE=Noctis.ITEMS.register("wine_bottle",WineItem::new);
    public WineItem(){super(new Item.Properties().stacksTo(16));}
    @Override public UseAnim getUseAnimation(ItemStack s){return UseAnim.DRINK;}
    @Override public int getUseDuration(ItemStack s){return 32;}
    @Override public InteractionResultHolder<ItemStack> use(Level l,Player p,InteractionHand h){p.startUsingItem(h);return InteractionResultHolder.consume(p.getItemInHand(h));}
    @Override public ItemStack finishUsingItem(ItemStack s,Level l,LivingEntity e){
        if(e instanceof Player p){if(!l.isClientSide){p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,900,0));p.sendSystemMessage(Component.literal("Vino miracoloso: Resistenza per 45 secondi."));}
            return ItemUtils.createFilledResult(s,p,new ItemStack(Items.GLASS_BOTTLE),false);
        }return s;
    }
    @SubscribeEvent public static void fill(PlayerInteractEvent.RightClickItem e){
        Player p=e.getEntity();Level l=e.getLevel();ItemStack s=e.getItemStack();if(!s.is(Items.GLASS_BOTTLE))return;
        Vec3 start=p.getEyePosition(),end=start.add(p.getLookAngle().scale(5));
        BlockHitResult hit=l.clip(new ClipContext(start,end,ClipContext.Block.OUTLINE,ClipContext.Fluid.SOURCE_ONLY,p));
        if(hit.getType()!=HitResult.Type.BLOCK||!l.getBlockState(hit.getBlockPos()).is(MiracleLiquid.BLOCK.get()))return;
        if(!l.isClientSide){p.setItemInHand(e.getHand(),ItemUtils.createFilledResult(s,p,new ItemStack(WINE.get())));l.playSound(null,p.getX(),p.getY(),p.getZ(),SoundEvents.BOTTLE_FILL,SoundSource.PLAYERS,1,1);}
        e.setCancellationResult(InteractionResult.sidedSuccess(l.isClientSide));e.setCanceled(true);
    }
}''')
edit(java/'MiracleEncounter.java',[
('center.offset(-5,-3,-5),center.offset(5,3,5)','center.offset(-9,-5,-9),center.offset(9,5,9)'),
('if(n>=64)break;','if(n>=128)break;'),
('if(l.hasChunkAt(q)&&l.getBlockState(q).is(Blocks.WATER)','if(q.distSqr(center)<=100&&l.hasChunkAt(q)&&l.getBlockState(q).is(Blocks.WATER)')
])
# A single ritual per world; creative egg can be used after defeat, but never creates a second active boss.
write('FallenRitual.java','''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class FallenRitual extends SavedData {
    private UUID active;private boolean invoked;
    static FallenRitual load(CompoundTag n){FallenRitual d=new FallenRitual();if(n.hasUUID("Active"))d.active=n.getUUID("Active");d.invoked=n.getBoolean("Invoked");return d;}
    @Override public CompoundTag save(CompoundTag n){if(active!=null)n.putUUID("Active",active);n.putBoolean("Invoked",invoked);return n;}
    static FallenRitual get(ServerLevel l){return l.getServer().overworld().getDataStorage().computeIfAbsent(FallenRitual::load,FallenRitual::new,"noctis_fallen_ritual");}
    static boolean canInvoke(ServerLevel l){FallenRitual d=get(l);return !d.invoked&&d.active==null;}
    static void invoked(ServerLevel l){FallenRitual d=get(l);d.invoked=true;d.setDirty();}
    static void clear(ServerLevel l,UUID id){FallenRitual d=get(l);if(id.equals(d.active)){d.active=null;d.setDirty();}}
    @SubscribeEvent public static void join(EntityJoinLevelEvent e){
        if(!(e.getLevel() instanceof ServerLevel l)||!(e.getEntity() instanceof OneWinged boss))return;
        FallenRitual d=get(l);if(d.active!=null&&!d.active.equals(boss.getUUID())){e.setCanceled(true);return;}
        d.active=boss.getUUID();d.setDirty();boss.setPersistenceRequired();
    }
}''')
edit(java/'FallenEncounter.java',[
('if(l.dimension()!=Level.OVERWORLD||l.getDifficulty()==Difficulty.PEACEFUL||','if(l.dimension()!=Level.OVERWORLD||!FallenRitual.canInvoke(l)||l.getDifficulty()==Difficulty.PEACEFUL||'),
('sign.getPersistentData().putBoolean("NoctisFallenSummoned",true);','FallenRitual.invoked(l);sign.getPersistentData().putBoolean("NoctisFallenSummoned",true);')
])
edit(java/'OneWinged.java',[
('bar.removeAllPlayers();super.remove(reason);','bar.removeAllPlayers();if(reason.shouldDestroy()&&level() instanceof ServerLevel l)FallenRitual.clear(l,getUUID());super.remove(reason);'),
('t=l.getNearestPlayer(this,75);if(t instanceof Player p&&(p.isCreative()||p.isSpectator()))t=null;','t=l.players().stream().filter(p->p.isAlive()&&!p.isCreative()&&!p.isSpectator()&&distanceTo(p)<75).min(java.util.Comparator.comparingDouble(p->distanceToSqr(p))).orElse(null);'),
('if(t==null){setDeltaMovement(getDeltaMovement().scale(.85));return;}','if(t==null){double floor=l.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,getBlockX(),getBlockZ());double dy=getY()<floor+5?.13:0;setDeltaMovement(getDeltaMovement().scale(.85).add(0,dy,0));return;}')
])
# Model and texture updates: each familiar uses its own silhouette and atlas.
edit(java/'Client.java',[
('e.registerLayerDefinition(IMP,()->ShapeModel.mesh(3));','e.registerLayerDefinition(IMP,()->FamiliarArt.mesh(3));'),
('e.registerLayerDefinition(DEVIL,()->ShapeModel.mesh(4));','e.registerLayerDefinition(DEVIL,()->FamiliarArt.mesh(4));'),
('e.registerLayerDefinition(FROST,()->ShapeModel.mesh(5));','e.registerLayerDefinition(FROST,()->FamiliarArt.mesh(5));'),
('e.registerLayerDefinition(NIGHT,()->ShapeModel.mesh(6));','e.registerLayerDefinition(NIGHT,()->FamiliarArt.mesh(6));'),
('e.registerLayerDefinition(ANGEL,()->ShapeModel.mesh(7));','e.registerLayerDefinition(ANGEL,FamiliarArt::angel);')
])
write('FamiliarArt.java','''package it.noctis.magic;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
public class FamiliarArt {
    static CubeListBuilder c(int u,int v){return CubeListBuilder.create().texOffs(u,v);}
    static PartDefinition part(PartDefinition p,String n,CubeListBuilder b,float x,float y,float z){return p.addOrReplaceChild(n,b,PartPose.offset(x,y,z));}
    static LayerDefinition mesh(int k){
        MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
        boolean devil=k==4,ice=k==5,night=k==6;
        float headY=devil?10:ice?12:13,bodyY=devil?18:19;
        PartDefinition body=part(r,"body",c(0,24).addBox(-3,devil?-9:-7,-2,6,devil?9:7,4),0,bodyY,0);
        PartDefinition head=part(r,"head",c(0,0).addBox(-4,-7,-3,8,7,6),0,headY,0);
        for(int i=0;i<2;i++){
            int s=i==0?-1:1;
            PartDefinition arm=part(r,"arm"+i,c(28,24).addBox(-1,0,-1,2,devil?8:5,2).texOffs(40,24).addBox(-1.5f,devil?6:4,-1.5f,3,2,3),s*4,bodyY-7,0);
            PartDefinition leg=part(r,"leg"+i,c(28,40).addBox(-1,0,-1,2,6,2).texOffs(42,40).addBox(-1.5f,4,-2.5f,3,2,4),s*1.8f,18,0);
            PartDefinition wing=r.addOrReplaceChild("wing"+i,c(56,24).addBox(s<0?-7:0,-3,0,7,5,1),PartPose.offsetAndRotation(s*2.5f,bodyY-5,2,0,s*.4f,0));
            if(devil){
                wing.addOrReplaceChild("longwing",c(56,32).addBox(s<0?-12:0,-4,0,12,7,1).texOffs(88,24).addBox(s<0?-13:0,-5,0,13,2,1).texOffs(88,36).addBox(s<0?-11:7,2,0,4,6,1),PartPose.ZERO);
                head.addOrReplaceChild("horn"+i,c(56,0).addBox(-1.5f,-5,-1.5f,3,5,3).texOffs(72,0).addBox(-1,-9,-1,2,5,2).texOffs(84,0).addBox(-.5f,-11,-1,1,3,1),PartPose.offsetAndRotation(s*3,-6,0,-.32f,0,s*.42f));
                arm.addOrReplaceChild("claws",c(112,32).addBox(-1,7,-2,1,3,1).texOffs(112,32).addBox(.2f,7,-2,1,2,1),PartPose.ZERO);
                body.addOrReplaceChild("plate"+i,c(96,24).addBox(-2,-1,-2.7f,4,4,1),PartPose.offset(s*2,-7,0));
            }else if(ice){
                for(int q=0;q<3;q++)wing.addOrReplaceChild("ice"+q,c(56,40).addBox(-1,-7-q,0,2,12+q,2).texOffs(72,40).addBox(-.5f,-9-q,.4f,1,3,1),PartPose.offsetAndRotation(s*(3+q*2),0,0,0,0,s*(.35f+q*.22f)));
                head.addOrReplaceChild("crystal"+i,c(56,0).addBox(-1.5f,-7,-1.5f,3,7,3).texOffs(72,0).addBox(-.6f,-10,-.6f,1.2f,4,1.2f),PartPose.offsetAndRotation(s*3,-6,0,.12f,0,s*.38f));
                body.addOrReplaceChild("iceShoulder"+i,c(96,24).addBox(-1,-3,-1,2,5,2),PartPose.offsetAndRotation(s*3,-5,0,0,0,s*.4f));
            }else if(night){
                wing.addOrReplaceChild("veil",c(56,32).addBox(s<0?-10:0,-2,0,10,10,1).texOffs(88,24).addBox(s<0?-10:6,7,0,4,5,1),PartPose.ZERO);
                head.addOrReplaceChild("hood"+i,c(56,0).addBox(-1.5f,-6,-3,3,8,6),PartPose.offset(s*3.6f,-3,0));
            }else{
                wing.addOrReplaceChild("emberwing",c(56,32).addBox(s<0?-8:0,-4,0,8,5,1).texOffs(88,24).addBox(s<0?-9:0,-5,0,9,2,1),PartPose.ZERO);
                head.addOrReplaceChild("flare"+i,c(56,0).addBox(-1.2f,-4,-1.2f,2.4f,4,2.4f).texOffs(72,0).addBox(-.7f,-7,-.7f,1.4f,4,1.4f),PartPose.offsetAndRotation(s*3,-6,0,0,0,s*.3f));
                head.addOrReplaceChild("ear"+i,c(88,0).addBox(-1,-1,-1,2,3,2),PartPose.offsetAndRotation(s*4,-3,0,0,0,s*.65f));
            }
        }
        PartDefinition tail=r.addOrReplaceChild("tail",c(0,46).addBox(-1,-1,0,2,2,7),PartPose.offsetAndRotation(0,bodyY-1,2,-.3f,0,0));
        tail.addOrReplaceChild("tip",c(20,46).addBox(-1.6f,-1.6f,0,3.2f,3.2f,2),PartPose.offsetAndRotation(0,0,6,0,0,.7f));
        if(devil)tail.addOrReplaceChild("longtail",c(0,56).addBox(-.8f,-.8f,0,1.6f,1.6f,6),PartPose.offsetAndRotation(0,0,7,-.5f,0,0));
        if(ice)head.addOrReplaceChild("crown",c(72,0).addBox(-1,-9,-1,2,10,2),PartPose.offset(0,-6,0));
        if(night){head.addOrReplaceChild("crown",c(56,0).addBox(-5,-9,-4,10,3,8),PartPose.ZERO);body.addOrReplaceChild("cloak",c(56,32).addBox(-4,-5,2,8,11,1),PartPose.ZERO);}
        body.addOrReplaceChild("chest",c(96,16).addBox(-2,-5,-2.6f,4,4,1),PartPose.offsetAndRotation(0,0,0,0,0,.15f));
        return LayerDefinition.create(m,128,64);
    }
    static LayerDefinition angel(){
        MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
        PartDefinition body=part(r,"body",c(0,0).addBox(-5,-5,-4,10,10,8),0,16,0);
        body.addOrReplaceChild("centralEye",c(0,22).addBox(-5,-4,-5,10,8,1).texOffs(0,22).addBox(-5,-4,4,10,8,1),PartPose.ZERO);
        for(int ring=0;ring<3;ring++){
            int segments=12+ring*4;float rad=12+ring*5;
            PartDefinition band=r.addOrReplaceChild("ring"+ring,CubeListBuilder.create(),PartPose.offsetAndRotation(0,16,0,ring==1?1.05f:0,ring==2?1.05f:0,ring*.8f));
            for(int i=0;i<segments;i++){
                float a=(float)(i*Math.PI*2/segments);float width=(float)(2*rad*Math.sin(Math.PI/segments))+.2f;
                PartDefinition seg=band.addOrReplaceChild("segment"+i,c(40,0).addBox(-width/2,-1.6f,-1.4f,width,3.2f,2.8f),PartPose.offsetAndRotation((float)Math.sin(a)*rad,(float)Math.cos(a)*rad,0,0,0,-a));
                seg.addOrReplaceChild("eye",c(64,0).addBox(-3,-2.6f,-2.5f,6,5,1).texOffs(64,0).addBox(-3,-2.6f,1.5f,6,5,1),PartPose.ZERO);
                seg.addOrReplaceChild("outerEye",c(84,0).addBox(-2,-2,-1,4,4,1),PartPose.offsetAndRotation(0,1.8f,0,1.57f,0,0));
            }
        }
        return LayerDefinition.create(m,128,64);
    }
}''')
edit(java/'Familiar.java',[
('if(getHealth()<getMaxHealth())setHealth(getMaxHealth());clearFire();','''if(getHealth()<getMaxHealth())setHealth(getMaxHealth());clearFire();
        if(getType()==Noctis.IMP.get()&&tickCount%4==0&&level() instanceof ServerLevel fireLevel){
            fireLevel.sendParticles(net.minecraft.core.particles.ParticleTypes.FLAME,getX(),getY()+.65,getZ(),5,.24,.35,.24,.025);
            fireLevel.sendParticles(net.minecraft.core.particles.ParticleTypes.SMALL_FLAME,getX(),getY()+1,getZ(),3,.2,.22,.2,.01);
            fireLevel.sendParticles(net.minecraft.core.particles.ParticleTypes.SMOKE,getX(),getY()+.9,getZ(),1,.13,.2,.13,.01);
        }''')
])
edit(java/'Angel.java',[
('}else setDeltaMovement(getDeltaMovement().scale(.85));','''}else {double floor=l.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,getBlockX(),getBlockZ());
            double dy=getY()<floor+4?.10:0;setDeltaMovement(getDeltaMovement().scale(.85).add(0,dy,0));}''')
])
# First-person cigarette pose and smoke during the whole use, not just at the end.
edit(java/'SmokeItem.java',[
('return UseAnim.DRINK;','return UseAnim.NONE;'),
('p.startUsingItem(h);return InteractionResultHolder.consume(p.getItemInHand(h));','if(p.getCooldowns().isOnCooldown(this))return InteractionResultHolder.fail(p.getItemInHand(h));p.startUsingItem(h);return InteractionResultHolder.consume(p.getItemInHand(h));'),
('    @Override public ItemStack finishUsingItem','''    @Override public void onUseTick(Level l,LivingEntity e,ItemStack s,int remaining){
        if(l instanceof ServerLevel sl&&remaining%5==0){
            net.minecraft.world.phys.Vec3 pos=e.getEyePosition().add(e.getLookAngle().scale(.28));
            sl.sendParticles(ParticleTypes.SMOKE,pos.x,pos.y-.12,pos.z,3,.025,.035,.025,.015);
            if(remaining%10==0)sl.sendParticles(ParticleTypes.SMALL_FLAME,pos.x,pos.y-.16,pos.z,1,0,0,0,0);
        }
    }
    @Override public void initializeClient(java.util.function.Consumer<net.minecraftforge.client.extensions.common.IClientItemExtensions> consumer){
        consumer.accept(new net.minecraftforge.client.extensions.common.IClientItemExtensions(){
            @Override public boolean applyForgeHandTransform(com.mojang.blaze3d.vertex.PoseStack pose,net.minecraft.client.player.LocalPlayer p,net.minecraft.world.entity.HumanoidArm arm,ItemStack s,float partial,float equip,float swing){
                if(!p.isUsingItem()||p.getUseItem()!=s)return false;
                int sign=arm==net.minecraft.world.entity.HumanoidArm.RIGHT?1:-1;
                float age=getUseDuration(s)-p.getUseItemRemainingTicks()+partial;
                float lift=Math.min(1,age/8f),out=Math.min(1,p.getUseItemRemainingTicks()/6f),t=lift*out;
                pose.translate(sign*(.56-.38*t),-.52+.45*t+Math.sin(age*.24)*.012,-.72+.23*t);
                pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(-12-25*t));
                pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(sign*(15+40*t)));
                pose.mulPose(com.mojang.math.Axis.ZP.rotationDegrees(sign*(12+22*t)));
                return true;
            }
        });
    }
    @Override public ItemStack finishUsingItem''')
])
# New friendly vampire vocal-like sound, and use it for the bow.
edit(java/'FallenEncounter.java',[
('static final RegistryObject<SoundEvent> THEME=', '''static final RegistryObject<SoundEvent> VAMP_HELLO=SOUNDS.register("vampire_friendly",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"vampire_friendly")));
    static final RegistryObject<SoundEvent> THEME=''')
])
edit(java/'Vampire.java',[
('return net.minecraft.sounds.SoundEvents.WANDERING_TRADER_AMBIENT;','return FallenEncounter.VAMP_HELLO.get();'),
('bowTo(p);playSound(net.minecraft.sounds.SoundEvents.VILLAGER_YES,.7f,.85f);','bowTo(p);playSound(FallenEncounter.VAMP_HELLO.get(),.8f,1f);')
])
# Custom textures with explicit cube UV face coordinates and readable eyes.
def png(path,w,h,fn):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for x in range(w) for v in fn(x,y)) for y in range(h))
    p=assets/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
def canvas(name,base):
    rng=random.Random(name);pix=[[(*base,255) for x in range(128)] for y in range(64)]
    def rect(x,y,w,h,col,noise=0):
        for yy in range(max(0,y),min(64,y+h)):
            for xx in range(max(0,x),min(128,x+w)):
                d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col)+(255,)
    return pix,rect
for name,base,dark,trim,light in [
    ('imp',(157,55,34),(49,22,26),(239,119,37),(255,223,113)),
    ('devil',(96,29,48),(27,16,29),(176,65,72),(247,181,78)),
    ('frost_familiar',(63,139,203),(24,56,101),(114,211,245),(235,255,255)),
    ('night_familiar',(55,38,83),(20,13,39),(122,74,177),(221,160,255))]:
    pix,R=canvas(name,base);R(0,0,128,64,base,13)
    R(0,0,30,13,base,9);R(6,6,8,7,base,4);R(6,6,8,1,dark)
    R(7,8,2,2,dark);R(11,8,2,2,dark);R(7,8,2,1,light);R(11,8,2,1,light);R(8,11,4,1,dark)
    R(8,11,1,1,(248,237,210));R(11,11,1,1,(248,237,210))
    R(0,24,24,14,dark,9);R(4,28,6,7,base,8);R(4,29,1,5,trim);R(9,29,1,5,trim);R(6,30,2,3,light)
    R(28,24,16,15,base,12);R(40,24,14,12,dark,8);R(28,40,24,16,dark,12);R(42,40,14,12,trim,10)
    R(56,0,40,23,trim,13);R(56,24,40,30,dark,10);R(88,24,32,18,trim,12);R(96,16,22,8,light,6);R(96,24,24,14,trim,8)
    R(0,46,25,18,base,9);R(20,46,18,8,light,9)
    if name=='imp':
        for x,y in [(3,2),(15,5),(22,9),(3,31),(11,33),(30,29),(60,33),(65,36),(74,40),(12,52)]:
            R(x,y,3,1,trim);R(x+1,y+1,1,2,light)
    elif name=='devil':
        R(6,7,3,1,dark);R(11,7,3,1,dark);R(7,8,2,1,light);R(11,8,2,1,light)
        for x in range(59,94,7):R(x,25,1,21,trim)
        R(56,0,40,12,dark,12);R(96,24,24,14,(134,109,61),12)
    elif name=='frost_familiar':
        for x in range(57,120,5):
            R(x,1,1,20,light);R(x+1,25,1,24,(161,231,251))
        R(7,8,2,2,light);R(11,8,2,2,light);R(6,6,8,1,(89,199,245))
    else:
        R(6,6,8,7,dark,4);R(7,8,2,1,light);R(11,8,2,1,light)
        for x in range(60,95,8):R(x,32,1,11,trim)
    png('textures/entity/'+name+'.png',128,64,lambda x,y,pix=pix:pix[y][x])
pix,R=canvas('ophanim',(155,110,38));R(0,0,128,64,(143,99,35),9);R(0,0,40,22,(177,124,45),11);R(40,0,23,14,(207,158,58),12)
def eye(x,y,w,h):
    R(x,y,w,h,(65,40,31));R(x+1,y+1,w-2,h-2,(247,240,217))
    if w>=6:
        R(x+w//2-1,y+1,2,h-2,(124,66,31));R(x+w//2,y+1,1,h-2,(12,12,20));R(x+w//2-1,y+1,1,1,(255,255,255))
    else:R(x+w//2,y+1,1,max(1,h-2),(15,14,24))
# Front/back UVs of 6x5x1, 4x4x1 and 10x8x1 boxes.
for x in [65,72]:eye(x,1,6,5)
for x in [85,90]:eye(x,1,4,4)
for x in [1,12]:eye(x,23,10,8)
R(40,0,23,1,(248,206,113));R(41,4,21,1,(103,63,23))
png('textures/entity/ophanim.png',128,64,lambda x,y:pix[y][x])
def wine(x,y):
    if 6<=x<=9 and 1<=y<=3:return (172,121,72,255)
    if 6<=x<=9 and 4<=y<=6:return (166,198,221,210)
    if 4<=x<=11 and 7<=y<=14:
        if x in (4,11) or y in (7,14):return (123,154,183,220)
        if y==8:return (213,105,230,255)
        if x==5:return (220,144,240,255)
        return (126+(y%3)*13,28,158+(y%2)*20,255)
    return (0,0,0,0)
png('textures/item/wine_bottle.png',16,16,wine)
j('assets/noctismagic/models/item/wine_bottle.json',{"parent":"minecraft:item/generated","textures":{"layer0":"noctismagic:item/wine_bottle"}})
for id in ['one_winged_angel','sora']:j('assets/noctismagic/models/item/'+id+'_spawn_egg.json',{"parent":"minecraft:item/template_spawn_egg"})
# A short, original low-pitched warm greeting: synthesized vowel formants, soft breath, no reused villager audio.
rate=22050;dur=1.35;rng=random.Random(77);pcm=array.array('h');ph=0
for i in range(int(rate*dur)):
    t=i/rate;f=111+14*math.sin(math.pi*t/dur)-9*t;ph+=2*math.pi*f/rate
    env=min(1,t/.12)*min(1,max(0,(dur-t)/.27))*(.62+.38*math.sin(math.pi*t/dur))
    v=0
    for h in range(1,19):
        freq=f*h
        weight=(.72*math.exp(-((freq-340)/180)**2)+.44*math.exp(-((freq-1050)/280)**2)+.16*math.exp(-((freq-2250)/450)**2))/math.sqrt(h)
        v+=weight*math.sin(ph*h)
    v=env*(.18*v+.012*(rng.random()*2-1))
    pcm.append(int(max(-.95,min(.95,v))*32767))
sounddir=assets/'sounds';wav=sounddir/'vampire_friendly.wav'
with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm.tobytes())
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(sounddir/'vampire_friendly.ogg')],check=True);wav.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['vampire_friendly']={"sounds":[{"name":"noctismagic:vampire_friendly"}]};p.write_text(json.dumps(d),encoding='utf-8')
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
    d.update({'item.noctismagic.one_winged_angel_spawn_egg':'One Winged Angel','item.noctismagic.sora_spawn_egg':'Uovo generatore: Sora' if it else 'Sora Spawn Egg','item.noctismagic.wine_bottle':'Ampolla di vino' if it else 'Wine Bottle','item.noctismagic.miracle_liquid_bucket':'Secchio di vino' if it else 'Wine Bucket','block.noctismagic.miracle_liquid':'Vino' if it else 'Wine','fluid_type.noctismagic.miracle_liquid':'Vino' if it else 'Wine'})
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.8.0 source patch applied')
