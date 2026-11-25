"""1.3.4: summonable sushi restaurant, Maomao and Jinshi, five sushi dishes."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic';res=root/'src/main/resources'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
    p.parent.mkdir(parents=True,exist_ok=True)
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
foods=[('salmon_nigiri','Nigiri al salmone','Salmon nigiri',5,(235,124,82)),('tuna_nigiri','Nigiri al tonno','Tuna nigiri',5,(167,46,63)),('maki_roll','Maki','Maki roll',6,(38,74,52)),('onigiri','Onigiri','Onigiri',6,(238,234,215)),('matcha_tea','Tè matcha','Matcha tea',2,(110,153,61))]
decl='''public static final RegistryObject<Item> SUSHI_EGG=ITEMS.register("sushi_restaurant_egg",()->new GothicEgg(false,false,false,true));
    public static final RegistryObject<EntityType<SushiGuest>> MAOMAO=ENTITIES.register("maomao",()->EntityType.Builder.<SushiGuest>of(SushiGuest::new,MobCategory.CREATURE).sized(.6f,1.7f).clientTrackingRange(10).build(ID+":maomao"));
    public static final RegistryObject<EntityType<SushiGuest>> JINSHI=ENTITIES.register("jinshi",()->EntityType.Builder.<SushiGuest>of(SushiGuest::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":jinshi"));
    public static final RegistryObject<Item> MAOMAO_EGG=ITEMS.register("maomao_spawn_egg",()->new ForgeSpawnEggItem(MAOMAO,0x22956b,0x193b39,new Item.Properties()));
    public static final RegistryObject<Item> JINSHI_EGG=ITEMS.register("jinshi_spawn_egg",()->new ForgeSpawnEggItem(JINSHI,0x726aa3,0x482539,new Item.Properties()));
    '''
for n,it,en,food,c in foods:decl+=f'public static final RegistryObject<Item> SUSHI_{n.upper()}=ITEMS.register("{n}",()->new SushiFood({food},{str(n=="matcha_tea").lower()}));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG=';edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(MAOMAO.get(),SushiGuest.attributes().build());e.put(JINSHI.get(),SushiGuest.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(SUSHI_EGG.get());e.accept(MAOMAO_EGG.get());e.accept(JINSHI_EGG.get());')
a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';edit('Noctis.java',a,'if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS){'+''.join(f'e.accept(SUSHI_{n.upper()}.get());' for n,*_ in foods)+'}'+a)
edit('GothicEgg.java','private final boolean castle,bakery,pastry;','private final boolean castle,bakery,pastry,sushi;')
edit('GothicEgg.java','public GothicEgg(boolean castle,boolean bakery,boolean pastry){super(new Item.Properties().stacksTo(1));this.castle=castle;this.bakery=bakery;this.pastry=pastry;}','public GothicEgg(boolean castle,boolean bakery,boolean pastry){this(castle,bakery,pastry,false);} public GothicEgg(boolean castle,boolean bakery,boolean pastry,boolean sushi){super(new Item.Properties().stacksTo(1));this.castle=castle;this.bakery=bakery;this.pastry=pastry;this.sushi=sushi;}')
edit('GothicEgg.java','Plan plan=bakery?bakery(pastry):castle?castle():cathedral();','Plan plan=sushi?sushiRestaurant():bakery?bakery(pastry):castle?castle():cathedral();')
edit('GothicEgg.java','p.w==25?(p.name.startsWith("Pasticceria")','p.w==29?Noctis.SUSHI_EGG.get():p.w==25?(p.name.startsWith("Pasticceria")')
edit('GothicEgg.java','    static Plan bakery(boolean pastry){','''    static Plan sushiRestaurant(){
        Plan p=new Plan(29,25,14,"Ristorante Sushi del Gatto di Giada");
        // Tatami-like floor, dark timber framing, curved stepped roof and red entrance.
        for(int x=0;x<29;x++)for(int z=0;z<25;z++)
            p.put(x,0,z,x==0||x==28||z==0||z==24?Blocks.POLISHED_ANDESITE:(x%5==0||z%5==0?Blocks.DARK_OAK_PLANKS:Blocks.STRIPPED_BAMBOO_BLOCK));
        p.walls(1,1,4,27,7,23,Blocks.SMOOTH_QUARTZ);
        for(int x=1;x<=27;x+=6)for(int z:new int[]{4,23})p.box(x,1,z,x,7,z,Blocks.DARK_OAK_LOG);
        for(int z=4;z<=23;z+=6)for(int x:new int[]{1,27})p.box(x,1,z,x,7,z,Blocks.DARK_OAK_LOG);
        for(int x=3;x<=25;x++)if(x<11||x>17){p.box(x,2,4,x,5,4,Blocks.WHITE_STAINED_GLASS);if(x%3==0)p.box(x,2,4,x,5,4,Blocks.DARK_OAK_FENCE);}
        p.box(12,1,4,16,4,4,Blocks.AIR);
        // Noren curtain and freestanding torii-style portal.
        for(int x=11;x<=17;x++)p.put(x,5,3,Blocks.RED_WOOL);
        for(int x:new int[]{9,19})p.box(x,1,1,x,5,1,Blocks.RED_TERRACOTTA);
        p.box(8,5,1,20,5,1,Blocks.RED_TERRACOTTA);p.box(7,6,1,21,6,1,Blocks.DEEPSLATE_TILES);
        p.box(1,8,4,27,8,23,Blocks.DARK_OAK_PLANKS);
        for(int y=0;y<5;y++){p.ring(y,8+y,3+y,28-y,24-y,Blocks.DEEPSLATE_TILE_SLAB);p.box(y+1,8+y,4+y,27-y,8+y,23-y,Blocks.DEEPSLATE_TILES);}
        p.box(5,13,8,23,13,19,Blocks.DEEPSLATE_TILE_SLAB);
        // Lantern-lit dining room, stools, low tables and potted bamboo.
        for(int x:new int[]{5,14,23})for(int z:new int[]{8,12}){
            p.box(x-1,1,z,x+1,1,z,Blocks.DARK_OAK_SLAB);
            p.stair(x,1,z-2,Blocks.BAMBOO_STAIRS,Direction.SOUTH);p.stair(x,1,z+2,Blocks.BAMBOO_STAIRS,Direction.NORTH);
            p.put(x,2,z,Blocks.FLOWER_POT);
        }
        for(int x:new int[]{3,25})for(int z:new int[]{6,14,21}){p.put(x,1,z,Blocks.POTTED_BAMBOO);}
        for(int x:new int[]{5,14,23})for(int z:new int[]{8,16,21}){p.put(x,7,z,Blocks.CHAIN);p.put(x,6,z,Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING,true));}
        // Wide sushi bar and kitchen, central corridor open.
        p.box(3,1,16,11,1,16,Blocks.STRIPPED_DARK_OAK_LOG);p.box(17,1,16,25,1,16,Blocks.STRIPPED_DARK_OAK_LOG);
        p.box(3,2,16,11,2,16,Blocks.SMOOTH_QUARTZ_SLAB);p.box(17,2,16,25,2,16,Blocks.SMOOTH_QUARTZ_SLAB);
        for(int x:new int[]{5,8,20,23})p.stair(x,1,14,Blocks.DARK_OAK_STAIRS,Direction.NORTH);
        for(int x:new int[]{5,9,19,23}){p.put(x,1,22,Blocks.SMOKER);p.put(x,2,22,Blocks.BARREL);}
        p.put(3,1,20,Furniture.FRIDGE.get());p.put(25,1,20,Furniture.DISHWASHER.get());p.put(14,1,22,Blocks.CRAFTING_TABLE);p.put(16,1,22,Blocks.CAULDRON);
        return p;
    }
    static Plan bakery(boolean pastry){''')
a='            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");'
edit('GothicEgg.java',a,'''            if(p.w==29){
                for(int i=0;i<2;i++){
                    SushiGuest staff=(i==0?Noctis.MAOMAO.get():Noctis.JINSHI.get()).create(l);
                    if(staff!=null){BlockPos q=pos(i==0?8:20,1,18);staff.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+180,0);staff.setHome(q);staff.setPersistenceRequired();if(l.noCollision(staff))l.addFreshEntity(staff);}
                }
            }
'''+a)
(java/'SushiFood.java').write_text('''package it.noctis.magic;
import net.minecraft.world.item.*;
import net.minecraft.world.food.FoodProperties;
public class SushiFood extends Item{
    final boolean tea;
    SushiFood(int food,boolean tea){super(new Properties().food(new FoodProperties.Builder().nutrition(food).saturationMod(.6f).build()));this.tea=tea;}
    @Override public UseAnim getUseAnimation(ItemStack s){return tea?UseAnim.DRINK:UseAnim.EAT;}
}''',encoding='utf-8')
(java/'SushiGuest.java').write_text('''package it.noctis.magic;
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
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
public class SushiGuest extends PathfinderMob{
    BlockPos home;int speech,pose;
    public SushiGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setPersistenceRequired();}
    public boolean maomao(){return getType()==Noctis.MAOMAO.get();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,45).add(Attributes.MOVEMENT_SPEED,.23).add(Attributes.KNOCKBACK_RESISTANCE,.8);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(2,new RandomLookAroundGoal(this));}
    public void setHome(BlockPos p){home=p;}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}
    @Override public void tick(){super.tick();if(speech>0)speech--;if(pose>0)pose--;if(!(level() instanceof ServerLevel l))return;
        if(home!=null&&tickCount%20==0&&distanceToSqr(home.getX()+.5,home.getY(),home.getZ()+.5)>1.5)getNavigation().moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.8);
        if(maomao()&&tickCount%90==0&&l.getNearestPlayer(this,12)!=null)l.broadcastEntityEvent(this,(byte)112);
        if(maomao()&&speech==0&&tickCount%240==0&&l.getNearestPlayer(this,9)!=null&&random.nextInt(3)==0){
            speech=240;var others=l.getEntitiesOfClass(SushiGuest.class,getBoundingBox().inflate(16),e->!e.maomao());
            if(!others.isEmpty()){say(l,"Jinshi-sama, il pesce va controllato. Non ammirato.");others.get(0).say(l,"Maomao, almeno assaggia il mio nigiri.");}
        }
    }
    Item product(int i){return switch(i){case 0->Noctis.SUSHI_SALMON_NIGIRI.get();case 1->Noctis.SUSHI_TUNA_NIGIRI.get();case 2->Noctis.SUSHI_MAKI_ROLL.get();case 3->Noctis.SUSHI_ONIGIRI.get();default->Noctis.SUSHI_MATCHA_TEA.get();};}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        ItemStack s=p.getItemInHand(h);if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET))return InteractionResult.PASS;
        if(level() instanceof ServerLevel l){
            String key="NoctisSushiMenu";int n=Math.floorMod(p.getPersistentData().getInt(key),5);
            if(s.isEmpty()){
                if(p.isShiftKeyDown()){n=(n+1)%5;p.getPersistentData().putInt(key,n);}
                p.sendSystemMessage(Component.literal("Menu: ").append(product(n).getDescription()).append(" | 1 pepita d'oro. Shift + clic a mano vuota: prossimo piatto."));
                if(speech==0){speech=100;say(l,maomao()?"Ho controllato gli ingredienti. Nessun veleno, purtroppo.":"Benvenuto. Maomao ha preparato tutto con estrema cura.");}
            }else{
                if(!p.getAbilities().instabuild)s.shrink(1);ItemStack out=new ItemStack(product(n),n==4?1:2);if(!p.getInventory().add(out))p.drop(out,false);
                l.broadcastEntityEvent(this,(byte)112);playSound(SoundEvents.VILLAGER_YES,.65f,1.2f);
                if(speech==0){speech=80;say(l,maomao()?"Ecco il tuo ordine. Non ho aggiunto esperimenti.":"Buon appetito!");}
            }
        }return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==112){pose=24;return;}super.handleEntityEvent(id);}
    public float serving(){return pose<=0?0:(float)Math.sin(pose*Math.PI/24);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(home!=null)t.putLong("Home",home.asLong());}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);home=t.contains("Home")?BlockPos.of(t.getLong("Home")):null;}
}''',encoding='utf-8')
# Articulated hair, flowing robes, distinctive facial textures.
N=256;S=4;W=N*S;meshes=[]
for k,n in enumerate(('maomao','jinshi')):
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
    part('b','r','body',(0,0,0),(0,0,0),[(-4,0,-2.5,8,10,5,'robe'),(-4,10,-2.8,8,2,6,'belt'),(-4.5,12,-2.5,9,11,5,'robe')])
    part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-4,8,2,8,'hair')])
    part('bun','h','bun',(0,-8,2),(0,0,0),[(-2,-3,-1,4,4,4,'hair'),(-2,-4,0,4,1,3,'ribbon')])
    for i in range(7):
        part('bang'+str(i),'h','bang'+str(i),(-3+i,-7,-3.6),(0,0,(i-3)*(.12 if k==0 else .23)),[(-.7,0,-.5,1,3+i%2,1,'hair')])
        if k==1:part('back'+str(i),'h','back'+str(i),(-3+i,-6,3),(0,0,(i-3)*.04),[(-.8,0,-.8,2,17+i%2,2,'hair')])
    for i,s in enumerate((-1,1)):
        part('lock'+str(i),'h','lock'+str(i),(s*3.4,-5,0),(0,0,s*.1),[(-1,0,-1,2,6,3,'hair')])
        part('braid'+str(i),'lock'+str(i),'braid',(0,5,0),(0,0,s*.22),[(-.7,0,-.7,1,7 if k==0 else 11,2,'hair'),(-.8,6 if k==0 else 10,-.8,2,1,2,'ribbon')])
        part('collar'+str(i),'b','collar'+str(i),(s*2,0,-2.8),(0,0,s*.35),[(-.8,0,-.3,2,7,1,'trim')])
        part('arm'+str(i),'r','arm'+str(i),(s*4.8,0,0),(0,0,-s*.1),[(-2,-1,-2,4,8,4,'robe'),(-2.3,6,-2.3,5,4,5,'trim'),(-1.4,10,-1.4,3,2,3,'face')])
        part('leg'+str(i),'r','leg'+str(i),(s*2,21,0),(0,0,0),[(-1.6,0,-2,3,3,4,'shoe')])
    part('tray','arm1','tray',(0,11,-2),(1.45,0,0),[(-3,0,-3,6,1,5,'tray'),(-2,-1,-2,2,1,3,'rice'),(-2,-2,-2,2,1,3,'fish'),(1,-1,-1,2,1,2,'rice')])
    meshes.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    pal={'robe':(36,156,111) if k==0 else (100,93,153),'trim':(159,211,181) if k==0 else (191,179,133),'belt':(33,104,88) if k==0 else (57,45,76),'face':(238,192,155),'hair':(23,57,51) if k==0 else (66,32,55),'ribbon':(218,165,70) if k==0 else (214,204,216),'shoe':(34,38,41),'tray':(95,54,34),'rice':(236,232,210),'fish':(235,125,86)}
    pix=bytearray(W*W*4)
    for x,y,w,h,m,f in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S);base=pal[m];g=.77+.23*math.sin(u*math.pi)+.04*math.cos(v*9)
                if m=='hair':g=.65+.34*math.sin(u*31+math.sin(v*7))**2
                c=tuple(int(a*g) for a in base)
                if m=='robe' and (abs(v-.88)<.035 or abs(math.sin(u*17+v*14))<.10 and v>.7):c=pal['trim']
                if m=='face' and f=='front' and h==7:
                    for ex in (.26,.74):
                        dx=(u-ex)/.19;dy=(v-.44)/(.17 if k==0 else .125);d=dx*dx+dy*dy
                        if d<1:c=(75,45,58)
                        if d<.76:c=(248,241,230)
                        if abs(dx)<.5 and abs(dy)<.85:c=(int(104+38*dy),int(65+42*dy),157 if k==0 else 111)
                        if abs(dx)<.18 and abs(dy)<.7:c=(29,23,40)
                        if (dx+.2)**2+(dy+.28)**2<.085:c=(255,255,255)
                    if k==0 and .49<v<.62 and .32<u<.68 and (int(u*35)+int(v*43))%7==0:c=(171,112,93)
                    if .42<u<.59 and abs(v-.78)<.022:c=(147,78,79)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
    png(assets/'textures/entity'/f'{n}.png',W,W,pix)
    dump(assets/'models/item'/f'{n}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
(java/'SushiGuestClient.java').write_text('''package it.noctis.magic;
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
public class SushiGuestClient{
    static final String[] N={"maomao","jinshi"};
    static final ModelLayerLocation[] L={new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[0]),"main"),new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[1]),"main")};
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],SushiGuestClient::mesh0);e.registerLayerDefinition(L[1],SushiGuestClient::mesh1);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MAOMAO.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.JINSHI.get(),c->new Renderer(c,1));}
'''+ '\n'.join(meshes)+'''
    static class Model extends EntityModel<SushiGuest>{
        final ModelPart r,h;final int k;Model(ModelPart r,int k){this.r=r;this.k=k;h=r.getChild("head");}
        @Override public void setupAnim(SushiGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.serving();h.yRot=yaw*.017f;h.xRot=pitch*.012f+a*.08f;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;r.getChild("leg"+i).xRot=w*.4f;r.getChild("arm"+i).xRot=-w*.35f-(i==1?1.15f*a:.35f*a);h.getChild("lock"+i).xRot=(float)Math.sin(age*.12+i)*.04f+amount*.12f;}
            r.getChild("arm1").getChild("tray").visible=a>0;
            if(k==1)for(int i=0;i<7;i++)h.getChild("back"+i).xRot=amount*.25f+(float)Math.sin(age*.11+i*.4)*.04f;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<SushiGuest,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.35f);this.k=k;}@Override protected void scale(SushiGuest e,PoseStack p,float partial){if(k==0)p.scale(.88f,.88f,.88f);}@Override public ResourceLocation getTextureLocation(SushiGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''',encoding='utf-8')
for n,it,en,food,col in foods:
    W=32;pix=bytearray(W*W*4)
    for y in range(W):
        for x in range(W):
            c=None;u=(x-15.5)/12;v=(y-16)/8
            if n=='matcha_tea':
                if 6<x<26 and 11<y<26 and abs(x-16)<10-(y-11)*.24:c=(221,218,194)
                if u*u+((y-11)/4)**2<1:c=col
            elif n=='onigiri':
                if 6<y<27 and abs(x-16)<(y-5)*.55:c=(239,232,210)
                if 12<x<20 and 19<y<27 and c:c=(38,64,48)
            elif n=='maki_roll':
                if u*u+v*v<1:c=(35,63,48) if u*u+v*v>.73 else (237,233,216) if u*u+v*v>.17 else (218,106,76)
            else:
                if u*u+v*v<1:c=(238,233,216) if y>17 else col
                if c and y<18 and (x+y*2)%8==0:c=tuple(min(255,a+37) for a in c)
            if c:pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
    png(assets/'textures/item'/f'{n}.png',W,W,pix);dump(assets/'models/item'/f'{n}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/'+n}})
W=32;pix=bytearray(W*W*4)
for y in range(W):
    for x in range(W):
        d=((x-15.5)/12)**2+((y-16)/14)**2
        if d>1:continue
        c=(196,160,83) if d>.82 else (39,88,74)
        if 7<x<25 and (10<y<14 or 17<y<19 or x in (10,11,20,21) and 13<y<25):c=(194,49,45)
        pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
png(assets/'textures/item/sushi_restaurant_egg.png',W,W,pix);dump(assets/'models/item/sushi_restaurant_egg.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/sushi_restaurant_egg'}})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['item.noctismagic.sushi_restaurant_egg']='Uovo del ristorante sushi' if lang=='it_it' else 'Sushi Restaurant Egg'
    for n,label in [('maomao','Maomao'),('jinshi','Jinshi')]:d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    for n,it,en,*_ in foods:d['item.noctismagic.'+n]=it if lang=='it_it' else en
    dump(p,d)
print('Sushi restaurant structure, Maomao and Jinshi, menu and animated serving installed')
