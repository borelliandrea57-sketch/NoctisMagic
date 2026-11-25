"""1.5.2: Stardust Dragon sculpted redesign, articulated membrane wings and silver-blue armor."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'SynchroClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.STARDUST.get(),c->new Renderer(c,false));'
assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'StardustSculptedClient.java').write_text('''package it.noctis.magic;
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
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class StardustSculptedClient{
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.STARDUST.get(),R::new);}
    // Smooth tapered bone / armor strut along an arbitrary 3-D segment.
    static Part spar(Part p,int mat,float x,float y,float z,float X,float Y,float Z,float r,float tip){
        float dx=X-x,dy=Y-y,dz=Z-z;
        float len=(float)Math.sqrt(dx*dx+dy*dy+dz*dz);
        Part q=p.child(x,y,z);q.rx=(float)Math.atan2(dz,Math.sqrt(dx*dx+dy*dy));q.rz=(float)Math.atan2(-dx,dy);
        q.loft(mat,16,0,0,0,r*.72f,r*.72f,len*.16f,0,0,r,r,len*.62f,0,0,r*.73f,r*.73f,len,0,0,tip,tip);return q;
    }
    static float[] xyz(float x,float y,float z){return new float[]{x,y,z};}
    // Double sided tessellated sail, with independent smooth membrane texture.
    static void tri(Part p,int mat,float[] a,float[] b,float[] c,float[] uv){
        float x=b[0]-a[0],y=b[1]-a[1],z=b[2]-a[2],X=c[0]-a[0],Y=c[1]-a[1],Z=c[2]-a[2];
        float nx=y*Z-z*Y,ny=z*X-x*Z,nz=x*Y-y*X,mag=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
        if(mag<.001f)return;nx/=mag;ny/=mag;nz/=mag;
        V v1=new V(a[0],a[1],a[2],uv[0],uv[1],nx,ny,nz),v2=new V(b[0],b[1],b[2],uv[2],uv[3],nx,ny,nz),v3=new V(c[0],c[1],c[2],uv[4],uv[5],nx,ny,nz);
        p.faces.add(new Q(v1,v2,v3,v3,mat));
        p.faces.add(new Q(new V(a[0],a[1],a[2],uv[0],uv[1],-nx,-ny,-nz),new V(c[0],c[1],c[2],uv[4],uv[5],-nx,-ny,-nz),new V(b[0],b[1],b[2],uv[2],uv[3],-nx,-ny,-nz),new V(b[0],b[1],b[2],uv[2],uv[3],-nx,-ny,-nz),mat));
    }
    static void sail(Part p,float[] hub,float[] a,float[] b){
        float[] mid=xyz((a[0]+b[0])*.5f,(a[1]+b[1])*.5f+.55f,(a[2]+b[2])*.5f-2.1f);
        tri(p,5,hub,a,mid,new float[]{.5f,0,0,1,.5f,.77f});tri(p,5,hub,mid,b,new float[]{.5f,0,.5f,.77f,1,1});
    }
    static class M extends EntityModel<SynchroDragon>{
        final Part root=new Part(0,0,0),body=root.child(0,10,0),neck=body.child(0,-1,-5.5f),head=neck.child(0,-8,-5.5f),jaw=head.child(0,1.2f,-2.0f);
        final Part[] wings=new Part[2],outer=new Part[2],arms=new Part[2],fore=new Part[2],legs=new Part[2],shin=new Part[2],tail=new Part[10];
        M(){
            // Elongated torso, narrow waist, protective layered breastplate.
            Part chest=body.child(0,0,0);chest.rx=(float)Math.PI/2;
            chest.loft(0,28,-7,0,0,2.0f,2.15f,-5.8f,0,0,3.9f,3.6f,-2.8f,0,0,4.4f,3.9f,1.3f,0,0,3.1f,2.7f,4.4f,0,0,3.2f,2.8f,7,0,0,1.8f,1.8f);
            body.oval(2,0,1.6f,-3.3f,3.0f,2.25f,3.1f);
            for(int i=0;i<4;i++){Part p=body.child(0,1.55f,-4.9f+i*2.7f);p.rx=(float)Math.PI/2;
                p.loft(3,24,-.6f,0,0,2.5f-i*.21f,1.45f,0,0,0,2.7f-i*.21f,1.55f,.4f,0,0,2.45f-i*.21f,1.4f);}
            // Tall arched neck and narrowing forward-facing head.
            neck.loft(2,24,-8.6f,0,-5.4f,1.25f,1.4f,-7.2f,0,-4.4f,1.55f,1.6f,-4.8f,0,-2.1f,2.05f,1.75f,-2.2f,0,-.7f,2.45f,2.05f,0,0,0,2.65f,2.35f);
            for(int i=0;i<5;i++){float f=i/4f;Part ring=neck.child(0,-1-f*6,-.7f-f*3.9f);ring.rx=-.50f;float w=2.55f-f*.95f;
                ring.loft(0,20,-.5f,0,0,w*.9f,w*.8f,0,0,0,w,w*.9f,.6f,0,0,w*.87f,w*.79f);
                spar(ring,0,0,0,1.3f,0,-2.7f,2.6f,.65f,.04f);}
            Part skull=head.child(0,0,-.5f);skull.rx=-(float)Math.PI/2;
            skull.loft(6,32,-2.0f,0,0,1.15f,1.5f,-.8f,0,0,2.55f,2.0f,.8f,0,0,2.65f,1.9f,2.5f,0,.15f,1.85f,1.35f,4.6f,0,.25f,.75f,.72f,5.25f,0,.2f,.45f,.35f);
            jaw.loft(2,20,-.3f,0,-.15f,1.9f,1.7f,.6f,0,-.35f,1.75f,2.1f,1.15f,0,-.5f,1.12f,1.8f);
            for(int s:new int[]{-1,1}){
                // Distinct narrow horns swept backwards, layered cheek blades and brow armor.
                spar(head,0,s*1.8f,-1.4f,.5f,s*3.3f,-5.7f,4.2f,.75f,.045f);
                spar(head,3,s*1.3f,-1.6f,.25f,s*1.7f,-6.5f,2.6f,.55f,.035f);
                head.blade(0,s*1.5f,-.7f,-.9f,s*3.65f,1.65f,2.5f,1.7f);
                head.blade(3,s*1.4f,-1.65f,-3.8f,s*2.1f,-1.7f,.35f,.65f);
                head.oval(12,s*1.82f,-.40f,-2.55f,.37f,.31f,.73f);
                for(int j=0;j<3;j++)spar(jaw,0,s*(1.15f-j*.16f),.2f,-1.4f-j*.45f,s*(1.12f-j*.16f),-.7f,-1.5f-j*.45f,.18f,.02f);
            }
            head.oval(12,0,-1.85f,-.65f,.75f,.20f,.85f);
            // Sculpted violet cabochons on breast and shoulders, set into silver rings.
            body.oval(0,0,-.5f,-6.2f,1.8f,2.35f,.85f);body.oval(12,0,-.5f,-6.88f,1.35f,1.85f,.62f);
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                body.oval(0,s*3.4f,-1.1f,-3.8f,1.95f,2.25f,2.1f);
                body.oval(12,s*4.35f,-1.1f,-4.35f,1.15f,1.45f,1.4f);
                arms[i]=body.child(s*3.1f,.6f,-4.5f);
                arms[i].loft(0,20,-.7f,0,0,1.45f,1.55f,1.0f,s*.65f,0,1.5f,1.5f,4.6f,s*.9f,-.5f,.88f,.9f);
                fore[i]=arms[i].child(s*.9f,4.5f,-.5f);
                fore[i].loft(2,18,-.15f,0,0,1.0f,1.05f,1.65f,s*.12f,-.15f,1.13f,1.15f,4.9f,0,0,.73f,.75f);
                fore[i].oval(0,0,5.2f,-.35f,1.2f,1.1f,1.15f);
                for(int j=0;j<3;j++)spar(fore[i],0,-.83f+j*.83f,5.4f,-.7f,-.9f+j*.9f,7.2f,-2.1f,.36f,.035f);
                legs[i]=body.child(s*2.8f,.5f,4.15f);
                legs[i].oval(0,s*.35f,1.5f,.1f,1.8f,2.3f,1.9f);
                legs[i].loft(2,20,1.5f,0,0,1.45f,1.55f,3.5f,0,-.65f,1.2f,1.3f,5.4f,0,-.9f,.84f,.85f);
                shin[i]=legs[i].child(0,5.3f,-.9f);
                shin[i].loft(0,18,-.3f,0,0,.95f,.95f,1.1f,0,.55f,.95f,1.0f,5.4f,0,.2f,.64f,.73f,7.7f,0,-.2f,.79f,1.0f);
                shin[i].oval(0,0,7.2f,-.7f,1.25f,.75f,1.45f);
                for(int j=0;j<3;j++)spar(shin[i],0,-.85f+j*.85f,7.2f,-1.2f,-.9f+j*.90f,8.05f,-2.6f,.34f,.025f);
                // Swept main wing arm with continuous membrane, not layered rectangular panels.
                Part w=wings[i]=body.child(s*3.6f,-2.4f,-2.0f);
                float[] origin=xyz(0,0,0),elbow=xyz(s*7,-3.5f,-.8f),hub=xyz(s*12,-8,-1.2f);
                spar(w,0,0,0,0,elbow[0],elbow[1],elbow[2],1.25f,.82f);
                spar(w,2,elbow[0],elbow[1],elbow[2],hub[0],hub[1],hub[2],.89f,.60f);
                tri(w,5,origin,hub,xyz(s*4,3.5f,10),new float[]{0,0,1,0,.2f,1});
                spar(w,0,0,0,0,s*4,3.5f,10,.52f,.045f);
                Part o=outer[i]=w.child(hub[0],hub[1],hub[2]);
                o.oval(0,0,0,0,.95f,.95f,.95f);
                float[][] tips={xyz(s*12,-1.3f,2.5f),xyz(s*10.5f,5.6f,8.4f),xyz(s*6.4f,10.7f,13.0f),xyz(s*1.5f,12.2f,15.0f),xyz(-s*5,10.8f,12)};
                float[] h=xyz(0,0,0);
                for(int j=0;j<tips.length;j++){
                    float[] t=tips[j];spar(o,0,0,0,0,t[0],t[1],t[2],j==0?.70f:.40f,.025f);
                    if(j>0)sail(o,h,tips[j-1],t);
                }
                // Lower pair of curved, tapered fin blades gives the characteristic Stardust silhouette.
                Part fin=body.child(s*3.4f,1.0f,2.8f);
                float[] f0=xyz(0,0,0),f1=xyz(s*8,2.5f,3.7f),f2=xyz(s*11,10.5f,10),f3=xyz(s*5,7.8f,8.0f);
                spar(fin,0,0,0,0,f1[0],f1[1],f1[2],.75f,.35f);
                spar(fin,3,f1[0],f1[1],f1[2],f2[0],f2[1],f2[2],.45f,.035f);
                sail(fin,f1,f2,f3);tri(fin,5,f0,f1,f3,new float[]{.5f,0,0,1,1,1});
                spar(fin,0,0,0,0,f3[0],f3[1],f3[2],.42f,.03f);
            }
            Part prev=body;
            for(int i=0;i<tail.length;i++){
                float r=1.8f-i*.155f;
                Part t=tail[i]=prev.child(0,i==0?0:0,i==0?6.15f:3.0f);t.rx=.05f;
                Part section=t.child(0,0,0);section.rx=(float)Math.PI/2;
                section.loft(2,20,-.25f,0,0,r,r,.65f,0,0,r*1.05f,r*1.05f,3.1f,0,0,r*.83f,r*.83f);
                spar(t,0,0,-r*.65f,.2f,0,-r*1.8f,2.2f,r*.47f,.025f);prev=t;
            }
            spar(prev,0,0,0,2.2f,0,-1.0f,6.1f,.45f,.025f);
        }
        @Override public void setupAnim(SynchroDragon e,float limb,float amount,float age,float yaw,float pitch){
            boolean air=!e.onGround()||e.isVehicle(),sit=e.isInSittingPose();float cast=e.casting();
            body.y=sit?12:10;body.rx=air?-.045f:0;
            neck.rx=-cast*.13f+(float)Math.sin(age*.09)*.025f;neck.ry=yaw*.004f;
            head.rx=pitch*.008f+cast*.1f;head.ry=yaw*.009f;jaw.rx=cast*.40f;
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;float flap=(float)Math.sin(age*(air?.24:.09))*(air?.50f:.10f);
                wings[i].rz=s*(flap+(air?-.05f:.28f));wings[i].ry=s*(air?.04f:.25f);outer[i].rz=s*(flap*.33f-.05f);
                float w=(float)Math.cos(limb*.63+i*Math.PI)*amount;
                arms[i].rx=air?-.65f:sit?-.55f:w*.48f;fore[i].rx=air?-.65f:sit?.25f:-.12f;
                legs[i].rx=air?.63f:sit?-.65f:-w*.42f;shin[i].rx=air?-.80f:sit?.65f:Math.max(0,w)*.28f;
            }
            for(int i=0;i<tail.length;i++){tail[i].ry=(float)Math.sin(age*.10-i*.46)*.13f;tail[i].rx=-.05f+(float)Math.cos(age*.09-i*.4)*.07f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class R extends MobRenderer<SynchroDragon,M>{
        R(EntityRendererProvider.Context c){super(c,new M(),1.2f);}
        @Override protected void scale(SynchroDragon e,PoseStack p,float partial){p.scale(2.15f,2.15f,2.15f);}
        @Override public ResourceLocation getTextureLocation(SynchroDragon e){return new ResourceLocation(Noctis.ID,"textures/entity/stardust_sculpted.png");}
    }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal={0:(211,229,232),2:(78,134,156),3:(159,197,210),5:(191,211,224),6:(204,225,231),12:(111,65,163)}
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
for m,base in pal.items():
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(61,104,129),.16*v+.18*(1-math.sin(u*math.pi)))
            if m in (0,3,6):
                c=blend(c,(249,255,255),.48*math.exp(-((u-.34)/.14)**2))
                c=blend(c,(55,119,147),.19*math.exp(-((u-.76)/.15)**2))
                if v>.96 or v<.02:c=blend(c,(75,130,151),.46)
            if m==2:
                c=blend(c,(166,216,229),.28*math.sin(u*math.pi)**2)
                if abs(math.sin(v*math.pi*5+u*.45))<.11:c=(56,98,123)
            if m==5:
                c=blend(base,(85,123,159),.42*v+.13*math.sin(u*math.pi*4)**2)
                c=blend(c,(237,250,250),.22*math.exp(-((u-.5)/.15)**2))
                if abs(math.sin(u*math.pi*5+v*.5))<.045:c=blend(c,(93,137,163),.42)
            if m==12:
                rr=math.hypot((u-.45)*1.5,(v-.43)*1.5)
                c=blend(base,(51,24,98),.42*clamp(rr))
                c=blend(c,(204,179,252),.78*math.exp(-((u-.36)/.12)**2-((v-.28)/.14)**2))
                if (x*31+y*17)%1543==0:c=(238,232,255)
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'stardust_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Stardust sculpted silver dragon: continuous wing membranes, violet gemstones, tapered armor and articulated limbs')
