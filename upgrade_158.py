"""1.5.8: independent sculpted Dante and Bayonetta, preserving combat and summon logic."""
from pathlib import Path
import sys, math, struct, zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
for name,anchor in [('DanteClient.java','e.registerEntityRenderer(Noctis.DANTE.get(),Renderer::new);'),('MoonGuestClient.java','e.registerEntityRenderer(Noctis.BAYONETTA.get(),c->new Renderer(c,0));')]:
 p=java/name;s=p.read_text(encoding='utf-8');assert anchor in s,(name,anchor);p.write_text(s.replace(anchor,''),encoding='utf-8')
(java/'WitchHunterClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
import java.util.*;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class WitchHunterClient {
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
  e.registerEntityRenderer(Noctis.DANTE.get(),c->new R<Dante>(c,false));
  e.registerEntityRenderer(Noctis.BAYONETTA.get(),c->new R<MoonGuest>(c,true));
 }
 static void show(Part p,Part q,boolean on){if(on){if(!p.children.contains(q))p.children.add(q);}else p.children.remove(q);}
 static V ring(float a,float b,float w,float h,float r,float u,float v){
  float ca=(float)Math.cos(a),sa=(float)Math.sin(a),cb=(float)Math.cos(b),sb=(float)Math.sin(b);
  return new V((w+r*cb)*ca,(h+r*cb)*sa,r*sb,u,v,ca*cb,sa*cb,sb);
 }
 static void loop(Part p,int m,float w,float h,float r){
  for(int i=0;i<24;i++)for(int j=0;j<8;j++){
   float a=i*(float)Math.PI/12,A=(i+1)*(float)Math.PI/12,b=j*(float)Math.PI/4,B=(j+1)*(float)Math.PI/4;
   p.faces.add(new Q(ring(a,b,w,h,r,i/24f,j/8f),ring(A,b,w,h,r,(i+1)/24f,j/8f),ring(A,B,w,h,r,(i+1)/24f,(j+1)/8f),ring(a,B,w,h,r,i/24f,(j+1)/8f),m));
  }
 }
 static Part gun(int m){
  Part p=new Part(0,5.1f,-.42f);p.rx=-1.4f;
  p.loft(3,16,-.65f,0,0,.38f,.51f,1.45f,0,0,.39f,.52f);
  Part slide=p.child(0,1.15f,-.25f);slide.rx=(float)Math.PI/2;
  slide.loft(m,20,-.7f,0,0,.48f,.57f,0,0,0,.62f,.64f,2.7f,0,0,.53f,.57f,3.6f,0,0,.47f,.49f);
  slide.loft(4,20,3.1f,0,0,.55f,.58f,3.42f,0,0,.55f,.58f);
  slide.oval(3,0,3.61f,0,.24f,.10f,.24f);
  return p;
 }
 static Part rebellion(){
  Part p=new Part(0,5.1f,-.5f);p.rx=-.95f;
  p.loft(3,20,-2.0f,0,0,.32f,.33f,-.1f,0,0,.34f,.35f,1.1f,0,0,.31f,.32f);
  p.oval(4,0,-2.1f,0,.55f,.53f,.54f);
  p.oval(4,0,1.2f,0,.79f,1.04f,.65f);
  for(int s:new int[]{-1,1}){
   p.oval(3,s*.30f,.99f,-.60f,.20f,.24f,.1f);
   p.blade(4,s*.4f,1.05f,0,s*2.65f,-.35f,0,.89f);
   p.blade(4,s*.62f,1.55f,0,s*2.65f,2.45f,0,.76f);
   p.blade(4,s*1.22f,1.65f,0,s*2.55f,3.3f,0,.55f);
  }
  p.loft(4,28,2.05f,0,0,.62f,.22f,3.3f,0,0,1.12f,.27f,5,0,0,1.16f,.26f,13.5f,0,0,.98f,.20f,16.8f,0,0,.52f,.12f,18.0f,0,0,.025f,.035f);
  p.blade(9,0,3.4f,-.28f,0,16.7f,-.12f,.25f);
  return p;
 }
 static class M<T extends Mob> extends EntityModel<T>{
  final boolean witch;
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1.05f,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shins=new Part[2],cloth=new Part[2],guns=new Part[2];
  final List<Part> locks=new ArrayList<>(),charms=new ArrayList<>();
  final Part sword,backSword;
  M(boolean witch){
   this.witch=witch;
   if(witch){
    // Long-limbed, sculpted black bodysuit with separate chest, waist and hip profiles.
    body.loft(0,40,-1,0,0,1.42f,1.16f,.1f,0,0,3.10f,1.65f,2.4f,0,-.10f,2.91f,1.96f,4.2f,0,0,2.44f,1.55f,7.4f,0,0,1.70f,1.18f,9.8f,0,.10f,2.35f,1.55f,11.05f,0,.12f,2.79f,1.80f);
    body.loft(1,28,-1.2f,0,0,1.2f,1.13f,.4f,0,0,1.42f,1.33f);
    body.loft(6,24,-1.85f,0,0,.99f,.98f,-.75f,0,0,1.15f,1.12f);
    // Gold medallion, red jewel, engraved border; gold seam lines and sleeve decorations.
    body.oval(4,0,2.9f,-2.04f,1.13f,1.15f,.29f);
    body.oval(3,0,2.9f,-2.26f,.86f,.87f,.15f);
    Part med=body.child(0,2.9f,-2.4f);loop(med,4,.84f,.85f,.095f);
    med.oval(2,0,0,-.10f,.33f,.34f,.15f);
    for(int j=0;j<8;j++){double a=j*Math.PI/4;med.oval(4,(float)Math.cos(a)*.63f,(float)Math.sin(a)*.63f,-.10f,.10f,.10f,.06f);}
    for(int s:new int[]{-1,1}){
     body.blade(4,s*1.8f,.15f,-1.33f,s*.85f,2.1f,-1.96f,.17f);
     body.blade(4,s*2.15f,5.1f,-1.1f,s*1.55f,8.9f,-1.12f,.13f);
    }
   }else{
    body.loft(0,32,-1,0,0,1.95f,1.42f,.15f,0,0,4.15f,2.2f,2.65f,0,-.12f,3.95f,2.35f,5.2f,0,0,3.18f,1.95f,8.5f,0,0,2.68f,1.7f,10.7f,0,0,3.10f,1.95f);
    body.oval(1,0,3.7f,-2.04f,2.14f,3.73f,.50f);
    body.loft(1,24,-1.45f,0,0,1.29f,1.2f,.45f,0,0,1.62f,1.48f);
    body.loft(6,20,-1.8f,0,0,1.14f,1.13f,-.95f,0,0,1.29f,1.2f);
    for(int s:new int[]{-1,1}){
     body.blade(2,s*2.6f,-.25f,-1.50f,s*.68f,5.8f,-2.21f,2.0f);
     body.blade(0,s*3.35f,.8f,-1.20f,s*2.23f,7.8f,-1.73f,1.55f);
     Part col=body.child(s*1.72f,-.6f,.35f);col.rz=-s*.25f;
     col.loft(2,22,-3.0f,s*.30f,.12f,.50f,1.05f,-2.2f,s*.15f,0,1.02f,1.5f,-.5f,0,0,1.25f,1.5f,.65f,s*.35f,-.05f,.83f,.95f);
     body.blade(1,s*1.2f,-.55f,-1.63f,s*.18f,3.25f,-2.43f,1.55f);
     body.blade(2,s*3.3f,2.4f,-1.0f,s*2.0f,3.65f,-2.02f,.24f);
    }
    for(int j=0;j<3;j++){float y=2.9f+j*1.92f;body.blade(3,-1.25f,y+.65f,-2.45f,1.95f,y-.5f,-2.11f,.63f);body.oval(4,.62f,y+.02f,-2.46f,.42f,.30f,.16f);}
    body.loft(3,28,9.45f,0,0,2.86f,1.86f,10.6f,0,0,3.10f,1.99f);
    body.oval(4,0,10.02f,-1.98f,.94f,.52f,.22f);
   }
   // Smooth face geometry, distinct facial proportions and asymmetric hair.
   float w=witch?2.95f:3.24f;
   head.loft(5,48,-7.8f,0,.12f,1.42f,1.64f,-7.25f,0,.06f,2.6f,2.45f,-5.6f,0,0,w,2.85f,-3.8f,0,-.06f,w*.97f,2.72f,-2.1f,0,-.12f,witch?2.30f:2.72f,2.36f,-.75f,0,-.20f,witch?1.36f:1.76f,1.65f,0,0,-.25f,.65f,.85f);
   head.loft(6,20,-3.8f,0,-2.55f,.22f,.17f,-2.6f,0,-2.93f,.39f,.46f,-2.04f,0,-2.82f,.32f,.24f);
   for(int s:new int[]{-1,1})head.oval(6,s*w*.95f,-3.37f,.1f,.40f,.83f,.55f);
   head.loft(7,40,-9.1f,.12f,.15f,.52f,.65f,-8.85f,.1f,.12f,2.45f,2.3f,-7.85f,0,.2f,3.38f,3.05f,-6.45f,0,.32f,3.42f,3.06f);
   if(witch){
    // Iconic tall swept black beehive and curved diagonal fringe, red silk ribbons.
    Part up=head.child(0,-7.9f,.55f);
    up.loft(7,32,-5.8f,0,.8f,.05f,.07f,-4.8f,.05f,.65f,.95f,.8f,-3.0f,.15f,.43f,1.66f,1.45f,-1.2f,.18f,.25f,2.42f,2.1f,.3f,0,.1f,2.9f,2.45f);
    up.loft(2,28,-4.55f,.05f,.65f,1.09f,.93f,-4.18f,.06f,.58f,1.25f,1.06f);
    for(int j=0;j<7;j++){Part q=head.child(-2.45f+j*.73f,-7.8f,-2.0f);
     q.loft(7,18,-.5f,0,.50f,.65f,.78f,.6f,.45f,-.35f,.83f,.71f,1.65f,.82f,-.61f,.68f,.47f,2.45f+j*.10f,1.05f,-.45f,.035f,.06f);}
    // Open black spectacle frames, violet hinge crystals, separate bridge and temples.
    for(int s:new int[]{-1,1}){
     Part glasses=head.child(s*1.34f,-4.00f,-2.65f);glasses.ry=-s*.22f;glasses.rz=-s*.12f;loop(glasses,3,1.14f,.58f,.108f);
     glasses.oval(8,s*1.14f,-.14f,-.02f,.17f,.17f,.11f);
     head.blade(3,s*2.4f,-4.12f,-2.36f,s*2.95f,-3.7f,.25f,.20f);
     Part ear=head.child(s*2.9f,-2.9f,.15f);charms.add(ear);loop(ear,4,.18f,.47f,.075f);ear.oval(4,0,.92f,0,.13f,.52f,.12f);
    }
    head.blade(3,-.35f,-4.02f,-2.86f,.35f,-4.02f,-2.86f,.16f);
   }else{
    Part nape=head.child(0,-6.85f,1.76f);
    nape.loft(7,28,-.75f,0,0,2.9f,1.55f,1.2f,0,.48f,3.22f,1.57f,3.6f,0,.7f,3.03f,1.32f,6,0,.6f,1.85f,.55f,7.0f,0,.48f,.72f,.15f);
    for(int j=0;j<9;j++){
     float x=-2.7f+j*.68f;Part q=head.child(x,-8.0f+(j%2)*.13f,-1.85f);locks.add(q);
     float len=j<3?4.4f+j*.32f:5.3f-(j-3)*.38f,sweep=-.95f+j*.10f;
     q.loft(j%3==0?8:7,20,-.55f,0,.45f,.63f,.72f,.48f,sweep*.3f,-.48f,.86f,.84f,1.65f,sweep*.65f,-.95f,.81f,.66f,len*.74f,sweep,-.98f,.56f,.4f,len,sweep*1.25f,-.4f,.025f,.055f);
    }
   }
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    for(int j=0;j<(witch?5:3);j++){
     Part q=head.child(s*(2.65f-j*.12f),-6.4f+j*.30f,.25f+j*.59f);locks.add(q);
     if(witch)q.loft(7,18,-.6f,0,0,.62f,.85f,2,s*.46f,.4f,.80f,.95f,6,s*.58f,1.2f,.84f,.71f,12,s*.71f,1.7f,.62f,.50f,18+j*.7f,s*.9f,2.1f,.03f,.05f);
     else q.loft(7,18,-.55f,0,0,.7f,1.02f,1.2f,s*.5f,-.3f,.85f,1.14f,3.6f,s*.35f,-.1f,.65f,.8f,5.4f+j*.35f,-s*.18f,.5f,.025f,.05f);
    }
    cloth[i]=(witch?head:body).child(s*(witch?1.25f:2.05f),witch?-11.4f:8.8f,witch?1.3f:.92f);
    if(witch)cloth[i].loft(2,20,0,0,0,.45f,.12f,3.5f,s*.9f,2.1f,.58f,.14f,8,s*1.5f,3.4f,.63f,.13f,14,s*1.8f,4.0f,.52f,.11f,20,s*2.4f,4.7f,.035f,.04f);
    else {
     cloth[i].loft(0,28,-.2f,0,0,1.48f,.47f,3.0f,s*.5f,.35f,2.15f,.52f,6.5f,s*1.1f,1.05f,2.65f,.52f,10.3f,s*1.75f,2.2f,2.85f,.49f,14.5f,s*2.4f,3.5f,1.90f,.35f,16.0f,s*2.85f,4.0f,.06f,.08f);
     Part lining=cloth[i].child(0,0,-.33f);lining.loft(2,24,0,0,0,1.35f,.24f,3,s*.5f,.35f,2.0f,.26f,6.5f,s*1.1f,1.05f,2.45f,.25f,10.3f,s*1.75f,2.2f,2.65f,.23f,14.5f,s*2.4f,3.5f,1.7f,.17f,15.7f,s*2.8f,3.94f,.04f,.05f);
    }
    arms[i]=body.child(s*(witch?3.25f:4.05f),.35f,0);
    arms[i].loft(0,26,-.8f,0,0,witch?.91f:1.34f,witch?.98f:1.4f,.65f,0,0,witch?1.24f:1.91f,witch?1.22f:1.79f,2.65f,0,0,witch?1.01f:1.77f,witch?1.02f:1.64f,4.65f,0,0,witch?.69f:1.12f,witch?.72f:1.18f);
    fore[i]=arms[i].child(0,4.55f,0);
    fore[i].loft(1,24,-.30f,0,0,witch?.75f:1.19f,witch?.75f:1.2f,1.55f,0,0,witch?.94f:1.4f,witch?.92f:1.34f,3.9f,0,0,witch?.58f:.90f,witch?.62f:.91f);
    fore[i].loft(witch?4:3,22,3.7f,0,0,witch?.65f:.97f,witch?.66f:.98f,4.1f,0,0,witch?.63f:.91f,witch?.65f:.94f);
    fore[i].oval(3,0,4.95f,-.12f,witch?.66f:.94f,1.08f,.70f);
    for(int j=0;j<4;j++)fore[i].oval(6,-.51f+j*.34f,5.56f,-.36f,.16f,.54f,.23f);
    legs[i]=root.child(s*(witch?1.38f:1.77f),11.05f,0);
    legs[i].loft(0,26,-.3f,0,0,witch?1.41f:1.62f,witch?1.43f:1.60f,2.45f,0,0,witch?1.18f:1.54f,witch?1.24f:1.45f,5.5f,0,0,witch?.73f:1.08f,witch?.78f:1.12f);
    shins[i]=legs[i].child(0,5.35f,0);
    shins[i].loft(0,24,-.25f,0,0,witch?.81f:1.18f,witch?.83f:1.2f,1.4f,0,0,witch?.94f:1.27f,witch?.95f:1.23f,4.4f,0,0,witch?.56f:.90f,witch?.59f:.93f);
    shins[i].loft(3,24,4.2f,0,0,witch?.64f:1.00f,witch?.68f:1.0f,5.5f,0,0,witch?.60f:.93f,witch?.67f:1.02f,6.7f,0,-.38f,witch?.76f:1.12f,witch?1.18f:1.65f,7.6f,0,-.65f,witch?.82f:1.25f,witch?1.40f:1.86f);
    if(witch){
     Part heel=shins[i].child(0,6.15f,.88f);heel.loft(2,16,0,0,0,.45f,.54f,1.3f,0,.05f,.23f,.27f,1.95f,0,.05f,.17f,.19f);
     shins[i].oval(4,0,6.55f,.85f,.35f,.37f,.25f);
     Part chain=arms[i].child(s*.7f,2.6f,.1f);charms.add(chain);loop(chain,4,.14f,.40f,.07f);chain.oval(4,0,.63f,0,.14f,.32f,.10f);
    }else{
     legs[i].loft(3,24,3.1f,0,0,1.47f,1.39f,3.7f,0,0,1.41f,1.34f);
     shins[i].blade(4,s*.75f,4.2f,-.25f,s*.82f,5.8f,-.40f,.18f);
    }
    guns[i]=gun(witch?2:i==0?4:9);
   }
   sword=rebellion();backSword=rebellion();backSword.x=.15f;backSword.y=-.4f;backSword.z=2.65f;backSword.rx=.03f;backSword.rz=.52f;
  }
  @Override public void setupAnim(T e,float limb,float amount,float age,float yaw,float pitch){
   float a=witch?((MoonGuest)e).action():((Dante)e).action();
   boolean shoot=witch||((Dante)e).mode()==1;
   boolean casting=a>.01f;float walk=amount;
   head.ry=yaw*.01745f;head.rx=pitch*.014f;body.ry=a*(shoot?.16f:.35f);
   for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*walk;
    arms[i].rx=-w*.60f*(1-a)-a*(shoot?1.40f:i==1?1.95f:.2f);
    arms[i].rz=-s*(.12f+(shoot?a*.23f:0));fore[i].rx=-a*(shoot?.28f:i==1?.64f:.1f);
    legs[i].rx=w*.68f;shins[i].rx=Math.max(0,-w)*.26f;
    cloth[i].rx=(witch?.28f:.17f)+walk*.34f+(float)Math.sin(age*.12+i)*.08f;
    cloth[i].rz=-s*(.1f+walk*.08f);
    show(fore[i],guns[i],shoot&&casting);
   }
   for(int j=0;j<locks.size();j++)locks.get(j).rx=walk*.07f+(float)Math.sin(age*.10+j*.5)*.025f;
   for(int j=0;j<charms.size();j++)charms.get(j).rz=(float)Math.sin(age*.16+j)*(.04f+walk*.12f);
   show(fore[1],sword,!witch&&!shoot&&casting);show(body,backSword,!witch&&(!casting||shoot));
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R<T extends Mob> extends MobRenderer<T,M<T>>{
  final boolean witch;R(EntityRendererProvider.Context c,boolean witch){super(c,new M<T>(witch),.40f);this.witch=witch;}
  @Override protected void scale(T e,PoseStack p,float partial){if(witch)p.scale(.99f,1.15f,.99f);else p.scale(1.02f,1.02f,1.02f);}
  @Override public ResourceLocation getTextureLocation(T e){return new ResourceLocation(Noctis.ID,"textures/entity/"+(witch?"bayonetta":"dante")+"_sculpted.png");}
 }
}''',encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
for witch in (False,True):
 pal=[(24,24,34) if witch else (153,29,44),(28,29,39),(122,21,44) if witch else (83,16,30),(21,20,29),(206,166,80) if witch else (181,192,207),(241,198,174),(241,198,174),(20,20,29) if witch else (224,224,237),(131,78,160) if witch else (245,243,251),(56,59,71)]
 pix=bytearray(W*H*4)
 for m,base in enumerate(pal):
  for y in range(128):
   v=clamp((y-3)/121)
   for x in range(128):
    u=clamp((x-3)/121);f=abs(u-.5)
    c=blend(base,(21,15,27),.10*v+.12*(1-math.sin(u*math.pi)))
    if m in (0,1,2,3):
     fold=math.sin(u*math.pi*7+v*3+math.sin(v*7)*.65)**2
     c=blend(c,(88,90,112) if witch else (211,79,84) if m==0 else (92,64,82),.17*fold)
     if m==0:
      if abs(v-.04)<.009 or abs(v-.95)<.012:c=blend(c,(140,111,65) if witch else (75,16,29),.6)
      if abs(u-.18)<.008 or abs(u-.82)<.008:c=blend(c,(75,71,92) if witch else (92,20,35),.5)
    if m==4:c=blend((108,77,34) if witch else (83,101,123),(249,223,149) if witch else (243,249,255),.25+.70*math.sin(u*math.pi)**2)
    if m in (7,8):
     flow=math.sin(u*math.pi*15+math.sin(v*6)*1.2)**2
     c=blend(base,(89,88,115) if witch else (255,255,255),.30*flow+.22*math.exp(-((v-.29)/.13)**2))
     c=blend(c,(12,13,23) if witch else (128,129,158),.15*(1-flow))
    if m==5:
     c=blend(base,(173,102,105),.13*math.exp(-((v-.71)/.16)**2)+.14*clamp((f-.17)*5))
     for ex in (.391,.609):
      dx=(u-ex)/(.072 if witch else .067);dy=(v-.50+(.048*dx if ex<.5 else -.048*dx))/(.087 if witch else .078)
      d=abs(dx)**1.8+abs(dy)**1.6
      if witch and d<1.23:c=blend(c,(113,67,112),.40)
      if d<1:c=(40,24,35)
      if d<.80:c=(248,239,229)
      if abs(dx)<.53 and d<.78:c=blend((102,112,120) if witch else (61,101,145),(179,199,201) if witch else (144,187,219),clamp((dy+.2)*.65))
      if abs(dx)<.22 and d<.74:c=(25,26,38)
      if (dx+.16)**2+(dy+.22)**2<.075:c=(255,255,251)
      if abs(dx)<1.06 and abs(v-(.36+.035*dx*(1 if ex<.5 else -1)))<.016:c=(38,24,39) if witch else (126,117,130)
      if witch and abs(dy+.85+.18*dx*(1 if ex<.5 else -1))<.13 and abs(dx)<1.18:c=(31,18,30)
     if witch:
      if f<.055 and abs(v-.80+.014*math.cos(f*58))<.022:c=(119,31,47)
      if f<.047 and .81<v<.837:c=(183,63,81)
      if ((u-.571)/.005)**2+((v-.864)/.008)**2<1:c=(54,31,34)
     else:
      if f<.061 and abs(v-.80+.012*math.cos(f*58))<.012:c=(131,63,69)
      if .08<f<.19 and abs(v-(.68+f*.39))<.012:c=blend(c,(129,71,70),.39)
    off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
 (assets/(('bayonetta' if witch else 'dante')+'_sculpted.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Dante and Bayonetta: new curved models, bespoke costumes, glasses and jewelry, articulated combat and original summon behavior')
