"""1.2.7: giant chubby cat boss triggered by five successfully tamed cats."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<GiantCat>> GIANT_CAT=ENTITIES.register("giant_cat",()->EntityType.Builder.<GiantCat>of(GiantCat::new,MobCategory.CREATURE).sized(4.4f,3.8f).clientTrackingRange(14).build(ID+":giant_cat"));
    public static final RegistryObject<Item> GIANT_CAT_EGG=ITEMS.register("giant_cat_spawn_egg",()->new ForgeSpawnEggItem(GIANT_CAT,0xc28d55,0xffe5b8,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(GIANT_CAT.get(),GiantCat.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(GIANT_CAT_EGG.get());')
(java/'CatRitual.java').write_text('''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.animal.Cat;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.living.AnimalTameEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class CatRitual{
    private record Attempt(UUID owner,Cat cat,long time){}
    private static final List<Attempt> pending=new ArrayList<>();
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void tame(AnimalTameEvent e){
        if(e.getAnimal() instanceof Cat c&&e.getTamer() instanceof ServerPlayer p)pending.add(new Attempt(p.getUUID(),c,p.serverLevel().getGameTime()));
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        ServerLevel l=p.serverLevel();var data=Noctis.data(p);
        for(Iterator<Attempt> it=pending.iterator();it.hasNext();){
            Attempt a=it.next();if(!a.owner().equals(p.getUUID()))continue;
            if(l.getGameTime()<=a.time())continue;
            it.remove();Cat c=a.cat();
            if(!c.isTame()||!p.getUUID().equals(c.getOwnerUUID())||c.getPersistentData().getBoolean("NoctisCatCounted"))continue;
            c.getPersistentData().putBoolean("NoctisCatCounted",true);
            int n=Math.min(5,data.getInt("GiantCatTames")+1);data.putInt("GiantCatTames",n);
            p.sendSystemMessage(Component.literal("Patto felino: "+n+"/5").withStyle(net.minecraft.ChatFormatting.GOLD));
            if(n==5&&!data.getBoolean("GiantCatSummoned"))p.sendSystemMessage(Component.literal("Un miagolio assordante risuona in lontananza... cerca uno spazio aperto."));
        }
        if(p.tickCount%20!=0||data.getInt("GiantCatTames")<5||data.getBoolean("GiantCatSummoned")||l.dimension()!=Level.OVERWORLD||l.getDifficulty()==Difficulty.PEACEFUL||p.isSpectator()||p.isCreative())return;
        if(!l.getEntitiesOfClass(GiantCat.class,p.getBoundingBox().inflate(96)).isEmpty())return;
        for(int i=0;i<12;i++){
            BlockPos q=Eclipse.spot(p,9,20);if(q==null)continue;
            GiantCat boss=Noctis.GIANT_CAT.get().create(l);if(boss==null)return;
            boss.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);
            if(!l.noCollision(boss))continue;
            boolean solid=true;
            for(int dx=-2;dx<=2;dx++)for(int dz=-2;dz<=2;dz++){BlockPos b=q.offset(dx,-1,dz);if(!l.hasChunkAt(b)||!l.getBlockState(b).isFaceSturdy(l,b,Direction.UP))solid=false;}
            if(!solid)continue;
            boss.bind(p);if(l.addFreshEntity(boss)){
                data.putBoolean("GiantCatSummoned",true);
                NpcDialogue.say(l,Component.literal("MIAUGUSTO, IL DIVORATORE DI CROCCHETTE, SI E' RISVEGLIATO!").withStyle(net.minecraft.ChatFormatting.GOLD,net.minecraft.ChatFormatting.BOLD));
                l.sendParticles(ParticleTypes.CLOUD,boss.getX(),boss.getY()+1,boss.getZ(),90,2,.7,2,.12);
                boss.playSound(net.minecraft.sounds.SoundEvents.CAT_HISS,3,.45f);return;
            }
        }
    }
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){pending.clear();}
}''',encoding='utf-8')
(java/'GiantCat.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class GiantCat extends PathfinderMob{
    final ServerBossEvent bar=new ServerBossEvent(Component.literal("Miaugusto - Divoratore di Crocchette"),BossEvent.BossBarColor.YELLOW,BossEvent.BossBarOverlay.NOTCHED_20);
    UUID challenger;int cooldown=85,phase,mode,windup,pose,animation;
    public GiantCat(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setPersistenceRequired();setMaxUpStep(1);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,650).add(Attributes.ARMOR,12).add(Attributes.ATTACK_DAMAGE,26).add(Attributes.MOVEMENT_SPEED,.25).add(Attributes.FOLLOW_RANGE,64).add(Attributes.KNOCKBACK_RESISTANCE,.95);}
    public void bind(ServerPlayer p){challenger=p.getUUID();setTarget(p);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public boolean causeFallDamage(float a,float b,net.minecraft.world.damagesource.DamageSource d){return false;}
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);bar.addPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
    @Override public void remove(RemovalReason reason){bar.removeAllPlayers();super.remove(reason);}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal("Miaugusto: "+s));}
    @Override public void tick(){
        super.tick();if(pose>0)pose--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        bar.setProgress(Math.max(0,getHealth()/getMaxHealth()));
        Player p=challenger==null?l.getNearestPlayer(this,40):l.getPlayerByUUID(challenger);
        if(p==null||!p.isAlive()||p.isCreative()||p.isSpectator()||distanceTo(p)>64||l.getDifficulty()==Difficulty.PEACEFUL){getNavigation().stop();setTarget(null);windup=0;return;}
        setTarget(p);getLookControl().setLookAt(p,30,30);
        int next=getHealth()<getMaxHealth()*.33?2:getHealth()<getMaxHealth()*.67?1:0;
        if(next>phase){phase=next;say(l,phase==1?"HO ANCORA FAME!":"ORA VOGLIO TUTTE LE CROCCHETTE!");playSound(SoundEvents.CAT_HISS,3,.55f);}
        if(windup>0){
            getNavigation().stop();
            if(--windup==0){perform(l,p,mode);mode=(mode+1)%3;cooldown=phase==2?44:phase==1?60:80;}
            return;
        }
        double d=distanceTo(p);if(d>5)getNavigation().moveTo(p,phase==2?1.25:1.0);else getNavigation().stop();
        if(cooldown>0)cooldown--;
        if(cooldown==0&&d<9&&hasLineOfSight(p)){
            windup=22;getNavigation().stop();l.broadcastEntityEvent(this,(byte)(97+mode));
            playSound(SoundEvents.CAT_AMBIENT,3,.5f);
            if(mode==1)say(l,"PANCIATA SUPREMA!");
            if(mode==2)say(l,"MIIIIIAAAAAOOO!");
            l.sendParticles(ParticleTypes.CLOUD,getX(),getY()+.3,getZ(),20,2,.15,2,.02);
        }
    }
    void perform(ServerLevel l,Player p,int attack){
        if(!hasLineOfSight(p))return;
        double d=distanceTo(p);Vec3 v=p.position().subtract(position());
        if(attack==0&&d<6.5){p.hurt(damageSources().mobAttack(this),26+phase*4);p.knockback(1.2,-v.x,-v.z);l.sendParticles(ParticleTypes.SWEEP_ATTACK,p.getX(),p.getY()+1,p.getZ(),5,.5,.5,.5,0);}
        else if(attack==1&&d<8){p.hurt(damageSources().mobAttack(this),32+phase*4);p.knockback(2.0,-v.x,-v.z);p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,1));l.sendParticles(ParticleTypes.POOF,getX(),getY()+.25,getZ(),60,3,.3,3,.12);playSound(SoundEvents.GENERIC_BIG_FALL,3,.6f);}
        else if(attack==2&&d<10){p.hurt(damageSources().magic(),16+phase*4);p.addEffect(new MobEffectInstance(MobEffects.CONFUSION,100,0));p.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,100,0));l.sendParticles(ParticleTypes.SONIC_BOOM,p.getX(),p.getY()+1,p.getZ(),1,0,0,0,0);playSound(SoundEvents.CAT_HISS,3,.45f);}
    }
    @Override public void handleEntityEvent(byte id){if(id>=97&&id<=99){pose=34;animation=id-97;return;}super.handleEntityEvent(id);}
    public float attackPose(){return pose<=0?0:(float)Math.sin(pose*Math.PI/34);}
    public int attackAnimation(){return animation;}
    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource s,int looting,boolean hit){super.dropCustomDeathLoot(s,looting,hit);spawnAtLocation(Items.NETHER_STAR);spawnAtLocation(Items.COOKED_COD,32);spawnAtLocation(Items.COOKED_SALMON,16);for(int i=0;i<8;i++)spawnAtLocation(Noctis.CRYSTAL.get());}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(challenger!=null)t.putUUID("Challenger",challenger);t.putInt("Phase",phase);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);challenger=t.hasUUID("Challenger")?t.getUUID("Challenger"):null;phase=t.getInt("Phase");}
}''',encoding='utf-8')
# Layered silhouette: barrel-shaped belly, fat haunches, rounded cheeks, muzzle, whiskers,
# separate toes, layered fur tufts, articulated tail, and expressive eyes.
N=256;S=8;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N,(mat,cx,cy)
    for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,mat,f))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
part('b','r','body',(0,12,1),(0,0,0),[(-9,-8,-8,18,14,20,'tabby'),(-11,-5,-6,22,10,16,'tabby'),(-8,-10,-6,16,4,16,'tabby'),(-8,4,-6,16,5,17,'cream')])
part('belly','b','belly',(0,4,-1),(0,0,0),[(-9,-1,-7,18,6,16,'cream')])
part('h','r','head',(0,7,-9),(0,0,0),[(-7,-7,-6,14,12,12,'face'),(-8,-3,-5,16,6,10,'face'),(-6,-8,-5,12,3,10,'tabby'),(-6,3,-5,12,3,10,'cream')])
part('muzzle','h','muzzle',(0,1,-6),(0,0,0),[(-5,-1,-2,10,4,3,'muzzle'),(-1.5,-1.8,-3,3,2,1,'nose'),(-2,3,-1,4,1,2,'mouth')])
for i,s in enumerate((-1,1)):
    part('ear'+str(i),'h','ear'+str(i),(s*5.7,-6,0),(0,0,s*.23),[(-2,-5,-1.6,4,5,3,'tabby'),(-1.4,-6,-1,3,2,2,'tabby'),(-1.5,-4,-1.8,3,3,1,'inner')])
    part('cheek'+str(i),'h','cheek'+str(i),(s*6.5,0,-3),(0,0,s*.14),[(-2,-3,-3,4,6,6,'cream'),(-1.5,-1,-3.2,3,3,1,'muzzle')])
    for j in range(3):
        part(f'whisk{i}{j}','cheek'+str(i),f'whisk{j}',(s*1.5,-.7+j*.8,-2.5),(0,s*.2,s*(j-1)*.17),[(0 if s>0 else -5,-.12,-.12,5,1,1,'whisk')])
    for j,z in enumerate((-6,8)):
        part(f'leg{i}{j}','r',f'leg{i}{j}',(s*6.8,17,z),(0,0,0),[(-3,-2,-3,6,5,6,'tabby'),(-3,3,-4,6,4,7,'cream')])
        for k in range(3):part(f'toe{i}{j}{k}',f'leg{i}{j}',f'toe{k}',(-2+k*2,5,-3.8),(0,0,0),[(-.7,0,-.7,2,2,2,'cream')])
    for j in range(3):
        part(f'ruff{i}{j}','b',f'ruff{i}{j}',(s*9,-3+j*3,-5),(0,0,-s*.3),[(-1,-1,-2,3,4,5,'tabby')])
part('t','b','tail',(0,-1,11),(-.6,0,0),[(-3,-2,-1,6,5,6,'tabby')])
for i in range(5):
    part('t'+str(i),'t' if i==0 else 't'+str(i-1),'seg'+str(i),(0,0,5 if i==0 else 4),(-.21,0,0),[(-2.5+i*.25,-2+i*.15,0,5-i//2,4-i//2,5,'tail')])
(java/'GiantCatClient.java').write_text('''package it.noctis.magic;
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
public class GiantCatClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"giant_cat"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,GiantCatClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.GIANT_CAT.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<GiantCat>{
        final ModelPart r,b,h,t,belly;Model(ModelPart r){this.r=r;b=r.getChild("body");h=r.getChild("head");t=b.getChild("tail");belly=b.getChild("belly");}
        @Override public void setupAnim(GiantCat e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.attackPose(),breathe=(float)Math.sin(age*.09f)*.035f;
            b.xScale=1+breathe;b.zScale=1+breathe;belly.yScale=1+breathe*2+(e.attackAnimation()==1?a*.16f:0);
            h.yRot=yaw*.01f;h.xRot=pitch*.012f+(e.attackAnimation()==2?-a*.25f:0);h.zRot=(float)Math.sin(age*.06f)*.045f;
            b.xRot=e.attackAnimation()==1?-a*.2f:0;
            for(int i=0;i<2;i++){
                h.getChild("ear"+i).zRot=(i==0?-1:1)*(.23f+(float)Math.sin(age*.15f+i)*.08f);
                for(int j=0;j<2;j++){ModelPart leg=r.getChild("leg"+i+j);leg.xRot=(float)Math.cos(limb*.5f+(i+j)*Math.PI)*amount*.45f;
                    if(j==0&&e.attackAnimation()==0&&i==1)leg.xRot-=a*1.35f;
                    if(e.attackAnimation()==1&&j==0)leg.xRot-=a*.25f;}
            }
            t.yRot=(float)Math.sin(age*.11f)*.25f;ModelPart cur=t;
            for(int i=0;i<5;i++){cur=cur.getChild("seg"+i);cur.yRot=(float)Math.sin(age*.14f-i*.6f)*.18f;cur.xRot=-.21f+(float)Math.sin(age*.10f+i*.5f)*.1f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<GiantCat,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),1.8f);}@Override protected void scale(GiantCat e,PoseStack p,float partial){p.scale(2.8f,2.8f,2.8f);}@Override public ResourceLocation getTextureLocation(GiantCat e){return new ResourceLocation(Noctis.ID,"textures/entity/giant_cat.png");}}
}''',encoding='utf-8')
# Hand-authored procedural tabby fur with cream belly, individual strands, stripe curves,
# golden eyes, dark pupils, reflections, pink nose and muzzle freckles.
pix=bytearray(W*W*4)
palette={'tabby':(193,132,70),'face':(210,150,86),'cream':(245,222,183),'muzzle':(247,224,191),'nose':(181,98,100),'mouth':(91,49,45),'inner':(219,145,132),'whisk':(233,221,199),'tail':(193,132,70)}
for x,y,w,h,m,f in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);base=palette[m]
            fine=math.sin(u*145+math.sin(v*34)*1.8)*.035+math.sin(u*281+v*19)*.023
            g=.76+.20*math.sin(u*math.pi)+.07*math.sin(v*math.pi)+fine
            if m in ('tabby','face','tail'):
                wave=math.sin((v if m=='tail' else u)*math.pi*(5 if m=='tail' else 6)+math.sin(v*7)*1.1)
                if wave>.72:g*=.55+.13*math.sin(v*math.pi)
            c=tuple(int(a*g) for a in base)
            if m=='face' and f=='front':
                for ex in (.24,.76):
                    dx=(u-ex)/.19;dy=(v-.42)/.20;d=dx*dx+dy*dy
                    if d<1:c=(80,55,37)
                    if d<.86:c=(235,177,56)
                    if d<.77:c=(int(239-42*abs(dy)),int(181-47*abs(dx)),48)
                    if abs(dx)<.21 and abs(dy)<.86:c=(25,22,20)
                    if (dx+.27)**2+(dy+.31)**2<.07:c=(255,252,231)
                    if (dx-.28)**2+(dy-.24)**2<.018:c=(255,244,200)
            if m=='muzzle' and f=='front':
                for a,b in ((.18,.38),(.31,.55),(.26,.72),(.82,.38),(.69,.55),(.74,.72)):
                    if ((u-a)/.032)**2+((v-b)/.052)**2<1:c=(114,79,64)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'textures/entity/giant_cat.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))))+ch(b'IEND',b''))
dump(assets/'models/item/giant_cat_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.giant_cat']='Miaugusto';d['item.noctismagic.giant_cat_spawn_egg']='Uovo generatore: Miaugusto' if lang=='it_it' else 'Miaugusto Spawn Egg';dump(p,d)
p=res/'data/forge/tags/entity_types/bosses.json';d=json.loads(p.read_text()) if p.exists() else {'replace':False,'values':[]};d['values'].append('noctismagic:giant_cat');dump(p,d)
print('Giant cat boss, five-cat ritual, 2048 atlas and three attack animations installed')
