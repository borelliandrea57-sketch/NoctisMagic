"""1.2.0: useful furniture, steampunk castle, Michael Jackson, Lelouch and C.C."""
from pathlib import Path
import sys,json,math,struct,zlib,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(path,w,h,pix):
    path.parent.mkdir(parents=True,exist_ok=True)
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h));path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
# Model cuboids, distinct materials, facing and functional categories.
def legs(m):return [(x,0,z,x+2,12,z+2,m) for x in (1,13) for z in (1,13)]
items={
'fridge':('Frigorifero','Refrigerator',1,[(1,0,2,15,16,15,'white'),(2,1,1,14,10,2,'steel'),(2,11,1,14,15,2,'steel'),(11,4,0,13,8,1,'dark'),(11,12,0,13,14,1,'dark')]),
'modern_cabinet':('Mobile contenitore moderno','Modern cabinet',1,[(1,1,2,15,15,15,'white'),(1,15,1,15,16,15,'dark'),(2,2,1,7,14,2,'gray'),(9,2,1,14,14,2,'gray'),(6,7,0,7,10,1,'steel'),(9,7,0,10,10,1,'steel')]),
'intercom':('Citofono','Intercom',2,[(4,3,11,12,14,15,'white'),(5,9,10,11,13,11,'dark'),(5,4,10,11,8,11,'steel'),(7,5,9,9,7,10,'blue')]),
'modern_desk':('Scrivania moderna','Modern desk',0,legs('steel')+[(0,12,0,16,14,16,'white'),(10,5,9,15,12,15,'gray')]),
'modern_chair':('Sedia moderna','Modern chair',0,[(x,0,z,x+2,6,z+2,'steel') for x in (3,11) for z in (3,11)]+[(2,6,2,14,8,14,'gray'),(3,8,12,13,15,14,'gray')]),
'modern_sofa':('Divanetto moderno','Modern sofa',0,[(1,0,2,15,3,15,'dark'),(2,3,2,14,8,13,'gray'),(1,8,11,15,15,15,'gray'),(0,5,2,2,11,13,'white'),(14,5,2,16,11,13,'white')]),
'modern_lamp':('Lampada LED','LED lamp',3,[(4,0,4,12,1,12,'dark'),(7,1,7,9,12,9,'steel'),(3,12,3,13,15,13,'light'),(3,15,3,13,16,13,'dark')]),
'modern_screen':('Schermo moderno','Modern display',0,[(4,0,6,12,1,11,'dark'),(7,1,7,9,4,9,'steel'),(1,4,5,15,14,8,'dark'),(2,5,4,14,13,5,'blue')]),
'steam_cabinet':('Credenza steampunk','Steampunk cabinet',1,[(1,0,1,15,16,15,'wood'),(0,14,0,16,16,16,'brass'),(2,2,0,7,13,1,'copper'),(9,2,0,14,13,1,'copper'),(6,6,0,8,8,1,'brass'),(8,6,0,10,8,1,'brass')]),
'steam_workbench':('Banco da officina steampunk','Steampunk workbench',5,legs('wood')+[(0,12,0,16,15,16,'wood'),(0,14,0,16,15,16,'brass'),(2,15,2,7,16,8,'copper')]),
'steam_lamp':('Lampada a vapore','Steam lamp',3,[(3,0,3,13,2,13,'brass'),(6,2,6,10,10,10,'copper'),(3,10,3,13,14,13,'light'),(2,14,2,14,16,14,'brass'),(2,10,2,3,14,3,'dark'),(13,10,13,14,14,14,'dark')]),
'steam_clock':('Orologio steampunk','Steampunk clock',4,[(2,0,9,14,16,15,'wood'),(2,5,7,14,15,9,'brass'),(3,6,6,13,14,7,'dial'),(7,8,5,8,12,6,'dark'),(8,9,5,11,10,6,'dark'),(6,1,7,10,5,9,'copper')]),
'steam_pipe':('Tubature in rame','Copper pipes',0,[(6,0,6,10,16,10,'copper'),(4,2,4,12,4,12,'brass'),(4,12,4,12,14,12,'brass'),(8,7,0,16,11,8,'copper'),(13,6,0,16,12,10,'brass')]),
'steam_gear':('Ingranaggi ornamentali','Decorative gears',0,[(2,2,12,14,14,15,'dark'),(4,4,9,12,12,12,'brass'),(6,1,9,10,15,12,'brass'),(1,6,9,15,10,12,'brass'),(6,6,8,10,10,9,'copper')]),
'steam_boiler':('Caldaia steampunk','Steampunk boiler',0,[(2,0,2,14,2,14,'dark'),(3,2,3,13,13,13,'copper'),(2,5,2,14,7,14,'brass'),(2,11,2,14,13,14,'brass'),(6,13,6,10,16,10,'steel'),(5,7,1,11,11,3,'dial'),(7,8,0,8,10,1,'dark')]),
'steam_gramophone':('Grammofono steampunk','Steampunk gramophone',0,[(2,0,2,14,5,14,'wood'),(3,5,3,13,6,13,'brass'),(5,6,5,11,7,11,'dark'),(11,6,10,13,11,12,'copper'),(7,10,7,14,13,14,'brass'),(4,12,4,16,16,16,'brass'),(6,15,6,14,16,14,'dark')])}
decl=''
for n,(_,_,k,_) in items.items():
    expr='new Storage()' if k==1 else f'new FurnitureBlock({k})'
    decl+=f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});\n    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));\n'
stores=','.join(n.upper()+'.get()' for n,(_,_,k,_) in items.items() if k==1)
write('Furniture.java','''package it.noctis.magic;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.*;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;
public class Furniture{
    static final DeferredRegister<BlockEntityType<?>> TYPES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,Noctis.ID);
'''+decl+'''
    static final RegistryObject<BlockEntityType<StorageEntity>> STORAGE=TYPES.register("furniture_storage",()->BlockEntityType.Builder.of(StorageEntity::new,'''+stores+''').build(null));
    static void register(IEventBus bus){TYPES.register(bus);}
    public static class FurnitureBlock extends Block{
        final int kind;
        static final DirectionProperty FACING=HorizontalDirectionalBlock.FACING;
        static final BooleanProperty LIT=BlockStateProperties.LIT;
        FurnitureBlock(int kind){super(BlockBehaviour.Properties.of().strength(1.8f).noOcclusion().lightLevel(s->kind==3&&s.getValue(LIT)?15:0));this.kind=kind;registerDefaultState(stateDefinition.any().setValue(FACING,Direction.NORTH).setValue(LIT,kind==3));}
        @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(FACING,LIT);}
        @Override public BlockState getStateForPlacement(BlockPlaceContext c){return defaultBlockState().setValue(FACING,c.getHorizontalDirection().getOpposite());}
        @Override public BlockState rotate(BlockState s,Rotation r){return s.setValue(FACING,r.rotate(s.getValue(FACING)));}
        @Override public BlockState mirror(BlockState s,Mirror m){return rotate(s,m.getRotation(s.getValue(FACING)));}
        @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){
            if(kind==2)return switch(s.getValue(FACING)){case NORTH->box(4,3,9,12,14,16);case SOUTH->box(4,3,0,12,14,7);case EAST->box(0,3,4,7,14,12);default->box(9,3,4,16,14,12);};
            if(kind==3)return box(3,0,3,13,16,13);
            return box(1,0,1,15,16,15);
        }
        @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player player,InteractionHand h,BlockHitResult hit){
            if(kind==0||kind==1)return InteractionResult.PASS;
            if(!l.isClientSide){
                if(kind==2){l.playSound(null,p,SoundEvents.NOTE_BLOCK_BELL.value(),net.minecraft.sounds.SoundSource.BLOCKS,1,1.3f);if(l instanceof ServerLevel sl)NpcDialogue.say(sl,Component.literal("Citofono: "+player.getDisplayName().getString()+" ha suonato!"));}
                else if(kind==3)l.setBlock(p,s.cycle(LIT),3);
                else if(kind==4){long t=(l.getDayTime()+6000)%24000;player.displayClientMessage(Component.literal(String.format("Orologio: %02d:%02d",t/1000,(t%1000)*60/1000)),true);}
                else if(kind==5)player.openMenu(new SimpleMenuProvider((id,inv,pl)->new CraftingMenu(id,inv,ContainerLevelAccess.create(l,p)){
                    @Override public boolean stillValid(Player q){return q.distanceToSqr(p.getX()+.5,p.getY()+.5,p.getZ()+.5)<=64&&l.getBlockState(p).is(STEAM_WORKBENCH.get());}
                },Component.literal("Officina steampunk")));
            }return InteractionResult.sidedSuccess(l.isClientSide);
        }
    }
    public static class Storage extends FurnitureBlock implements EntityBlock{
        Storage(){super(1);}
        @Override public BlockEntity newBlockEntity(BlockPos p,BlockState s){return new StorageEntity(p,s);}
        @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player player,InteractionHand h,BlockHitResult hit){if(!l.isClientSide&&l.getBlockEntity(p) instanceof StorageEntity be)player.openMenu(be);return InteractionResult.sidedSuccess(l.isClientSide);}
        @Override public void onRemove(BlockState s,Level l,BlockPos p,BlockState n,boolean moving){if(!s.is(n.getBlock())&&l.getBlockEntity(p) instanceof StorageEntity be)Containers.dropContents(l,p,be);super.onRemove(s,l,p,n,moving);}
    }
    public static class StorageEntity extends BlockEntity implements Container,MenuProvider{
        final NonNullList<ItemStack> items=NonNullList.withSize(27,ItemStack.EMPTY);
        StorageEntity(BlockPos p,BlockState s){super(STORAGE.get(),p,s);}
        @Override public int getContainerSize(){return items.size();}
        @Override public boolean isEmpty(){for(ItemStack s:items)if(!s.isEmpty())return false;return true;}
        @Override public ItemStack getItem(int i){return items.get(i);}
        @Override public ItemStack removeItem(int i,int n){ItemStack s=ContainerHelper.removeItem(items,i,n);if(!s.isEmpty())setChanged();return s;}
        @Override public ItemStack removeItemNoUpdate(int i){ItemStack s=ContainerHelper.takeItem(items,i);setChanged();return s;}
        @Override public void setItem(int i,ItemStack s){items.set(i,s);if(s.getCount()>getMaxStackSize())s.setCount(getMaxStackSize());setChanged();}
        @Override public boolean stillValid(Player p){return level!=null&&level.getBlockEntity(worldPosition)==this&&p.distanceToSqr(worldPosition.getX()+.5,worldPosition.getY()+.5,worldPosition.getZ()+.5)<=64;}
        @Override public void clearContent(){items.clear();setChanged();}
        @Override public void load(CompoundTag t){super.load(t);items.clear();ContainerHelper.loadAllItems(t,items);}
        @Override protected void saveAdditional(CompoundTag t){super.saveAdditional(t);ContainerHelper.saveAllItems(t,items);}
        @Override public Component getDisplayName(){return getBlockState().getBlock().getName();}
        @Override public AbstractContainerMenu createMenu(int id,Inventory inv,Player p){return ChestMenu.threeRows(id,inv,this);}
    }
}''')
edit('VampireLife.java','BLOCKS.register(bus);EFFECTS.register(bus);','Furniture.register(bus);BLOCKS.register(bus);EFFECTS.register(bus);')
edit('Noctis.java','if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)','if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join(f'e.accept(Furniture.{n.upper()}_ITEM.get());' for n in items)+'}if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)')
edit('GothicEgg.java','        spire(p,cx,61,50,6,23);\n        return p;','''        spire(p,cx,61,50,6,23);
        for(int z=40;z<=53;z+=6){p.put(20,13,z,Furniture.STEAM_WORKBENCH.get());p.put(29,13,z,Furniture.STEAM_BOILER.get());p.put(29,15,z,Furniture.STEAM_PIPE.get());p.put(19,15,z,Furniture.STEAM_GEAR.get());}
        for(int z=63;z<=83;z+=8){p.put(21,13,z,Furniture.STEAM_GRAMOPHONE.get());p.put(29,13,z,Furniture.STEAM_LAMP.get());}
        for(int z=40;z<=54;z+=7){p.put(22,1,z,Furniture.STEAM_LAMP.get());p.put(28,1,z,Furniture.STEAM_CABINET.get());}
        p.put(69,1,65,Furniture.STEAM_CLOCK.get());p.put(62,1,65,Furniture.STEAM_CABINET.get());p.put(69,1,80,Furniture.STEAM_LAMP.get());
        for(int z=41;z<=73;z+=8){p.put(34,13,z,Furniture.STEAM_LAMP.get());p.put(56,13,z,Furniture.STEAM_LAMP.get());}
        return p;''')
palette={'white':(226,232,234),'steel':(151,165,176),'dark':(30,35,42),'gray':(95,107,120),'blue':(35,112,167),'light':(247,221,139),'wood':(75,43,28),'brass':(191,140,55),'copper':(158,79,43),'dial':(221,198,153)}
for mat,col in palette.items():
    pix=bytearray(32*32*4)
    for y in range(32):
        for x in range(32):
            g=.90+.08*math.sin(x*.25)+.04*math.cos(y*.8)
            if mat=='wood':g=.76+.23*math.sin(x*1.7+math.sin(y*.2))**2
            if mat in ('steel','brass','copper'):g=.75+.32*math.exp(-((x-10)/6)**2)+.04*math.sin(y*2)
            if min(x,y,31-x,31-y)<1:g*=.65
            c=tuple(max(0,min(255,int(a*g))) for a in col)
            if mat=='dial' and math.hypot(x-15.5,y-15.5)>14:c=(93,66,41)
            pix[(y*32+x)*4:(y*32+x)*4+4]=bytes((*c,255))
    png(assets/'textures/block'/f'furniture_{mat}.png',32,32,pix)
extras=['snow_block','white_wool','note_block','stick','oak_stairs','gray_wool','glass_pane','black_dye','gold_ingot','crafting_table','chain','gold_nugget','iron_bars','iron_nugget','cauldron','jukebox']
for (n,(it,en,k,boxes)),extra in zip(items.items(),extras):
    textures={m:f'noctismagic:block/furniture_{m}' for m in palette};textures['particle']=textures['brass' if n.startswith('steam') else 'gray']
    el=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]
    dump(assets/'models/block'/f'{n}.json',{'textures':textures,'elements':el,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]},'ground':{'translation':[0,3,0],'scale':[.25,.25,.25]},'fixed':{'scale':[.5,.5,.5]}}})
    dump(assets/'models/item'/f'{n}.json',{'parent':f'noctismagic:block/{n}'})
    dump(assets/'blockstates'/f'{n}.json',{'variants':{f'facing={d},lit={lit}':{'model':f'noctismagic:block/{n}','y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}})
    dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':f'noctismagic:{n}'}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
    ingredient='copper_ingot' if n.startswith('steam') else 'iron_ingot'
    middle='glowstone' if k==3 else 'redstone' if k==2 else 'chest' if k==1 else 'clock' if k==4 else 'dark_oak_planks' if n.startswith('steam') else 'smooth_quartz'
    dump(res/'data/noctismagic/recipes'/f'{n}.json',{'type':'minecraft:crafting_shaped','pattern':[' I ','IMI',' E '],'key':{a:{'item':'minecraft:'+b} for a,b in [('I',ingredient),('M',middle),('E',extra)]},'result':{'item':f'noctismagic:{n}'}})
# Three peaceful guests, linked Code Geass pair.
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
ids=['michael_jackson','lelouch','cc'];labels=['Michael Jackson','Lelouch','C.C.'];colors=[('0x202027','0xe8e6e8'),('0x281b3d','0xd3b85d'),('0x83bb58','0xe7e5ed')]
decl=''
for n,(c,d) in zip(ids,colors):
    r=n.upper();decl+=f'public static final RegistryObject<EntityType<DramaGuest>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<DramaGuest>of(DramaGuest::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(10).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{c},{d},new Item.Properties()));\n    '
decl+='public static final RegistryObject<Item> PIZZA=ITEMS.register("pizza",()->new Item(new Item.Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(8).saturationMod(.65f).build())));\n    '
edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,''.join(f'e.put({n.upper()}.get(),DramaGuest.attributes().build());' for n in ids)+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({n.upper()}_EGG.get());' for n in ids))
edit('Noctis.java','if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)','if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS)e.accept(PIZZA.get());if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)')
edit('FallenEncounter.java','static final RegistryObject<SoundEvent> THEME=','static final RegistryObject<SoundEvent> MOONWALK_SHOUT=SOUNDS.register("moonwalk_shout",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"moonwalk_shout")));\n    static final RegistryObject<SoundEvent> THEME=')
write('DramaGuest.java','''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class DramaGuest extends PathfinderMob{
    UUID partner;int cd=40,dance=0,pizzaCd=0;
    public DramaGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public int kind(){return getType()==Noctis.MICHAEL_JACKSON.get()?0:getType()==Noctis.LELOUCH.get()?1:2;}
    static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,60).add(Attributes.MOVEMENT_SPEED,.29).add(Attributes.FOLLOW_RANGE,32);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.7){@Override public boolean canUse(){return dance==0&&kind()!=2&&canWanderTogether()&&super.canUse();}@Override public boolean canContinueToUse(){return dance==0&&kind()!=2&&canWanderTogether()&&super.canContinueToUse();}});goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));}
    boolean canWanderTogether(){return kind()==0||level() instanceof ServerLevel l&&partner!=null&&l.getEntity(partner) instanceof DramaGuest q&&q.isAlive()&&distanceTo(q)<5;}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}
    void perform(ServerLevel l){if(cd>0)return;cd=200;dance=60;getNavigation().stop();l.broadcastEntityEvent(this,(byte)94);say(l,"EH! HE!");playSound(FallenEncounter.MOONWALK_SHOUT.get(),1,1.15f);l.sendParticles(ParticleTypes.NOTE,getX(),getY()+1.9,getZ(),8,.5,.35,.5,.02);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        ItemStack item=p.getItemInHand(h);boolean pizza=kind()==2&&item.is(Noctis.PIZZA.get());if(!pizza&&!item.isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l){
            if(kind()==0)perform(l);
            else if(pizza&&pizzaCd==0){pizzaCd=200;if(!p.getAbilities().instabuild)item.shrink(1);say(l,"Finalmente una pizza! Ti concedo la mia gratitudine.");l.sendParticles(ParticleTypes.HEART,getX(),getY()+1.8,getZ(),8,.3,.3,.3,.02);p.addEffect(new MobEffectInstance(MobEffects.LUCK,1200,0));if(partner!=null&&l.getEntity(partner) instanceof DramaGuest q)q.say(l,"C.C., non puoi pensare sempre alla pizza.");}
            else if(cd==0){cd=100;String[] lines=kind()==1?new String[]{"C.C., cerca di non allontanarti.","Il mondo non cambiera' da solo.","Zero ha sempre un piano."}:new String[]{"Lelouch, voglio la pizza.","Hai portato la pizza?","Non mi interessa il tuo piano se non prevede una pizza."};say(l,lines[random.nextInt(lines.length)]);}
        }return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void tick(){super.tick();if(cd>0)cd--;if(dance>0)dance--;if(pizzaCd>0)pizzaCd--;if(!(level() instanceof ServerLevel l))return;
        if(kind()==0){if(dance>0){getNavigation().stop();double a=Math.toRadians(getYRot());Vec3 v=new Vec3(Math.sin(a)*.12,0,-Math.cos(a)*.12);if(l.noCollision(this,getBoundingBox().move(v)))move(MoverType.SELF,v);}else if(cd==0&&tickCount%100==0&&l.getNearestPlayer(this,12)!=null&&random.nextInt(3)==0)perform(l);return;}
        if(tickCount%10!=0)return;
        if(partner==null){DramaGuest q=(kind()==1?Noctis.CC.get():Noctis.LELOUCH.get()).create(l);if(q!=null){for(int i=0;i<8;i++){double a=i*Math.PI/4;q.moveTo(getX()+Math.cos(a)*1.5,getY(),getZ()+Math.sin(a)*1.5);if(l.noCollision(q)&&l.getBlockState(q.blockPosition().below()).isFaceSturdy(l,q.blockPosition().below(),net.minecraft.core.Direction.UP)){q.partner=getUUID();if(l.addFreshEntity(q)){partner=q.getUUID();q.setPersistenceRequired();setPersistenceRequired();}break;}}}return;}
        if(!(l.getEntity(partner) instanceof DramaGuest q)||!q.isAlive()){getNavigation().stop();return;}
        double d=distanceTo(q);
        if(kind()==1){if(d>5)getNavigation().stop();}
        else if(d>3)getNavigation().moveTo(q,1.2);else getNavigation().stop();
        if(kind()==2&&d>12){for(int i=0;i<8;i++){double a=i*Math.PI/4;double x=q.getX()+Math.cos(a)*2,z=q.getZ()+Math.sin(a)*2;BlockPos b=BlockPos.containing(x,q.getY(),z);if(l.hasChunkAt(b)&&l.getBlockState(b.below()).isFaceSturdy(l,b.below(),net.minecraft.core.Direction.UP)&&l.noCollision(this,getBoundingBox().move(x-getX(),q.getY()-getY(),z-getZ()))){teleportTo(x,q.getY(),z);break;}}}
        if(kind()==2&&cd==0&&tickCount%200==0&&l.getNearestPlayer(this,10)!=null&&random.nextInt(4)==0){cd=200;say(l,"Lelouch, quando mangiamo la pizza?");q.say(l,"Ancora?");}
    }
    @Override public void handleEntityEvent(byte id){if(id==94){dance=60;return;}super.handleEntityEvent(id);}
    public boolean dancing(){return dance>0;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(partner!=null)t.putUUID("Partner",partner);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);partner=t.hasUUID("Partner")?t.getUUID("Partner"):null;}
}''')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(p.getRandom().nextInt(24)==0&&l.getEntitiesOfClass(DramaGuest.class,p.getBoundingBox().inflate(80),m->m.kind()==0).isEmpty()){
            BlockPos q=Eclipse.spot(p,10,22);if(q!=null){DramaGuest m=Noctis.MICHAEL_JACKSON.get().create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }
        if(p.getRandom().nextInt(30)==0&&l.getEntitiesOfClass(DramaGuest.class,p.getBoundingBox().inflate(80),m->m.kind()!=0).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){DramaGuest m=Noctis.LELOUCH.get().create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }''')
# Independent humanoid models with custom hat, hair and robe parts.
write('DramaClient.java','''package it.noctis.magic;
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
public class DramaClient{
    static final String[] N={"michael_jackson","lelouch","cc"};
    static final ModelLayerLocation[] L=new ModelLayerLocation[3];
    static{for(int i=0;i<3;i++)L[i]=new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[i]),"main");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],()->mesh(0));e.registerLayerDefinition(L[1],()->mesh(1));e.registerLayerDefinition(L[2],()->mesh(2));}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MICHAEL_JACKSON.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.LELOUCH.get(),c->new Renderer(c,1));e.registerEntityRenderer(Noctis.CC.get(),c->new Renderer(c,2));}
    static LayerDefinition mesh(int k){MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot(),h=r.getChild("head"),b=r.getChild("body");
        r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        if(k==0){h.addOrReplaceChild("fedora",CubeListBuilder.create().texOffs(64,0).addBox(-5,-9,-5,10,1,10).texOffs(64,12).addBox(-3.5f,-13,-3.5f,7,4,7),PartPose.ZERO);h.addOrReplaceChild("curl",CubeListBuilder.create().texOffs(104,0).addBox(-.5f,-6,-4.3f,1,4,1),PartPose.offsetAndRotation(-2,0,0,0,0,-.18f));}
        else{h.addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.3f,-9,-4.3f,8,3,8),PartPose.ZERO);
            for(int i=0;i<5;i++)h.addOrReplaceChild("bang"+i,CubeListBuilder.create().texOffs(104,0).addBox(-1,0,-.5f,2,3+i%2,1),PartPose.offsetAndRotation(-3+i*1.5f,-8,-4,0,0,(i-2)*.18f));
            for(int i=0;i<2;i++){int s=i==0?-1:1;h.addOrReplaceChild("lock"+i,CubeListBuilder.create().texOffs(64+i*12,24).addBox(-1,0,-1,2,k==2?19:6,3),PartPose.offsetAndRotation(s*3.9f,-6,1,0,0,s*.08f));
                b.addOrReplaceChild("coat"+i,CubeListBuilder.create().texOffs(96+i*12,32).addBox(-2,0,-1,4,k==1?14:8,3),PartPose.offsetAndRotation(s*2.5f,9,2,.1f,0,s*.12f));}
        }return LayerDefinition.create(m,128,128);}
    static class Model extends HumanoidModel<DramaGuest>{
        final int k;Model(ModelPart r,int k){super(r);this.k=k;}
        @Override public void setupAnim(DramaGuest e,float limb,float amount,float age,float yaw,float pitch){super.setupAnim(e,limb,amount,age,yaw,pitch);body.yRot=0;head.zRot=0;
            if(k==0&&e.dancing()){float a=(float)Math.sin(age*.34);rightLeg.xRot=a*.65f;leftLeg.xRot=-a*.65f;rightArm.xRot=-1.65f;rightArm.zRot=.18f;leftArm.xRot=-.3f+a*.3f;body.yRot=a*.14f;head.zRot=-.12f;}
            if(k>0)for(int i=0;i<2;i++){head.getChild("lock"+i).xRot=amount*.2f+(float)Math.sin(age*.12+i)*.06f;body.getChild("coat"+i).xRot=.1f+amount*.2f;}
        }
    }
    static class Renderer extends MobRenderer<DramaGuest,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.35f);this.k=k;}@Override public ResourceLocation getTextureLocation(DramaGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''')
for k,n in enumerate(ids):
    S=4;W=128*S;pix=bytearray(W*W*4)
    def rect(x,y,w,h,col):
        for j in range(y*S,(y+h)*S):
            for i in range(x*S,(x+w)*S):
                g=.88+.12*math.sin((i-x*S)/max(1,w*S)*math.pi)
                c=tuple(int(v*g) for v in col);o=(j*W+i)*4;pix[o:o+4]=bytes((*c,255))
    cloth=[(28,26,33),(35,25,52),(222,223,232)][k];hair=[(26,22,28),(34,23,47),(143,196,73)][k];skin=[(196,151,123),(236,198,176),(244,210,183)][k]
    rect(0,0,128,128,cloth);rect(0,0,32,16,skin);rect(0,0,32,8,hair);rect(0,8,8,8,hair);rect(16,8,16,8,hair)
    for ex in (9,13):
        rect(ex,10,2,1,hair);rect(ex,11,2,2,(245,240,235));rect(ex+1,11,1,2,[(49,32,30),(135,68,180),(199,157,42)][k]);rect(ex+1,12,1,1,(25,22,33))
    rect(11,14,2,1,(132,68,70))
    rect(64,0,64,24,hair);rect(64,24,32,26,hair)
    if k==0:rect(23,21,3,8,(232,228,223));rect(24,21,1,5,(35,31,39));rect(40,26,16,6,(230,230,235));rect(0,29,16,2,(236,235,233))
    if k==1:
        rect(20,20,1,12,(204,171,70));rect(27,20,1,12,(204,171,70));rect(23,20,2,4,(226,207,188));rect(23,24,2,1,(196,154,65));rect(23,28,2,1,(196,154,65))
    if k==2:rect(20,22,8,2,(60,52,73));rect(20,29,8,2,(60,52,73));rect(40,24,16,2,(61,55,73))
    rect(96,32,32,24,cloth)
    png(assets/'textures/entity'/f'{n}.png',W,W,pix)
    dump(assets/'models/item'/f'{n}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
pix=bytearray(32*32*4)
for y in range(32):
    for x in range(32):
        r=math.hypot(x-15.5,y-15.5)
        if r>14:continue
        c=(181,111,51) if r>11.5 else (245,194,74)
        if r<10 and any((x-a)**2+(y-b)**2<5 for a,b in [(9,12),(20,10),(16,19),(23,20),(11,23)]):c=(177,37,37)
        pix[(y*32+x)*4:(y*32+x)*4+4]=bytes((*c,255))
png(assets/'textures/item/pizza.png',32,32,pix)
dump(assets/'models/item/pizza.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/pizza'}})
dump(res/'data/noctismagic/recipes/pizza.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'minecraft:bread'},{'item':'minecraft:beetroot'},{'item':'minecraft:cooked_porkchop'}],'result':{'item':'noctismagic:pizza','count':2}})
wav=assets/'sounds/moonwalk_shout.wav';wav.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['espeak-ng','-v','en','-p','78','-s','195','-w',str(wav),'Eh! Hee!'],check=True)
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(wav.with_suffix('.ogg'))],check=True);wav.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text());d['moonwalk_shout']={'sounds':[{'name':'noctismagic:moonwalk_shout'}]};dump(p,d)
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,(it,en,_,_) in items.items():d['block.noctismagic.'+n]=it if lang=='it_it' else en
    for n,label in zip(ids,labels):
        d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    d['item.noctismagic.pizza']='Pizza';dump(p,d)
print('Furniture and three peaceful guests installed')
