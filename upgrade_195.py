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
  // UVs are projected onto the actual helmet surface. Engraved spirals never float.
  // Smooth faceted helmet, with slope-aware normals and a continuous side/rear UV.
  V domeV(float[] r,int k,int j,int n,boolean front){
   double a=j*2*Math.PI/n;
   float sx=(float)Math.sin(a),cz=-(float)Math.cos(a);
   float x=r[k+1]+r[k+3]*sx,z=r[k+2]+r[k+4]*cz;
   int lo=Math.max(0,k-5),hi=Math.min(r.length-5,k+5);
   float dy=r[hi]-r[lo],nx=sx/Math.max(.08f,r[k+3]),nz=cz/Math.max(.08f,r[k+4]),ny=0;
   if(Math.abs(dy)>.001f)ny=-(nx*(r[hi+1]-r[lo+1]+sx*(r[hi+3]-r[lo+3]))/dy+nz*(r[hi+2]-r[lo+2]+cz*(r[hi+4]-r[lo+4]))/dy);
   float len=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
   float u=front?.5f+x/6.10f:.5f+(j/(float)n-.5f)*2;
   return new V(x,r[k],z,Math.max(.01f,Math.min(.99f,u)),Math.max(.01f,Math.min(.99f,(r[k]+8.95f)/4.55f)),nx/len,ny/len,nz/len);
  }
  void dome(Part p,float... r){
   int n=32;
   for(int k=0;k<r.length-5;k+=5)for(int j=0;j<n;j++){
    boolean front=Math.cos((j+.5)*2*Math.PI/n)>.25;
    p.faces.add(new Q(domeV(r,k,j,n,front),domeV(r,k+5,j,n,front),domeV(r,k+5,j+1,n,front),domeV(r,k,j+1,n,front),front?7:13));
   }
   for(int k:new int[]{0,r.length-5}){
    float ny=k==0?-1:1;V center=new V(r[k+1],r[k],r[k+2],.5f,.5f,0,ny,0);
    for(int j=0;j<n;j++){
     V a=domeV(r,k,j,n,false),b=domeV(r,k,j+1,n,false);
     p.faces.add(k==0?new Q(center,a,b,center,3):new Q(center,b,a,center,2));
    }
   }
  }
  // Separate convex lens surfaces, with an outer dark frame and a ribbed violet inset.
  V lensV(int side,float t,float v,boolean frame){
   float x=side*(.20f+2.00f*t);
   float top=-4.58f-.27f*t;
   float depth=(float)Math.sin(Math.PI*t);
   float height=.20f+(.81f*depth);
   float y=top+height*v;
   float z=-2.55f+.76f*t*t-.13f*depth*(1-Math.abs(v-.5f)*2);
   if(frame){x+=side*(t-.5f)*.15f;y+=(v-.5f)*.14f;z+=.065f;}
   return new V(x,y,z,t,v,side*.30f*t,0,-1);
  }
  void lens(Part p,int side,boolean frame){
   int n=14;
   for(int j=0;j<n;j++)for(int k=0;k<4;k++){
    float u=j/(float)n,U=(j+1)/(float)n,v=k/4f,VV=(k+1)/4f;
    V a=lensV(side,u,v,frame),b=lensV(side,u,VV,frame),c=lensV(side,U,VV,frame),d=lensV(side,U,v,frame);
    p.faces.add(side>0?new Q(a,b,c,d,frame?5:15):new Q(d,c,b,a,frame?5:15));
   }
  }
  // Side ear medallions are actual concentric beveled cylinders in the YZ plane.
  V earV(int side,float x,float radius,double a,float u,float v,float nx){
   return new V(side*x,-4.55f+radius*(float)Math.cos(a),.24f+radius*(float)Math.sin(a),u,v,side*nx,0,0);
  }
  void ear(Part p,int side){
   float[] radii={.04f,.36f,.40f,.52f,.69f,.77f,.80f};
   float[] xs={2.66f,2.66f,2.76f,2.83f,2.73f,2.56f,2.28f};
   int[] mats={12,5,3,10,5,2};
   for(int k=0;k<radii.length-1;k++)for(int j=0;j<24;j++){
    double a=j*Math.PI/12,b=(j+1)*Math.PI/12;
    V A=earV(side,xs[k],radii[k],a,j/24f,0,1),B=earV(side,xs[k+1],radii[k+1],a,j/24f,1,1),C=earV(side,xs[k+1],radii[k+1],b,(j+1)/24f,1,1),D=earV(side,xs[k],radii[k],b,(j+1)/24f,0,1);
    p.faces.add(side>0?new Q(A,B,C,D,mats[k]):new Q(D,C,B,A,mats[k]));
   }
  }
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
   // Sculpted rear armor: gold trapezius, ivory back muscle plates and dark spinal channel.
   plate(torso,10,-.28f,0,.88f,1.72f,.73f,.72f,0,1.12f,3.12f,1.00f,2.52f,0,1.15f,2.95f,.88f,3.40f,0,1.10f,2.36f,.68f);
   for(int side:new int[]{-1,1}){
    plate(torso,1,2.80f,side*1.82f,1.42f,1.06f,.54f,4.0f,side*1.41f,1.62f,1.12f,.53f,5.65f,side*.91f,1.32f,.81f,.42f,7.75f,side*.54f,1.15f,.32f,.30f);
    panel(torso,3,side*2.55f,2.9f,1.78f,side*.62f,7.45f,1.52f,.24f);
    panel(torso,5,side*.52f,3.4f,1.99f,side*.34f,8.0f,1.49f,.25f);
    for(int j=0;j<3;j++){
     float yy=.65f+j*.75f;float xx=side*(1.92f-j*.14f);
     panel(torso,5,xx-.29f,yy,2.03f,xx+.29f,yy+.07f,2.03f,.15f);
    }
    for(int j=0;j<5;j++){
     float x=side*(.45f+j*.48f),X=side*(.93f+j*.48f);
     float yy=9.13f+j*.35f,Y=9.13f+(j+1)*.35f;
     panel(torso,8,x,yy,1.74f,X,Y,1.65f,.39f);
    }
    plate(torso,2,10.0f,side*1.24f,.85f,1.18f,.82f,11.18f,side*1.21f,1.04f,1.27f,.85f,12.02f,side*1.17f,.83f,.76f,.56f);
   }
   for(int j=0;j<4;j++){
    float y=4.0f+j*.90f;
    panel(torso,2,-.23f,y,1.90f,.23f,y+.16f,1.90f,.25f);
   }
   // Mechanical neck and sculpted angular face mask.
   plate(torso,5,-1.82f,0,.06f,1.09f,1.03f,0,0,.08f,1.26f,1.19f);
   portrait(head,5,6,-5.40f,0,.02f,1.64f,1.50f,-4.65f,0,-.06f,2.17f,1.89f,-3.84f,0,-.15f,2.02f,1.95f,-3.10f,0,-.21f,1.75f,1.72f,-2.45f,0,-.29f,1.30f,1.38f,-1.92f,0,-.39f,.88f,.99f);
   // Large swept-back helmet dome with an angular lower flange.
   dome(head,-8.95f,0,.14f,.14f,.20f,-8.75f,0,.13f,.99f,.91f,-8.32f,0,.14f,1.86f,1.72f,-7.68f,0,.19f,2.49f,2.24f,-6.90f,0,.29f,2.91f,2.57f,-6.15f,0,.43f,3.03f,2.68f,-5.44f,0,.44f,2.96f,2.68f,-4.95f,0,.30f,2.73f,2.48f,-4.55f,0,.16f,2.42f,2.22f);
   // Deep black outline and rounded protruding forehead shield, as a single solid assembly.
   plate(head,5,-7.36f,0,-1.58f,.20f,.16f,-7.02f,0,-1.97f,.85f,.37f,-6.44f,0,-2.31f,1.28f,.46f,-5.69f,0,-2.40f,1.45f,.50f,-4.62f,0,-2.33f,1.38f,.39f,-4.41f,0,-2.24f,1.10f,.25f);
   CinnabarClient.Model.angular(head,3,14,3.0f,-7.12f,-4.52f,-7.12f,0,-1.84f,.30f,.18f,-6.78f,0,-2.10f,.81f,.32f,-6.23f,0,-2.40f,1.14f,.42f,-5.55f,0,-2.48f,1.27f,.43f,-4.67f,0,-2.41f,1.22f,.33f,-4.52f,0,-2.31f,1.05f,.23f);
   for(int side:new int[]{-1,1}){
    // Lens surfaces are explicitly in front of the face, so the violet cannot be hidden by the mask.
    lens(head,side,true);lens(head,side,false);
    ear(head,side);
    plate(head,2,-5.55f,side*1.98f,.86f,.71f,1.14f,-4.46f,side*1.99f,1.02f,.69f,1.19f,-3.53f,side*1.65f,.93f,.56f,.91f,-2.35f,side*.95f,.59f,.35f,.61f,-1.72f,side*.70f,.50f,.29f,.41f);
    // Bright gold cheek armor and silver stripe descending from each eye.
    plate(head,1,-3.97f,side*1.15f,-1.39f,.61f,.43f,-3.40f,side*1.09f,-1.44f,.58f,.39f,-2.78f,side*.91f,-1.32f,.48f,.32f,-2.26f,side*.65f,-1.12f,.28f,.19f);
    panel(head,5,side*1.25f,-3.79f,-1.94f,side*1.43f,-2.57f,-1.60f,.23f);
    panel(head,8,side*1.25f,-3.79f,-2.00f,side*1.43f,-2.57f,-1.67f,.13f);
    panel(head,8,side*1.43f,-2.57f,-1.67f,side*1.27f,-2.36f,-1.48f,.13f);
   }
   // Layered armored nape with a central raised spine, attached to the shell.
   plate(head,2,-5.30f,0,1.48f,1.72f,1.03f,-4.41f,0,1.43f,1.56f,1.01f,-3.43f,0,1.09f,1.26f,.79f,-2.38f,0,.81f,.88f,.59f,-1.60f,0,.57f,.72f,.42f);
   plate(head,3,-5.05f,0,2.13f,.30f,.22f,-4.13f,0,2.16f,.34f,.24f,-3.28f,0,1.79f,.29f,.18f,-2.38f,0,1.27f,.19f,.13f);
   // Faceted nose, sculpted gold lips, and a large violet chin jewel.
   plate(head,3,-4.04f,0,-2.00f,.13f,.11f,-3.68f,0,-2.13f,.17f,.18f,-3.32f,0,-2.17f,.24f,.23f,-3.15f,0,-1.92f,.18f,.11f);
   panel(head,5,-.47f,-2.80f,-1.79f,-.13f,-2.91f,-1.94f,.17f);
   panel(head,5,-.13f,-2.91f,-1.94f,.14f,-2.88f,-1.93f,.17f);
   panel(head,5,.14f,-2.88f,-1.93f,.46f,-2.74f,-1.76f,.17f);
   panel(head,3,-.39f,-2.65f,-1.82f,.38f,-2.62f,-1.82f,.18f);
   plate(head,5,-2.51f,0,-1.27f,.30f,.25f,-2.20f,0,-1.39f,.49f,.35f,-1.81f,0,-1.22f,.32f,.25f);
   plate(head,4,-2.44f,0,-1.39f,.25f,.21f,-2.15f,0,-1.49f,.40f,.32f,-1.85f,0,-1.34f,.25f,.21f);
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
    panel(a,1,0,2.35f,1.15f,0,5.65f,.81f,1.20f);
    panel(a,5,s*.65f,2.55f,.85f,s*.40f,5.56f,.63f,.20f);
    Part f=fore[i]=a.child(0,5.85f,0);
    plate(f,2,-.42f,0,0,.80f,.82f,.64f,0,0,1.02f,1.04f,2.10f,0,0,.91f,.91f,3.65f,0,0,.60f,.65f,4.15f,0,0,.64f,.68f);
    panel(f,1,0,.44f,-1.04f,0,3.8f,-.69f,1.09f);
    panel(f,5,s*.64f,.48f,-.73f,s*.39f,3.65f,-.59f,.18f);
    panel(f,1,0,.50f,1.02f,0,3.75f,.67f,1.03f);
    insignia(f,0,4.18f,-.90f,.63f);
    plate(f,0,4.08f,0,0,.64f,.66f,4.7f,0,-.10f,.88f,.62f,5.5f,0,-.22f,.78f,.54f,5.72f,0,-.25f,.52f,.42f);
    for(int j=0;j<3;j++)panel(f,5,-.38f+j*.38f,5.0f,-.78f,-.38f+j*.38f,5.53f,-.73f,.09f);
    Part leg=legs[i]=root.child(s*1.44f,11,0);
    plate(leg,0,-.36f,0,0,1.39f,1.52f,1.3f,s*.14f,0,1.48f,1.52f,3.0f,s*.09f,0,1.30f,1.36f,5.4f,0,0,.85f,.90f,6.3f,0,0,.83f,.87f);
    panel(leg,1,s*.38f,.42f,-1.43f,0,5.70f,-.94f,1.56f);
    panel(leg,5,-s*.65f,.56f,-1.27f,-s*.36f,5.65f,-.79f,.43f);
    insignia(leg,s*.79f,.65f,-1.48f,.60f);
    panel(leg,8,s*.90f,.80f,-1.58f,s*2.43f,3.0f,-.81f,.78f);
    panel(leg,1,s*.18f,.60f,1.53f,0,5.70f,.93f,1.50f);
    panel(leg,5,-s*.69f,1.10f,1.20f,-s*.37f,5.60f,.82f,.26f);
    Part shin=shins[i]=leg.child(0,6.1f,0);
    plate(shin,2,-.35f,0,0,.89f,.94f,.48f,0,0,1.04f,1.07f,2.15f,0,.08f,1.04f,1.09f,4.8f,0,0,.63f,.69f,6.15f,0,0,.57f,.66f);
    insignia(shin,0,.45f,-1.33f,.82f);
    panel(shin,1,0,1.13f,-1.1f,0,5.74f,-.73f,1.10f);
    panel(shin,1,0,1.18f,1.13f,0,5.70f,.73f,1.07f);
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
   // Gold sparks are handled on the server; no tall transparent ribbon outlines.
  }
 }
}''',encoding='utf-8')
# Hand-painted atlas with bright gold edges, deep engraved shadow, purple scarabs and ivory fins.
im=Image.new('RGBA',(1024,512))
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for m in range(16):
 for y in range(128):
  v=max(0,min(1,(y-3)/121))
  for x in range(128):
   u=max(0,min(1,(x-3)/121));f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   alpha=255
   if m in (0,1,2,3,6,7,10,12,13,14):
    base={0:(224,157,44),1:(255,229,156),2:(204,127,29),3:(255,246,200),6:(247,220,153),7:(248,218,135),10:(243,154,31),12:(186,118,37),13:(245,220,144),14:(255,237,173)}[m]
    c=mix(base,(86,45,15),.25*f+.11*v)
    c=mix(c,(255,244,196),.48*g(.31,.31,.20,.46))
    c=mix(c,(255,247,213),.35*g(.17,.28,.043,.32))
    c=mix(c,(77,49,27),.25*max(0,math.sin(u*16+v*1.4))**10)
    if m in (7,13,14):
     # Strong gold highlights and controlled engraved black lines, rather than muddy brown.
     c=mix(c,(255,249,205),.44*g(.34,.23,.24,.32))
     c=mix(c,(133,101,44),.21*g(.83,.76,.22,.48))
    if m==7:
     for side in (-1,1):
      cx=.5+side*.225;cy=.43
      dx=(u-cx)*side;dy=(v-cy)*.82
      rad=math.hypot(dx,dy);ang=math.atan2(dy,dx)
      if rad<.123 and min(abs(rad-(.012+.016*(ang+math.pi+k*2*math.pi))) for k in (0,1))<.012:c=(31,27,25)
      seam=.5+side*(.075+.13*v+.085*math.sin(v*math.pi))
      if abs(u-seam)<.011:c=(35,30,26)
     if abs(u-.5)<.010 and v<.33:c=(38,32,25)
     if abs(v-(.82-.22*abs(u-.5)))<.016:c=(33,28,25)
    if m==13:
     for target in (.41+.15*abs(u-.5),.73-.13*abs(u-.5)):
      if abs(v-target)<.015:c=(37,31,25)
      elif abs(v-target-.021)<.010:c=(255,239,180)
     if abs(u-.5)<.010:c=(50,39,27)
    if m==14:
     c=mix(c,(255,255,231),.72*g(.32,.34,.22,.42))
     c=mix(c,(112,84,39),.23*g(.85,.63,.18,.48))
     if abs(u-.5)<.012:c=mix(c,(255,250,208),.38)
    if m==6:
     c=mix(c,(255,239,180),.35*g(.36,.52,.23,.35))
     c=mix(c,(103,72,34),.33*g(.84,.60,.16,.33))
     if abs(u-.5)<.085 and abs(v-.81)<.012:c=(42,32,27)
   elif m==15:
    # Ribbed violet optics: bright lavender strips with dark purple grooves.
    rib=(.5+.5*math.cos(u*math.pi*20+.55*v))**3
    c=mix((88,30,166),(220,160,255),.45+.48*rib)
    c=mix(c,(255,229,255),.68*g(.32,.27,.32,.21))
    c=mix(c,(70,19,135),.22*v)
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
