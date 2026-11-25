"""1.3.1: Pochita companion, petting, and five wolf variants."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
    p.parent.mkdir(parents=True,exist_ok=True)
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
breeds=[('arctic_wolf','Lupo artico','Arctic wolf',(225,229,235),(174,183,193)),('black_wolf','Lupo nero','Black wolf',(38,39,45),(71,73,80)),('red_wolf','Lupo rosso','Red wolf',(157,92,55),(223,173,116)),('timber_wolf','Lupo grigio dei boschi','Timber wolf',(108,103,94),(181,171,149)),('silver_wolf','Lupo argentato','Silver wolf',(142,153,169),(222,225,232))]
decl='''public static final RegistryObject<EntityType<Pochita>> POCHITA=ENTITIES.register("pochita",()->EntityType.Builder.<Pochita>of(Pochita::new,MobCategory.CREATURE).sized(.8f,.85f).clientTrackingRange(10).build(ID+":pochita"));
    public static final RegistryObject<Item> POCHITA_EGG=ITEMS.register("pochita_spawn_egg",()->new ForgeSpawnEggItem(POCHITA,0xe67a33,0x28252b,new Item.Properties()));
    '''
for n,it,en,c,d in breeds:
    r=n.upper();a=int.from_bytes(bytes(c),'big');b=int.from_bytes(bytes(d),'big')
    decl+=f'public static final RegistryObject<EntityType<BreedWolf>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<BreedWolf>of(BreedWolf::new,MobCategory.CREATURE).sized(.65f,.85f).clientTrackingRange(10).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{a},{b},new Item.Properties()));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG=';edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(POCHITA.get(),Pochita.attributes().build());'+''.join(f'e.put({n.upper()}.get(),net.minecraft.world.entity.animal.Wolf.createAttributes().build());' for n,*_ in breeds)+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(POCHITA_EGG.get());'+''.join(f'e.accept({n.upper()}_EGG.get());' for n,*_ in breeds))
write('Pochita.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
public class Pochita extends TamableAnimal{
    int cuddle,saw;
    public Pochita(EntityType<? extends TamableAnimal> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,40).add(Attributes.ATTACK_DAMAGE,9).add(Attributes.MOVEMENT_SPEED,.31).add(Attributes.FOLLOW_RANGE,24);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));goalSelector.addGoal(2,new MeleeAttackGoal(this,1.15,true));goalSelector.addGoal(3,new FollowOwnerGoal(this,1.2,4,1.5f,false));goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(5,new LookAtPlayerGoal(this,Player.class,8));targetSelector.addGoal(1,new OwnerHurtByTargetGoal(this));targetSelector.addGoal(2,new OwnerHurtTargetGoal(this));}
    @Override public boolean isFood(ItemStack s){return s.is(ItemTags.LOGS)||s.is(ItemTags.PLANKS);}
    @Override public boolean wantsToAttack(LivingEntity t,LivingEntity o){return Eclipse.hostile(t);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        ItemStack s=p.getItemInHand(h);
        if(!isTame()&&isFood(s)){if(level() instanceof ServerLevel l){if(!p.getAbilities().instabuild)s.shrink(1);if(random.nextInt(3)==0||p.getAbilities().instabuild){tame(p);setPersistenceRequired();setHealth(getMaxHealth());l.broadcastEntityEvent(this,(byte)7);}else l.broadcastEntityEvent(this,(byte)6);}return InteractionResult.sidedSuccess(level().isClientSide);}
        if(isTame()&&isOwnedBy(p)){
            if(isFood(s)){if(!level().isClientSide){if(!p.getAbilities().instabuild)s.shrink(1);heal(6);}return InteractionResult.sidedSuccess(level().isClientSide);}
            if(s.isEmpty()){if(level() instanceof ServerLevel l){if(p.isShiftKeyDown()){setOrderedToSit(!isOrderedToSit());getNavigation().stop();setTarget(null);}else if(cuddle==0){cuddle=40;l.broadcastEntityEvent(this,(byte)107);l.sendParticles(ParticleTypes.HEART,getX(),getY()+.7,getZ(),9,.25,.25,.25,.02);playSound(SoundEvents.WOLF_AMBIENT,.6f,1.65f);}}return InteractionResult.sidedSuccess(level().isClientSide);}
        }return InteractionResult.PASS;
    }
    @Override public boolean doHurtTarget(Entity e){if(!(e instanceof LivingEntity t)||!Eclipse.hostile(t))return false;boolean hit=super.doHurtTarget(e);if(hit&&level() instanceof ServerLevel l){l.broadcastEntityEvent(this,(byte)108);l.sendParticles(ParticleTypes.CRIT,e.getX(),e.getY()+.7,e.getZ(),8,.3,.3,.3,.1);playSound(SoundEvents.STONE_BREAK,.5f,1.4f);}return hit;}
    @Override public void tick(){super.tick();if(cuddle>0)cuddle--;if(saw>0)saw--;}
    @Override public void handleEntityEvent(byte id){if(id==107){cuddle=40;return;}if(id==108){saw=15;return;}super.handleEntityEvent(id);}
    public float cuddling(){return cuddle<=0?0:(float)Math.sin(cuddle*Math.PI/40);}
    public float sawing(){return saw<=0?0:(float)Math.sin(saw*Math.PI/15);}
    @Override public AgeableMob getBreedOffspring(ServerLevel l,AgeableMob a){return null;}
    @Override public boolean canMate(Animal a){return false;}
}''')
write('PetCare.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class PetCare{
    @SubscribeEvent public static void pet(PlayerInteractEvent.EntityInteract e){
        if(e.getHand()!=InteractionHand.MAIN_HAND||!e.getItemStack().isEmpty()||e.getEntity().isShiftKeyDown())return;
        if(e.getTarget() instanceof Familiar f&&f.getType()==Noctis.UMBREON.get()&&f.isTame()&&f.isOwnedBy(e.getEntity())){
            e.setCanceled(true);e.setCancellationResult(InteractionResult.sidedSuccess(e.getLevel().isClientSide));
            if(e.getLevel() instanceof ServerLevel l&&f.getPersistentData().getLong("PetNext")<=l.getGameTime()){
                f.getPersistentData().putLong("PetNext",l.getGameTime()+40);l.broadcastEntityEvent(f,(byte)109);l.sendParticles(ParticleTypes.HEART,f.getX(),f.getY()+.8,f.getZ(),8,.25,.25,.25,.02);f.playSound(SoundEvents.FOX_AMBIENT,.45f,1.25f);
            }
        }
    }
}''')
# Umbreon previously had no petting pose. Fennekin already has heart, sound and animated cuddle.
edit('Familiar.java','private int moonAttack=0;','private int moonAttack=0;private int petPose=0;')
edit('Familiar.java','if(moonAttack>0)moonAttack--;','if(moonAttack>0)moonAttack--;if(petPose>0)petPose--;')
edit('Familiar.java','if(id==74){moonAttack=12;return;}','if(id==109){petPose=40;return;}if(id==74){moonAttack=12;return;}')
edit('Familiar.java','public float moonAttackPose(float partial)','public float petting(){return petPose<=0?0:(float)Math.sin(petPose*Math.PI/40);}\n    public float moonAttackPose(float partial)')
# Shift click explicitly controls sit, independent of other familiar interaction changes.
edit('PetCare.java','||e.getEntity().isShiftKeyDown()','')
edit('PetCare.java','if(e.getLevel() instanceof ServerLevel l&&f.getPersistentData().getLong("PetNext")<=l.getGameTime()){','if(e.getLevel() instanceof ServerLevel l&&e.getEntity().isShiftKeyDown()){f.setOrderedToSit(!f.isOrderedToSit());f.getNavigation().stop();f.setTarget(null);return;}\n            if(e.getLevel() instanceof ServerLevel l&&f.getPersistentData().getLong("PetNext")<=l.getGameTime()){')
edit('UmbreonRenderer.java','tail.yRot=(float)Math.sin(age*(amount>.25?.25:.11))*(sit?.18f:.32f);','tail.yRot=(float)Math.sin(age*(amount>.25?.25:.11))*(sit?.18f:.32f);float pet=e.petting();head.zRot=pet*.25f;head.xRot-=pet*.16f;tail.yRot+=(float)Math.sin(age*.85f)*pet*.7f;')
write('BreedWolf.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraft.world.level.Level;
public class BreedWolf extends Wolf{
    public BreedWolf(EntityType<? extends Wolf> t,Level l){super(t,l);}
    @Override public Wolf getBreedOffspring(ServerLevel l,AgeableMob other){
        Wolf pup=(Wolf)getType().create(l);
        if(pup!=null&&getOwnerUUID()!=null){pup.setOwnerUUID(getOwnerUUID());pup.setTame(true);}
        return pup;
    }
}''')
# Rare naturally occurring companions, with region-appropriate wolf varieties.
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(l.isDay()&&p.getRandom().nextInt(20)==0&&l.getEntitiesOfClass(Pochita.class,p.getBoundingBox().inflate(64)).isEmpty()){
            BlockPos q=Eclipse.spot(p,10,24);if(q!=null){Pochita m=Noctis.POCHITA.get().create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }
        if(l.isDay()&&p.getRandom().nextInt(12)==0&&l.getEntitiesOfClass(BreedWolf.class,p.getBoundingBox().inflate(64)).size()<3){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){
                var biome=l.getBiome(q);var type=biome.is(net.minecraft.world.level.biome.Biomes.SNOWY_TAIGA)||biome.is(net.minecraft.world.level.biome.Biomes.SNOWY_PLAINS)?Noctis.ARCTIC_WOLF.get():biome.is(net.minecraft.world.level.biome.Biomes.SAVANNA)?Noctis.RED_WOLF.get():java.util.List.of(Noctis.BLACK_WOLF.get(),Noctis.TIMBER_WOLF.get(),Noctis.SILVER_WOLF.get(),Noctis.RED_WOLF.get()).get(p.getRandom().nextInt(4));
                BreedWolf m=type.create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}
            }
        }''')
# Pochita: custom rounded body, blade teeth, handles and tail with moving parts.
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
part('b','r','body',(0,17,1),(0,0,0),[(-6,-6,-6,12,10,12,'orange'),(-7,-4,-5,14,7,10,'orange'),(-5,-7,-4,10,3,8,'orange'),(-5,2,-4,10,3,8,'orange')])
part('h','r','head',(0,15,-5),(0,0,0),[(-6,-6,-5,12,10,8,'face'),(-7,-3,-4,14,6,6,'orange'),(-4,-7,-3,8,2,6,'orange')])
part('muzzle','h','muzzle',(0,1,-5),(0,0,0),[(-3,-2,-2,6,3,3,'orange'),(-2,1,-1,4,2,1,'mouth'),(-1.5,2,-2,3,2,1,'tongue')])
part('saw','h','saw',(0,-4,-4),(-.6,0,0),[(-.8,-11,-1,2,12,2,'steel'),(-.9,-12,-1,2,1,2,'steel')])
for i in range(6):
    for s in (-1,1):part(f'tooth{i}{s+1}','saw',f'tooth{i}_{s}',(0,-1-i*2,s*1.2),(.4*s,0,0),[(-.7,-1,-.6,1,2,1,'dark')])
part('handle','h','handle',(0,-5,0),(0,0,0),[(-5,-3,1,10,1,2,'dark'),(-5,-2,1,1,4,2,'dark'),(4,-2,1,1,4,2,'dark')])
part('tail','b','tail',(0,-1,6),(-.4,0,0),[(-.5,-1,0,1,1,5,'dark'),(-1.5,-2,4,3,1,2,'dark'),(-1.5,0,4,3,1,2,'dark')])
for i,s in enumerate((-1,1)):
    for j,z in enumerate((-4,5)):
        part(f'leg{i}{j}','r',f'leg{i}{j}',(s*4.5,20,z),(0,0,0),[(-1.5,0,-1.5,3,4,3,'orange'),(-1.5,3,-2,3,1,4,'orange')])
write('PochitaClient.java','''package it.noctis.magic;
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
public class PochitaClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"pochita"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,PochitaClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.POCHITA.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<Pochita>{
        final ModelPart r,b,h;Model(ModelPart r){this.r=r;b=r.getChild("body");h=r.getChild("head");}
        @Override public void setupAnim(Pochita e,float limb,float amount,float age,float yaw,float pitch){
            float c=e.cuddling(),a=e.sawing(),breath=(float)Math.sin(age*.12)*.035f;
            b.xScale=1+breath;b.zScale=1+breath;h.yRot=yaw*.012f;h.xRot=pitch*.012f-c*.22f;h.zRot=c*.28f;
            h.getChild("saw").xRot=-.6f+(float)Math.sin(age*2.3f)*a*.08f;
            b.getChild("tail").yRot=(float)Math.sin(age*(c>0?.85f:.17f))*(.2f+c*.65f);
            for(int i=0;i<2;i++)for(int j=0;j<2;j++){ModelPart p=r.getChild("leg"+i+j);p.xRot=e.isInSittingPose()?(j==1?-1.1f:.05f):(float)Math.cos(limb*.666+(i+j)*Math.PI)*amount*.8f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<Pochita,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.4f);}@Override protected void scale(Pochita e,PoseStack p,float partial){p.scale(.92f,.92f,.92f);}@Override public ResourceLocation getTextureLocation(Pochita e){return new ResourceLocation(Noctis.ID,"textures/entity/pochita.png");}}
}''')
pal={'orange':(239,120,49),'face':(250,140,60),'mouth':(94,43,40),'tongue':(241,137,136),'steel':(192,200,214),'dark':(36,37,44)}
pix=bytearray(W*W*4)
for x,y,w,h,m,f in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);base=pal[m];g=.69+.29*math.sin(u*math.pi)+.08*math.sin(v*math.pi)
            if m=='steel':g=.55+.44*math.exp(-((u-.37)/.24)**2)
            c=tuple(int(a*g) for a in base)
            if m=='face' and f=='front':
                for ex in (.23,.77):
                    dx=(u-ex)/.19;dy=(v-.38)/.25;d=dx*dx+dy*dy
                    if d<1:c=(252,247,233)
                    if d<.79:c=(25,23,24)
                    if (dx+.22)**2+(dy+.31)**2<.1:c=(255,255,255)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
png(assets/'textures/entity/pochita.png',W,W,pix)
# Vanilla WolfRenderer retains sitting, shaking, wet fur and colored collar layers.
renderers=''.join(f'e.registerEntityRenderer(Noctis.{n.upper()}.get(),c->new VariantRenderer(c,"{n}"));' for n,*_ in breeds)
write('BreedWolfClient.java','''package it.noctis.magic;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class BreedWolfClient{
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){'''+renderers+'''}
    static class VariantRenderer extends WolfRenderer{
        final ResourceLocation tex;VariantRenderer(EntityRendererProvider.Context c,String n){super(c);tex=new ResourceLocation(Noctis.ID,"textures/entity/"+n+".png");}
        @Override public ResourceLocation getTextureLocation(Wolf e){return tex;}
    }
}''')
# Vanilla wolf UV 64x32, painted muzzle and eyes and shaded fur.
for n,it,en,base,light in breeds:
    S=4;W=64*S;H=32*S;pix=bytearray(W*H*4)
    for y in range(H):
        for x in range(W):
            u=x/S;v=y/S;g=.78+.19*math.sin(u*.6)**2+.04*math.sin(u*9+v*.8)
            col=light if (v>15 and (int(u)//5)%3==0) or (u<10 and 6<v<11) else base
            c=tuple(int(a*g) for a in col)
            # head face (6,4) to (12,10), eyes
            if 6<=u<12 and 4<=v<10:
                if 7<=v<9:c=light
                if 6<=v<7.4 and (7<=u<8.4 or 9.7<=u<11.1):c=(225,196,115)
                if 6.2<=v<7.2 and (7.5<=u<8.2 or 10.2<=u<10.9):c=(24,23,25)
            if 4<=u<7 and 14<=v<16:c=(36,32,33)
            pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*[max(0,min(255,a)) for a in c],255))
    png(assets/'textures/entity'/f'{n}.png',W,H,pix)
for n in ['pochita']+[n for n,*_ in breeds]:dump(assets/'models/item'/f'{n}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,it,en,*_ in [('pochita','Pochita','Pochita')]+breeds:
        label=it if lang=='it_it' else en;d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    dump(p,d)
print('Pochita, Umbreon petting and five tameable wolf variants installed; Fennekin retains cuddles')
