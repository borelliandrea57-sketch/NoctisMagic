"""1.2.3: a bakery structure egg with two satirical baker NPCs and useful counters."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<BakeryClerk>> BAKER_HITLER=ENTITIES.register("baker_hitler",()->EntityType.Builder.<BakeryClerk>of(BakeryClerk::new,MobCategory.CREATURE).sized(.6f,1.95f).clientTrackingRange(10).build(ID+":baker_hitler"));
    public static final RegistryObject<EntityType<BakeryClerk>> BAKER_STALIN=ENTITIES.register("baker_stalin",()->EntityType.Builder.<BakeryClerk>of(BakeryClerk::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":baker_stalin"));
    public static final RegistryObject<Item> BAKERY_EGG=ITEMS.register("bakery_egg",()->new GothicEgg(false,true));
    public static final RegistryObject<Item> PASTRY_EGG=ITEMS.register("pastry_egg",()->new GothicEgg(false,true,true));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',a,'e.put(BAKER_HITLER.get(),BakeryClerk.attributes().build());e.put(BAKER_STALIN.get(),BakeryClerk.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(BAKERY_EGG.get());e.accept(PASTRY_EGG.get());')
edit('GothicEgg.java','private final boolean castle;','private final boolean castle,bakery,pastry;')
edit('GothicEgg.java','public GothicEgg(boolean castle){super(new Item.Properties().stacksTo(1));this.castle=castle;}','public GothicEgg(boolean castle){this(castle,false);} public GothicEgg(boolean castle,boolean bakery){this(castle,bakery,false);} public GothicEgg(boolean castle,boolean bakery,boolean pastry){super(new Item.Properties().stacksTo(1));this.castle=castle;this.bakery=bakery;this.pastry=pastry;}')
edit('GothicEgg.java','Plan plan=castle?castle():cathedral();','Plan plan=bakery?bakery(pastry):castle?castle():cathedral();')
edit('GothicEgg.java','p.w==91?Noctis.CASTLE_EGG.get():Noctis.CATHEDRAL_EGG.get()','p.w==25?(p.name.startsWith("Pasticceria")?Noctis.PASTRY_EGG.get():Noctis.BAKERY_EGG.get()):p.w==91?Noctis.CASTLE_EGG.get():Noctis.CATHEDRAL_EGG.get()')
edit('GothicEgg.java','    static Plan cathedral(){','''    static Plan bakery(boolean pastry){
        Plan p=new Plan(25,23,13,pastry?"Pasticceria dei Due Brontoloni":"Il Forno dei Due Brontoloni");
        // Warm brick exterior, striped awning, storefront windows, tiled floor.
        for(int x=0;x<25;x++)for(int z=0;z<23;z++)p.put(x,0,z,x==0||x==24||z==0||z==22?Blocks.STONE_BRICKS:((x+z)%2==0?Blocks.WHITE_TERRACOTTA:Blocks.BROWN_TERRACOTTA));
        p.walls(1,1,3,23,7,21,pastry?Blocks.SMOOTH_QUARTZ:Blocks.BRICKS);
        for(int x:new int[]{1,23})for(int z:new int[]{3,21})p.box(x,1,z,x,7,z,Blocks.DARK_OAK_LOG);
        for(int x=3;x<=21;x++)if(x<10||x>14){p.box(x,2,3,x,5,3,Blocks.GLASS);p.put(x,1,3,Blocks.QUARTZ_BLOCK);}
        p.box(11,1,3,13,3,3,Blocks.AIR);
        for(int x=2;x<=22;x++){p.put(x,6,3,Blocks.SMOOTH_QUARTZ);p.put(x,5,2,x%2==0?(pastry?Blocks.PINK_WOOL:Blocks.RED_WOOL):Blocks.WHITE_WOOL);p.put(x,5,1,x%2==0?(pastry?Blocks.PINK_WOOL:Blocks.RED_WOOL):Blocks.WHITE_WOOL);p.put(x,4,1,x%2==0?(pastry?Blocks.PINK_WOOL:Blocks.RED_WOOL):Blocks.WHITE_WOOL);}
        for(int z=6;z<=18;z+=6)for(int x:new int[]{1,23})p.box(x,2,z,x,5,z+2,Blocks.GLASS);
        p.box(1,8,3,23,8,21,Blocks.SPRUCE_PLANKS);
        for(int k=0;k<4;k++)p.ring(k,9+k,2+k,24-k,22-k,Blocks.DARK_OAK_STAIRS);
        p.box(4,12,6,20,12,18,Blocks.DARK_OAK_PLANKS);
        p.box(18,8,18,20,12,20,Blocks.BRICKS);
        // Customer area: tables, seating, storage and lit display cases.
        for(int x:new int[]{5,19})for(int z:new int[]{7,11}){
            p.put(x,1,z,Blocks.DARK_OAK_FENCE);p.put(x,2,z,Blocks.DARK_OAK_PRESSURE_PLATE);
            p.stair(x-2,1,z,Blocks.SPRUCE_STAIRS,Direction.WEST);p.stair(x+2,1,z,Blocks.SPRUCE_STAIRS,Direction.EAST);
            p.put(x,3,z,Blocks.FLOWER_POT);
        }
        p.box(3,1,14,21,1,14,Blocks.SMOOTH_QUARTZ);
        for(int x=3;x<=21;x++){p.put(x,2,14,Blocks.GLASS);if(x%4==0)p.put(x,2,14,Blocks.CAKE);}
        p.box(11,1,14,13,2,14,Blocks.AIR);
        p.put(4,1,13,Furniture.STEAM_CABINET.get());p.put(20,1,13,Furniture.MODERN_CABINET.get());
        for(int x=3;x<=21;x+=3){p.put(x,1,20,Blocks.FURNACE.defaultBlockState().setValue(FurnaceBlock.FACING,Direction.NORTH));p.put(x,2,20,Blocks.SMOKER.defaultBlockState().setValue(SmokerBlock.FACING,Direction.NORTH));p.put(x,3,20,Blocks.BARREL.defaultBlockState().setValue(BarrelBlock.FACING,Direction.NORTH));}
        p.put(3,1,18,Blocks.CRAFTING_TABLE);p.put(21,1,18,Furniture.FRIDGE.get());
        p.box(5,1,19,8,1,19,Blocks.SPRUCE_PLANKS);p.box(16,1,19,19,1,19,Blocks.SPRUCE_PLANKS);
        p.put(6,2,19,Blocks.CAKE);p.put(17,2,19,Blocks.CAKE);
        for(int x:new int[]{5,12,19})for(int z:new int[]{8,16}){p.put(x,7,z,Blocks.CHAIN);p.put(x,6,z,Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING,true));}
        if(pastry){
            for(int x=3;x<=21;x++)if(x<11||x>13){p.put(x,1,14,Blocks.PINK_TERRACOTTA);p.put(x,2,14,x%3==0?Blocks.CAKE:Blocks.GLASS);}
            for(int x:new int[]{5,19})for(int z:new int[]{7,11})p.put(x,0,z,Blocks.PINK_GLAZED_TERRACOTTA);
            p.put(3,1,17,Furniture.MODERN_LAMP.get());p.put(21,1,17,Furniture.MODERN_LAMP.get());
        }else{
            for(int x=3;x<=21;x+=3)p.put(x,4,20,Blocks.HAY_BLOCK);
            p.put(3,1,17,Blocks.BARREL);p.put(21,1,17,Blocks.BARREL);
        }
        return p;
    }
    static Plan cathedral(){''')
# Install the two clerks only when the queued structure has finished.
edit('GothicEgg.java','            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");','''            if(p.w==25){
                for(int i=0;i<2;i++){
                    BakeryClerk clerk=(i==0?Noctis.BAKER_HITLER.get():Noctis.BAKER_STALIN.get()).create(l);
                    if(clerk!=null){BlockPos q=pos(i==0?8:16,1,16);clerk.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+180,0);clerk.setPersistenceRequired();if(l.noCollision(clerk))l.addFreshEntity(clerk);}
                }
            }
            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");''')
write('BakeryClerk.java','''package it.noctis.magic;
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
public class BakeryClerk extends PathfinderMob{
    private int cooldown;
    public BakeryClerk(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public boolean stalin(){return getType()==Noctis.BAKER_STALIN.get();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,40).add(Attributes.MOVEMENT_SPEED,.15).add(Attributes.KNOCKBACK_RESISTANCE,.8);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(2,new RandomLookAroundGoal(this));}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}
    static final String[] H={"Questi forni mi ricordano i bei tempi... quando riuscivo ancora a non bruciare il pane.","Avevo un piano per il pane. Il lievito non era d'accordo.","Questa brioche e' venuta storta. Per fortuna non dirige un esercito.","Il mio unico ordine oggi: togliere il pane dal forno prima che bruci."};
    static final String[] S={"Mi sono venduto al capitalismo. Una pepita per il prossimo biscotto!","Il piano quinquennale delle brioche e' gia in ritardo.","La torta e' di tutti, ma la fetta piu grande l'ho gia mangiata.","Il comitato del lievito ha approvato il pane. Purtroppo e' duro come una pietra."};
    @Override public void tick(){super.tick();if(cooldown>0)cooldown--;if(level() instanceof ServerLevel l&&cooldown==0&&tickCount%160==0&&l.getNearestPlayer(this,9)!=null&&random.nextInt(4)==0){cooldown=200;String[] lines=stalin()?S:H;say(l,lines[random.nextInt(lines.length)]);}}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        ItemStack s=p.getItemInHand(h);if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET))return InteractionResult.PASS;
        if(level() instanceof ServerLevel l&&cooldown<120){
            cooldown=140;
            if(s.is(Items.GOLD_NUGGET)){
                if(!p.getAbilities().instabuild)s.shrink(1);
                ItemStack food=stalin()?new ItemStack(p.isShiftKeyDown()?Items.PUMPKIN_PIE:Items.COOKIE,p.isShiftKeyDown()?1:4):new ItemStack(p.isShiftKeyDown()?Items.CAKE:Items.BREAD,p.isShiftKeyDown()?1:3);
                if(!p.getInventory().add(food))p.drop(food,false);
                say(l,stalin()?"Un dolce per il cliente. Non per il comitato!":"Ecco il suo ordine. Almeno questo ha funzionato.");
                playSound(SoundEvents.VILLAGER_YES,.6f,1.1f);
            }else{String[] lines=stalin()?S:H;say(l,lines[random.nextInt(lines.length)]);p.sendSystemMessage(Component.literal(stalin()?"1 pepita: 4 biscotti. Shift + pepita: torta di zucca.":"1 pepita: 3 pani. Shift + pepita: torta."));}
        }return InteractionResult.sidedSuccess(level().isClientSide);
    }
}''')
write('BakeryClient.java','''package it.noctis.magic;
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
public class BakeryClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"bakery_clerk"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,BakeryClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.BAKER_HITLER.get(),c->new Renderer(c,false));e.registerEntityRenderer(Noctis.BAKER_STALIN.get(),c->new Renderer(c,true));}
    static LayerDefinition mesh(){MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot();
        r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        r.getChild("head").addOrReplaceChild("chefhat",CubeListBuilder.create().texOffs(64,0).addBox(-4,-10,-4,8,2,8).texOffs(64,12).addBox(-5,-15,-5,10,5,10),PartPose.ZERO);
        r.getChild("body").addOrReplaceChild("apron",CubeListBuilder.create().texOffs(64,30).addBox(-3.5f,1,-2.5f,7,15,1),PartPose.ZERO);
        return LayerDefinition.create(m,128,128);}
    static class Renderer extends MobRenderer<BakeryClerk,HumanoidModel<BakeryClerk>>{
        final boolean stalin;Renderer(EntityRendererProvider.Context c,boolean s){super(c,new HumanoidModel<>(c.bakeLayer(L)),.35f);stalin=s;}
        @Override public ResourceLocation getTextureLocation(BakeryClerk e){return new ResourceLocation(Noctis.ID,"textures/entity/"+(stalin?"baker_stalin":"baker_hitler")+".png");}
    }
}''')
def png(path,w,h,pix):
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
for k,name in enumerate(('baker_hitler','baker_stalin')):
    S=4;W=128*S;pix=bytearray(W*W*4)
    def rect(x,y,w,h,c):
        for j in range(y*S,(y+h)*S):
            for i in range(x*S,(x+w)*S):
                g=.84+.16*math.sin((i-x*S)/max(1,w*S)*math.pi);o=(j*W+i)*4;pix[o:o+4]=bytes((*[int(a*g) for a in c],255))
    skin=(221,181,146) if k==0 else (218,173,137);hair=(52,41,35) if k==0 else (71,67,63)
    rect(0,0,128,128,(93,76,61));rect(0,0,32,16,skin);rect(0,0,32,8,hair);rect(0,8,8,8,hair);rect(16,8,16,8,hair)
    rect(8,8,8,2,hair)
    if k==0:rect(8,10,2,1,hair)
    for ex in (9,13):
        rect(ex,10,2,1,hair);rect(ex,11,2,1,(239,235,225));rect(ex+1,11,1,1,(55,48,43))
    rect(11 if k==0 else 9,13,2 if k==0 else 6,1,hair);rect(11,14,2,1,(135,84,75))
    rect(16,16,24,16,(218,210,190));rect(40,16,16,16,(222,214,195));rect(40,27,16,5,skin)
    rect(0,16,16,16,(60,53,49));rect(0,28,16,4,(31,29,28))
    rect(64,0,64,29,(239,231,211));rect(64,30,24,20,(236,226,201));rect(65,38,6,3,(197,181,150))
    png(assets/'textures/entity'/f'{name}.png',W,W,pix)
W=32;pix=bytearray(W*W*4)
for y in range(W):
    for x in range(W):
        u=(x-15.5)/12;v=(y-16)/14
        if u*u+v*v>1:continue
        c=(155,90,48) if u*u+v*v>.76 else (233,196,134)
        if 7<x<25 and 12<y<24:c=(171,104,55)
        if 7<x<25 and 10<y<14:c=(196,40,51) if x%4<2 else (246,231,204)
        if 13<x<18 and 17<y<24:c=(82,55,39)
        if 8<x<13 and 16<y<20 or 18<x<24 and 16<y<20:c=(244,215,151)
        pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
png(assets/'textures/item/bakery_egg.png',W,W,pix)
for i in range(0,len(pix),4):
    if pix[i+3] and pix[i]>100 and pix[i]>pix[i+1]*1.2:pix[i:i+3]=bytes((225,145,178))
png(assets/'textures/item/pastry_egg.png',W,W,pix)
(assets/'models/item/pastry_egg.json').write_text('{"parent":"minecraft:item/generated","textures":{"layer0":"noctismagic:item/pastry_egg"}}')
(assets/'models/item/bakery_egg.json').write_text('{"parent":"minecraft:item/generated","textures":{"layer0":"noctismagic:item/bakery_egg"}}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['item.noctismagic.bakery_egg']='Uovo del Panificio - Il Forno dei Due Brontoloni' if lang=='it_it' else 'Two Grumpy Bakers Bakery Egg'
    d['item.noctismagic.pastry_egg']='Uovo della Pasticceria' if lang=='it_it' else 'Pastry Shop Egg'
    d['entity.noctismagic.baker_hitler']='Adolf Hitler - Panettiere' if lang=='it_it' else 'Adolf Hitler - Baker'
    d['entity.noctismagic.baker_stalin']='Stalin - Pasticciere' if lang=='it_it' else 'Stalin - Pastry Chef'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Bakery egg, safe building queue, two satirical bakers and food trades installed')
