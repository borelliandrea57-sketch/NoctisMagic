"""1.5.1: Leon's RE4-inspired sculpted model and animated aiming pose."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'CrossoverClient.java';s=p.read_text(encoding='utf-8')
a='e.registerEntityRenderer(Noctis.LEON_KENNEDY.get(),c->new Renderer(c,0));'
assert a in s;p.write_text(s.replace(a,''),encoding='utf-8')
(java/'LeonSculptedClient.java').write_text('''package it.noctis.magic;
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
public class LeonSculptedClient {
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
        e.registerEntityRenderer(Noctis.LEON_KENNEDY.get(),R::new);
    }
    static class M extends EntityModel<CrossoverGuest>{
        final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1,0);
        final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],calves=new Part[2];
        final List<Part> hair=new ArrayList<>();
        final Part weapon;
        M(){
            // Broad shoulders, open brown flight jacket and tapered waist.
            body.loft(0,28,-.7f,0,0,2.0f,1.65f,.25f,0,0,4.0f,2.2f,2.6f,0,0,3.8f,2.15f,6.1f,0,0,3.15f,1.9f,9.45f,0,0,3.0f,1.85f,10.4f,0,0,3.25f,1.95f);
            body.loft(1,24,9.6f,0,0,3.17f,1.94f,10.45f,0,0,3.15f,1.92f);
            body.blade(2,0,-.6f,-1.9f,0,9.6f,-1.96f,2.65f);
            body.loft(3,18,-1.6f,0,0,1.28f,1.15f,.8f,0,0,1.4f,1.3f);
            for(int s:new int[]{-1,1}){
                // Raised shearling collar, stitched chest seams, pocket flaps and brass zipper.
                Part collar=body.child(s*1.35f,-.65f,.2f);collar.rz=-s*.22f;
                collar.loft(1,20,-2.25f,s*.30f,.45f,.70f,.85f,-1.2f,s*.18f,.3f,1.15f,1.40f,.15f,s*.3f,0,1.30f,1.55f,1.45f,s*.6f,-.35f,.75f,.6f);
                body.blade(0,s*1.85f,-.15f,-1.70f,s*.52f,3.1f,-2.15f,2.05f);
                body.blade(4,s*1.10f,1.4f,-2.02f,s*.55f,9.2f,-1.92f,.20f);
                body.blade(4,s*3.25f,1.2f,-1.12f,s*1.95f,2.0f,-1.95f,.24f);
                Part pocket=body.child(s*2.15f,6.1f,-1.73f);pocket.rz=s*.16f;
                pocket.loft(0,16,-.15f,0,0,1.0f,.14f,.15f,0,0,1.08f,.22f,1.8f,0,0,.83f,.19f);
                pocket.blade(4,-.85f,.05f,-.2f,.85f,.05f,-.2f,.22f);
            }
            body.loft(5,24,10.65f,0,0,3.0f,1.9f,11.65f,0,0,3.0f,1.9f);
            body.oval(6,0,11.15f,-1.96f,.78f,.48f,.22f);
            // Anatomical head; one pair of eyes on one continuous surface.
            head.loft(7,32,-7.6f,0,.12f,1.5f,1.7f,-7.0f,0,.06f,2.65f,2.5f,-5.4f,0,0,3.25f,2.9f,-3.55f,0,-.08f,3.18f,2.75f,-1.9f,0,-.17f,2.85f,2.4f,-.7f,0,-.24f,1.9f,1.65f,0,0,-.25f,.72f,.95f);
            head.loft(3,16,-3.55f,0,-2.6f,.25f,.20f,-2.7f,0,-2.92f,.39f,.43f,-2.1f,0,-2.87f,.35f,.27f);
            for(int s:new int[]{-1,1})head.oval(3,s*3.12f,-3.25f,.1f,.40f,.83f,.56f);
            // Side-parted ash blond hair, wide swept fringe, shaped nape.
            head.loft(8,24,-8.85f,.25f,.15f,.64f,.72f,-8.55f,.15f,.15f,2.65f,2.45f,-7.45f,0,.3f,3.45f,3.05f,-6.15f,0,.42f,3.48f,3.0f);
            Part back=head.child(0,-6.8f,1.9f);
            back.loft(8,20,-.75f,0,0,2.8f,1.55f,1.1f,0,.3f,3.1f,1.55f,3.8f,0,.6f,2.8f,1.25f,5.4f,0,.5f,1.5f,.24f);
            for(int j=0;j<7;j++){
                float x=-2.45f+j*.73f;Part lock=head.child(x,-7.65f+.08f*j,-1.9f);hair.add(lock);
                float end= j<4?5.0f-j*.28f:2.7f+(j%2)*.35f;
                lock.loft(j<4?9:8,14,-.5f,0,.65f,.66f,.70f,.5f,-.55f,-.35f,.95f,.75f,1.75f,-.85f,-.95f,.84f,.57f,end*.76f,-1.0f,-.8f,.52f,.37f,end,-.72f,-.42f,.035f,.06f);
            }
            for(int i=0;i<2;i++){int s=i==0?-1:1;
                Part side=head.child(s*2.92f,-6.2f,.2f);hair.add(side);
                side.loft(8,14,-.5f,0,0,.74f,1.1f,1.35f,s*.45f,-.25f,.80f,1.2f,3.7f,s*.30f,.1f,.62f,.8f,4.8f,0,.5f,.04f,.06f);
                arms[i]=body.child(s*4.15f,.45f,0);
                arms[i].loft(0,20,-.65f,0,0,1.35f,1.35f,.75f,0,0,1.78f,1.7f,3.1f,0,0,1.52f,1.49f,5.0f,0,0,1.18f,1.2f);
                fore[i]=arms[i].child(0,4.8f,0);
                fore[i].loft(0,20,-.4f,0,0,1.2f,1.22f,1.0f,0,0,1.28f,1.27f,3.8f,0,0,1.02f,1.05f);
                fore[i].loft(1,18,3.35f,0,0,1.09f,1.10f,4.05f,0,0,1.03f,1.06f);
                fore[i].oval(5,0,4.85f,-.12f,.9f,1.0f,.68f);
                for(int j=0;j<3;j++)fore[i].oval(3,-.44f+j*.44f,5.5f,-.33f,.20f,.49f,.26f);
                legs[i]=root.child(s*1.85f,11.35f,0);
                legs[i].loft(10,20,-.15f,0,0,1.65f,1.65f,2.7f,0,0,1.52f,1.45f,5.6f,0,0,1.14f,1.18f);
                Part pocketLeg=legs[i].child(s*1.10f,2.7f,-.25f);
                pocketLeg.loft(10,16,-.5f,0,0,.6f,.94f,0,0,0,.7f,1.12f,2.3f,0,0,.59f,.9f);
                pocketLeg.loft(5,16,-.4f,0,0,.65f,1.04f,.10f,0,0,.70f,1.13f);
                calves[i]=legs[i].child(0,5.3f,0);
                calves[i].loft(10,18,-.3f,0,0,1.19f,1.2f,2,0,0,1.02f,1.07f,4.4f,0,0,.85f,.88f);
                calves[i].loft(5,20,3.7f,0,0,1.02f,1.08f,5.4f,0,-.12f,1.04f,1.28f,6.75f,0,-.6f,1.22f,1.83f,7.35f,0,-.60f,1.19f,1.79f);
                for(int j=0;j<3;j++)calves[i].blade(4,-.55f,4.6f+j*.45f,-1.13f,.55f,4.75f+j*.45f,-1.14f,.13f);
            }
            // Distinct thigh holster and straps remain visible when walking.
            legs[1].loft(5,20,1.4f,0,0,1.61f,1.51f,1.78f,0,0,1.59f,1.49f);
            legs[1].loft(5,20,3.0f,0,0,1.52f,1.42f,3.38f,0,0,1.50f,1.40f);
            Part holster=legs[1].child(1.4f,.5f,.45f);holster.rz=-.12f;
            holster.loft(5,16,0,0,0,.62f,1.02f,.9f,0,0,.80f,1.08f,4.25f,0,.10f,.60f,.72f);
            // Stylized in-game sidearm held only during the shooting animation.
            weapon=new Part(0,5.0f,-.55f);weapon.rx=-(float)Math.PI/2;
            weapon.loft(11,16,-.8f,0,0,.45f,.52f,1.8f,0,0,.45f,.52f);
            Part slide=weapon.child(0,1.5f,0);slide.rx=(float)Math.PI/2;
            slide.loft(11,16,-.7f,0,0,.53f,.62f,0,0,0,.57f,.63f,3.4f,0,0,.50f,.55f);
        }
        @Override public void setupAnim(CrossoverGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.animation()==2?e.action():0;
            boolean aiming=e.getTarget()!=null&&!e.level().isDay();
            float pose=aiming?1:a;
            body.ry=-pose*.14f;head.ry=yaw*.01745f-body.ry;head.rx=pitch*.016f-pose*.04f;
            for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;
                arms[i].rx=-w*.6f*(1-pose)-pose*(i==1?1.35f:.95f)-a*.10f;
                arms[i].rz=-s*.10f+pose*(i==0?-.32f:.02f);
                arms[i].ry=pose*(i==0?-.36f:.08f);
                fore[i].rx=-pose*(i==0?.78f:.15f);
                legs[i].rx=w*.65f;calves[i].rx=Math.max(0,-w)*.35f;
            }
            for(int i=0;i<hair.size();i++)hair.get(i).rx=(float)Math.sin(age*.10+i*.5)*.013f+amount*.04f;
            if(pose>.10f){if(!fore[1].children.contains(weapon))fore[1].children.add(weapon);}
            else fore[1].children.remove(weapon);
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    }
    static class R extends MobRenderer<CrossoverGuest,M>{
        R(EntityRendererProvider.Context c){super(c,new M(),.37f);}
        @Override public ResourceLocation getTextureLocation(CrossoverGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/leon_sculpted.png");}
    }
}''',encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(104,75,58),(191,164,127),(35,35,36),(224,179,148),(132,103,77),(35,35,38),(151,144,133),(224,179,148),(118,94,68),(157,130,91),(59,59,61),(83,87,91)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(36,29,30),.13*v+.10*(1-math.sin(u*math.pi)))
            if m in (0,1,5,10):
                grain=(math.sin(u*163+v*49)*math.cos(v*147-u*53)+1)*.5
                c=blend(c,base,.21*grain)
                if m==1:c=blend(c,(230,212,177),.27*grain)
                if m==0 and (v>.955 or v<.025):c=blend(c,pal[4],.65)
                if m==10 and (abs(u-.25)<.013 or abs(u-.75)<.013):c=blend(c,(107,106,105),.32)
            if m in (8,9):
                wave=math.sin(u*math.pi*16+math.sin(v*6)*1.1)**2
                c=blend(base,(196,168,120),.32*wave+.17*math.exp(-((v-.30)/.14)**2))
                c=blend(c,(63,49,37),.16*(1-wave))
            if m==7:
                c=blend(base,(159,100,85),.14*math.exp(-((v-.71)/.18)**2)+.12*clamp((f-.17)*5))
                for ex in (.398,.602):
                    dx=(u-ex)/.063;dy=(v-.505+(.038*dx if ex<.5 else -.038*dx))/.085;d=dx*dx+dy*dy
                    if d<1:c=(68,43,38)
                    if d<.80:c=(241,233,217)
                    if abs(dx)<.53 and d<.80:c=blend((64,100,119),(141,184,191),clamp((dy+.2)*.6))
                    if abs(dx)<.22 and abs(dy)<.75 and d<.8:c=(28,34,38)
                    if (dx+.16)**2+(dy+.24)**2<.075:c=(255,255,249)
                    if abs(dx)<1.05 and abs(v-(.365+.03*dx*(1 if ex<.5 else -1)))<.015:c=(107,75,53)
                if f<.06 and abs(v-.80+.009*math.cos(f*55))<.012:c=(139,78,70)
                if v>.77 and f<.25:c=blend(c,(116,94,79),.055*(1+math.sin(u*139+v*83)))
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'leon_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Leon: ash blond swept hair, leather shearling jacket, cargo trousers, articulated aiming pose')
