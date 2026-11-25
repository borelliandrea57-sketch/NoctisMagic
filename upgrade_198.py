"""1.7.33: new artisan bakery; pastry shop remains independent."""
from pathlib import Path
import sys,math,json,random
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
pal={'brick':(158,86,57),'stone':(203,179,143),'carved':(190,154,112),'copper':(90,125,105),'roof':(82,108,97),'wood':(151,104,58),'dark':(82,53,37),'cream':(229,214,181),'floor':(174,129,87),'tile':(209,191,160),'iron':(61,54,48),'gold':(213,166,80),'crust':(179,105,45),'flour':(230,190,130),'bag':(181,165,129),'cloth':(116,63,45),'leaf':(92,124,62),'glass':(190,220,217)}
for n,base in pal.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   v=.91+rng.random()*.13
   if n=='brick':
    u=(x+16*((y//16)%2))%32;h=y%16
    if u<2 or h<2:v*=.55
    elif u==2 or h==2:v*=1.14
   if n in ('stone','floor','tile'):
    if x%32==0 or y%32==0:v*=.64
    if n=='floor':v*=.91+.14*((x//32+y//32)%2)
   if n in ('wood','dark'):
    v*=.85+.18*math.sin(x*.4+math.sin(y*.12))**2
    if x%16==0:v*=.65
   if n in ('roof','copper'):v*=.85+.24*math.sin(math.pi*(x%16)/16)**2
   if n=='roof' and y%16==0:v*=.6
   if n=='crust':v*=.83+.22*math.sin(x*.12+y*.11)**2
   if n in ('bag','cloth'):v*=.96+.045*((x+y)%2)
   im.putpixel((x,y),(*[max(0,min(255,round(q*v))) for q in base],115 if n=='glass' else 255))
 d=ImageDraw.Draw(im)
 if n=='carved':
  d.rectangle((3,3,60,60),outline=(109,78,49),width=2);d.rectangle((6,6,57,57),outline=(231,196,145),width=2)
  for side in (-1,1):
   d.line((32,54,32+side*12,13),fill=(112,83,50),width=2)
   for j in range(5):
    x=32+side*(j*2+3);y=46-j*6
    d.ellipse((x-4,y-5,x+4,y+3),fill=(145,107,59),outline=(222,182,119))
 if n=='crust':
  for j in range(3):d.line((12+j*16,19,19+j*16,43),fill=(236,190,115),width=3)
 im.save(assets/'textures/block'/f'forno_{n}.png')
# Store sign, a single continuous artwork across five panels.
im=Image.new('RGBA',(320,64),(72,46,32,255));d=ImageDraw.Draw(im)
d.rectangle((3,3,316,60),outline=(215,170,93),width=2);d.rectangle((7,7,312,56),outline=(142,99,52),width=1)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',20)
except OSError:font=ImageFont.load_default()
d.text((160,28),'IL FORNO',font=font,fill=(245,222,172),anchor='mm')
d.text((160,46),'PANE  •  LIEVITO  •  GRANO',font=ImageFont.load_default(),fill=(222,188,125),anchor='mm')
for side in (-1,1):
 x=160+side*124
 d.line((x,49,x+side*8,14),fill=(221,170,76),width=2)
 for i in range(5):
  xx=x+side*i*2;yy=44-i*5;d.ellipse((xx-5,yy-4,xx+5,yy+3),fill=(218,168,76))
for i in range(5):im.crop((i*64,0,(i+1)*64,64)).save(assets/'textures/block'/f'forno_sign_{i}.png')
items={}
def add(n,it,en,boxes=None,tex=None,kind=0,creative=True):items['forno_'+n]=(it,en,boxes,tex,kind,creative)
for n,it,en in [('brick','Mattone artigianale cotto','Hand-fired brick'),('stone','Pietra arenaria antica','Aged sandstone'),('carved','Pietra incisa con spighe','Wheat carved stone'),('floor','Cotto da pavimento','Terracotta floor'),('tile','Piastrella da laboratorio','Workshop tile'),('roof','Tegola in rame ossidato','Oxidized copper roofing'),('wood','Rovere chiaro lavorato','Worked oak')]:
 add(n,it,en,tex=n)
add('pillar','Pilastro scolpito del forno','Carved bakery pillar',[B(0,0,0,16,2,16,'stone'),B(1,2,1,15,4,15,'carved'),B(2,4,2,14,13,14,'stone'),B(1,13,1,15,15,15,'carved'),B(0,15,0,16,16,16,'stone')]+[B(x,4,1.1,x+1,13,2,'carved') for x in (4,7,10,13)])
add('cornice','Cornice di cotto e rame','Copper and terracotta cornice',[B(0,0,8,16,16,16,'brick'),B(0,3,5,16,6,8,'stone'),B(0,8,3,16,11,8,'carved'),B(0,12,1,16,15,8,'copper')])
add('awning','Tendina del panificio','Bakery awning',[B(0,13,14,16,15,16,'iron')]+[B(i*2,5+j*1.1,j*2,i*2+2,7+j*1.1,j*2+2,'cloth' if i%2==0 else 'cream') for i in range(8) for j in range(8)]+[B(i*2,2+(i%2)*.5,0,i*2+2,6,1,'cloth' if i%2==0 else 'cream') for i in range(8)]+[B(0,5,1,16,6,2,'iron')])
add('counter','Bancone artigianale','Artisan counter',[B(0,0,0,16,2,16,'dark'),B(1,2,1,15,13,15,'wood'),B(0,13,0,16,16,16,'stone'),B(2,3,.5,14,11,1,'dark'),B(3,4,0,13,10,.5,'carved')])
def loaf(x,y,z,w,h,d):
 # Each layer has non-coplanar sides; wheat cuts are engraved on top.
 return [B(x+.7,y,z+.7,x+w-.7,y+h*.30,z+d-.7,'crust'),B(x,y+h*.30,z,x+w,y+h*.74,z+d,'crust'),B(x+.65,y+h*.74,z+.65,x+w-.65,y+h,z+d-.65,'flour')]
add('bread_display','Vassoio di pagnotte','Bread display',[B(0,0,0,16,2,16,'wood'),B(1,2,1,15,3,15,'dark')]+loaf(1,3,2,6,5,11)+loaf(9,3,1,6,6,13))
add('baguette_display','Cesto di baguette','Baguette basket',[B(0,0,0,16,2,16,'dark'),B(0,2,0,1,6,16,'wood'),B(15,2,0,16,6,16,'wood'),B(1,2,0,15,6,1,'wood'),B(1,2,15,15,6,16,'wood')]+[q for x in (2,6,10) for q in loaf(x,3,1,3.5,5,14)])
add('shelf','Scaffale espositivo del pane','Bakery bread shelf',[B(0,0,12,16,16,16,'dark'),B(0,0,0,16,2,16,'wood'),B(0,8,0,16,10,16,'wood')]+loaf(1,2,2,6,4,9)+loaf(9,2,1,6,5,10)+loaf(2,10,3,12,5,8))
add('flour_sack','Sacco di farina','Flour sack',[B(2,0,2,14,3,14,'bag'),B(1,3,1,15,11,15,'bag'),B(3,11,3,13,13,13,'bag'),B(5,13,5,11,15,11,'bag'),B(4,12,4,12,13,12,'dark'),B(5,5,.6,11,9,1,'cream')])
add('worktable','Tavolo da impasto','Kneading table',[B(1,0,1,3,13,3,'dark'),B(13,0,1,15,13,3,'dark'),B(1,0,13,3,13,15,'dark'),B(13,0,13,15,13,15,'dark'),B(0,12,0,16,16,16,'wood')])
add('dough_board','Spianatoia e impasto','Dough board',[B(1,0,2,15,1,14,'wood'),B(4,1,4,12,3,12,'flour'),B(5,3,5,11,4,11,'cream'),B(1,1,12,15,3,14,'dark'),B(0,1.5,12.5,2,2.5,13.5,'wood'),B(14,1.5,12.5,16,2.5,13.5,'wood')])
add('chair','Sedia del panificio','Bakery chair',[B(1,0,1,3,8,3,'dark'),B(13,0,1,15,8,3,'dark'),B(1,0,13,3,8,15,'dark'),B(13,0,13,15,8,15,'dark'),B(1,8,1,15,10,15,'wood'),B(1,10,13,3,16,15,'dark'),B(13,10,13,15,16,15,'dark'),B(3,13,13,13,16,15,'carved')])
add('lamp','Lanterna del forno','Bakery lantern',[B(6,13,6,10,16,10,'iron'),B(3,11,3,13,13,13,'copper'),B(4,3,4,12,11,12,'cream'),B(3,1,3,13,3,13,'copper')]+[B(x,3,z,x+1,11,z+1,'iron') for x in (3,12) for z in (3,12)],kind=3)
add('wall_sign','Insegna a bandiera del forno','Bakery blade sign',[B(6,13,1,10,15,16,'iron'),B(5,14,13,11,16,16,'iron'),B(7,9,3,9,13,4,'iron'),B(7,9,11,9,13,12,'iron'),B(6,1,2,10,10,13,'dark'),B(5.7,2,3,6,9,12,'carved'),B(10,2,3,10.3,9,12,'carved'),B(5.5,0,2,10.5,1,13,'gold')])
for i in range(5):add(f'sign_{i}','Tassello insegna del forno','Bakery sign tile',[B(0,0,13,16,16,16,f'sign_{i}')],creative=False)
decl=[]
for n,(it,en,boxes,tex,kind,creative) in items.items():
 expr='new Block(BlockBehaviour.Properties.of().strength(2f,6f))' if boxes is None else f'new FurnitureBlock({kind})'
 decl.append(f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});')
 if creative:decl.append(f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));')
 if boxes is None:
  model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/forno_'+tex}};variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tx={m:'noctismagic:block/forno_'+m for *_,m in boxes};tx['particle']=next(iter(tx.values()))
  model={'textures':tx,'elements':[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 if creative:
  dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
  dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s;s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n,q in items.items() if q[-1])+'}'+a,1);p.write_text(s,encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,*_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a='    static Plan bakery(boolean pastry){';assert a in s
s=s.replace(a,'''    static Plan artisanBakery(){
        Plan p=new Plan(25,23,13,"Il Forno dei Due Brontoloni");
        Block brick=Furniture.FORNO_BRICK.get(),stone=Furniture.FORNO_STONE.get(),roof=Furniture.FORNO_ROOF.get(),wood=Furniture.FORNO_WOOD.get(),carved=Furniture.FORNO_CARVED.get();
        for(int x=0;x<25;x++)for(int z=0;z<23;z++){
            p.put(x,0,z,z<3||x==0||x==24||z==22?stone:z>=15?Furniture.FORNO_TILE.get():Furniture.FORNO_FLOOR.get());
        }
        p.walls(1,1,3,23,7,21,brick);
        for(int x:new int[]{1,23})for(int z:new int[]{3,21})for(int y=1;y<=7;y++)p.put(x,y,z,Furniture.FORNO_PILLAR.get());
        for(int x=2;x<=22;x++){p.put(x,1,3,stone);p.put(x,6,3,carved);p.put(x,7,3,stone);}
        // Wide shop windows, arches, raised trim; real double doors in an uninterrupted wall.
        for(int x:new int[]{3,4,5,6,7,8,9,15,16,17,18,19,20,21})for(int y=2;y<=4;y++)p.put(x,y,3,Furniture.FAST_WINDOW.get());
        for(int x:new int[]{2,10,14,22})for(int y=1;y<=5;y++)p.put(x,y,3,Furniture.FORNO_PILLAR.get());
        for(int x:new int[]{3,9,15,21})p.put(x,5,3,carved);
        for(int x=11;x<=12;x++){
            BlockState ds=Blocks.SPRUCE_DOOR.defaultBlockState().setValue(DoorBlock.FACING,Direction.NORTH).setValue(DoorBlock.HINGE,x==11?net.minecraft.world.level.block.state.properties.DoorHingeSide.LEFT:net.minecraft.world.level.block.state.properties.DoorHingeSide.RIGHT);
            p.put(x,1,3,ds.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER));
            p.put(x,2,3,ds.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER));
            p.put(x,3,3,Furniture.FAST_WINDOW.get());
        }
        p.box(13,1,3,13,5,3,carved);p.box(11,4,3,12,5,3,stone);
        for(int x=3;x<=9;x++)royalFacing(p,x,5,2,Furniture.FORNO_AWNING.get(),Direction.NORTH);
        for(int x=15;x<=21;x++)royalFacing(p,x,5,2,Furniture.FORNO_AWNING.get(),Direction.NORTH);
        Block[] sign={Furniture.FORNO_SIGN_0.get(),Furniture.FORNO_SIGN_1.get(),Furniture.FORNO_SIGN_2.get(),Furniture.FORNO_SIGN_3.get(),Furniture.FORNO_SIGN_4.get()};
        for(int i=0;i<5;i++)royalFacing(p,10+i,6,2,sign[i],Direction.NORTH);
        royalFacing(p,22,4,2,Furniture.FORNO_WALL_SIGN.get(),Direction.NORTH);
        for(int x:new int[]{1,23})for(int z=5;z<=19;z++){
            if(z%5==0){for(int y=1;y<=7;y++)p.put(x,y,z,Furniture.FORNO_PILLAR.get());}
            else if(z%5<4)for(int y=3;y<=5;y++)p.put(x,y,z,Furniture.FAST_WINDOW.get());
        }
        for(int x:new int[]{3,21}){p.put(x,1,1,Blocks.POTTED_AZALEA_BUSH);p.put(x,1,2,Blocks.BARREL);}
        // Closed roof: full supported cross-section below every rising row, no floating slabs.
        p.box(1,8,3,23,8,21,wood);
        for(int z=2;z<=22;z++){
            int rise=Math.min(4,Math.min(z-2,22-z)/2);
            for(int x=0;x<=24;x++){
                for(int y=8;y<8+rise;y++)p.put(x,y,z,x==0||x==24?brick:wood);
                p.put(x,8+rise,z,roof);
            }
        }
        for(int x=0;x<=24;x++){p.put(x,8,2,stone);p.put(x,8,22,stone);}
        // Chimney rises from the back oven wall and is capped by a working campfire.
        p.box(18,2,19,20,11,20,brick);
        p.put(19,12,19,Blocks.CAMPFIRE);
        // Open customer aisle and separate bakery work area.
        for(int x=3;x<=21;x++)if(x<11||x>13){
            p.put(x,1,13,Furniture.FORNO_COUNTER.get());
            royalFacing(p,x,2,13,x%3==0?Furniture.FORNO_BAGUETTE_DISPLAY.get():Furniture.FORNO_BREAD_DISPLAY.get(),Direction.NORTH);
        }
        for(int x:new int[]{4,20})for(int z:new int[]{7,10}){
            p.put(x,1,z,Furniture.FORNO_WORKTABLE.get());
            royalFacing(p,x-1,1,z,Furniture.FORNO_CHAIR.get(),Direction.EAST);
            royalFacing(p,x+1,1,z,Furniture.FORNO_CHAIR.get(),Direction.WEST);
        }
        for(int x:new int[]{3,4,5,6,7,16,17,21})for(int y=2;y<=4;y++)royalFacing(p,x,y,20,Furniture.FORNO_SHELF.get(),Direction.NORTH);
        // Functioning furnace bank with massive stone arch surround and visible chimney.
        for(int x=8;x<=16;x++)for(int y=1;y<=5;y++)p.put(x,y,20,brick);
        for(int x:new int[]{10,12,14}){
            p.put(x,1,19,Blocks.FURNACE.defaultBlockState().setValue(FurnaceBlock.FACING,Direction.NORTH));
            p.put(x,2,19,Blocks.SMOKER.defaultBlockState().setValue(SmokerBlock.FACING,Direction.NORTH));
            p.put(x,3,19,carved);
        }
        for(int x=9;x<=15;x++)p.put(x,4,19,stone);
        for(int x:new int[]{9,15})for(int y=1;y<=3;y++)p.put(x,y,19,Furniture.FORNO_PILLAR.get());
        for(int x:new int[]{5,6,7,17,18,19}){
            p.put(x,1,18,Furniture.FORNO_WORKTABLE.get());
            p.put(x,2,18,Furniture.FORNO_DOUGH_BOARD.get());
        }
        p.put(4,1,18,Blocks.CRAFTING_TABLE);p.put(20,1,18,Blocks.BARREL);
        for(int x:new int[]{2,22})for(int z:new int[]{16,18,19})p.put(x,1,z,Furniture.FORNO_FLOUR_SACK.get());
        for(int x:new int[]{5,12,19})for(int z:new int[]{8,16}){
            p.put(x,7,z,Blocks.CHAIN);p.put(x,6,z,Furniture.FORNO_LAMP.get());
        }
        // Existing bakery NPC spawn positions (8,1,16 and 16,1,16) are deliberately clear.
        return p;
    }
    static Plan bakery(boolean pastry){
        if(!pastry)return artisanBakery();''',1).replace('p.put(x,1,1,Blocks.POTTED_AZALEA_BUSH);p.put(x,1,2,Blocks.BARREL);','p.put(x,1,1,Blocks.POTTED_POPPY);p.put(x,1,2,Blocks.BARREL);',1)
p.write_text(s,encoding='utf-8')
print('Artisan bakery rebuilt from scratch; pastry branch untouched; original bread recipes and clerk spawn preserved.')
