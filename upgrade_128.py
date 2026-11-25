"""1.2.8: Dante summon, optional duel, Rebellion and Ebony/Ivory rewards."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic';res=root/'src/main/resources'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
    p.parent.mkdir(parents=True,exist_ok=True)
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Dante>> DANTE=ENTITIES.register("dante",()->EntityType.Builder.<Dante>of(Dante::new,MobCategory.MISC).sized(.75f,1.95f).clientTrackingRange(12).build(ID+":dante"));
    public static final RegistryObject<Item> REBELLION=ITEMS.register("rebellion",()->new net.minecraft.world.item.SwordItem(net.minecraft.world.item.Tiers.NETHERITE,16,-2.3f,new Item.Properties().durability(4096).rarity(net.minecraft.world.item.Rarity.EPIC)));
    public static final RegistryObject<Item> EBONY=ITEMS.register("ebony",()->new DanteRelic(false));
    public static final RegistryObject<Item> IVORY=ITEMS.register("ivory",()->new DanteRelic(true));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(DANTE.get(),Dante.attributes().build());'+a)
a='RAIDEN("Evoca Raiden",7,85);';edit('Noctis.java',a,'RAIDEN("Evoca Raiden",7,85),DANTE("Evoca Dante",8,95);')
a='case RAIDEN ->';edit('Noctis.java',a,'case DANTE -> {if(!Dante.summon(p)){tell(p,"Dante e gia presente, oppure manca spazio.");return;}}\n            '+a)
a='if(e.getTabKey()==CreativeModeTabs.COMBAT){';edit('Noctis.java',a,a+'e.accept(REBELLION.get());e.accept(EBONY.get());e.accept(IVORY.get());')
# Use Minecraft's raycast for fictional demonic energy bolts, no real firearm mechanics.
(java/'DanteRelic.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
public class DanteRelic extends Item{
    final boolean ivory;
    public DanteRelic(boolean ivory){super(new Properties().stacksTo(1).durability(3072).rarity(Rarity.EPIC));this.ivory=ivory;}
    @Override public InteractionResultHolder<ItemStack> use(Level l,Player p,InteractionHand hand){
        ItemStack s=p.getItemInHand(hand);if(l instanceof ServerLevel sl){
            Vec3 a=p.getEyePosition(),v=p.getLookAngle().scale(32),b=a.add(v);
            HitResult wall=p.pick(32,0,false);if(wall.getType()!=HitResult.Type.MISS)b=wall.getLocation();
            EntityHitResult hit=ProjectileUtil.getEntityHitResult(p,a,b,p.getBoundingBox().expandTowards(b.subtract(a)).inflate(1),e->e instanceof LivingEntity&&e.isAlive()&&!e.isSpectator()&&e.isPickable(),a.distanceToSqr(b));
            if(hit!=null&&hit.getEntity() instanceof LivingEntity target){b=hit.getLocation();target.hurt(p.damageSources().magic(),ivory?9:12);}
            for(int i=0;i<18;i++){Vec3 q=a.lerp(b,i/17.0);sl.sendParticles(ivory?ParticleTypes.END_ROD:ParticleTypes.ELECTRIC_SPARK,q.x,q.y,q.z,1,.02,.02,.02,0);}
            p.playSound(SoundEvents.FIREWORK_ROCKET_BLAST,.8f,ivory?1.7f:1.3f);
            p.getCooldowns().addCooldown(this,ivory?8:12);if(!p.getAbilities().instabuild)s.hurtAndBreak(1,p,x->x.broadcastBreakEvent(hand));
        }return InteractionResultHolder.sidedSuccess(s,l.isClientSide);
    }
}''',encoding='utf-8')
(java/'Dante.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Dante extends TamableAnimal{
    final ServerBossEvent bar=new ServerBossEvent(Component.literal("Dante - Devil Hunter"),BossEvent.BossBarColor.RED,BossEvent.BossBarOverlay.NOTCHED_20);
    long expires,duelEnd;boolean duel;int attack,pose,mode,cd=40;
    public Dante(EntityType<? extends TamableAnimal> t,Level l){super(t,l);setPersistenceRequired();bar.setVisible(false);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,180).add(Attributes.ARMOR,14).add(Attributes.ATTACK_DAMAGE,28).add(Attributes.MOVEMENT_SPEED,.37).add(Attributes.FOLLOW_RANGE,32).add(Attributes.KNOCKBACK_RESISTANCE,.75);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.3,true));goalSelector.addGoal(2,new FollowOwnerGoal(this,1.1,6,2,false){@Override public boolean canUse(){return !duel&&super.canUse();}@Override public boolean canContinueToUse(){return !duel&&super.canContinueToUse();}});goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob a){return null;}
    @Override public boolean canMate(Animal a){return false;}
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);bar.addPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
    @Override public void remove(RemovalReason r){bar.removeAllPlayers();super.remove(r);}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal("Dante: "+s));}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty()||!isOwnedBy(p))return InteractionResult.PASS;
        if(level() instanceof ServerLevel l&&!duel){
            if(!p.isShiftKeyDown()){p.displayClientMessage(Component.literal("Dante: Vuoi un duello? Shift + clic destro a mano vuota per accettare."),false);return InteractionResult.CONSUME;}
            if(!(p instanceof ServerPlayer sp)||p.isCreative()||p.isSpectator()||Noctis.data(sp).getBoolean("DanteDuelWon")){p.displayClientMessage(Component.literal("Duello disponibile in Sopravvivenza, premio una volta per giocatore."),true);return InteractionResult.CONSUME;}
            duel=true;duelEnd=l.getGameTime()+6000;expires=duelEnd;getAttribute(Attributes.MAX_HEALTH).setBaseValue(480);setHealth(getMaxHealth());getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(32);bar.setVisible(true);setTarget(p);say(l,"Jackpot! Fammi vedere il tuo stile.");
        }return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public boolean isAlliedTo(Entity e){if(duel&&e instanceof Player p&&isOwnedBy(p))return false;return super.isAlliedTo(e);}
    @Override public boolean doHurtTarget(Entity e){
        if(!(e instanceof LivingEntity t)||!(duel?isOwnedBy(t):Eclipse.hostile(t)))return false;
        boolean ok=super.doHurtTarget(e);if(ok&&level() instanceof ServerLevel l){l.broadcastEntityEvent(this,(byte)100);l.sendParticles(ParticleTypes.SWEEP_ATTACK,e.getX(),e.getY()+.8,e.getZ(),3,.25,.25,.25,0);}return ok;
    }
    @Override public boolean hurt(DamageSource s,float amount){
        if(duel){if(!(s.getEntity() instanceof Player p)||!isOwnedBy(p))return false;}
        else if(s.getEntity() instanceof Player)return false;
        return super.hurt(s,amount);
    }
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(cd>0)cd--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        if(l.getGameTime()>=expires){if(duel)say(l,"Il tempo e scaduto. Ci riproveremo.");discard();return;}
        LivingEntity owner=getOwner();
        if(duel){
            bar.setProgress(Math.max(0,getHealth()/getMaxHealth()));
            if(!(owner instanceof Player p)||!p.isAlive()||p.isCreative()||p.isSpectator()||distanceTo(p)>48){say(l,"Duello interrotto.");discard();return;}
            setTarget(p);
        }else if(tickCount%15==0&&owner!=null){
            setTarget(l.getEntitiesOfClass(LivingEntity.class,owner.getBoundingBox().inflate(24),e->e!=this&&e.isAlive()&&Eclipse.hostile(e)).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null));
        }
        LivingEntity t=getTarget();if(t==null||!t.isAlive()||!hasLineOfSight(t))return;
        if(cd==0&&distanceTo(t)<18){
            cd=duel&&getHealth()<getMaxHealth()*.5?32:55;
            if(distanceTo(t)<4){t.hurt(damageSources().mobAttack(this),duel?24:18);t.knockback(1,getX()-t.getX(),getZ()-t.getZ());l.broadcastEntityEvent(this,(byte)100);l.sendParticles(ParticleTypes.SWEEP_ATTACK,t.getX(),t.getY()+1,t.getZ(),4,.4,.4,.4,0);}
            else{l.broadcastEntityEvent(this,(byte)101);Vec3 a=getEyePosition(),b=t.getEyePosition();for(int i=0;i<20;i++){Vec3 q=a.lerp(b,i/19.0);l.sendParticles(ParticleTypes.ELECTRIC_SPARK,q.x,q.y,q.z,2,.05,.05,.05,.01);}t.hurt(damageSources().magic(),duel?14:10);playSound(SoundEvents.FIREWORK_ROCKET_BLAST,1,1.4f);}
        }
    }
    @Override public void die(DamageSource s){
        if(duel&&level() instanceof ServerLevel l&&s.getEntity() instanceof ServerPlayer p&&isOwnedBy(p)&&!Noctis.data(p).getBoolean("DanteDuelWon")){
            Noctis.data(p).putBoolean("DanteDuelWon",true);
            for(Item item:new Item[]{Noctis.REBELLION.get(),Noctis.EBONY.get(),Noctis.IVORY.get()}){ItemStack out=new ItemStack(item);if(!p.getInventory().add(out))p.drop(out,false);}
            say(l,"Niente male! Rebellion, Ebony e Ivory sono tue.");
        }super.die(s);
    }
    @Override public void handleEntityEvent(byte id){if(id==100||id==101){pose=18;mode=id-100;return;}super.handleEntityEvent(id);}
    public float action(){return pose<=0?0:(float)Math.sin(pose*Math.PI/18);}
    public int mode(){return mode;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putLong("Expires",expires);t.putLong("DuelEnd",duelEnd);t.putBoolean("Duel",duel);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);expires=t.getLong("Expires");duelEnd=t.getLong("DuelEnd");duel=t.getBoolean("Duel");bar.setVisible(duel);}
    static boolean summon(ServerPlayer p){
        ServerLevel l=p.serverLevel();CompoundTag d=Noctis.data(p);long now=l.getGameTime();
        if(d.getLong("danteUntil")>now||!l.getEntitiesOfClass(Dante.class,p.getBoundingBox().inflate(96),x->x.isOwnedBy(p)).isEmpty())return false;
        for(int i=0;i<20;i++){
            BlockPos q=p.blockPosition().offset(p.getRandom().nextInt(9)-4,0,p.getRandom().nextInt(9)-4);
            if(q.distSqr(p.blockPosition())<4||!l.hasChunkAt(q)||!l.isEmptyBlock(q)||!l.isEmptyBlock(q.above())||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))continue;
            Dante r=Noctis.DANTE.get().create(l);if(r==null)return false;r.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);r.tame(p);r.expires=now+2400;
            if(!l.noCollision(r)||!l.addFreshEntity(r))continue;d.putLong("danteUntil",now+2400);r.say(l,"Let's rock!");l.sendParticles(ParticleTypes.FLAME,r.getX(),r.getY()+1,r.getZ(),45,.5,.7,.5,.08);return true;
        }return false;
    }
}''',encoding='utf-8')
# Dedicated custom Dante mesh, white bangs, scarlet long coat, sword and two fantasy pistols.
N=256;S=4;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,m):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
    for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,m,f))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
part('b','r','body',(0,0,0),(0,0,0),[(-4,0,-2.5,8,9,5,'coat'),(-3,1,-3,6,8,1,'shirt'),(-4,9,-2.5,8,2,5,'belt')])
part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-4,8,2,8,'hair')])
for i in range(7):part('bang'+str(i),'h','bang'+str(i),(-3+i,-7,-3.5),(0,0,(i-3)*.13),[(-.7,0,-.7,1,3+i%3,2,'hair')])
for i,s in enumerate((-1,1)):
    part('side'+str(i),'h','side'+str(i),(s*3.6,-6,0),(0,0,s*.1),[(-1,0,-1,2,5,3,'hair')])
    part('lapel'+str(i),'b','lapel'+str(i),(s*3,-.7,-2.8),(0,0,s*.22),[(-1,0,-.5,2,7,1,'lapel')])
    part('tail'+str(i),'b','tail'+str(i),(s*2.5,9,2),(.12,0,s*.1),[(-2,0,-1,4,12,2,'coat')])
    part('arm'+str(i),'r','arm'+str(i),(s*5.1,0,0),(0,0,-s*.12),[(-2,-1,-2,4,8,4,'coat'),(-1.5,7,-1.5,3,4,3,'glove')])
    part('leg'+str(i),'r','leg'+str(i),(s*2.1,11,0),(0,0,0),[(-2,0,-2,4,8,4,'shirt'),(-2,8,-3,4,5,5,'boot')])
    part('pistol'+str(i),'arm'+str(i),'pistol',(0,9,-2),(0,0,0),[(-.6,-1,-4,1,2,5,'silver' if i else 'dark'),(-.6,1,-.8,1,3,2,'glove')])
part('sword','arm1','sword',(0,10,-1),(-.2,0,0),[(-.6,0,-.6,1,4,1,'glove'),(-3,4,-1,6,2,2,'silver'),(-2,6,-.5,4,15,1,'silver'),(-1,21,-.5,2,3,1,'silver')])
(java/'DanteClient.java').write_text('''package it.noctis.magic;
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
public class DanteClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"dante"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,DanteClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.DANTE.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<Dante>{
        final ModelPart r,h,b;Model(ModelPart r){this.r=r;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(Dante e,float limb,float amount,float age,float yaw,float pitch){
            h.yRot=yaw*.017f;h.xRot=pitch*.012f;float a=e.action();boolean guns=a>0&&e.mode()==1;
            b.yRot=a*.2f;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;ModelPart arm=r.getChild("arm"+i);arm.xRot=-w*.65f-(guns?1.5f*a:i==1?1.8f*a:0);arm.getChild("pistol").visible=guns;r.getChild("leg"+i).xRot=w*.65f;b.getChild("tail"+i).xRot=.12f+amount*.3f+(float)Math.sin(age*.12+i)*.08f;}
            r.getChild("arm1").getChild("sword").visible=!guns;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<Dante,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.45f);}@Override public ResourceLocation getTextureLocation(Dante e){return new ResourceLocation(Noctis.ID,"textures/entity/dante.png");}}
}''',encoding='utf-8')
palette={'coat':(147,26,37),'lapel':(106,22,29),'shirt':(36,35,41),'belt':(81,60,45),'face':(230,193,173),'hair':(224,227,236),'glove':(35,32,36),'boot':(34,30,34),'silver':(183,197,213),'dark':(36,40,49)}
pix=bytearray(W*W*4)
for x,y,w,h,m,f in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);base=palette[m];g=.68+.31*math.sin(u*math.pi)+.04*math.cos(v*8)
            if m=='hair':g=.72+.27*math.sin(u*35+v*5)**2
            if m=='silver':g=.52+.48*math.exp(-((u-.35)/.24)**2)
            c=tuple(int(a*g) for a in base)
            if m in ('coat','lapel') and (u<.06 or u>.94 or abs(v-.92)<.025):c=(83,19,26)
            if m=='face' and f=='front':
                for ex in (.27,.73):
                    dx=(u-ex)/.18;dy=(v-.46)/.12
                    if dx*dx+dy*dy<1:c=(47,39,48)
                    if dx*dx+dy*dy<.77:c=(239,236,229)
                    if abs(dx)<.4 and abs(dy)<.8:c=(83,125,172)
                    if abs(dx)<.16 and abs(dy)<.7:c=(24,29,42)
                if .4<u<.62 and abs(v-.79)<.024:c=(125,65,70)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
png(assets/'textures/entity/dante.png',W,W,pix)
for n in ('rebellion','ebony','ivory'):
    W=32;pix=bytearray(W*W*4)
    for y in range(W):
        for x in range(W):
            c=None
            if n=='rebellion':
                a=x+y-30
                if abs(a)<3 and x>8 and y<23:c=(218,226,239) if a<0 else (105,122,145)
                if 9<x<18 and 17<y<24 and abs(x-y+6)<5:c=(151,161,174)
                if 3<x<12 and 22<y<30 and abs(a)<2:c=(68,47,45)
            else:
                if 7<=x<=27 and 8<=y<=13:c=(195,203,213) if n=='ivory' else (40,44,54)
                if 10<=x<=17 and 13<y<24 and x+y<38:c=(77,61,55) if n=='ivory' else (33,32,36)
                if 18<=x<=22 and 14<=y<=17:c=(120,126,137)
            if c:pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
    png(assets/'textures/item'/f'{n}.png',W,W,pix);dump(assets/'models/item'/f'{n}.json',{'parent':'minecraft:item/handheld','textures':{'layer0':'noctismagic:item/'+n}})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.dante']='Dante';d['item.noctismagic.rebellion']='Rebellion';d['item.noctismagic.ebony']='Ebony';d['item.noctismagic.ivory']='Ivory';dump(p,d)
print('Dante summon, optional duel and three unique rewards installed')
