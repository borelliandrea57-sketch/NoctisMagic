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
  @Override protected void scale(JojoMob e,PoseStack p,float partial){p.scale(1.12f,1.12f,1.12f);}
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
   // Muscular athletic silhouette: wide chest, tapered waist, curved armor ridges.
   plate(torso,0,-.5f,0,0,2.75f,1.7f,1.0f,0,0,3.65f,2.05f,3.5f,0,0,3.12f,1.95f,6.0f,0,0,2.30f,1.52f,8.3f,0,0,1.83f,1.30f,10.1f,0,0,2.37f,1.49f,11.5f,0,0,2.75f,1.62f);
   for(int side:new int[]{-1,1}){
    // Pectoral and abdominal shields, black gaps, golden ribs.
    panel(torso,1,side*.50f,.60f,-1.94f,side*2.83f,1.52f,-2.05f,2.4f);
    panel(torso,5,side*2.38f,3.05f,-1.89f,side*.77f,7.87f,-1.51f,.72f);
    panel(torso,1,side*1.95f,3.3f,-1.91f,side*.76f,7.35f,-1.60f,1.55f);
    panel(torso,2,side*2.65f,3.35f,-1.57f,side*1.62f,8.5f,-1.18f,.77f);
    panel(torso,3,side*2.52f,.30f,-1.65f,side*.88f,1.03f,-2.13f,.38f);
    insignia(torso,side*2.28f,2.15f,-2.08f,.63f);
    for(int j=0;j<3;j++)panel(torso,5,side*(1.83f+j*.24f),.68f+j*.36f,-2.14f,side*(2.06f+j*.24f),.85f+j*.36f,-2.14f,.14f);
   }
   panel(torso,1,0,3.24f,-2.02f,0,8.22f,-1.54f,1.36f);
   panel(torso,5,0,3.35f,-2.20f,0,8.1f,-1.75f,.17f);
   plate(torso,2,8.7f,0,0,2.15f,1.50f,9.5f,0,0,2.68f,1.77f,10.25f,0,0,2.52f,1.66f);
   panel(torso,1,0,9.65f,-1.82f,0,12.25f,-1.31f,1.90f);
   // Neck and angular helmet with separate face mask and visor.
   plate(torso,5,-1.4f,0,0,.88f,.91f,0,0,0,1.05f,1.02f);
   portrait(head,2,6,-5.72f,0,.06f,1.18f,1.12f,-5.25f,0,.06f,2.07f,1.76f,-3.92f,0,0,2.22f,1.91f,-2.45f,0,-.09f,2.08f,1.76f,-1.03f,0,-.22f,1.57f,1.35f,-.12f,0,-.32f,.80f,.84f);
   portrait(head,0,7,-7.80f,0,.34f,.66f,.79f,-7.4f,0,.19f,1.64f,1.49f,-6.46f,0,.11f,2.47f,2.12f,-5.32f,0,.02f,2.69f,2.24f,-4.66f,0,-.03f,2.58f,2.18f,-4.21f,0,.04f,2.20f,1.96f);
   // Central crest and visor frame; no human cartoon eyes.
   panel(head,1,0,-7.48f,-.65f,0,-4.36f,-2.28f,1.50f);
   panel(head,5,-2.03f,-4.39f,-1.62f,-.25f,-3.89f,-2.03f,.77f);
   panel(head,5,2.03f,-4.39f,-1.62f,.25f,-3.89f,-2.03f,.77f);
   for(int side:new int[]{-1,1}){
    panel(head,4,side*.25f,-3.97f,-2.14f,side*1.83f,-4.21f,-1.92f,.24f);
    panel(head,1,side*2.12f,-5.36f,-1.55f,side*2.17f,-2.74f,-.55f,1.03f);
    panel(head,5,side*1.77f,-2.98f,-1.43f,side*.95f,-1.25f,-1.48f,.26f);
    // Black spiral grooves on the helmet crown, made of connected engraved strips.
    float ox=side*1.40f,oy=-6.04f;
    for(int j=0;j<14;j++){
     double a=j*.44,b=(j+1)*.44;float r=.07f+j*.043f,rr=r+.043f;
     panel(head,5,ox+side*(float)Math.cos(a)*r,oy+(float)Math.sin(a)*r,-2.12f,ox+side*(float)Math.cos(b)*rr,oy+(float)Math.sin(b)*rr,-2.12f,.10f);
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
    panel(a,8,s*.38f,1.5f,-1.58f,s*1.36f,-2.72f,-1.03f,1.92f);
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
    insignia(f,0,4.07f,-.70f,.46f);
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
    insignia(shin,0,.45f,-1.13f,.65f);
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
   aura.y=root.y; aura.ry=age*.025f;
   for(int i=0;i<wisps.length;i++){wisps[i].y=(float)Math.sin(age*.16f+i)*1.45f;wisps[i].ry=(float)Math.sin(age*.09f+i)*.10f;}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){
   root.draw(p,v,LightTexture.pack(Math.max(10,LightTexture.block(light)),Math.max(10,LightTexture.sky(light))),overlay,r,g,b,a*.87f);
   aura.draw(p,v,LightTexture.FULL_BRIGHT,overlay,1f,.92f,.65f,a*pulse);
  }
 }
}''',encoding='utf-8')
# Hand-painted atlas with bright gold edges, deep engraved shadow, purple scarabs and ivory fins.
im=Image.new('RGBA',(1024,512))
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for m in range(10):
 for y in range(128):
  v=max(0,min(1,(y-3)/121))
  for x in range(128):
   u=max(0,min(1,(x-3)/121));f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   alpha=255
   if m in (0,1,2,3,6,7):
    base={0:(178,114,31),1:(247,222,142),2:(144,89,26),3:(253,239,180),6:(224,193,111),7:(219,177,75)}[m]
    c=mix(base,(67,40,23),.38*f+.22*v)
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
   elif m==8:
    c=mix((130,142,142),(248,243,213),.45+.40*math.sin(u*math.pi)**2)
    c=mix(c,(255,255,241),.36*g(.32,.38,.17,.40))
   else:
    c=mix((248,143,36),(255,249,188),max(0,1-f*2)**2)
    alpha=round(205*max(0,1-f*2)**2.4*max(0,math.sin(v*math.pi))**.8)
   im.putpixel((m%8*128+x,m//8*128+y),(*c,alpha))
im.save(assets/'textures/entity/gold_experience_spirit.png')
# Extra server-side floating golden sparks, visible independently of the translucent model.
p=java/'JojoMob.java';s=p.read_text(encoding='utf-8')
a='if(!(level() instanceof ServerLevel l)||!stand())return;'
assert a in s
s=s.replace(a,a+'''
        if(variant()==5&&tickCount%4==0){
            var gold=new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(1f,.77f,.21f),.85f);
            for(int i=0;i<3;i++){
                double a=tickCount*.14+i*Math.PI*2/3;
                l.sendParticles(gold,getX()+Math.cos(a)*.48,getY()+.35+(tickCount%32)/16.0,getZ()+Math.sin(a)*.48,2,.12,.12,.12,.015);
            }
            if(tickCount%12==0)l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+1.1,getZ(),2,.43,.8,.43,.025);
        }
''',1);p.write_text(s,encoding='utf-8')
print('Gold Experience: original faceted golden armor, black visor, violet scarabs, shoulder fins, spectral translucent body and animated aura ribbons.')
