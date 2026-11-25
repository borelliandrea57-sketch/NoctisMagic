"""1.6.8: Jade Cat sushi restaurant overhaul."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
 p.parent.mkdir(parents=True,exist_ok=True)
 def ch(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
palette={'lacquer':(98,34,22),'walnut':(73,41,26),'gold':(198,143,55),'cream':(226,207,165),'indigo':(38,43,74),'porcelain':(234,226,209),'jade':(44,104,74),'salmon':(229,115,70),'tuna':(167,44,57),'nori':(26,51,38),'paper':(252,210,132),'sakura':(133,40,56),'black':(28,23,27)}
for m,col in palette.items():
 N=64;pix=bytearray()
 for y in range(N):
  for x in range(N):
   v=.89+.05*math.sin(x*1.7+y*.08)+.025*math.cos(y*2.7+x*.4)
   if m in ('lacquer','walnut'):
    v=.78+.15*math.sin(y*.8+math.sin(x*.13))**2+.32*math.exp(-((y-12)/3.2)**2)+.11*math.exp(-((y-21)/8)**2)
    if y%16==0:v*=.58
   elif m=='gold':v=.77+.44*math.exp(-((x-20)/12)**2)
   elif m in ('cream','indigo'):v=.86+.09*((x+y)%2)+.04*math.sin(x*2)
   elif m=='paper':v=.91+.13*math.exp(-((x-32)/22)**2)
   c=tuple(max(0,min(255,int(a*v))) for a in col)
   if m=='sakura':
    if abs(y-(48-x*.53+3*math.sin(x*.14)))<1.6:c=(99,61,39)
    for cx,cy in [(12,42),(22,27),(37,32),(49,15),(55,23),(8,19)]:
     dx=x-cx;dy=y-cy;rad=math.hypot(dx,dy);ang=math.atan2(dy,dx)
     if rad<4.5+1.5*math.cos(5*ang):c=(244,167,184) if rad>1.6 else (255,224,179)
   if min(x,y,N-1-x,N-1-y)==0:c=tuple(int(a*.65) for a in c)
   pix.extend((*c,255))
 png(assets/'textures/block'/('jade_'+m+'.png'),N,N,pix)
def legs(h):return [(x,0,z,x+2,h,z+2,'walnut') for x in (1,13) for z in (1,13)]
chair=legs(7)+[(1,7,1,15,9,15,'lacquer'),(2,9,2,14,10,13,'cream'),(1,9,13,3,16,15,'walnut'),(13,9,13,15,16,15,'walnut'),(3,11,13,13,15,15,'sakura'),(1,15,13,15,16,15,'gold'),(1,2,13,15,3,15,'walnut')]
table=legs(12)+[(0,12,0,16,14,16,'walnut'),(0,14,0,16,16,16,'lacquer'),(0,13,0,16,14,1,'gold'),(0,13,15,16,14,16,'gold'),(0,13,1,1,14,15,'gold'),(15,13,1,16,14,15,'gold'),(1,15.98,6,15,16,10,'sakura')]
counter=[(0,0,1,16,14,15,'walnut'),(0,14,0,16,16,16,'lacquer'),(1,2,0,15,12,1,'sakura'),(0,1,0,16,2,1,'gold'),(0,12,0,16,13,1,'gold'),(0,2,0,1,12,1,'gold'),(15,2,0,16,12,1,'gold')]
shelf=[(1,0,13,15,16,15,'walnut'),(0,0,3,2,16,15,'walnut'),(14,0,3,16,16,15,'walnut')]+[(0,y,3,16,y+1,15,'lacquer') for y in (0,5,10,15)]+[(0,y,3,16,y+1,4,'gold') for y in (0,5,10,15)]
for y in (1,6,11):
 for x in (3,7,11):
  shelf.extend([(x,y,8,x+3,y+2,12,'jade' if (x+y)%2 else 'porcelain'),(x+1,y+2,9,x+2,y+4,11,'gold')])
tray=[(1,0,2,15,1,14,'lacquer'),(2,1,3,14,2,13,'black'),(3,2,4,8,3,8,'porcelain'),(4,3,5,7,4,7,'salmon'),(9,2,4,12,3,7,'porcelain'),(9,3,4,12,4,7,'tuna'),(4,2,9,7,4,12,'nori'),(5,4,10,6,5,11,'salmon'),(10,2,9,13,4,12,'jade'),(10,4,9,13,5,12,'cream'),(1,1,1,14,2,2,'gold')]
display=[(0,0,1,16,1,15,'lacquer'),(0,1,1,1,9,15,'gold'),(15,1,1,16,9,15,'gold'),(0,8,1,16,9,2,'gold'),(0,8,14,16,9,15,'gold'),(0,1,1,16,8,2,'glass'),(1,8,2,15,9,14,'glass')]
for x in (2,6,10):display.extend([(x,1,4,x+3,2,8,'porcelain'),(x,2,4,x+3,3,8,'salmon' if x!=6 else 'tuna'),(x,1,10,x+3,3,13,'nori'),(x+1,3,11,x+2,4,12,'cream')])
lamp=[(3,0,3,13,2,13,'lacquer'),(4,2,4,12,13,12,'paper'),(3,13,3,13,15,13,'lacquer'),(6,15,6,10,16,10,'gold')]+[(x,2,z,x+1,13,z+1,'walnut') for x in (3,12) for z in (3,12)]
for y in (5,9):lamp.extend([(3,y,3,13,y+1,4,'walnut'),(3,y,12,13,y+1,13,'walnut'),(3,y,4,4,y+1,12,'walnut'),(12,y,4,13,y+1,12,'walnut')])
panel=[(0,0,13,16,16,16,'walnut'),(1,1,12,15,15,13,'sakura'),(0,0,11,16,1,13,'gold'),(0,15,11,16,16,13,'gold'),(0,1,11,1,15,13,'gold'),(15,1,11,16,15,13,'gold')]
items={
 'jade_chair':('Sedia laccata Sakura','Sakura lacquer chair',0,chair),
 'jade_table':('Tavolo laccato Sakura','Sakura lacquer table',0,table),
 'jade_counter':('Bancone del Gatto di Giada','Jade Cat counter',0,counter),
 'jade_shelf':('Scaffale di ceramiche e sake','Sake and porcelain shelf',0,shelf),
 'jade_sushi_tray':('Vassoio di sushi','Sushi tray',0,tray),
 'jade_sushi_display':('Vetrina nigiri','Nigiri display case',0,display),
 'jade_lantern':('Lanterna di carta dorata','Golden paper lantern',3,lamp),
 'jade_sakura_panel':('Pannello dipinto Sakura','Sakura painted panel',0,panel),
 'jade_lacquer_floor':('Parquet laccato','Lacquered parquet',-1,[(0,0,0,16,16,16,'lacquer')]),
 'jade_sakura_door':('Porta dipinta Sakura','Sakura painted door',-2,[])
}
decl=[]
for n,(it,en,k,boxes) in items.items():
 expr='new Block(BlockBehaviour.Properties.of().strength(2f))' if k==-1 else 'new SakuraDoor()' if k==-2 else f'new FurnitureBlock({k})'
 decl.extend([f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));'])
f=java/'Furniture.java';s=f.read_text(encoding='utf-8');a='public class Furniture{';assert a in s
s=s.replace(a,a+'\n'+'\n'.join(decl)+'''
    public static class SakuraDoor extends DoorBlock{
        SakuraDoor(){super(BlockBehaviour.Properties.copy(Blocks.CHERRY_DOOR),BlockSetType.CHERRY);}
    }
''',1);f.write_text(s,encoding='utf-8')
f=java/'Noctis.java';s=f.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s
s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a,1);f.write_text(s,encoding='utf-8')
for n,(it,en,k,boxes) in items.items():
 if k==-2:
  for half in ('bottom','top'):
   for hinge in ('left','right'):
    for opened in (False,True):
     suffix=half+'_'+hinge+('_open' if opened else '')
     dump(assets/'models/block'/f'{n}_{suffix}.json',{'parent':'minecraft:block/door_'+suffix,'textures':{'bottom':'noctismagic:block/jade_sakura','top':'noctismagic:block/jade_sakura'}})
  variants={}
  for d,ang in [('east',0),('south',90),('west',180),('north',270)]:
   for half,modelhalf in [('lower','bottom'),('upper','top')]:
    for hinge in ('left','right'):
     for opened in (False,True):
      suffix=modelhalf+'_'+hinge+('_open' if opened else '')
      rotation=(ang+(90 if hinge=='left' else -90) if opened else ang)%360
      variants[f'facing={d},half={half},hinge={hinge},open={str(opened).lower()}']={'model':'noctismagic:block/'+n+'_'+suffix,'y':rotation}
  dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
  dump(assets/'models/item'/f'{n}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:block/jade_sakura'}})
 else:
  tex={m:'noctismagic:block/jade_'+m for m in palette};tex['particle']=tex['walnut'];tex['glass']='minecraft:block/glass'
  elements=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{face:{'texture':'#'+m,'uv':[0,0,16,16]} for face in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]
  model={'textures':tex,'elements':elements,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]},'ground':{'translation':[0,3,0],'scale':[.25,.25,.25]}}}
  if n=='jade_sushi_display':model['render_type']='minecraft:cutout'
  dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
  variants={'':{'model':'noctismagic:block/'+n}} if k==-1 else {f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
  dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 pool={'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}
 if k==-2:pool['conditions'].append({'condition':'minecraft:block_state_property','block':'noctismagic:'+n,'properties':{'half':'lower'}})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[pool]})
for loc in ('it_it','en_us'):
 f=assets/'lang'/f'{loc}.json';d=json.loads(f.read_text(encoding='utf-8'))
 for n,(it,en,k,boxes) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(f,d)
f=java/'GothicEgg.java';s=f.read_text(encoding='utf-8')
a=s.index('    static Plan sushiRestaurant(){');b=s.index('        // Rear sakura garden',a)
s=s[:a]+'''    static void jadeFacing(Plan p,int x,int y,int z,Block b,Direction d){
        p.put(x,y,z,b.defaultBlockState().setValue(HorizontalDirectionalBlock.FACING,d));
    }
    static void jadeDoor(Plan p,int x,int z,net.minecraft.world.level.block.state.properties.DoorHingeSide hinge){
        BlockState door=Furniture.JADE_SAKURA_DOOR.get().defaultBlockState().setValue(DoorBlock.FACING,Direction.NORTH).setValue(DoorBlock.HINGE,hinge);
        p.put(x,1,z,door.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER));
        p.put(x,2,z,door.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER));
    }
    static Plan sushiRestaurant(){
        Plan p=new Plan(29,35,14,"Ristorante Sushi del Gatto di Giada");
        Block lacquer=Furniture.JADE_LACQUER_FLOOR.get();
        for(int x=0;x<29;x++)for(int z=0;z<25;z++){
            boolean tatami=(x>=3&&x<=10||x>=18&&x<=25)&&(z>=7&&z<=14);
            p.put(x,0,z,x==0||x==28||z<=3||z==24?Blocks.POLISHED_ANDESITE:tatami&&(x+z)%5!=0?Blocks.STRIPPED_BAMBOO_BLOCK:lacquer);
        }
        p.walls(1,1,4,27,7,23,Blocks.SMOOTH_QUARTZ);
        for(int y:new int[]{1,5,7})p.ring(1,y,4,27,23,y==5?Blocks.STRIPPED_DARK_OAK_WOOD:Blocks.DARK_OAK_PLANKS);
        for(int x:new int[]{1,7,11,17,21,27})for(int z:new int[]{4,23})p.box(x,1,z,x,7,z,Blocks.DARK_OAK_LOG);
        for(int z:new int[]{4,9,14,19,23})for(int x:new int[]{1,27})p.box(x,1,z,x,7,z,Blocks.DARK_OAK_LOG);
        for(int x=3;x<=25;x++)if(x<=10||x>=18){
            p.box(x,2,4,x,4,4,x%3==0?Blocks.DARK_OAK_FENCE:Blocks.WHITE_STAINED_GLASS);
            p.put(x,6,4,x%2==0?Blocks.GLOWSTONE:Blocks.DARK_OAK_TRAPDOOR);
        }
        for(int z=6;z<=21;z++)if(z%5!=4)for(int x:new int[]{1,27})p.box(x,2,z,x,4,z,z%3==0?Blocks.DARK_OAK_FENCE:Blocks.WHITE_STAINED_GLASS);
        p.box(12,1,4,16,4,4,Blocks.AIR);
        p.box(12,1,4,12,4,4,Blocks.DARK_OAK_LOG);p.box(15,1,4,16,4,4,Blocks.DARK_OAK_LOG);
        jadeDoor(p,13,4,net.minecraft.world.level.block.state.properties.DoorHingeSide.LEFT);
        jadeDoor(p,14,4,net.minecraft.world.level.block.state.properties.DoorHingeSide.RIGHT);
        p.box(13,3,4,14,4,4,Blocks.PINK_STAINED_GLASS);
        for(int x=11;x<=17;x++)p.put(x,5,3,Blocks.RED_WOOL);
        for(int x:new int[]{9,19})p.box(x,1,1,x,5,1,Blocks.RED_TERRACOTTA);
        p.box(8,5,1,20,5,1,Blocks.RED_TERRACOTTA);p.box(7,6,1,21,6,1,Blocks.DEEPSLATE_TILES);
        p.box(1,8,4,27,8,23,Blocks.DARK_OAK_PLANKS);
        for(int x=3;x<=25;x+=4)p.box(x,7,5,x,7,22,Blocks.DARK_OAK_LOG);
        for(int z=6;z<=22;z+=4)p.box(2,7,z,26,7,z,Blocks.DARK_OAK_LOG);
        for(int y=0;y<5;y++){p.ring(y,8+y,3+y,28-y,24-y,Blocks.DEEPSLATE_TILE_SLAB);p.box(y+1,8+y,4+y,27-y,8+y,23-y,Blocks.DEEPSLATE_TILES);}
        p.box(5,13,8,23,13,19,Blocks.DEEPSLATE_TILE_SLAB);
        for(int x:new int[]{5,9,19,23})for(int z:new int[]{8,13}){
            p.put(x,1,z,Furniture.JADE_TABLE.get());p.put(x+1,1,z,Furniture.JADE_TABLE.get());
            jadeFacing(p,x,1,z-1,Furniture.JADE_CHAIR.get(),Direction.SOUTH);
            jadeFacing(p,x+1,1,z+1,Furniture.JADE_CHAIR.get(),Direction.NORTH);
            p.put(x,2,z,Furniture.JADE_SUSHI_TRAY.get());p.put(x+1,2,z,Blocks.POTTED_CHERRY_SAPLING);
        }
        for(int x:new int[]{4,8,20,24})for(int z:new int[]{7,12,18}){
            p.put(x,6,z,Blocks.CHAIN);p.put(x,5,z,Furniture.JADE_LANTERN.get());
        }
        for(int x=3;x<=25;x++)if(x<=11||x>=17){
            p.put(x,1,16,Furniture.JADE_COUNTER.get());
            if(x%2==0)p.put(x,2,16,Furniture.JADE_SUSHI_DISPLAY.get());
            if(x%3==0)jadeFacing(p,x,1,15,Furniture.JADE_CHAIR.get(),Direction.SOUTH);
        }
        for(int x:new int[]{3,4,6,7,9,10,18,19,21,22,24,25})for(int y=1;y<=3;y++)p.put(x,y,22,Furniture.JADE_SHELF.get());
        for(int x:new int[]{5,11,17,23})p.put(x,4,22,Furniture.JADE_SAKURA_PANEL.get());
        for(int z:new int[]{7,11,17,21}){
            jadeFacing(p,2,1,z,Furniture.JADE_SHELF.get(),Direction.EAST);
            jadeFacing(p,26,1,z,Furniture.JADE_SHELF.get(),Direction.WEST);
        }
        for(int z:new int[]{6,10,15,20}){
            jadeFacing(p,1,3,z,Furniture.JADE_SAKURA_PANEL.get(),Direction.EAST);
            jadeFacing(p,27,3,z,Furniture.JADE_SAKURA_PANEL.get(),Direction.WEST);
        }
        for(int x:new int[]{3,25})for(int z:new int[]{6,19}){
            p.put(x,1,z,Furniture.JADE_TABLE.get());p.put(x,2,z,Furniture.JADE_LANTERN.get());
        }
        p.put(3,1,20,Furniture.FRIDGE.get());p.put(25,1,20,Furniture.DISHWASHER.get());
        p.put(12,1,21,Blocks.CRAFTING_TABLE);p.put(17,1,21,Blocks.CAULDRON);
        p.box(12,1,23,16,4,23,Blocks.AIR);
'''+s[b:]
s=s.replace('for(int x:new int[]{5,14,23})for(int z:new int[]{8,12})p.put(x,2,z,Blocks.POTTED_CHERRY_SAPLING);','',1)
s=s.replace('p.box(x-1,1,33,x+1,1,33,Blocks.CHERRY_SLAB);p.put(x,2,33,Blocks.FLOWER_POT);','p.box(x-1,1,33,x+1,1,33,Blocks.CHERRY_PLANKS);p.put(x,2,33,Blocks.POTTED_CHERRY_SAPLING);',1)
s=s.replace('pos(i==0?8:20,1,18)','pos(i==0?11:17,1,7)',1)
f.write_text(s,encoding='utf-8')
(java/'JadeWelcome.java').write_text('''package it.noctis.magic;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class JadeWelcome{
    private static final WeakHashMap<ServerPlayer,BlockPos> INSIDE=new WeakHashMap<>();
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%10!=0)return;
        ServerLevel l=p.serverLevel();
        for(SushiCats.Restaurant r:SushiCats.get(l).restaurants){
            BlockPos q=r.pos(14,0,4);
            double dx=p.getX()-q.getX()-.5,dz=p.getZ()-q.getZ()-.5;
            double depth=dx*r.front().getStepX()+dz*r.front().getStepZ();
            var right=r.front().getCounterClockWise();
            double side=dx*right.getStepX()+dz*right.getStepZ();
            if(depth<.5||depth>18.5||Math.abs(side)>12.5||p.getY()<q.getY()+.5||p.getY()>q.getY()+6)continue;
            if(r.marker().equals(INSIDE.get(p)))return;
            INSIDE.put(p,r.marker());
            for(SushiGuest guest:l.getEntitiesOfClass(SushiGuest.class,p.getBoundingBox().inflate(25),g->g.isAlive()&&g.home!=null)){
                if(guest.home.distSqr(r.pos(14,1,12))>180)continue;
                p.sendSystemMessage(Component.literal(guest.maomao()?"Maomao: Benvenuto al Gatto di Giada. Ho controllato personalmente gli ingredienti.":"Jinshi: Benvenuto! Accomodati pure, oggi il sushi e' eccellente.").withStyle(guest.maomao()?net.minecraft.ChatFormatting.GREEN:net.minecraft.ChatFormatting.LIGHT_PURPLE));
                l.broadcastEntityEvent(guest,(byte)112);
            }
            return;
        }
        INSIDE.remove(p);
    }
}
''',encoding='utf-8')
print('Jade Cat: ten new blocks, painted doors, lacquered furnishings, supported plants, welcoming staff and retained garden.')
