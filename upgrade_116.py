"""1.1.6: Malfoid, adult tsundere sorceress, affinity and three-strike boss duel."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Malfoid>> MALFOID=ENTITIES.register("malfoid",()->EntityType.Builder.<Malfoid>of(Malfoid::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(12).build(ID+":malfoid"));
    public static final RegistryObject<Item> MALFOID_EGG=ITEMS.register("malfoid_spawn_egg",()->new ForgeSpawnEggItem(MALFOID,0x203b2e,0xe9cf77,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(MALFOID.get(),Malfoid.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'e.accept(MALFOID_EGG.get());')
(java/'Malfoid.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Malfoid extends PathfinderMob{
    private final ServerBossEvent bar=new ServerBossEvent(Component.literal("Malfoid - Erede dei Malfoy"),BossEvent.BossBarColor.GREEN,BossEvent.BossBarOverlay.NOTCHED_20);
    private CompoundTag affinity=new CompoundTag();
    private UUID partner,enemy;
    private boolean boss=false,stay=false;
    private int speech,cast,cd=45,phase,attack,absent;
    public Malfoid(EntityType<? extends PathfinderMob> t,Level l){super(t,l);bar.setDarkenScreen(true);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,160).add(Attributes.ARMOR,10).add(Attributes.MOVEMENT_SPEED,.30).add(Attributes.FOLLOW_RANGE,64).add(Attributes.KNOCKBACK_RESISTANCE,.65);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(2,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.7){@Override public boolean canUse(){return !boss&&partner==null&&!stay&&super.canUse();}@Override public boolean canContinueToUse(){return !boss&&partner==null&&!stay&&super.canContinueToUse();}});}
    private void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal("Malfoid: "+s));}
    private int points(Player p){return affinity.getInt(p.getUUID().toString());}
    private void points(Player p,int n){affinity.putInt(p.getUUID().toString(),Math.max(0,Math.min(12,n)));}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        ItemStack item=p.getItemInHand(h);
        boolean gift=item.is(Items.EMERALD)||item.is(Items.AMETHYST_SHARD)||item.is(Items.POPPY);
        if(!gift&&!item.isEmpty())return InteractionResult.PASS;
        if(!(level() instanceof ServerLevel l))return InteractionResult.SUCCESS;
        if(boss)return InteractionResult.CONSUME;
        if(speech>0)return InteractionResult.CONSUME;
        speech=65;int a=points(p);
        if(gift){
            if(partner!=null&&!partner.equals(p.getUUID())){say(l,"Ho gia scelto la mia compagnia. Tieniti il regalo.");return InteractionResult.CONSUME;}
            if(a>=12){say(l,"Non devi comprarti il mio affetto, idiota.");return InteractionResult.CONSUME;}
            if(!p.getAbilities().instabuild)item.shrink(1);
            points(p,++a);l.sendParticles(ParticleTypes.HEART,getX(),getY()+1.8,getZ(),5,.3,.3,.3,.01);
            say(l,a<4?"Tsk. Almeno hai un minimo di gusto.":a<8?"Non pensare che questo significhi qualcosa!":a<12?"Forse... la tua compagnia non e' cosi terribile.":"Forse mi piaci davvero. Non farmelo ripetere!");
            p.displayClientMessage(Component.literal("Affinita' Malfoid: "+a+"/12"),true);
        }else if(a>=12&&partner==null&&p.isShiftKeyDown()){
            partner=p.getUUID();stay=false;setPersistenceRequired();say(l,"Va bene, ti accompagnero'. Ma non montarti la testa!");l.sendParticles(ParticleTypes.HEART,getX(),getY()+1.5,getZ(),15,.4,.4,.4,.03);
        }else if(p.getUUID().equals(partner)&&p.isShiftKeyDown()){
            stay=!stay;getNavigation().stop();say(l,stay?"Ti aspetto qui. Non tardare.":"Andiamo, prima che cambi idea.");
        }else{
            String[] lines=a<4?new String[]{"Non hai di meglio da fare?","Sai chi e' mio padre?","Tsk. Stai attento a come mi parli."}:a<8?new String[]{"Non e' che aspettassi proprio te.","Sei meno insopportabile del solito."}:new String[]{"Non guardarmi cosi!","B-bene, puoi restare ancora un po'.","Non e' che mi mancassi, sia chiaro."};
            say(l,lines[random.nextInt(lines.length)]);
            if(a>=12&&partner==null)p.displayClientMessage(Component.literal("Shift + tasto destro per chiederle di accompagnarti."),true);
        }
        return InteractionResult.CONSUME;
    }
    @Override public boolean hurt(DamageSource s,float amount){
        if(!(level() instanceof ServerLevel l)||boss)return super.hurt(s,amount);
        if(s.getEntity() instanceof Player p&&!p.isCreative()&&!p.isSpectator()&&amount>0){
            String k="Strikes_"+p.getUUID();String time="Last_"+p.getUUID();long now=l.getGameTime();
            if(affinity.contains(time)&&now-affinity.getLong(time)<8)return false;
            int n=affinity.getInt(k)+1;affinity.putInt(k,n);affinity.putLong(time,now);points(p,points(p)-3);
            if(n==1){say(l,"COME OSI?! LO DIRO' A MIO PADRE!");return false;}
            if(n==2){say(l,"Ultimo avvertimento. Mio padre verra' a saperlo!");return false;}
            affinity.putInt(k,0);enemy=p.getUUID();partner=null;stay=false;boss=true;setAggressive(true);setPersistenceRequired();
            getAttribute(Attributes.MAX_HEALTH).setBaseValue(700);getAttribute(Attributes.ARMOR).setBaseValue(18);setHealth(getMaxHealth());
            getNavigation().stop();cd=35;phase=0;attack=0;absent=0;bar.setProgress(1);bar.addPlayer((ServerPlayer)p);
            say(l,"BASTA! Non ho bisogno di mio padre per sistemarti!");l.sendParticles(ParticleTypes.WITCH,getX(),getY()+1,getZ(),90,.8,1,.8,.15);playSound(SoundEvents.WITHER_SPAWN,1,.9f);return false;
        }
        return super.hurt(s,amount);
    }
    void spell(ServerLevel l,LivingEntity victim,boolean duel){
        int mode=attack++%3;l.broadcastEntityEvent(this,(byte)89);Vec3 a=getEyePosition(),b=victim.getEyePosition();
        for(int i=0;i<26;i++){Vec3 v=a.lerp(b,i/25.0);l.sendParticles(mode==0?ParticleTypes.WITCH:mode==1?ParticleTypes.ELECTRIC_SPARK:ParticleTypes.END_ROD,v.x,v.y,v.z,3,.12,.12,.12,.02);}
        float damage=duel?22+phase*5:16;
        victim.hurt(damageSources().mobAttack(this),damage);
        if(mode==0){victim.addEffect(new MobEffectInstance(MobEffects.POISON,100,0));if(duel)say(l,"Crucio!");}
        else if(mode==1){victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,80,3));victim.knockback(1.2,getX()-victim.getX(),getZ()-victim.getZ());if(duel)say(l,"Expelliarmus!");}
        else{addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,100,1));if(duel){heal(8);say(l,"Protego!");}else if(partner!=null&&l.getEntity(partner) instanceof LivingEntity ally)ally.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,100,0));}
        playSound(SoundEvents.EVOKER_CAST_SPELL,1,.85f);
    }
    @Override public void tick(){
        super.tick();if(speech>0)speech--;if(cast>0)cast--;if(cd>0)cd--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        if(boss){
            bar.setProgress(getHealth()/getMaxHealth());
            if(tickCount%20==0){for(ServerPlayer p:l.players())if(distanceToSqr(p)<4096)bar.addPlayer(p);else bar.removePlayer(p);}
            Player t=enemy==null?null:l.getPlayerByUUID(enemy);
            if(t==null||!t.isAlive()||t.isCreative()||t.isSpectator()||distanceToSqr(t)>6400){
                getNavigation().stop();if(++absent>600){boss=false;enemy=null;setAggressive(false);bar.removeAllPlayers();getAttribute(Attributes.MAX_HEALTH).setBaseValue(160);getAttribute(Attributes.ARMOR).setBaseValue(10);setHealth(getMaxHealth());}return;
            }
            absent=0;int next=getHealth()<getMaxHealth()*.33?2:getHealth()<getMaxHealth()*.67?1:0;
            if(next>phase){phase=next;say(l,phase==1?"Adesso basta giocare!":"NON SAI CON CHI HAI A CHE FARE!");l.sendParticles(ParticleTypes.WITCH,getX(),getY()+1,getZ(),70,.6,.8,.6,.12);}
            getLookControl().setLookAt(t,50,50);
            if(distanceTo(t)>13||!hasLineOfSight(t)){if(tickCount%5==0)getNavigation().moveTo(t,1.25);return;}
            getNavigation().stop();if(cd==0){cd=phase==2?28:phase==1?40:55;spell(l,t,true);}
        }else if(partner!=null&&l.getEntity(partner) instanceof Player p&&p.isAlive()){
            if(!stay&&distanceTo(p)>4&&tickCount%10==0)getNavigation().moveTo(p,1.15);
            if(cd==0){LivingEntity t=l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(16),e->e!=this&&e.isAlive()&&Eclipse.hostile(e)&&hasLineOfSight(e)).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);if(t!=null){getLookControl().setLookAt(t,50,50);cd=55;spell(l,t,false);}}
        }
    }
    @Override public void handleEntityEvent(byte id){if(id==89){cast=24;return;}super.handleEntityEvent(id);}
    public float casting(){return cast<=0?0:(float)Math.sin(cast*Math.PI/24);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
    @Override public void remove(RemovalReason reason){bar.removeAllPlayers();super.remove(reason);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("Affinity",affinity.copy());if(partner!=null)t.putUUID("Partner",partner);if(enemy!=null)t.putUUID("Enemy",enemy);t.putBoolean("Boss",boss);t.putBoolean("Stay",stay);t.putInt("Phase",phase);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);affinity=t.getCompound("Affinity");partner=t.hasUUID("Partner")?t.getUUID("Partner"):null;enemy=t.hasUUID("Enemy")?t.getUUID("Enemy"):null;boss=t.getBoolean("Boss");stay=t.getBoolean("Stay");phase=t.getInt("Phase");setAggressive(boss);}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(p.getRandom().nextInt(20)==0&&l.getEntitiesOfClass(Malfoid.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){Malfoid m=Noctis.MALFOID.get().create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }''')
# Face-specific custom atlas and long swept blonde hair, green-trimmed robe.
N=256;S=4;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((fx,fy,fw,fh,mat,face))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
part('b','r','body',(0,0,0),(0,0,0),[(-3,-1,-2,6,11,4,'vest'),(-3,9,-2,6,3,4,'robe')])
part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face')])
part('hair','h','hair',(0,-7,0),(0,0,0),[(-4,-1,-3.5,8,2,7,'hair')])
for j in range(7):
    part('back'+str(j),'h','back'+str(j),(-3.5+j*1.15,-6,2.5),(0,0,(j-3)*.035),[(-.65,0,-.5,2,16+j%3,2,'hair')])
for i,sign in enumerate((-1,1)):
    part('lock'+str(i),'h','lock'+str(i),(sign*3.6,-6,-.2),(0,0,sign*.12),[(-1,0,-1.5,2,17,3,'hair')])
    part('ear'+str(i),'h','ear'+str(i),(sign*3.5,-3,0),(0,0,0),[(-.5,-1,-.5,1,2,1,'skin')])
    part('hoop'+str(i),'ear'+str(i),'hoop',(0,1,-.5),(0,0,0),[(-.5,0,0,1,3,1,'metal'),(-.5,2,-.5,2,1,1,'metal')])
    part('arm'+str(i),'r','arm'+str(i),(sign*4,0,0),(0,0,-sign*.08),[(-1.5,-1,-1.5,3,9,3,'robe'),(-1.5,7,-1.5,3,2,3,'green'),(-1,9,-1,2,2,2,'skin')])
    part('leg'+str(i),'r','leg'+str(i),(sign*1.8,12,0),(0,0,0),[(-1.5,0,-1.5,3,9,3,'robe'),(-1.5,9,-2,3,3,4,'metal')])
    part('coat'+str(i),'b','coat'+str(i),(sign*2.5,8,1),(.1,0,sign*.12),[(-2,0,-2,4,13,3,'robe')])
    part('lapel'+str(i),'b','lapel'+str(i),(sign*2.6,-.5,-2.1),(0,0,sign*.22),[(-.5,0,-.5,2,8,1,'green')])
for j in range(5):
    part('bang'+str(j),'h','bang'+str(j),(-2.4+j*1.15,-7,-3.5),(0,0,-.30+j*.14),[(-.6,0,-.5,2,2+j%3,1,'hair')])
part('tie','b','tie',(0,0,-2.4),(0,0,0),[(-.75,0,-.3,1,6,1,'tie')])
part('wand','arm1','wand',(0,10,-1),(0,0,.2),[(-.3,-.5,-.3,1,8,1,'wood')])
(java/'MalfoidClient.java').write_text('''package it.noctis.magic;
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
public class MalfoidClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"malfoid"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,MalfoidClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MALFOID.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<Malfoid>{
        final ModelPart r,h,b;Model(ModelPart r){this.r=r;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(Malfoid e,float limb,float amount,float age,float yaw,float pitch){
            float cast=e.casting();h.yRot=yaw*.01745f;h.xRot=pitch*.01745f;h.zRot=e.isAggressive()?0:.06f;
            for(int i=0;i<2;i++){int side=i==0?-1:1;float walk=(float)Math.cos(limb*.6662+i*Math.PI)*amount;r.getChild("leg"+i).xRot=walk*.7f;r.getChild("arm"+i).xRot=-walk*.7f-(i==1?cast*1.9f:0);h.getChild("lock"+i).xRot=amount*.18f+(float)Math.sin(age*.12+i)*.07f;h.getChild("lock"+i).zRot=side*(.12f+cast*.16f);b.getChild("coat"+i).xRot=.1f+amount*.2f;}
            for(int j=0;j<7;j++)h.getChild("back"+j).xRot=amount*.25f+(float)Math.sin(age*.12+j*.5)*.07f+cast*.12f;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<Malfoid,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.35f);}@Override public ResourceLocation getTextureLocation(Malfoid e){return new ResourceLocation(Noctis.ID,"textures/entity/malfoid.png");}}
}''',encoding='utf-8')
pal={'vest':(81,77,76),'robe':(47,35,35),'face':(239,186,151),'skin':(230,179,148),'hair':(237,194,96),'metal':(28,25,31),'green':(35,91,67),'tie':(33,78,57),'wood':(75,44,35)}
pix=bytearray(W*W*4)
for x,y,w,h,mat,face in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);base=pal[mat];g=.76+.23*math.sin(u*math.pi)+.04*math.cos(v*10)
            if mat=='hair':g=.62+.36*math.sin(u*30+v*3)**2+.06*math.sin(v*2)
            c=tuple(int(z*g) for z in base)
            if mat=='face' and face=='front':
                for ex in (.27,.73):
                    dx=(u-ex)/.20;dy=(v-.46+(.5-ex)*dx*.045)/.15;d=dx*dx+dy*dy
                    if d<1:c=(39,27,28)
                    if d<.76:c=(250,241,224)
                    if d<.72 and abs(dx)<.48:c=(93,148,82)
                    if d<.65 and abs(dx)<.22:c=(22,42,26)
                    if (dx+.15)**2+(dy+.32)**2<.06:c=(250,255,235)
                    if abs(dx)<1 and abs(dy+.86)<.15:c=(53,32,28)
                    if abs(u-ex)<.15 and abs(v-.25+dx*.027)<.025:c=(132,92,44)
                if .39<u<.61 and abs(v-.79)<.018:c=(142,65,59)
            if mat=='tie' and (u+v*5)%1<.18:c=(190,192,173)
            if mat=='vest' and v<.26 and abs(u-.5)<.25-v*.5:c=(218,212,198)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,z)) for z in c],255))
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
(assets/'textures/entity/malfoid.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(assets/'models/item/malfoid_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.malfoid']='Malfoid';d['item.noctismagic.malfoid_spawn_egg']='Uovo generatore: Malfoid' if lang=='it_it' else 'Malfoid Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Malfoid affinity, public dialogue and three-strike boss installed')
