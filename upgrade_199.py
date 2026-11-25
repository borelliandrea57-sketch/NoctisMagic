"""1.7.34: cathedral mechanism, sacred music, arcane HUD and expressive idle poses."""
from pathlib import Path
import sys,math,json,wave,struct,subprocess,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
def edit(file,fn):
 p=java/file;s=p.read_text(encoding='utf-8');p.write_text(fn(s),encoding='utf-8')
def B(x,y,z,X,Y,Z,m):return (x,y,z,X,Y,Z,m)
# Rich architectural surfaces and coherent reliefs.
colors={'limestone':(183,172,153),'bronze':(135,104,57),'gold':(222,183,95),'iron':(62,61,69),'marble':(234,230,219),'dark':(76,69,68),'ivory':(245,235,206),'red':(108,30,41),'pipe':(179,165,125)}
for n,c in colors.items():
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   t=.94+.06*math.sin(x*.12+y*.09)+rng.uniform(-.022,.022)
   if n in ('bronze','gold','pipe'):t=.76+.25*math.sin(math.pi*x/64)**2
   if n=='marble':t-=.09*max(0,math.sin(x*.13+y*.17+2*math.sin(y*.10)))**12
   im.putpixel((x,y),(*[max(0,min(255,round(v*t))) for v in c],255))
 im.save(assets/'textures/block'/f'lacra_{n}.png')
# Smooth halo texture with no grain.
Image.new('RGBA',(64,64),(255,239,179,255)).save(assets/'textures/block/sanctuary_halo.png')
items={}
def add(n,it,en,boxes,expr='new FurnitureBlock(0)'):items[n]=(it,en,boxes,expr)
add('lacra_portal_pillar','Pilastro del portale','Portal pier',[B(0,0,0,16,16,16,'limestone'),B(2,0,-.5,14,2,0,'gold'),B(2,14,-.5,14,16,0,'gold')]+[B(x,2,-1,x+1.2,14,0,'marble') for x in (3,6,9,12)])
add('lacra_portal_relief','Rilievo del portale','Portal relief',[B(0,0,7,16,16,16,'limestone'),B(1,1,5,15,15,7,'marble'),B(7,3,4,9,13,5,'gold'),B(3,8,4,13,10,5,'gold'),B(2,2,4,4,4,5,'bronze'),B(12,2,4,14,4,5,'bronze')])
add('lacra_gate','Grata sacra in ferro e bronzo','Sacred bronze portcullis',[B(x,0,6,x+1.5,16,10,'iron') for x in (1,5,9,13)]+[B(0,y,5,16,y+1.6,11,'bronze') for y in (2,13)]+[B(7,5,4,9,11,5,'gold'),B(5,8,4,11,9.5,5,'gold')])
gear=[B(0,0,13,16,16,16,'dark'),B(2,2,10,14,14,13,'bronze'),B(5,5,8,11,11,10,'iron'),B(7,6,6,9,10,8,'gold')]
for i in range(12):
 a=i*math.tau/12;x=8+5.9*math.cos(a);y=8+5.9*math.sin(a);gear.append(B(x-.8,y-.8,9,x+.8,y+.8,12,'gold'))
add('lacra_gear','Ingranaggio del portale','Portal gear',gear)
add('lacra_lever','Leva del portone sacro','Sacred gate lever',gear+[B(7,8,3,9,10,8,'iron'),B(7,9,2,9,14,4,'bronze'),B(6,13,1,10,15,4,'red')],'new SacredGateLever()')
add('lacra_cross','Croce d’altare in bronzo','Bronze altar cross',[B(1,0,2,15,2,14,'marble'),B(5,2,5,11,4,11,'bronze'),B(7,4,7,9,16,9,'gold'),B(2,10,7,14,12,9,'gold'),B(6,9,6,10,13,7,'ivory')])
add('lacra_organ_console','Organo del coro celeste','Celestial choir organ',[B(0,0,4,16,9,16,'dark'),B(0,9,3,16,11,16,'bronze'),B(1,11,3,15,12,11,'ivory'),B(1,12,11,15,16,16,'dark')]+[B(x,12,6,x+.7,12.5,11,'iron') for x in (2,4,7,9,11,13)],'new SacredOrgan()')
for row in range(3):
 boxes=[B(0,0,13,16,16,16,'dark')]
 for j in range(5):
  x=.7+j*3.1;h=16 if row<2 else 7+(j*3)%9
  boxes.extend([B(x,0,7,x+2.4,h,13,'pipe'),B(x+.4,0,6.8,x+1.1,h,7,'gold')])
  if row==0:boxes.append(B(x+.45,4,6.6,x+1.9,5.5,6.8,'iron'))
 add('lacra_pipe_'+str(row),'Canne dell’organo sacro','Sacred organ pipes',boxes)
decl=[]
for n,(it,en,boxes,expr) in items.items():
 decl.extend([f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->{expr});',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));'])
 tx={m:'noctismagic:block/lacra_'+m for m in colors};tx['particle']=tx['limestone']
 model={'textures':tx,'elements':[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]}
 variants={f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n,'y':ang} for d,ang in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}
 dump(assets/'models/block'/f'{n}.json',model);dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n});dump(assets/'blockstates'/f'{n}.json',{'variants':variants})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
# Each controller operates a 7x6 gate from its side; refuse to close on entities.
edit('Furniture.java',lambda s:s.replace('public class Furniture{','public class Furniture{\n'+'\n'.join(decl)+'''
 public static class SacredGateLever extends FurnitureBlock{
  SacredGateLever(){super(0);}
  @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player player,InteractionHand h,BlockHitResult hit){
   if(!l.isClientSide){
    Direction f=s.getValue(FACING);
    BlockPos o=p.relative(f.getOpposite()).relative(f.getCounterClockWise(),6);
    boolean open=l.getBlockState(o).is(LACRA_GATE.get());
    for(int x=-3;x<=3;x++)for(int y=0;y<6;y++){
     BlockPos q=o.relative(f.getClockWise(),x).above(y);
     if(!l.hasChunkAt(q)||!l.mayInteract(player,q)||(!open&&!l.getBlockState(q).canBeReplaced())||(open&&!l.getBlockState(q).is(LACRA_GATE.get()))||(!open&&!l.getEntities(null,new net.minecraft.world.phys.AABB(q)).isEmpty())){
      player.displayClientMessage(Component.literal("Il meccanismo è bloccato."),true);return InteractionResult.CONSUME;
     }
    }
    for(int x=-3;x<=3;x++)for(int y=0;y<6;y++){
     BlockPos q=o.relative(f.getClockWise(),x).above(y);
     l.setBlock(q,open?Blocks.AIR.defaultBlockState():LACRA_GATE.get().defaultBlockState().setValue(FACING,f),3);
    }
    l.setBlock(p,s.cycle(LIT),3);
    l.playSound(null,p,open?SoundEvents.PISTON_EXTEND:SoundEvents.PISTON_CONTRACT,net.minecraft.sounds.SoundSource.BLOCKS,1.2f,.65f);
    player.displayClientMessage(Component.literal(open?"Il portone si apre.":"Il portone si chiude."),true);
   }
   return InteractionResult.sidedSuccess(l.isClientSide);
  }
 }
 public static class SacredOrgan extends FurnitureBlock{
  SacredOrgan(){super(0);}
  @Override public void onPlace(BlockState s,Level l,BlockPos p,BlockState old,boolean moving){
   super.onPlace(s,l,p,old,moving);if(!l.isClientSide&&!old.is(this))l.scheduleTick(p,this,20);
  }
  @Override public void tick(BlockState s,ServerLevel l,BlockPos p,net.minecraft.util.RandomSource r){
   if(!s.getValue(LIT)){
    boolean near=l.hasNearbyAlivePlayer(p.getX()+.5,p.getY()+.5,p.getZ()+.5,100);
    if(near)l.playSound(null,p,LacraMusic.SOUND,net.minecraft.sounds.SoundSource.RECORDS,5f,1f);
    l.scheduleTick(p,this,near?640:40);
   }
  }
  @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player player,InteractionHand h,BlockHitResult hit){
   if(!l.isClientSide){l.setBlock(p,s.cycle(LIT),3);if(s.getValue(LIT))l.scheduleTick(p,this,1);}
   return InteractionResult.sidedSuccess(l.isClientSide);
  }
 }
''',1))
edit('Noctis.java',lambda s:s.replace('if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)','if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)',1))
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for n,(it,en,*_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
# Original organ and wordless choir synthesis, with harmonics and reverberation.
rate=22050;secs=32;buf=[0.]*(rate*secs)
chords=[(45,52,57,60),(41,48,53,57),(43,50,55,59),(40,47,52,56),(45,52,57,64),(38,45,53,57),(40,47,56,59),(45,52,57,60)]
for k,ch in enumerate(chords):
 for j,n in enumerate(ch):
  f=440*2**((n-69)/12)
  for i in range(rate*4):
   t=i/rate;phase=math.tau*f*t;env=min(1,t/.22,(4-t)/.30)
   organ=(math.sin(phase)+.24*math.sin(2*phase)+.11*math.sin(3*phase))*.038
   vib=.7*math.sin(math.tau*5.1*t+j)
   choir=(math.sin(2*phase+vib)+.25*math.sin(4*phase+vib)+.10*math.sin(6*phase+vib))*.025*min(1,t/.85,(4-t)/.60)
   buf[k*rate*4+i]+=(organ+choir)*env
for delay,amp in ((.17,.22),(.31,.15),(.48,.10)):
 off=int(delay*rate)
 for i in range(len(buf)-1,off-1,-1):buf[i]+=buf[i-off]*amp
wav=root/'lacra_music.wav'
with wave.open(str(wav),'wb') as f:
 f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,x))*32700)) for x in buf))
ogg=assets/'sounds/lacra_music.ogg';ogg.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','5',str(ogg)],check=True);wav.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['lacra_music']={'sounds':[{'name':'noctismagic:lacra_music','stream':True,'attenuation_distance':100}]};dump(p,d)
(java/'LacraMusic.java').write_text('''package it.noctis.magic;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegisterEvent;
import net.minecraftforge.registries.ForgeRegistries;
@Mod.EventBusSubscriber(modid=Noctis.ID,bus=Mod.EventBusSubscriber.Bus.MOD)
public class LacraMusic{
 public static final ResourceLocation ID=new ResourceLocation(Noctis.ID,"lacra_music");
 public static final SoundEvent SOUND=SoundEvent.createVariableRangeEvent(ID);
 @SubscribeEvent public static void register(RegisterEvent e){e.register(ForgeRegistries.Keys.SOUND_EVENTS,h->h.register(ID,SOUND));}
}''',encoding='utf-8')
def cathedral(s):
 a=s.index('    static Plan cathedral(){');b=s.index('        return p;',a)
 s=s[:b]+'        finalCathedral(p);\n'+s[b:]
 a=s.index('    static Plan cathedral(){')
 return s[:a]+'''    static void finalCathedral(Plan p){
        Block pier=Furniture.LACRA_PORTAL_PILLAR.get(),relief=Furniture.LACRA_PORTAL_RELIEF.get();
        // Close secondary bypasses, keep the ceremonial gate as the entrance.
        p.box(15,1,8,19,9,8,Furniture.SANCTUARY_ASHLAR.get());
        p.box(41,1,8,45,9,8,Furniture.SANCTUARY_ASHLAR.get());
        p.box(27,1,7,33,6,10,Blocks.AIR);
        for(int x=27;x<=33;x++)for(int y=1;y<=6;y++)royalFacing(p,x,y,8,Furniture.LACRA_GATE.get(),Direction.NORTH);
        for(int x:new int[]{23,25,35,37})for(int y=1;y<=13;y++)royalFacing(p,x,y,7,y%4==0?relief:pier,Direction.NORTH);
        for(int k=0;k<5;k++)for(int side:new int[]{-1,1}){
            int x=30+side*(6-k);
            for(int z=6;z<=8;z++)p.put(x,8+k,z,relief);
        }
        for(int x=29;x<=31;x++)p.put(x,13,7,relief);
        // Connected visible gear columns, controller at ground level on each side.
        p.put(36,0,7,Furniture.SANCTUARY_ASHLAR.get());p.put(24,0,9,Furniture.SANCTUARY_ASHLAR.get());
        p.put(36,1,8,pier);p.put(24,1,8,pier);
        royalFacing(p,36,1,7,Furniture.LACRA_LEVER.get(),Direction.NORTH);
        royalFacing(p,24,1,9,Furniture.LACRA_LEVER.get(),Direction.SOUTH);
        for(int y=2;y<=7;y++){
            p.put(36,y,8,pier);p.put(24,y,8,pier);
            royalFacing(p,36,y,7,Furniture.LACRA_GEAR.get(),Direction.NORTH);
            royalFacing(p,24,y,9,Furniture.LACRA_GEAR.get(),Direction.SOUTH);
        }
        for(int x=26;x<=34;x++)p.put(x,7,8,pier);
        // Replace broken suspended altar fragments with a single connected cross.
        p.box(28,4,76,32,10,76,Blocks.AIR);
        p.put(30,4,76,Furniture.LACRA_CROSS.get());
        // Side shrine crosses receive a real pedestal; ceiling lamps get chains of their own.
        for(int z=17;z<=73;z+=8){
            for(int x:new int[]{11,49})if(z%16!=1)p.put(x,1,z+3,Furniture.SANCTUARY_LAMP.get());
            for(int x:new int[]{20,21,22,38,39,40}){
                p.box(x,22,z,x,31,z,Blocks.CHAIN);
                int anchorY=32+Math.min(x-14,46-x);
                p.box(x,32,z,x,anchorY-1,z,Blocks.CHAIN);
            }
        }
        // Recessed pipe organ at the west side of the nave, accessible from outside acoustically.
        p.box(6,1,32,10,8,35,Blocks.AIR);
        for(int x=6;x<=10;x++){
            p.put(x,1,34,Furniture.SANCTUARY_ASHLAR.get());
            for(int y=2;y<=6;y++)royalFacing(p,x,y,34,y==2?Furniture.LACRA_PIPE_0.get():Furniture.LACRA_PIPE_1.get(),Direction.NORTH);
            royalFacing(p,x,7,34,Furniture.LACRA_PIPE_2.get(),Direction.NORTH);
        }
        royalFacing(p,8,1,32,Furniture.LACRA_ORGAN_CONSOLE.get(),Direction.NORTH);
        for(int x:new int[]{7,9})p.put(x,1,32,Furniture.SANCTUARY_LAMP.get());
    }
'''+s[a:]
edit('GothicEgg.java',cathedral)
# Magic HUD at top left, compact typography, arcane diamond and separate XP stripe.
def hud(s):
 a=s.index('    @SubscribeEvent public static void overlay(RegisterGuiOverlaysEvent');b=s.index('    @Mod.EventBusSubscriber',a)
 return s[:a]+'''    @SubscribeEvent public static void overlay(RegisterGuiOverlaysEvent e){
        e.registerAboveAll("mana",(gui,g,partial,w,h)->{
            Minecraft mc=Minecraft.getInstance();if(mc.player==null||mc.options.hideGui||mc.player.isSpectator())return;
            int lv=limit(Noctis.View.level,1,10),max=Math.max(1,Noctis.max(lv)),mana=limit(Noctis.View.mana,0,max);
            selected=limit(selected,0,Noctis.Spell.values().length-1);
            Noctis.Spell spell=Noctis.Spell.values()[selected];int cd=Math.max(0,Noctis.View.cooldown);
            boolean ready=mana>=spell.cost&&lv>=spell.level&&cd==0;
            if(displayMana<0||lastLevel!=lv){displayMana=mana;lastLevel=lv;}
            displayMana+=(mana-displayMana)*.13f;
            int x=32,y=17,bw=Math.max(96,Math.min(145,w/3-38)),right=x+bw;
            int fill=limit(Math.round(bw*displayMana/max),0,bw);
            g.fillGradient(8,7,right+9,73,0xE21B142B,0xB0080714);
            g.fill(8,7,right+9,8,0xFFCAA568);g.fill(8,72,right+9,73,0xFF8A6A45);
            g.fill(8,8,9,72,0xFF8A6A45);g.fill(right+8,8,right+9,72,0xFF8A6A45);
            diamond(g,19,25,10,0xFFB99B60);diamond(g,19,25,8,0xFF3A235B);diamond(g,19,25,5,ready?0xFFC2A4FF:0xFF806394);
            float pulse=(float)Math.sin(mc.player.tickCount*.15);diamond(g,19,25,2+(pulse>0?1:0),0xFFF7E9FF);
            g.drawString(mc.font,"MANA",x,y-5,0xFFEAD9FF);
            String num=mana+" / "+max;g.drawString(mc.font,num,right-mc.font.width(num),y-5,0xFFEAD9FF);
            g.fill(x-1,y+6,right+1,y+18,0xFF967247);g.fill(x,y+7,right,y+17,0xFF1A1232);
            if(fill>0){
              g.fillGradient(x,y+7,x+fill,y+17,0xFFD5B5FF,0xFF5035A3);
              g.fill(x,y+7,x+fill,y+8,0xFFF0DEFF);
              for(int i=7;i<fill;i+=10)g.fill(x+i,y+9,x+i+1,y+16,0x307EF2FF);
            }
            int exp=lv==10?bw:limit(bw*Noctis.View.xp/Math.max(1,Noctis.needed(lv)),0,bw);
            g.fill(x,y+20,right,y+22,0xFF332838);g.fill(x,y+20,x+exp,y+22,0xFFE2B969);
            g.drawString(mc.font,"Lv "+lv,12,40,0xFFFFD98D);
            String label=mc.font.plainSubstrByWidth(spell.label,bw-2);
            g.drawString(mc.font,label,x+6,42,ready?0xFFF1E5FF:0xFFC3B2D1);
            String keys=CAST.getTranslatedKeyMessage().getString()+"/"+MENU.getTranslatedKeyMessage().getString();
            String state=cd>0?String.format(java.util.Locale.ROOT,"%.1fs",cd/20f):lv<spell.level?"Lv "+spell.level:mana<spell.cost?"Mana!":spell.cost+" MP";
            g.drawString(mc.font,keys,x,55,0xFFB6A7CB);
            g.drawString(mc.font,state,right-mc.font.width(state),55,ready?0xFFA9EACF:0xFFFFA68E);
        });
    }
'''+s[b:]
edit('Client.java',hud)
# Pose cycles are deterministic per individual and never override combat or serving.
def witch(s):
 a='   for(int j=0;j<locks.size();j++)';assert a in s
 s=s.replace(a,'''   if(witch){
    head.rz=0;body.rz=0;legs[0].rz=0;legs[1].rz=0;
    if(a<.01f&&amount<.10f){
     int pose=(e.tickCount/85+e.getId())%4;
     float t=Math.min(1f,Math.min(e.tickCount%85,(85-e.tickCount%85))/9f);
     if(pose==0){body.rz=.08f*t;head.rz=-.12f*t;arms[0].rz=.55f*t;fore[0].rx=-1.45f*t;arms[1].rx=-.28f*t;legs[0].rz=.13f*t;}
     if(pose==1){arms[1].rx=-1.1f*t;fore[1].rx=-1.4f*t;head.rz=.11f*t;body.ry=.20f*t;}
     if(pose==2){arms[0].rx=-.65f*t;arms[1].rx=-.65f*t;fore[0].rx=-1.1f*t;fore[1].rx=-1.1f*t;head.rx=-.10f*t;}
     if(pose==3){arms[0].rz=.9f*t;arms[1].rz=-.42f*t;fore[0].rx=-.65f*t;body.rz=-.09f*t;head.rz=.15f*t;}
    }
   }
'''+a,1)
 a='(witch?"bayonetta_sculpted":"dante_sculpted"+((Dante)e).faceStyle())';assert a in s
 return s.replace(a,'(witch?"bayonetta_sculpted"+ExprStyle.face(e):"dante_sculpted"+((Dante)e).faceStyle())',1)
edit('WitchHunterClient.java',witch)
def sushi(s):
 a='            tray.rx=1.12f*a;';assert a in s
 s=s.replace(a,'''            head.rz=0;body.rz=0;
            if(a<.04f&&amount<.10f){
                int pose=(e.tickCount/90+e.getId())%3;
                float t=Math.min(1f,Math.min(e.tickCount%90,(90-e.tickCount%90))/10f);
                if(pose==0){head.rz=(mao?-.14f:.10f)*t;arms[0].rx=-.75f*t;arms[0].rz=.24f*t;}
                if(pose==1){arms[0].rx=-.95f*t;arms[1].rx=-.85f*t;head.rx+=.10f*t;body.rz=.045f*t;}
                if(pose==2){head.rz=(mao?.16f:-.12f)*t;arms[1].rx=-.62f*t;arms[1].rz=-.35f*t;}
            }
'''+a,1)
 return s.replace('+(mao?"maomao":"jinshi")+"_sculpted.png"','+(mao?"maomao":"jinshi")+"_sculpted"+ExprStyle.face(e)+".png"',1)
edit('SushiGuestClient.java',sushi)
(java/'ExprStyle.java').write_text('''package it.noctis.magic;
import net.minecraft.world.entity.LivingEntity;
public final class ExprStyle{
 public static String face(LivingEntity e){
  if(e.hurtTime>0)return "_wince";
  if((e.tickCount+e.getId()*13)%91<4)return "_blink";
  int q=(e.tickCount/85+e.getId())%4;
  return q==0?"_smirk":q==2?"_amused":"";
 }
}''',encoding='utf-8')
# Face variants keep the original skin, brows, nose and shading outside eye/mouth region.
for name,tile,eyes,lip in [('bayonetta',5,.455,.79),('maomao',6,.506,.79),('jinshi',6,.515,.79)]:
 base=Image.open(assets/'textures/entity'/f'{name}_sculpted.png').convert('RGBA')
 X=tile%8*128;Y=tile//8*128
 for style in ('blink','wince','smirk','amused'):
  im=base.copy();d=ImageDraw.Draw(im)
  if style in ('blink','wince','amused'):
   for side in (-1,1):
    center=.5+side*(.21 if name=='bayonetta' else .078);width=.115 if name=='bayonetta' else .055
    if style=='amused' and name=='bayonetta' and side==1:continue
    for y in range(128):
     v=(y-3)/121
     for x in range(128):
      u=(x-3)/121;dx=(u-center)/width
      if abs(dx)>1.25 or abs(v-eyes)>(.069 if name=='bayonetta' else .083):continue
      skin=base.getpixel((X+max(0,min(127,round((center+side*width*1.5)*121+3))),Y+y))
      c=skin
      line=eyes+(.022 if style=='wince' else -.022)*(1-dx*dx)
      if abs(dx)<1.02 and abs(v-line)<.008:c=(57,31,47,255)
      im.putpixel((X+x,Y+y),c)
  if style in ('smirk','amused','wince'):
   for y in range(128):
    v=(y-3)/121
    for x in range(128):
     u=(x-3)/121;dx=u-.5
     width=.088 if name=='bayonetta' else .038
     if abs(dx)>width*1.25 or abs(v-lip)>.037:continue
     c=base.getpixel((X+max(0,min(127,round((.5+width*1.4)*121+3))),Y+y))
     line=lip+(.020 if style=='wince' else -.018)*(dx/width)**2+(.015*dx/width if style=='smirk' else 0)
     if abs(dx)<width and abs(v-line)<.008:c=(129,38,66,255) if name=='bayonetta' else (136,78,78,255)
     im.putpixel((X+x,Y+y),c)
  im.save(assets/'textures/entity'/f'{name}_sculpted_{style}.png')
print('Cathedral gate, organ and choir; arcane HUD and expressive Bayonetta/Maomao/Jinshi.')
