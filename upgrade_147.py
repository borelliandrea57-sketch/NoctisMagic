"""1.4.7: rebuild Lelouch and C.C. with distinct polygon costumes, faces and hair."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'DramaClient.java';s=p.read_text(encoding='utf-8')
for a in ('e.registerEntityRenderer(Noctis.LELOUCH.get(),c->new Renderer(c,1));','e.registerEntityRenderer(Noctis.CC.get(),c->new Renderer(c,2));'):
    assert a in s,a;s=s.replace(a,'')
p.write_text(s,encoding='utf-8')
(java/'GeassSculptedClient.java').write_text('''package it.noctis.magic;
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
public class GeassSculptedClient{
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
        e.registerEntityRenderer(Noctis.LELOUCH.get(),c->new R(c,false));
        e.registerEntityRenderer(Noctis.CC.get(),c->new R(c,true));
    }
    static class M extends EntityModel<DramaGuest>{
        final boolean cc;
        final Part root=new Part(0,0,0),body=root.child(0,0,0),head=root.child(0,-1,0);
        final Part[] arms=new Part[2],legs=new Part[2],cape=new Part[2];
        final List<Part> hair=new ArrayList<>();
        M(boolean cc){
            this.cc=cc;
            body.loft(0,24,-1,0,0,1.8f,1.3f,0,0,0,cc?3.0f:3.65f,1.8f,2.6f,0,-.1f,cc?3.0f:3.45f,cc?2.0f:1.85f,6.5f,0,0,2.05f,1.5f,9.7f,0,0,2.3f,1.65f,11,0,0,cc?3.05f:2.75f,1.85f);
            body.loft(1,20,9.2f,0,0,2.45f,1.85f,10.1f,0,0,2.65f,1.95f);
            body.loft(2,16,-1.15f,0,0,1.2f,1.1f,.35f,0,0,1.5f,1.4f);
            if(!cc){
                // White cravat, layered royal collar and gold seams.
                body.blade(3,0,-.3f,-1.8f,0,4.6f,-2.1f,2.9f);
                body.blade(3,-.55f,.7f,-2.0f,-1.0f,4.0f,-2.25f,1.0f);
                body.blade(3,.55f,.7f,-2.0f,1.0f,4.0f,-2.25f,1.0f);
                for(int s:new int[]{-1,1}){
                    body.blade(4,s*2.5f,.0f,-1.5f,s*.55f,6.8f,-1.75f,.55f);
                    body.blade(5,s*2.0f,.1f,0,s*4.7f,-5.1f,1.1f,3.0f);
                    body.blade(4,s*2.1f,-.1f,-.18f,s*4.65f,-5.15f,.9f,.30f);
                }
            }else{
                body.blade(4,0,-.8f,-1.45f,0,3.2f,-2.0f,.38f);
                body.loft(3,20,10.25f,0,0,2.5f,1.75f,11.8f,0,0,2.85f,1.85f,13.0f,0,0,2.65f,1.65f);
                for(int s:new int[]{-1,1})body.blade(4,s*2.0f,9.7f,-1.5f,s*2.2f,12.3f,-1.5f,.42f);
            }
            // Separate head silhouette, face mapped only once.
            float w=cc?3.35f:3.05f;
            head.loft(6,32,-7.35f,0,.15f,1.35f,1.65f,-6.85f,0,.05f,2.65f,2.4f,-5.3f,0,0,w,2.85f,-3.55f,0,-.05f,w,2.7f,-1.85f,0,-.15f,cc?2.55f:2.3f,2.25f,-.55f,0,-.25f,cc?1.65f:1.25f,1.45f,0,0,-.3f,.55f,.75f);
            head.oval(7,0,-2.7f,-2.75f,.30f,.43f,.34f);
            for(int s:new int[]{-1,1})head.oval(7,s*w,-3.4f,.1f,.38f,.78f,.52f);
            head.loft(8,24,-8.7f,0,.1f,.50f,.60f,-8.5f,0,.1f,2.35f,2.25f,-7.5f,0,.2f,3.4f,3.05f,-6.1f,0,.3f,3.55f,3.15f);
            for(int i=0;i<(cc?8:6);i++){
                float x=cc?-2.9f+i*.83f:-2.8f+i*1.08f;
                Part fringe=head.child(x,-7.2f,-2.5f);
                float d=cc?(i-3.5f)*.19f:-.85f+i*.12f;
                float end=cc?2.55f+(i%3)*.23f:2.9f+(i%3)*.45f;
                fringe.loft(8,12,-.65f,0,.35f,.76f,.74f,.6f,d*.25f,-.2f,.82f,.55f,1.65f,d*.6f,-.45f,.65f,.38f,end,d,-.4f,.04f,.06f);
            }
            Part back=head.child(0,-6.3f,1.9f);hair.add(back);
            if(cc){
                back.loft(8,24,-.6f,0,0,2.85f,1.6f,2,0,.4f,3.2f,1.65f,6,0,1.2f,3.4f,1.55f,11,0,2.1f,3.7f,1.5f,16,0,2.4f,3.1f,1.1f,20,0,2.6f,2.1f,.35f);
                for(int j=0;j<7;j++){
                    Part q=head.child(-2.65f+j*.88f,-5.8f,2.8f);hair.add(q);
                    q.loft(8,10,0,0,0,.58f,.6f,5,(j-3)*.18f,.4f,.78f,.73f,11,(j-3)*.30f,1.25f,.80f,.65f,17,(j-3)*.45f,1.9f,.65f,.5f,20+(j%3), (j-3)*.5f,1.9f,.04f,.07f);
                }
            }else back.loft(8,20,-.7f,0,0,2.7f,1.7f,1.3f,0,.4f,3.1f,1.5f,4.0f,0,.35f,2.85f,1.25f,6.2f,0,.5f,1.25f,.18f);
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                Part lock=head.child(s*2.85f,-5.9f,.1f);hair.add(lock);
                lock.loft(8,12,-.8f,0,0,.74f,1.05f,1.5f,s*.5f,-.3f,.88f,1.12f,cc?7:3.2f,s*.65f,-.2f,.72f,.75f,cc?14.8f:5.7f,s*.35f,.5f,.04f,.07f);
                arms[i]=root.child(s*(cc?3.8f:4.15f),.25f,0);
                if(cc){
                    arms[i].oval(7,0,.7f,0,1.14f,1.35f,1.15f);
                    arms[i].loft(0,16,2.0f,0,0,1.12f,1.15f,3.7f,0,0,1.03f,1.0f,8.7f,0,-.1f,.7f,.74f);
                    arms[i].loft(4,16,1.8f,0,0,1.16f,1.2f,2.35f,0,0,1.15f,1.18f);
                }else{
                    arms[i].loft(0,16,-.7f,0,0,1.15f,1.2f,.8f,0,0,1.55f,1.4f,4.9f,0,0,1.1f,1.1f,8.9f,0,0,.9f,.95f);
                    arms[i].loft(4,16,7.9f,0,0,1.04f,1.09f,8.4f,0,0,1.02f,1.07f);
                }
                arms[i].oval(cc?7:0,0,10,0,.74f,1.12f,.65f);
                legs[i]=root.child(s*1.55f,11.8f,0);
                legs[i].loft(cc?7:0,16,0,0,0,1.45f,1.45f,4.1f,0,0,1.13f,1.18f,6.1f,0,0,.95f,.98f);
                legs[i].loft(cc?9:0,18,5.2f,0,0,1.10f,1.10f,6.5f,0,0,.95f,1.0f,10.7f,0,-.12f,.72f,.8f,12.2f,0,-.5f,.9f,1.5f);
                legs[i].blade(4,0,10.6f,-.8f,0,12.3f,-1.9f,.80f);
                // Broad animated dark cloth with burgundy lining and gold trim, open at front.
                cape[i]=body.child(s*(cc?1.95f:2.45f),cc?9.7f:-.2f,1.65f);
                float len=cc?15.4f:23.8f;
                Part c=cape[i];
                c.loft(5,18,0,0,0,cc?1.5f:2.7f,.32f,len*.24f,s*.6f,.4f,cc?2.0f:3.4f,.37f,len*.54f,s*1.25f,1.2f,cc?2.4f:4.1f,.4f,len*.80f,s*2.0f,2.0f,cc?1.7f:3.6f,.34f,len,s*2.7f,3.3f,.08f,.10f);
                c.blade(4,s*(cc?1.4f:2.55f),.2f,-.32f,s*3.0f,len-.3f,2.9f,.30f);
            }
        }
        @Override public void setupAnim(DramaGuest e,float limb,float amount,float age,float yaw,float pitch){
            head.ry=yaw*.01745f;head.rx=pitch*.014f;head.rz=cc?.025f:0;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;
                arms[i].rx=-w*.58f;arms[i].rz=-s*.10f;legs[i].rx=w*.68f;
                cape[i].rx=.12f+amount*.35f+(float)Math.sin(age*.11+i)*.055f;
                cape[i].rz=-s*(.10f+amount*.045f);
            }
            for(int i=0;i<hair.size();i++)hair.get(i).rx=amount*.13f+(float)Math.sin(age*.12+i*.55f)*.025f;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class R extends MobRenderer<DramaGuest,M>{
        final boolean cc;R(EntityRendererProvider.Context c,boolean cc){super(c,new M(cc),.36f);this.cc=cc;}
        @Override protected void scale(DramaGuest e,PoseStack p,float partial){float s=cc?.94f:1.02f;p.scale(s,s,s);}
        @Override public ResourceLocation getTextureLocation(DramaGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+(cc?"cc":"lelouch")+"_sculpted.png");}
    }
}''',encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
for cc in (False,True):
    name='cc' if cc else 'lelouch'
    pal=[(37,31,49) if cc else (45,34,91),(105,24,52) if cc else (156,119,57),(39,27,46),(230,231,238) if cc else (209,211,231),(191,155,81),(38,24,50),(244,204,179),(244,204,179),(157,187,75) if cc else (44,33,52),(189,199,220)]
    pix=bytearray(W*H*4)
    for m,base in enumerate(pal):
        for y in range(128):
            v=clamp((y-3)/121)
            for x in range(128):
                u=clamp((x-3)/121);front=abs(u-.5)
                c=blend(base,(27,19,37),.13*v+.10*(1-math.sin(u*math.pi)))
                if m==8:
                    wave=math.sin(u*math.pi*16+math.sin(v*5)*.8)**2
                    c=blend(base,(220,237,137) if cc else (99,77,105),.30*wave+.13*math.exp(-((v-.3)/.12)**2))
                if m==5:
                    # Front/inside burgundy, exterior dark violet. Thin embroidered hem.
                    c=blend((109,20,49) if front<.24 else (34,23,54),(142,90,125),.13*math.sin(u*math.pi*10+v)**2)
                    if v>.95 or abs(front-.24)<.013:c=(179,141,67)
                if m==0 and abs(v-.85)<.015:c=blend(c,pal[4],.60)
                if m==4:c=blend((118,80,38),(239,205,123),.35+.55*math.sin(u*math.pi)**2)
                if m==6:
                    c=blend(base,(200,137,132),.10*math.exp(-((v-.69)/.19)**2)+.10*clamp((front-.17)*5))
                    for ex in (.393,.607):
                        dx=(u-ex)/.068;dy=(v-.51+(.038*dx if ex<.5 else -.038*dx))/(.123 if cc else .087)
                        d=dx*dx+dy*dy
                        if d<1:c=(55,30,43)
                        if d<.81:c=(250,245,236)
                        if abs(dx)<.55 and d<.8:c=blend((181,138,40) if cc else (103,48,141),(241,209,105) if cc else (171,105,218),clamp((dy+.25)*.6))
                        if abs(dx)<.22 and abs(dy)<.75 and d<.8:c=(34,24,40)
                        if (dx+.18)**2+(dy+.24)**2<.085:c=(255,255,255)
                        if abs(dx)<.95 and abs(v-(.365+.022*dx*(1 if ex<.5 else -1)))<.014:c=(83,104,42) if cc else (57,34,53)
                    if front<.043 and abs(v-.81+.009*math.cos(front*65))<.012:c=(163,83,90)
                off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
    (assets/(name+'_sculpted.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Lelouch and C.C. sculpted models with original costume references, retained DramaGuest logic')
