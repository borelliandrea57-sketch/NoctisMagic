"""1.2.2: Giuseppe, muscular metalhead with endless pogo and Italian voice."""
from pathlib import Path
import sys,json,math,struct,zlib,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<Giuseppe>> GIUSEPPE=ENTITIES.register("giuseppe",()->EntityType.Builder.<Giuseppe>of(Giuseppe::new,MobCategory.CREATURE).sized(.92f,2.1f).clientTrackingRange(10).build(ID+":giuseppe"));
    public static final RegistryObject<Item> GIUSEPPE_EGG=ITEMS.register("giuseppe_spawn_egg",()->new ForgeSpawnEggItem(GIUSEPPE,0x211e24,0x775038,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(GIUSEPPE.get(),Giuseppe.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(GIUSEPPE_EGG.get());')
a='static final RegistryObject<SoundEvent> MOONWALK_SHOUT='
edit('FallenEncounter.java',a,'''static final RegistryObject<SoundEvent> GIUSEPPE_SHOUT=SOUNDS.register("giuseppe_shout",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"giuseppe_shout")));
    '''+a)
write('Giuseppe.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class Giuseppe extends PathfinderMob{
    private int speech=80;
    static final String[] LINES={"NON HO SOLDI!","Frate', io vengo per il pogo, non per consumare.","Non ho soldi ma ho rabbia.","Se parte il breakdown io mi butto.","Ho finito i soldi, ma il pezzo spacca!"};
    public Giuseppe(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,100).add(Attributes.ARMOR,5).add(Attributes.ATTACK_DAMAGE,9).add(Attributes.MOVEMENT_SPEED,.30).add(Attributes.KNOCKBACK_RESISTANCE,.45);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new LookAtPlayerGoal(this,Player.class,7));goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.6));}
    void shout(ServerLevel l,int i){
        speech=180+random.nextInt(160);
        NpcDialogue.say(l,Component.literal("Giuseppe: "+LINES[i]));
        if(i==0)playSound(FallenEncounter.GIUSEPPE_SHOUT.get(),1,.88f+random.nextFloat()*.12f);
        l.sendParticles(ParticleTypes.NOTE,getX(),getY()+2,getZ(),4,.3,.25,.3,.02);
    }
    @Override public void tick(){
        super.tick();if(speech>0)speech--;
        if(!(level() instanceof ServerLevel l)||!isAlive())return;
        if(onGround()&&!isInWater()&&tickCount%11==0){
            double a=Math.toRadians(getYRot())+Math.PI/2;double side=(tickCount/11%2==0?.075:-.075);
            Vec3 jump=new Vec3(Math.sin(a)*side,.24,Math.cos(a)*side);
            if(l.noCollision(this,getBoundingBox().move(jump)))setDeltaMovement(getDeltaMovement().add(jump));
        }
        if(speech==0&&l.getNearestPlayer(this,16)!=null)shout(l,random.nextInt(3)==0?random.nextInt(LINES.length):0);
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        ItemStack s=p.getItemInHand(h);
        if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET)&&!s.is(Items.GOLD_INGOT)&&!s.isEdible())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l){
            if(speech>140)return InteractionResult.CONSUME;
            if(!s.isEmpty()){if(!p.getAbilities().instabuild)s.shrink(1);speech=220;
                NpcDialogue.say(l,Component.literal("Giuseppe: GRANDE! Almeno oggi non resto a secco!"));
                l.sendParticles(ParticleTypes.HEART,getX(),getY()+2,getZ(),5,.3,.2,.3,.02);
            }else shout(l,0);
        }return InteractionResult.sidedSuccess(level().isClientSide);
    }
}''')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!l.isDay()&&p.getRandom().nextInt(18)==0&&l.getEntitiesOfClass(Giuseppe.class,p.getBoundingBox().inflate(64)).isEmpty()){
            BlockPos q=Eclipse.spot(p,10,22);if(q!=null){Giuseppe g=Noctis.GIUSEPPE.get().create(l);if(g!=null){g.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(g))l.addFreshEntity(g);}}
        }''')
# Mesh, independent hair curls, broad chest, tapered waist, biceps and rolled leather sleeves.
N=256;S=4;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
    for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,mat,f))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
part('b','r','body',(0,0,0),(0,0,0),[(-5,-1,-3,10,7,6,'leather'),(-3.5,6,-2.5,7,6,5,'shirt'),(-4,10,-3,8,2,6,'belt')])
part('h','b','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-3.5,8,2,7,'hair')])
for i,side in enumerate((-1,1)):
    part('lapel'+str(i),'b','lapel'+str(i),(side*3.2,-1,-3),(0,0,side*.25),[(-1,0,-.5,2,7,1,'lapel')])
    part('arm'+str(i),'r','arm'+str(i),(side*6,0,0),(0,0,-side*.2),[(-2.5,-1,-2.5,5,4,5,'leather'),(-2.2,3,-2,4,4,4,'tattoo')])
    part('fore'+str(i),'arm'+str(i),'fore',(0,7,0),(-.35,0,0),[(-1.7,0,-1.7,3,4,3,'tattoo'),(-1.5,4,-1.5,3,2,3,'skin')])
    part('leg'+str(i),'r','leg'+str(i),(side*2.2,12,0),(0,0,0),[(-2,0,-2,4,9,4,'denim'),(-2,9,-3,4,3,5,'boot')])
    part('lock'+str(i),'h','lock'+str(i),(side*3.5,-6,0),(0,0,side*.12),[(-1,0,-1,2,6,3,'hair')])
    part('curl'+str(i),'lock'+str(i),'curl',(0,5,0),(0,0,-side*.35),[(-1,0,-1,2,7,2,'hair')])
for j in range(9):
    part('curl'+str(j)+'b','h','back'+str(j),(-3.7+j*.9,-6,2.8),(0,0,(j-4)*.06),[(-.75,0,-.5,2,7+j%3,2,'hair')])
    part('tip'+str(j),'curl'+str(j)+'b','tip',(0,7+j%3,0),(0,0,.32 if j%2 else -.32),[(-.8,0,-.5,2,6,2,'hair')])
for j in range(5):part('bang'+str(j),'h','bang'+str(j),(-3+j*1.5,-7.5,-3.4),(0,0,(j-2)*.23),[(-.8,0,-.6,2,3+j%2,1,'hair')])
write('GiuseppeClient.java','''package it.noctis.magic;
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
public class GiuseppeClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"giuseppe"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,GiuseppeClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.GIUSEPPE.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<Giuseppe>{
        final ModelPart r,b,h;Model(ModelPart r){this.r=r;b=r.getChild("body");h=b.getChild("head");}
        @Override public void setupAnim(Giuseppe e,float limb,float amount,float age,float yaw,float pitch){
            float pogo=(float)Math.sin(age*.58f),beat=(float)Math.sin(age*.84f);
            h.xRot=.18f+beat*.5f;h.yRot=yaw*.008f;h.zRot=pogo*.16f;b.xRot=.12f+beat*.09f;b.zRot=pogo*.10f;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;
                ModelPart a=r.getChild("arm"+i);a.xRot=-.55f+beat*s*.55f-w*.3f;a.zRot=-s*(.25f+.22f*pogo);a.getChild("fore").xRot=-.8f+beat*.22f;
                r.getChild("leg"+i).xRot=w*.6f+s*pogo*.20f;
                h.getChild("lock"+i).xRot=-beat*.42f;h.getChild("lock"+i).getChild("curl").zRot=s*(.22f+pogo*.18f);}
            for(int j=0;j<9;j++){ModelPart p=h.getChild("back"+j);p.xRot=-beat*.5f+(float)Math.sin(age*.42f+j*.5f)*.12f;p.getChild("tip").xRot=(float)Math.sin(age*.66f+j*.32f)*.28f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<Giuseppe,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.48f);}@Override public ResourceLocation getTextureLocation(Giuseppe e){return new ResourceLocation(Noctis.ID,"textures/entity/giuseppe.png");}}
}''')
palette={'leather':(32,30,35),'lapel':(62,58,63),'shirt':(25,24,28),'belt':(47,38,34),'face':(216,166,130),'skin':(213,161,126),'tattoo':(207,156,119),'hair':(104,64,40),'denim':(46,47,58),'boot':(25,24,27)}
pix=bytearray(W*W*4)
for x,y,w,h,mat,face in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);base=palette[mat];g=.73+.24*math.sin(u*math.pi)+.04*math.cos(v*9)
            c=tuple(int(a*g) for a in base)
            if mat=='hair':
                g=.65+.35*math.sin(u*29+math.sin(v*13)*2.3)**2;c=tuple(int(a*g) for a in base)
            if mat=='tattoo':
                # intertwined tribal lines and a skull motif on the outer bicep
                if .08<v<.9 and (abs(math.sin(u*15+v*10))<.25 or abs(math.sin(u*22-v*12))<.13):c=(54,49,52)
                if face in ('front','left','right') and ((u-.5)/.23)**2+((v-.44)/.20)**2<1:
                    c=(43,43,47)
                    if .32<v<.44 and (.36<u<.46 or .54<u<.64):c=base
                    if .51<v<.60 and .42<u<.58:c=base
            if mat in ('leather','lapel') and (min(u,1-u)<.06 or abs(v-.83)<.025):c=(107,105,110)
            if mat=='shirt' and face=='front' and .2<u<.8 and .2<v<.55 and abs(math.sin(u*18+v*19))<.3:c=(172,174,181)
            if mat=='face' and face=='front':
                for ex in (.26,.74):
                    dx=(u-ex)/.17;dy=(v-.46)/.10
                    if dx*dx+dy*dy<1:c=(44,30,28)
                    if dx*dx+dy*dy<.72:c=(241,229,213)
                    if abs(dx)<.4 and abs(dy)<.7:c=(86,58,36)
                    if abs(dx)<.16 and abs(dy)<.65:c=(24,21,23)
                    if abs(dx)<1 and abs(v-.31)<.025:c=(70,42,31)
                if .25<u<.75 and v>.72:c=(103,66,44) if abs(math.sin(u*60+v*20))<.6 else c
                if .39<u<.61 and abs(v-.79)<.02:c=(93,46,40)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
(assets/'textures/entity/giuseppe.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
(assets/'models/item/giuseppe_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
wav=assets/'sounds/giuseppe_shout.wav'
subprocess.run(['espeak-ng','-v','it','-p','39','-s','145','-a','160','-w',str(wav),'NON HO SOLDI!'],check=True)
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(wav.with_suffix('.ogg'))],check=True);wav.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text());d['giuseppe_shout']={'sounds':[{'name':'noctismagic:giuseppe_shout'}]};p.write_text(json.dumps(d,indent=2))
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.giuseppe']='Giuseppe';d['item.noctismagic.giuseppe_spawn_egg']='Uovo generatore: Giuseppe' if lang=='it_it' else 'Giuseppe Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Giuseppe metalhead, muscles, tattoos, moving curls and Italian shout installed')
