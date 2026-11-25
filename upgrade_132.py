"""1.3.2: Maelle painting and Verso piano performances, craftable art furniture."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
    p.parent.mkdir(parents=True,exist_ok=True)
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
ids=['maelle','verso'];labels=['Maelle','Verso']
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
decl=''
for n,c,d in zip(ids,['0xa04c35','0x30343b'],['0x263444','0xbfc1c5']):
    r=n.upper();decl+=f'public static final RegistryObject<EntityType<ArtGuest>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<ArtGuest>of(ArtGuest::new,MobCategory.CREATURE).sized(1.5f,1.95f).clientTrackingRange(12).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{c},{d},new Item.Properties()));\n    '
edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,''.join(f'e.put({n.upper()}.get(),ArtGuest.attributes().build());' for n in ids)+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({n.upper()}_EGG.get());' for n in ids))
edit('Furniture.java','    static final RegistryObject<BlockEntityType<StorageEntity>> STORAGE=', '''    public static final RegistryObject<Block> PIANO=VampireLife.BLOCKS.register("piano",()->new ArtFurniture(true));
    public static final RegistryObject<Block> EASEL=VampireLife.BLOCKS.register("easel",()->new ArtFurniture(false));
    public static final RegistryObject<Item> PIANO_ITEM=Noctis.ITEMS.register("piano",()->new BlockItem(PIANO.get(),new Item.Properties()));
    public static final RegistryObject<Item> EASEL_ITEM=Noctis.ITEMS.register("easel",()->new BlockItem(EASEL.get(),new Item.Properties()));
    static final RegistryObject<BlockEntityType<StorageEntity>> STORAGE=''')
edit('Noctis.java','if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){','if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){e.accept(Furniture.PIANO_ITEM.get());e.accept(Furniture.EASEL_ITEM.get());')
(java/'ArtFurniture.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
public class ArtFurniture extends Furniture.FurnitureBlock{
    final boolean piano;
    ArtFurniture(boolean piano){super(0);this.piano=piano;}
    @Override public InteractionResult use(BlockState s,Level l,BlockPos pos,Player p,InteractionHand h,BlockHitResult hit){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(l instanceof ServerLevel sl){
            if(piano){double x=hit.getLocation().x-pos.getX(),z=hit.getLocation().z-pos.getZ();
                double u=switch(s.getValue(FACING)){case NORTH->x;case SOUTH->1-x;case EAST->z;default->1-z;};
                int note=Math.max(0,Math.min(7,(int)(u*8)));int[] scale={0,2,3,5,7,8,10,12};
                l.playSound(null,pos,SoundEvents.NOTE_BLOCK_HARP.value(),SoundSource.BLOCKS,1f,(float)Math.pow(2,(scale[note]-6)/12.0));
                sl.sendParticles(ParticleTypes.NOTE,pos.getX()+.5,pos.getY()+1.05,pos.getZ()+.5,1,0,0,0,0);
            }else{l.setBlock(pos,s.cycle(LIT),3);sl.sendParticles(ParticleTypes.WAX_ON,pos.getX()+.5,pos.getY()+.85,pos.getZ()+.5,8,.25,.25,.25,.01);}
        }return InteractionResult.sidedSuccess(l.isClientSide);
    }
}''',encoding='utf-8')
(java/'ArtGuest.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
public class ArtGuest extends PathfinderMob{
    static final EntityDataAccessor<Integer> PROGRESS=SynchedEntityData.defineId(ArtGuest.class,EntityDataSerializers.INT);
    // Original quiet melody written for the mod, using Minecraft note-block timbre.
    static final int[] MELODY={0,7,12,15,12,7,3,7,2,9,12,14,12,9,5,9,3,10,15,17,15,10,7,10,0,7,12,15,14,12,7,0};
    static final int[] BASS={-12,-10,-9,-12};
    int step,pose,speech;boolean paused;
    public ArtGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setPersistenceRequired();}
    public boolean maelle(){return getType()==Noctis.MAELLE.get();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,80).add(Attributes.ARMOR,5).add(Attributes.MOVEMENT_SPEED,.22).add(Attributes.KNOCKBACK_RESISTANCE,.9);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(PROGRESS,0);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));}
    public int progress(){return entityData.get(PROGRESS);}
    public float motion(){return pose<=0?0:(float)Math.sin(pose*Math.PI/16);}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(speech>0)speech--;
        if(!(level() instanceof ServerLevel l)||paused||!onGround()||l.getNearestPlayer(this,28)==null)return;
        if(maelle()){
            if(tickCount%24==0){
                int n=progress();if(n<5)entityData.set(PROGRESS,n+1);
                else if(tickCount%240==0)entityData.set(PROGRESS,0);
                l.broadcastEntityEvent(this,(byte)110);
                if(n<5){l.sendParticles(ParticleTypes.WAX_ON,getX(),getY()+1.2,getZ(),5,.25,.15,.25,.015);}
            }
        }else if(tickCount%8==0){
            int note=MELODY[step%MELODY.length];playSound(SoundEvents.NOTE_BLOCK_HARP.value(),.75f,(float)Math.pow(2,(note-6)/12.0));
            if(step%8==0)playSound(SoundEvents.NOTE_BLOCK_HARP.value(),.45f,(float)Math.pow(2,(BASS[(step/8)%4]+6)/12.0));
            step=(step+1)%MELODY.length;l.broadcastEntityEvent(this,(byte)110);
            if(step%4==0)l.sendParticles(ParticleTypes.NOTE,getX(),getY()+1.5,getZ(),1,.15,.15,.15,0);
        }
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l){
            if(p.isShiftKeyDown()){paused=!paused;p.displayClientMessage(Component.literal(paused?"Esibizione in pausa.":"Esibizione ripresa."),true);}
            else if(speech==0){speech=100;say(l,maelle()?"Ogni colore racconta qualcosa.":"Vuoi ascoltare un altro pezzo?");if(maelle()&&progress()==5)entityData.set(PROGRESS,0);}
        }return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==110){pose=16;return;}super.handleEntityEvent(id);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putInt("Painting",progress());t.putInt("Step",step);t.putBoolean("Paused",paused);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);entityData.set(PROGRESS,Math.max(0,Math.min(5,t.getInt("Painting"))));step=Math.floorMod(t.getInt("Step"),MELODY.length);paused=t.getBoolean("Paused");}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(l.isDay()&&p.getRandom().nextInt(24)==0&&l.getEntitiesOfClass(ArtGuest.class,p.getBoundingBox().inflate(72)).isEmpty()){
            for(int i=0;i<2;i++){
                BlockPos q=Eclipse.spot(p,12,24);if(q==null)continue;
                ArtGuest a=(i==0?Noctis.MAELLE.get():Noctis.VERSO.get()).create(l);
                if(a!=null){a.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(a)&&l.getEntitiesOfClass(ArtGuest.class,a.getBoundingBox().inflate(4)).isEmpty())l.addFreshEntity(a);}
            }
        }''')
# Craftable piano and easel; custom 3D geometry, natural material texture, active canvas.
for n,piano in [('piano',True),('easel',False)]:
    if piano:
        boxes=[(1,5,6,15,16,15,'dark'),(1,5,1,15,10,7,'wood'),(2,10,1,14,11,7,'white'),(1,0,2,3,5,4,'dark'),(13,0,2,15,5,4,'dark'),(1,0,12,15,5,15,'dark'),(2,13,5,14,14,6,'brass')]
        for i in range(8):boxes.append((2+i*1.5,10.9,1,2.2+i*1.5,11.1,6,'dark'))
        for i in (0,1,3,4,5):boxes.append((3+i*1.5,11,4,3.7+i*1.5,12,7,'dark'))
    else:
        boxes=[(2,0,9,4,16,11,'wood'),(12,0,9,14,16,11,'wood'),(7,0,13,9,13,15,'wood'),(2,4,6,14,5,11,'wood'),(2,5,7,14,15,8,'white')]
    for lit in (False,True):
        model=n+('_painted' if lit and not piano else '')
        bs=boxes+([] if piano or not lit else [(3,6,6.8,13,14,7,'art')])
        textures={m:'noctismagic:block/furniture_'+m for m in ('dark','wood','white','brass')};textures['art']='noctismagic:block/maelle_canvas';textures['particle']=textures['wood']
        elements=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in bs]
        dump(assets/'models/block'/f'{model}.json',{'textures':textures,'elements':elements,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]}}})
    dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
    dump(assets/'blockstates'/f'{n}.json',{'variants':{f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n+('_painted' if lit=='true' and not piano else ''),'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}})
    dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
    dump(res/'data/noctismagic/recipes'/f'{n}.json',{'type':'minecraft:crafting_shaped','pattern':['WWW','WXW',' S '],'key':{'W':{'item':'minecraft:dark_oak_planks'},'X':{'item':'minecraft:note_block' if piano else 'minecraft:painting'},'S':{'item':'minecraft:stick'}},'result':{'item':'noctismagic:'+n}})
def landscape(u,v):
    if v<.52:
        if (u-.69)**2+(v-.25)**2<.026:return (247,197,131)
        if v>.40+.08*math.sin(u*12):return (103,116,139)
        return (int(76+v*90),int(100+v*80),int(144+v*45))
    if v<.65+.08*math.sin(u*9):return (72,91,94)
    return (int(100+35*math.sin(u*19+v*5)**2),int(104+36*math.sin(u*17)**2),66)
pix=bytearray(64*64*4)
for y in range(64):
    for x in range(64):
        c=landscape(x/63,y/63);pix[(y*64+x)*4:(y*64+x)*4+4]=bytes((*c,255))
png(assets/'textures/block/maelle_canvas.png',64,64,pix)
# Independent character and integrated performance props. Props are part of model, not generated world blocks.
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
    y=0 if k==0 else 4
    part('b','r','body',(0,y,0),(0,0,0),[(-4,0,-2.5,8,10,5,'coat'),(-4,10,-2,8,2,4,'belt'),(-2,0,-2.8,4,8,1,'shirt')])
    part('h','r','head',(0,y-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-4,8,2,8,'hair')])
    for i in range(7):
        part('bang'+str(i),'h','bang'+str(i),(-3+i,-7.5,-3.5),(0,0,(i-3)*.18),[(-.8,0,-.7,2,3+i%3,2,'streak' if k==1 and i in (1,2) else 'hair')])
    if k==0:
        part('pony','h','pony',(0,-4,3),(-.4,0,.25),[(-2,0,0,4,5,4,'hair'),(-1.5,4,2,3,7,3,'hair')])
    else:
        for i in range(5):part('lock'+str(i),'h','lock'+str(i),(-3+i*1.5,-5,3),(0,0,(i-2)*.1),[(-1,0,0,2,6,2,'hair')])
        part('fur','b','fur',(0,0,0),(0,0,0),[(-5,-1,-1,10,2,5,'fur')])
    for i,s in enumerate((-1,1)):
        part('lapel'+str(i),'b','lapel'+str(i),(s*2.8,0,-2.8),(0,0,s*.24),[(-.7,0,-.3,1,8,1,'gold')])
        part('arm'+str(i),'r','arm'+str(i),(s*5,y,0),(0,0,-s*.1),[(-2,-1,-2,4,8,4,'coat'),(-1.5,7,-1.5,3,4,3,'face')])
        part('leg'+str(i),'r','leg'+str(i),(s*2.1,y+12,0),(0,0,0),[(-2,0,-2,4,7,4,'pants'),(-2,7,-2,4,5,4,'boot')])
    if k==0:
        part('brush','arm1','brush',(0,10,-1),(-.8,0,0),[(-.4,0,-.4,1,6,1,'wood'),(-.4,6,-.4,1,2,1,'gold')])
        part('palette','arm0','palette',(0,10,-1),(1.5,0,0),[(-3,0,-2,6,1,4,'wood'),(-2,-1,-1,1,1,1,'paintred'),(0,-1,0,1,1,1,'paintblue'),(2,-1,-1,1,1,1,'gold')])
        part('prop','r','prop',(0,0,-13),(0,0,0),[(-6,5,2,2,19,2,'wood'),(4,5,2,2,19,2,'wood'),(-1,8,-2,2,16,2,'wood'),(-6,15,0,12,2,4,'wood'),(-6,3,3,12,13,1,'canvas')])
        for j in range(5):part('stripe'+str(j),'prop','stripe'+str(j),(-6,3+j*2.6,4.1),(0,0,0),[(0,0,0,12,3,1,'art'+str(j))])
    else:
        part('prop','r','prop',(0,0,-12),(0,0,0),[(-11,-2,-9,22,17,10,'piano'),(-11,10,1,22,4,7,'piano'),(-10,14,1,2,10,2,'piano'),(8,14,1,2,10,2,'piano'),(-10,14,-8,20,10,2,'piano'),(-10,9,2,20,1,6,'canvas'),(-9,5,1,18,4,1,'piano'),(-9,4,2,18,1,1,'gold')])
        for j in range(10):part('key'+str(j),'prop','key'+str(j),(-10+j*2,8,2),(0,0,0),[(0,0,0,2,1,6,'canvas')])
        for j in (0,1,3,4,5,7,8):part('black'+str(j),'prop','black'+str(j),(-9+j*2,7,2),(0,0,0),[(0,0,0,1,1,3,'piano')])
        part('bench','r','bench',(0,18,3),(0,0,0),[(-5,-1,-3,10,2,6,'piano'),(-5,1,-3,2,5,2,'wood'),(3,1,-3,2,5,2,'wood'),(-5,1,1,2,5,2,'wood'),(3,1,1,2,5,2,'wood')])
    meshes.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    pal={'coat':(37,43,58) if k==0 else (40,43,45),'shirt':(49,46,70) if k==0 else (105,106,109),'face':(226,179,146),'hair':(172,70,45) if k==0 else (45,42,42),'streak':(176,177,183),'belt':(43,36,32),'pants':(47,45,48),'boot':(30,28,32),'gold':(194,153,71),'fur':(120,116,110),'wood':(100,65,40),'piano':(28,26,30),'canvas':(240,230,206),'paintred':(171,51,52),'paintblue':(53,91,143)}
    pix=bytearray(W*W*4)
    for x,y,w,h,m,f in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S)
                if m.startswith('art'):c=landscape(u,min(1,(int(m[-1])+v)/5))
                else:
                    base=pal[m];g=.73+.24*math.sin(u*math.pi)+.04*math.cos(v*9)
                    if m in ('hair','streak','fur'):g=.65+.34*math.sin(u*34+math.sin(v*8)*1.5)**2
                    if m=='gold':g=.55+.45*math.exp(-((u-.3)/.25)**2)
                    c=tuple(int(a*g) for a in base)
                    if m=='face' and f=='front' and h==7:
                        for ex in (.26,.74):
                            dx=(u-ex)/.18;dy=(v-.46)/.13
                            if dx*dx+dy*dy<1:c=(66,45,43)
                            if dx*dx+dy*dy<.74:c=(240,234,225)
                            if abs(dx)<.4 and abs(dy)<.8:c=(91,125,109) if k==0 else (110,138,148)
                            if abs(dx)<.16 and abs(dy)<.7:c=(24,25,29)
                        if k==1 and v>.66 and (u<.32 or u>.68 or v>.83):c=(59,46,40)
                        if .4<u<.62 and abs(v-.79)<.024:c=(136,74,65)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
    png(assets/'textures/entity'/f'{n}.png',W,W,pix);dump(assets/'models/item'/f'{n}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
(java/'ArtGuestClient.java').write_text('''package it.noctis.magic;
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
public class ArtGuestClient{
    static final String[] N={"maelle","verso"};
    static final ModelLayerLocation[] L={new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[0]),"main"),new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[1]),"main")};
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],ArtGuestClient::mesh0);e.registerLayerDefinition(L[1],ArtGuestClient::mesh1);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MAELLE.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.VERSO.get(),c->new Renderer(c,1));}
'''+ '\n'.join(meshes)+'''
    static class Model extends EntityModel<ArtGuest>{
        final ModelPart r,h,b,prop;final int k;Model(ModelPart r,int k){this.r=r;this.k=k;h=r.getChild("head");b=r.getChild("body");prop=r.getChild("prop");}
        @Override public void setupAnim(ArtGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.motion();
            h.xRot=.12f+a*.10f;h.yRot=(float)Math.sin(age*.04)*.06f;
            if(k==0){r.getChild("arm1").xRot=-1.05f-a*.48f;r.getChild("arm1").zRot=.10f+a*.22f;r.getChild("arm0").xRot=-.72f;h.getChild("pony").xRot=-.4f+(float)Math.sin(age*.13)*.06f;
                for(int j=0;j<5;j++)prop.getChild("stripe"+j).visible=j<e.progress();
            }else{
                for(int i=0;i<2;i++){r.getChild("arm"+i).xRot=-1.24f+(float)Math.sin(age*.6+i*1.4)*a*.25f;r.getChild("leg"+i).xRot=-1.2f;}
                for(int j=0;j<10;j++)prop.getChild("key"+j).y=a>0&&j==(int)(age/8)%10?.35f:0;
            }
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<ArtGuest,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.65f);this.k=k;}@Override public ResourceLocation getTextureLocation(ArtGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''',encoding='utf-8')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in zip(ids,labels):d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    d['block.noctismagic.piano']='Pianoforte' if lang=='it_it' else 'Piano';d['block.noctismagic.easel']='Cavalletto' if lang=='it_it' else 'Easel';dump(p,d)
print('Maelle and Verso: live painting, original piano melody, art furniture and spawn eggs')
