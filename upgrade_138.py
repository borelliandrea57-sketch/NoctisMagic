"""1.3.8: Shrek's summonable swamp homestead and resident ogre."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
    p.parent.mkdir(parents=True,exist_ok=True)
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<Item> SHREK_HOUSE_EGG=ITEMS.register("shrek_house_egg",()->new GothicEgg(false,false,false,false,true));
    public static final RegistryObject<EntityType<ShrekGuest>> SHREK=ENTITIES.register("shrek",()->EntityType.Builder.<ShrekGuest>of(ShrekGuest::new,MobCategory.CREATURE).sized(1.0f,2.5f).clientTrackingRange(12).build(ID+":shrek"));
    public static final RegistryObject<Item> SHREK_EGG=ITEMS.register("shrek_spawn_egg",()->new ForgeSpawnEggItem(SHREK,0x809e39,0x70503a,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(SHREK.get(),ShrekGuest.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(SHREK_HOUSE_EGG.get());e.accept(SHREK_EGG.get());')
edit('GothicEgg.java','private final boolean castle,bakery,pastry,sushi;','private final boolean castle,bakery,pastry,sushi,shrek;')
edit('GothicEgg.java','public GothicEgg(boolean castle,boolean bakery,boolean pastry,boolean sushi){super(new Item.Properties().stacksTo(1));this.castle=castle;this.bakery=bakery;this.pastry=pastry;this.sushi=sushi;}','public GothicEgg(boolean castle,boolean bakery,boolean pastry,boolean sushi){this(castle,bakery,pastry,sushi,false);} public GothicEgg(boolean castle,boolean bakery,boolean pastry,boolean sushi,boolean shrek){super(new Item.Properties().stacksTo(1));this.castle=castle;this.bakery=bakery;this.pastry=pastry;this.sushi=sushi;this.shrek=shrek;}')
edit('GothicEgg.java','Plan plan=sushi?sushiRestaurant():','Plan plan=shrek?shrekSwamp():sushi?sushiRestaurant():')
edit('GothicEgg.java','p.w==29?Noctis.SUSHI_EGG.get():','p.w==31?Noctis.SHREK_HOUSE_EGG.get():p.w==29?Noctis.SUSHI_EGG.get():')
edit('GothicEgg.java','    static Plan sushiRestaurant(){','''    static Plan shrekSwamp(){
        Plan p=new Plan(31,31,15,"La Palude di Shrek");
        // Moss, dirt paths, pond with retaining rim and a curved earthen cottage.
        for(int x=0;x<31;x++)for(int z=0;z<31;z++){
            boolean path=x>=13&&x<=17&&z<13;
            boolean pond=(x-6)*(x-6)+(z-21)*(z-21)<29;
            boolean rim=(x-6)*(x-6)+(z-21)*(z-21)<43;
            p.put(x,0,z,path?Blocks.COARSE_DIRT:rim?Blocks.MUD:(x*13+z*7)%5==0?Blocks.ROOTED_DIRT:Blocks.GRASS_BLOCK);
            if(pond)p.put(x,1,z,Blocks.WATER);
            else if(!path&&!rim&&(x<8||x>23)&&(x*7+z*3)%6==0)p.put(x,1,z,Blocks.BROWN_MUSHROOM);
        }
        // Round cottage under a grassy mound: hollow interior, no buried walkways.
        for(int x=8;x<=23;x++)for(int z=10;z<=23;z++){
            double a=(x-15.5)/7.6,b=(z-16.5)/6.7,d=a*a+b*b;
            if(d<=1.1)p.put(x,0,z,Blocks.SPRUCE_PLANKS);
            for(int y=1;y<=8;y++){
                double q=d+Math.pow((y-1)/7.6,2);
                if(q<=1.12&&(q>.78||y==8))p.put(x,y,z,y>=5?Blocks.MOSS_BLOCK:(x+z+y)%5==0?Blocks.ROOTED_DIRT:Blocks.MUD_BRICKS);
            }
        }
        // Flatten and open the doorway; log frame and open two-block entrance.
        p.box(13,1,10,17,4,13,Blocks.AIR);
        p.box(12,1,10,12,4,10,Blocks.DARK_OAK_LOG);p.box(18,1,10,18,4,10,Blocks.DARK_OAK_LOG);
        p.box(12,4,10,18,4,10,Blocks.DARK_OAK_LOG);
        p.box(14,1,14,16,3,16,Blocks.AIR);
        p.put(10,3,15,Blocks.GLASS);p.put(21,3,15,Blocks.GLASS);
        p.put(15,4,16,Blocks.LANTERN);p.put(19,1,18,Blocks.SMOKER);p.put(20,1,18,Blocks.CRAFTING_TABLE);
        p.put(19,2,18,Blocks.BRICKS);p.box(19,3,18,19,10,18,Blocks.BRICKS);p.put(19,11,18,Blocks.CAMPFIRE);
        p.put(11,1,18,Blocks.BARREL);p.put(12,1,18,Blocks.CHEST);
        p.put(11,1,15,Blocks.GREEN_BED.defaultBlockState().setValue(net.minecraft.world.level.block.BedBlock.FACING,Direction.SOUTH).setValue(net.minecraft.world.level.block.BedBlock.PART,net.minecraft.world.level.block.state.properties.BedPart.FOOT));
        p.put(11,1,16,Blocks.GREEN_BED.defaultBlockState().setValue(net.minecraft.world.level.block.BedBlock.FACING,Direction.SOUTH).setValue(net.minecraft.world.level.block.BedBlock.PART,net.minecraft.world.level.block.state.properties.BedPart.HEAD));
        p.put(15,1,20,Blocks.SPRUCE_FENCE);p.put(15,2,20,Blocks.SPRUCE_PRESSURE_PLATE);p.stair(14,1,20,Blocks.SPRUCE_STAIRS,Direction.WEST);
        // Iconic wooden outhouse, open doorway, crescent-like light slit.
        p.box(24,0,5,28,0,9,Blocks.SPRUCE_PLANKS);
        p.walls(24,1,5,28,4,9,Blocks.DARK_OAK_PLANKS);
        p.box(26,1,5,26,2,5,Blocks.AIR);p.put(26,3,5,Blocks.OAK_FENCE);
        p.box(23,5,4,29,5,10,Blocks.SPRUCE_SLAB);p.put(26,1,8,Blocks.CAULDRON);
        // Crooked swamp trees with permanent leaves and hanging vines.
        for(int[] t:new int[][]{{4,7},{26,17},{7,27},{25,26}}){
            int x=t[0],z=t[1];p.box(x,1,z,x,6,z,Blocks.OAK_LOG);
            for(int dx=-2;dx<=2;dx++)for(int dz=-2;dz<=2;dz++)for(int y=5;y<=8;y++)if(Math.abs(dx)+Math.abs(dz)+Math.abs(y-6)<=4&&!(dx==0&&dz==0&&y<=6))
                p.put(x+dx,y,z+dz,Blocks.OAK_LEAVES.defaultBlockState().setValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT,true));
        }
        for(int[] q:new int[][]{{4,20},{7,22},{6,19},{8,21}})p.put(q[0],2,q[1],Blocks.LILY_PAD);
        for(int x:new int[]{11,19}){p.put(x,1,6,Blocks.OAK_FENCE);p.put(x,2,6,Blocks.LANTERN);}
        p.put(20,1,8,Blocks.COMPOSTER);p.put(10,1,8,Blocks.POTTED_BROWN_MUSHROOM);
        return p;
    }
    static Plan sushiRestaurant(){''')
a='            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");'
edit('GothicEgg.java',a,'''            if(p.w==31){
                ShrekGuest ogre=Noctis.SHREK.get().create(l);
                if(ogre!=null){BlockPos q=pos(15,1,8);ogre.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+180,0);ogre.setHome(q);ogre.setPersistenceRequired();if(l.noCollision(ogre))l.addFreshEntity(ogre);}
            }
'''+a)
(java/'ShrekGuest.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
public class ShrekGuest extends PathfinderMob{
    BlockPos home;int speech,gesture;UUID visitor;
    static final String[] LINES={"CHE CI FAI NELLA MIA PALUDE?!","Gli orchi sono come le cipolle. Hanno gli strati!","La porta e' aperta, ma non significa che sei invitato.","Voglio solo un po' di tranquillita'."};
    public ShrekGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,120).add(Attributes.ARMOR,8).add(Attributes.MOVEMENT_SPEED,.26).add(Attributes.KNOCKBACK_RESISTANCE,.7);}
    public void setHome(BlockPos p){home=p;restrictTo(p,12);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MoveTowardsRestrictionGoal(this,.85));goalSelector.addGoal(2,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.65));}
    void talk(ServerLevel l,String s){speech=180;NpcDialogue.say(l,Component.literal("Shrek: "+s).withStyle(net.minecraft.ChatFormatting.GREEN));l.broadcastEntityEvent(this,(byte)114);}
    @Override public void tick(){super.tick();if(speech>0)speech--;if(gesture>0)gesture--;if(!(level() instanceof ServerLevel l))return;
        if(home!=null&&tickCount%20==0&&distanceToSqr(home.getX()+.5,home.getY(),home.getZ()+.5)>144)getNavigation().moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.9);
        Player p=l.getNearestPlayer(this,7);if(p==null){visitor=null;return;}if(speech==0&&!p.getUUID().equals(visitor)){visitor=p.getUUID();talk(l,LINES[0]);}
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;if(level() instanceof ServerLevel l&&speech==0)talk(l,LINES[random.nextInt(LINES.length)]);return InteractionResult.sidedSuccess(level().isClientSide);}
    @Override public void handleEntityEvent(byte id){if(id==114){gesture=28;return;}super.handleEntityEvent(id);}
    public float gesture(){return gesture<=0?0:(float)Math.sin(gesture*Math.PI/28);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(home!=null)t.putLong("Home",home.asLong());}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);if(t.contains("Home"))setHome(BlockPos.of(t.getLong("Home")));}
}''',encoding='utf-8')
# Broad pear-shaped ogre, rounded muzzle, ears as flared trumpets, patchwork vest.
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
part('b','r','body',(0,0,0),(0,0,0),[(-5.5,-1,-3.5,11,7,7,'vest'),(-6.5,5,-4.5,13,7,9,'tunic'),(-6,11,-4,12,2,8,'belt'),(-3,0,-3.9,6,6,1,'tunic')])
part('h','r','head',(0,-1,0),(0,0,0),[(-4.5,-7,-4,9,8,8,'face'),(-5,-3,-3.5,10,4,7,'skin'),(-3.5,-8,-3.5,7,2,7,'skin'),(-1.5,-3,-5,3,3,2,'skin')])
for i,s in enumerate((-1,1)):
    part('ear'+str(i),'h','ear'+str(i),(s*4.1,-5,0),(0,0,-s*.35),[(0 if s>0 else -3,-.8,-.8,3,2,2,'skin'),(2 if s>0 else -4,-1.5,-1.5,2,3,3,'ear')])
    part('a'+str(i),'r','arm'+str(i),(s*6.5,0,0),(0,0,-s*.15),[(-2.5,-1,-2.5,5,6,5,'tunic'),(-2,5,-2,4,5,4,'skin'),(-2,10,-2,4,2,4,'skin')])
    part('leg'+str(i),'r','leg'+str(i),(s*3.2,13,0),(0,0,0),[(-2.5,0,-2.5,5,7,5,'pants'),(-2.5,7,-3,5,4,6,'boot')])
(java/'ShrekClient.java').write_text('''package it.noctis.magic;
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
public class ShrekClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"shrek"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,ShrekClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.SHREK.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);}
    static class Model extends EntityModel<ShrekGuest>{
        final ModelPart r,h,b;Model(ModelPart r){this.r=r;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(ShrekGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.gesture();h.yRot=yaw*.017f;h.xRot=pitch*.015f-a*.15f;b.yRot=a*.10f;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;r.getChild("leg"+i).xRot=w*.5f;r.getChild("arm"+i).xRot=-w*.5f-a*(i==1?1.1f:.35f);h.getChild("ear"+i).zRot=(i==0?1:-1)*(.35f+(float)Math.sin(age*.10+i)*.06f);}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float rr,float g,float bb,float a){r.render(p,v,light,overlay,rr,g,bb,a);}
    }
    static class Renderer extends MobRenderer<ShrekGuest,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.55f);}@Override protected void scale(ShrekGuest e,PoseStack p,float partial){p.scale(1.24f,1.24f,1.24f);}@Override public ResourceLocation getTextureLocation(ShrekGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/shrek.png");}}
}''',encoding='utf-8')
pal={'skin':(133,160,66),'face':(142,169,73),'ear':(119,147,57),'vest':(100,65,44),'tunic':(214,204,170),'belt':(74,48,31),'pants':(107,83,55),'boot':(64,45,34)}
pix=bytearray(W*W*4)
for x,y,w,h,m,f in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);base=pal[m];g=.74+.26*math.sin(u*math.pi)+.035*math.cos(v*9)
            if m in ('vest','tunic','pants'):g*=.94+.06*math.sin(u*95+v*81)
            c=tuple(int(a*g) for a in base)
            if m=='face' and f=='front':
                for ex in (.25,.75):
                    dx=(u-ex)/.19;dy=(v-.43)/.13
                    if dx*dx+dy*dy<1:c=(65,80,37)
                    if dx*dx+dy*dy<.76:c=(240,229,191)
                    if abs(dx)<.42 and abs(dy)<.8:c=(107,83,40)
                    if abs(dx)<.18 and abs(dy)<.72:c=(30,29,20)
                    if (dx+.17)**2+(dy+.22)**2<.08:c=(255,252,227)
                    if abs(dx)<1 and abs(v-.24)<.025:c=(77,99,38)
                if .24<u<.76 and abs(v-(.77+.10*(1-((u-.5)/.26)**2)))<.025:c=(65,91,37)
            if m=='vest' and f=='front' and (u<.06 or u>.94):c=(61,40,29)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
png(assets/'textures/entity/shrek.png',W,W,pix)
dump(assets/'models/item/shrek_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
W=32;pix=bytearray(W*W*4)
for y in range(W):
    for x in range(W):
        d=((x-15.5)/12)**2+((y-16)/14)**2
        if d>1:continue
        c=(133,104,62) if d>.82 else (79,121,50)
        if 7<x<25 and 13<y<24:c=(119,82,52)
        if 7<x<25 and 7<y<=15 and abs(x-16)<(y-5)*1.3:c=(121,158,63)
        if 13<x<19 and 17<y<24:c=(53,40,28)
        pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
png(assets/'textures/item/shrek_house_egg.png',W,W,pix);dump(assets/'models/item/shrek_house_egg.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/shrek_house_egg'}})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.shrek']='Shrek';d['item.noctismagic.shrek_spawn_egg']='Uovo generatore: Shrek' if lang=='it_it' else 'Shrek Spawn Egg';d['item.noctismagic.shrek_house_egg']='Uovo della Palude di Shrek' if lang=='it_it' else "Shrek's Swamp Egg";dump(p,d)
print('Shrek swamp cottage, resident ogre and two eggs installed')
