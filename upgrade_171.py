"""1.7.1: contemporary fast-food restaurant, new furniture and custom signs."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
 p.parent.mkdir(parents=True,exist_ok=True)
 def ch(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
palette={'oak':(155,106,64),'cream':(237,229,213),'red':(178,30,36),'yellow':(248,193,29),'charcoal':(46,48,46),'steel':(165,176,179),'black':(25,29,31),'white':(245,244,232),'bun':(223,156,68),'meat':(92,53,35),'lettuce':(97,156,57),'light':(255,243,190),'green':(65,113,76),'screen':(33,49,53)}
for m,c in palette.items():
 pix=bytearray()
 for y in range(64):
  for x in range(64):
   v=.89+.08*math.sin(x*.19)**2+.13*math.exp(-((x-18)/7)**2)+.02*math.cos(x*2+y)
   if m=='oak':v*=.78+.22*math.sin(y*.95+math.sin(x*.12))**2
   if min(x,y,63-x,63-y)<1:v*=.74
   pix.extend((*[max(0,min(255,int(a*v))) for a in c],255))
 png(assets/'textures/block'/f'fast_{m}.png',64,64,pix)
# Self-contained artwork: true curved golden arches, illustrated menu cards and clear mullioned glass.
def artwork(name,w,h,fn):
 pix=bytearray()
 for y in range(h):
  for x in range(w):pix.extend(fn(x,y))
 png(assets/'textures/block'/f'fast_{name}.png',w,h,pix)
def logo(x,y):
 X=x/127;Y=y/127
 # Two arches with legs extending to the bottom, on a dark red sign.
 arch=False
 for center in (.32,.68):
  dx=(X-center)/.185;dy=(Y-.76)/.53
  if Y<=.76 and .68<=math.hypot(dx,dy)<=1.13:arch=True
  if .72<=Y<=.89 and abs(abs(dx)-.9)<.25:arch=True
 if arch:return (255,198,24,255)
 if min(x,y,127-x,127-y)<3:return (59,38,32,255)
 return (150+int(12*math.sin(Y*3)),21,28,255)
artwork('logo',128,128,logo)
def window(x,y):
 if min(x,y,63-x,63-y)<2:return (72,78,77,255)
 if abs(x+y-24)<1 or abs(x+y-31)<1:return (240,255,255,125)
 return (203,233,240,34)
artwork('window',64,64,window)
def foodpic(n,x,y):
 # Pixel illustration on a warm menu background.
 if n==0:
  if 14<x<50 and 17<y<25 and ((x-32)/19)**2+((y-25)/9)**2<1:return (222,155,63,255)
  if 14<x<50 and 25<=y<29:return (104,168,52,255)
  if 15<x<49 and 29<=y<35:return (93,51,32,255)
  if 15<x<49 and 35<=y<40:return (218,145,62,255)
 elif n==1:
  if 18<x<46 and 10<y<33 and (x%7<4):return (244,189,58,255)
  if 17<x<47 and 28<y<45:return (182,27,34,255)
 elif n==2:
  if 22<x<43 and 15<y<45:return (176,35,42,255)
  if 19<x<46 and 13<y<18:return (236,233,217,255)
  if 31<x<34 and 5<y<14:return (237,193,46,255)
 else:
  if any(((x-a)/7)**2+((y-b)/5)**2<1 for a,b in [(23,24),(38,22),(30,36),(44,35)]):return (207,132,51,255)
 return None
glyph={'B':['11110','10001','11110','10001','11110'],'U':['10001','10001','10001','10001','01110'],'R':['11110','10001','11110','10100','10010'],'G':['01111','10000','10111','10001','01111'],'E':['11111','10000','11110','10000','11111'],'F':['11111','10000','11110','10000','10000'],'I':['111','010','010','010','111'],'S':['01111','10000','01110','00001','11110'],'C':['01111','10000','10000','10000','01111'],'O':['01110','10001','10001','10001','01110'],'L':['10000','10000','10000','10000','11111'],'A':['01110','10001','11111','10001','10001'],'N':['10001','11001','10101','10011','10001'],'T':['11111','00100','00100','00100','00100'],'1':['010','110','010','010','111']}
def menu(n,x,y):
 if min(x,y,63-x,63-y)<2:return (32,36,35,255)
 if y<10:return (169,28,35,255)
 pic=foodpic(n,x,y)
 if pic:return pic
 word=['BURGER','FRIES','COLA','NUGGETS'][n];start=32-(len(word)*6-1)//2
 if 48<=y<53:
  for i,c in enumerate(word):
   xx=x-start-i*6;g=glyph.get(c)
   if g and 0<=xx<len(g[0]) and g[y-48][xx]=='1':return (42,39,34,255)
 if 56<=y<=60 and 29<=x<=31 and glyph['1'][y-56][x-29]=='1':return (160,27,35,255)
 return (249,239,214,255)
for i in range(4):artwork('menu'+str(i),64,64,lambda x,y,i=i:menu(i,x,y))
# Models fit within the block, with separate geometry rather than repainted stairs.
chair=[(x,0,z,x+2,7,z+2,'steel') for x in (2,12) for z in (2,12)]+[(1,7,1,15,9,15,'charcoal'),(2,9,2,14,10,13,'red'),(2,9,13,4,16,15,'steel'),(12,9,13,14,16,15,'steel'),(4,10,13,12,15,15,'red')]
booth=[(0,0,2,16,4,16,'charcoal'),(0,4,2,16,9,14,'red'),(0,9,12,16,16,16,'red'),(0,15,12,16,16,16,'oak'),(0,4,1,16,5,2,'charcoal')]
table=[(2,0,2,14,2,14,'steel'),(6,2,6,10,12,10,'charcoal'),(0,12,0,16,14,16,'oak'),(0,14,0,16,16,16,'cream')]
counter=[(0,0,0,16,2,16,'charcoal'),(0,2,1,16,14,15,'oak'),(0,3,0,16,12,1,'red'),(0,12,0,16,14,1,'yellow'),(0,14,0,16,16,16,'cream')]
kiosk=[(3,0,3,13,2,13,'steel'),(6,2,6,10,8,10,'charcoal'),(3,8,5,13,16,12,'charcoal'),(4,9,4,12,15,5,'menu0'),(6,8,3,10,9,5,'steel')]
register=[(2,0,3,14,2,13,'charcoal'),(7,2,7,9,7,9,'steel'),(2,7,5,14,14,10,'black'),(3,8,4,13,13,5,'screen'),(3,1,1,13,3,5,'steel')]
tray=[(1,0,1,15,1,15,'red'),(2,1,2,14,2,14,'white'),(3,2,4,9,4,10,'bun'),(3,4,4,9,5,10,'meat'),(3,5,4,9,6,10,'lettuce'),(3,6,4,9,8,10,'bun'),(10,2,3,14,6,7,'red'),(10,6,3,11,9,4,'yellow'),(12,6,5,13,9,6,'yellow'),(10,2,10,14,8,14,'white'),(11,8,11,12,11,12,'red')]
fryer=[(1,0,1,15,13,15,'steel'),(0,13,0,16,15,16,'steel'),(2,15,2,8,16,14,'black'),(9,15,2,14,16,14,'black'),(3,15,3,7,16,13,'yellow'),(3,4,0,13,8,1,'charcoal'),(4,5,0,6,7,1,'red')]
soda=[(1,0,1,15,2,15,'steel'),(1,2,10,15,16,15,'charcoal'),(1,12,2,15,16,10,'red'),(2,13,1,14,15,2,'white')]+[(x,8,8,x+2,12,10,'steel') for x in (3,7,11)]
binbox=[(2,0,2,14,14,14,'charcoal'),(1,13,1,15,16,15,'oak'),(4,8,1,12,12,2,'black'),(5,3,1,11,6,2,'yellow')]
lamp=[(1,12,1,15,16,15,'charcoal'),(2,11,2,14,12,14,'light'),(1,10,1,2,12,15,'steel'),(14,10,1,15,12,15,'steel')]
planter=[(1,0,1,15,5,15,'oak'),(2,5,2,14,6,14,'charcoal'),(6,6,6,10,14,10,'green'),(3,9,3,13,12,13,'green'),(5,13,4,12,16,12,'green')]
panel=lambda mat:[(0,0,13,16,16,16,'charcoal'),(0,0,12,16,16,13,mat)]
items={'fast_chair':('Sedia fast food','Fast food chair',0,chair),'fast_booth':('Divanetto imbottito','Upholstered booth',0,booth),'fast_table':('Tavolo fast food','Fast food table',0,table),'fast_counter':('Bancone moderno','Modern counter',0,counter),'fast_kiosk':('Totem ordinazioni','Ordering kiosk',0,kiosk),'fast_register':('Cassa touch','Touch register',0,register),'fast_tray':('Vassoio menu completo','Meal tray',0,tray),'fast_fryer':('Friggitrice industriale','Industrial fryer',0,fryer),'fast_soda':('Distributore bibite','Soda fountain',0,soda),'fast_bin':('Cestino raccolta vassoi','Tray return bin',0,binbox),'fast_lamp':('Pannello LED','LED panel',3,lamp),'fast_planter':('Fioriera moderna','Modern planter',0,planter),'fast_logo':('Insegna archi dorati','Golden arches sign',0,panel('logo')),'fast_window':('Vetrata moderna','Modern window',-1,[])}
for i in range(4):items['fast_menu'+str(i)]=(f'Menu luminoso {i+1}',f'Illuminated menu {i+1}',3,panel('menu'+str(i)))
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
  model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/fast_window'},'render_type':'minecraft:translucent'};variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tex={m:'noctismagic:block/fast_'+m for m in list(palette)+['logo','menu0','menu1','menu2','menu3']};tex['particle']=tex['oak']
  el=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{face:{'texture':'#'+m,'uv':[0,0,16,16]} for face in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]
  model={'textures':tex,'elements':el,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]}}}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n});dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
for loc in ('it_it','en_us'):
 f=assets/'lang'/f'{loc}.json';d=json.loads(f.read_text(encoding='utf-8'))
 for n,(it,en,k,boxes) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(f,d)
# Generate the golden arches as 4x3 large wall tiles with consistent UV art.
for yy in range(3):
 for xx in range(4):
  name=f'fast_logo_tile_{xx}_{yy}'
  # All tiles are separate registered blocks via a shared material and per-tile UVs.
  # This is intentionally not used; the large sign below is drawn with curved block geometry.
  pass
f=java/'GothicEgg.java';s=f.read_text(encoding='utf-8')
a=s.index('    static Plan fastFood(){');b=s.index('    static Plan shrekSwamp(){',a)
s=s[:a]+'''    static Plan fastFood(){
        Plan p=new Plan(33,27,12,"McDonald's - Fast food");
        Block win=Furniture.FAST_WINDOW.get();
        for(int x=0;x<33;x++)for(int z=0;z<27;z++){
            Block floor=z<5?Blocks.GRAY_CONCRETE:((x+z)%5==0?Blocks.POLISHED_ANDESITE:Blocks.SMOOTH_QUARTZ);
            p.put(x,0,z,floor);
        }
        p.walls(1,1,5,31,7,25,Blocks.WHITE_CONCRETE);
        p.box(1,8,5,31,8,25,Blocks.GRAY_CONCRETE);
        p.ring(0,8,4,32,26,Blocks.DARK_OAK_PLANKS);
        p.ring(1,7,5,31,25,Blocks.STRIPPED_DARK_OAK_WOOD);
        p.box(2,6,5,30,6,5,Blocks.RED_CONCRETE);
        for(int x:new int[]{2,12,20,30})p.box(x,1,5,x,7,5,Blocks.STRIPPED_DARK_OAK_WOOD);
        for(int x=3;x<=29;x++)if(x<12||x>20)p.box(x,2,5,x,5,5,x%5==0?Blocks.GRAY_CONCRETE:win);
        p.box(13,1,5,19,4,5,Blocks.AIR);
        p.box(13,5,5,19,7,5,Blocks.GRAY_CONCRETE);
        p.box(12,5,3,20,5,5,Blocks.DARK_OAK_PLANKS);
        p.box(12,6,3,20,6,3,Blocks.RED_CONCRETE);
        // Smooth sign on an elevated facade, not the former rectangular letter.
        p.box(11,8,5,21,10,5,Blocks.GRAY_CONCRETE);
        for(int x=12;x<=20;x++)p.put(x,10,4,Blocks.YELLOW_CONCRETE);
        for(int x:new int[]{12,16,20})p.box(x,8,4,x,9,4,Blocks.YELLOW_CONCRETE);
        p.put(13,9,4,Blocks.YELLOW_CONCRETE);p.put(19,9,4,Blocks.YELLOW_CONCRETE);
        p.put(14,10,4,Blocks.GRAY_CONCRETE);p.put(18,10,4,Blocks.GRAY_CONCRETE);
        for(int x:new int[]{14,18})p.put(x,9,4,Blocks.YELLOW_CONCRETE);
        royalFacing(p,16,6,2,Furniture.FAST_LOGO.get(),Direction.NORTH);
        for(int z=7;z<=22;z++)for(int x:new int[]{1,31}){
            if(z%5==0)p.box(x,1,z,x,7,z,Blocks.STRIPPED_DARK_OAK_WOOD);
            else p.box(x,2,z,x,5,z,win);
        }
        for(int x=3;x<=29;x+=4)p.box(x,7,6,x,7,24,Blocks.STRIPPED_BIRCH_WOOD);
        for(int x:new int[]{4,10,16,22,28})for(int z:new int[]{8,13,18,23})p.put(x,7,z,Furniture.FAST_LAMP.get());
        // Seating: continuous booths against the windows and freestanding tables.
        for(int z:new int[]{9,14})for(int x:new int[]{5,11,21,27}){
            p.put(x,1,z,Furniture.FAST_TABLE.get());
            p.put(x,2,z,Furniture.FAST_TRAY.get());
            royalFacing(p,x-1,1,z,Furniture.FAST_CHAIR.get(),Direction.EAST);
            royalFacing(p,x+1,1,z,Furniture.FAST_CHAIR.get(),Direction.WEST);
        }
        for(int z=8;z<=14;z++){
            royalFacing(p,2,1,z,Furniture.FAST_BOOTH.get(),Direction.EAST);
            royalFacing(p,30,1,z,Furniture.FAST_BOOTH.get(),Direction.WEST);
        }
        for(int z:new int[]{9,13}){
            p.put(3,1,z,Furniture.FAST_TABLE.get());p.put(29,1,z,Furniture.FAST_TABLE.get());
        }
        for(int x:new int[]{11,21}){
            p.put(x,1,7,Furniture.FAST_KIOSK.get());
            p.put(x,1,6,Furniture.FAST_PLANTER.get());
        }
        for(int x:new int[]{4,28})p.put(x,1,6,Furniture.FAST_BIN.get());
        for(int x=4;x<=28;x++)if(x<14||x>18)p.put(x,1,17,Furniture.FAST_COUNTER.get());
        for(int x:new int[]{7,12,20,25})p.put(x,2,17,Furniture.FAST_REGISTER.get());
        for(int x:new int[]{5,9,23,27})p.put(x,2,17,Furniture.FAST_TRAY.get());
        // Suspended menu boards are fixed to a crossbeam.
        p.box(4,6,18,28,6,18,Blocks.GRAY_CONCRETE);
        Block[] menu={Furniture.FAST_MENU0.get(),Furniture.FAST_MENU1.get(),Furniture.FAST_MENU2.get(),Furniture.FAST_MENU3.get()};
        for(int i=0;i<4;i++){
            int x=6+i*6;
            p.box(x-1,4,18,x+1,5,18,Blocks.GRAY_CONCRETE);
            royalFacing(p,x,5,17,menu[i],Direction.NORTH);
            royalFacing(p,x+1,5,17,menu[i],Direction.NORTH);
            p.put(x,6,17,Blocks.IRON_BARS);p.put(x+1,6,17,Blocks.IRON_BARS);
        }
        // Fully furnished stainless kitchen with work stations.
        for(int x=4;x<=28;x++)p.put(x,1,24,Furniture.FAST_COUNTER.get());
        for(int x:new int[]{5,8,22,25}){
            p.put(x,1,23,Furniture.FAST_FRYER.get());
            p.put(x,4,23,Blocks.IRON_BLOCK);
            p.put(x,5,23,Blocks.IRON_BLOCK);
        }
        p.put(11,1,23,Furniture.FAST_SODA.get());p.put(20,1,23,Furniture.FAST_SODA.get());
        p.put(3,1,22,Furniture.FRIDGE.get());p.put(29,1,22,Furniture.DISHWASHER.get());
        p.put(12,1,24,Blocks.CRAFTING_TABLE);p.put(19,1,24,Blocks.CAULDRON);
        for(int x:new int[]{6,10,14,18,22,26})p.put(x,3,25,Furniture.MODERN_CABINET.get());
        for(int x:new int[]{4,10,22,28})p.box(x,0,1,x,0,3,Blocks.WHITE_CONCRETE);
        // Exterior bollards, planted beds and marked entrance.
        for(int x:new int[]{2,30}){p.put(x,1,3,Furniture.FAST_PLANTER.get());p.put(x,1,4,Furniture.FAST_PLANTER.get());}
        for(int x:new int[]{13,19})p.put(x,1,3,Blocks.POLISHED_BLACKSTONE_WALL);
        for(int x=14;x<=18;x++)p.put(x,0,4,Blocks.SMOOTH_STONE);
        return p;
    }
'''+s[b:]
f.write_text(s,encoding='utf-8')
print('McDonalds: 18 dedicated blocks with menu illustrations, custom glass, booths, chairs, tills, trays, kitchen and improved facade.')
