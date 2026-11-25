"""1.7.24: supported Japanese roof ornaments, vermilion lacquer torii and carved botanical wall panels."""
from pathlib import Path
import sys,math,json,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
pal={'vermilion':(208,48,27),'darkred':(116,22,19),'black':(43,32,35),'gold':(212,161,64),'tile':(48,65,85),'wood':(103,61,37),'paper':(233,216,181),'branch':(109,59,42),'pink':(233,145,176),'petal':(255,207,218),'leaf':(78,121,74),'plum':(172,65,105)}
for n,base in pal.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   t=.92+rng.random()*.05
   if n in ('vermilion','darkred','wood'):t*=.90+.12*math.sin(x*.26+math.sin(y*.08))**2
   if n=='vermilion':t+=.20*math.exp(-((x-15)/9)**2)+.08*math.exp(-((x-46)/4)**2)
   if n=='gold':t*=.80+.30*math.sin(math.pi*x/64)**2
   if n=='tile':t*=.78+.25*math.sin(math.pi*(x%16)/16)**2
   im.putpixel((x,y),(*[max(0,min(255,round(c*t))) for c in base],255))
 im.save(assets/'textures/block'/f'torii_{n}.png')
# Fine gold cloud scrollwork carved into lacquered wood.
im=Image.open(assets/'textures/block/torii_vermilion.png').copy();d=ImageDraw.Draw(im)
for y in (5,58):d.line((2,y,61,y),fill=(247,186,75),width=2)
for x in (12,32,52):
 for dx,dy in ((-5,0),(0,-5),(5,0)):
  d.arc((x+dx-6,32+dy-5,x+dx+6,32+dy+5),180,360,fill=(242,180,70),width=2)
 d.line((x-11,33,x+11,33),fill=(242,180,70),width=1)
im.save(assets/'textures/block/torii_scroll.png')
# Hand-painted botanical plaques, with shadowed petals and branching silhouettes.
for n,flower in [('sakura',(240,155,184)),('ume',(183,66,113)),('kiku',(224,168,54))]:
 im=Image.new('RGBA',(128,128),(65,42,38,255));d=ImageDraw.Draw(im)
 d.rectangle((3,3,124,124),fill=(224,208,173),outline=(214,160,66),width=3)
 d.rectangle((9,9,118,118),outline=(132,89,57),width=1)
 d.line([(17,110),(43,79),(65,53),(99,23)],fill=(105,63,43),width=5)
 d.line([(43,79),(30,44),(19,28)],fill=(117,71,46),width=3)
 d.line([(65,53),(87,69),(105,72)],fill=(117,71,46),width=3)
 for cx,cy in ((20,30),(33,48),(48,65),(67,45),(85,30),(103,21),(87,65),(105,73)):
  count=10 if n=='kiku' else 5
  for i in range(count):
   a=math.tau*i/count;xx=cx+6*math.cos(a);yy=cy+6*math.sin(a)
   d.ellipse((xx-4,yy-4,xx+4,yy+4),fill=flower,outline=tuple(max(0,c-35) for c in flower),width=1)
  d.ellipse((cx-2,cy-2,cx+2,cy+2),fill=(250,221,120))
 im.save(assets/'textures/block'/f'torii_{n}.png')
items={}
def add(n,it,en,b):items[n]=(it,en,b)
add('jade_torii_pillar','Colonna torii in lacca vermiglia','Vermilion torii pillar',[B(1,0,1,15,16,15,'vermilion'),B(0,0,0,16,1,16,'gold'),B(0,15,0,16,16,16,'gold'),B(3,2,0.65,13,14,1,'scroll')])
add('jade_torii_base','Basamento torii','Torii base',[B(0,0,0,16,3,16,'black'),B(1,3,1,15,6,15,'black'),B(1,6,1,15,16,15,'vermilion'),B(0,6,0,16,7,16,'gold')])
add('jade_torii_beam','Trave torii scolpita','Carved torii beam',[B(0,4,2,16,15,14,'vermilion'),B(0,3,1.5,16,4,14.5,'gold'),B(0,15,1.5,16,16,14.5,'darkred'),B(0,5,1.65,16,14,2,'scroll')])
add('jade_torii_joint','Capitello torii','Torii capital',[B(0,4,2,16,15,14,'vermilion'),B(0,3,1.5,16,4,14.5,'gold'),B(0,15,1.5,16,16,14.5,'darkred'),B(0,5,1.65,16,14,2,'scroll'),B(1,0,1,15,3,15,'darkred'),B(1,3,1,15,4,15,'gold')])
add('jade_torii_crown','Architrave torii laccato','Lacquered torii lintel',[B(0,0,2,16,4,14,'darkred'),B(0,4,1,16,7,15,'vermilion'),B(0,7,0,16,10,16,'black'),B(0,10,1,16,12,15,'tile'),B(0,3,1.4,16,4,2,'gold')])
# End caps are attached to the lintel rather than placed a block above.
add('jade_torii_tip','Estremità rialzata torii','Upturned torii end',[B(0,0,2,16,4,14,'darkred'),B(0,4,1,16,7,15,'vermilion'),B(0,7,0,16,10,16,'black'),B(0,10,1,16,12,15,'tile'),B(0,12,2,5,15,14,'tile'),B(0,15,3,3,18,13,'gold')])
crest=[B(2,0,1,14,14,4,'black'),B(3,1,0,13,13,1,'scroll'),B(1,0,0,15,1,4,'gold'),B(1,13,0,15,14,4,'gold'),B(6,14,2,10,20,4,'gold')]
add('jade_torii_crest','Targa dorata del torii','Gilded torii plaque',crest)
# Roof ornaments occupy the same block as the tiles below them.
roof=[B(0,0,0,16,3,16,'tile')]+[B(x,3,0,x+3,5,16,'tile') for x in (0,4,8,12)]
add('jade_roof_corner','Tegola angolare rialzata','Upturned corner tile',roof+[B(1,5,1,8,7,8,'tile'),B(1,7,1,6,10,6,'tile'),B(1,10,1,4,13,4,'tile'),B(1,13,1,3,15,3,'gold')])
add('jade_roof_ridge','Colmo continuo kawara','Continuous kawara ridge',[B(0,0,0,16,3,16,'tile'),B(0,3,3,16,5,13,'tile'),B(0,5,5,16,8,11,'tile'),B(0,8,6,16,10,10,'tile')])
for n,it,en,petal in [('sakura','Fregio di ciliegio','Cherry blossom relief','pink'),('ume','Fregio di pruno','Plum blossom relief','plum'),('kiku','Fregio di crisantemo','Chrysanthemum relief','gold')]:
 boxes=[B(0,0,13,16,16,16,'wood'),B(1,1,12,15,15,13,n)]
 # Relief blossoms project from the painted plaque. Distinct depths avoid coplanar surfaces.
 for cx,cy in ((4,11),(8,8),(12,12),(11,4)):
  for j in range(5):
   a=math.tau*j/5;xx=cx+1.05*math.cos(a);yy=cy+1.05*math.sin(a)
   boxes.append(B(xx-.55,yy-.55,11.15,xx+.55,yy+.55,11.95,petal))
  boxes.append(B(cx-.43,cy-.43,10.7,cx+.43,cy+.43,11.15,'gold'))
 boxes += [B(0,0,11,16,1,13,'gold'),B(0,15,11,16,16,13,'gold')]
 add('jade_flower_'+n,it,en,boxes)
decl=[]
mats=list(pal)+['scroll','sakura','ume','kiku']
for n,(it,en,boxes) in items.items():
 decl += [f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->new FurnitureBlock(0));',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));']
 tx={m:'noctismagic:block/torii_'+m for m in mats};tx['particle']=tx['vermilion']
 model={'textures':tx,'elements':[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
 dump(assets/'blockstates'/f'{n}.json',{'variants':{f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s;s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a,1);p.write_text(s,encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static Plan sushiRestaurant(){');b=s.index('        return p;',a);sub=s[a:b]
old='for(int x:new int[]{l,r})for(int z:new int[]{n,f})p.put(x,y+1,z,Blocks.DEEPSLATE_TILE_WALL);'
assert old in sub
sub=sub.replace(old,'''// Corner ornaments share their own tile base; no detached wall blocks.
            jadeFacing(p,l,y,n,Furniture.JADE_ROOF_CORNER.get(),Direction.NORTH);
            jadeFacing(p,r,y,n,Furniture.JADE_ROOF_CORNER.get(),Direction.EAST);
            jadeFacing(p,r,y,f,Furniture.JADE_ROOF_CORNER.get(),Direction.SOUTH);
            jadeFacing(p,l,y,f,Furniture.JADE_ROOF_CORNER.get(),Direction.WEST);''',1)
old='for(int z=9;z<=18;z++)p.put(14,13,z,Blocks.DEEPSLATE_TILE_WALL);';assert old in sub
sub=sub.replace(old,'''for(int z=8;z<=19;z++){
            p.put(14,12,z,Blocks.DEEPSLATE_TILES);
            jadeFacing(p,14,13,z,Furniture.JADE_ROOF_RIDGE.get(),Direction.EAST);
        }''',1)
# Remove bare terracotta from the original portal; final decorations replace the old cap.
old='for(int x:new int[]{9,19})p.box(x,1,1,x,5,1,Blocks.RED_TERRACOTTA);';assert old in sub
sub=sub.replace(old,'for(int x:new int[]{9,19})p.box(x,1,1,x,5,1,Furniture.JADE_TORII_PILLAR.get());',1)
old='p.box(8,5,1,20,5,1,Blocks.RED_TERRACOTTA);';assert old in sub
sub=sub.replace(old,'p.box(8,5,1,20,5,1,Furniture.JADE_TORII_BEAM.get());',1)
sub+='''        // Finish the portal after the veranda, so lanterns and trim cannot overwrite it.
        for(int x:new int[]{9,19}){
            p.put(x,1,1,Furniture.JADE_TORII_BASE.get());
            for(int y=2;y<=4;y++)p.put(x,y,1,Furniture.JADE_TORII_PILLAR.get());
        }
        for(int x=8;x<=20;x++)p.put(x,5,1,x==9||x==19?Furniture.JADE_TORII_JOINT.get():Furniture.JADE_TORII_BEAM.get());
        for(int x=7;x<=21;x++)p.put(x,6,1,Furniture.JADE_TORII_CROWN.get());
        jadeFacing(p,7,6,1,Furniture.JADE_TORII_TIP.get(),Direction.NORTH);
        jadeFacing(p,21,6,1,Furniture.JADE_TORII_TIP.get(),Direction.SOUTH);
        p.put(14,4,1,Furniture.JADE_TORII_CREST.get());
        p.put(14,5,4,Furniture.JADE_EXT_SIGN.get());
        // Floral plaques on existing facade piers; leave the shoji windows open.
        Block[] blooms={Furniture.JADE_FLOWER_SAKURA.get(),Furniture.JADE_FLOWER_UME.get(),Furniture.JADE_FLOWER_KIKU.get()};
        int[] piers={2,7,21,26};
        for(int i=0;i<piers.length;i++)jadeFacing(p,piers[i],3,1,blooms[i%3],Direction.NORTH);
        for(int i=0;i<4;i++)for(int x:new int[]{1,27}){
            int z=9+i*4;
            jadeFacing(p,x,5,z,blooms[i%3],x==1?Direction.WEST:Direction.EAST);
        }
        for(int i=0;i<3;i++)jadeFacing(p,8+i*6,5,22,blooms[i],Direction.NORTH);
'''
s=s[:a]+sub+s[b:];p.write_text(s,encoding='utf-8')
print('Jade Cat: attached roof corner ornaments, continuous supported ridge, lacquered vermilion torii and three raised floral wall plaques.')
