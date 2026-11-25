"""1.4.6: distinguish Maomao and Jinshi with sculpted faces, layered hanfu and animated hair."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
(java/'SushiGuestClient.java').write_text('''package it.noctis.magic;
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
public class SushiGuestClient{
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
        e.registerEntityRenderer(Noctis.MAOMAO.get(),c->new Renderer(c,true));
        e.registerEntityRenderer(Noctis.JINSHI.get(),c->new Renderer(c,false));
    }
    static class Model extends EntityModel<SushiGuest>{
        final boolean mao;
        final Part root=new Part(0,0,0),body=root.child(0,0,0),head=root.child(0,-1,0);
        final Part[] arms=new Part[2],feet=new Part[2],panels=new Part[2];
        final List<Part> locks=new ArrayList<>();
        final Part tray;
        Model(boolean mao){
            this.mao=mao;
            float width=mao?3.1f:3.7f;
            // Distinct silhouettes: Maomao's short green robe and Jinshi's tall lilac court robes.
            body.loft(0,24,-.8f,0,0,1.85f,1.35f,.25f,0,0,width,1.9f,3.7f,0,0,width*.94f,1.8f,7.8f,0,0,2.5f,1.5f,10.1f,0,0,2.8f,1.7f);
            body.loft(1,24,9.1f,0,0,2.55f,1.65f,10.8f,0,0,2.9f,1.8f);
            body.loft(2,24,10.5f,0,0,2.7f,1.7f,14,0,0,3.4f,2.2f,19,0,0,4.1f,2.6f,22.5f,0,0,4.45f,2.85f,23,0,0,4.3f,2.8f);
            body.loft(3,16,-1.3f,0,0,1.35f,1.2f,.3f,0,0,1.5f,1.35f,1.3f,0,-.1f,1.75f,1.45f);
            // Crossed lapels, pale undercollar and sash wrapping around the waist.
            for(int s:new int[]{-1,1}){
                body.blade(4,s*1.9f,-.5f,-1.65f,-s*1.15f,5.2f,-1.95f,1.65f);
                body.blade(3,s*1.2f,-.9f,-1.78f,-s*.45f,3.3f,-2.0f,.65f);
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                panels[i]=body.child(s*1.8f,10.7f,-1.65f);
                panels[i].blade(4,s*.45f,0,0,s*1.8f,11.8f,-.65f,1.55f);
                if(!mao)panels[i].blade(5,s*.8f,.3f,-.15f,s*2.05f,11.5f,-.75f,.48f);
            }
            // Face geometry and continuous face UV: two eyes, never on the hair or other surfaces.
            float fw=mao?3.30f:3.05f;
            head.loft(6,32,-7.15f,0,.1f,1.5f,1.6f,-6.7f,0,.05f,2.65f,2.35f,-5.3f,0,0,fw,2.83f,-3.45f,0,-.05f,fw,2.75f,-1.9f,0,-.12f,mao?2.72f:2.5f,2.35f,-.65f,0,-.18f,mao?1.85f:1.45f,1.6f,0,0,-.25f,.72f,.85f);
            head.oval(7,0,-2.7f,-2.70f,.34f,.46f,.37f);
            for(int s:new int[]{-1,1})head.oval(7,s*fw,-3.3f,.0f,.43f,.87f,.57f);
            // Continuous crown, hairline stays above eyes.
            head.loft(8,24,-8.7f,0,.1f,.60f,.65f,-8.45f,0,.1f,2.3f,2.1f,-7.5f,0,.2f,3.35f,3.05f,-6.25f,0,.35f,3.55f,3.05f);
            if(mao){
                head.oval(8,-1.8f,-8.2f,1.4f,1.95f,1.6f,1.85f);
                head.oval(8,1.8f,-8.2f,1.4f,1.95f,1.6f,1.85f);
                head.oval(9,0,-9.25f,2.1f,.85f,.32f,.8f);
                for(int i=0;i<7;i++){
                    float x=-2.7f+i*.9f;Part strand=head.child(x,-7.1f,-2.55f);
                    strand.loft(8,12,-.7f,0,.35f,.7f,.75f,.55f,0,-.22f,.63f,.48f,1.55f,(i-3)*.09f,-.42f,.49f,.31f,2.5f+(i%2)*.3f,(i-3)*.14f,-.27f,.04f,.07f);
                }
                Part back=head.child(0,-6.4f,1.8f);locks.add(back);
                back.loft(8,20,-.8f,0,0,2.8f,1.6f,2,0,.2f,3.15f,1.5f,5,0,.7f,3.0f,1.3f,7.3f,0,.8f,2.65f,.9f,9,0,1.1f,.2f,.2f);
                for(int s:new int[]{-1,1}){
                    Part lock=head.child(s*2.7f,-5.2f,.7f);locks.add(lock);
                    lock.loft(8,14,-.5f,0,0,.75f,1.0f,2,s*.7f,-.3f,.95f,.94f,5,s*.5f,0,.83f,.76f,7.8f,s*.25f,.1f,.53f,.56f);
                    Part braid=lock.child(s*.25f,7.4f,0);
                    for(int j=0;j<4;j++)braid.oval(8,(j%2==0?.14f:-.14f)*s,j*1.0f,.12f,.62f,.79f,.61f);
                    braid.oval(9,0,3.85f,0,.66f,.27f,.64f);
                    braid.loft(8,12,3.9f,0,0,.50f,.52f,5.2f,-s*.25f,-.12f,.36f,.34f,6,-s*.40f,-.2f,.03f,.04f);
                }
            }else{
                // Jinshi's tied crown and long purple hair with curved side locks.
                head.oval(8,0,-8.1f,1.7f,2.1f,2.0f,2.0f);
                head.oval(9,0,-9.9f,1.7f,1.65f,.45f,1.0f);
                head.blade(9,-1.7f,-9.5f,1.4f,-3.0f,-11.0f,1.4f,1.05f);
                head.blade(9,1.6f,-9.5f,1.4f,3.0f,-10.8f,1.4f,1.05f);
                for(int i=0;i<5;i++){
                    float x=-2.8f+i*1.4f;
                    Part sweep=head.child(x,-7.5f,-2.0f);
                    sweep.loft(8,12,-.8f,0,.1f,.95f,.83f,.4f,.1f,-.7f,1.0f,.68f,2.0f,(i<2?-1:1)*.45f,-.9f,.85f,.42f,3.65f,(i<2?-1:1)*.82f,-.42f,.10f,.10f);
                }
                Part back=head.child(0,-6.0f,2.0f);locks.add(back);
                back.loft(8,24,-1.2f,0,0,2.9f,1.75f,2,0,.6f,3.2f,1.65f,7,0,1.4f,3.1f,1.5f,13,0,1.9f,2.9f,1.25f,18,0,2.2f,2.2f,.85f,21,0,2.0f,1.3f,.15f);
                for(int i=0;i<5;i++){Part q=head.child(-2.4f+i*1.2f,-5.8f,2.9f);locks.add(q);q.loft(8,10,-.5f,0,0,.6f,.65f,5,(i-2)*.17f,.4f,.8f,.8f,12,(i-2)*.34f,1.3f,.85f,.65f,18+(i%2)*2,(i-2)*.45f,1.5f,.04f,.06f);}
                for(int s:new int[]{-1,1}){Part q=head.child(s*2.9f,-5.8f,.1f);locks.add(q);q.loft(8,12,-.7f,0,0,.75f,1.05f,2,s*.48f,-.4f,.78f,.95f,6,s*.50f,.1f,.58f,.75f,11,s*.18f,.9f,.06f,.08f);}
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                arms[i]=root.child(s*(width+.6f),.45f,0);
                arms[i].loft(0,18,-.75f,0,0,1.18f,1.15f,.7f,0,0,1.65f,1.55f,4.5f,0,.2f,1.7f,1.55f,8.6f,0,.1f,mao?1.92f:2.45f,mao?1.7f:2.15f,10,0,0,mao?1.72f:2.2f,mao?1.65f:2f);
                arms[i].loft(4,16,8.7f,0,0,mao?1.95f:2.48f,mao?1.75f:2.18f,9.6f,0,0,mao?1.8f:2.26f,mao?1.68f:2f);
                arms[i].oval(7,0,10.45f,-.35f,.84f,1.1f,.62f);
                feet[i]=root.child(s*1.65f,21.3f,0);
                feet[i].oval(10,0,1.8f,-.4f,1.25f,.86f,1.85f);
            }
            tray=arms[1].child(0,10.8f,-.7f);tray.rx=1.2f;
            tray.loft(11,20,-.25f,0,0,2.8f,2.0f,0,0,0,3.0f,2.2f,.35f,0,0,2.85f,2.1f);
            for(int i=0;i<2;i++){
                tray.oval(3,-1.15f+i*2.3f,-.5f,0,.8f,.48f,1.15f);
                tray.oval(14,-1.15f+i*2.3f,-.94f,0,.83f,.25f,1.1f);
            }
        }
        @Override public void setupAnim(SushiGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.serving();
            head.ry=yaw*.017f;head.rx=pitch*.012f+a*.045f;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.66+i*Math.PI)*amount;
                arms[i].rx=-w*.25f-(i==1?1.12f*a:.30f*a);
                arms[i].rz=(i==0?1:-1)*(.11f+.10f*a);
                feet[i].rx=w*.35f;panels[i].rx=(float)Math.sin(age*.10+i)*.025f+w*.04f;
            }
            for(int i=0;i<locks.size();i++)locks.get(i).rx=(float)Math.sin(age*.10+i*.55)*.025f+amount*.10f;
            tray.rx=1.12f*a;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){
            // The tray belongs to the animated serving pose, not the idle model.
            if(tray.rx<.04f){arms[1].children.remove(tray);try{root.draw(p,v,light,overlay,r,g,b,a);}finally{arms[1].children.add(tray);}}
            else root.draw(p,v,light,overlay,r,g,b,a);
        }
    }
    static class Renderer extends MobRenderer<SushiGuest,Model>{
        final boolean mao;Renderer(EntityRendererProvider.Context c,boolean mao){super(c,new Model(mao),.34f);this.mao=mao;}
        @Override protected void scale(SushiGuest e,PoseStack p,float partial){float s=mao?.86f:1.00f;p.scale(s,s,s);}
        @Override public ResourceLocation getTextureLocation(SushiGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+(mao?"maomao":"jinshi")+"_sculpted.png");}
    }
}''',encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
for mao in (True,False):
    name='maomao' if mao else 'jinshi'
    pal=[(40,149,111) if mao else (85,77,135),(30,96,81) if mao else (53,40,72),(36,125,100) if mao else (53,48,92),(239,239,216),(154,214,176) if mao else (192,178,133),(178,155,95),(246,203,169),(246,203,169),(22,58,52) if mao else (64,29,51),(206,160,72) if mao else (211,204,217),(33,39,43),(102,62,39),(255,255,255),(255,255,255),(232,120,81)]
    pix=bytearray(W*H*4)
    for m,base in enumerate(pal):
        for y in range(128):
            v=clamp((y-3)/121)
            for x in range(128):
                u=clamp((x-3)/121);f=abs(u-.5)
                c=blend(base,(46,25,49),.10*v+.10*(1-math.sin(u*math.pi)))
                if m in (0,2,4,5):
                    c=blend(c,base,.20*math.sin(u*math.pi*12+v*.3)**2)
                    if m in (0,2) and (v>.92 or v<.025):c=pal[4]
                    # Subtle embroidered blossoms and fine fabric borders.
                    if m==2:
                        a=(u*12)%1-.5;b=(v*9)%1-.5
                        rr=math.hypot(a,b);ang=math.atan2(b,a)
                        if rr<.09+.055*math.cos(ang*5) and (int(u*12)+int(v*9))%3==0:c=blend(c,pal[4],.45)
                if m==8:
                    phase=u*math.pi*14+math.sin(v*5)*.7
                    c=blend(base,(116,161,132) if mao else (156,73,108),.26*math.sin(phase)**2+.11*math.exp(-((v-.30)/.14)**2))
                    if abs(math.sin(phase))<.055:c=blend(c,base,.55)
                if m==6:
                    c=blend(base,(203,138,123),.12*math.exp(-((v-.72)/.18)**2)+.12*clamp((f-.18)*5))
                    for ex in (.395,.605):
                        dx=(u-ex)/(.069 if mao else .070)
                        dy=(v-.525+(.025*dx if ex<.5 else -.025*dx))/(.13 if mao else .085)
                        d=dx*dx+dy*dy
                        if d<1:c=(70,42,53)
                        if d<.85:c=(253,247,235)
                        if ((dx+(.07 if ex<.5 else -.07))/.57)**2+(dy/.88)**2<1 and d<.84:
                            iris=(116,76,168) if mao else (139,58,115)
                            c=blend(iris,(101,195,193) if mao else (233,126,172),clamp((dy+.1)*.55))
                        if abs(dx)<.23 and abs(dy)<.75 and d<.8:c=(45,29,58)
                        if (dx+.18)**2+(dy+.27)**2<.10 or (dx-.25)**2+(dy-.27)**2<.026:c=(255,255,255)
                        if abs(dx)<.93 and abs(v-(.365+.018*dx*(1 if ex<.5 else -1)))<.013:c=(39,65,58) if mao else (78,36,56)
                        if d>1 and abs(dy+.94)<.08 and abs(dx)<1:c=(53,33,44)
                    if f<.016 and .64<v<.71:c=blend(base,(171,103,96),.15)
                    if mao:
                        for ex,ey in ((.458,.66),(.472,.675),(.484,.654),(.515,.657),(.529,.677),(.544,.661),(.438,.673),(.563,.672)):
                            if ((u-ex)/.005)**2+((v-ey)/.009)**2<1:c=(163,105,88)
                    if f<(.035 if mao else .044) and abs(v-.81+.012*math.cos(f*55))<.013:c=(171,93,94)
                off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
    (assets/(name+'_sculpted.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Maomao and Jinshi: separate sculpted hair, faces, robes and serving animation')
