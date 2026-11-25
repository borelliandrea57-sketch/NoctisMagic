"""1.5.5: Lucy custom asymmetric pastel bob, cyberpunk tailoring and detailed face."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'MoonGuestClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.LUCY.get(),c->new Renderer(c,1));'
assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'LucySculptedClient.java').write_text('''package it.noctis.magic;
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
public class LucySculptedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.LUCY.get(),R::new);}
 static class M extends EntityModel<MoonGuest>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1.3f,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shin=new Part[2];
  final List<Part> strands=new ArrayList<>(); final Part longlock;
  M(){
   // High collar, fitted dark techwear bodysuit and cropped white jacket.
   body.loft(0,32,-.8f,0,0,1.65f,1.25f,0,0,0,3.05f,1.65f,2.5f,0,-.15f,2.95f,1.92f,5.4f,0,0,2.15f,1.46f,8.8f,0,0,2.15f,1.6f,10.5f,0,0,3.0f,1.85f);
   body.loft(1,24,-1.7f,0,0,1.15f,1.12f,-.8f,0,0,1.43f,1.3f,.1f,0,0,1.6f,1.46f);
   body.loft(2,24,-1.78f,0,0,1.19f,1.16f,-1.48f,0,0,1.24f,1.2f);
   body.blade(2,-1.15f,-1.1f,-1.35f,0,1.5f,-1.81f,.32f);
   body.blade(2,1.15f,-1.1f,-1.35f,0,1.5f,-1.81f,.32f);
   body.blade(3,0,1.3f,-1.83f,0,4.7f,-1.9f,.28f);
   for(int i=0;i<2;i++){int s=i==0?-1:1;
    Part panel=body.child(s*2.35f,1.6f,-.65f);panel.rz=-s*.13f;
    panel.loft(4,20,-.5f,0,0,.95f,1.18f,.5f,0,-.1f,1.10f,1.32f,3.3f,0,0,.87f,1.1f,4.7f,0,.1f,.75f,.88f);
    body.blade(5,s*3.05f,1.05f,-.85f,s*.95f,3.1f,-1.86f,.65f);
    body.blade(2,s*1.75f,4.4f,-1.65f,s*.85f,5.5f,-1.72f,.25f);
    body.blade(2,s*1.8f,7.5f,-1.34f,s*.9f,8.35f,-1.72f,.23f);
   }
   body.loft(4,28,10.2f,0,0,2.9f,1.82f,11.7f,0,0,3.02f,1.9f,12.1f,0,0,2.68f,1.6f);
   body.loft(5,28,9.85f,0,0,2.95f,1.85f,10.55f,0,0,3.08f,1.95f);
   body.oval(3,0,10.2f,-1.98f,.65f,.43f,.18f);
   Part pouch=body.child(2.8f,10.3f,-.4f);
   pouch.loft(5,18,-.65f,0,0,.72f,1.16f,-.35f,0,0,.95f,1.3f,2.3f,0,0,.95f,1.25f,2.6f,0,0,.72f,1.05f);
   // Face with tapered jaw, cheek contour, visible ear and cyberware.
   head.loft(6,40,-7.65f,0,.18f,1.2f,1.55f,-7.15f,0,.1f,2.45f,2.35f,-5.8f,0,0,3.16f,2.75f,-4.25f,0,-.05f,3.23f,2.80f,-3.0f,0,-.1f,2.95f,2.56f,-1.55f,0,-.16f,2.25f,2.08f,-.45f,0,-.25f,1.15f,1.33f,0,0,-.30f,.42f,.65f);
   head.oval(7,0,-2.75f,-2.61f,.29f,.41f,.34f);
   head.oval(7,-3.02f,-3.65f,.05f,.47f,.95f,.61f);
   head.oval(8,-3.25f,-3.6f,-.25f,.20f,.57f,.28f);
   // One continuous crown plus asymmetrical curved panels, with pastel gradients.
   head.loft(9,36,-9.3f,.30f,.12f,.44f,.55f,-9.05f,.20f,.10f,2.1f,2.05f,-8.25f,.08f,.15f,3.05f,2.8f,-7.1f,0,.18f,3.54f,3.10f,-5.8f,0,.35f,3.57f,3.05f);
   Part back=head.child(0,-7.05f,1.4f);
   back.loft(10,28,-.85f,0,0,2.85f,1.6f,.85f,0,.40f,3.42f,1.86f,3.25f,0,.72f,3.48f,1.75f,5.5f,0,.60f,3.15f,1.44f,7.4f,-.28f,.40f,2.30f,.54f,8.2f,-.48f,.20f,.45f,.10f);
   // Side-swept fringe starts off-centre and ends above the eyes.
   for(int j=0;j<5;j++){
    float x=-.72f+j*.77f;Part q=head.child(x,-8.15f,-2.04f);
    q.loft(9,18,-.55f,0,.45f,.52f,.58f,.6f,-.18f,-.42f,.85f,.73f,1.75f,.03f,-.83f,.83f,.56f,2.7f,.30f,-.71f,.68f,.38f,3.45f+(j==2?.20f:0),.41f,-.46f,.45f,.22f,3.64f+(j==2?.2f:0),.42f,-.39f,.14f,.08f);
    strands.add(q);
   }
   // Short violet side on the left, exposing an ear and pale shaved section.
   Part shortSide=head.child(-2.65f,-6.85f,.08f);
   shortSide.loft(10,20,-.55f,0,0,.8f,1.25f,1.35f,-.54f,.2f,1.05f,1.45f,3.55f,-.70f,.55f,.89f,1.1f,5.6f,-.38f,.38f,.58f,.74f,7.6f,.12f,.0f,.03f,.05f);
   Part shaved=head.child(-2.12f,-6.7f,-1.78f);
   shaved.loft(11,14,-.5f,0,.1f,.57f,.30f,.7f,-.25f,-.16f,.66f,.27f,2.1f,-.48f,-.18f,.44f,.16f,3.2f,-.58f,-.1f,.045f,.04f);
   // Long right lock, pastel pink -> icy blue -> mint -> yellow.
   longlock=head.child(2.65f,-7.15f,-.55f);
   longlock.loft(12,24,-.65f,0,.2f,.70f,1.05f,1.1f,.58f,-.36f,1.04f,1.23f,3.8f,.68f,-.7f,1.02f,.94f,6.4f,.45f,-.92f,.89f,.68f,9.0f,.12f,-1.15f,.72f,.48f,11.5f,-.35f,-1.25f,.44f,.32f,13.5f,-.82f,-1.35f,.035f,.045f);
   Part sliver=head.child(-2.6f,-5.0f,-1.0f);
   sliver.loft(12,12,-.1f,0,0,.23f,.30f,2.8f,.14f,-.50f,.25f,.21f,5.7f,.55f,-.65f,.035f,.04f);
   for(int i=0;i<2;i++){int s=i==0?-1:1;
    arms[i]=body.child(s*3.58f,.65f,0);
    arms[i].oval(7,0,.5f,0,1.16f,1.22f,1.18f);
    arms[i].loft(4,22,1.3f,0,0,1.32f,1.32f,2.1f,0,0,1.53f,1.45f,4.2f,0,0,1.3f,1.31f,5.1f,0,0,1.12f,1.1f);
    arms[i].loft(5,20,1.25f,0,0,1.36f,1.37f,1.78f,0,0,1.45f,1.4f);
    fore[i]=arms[i].child(0,4.95f,0);
    fore[i].loft(4,20,-.2f,0,0,1.15f,1.13f,1.55f,0,0,1.27f,1.22f,3.95f,0,0,.79f,.81f);
    fore[i].loft(5,20,3.65f,0,0,.87f,.88f,4.15f,0,0,.83f,.84f);
    fore[i].oval(7,0,5.02f,-.08f,.72f,1.0f,.56f);
    for(int j=0;j<4;j++)fore[i].oval(7,-.46f+j*.30f,5.65f,-.32f,.16f,.49f-(j==3?.10f:0),.18f);
    fore[i].blade(2,-s*.44f,5.8f,-.49f,-s*.44f,6.1f,-.5f,.14f);
    legs[i]=root.child(s*1.55f,11.3f,0);
    legs[i].loft(13,22,-.25f,0,0,1.51f,1.47f,2.35f,0,0,1.43f,1.32f,5.8f,0,0,.96f,.98f);
    shin[i]=legs[i].child(0,5.6f,0);
    shin[i].oval(5,0,.1f,-.39f,1.09f,1.16f,.98f);
    shin[i].loft(5,24,.5f,0,0,1.03f,1.08f,2.2f,0,.05f,1.12f,1.05f,4.7f,0,0,.70f,.82f,6.0f,0,-.08f,.78f,.88f,7.1f,0,-.52f,1.02f,1.63f);
    shin[i].blade(3,0,1.05f,-1.1f,0,5.2f,-.83f,.52f);
    for(int j=0;j<2;j++)shin[i].blade(2,s*.64f,2.0f+j*1.25f,-.65f,s*.18f,2.8f+j*1.25f,-.86f,.22f);
    shin[i].loft(2,24,6.65f,0,-.51f,1.04f,1.65f,6.83f,0,-.52f,1.03f,1.65f);
   }
  }
  @Override public void setupAnim(MoonGuest e,float limb,float amount,float age,float yaw,float pitch){
   float a=e.action();head.ry=yaw*.01745f;head.rx=pitch*.014f-(amount<.05f?.13f:0)-a*.10f;
   body.ry=(float)Math.sin(limb*.33)*amount*.025f;
   for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;
    arms[i].rx=-w*.55f-(i==1?a*.25f:0);arms[i].rz=-s*.11f;
    fore[i].rx=-.06f-(i==1?a*.6f:0);
    legs[i].rx=w*.65f;shin[i].rx=Math.max(0,-w)*.33f;
   }
   longlock.rx=amount*.14f+(float)Math.sin(age*.11)*.035f;
   longlock.rz=(float)Math.sin(age*.09)*.034f;
   for(int i=0;i<strands.size();i++)strands.get(i).rx=(float)Math.sin(age*.10+i*.6)*.009f;
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<MoonGuest,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.35f);}
  @Override public ResourceLocation getTextureLocation(MoonGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/lucy_sculpted.png");}
 }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(65,62,91),(46,42,64),(218,66,69),(108,117,148),(219,225,245),(38,40,57),(250,226,212),(250,226,212),(209,145,154),(248,218,244),(160,171,229),(231,236,250),(247,219,242),(119,118,152)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def grad(v,stops):
    for (a,c),(b,d) in zip(stops,stops[1:]):
        if v<=b:return blend(c,d,clamp((v-a)/(b-a)))
    return stops[-1][1]
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(40,36,66),.09*v+.09*(1-math.sin(u*math.pi)))
            if m in (9,10,12):
                stops=[(0,(250,222,246)),(.34,(246,213,241)),(.53,(193,222,246)),(.70,(179,229,214)),(.88,(248,240,177)),(1,(247,184,214))] if m==12 else [(0,(251,222,246)),(.48,(247,218,245)),(.62,(194,219,244)),(1,(175,191,236))] if m==9 else [(0,(230,214,247)),(.48,(179,199,239)),(1,(131,139,207))]
                c=grad(v,stops);c=blend(c,(255,252,255),.13*math.exp(-((u-.34)/.16)**2))
                c=blend(c,(94,104,160),.10*(1-math.sin(u*math.pi)**2))
                # Thin directional strand lines, not repetitive high-contrast stripes.
                if abs(math.sin(u*math.pi*5+v*1.9))<.06:c=blend(c,(110,119,174),.16)
            if m==11:
                if abs(v-.36-.1*math.sin(u*math.pi))<.025 or abs(v-.72-.08*math.sin(u*math.pi))<.025:c=(139,158,207)
            if m==4:
                if abs(v-.18-.045*math.sin(u*math.pi*2))<.016 or abs(v-.85)<.014:c=(153,166,208)
                c=blend(c,(153,164,205),.12*math.sin(u*math.pi*4+v)**2)
            if m in (0,5,13):
                if abs(f-.23)<.014:c=blend(c,(143,144,174),.30)
                if v>.96 or v<.025:c=blend(c,(143,144,174),.22)
            if m==6:
                c=blend(base,(208,146,157),.16*math.exp(-((v-.66)/.19)**2)+.08*clamp((f-.17)*5))
                for ex in (.395,.605):
                    dx=(u-ex)/.073;dy=(v-.51+(.045*dx if ex<.5 else -.045*dx))/.100
                    # angular almond-shaped eyes with strong upper liner and coral triangle beneath
                    d=abs(dx)**1.7+abs(dy)**1.55
                    if abs(dx)<1.12 and .69<dy<1.55-.55*abs(dx):c=(218,82,80)
                    if d<1:c=(32,25,42)
                    if d<.80:c=(249,248,240)
                    if abs(dx)<.54 and d<.8:c=grad(clamp((dy+1)/2),[(0,(125,116,190)),(.45,(168,207,224)),(1,(119,222,181))])
                    if abs(dx)<.22 and abs(dy)<.74 and d<.78:c=(31,28,55)
                    if (dx+.18)**2+(dy+.25)**2<.075:c=(255,255,255)
                    if abs(dx)<1.04 and abs(dy+.67+.18*dx*(1 if ex<.5 else -1))<.12:c=(36,25,43)
                    if abs(dx)<.92 and abs(v-(.365+.035*dx*(1 if ex<.5 else -1)))<.012:c=(137,131,178)
                if f<.018 and .66<v<.71:c=blend(c,(151,88,115),.30)
                if f<.052 and abs(v-.80+.012*math.cos(f*60))<.012:c=(131,63,73)
                if f<.040 and .81<v<.835:c=blend(c,(224,109,119),.77)
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'lucy_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Lucy: asymmetric sculpted pastel hair, detailed makeup, cyberpunk jacket and animated articulated limbs')
