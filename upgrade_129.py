"""1.2.9: Leon zombie patrol, Phoenix and Edgeworth tea in pastry shops."""
from pathlib import Path
import sys,json,math,struct,zlib,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
ids=['leon_kennedy','phoenix_wright','miles_edgeworth'];labels=['Leon S. Kennedy','Phoenix Wright','Miles Edgeworth']
decl=''
for n,c,d in zip(ids,['0x71583b','0x234b80','0x8f263b'],['0xceb480','0xb6356c','0xe8e5df']):
    r=n.upper();decl+=f'public static final RegistryObject<EntityType<CrossoverGuest>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<CrossoverGuest>of(CrossoverGuest::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{c},{d},new Item.Properties()));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG=';edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,''.join(f'e.put({n.upper()}.get(),CrossoverGuest.attributes().build());' for n in ids)+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({n.upper()}_EGG.get());' for n in ids))
a='static final RegistryObject<SoundEvent> MOONWALK_SHOUT='
edit('FallenEncounter.java',a,'''static final RegistryObject<SoundEvent> PHOENIX_OBJECTION=SOUNDS.register("phoenix_objection",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"phoenix_objection")));
    static final RegistryObject<SoundEvent> MILES_OBJECTION=SOUNDS.register("miles_objection",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"miles_objection")));
    '''+a)
write('CrossoverGuest.java','''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class CrossoverGuest extends PathfinderMob{
    int cooldown=40,speech=0,pose=0,animation=0;UUID lastVisitor;BlockPos home;
    public CrossoverGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public int kind(){return getType()==Noctis.LEON_KENNEDY.get()?0:getType()==Noctis.PHOENIX_WRIGHT.get()?1:2;}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,100).add(Attributes.ARMOR,8).add(Attributes.MOVEMENT_SPEED,.33).add(Attributes.ATTACK_DAMAGE,18).add(Attributes.FOLLOW_RANGE,40);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.2,true){@Override public boolean canUse(){return kind()==0&&!level().isDay()&&super.canUse();}@Override public boolean canContinueToUse(){return kind()==0&&!level().isDay()&&super.canContinueToUse();}});
        goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.8){@Override public boolean canUse(){return kind()==0&&super.canUse();}@Override public boolean canContinueToUse(){return kind()==0&&super.canContinueToUse();}});
        goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));
    }
    public void setHome(BlockPos p){home=p;}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}
    void object(ServerLevel l,Player p){
        speech=180;lastVisitor=p.getUUID();l.broadcastEntityEvent(this,(byte)102);
        say(l,"OBIEZIONE!");playSound(kind()==1?FallenEncounter.PHOENIX_OBJECTION.get():FallenEncounter.MILES_OBJECTION.get(),1.3f,1f);
        l.sendParticles(ParticleTypes.ANGRY_VILLAGER,getX(),getY()+1.9,getZ(),4,.2,.2,.2,.01);
    }
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(cooldown>0)cooldown--;if(speech>0)speech--;
        if(!(level() instanceof ServerLevel l))return;
        if(kind()==0){
            if(l.isDay()||l.dimension()!=Level.OVERWORLD){if(getTarget()!=null){setTarget(null);getNavigation().stop();}return;}
            if(tickCount%10==0)setTarget(l.getEntitiesOfClass(Zombie.class,getBoundingBox().inflate(36),z->z.isAlive()).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null));
            LivingEntity t=getTarget();
            if(t instanceof Zombie&&t.isAlive()&&cooldown==0&&distanceTo(t)<18&&hasLineOfSight(t)){
                cooldown=30;l.broadcastEntityEvent(this,(byte)104);
                Vec3 a=getEyePosition(),b=t.getEyePosition();
                for(int i=0;i<16;i++){Vec3 q=a.lerp(b,i/15.0);l.sendParticles(ParticleTypes.CRIT,q.x,q.y,q.z,1,.015,.015,.015,0);}
                t.hurt(damageSources().mobAttack(this),22);playSound(SoundEvents.FIREWORK_ROCKET_BLAST,.75f,1.7f);
                if(speech==0){speech=240;say(l,"Un altro zombie. Proprio quello che ci voleva.");}
            }
        }else{
            if(home!=null&&tickCount%20==0&&distanceToSqr(home.getX()+.5,home.getY(),home.getZ()+.5)>1.2)getNavigation().moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.8);
            Player p=l.getNearestPlayer(this,6);
            if(p==null){lastVisitor=null;}else if(speech==0&&!p.getUUID().equals(lastVisitor)){object(l,p);}
            if(tickCount%100==(kind()==1?20:60)&&pose==0&&speech<150){l.broadcastEntityEvent(this,(byte)103);l.sendParticles(ParticleTypes.CLOUD,getX(),getY()+1.3,getZ(),3,.08,.06,.08,.005);}
        }
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l&&speech==0){if(kind()==0){speech=100;say(l,l.isDay()?"Di giorno mi prendo una pausa.":"Resta lontano dagli zombie.");}else object(l,p);}
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public boolean doHurtTarget(Entity e){return kind()==0&&!level().isDay()&&e instanceof Zombie&&super.doHurtTarget(e);}
    @Override public void handleEntityEvent(byte id){if(id>=102&&id<=104){animation=id-102;pose=id==103?34:18;return;}super.handleEntityEvent(id);}
    public float action(){return pose<=0?0:(float)Math.sin(pose*Math.PI/(animation==1?34:18));}
    public int animation(){return animation;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(home!=null)t.putLong("Home",home.asLong());}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);home=t.contains("Home")?BlockPos.of(t.getLong("Home")):null;}
}''')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!l.isDay()&&p.getRandom().nextInt(18)==0&&l.getEntitiesOfClass(CrossoverGuest.class,p.getBoundingBox().inflate(80),m->m.kind()==0).isEmpty()){
            BlockPos q=Eclipse.spot(p,10,24);if(q!=null){CrossoverGuest m=Noctis.LEON_KENNEDY.get().create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }''')
# Both lawyers stand by the same tea table; don't place an entity inside the stair seats.
a='            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");'
edit('GothicEgg.java',a,'''            if(p.w==25&&p.name.startsWith("Pasticceria")){
                for(int i=0;i<2;i++){
                    CrossoverGuest guest=(i==0?Noctis.PHOENIX_WRIGHT.get():Noctis.MILES_EDGEWORTH.get()).create(l);
                    if(guest!=null){BlockPos q=pos(i==0?4:6,1,8);guest.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+180,0);guest.setHome(q);guest.setPersistenceRequired();if(l.noCollision(guest))l.addFreshEntity(guest);}
                }
            }
'''+a)
# Individually sculpted silhouettes and accessories, independent hair locks, tea cup.
N=256;S=4;W=N*S
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
    part('b','r','body',(0,0,0),(0,0,0),[(-4,0,-2.5,8,10,5,'jacket'),(-4,10,-2,8,2,4,'belt'),(-2,0,-2.8,4,8,1,'shirt')])
    part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-4,8,2,8,'hair')])
    for i in range(7):
        if k==1:part('hair'+str(i),'h','hair'+str(i),(-3+i,-7,1),(-.5,0,(i-3)*.1),[(-1,-2,0,2,3,5+i%3,'hair')])
        else:part('hair'+str(i),'h','hair'+str(i),(-3+i,-7,-3.6),(0,0,(i-3)*(.15 if k==0 else .23)),[(-.7,0,-.7,1,3+(i%3 if k==0 else abs(i-3)),2,'hair')])
    for i,s in enumerate((-1,1)):
        part('lock'+str(i),'h','lock'+str(i),(s*3.5,-6,-.5),(0,0,s*.1),[(-1,0,-1,2,5 if k==2 else 3,3,'hair')])
        part('lapel'+str(i),'b','lapel'+str(i),(s*2.8,0,-2.8),(0,0,s*.29),[(-.8,0,-.3,2,6,1,'lapel')])
        part('arm'+str(i),'r','arm'+str(i),(s*5.1,0,0),(0,0,-s*.08),[(-2,-1,-2,4,9,4,'jacket'),(-1.5,8,-1.5,3,3,3,'face')])
        part('leg'+str(i),'r','leg'+str(i),(s*2.1,12,0),(0,0,0),[(-2,0,-2,4,9,4,'pants'),(-2,9,-3,4,3,5,'boot')])
    if k==0:
        part('tool','arm1','accessory',(0,10,-1),(0,0,0),[(-.6,-1,-3,1,2,4,'boot'),(-.6,1,0,1,2,2,'belt')])
    else:
        part('neck','b','neck',(0,0,-3.2),(0,0,0),[(-.6,1,0,1 if k==1 else 3,5,1,'tie'),(-1.5,0,-.4,3,2,1,'tie')])
        part('cup','arm1','accessory',(0,10,-1.5),(0,0,0),[(-1.5,-2,-2,3,3,3,'cup'),(-1.2,-2.2,-1.7,2,1,2,'tea'),(1.5,-1.5,-1,1,2,1,'cup')])
    if k==0:meshes=[]
    meshes.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    jacket=[(100,79,56),(37,69,117),(130,37,57)][k];hair=[(174,139,83),(35,32,38),(106,100,104)][k];skin=(230,187,157)
    pal={'jacket':jacket,'lapel':tuple(int(a*.8) for a in jacket),'shirt':(37,34,35) if k==0 else (239,236,230),'hair':hair,'face':skin,'belt':(58,46,38),'pants':(43,42,47) if k==0 else jacket,'boot':(35,31,35),'tie':(173,42,104) if k==1 else (235,233,229),'cup':(245,240,225),'tea':(159,100,46)}
    pix=bytearray(W*W*4)
    for x,y,w,h,m,f in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[m];g=.76+.23*math.sin(u*math.pi)+.04*math.cos(v*7)
                if m=='hair':g=.69+.30*math.sin(u*25+v*4)**2
                c=tuple(int(a*g) for a in base)
                if m=='jacket' and f=='front' and (min(u,1-u)<.035 or abs(v-.8)<.025):c=pal['lapel']
                if m=='face' and f=='front' and h==7:
                    for ex in (.26,.74):
                        dx=(u-ex)/.18;dy=(v-.46)/.12
                        if dx*dx+dy*dy<1:c=(65,47,43)
                        if dx*dx+dy*dy<.76:c=(245,239,229)
                        if abs(dx)<.42 and abs(dy)<.8:c=(82,117,149) if k==0 else (86,74,67)
                        if abs(dx)<.17 and abs(dy)<.7:c=(26,25,29)
                        if abs(dx)<1 and abs(v-.28)<.023:c=hair
                    if .40<u<.62 and abs(v-.79)<.02:c=(125,73,62)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    (assets/'textures/entity'/f'{n}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))))+ch(b'IEND',b''))
    (assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
write('CrossoverClient.java','''package it.noctis.magic;
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
public class CrossoverClient{
    static final String[] N={"leon_kennedy","phoenix_wright","miles_edgeworth"};
    static final ModelLayerLocation[] L=new ModelLayerLocation[3];
    static{for(int i=0;i<3;i++)L[i]=new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[i]),"main");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],CrossoverClient::mesh0);e.registerLayerDefinition(L[1],CrossoverClient::mesh1);e.registerLayerDefinition(L[2],CrossoverClient::mesh2);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.LEON_KENNEDY.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.PHOENIX_WRIGHT.get(),c->new Renderer(c,1));e.registerEntityRenderer(Noctis.MILES_EDGEWORTH.get(),c->new Renderer(c,2));}
'''+ '\n'.join(meshes)+'''
    static class Model extends EntityModel<CrossoverGuest>{
        final ModelPart r,b,h;final int k;Model(ModelPart r,int k){this.r=r;this.k=k;b=r.getChild("body");h=r.getChild("head");}
        @Override public void setupAnim(CrossoverGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.action();h.yRot=yaw*.017f;h.xRot=pitch*.012f;b.yRot=0;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;r.getChild("arm"+i).xRot=-w*.6f;r.getChild("leg"+i).xRot=w*.65f;}
            ModelPart arm=r.getChild("arm1");
            if(k==0){arm.xRot-=a*1.5f;arm.getChild("accessory").visible=a>0;}
            else{arm.xRot=-.45f;if(a>0&&e.animation()==1)arm.xRot=-.45f-a*1.6f;
                if(a>0&&e.animation()==0){arm.xRot=-1.7f*a;r.getChild("arm0").xRot=-.3f;b.yRot=a*.14f;}
                arm.getChild("accessory").visible=!(a>0&&e.animation()==0);}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<CrossoverGuest,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.35f);this.k=k;}@Override public ResourceLocation getTextureLocation(CrossoverGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''')
p=assets/'sounds.json';d=json.loads(p.read_text())
for n,pitch in [('phoenix_objection','63'),('miles_objection','37')]:
    wav=assets/'sounds'/f'{n}.wav';subprocess.run(['espeak-ng','-v','it','-p',pitch,'-s','155','-a','170','-w',str(wav),'OBIEZIONE!'],check=True);subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(wav.with_suffix('.ogg'))],check=True);wav.unlink();d[n]={'sounds':[{'name':'noctismagic:'+n}]}
p.write_text(json.dumps(d,indent=2))
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in zip(ids,labels):d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Leon zombie patrol and Ace Attorney tea guests installed')
