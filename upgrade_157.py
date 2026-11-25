"""1.5.7: Faputa, a genuinely non-humanoid four-armed sculpted creature."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'MoonGuestClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.FAPUTA.get(),c->new Renderer(c,2));'
assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'FaputaSculptedClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import java.util.*;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class FaputaSculptedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.FAPUTA.get(),R::new);}
 static class M extends EntityModel<MoonGuest>{
  final Part root=new Part(0,0,0),body=root.child(0,8,0),head=body.child(0,-3.5f,-.35f);
  final Part[] ears=new Part[2],arms=new Part[4],fore=new Part[4],legs=new Part[2],feet=new Part[2],tails=new Part[3];
  final List<Part> locks=new ArrayList<>();
  M(){
   // Small brown upper torso transitions into a fluffy pear-shaped lower body.
   body.loft(0,32,-2.2f,0,0,1.55f,1.32f,-.8f,0,0,2.48f,1.65f,2.0f,0,0,2.30f,1.56f,4.8f,0,0,1.87f,1.44f,7.1f,0,.12f,2.75f,2.05f);
   body.loft(1,32,4.75f,0,.10f,1.84f,1.48f,6.5f,0,.15f,2.75f,2.15f,9.25f,0,.25f,3.48f,2.63f,11.3f,0,.25f,3.22f,2.37f,12.8f,0,.05f,1.95f,1.65f);
   // Two round raised bronze ornaments with four-lobed inner design.
   for(int s:new int[]{-1,1}){
    Part med=body.child(s*1.32f,.05f,-1.48f);med.ry=-s*.25f;
    med.oval(3,0,0,0,1.13f,1.13f,.42f);
    med.oval(4,0,0,-.35f,.86f,.86f,.25f);
    for(int j=0;j<4;j++){float a=j*(float)Math.PI/2;Part petal=med.child(0,0,-.55f);petal.rz=a;petal.oval(3,0,-.34f,0,.18f,.35f,.07f);}
    med.oval(3,0,0,-.65f,.17f,.17f,.10f);
   }
   // Dark rounded face: the only eye-bearing UV surface.
   head.loft(5,48,-6.8f,0,.15f,1.1f,1.3f,-6.2f,0,.1f,2.45f,2.25f,-4.7f,0,0,3.15f,2.65f,-2.9f,0,-.12f,3.08f,2.62f,-1.4f,0,-.22f,2.48f,2.10f,-.4f,0,-.28f,1.50f,1.34f,0,0,-.25f,.55f,.65f);
   head.oval(0,0,-1.8f,-2.53f,.27f,.25f,.28f);
   // Cream crown and swept layered tufts, asymmetrical framing of the eyes.
   head.loft(1,36,-8.25f,0,.1f,.42f,.50f,-8.0f,0,.05f,2.30f,2.2f,-7.05f,0,.1f,3.5f,3.0f,-5.9f,0,.3f,3.6f,3.05f);
   Part rear=head.child(0,-5.9f,1.8f);
   rear.loft(1,24,-.65f,0,0,2.85f,1.5f,1.5f,0,.4f,3.15f,1.45f,3.6f,0,.45f,2.85f,1.2f,5.4f,0,.6f,1.55f,.20f);
   for(int j=0;j<7;j++){
    float x=-2.45f+j*.82f;Part q=head.child(x,-7.2f,-2.02f);locks.add(q);
    float len=j==3?4.15f:j==2||j==4?3.25f:2.7f;
    q.loft(j==1||j==3||j==5?6:1,18,-.55f,0,.50f,.61f,.75f,.55f,(j-3)*.08f,-.30f,.82f,.75f,1.6f,(j-3)*.13f,-.55f,.77f,.57f,len*.82f,(j-3)*.13f,-.5f,.45f,.35f,len,(j-3)*.09f,-.17f,.035f,.055f);
   }
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    // Large horizontal, pointed, pink-lined ears; taper to thin curved tips.
    Part ear=ears[i]=head.child(s*2.68f,-4.95f,.35f);ear.rz=-s*1.14f;ear.rx=-.12f;
    ear.loft(1,28,-.5f,0,0,.85f,1.38f,1.1f,0,0,1.35f,1.90f,3.15f,-s*.23f,.12f,1.17f,1.61f,4.85f,-s*.50f,.08f,.66f,1.03f,6.35f,-s*.9f,-.12f,.06f,.09f);
    Part inner=ear.child(0,.40f,-1.05f);
    inner.loft(2,24,0,0,0,.47f,.25f,1.15f,0,-.65f,.89f,.32f,2.8f,-s*.20f,-.53f,.80f,.26f,4.4f,-s*.46f,-.24f,.39f,.12f,5.35f,-s*.71f,.12f,.025f,.035f);
    for(int j=0;j<3;j++){
     Part cheek=head.child(s*(2.6f+j*.18f),-4.5f+j*.6f,.25f+j*.55f);locks.add(cheek);cheek.rz=-s*.14f;
     cheek.loft(1,16,-.5f,0,0,.70f,1.05f,1.3f,s*.40f,-.10f,.90f,1.03f,2.85f,s*.66f,.12f,.56f,.66f,4.1f,s*.95f,.35f,.03f,.05f);
    }
    // Four independent arms: long outer forelimbs and shorter inner forelimbs.
    for(int j=0;j<2;j++){
     int k=i*2+j;Part arm=arms[k]=body.child(s*(j==0?2.30f:2.04f),j==0?.1f:2.45f,j==0?.28f:.72f);
     arm.loft(0,20,-.45f,0,0,.67f,.73f,.6f,0,0,.80f,.85f,2.7f,s*.28f,0,.67f,.69f,3.35f,s*.32f,0,.54f,.56f);
     Part f=fore[k]=arm.child(s*.32f,3.05f,0);
     float len=j==0?5.0f:4.25f;
     f.loft(1,24,-.4f,0,0,.65f,.68f,.75f,s*.1f,0,1.15f,1.22f,2.3f,s*.18f,0,1.42f,1.30f,len-1.1f,s*.1f,-.10f,1.14f,1.06f,len,0,-.12f,.70f,.65f);
     for(int n=0;n<3;n++){Part claw=f.child((n-1)*.57f,len-.3f,-.33f);claw.rx=-.25f;
      claw.loft(6,16,-.20f,0,0,.33f,.35f,.6f,0,0,.33f,.30f,1.45f,0,-.22f,.17f,.17f,1.92f,0,-.52f,.025f,.035f);}
    }
    // Thick furred haunches, tapered digitigrade legs, red claw tips.
    Part leg=legs[i]=body.child(s*1.94f,9.1f,.22f);
    leg.loft(1,28,-1.0f,0,0,1.58f,1.62f,.65f,s*.22f,0,2.0f,1.92f,2.8f,s*.12f,.12f,1.65f,1.60f,4.75f,0,.05f,.96f,1.02f,5.5f,0,0,.73f,.73f);
    Part foot=feet[i]=leg.child(0,4.95f,.05f);
    foot.loft(1,22,-.1f,0,0,.79f,.81f,1.05f,0,.27f,.65f,.68f,1.9f,0,-.12f,.79f,1.05f);
    foot.loft(6,22,1.45f,0,-.10f,.76f,1.01f,1.95f,0,-.24f,.79f,1.15f,2.15f,0,-.3f,.68f,1.06f);
    leg.blade(6,s*.25f,2.4f,-1.46f,s*.12f,4.1f,-1.02f,.63f);
    leg.blade(6,-s*.45f,1.45f,-1.62f,-s*.29f,2.5f,-1.59f,.47f);
   }
   // Three individually animated, broad leaf-shaped tails, rising in a fan.
   for(int i=0;i<3;i++){
    Part t=tails[i]=body.child(0,7.45f,1.95f);
    t.rx=1.18f-i*.43f;t.rz=(i-1)*.45f;t.ry=(i-1)*.37f;
    float len=8.0f+i*.7f;
    t.loft(1,32,-.65f,0,0,.66f,.84f,1.5f,0,0,1.65f,1.32f,3.8f,0,.5f,2.46f,1.62f,6.0f,.15f,.92f,2.10f,1.18f,len-1.2f,.35f,1.05f,.98f,.62f,len,.54f,.8f,.035f,.05f);
   }
  }
  @Override public void setupAnim(MoonGuest e,float limb,float amount,float age,float yaw,float pitch){
   boolean rage=e.berserk();float hit=e.action();float move=Math.min(1,amount);
   body.y=8+(float)Math.sin(limb*1.32)*move*.36f;body.rx=rage?.17f:0;
   head.ry=yaw*.01745f;head.rx=pitch*.012f-(rage?.13f:0);
   for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*move;
    ears[i].rz=-s*(1.14f+(rage?.20f:0)+(float)Math.sin(age*.13+i)*.055f);
    legs[i].rx=w*.72f;feet[i].rx=Math.max(0,-w)*.32f;
    for(int j=0;j<2;j++){int k=i*2+j;arms[k].rz=-s*(j==0?.24f:.57f)-(rage?s*.22f:0);arms[k].rx=-w*(j==0?.5f:-.33f)-hit*(j==0?1.25f:.80f)-(rage?.35f:0);
     fore[k].rx=-hit*.75f+(j==0?-.12f:-.35f);}
   }
   for(int i=0;i<3;i++){tails[i].rx=1.18f-i*.43f+(float)Math.sin(age*(rage?.23:.12)+i*.8f)*(.11f+move*.15f);tails[i].rz=(i-1)*.45f+(float)Math.sin(age*.11+i)*.10f;}
   for(int i=0;i<locks.size();i++)locks.get(i).rz=(float)Math.sin(age*.13+i*.65f)*(.025f+move*.03f);
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<MoonGuest,M>{
  static final ResourceLocation NORMAL=new ResourceLocation(Noctis.ID,"textures/entity/faputa_sculpted.png"),RAGE=new ResourceLocation(Noctis.ID,"textures/entity/faputa_rage.png");
  R(EntityRendererProvider.Context c){super(c,new M(),.39f);}
  @Override protected void scale(MoonGuest e,PoseStack p,float partial){p.scale(.88f,.88f,.88f);}
  @Override public ResourceLocation getTextureLocation(MoonGuest e){return e.berserk()?RAGE:NORMAL;}
 }
}''',encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
pal=[(128,99,76),(246,239,220),(217,169,162),(196,147,72),(120,79,39),(128,99,76),(166,32,46)]
for rage in (False,True):
 pix=bytearray(W*H*4)
 for m,base in enumerate(pal):
  for y in range(128):
   v=clamp((y-3)/121)
   for x in range(128):
    u=clamp((x-3)/121);f=abs(u-.5)
    c=blend(base,(88,66,64),.10*v+.09*(1-math.sin(u*math.pi)))
    if m==1:
     flow=math.sin(u*math.pi*15+math.sin(v*7)*1.5)**2
     c=blend(base,(184,166,155),.12*(1-flow)+.07*v)
     c=blend(c,(255,253,244),.20*math.exp(-((u-.38)/.16)**2))
    if m==2:c=blend(base,(249,218,205),.38*math.sin(u*math.pi)**2)
    if m in (3,4):c=blend((105,65,30),(244,202,124),.28+.65*math.sin(u*math.pi)**2)
    if m==6:
     c=blend((130,20,39),(231,66,75),.25+.55*math.sin(u*math.pi)**2)
     # Red forehead marking is on cream fringe only at its centre; claws have red tips.
     if v<.35:c=blend((246,239,220),c,clamp(v*3))
    if m==5:
     c=blend(base,(80,58,52),.17*clamp((f-.15)*4)+.14*math.exp(-((v-.80)/.15)**2))
     for ex in (.383,.617):
      dx=(u-ex)/.079;dy=(v-.52+(.045*dx if ex<.5 else -.045*dx))/.159
      if rage:dy=(v-.54+(.09*dx if ex<.5 else -.09*dx))/.115
      d=dx*dx+dy*dy
      if d<1:c=(48,31,28)
      if d<.88:c=(252,242,219)
      if ((dx+(.10 if ex<.5 else -.10))/.67)**2+(dy/.90)**2<1 and d<.86:
       c=blend((204,46,35) if rage else (179,126,47),(255,192,83) if rage else (255,226,138),clamp((dy+.3)*.6))
      if abs(dx)<(.17 if rage else .25) and abs(dy)<.75 and d<.8:c=(33,25,26)
      if (dx+.18)**2+(dy+.26)**2<.09 or (dx-.22)**2+(dy-.27)**2<.027:c=(255,255,244)
      if abs(dx)<1.05 and abs(dy+.92)<.09:c=(48,31,28)
     if f<(.065 if rage else .032) and abs(v-.83+.012*math.cos(f*45))<(.033 if rage else .011):c=(59,30,31)
    off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
 # Dedicated red marking tile 7, ivory with a ruby lance-shaped mark.
 for y in range(128):
  v=clamp((y-3)/121)
  for x in range(128):
   u=clamp((x-3)/121);c=(244,237,221)
   if .16<v<.83 and abs(u-.5)<.13*math.sin((v-.16)/.67*math.pi):c=(173,31,47)
   off=(y*W+7*128+x)*4;pix[off:off+4]=bytes((*c,255))
 name='faputa_rage.png' if rage else 'faputa_sculpted.png'
 (assets/name).write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
# Forehead uses the dedicated ivory/red marking material, never the claw tile.
p=java/'FaputaSculptedClient.java';s=p.read_text(encoding='utf-8');s=s.replace('j==1||j==3||j==5?6:1','j==1||j==3||j==5?7:1');p.write_text(s,encoding='utf-8')
print('Faputa rebuilt with four arms, three tails, large pointed ears, fur tufts, gold medallions and distinct berserk texture')
