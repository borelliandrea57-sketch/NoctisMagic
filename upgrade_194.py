"""Valdracula hall and Geass reliability."""
from pathlib import Path
import sys,json,math,random,wave,struct,subprocess
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
def edit(f,a,b):
 p=java/f;s=p.read_text(encoding='utf-8');assert a in s,(f,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
# Geass remains active for its full duration when no safe route exists.
p=java/'GeassExile.java';s=p.read_text(encoding='utf-8')
s=s.replace('if(o.stuck>=4){release(p,false);return;}','if(o.stuck>=4){o.stuck=0;o.avoid=-1;o.dir=-1;}').replace('if(o.blocked>=60){release(p,false);return;}','if(o.blocked>=60){o.blocked=0;o.avoid=-1;}')
s=s.replace('if(o.dir!=best||!p.hasEffect(VampireLife.GEASS_EXILE.get()))','if(o.dir!=best||!p.hasEffect(VampireLife.GEASS_EXILE.get())||p.tickCount%40==0)')
p.write_text(s,encoding='utf-8')
p=java/'GeassMagic.java';s=p.read_text(encoding='utf-8')
s=s.replace('look.dot(d.normalize())>.965','look.dot(d.normalize())>.91').replace('l.getGameTime()+600','l.getGameTime()+1800').replace('if(m.tickCount%5!=0)return;','if(m.tickCount%3!=0)return;')
p.write_text(s,encoding='utf-8')
items={}
def add(n,it,en,boxes=None,tex=None,expr='new FurnitureBlock(0)',creative=True):items[n]=(it,en,boxes,tex,expr,creative)
# Hand-painted weathered masonry with individual scratches and aged mortar.
pal={'stone_aged':(104,99,94),'stone_ivy':(92,97,83),'stone_scar':(91,86,87),'stone_blood':(94,87,85),'stone_rune':(121,113,100),'stone_ash':(142,139,133),'stone_red':(112,68,68)}
for n,base in pal.items():
 rng=random.Random(n);im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
 for y in range(64):
  for x in range(64):
   u=(x+16*(y//16%2))%32;v=y%16;f=.85+rng.random()*.18
   if u==0 or v==0:f*=.46
   elif u==1 or v==1:f*=1.20
   im.putpixel((x,y),(*[max(0,min(255,round(q*f))) for q in base],255))
 for i in range(8):
  x,y=rng.randrange(3,57),rng.randrange(3,57)
  d.line([(x,y),(x+3,y+2),(x+6,y+1)],fill=(55,51,49),width=1)
 if n=='stone_ivy':
  for k in range(4):
   x=8+k*15
   pts=[(x+int(3*math.sin(y*.15+k)),y) for y in range(64)]
   d.line(pts,fill=(65,62,34),width=2)
   for y in range(4,63,6):
    xx=pts[y][0];side=(-1)**(y//6)
    d.polygon([(xx,y),(xx+side*6,y-3),(xx+side*5,y+4),(xx,y+3)],fill=(65+k*8,105+k*7,45),outline=(40,64,30))
 if n in ('stone_scar','stone_blood'):
  for k in range(3):
   x=12+k*8;d.line((x,12,x+15,48),fill=(39,35,36),width=2)
   d.line((x+2,12,x+17,48),fill=(145,134,126),width=1)
   if n=='stone_blood':
    d.line((x+1,17,x+13,46),fill=(107,15,28),width=2);d.line((x+13,46,x+13,56),fill=(80,18,23),width=1)
 if n=='stone_rune':
  d.polygon([(32,8),(52,32),(32,56),(12,32)],outline=(54,48,45),width=3)
  d.line([(32,16),(32,48)],fill=(62,51,45),width=3);d.line([(21,25),(43,25)],fill=(62,51,45),width=3)
 im.save(assets/'textures/block'/f'val_{n}.png')
 add('val_'+n,{'stone_aged':'Pietra gotica consumata','stone_ivy':'Pietra con edera','stone_scar':'Pietra graffiata','stone_blood':'Pietra con graffi insanguinati','stone_rune':'Pietra incisa','stone_ash':'Calcare grigio','stone_red':'Marmo rosso antico'}[n],n.replace('_',' ').title(),tex='val_'+n,expr='new Block(BlockBehaviour.Properties.of().strength(2.5f,6f))')
colors={'velvet':(111,16,39),'ebony':(47,31,39),'gold':(208,162,78),'pipe':(166,144,96),'ivory':(239,228,204),'black':(26,22,29),'ruby':(178,32,53),'leaf':(76,122,43)}
for n,c in colors.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   v=.85+.22*math.sin(math.pi*x/64)**2+rng.uniform(-.035,.035)
   im.putpixel((x,y),(*[max(0,min(255,round(q*v))) for q in c],255))
 im.save(assets/'textures/block'/f'val_{n}.png')
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,'val_'+m)
add('val_ivy_relief','Edera in rilievo','Raised ivy',[B(7,0,14,9,16,15,'leaf')]+[B(x,y,13,x+5,y+3,14.2,'leaf') for x,y in [(3,2),(8,5),(2,8),(9,11),(4,13)]])
add('val_throne_chair','Trono di Valdracula','Valdracula throne',[B(1,0,1,4,3,4,'gold'),B(12,0,1,15,3,4,'gold'),B(1,0,12,4,3,15,'gold'),B(12,0,12,15,3,15,'gold'),B(1,3,1,15,8,15,'ebony'),B(2,8,2,14,10,14,'velvet'),B(0,7,3,2,15,13,'ebony'),B(14,7,3,16,15,13,'ebony'),B(0,14,2,3,16,14,'gold'),B(13,14,2,16,16,14,'gold'),B(1,10,13,15,16,16,'velvet')])
add('val_throne_back','Schienale gotico','Gothic throne back',[B(0,0,10,16,16,16,'ebony'),B(1,1,8,15,15,10,'velvet'),B(0,0,8,2,16,10,'gold'),B(14,0,8,16,16,10,'gold')]+[B(x,2,7,x+.7,14,8,'gold') for x in (4,8,12)])
add('val_throne_crown','Corona del trono','Throne crown',[B(0,0,10,16,3,16,'ebony'),B(0,3,9,16,5,16,'gold'),B(2,5,10,5,9,15,'gold'),B(7,5,9,9,14,16,'gold'),B(11,5,10,14,9,15,'gold'),B(7,9,8,9,12,9,'ruby')])
add('val_candle_base','Piedistallo per candelabro','Candelabrum pedestal',[B(2,0,2,14,2,14,'ebony'),B(4,2,4,12,4,12,'gold'),B(6,4,6,10,13,10,'ebony'),B(4,13,4,12,15,12,'gold'),B(2,15,2,14,16,14,'ebony')])
add('val_organ_console','Organo automatico','Automatic organ',[B(0,0,4,16,8,16,'ebony'),B(0,8,3,16,10,16,'gold'),B(1,10,4,15,11,12,'ivory'),B(1,11,12,15,15,16,'ebony')]+[B(x,11,8,x+.65,11.6,12,'black') for x in (2,4,7,9,11,13)],expr='new OrganBlock()')
for k in range(3):
 boxes=[B(0,0,12,16,16,16,'ebony')]
 for j in range(5):
  x=.8+j*3.1;h=16 if k<2 else 7+((j*3)%9)
  boxes += [B(x,0,7,x+2.2,h,12,'pipe'),B(x+.35,0,6.7,x+1.85,h,7,'gold')]
  if k==0:boxes.append(B(x+.45,3,6.5,x+1.75,4.5,6.7,'black'))
 add('val_organ_pipes_'+str(k),'Canne dell’organo','Organ pipes',boxes)
# One original design spread over a 9 by 41 block runner; reuse 180-degree symmetric halves.
W,H=288,1312;im=Image.new('RGBA',(W,H),(102,17,38,255));d=ImageDraw.Draw(im);rng=random.Random(41)
for y in range(H//2):
 for x in range(W):
  v=rng.randrange(-4,5);d.point((x,y),fill=(102+v,17+v//2,38+v,255))
for off,col,th in [(4,(31,21,31),4),(12,(203,155,74),3),(19,(116,64,64),3),(24,(215,179,104),1)]:d.rectangle((off,off,W-1-off,H-1-off),outline=col,width=th)
for y in range(38,H//2,30):
 for x in (16,W-17):d.polygon([(x,y-8),(x+7,y),(x,y+8),(x-7,y)],fill=(202,151,67))
for cy in (230,510):
 cx=W//2;rx=87;ry=109;d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(57,25,37),outline=(209,166,85),width=3)
 for k in range(12):
  a=k*math.tau/12;x=cx+rx*.78*math.cos(a);y=cy+ry*.78*math.sin(a);d.ellipse((x-7,y-10,x+7,y+10),fill=(161,67,76),outline=(218,169,90),width=2)
 d.polygon([(cx,cy-22),(cx-12,cy-7),(cx-65,cy-28),(cx-47,cy+11),(cx-16,cy+4),(cx,cy+24),(cx+16,cy+4),(cx+47,cy+11),(cx+65,cy-28),(cx+12,cy-7)],fill=(28,22,32),outline=(215,172,91),width=3)
im.paste(im.crop((0,0,W,H//2)).rotate(180),(0,H//2))
for y in range(21):
 for x in range(9):
  n=f'val_runner_{x}_{y}';im.crop((x*32,y*32,(x+1)*32,(y+1)*32)).save(assets/'textures/block'/f'{n}.png');add(n,'Sezione tappeto','Carpet section',[(0,0,0,16,1,16,n)],expr='new CarpetTile()',creative=False)
decl=[]
for n,(it,en,boxes,tex,expr,creative) in items.items():
 decl.append(f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});')
 if creative:decl.append(f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));')
 if tex:
  model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/'+tex}};variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tx={m:'noctismagic:block/'+m for *_,m in boxes};tx['particle']=next(iter(tx.values()))
  model={'textures':tx,'elements':[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 if creative:
  dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
  dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
# Original minor-key pipe organ loop.
rate=16000;secs=24;buf=[0.]*(rate*secs)
for k,ch in enumerate([(45,52,57,60),(41,48,53,57),(43,50,55,59),(40,47,52,56),(45,52,57,64),(38,45,53,57),(40,47,56,59),(45,52,57,60)]):
 for j,n in enumerate(ch):
  freq=440*2**((n-69)/12)
  for i in range(rate*3):
   t=i/rate;a=math.tau*freq*t;env=min(1,t/.08,(3-t)/.18)
   buf[k*rate*3+i]+=(math.sin(a)+.33*math.sin(2*a)+.16*math.sin(3*a))*.07*env
wav=root/'val_organ.wav'
with wave.open(str(wav),'wb') as f:
 f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,x))*32700)) for x in buf))
ogg=assets/'sounds/val_organ.ogg';ogg.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(ogg)],check=True);wav.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['val_organ']={'sounds':[{'name':'noctismagic:val_organ','stream':True}]};dump(p,d)
(java/'ValOrgan.java').write_text('''package it.noctis.magic;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegisterEvent;
import net.minecraftforge.registries.ForgeRegistries;
@Mod.EventBusSubscriber(modid=Noctis.ID,bus=Mod.EventBusSubscriber.Bus.MOD)
public class ValOrgan{
 public static final ResourceLocation ID=new ResourceLocation(Noctis.ID,"val_organ");
 public static final SoundEvent SOUND=SoundEvent.createVariableRangeEvent(ID);
 @SubscribeEvent public static void register(RegisterEvent e){e.register(ForgeRegistries.Keys.SOUND_EVENTS,h->h.register(ID,SOUND));}
}''',encoding='utf-8')
edit('Furniture.java','public class Furniture{','public class Furniture{\n'+'\n'.join(decl)+'''
 public static class CarpetTile extends FurnitureBlock{
  CarpetTile(){super(0);}
  @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return box(0,0,0,16,1,16);}
 }
 public static class OrganBlock extends FurnitureBlock{
  OrganBlock(){super(0);}
  @Override public void onPlace(BlockState s,Level l,BlockPos p,BlockState old,boolean moving){
   super.onPlace(s,l,p,old,moving);if(!l.isClientSide&&!old.is(this))l.scheduleTick(p,this,20);
  }
  @Override public void tick(BlockState s,ServerLevel l,BlockPos p,net.minecraft.util.RandomSource r){
   if(!s.getValue(LIT)){
    boolean near=l.hasNearbyAlivePlayer(p.getX()+.5,p.getY()+.5,p.getZ()+.5,32);
    if(near)l.playSound(null,p,ValOrgan.SOUND,net.minecraft.sounds.SoundSource.RECORDS,1.6f,1f);
    l.scheduleTick(p,this,near?480:40);
   }
  }
  @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player player,InteractionHand h,BlockHitResult hit){
   if(!l.isClientSide){l.setBlock(p,s.cycle(LIT),3);if(s.getValue(LIT))l.scheduleTick(p,this,1);}
   return InteractionResult.sidedSuccess(l.isClientSide);
  }
 }
''')
arr=','.join('Furniture.VAL_RUNNER_'+str(x)+'_'+str(y)+'.get()' for y in range(21) for x in range(9))
(java/'ValRunner.java').write_text('''package it.noctis.magic;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
public class ValRunner extends Item{
 public ValRunner(Properties p){super(p);}
 static Block[] tiles(){return new Block[]{'''+arr+'''};}
 static BlockState tile(Block[] a,int x,int z,Direction f){
  boolean r=z>20;return a[r?(40-z)*9+8-x:z*9+x].defaultBlockState().setValue(Furniture.FurnitureBlock.FACING,r?f.getOpposite():f);
 }
 @Override public InteractionResult useOn(UseOnContext c){
  if(!(c.getLevel() instanceof ServerLevel l))return InteractionResult.SUCCESS;
  if(c.getPlayer()==null)return InteractionResult.FAIL;
  BlockPos o=c.getClickedPos().relative(c.getClickedFace());
  Direction f=c.getHorizontalDirection().getOpposite(),right=f.getClockWise(),forward=f.getOpposite();
  for(int z=0;z<41;z++)for(int x=0;x<9;x++){
   BlockPos p=o.relative(right,x).relative(forward,z);
   if(!l.hasChunkAt(p)||l.isOutsideBuildHeight(p)||!l.getWorldBorder().isWithinBounds(p)||!l.getBlockState(p).canBeReplaced()||!l.mayInteract(c.getPlayer(),p)||!l.getBlockState(p.below()).isFaceSturdy(l,p.below(),Direction.UP)){
    c.getPlayer().displayClientMessage(net.minecraft.network.chat.Component.literal("Serve un pavimento libero di 9 x 41 blocchi."),true);return InteractionResult.FAIL;
   }
  }
  Block[] a=tiles();
  for(int z=0;z<41;z++)for(int x=0;x<9;x++)l.setBlock(o.relative(right,x).relative(forward,z),tile(a,x,z,f),3);
  if(!c.getPlayer().getAbilities().instabuild)c.getItemInHand().shrink(1);
  return InteractionResult.CONSUME;
 }
}''',encoding='utf-8')
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','public static final RegistryObject<Item> VAL_RUNNER=ITEMS.register("val_runner",()->new ValRunner(new Item.Properties().stacksTo(1)));\n    public static final RegistryObject<Item> CATHEDRAL_EGG=')
edit('Noctis.java','if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)','if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){e.accept(VAL_RUNNER.get());'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n,q in items.items() if q[-1])+'}if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)')
dump(assets/'models/item/val_runner.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/val_runner'}})
im.resize((16,32)).save(assets/'textures/item/val_runner.png')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'));d['item.noctismagic.val_runner']='Tappeto imperiale (9×41)' if loc=='it_it' else 'Imperial carpet (9×41)'
 for n,(it,en,*_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static Plan castle(){');b=s.index('        return p;',a)
s=s[:b]+'''        valHall(p);
'''+s[b:]
a=s.index('    static Plan castle(){')
s=s[:a]+'''    static void valHall(Plan p){
        // Replace detached wall sconces with a backing pillar and put freestanding lamps on pedestals.
        for(int z=40;z<=80;z+=8)for(int x:new int[]{32,58}){
            int backing=x==32?31:59;
            for(int y=3;y<=6;y++)p.put(backing,y,z,Blocks.CHISELED_POLISHED_BLACKSTONE);
            royalFacing(p,x,5,z,Furniture.ROYAL_SCONCE.get(),x==32?Direction.EAST:Direction.WEST);
        }
        for(int z=44;z<=76;z+=8)for(int x:new int[]{39,51}){
            for(int dx:new int[]{-1,1})p.put(x+dx,14,z,Blocks.AIR);
            p.box(x,15,z,x,24,z,Blocks.CHAIN);p.put(x,14,z,Furniture.ROYAL_CHANDELIER.get());
            p.put(x,25,z,Blocks.POLISHED_BLACKSTONE_BRICKS);
        }
        for(int z=40;z<=80;z+=10)for(int x:new int[]{32,58})p.put(x,1,z,Furniture.VAL_CANDLE_BASE.get());
        // Continuous imperial carpet.
        Block[] runner=ValRunner.tiles();
        for(int z=0;z<41;z++)for(int x=0;x<9;x++)p.put(41+x,1,36+z,ValRunner.tile(runner,x,z,Direction.NORTH));
        // Replace the original three-piece seat with a single sit-able throne and monumental back.
        p.box(44,4,81,46,7,82,Blocks.AIR);
        royalFacing(p,45,4,81,Furniture.VAL_THRONE_CHAIR.get(),Direction.NORTH);
        for(int x=44;x<=46;x++)for(int y=4;y<=6;y++)royalFacing(p,x,y,82,Furniture.VAL_THRONE_BACK.get(),Direction.NORTH);
        for(int x=44;x<=46;x++)royalFacing(p,x,7,82,Furniture.VAL_THRONE_CROWN.get(),Direction.NORTH);
        // Two broad side stairs and clear headroom, connecting to existing upper walkways.
        for(int k=0;k<12;k++)for(int x:new int[]{34,35,55,56}){
            int y=1+k,z=37+k;
            p.box(x,y+1,z,x,y+3,z,Blocks.AIR);
            p.stair(x,y,z,Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS,Direction.SOUTH);
            if(y>1)p.put(x,y-1,z,Blocks.POLISHED_BLACKSTONE_BRICKS);
        }
        for(int x:new int[]{34,35,55,56}){p.put(x,12,49,Blocks.POLISHED_BLACKSTONE_BRICKS);p.box(x,13,49,x,15,50,Blocks.AIR);}
        // Pipe organ in the rear side bay, with a single musical console.
        p.box(19,1,69,26,9,73,Blocks.AIR);
        for(int x=20;x<=25;x++){
            p.put(x,1,72,Furniture.VAL_CANDLE_BASE.get());
            for(int y=2;y<=6;y++)royalFacing(p,x,y,72,Furniture.VAL_ORGAN_PIPES_1.get(),Direction.NORTH);
            royalFacing(p,x,7,72,Furniture.VAL_ORGAN_PIPES_2.get(),Direction.NORTH);
        }
        royalFacing(p,22,1,70,Furniture.VAL_ORGAN_CONSOLE.get(),Direction.NORTH);
        // Weathered masonry accents, with actual raised ivy on selected exterior walls.
        Block[] stone={Furniture.VAL_STONE_AGED.get(),Furniture.VAL_STONE_IVY.get(),Furniture.VAL_STONE_SCAR.get(),Furniture.VAL_STONE_BLOOD.get(),Furniture.VAL_STONE_RUNE.get(),Furniture.VAL_STONE_ASH.get(),Furniture.VAL_STONE_RED.get()};
        for(int z=39;z<=85;z++)for(int x:new int[]{18,72,31,59})for(int y=2;y<=27;y++){
            int h=Math.floorMod(x*13+y*23+z*41,29);
            BlockState old=p.blocks.get(p.key(x,y,z));
            if(h<7&&old!=null&&(old.is(Blocks.DEEPSLATE_BRICKS)||old.is(Blocks.STONE_BRICKS)||old.is(Blocks.POLISHED_BLACKSTONE_BRICKS)||old.is(Blocks.DEEPSLATE_TILES)))p.put(x,y,z,stone[h]);
        }
        for(int z=42;z<=80;z+=9)for(int x:new int[]{18,72})for(int y=2;y<=6;y++){
            int xx=x==18?17:73;
            if(!p.blocks.containsKey(p.key(xx,y,z)))royalFacing(p,xx,y,z,Furniture.VAL_IVY_RELIEF.get(),x==18?Direction.WEST:Direction.EAST);
        }
    }
'''+s[a:]
# The completion hook runs once per construction.
anchor='            msg(p.name+" completato!'
i=s.index(anchor);s=s[:i]+'''            if(p.w==91){
                Vampire.Friendly v=Noctis.FRIENDLY.get().create(l);
                if(v!=null){
                    BlockPos q=pos(45,2,58);
                    v.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+180,0);
                    v.setPersistenceRequired();
                    if(l.noCollision(v))l.addFreshEntity(v);
                }
            }
'''+s[i:];p.write_text(s,encoding='utf-8')
print('Valdracula hall and durable Geass installed.')
