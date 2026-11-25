"""1.5.6: Bucciarati individual sculpted model, tailored keyhole suit and zipper hardware."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'JojoClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.BUCCIARATI.get(),c->new Renderer(c,1));'
assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'BucciaratiSculptedClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
import java.util.*;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class BucciaratiSculptedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.BUCCIARATI.get(),R::new);}
 // Open elliptical zipper pull, built from a toroidal mesh.
 static V ring(float a,float b,float w,float h,float r,float u,float v){
  float ca=(float)Math.cos(a),sa=(float)Math.sin(a),cb=(float)Math.cos(b),sb=(float)Math.sin(b);
  return new V((w+r*cb)*ca,(h+r*cb)*sa,r*sb,u,v,ca*cb,sa*cb,sb);
 }
 static void loop(Part p,float w,float h,float r){
  for(int i=0;i<24;i++)for(int j=0;j<8;j++){
   float a=i*(float)Math.PI/12,A=(i+1)*(float)Math.PI/12,b=j*(float)Math.PI/4,B=(j+1)*(float)Math.PI/4;
   p.faces.add(new Q(ring(a,b,w,h,r,i/24f,j/8f),ring(A,b,w,h,r,(i+1)/24f,j/8f),ring(A,B,w,h,r,(i+1)/24f,(j+1)/8f),ring(a,B,w,h,r,i/24f,(j+1)/8f),3));
  }
 }
 static class M extends EntityModel<JojoMob>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1.2f,0);
  final Part[] arm=new Part[2],fore=new Part[2],leg=new Part[2],shin=new Part[2],hem=new Part[2],pulls=new Part[2];
  final List<Part> locks=new ArrayList<>();
  M(){
   // The chest opening is integrated into the torso UV; its curved border follows the body.
   body.loft(0,40,-1,0,0,1.9f,1.5f,.1f,0,0,3.75f,2.13f,2.4f,0,-.12f,3.65f,2.23f,5.3f,0,0,2.95f,1.85f,8.5f,0,0,2.35f,1.62f,10.4f,0,0,2.8f,1.80f);
   body.loft(2,28,-1.55f,0,0,1.25f,1.18f,-.95f,0,0,1.49f,1.4f,.15f,0,0,1.68f,1.48f);
   body.loft(3,28,-.95f,0,0,1.51f,1.43f,-.58f,0,0,1.55f,1.45f);
   for(int s:new int[]{-1,1}){
    // Raised, contrasting lapels around the low diamond-shaped opening.
    body.blade(1,s*1.85f,.35f,-1.75f,s*2.02f,2.2f,-1.95f,.48f);
    body.blade(1,s*2.02f,2.2f,-1.95f,s*1.15f,5.4f,-1.92f,.46f);
    body.blade(1,s*1.15f,5.4f,-1.92f,0,6.75f,-1.85f,.41f);
    Part zipper=body.child(s*2.72f,.1f,-1.38f);zipper.rz=-s*.12f;
    zipper.blade(3,0,0,0,0,4.4f,-.34f,.32f);
    for(int j=0;j<12;j++)zipper.oval(4,0,.20f+j*.32f,-.12f-j*.021f,.25f,.105f,.16f);
    Part pull=pulls[s<0?0:1]=zipper.child(0,4.35f,-.34f);
    pull.oval(3,0,-.16f,0,.31f,.53f,.16f);Part ring=pull.child(0,.73f,0);loop(ring,.38f,.57f,.145f);
   }
   body.oval(3,.05f,8.9f,-1.69f,.38f,.40f,.17f);
   body.blade(1,0,6.65f,-1.86f,.15f,9.3f,-1.71f,.38f);
   // Shaped face with anime/manga shading, angular nose and narrow chin.
   head.loft(5,48,-7.9f,0,.10f,1.2f,1.4f,-7.3f,0,.05f,2.55f,2.35f,-5.8f,0,0,3.13f,2.78f,-4.3f,0,-.06f,3.10f,2.75f,-3.0f,0,-.10f,2.82f,2.55f,-1.5f,0,-.17f,2.20f,2.02f,-.45f,0,-.23f,1.32f,1.35f,0,0,-.26f,.62f,.72f);
   head.loft(6,18,-3.85f,0,-2.48f,.19f,.16f,-2.7f,0,-2.86f,.37f,.41f,-2.1f,0,-2.83f,.31f,.20f);
   for(int s:new int[]{-1,1})head.oval(6,s*3.03f,-3.45f,.10f,.39f,.83f,.55f);
   // Rounded, glossy blue-black bob. Fringe ends at the brow rather than obscuring eyes.
   head.loft(7,36,-9.2f,0,.15f,.5f,.65f,-8.9f,0,.1f,2.25f,2.2f,-8.0f,0,.12f,3.25f,2.9f,-6.65f,0,.26f,3.48f,3.04f,-5.65f,0,.42f,3.46f,2.96f);
   Part back=head.child(0,-6.7f,1.50f);
   back.loft(7,28,-.6f,0,0,2.9f,1.65f,1.2f,0,.4f,3.32f,1.65f,4.2f,0,.58f,3.28f,1.56f,6.4f,0,.20f,2.75f,1.11f,7.5f,0,-.1f,1.5f,.35f);
   for(int i=0;i<9;i++){
    float x=-2.7f+i*.675f;Part q=head.child(x,-7.5f,-2.16f);
    float end=2.32f+(i%3)*.12f;
    q.loft(7,14,-.5f,0,.5f,.53f,.7f,.4f,0,-.30f,.60f,.58f,1.35f,.04f,-.48f,.53f,.40f,end,.11f,-.34f,.43f,.15f);
   }
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    Part side=head.child(s*2.74f,-6.65f,.1f);locks.add(side);
    side.loft(7,24,-.5f,0,.10f,.85f,1.35f,1.0f,s*.46f,-.1f,1.0f,1.65f,3.0f,s*.40f,-.1f,.93f,1.65f,5.2f,s*.08f,-.08f,.67f,1.2f,6.6f,-s*.15f,-.10f,.28f,.42f);
    // Two gold barrel clips at the front temples.
    Part clip=head.child(s*2.25f,-6.95f,-2.47f);clip.rz=-s*.42f;
    clip.loft(3,18,-.68f,0,0,.27f,.23f,-.46f,0,0,.43f,.30f,.48f,0,0,.43f,.30f,.68f,0,0,.25f,.21f);
    for(int j=0;j<3;j++)clip.loft(4,18,-.44f+j*.39f,0,0,.445f,.315f,-.35f+j*.39f,0,0,.445f,.315f);
    hem[i]=body.child(s*1.42f,9.85f,0);
    hem[i].loft(8,24,-.1f,0,0,1.57f,1.75f,2.0f,s*.18f,0,1.74f,1.84f,4.1f,s*.40f,.12f,1.83f,1.78f,4.6f,s*.37f,.18f,1.64f,1.61f);
    arm[i]=body.child(s*3.86f,.35f,0);
    arm[i].loft(8,24,-.85f,0,0,1.23f,1.31f,.55f,0,0,1.75f,1.67f,2.6f,0,0,1.60f,1.50f,4.8f,0,0,1.05f,1.05f);
    fore[i]=arm[i].child(0,4.65f,0);
    fore[i].loft(8,24,-.25f,0,0,1.12f,1.13f,1.55f,0,0,1.29f,1.22f,3.75f,0,0,.87f,.87f,4.5f,0,0,.79f,.81f);
    fore[i].loft(3,24,3.9f,0,0,.88f,.90f,4.3f,0,0,.87f,.89f);
    fore[i].oval(6,0,5.12f,-.1f,.78f,1.03f,.66f);
    for(int j=0;j<4;j++)fore[i].oval(6,-.50f+j*.34f,5.83f,-.31f,.17f,.53f,.24f);
    Part shoulder=arm[i].child(s*1.38f,1.5f,-.15f);shoulder.ry=s*1.2f;
    shoulder.blade(3,0,-.35f,0,0,1.8f,0,.25f);Part sr=shoulder.child(0,2.1f,0);loop(sr,.30f,.48f,.12f);
    leg[i]=root.child(s*1.62f,11.4f,0);
    leg[i].loft(8,24,-.35f,0,0,1.52f,1.48f,2.9f,0,0,1.34f,1.31f,5.6f,0,0,1.02f,1.04f);
    shin[i]=leg[i].child(0,5.4f,0);
    shin[i].loft(8,24,-.3f,0,0,1.11f,1.09f,1.5f,0,0,1.24f,1.23f,4.1f,0,0,.91f,.93f,5.75f,0,0,1.10f,1.09f);
    shin[i].loft(9,24,5.5f,0,-.05f,.95f,.99f,6.55f,0,-.55f,1.10f,1.60f,7.2f,0,-.64f,1.13f,1.69f);
    shin[i].blade(3,s*.85f,5.7f,-.2f,s*.95f,6.75f,-.30f,.15f);
   }
  }
  @Override public void setupAnim(JojoMob e,float limb,float amount,float age,float yaw,float pitch){
   head.ry=yaw*.01745f;head.rx=pitch*.015f;body.ry=(float)Math.sin(limb*.33)*amount*.06f;
   float pose=amount<.08f?(float)Math.pow(Math.max(0,Math.sin(age*.025)),8):0;
   for(int i=0;i<2;i++){int s=i==0?-1:1;float walk=(float)Math.cos(limb*.666+i*Math.PI)*amount;
    arm[i].rx=-walk*.58f+(i==1?-.20f*pose:0);arm[i].rz=-s*.10f+(i==1?-1.0f*pose:0);
    fore[i].rx=i==1?-.42f*pose:0;fore[i].rz=i==1?.9f*pose:0;
    leg[i].rx=walk*.65f;shin[i].rx=Math.max(0,-walk)*.29f;
    hem[i].rx=walk*.09f;pulls[i].rx=(float)Math.sin(age*.15+i)*(.035f+amount*.12f);
   }
   for(int j=0;j<locks.size();j++)locks.get(j).rz=(float)Math.sin(age*.10+j)*.016f;
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<JojoMob,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.36f);}
  @Override public ResourceLocation getTextureLocation(JojoMob e){return new ResourceLocation(Noctis.ID,"textures/entity/bucciarati_sculpted.png");}
 }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(242,242,235),(225,228,223),(166,171,168),(222,175,64),(167,116,38),(230,184,145),(230,184,145),(22,27,48),(242,242,235),(35,46,52)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def keyhole(u,v):
    # black teardrop/keyhole pattern, staggered on each garment section.
    a=(u*10+.5*(int(v*5)%2))%1-.5;b=(v*5)%1-.5
    return a*a+(b+.12)**2<.012 or (abs(a)<.038 and -.10<b<.19)
for m,base in enumerate(pal):
 for y in range(128):
  v=clamp((y-3)/121)
  for x in range(128):
   u=clamp((x-3)/121);f=abs(u-.5)
   c=blend(base,(55,65,76),.12*v+.15*(1-math.sin(u*math.pi)))
   if m in (0,8):
    fold=math.sin(u*math.pi*7+v*4+math.sin(v*7)*.45)**2
    c=blend(c,(145,154,155),.20*fold)
    if keyhole(u,v):c=(25,27,34)
    if m==0:
     # central open chest panel and lace, tapering down to the jacket fastening.
     lim=.146 if v<.25 else max(0,.146*(.70-v)/.45)
     if .105<v<.70 and f<lim:
      c=blend(pal[6],(137,83,71),.20*math.exp(-(f/.037)**2)+.12*v)
      if v>.32 and f>lim*.48:
       a=abs(math.sin((u*24+v*12)*math.pi));b=abs(math.sin((u*24-v*12)*math.pi))
       if min(a,b)<.20:c=(77,49,41)
      if v>.57 and f<.06 and abs(math.sin(u*70+v*32))<.16:c=(65,40,38)
   if m in (3,4):c=blend((114,72,24),(255,225,134),.28+.64*math.sin(u*math.pi)**2)
   if m==7:
    wave=math.sin(u*math.pi*16+math.sin(v*5)*.4)**2
    c=blend(base,(74,91,142),.22*wave+.38*math.exp(-((v-.31-.04*math.sin(u*14))/.10)**2))
   if m==5:
    c=blend(base,(158,94,74),.16*math.exp(-((v-.70)/.19)**2)+.15*clamp((f-.17)*5))
    for ex in (.397,.603):
     dx=(u-ex)/.066;dy=(v-.51+(.045*dx if ex<.5 else -.045*dx))/.087
     d=abs(dx)**1.7+abs(dy)**1.5
     if d<1:c=(35,30,42)
     if d<.78:c=(248,241,224)
     if abs(dx)<.53 and d<.78:c=blend((47,88,143),(147,193,227),clamp((dy+.2)*.65))
     if abs(dx)<.21 and abs(dy)<.75 and d<.8:c=(25,28,42)
     if (dx+.16)**2+(dy+.24)**2<.078:c=(255,255,255)
     if abs(dx)<1.04 and abs(v-(.365+.039*dx*(1 if ex<.5 else -1)))<.018:c=(35,30,42)
     if abs(dx)<1.05 and abs(dy+.85+.15*dx*(1 if ex<.5 else -1))<.11:c=(34,28,40)
    if .10<f<.18 and abs(v-(.66+f*.5))<.014:c=blend(c,(126,73,64),.55)
    if f<.054 and abs(v-.79+.013*math.cos(f*60))<.012:c=(93,51,49)
    if f<.043 and .80<v<.835:c=blend(c,(174,89,83),.48)
   off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'bucciarati_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Bucciarati: distinctive bob, gold clips, open chest lace, keyhole pattern, articulated golden zipper pulls')
