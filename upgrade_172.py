"""1.7.2: Code Geass portraits and a working range of oven-baked bread."""
from pathlib import Path
import sys,json,math,struct,zlib,re
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
 p.parent.mkdir(parents=True,exist_ok=True)
 def ch(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+ch(b'IEND',b''))
def sat(v):return max(0,min(1,v))
def mix(a,b,t):return tuple(int(x+(y-x)*sat(t)) for x,y in zip(a,b))
def shade(a,t):return tuple(max(0,min(255,int(x*t))) for x in a)
# Same reliable 128x128 material atlas layout, with expressive painted portraits.
for cc in (False,True):
 W,H=1024,512;pix=bytearray(W*H*4)
 pal=[(30,34,81),(122,26,54),(24,24,43),(224,225,248),(219,172,54),(111,22,46),(239,191,157),(239,191,157),(102,164,54) if cc else (26,24,39),(177,190,213),(157,168,204),(45,92,43) if cc else (26,27,54),(43,49,105) if not cc else (51,54,80),(57,33,45),(170,101,92),(183,224,100) if cc else (77,70,105)]
 for tile,base in enumerate(pal):
  for y in range(128):
   v=sat((y-3)/121)
   for x in range(128):
    u=sat((x-3)/121);f=abs(u-.5)
    c=shade(base,.84+.16*math.sin(math.pi*u)+.035*math.sin(u*47+v*19)**2)
    if tile in (0,2,5,12):
     wave=math.sin(u*math.pi*5+v*4+math.sin(v*8)*.3)
     c=mix(c,(95,100,173) if tile!=5 else (194,59,91),.27*max(0,wave)**5)
     c=mix(c,(12,14,31) if tile!=5 else (48,10,24),.29*max(0,-wave)**5)
    if tile==4:c=mix(c,(255,233,137),.40*math.sin(math.pi*u)**2)
    if tile in (8,15) or tile==11 and cc:
     wave=math.sin(u*math.pi*30+v*5+.4*math.sin(v*7))
     c=mix(c,(213,244,125) if cc else (95,89,135),.38*max(0,wave)**6+.11*math.exp(-((v-.34)/.18)**2))
     c=mix(c,(36,82,37) if cc else (11,12,23),.36*max(0,-wave)**6)
    if tile==6:
     # Eyes are on the broad, front-facing plane, not a wrapped sphere.
     c=mix(base,(155,87,82),.28*sat((f-.24)*4)+.09*v)
     c=mix(c,(255,225,197),.30*math.exp(-((u-.50)/.16)**2-((v-.48)/.33)**2))
     for side in (-1,1):
      ex=.5+side*.17;dx=side*(u-ex)/(.139 if cc else .133)
      dy=(v-(.47-.043*dx))/(.069 if cc else .059)
      d=abs(dx)**1.55+abs(dy)**1.35
      if d<1.19:c=(39,26,38)
      if d<.84:c=(250,242,231)
      if d<.82 and abs(dx+.03)<.46:
       light=(235,186,61) if cc else (213,94,234) if side<0 else (240,67,125)
       dark=(101,63,25) if cc else (71,32,119) if side<0 else (105,22,65)
       c=mix(dark,light,sat((dy+.60)/1.3))
       if abs(dx+.03)<.17:c=(29,17,33)
       if (dx+.20)**2+(dy+.25)**2<.057:c=(255,250,241)
      if abs(dx)<1.1 and abs(v-(.351-.041*dx))<.014:c=(56,89,38) if cc else (30,25,42)
      if cc and .7<dx<1.15 and abs(v-(.427-.04*dx))<.014:c=(34,22,35)
     if f<.034 and abs(v-.665)<.012:c=(165,97,84)
     if f<.083 and abs(v-(.78-.016*(1-f/.083)+.019*(u-.5)))<.009:c=(116,50,60)
     if f<.050 and abs(v-.807)<.008:c=(221,140,125)
    o=((tile//8*128+y)*W+tile%8*128+x)*4;pix[o:o+4]=bytes((*c,255))
 png(assets/'textures/entity'/('cc_sculpted.png' if cc else 'lelouch_sculpted.png'),W,H,pix)
# Rebuild both heads together, using the known flat-front portrait helper for both.
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('            // Separate head silhouette');b=s.index('                arms[i]=root.child(',a)
s=s[:a]+'''            // Chamfered voxel faces, full hair cap and a clear eye line.
            float w=cc?3.08f:3.02f;
            VoxelPortrait.head(head,6,7,6.3f,7.8f,
                -7.8f,2.35f,2.10f,.08f,.28f,
                -7.12f,2.90f,2.48f,.04f,.32f,
                -5.3f,w,2.58f,0,.35f,
                -3.5f,cc?2.85f:2.78f,2.44f,-.04f,.36f,
                -1.65f,cc?2.35f:2.24f,2.05f,-.16f,.44f,
                -.40f,cc?1.70f:1.58f,1.55f,-.22f,.40f,
                0,1.12f,1.16f,-.25f,.32f);
            head.loft(7,8,-4.05f,0,-2.43f,.10f,.07f,-3.35f,0,-2.55f,.19f,.13f,-2.87f,0,-2.70f,.26f,.17f,-2.60f,0,-2.47f,.17f,.08f);
            head.loft(7,8,-.45f,0,.04f,.80f,.83f,.65f,0,.04f,1.04f,1.02f,1.50f,0,.04f,1.14f,1.04f);
            for(int side:new int[]{-1,1})head.oval(7,side*2.83f,-3.9f,.04f,.27f,.63f,.37f);
            // Crown and rear hair: no exposed skin on the back of the head.
            head.loft(8,16,-8.65f,0,.08f,1.35f,1.45f,-8.10f,0,.10f,2.85f,2.62f,-7.30f,0,.16f,3.24f,2.86f,-6.10f,0,.22f,3.30f,2.88f);
            Part cap=head.child(0,-7.05f,1.65f);
            cap.loft(8,16,-.65f,0,0,2.74f,1.30f,1.15f,0,.46f,3.0f,1.43f,3.30f,0,.48f,2.80f,1.45f,5.35f,0,.30f,2.29f,1.25f,cc?7.9f:6.45f,0,.10f,1.70f,.62f);
            // Forehead strands are shorter at the eyes; long asymmetric central lock for Zero.
            for(int j=0;j<11;j++){
                float t=j/10f,dx=cc?(t-.5f)*.80f:-.95f+t*.52f;
                Part q=head.child(-2.62f+t*5.24f,-7.95f,-2.03f);
                float len=cc?1.62f+1.18f*(float)Math.sin(t*Math.PI):1.46f+1.32f*(float)Math.sin(t*Math.PI);
                if(!cc&&j==6)len=3.70f;
                q.loft(8,8,-.38f,0,.48f,.51f,.45f,.5f,dx*.24f,-.19f,.52f,.36f,len*.68f,dx*.63f,-.44f,.34f,.22f,len,dx,-.28f,.035f,.04f);
                q.blade(15,-.12f,.17f,-.43f,dx*.77f,len*.80f,-.46f,.105f);
            }
            for(int j=0;j<9;j++){
                float t=j/8f;
                Part q=head.child(-2.55f+t*5.1f,-8.32f,.18f);
                float dx=cc?(t-.5f)*.7f:-.72f+t*.45f;
                q.loft(8,8,-.40f,0,.15f,.45f,.52f,.55f,0,-.17f,.55f,.59f,1.40f,dx*.5f,-.52f,.41f,.35f,2.15f,dx,-.86f,.045f,.045f);
            }
            if(cc)for(int j=0;j<13;j++){
                float t=j/12f,spread=(t-.5f)*5.7f;
                Part q=head.child(-2.85f+t*5.7f,-6.55f,2.15f);hair.add(q);
                float len=21.8f+2.6f*(float)Math.sin(t*Math.PI);
                q.loft(j%4==0?11:8,10,0,0,0,.52f,.55f,3,spread*.15f,.3f,.62f,.63f,9,spread*.36f,.80f,.67f,.57f,16,spread*.70f,1.5f,.62f,.41f,len,spread,2.10f,.05f,.06f);
                q.blade(15,0,1,-.55f,spread*.8f,len*.87f,1.41f,.13f);
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                for(int j=0;j<3;j++){
                    Part lock=head.child(s*(2.62f+j*.13f),-6.9f+j*.27f,-.62f+j*.52f);hair.add(lock);
                    float len=cc?16.4f+j*1.35f:4.8f+j*.36f;
                    lock.loft(8,8,-.35f,0,.10f,.47f,.49f,1.0f,s*.25f,-.21f,.55f,.55f,len*.42f,s*.37f,-.27f,.48f,.39f,len*.78f,s*(cc?1f:.29f),.10f,.31f,.23f,len,s*(cc?1.25f:.19f),.32f,.035f,.045f);
                }
'''+s[b:]
s=s.replace('if(cc)AngularHeads.apply(head,6,.85f,.98f,.94f,.16f);','',1)
# A dark outer cape with red inner lining and gold border; original animation is unchanged.
a='else c.loft(5,36,0,0,0,2.4f,.22f,len*.24f,s*.50f,.65f,3.15f,.28f,len*.54f,s*1.15f,1.55f,3.6f,.37f,len*.80f,s*1.65f,2.4f,3.65f,.32f,len,s*1.8f,3.0f,2.9f,.13f);'
if a in s:
 s=s.replace(a,'''else{
                    c.loft(0,16,0,0,.13f,2.4f,.24f,len*.24f,s*.50f,.78f,3.15f,.28f,len*.54f,s*1.15f,1.68f,3.6f,.37f,len*.80f,s*1.65f,2.53f,3.65f,.32f,len,s*1.8f,3.13f,2.9f,.13f);
                    c.loft(5,16,0,0,-.13f,2.37f,.09f,len*.24f,s*.50f,.37f,3.12f,.10f,len*.54f,s*1.15f,1.16f,3.56f,.10f,len*.80f,s*1.65f,2.01f,3.60f,.10f,len,s*1.8f,2.73f,2.85f,.06f);
                }''',1)
p.write_text(s,encoding='utf-8')
# Six actual baked breads, each with a raw dough recipe and two cooking recipes.
breads={
 'baguette':('Baguette','Baguette',6,['wheat','wheat','wheat'],(202,144,70),'long'),
 'focaccia':('Focaccia alle erbe','Herb focaccia',7,['wheat','wheat','beetroot_seeds'],(221,164,76),'flat'),
 'seeded_loaf':('Pane ai semi','Seeded bread',7,['wheat','pumpkin_seeds','wheat_seeds'],(157,99,53),'loaf'),
 'potato_bread':('Pane alle patate','Potato bread',7,['wheat','potato','wheat'],(222,170,93),'round'),
 'milk_roll':('Panino al latte','Milk roll',5,['wheat','milk_bucket','sugar'],(235,177,96),'round'),
 'dark_rye_style':('Pane nero ai cereali','Dark grain bread',7,['wheat','beetroot','wheat'],(105,68,44),'loaf')
}
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='public static final RegistryObject<Item> CATHEDRAL_EGG=';assert a in s
decl=''
for n,(it,en,nut,ings,col,shape) in breads.items():
 decl+=f'public static final RegistryObject<Item> BREAD_{n.upper()}=ITEMS.register("{n}",()->new Item(new Item.Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition({nut}).saturationMod(.7f).build())));\n    public static final RegistryObject<Item> DOUGH_{n.upper()}=ITEMS.register("{n}_dough",()->new Item(new Item.Properties()));\n    '
s=s.replace(a,decl+a,1);a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s
s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS){'+''.join(f'e.accept(BREAD_{n.upper()}.get());e.accept(DOUGH_{n.upper()}.get());' for n in breads)+'}'+a,1);p.write_text(s,encoding='utf-8')
for n,(it,en,nut,ings,col,shape) in breads.items():
 for dough in (False,True):
  name=n+('_dough' if dough else '');pix=bytearray()
  for y in range(32):
   for x in range(32):
    dx=x-15.5;dy=y-15.5
    if shape=='long':u=(dx+dy)*.707;v=(dy-dx)*.707;inside=(u/19)**2+(v/5.9)**2<1
    elif shape=='flat':u=dx;v=dy;inside=abs(dx)<13 and abs(dy)<8 and abs(dx)+abs(dy)<19
    elif shape=='round':u=dx;v=dy;inside=(dx/11)**2+(dy/10)**2<1
    else:u=dx;v=dy;inside=(dx/12)**2+(dy/10)**2<1
    if not inside:pix.extend((0,0,0,0));continue
    base=(225,208,174) if dough else col
    c=shade(base,.84+.22*math.exp(-((v+3)/5)**2)+.05*math.sin(x*2+y*3))
    if not dough:
     if shape in ('long','loaf') and abs((u+v*.45+20)%8-4)<.8 and abs(v)<4:c=mix(c,(247,207,144),.67)
     if n in ('seeded_loaf','focaccia') and (x*13+y*7)%19==0:c=(76,108,43) if n=='focaccia' else (244,224,167)
     if shape=='round' and (dx/8)**2+((dy+1)/7)**2>.95:c=shade(c,.81)
    pix.extend((*c,255))
  png(assets/'textures/item'/f'{name}.png',32,32,pix)
  dump(assets/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/'+name}})
 dump(res/'data/noctismagic/recipes'/f'{n}_dough.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'minecraft:'+x} for x in ings],'result':{'item':'noctismagic:'+n+'_dough','count':2}})
 for kind,t in [('smelting',200),('smoking',100)]:
  dump(res/'data/noctismagic/recipes'/f'{n}_{kind}.json',{'type':'minecraft:'+kind,'ingredient':{'item':'noctismagic:'+n+'_dough'},'result':'noctismagic:'+n,'experience':.35,'cookingtime':t})
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,nut,ings,col,shape) in breads.items():
  d['item.noctismagic.'+n]=it if loc=='it_it' else en
  d['item.noctismagic.'+n+'_dough']=('Impasto: '+it) if loc=='it_it' else (en+' dough')
 dump(p,d)
print('Code Geass: rebuilt both faces and full rear hair caps, sharp eyes and Zero colors; six breads with raw dough and oven recipes.')
