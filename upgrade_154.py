"""1.5.4: sculpted Griffith, flowing silver curls and Renaissance plate armor."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
(java/'GriffithClient.java').write_text('''package it.noctis.magic;
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
public class GriffithClient{
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.GRIFFITH.get(),R::new);}
    static class M extends EntityModel<Griffith>{
        final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1.3f,0);
        final Part[] arm=new Part[2],fore=new Part[2],leg=new Part[2],shin=new Part[2];
        final List<Part> curls=new ArrayList<>(),ends=new ArrayList<>();
        M(){
            // Curved breastplate, shaped waist, layered fauld and crossed leather belts.
            body.loft(0,32,-.9f,0,0,1.9f,1.45f,.3f,0,0,3.8f,2.25f,2.4f,0,-.25f,3.95f,2.6f,5.7f,0,-.18f,3.3f,2.1f,8.4f,0,0,2.55f,1.65f,9.6f,0,0,2.8f,1.85f);
            body.loft(1,24,-1.8f,0,0,1.3f,1.2f,-1.25f,0,0,1.7f,1.5f,.8f,0,0,2.0f,1.65f);
            for(int i=0;i<4;i++){float y=8.9f+i*.76f,w=2.68f+i*.24f;
                body.loft(0,24,y,0,0,w,1.9f+i*.11f,y+.62f,0,0,w+.16f,2.05f+i*.11f);
            }
            body.loft(2,24,8.2f,0,0,2.66f,1.83f,9.0f,0,0,2.8f,1.94f);
            Part strap=body.child(0,10,0);strap.rz=-.19f;
            strap.loft(2,24,-.3f,0,0,3.17f,2.13f,.38f,0,0,3.20f,2.15f);
            for(int j=0;j<2;j++)body.oval(3,.55f,8.6f+j*1.4f,-2.04f,.62f,.40f,.17f);
            // Delicate face: smooth cheeks, narrow chin, continuous UV, small sculpted nose.
            head.loft(4,32,-7.6f,0,.15f,1.4f,1.7f,-7.1f,0,.05f,2.6f,2.45f,-5.5f,0,0,3.2f,2.85f,-3.7f,0,-.08f,3.10f,2.76f,-2,0,-.15f,2.55f,2.32f,-.65f,0,-.20f,1.52f,1.55f,0,0,-.25f,.55f,.85f);
            head.loft(5,16,-3.6f,0,-2.6f,.23f,.15f,-2.7f,0,-2.87f,.32f,.43f,-2.1f,0,-2.87f,.28f,.20f);
            for(int s:new int[]{-1,1})head.oval(5,s*3.05f,-3.3f,.1f,.38f,.78f,.55f);
            // Rounded crown and independent soft, S-shaped silver curls, no flat hair slabs.
            head.loft(6,28,-9.2f,0,.1f,.65f,.70f,-8.9f,0,.1f,2.5f,2.4f,-7.7f,0,.2f,3.65f,3.15f,-6.1f,0,.35f,3.65f,3.05f);
            for(int j=0;j<8;j++){
                float x=-2.9f+j*.82f;Part q=head.child(x,-8.0f,-2.0f);float d=(j-3.5f)*.12f;
                q.loft(6,16,-.6f,0,.55f,.66f,.72f,.55f,d-.35f,-.35f,.88f,.83f,1.6f,d+.27f,-.82f,.84f,.65f,2.65f,d+.43f,-.70f,.66f,.46f,3.55f+(j%2)*.25f,d-.10f,-.32f,.09f,.1f);
                curls.add(q);
            }
            Part back=head.child(0,-6.7f,1.9f);
            back.loft(6,24,-.7f,0,0,2.9f,1.8f,1.4f,0,.5f,3.5f,1.65f,4.6f,0,1.15f,3.5f,1.65f,8.2f,0,1.55f,3.35f,1.45f,11.9f,0,1.7f,2.9f,1.05f,14.8f,0,1.6f,1.5f,.25f);
            for(int j=0;j<9;j++){
                float x=-3.05f+j*.76f,phase=j*.85f;
                Part q=head.child(x,-6.5f,2.65f);curls.add(q);
                q.loft(6,14,0,0,0,.66f,.78f,2.5f,.55f*(float)Math.sin(phase),.6f,.86f,.88f,5.5f,.75f*(float)Math.sin(phase+1.7f),.65f,.84f,.87f,8.3f,.8f*(float)Math.sin(phase+3.3f),1.05f,.79f,.72f,11.5f,.65f*(float)Math.sin(phase+4.9f),1.5f,.65f,.59f);
                Part tip=q.child(.65f*(float)Math.sin(phase+4.9f),11.3f,1.5f);ends.add(tip);
                tip.loft(6,14,-.25f,0,0,.65f,.60f,1.7f,.45f*(float)Math.sin(phase),.45f,.63f,.62f,3.4f,-.5f*(float)Math.sin(phase),.5f,.43f,.39f,5.1f+(j%3)*.5f,.35f*(float)Math.sin(phase+1),.65f,.035f,.05f);
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                for(int j=0;j<3;j++){
                    Part q=head.child(s*(2.75f+j*.19f),-5.8f+j*.45f,-.1f+j*.72f);curls.add(q);
                    q.loft(6,16,-.7f,0,0,.75f,1.05f,1.3f,s*.72f,-.15f,.91f,1.0f,3.2f,s*.13f,-.6f,.85f,.78f,5.25f,s*.85f,-.65f,.88f,.72f,7.3f,s*.40f,-.95f,.72f,.64f,9.4f,s*.95f,-.85f,.65f,.57f);
                    Part tip=q.child(s*.95f,9.15f,-.85f);ends.add(tip);
                    tip.loft(6,14,-.3f,0,0,.66f,.59f,1.7f,-s*.4f,-.35f,.65f,.55f,3.35f,s*.25f,-.2f,.42f,.38f,4.8f,-s*.38f,.12f,.045f,.055f);
                }
                arm[i]=body.child(s*4.05f,.35f,0);
                // Overlapping curved pauldrons, riveted edges, articulated arm harness.
                for(int j=0;j<3;j++){
                    float y=j*1.15f,w=2.05f-j*.22f;
                    Part plate=arm[i].child(s*.17f*j,y,0);plate.rz=-s*.13f;
                    plate.loft(0,24,-1.15f,0,0,w*.63f,1.4f,-.55f,0,0,w,1.85f,.85f,0,0,w*.97f,1.75f,1.65f,s*.15f,0,w*.83f,1.43f);
                    plate.oval(3,s*w*.72f,.75f,-1.2f,.15f,.15f,.12f);
                }
                arm[i].loft(7,20,1.8f,0,0,1.3f,1.25f,4.6f,0,0,1.03f,1.02f);
                fore[i]=arm[i].child(0,4.7f,0);
                fore[i].oval(0,0,0,-.03f,1.43f,1.25f,1.32f);
                fore[i].loft(0,24,.7f,0,0,1.27f,1.2f,2.35f,0,0,1.25f,1.16f,4.3f,0,0,.83f,.87f);
                fore[i].oval(0,0,5.12f,-.15f,.91f,1.03f,.69f);
                for(int j=0;j<3;j++)fore[i].oval(0,-.45f+j*.45f,5.72f,-.36f,.22f,.52f,.26f);
                leg[i]=root.child(s*1.72f,11.1f,0);
                leg[i].loft(0,22,-.2f,0,0,1.63f,1.5f,2.4f,0,0,1.5f,1.4f,5.7f,0,0,1.07f,1.12f);
                shin[i]=leg[i].child(0,5.5f,0);
                shin[i].oval(0,0,0,-.4f,1.28f,1.1f,1.10f);
                shin[i].loft(0,22,.3f,0,0,1.15f,1.18f,2.1f,0,0,1.28f,1.25f,5.1f,0,-.05f,.83f,.9f,6.8f,0,-.25f,1.0f,1.12f);
                shin[i].loft(0,24,6.1f,0,-.45f,1.02f,1.5f,7.2f,0,-.65f,1.13f,1.82f,7.4f,0,-.65f,1.10f,1.78f);
            }
            // Falcon-style helmet carried in the left hand.
            Part helm=fore[0].child(-.15f,3.9f,-1.5f);helm.rx=-.35f;helm.rz=.2f;
            helm.loft(0,28,-3.8f,0,0,.3f,.35f,-3.3f,0,0,1.8f,1.7f,-1.6f,0,0,2.25f,2.2f,.1f,0,-.25f,1.8f,2.3f,1.65f,0,-.6f,1.1f,1.7f,2.2f,0,-.5f,.55f,.8f);
            helm.blade(8,-1.65f,-.8f,-1.8f,0,.65f,-2.85f,.55f);
            helm.blade(8,1.65f,-.8f,-1.8f,0,.65f,-2.85f,.55f);
            helm.blade(0,0,-2.2f,-1.65f,0,1.65f,-3.0f,.85f);
            // Slim sword drawn for the Eclipse combat animation.
            Part sword=fore[1].child(0,5.0f,-.45f);sword.rx=-1.15f;
            sword.loft(2,12,-.7f,0,0,.29f,.29f,1.35f,0,0,.29f,.29f);
            sword.blade(3,-1.45f,1.2f,0,1.45f,1.2f,0,.42f);
            sword.loft(0,12,1.35f,0,0,.48f,.17f,2.2f,0,0,.56f,.18f,10.5f,0,0,.34f,.12f,12.4f,0,0,.025f,.035f);
            weapon=sword;
        }
        final Part weapon;
        @Override public void setupAnim(Griffith e,float limb,float amount,float age,float yaw,float pitch){
            float hit=e.slashing();head.ry=yaw*.01745f;head.rx=pitch*.014f;body.ry=hit*.3f;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float walk=(float)Math.cos(limb*.666+i*Math.PI)*amount;
                arm[i].rx=i==0?-.24f-walk*.16f:-walk*.55f-hit*1.55f;
                arm[i].rz=-s*.13f;fore[i].rx=i==0?-.65f:-.06f-hit*.52f;
                leg[i].rx=walk*.65f;shin[i].rx=Math.max(0,-walk)*.3f;
            }
            for(int i=0;i<curls.size();i++)curls.get(i).rx=amount*.065f+(float)Math.sin(age*.10+i*.57f)*.024f;
            for(int i=0;i<ends.size();i++){ends.get(i).rx=amount*.18f+(float)Math.sin(age*.12+i*.65f)*.09f;ends.get(i).rz=(float)Math.sin(age*.08+i*.55f)*.055f;}
            if(e.eclipsed()){if(!fore[1].children.contains(weapon))fore[1].children.add(weapon);}else fore[1].children.remove(weapon);
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class R extends MobRenderer<Griffith,M>{
        R(EntityRendererProvider.Context c){super(c,new M(),.37f);}
        @Override public ResourceLocation getTextureLocation(Griffith e){return new ResourceLocation(Noctis.ID,"textures/entity/griffith_sculpted.png");}
    }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(204,216,232),(173,185,207),(91,71,61),(174,181,195),(245,216,188),(245,216,188),(242,239,250),(102,108,125),(27,34,50)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(57,69,96),.10*v+.15*(1-math.sin(u*math.pi)))
            if m in (0,1,3):
                c=blend(c,(253,254,255),.65*math.exp(-((u-.35)/.16)**2))
                c=blend(c,(75,90,122),.23*math.exp(-((u-.76)/.12)**2))
                if v>.96 or v<.025:c=blend(c,(89,100,129),.31)
            if m==6:
                wave=math.sin(u*math.pi*9+math.sin(v*7)*.9)**2
                c=blend(base,(151,150,190),.24*(1-wave)+.09*math.sin(v*8)**2)
                c=blend(c,(255,254,255),.32*math.exp(-((u-.38)/.15)**2))
            if m==7:
                a=abs(math.sin(u*math.pi*15+v*12));b=abs(math.sin(u*math.pi*15-v*12))
                if min(a,b)<.25:c=blend(c,(182,185,199),.48)
            if m==4:
                c=blend(base,(194,135,124),.12*math.exp(-((v-.70)/.17)**2)+.10*clamp((f-.17)*5))
                for ex in (.397,.603):
                    dx=(u-ex)/.068;dy=(v-.505+(.024*dx if ex<.5 else -.024*dx))/.093;d=dx*dx+dy*dy
                    if d<1:c=(72,65,83)
                    if d<.83:c=(250,249,240)
                    if abs(dx)<.54 and d<.82:c=blend((62,108,168),(151,191,225),clamp((dy+.15)*.65))
                    if abs(dx)<.22 and abs(dy)<.75 and d<.8:c=(30,42,70)
                    if (dx+.16)**2+(dy+.25)**2<.095:c=(255,255,255)
                    if abs(dx)<1 and abs(v-(.365+.018*dx*(1 if ex<.5 else -1)))<.012:c=(150,143,168)
                    if abs(dy+.93)<.095 and abs(dx)<1:c=(63,53,73)
                if f<.043 and abs(v-.81+.012*math.cos(f*60))<.012:c=(163,93,101)
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'griffith_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Griffith: flowing silver curls, sculpted face, layered plate armor, helmet and Eclipse sword')
