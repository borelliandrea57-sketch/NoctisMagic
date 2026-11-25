"""1.7.32: expressive bigger ponies, relentless Geass and modern fast-food architecture."""
from pathlib import Path
import sys,re,math,json,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
# Geass ignores fluid, ground support and danger. Actual walls still obstruct normal movement.
p=java/'GeassExile.java';s=p.read_text(encoding='utf-8')
a=s.index(' static boolean safe(ServerPlayer p,Vec3 d){');b=s.index(' static void release',a)
s=s[:a]+''' static boolean safe(ServerPlayer p,Vec3 d){
  ServerLevel l=p.serverLevel();
  BlockPos b=BlockPos.containing(p.position().add(d.scale(.65)));
  if(!l.hasChunkAt(b)||!l.getWorldBorder().isWithinBounds(b))return false;
  return l.noCollision(p,p.getBoundingBox().move(d.x*.55,0,d.z*.55))
      ||l.noCollision(p,p.getBoundingBox().move(d.x*.55,1,d.z*.55));
 }
'''+s[b:]
s=s.replace('if(i==o.avoid)continue;','if(i==o.avoid&&safe(p,direction(o.dir<0?i:o.dir)))continue;')
s=s.replace('+(GeassWalkSafety.safe(p,d,2.5)?.60:0)+(GeassWalkSafety.safe(p,d,4.0)?.35:0)','')
s=s.replace('if(best<0){best=16;o.blocked++;if(o.blocked>=60){release(p,false);return;}}','if(best<0){best=o.dir>=0&&o.dir<16?o.dir:0;o.blocked++;}')
s=s.replace('if(best<0){best=16;o.blocked++;if(o.blocked>=60){o.blocked=0;o.avoid=-1;}}','if(best<0){best=o.dir>=0&&o.dir<16?o.dir:0;o.blocked++;}')
s=s.replace('if(o.stuck>=4){release(p,false);return;}','if(o.stuck>=4){o.stuck=0;o.avoid=-1;o.dir=-1;}')
# Keep the direction during falls and swimming rather than rerouting to a dry bank.
s=s.replace('if(o.dir<0||o.dir==16||p.tickCount%5==0||!safe(p,direction(o.dir))){','if(o.dir<0||o.dir==16||(p.onGround()&&!p.isInWater()&&!p.isInLava()&&(p.tickCount%5==0||!safe(p,direction(o.dir))))){')
s=s.replace('if(p.tickCount%20==0){\n   double progress','if(p.tickCount%20==0&&p.onGround()&&!p.isInWater()&&!p.isInLava()){\n   double progress')
p.write_text(s,encoding='utf-8')
p=java/'GeassExileClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('boolean walk=dir<16&&GeassWalkSafety.safe(p,GeassWalkSafety.direction(dir),.75);','boolean walk=dir<16;')
s=s.replace('input.forwardImpulse=walk?.72f:0','input.forwardImpulse=walk?1f:0').replace('input.jumping=false;','input.jumping=walk&&p.horizontalCollision&&p.onGround();')
p.write_text(s,encoding='utf-8')
# Pony size: matching body and collision bounds, riding height and face changes.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
s,n=re.subn(r'(EntityType\.Builder\.<FriendshipPony>of\(FriendshipPony::new,MobCategory\.CREATURE\)\.sized\()[^)]*\)',r'\g<1>1.30f,2.06f)',s);assert n>=6
p.write_text(s,encoding='utf-8')
p=java/'FriendshipPony.java';s=p.read_text(encoding='utf-8')
s=re.sub(r'(double getPassengersRidingOffset\(\)\{return )[\d.]+;',r'\g<1>1.38;',s,count=1);p.write_text(s,encoding='utf-8')
p=java/'PonyCartoonClient.java';s=p.read_text(encoding='utf-8')
a='  @Override public ResourceLocation getTextureLocation(FriendshipPony e){';assert a in s
b=s.index(a);end=s.index('\n',b)
s=s[:b]+'''  @Override protected void scale(FriendshipPony e,PoseStack p,float partial){p.scale(1.25f,1.25f,1.25f);}
  static String expression(FriendshipPony e){
   if(e.hurtTime>0)return "_hurt";
   if((e.tickCount+e.getId()*11)%83<4)return "_blink";
   if(e.isInSittingPose())return "_happy";
   int t=(e.tickCount+e.getId()*31)%200;
   return t<40?"_happy":t>=150&&t<180?"_curious":"";
  }
  @Override public ResourceLocation getTextureLocation(FriendshipPony e){return new ResourceLocation(Noctis.ID,"textures/entity/pony_cartoon_"+k+expression(e)+".png");}'''+s[end:]
a='   tail.ry=(float)Math.sin(age*.13f)*(.18f+amount*.12f);';assert a in s
s=s.replace(a,'''   String expr=R.expression(e);
   head.rz=(expr.equals("_curious")?.15f:expr.equals("_hurt")?-.12f:0)+(float)Math.sin(age*.07f)*.025f;
   if(expr.equals("_happy")){head.rx-=.09f;ears[0].rz-=.12f;ears[1].rz+=.12f;}
   if(expr.equals("_hurt")){head.rx+=.14f;ears[0].rz+=.42f;ears[1].rz-=.42f;}
'''+a,1)
p.write_text(s,encoding='utf-8')
def mix(a,b,t):return tuple(round(x+(y-x)*max(0,min(1,t))) for x,y in zip(a,b))
for k in range(4,10):
 base=Image.open(assets/'textures/entity'/f'pony_cartoon_{k}.png').convert('RGBA')
 for expr in ('blink','happy','hurt','curious'):
  im=base.copy()
  for tile in (21,22):
   X,Y=tile%8*128,tile//8*128
   for y in range(128):
    v=(y-3)/121
    for x in range(128):
     u=(x-3)/121;c=im.getpixel((X+x,Y+y))[:3]
     coat=base.getpixel((X+7,Y+y))[:3]
     if tile==21:
      for side in (-1,1):
       dx=(u-(.5+side*.119))/.082
       if abs(dx)<1.26 and .25<v<.70 and expr in ('blink','happy','hurt'):
        c=coat
        if abs(dx)<1.05:
         line=.49+(.04 if expr=='hurt' else -.065)*(1-dx*dx)+(.035*side*dx if expr=='hurt' else 0)
         if abs(v-line)<.011:c=(63,38,65)
         if .76<abs(dx)<1.06 and abs(v-line+.02)<.025:c=(63,38,65)
       if expr=='curious' and abs(dx)<1 and abs(v-(.26+.055*side+.025*dx))<.009:c=mix(coat,(48,33,59),.7)
      if expr=='happy':c=mix(c,(241,119,151),.28*math.exp(-((abs(u-.5)-.18)/.045)**2-((v-.68)/.04)**2))
     elif .60<v<.87 and abs(u-.5)<.19:
      c=coat;f=abs(u-.5)
      if expr=='happy' and f<.145:
       line=.75-.13*(f/.145)**2
       if abs(v-line)<.025*(1-f/.16)+.007:c=(89,44,70)
       if f<.09 and abs(v-line+.012)<.008:c=(242,219,213)
      elif expr=='hurt' and f<.10 and abs(v-(.70+.09*(f/.10)**2))<.014:c=(89,44,70)
      elif expr=='curious' and ((u-.5)/.042)**2+((v-.73)/.05)**2<1:c=(89,44,70)
      elif expr=='blink' and f<.105 and abs(v-(.707-.10*(f/.105)**2))<.012:c=mix(coat,(89,50,80),.57)
     im.putpixel((X+x,Y+y),(*c,255))
  im.save(assets/'textures/entity'/f'pony_cartoon_{k}_{expr}.png')
# Modern architectural surfaces, individually placeable.
materials={
 'fast_terrazzo':('Gres terrazzo avorio','Ivory terrazzo', (220,213,199),'terrazzo'),
 'fast_porcelain':('Piastrella porcellanata grigio caldo','Warm porcelain tile',(159,160,157),'tile'),
 'fast_parquet':('Parquet a spina di pesce','Herringbone parquet',(166,121,78),'parquet'),
 'fast_kitchen_tile':('Piastrella cucina antiscivolo','Kitchen safety tile',(117,124,130),'tile'),
 'fast_metal_clad':('Rivestimento antracite composito','Anthracite composite cladding',(55,62,69),'metal'),
 'fast_aluminium':('Pannello alluminio satinato','Brushed aluminium panel',(156,167,177),'metal'),
 'fast_roof_panel':('Copertura metallica aggraffata','Standing seam roofing',(47,54,62),'roof'),
 'fast_wall_tile':('Rivestimento ceramico crema','Cream ceramic wall tile',(232,226,211),'tile')}
for n,(it,en,base,kind) in materials.items():
 rng=random.Random(n);im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
 for y in range(64):
  for x in range(64):
   t=.96+rng.uniform(-.025,.025)
   if kind=='metal':t+=.045*math.sin(x*.21)+.025*math.sin(y*2.8)
   if kind=='tile' and (x%32<2 or y%32<2):t*=.66
   if kind=='roof':t*=.88+.16*math.sin(math.pi*(x%16)/16)**2+(0.19 if x%16 in (0,1) else 0)
   if kind=='parquet':
    a=(x+y)//12;b=(x-y)//12;t*=.80+.19*((a*5+b*3)%7)/6
    if (x+y)%12==0 or (x-y)%12==0:t*=.72
    t+=.03*math.sin((x+y)*2 if (a+b)%2 else (x-y)*2)
   im.putpixel((x,y),(*[max(0,min(255,round(q*t))) for q in base],255))
 if kind=='terrazzo':
  for i in range(150):
   x,y=rng.randrange(64),rng.randrange(64);r=rng.choice([1,1,2]);c=rng.choice([(171,157,143),(239,233,219),(120,122,124),(199,177,152)])
   d.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill=c)
 im.save(assets/'textures/block'/f'{n}.png')
# Replace old facade slats' wood with metal without altering other furniture.
p=assets/'models/block/fast_facade_panel.json';d=json.loads(p.read_text(encoding='utf-8'));d['textures']['oak']='noctismagic:block/fast_aluminium';dump(p,d)
# One continuous, antialiased 8x3 sign. Explicit front UVs prevent repeated fragments.
W,H=512,192;im=Image.new('RGBA',(W,H),(35,39,44,255));d=ImageDraw.Draw(im)
# Two smoothly sampled arches, with strong golden legs and a central junction.
for cx in (W*.31,W*.69):
 pts=[]
 for j in range(181):
  a=math.pi*j/180
  pts.append((cx+W*.19*math.cos(a),H*.89-H*.74*math.sin(a)))
 d.line(pts,fill=(241,181,13),width=22,joint='curve')
 d.line([(x,y-2) for x,y in pts],fill=(255,207,30),width=12,joint='curve')
for row in range(3):
 for x in range(8):
  n=f'fast_m_logo_{x}_{row}';im.crop((x*64,row*64,(x+1)*64,(row+1)*64)).save(assets/'textures/block'/f'{n}.png')
  materials[n]=('Tassello insegna dorata','Golden arches sign tile',(0,0,0),'logo')
decl=[]
for n,(it,en,base,kind) in materials.items():
 decl.append(f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->new Block(BlockBehaviour.Properties.of().strength(2f,6f)'+('.lightLevel(s->5)' if kind=='logo' else '')+'));')
 if kind!='logo':decl.append(f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));')
 tx='noctismagic:block/'+n
 if kind=='logo':
  model={'textures':{'all':tx,'side':'noctismagic:block/fast_metal_clad','particle':tx},'elements':[{'from':[0,0,0],'to':[16,16,16],'faces':{f:{'texture':'#all' if f=='north' else '#side','uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}}]}
 else:model={'parent':'minecraft:block/cube_all','textures':{'all':tx}}
 # Same north-facing image for building rotations using directional sign block below.
 if kind=='logo':
  decl[-1]=f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->new FurnitureBlock(0));'
  model['elements'][0]['from']=[0,0,13]
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 else:variants={'':{'model':'noctismagic:block/'+n}}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 if kind!='logo':
  dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
  dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s;s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n,q in materials.items() if q[-1]!='logo')+'}'+a,1);p.write_text(s,encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,*_) in materials.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static Plan fastFood(){');b=s.index('        return p;',a);sub=s[a:b]
for old,new in [('Blocks.DARK_OAK_PLANKS','Furniture.FAST_METAL_CLAD.get()'),('Blocks.STRIPPED_DARK_OAK_WOOD','Furniture.FAST_ALUMINIUM.get()'),('Blocks.STRIPPED_BIRCH_WOOD','Furniture.FAST_ALUMINIUM.get()'),('Blocks.WHITE_CONCRETE','Furniture.FAST_WALL_TILE.get()')]:
 sub=sub.replace(old,new)
# Preserve parking lines and existing seats, change interior floor and roof.
sub+='''        for(int z=6;z<=24;z++)for(int x=2;x<=30;x++){
            Block floor=z>=19?Furniture.FAST_KITCHEN_TILE.get():
                (x>=13&&x<=19?Furniture.FAST_TER RAZZO.get():(x==2||x==30||z==6||z==17?Furniture.FAST_PORCELAIN.get():Furniture.FAST_PARQUET.get()));
            p.put(x,0,z,floor);
        }
        p.box(0,8,4,32,8,26,Furniture.FAST_METAL_CLAD.get());
        p.box(1,9,6,31,9,25,Furniture.FAST_ROOF_PANEL.get());
        p.ring(0,9,4,32,26,Furniture.FAST_ALUMINIUM.get());
        p.ring(1,10,6,31,25,Furniture.FAST_METAL_CLAD.get());
        for(int x=2;x<=30;x++)p.put(x,8,4,Furniture.FAST_ALUMINIUM.get());
        p.box(12,5,3,20,5,4,Furniture.FAST_METAL_CLAD.get());
        for(int x=12;x<=20;x++)p.put(x,6,3,Furniture.FAST_FACADE_TRIM.get());
        p.box(11,8,4,21,11,4,Blocks.AIR);
        p.box(11,9,5,21,11,5,Furniture.FAST_METAL_CLAD.get());
        Block[][] bigLogo={'''+','.join('{'+','.join('Furniture.FAST_M_LOGO_'+str(x)+'_'+str(y)+'.get()' for x in range(8))+'}' for y in range(3))+'''};
        for(int row=0;row<3;row++)for(int x=0;x<8;x++)royalFacing(p,12+x,11-row,4,bigLogo[row][x],Direction.NORTH);
        for(int z=6;z<=25;z++)for(int x:new int[]{1,31})if(z%5==0)p.box(x,1,z,x,7,z,Furniture.FAST_ALUMINIUM.get());
'''.replace('TER RAZZO','TERRAZZO')
s=s[:a]+sub+s[b:];p.write_text(s,encoding='utf-8')
print('Larger expressive ponies, hazard-indifferent Geass, modern McDonalds materials and continuous 8x3 golden arches.')
