"""1.5.3: Jotaro sculpted redesign, muscular silhouette, cap, chain and double belt."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'JojoClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.JOTARO.get(),c->new Renderer(c,0));'
assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'JotaroSculptedClient.java').write_text('''package it.noctis.magic;
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
public class JotaroSculptedClient {
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.JOTARO.get(),R::new);}
    static V ring(float a,float b,float w,float h,float r,float u,float v){
        float ca=(float)Math.cos(a),sa=(float)Math.sin(a),cb=(float)Math.cos(b),sb=(float)Math.sin(b);
        return new V((w+r*cb)*ca,(h+r*cb)*sa,r*sb,u,v,ca*cb,sa*cb,sb);
    }
    static void link(Part p,float w,float h,float r){
        for(int i=0;i<20;i++)for(int j=0;j<8;j++){
            float a=i*(float)Math.PI/10,A=(i+1)*(float)Math.PI/10,b=j*(float)Math.PI/4,B=(j+1)*(float)Math.PI/4;
            p.faces.add(new Q(ring(a,b,w,h,r,i/20f,j/8f),ring(A,b,w,h,r,(i+1)/20f,j/8f),ring(A,B,w,h,r,(i+1)/20f,(j+1)/8f),ring(a,B,w,h,r,i/20f,(j+1)/8f),4));
        }
    }
    static class M extends EntityModel<JojoMob>{
        final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1.3f,0);
        final Part[] arm=new Part[2],fore=new Part[2],leg=new Part[2],shin=new Part[2],coat=new Part[2];
        final Part[] chain=new Part[5];
        M(){
            // Broad chest, powerful shoulders, narrow waist, open long black coat.
            body.loft(0,28,-1.2f,0,0,2.2f,1.5f,.1f,0,0,4.6f,2.45f,2.5f,0,0,4.55f,2.5f,5.1f,0,0,3.65f,2.2f,8.8f,0,0,2.75f,1.8f,11,0,0,3.45f,2.0f);
            body.oval(1,0,3.2f,-2.1f,3.1f,3.35f,.82f);
            body.loft(1,24,3.5f,0,-.65f,2.6f,1.7f,7.9f,0,-.5f,2.3f,1.55f,9.3f,0,-.2f,2.45f,1.5f);
            body.loft(2,18,-1.6f,0,0,1.38f,1.35f,.65f,0,0,1.7f,1.4f);
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                body.blade(0,s*3.2f,.05f,-1.8f,s*2.5f,9.5f,-1.85f,2.4f);
                body.blade(3,s*1.9f,-.3f,-2.1f,s*1.75f,8.8f,-2.0f,.55f);
                Part collar=body.child(s*1.8f,-.1f,.25f);collar.rz=-s*.20f;
                collar.loft(0,18,-3.3f,0,.05f,.70f,1.2f,-2.6f,s*.1f,0,1.05f,1.65f,.15f,s*.25f,0,1.25f,1.85f,1.3f,s*.5f,-.15f,.85f,.9f);
                for(int j=0;j<3;j++)body.oval(4,s*2.35f,2.3f+j*2.2f,-2.12f,.30f,.30f,.17f);
                if(i==0){collar.oval(4,-.6f,-2.35f,-1.3f,.42f,.42f,.22f);collar.oval(4,.32f,-2.35f,-1.3f,.42f,.42f,.22f);}
                coat[i]=body.child(s*2.25f,8.7f,1.2f);
                coat[i].loft(0,20,0,0,0,1.8f,.55f,3.3f,s*.4f,.4f,2.1f,.52f,7,s*.8f,1.3f,2.4f,.48f,10.8f,s*1.45f,2.6f,2.25f,.42f,14.1f,s*2.0f,3.6f,1.30f,.25f,15.2f,s*2.45f,4.1f,.08f,.08f);
                coat[i].blade(3,s*1.55f,.2f,-.34f,s*3.2f,13.3f,3.4f,.35f);
            }
            body.loft(5,28,9.25f,0,0,2.98f,1.92f,10.1f,0,0,3.05f,1.99f);
            body.loft(5,28,10.45f,0,0,3.16f,2.02f,11.25f,0,0,3.23f,2.08f);
            for(int j=0;j<2;j++){Part b=body.child(.35f,9.7f+j*1.15f,-2.1f);link(b,.70f,.34f,.13f);}
            // Five actual open gold links, alternating depth and swing.
            Part prev=body;
            for(int j=0;j<5;j++){
                chain[j]=prev.child(j==0?3.3f:j==1?.35f:-.10f,j==0?-1.8f:1.15f,j==0?-1.85f:0);
                chain[j].ry=j%2==0?.25f:1.12f;link(chain[j],.49f,.77f,.19f);prev=chain[j];
            }
            // Angular jaw and pronounced brow; one continuous face UV.
            head.loft(6,32,-7.55f,0,.1f,1.7f,1.8f,-7.05f,0,0,2.75f,2.5f,-5.55f,0,0,3.25f,2.9f,-3.75f,0,-.04f,3.18f,2.7f,-2.0f,0,-.1f,2.75f,2.38f,-.6f,0,-.2f,1.95f,1.6f,0,0,-.25f,1.15f,1.0f);
            head.loft(2,16,-3.9f,0,-2.6f,.27f,.2f,-2.75f,0,-2.92f,.42f,.55f,-2.15f,0,-2.85f,.45f,.30f);
            for(int s:new int[]{-1,1}){head.oval(2,s*3.17f,-3.25f,.12f,.44f,.89f,.55f);head.oval(4,s*3.35f,-2.75f,-.20f,.17f,.22f,.18f);}
            // Hair and cap merge into the same silhouette, visor extends forward.
            head.loft(7,24,-8.6f,0,.55f,.9f,.9f,-8.15f,0,.4f,2.9f,2.65f,-6.4f,0,.6f,3.45f,3.0f,-4.5f,0,1.35f,3.1f,2.2f);
            for(int i=0;i<6;i++){float x=-2.65f+i*1.06f;head.blade(7,x,-6.9f,1.8f,x+(i-2.5f)*.3f,-9.1f+(i%2)*.4f,3.2f,1.65f);}
            Part cap=head.child(0,-6.6f,-.25f);
            cap.loft(0,28,-2.9f,0,.3f,2.7f,2.4f,-2.45f,0,.18f,3.3f,2.9f,-.6f,0,0,3.6f,3.0f,.15f,0,0,3.45f,2.95f);
            cap.loft(4,28,-.65f,0,0,3.52f,3.02f,-.35f,0,0,3.57f,3.07f);
            cap.loft(0,28,.05f,0,-1.95f,3.4f,2.7f,.32f,0,-2.05f,3.5f,2.82f,.60f,0,-2.0f,3.3f,2.7f);
            cap.oval(4,-1.45f,-1.5f,-2.75f,.54f,.58f,.18f);
            cap.oval(8,1.0f,-1.5f,-2.8f,.77f,.72f,.17f);
            for(int j=0;j<4;j++)cap.oval(4,.62f+j*.24f,-1.82f,-2.95f,.095f,.34f,.10f);
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                arm[i]=body.child(s*4.55f,.45f,0);
                arm[i].loft(0,24,-.95f,0,0,1.45f,1.55f,.65f,0,0,2.1f,1.95f,2.45f,0,0,1.85f,1.75f,4.1f,0,0,1.55f,1.48f,5.5f,0,0,1.1f,1.15f);
                fore[i]=arm[i].child(0,5.25f,0);
                fore[i].loft(0,22,-.3f,0,0,1.17f,1.2f,1.4f,0,0,1.54f,1.47f,3.1f,0,0,1.25f,1.25f,4.4f,0,0,1.03f,1.02f);
                fore[i].oval(2,0,5.25f,-.15f,1.05f,1.23f,.82f);
                for(int j=0;j<3;j++)fore[i].oval(4,s*.95f,2.2f+j*.75f,-.4f,.16f,.18f,.13f);
                leg[i]=root.child(s*1.95f,11.0f,0);
                leg[i].loft(0,22,-.35f,0,0,1.8f,1.8f,2.25f,0,0,1.72f,1.66f,4.5f,0,0,1.25f,1.22f,6.1f,0,0,1.1f,1.15f);
                shin[i]=leg[i].child(0,5.9f,0);
                shin[i].loft(0,22,-.35f,0,0,1.19f,1.2f,1.3f,0,0,1.37f,1.35f,4.2f,0,0,1.0f,1.04f,6.15f,0,0,1.30f,1.22f);
                shin[i].loft(8,24,5.7f,0,-.12f,1.15f,1.24f,6.5f,0,-.65f,1.32f,1.90f,7.1f,0,-.75f,1.30f,2.0f);
            }
        }
        @Override public void setupAnim(JojoMob e,float limb,float amount,float age,float yaw,float pitch){
            head.ry=yaw*.01745f;head.rx=pitch*.013f-.045f;body.ry=(float)Math.sin(limb*.33)*amount*.04f;
            float pose=amount<.08f?(float)Math.pow(Math.max(0,Math.sin(age*.025)),12):0;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;
                arm[i].rx=-w*.50f-(i==1?pose*.90f:0);arm[i].rz=-s*.12f+(i==1?-.55f*pose:0);
                fore[i].rx=-.06f-(i==1?1.35f*pose:0);
                leg[i].rx=w*.65f;shin[i].rx=Math.max(0,-w)*.25f;
                coat[i].rx=.16f+amount*.30f+(float)Math.sin(age*.095+i)*.075f;coat[i].rz=-s*(.10f+amount*.08f);
            }
            for(int j=0;j<5;j++)chain[j].rx=(float)Math.sin(age*.12-j*.6)*(.035f+amount*.08f);
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class R extends MobRenderer<JojoMob,M>{
        R(EntityRendererProvider.Context c){super(c,new M(),.48f);}
        @Override protected void scale(JojoMob e,PoseStack p,float partial){p.scale(1.02f,1.07f,1.02f);}
        @Override public ResourceLocation getTextureLocation(JojoMob e){return new ResourceLocation(Noctis.ID,"textures/entity/jotaro_sculpted.png");}
    }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(28,28,29),(130,142,122),(220,177,141),(187,182,149),(194,147,61),(45,44,41),(220,177,141),(22,24,27),(28,36,39)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(12,13,18),.15*v+.14*(1-math.sin(u*math.pi)))
            if m==0:
                folds=math.sin(u*math.pi*9+v*3+math.sin(v*6))**2
                c=blend(c,(83,83,76),.24*folds)
                if abs(math.sin(u*math.pi*5+v*2))<.10:c=blend(c,(7,8,12),.28)
            if m==1:
                c=blend(c,(55,67,60),.22*math.sin(v*math.pi*4+u*.7)**2)
                if abs(v-.32)<.018 or abs(v-.65)<.018:c=blend(c,(46,55,49),.6)
            if m==4:
                c=blend((123,80,28),(249,217,132),.25+.66*math.sin(u*math.pi)**2)
            if m==5:
                q=(u*12)%1;tri=abs(q-.5)*2
                if .17<v<.83 and tri<1-abs(v-.5)*1.7:c=(211,105,88) if int(u*12)%2==0 else (75,159,151)
                if v<.12 or v>.88:c=(177,140,72)
            if m==6:
                c=blend(base,(140,81,63),.13*math.exp(-((v-.69)/.16)**2)+.13*clamp((f-.17)*5))
                for ex in (.398,.602):
                    dx=(u-ex)/.069;dy=(v-.49+(.045*dx if ex<.5 else -.045*dx))/.072;d=dx*dx+dy*dy
                    if d<1:c=(41,30,28)
                    if d<.75:c=(237,228,207)
                    if abs(dx)<.52 and d<.76:c=blend((43,105,103),(113,180,170),clamp((dy+.2)*.65))
                    if abs(dx)<.22 and d<.72:c=(21,29,29)
                    if (dx+.17)**2+(dy+.2)**2<.065:c=(255,255,247)
                    if abs(dx)<1.1 and abs(v-(.365+.043*dx*(1 if ex<.5 else -1)))<.022:c=(31,28,26)
                # Manga cheek / nose shadows, without duplicate eyes.
                if .09<f<.19 and abs(v-(.68+f*.4))<.013:c=blend(c,(113,62,50),.42)
                if f<.053 and abs(v-.80+.012*math.cos(f*55))<.012:c=(100,53,47)
                if f<.032 and .83<v<.85:c=blend(c,(117,64,53),.34)
            if m==7:c=blend(c,(85,91,93),.23*math.sin(u*math.pi*13+v*2)**2)
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'jotaro_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Jotaro sculpted: muscular torso, face, fused cap/hair, actual chain links and animated long coat')
