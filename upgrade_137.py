"""1.3.7: fictional in-game cannabis crop, decorative foliage and hemp fiber recipes."""
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
edit('Furniture.java','    static final RegistryObject<BlockEntityType<StorageEntity>> STORAGE=', '''    public static final RegistryObject<Block> CANNABIS=VampireLife.BLOCKS.register("cannabis_crop",CannabisCrop::new);
    public static final RegistryObject<Item> CANNABIS_SEEDS=Noctis.ITEMS.register("cannabis_seeds",()->new net.minecraft.world.item.ItemNameBlockItem(CANNABIS.get(),new Item.Properties()));
    public static final RegistryObject<Item> CANNABIS_LEAF=Noctis.ITEMS.register("cannabis_leaf",()->new Item(new Item.Properties()));
    public static final RegistryObject<Item> HEMP_FIBER=Noctis.ITEMS.register("hemp_fiber",()->new Item(new Item.Properties()));
    static final RegistryObject<BlockEntityType<StorageEntity>> STORAGE=''')
edit('Noctis.java','if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)','if(e.getTabKey()==CreativeModeTabs.INGREDIENTS){e.accept(Furniture.CANNABIS_LEAF.get());e.accept(Furniture.HEMP_FIBER.get());}if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS){e.accept(Furniture.CANNABIS_SEEDS.get());}if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)')
(java/'CannabisCrop.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemLike;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.phys.shapes.*;
public class CannabisCrop extends CropBlock{
    CannabisCrop(){super(BlockBehaviour.Properties.of().noCollission().randomTicks().instabreak().sound(SoundType.CROP));}
    @Override protected ItemLike getBaseSeedId(){return Furniture.CANNABIS_SEEDS.get();}
    @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return box(1,0,1,15,2+getAge(s)*2,15);}
}'''.replace('import net.minecraft.world.item.ItemLike;','import net.minecraft.world.level.ItemLike;'),encoding='utf-8')
# Small chance of fictional in-game seeds from vanilla grass. No real-world cultivation details.
(java/'CannabisSeeds.java').write_text('''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class CannabisSeeds{
    @SubscribeEvent public static void grass(BlockEvent.BreakEvent e){
        if(!(e.getLevel() instanceof ServerLevel l)||e.getPlayer().isCreative()||!l.getGameRules().getBoolean(GameRules.RULE_DOBLOCKDROPS))return;
        if((e.getState().is(Blocks.GRASS)||e.getState().is(Blocks.TALL_GRASS))&&l.random.nextInt(18)==0)
            Block.popResource(l,e.getPos(),new ItemStack(Furniture.CANNABIS_SEEDS.get()));
    }
}''',encoding='utf-8')
# Pixel art: palmate, serrated foliage, eight progressive stages, transparent sprite.
def line(pix,W,x0,y0,x1,y1,c,r=0):
    steps=max(1,int(max(abs(x1-x0),abs(y1-y0))*2))
    for t in range(steps+1):
        x=round(x0+(x1-x0)*t/steps);y=round(y0+(y1-y0)*t/steps)
        for dx in range(-r,r+1):
            for dy in range(-r,r+1):
                if 0<=x+dx<W and 0<=y+dy<W:pix[((y+dy)*W+x+dx)*4:((y+dy)*W+x+dx)*4+4]=bytes((*c,255))
def leaf(pix,W,x,y,size):
    for i in range(7):
        a=(i-3)*.39
        length=size*(1-.095*abs(i-3))
        for j in range(1,int(length*2)+1):
            t=j/(length*2);cx=x+math.sin(a)*length*t;cy=y-math.cos(a)*length*t
            width=max(.4,math.sin(t*math.pi)*size*.14*(.75+.25*math.cos(j*2.1)))
            for side in (-1,1):
                line(pix,W,cx,cy,cx+side*math.cos(a)*width,cy+side*math.sin(a)*width,(40+int(27*(1-t)),116+int(54*(1-t)),46))
        line(pix,W,x,y,x+math.sin(a)*length,y-math.cos(a)*length,(104,169,69))
for age in range(8):
    W=32;pix=bytearray(W*W*4)
    height=5+age*3.2
    line(pix,W,16,31,16,31-height,(80,124,53),0)
    for j in range(1+age//2):
        y=30-height*(j+1)/(2+age//2)
        for side in (-1,1):
            x=16+side*(3+age*.55)
            line(pix,W,16,y+3,x,y,(68,120,48))
            leaf(pix,W,x,y,4+age*.65)
    leaf(pix,W,16,32-height,4+age*.8)
    n='cannabis_stage'+str(age)
    png(assets/'textures/block'/f'{n}.png',W,W,pix)
    dump(assets/'models/block'/f'{n}.json',{'parent':'minecraft:block/crop','render_type':'minecraft:cutout','textures':{'crop':'noctismagic:block/'+n}})
dump(assets/'blockstates/cannabis_crop.json',{'variants':{f'age={i}':{'model':f'noctismagic:block/cannabis_stage{i}'} for i in range(8)}})
for n in ('cannabis_seeds','cannabis_leaf','hemp_fiber'):
    W=32;pix=bytearray(W*W*4)
    if n=='cannabis_leaf':
        leaf(pix,W,16,27,14);line(pix,W,16,27,16,30,(93,140,58))
    elif n=='cannabis_seeds':
        for x,y in ((10,12),(19,10),(15,20),(23,22),(8,23)):
            for yy in range(y-3,y+4):
                for xx in range(x-2,x+3):
                    if ((xx-x)/2.5)**2+((yy-y)/3.5)**2<=1:pix[(yy*W+xx)*4:(yy*W+xx)*4+4]=bytes((118+(xx%2)*30,95+(yy%2)*20,51,255))
    else:
        for i in range(7):line(pix,W,6+i,25,19+i,5,(180+i*7,151+i*5,96+i*6),1)
        line(pix,W,9,17,21,19,(103,77,47),1)
    png(assets/'textures/item'/f'{n}.png',W,W,pix);dump(assets/'models/item'/f'{n}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/'+n}})
dump(res/'data/noctismagic/loot_tables/blocks/cannabis_crop.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:cannabis_seeds'}],'conditions':[{'condition':'minecraft:survives_explosion'}]},{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:cannabis_leaf','functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':2,'max':4}}]},{'type':'minecraft:item','name':'noctismagic:cannabis_seeds','weight':1,'functions':[{'function':'minecraft:set_count','count':2}]}],'conditions':[{'condition':'minecraft:block_state_property','block':'noctismagic:cannabis_crop','properties':{'age':'7'}},{'condition':'minecraft:survives_explosion'}]}]})
for n,ingredient,out,count in [('hemp_fiber','noctismagic:cannabis_leaf','noctismagic:hemp_fiber',2),('hemp_string','noctismagic:hemp_fiber','minecraft:string',2),('hemp_paper','noctismagic:hemp_fiber','minecraft:paper',2)]:
    dump(res/'data/noctismagic/recipes'/f'{n}.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':ingredient},{'item':ingredient}]+([{'item':ingredient}] if n=='hemp_paper' else []),'result':{'item':out,'count':count}})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for key,it,en in [('block.noctismagic.cannabis_crop','Cannabis','Cannabis'),('item.noctismagic.cannabis_seeds','Semi di cannabis','Cannabis seeds'),('item.noctismagic.cannabis_leaf','Foglie di cannabis','Cannabis leaves'),('item.noctismagic.hemp_fiber','Fibra di canapa','Hemp fiber')]:d[key]=it if lang=='it_it' else en
    dump(p,d)
print('Cannabis in-game crop, eight growth sprites and fiber crafting installed')
