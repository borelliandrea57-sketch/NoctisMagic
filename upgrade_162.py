"""1.6.2: six individual cartoon pony silhouettes, curved hair, clean eyes, feathered wings."""
from pathlib import Path
import sys, math, struct, zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'SculptedGuestsClient.java';s=p.read_text(encoding='utf-8')
names=['PINKIE_PIE','TWILIGHT_SPARKLE','RAINBOW_DASH','FLUTTERSHY','RARITY','APPLEJACK']
for k,n in enumerate(names,4):
 a=f'e.registerEntityRenderer(Noctis.{n}.get(),c->new R<FriendshipPony>(c,{k}));'
 assert a in s,a
 s=s.replace(a,'',1)
p.write_text(s,encoding='utf-8')
(java/'PonyCartoonClient.java').write_text('''package it.noctis.magic;
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
public class PonyCartoonClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
  e.registerEntityRenderer(Noctis.PINKIE_PIE.get(),c->new R(c,4));
  e.registerEntityRenderer(Noctis.TWILIGHT_SPARKLE.get(),c->new R(c,5));
  e.registerEntityRenderer(Noctis.RAINBOW_DASH.get(),c->new R(c,6));
  e.registerEntityRenderer(Noctis.FLUTTERSHY.get(),c->new R(c,7));
  e.registerEntityRenderer(Noctis.RARITY.get(),c->new R(c,8));
  e.registerEntityRenderer(Noctis.APPLEJACK.get(),c->new R(c,9));
 }
 // Curved locks swept along a Catmull-Rom spline; smooth continuous mesh instead of stacked boxes.
 static float cat(float a,float b,float c,float d,float t){
  return .5f*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);
 }
 static float[] point(float[] a,int seg,float t){
  int n=a.length/4;float[] r=new float[4];
  for(int i=0;i<4;i++)r[i]=cat(a[Math.max(0,seg-1)*4+i],a[seg*4+i],a[Math.min(n-1,seg+1)*4+i],a[Math.min(n-1,seg+2)*4+i],t);
  r[3]=Math.max(.035f,r[3]);return r;
 }
 static void lock(Part p,int m,float depth,float... a){
  int n=a.length/4,steps=(n-1)*5,N=18;V[][] r=new V[steps+1][N+1];
  for(int j=0;j<=steps;j++){
   int seg=Math.min(n-2,j/5);float t=(j-seg*5)/5f;
   float[] q=point(a,seg,t),prev=point(a,seg,Math.max(0,t-.035f)),next=point(a,seg,Math.min(1,t+.035f));
   float dx=next[0]-prev[0],dy=next[1]-prev[1],dz=next[2]-prev[2];
   float len=(float)Math.sqrt(dx*dx+dy*dy+dz*dz);
   if(len<.00001f){dx=0;dy=1;dz=0;len=1;}dx/=len;dy/=len;dz/=len;
   // Cross tangent with the depth axis, with a stable fallback for longitudinal locks.
   float ax=-dy,ay=dx,az=0,al=(float)Math.sqrt(ax*ax+ay*ay);
   if(al<.001f){ax=1;ay=0;az=0;al=1;}ax/=al;ay/=al;
   float bx=dy*az-dz*ay,by=dz*ax-dx*az,bz=dx*ay-dy*ax;
   for(int i=0;i<=N;i++){
    double angle=i*Math.PI*2/N;float cs=(float)Math.cos(angle),sn=(float)Math.sin(angle);
    float nx=ax*cs+bx*sn,ny=ay*cs+by*sn,nz=az*cs+bz*sn;
    r[j][i]=new V(q[0]+q[3]*(ax*cs+bx*sn*depth),q[1]+q[3]*(ay*cs+by*sn*depth),q[2]+q[3]*(az*cs+bz*sn*depth),i/(float)N,j/(float)steps,nx,ny,nz);
   }
  }
  for(int j=0;j<steps;j++)for(int i=0;i<N;i++)p.faces.add(new Q(r[j][i],r[j+1][i],r[j+1][i+1],r[j][i+1],m));
 }
 static void curl(Part p,int m,float cx,float cy,float cz,float radius,float start,float direction){
  float[] a=new float[8*4];
  for(int i=0;i<8;i++){float f=i/7f,theta=start+direction*f*5.3f,rr=radius*(1-.66f*f);
   a[4*i]=cx+(float)Math.cos(theta)*rr;a[4*i+1]=cy+(float)Math.sin(theta)*rr;a[4*i+2]=cz+.24f*f;
   a[4*i+3]=i==7?.035f:radius*(.62f-.36f*f);
  }
  lock(p,m,.87f,a);
 }
 static class M extends EntityModel<FriendshipPony>{
  final int k;
  final Part root=new Part(0,0,0),body=root.child(0,14,0),head=root.child(0,6.0f,-4.9f);
  final Part neck=body.child(0,-3.0f,-4.0f),mane=head.child(0,0,0),tail=body.child(0,-1.0f,5.9f);
  final Part[] ears=new Part[2],legs=new Part[4],shins=new Part[4],wings=new Part[2],tips=new Part[2];
  final List<Part> locks=new ArrayList<>();
  M(int k){
   this.k=k;
   // Compact barrel, rounded chest and haunches; no oversized cylindrical neck.
   Part barrel=body.child(0,0,0);barrel.rx=(float)Math.PI/2;
   barrel.loft(16,36,-6.3f,0,0,1.2f,1.5f,-5.4f,0,0,2.85f,3.1f,-3.3f,0,0,3.42f,3.6f,0,0,0,3.42f,3.25f,2.8f,0,0,3.88f,3.65f,5.1f,0,0,3.52f,3.3f,6.3f,0,0,1.70f,2.0f);
   neck.loft(20,32,-5.3f,0,-.75f,2.15f,2.10f,-3.5f,0,-.70f,2.55f,2.40f,-1.5f,0,-.25f,2.83f,2.56f,1.8f,0,.20f,3.1f,2.7f,3.9f,0,.35f,2.2f,2.0f);
   // Broad rounded forehead, rounded cheeks and very short snout; exactly one eye surface.
   head.loft(21,56,-4.85f,0,.10f,1.35f,1.4f,-4.40f,0,.08f,2.75f,2.45f,-3.1f,0,0,3.95f,3.37f,-1.45f,0,-.08f,4.32f,3.52f,.15f,0,-.18f,4.18f,3.52f,1.65f,0,-.28f,3.71f,3.13f,2.65f,0,-.43f,2.72f,2.25f,3.25f,0,-.42f,1.25f,1.3f);
   head.oval(22,0,1.68f,-2.94f,2.53f,1.50f,1.56f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    ears[i]=head.child(s*2.85f,-3.7f,.35f);
    ears[i].rz=s*.23f;
    ears[i].loft(20,24,-3.25f,0,.12f,.05f,.06f,-2.35f,0,.05f,.69f,.49f,-1.0f,0,0,1.10f,.76f,.6f,0,0,1.18f,.85f);
    ears[i].blade(23,0,-2.68f,-.39f,0,.05f,-.79f,1.14f);
    if(k==5||k==8){
     // Slender spiral unicorn horn.
     if(i==0){Part horn=head.child(0,-3.8f,-2.25f);horn.rx=.26f;
      horn.loft(17,32,-4.5f,0,0,.035f,.04f,-3.6f,0,0,.27f,.29f,-2.2f,0,0,.49f,.51f,-.7f,0,0,.72f,.73f,.25f,0,0,.87f,.86f);}
    }
    if(k>=5&&k<=7){
     Part wing=wings[i]=body.child(s*2.9f,-2.2f,-1.4f);
     wing.oval(20,s*.87f,-.1f,.5f,1.95f,1.20f,2.30f);
     Part tip=tips[i]=wing.child(s*1.4f,.0f,.30f);
     for(int j=0;j<6;j++){
      float f=j/5f;
      lock(tip,18,.54f,0,.2f,-1.1f+f*2.7f,.58f,s*(2.1f+f*.2f),-.65f+f*.7f,-.8f+f*3.3f,.82f,s*(4.5f-f*.9f),-1.5f+f*2.1f,.15f+f*4.1f,.71f,s*(6.2f-f*1.7f),-2.3f+f*3.7f,1.0f+f*4.8f,.035f);
     }
     for(int j=0;j<4;j++)wing.oval(18,s*(.8f+j*.48f),-.82f,-.6f+j*.62f,.94f,.34f,.88f);
    }
   }
   for(int i=0;i<4;i++){
    int side=i/2==0?-1:1;boolean hind=i%2==1;
    Part leg=legs[i]=root.child(side*(hind?2.55f:2.14f),hind?15.0f:15.15f,hind?3.85f:-3.8f);
    leg.loft(20,24,-1.4f,0,0,hind?1.72f:1.29f,hind?1.84f:1.34f,1.25f,0,hind?-.35f:0,hind?1.46f:1.11f,hind?1.53f:1.20f,4.1f,0,hind?-.35f:0,1.01f,1.08f);
    Part shin=shins[i]=leg.child(0,3.9f,hind?-.35f:0);
    shin.loft(20,24,-.25f,0,0,1.03f,1.09f,1.6f,0,hind?.35f:0,1.02f,1.08f,3.9f,0,-.10f,1.36f,1.43f,4.95f,0,-.23f,1.52f,1.61f,5.15f,0,-.23f,1.44f,1.52f);
   }
   hairstyle();
  }
  void hairstyle(){
   if(k==4){
    // Pinkie's full bubble curls, scalloped silhouette and large springy tail.
    mane.oval(24,0,-4.4f,.55f,3.65f,2.1f,3.0f);
    curl(mane,24,-1.65f,-4.5f,-1.7f,2.45f,3.1f,1);
    curl(mane,24,1.5f,-5.0f,-.75f,2.35f,4.15f,-1);
    curl(mane,24,3.0f,-1.85f,1.6f,2.1f,.2f,1);
    curl(mane,24,-3.0f,1.15f,1.6f,2.1f,3.1f,-1);
    curl(mane,24,-2.3f,4.0f,2.7f,2.15f,3.0f,1);
    curl(mane,24,.2f,6.0f,3.2f,2.25f,.5f,-1);
    tail.oval(24,0,-.7f,3.1f,2.15f,2.3f,2.75f);
    curl(tail,24,-1.25f,-1.7f,4.9f,2.5f,3.8f,1);
    curl(tail,24,1.35f,.7f,6.0f,2.8f,.5f,-1);
    curl(tail,24,-.75f,3.9f,6.5f,2.55f,2.1f,1);
    curl(tail,24,.9f,6.25f,5.8f,2.0f,1.4f,-1);
   }else if(k==5){
    // Twilight: straight neat fringe, navy mane with pink and violet ribbon-like streaks.
    mane.oval(24,0,-4.30f,.5f,3.65f,1.72f,3.1f);
    for(int j=0;j<5;j++){
     float x=-2.85f+j*1.38f;int m=j==2?26:j==3?27:24;
     lock(mane,m,.65f,x,-5.35f,-.9f,.25f,x,-4.65f,-2.1f,.94f,x+.12f,-3.72f,-3.02f,.83f,x+.20f,-2.75f,-3.24f,.56f);
     lock(mane,m,.72f,x*.75f,-4.3f,1.8f,.65f,x*.8f,-1.5f,3.45f,.94f,x*.8f,3.25f,4.4f,.95f,x*.65f,7.1f,5.15f,.76f,x*.6f,8.5f,5.65f,.10f);
     lock(tail,m,.76f,x*.30f,-1.4f,0,.55f,x*.70f,-.8f,3.2f,.95f,x*.78f,2.1f,5.2f,1.03f,x*.65f,6.2f,6.4f,.80f,x*.40f,8.0f,6.2f,.08f);
    }
   }else if(k==6){
    // Rainbow's swept, multicolored mane and tail; six separate saturated bands.
    for(int j=0;j<6;j++){
     float x=-2.85f+j*1.12f;
     lock(mane,26+j,.88f,x,-3.5f,-2.0f,.25f,x-.4f,-5.35f,-.35f,.95f,x-.2f,-5.0f,1.65f,1.03f,x+.12f,-2.8f,3.5f,.82f,x+.5f,1.5f,5.2f,.70f,x+.55f,5.5f,6.0f,.035f);
     lock(tail,26+j,.84f,x*.25f,-1.3f,.2f,.35f,x*.62f,-.9f,2.7f,.70f,x*.9f,.5f,5.1f,.84f,x*.85f,3.6f,7.6f,.65f,x*.65f,6.9f,8.2f,.035f);
    }
   }else if(k==7){
    // Fluttershy: large sweeping pastel-pink forelock and long tapered hair, not a straight slab.
    mane.oval(24,-.25f,-4.4f,.4f,3.55f,1.9f,3.0f);
    for(int j=0;j<5;j++){float f=j/4f;Part q=mane.child(0,0,0);locks.add(q);
     lock(q,24,.68f,1.8f-f*1.1f,-5.2f+f*.35f,-.7f,.20f,-.4f-f*.65f,-4.8f+f*.35f,-2.5f,1.0f,-2.7f-f*.22f,-3.1f+f*.34f,-2.4f,1.15f,-3.8f-f*.18f,.5f+f*.65f,-1.3f,1.0f,-3.65f-f*.2f,4.6f+f*.5f,.3f,.83f,-2.6f-f*.35f,8.7f+f*.65f,2.6f,.035f);
    }
    lock(mane,24,.76f,2.1f,-4.5f,1.4f,1.25f,3.3f,-1.4f,3.1f,1.75f,3.0f,3.7f,4.6f,1.55f,1.85f,8.4f,5.6f,1.25f,.5f,11.0f,5.8f,.04f);
    lock(tail,24,.83f,0,-1.2f,0,.7f,0,-.4f,3.6f,2.0f,-.8f,2.8f,6.1f,2.45f,-.6f,6.3f,7.0f,2.0f,1.05f,8.0f,7.4f,1.3f,2.35f,9.3f,7.5f,.035f);
    curl(tail,24,1.5f,6.8f,7.3f,1.9f,2.0f,-1);
   }else if(k==8){
    // Rarity: pronounced side-swept violet coiffure and elegant spiral ringlets.
    mane.oval(24,-.55f,-4.65f,.5f,3.6f,2.1f,3.15f);
    lock(mane,24,.75f,-2.8f,-4.1f,-1.0f,.15f,-1.2f,-5.7f,-2.0f,1.2f,1.45f,-4.8f,-2.5f,1.45f,3.3f,-2.35f,-1.3f,1.25f,3.5f,.75f,-.35f,.92f,2.2f,2.8f,-.1f,.035f);
    curl(mane,24,3.0f,.3f,.7f,2.1f,-1.1f,1);
    lock(mane,24,.9f,-2.0f,-4.0f,1.5f,.9f,-3.35f,-.35f,3.1f,1.6f,-3.1f,3.3f,4.15f,1.9f,-1.1f,6.6f,4.25f,1.55f,.4f,7.9f,3.75f,.2f);
    curl(mane,24,-.8f,6.9f,3.65f,2.25f,2.6f,-1);
    lock(tail,24,.86f,0,-1.2f,0,.8f,-1.0f,-1.9f,3.3f,1.6f,-1.35f,.5f,5.3f,2.35f,.4f,3.7f,6.0f,2.2f,1.6f,5.7f,5.9f,1.5f,.1f,7.3f,5.2f,.15f);
    curl(tail,24,.8f,5.9f,6.0f,2.5f,1.9f,-1);
   }else{
    // Applejack's straw-colored tied mane, tied tail, wide curved cowboy hat.
    mane.oval(24,0,-4.25f,.4f,3.55f,1.6f,3.0f);
    lock(mane,24,.70f,2.1f,-4.8f,-.8f,.28f,.4f,-4.8f,-2.55f,1.27f,-1.9f,-3.6f,-2.75f,1.13f,-3.15f,-2.4f,-1.55f,.70f,-3.15f,-1.3f,-.95f,.035f);
    lock(mane,24,.88f,0,-4.1f,2.2f,1.25f,.1f,-.8f,3.65f,1.9f,.45f,3.3f,4.5f,1.63f,.55f,6.2f,4.9f,.80f,.45f,8.5f,5.2f,1.05f,.3f,10.2f,5.4f,.035f);
    mane.oval(27,.55f,6.35f,4.9f,1.0f,.33f,.92f);
    lock(tail,24,.83f,0,-1.1f,0,.8f,-.25f,-1.1f,2.8f,1.65f,-.20f,1.8f,5.1f,2.02f,.1f,4.4f,6.2f,1.10f,.20f,5.5f,6.7f,.8f,.65f,7.3f,6.95f,1.3f,1.45f,9.15f,7.1f,.035f);
    tail.oval(27,.2f,5.4f,6.7f,1.03f,.34f,.96f);
    Part hat=head.child(0,-4.9f,.10f);hat.rz=.06f;
    hat.loft(28,40,-.52f,0,0,4.75f,3.80f,-.18f,0,0,5.20f,4.20f,.22f,0,0,5.12f,4.15f,.45f,0,0,4.65f,3.74f);
    hat.loft(28,36,-3.4f,0,.24f,1.95f,2.07f,-2.92f,0,.20f,2.55f,2.61f,-1.9f,0,.10f,2.78f,2.78f,-.28f,0,0,3.05f,3.03f);
    hat.loft(29,36,-.95f,0,0,2.99f,2.99f,-.40f,0,0,3.09f,3.09f);
   }
  }
  @Override public void setupAnim(FriendshipPony e,float limb,float amount,float age,float yaw,float pitch){
   boolean sit=e.isInSittingPose(),flight=e.winged()&&!e.onGround()&&!sit;
   float bob=(float)Math.sin(limb*1.32f)*amount*.15f;
   body.y=(sit?16.2f:14)+bob;body.rx=sit?-.17f:flight?-.08f:0;
   head.y=(sit?8.0f:6.0f)+bob;head.ry=yaw*.012f;head.rx=pitch*.010f;
   for(int i=0;i<4;i++){
    boolean hind=i%2==1;float w=(float)Math.cos(limb*.67f+(i/2+i%2)*Math.PI)*amount;
    legs[i].rx=sit?(hind?1.05f:-.23f):flight?(hind?.45f:-.33f):w*.60f;
    shins[i].rx=sit?(hind?-.70f:.25f):flight?(hind?-.18f:.70f):Math.max(0,-w)*.42f;
   }
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    ears[i].rz=s*(.23f+.05f*(float)Math.sin(age*.12f+i));
    if(wings[i]!=null){
     wings[i].rz=s*(flight?-.22f+(float)Math.sin(age*.35f)*.70f:.32f);
     wings[i].ry=s*(flight?.05f:.86f);tips[i].rz=s*(flight?(float)Math.sin(age*.35f-.6f)*.22f:.42f);
    }
   }
   tail.ry=(float)Math.sin(age*.13f)*(.18f+amount*.12f);
   tail.rx=-amount*.15f+(float)Math.sin(age*.10f)*.035f;
   mane.rx=(float)Math.sin(age*.11f)*.02f+amount*.035f;
   for(int i=0;i<locks.size();i++)locks.get(i).rz=(float)Math.sin(age*.10f+i*.5f)*.025f;
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<FriendshipPony,M>{
  final int k;
  R(EntityRendererProvider.Context c,int k){super(c,new M(k),.45f);this.k=k;}
  @Override public ResourceLocation getTextureLocation(FriendshipPony e){return new ResourceLocation(Noctis.ID,"textures/entity/pony_cartoon_"+k+".png");}
 }
}''',encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
spec=[((249,151,194),(222,35,122),(58,161,218)),((174,133,214),(48,40,91),(117,67,170)),((111,201,240),(232,58,64),(191,55,133)),((251,235,157),(246,169,199),(55,163,162)),((247,245,252),(92,42,145),(48,113,207)),((245,170,81),(248,220,111),(62,153,70))]
rainbow=[(233,55,66),(255,142,50),(255,224,59),(67,186,97),(67,127,231),(151,77,193)]
def coat(u,v,b):return mix(mix(b,(255,255,255),.08*(1-v)),(100,67,100),.045*v)
def mark(x,y,k):
 # x,y in [-1,1]; each flank mark is drawn on the body surface only.
 if k==4:
  for cx,cy,col in [(-.37,-.36,(95,190,244)),(.37,-.36,(95,190,244)),(0,.20,(250,218,62))]:
   if ((x-cx)/.22)**2+((y-cy)/.30)**2<1:return col
   if cy+.25<y<cy+.55 and abs(x-cx-.055*math.sin(y*10))<.025:return (115,66,134)
 if k==5:
  if abs(x)<.12 and abs(y)<.58 or abs(y)<.11 and abs(x)<.60 or abs(abs(x)-abs(y))<.11 and abs(x)<.40:return (222,66,164)
  for a,b in [(-.56,-.42),(.56,-.42),(-.56,.40),(.56,.40),(0,.76)]:
   if abs(x-a)+abs(y-b)<.14:return (255,250,250)
 if k==6:
  if any(((x-a)/.30)**2+((y-b)/.22)**2<1 for a,b in [(-.29,-.38),(0,-.48),(.28,-.38)]):return (249,253,255)
  if -.30<y<.73 and abs(x-(.12-.45*y))<.21:return (235,50,56) if x<-.03-.45*y else (251,224,57) if x<.12-.45*y else (64,139,228)
 if k==7:
  for a,b in [(-.37,-.36),(.37,-.36),(0,.30)]:
   if any(((x-a-d)/.16)**2+((y-b)/.25)**2<1 for d in [-.12,.12]):return (232,112,166)
   if abs(x-a)<.045 and abs(y-b)<.25:return (78,171,187)
 if k==8:
  for a,b in [(-.36,-.34),(.36,-.34),(0,.33)]:
   if abs(x-a)/.23+abs(y-b)/.34<1:return (84,164,235) if x<a else (133,207,249)
 if k==9:
  for a,b in [(-.36,-.32),(.36,-.32),(0,.33)]:
   if ((x-a)/.23)**2+((y-b)/.22)**2<1:return (215,44,48)
   if abs(x-a)<.045 and -.33<y-b<-.17:return (100,69,35)
   if ((x-a-.11)/.14)**2+((y-b+.22)/.07)**2<1:return (75,141,68)
 return None
def face(u,v,k,b,iris):
 c=coat(u,v,b)
 for side in (-1,1):
  # one pair, positioned nearer the front than the old lateral-only eyes.
  ex=.5+side*.119
  width=.083 if k==4 else .075 if k in (5,7,8) else .071
  height=.178 if k in (4,7) else .151 if k in (5,8) else .136
  dx=(u-ex)/width;dy=(v-.475+side*dx*(.012 if k in (6,9) else .004))/height
  d=dx*dx+dy*dy
  if d<1.065:c=(61,39,66)
  if d<.90:c=(255,252,251)
  ix=(dx+side*.09)/.64;iy=(dy+.025)/.89
  if ix*ix+iy*iy<1 and d<.9:
   c=mix(mix(iris,(29,30,56),.17),mix(iris,(255,255,255),.44),clamp((dy+.45)*.66))
   if ((dx+side*.09)/.34)**2+(dy/.73)**2<1:c=(26,23,41)
   if ((dx+.15)/.20)**2+((dy+.28)/.23)**2<1:c=(255,255,255)
   if ((dx-.19)/.095)**2+((dy-.27)/.12)**2<1:c=(255,255,255)
  if k in (4,5,7,8):
   for n in range(2 if k!=8 else 3):
    # short lashes grow from the outside edge, never additional eye shapes.
    if .64<side*dx<1.18+n*.06 and abs(dy+(.80-n*.16)-.72*(side*dx-.65))<.055:c=(58,36,65)
  if k in (6,9) and abs(dx)<.9 and abs(v-(.276+side*dx*.018))<.011:c=mix(b,(58,41,59),.57)
 if k==9:
  for side in (-1,1):
   for dx,dy in [(0,0),(.018,.021),(-.018,.016)]:
    if ((u-(.5+side*.064+dx))/.006)**2+((v-(.69+dy))/.010)**2<1:c=(167,94,50)
 return c
def sample(m,u,v,k,b,h,e):
 if m in (16,17,18,20,21,22,23,25):
  c=coat(u,v,b)
  if m==16:
   for side in (.25,.75):
    color=mark((u-side)/.065,(v-.73)/.185,k)
    if color:c=color
  elif m==17:
   if abs(math.sin(v*math.pi*4+u*math.pi*2))<.115:c=mix(b,(90,66,110),.18)
  elif m==18:
   c=mix(c,(255,255,255),.10*math.sin(u*math.pi)**2)
   if v>.83:c=mix(c,(90,65,105),.06)
  elif m==21:c=face(u,v,k,b,e)
  elif m==22:
   # Small round muzzle, tiny nostrils, friendly subtle smile.
   for x in (.459,.541):
    if ((u-x)/.014)**2+((v-.41)/.028)**2<1:c=mix(b,(89,50,80),.47)
   f=abs(u-.5)
   if f<.105 and abs(v-(.707-.105*(f/.105)**2))<.014:c=mix(b,(89,50,80),.57)
  elif m==23:c=mix(b,(176,77,113),.27)
  return c
 base=h
 if k==6 and 26<=m<=31:base=rainbow[m-26]
 elif k==5 and m==26:base=(224,68,161)
 elif k==5 and m==27:base=(142,70,186)
 elif k==9 and m==27:base=(191,45,47)
 elif k==9 and m==28:base=(157,101,53)
 elif k==9 and m==29:base=(105,63,40)
 # Broad satin bands with subtle edge gradients instead of repetitive dark ridges.
 c=mix(base,(255,255,255),.24*math.exp(-((u-.34-.04*math.sin(v*5))/.22)**2))
 c=mix(c,(47,29,58),.15*math.exp(-((u-.87)/.19)**2))
 return c
for k,(b,h,e) in enumerate(spec,4):
 pix=bytearray(W*H*4)
 for m in range(16,32):
  for y in range(128):
   for x in range(128):
    if m in (16,21,22):
     colors=[sample(m,clamp((x+dx-3)/121),clamp((y+dy-3)/121),k,b,h,e) for dx in (.2,.8) for dy in (.2,.8)]
     c=tuple(round(sum(t[j] for t in colors)/4) for j in range(3))
    else:c=sample(m,clamp((x-3)/121),clamp((y-3)/121),k,b,h,e)
    off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
 (assets/f'pony_cartoon_{k}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Six distinct pony models: broad heads, short necks, curved individual hairstyles, articulated legs, feathered wings and flank marks.')
