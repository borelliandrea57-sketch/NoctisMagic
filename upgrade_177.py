"""1.7.7: actual Shrek wetlands, rustic furniture, functional doors and Joker's supplied voice."""
from pathlib import Path
import sys,json,math,random,subprocess
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
palette={'bark':(85,59,37),'oak':(120,79,43),'moss':(72,94,42),'clay':(133,104,76),'iron':(86,88,77),'linen':(181,166,115),'amber':(245,190,91),'green':(92,107,50),'onion':(210,165,98),'stone':(95,100,83)}
for name,col in palette.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(name)
 for y in range(64):
  for x in range(64):
   v=.85+.12*rng.random()+.05*math.sin(x*.7+y*.11)
   if name in ('oak','bark'):v*=.78+.28*math.sin(y*.45+math.sin(x*.13))**2
   if name=='clay' and (y%16==0 or (x+(y//16%2)*16)%32==0):v*=.46
   if name=='moss':v*=.8+.28*math.sin(x*.25)*math.cos(y*.19)
   if name=='iron':v*=.77+.28*math.sin(x*math.pi/64)**2
   im.putpixel((x,y),(*[max(0,min(255,int(c*v))) for c in col],255))
 p=assets/'textures/block'/f'swamp_{name}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
table=[B(x,0,z,x+3,12,z+3,'bark') for x in (1,12) for z in (1,12)]+[B(0,12,0,16,16,16,'oak'),B(0,12,0,16,13,1,'iron')]
chair=[B(x,0,z,x+2,7,z+2,'bark') for x in (1,13) for z in (1,13)]+[B(1,7,1,15,9,15,'oak'),B(1,9,13,3,16,15,'bark'),B(13,9,13,15,16,15,'bark'),B(3,11,13,13,15,15,'oak')]
shelf=[B(0,0,13,16,16,16,'bark'),B(0,0,3,2,16,15,'oak'),B(14,0,3,16,16,15,'oak')]+[B(0,y,3,16,y+1,15,'oak') for y in (0,5,10,15)]
for y in (1,6,11):
 for x in (3,8):shelf += [B(x,y,7,x+4,y+3,12,'clay'),B(x+1,y+3,8,x+3,y+4,11,'iron')]
onions=[B(1,0,1,15,1,15,'oak'),B(1,1,1,15,3,2,'bark'),B(1,1,14,15,3,15,'bark')]
for x,z in ((4,4),(9,4),(4,9),(10,10)):
 onions += [B(x,1,z,x+4,4,z+4,'onion'),B(x+1,4,z+1,x+3,5,z+3,'onion'),B(x+1.5,5,z+1.5,x+2.5,6,z+2.5,'green')]
stove=[B(0,0,0,16,2,16,'stone'),B(1,2,1,15,13,15,'iron'),B(2,3,0,14,10,2,'oak'),B(4,5,0,12,8,1,'amber'),B(0,13,0,16,15,16,'stone'),B(7,15,7,9,16,9,'iron')]
lamp=[B(5,0,5,11,2,11,'iron'),B(4,2,4,12,12,12,'amber'),B(3,12,3,13,14,13,'iron'),B(7,14,7,9,16,9,'iron')]+[B(x,2,z,x+1,12,z+1,'iron') for x in (3,12) for z in (3,12)]
sign=[B(0,4,12,16,13,15,'oak'),B(7,0,13,9,4,15,'bark'),B(2,5,11,14,12,12,'sign')]
im=Image.new('RGBA',(64,64),(121,78,43,255));d=ImageDraw.Draw(im);d.rectangle((1,1,62,62),outline=(64,40,26),width=3);d.text((5,12),'BEWARE',fill=(240,222,155));d.text((8,30),'OGRE',fill=(240,222,155));im.save(assets/'textures/block/swamp_sign.png')
items={'swamp_table':('Tavolo rustico','Rustic table',0,table),'swamp_chair':('Sedia rustica','Rustic chair',0,chair),'swamp_shelf':('Credenza di terracotta','Earthenware cupboard',0,shelf),'swamp_onions':('Cesto di cipolle','Onion basket',0,onions),'swamp_stove':('Stufa in ghisa','Cast iron stove',0,stove),'swamp_lamp':('Lanterna della palude','Swamp lantern',3,lamp),'swamp_sign':('Cartello Attenti all’orco','Beware ogre sign',0,sign),'swamp_mud_bricks':('Mattoni di fango lavorati','Worked mud bricks',-1,'clay'),'swamp_moss_roof':('Tetto di muschio','Moss roof',-1,'moss')}
decl=[]
for n,(it,en,k,boxes) in items.items():
 expr='new Block(BlockBehaviour.Properties.of().strength(1.5f))' if k<0 else f'new FurnitureBlock({k})'
 decl += [f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));']
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s;s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a,1);p.write_text(s,encoding='utf-8')
for n,(it,en,k,boxes) in items.items():
 if k<0:
  model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/swamp_'+boxes}};variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tx={m:'noctismagic:block/swamp_'+m for m in list(palette)+['sign']};tx['particle']=tx['oak']
  model={'textures':tx,'elements':[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]}
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n});dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,k,boxes) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static Plan shrekSwamp(){');b=s.index('        return p;',a)+len('        return p;')
s=s[:a]+'''    static void swampDoor(Plan p,int x,int z,Block door,net.minecraft.world.level.block.state.properties.DoorHingeSide hinge){
        BlockState st=door.defaultBlockState().setValue(DoorBlock.FACING,Direction.NORTH).setValue(DoorBlock.HINGE,hinge);
        p.put(x,1,z,st.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER));
        p.put(x,2,z,st.setValue(DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER));
    }
    static Plan shrekSwamp(){
        Plan p=new Plan(31,31,15,"La Palude di Shrek");
        Block mud=Furniture.SWAMP_MUD_BRICKS.get(),moss=Furniture.SWAMP_MOSS_ROOF.get();
        for(int x=0;x<31;x++)for(int z=0;z<31;z++){
            boolean trail=x>=13&&x<=17&&z<13;
            boolean pond=(x-5)*(x-5)*.8+(z-19)*(z-19)*.45<23 || (x-25)*(x-25)*.9+(z-23)*(z-23)*.5<19 || (x-5)*(x-5)+(z-4)*(z-4)<10;
            boolean house=x>=9&&x<=21&&z>=10&&z<=23;
            boolean wc=x>=24&&x<=29&&z>=4&&z<=10;
            p.put(x,-2,z,Blocks.CLAY);p.put(x,-1,z,Blocks.MUD);
            if(pond&&!house&&!trail&&!wc&&x>0&&x<30&&z>0&&z<30){
                p.put(x,0,z,Blocks.WATER);
                if((x*7+z*11)%9==0)p.put(x,1,z,Blocks.LILY_PAD);
                if((x+z)%3==0)p.put(x,-1,z,Blocks.SEA_LANTERN);
            }else{
                p.put(x,0,z,trail?Blocks.COARSE_DIRT:(x*13+z*7)%4==0?Blocks.MUD:Blocks.GRASS_BLOCK);
                if(!trail&&!house&&!wc&&(x*7+z*3)%8==0)p.put(x,1,z,(x+z)%3==0?Blocks.BROWN_MUSHROOM:Blocks.FERN);
            }
        }
        for(int x=8;x<=22;x++)for(int z=10;z<=23;z++){
            double d=Math.pow((x-15)/7.1,2)+Math.pow((z-16.5)/6.7,2);
            if(d<=1.11)p.put(x,0,z,Blocks.SPRUCE_PLANKS);
            for(int y=1;y<=8;y++){
                double q=d+Math.pow((y-1)/7.5,2);
                if(q<=1.14&&(q>.81||y==8))p.put(x,y,z,y>=5?moss:(x+z+y)%5==0?Blocks.ROOTED_DIRT:mud);
                if(y>=5&&q>.96&&q<1.13&&(x+z+y)%7==0)p.put(x,y+1,z,Blocks.MOSS_CARPET);
            }
        }
        p.box(13,1,10,17,3,13,Blocks.AIR);
        p.box(12,1,10,12,4,10,Blocks.DARK_OAK_LOG);p.box(18,1,10,18,4,10,Blocks.DARK_OAK_LOG);
        p.box(12,4,10,18,4,10,Blocks.DARK_OAK_LOG);
        p.box(13,1,10,13,3,10,mud);p.box(16,1,10,17,3,10,mud);
        swampDoor(p,14,10,Blocks.DARK_OAK_DOOR,net.minecraft.world.level.block.state.properties.DoorHingeSide.LEFT);
        swampDoor(p,15,10,Blocks.DARK_OAK_DOOR,net.minecraft.world.level.block.state.properties.DoorHingeSide.RIGHT);
        p.box(14,3,10,15,3,10,Blocks.DARK_OAK_PLANKS);
        for(int x:new int[]{11,19}){p.put(x,3,11,Blocks.SPRUCE_TRAPDOOR);p.put(x,2,9,Furniture.SWAMP_LAMP.get());}
        for(int z:new int[]{15,19})for(int x:new int[]{9,21})p.put(x,3,z,Furniture.SWEET_WINDOW.get());
        p.box(14,1,13,16,3,17,Blocks.AIR);
        p.put(15,4,16,Blocks.CHAIN);p.put(15,3,16,Furniture.SWAMP_LAMP.get());
        p.put(19,1,18,Furniture.SWAMP_STOVE.get());p.put(20,1,18,Blocks.SMOKER);
        p.box(19,3,18,19,10,18,Blocks.BRICKS);p.put(19,11,18,Blocks.CAMPFIRE);
        for(int x:new int[]{11,12,13})p.put(x,1,19,Furniture.SWAMP_SHELF.get());
        p.put(11,1,18,Blocks.BARREL);p.put(12,1,18,Blocks.CHEST);
        p.put(11,1,15,Blocks.GREEN_BED.defaultBlockState().setValue(BedBlock.FACING,Direction.SOUTH).setValue(BedBlock.PART,net.minecraft.world.level.block.state.properties.BedPart.FOOT));
        p.put(11,1,16,Blocks.GREEN_BED.defaultBlockState().setValue(BedBlock.FACING,Direction.SOUTH).setValue(BedBlock.PART,net.minecraft.world.level.block.state.properties.BedPart.HEAD));
        p.put(15,1,20,Furniture.SWAMP_TABLE.get());p.put(15,2,20,Furniture.SWAMP_ONIONS.get());
        royalFacing(p,14,1,20,Furniture.SWAMP_CHAIR.get(),Direction.EAST);royalFacing(p,16,1,20,Furniture.SWAMP_CHAIR.get(),Direction.WEST);
        p.put(18,1,20,Blocks.CRAFTING_TABLE);p.put(18,2,20,Blocks.POTTED_BROWN_MUSHROOM);
        p.box(24,0,5,28,0,9,Blocks.SPRUCE_PLANKS);p.walls(24,1,5,28,4,9,Blocks.DARK_OAK_PLANKS);
        swampDoor(p,26,5,Blocks.SPRUCE_DOOR,net.minecraft.world.level.block.state.properties.DoorHingeSide.LEFT);
        p.put(26,3,5,Blocks.OAK_FENCE);
        for(int k=0;k<3;k++)for(int z=4;z<=10;z++){p.put(23+k,5+k,z,Blocks.SPRUCE_SLAB);p.put(29-k,5+k,z,Blocks.SPRUCE_SLAB);}
        p.box(25,5,5,27,5,9,Blocks.SPRUCE_PLANKS);p.put(26,1,8,Blocks.CAULDRON);p.put(27,2,8,Furniture.SWAMP_LAMP.get());
        for(int[] t:new int[][]{{3,9},{27,14},{7,27},{25,28},{3,27}}){
            int x=t[0],z=t[1];p.put(x,0,z,Blocks.ROOTED_DIRT);p.box(x,1,z,x,6,z,Blocks.OAK_LOG);
            for(int dx=-3;dx<=3;dx++)for(int dz=-3;dz<=3;dz++)for(int y=5;y<=9;y++)if(Math.abs(dx)+Math.abs(dz)+Math.abs(y-7)<=5&&!(dx==0&&dz==0&&y<=6))
                p.put(x+dx,y,z+dz,Blocks.OAK_LEAVES.defaultBlockState().setValue(LeavesBlock.PERSISTENT,true));
            for(int dx:new int[]{-2,2})for(int y=3;y<=5;y++)p.put(x+dx,y,z,Blocks.VINE.defaultBlockState().setValue(dx<0?VineBlock.EAST:VineBlock.WEST,true));
        }
        for(int[] t:new int[][]{{2,15},{8,24},{23,18},{28,19},{6,14},{9,27}}){
            p.put(t[0],0,t[1],Blocks.MUD);p.put(t[0],1,t[1],Blocks.FERN);
        }
        for(int z=2;z<=8;z+=3)for(int x:new int[]{11,19}){p.put(x,1,z,Blocks.OAK_FENCE);p.put(x,2,z,Furniture.SWAMP_LAMP.get());}
        for(int z=1;z<=9;z++)for(int x=13;x<=17;x++)if((x+z)%3==0)p.put(x,0,z,Blocks.MUD_BRICKS);
        p.put(10,1,8,Furniture.SWAMP_SIGN.get());p.put(20,1,8,Blocks.COMPOSTER);
        return p;'''+s[b:]
p.write_text(s,encoding='utf-8')
p=java/'FallenEncounter.java';s=p.read_text(encoding='utf-8');a='static final RegistryObject<SoundEvent> PHOENIX_OBJECTION=';assert a in s
s=s.replace(a,'public static final RegistryObject<SoundEvent> JOKER_ARSENE_VOICE=SOUNDS.register("joker_arsene_voice",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"joker_arsene_voice")));\n    '+a,1);p.write_text(s,encoding='utf-8')
p=java/'Joker.java';s=p.read_text(encoding='utf-8');a='persona=a.getUUID();say(l,"Persona! Arsene!");';assert a in s
s=s.replace(a,a+'\n                    playSound(FallenEncounter.JOKER_ARSENE_VOICE.get(),1.3f,1.0f);',1);p.write_text(s,encoding='utf-8')
target=assets/'sounds/joker_arsene_voice.ogg';target.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(Path(__file__).with_name('joker_arsene_audio.opus')),'-ac','1','-c:a','libvorbis','-q:a','4',str(target)],check=True)
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['joker_arsene_voice']={'sounds':[{'name':'noctismagic:joker_arsene_voice'}]};dump(p,d)
print('Shrek: wetland pools, new furniture, functional doors, and original Joker summon sound.')
