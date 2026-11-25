"""1.3.9: summonable McDonald's parody restaurant and satirical cashier."""
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
foods=[('mcd_burger','Hamburger','Hamburger',8),('mcd_fries','Patatine fritte','Fries',5),('mcd_cola','Cola','Cola',2),('mcd_nuggets','Nuggets di pollo','Chicken nuggets',5)]
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
decl='''public static final RegistryObject<Item> MCD_EGG=ITEMS.register("mcdonalds_egg",()->new GothicEgg(false,false,false,false,false,true));
    public static final RegistryObject<EntityType<FastFoodGuest>> MCD_CASHIER=ENTITIES.register("mcd_cashier",()->EntityType.Builder.<FastFoodGuest>of(FastFoodGuest::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":mcd_cashier"));
    public static final RegistryObject<Item> MCD_CASHIER_EGG=ITEMS.register("mcd_cashier_spawn_egg",()->new ForgeSpawnEggItem(MCD_CASHIER,0xb92129,0xecc748,new Item.Properties()));
    '''
for n,it,en,f in foods:
    decl+=f'public static final RegistryObject<Item> {n.upper()}=ITEMS.register("{n}",()->new SushiFood({f},{str(n=="mcd_cola").lower()}));\n    '
edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(MCD_CASHIER.get(),FastFoodGuest.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(MCD_EGG.get());e.accept(MCD_CASHIER_EGG.get());')
a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';edit('Noctis.java',a,'if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS){'+''.join(f'e.accept({n.upper()}.get());' for n,*_ in foods)+'}'+a)
edit('GothicEgg.java','private final boolean castle,bakery,pastry,sushi,shrek;','private final boolean castle,bakery,pastry,sushi,shrek,mcd;')
edit('GothicEgg.java','public GothicEgg(boolean castle,boolean bakery,boolean pastry,boolean sushi,boolean shrek){super(new Item.Properties().stacksTo(1));this.castle=castle;this.bakery=bakery;this.pastry=pastry;this.sushi=sushi;this.shrek=shrek;}','public GothicEgg(boolean castle,boolean bakery,boolean pastry,boolean sushi,boolean shrek){this(castle,bakery,pastry,sushi,shrek,false);} public GothicEgg(boolean castle,boolean bakery,boolean pastry,boolean sushi,boolean shrek,boolean mcd){super(new Item.Properties().stacksTo(1));this.castle=castle;this.bakery=bakery;this.pastry=pastry;this.sushi=sushi;this.shrek=shrek;this.mcd=mcd;}')
edit('GothicEgg.java','Plan plan=shrek?shrekSwamp():','Plan plan=mcd?fastFood():shrek?shrekSwamp():')
edit('GothicEgg.java','p.w==31?Noctis.SHREK_HOUSE_EGG.get():','p.w==33?Noctis.MCD_EGG.get():p.w==31?Noctis.SHREK_HOUSE_EGG.get():')
# Keep pond water contained and separate from cottage.
edit('GothicEgg.java','boolean pond=(x-6)*(x-6)+(z-21)*(z-21)<29;','boolean pond=(x-5)*(x-5)+(z-23)*(z-23)<13;')
edit('GothicEgg.java','boolean rim=(x-6)*(x-6)+(z-21)*(z-21)<43;','boolean rim=(x-5)*(x-5)+(z-23)*(z-23)<23;')
edit('GothicEgg.java','if(pond)p.put(x,1,z,Blocks.WATER);','if(pond)p.put(x,1,z,Blocks.WATER);else if(rim)p.put(x,1,z,Blocks.MUD);')
edit('GothicEgg.java','new int[][]{{4,20},{7,22},{6,19},{8,21}}','new int[][]{{4,22},{6,23},{5,21},{5,25}}')
edit('GothicEgg.java','    static Plan shrekSwamp(){','''    static Plan fastFood(){
        Plan p=new Plan(33,27,12,"McDonald's - Fast food");
        for(int x=0;x<33;x++)for(int z=0;z<27;z++)p.put(x,0,z,z<5?Blocks.GRAY_CONCRETE:((x+z)%2==0?Blocks.SMOOTH_QUARTZ:Blocks.POLISHED_DIORITE));
        p.walls(1,1,5,31,7,25,Blocks.WHITE_CONCRETE);
        for(int x=1;x<=31;x++)for(int z=5;z<=25;z++)p.put(x,8,z,Blocks.RED_CONCRETE);
        p.ring(0,8,4,32,26,Blocks.YELLOW_CONCRETE);
        p.ring(1,7,5,31,25,Blocks.RED_CONCRETE);
        p.box(14,1,5,18,3,5,Blocks.AIR);
        for(int x=3;x<=29;x++)if(x<12||x>20)p.box(x,2,5,x,5,5,Blocks.GLASS);
        for(int z=7;z<=22;z+=4)for(int x:new int[]{1,31})p.box(x,2,z,x,5,z+1,Blocks.GLASS);
        // Golden arches on the facade, drawn as two connected block arches.
        for(int x:new int[]{12,16,20})p.box(x,7,4,x,10,4,Blocks.YELLOW_CONCRETE);
        p.box(13,10,4,15,10,4,Blocks.YELLOW_CONCRETE);p.box(17,10,4,19,10,4,Blocks.YELLOW_CONCRETE);
        p.put(13,9,4,Blocks.YELLOW_CONCRETE);p.put(19,9,4,Blocks.YELLOW_CONCRETE);
        for(int x:new int[]{5,11,21,27})for(int z:new int[]{9,13}){
            p.put(x,1,z,Blocks.IRON_BARS);p.put(x,2,z,Blocks.SMOOTH_QUARTZ_SLAB);
            p.stair(x-2,1,z,Blocks.RED_SANDSTONE_STAIRS,Direction.WEST);p.stair(x+2,1,z,Blocks.RED_SANDSTONE_STAIRS,Direction.EAST);
        }
        for(int x:new int[]{5,11,16,21,27})for(int z:new int[]{9,16,22})p.put(x,7,z,Blocks.SEA_LANTERN);
        p.box(4,1,17,13,1,17,Blocks.RED_CONCRETE);p.box(19,1,17,28,1,17,Blocks.RED_CONCRETE);
        p.box(4,2,17,13,2,17,Blocks.SMOOTH_QUARTZ_SLAB);p.box(19,2,17,28,2,17,Blocks.SMOOTH_QUARTZ_SLAB);
        for(int x:new int[]{6,11,21,26}){p.box(x-1,5,18,x+1,6,18,Blocks.BLACK_CONCRETE);p.put(x,5,17,Blocks.YELLOW_CONCRETE);}
        for(int x:new int[]{5,9,23,27}){p.put(x,1,24,Blocks.SMOKER);p.put(x,2,24,Blocks.IRON_TRAPDOOR);}
        p.put(3,1,22,Furniture.FRIDGE.get());p.put(29,1,22,Furniture.DISHWASHER.get());p.put(12,1,24,Blocks.CRAFTING_TABLE);
        p.put(19,1,24,Blocks.CAULDRON);p.put(21,1,24,Blocks.BARREL);
        for(int x:new int[]{3,29})p.put(x,1,6,Blocks.COMPOSTER);
        for(int x:new int[]{4,10,22,28})p.box(x,0,1,x,0,3,Blocks.WHITE_CONCRETE);
        return p;
    }
    static Plan shrekSwamp(){''')
a='            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");'
edit('GothicEgg.java',a,'''            if(p.w==33){
                FastFoodGuest clerk=Noctis.MCD_CASHIER.get().create(l);
                if(clerk!=null){BlockPos q=pos(10,1,19);clerk.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+180,0);clerk.setHome(q);if(l.noCollision(clerk))l.addFreshEntity(clerk);}
            }
'''+a)
(java/'FastFoodGuest.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
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
public class FastFoodGuest extends PathfinderMob{
    BlockPos home;int speech,pose;
    static final String[] LINES={"Il mio grande piano? Sbloccare la macchina del gelato.","Non riesco a far rispettare nemmeno la fila.","Ho perso il potere. Adesso ho il turno di chiusura.","Patatine grandi? Anche il mio ego era grande."};
    public FastFoodGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,40).add(Attributes.MOVEMENT_SPEED,.22);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(2,new RandomLookAroundGoal(this));}
    public void setHome(BlockPos p){home=p;}
    @Override public void tick(){super.tick();if(speech>0)speech--;if(pose>0)pose--;if(level() instanceof ServerLevel l&&home!=null&&tickCount%20==0&&distanceToSqr(home.getX()+.5,home.getY(),home.getZ()+.5)>1.5)getNavigation().moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.8);}
    void say(ServerLevel l,String s){speech=100;NpcDialogue.say(l,Component.literal("Mussolini: "+s));}
    Item product(int i){return switch(i){case 0->Noctis.MCD_BURGER.get();case 1->Noctis.MCD_FRIES.get();case 2->Noctis.MCD_NUGGETS.get();default->Noctis.MCD_COLA.get();};}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        ItemStack s=p.getItemInHand(h);if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET))return InteractionResult.PASS;
        if(level() instanceof ServerLevel l){String key="NoctisMcDMenu";int n=Math.floorMod(p.getPersistentData().getInt(key),5);
            if(s.isEmpty()){
                if(p.isShiftKeyDown()){n=(n+1)%5;p.getPersistentData().putInt(key,n);}
                p.sendSystemMessage(Component.literal("Menu: ").append(n==4?Component.literal("Menu completo (hamburger, patatine, cola)"):product(n).getDescription()).append(n==4?" | 3 pepite d'oro":" | 1 pepita d'oro").append(" | Shift + clic a mano vuota per cambiare."));
                if(speech==0)say(l,LINES[random.nextInt(LINES.length)]);
            }else{
                int cost=n==4?3:1;
                if(!p.getAbilities().instabuild&&s.getCount()<cost){p.displayClientMessage(Component.literal("Servono 3 pepite."),true);return InteractionResult.CONSUME;}
                if(!p.getAbilities().instabuild)s.shrink(cost);
                Item[] items=n==4?new Item[]{Noctis.MCD_BURGER.get(),Noctis.MCD_FRIES.get(),Noctis.MCD_COLA.get()}:new Item[]{product(n)};
                for(Item item:items){ItemStack out=new ItemStack(item);if(!p.getInventory().add(out))p.drop(out,false);}
                l.broadcastEntityEvent(this,(byte)115);playSound(SoundEvents.VILLAGER_YES,.8f,1.2f);if(speech==0)say(l,"Ordine pronto. Avanti il prossimo!");
            }
        }return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==115){pose=24;return;}super.handleEntityEvent(id);}
    public float serving(){return pose<=0?0:(float)Math.sin(pose*Math.PI/24);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(home!=null)t.putLong("Home",home.asLong());}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);home=t.contains("Home")?BlockPos.of(t.getLong("Home")):null;}
}''',encoding='utf-8')
(java/'FastFoodClient.java').write_text('''package it.noctis.magic;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class FastFoodClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"mcd_cashier"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,()->{
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot();r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        r.getChild("head").addOrReplaceChild("cap",CubeListBuilder.create().texOffs(64,0).addBox(-4.2f,-9,-4.2f,8,2,8).texOffs(64,12).addBox(-4,-7.4f,-7,8,1,4),PartPose.ZERO);
        r.getChild("body").addOrReplaceChild("apron",CubeListBuilder.create().texOffs(64,32).addBox(-3.5f,3,-2.4f,7,10,1),PartPose.ZERO);
        return LayerDefinition.create(m,128,128);
    });}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MCD_CASHIER.get(),Renderer::new);}
    static class Model extends HumanoidModel<FastFoodGuest>{Model(ModelPart p){super(p);}@Override public void setupAnim(FastFoodGuest e,float l,float a,float age,float yaw,float pitch){super.setupAnim(e,l,a,age,yaw,pitch);rightArm.xRot-=e.serving()*1.3f;}}
    static class Renderer extends MobRenderer<FastFoodGuest,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.35f);}@Override public ResourceLocation getTextureLocation(FastFoodGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/mcd_cashier.png");}}
}''',encoding='utf-8')
S=4;W=128*S;pix=bytearray(W*W*4)
def rect(x,y,w,h,col):
    for j in range(y*S,(y+h)*S):
        for i in range(x*S,(x+w)*S):
            g=.82+.18*math.sin((i-x*S)/max(1,w*S)*math.pi);o=(j*W+i)*4;pix[o:o+4]=bytes((*[int(a*g) for a in col],255))
skin=(220,175,145);red=(180,31,40);gold=(240,191,56)
rect(0,0,128,128,(53,49,51));rect(0,0,32,16,skin);rect(0,0,32,7,(191,146,120))
for x in (9,13):
    rect(x,10,2,1,(88,57,46));rect(x,11,2,1,(239,228,216));rect(x+1,11,1,1,(46,36,33))
rect(10,14,4,1,(124,77,67))
rect(16,16,24,16,red);rect(40,16,16,12,red);rect(40,28,16,4,skin);rect(0,16,16,16,(52,48,49));rect(64,0,40,26,red);rect(64,32,32,16,(65,59,56));rect(66,34,3,2,gold)
png(assets/'textures/entity/mcd_cashier.png',W,W,pix);dump(assets/'models/item/mcd_cashier_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for n in [f[0] for f in foods]+['mcdonalds_egg']:
    W=32;pix=bytearray(W*W*4)
    for y in range(W):
        for x in range(W):
            c=None
            if n=='mcd_burger':
                if ((x-16)/13)**2+((y-14)/9)**2<1 and y<16:c=(213,150,62)
                if 4<x<28 and 15<=y<=24:c={15:(75,130,51),16:(181,40,41),17:(244,191,58),18:(92,48,31),19:(92,48,31)}.get(y,(208,141,58))
                if c and y<14 and (x*3+y*7)%19==0:c=(249,221,158)
            elif n=='mcd_fries':
                if 5<x<27 and 14<y<29 and abs(x-16)<11-(y-15)*.13:c=(188,35,40)
                if 6<x<26 and 4+(x*7)%9<y<18 and x%5!=0:c=(239,189,67)
                if 12<x<20 and 20<y<25 and (x%3==0 or y==21):c=(246,204,65)
            elif n=='mcd_cola':
                if 8<x<24 and 9<y<29 and abs(x-16)<8-(y-10)*.12:c=(173,35,41)
                if 7<x<25 and 8<y<12:c=(231,232,221)
                if 17<x<20 and 2<y<9:c=(240,221,214)
            elif n=='mcd_nuggets':
                for a,b in ((10,11),(21,13),(15,23)):
                    if ((x-a)/6)**2+((y-b)/5)**2<1:c=(204+(x+y)%4*8,137+(x*y)%4*8,60)
            else:
                d=((x-15.5)/12)**2+((y-16)/14)**2
                if d<=1:
                    c=(230,189,56) if d>.82 else (187,34,40)
                    if 8<x<24 and 9<y<24 and (x in (9,10,15,16,21,22) or y in (10,11)):c=(255,215,60)
            if c:pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
    png(assets/'textures/item'/f'{n}.png',W,W,pix);dump(assets/'models/item'/f'{n}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/'+n}})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    d['entity.noctismagic.mcd_cashier']='Mussolini - Cassiere' if lang=='it_it' else 'Mussolini - Cashier';d['item.noctismagic.mcd_cashier_spawn_egg']='Uovo generatore: Mussolini' if lang=='it_it' else 'Mussolini Spawn Egg'
    d['item.noctismagic.mcdonalds_egg']="Uovo del McDonald's" if lang=='it_it' else "McDonald's Egg"
    for n,it,en,f in foods:d['item.noctismagic.'+n]=it if lang=='it_it' else en
    dump(p,d)
print('Fast food structure, satirical cashier, four food items and menu trades installed')
