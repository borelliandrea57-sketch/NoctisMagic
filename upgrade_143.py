"""1.4.3: rebuild Joker, Arsene, Phos, Cinnabar and Pinkie Pie with rounded polygon meshes."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
for f in ('PhantomClient.java','GemGuestClient.java'):(java/f).unlink()
p=java/'PonyClient.java';s=p.read_text();a='e.registerEntityRenderer(Noctis.PINKIE_PIE.get(),c->new Renderer(c,5));';assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'SculptedGuestsClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import com.mojang.math.Axis;
import java.util.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class SculptedGuestsClient {
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
        e.registerEntityRenderer(Noctis.JOKER.get(),c->new R<Joker>(c,0));
        e.registerEntityRenderer(Noctis.ARSENE.get(),c->new R<Arsene>(c,1));
        e.registerEntityRenderer(Noctis.PHOSPHOPHYLLITE.get(),c->new R<GemGuest>(c,2));
        e.registerEntityRenderer(Noctis.CINNABAR.get(),c->new R<GemGuest>(c,3));
        e.registerEntityRenderer(Noctis.PINKIE_PIE.get(),c->new R<FriendshipPony>(c,4));
    }
    record V(float x,float y,float z,float u,float v,float nx,float ny,float nz){}
    record Q(V a,V b,V c,V d,int tile){}
    static final class Part{
        final List<Q> faces=new ArrayList<>();final List<Part> children=new ArrayList<>();
        float x,y,z,rx,ry,rz;
        Part(float x,float y,float z){this.x=x;this.y=y;this.z=z;}
        Part child(float x,float y,float z){Part p=new Part(x,y,z);children.add(p);return p;}
        V ring(float[] a,int j,int i,int n,float v){
            double angle=-Math.PI+i*(2*Math.PI/n);
            float sx=(float)Math.sin(angle),cz=-(float)Math.cos(angle);
            return new V(a[j+1]+sx*a[j+3],a[j],a[j+2]+cz*a[j+4],i/(float)n,v,sx,0,cz);
        }
        Part loft(int m,int n,float... a){
            int count=a.length/5;
            for(int j=0;j<count-1;j++)for(int i=0;i<n;i++){
                float v=(a[j*5]-a[0])/(a[(count-1)*5]-a[0]),w=(a[(j+1)*5]-a[0])/(a[(count-1)*5]-a[0]);
                faces.add(new Q(ring(a,j*5,i,n,v),ring(a,(j+1)*5,i,n,w),ring(a,(j+1)*5,i+1,n,w),ring(a,j*5,i+1,n,v),m));
            }
            // End caps: use solid portion of material texture, no duplicate facial features.
            for(int i=0;i<n;i++){
                int j=(count-1)*5;
                V t=new V(a[1],a[0],a[2],.05f,0,0,-1,0),b=new V(a[j+1],a[j],a[j+2],.05f,1,0,1,0);
                V t1=ring(a,0,i,n,0),t2=ring(a,0,i+1,n,0),b1=ring(a,j,i,n,1),b2=ring(a,j,i+1,n,1);
                faces.add(new Q(t,new V(t1.x,t1.y,t1.z,.05f,0,0,-1,0),new V(t2.x,t2.y,t2.z,.05f,0,0,-1,0),t,m));
                faces.add(new Q(b,new V(b2.x,b2.y,b2.z,.05f,1,0,1,0),new V(b1.x,b1.y,b1.z,.05f,1,0,1,0),b,m));
            }
            return this;
        }
        Part oval(int m,float x,float y,float z,float w,float h,float d){
            return loft(m,20,y-h,x,z,.04f,.04f,y-h*.80f,x,z,w*.60f,d*.60f,y-h*.35f,x,z,w*.94f,d*.94f,y,x,z,w,d,y+h*.45f,x,z,w*.89f,d*.89f,y+h*.82f,x,z,w*.57f,d*.57f,y+h,x,z,.04f,.04f);
        }
        Part blade(int m,float x,float y,float z,float X,float Y,float Z,float width){
            float dx=X-x,dy=Y-y,dz=Z-z,len=(float)Math.sqrt(dx*dx+dy*dy);
            float px=-dy/Math.max(.01f,len),py=dx/Math.max(.01f,len);
            float[] t={0,.22f,.55f,.82f,1},w={.35f,1,.92f,.55f,.02f};
            V[][] r=new V[t.length][9];
            for(int j=0;j<t.length;j++)for(int i=0;i<=8;i++){
                double a=i*Math.PI/4;float cs=(float)Math.cos(a),sn=(float)Math.sin(a);
                float h=cs*w[j]*width*.5f,depth=sn*w[j]*.23f;
                r[j][i]=new V(x+dx*t[j]+px*h,y+dy*t[j]+py*h,z+dz*t[j]+depth,i/8f,t[j],px*cs,py*cs,sn);
            }
            for(int j=0;j<t.length-1;j++)for(int i=0;i<8;i++)faces.add(new Q(r[j][i],r[j+1][i],r[j+1][i+1],r[j][i+1],m));
            return this;
        }
        void draw(PoseStack p,VertexConsumer buf,int light,int overlay,float red,float green,float blue,float alpha){
            p.pushPose();p.translate(x/16f,y/16f,z/16f);
            if(rz!=0)p.mulPose(Axis.ZP.rotation(rz));if(ry!=0)p.mulPose(Axis.YP.rotation(ry));if(rx!=0)p.mulPose(Axis.XP.rotation(rx));
            var mat=p.last().pose();var norm=p.last().normal();
            for(Q f:faces){
                int l=(f.tile==12||f.tile==13)?(Math.max(light&65535,11<<4)|Math.max(light&0xffff0000,11<<20)):light;
                for(int i=0;i<4;i++){
                    V v=switch(i){case 0->f.a;case 1->f.b;case 2->f.c;default->f.d;};
                    float u=((f.tile%8)*128+3+v.u*121)/1024f, vv=((f.tile/8)*128+3+v.v*121)/512f;
                    buf.vertex(mat,v.x/16f,v.y/16f,v.z/16f).color(red,green,blue,alpha).uv(u,vv).overlayCoords(overlay).uv2(l).normal(norm,v.nx,v.ny,v.nz).endVertex();
                }
            }
            for(Part c:children)c.draw(p,buf,light,overlay,red,green,blue,alpha);p.popPose();
        }
    }
    static class M<T extends Mob> extends EntityModel<T>{
        final int k;final Part root=new Part(0,0,0),body=root.child(0,0,0),head=root.child(0,-1,0);
        final Part[] arms=new Part[2],legs=new Part[2],tails=new Part[2],wings=new Part[2],ponyLegs=new Part[4];
        final List<Part> hair=new ArrayList<>();Part ponyTail;
        M(int k){this.k=k;if(k==4)pony();else build();}
        void pony(){
            body.y=12;body.oval(20,0,0,1,4.2f,4.2f,7.0f);
            body.oval(20,0,-3.4f,-3.9f,2.8f,4.3f,3.3f);
            head.y=4;head.z=-5.5f;
            head.loft(21,28,-6,0,0,1.0f,1.4f,-5.5f,0,0,3.2f,3.0f,-4,0,0,4,3.65f,-1.5f,0,-.25f,4.05f,3.8f,1,0,-.35f,3.7f,3.4f,3.3f,0,-.25f,2.7f,2.4f,4,0,0,.9f,1);
            head.oval(22,0,1.8f,-3.1f,2.75f,1.85f,2.35f);
            for(int i=0;i<2;i++){int s=i==0?-1:1;Part ear=head.child(s*2.8f,-4.5f,.1f);ear.rz=s*.35f;ear.loft(20,12,-3.6f,0,0,.13f,.13f,-2.4f,0,0,.78f,.48f,0,0,0,1.15f,.8f);ear.blade(23,0,-2.7f,-.45f,0,-.45f,-.7f,.85f);}
            // Large interlocking curls, not narrow rectangular mane strips.
            Part mane=head.child(0,-4.8f,0);hair.add(mane);
            mane.oval(24,-2.2f,-.3f,-1.0f,2.6f,2.5f,2.7f);
            mane.oval(24,.5f,-1.9f,-.8f,2.9f,2.6f,2.8f);
            mane.oval(24,2.5f,-.3f,.6f,2.3f,2.8f,2.9f);
            mane.oval(24,-2.9f,2.2f,2.3f,2.1f,2.6f,2.2f);
            mane.oval(24,2.7f,2.8f,2.4f,2.15f,2.8f,2.3f);
            mane.oval(24,0,4.6f,3.1f,3.1f,3.2f,2.7f);
            mane.oval(24,1.2f,8.1f,3.0f,2.8f,2.8f,2.6f);
            // Forelock has a smooth curled edge, above both eyes.
            mane.oval(24,-.8f,.5f,-2.4f,2.25f,1.5f,1.65f);
            for(int i=0;i<4;i++){int side=i/2==0?-1:1;Part leg=root.child(side*2.6f,14.8f,i%2==0?-3.8f:5.4f);ponyLegs[i]=leg;
                leg.loft(20,16,-1,0,0,1.55f,1.65f,2.4f,0,0,1.16f,1.3f,5.1f,0,0,1.18f,1.35f,8.3f,0,-.25f,1.75f,1.85f,9.2f,0,-.25f,1.72f,1.8f);}
            ponyTail=body.child(0,-1.2f,6.6f);
            ponyTail.oval(24,0,-1,2,2.3f,2.6f,3.0f);ponyTail.oval(24,0,.2f,5.4f,2.8f,3.2f,3.2f);ponyTail.oval(24,-.5f,3.4f,6.3f,2.5f,3.1f,2.7f);ponyTail.oval(24,.4f,5.7f,4.8f,2.1f,2.4f,2.0f);
            // Two flank marks; separate oval patches, one on each side.
            for(int s:new int[]{-1,1}){Part mark=body.child(s*3.85f,.4f,4);mark.ry=-s*(float)Math.PI/2;mark.oval(25,0,0,0,1.45f,1.45f,.16f);}
        }
        void build(){
            boolean ars=k==1,gem=k>=2;int suit=ars?7:gem?10:0,face=k==0?1:k==1?8:k==2?14:15;
            body.loft(suit,16,-1,0,0,2.4f,1.65f,0,0,0,3.6f,2,2,0,0,3.7f,2.1f,6,0,0,2.55f,1.6f,9,0,0,2.45f,1.65f,11,0,0,3.25f,1.9f);
            body.loft(gem?11:ars?9:2,12,-.85f,0,-.05f,1.25f,1.15f,1,0,-.12f,1.55f,1.4f);
            for(int s:new int[]{-1,1}){
                body.blade(gem?11:ars?9:2,s*1.9f,.1f,-1.75f,s*.22f,gem?3.6f:6.6f,-1.85f,gem?1.7f:2.0f);
                if(ars)body.blade(9,s*2,0,0,s*4.9f,-5.7f,1,3.1f);
            }
            if(gem){body.blade(0,0,1.6f,-2.08f,0,7.1f,-1.75f,.85f);body.loft(16,16,9.3f,0,0,2.55f,1.72f,10,0,0,2.72f,1.8f);}
            if(ars){
                head.loft(face,20,-7,0,0,2,1.9f,-5.6f,0,-.05f,3,2.6f,-3.6f,0,-.1f,2.6f,2.55f,-1.3f,0,-.4f,1.5f,1.8f,.2f,0,-.85f,.18f,.25f);
                Part hat=head.child(0,-6.5f,0);hat.rz=.12f;
                hat.loft(9,24,-.55f,0,0,5.35f,3.7f,-.13f,0,0,5.6f,3.85f,.25f,0,0,4.65f,3.5f);
                hat.loft(9,20,-10,0,.45f,3.25f,2.9f,-9.7f,0,.45f,3.55f,3.15f,-3,0,0,2.85f,2.6f,-.2f,0,0,2.95f,2.7f);
                hat.loft(7,20,-2,0,0,3.02f,2.78f,-.75f,0,0,3.1f,2.85f);
                for(int s:new int[]{-1,1})head.blade(7,s*2.2f,-4.9f,-1.8f,s*4.6f,-8.2f,-.7f,1.8f);
            }else{
                head.loft(face,24,-7.2f,0,.08f,2.15f,2.15f,-6.5f,0,.02f,3,2.73f,-5.1f,0,0,3.25f,2.9f,-3.4f,0,-.03f,3.15f,2.85f,-1.8f,0,-.12f,2.75f,2.45f,-.55f,0,-.2f,1.75f,1.85f,0,0,-.25f,.65f,1);
                int h=k==0?3:k==2?12:13;
                head.loft(h,18,-8.8f,0,.1f,.55f,.7f,-8.5f,0,.1f,2.3f,2.1f,-7.6f,0,.15f,3.3f,3.1f,-6.2f,0,.25f,3.45f,3.05f);
                Part back=head.child(0,-6.8f,1.8f);hair.add(back);float end=k==3?15:k==2?6.6f:4.9f;
                back.loft(h,16,-.8f,0,0,2.8f,1.8f,1.2f,0,.45f,3.1f,1.55f,4,0,.7f,3.05f,1.35f,Math.max(4.2f,end*.72f),0,1.15f,k==3?3.1f:2.6f,1.1f,end,0,1,k==3?2.4f:1.4f,.22f);
                for(int i=0;i<(k==0?6:4);i++){
                    float x=k==0?-2.9f+i*1.03f:-2.7f+i*1.55f;Part q=head.child(x,-7.5f,-2.1f);hair.add(q);
                    float drift=k==0?-.8f:k==2?(i<2?-.7f:.55f):(i<2?-.35f:1.05f);
                    q.loft(h,10,-.7f,0,.4f,.85f,.78f,.7f,drift*.35f,-.28f,.88f,.72f,1.7f,drift*.7f,-.55f,.60f,.38f,2.5f+(i==0||i==3?.55f:0),drift,-.46f,.045f,.06f);
                }
                for(int s:new int[]{-1,1}){
                    Part q=head.child(s*2.9f,-6.1f,0);hair.add(q);float e=k==3?(s<0?13.6f:11.5f):k==2?6.2f:3.7f;
                    q.loft(h,10,-1,0,0,.75f,1.25f,1,s*.45f,-.3f,.9f,1.35f,e*.65f,s*.66f,-.25f,.82f,1.15f,e,s*.1f,-.2f,.045f,.08f);
                }
                if(k==3)for(int i=0;i<4;i++){Part q=head.child(-2.3f+i*1.55f,-5.6f,2.7f);hair.add(q);q.loft(h,8,0,0,0,.7f,.75f,5,(i-1.5f)*.25f,.45f,.85f,.8f,10,(i-1.5f)*.65f,.75f,.7f,.6f,14.5f+(i%2)*1.5f,(i-1.5f)*.75f,.5f,.04f,.07f);}
            }
            for(int i=0;i<2;i++){int s=i==0?-1:1;Part a=arms[i]=root.child(s*4,0,0);
                a.loft(suit,12,-.65f,0,0,1.15f,1.25f,.5f,0,0,1.55f,1.5f,gem?2.4f:4.6f,0,0,gem?1.5f:1.12f,1.3f,gem?3.2f:8.4f,0,0,1.08f,1.04f);
                a.loft(gem?17:ars?9:4,12,gem?3.1f:8.3f,0,0,.92f,.95f,9.2f,0,0,.68f,.69f,10.7f,0,-.12f,.82f,.63f,11.2f,0,-.1f,.52f,.44f);
                if(ars)for(int j=0;j<4;j++)a.blade(9,-1+j*.65f,10,-.3f,-1.3f+j*.8f,14.1f,-1.1f,.67f);
                else if(!gem&&i==1){Part d=a.child(0,10,-.6f);d.rx=-1.2f;d.loft(0,8,0,0,0,.53f,.53f,2,0,0,.53f,.53f);d.blade(18,0,2,0,0,8,0,1.4f);}
                Part leg=legs[i]=root.child(s*1.8f,11,0);
                leg.loft(suit,12,0,0,0,1.58f,1.55f,gem?3.9f:7.3f,0,0,1.1f,1.1f);
                if(gem)leg.loft(17,12,3.8f,0,0,1.1f,1.1f,7.5f,0,0,.86f,.9f,10.9f,0,0,.7f,.75f);
                leg.loft(5,12,gem?10.8f:6.4f,0,0,.85f,.9f,12,0,-.42f,1.06f,1.6f,13,0,-.42f,1.04f,1.6f);
                if(!gem){tails[i]=body.child(s*1.6f,8.7f,1.35f);tails[i].blade(suit,s*.2f,0,0,s*2.6f,ars?15:12,2.6f,4.3f);}
                if(ars){
                    Part wing=wings[i]=body.child(s*2.4f,0,2);
                    wing.blade(6,0,1,0,s*15,-5,1.2f,5);
                    for(int j=0;j<9;j++){float t=j/8f;wing.blade(6,s*(3+11*t),-2.5f-1.2f*t,1.1f,s*(9+15*t),22-16*t,2.4f,4.2f-.65f*t);}
                    for(int j=0;j<8;j++){float t=j/7f;wing.blade(19,s*(1.4f+11*t),-.5f-2*t,.35f,s*(5+15*t),14-10*t,1.25f,3.9f);}
                    for(int j=0;j<6;j++){float t=j/5f;wing.blade(6,s*(.5f+10*t),.1f-2.8f*t,-.15f,s*(3.7f+11*t),7-5*t,.5f,3.1f);}
                }
            }
        }
        @Override public void setupAnim(T e,float limb,float amount,float age,float yaw,float pitch){
            if(k==4){head.ry=yaw*.012f;head.rx=pitch*.01f;boolean sit=e instanceof FriendshipPony p&&p.isInSittingPose();head.y=sit?7:4;body.y=sit?15:12;
                for(int i=0;i<4;i++)ponyLegs[i].rx=sit?(i%2==0?-.6f:1): (float)Math.cos(limb*.66+(i/2+i%2)*Math.PI)*amount*.65f;
                ponyTail.ry=(float)Math.sin(age*.13)*.30f;ponyTail.rx=-amount*.15f;hair.get(0).rx=(float)Math.sin(age*.10)*.035f;return;}
            float cast=e instanceof Joker j?j.summoning():e instanceof Arsene a?a.casting():e instanceof GemGuest g?g.gesture():0;
            head.ry=yaw*.01745f;head.rx=pitch*.01745f;head.rz=k==2?cast*.10f:k==3?-cast*.04f:0;body.ry=k<2?cast*.14f:0;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float walk=(float)Math.cos(limb*.6662+i*Math.PI)*amount;
                arms[i].rx=-walk*.65f-(k==1?cast*1.2f:i==1?cast*(k==0?1.55f:.7f):0);arms[i].rz=s*(-.08f-(k==1?cast*.6f:.05f));legs[i].rx=k==1?.12f+i*.09f:walk*.65f;
                if(tails[i]!=null){tails[i].rx=.08f+amount*.23f+cast*.18f+(float)Math.sin(age*.10f+i)*.055f;tails[i].rz=s*.09f;}
                if(wings[i]!=null){wings[i].ry=s*(.18f+(float)Math.sin(age*.11f)*.27f+cast*.25f);wings[i].rz=s*(.07f+(float)Math.sin(age*.11f)*.12f);}
            }
            for(int i=0;i<hair.size();i++)hair.get(i).rx=(float)Math.sin(age*.1f+i*.7f)*.025f+(k==3?amount*.12f:amount*.04f);
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class R<T extends Mob> extends MobRenderer<T,M<T>>{
        final int k;R(EntityRendererProvider.Context c,int k){super(c,new M<T>(k),k==1?.7f:k==4?.48f:.35f);this.k=k;}
        @Override protected void scale(T e,PoseStack p,float partial){float s=k==1?1.38f:k==2?.92f:k==3?.98f:1;p.scale(s,s,s);}
        @Override public ResourceLocation getTextureLocation(T e){return new ResourceLocation(Noctis.ID,"textures/entity/sculpted_guests.png");}
    }
}''',encoding='utf-8')
# Texture atlas. Face UV front at .5; Pinkie has precisely two eyes on the continuous head surface.
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(25,29,39),(236,200,173),(91,99,119),(22,23,34),(209,20,45),(22,19,29),(37,28,45),(151,18,42),(21,14,28),(28,20,33),(25,32,43),(240,240,230),(68,219,188),(190,25,53),(247,237,220),(247,235,223),(172,184,184),(244,235,219),(188,198,212),(48,32,52),(244,143,186),(244,143,186),(244,143,186),(219,104,150),(223,42,129),(244,143,186)]
def blend(a,b,t):return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
def clamp(x):return max(0,min(1,x))
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);front=abs(u-.5);light=.85+.15*math.cos((u-.5)*math.pi*2)
            c=tuple(int(a*light) for a in base)
            if m in (1,14,15):
                c=blend(base,(214,161,148),.13*math.exp(-((v-.69)/.16)**2)+.12*clamp((front-.16)*6))
                if m==1 and front<.18 and abs(v-.53)<.14*(1-.55*front/.18):c=(240,241,239)
                for ex in (.405,.595):
                    dx=(u-ex)/(.061 if m==1 else .065);dy=(v-.53+(.035*dx if ex<.5 else -.035*dx))/.102
                    d=dx*dx+dy*dy
                    if d<1:c=(41,37,46) if m!=15 else (84,35,43)
                    if d<.79:c=(244,244,233)
                    if abs(dx)<.48 and d<.82:c=(177,35,57) if m==1 else (62,174,143) if m==14 else (177,28,58)
                    if abs(dx)<.20 and abs(dy)<.72 and d<.8:c=(28,28,36)
                    if (dx+.15)**2+(dy+.22)**2<.085:c=(255,255,255)
                    if abs(dx)<1.1 and abs(v-(.39+(.018*dx if ex<.5 else -.018*dx)))<.016 and m!=1:c=(63,113,103) if m==14 else (110,32,47)
                if abs(u-.5)<.013 and .64<v<.71:c=blend(base,(155,101,94),.22)
                if abs(u-.5)<.043 and abs(v-.82+.014*math.cos((u-.5)*65))<.013:c=(153,88,88) if m==1 else (179,130,121)
            elif m==8:
                for ex in (.401,.599):
                    dx=(u-ex)/.072;dy=(v-.48+(u-.5)*.2)/.078
                    if abs(dx)<1 and abs(dy)<1-abs(dx)*.62:c=(239,28,58)
                    if abs(dx)<.36 and abs(dy)<.35:c=(255,155,122)
                if abs(front-(.07+.11*v))<.013 and .61<v<.86:c=(130,23,48)
            elif m in (12,13):
                band=int(u*6);f=u*6-band;g=(.62,.92,.73,1,.83,.55)[band%6]
                if f+v*.75>1:g*=.78
                c=tuple(int(a*g) for a in base);c=blend(c,(204,255,245) if m==12 else (255,169,179),.38*math.exp(-((f-.32-v*.16)/.08)**2))
                if abs(f-.22-v*.12)<.014:c=(224,255,249) if m==12 else (255,211,219)
            elif m in (3,24):
                g=.78+.22*math.sin(u*math.pi*6+v*2)**2;c=tuple(int(a*g) for a in base)
                c=blend(c,(83,85,103) if m==3 else (255,125,185),.45*math.exp(-((v-.32)/.11)**2))
            elif m in (6,19):
                c=blend(c,(80,54,82),.30*math.exp(-((u-.25)/.16)**2))
                if abs(u-.25)<.015:c=(81,61,83)
            elif m in (0,7,10):
                if front<.018:c=blend(c,(100,104,120),.35)
                if m==7 and front<.13 and abs((v*5)%1-.5)<.055:c=(215,171,95)
            elif m==21:
                for ex in (.33,.67):
                    dx=(u-ex)/.092;dy=(v-.48)/.26;d=dx*dx+dy*dy
                    if d<1:c=(85,35,74)
                    if d<.92:c=(255,252,249)
                    if ((dx-(.18 if ex<.5 else -.18))/.60)**2+(dy/.86)**2<1 and d<.9:c=(55,157,218)
                    if ((dx-(.18 if ex<.5 else -.18))/.30)**2+(dy/.71)**2<1 and d<.85:c=(25,30,61)
                    if (dx+.13)**2+(dy+.30)**2<.095:c=(255,255,255)
                    if (dx-.24)**2+(dy-.27)**2<.027:c=(255,255,255)
            elif m==22:
                if front<.13 and abs(v-.70-.06*math.cos(front*16))<.024:c=(143,55,107)
                if any(((u-ex)/.022)**2+((v-.4)/.035)**2<1 for ex in (.40,.60)):c=(164,65,117)
            elif m==25:
                for ex,ey,col in ((.37,.31,(94,187,236)),(.63,.31,(94,187,236)),(.5,.58,(255,220,65))):
                    if ((u-ex)/.087)**2+((v-ey)/.13)**2<1:c=col
                    if abs(u-ex-.025*math.sin(v*14))<.007 and ey+.10<v<ey+.30:c=(113,75,143)
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'textures/entity/sculpted_guests.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Five redesigned polygon models installed; original behavior retained.')
