"""1.6.9 Valdracula: original gothic furniture, stained glass, royal hall and towers."""
from pathlib import Path
import sys,json,math,struct,zlib,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
 p.parent.mkdir(parents=True,exist_ok=True)
 def ch(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
palette={'ebony':(51,27,28),'bronze':(181,119,52),'gold':(220,174,79),'velvet':(104,12,35),'dark':(29,26,35),'silver':(133,143,156),'marble':(207,196,175),'ruby':(157,21,51),'candle':(255,224,158),'bookred':(106,31,39),'bookblue':(43,59,91),'bookgreen':(42,78,58),'paper':(225,205,160),'steel':(78,89,110)}
for m,col in palette.items():
 N=64;pix=bytearray()
 for y in range(N):
  for x in range(N):
   v=.9+.035*math.sin(x*1.7+y*.17)+.035*math.cos(y*1.6+x*.3)
   if m=='ebony':v=.72+.22*math.sin(x*.6+math.sin(y*.16))**2+.13*math.exp(-((x-14)/5)**2)
   if m in ('bronze','gold','silver','steel'):v=.69+.41*math.exp(-((x-20)/12)**2)+.14*math.exp(-((x-45)/4)**2)
   if m=='velvet':v=.78+.13*math.cos(x*.17)+.07*math.cos(y*.27)+.06*math.sin((x+y)*2.1)
   if m=='marble':v=.93+.06*math.sin((x+y)*.17+2*math.sin(y*.11))
   if m=='candle':v=.88+.16*math.exp(-((x-32)/17)**2)
   c=tuple(max(0,min(255,int(a*v))) for a in col)
   if m=='velvet' and ((x-32)**2+(y-32)**2<10 or abs((x+y)%32-16)<.6 or abs((x-y)%32-16)<.6):c=tuple(int(a*.67) for a in c)
   if min(x,y,N-1-x,N-1-y)==0:c=tuple(int(a*.64) for a in c)
   pix.extend((*c,255))
 png(assets/'textures/block'/('royal_'+m+'.png'),N,N,pix)
# Original leaded glass, each color has a gold filigree and jewel-like rose.
glasscols=[(170,34,55),(36,89,183),(118,53,166),(224,154,49),(33,155,141)]
for i,col in enumerate(glasscols):
 N=64;pix=bytearray()
 for y in range(N):
  for x in range(N):
   dx=x-31.5;dy=y-31.5;r=math.hypot(dx,dy);a=math.atan2(dy,dx)
   lead=min(x,y,63-x,63-y)<2 or abs(r-26)<1.2 or abs(r-13)<1.15 or (r>8 and abs(math.sin(a*6))*r<1.05) or (r>27 and abs(abs(dx)-abs(dy))<1.3)
   if lead:rgba=(55,43,40,255)
   elif r<6:rgba=(247,196,91,235)
   else:
    v=.65+.23*math.sin(a*3+.4)**2+.24*math.exp(-((r-18)/8)**2)+.045*math.sin(x*2+y)
    rgba=(*[max(0,min(255,int(c*v+22))) for c in col],205)
   pix.extend(rgba)
 png(assets/'textures/block'/f'royal_glass_{i}.png',N,N,pix)
def legs(h,m='ebony'):return [(x,0,z,x+2,h,z+2,m) for x in (1,13) for z in (1,13)]
chair=legs(7)+[(1,7,1,15,9,15,'ebony'),(2,9,2,14,11,13,'velvet'),(1,9,13,3,16,15,'gold'),(13,9,13,15,16,15,'gold'),(3,10,13,13,15,15,'velvet'),(1,15,13,15,16,15,'bronze'),(6,13,12,10,15,13,'gold')]
table=legs(12)+[(0,12,0,16,14,16,'ebony'),(0,14,0,16,16,16,'ebony'),(0,13,0,16,14,1,'gold'),(0,13,15,16,14,16,'gold'),(0,13,1,1,14,15,'gold'),(15,13,1,16,14,15,'gold')]
seat=[(0,0,0,16,3,16,'ebony'),(1,3,1,15,5,15,'gold'),(1,5,1,15,12,15,'velvet'),(0,11,0,16,12,16,'bronze'),(1,12,1,15,16,15,'velvet')]
arm=[(2,0,2,14,3,14,'ebony'),(4,3,4,12,12,12,'bronze'),(2,11,1,14,14,15,'velvet'),(2,14,1,14,15,15,'gold'),(5,4,2,11,9,4,'ruby')]
back=[(0,0,9,16,16,16,'ebony'),(1,1,7,15,15,10,'velvet'),(0,0,6,2,16,10,'gold'),(14,0,6,16,16,10,'gold'),(4,5,6,12,11,7,'ruby'),(6,7,5,10,9,6,'gold')]
crown=[(0,0,9,16,5,16,'ebony'),(1,2,7,15,5,10,'gold'),(2,5,9,14,8,15,'bronze'),(4,8,9,12,11,15,'gold'),(6,11,9,10,15,15,'gold'),(7,12,7,9,14,9,'ruby'),(0,5,9,3,10,15,'gold'),(13,5,9,16,10,15,'gold')]
boots=[(1,0,1,15,2,15,'marble'),(3,2,4,7,9,12,'steel'),(9,2,4,13,9,12,'steel'),(2,2,2,7,4,11,'silver'),(9,2,2,14,4,11,'silver'),(2,9,3,14,15,13,'steel'),(3,13,2,13,16,14,'silver'),(3,10,2,13,12,4,'bronze')]
body=[(3,0,4,13,10,13,'steel'),(4,1,2,12,8,5,'silver'),(1,6,4,5,11,12,'silver'),(11,6,4,15,11,12,'silver'),(1,0,5,4,7,10,'steel'),(12,0,5,15,7,10,'steel'),(6,3,1,10,7,3,'gold'),(7,0,0,9,5,2,'silver'),(5,10,4,11,13,12,'steel'),(4,13,4,12,16,12,'silver')]
head=[(4,0,3,12,8,13,'steel'),(3,2,2,13,7,5,'silver'),(4,4,1,12,5,3,'dark'),(7,0,1,9,4,3,'gold'),(5,8,4,11,10,12,'silver'),(7,10,5,9,14,11,'ruby')]
lamp=[(6,0,6,10,4,10,'bronze'),(2,4,2,14,6,14,'gold'),(6,6,6,10,16,10,'bronze'),(1,6,1,4,8,4,'gold'),(12,6,1,15,8,4,'gold'),(1,6,12,4,8,15,'gold'),(12,6,12,15,8,15,'gold')]
for x in (2,12):
 for z in (2,12):lamp.extend([(x,8,z,x+2,13,z+2,'candle'),(x,13,z,x+2,15,z+2,'candle')])
sconce=[(5,2,13,11,14,16,'bronze'),(6,5,5,10,8,14,'gold'),(4,7,3,12,9,11,'bronze'),(6,9,5,10,14,9,'candle'),(7,14,6,9,16,8,'candle')]
bookcase=[(0,0,0,16,1,16,'ebony'),(0,0,13,16,16,16,'ebony'),(0,0,1,2,16,15,'ebony'),(14,0,1,16,16,15,'ebony')]
for y in (0,5,10,15):bookcase.extend([(0,y,1,16,y+1,15,'ebony'),(0,y,0,16,y+1,1,'gold')])
for y in (1,6,11):
 for x in range(2,14,2):bookcase.extend([(x,y,4,x+1.7,y+3.5,13,['bookred','bookblue','bookgreen'][int(x+y)%3]),(x,y+.6,3.8,x+1.7,y+1,4,'gold')])
cabinet=[(1,0,1,15,15,15,'ebony'),(0,14,0,16,16,16,'bronze'),(2,2,0,7,13,1,'velvet'),(9,2,0,14,13,1,'velvet'),(6,6,0,7,9,1,'gold'),(9,6,0,10,9,1,'gold')]
banner=[(0,0,13,16,16,15,'velvet'),(0,0,12,2,16,13,'gold'),(14,0,12,16,16,13,'gold'),(5,5,12,11,11,13,'gold'),(7,3,11,9,13,12,'gold')]
crest=[(1,1,13,15,15,15,'bronze'),(2,2,12,14,14,13,'velvet'),(4,4,11,12,12,12,'gold'),(6,6,10,10,10,11,'ruby'),(1,7,11,4,9,13,'gold'),(12,7,11,15,9,13,'gold')]
vase=[(4,0,4,12,2,12,'bronze'),(5,2,5,11,5,11,'marble'),(3,5,3,13,10,13,'marble'),(4,10,4,12,12,12,'gold'),(6,12,6,10,15,10,'marble'),(5,15,5,11,16,11,'bronze')]
plate=[(2,0,2,14,1,14,'bronze'),(3,1,3,13,2,13,'marble'),(5,2,5,11,4,11,'ruby'),(1,1,1,2,3,13,'gold')]
items={
 'royal_throne_seat':('Seduta del trono','Throne seat',0,seat),
 'royal_throne_arm':('Bracciolo del trono','Throne arm',0,arm),
 'royal_throne_back':('Schienale del trono','Throne back',0,back),
 'royal_throne_crown':('Corona del trono','Throne crown',0,crown),
 'royal_chair':('Sedia gotica','Gothic chair',0,chair),
 'royal_table':('Tavolo gotico','Gothic table',0,table),
 'royal_knight_legs':('Statua armata: gambe','Armored statue legs',0,boots),
 'royal_knight_body':('Statua armata: busto','Armored statue torso',0,body),
 'royal_knight_head':('Statua armata: elmo','Armored statue helmet',0,head),
 'royal_chandelier':('Lampadario barocco','Baroque chandelier',3,lamp),
 'royal_sconce':('Candelabro da parete','Wall candelabra',3,sconce),
 'royal_bookcase':('Libreria intagliata','Carved bookcase',0,bookcase),
 'royal_cabinet':('Credenza nobiliare','Noble cabinet',0,cabinet),
 'royal_banner':('Arazzo reale','Royal tapestry',0,banner),
 'royal_crest':('Stemma di Valdracula','Valdracula crest',0,crest),
 'royal_vase':('Vaso di marmo','Marble vase',0,vase),
 'royal_plate':('Stoviglie nobiliari','Royal tableware',0,plate)
}
for i in range(5):items[f'royal_glass_{i}']=(f'Vetrata a mosaico {i+1}',f'Mosaic stained glass {i+1}',-1,[])
decl=[]
for n,(it,en,k,boxes) in items.items():
 expr='new GlassBlock(BlockBehaviour.Properties.copy(Blocks.GLASS).noOcclusion())' if k==-1 else f'new FurnitureBlock({k})'
 decl.extend([f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));'])
f=java/'Furniture.java';s=f.read_text(encoding='utf-8');a='public class Furniture{';assert a in s
s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);f.write_text(s,encoding='utf-8')
f=java/'Noctis.java';s=f.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s
s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a,1);f.write_text(s,encoding='utf-8')
for n,(it,en,k,boxes) in items.items():
 if k==-1:
  model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/'+n},'render_type':'minecraft:translucent'}
  variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tex={m:'noctismagic:block/royal_'+m for m in palette};tex['particle']=tex['ebony']
  elements=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{face:{'texture':'#'+m,'uv':[0,0,16,16]} for face in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]
  model={'textures':tex,'elements':elements,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]},'ground':{'translation':[0,3,0],'scale':[.25,.25,.25]}}}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
 dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
for loc in ('it_it','en_us'):
 f=assets/'lang'/f'{loc}.json';d=json.loads(f.read_text(encoding='utf-8'))
 for n,(it,en,k,boxes) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(f,d)
# Upgrade existing vanilla stained-glass override files only if present inside this mod.
# Correct models are generated for any overrides rather than guessing which external pack is installed.
mc=res/'assets/minecraft'
for color in ('white','orange','magenta','light_blue','yellow','lime','pink','gray','light_gray','cyan','purple','blue','brown','green','red','black'):
 name=color+'_stained_glass'
 model=mc/'models/block'/f'{name}.json'
 if model.exists():dump(model,{'parent':'minecraft:block/cube_all','textures':{'all':'minecraft:block/'+name},'render_type':'minecraft:translucent'})
 state=mc/'blockstates'/f'{name}.json'
 if state.exists():dump(state,{'variants':{'':{'model':'minecraft:block/'+name}}})
f=java/'GothicEgg.java';s=f.read_text(encoding='utf-8')
a='    static Plan castle(){';assert a in s
s=s.replace(a,'''    static Block[] royalGlass(){
        return new Block[]{Furniture.ROYAL_GLASS_0.get(),Furniture.ROYAL_GLASS_1.get(),Furniture.ROYAL_GLASS_2.get(),Furniture.ROYAL_GLASS_3.get(),Furniture.ROYAL_GLASS_4.get()};
    }
    static void royalFacing(Plan p,int x,int y,int z,Block b,Direction d){p.put(x,y,z,b.defaultBlockState().setValue(HorizontalDirectionalBlock.FACING,d));}
    static void royalKnight(Plan p,int x,int y,int z,Direction d){
        p.box(x-1,y,z-1,x+1,y,z+1,Blocks.POLISHED_BLACKSTONE_BRICKS);
        royalFacing(p,x,y+1,z,Furniture.ROYAL_KNIGHT_LEGS.get(),d);
        royalFacing(p,x,y+2,z,Furniture.ROYAL_KNIGHT_BODY.get(),d);
        royalFacing(p,x,y+3,z,Furniture.ROYAL_KNIGHT_HEAD.get(),d);
    }
    static void royalWindows(Plan p){
        Block[] glass=royalGlass();
        for(var entry:p.blocks.entrySet()){
            BlockState b=entry.getValue();
            for(int i=0;i<GLASS.length;i++)if(b.is(GLASS[i])){entry.setValue(glass[i].defaultBlockState());break;}
        }
    }
    static void royalHall(Plan p){
        // Remove the original small wool throne, and rebuild a five-wide elevated dais.
        p.box(39,1,77,51,8,85,Blocks.AIR);
        p.box(39,1,77,51,1,85,Blocks.POLISHED_BLACKSTONE_BRICKS);
        p.box(41,2,79,49,2,84,Blocks.CHISELED_STONE_BRICKS);
        p.box(42,3,80,48,3,84,Blocks.POLISHED_BLACKSTONE);
        for(int x=42;x<=48;x++){
            p.stair(x,1,77,Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS,Direction.SOUTH);
            p.stair(x,2,78,Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS,Direction.SOUTH);
            p.stair(x,3,79,Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS,Direction.SOUTH);
        }
        p.put(45,4,81,Furniture.ROYAL_THRONE_SEAT.get());
        for(int x:new int[]{44,46})p.put(x,4,81,Furniture.ROYAL_THRONE_ARM.get());
        for(int x=44;x<=46;x++)for(int y=4;y<=6;y++)p.put(x,y,82,Furniture.ROYAL_THRONE_BACK.get());
        for(int x=44;x<=46;x++)p.put(x,7,82,Furniture.ROYAL_THRONE_CROWN.get());
        for(int x:new int[]{41,49}){
            p.box(x,4,83,x,10,83,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
            p.put(x,10,83,Blocks.CHISELED_STONE_BRICKS);
            p.put(x,4,80,Furniture.ROYAL_CHANDELIER.get());
        }
        p.box(41,10,82,49,10,84,Blocks.POLISHED_BLACKSTONE_BRICKS);
        p.box(42,9,82,48,9,82,Blocks.RED_WOOL);
        p.put(45,8,83,Furniture.ROYAL_CREST.get());
        for(int z=36;z<=76;z++)for(int x=41;x<=49;x++){
            p.put(x,1,z,Math.abs(x-45)==4?Blocks.BLACK_CARPET:Math.abs(x-45)==3?Blocks.YELLOW_CARPET:Blocks.RED_CARPET);
            if(z%6==0&&Math.abs(x-45)==2)p.put(x,1,z,Blocks.YELLOW_CARPET);
        }
        // Replace the block crosses with detailed three-piece armored sculptures.
        for(int z=40;z<=80;z+=8)for(int x:new int[]{35,55}){
            p.box(x-1,1,z-1,x+1,7,z+1,Blocks.AIR);
            royalKnight(p,x,1,z,x==35?Direction.EAST:Direction.WEST);
            p.put(x,1,z+2,Furniture.ROYAL_CHANDELIER.get());
            royalFacing(p,x==35?32:58,5,z,Furniture.ROYAL_SCONCE.get(),x==35?Direction.EAST:Direction.WEST);
        }
        // Lower candle lamps and rich hanging tapestries between pilasters.
        for(int z=44;z<=76;z+=8){
            for(int x:new int[]{34,56}){
                for(int y=5;y<=8;y++)royalFacing(p,x,y,z,Furniture.ROYAL_BANNER.get(),x==34?Direction.EAST:Direction.WEST);
                royalFacing(p,x,9,z,Furniture.ROYAL_CREST.get(),x==34?Direction.EAST:Direction.WEST);
            }
            for(int x:new int[]{39,51}){
                p.box(x,15,z,x,21,z,Blocks.CHAIN);
                p.put(x,14,z,Furniture.ROYAL_CHANDELIER.get());
                for(int dx:new int[]{-1,1})p.put(x+dx,14,z,Furniture.ROYAL_CHANDELIER.get());
            }
        }
        // Council seating and side tables, outside the central ceremonial aisle.
        for(int z:new int[]{47,55,63,71})for(int x:new int[]{38,52}){
            p.put(x,1,z,Furniture.ROYAL_TABLE.get());p.put(x,2,z,Furniture.ROYAL_VASE.get());
            royalFacing(p,x,1,z+2,Furniture.ROYAL_CHAIR.get(),Direction.NORTH);
        }
        // Tall colored mosaics in the rear wall above the throne, with pointed frames.
        Block[] glass=royalGlass();
        for(int center:new int[]{39,45,51})for(int dy=0;dy<12;dy++){
            int half=dy<8?2:Math.max(0,2-(dy-8)/2);
            for(int dx=-half;dx<=half;dx++)p.put(center+dx,13+dy,87,dx==0&&dy%4==0?glass[3]:glass[Math.floorMod(Math.abs(dx)+dy/3+(center-39)/6,5)]);
            for(int sign:new int[]{-1,1})p.put(center+sign*(half+1),13+dy,87,Blocks.CHISELED_STONE_BRICKS);
        }
        // Library, dining hall and bedroom use dedicated carved furniture.
        for(int z=38;z<=56;z+=3)for(int y=1;y<=4;y++){
            royalFacing(p,20,y,z,Furniture.ROYAL_BOOKCASE.get(),Direction.EAST);
            royalFacing(p,29,y,z,Furniture.ROYAL_BOOKCASE.get(),Direction.WEST);
        }
        for(int z=64;z<=80;z++){
            p.put(24,2,z,Furniture.ROYAL_TABLE.get());p.put(25,2,z,Furniture.ROYAL_TABLE.get());
            if(z%3==0){p.put(24,3,z,Furniture.ROYAL_PLATE.get());royalFacing(p,22,1,z,Furniture.ROYAL_CHAIR.get(),Direction.EAST);royalFacing(p,27,1,z,Furniture.ROYAL_CHAIR.get(),Direction.WEST);}
        }
        for(int z:new int[]{62,66,80,84}){royalFacing(p,61,1,z,Furniture.ROYAL_CABINET.get(),Direction.EAST);p.put(61,2,z,Furniture.ROYAL_VASE.get());}
    }
    static void royalTowers(Plan p){
        // Sculpted buttresses and corbel belts on perimeter and gatehouse towers.
        int[][] towers={{9,9,7,35},{81,9,7,35},{9,91,7,35},{81,91,7,35},{34,9,5,30},{56,9,5,30},{20,36,6,53},{70,36,6,53},{20,85,6,53},{70,85,6,53}};
        for(int[] t:towers){
            int x=t[0],z=t[1],r=t[2],h=t[3];
            for(int y=5;y<h-4;y+=8){
                p.ring(x-r-1,y,z-r-1,x+r+1,z+r+1,Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);
                for(int dx:new int[]{-r,r})for(int dz:new int[]{-r,r})p.put(x+dx,y+1,z+dz,Blocks.CHISELED_STONE_BRICKS);
            }
            for(int dx:new int[]{-r,r})for(int dz:new int[]{-r,r}){
                int ax=x+dx,az=z+dz;
                p.box(ax,1,az,ax,h-2,az,Blocks.POLISHED_BLACKSTONE_BRICKS);
                for(int y=4;y<h-2;y+=5)p.put(ax,y,az,Blocks.CHISELED_STONE_BRICKS);
                p.put(ax,h-1,az,Blocks.LANTERN);
            }
            for(int d=-r;d<=r;d+=3){
                p.put(x+d,h+1,z-r,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
                p.put(x+d,h+1,z+r,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
                p.put(x-r,h+1,z+d,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
                p.put(x+r,h+1,z+d,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
            }
        }
        for(int x:new int[]{33,57})for(int z:new int[]{35,86}){
            p.box(x,1,z,x,22,z,Blocks.POLISHED_BLACKSTONE_BRICKS);
            for(int y=4;y<22;y+=5)p.put(x,y,z,Blocks.CHISELED_STONE_BRICKS);
            spire(p,x,z,23,2,10);
        }
    }
'''+a,1)
# Install after existing castle decorations, before the castle return.
a=s.index('    static Plan castle(){');b=s.index('        return p;',a)
s=s[:b]+'        royalHall(p);royalTowers(p);royalWindows(p);\n'+s[b:]
# Fix cathedral stained glass with same self-contained assets.
a=s.index('    static Plan cathedral(){');b=s.index('        return p;',a)
s=s[:b]+'        royalWindows(p);\n'+s[b:]
f.write_text(s,encoding='utf-8')
print('Valdracula: 22 original blocks, carved throne and furniture, mosaic glass, statues, lamps and tower trim.')
