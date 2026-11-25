"""1.4.5: Gabumon polygon remake, one continuous facial UV and articulated pelt."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
(java/'GabumonModel.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import it.noctis.magic.SculptedGuestsClient.Part;
public class GabumonModel extends EntityModel<Gabumon>{
    final Part root=new Part(0,0,0),body=root.child(0,15,0),head=root.child(0,8,-1.6f);
    final Part jaw=head.child(0,.2f,-2.3f),tail=body.child(0,2.7f,3.4f),tip=tail.child(0,0,4.5f),pelt=body.child(0,-4.4f,1.8f);
    final Part[] arms=new Part[2],feet=new Part[2],ears=new Part[2],paws=new Part[2];
    // One continuous head surface; facial features occur only on material 2.
    GabumonModel(ModelPart ignored){
        body.loft(0,24,-7,0,0,1.6f,1.75f,-5.3f,0,0,3.1f,2.9f,-2.4f,0,0,4.25f,3.45f,1.1f,0,.25f,4.5f,3.9f,4.7f,0,.4f,3.65f,3.3f,6,0,.25f,1.75f,1.9f);
        // Rounded blue belly, with a single magenta spiral.
        body.oval(6,0,-.7f,-3.03f,3.2f,4.45f,1.10f);
        pelt.loft(1,20,-1.3f,0,.1f,2.8f,2.05f,1.2f,0,.45f,4.2f,2.5f,4.5f,0,.6f,4.3f,2.65f,8,0,1.4f,3.4f,2.1f,10.4f,0,2.4f,1.7f,1.1f);
        head.loft(2,32,-6.7f,0,.2f,1.2f,1.2f,-6.2f,0,.1f,2.8f,2.4f,-4.6f,0,0,4.3f,3.1f,-2.7f,0,-.25f,4.45f,3.35f,-.2f,0,-.35f,3.9f,3.0f,1.5f,0,-.3f,2.5f,2.1f,2.1f,0,-.2f,1.1f,1.1f);
        head.loft(0,20,.4f,0,-.15f,2.8f,2.5f,2.8f,0,-.1f,2.1f,2.2f,3.4f,0,0,1.65f,1.8f);
        // Wolf muzzle has no eyes and no second copy of the face.
        head.oval(3,0,-.45f,-3.7f,2.95f,1.75f,3.1f);
        head.oval(4,0,-1.15f,-6.35f,1.34f,.76f,.82f);
        jaw.oval(8,0,.57f,-2.2f,2.35f,.52f,2.5f);
        jaw.oval(0,0,1.02f,-1.95f,2.52f,.74f,2.58f);
        jaw.oval(9,0,.25f,-2.1f,1.08f,.23f,1.28f);
        Part horn=head.child(0,-5.1f,-2.3f);horn.rx=.36f;
        horn.loft(5,28,-6.85f,0,-.65f,.025f,.025f,-5.9f,0,-.52f,.38f,.40f,-4.6f,0,-.35f,.75f,.78f,-3.1f,0,-.18f,1.08f,1.12f,-1.5f,0,0,1.45f,1.45f,0,0,0,1.7f,1.7f);
        for(int i=0;i<2;i++){int s=i==0?-1:1;
            ears[i]=head.child(s*3.3f,-4.4f,.6f);ears[i].rz=s*.54f;ears[i].rx=-.12f;
            ears[i].loft(10,16,-5.8f,0,.4f,.035f,.05f,-4.5f,0,.15f,.64f,.50f,-2.8f,0,0,1.08f,.73f,-.7f,0,0,1.29f,.85f,.8f,0,0,.9f,.65f);
            ears[i].blade(11,0,-4.6f,-.48f,0,-.45f,-.76f,1.15f);
            Part tuft=head.child(s*3.5f,-.8f,.7f);tuft.rz=-s*.12f;
            tuft.loft(1,12,-1,0,0,.9f,1.5f,.7f,s*.65f,.1f,1.2f,1.7f,2.7f,s*.35f,1,1.1f,1.3f,4.7f,-s*.15f,1.9f,.05f,.08f);
            head.blade(7,s*2.15f,.18f,-4.8f,s*2.05f,1.75f,-5.0f,.78f);
            arms[i]=root.child(s*4.0f,11.8f,0);
            arms[i].loft(0,16,-.8f,0,0,1.15f,1.25f,.4f,0,0,1.65f,1.7f,3.7f,0,-.2f,1.4f,1.5f,6.5f,0,-.5f,1.2f,1.3f);
            paws[i]=arms[i].child(s*.4f,3.9f,.8f);
            paws[i].loft(1,18,-1.6f,0,0,1.75f,1.8f,.8f,0,.45f,2.4f,2.4f,3,0,.5f,2.1f,2.2f,4.5f,0,.5f,1.5f,1.6f);
            arms[i].oval(0,0,5.8f,-1.35f,1.5f,1.45f,1.55f);
            for(int j=0;j<3;j++){
                float x=-1.35f+j*1.35f;
                Part claw=paws[i].child(x,3.4f,-.05f);claw.rx=-.18f;
                claw.loft(12,12,0,0,0,.63f,.68f,1.2f,0,-.1f,.53f,.55f,2.65f,0,-.45f,.035f,.035f);
            }
            feet[i]=root.child(s*2.7f,19.6f,0);
            feet[i].oval(0,0,-.1f,0,2.03f,2.3f,2.15f);
            feet[i].loft(0,20,.2f,0,-.9f,1.95f,2.55f,2.0f,0,-1.35f,2.12f,3.0f,3.7f,0,-1.35f,2.15f,2.9f,4.4f,0,-1.35f,1.8f,2.7f);
            for(int j=0;j<3;j++){
                Part claw=feet[i].child(-1.35f+j*1.35f,2.55f,-3.5f);claw.rx=-1.15f;
                claw.loft(7,12,0,0,0,.65f,.67f,1.1f,0,0,.57f,.59f,2.45f,0,0,.035f,.045f);
            }
        }
        tail.loft(0,20,-1.45f,0,-.6f,1.6f,2.4f,.0f,0,2.0f,1.55f,3.1f,1.7f,0,3.0f,1.1f,2.25f,2.25f,0,3.6f,.9f,1.5f);
        tip.loft(0,16,-.9f,0,-.5f,1.0f,1.2f,0,0,1.8f,.8f,2.2f,1.1f,0,3.8f,.36f,.9f,1.8f,0,4.7f,.035f,.07f);
        Part flap=pelt.child(0,6.3f,2.5f);flap.loft(1,20,-1.0f,0,0,2.4f,1.6f,1.2f,0,1.3f,2.5f,2.0f,3.7f,0,2.8f,1.95f,1.6f,5.1f,0,3.4f,1.35f,.65f);
        for(int j=0;j<3;j++)flap.blade(12,-1.25f+j*1.25f,4.1f,3.6f,-1.25f+j*1.25f,6.5f,4.6f,.9f);
    }
    // Keep the pre-existing layer registration compatible, renderer uses polygon parts.
    static LayerDefinition mesh(){return LayerDefinition.create(new MeshDefinition(),16,16);}
    @Override public void setupAnim(Gabumon e,float limb,float amount,float age,float yaw,float pitch){
        boolean sit=e.isInSittingPose(),air=!e.onGround()&&!sit;float breath=e.breathPose(age-e.tickCount);
        float bob=sit?0:(float)Math.sin(limb*1.33)*amount*.42f;
        body.y=(sit?17:15)+bob;body.rx=sit?-.12f:air?-.09f:amount*.05f;
        head.y=(sit?10:8)+bob;head.ry=yaw*.01745f;head.rx=pitch*.01745f-breath*.24f;
        jaw.rx=.03f+breath*.55f;tail.ry=(float)Math.sin(age*.16)*.28f;tip.ry=(float)Math.sin(age*.16-.7f)*.29f;
        pelt.rx=-amount*.09f+(float)Math.sin(age*.10f)*.015f;
        for(int i=0;i<2;i++){int s=i==0?-1:1;float walk=(float)Math.cos(limb*.6662+i*Math.PI)*amount;
            arms[i].y=(sit?13.8f:11.8f)+bob;arms[i].rx=air?-.9f:-walk*.55f-breath*.6f;arms[i].rz=-s*(.17f+breath*.34f);
            feet[i].rx=sit?-.85f:air?-.4f:walk*.55f;feet[i].y=sit?21:19.6f;
            ears[i].rz=s*(.54f+(float)Math.sin(age*.14+i)*.055f);ears[i].rx=-.12f+breath*.19f;
            paws[i].rx=walk*.12f;
        }
    }
    @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
    static class Renderer extends MobRenderer<Gabumon,GabumonModel>{
        Renderer(EntityRendererProvider.Context c){super(c,new GabumonModel(c.bakeLayer(EclipseGuestsClient.B)),.46f);}
        @Override public ResourceLocation getTextureLocation(Gabumon e){return new ResourceLocation(Noctis.ID,"textures/entity/gabumon_sculpted.png");}
        @Override protected void scale(Gabumon e,PoseStack p,float partial){p.scale(.82f,.82f,.82f);}
    }
}''',encoding='utf-8')
# Material atlas for the shared polygon renderer. Only tile 2 contains eyes.
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(246,199,74),(239,239,235),(237,240,238),(240,240,237),(36,35,43),(231,174,55),(72,178,213),(247,241,216),(76,32,45),(219,86,109),(237,239,236),(208,182,184),(157,46,101)]
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
for m,base in enumerate(pal):
    for y in range(128):
        v=clamp((y-3)/121)
        for x in range(128):
            u=clamp((x-3)/121);f=abs(u-.5)
            c=blend(base,(70,53,73),.10*v)
            if m in (1,2,10):
                stripe=math.sin((v*2.2+.26*math.cos(u*math.pi*4)+.08*math.cos(u*math.pi*12))*math.pi*2)
                if m==1 and stripe>.40:c=(51,69,151)
                if m==2 and ((v<.22 and f<.38) or (f>.27 and stripe>.35) or (v>.77 and f>.18 and stripe>.25)):c=(51,69,151)
                if m==10 and v<.37:c=(51,69,151)
                c=blend(c,(110,121,149),.06*(1-math.sin(u*math.pi*8+v*6)**2))
            if m==2:
                # Left and right eye are a single pair, painted once on a continuous UV.
                for ex in (.37,.63):
                    dx=(u-ex)/.070;dy=(v-.51+(.05*dx if ex<.5 else -.05*dx))/.18
                    d=dx*dx+dy*dy
                    if d<1:c=(44,30,43)
                    if d<.85:c=(253,249,235)
                    if ((dx-(.15 if ex<.5 else -.15))/.58)**2+(dy/.9)**2<1 and d<.84:c=(177,35+int(38*clamp(dy+.5)),57)
                    if ((dx-(.15 if ex<.5 else -.15))/.30)**2+(dy/.72)**2<1 and d<.8:c=(38,22,35)
                    if (dx+.18)**2+(dy+.27)**2<.095:c=(255,255,255)
                    if abs(dx)<.9 and abs(dy+.98)<.075:c=(49,34,48)
            if m==3:
                if v>.7:c=blend(c,(155,171,199),.19)
                if f<.14 and abs(v-.8-.06*math.cos(f*14))<.015:c=(121,113,130)
            if m==4:c=blend(base,(150,156,175),.34*math.exp(-((u-.43)/.11)**2-((v-.32)/.22)**2))
            if m==5:
                c=blend((170,112,32),(255,219,115),.35+.6*math.sin(u*math.pi)**2)
                if abs(math.sin(v*math.pi*5+u*.8))<.075:c=blend(c,(127,85,33),.27)
            if m==6:
                dx=(u-.5)*2.4;dy=(v-.5)*2.2;r=math.hypot(dx,dy);a=math.atan2(dy,dx)
                if r>.85:c=(41,103,151)
                if r<.77 and (abs(r-(.26+.085*(a+math.pi)))<.09 or (abs(dx+.3)<.08 and -.28<dy<.17)):c=(203,64,132)
            if m==12:c=blend((111,25,69),(212,77,136),.30+.5*math.sin(u*math.pi))
            off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'gabumon_sculpted.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Gabumon redesigned: rounded continuous head, single eye pair, tapered horn, curved claws, animated pelt and tail')
