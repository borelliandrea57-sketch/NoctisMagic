"""Noctis 0.5.0: secret fallen angel boss, original theme, Neapolitan vampire dialogue."""
from pathlib import Path
import json,sys,struct,zlib,random,math,wave,array,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(p,pairs):
    s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s: raise ValueError(f'Missing anchor {p.name}: {a[:100]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
def write(name,s): (java/name).write_text(s,encoding='utf-8')
def j(path,data):
    p=res/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
edit(root/'gradle.properties',[('mod_version=0.4.0','mod_version=0.5.0')])
edit(java/'Noctis.java',[
('public static final RegistryObject<EntityType<Angel>> ANGEL=', '''public static final RegistryObject<EntityType<OneWinged>> FALLEN=ENTITIES.register("one_winged_angel",()->EntityType.Builder.<OneWinged>of(OneWinged::new,MobCategory.MONSTER).sized(.95f,2.9f).clientTrackingRange(14).fireImmune().build(ID+":one_winged_angel"));
    public static final RegistryObject<EntityType<Angel>> ANGEL='''),
('VampireLife.register(bus);','VampireLife.register(bus);FallenEncounter.SOUNDS.register(bus);'),
('e.put(ANGEL.get(),Angel.attributes().build());','e.put(FALLEN.get(),OneWinged.attributes().build());e.put(ANGEL.get(),Angel.attributes().build());')
])
write('FallenEncounter.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.sounds.*;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.*;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class FallenEncounter {
    static final DeferredRegister<SoundEvent> SOUNDS=DeferredRegister.create(ForgeRegistries.SOUND_EVENTS,Noctis.ID);
    static final RegistryObject<SoundEvent> THEME=SOUNDS.register("fallen_angel_theme",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"fallen_angel_theme")));
    static boolean matches(SignText t){
        StringBuilder b=new StringBuilder();
        for(Component line:t.getMessages(false)){String s=line.getString().trim();if(!s.isEmpty()){if(b.length()>0)b.append(" ");b.append(s);}}
        return b.toString().equalsIgnoreCase("One Winged Angel");
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0||p.isSpectator())return;
        ServerLevel l=p.serverLevel();if(l.dimension()!=Level.OVERWORLD||l.getDifficulty()==Difficulty.PEACEFUL||!l.getEntitiesOfClass(OneWinged.class,p.getBoundingBox().inflate(120)).isEmpty())return;
        BlockPos center=p.blockPosition();
        for(BlockPos q:BlockPos.betweenClosed(center.offset(-5,-3,-5),center.offset(5,3,5))){
            if(!l.hasChunkAt(q)||!(l.getBlockEntity(q) instanceof SignBlockEntity sign)||sign.getPersistentData().getBoolean("NoctisFallenSummoned"))continue;
            if(!matches(sign.getFrontText())&&!matches(sign.getBackText()))continue;
            BlockPos surface=l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,q);
            int y=Math.max(surface.getY()+15,p.getBlockY()+15);
            if(y>l.getMaxBuildHeight()-5)continue;
            OneWinged boss=Noctis.FALLEN.get().create(l);if(boss==null)return;
            boss.moveTo(q.getX()+.5,y,q.getZ()+.5,p.getYRot()+180,0);
            boss.setPersistenceRequired();boss.setTarget(p);
            if(!l.noCollision(boss)||!l.addFreshEntity(boss))continue;
            sign.getPersistentData().putBoolean("NoctisFallenSummoned",true);sign.setChanged();
            l.sendParticles(ParticleTypes.END_ROD,boss.getX(),boss.getY(),boss.getZ(),100,2,3,2,.1);
            for(ServerPlayer near:l.players())if(near.distanceTo(p)<90)near.sendSystemMessage(Component.literal("L'aria si e' fatta immobile. Dal cielo discende l'Angelo dall'Unica Ala."));
            return;
        }
    }
}''')
write('OneWinged.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.LargeFireball;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.effect.*;
import net.minecraft.nbt.CompoundTag;
public class OneWinged extends Monster {
    final ServerBossEvent bar=new ServerBossEvent(Component.literal("One Winged Angel"),BossEvent.BossBarColor.PURPLE,BossEvent.BossBarOverlay.NOTCHED_20);
    private int cooldown=65,phase=0,attack=0;
    public OneWinged(EntityType<? extends Monster> type,Level level){super(type,level);setNoGravity(true);bar.setDarkenScreen(true);}
    public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,600).add(Attributes.ATTACK_DAMAGE,24).add(Attributes.ARMOR,12).add(Attributes.FOLLOW_RANGE,80).add(Attributes.MOVEMENT_SPEED,.35).add(Attributes.KNOCKBACK_RESISTANCE,.9);}
    @Override protected void registerGoals(){}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public boolean causeFallDamage(float d,float m,net.minecraft.world.damagesource.DamageSource s){return false;}
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);bar.addPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
    @Override public void remove(RemovalReason reason){bar.removeAllPlayers();super.remove(reason);}
    @Override public void tick(){
        super.tick();if(!(level() instanceof ServerLevel l)||!isAlive())return;
        bar.setProgress(getHealth()/getMaxHealth());setNoGravity(true);
        LivingEntity t=getTarget();if(t==null||!t.isAlive()||distanceTo(t)>100||(t instanceof Player p&&(p.isCreative()||p.isSpectator()))){t=l.getNearestPlayer(this,75);if(t instanceof Player p&&(p.isCreative()||p.isSpectator()))t=null;setTarget(t);}
        if(t==null){setDeltaMovement(getDeltaMovement().scale(.85));return;}
        int next=getHealth()<getMaxHealth()*.33?2:getHealth()<getMaxHealth()*.67?1:0;
        if(next>phase){phase=next;l.sendParticles(ParticleTypes.PORTAL,getX(),getY()+1,getZ(),100,1.5,2,1.5,.2);playSound(SoundEvents.WITHER_SPAWN,.65f,.8f);for(ServerPlayer p:l.players())if(distanceTo(p)<70)p.sendSystemMessage(Component.literal(phase==1?"Angelo: La mia ala oscurera' il sole.":"Angelo: Contempla il giudizio finale."));}
        Vec3 to=t.position().subtract(position());double dist=to.length();
        double angle=tickCount*.035;Vec3 goal=t.position().add(Math.cos(angle)*(phase==2?4:7),phase==2?3:6,Math.sin(angle)*(phase==2?4:7));
        if(attack%3==0&&cooldown<16)goal=t.position().add(0,.7,0);
        Vec3 diff=goal.subtract(position());Vec3 velocity=diff.length()>1?diff.normalize().scale(phase==2?.52:.37):Vec3.ZERO;
        setDeltaMovement(getDeltaMovement().scale(.65).add(velocity.scale(.35)));
        getLookControl().setLookAt(t,45,45);float yaw=(float)(Math.atan2(to.z,to.x)*180/Math.PI)-90;setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);
        if(tickCount%4==0)l.sendParticles(ParticleTypes.SMOKE,getX(),getY()+2,getZ(),4,.8,.4,.8,.015);
        if(--cooldown>0)return;
        if(dist>36){cooldown=12;return;}
        cooldown=phase==2?35:phase==1?50:65;int mode=attack++%3;
        if(mode==0){
            if(dist<5&&hasLineOfSight(t)){t.hurt(damageSources().mobAttack(this),24+phase*4);t.knockback(1.2,to.x,to.z);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,1.3f,.65f);}
            else{cooldown=12;attack--;setDeltaMovement(to.normalize().scale(.85));}
        }else if(mode==1&&hasLineOfSight(t)){
            Vec3 start=position().add(0,2,0),end=t.getEyePosition();
            for(int i=0;i<=28;i++){Vec3 q=start.lerp(end,i/28.0);l.sendParticles(ParticleTypes.END_ROD,q.x,q.y,q.z,2,.12,.12,.12,0);}
            t.hurt(damageSources().magic(),15+phase*4);t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,65,1));playSound(SoundEvents.BLAZE_SHOOT,1,.55f);
        }else{
            for(int i=0;i<3+phase;i++){Vec3 aim=t.getEyePosition().subtract(position().add(0,2,0)).add((random.nextDouble()-.5)*2,0,(random.nextDouble()-.5)*2).normalize();LargeFireball f=new LargeFireball(l,this,aim.x,aim.y,aim.z,1);f.setPos(getX()+aim.x,getY()+2,getZ()+aim.z);l.addFreshEntity(f);}
            l.sendParticles(ParticleTypes.DRAGON_BREATH,getX(),getY()+1.5,getZ(),45,1,1,1,.12);playSound(SoundEvents.ENDER_DRAGON_SHOOT,1,.7f);
        }
    }
    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource s,int looting,boolean hit){super.dropCustomDeathLoot(s,looting,hit);for(int i=0;i<8;i++)spawnAtLocation(Noctis.CRYSTAL.get());spawnAtLocation(net.minecraft.world.item.Items.NETHER_STAR);}
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);n.putInt("Phase",phase);n.putInt("Attack",attack);}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);phase=n.getInt("Phase");attack=n.getInt("Attack");}
}''')
# Bow is synchronized with entity events, animated independently of the server AI.
edit(java/'Vampire.java',[
('private boolean gifted=false;','''private boolean gifted=false;
        private int bowTicks=0;
        public float bow(float partial){return bowTicks>0?(float)Math.sin(Math.PI*Math.max(0,bowTicks-partial)/32.0)*.62f:0;}
        @Override public void handleEntityEvent(byte id){if(id==61){bowTicks=32;return;}super.handleEntityEvent(id);}
        private void bowTo(Player p){bowTicks=32;getNavigation().stop();getLookControl().setLookAt(p,30,30);level().broadcastEntityEvent(this,(byte)61);}'''),
('public void tick(){super.tick();if(!(level() instanceof net.minecraft.server.level.ServerLevel l))return;','public void tick(){super.tick();if(bowTicks>0)bowTicks--;if(!(level() instanceof net.minecraft.server.level.ServerLevel l))return;if(bowTicks>0){getNavigation().stop();return;}'),
('playSound(net.minecraft.sounds.SoundEvents.VILLAGER_YES,.7f,.85f);','bowTo(p);playSound(net.minecraft.sounds.SoundEvents.VILLAGER_YES,.7f,.85f);'),
('if(points>=10){if(!VampireLife.isVampire(p))offer(p);else p.sendSystemMessage(Component.literal("Vampiro: Il nostro legame e' eterno."));return true;}','if(points>=10){if(!p.getAbilities().instabuild){s.shrink(1);ItemStack bucket=new ItemStack(Items.BUCKET);if(!p.getInventory().add(bucket))p.drop(bucket,false);}bowTo(p);p.serverLevel().sendParticles(net.minecraft.core.particles.ParticleTypes.HEART,getX(),getY()+1.8,getZ(),8,.3,.4,.3,.03);playSound(net.minecraft.sounds.SoundEvents.VILLAGER_YES,.7f,.85f);p.sendSystemMessage(Component.literal("Vampiro: Grazie assaje, cumpa mio!"));if(!VampireLife.isVampire(p))offer(p);return true;}')
])
p=java/'Vampire.java';s=p.read_text(encoding='utf-8')
translations={
"Ti considero ormai uno di noi. Vuoi diventare un vampiro? Shift + tasto destro a mano vuota per accettare; tasto destro normale per rifiutare.":"Mo si' uno 'e nuje. Vuò addeventà vampiro pure tu? [Shift + tasto destro a mano vuota: accetta; tasto destro: rifiuta.]",
"Un dono prezioso, grazie. Amicizia ":"Maronna mia, grazie assaje! Te voglio bene. Amicizia ",
"Come desideri. La nostra amicizia non cambia. Potrai ripensarci.":"Fa' comme vuò, nun te preoccupà. Simmo amice 'o stesso. Ce può penzà n'ata vota.",
"Vi ringrazio dell'invito. Permesso!":"Grazie assaje pe' ll'invito. Cu permesso!",
"Buonasera... posso entrare? Aprite la porta, se lo desiderate.":"Bonasera... pozzo trasì? Si vuò, arape 'a porta.",
"Buonasera, viandante. Un piccolo regalo.":"Bonasera, viandante! Te voglio fa' nu rialo.",
"Un cristallo per la tua magia.":"Tieni, nu cristallo p' 'a magia toja.",
"La notte ci appartiene. Ti scambio un cristallo per uno smeraldo.":"'A notte è 'a nosta. Damme nu smeraldo e te dongo nu cristallo.",
"Il nostro legame e' eterno.":"Simmo amice pe' sempe."
}
for a,b in translations.items():s=s.replace(a,b)
p.write_text(s,encoding='utf-8')
edit(java/'Client.java',[
('new ZombieModel<>(c.bakeLayer(f?FRIENDLY:VAMPIRE))','new BowZombieModel(c.bakeLayer(f?FRIENDLY:VAMPIRE))'),
('static class VampRenderer extends','''static class BowZombieModel extends ZombieModel<Zombie>{
        BowZombieModel(ModelPart p){super(p);}
        @Override public void setupAnim(Zombie e,float swing,float amount,float age,float yaw,float pitch){
            super.setupAnim(e,swing,amount,age,yaw,pitch);
            if(e instanceof Vampire.Friendly f){
                float b=f.bow(age-e.tickCount);body.xRot+=b;head.xRot+=b;hat.xRot=head.xRot;
                rightArm.xRot=b*.7f;leftArm.xRot=b*.7f;rightArm.zRot=-.12f;leftArm.zRot=.12f;
            }
        }
    }
    static class VampRenderer extends''')
])
write('FallenClient.java','''package it.noctis.magic;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class FallenClient {
    static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"one_winged_angel"),"main");
    static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/one_winged_angel.png");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(LAYER,FallenClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.FALLEN.get(),Renderer::new);}
    static LayerDefinition mesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot(),h=r.getChild("head"),b=r.getChild("body");
        h.addOrReplaceChild("silver",CubeListBuilder.create().texOffs(64,0).addBox(-4.6f,-9,-4.5f,9.2f,3,9).texOffs(64,14).addBox(-4,-6,3,8,22,2),PartPose.ZERO);
        for(int s:new int[]{-1,1}){
            h.addOrReplaceChild("lock"+s,CubeListBuilder.create().texOffs(92,0).addBox(-1,-1,-1,2,17,3),PartPose.offsetAndRotation(s*4,-5,-1,0,0,s*.08f));
            b.addOrReplaceChild("coat"+s,CubeListBuilder.create().texOffs(0,64).addBox(-3,0,-2,6,13,4),PartPose.offsetAndRotation(s*2.5f,10,0,.1f,0,s*.08f));
        }
        PartDefinition wing=b.addOrReplaceChild("wing",CubeListBuilder.create().texOffs(0,84).addBox(0,-5,-1,17,7,3),PartPose.offsetAndRotation(3,2,2,-.15f,-.28f,-.55f));
        PartDefinition outer=wing.addOrReplaceChild("outer",CubeListBuilder.create().texOffs(48,84).addBox(0,-3,-1,16,5,2),PartPose.offsetAndRotation(15,-2,0,0,0,-.35f));
        for(int i=0;i<8;i++)wing.addOrReplaceChild("feather"+i,CubeListBuilder.create().texOffs(96,66).addBox(-1,0,-.6f,2.7f,11+i*.9f,1.2f),PartPose.offsetAndRotation(2+i*2,0,0,0,0,-.22f-i*.065f));
        for(int i=0;i<7;i++)outer.addOrReplaceChild("tip"+i,CubeListBuilder.create().texOffs(96,66).addBox(-1,0,-.5f,2.6f,18-i,1),PartPose.offsetAndRotation(1+i*2,0,0,0,0,-.5f-i*.06f));
        r.getChild("right_arm").addOrReplaceChild("sword",CubeListBuilder.create().texOffs(80,42).addBox(-3,0,-1,6,1,2).texOffs(80,48).addBox(-.9f,1,-.4f,1.8f,28,.8f),PartPose.offsetAndRotation(-1,9,0,0,0,-.12f));
        return LayerDefinition.create(m,128,128);
    }
    static class Model extends HumanoidModel<OneWinged>{
        final ModelPart wing,outer;
        Model(ModelPart root){super(root);wing=root.getChild("body").getChild("wing");outer=wing.getChild("outer");}
        @Override public void setupAnim(OneWinged e,float swing,float amount,float age,float yaw,float pitch){
            super.setupAnim(e,swing,amount,age,yaw,pitch);
            wing.yRot=-.35f+(float)Math.sin(age*.12)*.38f;wing.zRot=-.55f+(float)Math.sin(age*.12)*.16f;outer.zRot=-.35f+(float)Math.cos(age*.12)*.12f;
            leftLeg.xRot=.12f;rightLeg.xRot=-.12f;rightArm.xRot=-.7f+(float)Math.sin(age*.08)*.25f;leftArm.zRot=.15f;
        }
    }
    static class Renderer extends MobRenderer<OneWinged,Model>{
        Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(LAYER)),.65f);}
        @Override public ResourceLocation getTextureLocation(OneWinged e){return TEX;}
        @Override protected void scale(OneWinged e,com.mojang.blaze3d.vertex.PoseStack pose,float partial){pose.scale(1.45f,1.45f,1.45f);}
    }
    @Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
    public static class Music {
        private static SimpleSoundInstance current;
        @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
            if(e.phase!=TickEvent.Phase.END)return;Minecraft mc=Minecraft.getInstance();
            boolean active=mc.level!=null&&mc.player!=null&&!mc.level.getEntitiesOfClass(OneWinged.class,mc.player.getBoundingBox().inflate(85),OneWinged::isAlive).isEmpty();
            if(!active){if(current!=null){mc.getSoundManager().stop(current);current=null;}return;}
            if(current==null||!mc.getSoundManager().isActive(current)){current=SimpleSoundInstance.forMusic(FallenEncounter.THEME.get());mc.getSoundManager().play(current);}
        }
    }
}''')
# Texture atlas: original silver hair / charcoal coat / green eyes / black feather gradients.
rng=random.Random(504);pix=[[(27,24,32,255) for x in range(128)] for y in range(128)]
def rect(x,y,w,h,col,noise=0):
    for yy in range(max(y,0),min(y+h,128)):
        for xx in range(max(x,0),min(x+w,128)):
            d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col)+(255,)
rect(0,0,32,16,(203,190,180),8);rect(8,8,8,8,(224,209,193),6)
rect(9,10,2,1,(40,125,101));rect(13,10,2,1,(40,125,101));rect(10,13,4,1,(108,73,82))
rect(16,16,24,16,(25,25,34),10);rect(20,20,8,12,(39,38,46),7);rect(20,20,1,9,(154,148,163));rect(27,20,1,9,(154,148,163));rect(23,25,2,1,(170,162,145))
rect(40,16,16,16,(38,36,43),7);rect(44,20,4,2,(163,164,170),4);rect(0,16,16,16,(20,20,28),7);rect(16,48,48,16,(30,28,36),8)
rect(64,0,41,42,(198,198,213),12)
for x in range(65,105,3):rect(x,0,1,41,(235,236,245),5)
rect(0,64,24,20,(23,23,34),8)
for x in range(2,22,5):rect(x,65,1,17,(48,47,61),5)
rect(0,84,88,16,(22,20,31),10);rect(96,66,24,40,(18,16,27),8)
for x in range(97,119,4):rect(x,67,1,35,(51,45,61),7)
rect(80,42,16,6,(154,133,89),9);rect(80,48,8,29,(203,208,224),9);rect(82,49,1,27,(243,245,255),2)
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+bytes(c for p in row for c in p) for row in pix)
(assets/'textures/entity/one_winged_angel.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',128,128,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
# Original, synthesized dark ceremonial soundtrack (no sampled or copied music).
sounddir=assets/'sounds';sounddir.mkdir(exist_ok=True)
rate=22050;beat=.56;bars=16;total=bars*4*beat
samples=array.array('f',[0.0])*int(rate*total)
chords=[(45,52,57,60),(41,48,53,57),(43,50,55,58),(40,47,52,56),(45,52,57,64),(46,53,58,62),(41,48,53,60),(40,47,52,59)]
def note(midi,start,dur,amp,kind):
    f=440*2**((midi-69)/12);first=int(start*rate);n=min(int(dur*rate),len(samples)-first)
    for i in range(max(0,n)):
        t=i/rate;env=min(1,t/(.035 if kind=='bell' else .16))*min(1,max(0,(dur-t)/(.22 if kind=='bell' else .35)))
        a=2*math.pi*f*t
        if kind=='choir':v=(math.sin(a)+.32*math.sin(a*2)+.14*math.sin(a*3)+.07*math.sin(a*4))*(.85+.15*math.sin(2*math.pi*4.1*t))
        elif kind=='bell':v=(math.sin(a)+.4*math.sin(a*2.01)+.15*math.sin(a*3.01))*math.exp(-t*2.6)
        else:v=math.sin(a)+.3*math.sin(a*1.5)
        samples[first+i]+=amp*env*v
for bar in range(bars):
    start=bar*4*beat;ch=chords[bar%len(chords)]
    for idx,m in enumerate(ch):note(m,start,4*beat,.035 if idx else .075,'choir')
    for k in [0,2]:note(ch[0]-12,start+k*beat,beat*.9,.06,'bass')
    motif=[ch[2]+12,ch[1]+12,ch[3]+12,ch[2]+12] if bar%2==0 else [ch[3]+12,ch[2]+12,ch[1]+12,ch[0]+12]
    for k,m in enumerate(motif):note(m,start+k*beat,beat*.95,.035,'bell')
    for k in ([0,2] if bar<8 else [0,1,2,3]):note(33,start+k*beat,.23,.08,'bass')
wav=sounddir/'fallen_angel_theme.wav'
with wave.open(str(wav),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
    pcm=array.array('h',(int(max(-.98,min(.98,s))*32767) for s in samples));w.writeframes(pcm.tobytes())
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(sounddir/'fallen_angel_theme.ogg')],check=True)
wav.unlink()
j('assets/noctismagic/sounds.json',{"fallen_angel_theme":{"sounds":[{"name":"noctismagic:fallen_angel_theme","stream":True}]}})
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.one_winged_angel']='Angelo dall’Unica Ala' if lang=='it_it' else 'One Winged Angel';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.5.0 source patch applied')
