"""1.7.0: patisserie furniture, edible desserts, seated lawyers and satirical baker portrait."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
 p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
 p.parent.mkdir(parents=True,exist_ok=True)
 def ch(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
palette={'cream':(249,224,199),'rose':(212,116,153),'mint':(134,205,183),'gold':(215,165,86),'white':(255,245,224),'wood':(153,95,62),'wheel':(64,53,65),'berry':(178,40,77),'choc':(91,48,35),'pastry':(218,148,62),'pistachio':(142,172,88),'light':(255,241,190)}
for m,c in palette.items():
 pix=bytearray()
 for y in range(64):
  for x in range(64):
   v=.89+.07*math.sin(x*.23)**2+.17*math.exp(-((x-15)/5)**2)+.018*math.sin(x*2+y*3)
   if m=='wood':v*=.87+.13*math.sin(y*.9+math.sin(x*.2))**2
   if m=='rose' and (x%16-8)**2+(y%16-8)**2<3:v*=1.14
   if min(x,y,63-x,63-y)<1:v*=.72
   pix.extend((*[max(0,min(255,int(a*v))) for a in c],255))
 png(assets/'textures/block'/f'sweet_{m}.png',64,64,pix)
def legs(h):return [(x,0,z,x+2,h,z+2,'gold') for x in (2,12) for z in (2,12)]
chair=legs(7)+[(1,7,1,15,9,15,'cream'),(2,9,2,14,10,13,'rose'),(1,9,13,3,16,15,'gold'),(13,9,13,15,16,15,'gold'),(3,10,13,13,15,15,'mint'),(3,15,13,13,16,15,'gold')]
table=[(3,0,3,13,2,13,'gold'),(6,2,6,10,13,10,'wood'),(2,12,2,14,14,14,'cream'),(0,14,0,16,16,16,'white'),(0,13,0,16,14,1,'gold'),(0,13,15,16,14,16,'gold'),(0,13,1,1,14,15,'gold'),(15,13,1,16,14,15,'gold')]
counter=[(0,0,0,16,2,16,'gold'),(0,2,1,16,14,15,'cream'),(1,3,0,15,12,1,'rose'),(2,4,0,3,11,1,'gold'),(13,4,0,14,11,1,'gold'),(0,14,0,16,16,16,'white')]
def desserts(y):
 return [(2,y,2,6,y+1,7,'white'),(3,y+1,3,5,y+3,6,'pastry'),(7,y,2,11,y+1,7,'white'),(8,y+1,3,10,y+3,6,'choc'),(12,y,2,15,y+1,7,'white'),(12,y+1,3,15,y+3,6,'rose'),(3,y,9,7,y+1,14,'white'),(4,y+1,10,6,y+3,13,'pistachio'),(9,y,9,13,y+1,14,'white'),(10,y+1,10,12,y+3,13,'cream'),(10,y+3,10,12,y+4,13,'berry')]
case=[(0,0,0,16,2,16,'cream'),(0,7,0,16,8,16,'gold'),(0,14,0,16,16,16,'white')]+[(x,2,z,x+1,14,z+1,'gold') for x in (0,15) for z in (0,15)]+[(0,2,0,16,14,1,'glass'),(0,2,15,16,14,16,'glass')]+desserts(2)+desserts(8)
cart=[(x,0,z,x+3,3,z+3,'wheel') for x in (1,12) for z in (1,12)]+[(x,1,z,x+2,2,z+3,'gold') for x in (1,12) for z in (1,12)]+[(0,3,1,16,4,15,'mint'),(0,10,1,16,11,15,'white'),(1,4,1,2,10,15,'gold'),(14,4,1,15,10,15,'gold'),(0,12,1,1,15,15,'gold')]+desserts(4)+desserts(11)
lamp=[(6,0,6,10,3,10,'gold'),(3,3,3,13,5,13,'rose'),(4,5,4,12,12,12,'light'),(3,12,3,13,14,13,'gold'),(6,14,6,10,16,10,'gold')]
shelf=[(0,0,13,16,16,16,'mint'),(0,0,2,2,16,16,'cream'),(14,0,2,16,16,16,'cream')]+[(0,y,2,16,y+1,15,'white') for y in (0,5,10,15)]
for y in (1,6,11):
 for x in (3,7,11):shelf.extend([(x,y,7,x+3,y+3,12,['rose','mint','choc'][(x+y)%3]),(x,y+3,7,x+3,y+4,12,'gold')])
decor=[(0,0,13,16,16,16,'cream'),(1,1,12,15,15,13,'gold'),(2,2,11,14,14,12,'rose'),(4,5,10,12,10,11,'white'),(5,10,10,11,12,11,'pastry'),(7,12,10,9,14,11,'berry')]
tea=[(1,0,1,15,1,15,'gold'),(2,1,2,14,2,14,'white'),(3,2,4,9,7,10,'mint'),(9,3,5,12,5,9,'gold'),(4,7,5,8,8,9,'gold'),(10,2,10,14,5,14,'rose')]
items={'sweet_chair':('Sedia da pasticceria','Patisserie chair',0,chair),'sweet_table':('Tavolino in marmo rosa','Pink marble table',0,table),'sweet_counter':('Bancone confetteria','Confectionery counter',0,counter),'sweet_case':('Vetrina a due ripiani','Two-tier pastry case',0,case),'sweet_cart':('Carrello di dolci a rotelle','Wheeled pastry cart',0,cart),'sweet_lamp':('Lampada a globo pastello','Pastel pendant lamp',3,lamp),'sweet_shelf':('Scaffale di confetture','Jam shelf',0,shelf),'sweet_art':('Quadro pasticceria','Pastry wall art',0,decor),'sweet_tea':('Servizio da tè','Tea service',0,tea),'sweet_window':('Vetrina floreale','Floral window',-1,[])}
# A separate transparent window avoids depending on any broken vanilla override.
pix=bytearray()
for y in range(64):
 for x in range(64):
  if min(x,y,63-x,63-y)<3 or abs(x-32)<1 or abs(y-32)<1:rgba=(218,172,100,255)
  elif any((x-cx)**2+(y-cy)**2<12 for cx,cy in [(8,8),(56,8),(8,56),(56,56)]):rgba=(230,140,170,230)
  else:rgba=(222,247,242,55)
  pix.extend(rgba)
png(assets/'textures/block/sweet_window.png',64,64,pix)
decl=[]
for n,(it,en,k,boxes) in items.items():
 expr='new GlassBlock(BlockBehaviour.Properties.copy(Blocks.GLASS).noOcclusion())' if k==-1 else f'new FurnitureBlock({k})'
 decl.extend([f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));'])
edit('Furniture.java','public class Furniture{','public class Furniture{\n'+'\n'.join(decl)+'\n')
a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)'
edit('Noctis.java',a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a)
for n,(it,en,k,boxes) in items.items():
 if k==-1:
  model={'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/'+n},'render_type':'minecraft:translucent'};variants={'':{'model':'noctismagic:block/'+n}}
 else:
  tex={m:'noctismagic:block/sweet_'+m for m in palette};tex['glass']='minecraft:block/glass';tex['particle']=tex['cream']
  el=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{face:{'texture':'#'+m,'uv':[0,0,16,16]} for face in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]
  model={'textures':tex,'elements':el,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]}}}
  if n=='sweet_case':
   # Use own window texture for the case; cutout glass remains visible.
   tex['glass']='noctismagic:block/sweet_window';model['render_type']='minecraft:translucent'
  variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n});dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
foods={'croissant':('Cornetto al burro','Butter croissant',5,'pastry'),'pain_chocolat':('Pain au chocolat','Pain au chocolat',6,'choc'),'pistachio_croissant':('Cornetto al pistacchio','Pistachio croissant',6,'pistachio'),'strawberry_tart':('Crostatina alle fragole','Strawberry tart',6,'berry'),'cream_puff':('Bignè alla crema','Cream puff',5,'cream'),'macaron':('Macaron alla rosa','Rose macaron',4,'rose'),'cinnamon_roll':('Cinnamon roll','Cinnamon roll',6,'wood')}
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,''.join(f'public static final RegistryObject<Item> SWEET_{n.upper()}=ITEMS.register("{n}",()->new Item(new Item.Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition({hp}).saturationMod(.5f).build())));\n    ' for n,(it,en,hp,m) in foods.items())+a)
a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)'
edit('Noctis.java',a,'if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS){'+''.join('e.accept(SWEET_'+n.upper()+'.get());' for n in foods)+'}'+a)
for n,(it,en,hp,m) in foods.items():
 pix=bytearray();base=palette[m]
 for y in range(32):
  for x in range(32):
   dx=x-15.5;dy=y-15.5
   if n in ('croissant','pistachio_croissant'):inside=(dx/13)**2+(dy/9)**2<1 and not (dy>1 and (dx/6)**2+((dy-7)/6)**2<1)
   elif n=='pain_chocolat':inside=abs(dx)<12 and abs(dy)<8
   elif n=='macaron':inside=(dx/12)**2+(dy/8)**2<1
   else:inside=(dx/12)**2+(dy/11)**2<1
   if not inside:pix.extend((0,0,0,0));continue
   v=.83+.18*math.exp(-((dx+5)/7)**2)+.07*math.sin(dx*1.4+dy*.6)
   c=tuple(max(0,min(255,int(a*v))) for a in base)
   if n=='strawberry_tart' and dy>5:c=palette['pastry']
   if n=='macaron' and abs(dy)<2:c=palette['cream']
   if n=='pain_chocolat' and abs(dx)>7:c=palette['pastry']
   if n=='pistachio_croissant' and abs(dx)>6:c=palette['pastry']
   if n=='cinnamon_roll' and abs(math.sin(math.hypot(dx,dy)*.8+math.atan2(dy,dx)))<.35:c=palette['cream']
   pix.extend((*c,255))
 png(assets/'textures/item'/f'{n}.png',32,32,pix)
 dump(assets/'models/item'/f'{n}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/'+n}})
recipes={'croissant':['wheat','sugar','egg'],'pain_chocolat':['noctismagic:croissant','cocoa_beans'],'pistachio_croissant':['noctismagic:croissant','pumpkin_seeds'],'strawberry_tart':['wheat','sweet_berries','sugar'],'cream_puff':['wheat','milk_bucket','egg'],'macaron':['egg','sugar','pink_petals'],'cinnamon_roll':['wheat','sugar','cocoa_beans']}
for n,ings in recipes.items():
 dump(res/'data/noctismagic/recipes'/f'{n}.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':x if ':' in x else 'minecraft:'+x} for x in ings],'result':{'item':'noctismagic:'+n,'count':2}})
# Baking raw dough into butter croissants.
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','public static final RegistryObject<Item> SWEET_DOUGH=ITEMS.register("sweet_dough",()->new Item(new Item.Properties()));\n    public static final RegistryObject<Item> CATHEDRAL_EGG=')
dump(assets/'models/item/sweet_dough.json',{'parent':'minecraft:item/generated','textures':{'layer0':'minecraft:item/wheat'}})
dump(res/'data/noctismagic/recipes/sweet_dough.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'minecraft:wheat'},{'item':'minecraft:egg'},{'item':'minecraft:sugar'}],'result':{'item':'noctismagic:sweet_dough','count':3}})
for typ,ticks in [('smelting',200),('smoking',100)]:
 dump(res/'data/noctismagic/recipes'/f'croissant_{typ}.json',{'type':'minecraft:'+typ,'ingredient':{'item':'noctismagic:sweet_dough'},'result':'noctismagic:croissant','experience':.35,'cookingtime':ticks})
for loc in ('it_it','en_us'):
 f=assets/'lang'/f'{loc}.json';d=json.loads(f.read_text(encoding='utf-8'))
 for n,(it,en,k,boxes) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 for n,(it,en,hp,m) in foods.items():d['item.noctismagic.'+n]=it if loc=='it_it' else en
 d['item.noctismagic.sweet_dough']='Impasto dolce' if loc=='it_it' else 'Sweet dough'
 dump(f,d)
# Fresh, brighter patisserie layout; retain the separate bakery and existing NPC placement.
f=java/'GothicEgg.java';s=f.read_text(encoding='utf-8')
a=s.index('    static Plan bakery(boolean pastry){');b=s.index('        return p;',a)
s=s[:b]+'''        if(pastry){
            Block win=Furniture.SWEET_WINDOW.get();
            for(int x=2;x<23;x++)for(int z=4;z<=20;z++)p.put(x,0,z,(x+z)%2==0?Blocks.WHITE_TERRACOTTA:Blocks.PINK_TERRACOTTA);
            p.box(2,1,4,22,7,20,Blocks.AIR);
            for(int x=3;x<=21;x++)if(x<10||x>14)p.box(x,2,3,x,5,3,win);
            for(int z=6;z<=18;z+=6)for(int x:new int[]{1,23})p.box(x,2,z,x,5,z+2,win);
            for(int x:new int[]{1,23})for(int z=4;z<=20;z++)p.put(x,1,z,Blocks.PINK_TERRACOTTA);
            for(int x=2;x<=22;x++){p.put(x,5,21,Blocks.STRIPPED_BIRCH_WOOD);p.put(x,8,3,Blocks.WHITE_TERRACOTTA);}
            p.box(2,8,4,22,8,20,Blocks.BIRCH_PLANKS);
            for(int x:new int[]{4,12,20})for(int z:new int[]{6,10,14,18}){
                p.put(x,7,z,Blocks.CHAIN);p.put(x,6,z,Furniture.SWEET_LAMP.get());
            }
            for(int x:new int[]{5,10,19})for(int z:new int[]{8,12}){
                p.put(x,1,z,Furniture.SWEET_TABLE.get());p.put(x,2,z,Furniture.SWEET_TEA.get());
                royalFacing(p,x-1,1,z,Furniture.SWEET_CHAIR.get(),Direction.EAST);
                royalFacing(p,x+1,1,z,Furniture.SWEET_CHAIR.get(),Direction.WEST);
            }
            for(int x=3;x<=21;x++)if(x<11||x>13){
                p.put(x,1,14,Furniture.SWEET_COUNTER.get());
                p.put(x,2,14,Furniture.SWEET_CASE.get());
            }
            for(int x:new int[]{3,21})for(int z:new int[]{5,11,17})p.put(x,1,z,Furniture.SWEET_CART.get());
            for(int x=3;x<=21;x+=3){
                p.put(x,1,20,Blocks.FURNACE.defaultBlockState().setValue(FurnaceBlock.FACING,Direction.NORTH));
                p.put(x,2,20,Blocks.SMOKER.defaultBlockState().setValue(SmokerBlock.FACING,Direction.NORTH));
                p.put(x,3,20,Furniture.SWEET_SHELF.get());
            }
            for(int x:new int[]{4,8,16,20}){p.put(x,1,19,Furniture.SWEET_COUNTER.get());p.put(x,2,19,Furniture.SWEET_CASE.get());}
            for(int x:new int[]{6,10,14,18})p.put(x,4,21,Furniture.SWEET_ART.get());
            for(int z:new int[]{6,12,18}){royalFacing(p,1,4,z,Furniture.SWEET_ART.get(),Direction.EAST);royalFacing(p,23,4,z,Furniture.SWEET_ART.get(),Direction.WEST);}
            for(int x:new int[]{2,22})for(int z:new int[]{8,15}){p.put(x,1,z,Furniture.SWEET_TABLE.get());p.put(x,2,z,Blocks.POTTED_POPPY);}
            p.put(3,1,18,Blocks.CRAFTING_TABLE);p.put(21,1,18,Furniture.FRIDGE.get());
        }
'''+s[b:]
a='BlockPos q=pos(i==0?4:6,1,8);guest.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+180,0);'
assert a in s
s=s.replace(a,'BlockPos q=pos(i==0?4:6,2,8);guest.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,forward.toYRot()+(i==0?-90:90),0);',1)
f.write_text(s,encoding='utf-8')
# Pose is derived from the actual custom seat on both logical sides; standalone spawn eggs are unaffected.
edit('CrossoverGuest.java','public void setHome(BlockPos p){home=p;}','''public void setHome(BlockPos p){home=p;}
    public boolean pastrySeated(){return kind()!=0&&level().getBlockState(blockPosition().below()).is(Furniture.SWEET_CHAIR.get());}
''')
# Phoenix's mesh and Miles' independent articulated renderer.
edit('CrossoverClient.java','ModelPart arm=r.getChild("arm1");','''if(e.pastrySeated()){for(int i=0;i<2;i++)r.getChild("leg"+i).xRot=-1.35f;}
            ModelPart arm=r.getChild("arm1");''')
a='@Override public ResourceLocation getTextureLocation(CrossoverGuest e)'
edit('CrossoverClient.java',a,'''@Override protected void scale(CrossoverGuest e,com.mojang.blaze3d.vertex.PoseStack p,float partial){super.scale(e,p,partial);if(e.pastrySeated())p.translate(0,-1.02,0);}
        '''+a)
edit('EdgeworthSculptedClient.java','   // Opposite arm points','''   if(e.pastrySeated())for(int i=0;i<2;i++){legs[i].rx=-1.45f;shins[i].rx=1.45f;}
   // Opposite arm points''')
# Preserve any pre-existing renderer scaling.
f=java/'EdgeworthSculptedClient.java';s=f.read_text(encoding='utf-8');a='p.scale(1.08f,1.10f,1.08f);';assert a in s
s=s.replace(a,a+'if(e.pastrySeated())p.translate(0,-.94,0);',1);f.write_text(s,encoding='utf-8')
# Add visible sculpted hair and a small projecting moustache, with no political insignia.
f=java/'BakeryClient.java';s=f.read_text(encoding='utf-8')
a='        r.getChild("body").addOrReplaceChild("apron"'
assert a in s
s=s.replace(a,'''        r.getChild("head").addOrReplaceChild("sidepart",CubeListBuilder.create().texOffs(0,0).addBox(-4.2f,-8.7f,-4.2f,8.4f,1.7f,8.4f).texOffs(0,0).addBox(-4.2f,-7.9f,-4.3f,5.6f,1.8f,1.3f).texOffs(0,0).addBox(1.3f,-8.0f,-4.3f,2.7f,1.1f,1.2f),PartPose.ZERO);
        r.getChild("head").addOrReplaceChild("shortmoustache",CubeListBuilder.create().texOffs(0,0).addBox(-1.1f,-2.8f,-4.65f,2.2f,.85f,.75f),PartPose.ZERO);
'''+a,1)
a='            super.setupAnim(e,limb,amount,age,yaw,pitch);';assert a in s
s=s.replace(a,a+'''
            head.getChild("sidepart").visible=!e.stalin();
            head.getChild("shortmoustache").visible=!e.stalin();
            head.getChild("chefhat").visible=e.stalin();
''',1);f.write_text(s,encoding='utf-8')
print('Patisserie: ten furniture types, seven craftable desserts, baked dough, seated lawyer poses, sculpted baker hair and moustache.')
