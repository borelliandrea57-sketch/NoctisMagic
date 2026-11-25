"""Santa Lacrimosa: original carved masonry, monumental angel statues and cathedral furniture."""
from pathlib import Path
import sys,json,math,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def tex(name,base,style):
 N=64;im=Image.new('RGBA',(N,N));rng=random.Random(name)
 for y in range(N):
  for x in range(N):
   v=.92+.045*math.sin(x*.53+y*.17)+rng.uniform(-.045,.045)
   if style=='brick':
    row=y//16;xx=(x+row%2*16)%32;yy=y%16
    if min(xx,yy,31-xx,15-yy)<1:v*=.40
    elif min(xx,yy,31-xx,15-yy)<3:v*=1.20 if yy<3 or xx<3 else .67
   if style in ('marble','stone'):v+=.075*math.sin((x+y)*.13+3*math.sin(x*.14))
   if style=='flute':v*=.70+.34*math.sin(x*math.pi/16)**2
   if style=='gold':v*=.78+.40*math.sin(x*math.pi/64)**2
   if style=='wood':v*=.76+.25*math.sin(x*.6+math.sin(y*.13))**2
   if style=='velvet':v*=.81+.19*math.sin(x*math.pi/64)**2
   c=tuple(max(0,min(255,int(q*v))) for q in base);im.putpixel((x,y),(*c,255))
 d=ImageDraw.Draw(im)
 if style=='relief':
  d.rectangle((2,2,61,61),outline=(44,40,45),width=2)
  d.rectangle((5,5,58,58),outline=(179,169,152),width=2)
  for a in range(0,360,45):
   t=math.radians(a);cx=32+17*math.cos(t);cy=32+17*math.sin(t)
   d.ellipse((cx-8,cy-8,cx+8,cy+8),fill=(77,71,75),outline=(169,159,143),width=2)
  d.ellipse((23,23,41,41),fill=(105,92,78),outline=(218,188,124),width=2)
 if style=='script':
  d.rectangle((2,2,61,61),outline=(57,48,50),width=2)
  d.rectangle((5,5,58,58),outline=(174,156,129),width=1)
  # Imaginary carved ornamental lettering, no real inscription.
  for y in (13,27,41):
   for x in range(10,54,8):
    d.line([(x,y+8),(x+2,y),(x+5,y+8)],fill=(58,49,49),width=2)
    d.line([(x,y+4),(x+5,y+4)],fill=(142,126,107),width=1)
 if style=='mosaic':
  d.rectangle((0,0,63,63),outline=(41,36,43),width=2)
  d.polygon([(32,4),(60,32),(32,60),(4,32)],fill=(116,38,56),outline=(220,177,99),width=2)
  d.polygon([(32,13),(51,32),(32,51),(13,32)],fill=(43,72,108),outline=(224,187,116),width=2)
  d.ellipse((25,25,39,39),fill=(217,181,104),outline=(77,56,44),width=2)
  for x,y in [(9,9),(54,9),(9,54),(54,54)]:d.ellipse((x-3,y-3,x+3,y+3),fill=(218,194,151))
 if style=='window':
  # The entire leaded lancet panel is a self-contained texture.
  for y in range(N):
   for x in range(N):
    dx=x-31.5;dy=y-31.5;r=math.hypot(dx,dy);a=math.atan2(dy,dx)
    lead=min(x,y,63-x,63-y)<2 or abs(r-22)<1.3 or abs(math.sin(a*4))*r<1.1 or (abs(dx)<1.2 and abs(dy)>22)
    if lead:c=(51,43,43,255)
    elif r<5:c=(255,220,122,240)
    else:
     colors=[base,(190,56,70),(49,104,171),(226,169,66)]
     col=colors[int((a+math.pi)*2/math.pi)%4] if r<22 else base
     v=.76+.20*math.sin(a*4+.7)**2+.09*math.exp(-((r-14)/7)**2)
     c=(*[max(0,min(255,int(q*v+15))) for q in col],218)
    im.putpixel((x,y),c)
 p=assets/'textures/block'/('lacrimosa_'+name+'.png');p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
palette={'ash':((91,87,91),'brick'),'ashlight':((133,126,124),'brick'),'slate':((56,52,65),'brick'),'marble':((216,208,189),'marble'),'vein':((170,160,151),'stone'),'flute':((157,148,139),'flute'),'relief':((122,114,111),'relief'),'script':((118,108,101),'script'),'mosaic':((202,191,168),'mosaic'),'gold':((196,151,72),'gold'),'wood':((75,40,33),'wood'),'velvet':((114,21,47),'velvet'),'wax':((248,229,177),'stone'),'flame':((255,191,75),'gold'),'glassred':((152,39,66),'window'),'glassblue':((36,85,164),'window'),'glassgreen':((43,133,116),'window'),'glassamber':((207,139,45),'window'),'glassviolet':((110,52,155),'window')}
for n,(c,style) in palette.items():tex(n,c,style)
items={}
def add(n,it,en,k,boxes=None,material=None,creative=True):items['lacrimosa_'+n]=(it,en,k,boxes,material,creative)
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
for n,it,en,mat in [('ash_bricks','Mattoni di pietra cinerea','Ashlar masonry','ash'),('pale_bricks','Pietra antica chiara','Pale ashlar','ashlight'),('roof','Ardesia lavorata','Worked slate','slate'),('marble','Marmo venato','Veined marble','marble'),('mosaic','Tassello cosmatesco','Cosmatesque mosaic','mosaic'),('inscription','Pietra con iscrizione','Carved inscription stone','script'),('relief','Pietra con rosone inciso','Carved rose stone','relief')]:add(n,it,en,-1,material=mat)
for n,it,mat in [('red','rubino','glassred'),('blue','zaffiro','glassblue'),('green','smeraldo','glassgreen'),('amber','ambra','glassamber'),('violet','ametista','glassviolet')]:add('glass_'+n,'Vetrata '+it,'Cathedral glass '+n,-2,material=mat)
add('column','Colonna scanalata','Fluted column',0,[B(2,0,2,14,16,14,'flute')]+[B(x,0,z,x+2,16,z+2,'vein') for x in (1,13) for z in (1,13)])
add('capital','Capitello scolpito','Carved capital',0,[B(3,0,3,13,4,13,'flute'),B(2,4,2,14,8,14,'vein'),B(1,8,1,15,12,15,'relief'),B(0,12,0,16,16,16,'marble')])
add('cornice','Cornice gotica a rilievo','Gothic cornice',0,[B(0,0,4,16,3,16,'vein'),B(0,3,2,16,6,16,'relief'),B(0,6,0,16,9,16,'marble'),B(0,9,2,16,12,16,'vein'),B(0,12,4,16,16,16,'ashlight')])
add('panel','Bassorilievo floreale','Floral bas-relief',0,[B(0,0,12,16,16,16,'vein'),B(1,1,10,15,15,12,'relief'),B(0,0,9,16,1,13,'gold'),B(0,15,9,16,16,13,'gold'),B(0,1,9,1,15,13,'gold'),B(15,1,9,16,15,13,'gold')])
add('pew','Panca intagliata','Carved pew',0,[B(0,0,2,3,7,14,'wood'),B(13,0,2,16,7,14,'wood'),B(0,6,1,16,8,15,'wood'),B(0,8,12,16,15,15,'wood'),B(1,9,11,15,13,12,'relief'),B(0,15,11,16,16,15,'gold'),B(1,3,0,15,4,3,'wood')])
add('altar','Altare scolpito','Carved altar',0,[B(0,0,1,16,2,15,'marble'),B(1,2,2,15,12,14,'vein'),B(1,3,1,15,11,2,'relief'),B(0,12,0,16,16,16,'marble'),B(5,5,0,11,10,1,'gold')])
add('reliquary','Reliquiario dorato','Golden reliquary',0,[B(2,0,3,14,2,13,'gold'),B(3,2,4,13,9,12,'velvet'),B(2,8,3,14,10,13,'gold'),B(4,10,4,12,12,12,'gold'),B(6,12,6,10,14,10,'gold'),B(7,14,7,9,16,9,'gold')])
add('cross','Croce processionale','Processional cross',0,[B(3,0,5,13,2,11,'marble'),B(7,2,7,9,16,9,'gold'),B(2,10,7,14,12,9,'gold'),B(6,9,6,10,13,7,'relief')])
candles=[B(3,0,3,13,2,13,'gold'),B(7,2,7,9,6,9,'gold'),B(2,6,6,14,8,10,'gold')]
for x,z in [(3,7),(7,3),(7,11),(11,7),(7,7)]:
 candles += [B(x,8,z,x+2,13,z+2,'wax'),B(x+.5,13,z+.5,x+1.5,15,z+1.5,'flame')]
add('candles','Candelabro a cinque candele','Five-candle stand',3,candles)
chandelier=[B(7,5,7,9,16,9,'gold'),B(1,4,6,15,6,10,'gold'),B(6,4,1,10,6,15,'gold'),B(3,2,3,13,4,13,'gold')]
for x,z in [(2,2),(2,12),(12,2),(12,12),(7,7)]:chandelier += [B(x,6,z,x+2,10,z+2,'wax'),B(x+.5,10,z+.5,x+1.5,12,z+1.5,'flame')]
add('chandelier','Lampadario liturgico','Liturgical chandelier',3,chandelier)
# Monumental angel: continuous geometry in 16-unit blocks. Clip the sculpted
# figure into individual tiles so Minecraft can cull and load the statue normally.
statue=[]
def S(x,y,z,X,Y,Z,m='marble'):statue.append(B(x,y,z,X,Y,Z,m))
# Pedestal, layered robe and folds, shoulders, arms, hands, head and halo.
S(-22,0,-13,22,5,13,'vein');S(-19,5,-11,19,9,11);S(-15,9,-10,15,13,10,'relief')
for y,w in [(13,14),(25,12),(37,10),(49,9),(59,11)]:
 S(-w,y,-7,w,y+12,8)
 for x in range(-w+2,w,5):S(x,y,-9,x+2,y+12,-6,'vein')
S(-13,64,-8,13,80,8);S(-9,80,-6,9,86,7,'vein')
S(-9,86,-8,9,102,8);S(-7,102,-6,7,106,7);S(-10,96,5,10,106,10,'vein')
S(-10,84,6,-7,102,11,'vein');S(7,84,6,10,102,11,'vein')
# Nose, brows and carved hair over the face.
S(-2,91,-10,2,96,-7,'vein');S(-7,97,-9,-2,98,-7,'vein');S(2,97,-9,7,98,-7,'vein')
S(-3,88,-9,3,89,-8,'vein')
for side in (-1,1):
 def ss(a,y,z,b,Y,Z,m='marble'):S(min(side*a,side*b),y,z,max(side*a,side*b),Y,Z,m)
 ss(11,64,-6,20,79,7);ss(18,58,-10,25,71,4);ss(17,53,-15,24,62,-5);ss(12,53,-18,21,60,-11)
 for k in range(4):ss(12+k*2,55,-19,13+k*2,59,-16,'vein')
 # Raised wings: stepped sculpted feather silhouettes, with individual ribs.
 for j in range(8):
  x=12+j*4;y=69+j*4
  ss(x,y,6,x+9,y+24,13)
  ss(x+1,y-7,8,x+7,y+18,15,'vein')
  ss(x+3,y-12,9,x+6,y+10,16)
 for j in range(7):
  x=16+j*4;y=61+j*4
  ss(x,y,10,x+4,y+18,15)
# Halo with segmented golden ring set just behind the carved head.
for j in range(36):
 t=j*math.tau/36;x=15*math.cos(t);y=100+15*math.sin(t)
 S(x-2,y-2,9,x+2,y+2,12,'gold')
# Each tile is located relative to a central block. Negative x/z handled by floor.
tiles={}
for x,y,z,X,Y,Z,m in statue:
 for ix in range(math.floor((x+8)/16),math.ceil((X+8)/16)):
  for iy in range(math.floor(y/16),math.ceil(Y/16)):
   for iz in range(math.floor((z+8)/16),math.ceil((Z+8)/16)):
    ox=ix*16-8;oy=iy*16;oz=iz*16-8
    a,b,c=max(x,ox)-ox,max(y,oy)-oy,max(z,oz)-oz
    A,Bb,C=min(X,ox+16)-ox,min(Y,oy+16)-oy,min(Z,oz+16)-oz
    if A>a and Bb>b and C>c:tiles.setdefault((ix,iy,iz),[]).append((a,b,c,A,Bb,C,m))
def coord(n):return ('m'+str(-n)) if n<0 else str(n)
for (x,y,z),boxes in sorted(tiles.items()):
 n='angel_'+coord(x)+'_'+coord(y)+'_'+coord(z)
 add(n,'Frammento di statua angelica','Angel statue segment',0,boxes,creative=False)
# Register distinct blocks and item models, but do not clutter creative inventory with sculpture pieces.
decl=[]
for n,(it,en,k,boxes,material,creative) in items.items():
 expr='new Block(BlockBehaviour.Properties.of().strength(2.5f,6f))' if k==-1 else 'new GlassBlock(BlockBehaviour.Properties.copy(Blocks.GLASS).noOcclusion())' if k==-2 else f'new FurnitureBlock({k})'
 decl.extend([f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));'])
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s
s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n,q in items.items() if q[5])+'}'+a,1);p.write_text(s,encoding='utf-8')
for n,(it,en,k,boxes,material,creative) in items.items():
 if k<0:
  model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/lacrimosa_'+material}}
  if k==-2:model['render_type']='minecraft:translucent'
  variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tx={m:'noctismagic:block/lacrimosa_'+m for m in palette};tx['particle']=tx['marble' if n.startswith('lacrimosa_angel') else 'ash']
  el=[]
  for x,y,z,X,Y,Z,m in boxes:
   # Every clipped volume has valid block-local coordinates; texture UVs stay in range.
   el.append({'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}})
  model={'textures':tx,'elements':el,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]}}}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n});dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,*_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8')
a=s.index('    static Plan cathedral(){');b=s.index('        return p;',a)
helper='''    static void lacrimosaAngel(Plan p,int x,int y,int z){
'''+''.join(f'        p.put(x+({x}),y+{y},z+({z}),Furniture.LACRIMOSA_ANGEL_{coord(x).upper()}_{coord(y).upper()}_{coord(z).upper()}.get());\n' for x,y,z in sorted(tiles))+'''    }
    static void lacrimosaDetails(Plan p){
        Block ash=Furniture.LACRIMOSA_ASH_BRICKS.get(),pale=Furniture.LACRIMOSA_PALE_BRICKS.get(),roof=Furniture.LACRIMOSA_ROOF.get();
        Block marble=Furniture.LACRIMOSA_MARBLE.get(),mosaic=Furniture.LACRIMOSA_MOSAIC.get(),relief=Furniture.LACRIMOSA_RELIEF.get(),script=Furniture.LACRIMOSA_INSCRIPTION.get();
        Block[] glass={Furniture.LACRIMOSA_GLASS_RED.get(),Furniture.LACRIMOSA_GLASS_BLUE.get(),Furniture.LACRIMOSA_GLASS_GREEN.get(),Furniture.LACRIMOSA_GLASS_AMBER.get(),Furniture.LACRIMOSA_GLASS_VIOLET.get()};
        Block[] oldRoyal=royalGlass();
        for(var e:p.blocks.entrySet()){
            BlockState st=e.getValue();
            if(st.is(STONE))e.setValue(ash.defaultBlockState());
            else if(st.is(ROOF))e.setValue(roof.defaultBlockState());
            else if(st.is(EDGE))e.setValue(relief.defaultBlockState());
            else if(st.is(TRIM))e.setValue(pale.defaultBlockState());
            else for(int i=0;i<glass.length;i++)if(st.is(GLASS[i])||st.is(oldRoyal[i])){e.setValue(glass[i].defaultBlockState());break;}
        }
        // Inlaid ceremonial pavement and contrasting stone along the side aisles.
        for(int z=11;z<=78;z++)for(int x=6;x<=54;x++){
            if(x>=27&&x<=33)p.put(x,0,z,x==27||x==33?marble:mosaic);
            else if((x+z)%7==0)p.put(x,0,z,mosaic);
        }
        for(int z=17;z<=73;z+=8){
            for(int x:new int[]{11,49}){
                p.box(x-1,1,z-1,x+1,1,z+1,marble);
                for(int y=2;y<16;y++)p.put(x,y,z,y%5==0?Furniture.LACRIMOSA_CAPITAL.get():Furniture.LACRIMOSA_COLUMN.get());
                p.box(x-1,16,z-1,x+1,16,z+1,relief);
                // Remove the original crude statues, put the sculptural angel on a plinth.
                p.box(x-2,1,z+1,x+2,8,z+5,Blocks.AIR);
                if(z%16==1)lacrimosaAngel(p,x,1,z+3);
                else {p.put(x,1,z+3,Furniture.LACRIMOSA_CANDLES.get());p.put(x,2,z+3,Furniture.LACRIMOSA_CROSS.get());}
            }
            // Exterior buttresses with layered capitals, carved panels and projecting pinnacles.
            for(int x:new int[]{3,57}){
                p.box(x,1,z-1,x,3,z+1,marble);
                for(int y=4;y<=12;y++)p.put(x,y,z,y%4==0?Furniture.LACRIMOSA_CAPITAL.get():Furniture.LACRIMOSA_COLUMN.get());
                p.put(x,13,z,relief);
                p.put(x,14,z,script);
                for(int y=5;y<=14;y+=4)royalFacing(p,x==3?2:58,y,z,Furniture.LACRIMOSA_PANEL.get(),x==3?Direction.WEST:Direction.EAST);
            }
            for(int x:new int[]{21,39}){
                p.box(x,22,z,x,31,z,Blocks.CHAIN);
                p.put(x,21,z,Furniture.LACRIMOSA_CHANDELIER.get());
                p.put(x-1,21,z,Furniture.LACRIMOSA_CHANDELIER.get());
                p.put(x+1,21,z,Furniture.LACRIMOSA_CHANDELIER.get());
            }
        }
        // Replace benches in the nave with dedicated carved models.
        p.box(17,1,19,25,3,63,Blocks.AIR);p.box(35,1,19,43,3,63,Blocks.AIR);
        for(int z=20;z<=62;z+=4)for(int x=18;x<=42;x++){
            if(x>24&&x<36)continue;
            p.put(x,1,z,Furniture.LACRIMOSA_PEW.get());
        }
        // Sculpted sanctuary and large altar, with a clear central approach.
        p.box(24,1,67,36,9,76,Blocks.AIR);
        p.box(24,1,68,36,1,77,marble);
        p.box(26,2,70,34,2,77,mosaic);
        p.box(27,3,71,33,3,76,marble);
        for(int x=27;x<=33;x++)p.put(x,4,73,Furniture.LACRIMOSA_ALTAR.get());
        p.put(30,5,73,Furniture.LACRIMOSA_RELIQUARY.get());
        for(int x:new int[]{27,33})p.put(x,5,73,Furniture.LACRIMOSA_CANDLES.get());
        p.put(30,4,76,Furniture.LACRIMOSA_CROSS.get());
        // Two large flanking sculptures and two entrance angels.
        for(int x:new int[]{21,39}){
            p.box(x-3,2,81,x+3,10,85,Blocks.AIR);lacrimosaAngel(p,x,2,83);
        }
        for(int x:new int[]{12,48})lacrimosaAngel(p,x,1,5);
        // Deep carved portal bands, never obstruct the entrances.
        for(int x:new int[]{23,37})for(int y=2;y<=17;y++){
            p.put(x,y,7,y%4==0?relief:marble);
            if(y%4==1)p.put(x,y,6,Furniture.LACRIMOSA_PANEL.get());
        }
        for(int x=22;x<=38;x++)p.put(x,17,7,Furniture.LACRIMOSA_CORNICE.get());
        for(int x:new int[]{22,38})for(int y=2;y<=14;y+=3)p.put(x,y,8,script);
        // Framed rose windows, illuminated side shrines and detailed tower belts.
        for(int x:new int[]{9,51})for(int y=12;y<=42;y+=10){
            p.ring(x-7,y,3,x+7,17,pale);
            for(int dx:new int[]{-6,6})for(int dz:new int[]{-6,6})p.put(x+dx,y+1,10+dz,relief);
        }
        for(int z=23;z<=65;z+=14)for(int x:new int[]{7,53}){
            p.put(x,1,z,marble);p.put(x,2,z,Furniture.LACRIMOSA_RELIQUARY.get());
            p.put(x,2,z-2,Furniture.LACRIMOSA_CANDLES.get());
            p.put(x,2,z+2,Furniture.LACRIMOSA_CANDLES.get());
            royalFacing(p,x==7?6:54,5,z,Furniture.LACRIMOSA_PANEL.get(),x==7?Direction.EAST:Direction.WEST);
        }
    }
'''
s=s[:a]+helper+s[a:b]+'        lacrimosaDetails(p);\n'+s[b:];p.write_text(s,encoding='utf-8')
print(f'Santa Lacrimosa: {len(items)} registered block models including {len(tiles)} sculptural segments; original mosaics, inscriptions, glass, stone and furniture.')
