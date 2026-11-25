"""1.7.25: proper patisserie storefront, no legacy wool, ceramic roofing and projecting sign."""
from pathlib import Path
import sys,math,json,random
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
pal={'ceramic':(114,78,86),'ceramic_top':(143,99,106),'plaster':(231,212,184),'rose':(185,111,125),'bronze':(144,99,54),'gold':(218,174,93),'cream':(248,231,208),'dark':(83,49,49),'leaf':(104,145,113)}
for n,base in pal.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   v=.95+rng.uniform(-.045,.045)
   if n.startswith('ceramic'):
    row=y//16;xx=(x+8*(row%2))%16;yy=y%16
    v*=.84+.24*math.sin(math.pi*xx/16)**2
    if yy in (0,15) or xx==0:v*=.59
    if yy in (1,2):v*=1.15
   if n in ('bronze','gold'):v*=.76+.33*math.sin(math.pi*x/64)**2
   if n=='plaster':v+=.025*math.sin(x*.27+y*.31)
   im.putpixel((x,y),(*[max(0,min(255,round(c*v))) for c in base],255))
 im.save(assets/'textures/block'/f'patisserie_{n}.png')
# Art Nouveau shop blade sign, hand painted on both faces.
im=Image.new('RGBA',(128,128),(83,49,49,255));d=ImageDraw.Draw(im)
d.rounded_rectangle((4,4,123,123),radius=20,fill=(245,224,195),outline=(205,151,79),width=5)
d.rounded_rectangle((11,11,116,116),radius=16,outline=(151,82,90),width=2)
for side in (-1,1):
 x=64+side*39
 for y in (34,87):
  d.arc((x-10,y-12,x+10,y+12),0,320,fill=(111,145,106),width=2)
  d.ellipse((x-4,y-5,x+4,y+4),fill=(190,103,122))
# Illustrated pastry with layers, frosting and cherry.
d.polygon([(44,40),(84,40),(90,64),(38,64)],fill=(165,104,62),outline=(118,73,45),width=2)
for y in (47,55):d.line((43,y,85,y),fill=(252,222,171),width=3)
d.arc((42,24,86,49),180,360,fill=(202,111,135),width=8)
d.ellipse((59,22,69,32),fill=(165,39,59))
font=ImageFont.load_default()
for label,y in [('DOLCI',74),('& TEA',89)]:
 d.text((64,y),label,font=font,fill=(98,49,55),anchor='mt')
im.save(assets/'textures/block/patisserie_blade_sign.png')
items={}
def add(n,it,en,boxes):items[n]=(it,en,boxes)
add('sweet_fluted_column','Colonna scanalata in stucco','Fluted stucco column',[B(0,0,0,16,2,16,'bronze'),B(1,2,1,15,4,15,'cream'),B(2,4,2,14,13,14,'plaster'),B(1,13,1,15,15,15,'cream'),B(0,15,0,16,16,16,'gold')]+[B(x,4,1.2,x+1,13,2,'rose') for x in (3,6,9,12)]+[B(1.2,4,z,2,13,z+1,'rose') for z in (3,6,9,12)]+[B(14,4,z,14.8,13,z+1,'rose') for z in (3,6,9,12)])
# Roof tiles are solid architectural blocks with separate top and side textures.
add('sweet_ceramic_roof','Tegola in ceramica smaltata','Glazed ceramic roof tile',None)
add('sweet_ceramic_eave','Gronda in ceramica e ottone','Ceramic and brass eave',[B(0,0,0,16,3,16,'bronze'),B(0,3,0,16,8,16,'ceramic'),B(0,8,4,16,16,16,'ceramic'),B(0,8,0,16,9,4,'gold')]+[B(x,9,3,x+2.5,10,4,'ceramic_top') for x in (0,4,8,12)])
# Sign plane is perpendicular to wall, extends out from the bracket towards the street.
add('sweet_hanging_sign','Insegna a bandiera della pasticceria','Patisserie projecting shop sign',[
 B(5,9,14,11,16,16,'bronze'),B(7,14,1,9,16,15,'bronze'),B(6,12,3,10,14,14,'gold'),
 B(7,9,4,9,14,5,'bronze'),B(7,9,10,9,14,11,'bronze'),
 B(6.6,1,2,9.4,10,13,'dark'),B(6.3,1.5,2.5,6.6,9.5,12.5,'blade_sign'),B(9.4,1.5,2.5,9.7,9.5,12.5,'blade_sign'),
 B(6.2,0.5,2,9.8,1.5,13,'gold'),B(6.2,9.5,2,9.8,10.5,13,'gold')])
# Decorative sill, not a full cube of wood.
add('sweet_ornate_sill','Davanzale decorato','Decorative storefront sill',[B(0,0,8,16,3,16,'plaster'),B(0,3,6,16,6,16,'cream'),B(0,6,4,16,8,16,'rose'),B(0,8,4,16,9,16,'gold')])
decl=[]
for n,(it,en,boxes) in items.items():
 expr='new Block(BlockBehaviour.Properties.of().strength(2f,6f))' if boxes is None else 'new FurnitureBlock(0)'
 decl += [f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));']
 tx={m:'noctismagic:block/patisserie_'+m for m in list(pal)+['blade_sign']};tx['particle']=tx['plaster']
 if boxes is None:
  model={'parent':'minecraft:block/cube_bottom_top','textures':{'side':tx['ceramic'],'top':tx['ceramic_top'],'bottom':tx['ceramic']}}
  variants={'':{'model':'noctismagic:block/'+n}}
 else:
  el=[]
  for x,y,z,X,Y,Z,m in boxes:
   faces={f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}
   if m=='blade_sign':
    faces={f:{'texture':'#blade_sign','uv':[0,0,16,16]} for f in ('east','west')}
   el.append({'from':[x,y,z],'to':[X,Y,Z],'faces':faces})
  model={'textures':tx,'elements':el}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
 dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
# Replace stepped awning with a coherent sloped cloth, retaining the original block IDs and recipes.
for color in ('rose','mint','cocoa'):
 path=assets/'models/block'/f'shop_awning_{color}.json';model=json.loads(path.read_text(encoding='utf-8'))
 c1=color;c2='ivory' if color=='rose' else 'cream'
 boxes=[B(0,13,14,16,15,16,'gold'),B(0,5,0,16,6,1.1,'gold')]
 # Eight connected fabric strips with a curved valance and no underlying wool.
 for j in range(8):
  col=c1 if j%2==0 else c2
  for k in range(8):
   z=k*2;h=5.8+z*.52
   boxes.append(B(j*2,h,z,j*2+2,h+1.65,z+2,col))
  boxes.append(B(j*2,2.0+(j%2)*.65,0,j*2+2,6.35,1.0,col))
 for x in (.5,15.0):boxes.extend([B(x,2,0,x+.5,5.8,1.2,'gold'),B(x,5.5,0,x+.5,7,16,'gold')])
 model['elements']=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]
 dump(path,model)
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s;s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a,1);p.write_text(s,encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static Plan bakery(boolean pastry){');b=s.index('        return p;',a)
s=s[:b]+'''        if(pastry){
            // Clear every old wool row and the duplicate high awning.
            for(int x=2;x<=22;x++){
                p.put(x,5,1,Blocks.AIR);p.put(x,4,1,Blocks.AIR);p.put(x,5,2,Blocks.AIR);p.put(x,6,2,Blocks.AIR);
                if(x<=10||x>=15)p.put(x,5,2,Furniture.SHOP_AWNING_ROSE.get());
                if(x<=10||x>=15)p.put(x,1,2,Furniture.SWEET_ORNATE_SILL.get());
            }
            // Rebuild the entire entrance on the front wall, including the missing side jamb.
            for(int x:new int[]{11,14})p.box(x,1,3,x,3,3,Furniture.SWEET_FLUTED_COLUMN.get());
            for(int x=12;x<=13;x++){
                p.put(x,0,3,Blocks.POLISHED_DIORITE);
                p.put(x,3,3,Furniture.SWEET_WINDOW.get());
                BlockState ds=Blocks.CHERRY_DOOR.defaultBlockState().setValue(DoorBlock.FACING,Direction.NORTH)
                    .setValue(DoorBlock.HINGE,x==12?net.minecraft.world.level.block.state.properties.DoorHingeSide.LEFT:net.minecraft.world.level.block.state.properties.DoorHingeSide.RIGHT);
                p.put(x,1,3,ds.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER));
                p.put(x,2,3,ds.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER));
            }
            p.put(12,6,3,Furniture.SWEET_SIGN.get());
            p.put(11,6,3,Furniture.SWEET_CARVED_PANEL.get());
            p.put(13,6,3,Furniture.SWEET_CARVED_PANEL.get());
            // Two-sided projecting sign mounted directly on the entrance pier.
            p.put(15,4,2,Furniture.SWEET_HANGING_SIGN.get());
            for(int x:new int[]{1,23})for(int z:new int[]{3,21})for(int y=1;y<=7;y++)p.put(x,y,z,Furniture.SWEET_FLUTED_COLUMN.get());
            for(int x:new int[]{2,9,15,22})for(int y=2;y<=4;y++)p.put(x,y,3,Furniture.SWEET_FLUTED_COLUMN.get());
            // Replace old dark oak roof rings and ridge with glazed ceramic and brass eaves.
            Block tile=Furniture.SWEET_CERAMIC_ROOF.get();
            for(int k=0;k<4;k++){
                int l=k,r=24-k,n=2+k,f=22-k,y=9+k;
                p.ring(l,y,n,r,f,tile);
                for(int x=l;x<=r;x++){
                    royalFacing(p,x,y,n,Furniture.SWEET_CERAMIC_EAVE.get(),Direction.NORTH);
                    royalFacing(p,x,y,f,Furniture.SWEET_CERAMIC_EAVE.get(),Direction.SOUTH);
                }
                for(int z=n+1;z<f;z++){
                    royalFacing(p,l,y,z,Furniture.SWEET_CERAMIC_EAVE.get(),Direction.WEST);
                    royalFacing(p,r,y,z,Furniture.SWEET_CERAMIC_EAVE.get(),Direction.EAST);
                }
                if(k<3)p.ring(l+1,y,n+1,r-1,f-1,tile);
            }
            p.box(4,12,6,20,12,18,tile);
            for(int x=0;x<=24;x++)p.put(x,8,2,Furniture.SWEET_CORNICE.get());
        }
'''+s[b:];p.write_text(s,encoding='utf-8')
print('Patisserie: removed legacy wool, complete entrance, improved shop awnings, glazed ceramic roof, fluted stucco columns and perpendicular two-sided shop sign.')
