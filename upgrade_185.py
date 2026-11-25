"""1.7.18: Santa Lacrimosa and Valdracula architectural expansion."""
from pathlib import Path
import sys,math,json,random,re
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
pal={'ivory':(230,220,198),'rose':(174,119,115),'green':(75,113,95),'blue':(79,105,145),'gold':(205,164,82),'shadow':(144,130,114),'sand':(190,169,139),'black':(72,66,76),'red':(144,43,53),'wood':(89,52,39),'wax':(250,235,187),'flame':(255,199,91),'silver':(151,153,164)}
for n,c in pal.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   v=.94+.055*math.sin((x+y)*.16+2*math.sin(x*.13))+rng.uniform(-.035,.035)
   if n in ('gold','silver'):v=.80+.26*math.sin(math.pi*x/64)**2
   im.putpixel((x,y),(*[max(0,min(255,int(q*v))) for q in c],255))
 im.save(assets/'textures/block'/f'sanctuary_{n}.png')
for n,base in [('ashlar',pal['sand']),('rosebrick',pal['rose']),('greenbrick',pal['green']),('bluebrick',pal['blue']),('nightbrick',pal['black'])]:
 im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im);rng=random.Random(n)
 for row in range(4):
  y=row*16
  for x in range(-16 if row%2 else 0,64,32):
   c=tuple(max(0,min(255,int(q*rng.uniform(.85,1.06)))) for q in base)
   d.rectangle((x,y,x+31,y+15),fill=(67,61,61,255));d.rectangle((x+1,y+1,x+30,y+14),fill=(*c,255))
   d.line((x+1,y+1,x+30,y+1),fill=(*[min(255,q+32) for q in c],255))
   d.line((x+1,y+14,x+30,y+14),fill=(*[max(0,q-35) for q in c],255))
 im.save(assets/'textures/block'/f'sanctuary_{n}.png')
for n in ('mosaic_star','mosaic_flower','mosaic_border','mosaic_cross','mosaic_bat','icon','tapestry','tapestry_top','tapestry_end'):
 dark=n in ('mosaic_bat','tapestry','tapestry_top','tapestry_end')
 im=Image.new('RGBA',(128,128),(55,41,54,255) if dark else (224,209,181,255));d=ImageDraw.Draw(im)
 d.rectangle((1,1,126,126),outline=(79,67,62),width=3);d.rectangle((5,5,122,122),outline=(185,144,71),width=3)
 if n=='icon':
  d.ellipse((35,11,93,69),fill=(188,151,74),outline=(255,225,130),width=3)
  d.polygon([(64,38),(48,57),(28,110),(100,110),(81,58)],fill=(65,98,141),outline=(212,173,90),width=3)
  d.ellipse((49,25,79,58),fill=(211,181,144),outline=(117,78,60),width=2)
  d.line((64,62,64,105),fill=(225,188,104),width=4)
 elif n.startswith('tapestry'):
  d.rectangle((12,2,115,125),fill=(105,20,39),outline=(203,155,76),width=3)
  for x in range(15,115,6):d.line((x,8,x,119),fill=(115+(x%3)*7,27,46),width=1)
  if n=='tapestry':
   d.polygon([(64,35),(57,52),(38,38),(20,41),(31,57),(21,82),(48,67),(64,91),(80,67),(107,82),(97,57),(108,41),(90,38),(71,52)],fill=(25,20,29),outline=(220,170,84),width=2)
  elif n=='tapestry_top':
   d.polygon([(32,65),(25,29),(48,47),(64,21),(80,47),(103,29),(96,65)],fill=(198,150,65),outline=(251,212,128),width=3)
  else:
   for x in range(14,115,8):d.line((x,97,x,125),fill=(212,165,82),width=3)
 elif n=='mosaic_border':
  for k in range(0,128,16):d.polygon([(k,64),(k+8,48),(k+16,64),(k+8,80)],fill=(64,99,91),outline=(174,127,66),width=2)
  d.rectangle((10,12,117,28),fill=(126,48,62));d.rectangle((10,99,117,115),fill=(126,48,62))
 else:
  for k in range(8):
   a=k*math.pi/4;t=a+math.pi/8;outer=(64+49*math.cos(a),64+49*math.sin(a));inner=(64+22*math.cos(t),64+22*math.sin(t));prev=(64+22*math.cos(a-math.pi/8),64+22*math.sin(a-math.pi/8))
   if n=='mosaic_flower':
    x,y=64+30*math.cos(a),64+30*math.sin(a);d.ellipse((x-18,y-18,x+18,y+18),fill=(119,48,62) if k%2 else (64,105,94),outline=(202,165,91),width=3)
   else:d.polygon([(64,64),prev,outer,inner],fill=(48,80,122) if k%2 else (150,62,67),outline=(195,152,83),width=3)
  d.ellipse((47,47,81,81),fill=(206,167,83),outline=(79,64,61),width=3)
  if n=='mosaic_cross':
   d.rectangle((59,24,69,104),fill=(235,216,154),outline=(84,70,57),width=2);d.rectangle((39,49,89,59),fill=(235,216,154),outline=(84,70,57),width=2)
  if n=='mosaic_bat':d.polygon([(18,42),(48,51),(64,32),(80,51),(110,42),(93,83),(80,70),(64,98),(48,70),(35,83)],fill=(25,20,30),outline=(218,167,81),width=2)
 # Individual tessera seams with subtle contrast.
 if not n.startswith('tapestry'):
  for y in range(2,128,4):
   for x in range((y//4%2)*2,128,4):
    c=im.getpixel((x,y));d.point((x,y),fill=tuple(int(v*.66) for v in c[:3])+(255,))
 im.save(assets/'textures/block'/f'sanctuary_{n}.png')
items={}
def add(n,it,en,boxes=None,mat=None,light=False,creative=True):items[n]=(it,en,boxes,mat,light,creative)
for n,it,en,m in [('sanctuary_ashlar','Pietra calcarea squadrata','Limestone ashlar','ashlar'),('sanctuary_rose','Marmo rosato a conci','Rose marble ashlar','rosebrick'),('sanctuary_green','Serpentino verde a conci','Green serpentine ashlar','greenbrick'),('sanctuary_blue','Pietra azzurra a conci','Blue ashlar','bluebrick'),('sanctuary_night','Basalto gotico lavorato','Gothic basalt','nightbrick'),('sanctuary_star','Mosaico a stella','Star mosaic','mosaic_star'),('sanctuary_flower','Mosaico floreale','Floral mosaic','mosaic_flower'),('sanctuary_border','Fregio cosmatesco','Cosmatesque border','mosaic_border'),('sanctuary_cross','Mosaico della croce','Cross mosaic','mosaic_cross'),('sanctuary_bat','Mosaico del pipistrello','Bat mosaic','mosaic_bat')]:add(n,it,en,mat=m)
# Low visible lamps and sacred objects.
add('sanctuary_lamp','Lampada votiva','Votive lamp',[B(3,0,3,13,2,13,'gold'),B(6,2,6,10,5,10,'gold'),B(4,5,4,12,11,12,'wax'),B(7,11,7,9,14,9,'flame'),B(3,5,3,4,12,4,'gold'),B(12,5,12,13,12,13,'gold')],light=True)
add('sanctuary_font','Acquasantiera','Holy water font',[B(3,0,3,13,2,13,'shadow'),B(6,2,6,10,8,10,'ivory'),B(2,8,2,14,10,14,'ivory'),B(3,10,3,13,11,13,'blue')]+[B(x,10,z,X,13,Z,'ivory') for x,z,X,Z in [(1,1,3,15),(13,1,15,15),(3,1,13,3),(3,13,13,15)]])
add('sanctuary_chalice','Calice liturgico','Liturgical chalice',[B(4,0,4,12,2,12,'gold'),B(7,2,7,9,6,9,'gold'),B(5,6,5,11,8,11,'gold'),B(3,8,3,13,11,13,'gold'),B(4,11,4,12,12,12,'red')])
add('sanctuary_book','Libro sacro aperto','Open sacred book',[B(1,0,3,15,1,13,'wood'),B(2,1,3,8,3,13,'ivory'),B(8,1,3,14,3,13,'ivory')]+[B(x,3,z,x+4,3.15,z+.3,'shadow') for x in (3,9) for z in range(4,12,2)])
add('sanctuary_icon','Icona sacra dorata','Gilded sacred icon',[B(0,0,11,16,16,15,'gold'),B(1,1,10,15,15,11,'icon')])
add('sanctuary_niche','Nicchia scolpita','Sculpted niche',[B(0,0,13,16,16,16,'shadow'),B(0,0,5,3,16,13,'ivory'),B(13,0,5,16,16,13,'ivory'),B(3,0,5,13,2,13,'gold'),B(3,14,5,13,16,13,'gold'),B(3,11,7,5,14,13,'ivory'),B(11,11,7,13,14,13,'ivory'),B(5,13,8,11,14,13,'ivory')])
for n,it in [('tapestry','Arazzo del pipistrello'),('tapestry_top','Corona dell’arazzo'),('tapestry_end','Frangia dell’arazzo')]:
 add('sanctuary_'+n,it,n.replace('_',' ').title(),[B(0,0,13,16,16,15,n)]+([B(0,14,11,16,16,14,'gold')] if n=='tapestry_top' else []))
add('sanctuary_baluster','Balaustra gotica','Gothic balustrade',[B(0,0,5,16,2,11,'black'),B(0,14,4,16,16,12,'black')]+[B(x,2,7,x+2,14,9,'silver') for x in (1,7,13)]+[B(x,5,6,x+4,10,10,'black') for x in (0,6,12)])
# Sculptures: use non-coplanar tessellated volumetric cross-sections rather than a pile of cubes.
# Model sizes 5-8 blocks tall; split geometry into legal 16-unit tile models.
shapes={}
def sculpt(name):
 boxes=[]
 def box(x,y,z,X,Y,Z,m='ivory'):boxes.append(B(x,y,z,X,Y,Z,m))
 def ell(cx,cy,cz,rx,ry,rz,m='ivory',step=4):
  for y in range(math.floor(cy-ry),math.ceil(cy+ry),step):
   Y=min(y+step,cy+ry);t=(max(-1,min(1,((y+Y)/2-cy)/ry)));f=math.sqrt(max(.025,1-t*t))
   # Three depth bands create an octagonal, faceted cross-section.
   w=rx*f;d=rz*f
   box(cx-w,y,cz-d*.63,cx+w,Y,cz+d*.63,m)
   box(cx-w*.63,y,cz-d,cx+w*.63,Y,cz-d*.63,m)
   box(cx-w*.63,y,cz+d*.63,cx+w*.63,Y,cz+d,m)
 def rod(a,b,r,m):
  dist=math.dist(a,b);n=max(1,math.ceil(dist/(r*1.3)))
  for i in range(n+1):
   t=i/n;c=[a[j]+(b[j]-a[j])*t for j in range(3)]
   ell(*c,r,r*1.15,r,m,step=max(2,int(r)))
 base='black' if name=='guardian' else 'shadow';body='silver' if name=='guardian' else 'ivory'
 box(-22,0,-16,22,4,16,base);box(-18,4,-13,18,8,13,body)
 # Long garment, detailed hems, narrow waist, separated arms and hands.
 for y in range(8,68,4):
  width=15-(y-8)*.115+2*math.sin(y*.14);depth=9-(y-8)*.045
  box(-width,y,-depth,width,y+4,depth,body)
  for k in (-2,-1,0,1,2):
   x=k*width/3;box(x-.7,y,-depth-1.1,x+.7,y+4,-depth,base)
 ell(0,76,0,13,13,8,body);ell(0,89,0,4,5,4,body)
 ell(0,101,0,8.5,12,7.6,body,3)
 # Hair/helmet, facial ridge and separate brows.
 ell(0,108,2,9,7,8,base,3);box(-1.5,98,-9,1.5,104,-6,body)
 box(-5,104,-7.7,-1.8,105,-6,base);box(1.8,104,-7.7,5,105,-6,base)
 box(-2,94,-7.5,2,95,-6,base)
 for side in (-1,1):
  rod((side*11,80,0),(side*18,66,-3),3.7,body)
  rod((side*18,66,-3),(side*10,58,-13),3.2,body)
  ell(side*10,58,-13,3.6,4,3,body,2)
 if name in ('angel','guardian'):
  for side in (-1,1):
   # Broad wings, layered individual feather tips.
   for j in range(9):
    x=side*(11+j*4.1);y=70+j*3.4
    rod((side*9,76,5),(x,y+19,10),2.5,body)
    rod((x,y+19,10),(x+side*3,y-4-j*.9,12),2.0,base if name=='guardian' else body)
    rod((x+side*2,y+10,12),(x+side*4,y-10,14),1.5,body)
 if name=='guardian':
  # Horned helmet and vertically held sword.
  for side in (-1,1):rod((side*6,108,1),(side*12,119,2),2.2,base)
  box(7,24,-15,10,80,-12,'silver');box(2,73,-17,15,76,-11,'gold')
 else:
  for j in range(32):
   a=j*math.tau/32;x=14*math.cos(a);y=105+14*math.sin(a)
   box(x-1.6,y-1.6,8,x+1.6,y+1.6,10,'gold')
  if name=='saint':
   box(-12,56,-17,-2,68,-12,'red');box(-11,57,-18,-3,67,-17,'gold')
   box(9,56,-16,11,83,-13,'gold');box(4,74,-16,16,77,-13,'gold')
  else:
   box(-1.5,38,-17,1.5,74,-13,'gold');box(-8,63,-17,8,66,-13,'gold')
 return boxes
def coord(n):return 'm'+str(-n) if n<0 else str(n)
for name in ('angel','saint','guardian'):
 tiles={}
 for x,y,z,X,Y,Z,m in sculpt(name):
  for ix in range(math.floor((x+8)/16),math.ceil((X+8)/16)):
   for iy in range(math.floor(y/16),math.ceil(Y/16)):
    for iz in range(math.floor((z+8)/16),math.ceil((Z+8)/16)):
     ox=ix*16-8;oy=iy*16;oz=iz*16-8
     a,b,c=max(x,ox)-ox,max(y,oy)-oy,max(z,oz)-oz;A,D,C=min(X,ox+16)-ox,min(Y,oy+16)-oy,min(Z,oz+16)-oz
     if A>a and D>b and C>c:tiles.setdefault((ix,iy,iz),[]).append(B(a,b,c,A,D,C,m))
 shapes[name]=[]
 for (x,y,z),boxes in sorted(tiles.items()):
  n='sanctuary_statue_'+name+'_'+coord(x)+'_'+coord(y)+'_'+coord(z)
  add(n,'Frammento di statua','Statue segment',boxes,creative=False);shapes[name].append((x,y,z,n))
# Register all blocks, including hidden sculpture tiles.
decl=[]
mats=list(pal)+['ashlar','rosebrick','greenbrick','bluebrick','nightbrick','mosaic_star','mosaic_flower','mosaic_border','mosaic_cross','mosaic_bat','icon','tapestry','tapestry_top','tapestry_end']
for n,(it,en,boxes,mat,light,creative) in items.items():
 expr='new Block(BlockBehaviour.Properties.of().strength(2.5f,6f))' if mat else 'new FurnitureBlock('+('3' if light else '0')+')'
 decl += [f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});']
 if creative:decl += [f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));']
 if mat:model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/sanctuary_'+mat}};variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tx={m:'noctismagic:block/sanctuary_'+m for m in mats};tx['particle']=tx['ivory']
  # Omit internal coplanar faces where exact face coverage can be determined.
  el=[]
  for x,y,z,X,Y,Z,m in boxes:
   faces={f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}
   for a,b,c,A,D,C,_ in boxes:
    if a<=x and A>=X and c<=z and C>=Z:
     if abs(D-y)<1e-6:faces.pop('down',None)
     if abs(b-Y)<1e-6:faces.pop('up',None)
   if faces:el.append({'from':[x,y,z],'to':[X,Y,Z],'faces':faces})
  model={'textures':tx,'elements':el}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 if creative:
  dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
  dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
# Reusable, player-placed statue items. Never overwrite non-replaceable blocks.
names={'angel':('Statua monumentale: Arcangelo','Monumental archangel'),'saint':('Statua monumentale: Santo','Monumental saint'),'guardian':('Statua monumentale: Guardiano oscuro','Monumental dark guardian')}
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='public static final RegistryObject<Item> CATHEDRAL_EGG=';assert a in s
s=s.replace(a,''.join(f'public static final RegistryObject<Item> STATUE_{n.upper()}=ITEMS.register("statue_{n}",()->new MonumentItem("{n}",new Item.Properties().stacksTo(16)));\n    ' for n in shapes)+a,1)
a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s
s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n,q in items.items() if q[5])+''.join('e.accept(STATUE_'+n.upper()+'.get());' for n in shapes)+'}'+a,1);p.write_text(s,encoding='utf-8')
# Store each tile in a data-backed list; rotate positions and block geometry together.
methods=[]
for n,tiles in shapes.items():
 methods.append('static Tile[] '+n+'(){return new Tile[]{'+','.join('new Tile('+str(x)+','+str(y)+','+str(z)+',Furniture.'+key.upper()+'.get())' for x,y,z,key in tiles)+'};}')
(java/'MonumentItem.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.AABB;
public class MonumentItem extends Item{
 record Tile(int x,int y,int z,Block block){}
 private final String type;
 public MonumentItem(String type,Properties p){super(p);this.type=type;}
 '''+'\n'.join(methods)+'''
 static Tile[] tiles(String n){return switch(n){case "angel"->angel();case "saint"->saint();default->guardian();};}
 static int dx(Tile t,Direction f){return switch(f){case EAST->-t.z();case SOUTH->-t.x();case WEST->t.z();default->t.x();};}
 static int dz(Tile t,Direction f){return switch(f){case EAST->t.x();case SOUTH->-t.z();case WEST->-t.x();default->t.z();};}
 static BlockState state(Tile t,Direction f){return t.block().defaultBlockState().setValue(Furniture.FurnitureBlock.FACING,f);}
 @Override public InteractionResult useOn(UseOnContext c){
  if(!(c.getLevel() instanceof ServerLevel l))return InteractionResult.SUCCESS;
  if(c.getPlayer()==null)return InteractionResult.FAIL;
  BlockPos origin=c.getClickedPos().relative(c.getClickedFace());
  Direction f=c.getHorizontalDirection().getOpposite();
  Tile[] ts=tiles(type);
  for(Tile t:ts){
   BlockPos pos=origin.offset(dx(t,f),t.y(),dz(t,f));
   if(l.isOutsideBuildHeight(pos)||!l.hasChunkAt(pos)||!l.getWorldBorder().isWithinBounds(pos)||!l.getBlockState(pos).canBeReplaced()||!l.getEntities(c.getPlayer(),new AABB(pos)).isEmpty()||!l.mayInteract(c.getPlayer(),pos)){
    c.getPlayer().displayClientMessage(Component.literal("Non c’è abbastanza spazio libero per la statua."),true);return InteractionResult.FAIL;
   }
  }
  for(Tile t:ts)l.setBlock(origin.offset(dx(t,f),t.y(),dz(t,f)),state(t,f),3);
  if(!c.getPlayer().getAbilities().instabuild)c.getItemInHand().shrink(1);
  return InteractionResult.CONSUME;
 }
}''',encoding='utf-8')
for n,(it,en) in names.items():
 # Small pixel icon representing the sculpture.
 im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im);c=(173,175,190) if n=='guardian' else (235,221,197)
 d.rectangle((6,27,25,30),fill=(113,96,81));d.polygon([(12,11),(20,11),(22,27),(10,27)],fill=c);d.ellipse((12,3,20,12),fill=c)
 if n!='saint':d.polygon([(13,13),(3,5),(1,17),(9,23),(13,20),(19,20),(23,23),(31,17),(29,5),(19,13)],fill=c)
 d.rectangle((15,13,16,24),fill=(198,151,68));d.rectangle((12,16,19,17),fill=(198,151,68))
 p=assets/'textures/item'/f'statue_{n}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 dump(assets/'models/item'/f'statue_{n}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/statue_'+n}})
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,*_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 for n,(it,en) in names.items():d['item.noctismagic.statue_'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8')
# Replace old cathedral statues with the detailed monuments at the original anchors.
s=s.replace('lacrimosaAngel(p,x,1,z+3);','monument(p,x,1,z+3,"angel",Direction.NORTH);').replace('lacrimosaAngel(p,x,2,83);','monument(p,x,2,83,"saint",Direction.NORTH);').replace('lacrimosaAngel(p,x,1,5);','monument(p,x,1,5,"angel",Direction.NORTH);')
helper='''    static void monument(Plan p,int x,int y,int z,String n,Direction f){
        for(MonumentItem.Tile t:MonumentItem.tiles(n))p.put(x+MonumentItem.dx(t,f),y+t.y(),z+MonumentItem.dz(t,f),MonumentItem.state(t,f));
    }
    static void hiddenLight(Plan p,int x,int y,int z){
        if(!p.blocks.containsKey(p.key(x,y,z)))p.put(x,y,z,Blocks.LIGHT.defaultBlockState().setValue(net.minecraft.world.level.block.LightBlock.LEVEL,15));
    }
    static void sacredDetails(Plan p){
        Block ivory=Furniture.SANCTUARY_ASHLAR.get(),rose=Furniture.SANCTUARY_ROSE.get(),green=Furniture.SANCTUARY_GREEN.get(),blue=Furniture.SANCTUARY_BLUE.get();
        Block star=Furniture.SANCTUARY_STAR.get(),flower=Furniture.SANCTUARY_FLOWER.get(),border=Furniture.SANCTUARY_BORDER.get(),cross=Furniture.SANCTUARY_CROSS.get();
        Block lamp=Furniture.SANCTUARY_LAMP.get();
        for(int z=12;z<=77;z++)for(int x=16;x<=44;x++){
            if(x>=27&&x<=33)p.put(x,0,z,x==27||x==33?border:z%8<2?cross:(x+z)%2==0?star:flower);
            else if(x%4==0||z%6==0)p.put(x,0,z,(x+z)%3==0?rose:green);
        }
        // Light at eye level in the aisles and under the nave, not only on the high ceiling.
        for(int z=14;z<=78;z+=6){
            for(int x:new int[]{9,15,26,34,45,51}){hiddenLight(p,x,3,z);hiddenLight(p,x,8,z);}
            for(int x:new int[]{25,35})p.put(x,1,z,lamp);
            for(int x:new int[]{17,43}){p.put(x,4,z,lamp);p.put(x,3,z,ivory);}
        }
        for(int z=23;z<=65;z+=14)for(int x:new int[]{7,53}){
            Direction dir=x==7?Direction.EAST:Direction.WEST;
            // Freestanding recessed shrine: back wall, depth on both sides, pointed arch.
            int back=x==7?6:54;
            for(int y=2;y<=8;y++)for(int dz=-2;dz<=2;dz++)p.put(back,y,z+dz,y%3==0?blue:ivory);
            for(int dz:new int[]{-2,2})for(int y=2;y<=6;y++)p.put(x,y,z+dz,y%2==0?green:rose);
            for(int k=0;k<3;k++)for(int side:new int[]{-1,1})p.put(x,6+k,z+side*(2-k),ivory);
            royalFacing(p,x,4,z,Furniture.SANCTUARY_ICON.get(),dir);
            p.put(x,2,z,Furniture.LACRIMOSA_RELIQUARY.get());
            p.put(x,2,z-1,lamp);p.put(x,2,z+1,lamp);
            hiddenLight(p,x==7?8:52,5,z);
        }
        for(int x:new int[]{24,36}){p.put(x,1,12,Furniture.SANCTUARY_FONT.get());p.put(x,1,67,lamp);}
        p.put(29,5,73,Furniture.SANCTUARY_BOOK.get());p.put(31,5,73,Furniture.SANCTUARY_CHALICE.get());
        for(int x=20;x<=40;x+=5)for(int y=3;y<=13;y++)hiddenLight(p,x,y,77);
        for(int z=18;z<=74;z+=8)for(int x:new int[]{11,49})for(int y=3;y<=15;y+=4)p.put(x,y,z,y%3==0?rose:blue);
    }
    static void draculaDetails(Plan p){
        Block dark=Furniture.SANCTUARY_NIGHT.get(),red=Furniture.SANCTUARY_ROSE.get(),gold=Furniture.SANCTUARY_BORDER.get(),bat=Furniture.SANCTUARY_BAT.get(),star=Furniture.SANCTUARY_STAR.get();
        for(int z=35;z<=86;z++)for(int x=32;x<=58;x++){
            if(x>=41&&x<=49)p.put(x,0,z,x==41||x==49?gold:z%8==0?bat:star);
            else p.put(x,0,z,(x+z)%5==0?red:dark);
        }
        // Floor mosaics in the entrance avenue.
        for(int z=9;z<=33;z++)for(int x=40;x<=50;x++)p.put(x,0,z,x==40||x==50?gold:z%6==0?bat:(x+z)%2==0?dark:red);
        // Long multi-part tapestries, wall sconces and heraldic panels.
        for(int z=43;z<=79;z+=9)for(int x:new int[]{34,56}){
            Direction f=x==34?Direction.EAST:Direction.WEST;
            royalFacing(p,x,11,z,Furniture.SANCTUARY_TAPESTRY_TOP.get(),f);
            for(int y=6;y<=10;y++)royalFacing(p,x,y,z,Furniture.SANCTUARY_TAPESTRY.get(),f);
            royalFacing(p,x,5,z,Furniture.SANCTUARY_TAPESTRY_END.get(),f);
            royalFacing(p,x,4,z-2,Furniture.ROYAL_SCONCE.get(),f);
            royalFacing(p,x,4,z+2,Furniture.ROYAL_SCONCE.get(),f);
        }
        // New giant gargoyle-like armored guardians with wings, on the entrance avenue.
        for(int x:new int[]{35,55})for(int z:new int[]{16,30}){
            p.box(x-3,1,z-2,x+3,9,z+2,Blocks.AIR);
            monument(p,x,1,z,"guardian",Direction.NORTH);
        }
        // Projecting interior balcony bays connected to the existing walkways.
        for(int z=48;z<=76;z+=14)for(int side:new int[]{-1,1}){
            int a=side<0?37:50,b=side<0?40:53,edge=side<0?40:50;
            p.box(a,12,z-2,b,12,z+2,dark);
            p.box(side<0?37:53,13,z-1,side<0?37:53,13,z+1,Blocks.AIR);
            for(int x=a;x<=b;x++)for(int zz:new int[]{z-2,z+2})p.put(x,13,zz,Furniture.SANCTUARY_BALUSTER.get());
            for(int zz=z-2;zz<=z+2;zz++)royalFacing(p,edge,13,zz,Furniture.SANCTUARY_BALUSTER.get(),side<0?Direction.EAST:Direction.WEST);
            for(int x=a;x<=b;x++)p.put(x,11,z,Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);
        }
        // Exterior balconies at existing upper openings; door from the upper rooms.
        for(int z:new int[]{46,62,78})for(int x:new int[]{18,72}){
            int a=x==18?14:72,b=x==18?18:76,edge=x==18?14:76;
            p.box(a,12,z-2,b,12,z+2,dark);
            p.box(x,13,z-1,x,15,z+1,Blocks.AIR);
            for(int xx=a;xx<=b;xx++)for(int zz:new int[]{z-2,z+2})p.put(xx,13,zz,Furniture.SANCTUARY_BALUSTER.get());
            for(int zz=z-2;zz<=z+2;zz++)royalFacing(p,edge,13,zz,Furniture.SANCTUARY_BALUSTER.get(),x==18?Direction.WEST:Direction.EAST);
            p.put(edge,11,z,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
        }
        for(int z=40;z<=80;z+=10)for(int x:new int[]{32,58}){
            p.put(x,2,z,Furniture.ROYAL_CHANDELIER.get());hiddenLight(p,x==32?33:57,5,z);
        }
        // Darker exterior masonry accents and high contrasting cornices.
        for(int z=36;z<=85;z+=7)for(int x:new int[]{18,72})for(int y=3;y<=29;y+=6)p.put(x==18?17:73,y,z,red);
    }
'''
a=s.index('    static Plan cathedral(){');s=s[:a]+helper+s[a:]
a=s.index('    static Plan cathedral(){');b=s.index('        return p;',a);s=s[:b]+'        sacredDetails(p);\n'+s[b:]
a=s.index('    static Plan castle(){');b=s.index('        return p;',a);s=s[:b]+'        draculaDetails(p);\n'+s[b:];p.write_text(s,encoding='utf-8')
print('Santa Lacrimosa and Valdracula: new stone, mosaics, sacred objects, tapestry sets, balconies and three placeable monumental statues.')
