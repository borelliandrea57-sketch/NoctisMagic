"""1.7.17: ornate patisserie, modern fast-food seating, polluted purple swamp."""
from pathlib import Path
import sys,math,json,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
pal={'cream':(235,218,192),'rose':(198,112,130),'mint':(112,163,146),'cocoa':(100,57,45),'gold':(200,156,82),'stone':(176,166,152),'dark':(49,45,47),'red':(172,35,39),'yellow':(244,188,36),'steel':(133,140,144),'oak':(120,83,53),'dung':(94,59,30),'purple':(107,28,151),'ivory':(247,235,218)}
for n,base in pal.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   v=.89+.10*rng.random()
   if n in ('cream','stone','ivory'):v+=.045*math.sin(x*.22+y*.17)
   if n in ('rose','mint','cocoa','red'):v*=.88+.16*math.sin(x*math.pi/16)**2
   if n in ('gold','steel'):v*=.78+.33*math.sin(x*math.pi/64)**2
   if n=='oak':v*=.8+.24*math.sin(x*.75+math.sin(y*.14))**2
   if n=='purple':v*=.85+.21*math.sin(x*.28+y*.17)*math.sin(y*.21-x*.11)
   im.putpixel((x,y),(*[max(0,min(255,int(c*v))) for c in base],225 if n=='purple' else 255))
 p=assets/'textures/block'/f'atelier_{n}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
# Carved floral relief and confectionery shop sign.
for n in ('relief','sign','fastsign'):
 im=Image.new('RGBA',(64,64),(221,202,178,255) if n=='relief' else (103,57,53,255) if n=='sign' else (53,49,47,255));d=ImageDraw.Draw(im)
 if n=='relief':
  d.rectangle((1,1,62,62),outline=(145,116,103),width=2);d.rectangle((4,4,59,59),outline=(250,233,211),width=2)
  for k in range(8):
   a=k*math.pi/4;x=32+14*math.cos(a);y=32+14*math.sin(a);d.ellipse((x-7,y-7,x+7,y+7),fill=(192,160,145),outline=(249,229,208),width=2)
  d.ellipse((25,25,39,39),fill=(190,136,115),outline=(249,229,208),width=2)
 elif n=='sign':
  d.rectangle((2,2,61,61),outline=(226,182,103),width=2);d.text((8,11),'DOLCI',fill=(250,226,181));d.text((8,28),'& TEA',fill=(250,226,181));d.arc((14,41,49,58),0,180,fill=(236,170,166),width=2)
 else:
  for cx in (23,41):
   d.arc((cx-9,10,cx+9,58),180,360,fill=(255,202,45),width=6)
   d.line((cx-9,34,cx-9,53),fill=(255,202,45),width=5);d.line((cx+9,34,cx+9,53),fill=(255,202,45),width=5)
 im.save(assets/'textures/block'/f'atelier_{n}.png')
# A large tiled, smoothly curved double arch instead of a block letter.
logo=Image.new('RGBA',(256,128),(49,45,47,255));d=ImageDraw.Draw(logo)
for cx in (81,175):
 d.arc((cx-48,10,cx+48,185),180,360,fill=(255,198,29),width=17)
 d.line((cx-48,97,cx-48,120),fill=(255,198,29),width=17)
 d.line((cx+48,97,cx+48,120),fill=(255,198,29),width=17)
for yy in range(2):
 for xx in range(4):logo.crop((xx*64,yy*64,(xx+1)*64,(yy+1)*64)).save(assets/'textures/block'/f'atelier_arch_{xx}_{yy}.png')
items={}
def add(n,it,en,boxes,k=0,expr=None):items[n]=(it,en,boxes,k,expr)
add('sweet_carved_pillar','Pilastro inciso','Carved pilaster',[B(0,0,8,16,2,16,'stone'),B(2,2,9,14,14,16,'cream'),B(3,3,8,5,13,9,'gold'),B(11,3,8,13,13,9,'gold'),B(5,3,8,11,13,9,'relief'),B(0,14,8,16,16,16,'stone')])
add('sweet_carved_panel','Pannello floreale inciso','Carved floral panel',[B(0,0,10,16,16,16,'cream'),B(1,1,8,15,15,10,'relief'),B(0,0,7,16,1,10,'gold'),B(0,15,7,16,16,10,'gold'),B(0,1,7,1,15,10,'gold'),B(15,1,7,16,15,10,'gold')])
add('sweet_cornice','Cornice in stucco','Stucco cornice',[B(0,0,9,16,3,16,'stone'),B(0,3,6,16,6,16,'cream'),B(0,6,3,16,9,16,'relief'),B(0,9,1,16,12,16,'cream'),B(0,12,4,16,14,16,'gold'),B(0,14,7,16,16,16,'cream')])
add('sweet_sign','Insegna della pasticceria','Patisserie sign',[B(0,1,10,16,15,15,'cocoa'),B(1,2,8,15,14,10,'sign'),B(0,0,8,16,1,15,'gold'),B(0,15,8,16,16,15,'gold')])
for n,c1,c2,it in [('rose','rose','ivory','rosa e avorio'),('mint','mint','cream','menta e crema'),('cocoa','cocoa','cream','cioccolato e crema')]:
 aw=[B(0,13,12,16,15,16,'gold')]
 # Individually stepped fabric stripes descend towards the street.
 for j in range(4):
  col=c1 if j%2==0 else c2
  for z in range(0,16,4):
   h=6+z*.42;aw.append(B(j*4,h,z,j*4+4,h+1.5,z+4,col))
  aw.append(B(j*4,3+(j%2)*.5,0,j*4+4,7,1.5,col))
 add('shop_awning_'+n,'Tendina da negozio '+it,'Shop awning '+n,aw)
 curtains=[B(0,14,11,16,15,14,'gold')]
 for x in (1,3,5,10,12,14):
  curtains.append(B(x,1 if x in (1,14) else 3,11+(x%2)*.5,x+1.8,14,13.5,c1))
 curtains += [B(0,8,10,6.8,9,11.5,'gold'),B(9.5,8,10,16,9,11.5,'gold')]
 add('window_curtain_'+n,'Tenda da vetro '+it,'Window curtain '+n,curtains)
add('fast_armchair_red','Poltroncina rossa','Red armchair',[])
add('fast_armchair_gray','Poltroncina antracite','Charcoal armchair',[])
for n,c in [('fast_armchair_red','red'),('fast_armchair_gray','dark')]:
 it,en,_,k,e=items[n]
 boxes=[B(x,0,z,x+2,3,z+2,'steel') for x in (2,12) for z in (2,12)]
 boxes += [B(1,3,1,15,7,15,'dark'),B(2,7,2,14,9,14,c),B(1,7,2,3.5,12,14,c),B(12.5,7,2,15,12,14,c),B(2,9,12,14,16,15,c),B(3,10,11,13,15,12,c)]
 items[n]=(it,en,boxes,k,e)
add('fast_facade_panel','Pannello moderno scanalato','Ribbed facade panel',[B(0,0,11,16,16,16,'dark')]+[B(x,0,9,x+1.2,16,11,'oak') for x in (1,5,9,13)])
add('fast_facade_trim','Cornice moderna rossa','Red facade trim',[B(0,0,9,16,16,16,'dark'),B(0,3,5,16,13,9,'red'),B(0,12,4,16,14,9,'steel')])
for yy in range(2):
 for xx in range(4):add(f'fast_arch_{xx}_{yy}','Tassello insegna archi dorati','Golden arch sign tile',[B(0,0,10,16,16,16,f'arch_{xx}_{yy}')])
add('swamp_dung','Mucchio di escrementi','Dung pile',[B(3,0,3,13,2,13,'dung'),B(4,2,4,12,4,12,'dung'),B(6,4,5,11,6,10,'dung'),B(7,6,6,10,8,9,'dung')],expr='new SwampDung()')
add('swamp_purple_water','Acqua paludosa viola','Purple swamp water',[],expr='new PurpleSwampWater()')
decl=[]
for n,(it,en,boxes,k,expr) in items.items():
 expr=expr or f'new FurnitureBlock({k})'
 decl += [f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));']
 tx={m:'noctismagic:block/atelier_'+m for m in list(pal)+['relief','sign','fastsign']+[f'arch_{x}_{y}' for x in range(4) for y in range(2)]};tx['particle']=tx['cream']
 if n=='swamp_purple_water':
  model={'render_type':'minecraft:translucent','textures':{'particle':tx['purple'],'purple':tx['purple']},'elements':[{'from':[0,15.6,0],'to':[16,15.8,16],'faces':{'up':{'texture':'#purple'},'down':{'texture':'#purple'}}}]}
  variants={'':{'model':'noctismagic:block/'+n}}
 else:
  model={'textures':tx,'elements':[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes],'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]}}}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
 dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s
s=s.replace(a,a+'\n'+'\n'.join(decl)+'''
    public static class SwampDung extends FurnitureBlock{
        SwampDung(){super(0);}
        @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return box(3,0,3,13,8,13);}
        @Override public void animateTick(BlockState s,Level l,BlockPos p,net.minecraft.util.RandomSource r){
            // Tiny dark insects orbit and drift around the dung.
            for(int i=0;i<4;i++){
                double a=r.nextDouble()*Math.PI*2,rad=.17+r.nextDouble()*.37;
                l.addParticle(new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.065f,.055f,.04f),.45f),p.getX()+.5+Math.cos(a)*rad,p.getY()+.45+r.nextDouble()*.85,p.getZ()+.5+Math.sin(a)*rad,-Math.sin(a)*.035,.015,Math.cos(a)*.035);
            }
            if(r.nextInt(4)==0)l.addParticle(net.minecraft.core.particles.ParticleTypes.SMOKE,p.getX()+.5,p.getY()+.5,p.getZ()+.5,0,.035,0);
        }
    }
    public static class PurpleSwampWater extends Block implements net.minecraft.world.level.block.SimpleWaterloggedBlock{
        PurpleSwampWater(){super(BlockBehaviour.Properties.copy(Blocks.WATER).noCollission().noOcclusion().strength(0));registerDefaultState(stateDefinition.any().setValue(BlockStateProperties.WATERLOGGED,true));}
        @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(BlockStateProperties.WATERLOGGED);}
        @Override public net.minecraft.world.level.material.FluidState getFluidState(BlockState s){return s.getValue(BlockStateProperties.WATERLOGGED)?net.minecraft.world.level.material.Fluids.WATER.getSource(false):super.getFluidState(s);}
        @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return net.minecraft.world.phys.shapes.Shapes.empty();}
        @Override public void animateTick(BlockState s,Level l,BlockPos p,net.minecraft.util.RandomSource r){
            if(r.nextInt(6)==0)l.addParticle(net.minecraft.core.particles.ParticleTypes.ENTITY_EFFECT,p.getX()+r.nextDouble(),p.getY()+1.03,p.getZ()+r.nextDouble(),.42,.08,.60);
        }
    }
''',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s;s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items if not n.startswith('fast_arch_'))+'}'+a,1);p.write_text(s,encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,*_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
# Craftable shop awnings and window curtains in each color.
for n in ('rose','mint','cocoa'):
 wool={'rose':'pink_wool','mint':'green_wool','cocoa':'brown_wool'}[n]
 for typ,pattern in [('shop_awning',['SSS','WVW','VWV']),('window_curtain',['SSS','WVW','WVW'])]:
  name=typ+'_'+n
  dump(res/'data/noctismagic/recipes'/f'{name}.json',{'type':'minecraft:crafting_shaped','pattern':pattern,'key':{'S':{'item':'minecraft:stick'},'W':{'item':'minecraft:'+wool},'V':{'item':'minecraft:white_wool'}},'result':{'item':'noctismagic:'+name,'count':3}})
# Extend real seating to all existing booths and both new armchairs.
p=java/'ChairSeat.java';s=p.read_text(encoding='utf-8')
a='return name.endsWith("_chair")||name.equals("lacrimosa_pew")||name.equals("chair");';assert a in s
s=s.replace(a,'return name.endsWith("_chair")||name.startsWith("fast_armchair_")||name.equals("fast_booth")||name.equals("lacrimosa_pew")||name.equals("chair");',1)
s=s.replace('if(n.equals("swamp_chair"))','if(n.equals("fast_booth")||n.startsWith("fast_armchair_"))return 9/16.0;\n  if(n.equals("swamp_chair"))',1);p.write_text(s,encoding='utf-8')
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8')
a=s.index('    static Plan bakery(boolean pastry){');b=s.index('        return p;',a)
s=s[:b]+'''        if(pastry){
            // Layered stone base, ornate frame and pilasters; leave the doorway clear.
            for(int x=2;x<=22;x++){
                p.put(x,0,2,Blocks.SMOOTH_STONE);
                p.put(x,7,3,Furniture.SWEET_CORNICE.get());
                if(x<10||x>14){
                    p.put(x,6,2,Furniture.SHOP_AWNING_ROSE.get());
                    p.put(x,5,3,Furniture.SWEET_CARVED_PANEL.get());
                    if(x%3==0)p.put(x,4,4,Furniture.WINDOW_CURTAIN_ROSE.get().defaultBlockState().setValue(HorizontalDirectionalBlock.FACING,Direction.SOUTH));
                }
            }
            for(int x:new int[]{2,9,15,22})for(int y=1;y<=6;y++)p.put(x,y,3,Furniture.SWEET_CARVED_PILLAR.get());
            for(int x=11;x<=13;x++)p.put(x,6,2,Furniture.SWEET_SIGN.get());
            for(int x:new int[]{8,16})p.put(x,4,2,Furniture.SWEET_LAMP.get());
            for(int z=5;z<=19;z+=3)for(int x:new int[]{1,23}){
                royalFacing(p,x,6,z,Furniture.SWEET_CORNICE.get(),x==1?Direction.WEST:Direction.EAST);
                royalFacing(p,x,1,z,Furniture.SWEET_CARVED_PANEL.get(),x==1?Direction.WEST:Direction.EAST);
            }
            for(int x:new int[]{3,21}){p.put(x,1,2,Blocks.FLOWER_POT);p.put(x,1,2,Blocks.POTTED_POPPY);}
            // An actual pair of doors.
            BlockState door=Blocks.CHERRY_DOOR.defaultBlockState().setValue(DoorBlock.FACING,Direction.NORTH);
            for(int x=12;x<=13;x++){
                BlockState ds=door.setValue(DoorBlock.HINGE,x==12?net.minecraft.world.level.block.state.properties.DoorHingeSide.LEFT:net.minecraft.world.level.block.state.properties.DoorHingeSide.RIGHT);
                p.put(x,1,3,ds.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER));
                p.put(x,2,3,ds.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER));
            }
        }
'''+s[b:]
a=s.index('    static Plan fastFood(){');b=s.index('        return p;',a)
s=s[:b]+'''        // Refined modern facade and smooth tiled golden arches.
        p.box(11,8,4,21,10,4,Blocks.AIR);
        p.box(12,8,5,19,10,5,Blocks.GRAY_CONCRETE);
        Block[][] logo={{Furniture.FAST_ARCH_0_0.get(),Furniture.FAST_ARCH_1_0.get(),Furniture.FAST_ARCH_2_0.get(),Furniture.FAST_ARCH_3_0.get()},{Furniture.FAST_ARCH_0_1.get(),Furniture.FAST_ARCH_1_1.get(),Furniture.FAST_ARCH_2_1.get(),Furniture.FAST_ARCH_3_1.get()}};
        for(int row=0;row<2;row++)for(int x=0;x<4;x++)p.put(14+x,10-row,4,logo[row][x]);
        for(int x=2;x<=30;x++){p.put(x,7,5,Furniture.FAST_FACADE_TRIM.get());if(x<12||x>20)p.put(x,6,5,Furniture.FAST_FACADE_TRIM.get());}
        for(int x:new int[]{2,12,20,30})for(int y=1;y<=5;y++)p.put(x,y,5,Furniture.FAST_FACADE_PANEL.get());
        for(int x:new int[]{4,10,22,28}){
            royalFacing(p,x,1,9,Furniture.FAST_ARMCHAIR_RED.get(),x<16?Direction.EAST:Direction.WEST);
            royalFacing(p,x,1,14,Furniture.FAST_ARMCHAIR_GRAY.get(),x<16?Direction.EAST:Direction.WEST);
        }
        for(int x:new int[]{8,24}){
            p.put(x,1,11,Furniture.FAST_TABLE.get());p.put(x,2,11,Furniture.FAST_TRAY.get());
            royalFacing(p,x,1,10,Furniture.FAST_ARMCHAIR_RED.get(),Direction.SOUTH);
            royalFacing(p,x,1,12,Furniture.FAST_ARMCHAIR_GRAY.get(),Direction.NORTH);
        }
        for(int x=13;x<=19;x++)p.put(x,0,3,Blocks.SMOOTH_STONE);
        for(int x:new int[]{3,29})p.put(x,2,3,Furniture.FAST_LAMP.get());
'''+s[b:]
a=s.index('    static Plan shrekSwamp(){');b=s.index('        return p;',a)
sub=s[a:b].replace('p.put(x,0,z,Blocks.WATER);','p.put(x,0,z,Furniture.SWAMP_PURPLE_WATER.get());').replace('if((x+z)%3==0)p.put(x,-1,z,Blocks.SEA_LANTERN);','if((x+z)%3==0)p.put(x,-1,z,Blocks.MUD);')
s=s[:a]+sub+'''        // Dung and fly swarms in the muddy margins and outside the outhouse.
        for(int[] q:new int[][]{{8,8},{22,11},{7,25},{22,26},{26,3},{29,11},{11,25},{5,12}}){
            p.put(q[0],0,q[1],Blocks.MUD);p.put(q[0],1,q[1],Furniture.SWAMP_DUNG.get());
        }
'''+s[b:]
p.write_text(s,encoding='utf-8')
print('Ornate patisserie, craftable awnings and curtains, upholstered fast-food chairs and booths, purple waterlogged swamp surface, dung and fly particles.')
