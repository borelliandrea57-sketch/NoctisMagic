"""1.4.0: three original gothic horror enemies, inspired by supplied character art."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
    p.parent.mkdir(parents=True,exist_ok=True)
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
ids=['crimson_lady','iron_midwife','skull_stalker']
names=['Dama Cremisi','Levatrice del Ferro','Predatore delle Ossa']
decl=''
for n,w,h,hp,c1,c2 in zip(ids,[.85,2.4,1.3],[2.05,3.8,2.9],[180,420,160],['0x771a32','0x613d2e','0x473238'],['0xc3a26b','0xd69d4d','0xc6b69d']):
    r=n.upper();decl+=f'public static final RegistryObject<EntityType<GothicHorror>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<GothicHorror>of(GothicHorror::new,MobCategory.MONSTER).sized({w}f,{h}f).clientTrackingRange(12).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{c1},{c2},new Item.Properties()));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG=';edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,''.join(f'e.put({n.upper()}.get(),GothicHorror.attributes({i}).build());' for i,n in enumerate(ids))+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({n.upper()}_EGG.get());' for n in ids))
write('GothicHorror.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class GothicHorror extends Monster{
    final ServerBossEvent bar=new ServerBossEvent(Component.literal("Levatrice del Ferro"),BossEvent.BossBarColor.RED,BossEvent.BossBarOverlay.NOTCHED_20);
    int cooldown=70,windup,pose,phase;
    public GothicHorror(EntityType<? extends Monster> t,Level l){super(t,l);bar.setVisible(kind()==1);}
    public int kind(){return getType()==Noctis.CRIMSON_LADY.get()?0:getType()==Noctis.IRON_MIDWIFE.get()?1:2;}
    public static AttributeSupplier.Builder attributes(int k){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,k==0?180:k==1?420:160).add(Attributes.ARMOR,k==0?9:k==1?16:7).add(Attributes.ATTACK_DAMAGE,k==0?16:k==1?23:18).add(Attributes.MOVEMENT_SPEED,k==0?.31:k==1?.20:.35).add(Attributes.FOLLOW_RANGE,36).add(Attributes.KNOCKBACK_RESISTANCE,k==1?.9:.35);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));
        goalSelector.addGoal(1,new MeleeAttackGoal(this,1.15,true){@Override public boolean canUse(){return windup==0&&super.canUse();}@Override public boolean canContinueToUse(){return windup==0&&super.canContinueToUse();}});
        goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.7));
        goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));
        targetSelector.addGoal(1,new HurtByTargetGoal(this));
        targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));
    }
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);if(kind()==1)bar.addPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
    @Override public void remove(RemovalReason r){bar.removeAllPlayers();super.remove(r);}
    @Override public boolean removeWhenFarAway(double d){return kind()!=1;}
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(cooldown>0)cooldown--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        int k=kind();if(k==1){bar.setProgress(Math.max(0,getHealth()/getMaxHealth()));phase=getHealth()<getMaxHealth()*.5?1:0;}
        LivingEntity t=getTarget();
        if(windup>0){getNavigation().stop();if(--windup==0&&t!=null&&t.isAlive()&&hasLineOfSight(t)){special(l,t,k);cooldown=k==1?(phase==1?65:95):75;}return;}
        if(t==null||!t.isAlive())return;
        double d=distanceTo(t);
        if(k==1&&tickCount%20==0)l.sendParticles(ParticleTypes.SMOKE,getX(),getY()+3,getZ(),3,.35,.2,.35,.015);
        if(cooldown==0&&d<(k==0?10:k==1?8:7)&&hasLineOfSight(t)){
            windup=24;getNavigation().stop();l.broadcastEntityEvent(this,(byte)116);
            playSound(k==1?SoundEvents.IRON_GOLEM_HURT:k==2?SoundEvents.ENDERMAN_STARE:SoundEvents.EVOKER_PREPARE_ATTACK,1,.65f);
            if(k==1)l.sendParticles(ParticleTypes.FLAME,getX(),getY()+.25,getZ(),24,1,.08,1,.015);
        }
    }
    void special(ServerLevel l,LivingEntity t,int k){
        if(k==0){
            Vec3 a=getEyePosition(),b=t.position().add(0,1,0);
            for(int i=0;i<22;i++){Vec3 q=a.lerp(b,i/21.0);l.sendParticles(ParticleTypes.CRIMSON_SPORE,q.x,q.y,q.z,3,.08,.08,.08,.02);}
            if(distanceTo(t)<10){t.hurt(damageSources().magic(),13);t.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,100,0));}
        }else if(k==1){
            for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(5),p->p.isAlive()&&!p.isCreative()&&!p.isSpectator()&&hasLineOfSight(p))){
                p.hurt(damageSources().mobAttack(this),phase==1?27:22);p.knockback(1.4,getX()-p.getX(),getZ()-p.getZ());p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,1));}
            l.sendParticles(ParticleTypes.POOF,getX(),getY()+.3,getZ(),70,2,.2,2,.09);playSound(SoundEvents.ANVIL_LAND,1,.6f);
        }else{
            Vec3 v=t.position().subtract(position());if(onGround()&&distanceTo(t)>2.5){Vec3 h=new Vec3(v.x,0,v.z).normalize().scale(.55);setDeltaMovement(h.x,.35,h.z);}
            if(distanceTo(t)<5){t.hurt(damageSources().mobAttack(this),20);t.addEffect(new MobEffectInstance(MobEffects.DARKNESS,80,0));}
            l.sendParticles(ParticleTypes.SMOKE,getX(),getY()+1,getZ(),24,.5,.7,.5,.06);
        }
    }
    @Override public boolean doHurtTarget(Entity e){boolean ok=super.doHurtTarget(e);if(ok&&level() instanceof ServerLevel l)l.broadcastEntityEvent(this,(byte)117);return ok;}
    @Override public void handleEntityEvent(byte id){if(id==116||id==117){pose=id==116?32:16;return;}super.handleEntityEvent(id);}
    public float action(){return pose<=0?0:(float)Math.sin(Math.min(1,pose/24f)*Math.PI);}
    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource s,int looting,boolean hit){super.dropCustomDeathLoot(s,looting,hit);if(kind()==1){spawnAtLocation(Items.COPPER_INGOT,12);spawnAtLocation(Items.NETHER_STAR);}else spawnAtLocation(kind()==0?Items.AMETHYST_SHARD:Items.BONE,3+random.nextInt(3));}
}''')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if((!l.isDay()||Eclipse.active(l))&&l.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL&&!p.isCreative()&&p.getRandom().nextInt(Eclipse.active(l)?3:12)==0&&l.getEntitiesOfClass(GothicHorror.class,p.getBoundingBox().inflate(72)).isEmpty()){
            int roll=p.getRandom().nextInt(10);var type=roll<4?Noctis.CRIMSON_LADY.get():roll<6?Noctis.IRON_MIDWIFE.get():Noctis.SKULL_STALKER.get();
            BlockPos q=Eclipse.spot(p,18,30);if(q!=null){GothicHorror m=type.create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }''')
# Meshes with separate articulated limbs, layered garments, bronze cage, drapery, masks and skull lure.
N=512;S=4;W=N*S;meshes=[]
for k,n in enumerate(ids):
    cx=cy=rh=0;islands=[];lines=[]
    def cube(x,y,z,w,h,d,m):
        global cx,cy,rh
        ww=2*(w+d);hh=h+d
        if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
        u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
        for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,m,f))
        return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
    def part(var,parent,name,pos,rot,boxes):
        lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
    if k==0:
        part('b','r','body',(0,0,0),(0,0,0),[(-4,0,-2.5,8,9,5,'black'),(-3,8,-2,6,3,4,'red'),(-4,10,-2.6,8,1,5,'gold'),(-2,0,-3,4,3,1,'lace')])
        part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-4,8,2,8,'hair'),(-4,-10,-3.8,8,2,7,'red'),(-4.3,-8.5,-4.5,8,1,8,'gold'),(-4,-8,-4.6,2,2,1,'rose')])
        for j in range(7):
            part('bang'+str(j),'h','bang'+str(j),(-3+j,-7,-3.7),(0,0,(j-3)*.15),[(-.7,0,-.6,1,3+j%3,2,'hair')])
            part('lock'+str(j),'h','lock'+str(j),(-3+j,-5,3),(0,0,(j-3)*.08),[(-.8,0,-.6,2,7+j%3,2,'hair')])
        for i,s in enumerate((-1,1)):
            part('a'+str(i),'r','arm'+str(i),(s*5,0,0),(0,0,-s*.1),[(-2,-1,-2,4,8,4,'black'),(-2.5,-2,-2.5,5,2,5,'gold'),(-2.4,6,-2.4,5,2,5,'lace'),(-1.5,8,-1.5,3,3,3,'black')])
            part('leg'+str(i),'r','leg'+str(i),(s*2.2,12,0),(0,0,0),[(-1.5,0,-1.5,3,8,3,'black'),(-2,7,-2.5,4,5,5,'boot')])
            part('tail'+str(i),'b','tail'+str(i),(s*3,10,2),(.12,0,-s*.22),[(-3,0,-1,6,11,2,'red'),(-3,8,-1.2,6,3,1,'lace')])
        part('skirt','b','skirt',(0,10,0),(0,0,0),[(-5,0,-3,10,3,6,'red'),(-6,3,-4,12,2,8,'black'),(-6.4,5,-4.4,13,2,9,'lace'),(-6,7,-4,12,1,8,'red')])
        part('bow','b','bow',(0,10,-3.5),(0,0,0),[(-3,-1,-.5,6,2,1,'red'),(-.7,-1.5,-1,2,3,1,'gold')])
        part('blade','a1','blade',(0,10,-1),(-1.1,0,0),[(-.5,0,-.5,1,3,1,'black'),(-2,3,-1,4,1,2,'gold'),(-.5,4,-.5,1,13,1,'bone')])
    elif k==1:
        part('b','r','body',(0,4,0),(0,0,0),[(-8,-5,-5,16,12,11,'dark'),(-7,-12,-5,14,8,10,'amber'),(-8,-13,-6,16,2,12,'metal'),(-8,-5,-6,16,2,12,'metal'),(-6,6,-5,12,4,10,'dark')])
        part('h','b','head',(0,-2,-6),(0,0,0),[(-5,-4,-2,10,9,5,'cloth'),(-4,2,-3,8,5,3,'dark')])
        for j in range(7):
            x=-6+j*2
            part('rib'+str(j),'b','rib'+str(j),(x,-9,-5),(0,0,(j-3)*.045),[(-.5,-4,-.5,1,9,1,'metal')])
            part('mask'+str(j),'h','mask'+str(j),(-4+(j%3)*4,-2+(j//3)*3,-3.5),(0,(j%3-1)*.17,0),[(-1.4,-1.6,-.5,3,4,1,'mask')])
        part('crown','b','crown',(0,-13,0),(0,0,0),[(-6,-2,-4,12,2,8,'metal'),(-3,-4,-3,6,2,6,'metal'),(-1,-6,-1,2,2,2,'gold')])
        for i,s in enumerate((-1,1)):
            part('a'+str(i),'b','arm'+str(i),(s*8,2,-4),(0,0,-s*.45),[(-1.5,0,-1.5,3,8,3,'metal')])
            part('fore'+str(i),'a'+str(i),'fore',(0,7,0),(-.9,0,s*.2),[(-1,0,-1,2,8,2,'bone'),(-1,7,-1,2,3,2,'metal')])
            for j in range(3):part('claw'+str(i)+str(j),'fore'+str(i),'claw'+str(j),(-1+j,8,-.5),(-.3,0,0),[(-.25,0,-.25,1,5,1,'bone')])
            part('veil'+str(i),'b','veil'+str(i),(s*7,-8,0),(0,0,-s*.14),[(-2,0,-5,4,18,1,'lace'),(-2,0,0,4,15,1,'cloth'),(-2,0,4,4,17,1,'lace')])
            for j,z in enumerate((-3,4)):
                part('leg'+str(i)+str(j),'r','leg'+str(i)+str(j),(s*6,10,z),(0,0,-s*.45),[(-1.5,0,-1.5,3,8,3,'metal')])
                part('shin'+str(i)+str(j),'leg'+str(i)+str(j),'shin',(0,7,0),(0,0,s*.6),[(-1,0,-1,2,7,2,'metal'),(-1,6,-2,2,2,3,'bone')])
        for j in range(5):part('chain'+str(j),'b','chain'+str(j),(-6+j*3,1,6),(0,0,0),[(-.5,0,-.5,1,9+j%3,1,'chain')])
    else:
        part('b','r','body',(0,5,1),(.28,0,0),[(-4,-7,-3,8,11,6,'flesh'),(-3,3,-2,6,5,4,'dark'),(-4,-6,2,8,10,2,'bone')])
        part('h','b','head',(0,-6,-4),(-.25,0,0),[(-4,-5,-4,8,7,7,'dark'),(-3,2,-3.5,6,4,5,'mouth')])
        for i in range(7):
            part('tooth'+str(i),'h','tooth'+str(i),(-3+i,1,-4),(0,0,0),[(-.4,0,-.4,1,2+i%2,1,'bone')])
        for i,s in enumerate((-1,1)):
            for j in range(4):part('rib'+str(i)+str(j),'b','rib'+str(i)+str(j),(s*3,-5+j*2,-3),(0,0,s*.3),[(-.6,0,-.5,2,1,2,'bone')])
            part('a'+str(i),'b','arm'+str(i),(s*4,-4,0),(0,0,-s*.22),[(-1.5,0,-1.5,3,10,3,'flesh')])
            part('fore'+str(i),'a'+str(i),'fore',(0,9,0),(-.25,0,s*.13),[(-1,0,-1,2,9,2,'bone')])
            for j in range(3):part('claw'+str(i)+str(j),'fore'+str(i),'claw'+str(j),(-1+j,8,0),(-.5,0,0),[(-.3,0,-.3,1,5,1,'bone')])
            part('leg'+str(i),'r','leg'+str(i),(s*2.8,13,0),(-.25,0,0),[(-1.5,0,-1.5,3,7,3,'flesh')])
            part('shin'+str(i),'leg'+str(i),'shin',(0,6,0),(.55,0,0),[(-1,0,-1,2,6,2,'bone'),(-1.5,5,-2,3,2,4,'flesh')])
        part('lure','b','lure',(0,-7,3),(-.7,0,0),[(-1, -9,-1,2,9,2,'flesh')])
        part('arch','lure','arch',(0,-8,0),(.75,0,0),[(-1,-7,-1,2,7,2,'flesh')])
        part('tip','arch','tip',(0,-6,0),(1.15,0,0),[(-1,-7,-1,2,7,2,'flesh')])
        part('skull','tip','skull',(0,-6,0),(1.0,0,0),[(-2.5,-2.5,-2.5,5,5,5,'mask'),(-1.5,2,-2,3,2,3,'bone')])
    meshes.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,512,512);}')
    pal={'black':(34,24,33),'red':(117,12,38),'gold':(196,145,72),'lace':(222,199,181),'face':(238,192,169),'hair':(99,57,45),'rose':(168,17,49),'boot':(45,27,31),'dark':(46,26,31),'amber':(221,148,64),'metal':(112,73,43),'cloth':(93,35,42),'mask':(180,159,134),'bone':(192,175,149),'chain':(129,93,58),'flesh':(111,64,64),'mouth':(28,13,19)}
    pix=bytearray(W*W*4)
    for x,y,w,h,m,f in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[m]
                g=.65+.34*math.sin(u*math.pi)+.06*math.cos(v*13)+.025*math.sin(u*95+v*137)
                if m in ('metal','gold','bone'):g=.48+.52*math.exp(-((u-.36)/.24)**2)
                if m=='hair':g=.65+.34*math.sin(u*35+math.sin(v*9)*1.4)**2
                if m in ('cloth','red','lace'):g*=.83+.17*math.sin(u*24+math.sin(v*7))**2
                c=tuple(int(t*g) for t in base)
                if m in ('red','black') and k==0 and (min(u,1-u)<.04 or abs(v-.9)<.024 or (v>.6 and abs(math.sin(u*28+v*10))<.07)):c=pal['gold']
                if m=='lace' and abs(math.sin(u*31)*math.cos(v*27))<.14:c=(125,91,90)
                if m=='metal' and (min(u,1-u)<.07 or min(v,1-v)<.05):c=(59,36,29)
                if m=='amber':c=(int(225*g),int(145*g),int(50*g))
                if m in ('face','mask') and f=='front':
                    for ex in (.27,.73):
                        dx=(u-ex)/.18;dy=(v-.43)/.14
                        if dx*dx+dy*dy<1:c=(43,21,28)
                        if m=='face' and dx*dx+dy*dy<.78:c=(246,231,221)
                        if m=='face' and abs(dx)<.48 and abs(dy)<.9:c=(173,27,57)
                        if m=='face' and abs(dx)<.18 and abs(dy)<.7:c=(40,14,27)
                        if m=='face' and (dx+.18)**2+(dy+.23)**2<.09:c=(255,255,255)
                    if .38<u<.62 and abs(v-.78)<.03:c=(76,35,37)
                if m=='dark' and k==2 and f=='front' and h==7:
                    if v>.48:c=(20,10,15)
                    if any(((u-ex)/.085)**2+((v-.24)/.07)**2<1 for ex in (.2,.4,.6,.8)):c=(228,207,160)
                if m=='chain' and abs(math.sin(v*math.pi*12))<.28:c=(47,31,27)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,t)) for t in c],255))
    png(assets/'textures/entity'/f'{n}.png',W,W,pix)
    dump(assets/'models/item'/f'{n}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
write('GothicHorrorClient.java','''package it.noctis.magic;
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
public class GothicHorrorClient{
    static final String[] N={"crimson_lady","iron_midwife","skull_stalker"};
    static final ModelLayerLocation[] L=new ModelLayerLocation[3];
    static{for(int i=0;i<3;i++)L[i]=new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[i]),"main");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],GothicHorrorClient::mesh0);e.registerLayerDefinition(L[1],GothicHorrorClient::mesh1);e.registerLayerDefinition(L[2],GothicHorrorClient::mesh2);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.CRIMSON_LADY.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.IRON_MIDWIFE.get(),c->new Renderer(c,1));e.registerEntityRenderer(Noctis.SKULL_STALKER.get(),c->new Renderer(c,2));}
'''+ '\n'.join(meshes)+'''
    static class Model extends EntityModel<GothicHorror>{
        final ModelPart r,b,h;final int k;
        Model(ModelPart r,int k){this.r=r;this.k=k;b=r.getChild("body");h=k==0?r.getChild("head"):b.getChild("head");}
        @Override public void setupAnim(GothicHorror e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.action(),breath=(float)Math.sin(age*.11)*.035f;
            h.yRot=yaw*.008f;h.xRot=(k==2?-.25f:0)+pitch*.01f-a*.1f;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.6+i*Math.PI)*amount;
                ModelPart arm=(k==0?r:b).getChild("arm"+i);arm.xRot=-w*.45f-a*(k==0?1.3f:.85f);
                if(k==1){
                    for(int j=0;j<2;j++){ModelPart leg=r.getChild("leg"+i+j);float t=(float)Math.cos(limb*.55+(i+j)*Math.PI)*amount;leg.xRot=t*.46f;leg.getChild("shin").xRot=Math.max(0,-t)*.5f;}
                    b.getChild("veil"+i).xRot=breath+amount*.2f;arm.getChild("fore").xRot=-.9f-a*.4f;
                }else{
                    ModelPart leg=r.getChild("leg"+i);leg.xRot=(k==2?-.25f:0)+w*.65f;
                    if(k==0)b.getChild("tail"+i).xRot=.12f+amount*.25f+a*.2f;
                    else{leg.getChild("shin").xRot=.55f+Math.max(0,-w)*.5f;arm.getChild("fore").xRot=-.25f-a*.7f;}
                }
            }
            if(k==0){for(int j=0;j<7;j++)h.getChild("lock"+j).xRot=breath+amount*.18f;b.getChild("skirt").zRot=breath;}
            if(k==1){for(int j=0;j<5;j++)b.getChild("chain"+j).xRot=(float)Math.sin(age*.14+j*.6)*(.07f+amount*.14f);}
            if(k==2){b.xRot=.28f+breath+a*.18f;ModelPart lure=b.getChild("lure");lure.xRot=-.7f+breath+a*.2f;lure.getChild("arch").zRot=(float)Math.sin(age*.13)*.1f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float rr,float g,float bb,float a){r.render(p,v,light,overlay,rr,g,bb,a);}
    }
    static class Renderer extends MobRenderer<GothicHorror,Model>{
        final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),k==1?1.1f:.45f);this.k=k;}
        @Override protected void scale(GothicHorror e,PoseStack p,float partial){float s=k==1?1.5f:k==2?1.25f:1f;p.scale(s,s,s);}
        @Override public ResourceLocation getTextureLocation(GothicHorror e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}
    }
}''')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,it,en in zip(ids,names,['Crimson Lady','Iron Midwife','Skull Stalker']):
        name=it if lang=='it_it' else en;d['entity.noctismagic.'+n]=name;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+name
    dump(p,d)
p=res/'data/forge/tags/entity_types/bosses.json';d=json.loads(p.read_text()) if p.exists() else {'replace':False,'values':[]}
d['values'].append('noctismagic:iron_midwife');dump(p,d)
print('Three gothic horror enemies, custom 2048 textures, combat animations and spawn eggs installed')
