"""1.3.0: Oscar and Andre, paired non-damaging fencing practice."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
ids=['lady_oscar','andre_grandier'];labels=['Lady Oscar','André Grandier']
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
decl=''
for n,c,d in zip(ids,['0xe8cf85','0x47352c'],['0x254c83','0x486846']):
    r=n.upper();decl+=f'public static final RegistryObject<EntityType<Fencer>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<Fencer>of(Fencer::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{c},{d},new Item.Properties()));\n    '
edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,''.join(f'e.put({n.upper()}.get(),Fencer.attributes().build());' for n in ids)+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({n.upper()}_EGG.get());' for n in ids))
(java/'Fencer.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Fencer extends PathfinderMob{
    UUID partner;int beat=45,pose,action,speech;
    public Fencer(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setPersistenceRequired();}
    public boolean oscar(){return getType()==Noctis.LADY_OSCAR.get();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,80).add(Attributes.MOVEMENT_SPEED,.29).add(Attributes.ARMOR,6);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));}
    @Override public boolean doHurtTarget(Entity e){return false;}
    @Override public boolean hurt(DamageSource s,float damage){if(s.getEntity() instanceof Fencer)return false;return super.hurt(s,damage);}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}
    void pair(ServerLevel l){
        if(partner!=null)return;
        for(Fencer q:l.getEntitiesOfClass(Fencer.class,getBoundingBox().inflate(12),v->v!=this&&v.oscar()!=oscar()&&v.partner==null&&v.isAlive())){
            partner=q.getUUID();q.partner=getUUID();return;
        }
        for(int i=0;i<8;i++){
            double a=i*Math.PI/4;BlockPos p=BlockPos.containing(getX()+Math.cos(a)*2.7,getY(),getZ()+Math.sin(a)*2.7);
            if(!l.hasChunkAt(p)||!l.isEmptyBlock(p)||!l.isEmptyBlock(p.above())||!l.getBlockState(p.below()).isFaceSturdy(l,p.below(),Direction.UP))continue;
            Fencer q=(oscar()?Noctis.ANDRE_GRANDIER.get():Noctis.LADY_OSCAR.get()).create(l);if(q==null)return;
            q.moveTo(p.getX()+.5,p.getY(),p.getZ()+.5);
            if(l.noCollision(q)){q.partner=getUUID();if(l.addFreshEntity(q)){partner=q.getUUID();return;}}
        }
    }
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(speech>0)speech--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        if(partner==null&&tickCount%20==0)pair(l);
        if(partner==null||!(l.getEntity(partner) instanceof Fencer q)||!q.isAlive()){getNavigation().stop();return;}
        if(q.partner==null)q.partner=getUUID();
        getLookControl().setLookAt(q,40,40);
        double d=distanceTo(q);
        if(d>3.6){if(oscar()||d>6)getNavigation().moveTo(q,1.05);else getNavigation().stop();return;}
        getNavigation().stop();
        Vec3 diff=q.position().subtract(position());
        if(d<1.65&&d>.05&&onGround()){Vec3 back=new Vec3(-diff.x,0,-diff.z).normalize().scale(.065);if(l.noCollision(this,getBoundingBox().move(back)))setDeltaMovement(getDeltaMovement().add(back));}
        if(!oscar())return;
        if(!hasLineOfSight(q)||!onGround()||!q.onGround())return;
        if(--beat>0)return;beat=32+random.nextInt(23);
        // Synchronized fencing poses only: no damage source, knockback or melee goals.
        boolean oscarAttacks=random.nextBoolean();
        l.broadcastEntityEvent(this,(byte)(oscarAttacks?105:106));l.broadcastEntityEvent(q,(byte)(oscarAttacks?106:105));
        Vec3 mid=position().lerp(q.position(),.5).add(0,1.25,0);
        l.sendParticles(ParticleTypes.ELECTRIC_SPARK,mid.x,mid.y,mid.z,12,.15,.15,.15,.04);
        l.playSound(null,BlockPos.containing(mid),SoundEvents.ANVIL_LAND,net.minecraft.sounds.SoundSource.NEUTRAL,.22f,1.85f);
        if(speech==0&&l.getNearestPlayer(this,12)!=null&&random.nextInt(6)==0){speech=260;say(l,"En garde, André!");q.say(l,"Non ti risparmierò una parata, Oscar.");}
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l&&speech==0){speech=100;say(l,oscar()?"E' soltanto un allenamento. André sa il fatto suo.":"Oscar, non abbassare mai la guardia.");}
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==105||id==106){pose=22;action=id-105;return;}super.handleEntityEvent(id);}
    public float motion(){return pose<=0?0:(float)Math.sin(pose*Math.PI/22);}
    public boolean parry(){return action==1;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(partner!=null)t.putUUID("Partner",partner);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);partner=t.hasUUID("Partner")?t.getUUID("Partner"):null;}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(l.isDay()&&p.getRandom().nextInt(24)==0&&l.getEntitiesOfClass(Fencer.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){Fencer f=Noctis.LADY_OSCAR.get().create(l);if(f!=null){f.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(f))l.addFreshEntity(f);}}
        }''')
N=256;S=4;W=N*S;meshes=[]
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
    part('b','r','body',(0,0,0),(0,0,0),[(-4,0,-2.5,8,8,5,'coat'),(-3.5,8,-2,7,3,4,'coat'),(-2,0,-2.8,4,7,1,'shirt'),(-4,10,-2.6,8,2,5,'belt')])
    part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-4,8,2,8,'hair')])
    for i in range(7):
        part('bang'+str(i),'h','bang'+str(i),(-3+i,-7.5,-3.5),(0,0,(i-3)*.14),[(-.7,0,-.7,1,3+i%3,2,'hair')])
        if k==0:
            part('back'+str(i),'h','back'+str(i),(-3+i,-6,3),(0,0,(i-3)*.09),[(-.8,0,-.6,2,10+i%3,3,'hair')])
            part('tip'+str(i),'back'+str(i),'tip',(0,10+i%3,0),(0,0,.26 if i%2 else -.26),[(-.7,0,-.7,1,4,2,'hair')])
    for i,s in enumerate((-1,1)):
        part('lock'+str(i),'h','lock'+str(i),(s*3.7,-6,-.5),(0,0,s*.14),[(-1,0,-1,2,9 if k==0 else 5,3,'hair')])
        part('lapel'+str(i),'b','lapel'+str(i),(s*2.7,0,-2.8),(0,0,s*.22),[(-.7,0,-.4,1,8,1,'gold' if k==0 else 'lapel')])
        part('tail'+str(i),'b','tail'+str(i),(s*2.5,9,2),(.1,0,s*.12),[(-2,0,-1,4,7,2,'coat')])
        part('arm'+str(i),'r','arm'+str(i),(s*5,0,0),(0,0,-s*.1),[(-2,-1,-2,4,8,4,'coat'),(-2,7,-2,4,2,4,'gold' if k==0 else 'shirt'),(-1.5,9,-1.5,3,2,3,'face')])
        if k==0:part('ep'+str(i),'arm'+str(i),'ep',(0,0,0),(0,0,0),[(-2.5,-2,-2.3,5,2,5,'gold')])
        part('leg'+str(i),'r','leg'+str(i),(s*2.1,12,0),(0,0,0),[(-2,0,-2,4,6,4,'pants'),(-2,6,-2,4,6,4,'boot'),(-2,11,-3,4,1,5,'boot')])
    part('rapier','arm1','rapier',(0,10,-1),(-1.4,0,0),[(-.5,0,-.5,1,3,1,'belt'),(-2.5,3,-1,5,1,2,'gold'),(-.4,4,-.4,1,14,1,'steel')])
    meshes.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    pal={'coat':(39,73,127) if k==0 else (69,87,64),'lapel':(47,63,43),'gold':(210,166,70),'shirt':(237,232,218),'face':(235,194,173),'hair':(233,207,137) if k==0 else (76,52,37),'belt':(65,45,35),'pants':(226,222,204) if k==0 else (121,110,87),'boot':(39,34,32),'steel':(190,204,221)}
    pix=bytearray(W*W*4)
    for x,y,w,h,m,f in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[m];g=.76+.23*math.sin(u*math.pi)+.04*math.cos(v*9)
                if m=='hair':g=.68+.31*math.sin(u*32+math.sin(v*10)*1.6)**2
                if m in ('steel','gold'):g=.57+.43*math.exp(-((u-.34)/.25)**2)
                c=tuple(int(a*g) for a in base)
                if m=='coat' and f=='front' and k==0 and (.18<u<.26 or .74<u<.82) and abs((v*5)%1-.5)<.15:c=pal['gold']
                if m=='face' and f=='front' and h==7:
                    for ex in (.26,.74):
                        dx=(u-ex)/.19;dy=(v-.46)/.14
                        if dx*dx+dy*dy<1:c=(78,56,47)
                        if dx*dx+dy*dy<.76:c=(245,241,233)
                        if abs(dx)<.43 and abs(dy)<.8:c=(81,133,183) if k==0 else (80,104,66)
                        if abs(dx)<.17 and abs(dy)<.7:c=(29,31,40)
                        if (dx+.17)**2+(dy+.24)**2<.07:c=(255,255,255)
                    if .4<u<.62 and abs(v-.79)<.022:c=(141,76,77)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    (assets/'textures/entity'/f'{n}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))))+ch(b'IEND',b''))
    (assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
(java/'FencerClient.java').write_text('''package it.noctis.magic;
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
public class FencerClient{
    static final String[] N={"lady_oscar","andre_grandier"};
    static final ModelLayerLocation[] L={new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[0]),"main"),new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[1]),"main")};
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],FencerClient::mesh0);e.registerLayerDefinition(L[1],FencerClient::mesh1);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.LADY_OSCAR.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.ANDRE_GRANDIER.get(),c->new Renderer(c,1));}
'''+ '\n'.join(meshes)+'''
    static class Model extends EntityModel<Fencer>{
        final ModelPart r,b,h;final int k;Model(ModelPart r,int k){this.r=r;this.k=k;b=r.getChild("body");h=r.getChild("head");}
        @Override public void setupAnim(Fencer e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.motion(),breath=(float)Math.sin(age*.09)*.04f;
            h.yRot=yaw*.017f;h.xRot=pitch*.01f;b.yRot=(e.parry()?-.25f:.27f)*a;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;ModelPart arm=r.getChild("arm"+i),leg=r.getChild("leg"+i);arm.xRot=-w*.45f+(i==1?-.55f: .2f);arm.zRot=i==1?-.15f:.15f;leg.xRot=w*.6f+(i==1?-a*.32f:a*.19f);b.getChild("tail"+i).xRot=.1f+amount*.2f+a*.16f;h.getChild("lock"+i).xRot=breath+a*.15f;}
            ModelPart arm=r.getChild("arm1");arm.xRot-=a*(e.parry()?.55f:1.05f);arm.zRot+=a*(e.parry()?.65f:-.1f);arm.getChild("rapier").xRot=-1.4f+a*(e.parry()?1.1f:.6f);
            if(k==0)for(int i=0;i<7;i++){ModelPart q=h.getChild("back"+i);q.xRot=amount*.2f+a*.16f+(float)Math.sin(age*.12+i)*.05f;q.getChild("tip").xRot=breath+a*.16f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<Fencer,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.35f);this.k=k;}@Override public ResourceLocation getTextureLocation(Fencer e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''',encoding='utf-8')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in zip(ids,labels):d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Lady Oscar and Andre: paired safe fencing animations, rapier mesh and dialogue installed')
