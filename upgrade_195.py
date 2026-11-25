"""1.7.30: Gold Experience bespoke faceted armor, spectral rendering and golden aura."""
from pathlib import Path
import sys,math
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'JojoClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.GOLD_EXPERIENCE.get(),c->new Renderer(c,5));'
assert a in s
s=s.replace(a,'e.registerEntityRenderer(Noctis.GOLD_EXPERIENCE.get(),GoldExperienceClient.Renderer::new);',1);p.write_text(s,encoding='utf-8')
(java/'GoldExperienceClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.Q;
import it.noctis.magic.SculptedGuestsClient.V;
public final class GoldExperienceClient{
 static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/gold_experience_spirit.png");
 static final class Renderer extends MobRenderer<JojoMob,Model>{
  Renderer(EntityRendererProvider.Context c){super(c,new Model(),0f);}
  @Override public ResourceLocation getTextureLocation(JojoMob e){return TEX;}
  @Override protected void scale(JojoMob e,PoseStack p,float partial){p.scale(1.26f,1.26f,1.26f);}
 }
 static final class Model extends EntityModel<JojoMob>{
  final Part root=new Part(0,0,0),torso=root.child(0,0,0),head=torso.child(0,-.4f,0),aura=new Part(0,0,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shins=new Part[2],wisps=new Part[8];
  float pulse;
  // Faceted sections, never spherical primitives.
  void plate(Part p,int m,float... r){CinnabarClient.Model.angular(p,m,m,8,r[0],r[r.length-5],r);}
  void portrait(Part p,int m,int f,float... r){CinnabarClient.Model.angular(p,m,f,6.2f,r[0],r[r.length-5],r);}
  void insignia(Part p,float x,float y,float z,float size){
   // Polygonal violet scarab with a narrow center seam and six raised dark spots.
   Part q=p.child(x,y,z);
   plate(q,4,-size,0,0,size*.46f,.18f,-size*.65f,0,-.13f,size*.86f,.27f,0,0,-.21f,size,.38f,size*.65f,0,-.12f,size*.82f,.28f,size,0,0,size*.40f,.13f);
   q.blade(5,0,-size*.83f,-.61f,0,size*.86f,-.62f,.12f);
   for(int side:new int[]{-1,1})for(int j=0;j<3;j++){
    float yy=(j-1)*size*.50f;
    q.blade(5,side*size*.39f,yy-.12f,-.62f,side*size*.47f,yy+.17f,-.61f,.27f);
   }
  }
  void panel(Part p,int m,float x,float y,float z,float X,float Y,float Z,float w){p.blade(m,x,y,z,X,Y,Z,w);}
  Model(){super(RenderType::entityTranslucent);
   // Dark anatomical underlayer, with separate metallic golden armor.
   plate(torso,5,-.5f,0,0,2.75f,1.7f,1.0f,0,0,3.65f,2.05f,3.5f,0,0,3.12f,1.95f,6.0f,0,0,2.30f,1.52f,8.3f,0,0,1.83f,1.30f,10.1f,0,0,2.37f,1.49f,11.5f,0,0,2.75f,1.62f);
   // Solid orange-gold breastplate with a deep V neckline and a broad upper shoulder yoke.
   for(int side:new int[]{-1,1}){
    plate(torso,10,-.22f,side*1.95f,-.88f,1.02f,.72f,.48f,side*1.95f,-1.10f,1.60f,1.00f,1.62f,side*1.85f,-1.23f,1.63f,.98f,2.62f,side*1.60f,-1.37f,1.37f,.84f,3.30f,side*1.30f,-1.48f,.84f,.48f);
    panel(torso,5,side*.96f,-.15f,-1.70f,side*.45f,1.40f,-2.06f,.40f);
    panel(torso,3,side*1.14f,-.22f,-1.85f,side*.38f,1.55f,-2.24f,.22f);
    for(int j=0;j<3;j++){
     float yy=.48f+j*.72f;float xx=side*(1.96f-j*.18f);
     panel(torso,5,xx-.32f,yy,-2.18f,xx+.32f,yy+.06f,-2.18f,.18f);
     panel(torso,3,xx-.29f,yy-.03f,-2.22f,xx+.29f,yy+.03f,-2.22f,.08f);
    }
   }
   for(int side:new int[]{-1,1}){
    // Pectoral and abdominal shields, black gaps, golden ribs.
    panel(torso,10,side*.62f,.60f,-2.18f,side*2.90f,1.52f,-2.12f,1.75f);
    panel(torso,5,side*2.38f,3.05f,-1.89f,side*.77f,7.87f,-1.51f,.72f);
    panel(torso,1,side*1.95f,3.3f,-1.91f,side*.76f,7.35f,-1.60f,1.55f);
    panel(torso,2,side*2.65f,3.35f,-1.57f,side*1.62f,8.5f,-1.18f,.77f);
    panel(torso,3,side*2.52f,.30f,-1.65f,side*.88f,1.03f,-2.13f,.38f);
    insignia(torso,side*2.12f,2.60f,-2.43f,.83f);
    for(int j=0;j<3;j++)panel(torso,5,side*(1.83f+j*.24f),.68f+j*.36f,-2.14f,side*(2.06f+j*.24f),.85f+j*.36f,-2.14f,.14f);
   }
   for(int side:new int[]{-1,1}){
    plate(torso,1,3.17f,side*.94f,-1.68f,.70f,.48f,4.25f,side*.98f,-1.86f,.87f,.52f,5.65f,side*.73f,-1.59f,.64f,.42f,7.50f,side*.46f,-1.39f,.34f,.34f);
    panel(torso,3,side*1.52f,3.36f,-2.09f,side*.43f,7.37f,-1.78f,.26f);
   }
   panel(torso,1,0,3.24f,-2.02f,0,8.22f,-1.54f,.78f);
   panel(torso,5,0,3.35f,-2.20f,0,8.1f,-1.75f,.17f);
   plate(torso,2,8.7f,0,0,2.15f,1.50f,9.5f,0,0,2.68f,1.77f,10.25f,0,0,2.52f,1.66f);
   panel(torso,1,0,9.65f,-1.82f,0,12.25f,-1.31f,1.90f);
   // Curved silver waist rails and purple hip beetles.
   for(int side:new int[]{-1,1}){
    insignia(torso,side*2.50f,9.36f,-1.36f,.83f);
    for(int j=0;j<5;j++){
     float x=side*(1.3f+j*.48f),X=side*(1.78f+j*.48f);
     float yy=9.1f+j*.49f,Y=9.1f+(j+1)*.49f;
     panel(torso,8,x,yy,-1.85f,X,Y,-1.63f,.46f);
     panel(torso,11,x,yy+.28f,-1.91f,X,Y+.28f,-1.69f,.14f);
    }
   }
   // Neck and angular helmet with separate face mask and visor.
   plate(torso,5,-1.4f,0,0,.88f,.91f,0,0,0,1.05f,1.02f);
   portrait(head,2,6,-5.72f,0,.06f,1.18f,1.12f,-5.25f,0,.06f,2.07f,1.76f,-3.92f,0,0,2.22f,1.91f,-2.45f,0,-.09f,2.08f,1.76f,-1.03f,0,-.22f,1.57f,1.35f,-.12f,0,-.32f,.80f,.84f);
   portrait(head,1,7,-8.50f,0,.34f,.25f,.43f,-8.10f,0,.19f,1.34f,1.23f,-7.25f,0,.11f,2.42f,2.06f,-6.10f,0,.02f,2.85f,2.48f,-5.28f,0,-.03f,2.77f,2.45f,-4.72f,0,.04f,2.23f,2.12f);
   // Raised projecting gold forehead guard, separate from the dome.
   portrait(head,3,1,-6.73f,0,-2.03f,.36f,.26f,-6.35f,0,-2.27f,.90f,.42f,-5.62f,0,-2.39f,1.28f,.53f,-4.65f,0,-2.37f,1.31f,.54f,-4.08f,0,-2.31f,.94f,.35f);
   panel(head,5,0,-8.30f,-.70f,0,-6.60f,-2.41f,.22f);
   panel(head,3,0,-8.24f,-.82f,0,-6.72f,-2.49f,.13f);
   panel(head,5,-1.25f,-4.33f,-2.69f,1.25f,-4.33f,-2.69f,.48f);
   // Central crest and visor frame; no human cartoon eyes.
   panel(head,3,0,-6.42f,-2.69f,0,-4.55f,-2.91f,.45f);
   panel(head,5,-2.03f,-4.39f,-1.62f,-.25f,-3.89f,-2.03f,.77f);
   panel(head,5,2.03f,-4.39f,-1.62f,.25f,-3.89f,-2.03f,.77f);
   for(int side:new int[]{-1,1}){
    panel(head,4,side*.16f,-4.10f,-2.71f,side*1.77f,-4.43f,-2.18f,.36f);
    panel(head,1,side*2.12f,-5.36f,-1.55f,side*2.17f,-2.74f,-.55f,1.03f);
    panel(head,5,side*1.77f,-2.98f,-1.43f,side*.95f,-1.25f,-1.48f,.26f);
    // Black spiral grooves on the helmet crown, made of connected engraved strips.
    float ox=side*1.65f,oy=-6.78f;
    for(int j=0;j<14;j++){
     double a=j*.44,b=(j+1)*.44;float r=.07f+j*.043f,rr=r+.043f;
     panel(head,5,ox+side*(float)Math.cos(a)*r,oy+(float)Math.sin(a)*r,-2.45f,ox+side*(float)Math.cos(b)*rr,oy+(float)Math.sin(b)*rr,-2.45f,.13f);
    }
   }
   panel(head,1,0,-3.45f,-1.92f,0,-2.55f,-2.15f,.45f);
   panel(head,5,-.46f,-1.66f,-1.41f,.46f,-1.66f,-1.41f,.15f);
   panel(head,4,0,-1.46f,-1.40f,0,-.94f,-1.23f,.39f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    Part a=arms[i]=torso.child(s*3.62f,.64f,0);
    plate(a,0,-.72f,0,0,1.18f,1.34f,-.05f,s*.13f,0,1.65f,1.54f,1.7f,s*.11f,0,1.49f,1.42f,3.2f,0,0,1.04f,1.05f,5.9f,0,0,.76f,.79f);
    // Ivory spiral shoulder fins and segmented gold upper arm.
    plate(a,10,-.75f,0,0,1.52f,1.49f,.35f,s*.13f,0,1.83f,1.68f,1.78f,s*.11f,0,1.66f,1.54f);
    plate(a,8,-3.65f,s*1.28f,-.55f,.035f,.05f,-2.65f,s*1.01f,-.93f,.39f,.33f,-1.48f,s*.63f,-1.15f,.74f,.45f,-.10f,s*.49f,-1.28f,1.02f,.51f,.83f,s*.50f,-1.18f,.72f,.32f);
    panel(a,11,s*1.22f,-3.02f,-.82f,s*.63f,-.05f,-1.82f,.20f);
    for(int j=0;j<13;j++){
     double q=j*.47,r=(j+1)*.47;float rr=.045f+j*.047f,rr2=rr+.047f;
     panel(a,5,s*.59f+(float)Math.cos(q)*rr,.28f+(float)Math.sin(q)*rr,-1.77f,s*.59f+(float)Math.cos(r)*rr2,.28f+(float)Math.sin(r)*rr2,-1.77f,.11f);
    }
    panel(a,1,0,2.3f,-1.12f,0,5.55f,-.78f,1.26f);
    panel(a,5,s*.75f,2.55f,-.76f,s*.42f,5.60f,-.57f,.23f);
    Part f=fore[i]=a.child(0,5.85f,0);
    plate(f,2,-.42f,0,0,.80f,.82f,.64f,0,0,1.02f,1.04f,2.10f,0,0,.91f,.91f,3.65f,0,0,.60f,.65f,4.15f,0,0,.64f,.68f);
    panel(f,1,0,.44f,-1.04f,0,3.8f,-.69f,1.09f);
    panel(f,5,s*.64f,.48f,-.73f,s*.39f,3.65f,-.59f,.18f);
    insignia(f,0,4.18f,-.90f,.63f);
    plate(f,0,4.08f,0,0,.64f,.66f,4.7f,0,-.10f,.88f,.62f,5.5f,0,-.22f,.78f,.54f,5.72f,0,-.25f,.52f,.42f);
    for(int j=0;j<3;j++)panel(f,5,-.38f+j*.38f,5.0f,-.78f,-.38f+j*.38f,5.53f,-.73f,.09f);
    Part leg=legs[i]=root.child(s*1.44f,11,0);
    plate(leg,0,-.36f,0,0,1.39f,1.52f,1.3f,s*.14f,0,1.48f,1.52f,3.0f,s*.09f,0,1.30f,1.36f,5.4f,0,0,.85f,.90f,6.3f,0,0,.83f,.87f);
    panel(leg,1,s*.38f,.42f,-1.43f,0,5.70f,-.94f,1.56f);
    panel(leg,5,-s*.65f,.56f,-1.27f,-s*.36f,5.65f,-.79f,.43f);
    insignia(leg,s*.79f,.65f,-1.48f,.60f);
    panel(leg,8,s*.90f,.80f,-1.58f,s*2.43f,3.0f,-.81f,.78f);
    Part shin=shins[i]=leg.child(0,6.1f,0);
    plate(shin,2,-.35f,0,0,.89f,.94f,.48f,0,0,1.04f,1.07f,2.15f,0,.08f,1.04f,1.09f,4.8f,0,0,.63f,.69f,6.15f,0,0,.57f,.66f);
    insignia(shin,0,.45f,-1.33f,.82f);
    panel(shin,1,0,1.13f,-1.1f,0,5.74f,-.73f,1.10f);
    panel(shin,5,s*.69f,1.45f,-.83f,s*.36f,5.6f,-.58f,.22f);
    for(int j=0;j<3;j++)panel(shin,5,-.41f,2.4f+j*.77f,-1.02f,.12f,2.54f+j*.77f,-1.04f,.10f);
    plate(shin,1,5.83f,0,-.09f,.62f,.71f,6.46f,0,-.52f,.84f,1.36f,7.22f,0,-.62f,.88f,1.55f,7.48f,0,-.57f,.60f,1.30f);
   }
   // Wispy, tapering energy ribbons, not a spherical aura shell.
   for(int i=0;i<wisps.length;i++){
    Part q=wisps[i]=aura.child(0,0,0);
    float a=i*(float)Math.PI/4;float x=(float)Math.cos(a),z=(float)Math.sin(a);
    for(int j=0;j<9;j++){
     float y=23-j*3.8f,Y=y-3.8f;
     float r=4.8f+1.10f*(float)Math.sin(j*.7f+i),rr=4.8f+1.10f*(float)Math.sin((j+1)*.7f+i);
     float w=.65f*(float)Math.sin(Math.PI*(j+.5)/9),ww=.65f*(float)Math.sin(Math.PI*(j+1.5)/9);
     q.faces.add(new Q(new V(x*r-z*w,y,z*r+x*w,0,j/9f,x,0,z),new V(x*rr-z*ww,Y,z*rr+x*ww,0,(j+1)/9f,x,0,z),new V(x*rr+z*ww,Y,z*rr-x*ww,1,(j+1)/9f,x,0,z),new V(x*r+z*w,y,z*r-x*w,1,j/9f,x,0,z),9));
    }
   }
  }
  @Override public void setupAnim(JojoMob e,float limb,float amount,float age,float yaw,float pitch){
   float hit=e.punchPose();pulse=.55f+.30f*(float)Math.sin(age*.15f);
   root.y=-1.8f+(float)Math.sin(age*.12f)*.65f;
   torso.ry=.12f+(float)Math.sin(age*.08f)*.035f+hit*.24f*(float)Math.sin(age*1.7f);
   head.ry=yaw*.01745f;head.rx=pitch*.01745f;head.rz=-.045f;
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;float swing=(float)Math.cos(age*1.8f+i*Math.PI);
    float attack=hit*(.55f+.45f*swing);
    arms[i].rx=(i==0?-.30f:-.17f)-attack*1.65f;
    arms[i].rz=-s*(i==0?.28f:.56f)+s*.26f*attack;
    fore[i].rx=(i==0?-.66f:-1.25f)*(1-attack);
    fore[i].rz=s*(i==0?.08f:.56f)*(1-attack);
    legs[i].rx=(i==0?-.18f:.22f)+(float)Math.sin(age*.13f+i)*.045f;
    legs[i].rz=s*-.08f;shins[i].rx=i==0?.24f:.47f;
   }
   // Reset every optional joint before evaluating a pose; attack poses retain priority.
   torso.rx=0;torso.rz=0;
   for(int i=0;i<2;i++){arms[i].ry=0;fore[i].ry=0;legs[i].ry=0;shins[i].rz=0;}
   if(hit<.015f&&amount<.12f&&e.hurtTime==0){
    float clock=age+(e.getId()%97)*17f;
    int cycle=(int)(clock/160f),pose=Math.floorMod(cycle,4);
    float local=clock-cycle*160f;
    // A short flourish, long hold and eased release, followed by a normal idle.
    float t=Math.max(0,Math.min(1,Math.min((local-22f)/16f,(137f-local)/16f)));
    t=t*t*(3f-2f*t);
    float[] base={torso.rx,torso.ry,torso.rz,head.rz,arms[0].rx,arms[0].rz,fore[0].rx,fore[0].rz,arms[1].rx,arms[1].rz,fore[1].rx,fore[1].rz,legs[0].rx,legs[0].rz,legs[1].rx,legs[1].rz,shins[0].rx,shins[1].rx};
    if(pose==0){
     // Classic hand at the hip, opposite arm lowered, tilted helmet and bent knee.
     torso.rz=.14f*t;torso.ry+=.25f*t;head.rz-=.10f*t;
     arms[0].rz=.68f*t+.28f*(1-t);arms[0].rx=-.20f*t;
     fore[0].rz=-1.16f*t;fore[0].rx=-.46f*t;
     arms[1].rx=.10f*t;arms[1].rz=-.14f-.10f*t;fore[1].rx=-.26f;
     legs[0].rz=.20f*t;legs[1].rx=.25f*t;shins[1].rx=.45f*t;
    }else if(pose==1){
     // Stand's raised hand near the face, with the other hand angled across the waist.
     torso.ry-=.32f*t;torso.rz=-.10f*t;head.rz+=.16f*t;
     arms[1].rx=-1.12f*t-.17f*(1-t);arms[1].rz=-.52f*t-.22f;
     fore[1].rx=-1.52f*t-.30f*(1-t);fore[1].rz=.65f*t;
     arms[0].rz=.45f*t+.22f;fore[0].rz=-.83f*t;fore[0].rx=-.68f*t;
     legs[1].rz=-.18f*t;
    }else if(pose==2){
     // Wide asymmetric arm extension and contrapposto.
     torso.rz=.13f*t;torso.rx=-.08f*t;head.rz=-.12f*t;
     arms[1].rz=-1.14f*t-.20f;arms[1].rx=-.24f*t;fore[1].rx=-.42f*t;
     arms[0].rz=.62f*t+.20f;fore[0].rz=-1.02f*t;fore[0].rx=-.50f*t;
     legs[0].rz=.16f*t;legs[1].rx=.33f*t;shins[1].rx=.40f*t;
    }else{
     // Guard stance with one fist before the chest and the other near the shoulder.
     torso.ry+=.38f*t;head.rz+=.10f*t;
     arms[0].rx=-.93f*t-.20f;fore[0].rx=-1.32f*t;fore[0].rz=-.45f*t;
     arms[1].rx=-.65f*t-.15f;arms[1].rz=-.61f*t-.18f;fore[1].rx=-1.05f*t;
     legs[0].rx=-.26f*t;legs[1].rx=.27f*t;
    }
    torso.rx=base[0]+(torso.rx-base[0])*t;torso.ry=base[1]+(torso.ry-base[1])*t;torso.rz=base[2]+(torso.rz-base[2])*t;head.rz=base[3]+(head.rz-base[3])*t;
    for(int i=0;i<2;i++){
     int j=4+i*4,k=12+i*2;
     arms[i].rx=base[j]+(arms[i].rx-base[j])*t;arms[i].rz=base[j+1]+(arms[i].rz-base[j+1])*t;
     fore[i].rx=base[j+2]+(fore[i].rx-base[j+2])*t;fore[i].rz=base[j+3]+(fore[i].rz-base[j+3])*t;
     legs[i].rx=base[k]+(legs[i].rx-base[k])*t;legs[i].rz=base[k+1]+(legs[i].rz-base[k+1])*t;
     shins[i].rx=base[16+i]+(shins[i].rx-base[16+i])*t;
    }
   }
   aura.y=root.y; aura.ry=age*.025f;
   for(int i=0;i<wisps.length;i++){wisps[i].y=(float)Math.sin(age*.16f+i)*1.45f;wisps[i].ry=(float)Math.sin(age*.09f+i)*.10f;}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){
   root.draw(p,v,LightTexture.pack(Math.max(10,LightTexture.block(light)),Math.max(10,LightTexture.sky(light))),overlay,r,g,b,a);
   aura.draw(p,v,LightTexture.FULL_BRIGHT,overlay,1f,.92f,.65f,a*pulse);
  }
 }
}''',encoding='utf-8')
# Hand-painted atlas with bright gold edges, deep engraved shadow, purple scarabs and ivory fins.
im=Image.new('RGBA',(1024,512))
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for m in range(12):
 for y in range(128):
  v=max(0,min(1,(y-3)/121))
  for x in range(128):
   u=max(0,min(1,(x-3)/121));f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   alpha=255
   if m in (0,1,2,3,6,7,10):
    base={0:(224,157,44),1:(255,229,156),2:(204,127,29),3:(255,246,200),6:(247,220,153),7:(248,218,135),10:(243,154,31)}[m]
    c=mix(base,(86,45,15),.25*f+.11*v)
    c=mix(c,(255,244,196),.48*g(.31,.31,.20,.46))
    c=mix(c,(255,247,213),.35*g(.17,.28,.043,.32))
    c=mix(c,(77,49,27),.25*max(0,math.sin(u*16+v*1.4))**10)
    if m==7:
     # Helmet's curved dark-gold engraved channels.
     for side in (-1,1):
      xx=.5+side*.22;dx=u-xx
      if abs(v-(.30+.58*dx*dx+.12*side*dx))<.012:c=(91,55,25)
    if m==6:
     # Narrow shadowed mouth and cheek planes. Visor is actual geometry.
     c=mix(c,(104,68,38),.29*g(.50,.42,.28,.13))
     if abs(u-.5)<.078 and abs(v-.78)<.013:c=(48,34,28)
   elif m==4:
    c=mix((48,16,77),(147,75,192),.38+.35*math.sin(u*math.pi)**2)
    c=mix(c,(236,183,255),.75*g(.28,.27,.13,.19))
    c=mix(c,(36,11,59),.42*v)
   elif m==5:
    c=mix((19,15,23),(75,48,39),.25*math.sin(u*math.pi)**2)
   elif m in (8,11):
    c=mix((91,111,123),(251,250,236),.45+.48*math.sin(u*math.pi)**2)
    c=mix(c,(255,255,241),.36*g(.32,.38,.17,.40))
   else:
    c=mix((248,143,36),(255,249,188),max(0,1-f*2)**2)
    alpha=round(205*max(0,1-f*2)**2.4*max(0,math.sin(v*math.pi))**.8)
   im.putpixel((m%8*128+x,m//8*128+y),(*c,alpha))
im.save(assets/'textures/entity/gold_experience_spirit.png')
# Extra server-side floating golden sparks, visible independently of the translucent model.
p=java/'JojoMob.java';s=p.read_text(encoding='utf-8')
a='if(!stand()){JojoWorldPowers.tick(this,l);return;}'
assert a in s
s=s.replace(a,a+'''
        if(variant()==5&&tickCount%8==0){
            var gold=new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(1f,.77f,.21f),.85f);
            for(int i=0;i<3;i++){
                double a=tickCount*.14+i*Math.PI*2/3;
                l.sendParticles(gold,getX()+Math.cos(a)*.48,getY()+.35+(tickCount%32)/16.0,getZ()+Math.sin(a)*.48,2,.12,.12,.12,.015);
            }
            // No opaque white flashes obscuring the armor.
        }
''',1);p.write_text(s,encoding='utf-8')
print('Gold Experience: original faceted golden armor, black visor, violet scarabs, shoulder fins, spectral translucent body and animated aura ribbons.')
