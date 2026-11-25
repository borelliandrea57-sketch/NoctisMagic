"""1.7.15: compact character portraits and Japanese Jade Cat exterior."""
from pathlib import Path
import sys,math,json,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
# Rebuild the three portraits, preserving outfits, AI and affection animations.
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('            // Chamfered voxel faces');b=s.index('                arms[i]=root.child(',a)
s=s[:a]+'''            int first=head.faces.size();
            head.loft(6,16,-6.95f,0,.17f,1.75f,1.68f,-6.47f,0,.11f,2.65f,2.32f,
                -5.53f,0,.02f,3.01f,2.61f,-4.35f,0,-.06f,cc?3.05f:2.99f,2.60f,
                -3.10f,0,-.15f,cc?2.86f:2.80f,2.49f,-1.85f,0,-.24f,2.39f,2.22f,
                -.72f,0,-.32f,1.62f,1.58f,0,0,-.35f,1.03f,1.02f);
            for(int j=first;j<head.faces.size();j++){
                Q q=head.faces.get(j);boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.08f;
                head.faces.set(j,new Q(shortFace(q.a(),f),shortFace(q.b(),f),shortFace(q.c(),f),shortFace(q.d(),f),f?6:7));
            }
            head.loft(7,8,-3.63f,0,-2.53f,.10f,.07f,-2.94f,0,-2.66f,.19f,.14f,-2.49f,0,-2.79f,.27f,.19f,-2.30f,0,-2.53f,.15f,.09f);
            head.loft(7,8,-.55f,0,.06f,.81f,.80f,.45f,0,.06f,.96f,.96f,1.45f,0,.06f,1.15f,1.10f);
            head.loft(8,12,-8.25f,cc?-.25f:-.45f,.28f,.55f,.60f,-7.92f,0,.22f,1.87f,1.75f,
                -7.30f,0,.18f,2.90f,2.58f,-6.55f,0,.24f,3.28f,2.92f,-5.95f,0,.33f,3.17f,2.80f);
            Part cap=head.child(0,-6.55f,1.59f);
            cap.loft(8,12,-.70f,0,0,2.64f,1.30f,1.12f,0,.48f,2.97f,1.46f,
                3.1f,0,.55f,2.76f,1.38f,5.2f,0,.35f,2.10f,1.12f,cc?6.9f:5.8f,0,.12f,1.34f,.40f);
            for(int j=0;j<8;j++){
                float t=j/7f,x=-2.64f+t*5.28f;Part q=head.child(x,-7.15f,-2.18f);
                float dx=cc?(.55f-t*1.08f):(-.92f+t*.38f);
                float len=cc?1.26f+1.05f*(float)Math.sin(t*Math.PI):1.40f+1.05f*(float)Math.sin(t*Math.PI)+(j%3)*.15f;
                if(!cc&&j==5)len=2.92f;
                q.loft(8,6,-.35f,0,.35f,.50f,.46f,.3f,dx*.17f,-.46f,.65f,.40f,len*.65f,dx*.64f,-.61f,.37f,.24f,len,dx,-.45f,.025f,.04f);
            }
            if(cc)for(int j=0;j<13;j++){
                float t=j/12f,spread=(t-.5f)*5.3f;Part q=head.child(-2.78f+t*5.56f,-6.15f,2.05f);hair.add(q);
                float len=21.0f+2.7f*(float)Math.sin(t*Math.PI)+(j%3)*.35f;
                q.loft(j%5==0?11:8,8,-.25f,0,0,.44f,.52f,3,spread*.16f,.33f,.61f,.62f,9,spread*.35f,.90f,.68f,.53f,16,spread*.68f,1.42f,.59f,.36f,len,spread,1.90f,.04f,.05f);
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                for(int j=0;j<(cc?4:3);j++){
                    Part lock=head.child(s*(3.03f+j*.10f),-6.22f+j*.30f,.15f+j*.44f);hair.add(lock);
                    float len=cc?15.6f+j*1.4f:3.9f+j*.52f;
                    lock.loft(8,8,-.25f,0,.13f,.42f,.55f,1.0f,s*.37f,-.13f,.56f,.55f,len*.44f,s*.50f,.02f,.48f,.39f,len*.76f,s*(cc?.83f:.28f),.23f,.30f,.22f,len,s*(cc?1.1f:.10f),.50f,.035f,.045f);
                }
'''+s[b:]
a='        M(boolean cc){';assert a in s
s=s.replace(a,'''        static V shortFace(V v,boolean f){
            return new V(v.x(),v.y(),v.z(),f?Math.max(.025f,Math.min(.975f,.5f+v.x()/6.6f)):.025f,Math.max(.025f,Math.min(.975f,(v.y()+6.95f)/6.95f)),v.nx(),v.ny(),v.nz());
        }
'''+a,1)
p.write_text(s,encoding='utf-8')
p=java/'SculptedGuestsClient.java';s=p.read_text(encoding='utf-8')
a=s.index('}else if(gem){\n                    VoxelPortrait.head(head,face,17,');b=s.index('}else head.loft(face,24,',a)
s=s[:a]+'''}else if(k==2){
                    int first=head.faces.size();
                    head.loft(14,16,-6.72f,0,.20f,1.65f,1.62f,-6.22f,0,.11f,2.60f,2.30f,-5.26f,0,.02f,2.94f,2.56f,-4.03f,0,-.06f,2.98f,2.60f,-2.80f,0,-.18f,2.72f,2.40f,-1.57f,0,-.28f,2.21f,2.01f,-.48f,0,-.38f,1.45f,1.40f,0,0,-.39f,.90f,.88f);
                    for(int j=first;j<head.faces.size();j++){
                        Q q=head.faces.get(j);boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.08f;
                        head.faces.set(j,new Q(phosFace(q.a(),f),phosFace(q.b(),f),phosFace(q.c(),f),phosFace(q.d(),f),f?14:17));
                    }
                    head.loft(17,8,-3.55f,0,-2.52f,.10f,.08f,-2.80f,0,-2.65f,.19f,.15f,-2.35f,0,-2.72f,.25f,.17f,-2.16f,0,-2.48f,.16f,.08f);
                    head.loft(17,8,-.42f,0,.08f,.80f,.83f,.7f,0,.08f,1.07f,1.0f);
                '''+s[b:]
a='        static V cinnabarFace(V v,boolean front){';assert a in s
s=s.replace(a,'''        static V phosFace(V v,boolean f){
            return new V(v.x(),v.y(),v.z(),f?Math.max(.025f,Math.min(.975f,.5f+v.x()/6.5f)):.025f,Math.max(.025f,Math.min(.975f,(v.y()+6.72f)/6.72f)),v.nx(),v.ny(),v.nz());
        }
'''+a,1)
a=s.index('int h=k==0?3:k==2?12:13;');b=s.index('if(k==3){',a)
s=s[:b]+'''if(k==2){
                    head.loft(12,10,-8.05f,-.52f,.22f,.64f,.60f,-7.74f,-.30f,.20f,1.92f,1.72f,-7.10f,0,.21f,2.80f,2.52f,-6.18f,0,.30f,3.21f,2.81f);
                    for(int j=0;j<8;j++){
                        float x=-2.50f+j*.70f,drift=-.6f+j*.15f;Part q=head.child(x,-7.10f,-2.12f);
                        float len=1.45f+(j%3)*.29f+(j==3?.68f:0);
                        q.loft(12,5,-.25f,0,.32f,.40f,.42f,.31f,drift*.22f,-.43f,.60f,.43f,len*.64f,drift*.63f,-.58f,.33f,.24f,len,drift,-.42f,.035f,.045f);
                    }
                    for(int j=0;j<9;j++){
                        float x=(j-4)*.60f;Part q=head.child(x,-6.75f,1.93f);hair.add(q);float len=5.3f+(j%3)*.55f;
                        q.loft(12,5,-.35f,0,.0f,.48f,.60f,1.1f,(j-4)*.08f,.42f,.70f,.72f,3.55f,(j-4)*.14f,.78f,.63f,.47f,len,(j-4)*.18f,.65f,.04f,.06f);
                    }
                    for(int side:new int[]{-1,1})for(int j=0;j<3;j++){
                        Part q=head.child(side*(2.95f+j*.15f),-6.32f+j*.38f,.0f+j*.50f);hair.add(q);
                        q.loft(12,5,-.26f,0,.05f,.40f,.55f,1.1f,side*.30f,-.04f,.60f,.69f,3.1f,side*.51f,.15f,.55f,.44f,5.6f+j*.22f,side*.22f,.29f,.04f,.045f);
                    }
                }else '''+s[b:]
p.write_text(s,encoding='utf-8')
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def face(u,v,name,expr):
 f=abs(u-.5);skin=(245,224,203) if name=='phos' else (245,210,186) if name=='cc' else (240,207,186)
 c=mix(skin,(157,113,110),.16*min(1,f*2.2)+.035*v)
 def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
 c=mix(c,(255,238,218),.24*g(.5,.43,.17,.30))
 for side in (-1,1):
  ex=.5+side*.181;dx=side*(u-ex)/(.127 if name=='lelouch' else .135)
  ey=.485-(.008 if name=='cc' else .019 if name=='lelouch' else -.008)*dx
  dy=(v-ey)/(.067 if name=='lelouch' else .088 if name=='cc' else .094)
  if expr:
   if abs(dx)<1.01 and abs(v-(ey-.035*(1-dx*dx)))<.011:c=(48,29,42)
   c=mix(c,(215,115,125),.22*g(ex,.63,.10,.07))
  else:
   d=abs(dx)**1.8+abs(dy)**1.7
   if d<1.08:c=(47,29,43)
   if d<.89:c=(249,242,234)
   if d<.86 and abs(dx+.04)<.52:
    dark,light=((92,57,19),(244,191,64)) if name=='cc' else ((62,29,103),(181,105,226)) if name=='lelouch' else ((23,85,85),(100,230,207))
    c=mix(dark,light,(dy+.8)/1.6)
    if abs(dx+.04)<.16:c=(29,22,38)
    if (dx+.17)**2+(dy+.28)**2<.052:c=(255,251,241)
   if abs(dx)<1.02 and abs(v-(ey-.060+.018*dx*dx))<.009:c=(41,27,41)
  brow=(47,33,48) if name=='lelouch' else (70,111,42) if name=='cc' else (42,119,105)
  if abs(dx)<.93 and abs(v-(.352+.018*dx-.013*dx*dx))<.011:c=brow
 c=mix(c,(166,104,104),.28*g(.5,.665,.038,.018))
 mouth=.775+(.022 if expr else .004)*(1-min(1,f/.10))
 if f<.10 and abs(v-mouth)<.009:c=(127,68,79)
 return c
def paint(p,tile,name,expr=''):
 im=Image.open(p).convert('RGBA')
 for y in range(128):
  for x in range(128):im.putpixel((tile%8*128+x,tile//8*128+y),(*face((x-3)/121,(y-3)/121,name,expr),255))
 if name=='phos':
  for y in range(128):
   for x in range(128):
    u=x/127;v=y/127;t=(u*8+v*1.4)%1
    c=mix((38,132,120),(152,248,212),.32+.40*t+.12*math.sin(v*6)**2)
    c=mix(c,(222,255,236),.26*math.exp(-((t-.18)/.055)**2))
    im.putpixel((512+x,128+y),(*c,255))
 im.save(p)
for name in ('cc','lelouch'):
 for suffix in ('','_soft','_happy'):paint(assets/'textures/entity'/f'{name}_sculpted{suffix}.png',6,name,suffix)
paint(assets/'textures/entity/sculpted_guests.png',14,'phos')
# Japanese exterior: original tile, lattice, fabric, carved eaves and sign models.
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
pal={'kawara':(53,64,78),'cedar':(105,57,34),'paper':(235,217,177),'indigo':(35,60,100),'red':(160,42,37),'gold':(204,163,82),'stone':(111,115,109),'sign':(92,50,30)}
for name,base in pal.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(name)
 for y in range(64):
  for x in range(64):
   v=.86+.11*rng.random()
   if name=='kawara':v*=.69+.38*math.sin(math.pi*(x%16)/16)**2
   if name=='cedar':v*=.84+.22*math.sin(x*.54+math.sin(y*.11))**2
   if name in ('indigo','red'):v*=.89+.14*math.sin(x*.19)**2
   im.putpixel((x,y),(*[min(255,int(c*v)) for c in base],255))
 d=ImageDraw.Draw(im)
 if name=='sign':
  d.rectangle((2,2,61,61),outline=(214,174,89),width=2)
  d.text((12,11),'JADE',fill=(245,218,158));d.text((14,28),'CAT',fill=(245,218,158));d.text((8,45),'SUSHI',fill=(245,218,158))
 if name=='indigo':
  d.line((2,2,2,61),fill=(168,185,214),width=1);d.line((61,2,61,61),fill=(168,185,214),width=1)
  for cy in (48,54,60):
   for cx in range(-4,69,13):d.arc((cx-9,cy-9,cx+9,cy+9),180,360,fill=(180,194,211),width=1)
 p=assets/'textures/block'/f'jade_ext_{name}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
shoji=[B(0,0,7,16,16,8,'paper')]+[B(x,0,6,x+1,16,9,'cedar') for x in (0,5,10,15)]+[B(0,y,6,16,y+1,9,'cedar') for y in (0,5,10,15)]
noren=[B(0,14,5,16,16,8,'cedar'),B(1,2,6,7.7,14,7.5,'indigo'),B(8.3,1,6,15,14,7.5,'indigo')]
tile=[B(0,0,0,16,3,16,'kawara')]+[B(x,3,0,x+3,5,16,'kawara') for x in (0,4,8,12)]
eave=[B(0,10,0,16,15,16,'cedar'),B(1,7,1,15,10,15,'cedar'),B(3,4,3,13,7,13,'cedar'),B(5,1,5,11,4,11,'gold')]
lamp=[B(5,0,5,11,2,11,'cedar'),B(3,2,3,13,5,13,'red'),B(2,5,2,14,11,14,'red'),B(3,11,3,13,14,13,'red'),B(5,14,5,11,16,11,'cedar')]
for y in (4,7,10,12):
 lamp += [B(2,y,1.8,14,y+.5,2.2,'gold'),B(1.8,y,2,2.2,y+.5,14,'gold'),B(13.8,y,2,14.2,y+.5,14,'gold'),B(2,y,13.8,14,y+.5,14.2,'gold')]
stone=[B(2,0,2,14,3,14,'stone'),B(6,3,6,10,9,10,'stone'),B(3,9,3,13,11,13,'stone'),B(5,11,5,11,15,11,'paper'),B(2,15,2,14,16,14,'stone')]
sign=[B(0,1,10,16,15,14,'cedar'),B(1,2,9,15,14,10,'sign'),B(0,0,9,16,1,14,'gold'),B(0,15,9,16,16,14,'gold')]
items={'jade_ext_shoji':('Pannello shoji',0,shoji),'jade_ext_noren':('Tendina noren',0,noren),'jade_ext_kawara':('Tegole kawara',0,tile),'jade_ext_eave':('Mensola giapponese scolpita',0,eave),'jade_ext_chochin':('Lanterna chochin',3,lamp),'jade_ext_toro':('Lanterna di pietra toro',3,stone),'jade_ext_sign':('Insegna Gatto di Giada',0,sign)}
decl=[]
for n,(it,k,boxes) in items.items():
 decl += [f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->new FurnitureBlock({k}));',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));']
 tx={m:'noctismagic:block/jade_ext_'+m for m in pal};tx['particle']=tx['cedar']
 model={'textures':tx,'elements':[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
 dump(assets/'blockstates'/f'{n}.json',{'variants':{f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s;s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1);p.write_text(s,encoding='utf-8')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s;s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a,1);p.write_text(s,encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,k,boxes) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else n.removeprefix('jade_ext_').replace('_',' ').title()
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static Plan sushiRestaurant(){');b=s.index('        return p;',a)
# Refine the existing plan without deleting interior fittings or resident spawn hooks.
s=s[:b]+'''        // Traditional Japanese street frontage and covered veranda.
        for(int x=2;x<=26;x++)for(int z=2;z<=3;z++)p.put(x,0,z,Blocks.STRIPPED_SPRUCE_WOOD);
        for(int x:new int[]{2,7,11,17,21,26}){
            p.box(x,1,2,x,5,2,Blocks.STRIPPED_DARK_OAK_LOG);
            p.put(x,5,2,Furniture.JADE_EXT_EAVE.get());
            p.put(x,1,1,Furniture.JADE_EXT_TORO.get());
        }
        for(int x=2;x<=26;x++){
            p.put(x,6,2,Blocks.DARK_OAK_LOG);
            p.put(x,7,1,Furniture.JADE_EXT_KAWARA.get());
            p.put(x,7,2,Furniture.JADE_EXT_KAWARA.get());
            if(x<11||x>17)for(int y=2;y<=4;y++)p.put(x,y,4,Furniture.JADE_EXT_SHOJI.get());
            if(x>=12&&x<=15)p.put(x,4,3,Furniture.JADE_EXT_NOREN.get());
            if(x%4==2&&x!=14){p.put(x,5,1,Blocks.CHAIN);p.put(x,4,1,Furniture.JADE_EXT_CHOCHIN.get());}
        }
        p.put(14,6,1,Furniture.JADE_EXT_SIGN.get());
        for(int x:new int[]{11,17}){p.put(x,4,1,Furniture.JADE_EXT_CHOCHIN.get());p.put(x,3,1,Blocks.DARK_OAK_FENCE);}
        // Kawara roof ribs, projecting eaves and raised corners.
        for(int h=0;h<5;h++){
            int y=8+h,l=h,r=28-h,n=3+h,f=24-h;
            for(int x=l;x<=r;x++){
                p.put(x,y,n,Furniture.JADE_EXT_KAWARA.get());
                jadeFacing(p,x,y,f,Furniture.JADE_EXT_KAWARA.get(),Direction.SOUTH);
            }
            for(int z=n+1;z<f;z++){
                jadeFacing(p,l,y,z,Furniture.JADE_EXT_KAWARA.get(),Direction.WEST);
                jadeFacing(p,r,y,z,Furniture.JADE_EXT_KAWARA.get(),Direction.EAST);
            }
            for(int x:new int[]{l,r})for(int z:new int[]{n,f})p.put(x,y+1,z,Blocks.DEEPSLATE_TILE_WALL);
        }
        for(int z=9;z<=18;z++)p.put(14,13,z,Blocks.DEEPSLATE_TILE_WALL);
        // Side lattice windows and wooden brackets.
        for(int z=6;z<=21;z++)for(int x:new int[]{1,27}){
            if(z%5!=4)for(int y=2;y<=4;y++)jadeFacing(p,x,y,z,Furniture.JADE_EXT_SHOJI.get(),x==1?Direction.WEST:Direction.EAST);
            if(z%4==0)p.put(x,6,z,Furniture.JADE_EXT_EAVE.get());
        }
        // Low stone garden lanterns, stepping stones and plants along the entrance.
        for(int x:new int[]{3,5,23,25}){
            p.put(x,0,0,Blocks.MOSS_BLOCK);p.put(x,1,0,Blocks.POTTED_CHERRY_SAPLING);
            p.put(x,0,1,Blocks.MOSSY_COBBLESTONE);
        }
        for(int z=0;z<=1;z++)for(int x=12;x<=16;x++)p.put(x,0,z,Blocks.POLISHED_ANDESITE);
        for(int x:new int[]{9,19})p.put(x,1,0,Furniture.JADE_EXT_TORO.get());
'''+s[b:]
p.write_text(s,encoding='utf-8')
print('Three compact portraits; Japanese restaurant exterior with seven new decorative blocks, tiled eaves, shoji, noren, lanterns and signage.')
