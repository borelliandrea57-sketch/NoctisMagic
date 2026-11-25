"""1.4.8: Maelle sculpted redesign, retains original animated easel."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'ArtGuestClient.java';s=p.read_text(encoding='utf-8');a='e.registerEntityRenderer(Noctis.MAELLE.get(),c->new Renderer(c,0));';assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'MaelleSculptedClient.java').write_text('''package it.noctis.magic;
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
public class MaelleSculptedClient {
    static final ResourceLocation OLD=new ResourceLocation(Noctis.ID,"textures/entity/maelle.png");
    static final ResourceLocation NEW=new ResourceLocation(Noctis.ID,"textures/entity/maelle_sculpted.png");
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MAELLE.get(),R::new);}
    static class M extends EntityModel<ArtGuest>{
        final Part root=new Part(0,0,0),body=root.child(0,0,0),head=root.child(0,-1,0);
        final Part[] arms=new Part[2],forearms=new Part[2],legs=new Part[2],tails=new Part[2];
        final Part pony,ponyEnd;
        final List<Part> strands=new ArrayList<>();
        M(){
            body.loft(0,24,-.85f,0,0,1.85f,1.4f,.1f,0,0,3.25f,1.85f,2.7f,0,0,3.15f,1.9f,6.5f,0,0,2.45f,1.55f,9.8f,0,0,2.6f,1.7f,11.2f,0,0,3.1f,1.95f);
            body.loft(1,24,8.9f,0,0,2.58f,1.65f,9.65f,0,0,2.67f,1.78f);
            body.loft(2,20,-1.3f,0,0,1.3f,1.1f,-.65f,0,0,1.52f,1.36f,.8f,0,0,1.6f,1.44f);
            body.loft(1,20,-1.2f,0,0,1.36f,1.17f,-.95f,0,0,1.55f,1.4f);
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                body.blade(3,s*1.4f,0,-1.65f,s*2.0f,8.8f,-1.75f,.75f);
                body.blade(1,s*1.7f,.5f,-1.85f,s*2.0f,8.3f,-1.78f,.23f);
                for(int j=0;j<3;j++)body.oval(1,s*.85f,3.2f+j*1.6f,-1.9f,.23f,.22f,.12f);
                tails[i]=body.child(s*1.75f,10.7f,1.1f);
                tails[i].loft(0,14,0,0,0,1.5f,.35f,3,s*.4f,.55f,1.7f,.38f,7,s*.65f,1.1f,1.25f,.24f,9,s*.6f,1.3f,.08f,.06f);
                tails[i].blade(1,s*1.35f,.3f,-.3f,s*1.5f,8,1.1f,.21f);
            }
            // The ornamental shoulder mantle has its own art-deco texture.
            Part mantle=body.child(-2.5f,.25f,0);mantle.rz=.31f;
            mantle.loft(4,24,-1.15f,0,0,1.6f,1.45f,-.6f,-.25f,0,2.15f,2.15f,1.1f,-.65f,0,2.6f,2.35f,2.7f,-.9f,.15f,2.55f,2.15f,4.1f,-1.2f,.45f,2.2f,1.3f);
            mantle.loft(1,24,3.65f,-1.1f,.42f,2.3f,1.5f,3.95f,-1.17f,.45f,2.24f,1.4f);
            head.loft(5,32,-7.3f,0,.13f,1.35f,1.65f,-6.75f,0,.08f,2.6f,2.4f,-5.3f,0,0,3.2f,2.83f,-3.6f,0,-.05f,3.13f,2.75f,-1.85f,0,-.16f,2.65f,2.35f,-.7f,0,-.23f,1.7f,1.6f,0,0,-.3f,.65f,.9f);
            head.oval(6,0,-2.7f,-2.75f,.34f,.45f,.38f);
            for(int s:new int[]{-1,1})head.oval(6,s*3.13f,-3.5f,.12f,.39f,.78f,.55f);
            // Smooth crown, part in the middle and swept copper waves framing the cheeks.
            head.loft(7,24,-8.8f,0,.2f,.52f,.65f,-8.5f,0,.2f,2.45f,2.25f,-7.4f,0,.3f,3.4f,3.1f,-6.2f,0,.55f,3.52f,3.08f);
            Part back=head.child(0,-6.8f,1.8f);
            back.loft(7,20,-.9f,0,0,2.7f,1.65f,1.3f,0,.5f,3.2f,1.7f,4.3f,0,.75f,3.0f,1.5f,6.4f,0,1.05f,1.6f,.55f);
            for(int i=0;i<2;i++){int s=i==0?-1:1;
                for(int j=0;j<4;j++){
                    Part lock=head.child(s*(.45f+j*.64f),-7.65f+j*.2f,-2.05f);
                    lock.loft(7,12,-.45f,0,.5f,.6f,.62f,.55f,s*.55f,-.5f,.86f,.72f,1.9f,s*.95f,-.85f,.83f,.55f,3.25f,s*1.25f,-.60f,.55f,.34f,4.4f+j*.15f,s*1.35f,.1f,.045f,.07f);
                    strands.add(lock);
                }
                Part side=head.child(s*2.95f,-5.7f,.35f);
                side.loft(7,14,-.6f,0,0,.7f,1.0f,1.4f,s*.4f,-.3f,.84f,1.0f,3.6f,s*.35f,-.55f,.7f,.65f,5.2f,-s*.2f,-.4f,.05f,.08f);
                strands.add(side);
            }
            pony=head.child(0,-5.3f,3.2f);pony.rx=.25f;
            pony.oval(1,0,.4f,.25f,1.3f,.55f,1.15f);
            pony.loft(7,20,-.3f,0,0,1.15f,1.05f,1.6f,0,1.9f,1.65f,1.35f,4.3f,-.3f,3.1f,1.85f,1.6f,7.0f,-.65f,4.3f,1.6f,1.4f);
            ponyEnd=pony.child(-.65f,6.5f,4.2f);
            for(int j=0;j<5;j++){
                float x=-1.2f+j*.6f;
                ponyEnd.loft(7,10,-.5f,x,0,.55f,.6f,2.2f,x*1.12f,.8f,.65f,.7f,4.8f,x*1.4f,1.2f,.48f,.52f,7.1f+j%2,x*1.7f,1.0f,.04f,.05f);
            }
            for(int i=0;i<2;i++){int s=i==0?-1:1;
                arms[i]=root.child(s*3.85f,.35f,0);
                arms[i].loft(0,18,-.7f,0,0,1.15f,1.15f,.75f,0,0,1.45f,1.35f,3.2f,0,0,1.23f,1.17f,5.0f,0,0,1.0f,1.0f);
                forearms[i]=arms[i].child(0,4.7f,0);
                forearms[i].loft(3,18,0,0,0,1.02f,1.04f,1.4f,0,0,1.14f,1.1f,4.25f,0,0,.80f,.81f);
                forearms[i].loft(1,16,3.85f,0,0,.86f,.87f,4.25f,0,0,.83f,.84f);
                forearms[i].oval(6,0,5.05f,-.12f,.75f,1.0f,.6f);
                for(int j=0;j<3;j++)forearms[i].oval(6,-.43f+j*.43f,5.55f,-.4f,.21f,.57f,.25f);
                legs[i]=root.child(s*1.78f,11,0);
                legs[i].loft(8,18,0,0,0,1.56f,1.5f,3.2f,0,0,1.33f,1.25f,6.7f,0,0,1.04f,1.04f);
                legs[i].loft(9,18,6.3f,0,0,1.1f,1.08f,9.2f,0,0,.85f,.9f,11.3f,0,-.27f,.85f,1.13f,12.7f,0,-.55f,1.05f,1.7f,13,0,-.55f,1.0f,1.65f);
                if(i==1){legs[i].loft(1,18,1.4f,0,0,1.48f,1.43f,1.75f,0,0,1.45f,1.4f);legs[i].loft(1,18,2.1f,0,0,1.43f,1.39f,2.4f,0,0,1.4f,1.35f);}
            }
            Part brush=forearms[1].child(0,5.35f,-.45f);brush.rx=-.9f;
            brush.loft(10,12,-.7f,0,0,.22f,.22f,5.5f,0,0,.22f,.22f);
            brush.loft(1,12,5.5f,0,0,.29f,.29f,6.15f,0,0,.3f,.3f);
            brush.loft(11,12,6.15f,0,0,.33f,.33f,7.2f,0,-.1f,.02f,.02f);
            Part palette=forearms[0].child(0,5.2f,-.6f);palette.rx=1.1f;
            palette.loft(10,24,-.3f,0,0,2.6f,1.8f,.2f,0,0,2.7f,1.9f,.45f,0,0,2.55f,1.7f);
            palette.oval(14,-1.3f,-.3f,-.55f,.45f,.14f,.37f);
            palette.oval(15,0,-.3f,-1.0f,.45f,.14f,.37f);
            palette.oval(1,1.3f,-.3f,-.4f,.45f,.14f,.37f);
        }
        @Override public void setupAnim(ArtGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.motion();head.rx=.10f+a*.065f;head.ry=(float)Math.sin(age*.04)*.09f;head.rz=.025f;
            arms[1].rx=-.72f-a*.30f;arms[1].rz=-.10f+a*.12f;forearms[1].rx=-.68f-a*.25f;
            arms[0].rx=-.42f;arms[0].rz=.16f;forearms[0].rx=-.75f;
            pony.rx=.25f+(float)Math.sin(age*.12)*.045f;ponyEnd.rx=(float)Math.sin(age*.12-.6)*.09f;
            for(int i=0;i<strands.size();i++)strands.get(i).rz=(float)Math.sin(age*.09+i*.45)*.013f;
            for(int i=0;i<2;i++)tails[i].rx=.10f+(float)Math.sin(age*.09+i)*.035f;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class Easel extends RenderLayer<ArtGuest,M>{
        final ModelPart prop;
        Easel(R parent,ModelPart p){super(parent);prop=p.getChild("prop");}
        @Override public void render(PoseStack p,MultiBufferSource buf,int light,ArtGuest e,float limb,float amount,float partial,float age,float yaw,float pitch){
            if(e.isInvisible())return;
            for(int j=0;j<5;j++)prop.getChild("stripe"+j).visible=j<e.progress();
            prop.render(p,buf.getBuffer(RenderType.entityCutoutNoCull(OLD)),light,OverlayTexture.NO_OVERLAY,1,1,1,1);
        }
    }
    static class R extends MobRenderer<ArtGuest,M>{
        R(EntityRendererProvider.Context c){super(c,new M(),.65f);addLayer(new Easel(this,c.bakeLayer(ArtGuestClient.L[0])));}
        @Override public ResourceLocation getTextureLocation(ArtGuest e){return NEW;}
    }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(34,41,57),(199,157,75),(29,34,45),(48,43,68),(42,48,63),(237,193,164),(237,193,164),(177,77,51),(44,43,49),(29,29,37),(104,68,42),(91,53,33),(240,240,240),(240,240,240),(170,52,55),(55,104,159)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(20,18,29),.10*v+.11*(1-math.sin(u*math.pi)))
            if m in (0,3,8,9):
                c=blend(c,base,.30*math.sin(u*math.pi*10+v*.5)**2)
                if m==3 and abs(math.sin(u*math.pi*6))<.1:c=blend(c,(85,73,99),.22)
                if m==0 and (v>.94 or v<.027):c=pal[1]
            if m==1:c=blend((119,82,42),(239,205,132),.3+.62*math.sin(u*math.pi)**2)
            if m==4:
                a=(u*4)%1-.5;b=v-.32;r=math.hypot(a,b);ang=math.atan2(b,a)
                if abs(r-.24)<.016 or abs(r-.33)<.012 or (r<.33 and abs(math.sin(ang*8))<.11) or abs(v-.86)<.018 or abs(v-.94)<.012:c=pal[1]
                if abs(v-.90)<.011:c=(220,221,213)
            if m==7:
                wave=math.sin(u*math.pi*15+math.sin(v*5)*1.1)**2
                c=blend(base,(239,142,99),.30*wave+.16*math.exp(-((v-.28)/.15)**2))
                c=blend(c,(82,31,31),.13*(1-wave))
            if m==5:
                c=blend(base,(177,100,88),.12*math.exp(-((v-.70)/.18)**2)+.10*clamp((f-.17)*5))
                for ex in (.397,.603):
                    dx=(u-ex)/.066;dy=(v-.52+(.022*dx if ex<.5 else -.022*dx))/.093;d=dx*dx+dy*dy
                    if d<1:c=(80,49,44)
                    if d<.82:c=(248,238,225)
                    if abs(dx)<.53 and d<.80:c=blend((58,89,80),(146,181,156),clamp((dy+.2)*.6))
                    if abs(dx)<.22 and abs(dy)<.75 and d<.8:c=(32,40,38)
                    if (dx+.16)**2+(dy+.24)**2<.075:c=(255,255,249)
                    if abs(dx)<1.05 and abs(v-(.37+.021*dx*(1 if ex<.5 else -1)))<.013:c=(126,65,46)
                for ex,ey in ((.453,.645),(.465,.67),(.480,.65),(.49,.675),(.513,.665),(.526,.65),(.543,.677),(.555,.648),(.434,.66),(.571,.664)):
                    if ((u-ex)/.004)**2+((v-ey)/.006)**2<1:c=blend(c,(137,76,57),.63)
                if f<.044 and abs(v-.81+.013*math.cos(f*55))<.011:c=(159,82,76)
                if f<.027 and .82<v<.84:c=blend(c,(211,128,116),.35)
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'maelle_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Maelle: sculpted copper hair, asymmetrical embroidered uniform and separate original easel layer')
