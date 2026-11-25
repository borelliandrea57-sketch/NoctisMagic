"""1.4.1: Bayonetta summon, Lucy night guest, neutral berserk Faputa."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
ids=['bayonetta','lucy','faputa'];names=['Bayonetta','Lucy','Faputa']
decl=''
for i,n in enumerate(ids):
    r=n.upper();w=[.8,.65,.85][i];h=[2.3,1.95,1.7][i]
    decl+=f'public static final RegistryObject<EntityType<MoonGuest>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<MoonGuest>of(MoonGuest::new,MobCategory.CREATURE).sized({w}f,{h}f).clientTrackingRange(12).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{["0x20212e","0xd3c9e5","0xefe5d7"][i]},{["0xb12746","0x7ecfd4","0xa32635"][i]},new Item.Properties()));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG=';edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,''.join(f'e.put({n.upper()}.get(),MoonGuest.attributes({i}).build());' for i,n in enumerate(ids))+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({n.upper()}_EGG.get());' for n in ids))
edit('Noctis.java','DANTE("Evoca Dante",8,95);','DANTE("Evoca Dante",8,95),BAYONETTA("Evoca Bayonetta",9,120);')
edit('Noctis.java','case DANTE ->','case BAYONETTA -> {if(!MoonGuest.summon(p)){tell(p,"Bayonetta e gia presente, oppure manca spazio.");return;}}\n            case DANTE ->')
(java/'MoonGuest.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class MoonGuest extends PathfinderMob{
    static final EntityDataAccessor<Boolean> RAGE=SynchedEntityData.defineId(MoonGuest.class,EntityDataSerializers.BOOLEAN);
    UUID owner,aggressor;long expires;int rage,cd=20,witch=0,pose,animation,speech;
    public MoonGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public int kind(){return getType()==Noctis.BAYONETTA.get()?0:getType()==Noctis.LUCY.get()?1:2;}
    public static AttributeSupplier.Builder attributes(int k){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,k==0?320:k==1?65:240).add(Attributes.ARMOR,k==0?18:k==1?5:12).add(Attributes.ATTACK_DAMAGE,k==0?44:k==1?4:48).add(Attributes.MOVEMENT_SPEED,k==0?.38:k==1?.25:.36).add(Attributes.FOLLOW_RANGE,40).add(Attributes.KNOCKBACK_RESISTANCE,k==1?.15:.7);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(RAGE,false);}
    public boolean berserk(){return entityData.get(RAGE);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));
        goalSelector.addGoal(1,new MeleeAttackGoal(this,1.25,true){@Override public boolean canUse(){return kind()!=1&&getTarget()!=null&&super.canUse();}@Override public boolean canContinueToUse(){return kind()!=1&&getTarget()!=null&&super.canContinueToUse();}});
        goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.7){@Override public boolean canUse(){return owner==null&&getTarget()==null&&super.canUse();}@Override public boolean canContinueToUse(){return owner==null&&getTarget()==null&&super.canContinueToUse();}});
        goalSelector.addGoal(4,new LookAtPlayerGoal(this,Player.class,8));
    }
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s).withStyle(kind()==0?ChatFormatting.LIGHT_PURPLE:kind()==1?ChatFormatting.AQUA:ChatFormatting.GOLD));}
    @Override public boolean hurt(DamageSource s,float amount){
        if(kind()==0&&s.getEntity() instanceof Player)return false;
        boolean hit=super.hurt(s,amount);
        if(hit&&isAlive()&&kind()==2&&level() instanceof ServerLevel l&&s.getEntity() instanceof LivingEntity t&&t!=this&&!(t instanceof Player p&&(p.isCreative()||p.isSpectator()))){
            if(!berserk())say(l,"Faputa entra in berserk, sosu!");
            aggressor=t.getUUID();rage=600;entityData.set(RAGE,true);setTarget(t);
            addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,600,1));addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,600,1));
            l.broadcastEntityEvent(this,(byte)118);
        }return hit;
    }
    boolean enemy(LivingEntity t){return t!=null&&t.isAlive()&&(kind()==0?Eclipse.hostile(t):kind()==2&&berserk()&&t.getUUID().equals(aggressor));}
    @Override public boolean doHurtTarget(Entity t){
        if(!(t instanceof LivingEntity v)||!enemy(v))return false;
        boolean b=super.doHurtTarget(t);if(b&&level() instanceof ServerLevel l){l.broadcastEntityEvent(this,(byte)119);if(kind()==2)v.knockback(.8,getX()-v.getX(),getZ()-v.getZ());}return b;
    }
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(cd>0)cd--;if(witch>0)witch--;if(speech>0)speech--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        int k=kind();
        if(k==0){
            if(owner!=null&&l.getGameTime()>=expires){discard();return;}
            LivingEntity p=owner==null?null:l.getPlayerByUUID(owner);
            if(owner!=null&&(p==null||!p.isAlive())){discard();return;}
            if(tickCount%10==0){var area=p==null?getBoundingBox():p.getBoundingBox();setTarget(l.getEntitiesOfClass(LivingEntity.class,area.inflate(24),e->e!=this&&enemy(e)).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null));}
            if(getTarget()==null&&p!=null&&distanceTo(p)>5&&tickCount%10==0)getNavigation().moveTo(p,1.2);
            LivingEntity t=getTarget();
            if(enemy(t)&&distanceTo(t)<22&&hasLineOfSight(t)&&cd==0){
                cd=24;l.broadcastEntityEvent(this,(byte)119);
                Vec3 a=getEyePosition(),b=t.getEyePosition();
                for(int i=0;i<20;i++){Vec3 q=a.lerp(b,i/19.0);l.sendParticles(ParticleTypes.WITCH,q.x,q.y,q.z,2,.045,.045,.045,.02);}
                t.hurt(damageSources().mobAttack(this),34);playSound(SoundEvents.FIREWORK_ROCKET_BLAST,.8f,1.2f);
                if(witch==0){witch=200;l.broadcastEntityEvent(this,(byte)118);
                    for(LivingEntity e:l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(12),this::enemy)){e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,100,5));e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,100,1));}
                    l.sendParticles(ParticleTypes.PORTAL,getX(),getY()+1,getZ(),80,2,.7,2,.13);say(l,"Witch Time!");
                }
            }
        }else if(k==1){
            if(tickCount%100==0&&!l.isDay())l.sendParticles(ParticleTypes.ELECTRIC_SPARK,getX(),getY()+1.8,getZ(),3,.25,.3,.25,.02);
            Player p=l.getNearestPlayer(this,5);
            if(!l.isDay()&&p!=null&&speech==0){speech=480;say(l,"Mi porterai sulla luna?");l.broadcastEntityEvent(this,(byte)118);}
            if(cd==0){for(LivingEntity t:l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(6),Eclipse::hostile)){if(!hasLineOfSight(t))continue;t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,2));t.addEffect(new MobEffectInstance(MobEffects.BLINDNESS,40));l.sendParticles(ParticleTypes.ELECTRIC_SPARK,t.getX(),t.getY()+1,t.getZ(),12,.25,.4,.25,.04);cd=160;break;}}
        }else if(berserk()){
            LivingEntity t=aggressor!=null&&l.getEntity(aggressor) instanceof LivingEntity v?v:null;
            if(--rage<=0||!enemy(t)||distanceTo(t)>40||(t instanceof Player p&&(p.isCreative()||p.isSpectator()))){rage=0;aggressor=null;entityData.set(RAGE,false);setTarget(null);getNavigation().stop();removeEffect(MobEffects.MOVEMENT_SPEED);removeEffect(MobEffects.DAMAGE_RESISTANCE);return;}
            setTarget(t);if(tickCount%8==0)l.sendParticles(ParticleTypes.ANGRY_VILLAGER,getX(),getY()+1.3,getZ(),2,.25,.2,.25,.01);
            if(cd==0&&distanceTo(t)<8&&hasLineOfSight(t)){cd=28;l.broadcastEntityEvent(this,(byte)119);
                if(distanceTo(t)<4){t.hurt(damageSources().mobAttack(this),62);t.knockback(1.3,getX()-t.getX(),getZ()-t.getZ());l.sendParticles(ParticleTypes.SWEEP_ATTACK,t.getX(),t.getY()+1,t.getZ(),5,.3,.3,.3,0);}
                else if(onGround()){Vec3 v=t.position().subtract(position());Vec3 h=new Vec3(v.x,0,v.z).normalize().scale(.75);setDeltaMovement(h.x,.43,h.z);}
            }
        }
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l&&speech==0){speech=100;say(l,kind()==0?"Non preoccuparti, tesoro. Ci penso io.":kind()==1?"Mi porterai sulla luna?":berserk()?"Grrr, sosu!":"Faputa ti osserva, sosu.");l.broadcastEntityEvent(this,(byte)118);}
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==118||id==119){pose=24;animation=id-118;return;}super.handleEntityEvent(id);}
    public float action(){return pose<=0?0:(float)Math.sin(pose*Math.PI/24);}
    public int animation(){return animation;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(owner!=null)t.putUUID("Owner",owner);if(aggressor!=null)t.putUUID("Aggressor",aggressor);t.putLong("Expires",expires);t.putInt("Rage",rage);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;aggressor=t.hasUUID("Aggressor")?t.getUUID("Aggressor"):null;expires=t.getLong("Expires");rage=t.getInt("Rage");entityData.set(RAGE,rage>0&&aggressor!=null);}
    static boolean summon(ServerPlayer p){
        ServerLevel l=p.serverLevel();var d=Noctis.data(p);long now=l.getGameTime();
        if(d.getLong("bayonettaUntil")>now||!l.getEntitiesOfClass(MoonGuest.class,p.getBoundingBox().inflate(96),x->p.getUUID().equals(x.owner)).isEmpty())return false;
        for(int i=0;i<30;i++){BlockPos q=p.blockPosition().offset(p.getRandom().nextInt(11)-5,0,p.getRandom().nextInt(11)-5);
            if(q.distSqr(p.blockPosition())<4||!l.hasChunkAt(q)||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))continue;
            MoonGuest b=Noctis.BAYONETTA.get().create(l);if(b==null)return false;b.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);b.owner=p.getUUID();b.expires=now+3000;b.setPersistenceRequired();
            if(!l.noCollision(b)||!l.addFreshEntity(b))continue;
            d.putLong("bayonettaUntil",now+3000);b.say(l,"Let's dance, darling.");l.sendParticles(ParticleTypes.WITCH,b.getX(),b.getY()+1,b.getZ(),70,.6,.8,.6,.1);return true;
        }return false;
    }
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        for(int i=1;i<=2;i++){
            final int k=i;
            if((k==2||!l.isDay())&&p.getRandom().nextInt(25)==0&&l.getEntitiesOfClass(MoonGuest.class,p.getBoundingBox().inflate(80),m->m.kind()==k).isEmpty()){
                BlockPos q=Eclipse.spot(p,12,24);if(q!=null){MoonGuest m=(k==1?Noctis.LUCY.get():Noctis.FAPUTA.get()).create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
            }
        }''')
# Three independent articulated models. Atlas packing uses integer dimensions and floating offsets.
N=256;S=4;W=N*S;meshes=[]
for k,n in enumerate(ids):
    cx=cy=rh=0;islands=[];lines=[]
    def cube(x,y,z,w,h,d,m):
        global cx,cy,rh
        ww=2*(w+d);hh=h+d
        if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
        u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N,(n,m,v,hh)
        for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,m,f))
        return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
    def part(var,parent,name,pos,rot,boxes):
        lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
    if k==0:
        part('b','r','body',(0,0,0),(0,0,0),[(-4,-1,-2.5,8,6,5,'suit'),(-2.8,5,-2,6,5,4,'suit'),(-4,9,-2.5,8,3,5,'suit'),(-.8,-.4,-3,2,2,1,'gold')])
        for i,s in enumerate((-1,1)):
            part('bust'+str(i),'b','bust'+str(i),(s*2,1,-2.1),(0,s*.13,s*.05),[(-2,-1,-2,4,4,3,'suit'),(-1.5,-1.3,-1.7,3,2,2,'suit')])
    else:
        part('b','r','body',(0,0,0),(0,0,0),[(-3.5,0,-2.5,7,8,5,'suit'),(-3,7,-2,6,5,4,'suit'),(-3.5,10,-2.5,7,2,5,'trim')])
    part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-4,8,2,8,'hair')])
    for i in range(7):
        part('bang'+str(i),'h','bang'+str(i),(-3+i,-7.5,-3.5),(0,0,(i-3)*(.17 if k!=1 else .12)),[(-.8,0,-.6,1,3+i%3,2,'hair')])
    if k==0:
        part('tower','h','tower',(0,-8,1),(0,0,0),[(-3,-5,-2,6,6,5,'hair'),(-2,-9,-1,4,5,3,'hair'),(-2,-5,-2.3,4,1,1,'red')])
        part('glasses','h','glasses',(0,-3.7,-3.6),(0,0,0),[(-3,-1,-.3,3,1,1,'suit'),(.1,-1,-.3,3,1,1,'suit'),(-.6,-.8,-.6,1,1,1,'suit')])
        for i in range(6):part('lock'+str(i),'h','lock'+str(i),(-2.5+i,-5,3),(0,0,(i-2)*.05),[(-.7,0,-.6,2,12+i%3,2,'hair')])
    elif k==1:
        for i in range(5):part('lock'+str(i),'h','lock'+str(i),(-2.8+i*1.4,-5,3),(0,0,0),[(-.7,0,-.6,2,5+i%3,2,'hair')])
        part('longlock','h','longlock',(3,-5,-2),(0,0,-.08),[(-.7,0,-.5,2,11,2,'hair')])
    else:
        for i,s in enumerate((-1,1)):
            part('ear'+str(i),'h','ear'+str(i),(s*3,-5,0),(0,0,-s*.55),[(-2,-2,-1.5,4,4,3,'fur'),(-1.3,-1.2,-1.8,3,2,1,'pink')])
        for i in range(3):part('tail'+str(i),'b','tail'+str(i),((i-1)*3,6,2.5),(-.55,0,(i-1)*.65),[(-2,-8,-.5,4,9,4,'fur'),(-1.5,-11,0,3,4,3,'fur')])
        part('crest','h','crest',(0,-7,-3.7),(0,0,0),[(-.7,0,-.5,1,3,1,'red')])
    for i,s in enumerate((-1,1)):
        part('arm'+str(i),'r','arm'+str(i),(s*4.8,0,0),(0,0,-s*.12),[(-2,-1,-2,4,7,4,'suit' if k==0 else 'trim' if k==1 else 'fur'),(-1.5,6,-1.5,3,5,3,'suit' if k==0 else 'face' if k==1 else 'fur')])
        if k==0:
            part('gun'+str(i),'arm'+str(i),'gun',(0,10,-1),(0,0,0),[(-.7,-1,-4,2,2,5,'red'),(-.7,1,-.8,2,2,2,'gold')])
            part('ribbon'+str(i),'h','ribbon'+str(i),(s*2,-8,3),(0,0,s*.1),[(-.6,0,0,1,15,1,'red')])
        if k==2:
            for j in range(3):part('claw'+str(i)+str(j),'arm'+str(i),'claw'+str(j),(-1+j,10,-.5),(-.2,0,0),[(-.3,0,-.3,1,2,1,'red')])
        part('leg'+str(i),'r','leg'+str(i),(s*2.1,12,0),(0,0,0),[(-1.7,0,-1.7,3,7,4,'suit' if k!=2 else 'fur'),(-1.8,7,-2.3,4,5,5,'boot' if k!=2 else 'fur')])
    meshes.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    pal={'suit':[(23,24,33),(71,68,101),(143,112,88)][k],'trim':[(48,44,53),(229,232,247),(198,154,63)][k],'face':[(231,183,155),(248,222,208),(151,116,91)][k],'hair':[(27,27,34),(221,210,232),(243,234,213)][k],'gold':(205,156,69),'red':(150,26,53),'boot':(30,31,45),'fur':(241,230,210),'pink':(207,148,144)}
    pix=bytearray(W*W*4)
    for x,y,w,h,m,f in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[m]
                g=.74+.25*math.sin(u*math.pi)+.04*math.cos(v*9)
                if m in ('hair','fur'):g=.72+.27*math.sin(u*31+math.sin(v*7)*1.5)**2
                if k==1 and m=='hair':
                    base=(239,211,229) if v<.33 else (180,214,244) if v<.67 else (190,233,207)
                if m=='suit' and k==0:g=.60+.39*math.exp(-((u-.31)/.25)**2)
                c=tuple(int(a*g) for a in base)
                if m=='suit' and k==1 and (abs(u-.23-v*.15)<.025 or abs(v-.84)<.023):c=(193,57,70)
                if m=='suit' and k==0 and (abs(v-.87)<.022 or min(u,1-u)<.025):c=(143,114,70)
                if m=='face' and f=='front' and h==7:
                    for ex in (.26,.74):
                        dx=(u-ex)/.19;dy=(v-.46)/(.14 if k!=2 else .20);d=dx*dx+dy*dy
                        if d<1:c=(63,37,43)
                        if d<.75:c=(244,235,219)
                        if abs(dx)<.46 and abs(dy)<.85:c=[(104,112,132),(121,167,177),(219,178,68)][k]
                        if abs(dx)<.17 and abs(dy)<.7:c=(22,22,29)
                        if (dx+.18)**2+(dy+.26)**2<.085:c=(255,255,255)
                    if .40<u<.62 and abs(v-.79)<.023:c=(146,59,65)
                    if k==0 and .66<u<.70 and .80<v<.84:c=(59,37,33)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    (assets/'textures/entity'/f'{n}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))))+ch(b'IEND',b''))
    (assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
(java/'MoonGuestClient.java').write_text('''package it.noctis.magic;
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
public class MoonGuestClient{
    static final String[] N={"bayonetta","lucy","faputa"};
    static final ModelLayerLocation[] L=new ModelLayerLocation[3];
    static{for(int i=0;i<3;i++)L[i]=new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[i]),"main");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],MoonGuestClient::mesh0);e.registerLayerDefinition(L[1],MoonGuestClient::mesh1);e.registerLayerDefinition(L[2],MoonGuestClient::mesh2);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.BAYONETTA.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.LUCY.get(),c->new Renderer(c,1));e.registerEntityRenderer(Noctis.FAPUTA.get(),c->new Renderer(c,2));}
'''+ '\n'.join(meshes)+'''
    static class Model extends EntityModel<MoonGuest>{
        final ModelPart r,h,b;final int k;Model(ModelPart r,int k){this.r=r;this.k=k;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(MoonGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.action();h.yRot=yaw*.015f;h.xRot=pitch*.015f-(k==1&&amount<.05f?.18f:0);b.yRot=k==0?a*.3f:0;b.zRot=k==0?(float)Math.sin(limb*.5)*amount*.09f:0;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;ModelPart arm=r.getChild("arm"+i);arm.xRot=-w*.65f-a*(k==0?1.55f:k==2?1.2f:.2f);arm.zRot=(i==0?1:-1)*(.12f+(k==0?a*.4f:k==2&&e.berserk()?.18f:0));r.getChild("leg"+i).xRot=w*.7f;}
            if(k==0){for(int i=0;i<6;i++)h.getChild("lock"+i).xRot=amount*.25f+(float)Math.sin(age*.12+i*.4)*.06f;for(int i=0;i<2;i++)h.getChild("ribbon"+i).xRot=amount*.45f+(float)Math.sin(age*.19+i)*.14f;}
            if(k==1)h.getChild("longlock").xRot=amount*.15f+(float)Math.sin(age*.11)*.05f;
            if(k==2){for(int i=0;i<3;i++)b.getChild("tail"+i).xRot=-.55f+(float)Math.sin(age*(e.berserk()?.35f:.13f)+i)*.18f;for(int i=0;i<2;i++)h.getChild("ear"+i).xRot=(float)Math.sin(age*.13+i)*.1f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float rr,float g,float bb,float a){r.render(p,v,light,overlay,rr,g,bb,a);}
    }
    static class Renderer extends MobRenderer<MoonGuest,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.4f);this.k=k;}@Override protected void scale(MoonGuest e,PoseStack p,float partial){float s=k==0?1.13f:k==2?.86f:1;p.scale(s,s,s);}@Override public ResourceLocation getTextureLocation(MoonGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''',encoding='utf-8')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in zip(ids,names):d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Bayonetta summon and Witch Time, Lucy moon dialogue, Faputa neutral berserk installed')
