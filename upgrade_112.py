"""1.1.2: SirPiovra summons his colossal father after two player strikes."""
from pathlib import Path
import sys,json,struct,zlib,math
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Cthulhu>> CTHULHU=ENTITIES.register("cthulhu",()->EntityType.Builder.<Cthulhu>of(Cthulhu::new,MobCategory.MONSTER).sized(5.2f,10.5f).clientTrackingRange(16).fireImmune().build(ID+":cthulhu"));
    public static final RegistryObject<Item> CTHULHU_EGG=ITEMS.register("cthulhu_spawn_egg",()->new ForgeSpawnEggItem(CTHULHU,0x183f39,0x8bba66,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(CTHULHU.get(),Cthulhu.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(CTHULHU_EGG.get());')
(java/'CthulhuRitual.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class CthulhuRitual{
    @SubscribeEvent public static void strike(AttackEntityEvent e){
        if(!(e.getEntity() instanceof ServerPlayer p)||p.isSpectator()||p.isCreative()||!(e.getTarget() instanceof Familiar f)||f.getType()!=Noctis.OCTOPUS.get()||!f.isAlive())return;
        ServerLevel l=p.serverLevel();var d=f.getPersistentData();long now=l.getGameTime();
        if(d.getLong("FatherCooldown")>now||d.getLong("FatherHitAt")>now)return;
        d.putLong("FatherHitAt",now+10);
        String k="FatherStrikes_"+p.getUUID();
        int count=d.getInt(k)+1;d.putInt(k,Math.min(2,count));
        if(count<2){NpcDialogue.say(l,Component.literal("SirPiovra: Mio caro, non costringermi a chiamare mio padre."));return;}
        if(!l.getEntitiesOfClass(Cthulhu.class,p.getBoundingBox().inflate(128)).isEmpty()){NpcDialogue.say(l,Component.literal("SirPiovra: Mio padre e' gia qui."));d.putInt(k,0);d.putLong("FatherCooldown",now+1200);return;}
        Cthulhu boss=Noctis.CTHULHU.get().create(l);if(boss==null)return;
        BlockPos pos=null;
        for(int i=0;i<48;i++){
            double angle=Math.toRadians(p.getYRot()+90)+(i==0?0:(i%2==0?1:-1)*((i+1)/2)*Math.PI/24);
            int r=16+(i%4)*4,x=p.getBlockX()+(int)Math.round(Math.cos(angle)*r),z=p.getBlockZ()+(int)Math.round(Math.sin(angle)*r);
            if(!l.hasChunkAt(new BlockPos(x,p.getBlockY(),z)))continue;
            int y=l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
            if(Math.abs(y-p.getBlockY())>14||y+12>=l.getMaxBuildHeight())continue;
            BlockPos q=new BlockPos(x,y,z);boss.moveTo(x+.5,y,z+.5,p.getYRot()+180,0);
            if(l.getWorldBorder().isWithinBounds(q)&&l.noCollision(boss)){pos=q;break;}
        }
        if(pos==null){p.sendSystemMessage(Component.literal("Cthulhu non trova spazio: porta SirPiovra in un luogo aperto e riprova."));return;}
        boss.bind(p);boss.setPersistenceRequired();
        if(!l.addFreshEntity(boss))return;
        d.putInt(k,0);d.putLong("FatherCooldown",now+12000);
        NpcDialogue.say(l,Component.literal("SirPiovra: PAPAAAA!"));
        NpcDialogue.say(l,Component.literal("Cthulhu: CHI OSA TOCCARE MIO FIGLIO?!").withStyle(net.minecraft.ChatFormatting.DARK_GREEN,net.minecraft.ChatFormatting.BOLD));
        l.sendParticles(ParticleTypes.SCULK_SOUL,boss.getX(),boss.getY()+4,boss.getZ(),120,3,4,3,.08);
        l.playSound(null,boss.blockPosition(),SoundEvents.WARDEN_ROAR,net.minecraft.sounds.SoundSource.HOSTILE,4,.5f);
    }
}''',encoding='utf-8')
(java/'Cthulhu.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Cthulhu extends Monster{
    final ServerBossEvent bar=new ServerBossEvent(Component.literal("Cthulhu - Padre di SirPiovra"),BossEvent.BossBarColor.GREEN,BossEvent.BossBarOverlay.NOTCHED_20);
    UUID attacker;int cooldown=75,phase,attack,pose,vanish;
    public Cthulhu(EntityType<? extends Monster> t,Level l){super(t,l);setNoGravity(true);bar.setDarkenScreen(true);}
    public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,1000).add(Attributes.ATTACK_DAMAGE,30).add(Attributes.ARMOR,16).add(Attributes.FOLLOW_RANGE,100).add(Attributes.MOVEMENT_SPEED,.3).add(Attributes.KNOCKBACK_RESISTANCE,1);}
    public void bind(ServerPlayer p){attacker=p.getUUID();setTarget(p);}
    @Override protected void registerGoals(){}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);bar.addPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
    @Override public void remove(RemovalReason reason){bar.removeAllPlayers();super.remove(reason);}
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(!(level() instanceof ServerLevel l)||!isAlive())return;
        bar.setProgress(getHealth()/getMaxHealth());setNoGravity(true);
        Player t=attacker==null?l.getNearestPlayer(this,64):l.getPlayerByUUID(attacker);
        if(t==null||!t.isAlive()||t.isSpectator()||t.isCreative()||distanceTo(t)>100){setDeltaMovement(getDeltaMovement().scale(.7));if(++vanish>1200)discard();return;}
        vanish=0;setTarget(t);
        int next=getHealth()<getMaxHealth()*.33?2:getHealth()<getMaxHealth()*.67?1:0;
        if(next>phase){phase=next;NpcDialogue.say(l,Component.literal(phase==1?"Cthulhu: Gli abissi si risvegliano!":"Cthulhu: R'lyeh chiama il tuo nome!"));playSound(SoundEvents.WARDEN_ROAR,3,.55f);l.sendParticles(ParticleTypes.SCULK_SOUL,getX(),getY()+5,getZ(),80,3,4,3,.08);}
        Vec3 diff=t.position().subtract(position());double d=diff.horizontalDistance();
        float yaw=(float)(Math.atan2(diff.z,diff.x)*180/Math.PI)-90;setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);
        double dy=t.getY()-getY();Vec3 flat=new Vec3(diff.x,0,diff.z);Vec3 speed=d>7?flat.normalize().scale(phase==2?.48:.30):Vec3.ZERO;
        speed=speed.add(0,Math.max(-.22,Math.min(.22,dy*.08)),0);
        if(!l.noCollision(this,getBoundingBox().move(speed))){Vec3 up=new Vec3(0,.30,0);speed=l.noCollision(this,getBoundingBox().move(up))?up:Vec3.ZERO;}
        setDeltaMovement(getDeltaMovement().scale(.35).add(speed.scale(.65)));
        if(tickCount%5==0)l.sendParticles(ParticleTypes.SQUID_INK,getX(),getY()+4,getZ(),5,2,2,2,.01);
        if(--cooldown>0)return;
        if(distanceTo(t)>32||!hasLineOfSight(t)){cooldown=15;return;}
        cooldown=phase==2?38:phase==1?55:75;int mode=attack++%3;l.broadcastEntityEvent(this,(byte)84);
        if(mode==0){
            if(d>11){cooldown=15;attack--;return;}
            t.hurt(damageSources().mobAttack(this),30+phase*5);t.knockback(1.8,-diff.x,-diff.z);
            l.sendParticles(ParticleTypes.POOF,t.getX(),t.getY()+.5,t.getZ(),38,1,.5,1,.13);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,3,.45f);
        }else if(mode==1){
            Vec3 a=position().add(0,6,0),b=t.getEyePosition();
            for(int i=0;i<32;i++){Vec3 q=a.lerp(b,i/31.0);l.sendParticles(ParticleTypes.SCULK_SOUL,q.x,q.y,q.z,2,.15,.15,.15,.03);}
            t.hurt(damageSources().magic(),18+phase*4);t.addEffect(new MobEffectInstance(MobEffects.DARKNESS,100,0));t.addEffect(new MobEffectInstance(MobEffects.CONFUSION,140,0));playSound(SoundEvents.WARDEN_SONIC_BOOM,2,.65f);
        }else{
            for(int i=0;i<36;i++){double a=i*Math.PI/18;double r=4+(i%3)*2;l.sendParticles(ParticleTypes.DRAGON_BREATH,t.getX()+Math.cos(a)*r,t.getY()+.4,t.getZ()+Math.sin(a)*r,3,.25,.2,.25,.03);}
            t.hurt(damageSources().magic(),15+phase*4);t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,80,1));t.addEffect(new MobEffectInstance(MobEffects.POISON,100,0));playSound(SoundEvents.ENDER_DRAGON_GROWL,2,.5f);
        }
    }
    @Override public void handleEntityEvent(byte id){if(id==84){pose=24;return;}super.handleEntityEvent(id);}
    public float attackPose(){return pose<=0?0:(float)Math.sin(pose*Math.PI/24);}
    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource s,int looting,boolean hit){super.dropCustomDeathLoot(s,looting,hit);spawnAtLocation(net.minecraft.world.item.Items.NETHER_STAR);for(int i=0;i<12;i++)spawnAtLocation(Noctis.CRYSTAL.get());}
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);if(attacker!=null)n.putUUID("Attacker",attacker);n.putInt("Phase",phase);n.putInt("Attack",attack);}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);attacker=n.hasUUID("Attacker")?n.getUUID("Attacker"):null;phase=n.getInt("Phase");attack=n.getInt("Attack");}
}''',encoding='utf-8')
# Colossal custom geometry: hunched torso, octopus head, moving face tentacles, wings and claws.
N=256;S=4;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N,(mat,u,v)
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((fx,fy,fw,fh,mat,face))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
part('b','r','body',(0,-2,0),(.08,0,0),[(-7,-10,-4,14,14,9,'skin'),(-5,4,-3,10,8,7,'rib')])
part('h','b','head',(0,-10,-1),(.10,0,0),[(-6,-10,-5,12,10,10,'head'),(-5,-5,-6,10,6,4,'head')])
for i,side in enumerate((-1,1)):
    part('eye'+str(i),'h','eye'+str(i),(side*3,-5,-6.2),(0,side*.12,side*.16),[(-2,-1,-.5,4,2,1,'eye')])
    part('brow'+str(i),'h','brow'+str(i),(side*3,-7,-6),(0,0,-side*.22),[(-2,-.5,-.5,4,1,1,'skin')])
    part('arm'+str(i),'b','arm'+str(i),(side*8,-7,0),(0,0,-side*.24),[(-2,-2,-2,4,10,5,'skin'),(-2,8,-2,4,8,4,'rib')])
    for n in range(3):part(f'claw{i}{n}','arm'+str(i),f'claw{n}',(-2+n*1.5,16,-1),(-.23,0,0),[(-.5,0,-.5,1,4,1,'claw')])
    part('leg'+str(i),'r','leg'+str(i),(side*3.5,9,0),(0,0,side*.08),[(-3,0,-3,6,8,6,'skin'),(-2,8,-2,4,6,4,'rib'),(-3,14,-5,6,2,7,'claw')])
    part('wing'+str(i),'b','wing'+str(i),(side*5,-8,4),(0,side*.35,0),[(0 if side>0 else -12,-5,0,12,2,2,'skin'),(0 if side>0 else -10,-4,.5,10,13,1,'membrane')])
    for n in range(3):
        part(f'wingtip{i}{n}','wing'+str(i),f'wingtip{n}',(side*(9+n*3),-4+n*3,1),(0,0,side*(.40+n*.18)),[(0 if side>0 else -7,0,0,7,1,1,'skin'),(0 if side>0 else -6,1,.2,6,7-n,1,'membrane')])
for i in range(8):
    x=-4.5+i*1.28
    part('t'+str(i),'h','tentacle'+str(i),(x,-1,-5.8),(-.24,0,(i-3.5)*.13),[(-.8,0,-.8,2,7+(i%3),2,'tentacle')])
    part('tip'+str(i),'t'+str(i),'tip',(0,7+(i%3),0),(-.35,0,0),[(-.5,0,-.5,1,5,1,'tentacle')])
(java/'CthulhuClient.java').write_text('''package it.noctis.magic;
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
public class CthulhuClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"cthulhu"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,CthulhuClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.CTHULHU.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<Cthulhu>{
        final ModelPart root,body,head;final ModelPart[] arms=new ModelPart[2],legs=new ModelPart[2],wings=new ModelPart[2],tentacles=new ModelPart[8];
        Model(ModelPart r){root=r;body=r.getChild("body");head=body.getChild("head");for(int i=0;i<2;i++){arms[i]=body.getChild("arm"+i);legs[i]=r.getChild("leg"+i);wings[i]=body.getChild("wing"+i);}for(int i=0;i<8;i++)tentacles[i]=head.getChild("tentacle"+i);}
        @Override public void setupAnim(Cthulhu e,float limb,float amount,float age,float yaw,float pitch){
            float attack=e.attackPose();head.yRot=yaw*.012f;head.xRot=.10f+pitch*.008f;body.xRot=.08f+attack*.17f;
            for(int i=0;i<2;i++){int sign=i==0?-1:1;float walk=(float)Math.cos(limb*.55+i*Math.PI)*amount;arms[i].xRot=-walk*.4f-attack*1.15f;arms[i].zRot=-sign*(.24f+attack*.28f);legs[i].xRot=walk*.45f;wings[i].yRot=sign*(.35f+(float)Math.sin(age*.10)*.27f+attack*.20f);}
            for(int i=0;i<8;i++){tentacles[i].xRot=-.24f+(float)Math.sin(age*.14+i*.63)*.23f-attack*.50f;tentacles[i].zRot=(i-3.5f)*.13f+(float)Math.sin(age*.12+i)*.13f;tentacles[i].getChild("tip").xRot=-.35f+(float)Math.cos(age*.18+i)*.28f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    }
    static class Renderer extends MobRenderer<Cthulhu,Model>{
        Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),2.4f);}
        @Override protected void scale(Cthulhu e,PoseStack p,float partial){p.scale(4f,4f,4f);}
        @Override public ResourceLocation getTextureLocation(Cthulhu e){return new ResourceLocation(Noctis.ID,"textures/entity/cthulhu.png");}
    }
}''',encoding='utf-8')
pix=bytearray(W*W*4)
for x,y,w,h,mat,face in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);ripple=.5+.5*math.sin(u*31+v*19+math.sin(v*37));ridge=.5+.5*math.cos(v*math.pi*13)
            if mat=='eye': 
                d=((u-.5)/.42)**2+((v-.5)/.46)**2
                c=(22,44,32) if d>1 else (int(142+90*ripple),int(170+70*ripple),65) if abs(u-.5)>.065 else (7,13,12)
                if (u-.38)**2+(v-.28)**2<.012:c=(242,255,186)
            elif mat=='claw':c=(int(47+56*ripple),int(60+56*ripple),int(48+40*ripple))
            elif mat=='membrane':c=(int(21+35*ripple),int(55+40*ripple),int(48+35*ripple))
            else:
                val=20*ripple+18*math.sin(u*math.pi)+(18*ridge if mat in ('rib','tentacle') else 0)
                c=(int(20+val*.6),int(59+val),int(46+val*.8))
                if mat=='tentacle' and face=='front' and ((u-.5)/.25)**2+(((v*7)%1-.5)/.28)**2<1:c=(95,121,77)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*c,255))
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
(assets/'textures/entity/cthulhu.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(assets/'models/item/cthulhu_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.cthulhu']='Cthulhu';d['item.noctismagic.cthulhu_spawn_egg']='Uovo generatore: Cthulhu' if lang=='it_it' else 'Cthulhu Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'src/main/resources/data/noctismagic/tags/entity_types/vincent_protected.json';d=json.loads(p.read_text());d['values'].append('noctismagic:cthulhu');p.write_text(json.dumps(d))
p=root/'src/main/resources/data/forge/tags/entity_types/bosses.json';p.parent.mkdir(parents=True,exist_ok=True);d=json.loads(p.read_text()) if p.exists() else {'replace':False,'values':[]};d['values'].append('noctismagic:cthulhu');p.write_text(json.dumps(d))
print('Cthulhu father ritual and colossal boss installed')
