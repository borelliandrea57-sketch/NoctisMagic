"""1.4.9: sculpted Verso with signature silver forelock and articulated piano performance."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'ArtGuestClient.java';s=p.read_text(encoding='utf-8');a='e.registerEntityRenderer(Noctis.VERSO.get(),c->new Renderer(c,1));';assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'VersoSculptedClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import java.util.*;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class VersoSculptedClient {
    static final ResourceLocation OLD=new ResourceLocation(Noctis.ID,"textures/entity/verso.png");
    static final ResourceLocation NEW=new ResourceLocation(Noctis.ID,"textures/entity/verso_sculpted.png");
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.VERSO.get(),R::new);}
    static class M extends EntityModel<ArtGuest>{
        final Part root=new Part(0,0,0),body=root.child(0,4,0),head=body.child(0,-1,0);
        final Part[] arms=new Part[2],forearms=new Part[2],hands=new Part[2];
        final List<Part> locks=new ArrayList<>();
        M(){
            body.loft(0,24,-1,0,0,2.1f,1.55f,0,0,0,4.1f,2.15f,3,0,0,3.8f,2.15f,6.8f,0,0,2.95f,1.8f,10,0,0,3.1f,2.0f,12.1f,0,0,3.35f,2.1f);
            body.loft(1,24,7.5f,0,0,3.05f,1.95f,9,0,0,3.2f,2.05f,10.4f,0,0,3.2f,2.1f);
            body.loft(2,24,9.55f,0,0,3.25f,2.13f,10.15f,0,0,3.3f,2.15f);
            body.oval(3,0,9.85f,-2.1f,.75f,.45f,.18f);
            body.loft(4,16,-1.55f,0,0,1.25f,1.25f,1,0,0,1.55f,1.35f,2.1f,0,-.05f,1.7f,1.35f);
            // Broad asymmetric quilted lapels, light trim and fur collar.
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                body.blade(5,s*2.9f,-.4f,-1.65f,-s*.2f,5.2f,-2.05f,2.8f);
                body.blade(6,s*3.2f,-.15f,-1.95f,-s*.25f,5.6f,-2.2f,.35f);
                body.oval(7,s*2.3f,-.7f,.65f,2.0f,1.1f,1.9f);
                for(int j=0;j<3;j++)body.blade(7,s*(1.5f+j*.62f),-1.4f,.8f,s*(1.85f+j*.72f),.5f,1.25f,.8f);
                // Draped chains follow the chest rather than cutting through it.
                for(int j=0;j<2;j++){
                    float y=2.7f+j*1.1f;
                    body.blade(3,s*3.15f,y-.45f,-1.75f,s*1.6f,y+.5f,-2.13f,.18f);
                    body.blade(3,s*1.6f,y+.5f,-2.13f,0,y+.85f,-2.15f,.18f);
                }
            }
            Part badge=body.child(-3.35f,.75f,-1.65f);badge.rz=.16f;
            badge.loft(3,12,-.85f,0,0,.88f,.18f,.9f,0,0,.88f,.18f);
            badge.loft(6,12,-.62f,0,-.13f,.58f,.08f,.62f,0,-.13f,.58f,.08f);
            body.blade(1,2.25f,9.3f,-.65f,3.0f,18.2f,-1.2f,1.45f);
            body.blade(3,3.2f,9.75f,.8f,4.4f,14.5f,1.1f,1.1f);
            // Face with distinct cheekbones, chin, nose, beard and grey-green eyes.
            head.loft(8,32,-7.7f,0,.13f,1.45f,1.65f,-7.1f,0,.05f,2.8f,2.5f,-5.5f,0,0,3.35f,2.95f,-3.7f,0,-.05f,3.3f,2.8f,-2.0f,0,-.11f,2.95f,2.48f,-.65f,0,-.24f,2.0f,1.8f,0,0,-.2f,.8f,1.0f);
            head.loft(4,16,-3.5f,0,-2.65f,.27f,.19f,-2.7f,0,-2.9f,.40f,.46f,-2.15f,0,-2.91f,.39f,.28f);
            for(int s:new int[]{-1,1})head.oval(4,s*3.23f,-3.65f,.2f,.42f,.90f,.58f);
            head.loft(9,24,-9.1f,0,.2f,.55f,.7f,-8.8f,0,.15f,2.5f,2.3f,-7.6f,0,.25f,3.6f,3.1f,-6.4f,0,.4f,3.7f,3.15f);
            Part back=head.child(0,-6.7f,1.7f);locks.add(back);
            back.loft(9,20,-1,0,0,3.0f,1.7f,1.3f,0,.45f,3.45f,1.65f,4.2f,0,.9f,3.2f,1.6f,7.1f,0,.65f,2.8f,1.15f,8.4f,0,.8f,1.35f,.25f);
            // Wavy swept fringe: alternate broad silver and dark ribbons on the same curved flow.
            for(int j=0;j<8;j++){
                float x=-2.6f+j*.70f;
                Part q=head.child(x,-8.0f+.12f*j,-1.7f);
                int m=j<4?10:9;
                q.loft(m,14,-.8f,0,.65f,.60f,.65f,.55f,-.45f,-.35f,.85f,.77f,1.7f,-.85f,-1.0f,.78f,.65f,3.1f,-1.15f,-.72f,.54f,.40f,4.1f+(j%3)*.22f,-.70f,-.2f,.04f,.06f);
                locks.add(q);
            }
            for(int i=0;i<2;i++){int s=i==0?-1:1;
                for(int j=0;j<3;j++){
                    Part q=head.child(s*(2.9f-.15f*j),-6.2f+j*.3f,.3f+j*.75f);locks.add(q);
                    q.loft(9,12,-.6f,0,0,.72f,1.1f,1.5f,s*.65f,-.15f,1.0f,1.0f,3.9f,s*.48f,.55f,.86f,.8f,5.5f,-s*.1f,.65f,.52f,.54f,6.8f,s*.2f,.92f,.04f,.06f);
                }
                arms[i]=body.child(s*4.15f,.45f,0);
                arms[i].loft(0,18,-.7f,0,0,1.25f,1.3f,.7f,0,0,1.75f,1.65f,2.65f,0,0,1.64f,1.53f,3.55f,0,0,1.3f,1.34f);
                arms[i].loft(4,16,3.45f,0,0,1.3f,1.34f,5.2f,0,0,1.08f,1.1f);
                forearms[i]=arms[i].child(0,5.0f,0);
                forearms[i].loft(2,18,0,0,0,1.1f,1.12f,1.6f,0,0,1.19f,1.18f,3.3f,0,0,.85f,.87f,4.0f,0,0,.84f,.85f);
                for(int j=0;j<2;j++)forearms[i].loft(5,16,.6f+j*1.7f,0,0,1.16f-j*.13f,1.17f-j*.13f,.95f+j*1.7f,0,0,1.15f-j*.13f,1.16f-j*.13f);
                hands[i]=forearms[i].child(0,4,0);
                hands[i].oval(2,0,.65f,-.12f,.89f,1.10f,.65f);
                for(int j=0;j<4;j++)hands[i].oval(4,-.63f+j*.42f,1.5f,-.35f,.21f,.65f-(j==3?.13f:0),.29f);
                hands[i].oval(4,-s*.85f,.95f,-.44f,.28f,.45f,.27f);
                // A seated leg: horizontal thigh, downward calf, planted boot.
                Part thigh=root.child(s*1.85f,15.1f,0);thigh.rx=-1.48f;
                thigh.loft(11,18,-.3f,0,0,1.6f,1.6f,2,0,0,1.55f,1.48f,5.8f,0,0,1.26f,1.26f);
                Part calf=thigh.child(0,5.6f,0);calf.rx=1.48f;
                calf.loft(11,18,-.5f,0,0,1.3f,1.28f,2,0,0,1.05f,1.1f,6,0,0,.90f,.93f);
                calf.loft(2,18,4.5f,0,0,1.0f,1.05f,6.5f,0,-.15f,.92f,1.25f,8.2f,0,-.5f,1.18f,1.75f);
            }
        }
        @Override public void setupAnim(ArtGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.motion();body.rx=.035f+(float)Math.sin(age*.08)*.018f;head.rx=.12f+a*.05f;head.ry=(float)Math.sin(age*.035)*.07f;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float tap=(float)Math.sin(age*.75+i*1.7)*a;
                arms[i].rx=-.68f+tap*.05f;arms[i].rz=-s*.11f;forearms[i].rx=-.97f+tap*.08f;
                hands[i].rx=.1f+tap*.15f;hands[i].ry=(float)Math.sin(age*.12+i)*a*.12f;
            }
            for(int j=0;j<locks.size();j++)locks.get(j).rz=(float)Math.sin(age*.08+j*.4)*.014f;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class Piano extends RenderLayer<ArtGuest,M>{
        final ModelPart prop,bench;
        Piano(R parent,ModelPart r){super(parent);prop=r.getChild("prop");bench=r.getChild("bench");}
        @Override public void render(PoseStack p,MultiBufferSource buf,int light,ArtGuest e,float limb,float amount,float partial,float age,float yaw,float pitch){
            if(e.isInvisible())return;
            for(int j=0;j<10;j++)prop.getChild("key"+j).y=e.motion()>0&&j==(int)(age/8)%10?.35f:0;
            VertexConsumer v=buf.getBuffer(RenderType.entityCutoutNoCull(OLD));prop.render(p,v,light,OverlayTexture.NO_OVERLAY,1,1,1,1);bench.render(p,v,light,OverlayTexture.NO_OVERLAY,1,1,1,1);
        }
    }
    static class R extends MobRenderer<ArtGuest,M>{
        R(EntityRendererProvider.Context c){super(c,new M(),.65f);addLayer(new Piano(this,c.bakeLayer(ArtGuestClient.L[1])));}
        @Override public ResourceLocation getTextureLocation(ArtGuest e){return NEW;}
    }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(34,43,48),(57,61,113),(29,31,35),(185,147,76),(211,158,125),(43,53,57),(224,218,196),(119,117,116),(218,169,137),(37,33,35),(190,193,194),(43,43,50)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(20,18,27),.12*v+.10*(1-math.sin(u*math.pi)))
            if m in (0,5):
                a=abs(math.sin((u*11+v*6)*math.pi));b=abs(math.sin((u*11-v*6)*math.pi))
                c=blend(c,(99,111,114),.14*min(a,b))
                if min(a,b)<.105:c=blend(c,(14,18,22),.45)
            if m==1:c=blend(c,(103,111,169),.25*math.sin(v*math.pi*7+u*.4)**2)
            if m==3:c=blend((110,77,37),(229,202,132),.35+.55*math.sin(u*math.pi)**2)
            if m in (7,9,10):
                wave=math.sin(u*math.pi*13+math.sin(v*4.8)*1.25)**2
                c=blend(base,(145,144,149) if m==7 else (105,101,108) if m==9 else (245,245,239),.32*wave+.10*math.exp(-((v-.28)/.17)**2))
                c=blend(c,(25,24,30),.12*(1-wave))
            if m==8:
                c=blend(base,(145,86,70),.16*math.exp(-((v-.69)/.18)**2)+.14*clamp((f-.17)*4))
                # A single beard and moustache on the continuous face UV.
                beard=(v>.73-.24*clamp((f-.055)*6) and f<.31)
                if beard:
                    grain=.50+.24*math.sin(u*127+v*71)**2
                    c=blend(c,(47,36,35),grain+.17*clamp((v-.71)*7))
                for ex in (.397,.603):
                    dx=(u-ex)/.067;dy=(v-.505+(.04*dx if ex<.5 else -.04*dx))/.085;d=dx*dx+dy*dy
                    if d<1:c=(66,42,36)
                    if d<.77:c=(233,225,208)
                    if abs(dx)<.52 and d<.78:c=blend((65,86,77),(154,169,145),clamp((dy+.2)*.6))
                    if abs(dx)<.22 and abs(dy)<.75 and d<.8:c=(27,31,30)
                    if (dx+.16)**2+(dy+.23)**2<.073:c=(255,255,246)
                    if abs(dx)<1.05 and abs(v-(.365+.033*dx*(1 if ex<.5 else -1)))<.019:c=(54,38,33)
                if f<.068 and abs(v-.735-.035*math.sin(f*31))<.023:c=(56,40,35)
                if f<.046 and abs(v-.805+.009*math.cos(f*55))<.012:c=(117,63,53)
                if f<.013 and .63<v<.70:c=blend(c,(162,98,77),.18)
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'verso_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Verso: silver swept hair, beard, quilted coat and seated piano animation')
