"""1.0.4: adult cabaret companions offering a golden-nugget healing service."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8')
    assert a in s,(name,a)
    p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
names=['cabaret_rose','cabaret_noir','cabaret_luna']
regs=['CABARET_ROSE','CABARET_NOIR','CABARET_LUNA']
colors=[('0x93294b','0xe9b2c5'),('0x292039','0xbe7fc9'),('0x203e68','0xe4c082')]
anchor='public static final RegistryObject<EntityType<ScrapThief>> SCRAP_THIEF='
decl=''
for n,r,(a,b) in zip(names,regs,colors):
    decl+=f'public static final RegistryObject<EntityType<CabaretHealer>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<CabaretHealer>of(CabaretHealer::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(8).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{a},{b},new Item.Properties()));\n    '
edit('Noctis.java',anchor,decl+anchor)
anchor='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',anchor,''.join(f'e.put({r}.get(),CabaretHealer.attributes().build());' for r in regs)+anchor)
anchor='e.accept(SCRAP_THIEF_EGG.get());'
edit('Noctis.java',anchor,anchor+''.join(f'e.accept({r}_EGG.get());' for r in regs))
write('CabaretHealer.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
public class CabaretHealer extends PathfinderMob {
    public CabaretHealer(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public int variant(){return getType()==Noctis.CABARET_NOIR.get()?1:getType()==Noctis.CABARET_LUNA.get()?2:0;}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,32).add(Attributes.MOVEMENT_SPEED,.27).add(Attributes.FOLLOW_RANGE,16);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new PanicGoal(this,1.25));goalSelector.addGoal(2,new TemptGoal(this,.85,net.minecraft.world.item.crafting.Ingredient.of(Items.GOLD_NUGGET),false));goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.65));goalSelector.addGoal(5,new RandomLookAroundGoal(this));
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        ItemStack s=p.getItemInHand(h);
        if(!s.is(Items.GOLD_NUGGET)){if(p instanceof ServerPlayer sp&&h==InteractionHand.MAIN_HAND&&s.isEmpty())sp.displayClientMessage(Component.literal("Una pepita d'oro per cure e benedizioni."),true);return InteractionResult.PASS;}
        if(!(p instanceof ServerPlayer sp))return InteractionResult.sidedSuccess(level().isClientSide);
        ServerLevel l=sp.serverLevel();var data=Noctis.data(sp);
        if(data.getLong("cabaretUntil")>l.getGameTime()){sp.displayClientMessage(Component.literal("Torna fra qualche secondo."),true);return InteractionResult.CONSUME;}
        if(!p.getAbilities().instabuild)s.shrink(1);
        p.setHealth(p.getMaxHealth());
        p.addEffect(new MobEffectInstance(MobEffects.REGENERATION,400,0));
        switch(variant()){
            case 0 -> {p.addEffect(new MobEffectInstance(MobEffects.ABSORPTION,2400,1));p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,1200,0));}
            case 1 -> {p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,1800,0));p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,1800,0));}
            default -> {p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,3600,0));p.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE,2400,0));}
        }
        data.putLong("cabaretUntil",l.getGameTime()+600);
        l.sendParticles(ParticleTypes.HEART,getX(),getY()+1.9,getZ(),8,.35,.25,.35,.02);
        l.sendParticles(ParticleTypes.HAPPY_VILLAGER,p.getX(),p.getY()+1,p.getZ(),18,.45,.55,.45,.04);
        playSound(SoundEvents.PLAYER_LEVELUP,.55f,1.3f);
        sp.sendSystemMessage(Component.literal(getDisplayName().getString()+": Ecco le tue cure, tesoro."));
        l.broadcastEntityEvent(this,(byte)81);
        return InteractionResult.CONSUME;
    }
    private int greeting;
    @Override public void handleEntityEvent(byte id){if(id==81){greeting=30;return;}super.handleEntityEvent(id);}
    @Override public void tick(){super.tick();if(greeting>0)greeting--;}
    public float greetingPose(){return greeting>0?(float)Math.sin(greeting*Math.PI/30):0;}
}''')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!l.isDay()&&p.getRandom().nextInt(10)==0&&l.getEntitiesOfClass(CabaretHealer.class,p.getBoundingBox().inflate(64)).size()<2){
            BlockPos q=Eclipse.spot(p,8,20);if(q!=null){
                int k=p.getRandom().nextInt(3);CabaretHealer c=(k==0?Noctis.CABARET_ROSE.get():k==1?Noctis.CABARET_NOIR.get():Noctis.CABARET_LUNA.get()).create(l);
                if(c!=null){c.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(c))l.addFreshEntity(c);}
            }
        }''')
# Face-specific texture islands, reused for three color palettes.
N=128;S=4;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N,(mat,u,v)
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((fx,fy,fw,fh,mat,face))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
part('b','r','body',(0,0,0),(0,0,0),[(-3,-1,-2,6,11,4,'dress'),(-4,0,-3,8,5,5,'dress'),(-4,8,-3,8,4,6,'dress')])
part('sk','b','skirt',(0,10,0),(0,0,0),[(-4.5,0,-3,9,3,6,'skirt'),(-5,2,-3.5,10,2,7,'skirt')])
part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face')])
part('hair','h','hair',(0,-7,0),(0,0,0),[(-4,-1,-3.5,8,2,7,'hair'),(-4,0,2.5,8,10,2,'hair')])
for i,s in enumerate((-1,1)):
    part('lock'+str(i),'h','lock'+str(i),(s*3.5,-6,0),(0,0,s*.08),[(-1,0,-1,2,11,3,'hair')])
    part('bang'+str(i),'h','bang'+str(i),(s*1.5,-7,-3.5),(0,0,-s*.38),[(-1,0,-.5,2,4,1,'hair')])
    part('arm'+str(i),'r','arm'+str(i),(s*4.5,0,0),(0,0,-s*.10),[(-1.5,-1,-1.5,3,4,3,'dress'),(-1,3,-1,2,7,2,'skin')])
    part('leg'+str(i),'r','leg'+str(i),(s*2,12,0),(0,0,0),[(-1.5,0,-1.5,3,9,3,'fishnet'),(-1.5,9,-2,3,3,4,'boot')])
part('gem','b','gem',(0,1,-3.3),(0,0,0),[(-.5,0,-.5,1,2,1,'gold')])
assert cy+rh<=N
write('CabaretClient.java','''package it.noctis.magic;
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
public class CabaretClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"cabaret_healer"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,CabaretClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.CABARET_ROSE.get(),Renderer::new);e.registerEntityRenderer(Noctis.CABARET_NOIR.get(),Renderer::new);e.registerEntityRenderer(Noctis.CABARET_LUNA.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,128,128);}
    static class Model extends EntityModel<CabaretHealer>{
        final ModelPart root,head,body;final ModelPart[] arms=new ModelPart[2],legs=new ModelPart[2],locks=new ModelPart[2];
        Model(ModelPart r){root=r;head=r.getChild("head");body=r.getChild("body");for(int i=0;i<2;i++){arms[i]=r.getChild("arm"+i);legs[i]=r.getChild("leg"+i);locks[i]=head.getChild("lock"+i);}}
        @Override public void setupAnim(CabaretHealer e,float limb,float amount,float age,float yaw,float pitch){
            float g=e.greetingPose();head.yRot=yaw*.01745f;head.xRot=pitch*.01745f;head.zRot=g*.12f;
            body.zRot=(float)Math.sin(limb*.7)*amount*.045f;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float step=(float)Math.cos(limb*.6662+i*Math.PI)*amount;
                arms[i].xRot=-step*.65f-(i==0?g*1.5f:0);arms[i].zRot=-s*.10f+(i==0?g*.18f:0);
                legs[i].xRot=step*.7f;locks[i].zRot=s*.08f+(float)Math.sin(age*.13+i)*.07f;locks[i].xRot=-amount*.12f;
            }
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    }
    static class Renderer extends MobRenderer<CabaretHealer,Model>{
        static final String[] NAMES={"cabaret_rose","cabaret_noir","cabaret_luna"};
        Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.35f);}
        @Override public ResourceLocation getTextureLocation(CabaretHealer e){return new ResourceLocation(Noctis.ID,"textures/entity/"+NAMES[e.variant()]+".png");}
    }
}''')
def mix(a,b,t):return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
for name,skin,hair,dress,eye,lip in [
    ('cabaret_rose',(231,183,158),(143,46,39),(147,25,63),(65,135,100),(183,24,66)),
    ('cabaret_noir',(174,115,91),(25,20,33),(45,24,68),(159,91,174),(105,24,73)),
    ('cabaret_luna',(229,199,180),(217,188,126),(30,65,123),(70,130,191),(190,54,97))]:
    pix=bytearray(W*W*4)
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);edge=min(u,1-u,v,1-v)
                if mat in ('face','skin','fishnet'):
                    c=mix(tuple(max(0,z-35) for z in skin),skin,.55+.45*math.sin(u*math.pi))
                    if mat=='fishnet':
                        a=(u*4+v*9)%1;b=(u*4-v*9)%1
                        if min(a,1-a,b,1-b)<.12 or v<.12:c=(35,28,40)
                    if mat=='face' and face=='front':
                        for ex in (.28,.72):
                            dx=(u-ex)/.18;dy=(v-.43)/.14;d=dx*dx+dy*dy
                            if d<1:c=(43,26,39)
                            if d<.72:c=(248,239,230)
                            if d<.65 and abs(dx)<.42:c=eye
                            if d<.55 and abs(dx)<.16:c=(27,23,34)
                            if (dx+.18)**2+(dy+.32)**2<.06:c=(255,255,247)
                            if abs(dy+.9)<.14 and abs(dx)<.9:c=(37,25,34)
                            if abs(u-ex)<.13 and .23<v<.26:c=hair
                        if .38<u<.62 and abs(v-.78)<.035:c=lip
                        if .43<u<.57 and .79<v<.81:c=mix(lip,(244,153,171),.6)
                elif mat=='hair':c=mix(hair,tuple(min(255,z+65) for z in hair),.20+.45*math.sin(u*math.pi)**2+.18*math.sin(u*38+v*2))
                elif mat in ('dress','skirt'):
                    c=mix(tuple(max(0,z-28) for z in dress),tuple(min(255,z+30) for z in dress),.45+.28*math.cos(u*math.pi*6))
                    if mat=='skirt' and v>.80:c=(37,28,42) if v<.93 else (201,157,89)
                    if mat=='dress' and v>.88:c=(36,28,40)
                elif mat=='boot':c=(29+int(23*math.sin(u*math.pi)),23,34)
                else:c=(220,170,83)
                c=tuple(max(0,min(255,round(z))) for z in c);off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*c,255))
    raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
    (assets/'textures/entity'/f'{name}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
    (assets/'models/item'/f'{name}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in zip(names,('Rosalie','Lilith','Selene')):
        d['entity.noctismagic.'+n]=label+(' - Cortigiana' if lang=='it_it' else ' - Courtesan')
        d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 1.0.4: three adult courtesan NPCs, golden-nugget healing and blessings')
