"""1.5.0: five wolf varieties with forward-facing eyes and species-specific geometry."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
(java/'BreedWolfClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class BreedWolfClient {
    static final String[] IDS={"arctic_wolf","black_wolf","red_wolf","timber_wolf","silver_wolf"};
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
        e.registerEntityRenderer(Noctis.ARCTIC_WOLF.get(),c->new R(c,0));
        e.registerEntityRenderer(Noctis.BLACK_WOLF.get(),c->new R(c,1));
        e.registerEntityRenderer(Noctis.RED_WOLF.get(),c->new R(c,2));
        e.registerEntityRenderer(Noctis.TIMBER_WOLF.get(),c->new R(c,3));
        e.registerEntityRenderer(Noctis.SILVER_WOLF.get(),c->new R(c,4));
    }
    static class M extends EntityModel<BreedWolf>{
        final int k;final Part root=new Part(0,0,0),torso=root.child(0,13,0),neck=torso.child(0,-1,-4.8f),head=root.child(0,8,-6.2f);
        final Part tail=torso.child(0,-.8f,6.2f),tailTip=tail.child(0,5.2f,0);
        final Part collar=new Part(0,12,-4.8f);
        final Part[] legs=new Part[4],shins=new Part[4],ears=new Part[2];
        final float legHeight,headHeight,bodyHeight;
        boolean tame,young;float[] dye={1,1,1};
        M(int k){
            this.k=k;boolean red=k==2,arctic=k==0;
            float width=red?2.55f:arctic?3.25f:k==3?3.05f:2.9f;
            legHeight=red?13.0f:13.7f;bodyHeight=legHeight-.65f;headHeight=red?8.3f:7.6f;
            torso.y=bodyHeight;head.y=headHeight;
            Part trunk=torso.child(0,0,0);trunk.rx=(float)Math.PI/2;
            // Ring direction along the spine, not a rectangular box.
            trunk.loft(0,24,-6.6f,0,0,width*.68f,2.4f,-4.7f,0,0,width,3.05f,-1.2f,0,0,width*.98f,2.8f,2.7f,0,0,width*.82f,2.15f,5.4f,0,0,width*.89f,2.65f,6.9f,0,0,width*.55f,1.7f);
            torso.oval(2,0,1.35f,-2.9f,width*.83f,2.0f,3.3f);
            neck.rx=-.36f;neck.loft(0,24,-5.0f,0,-.9f,1.75f,1.8f,-3.0f,0,-.5f,2.25f,2.3f,-.5f,0,0,width*.90f,2.85f,2.6f,0,.3f,width*.83f,2.35f);
            neck.oval(2,0,.2f,-1.1f,width*.70f,2.9f,1.75f);
            if(arctic||k==3)for(int s:new int[]{-1,1})for(int j=0;j<3;j++)neck.blade(0,s*(1.8f+j*.12f),-2+j*1.1f,-.9f,s*(2.8f+j*.1f),2+j*.7f,.15f,1.65f);
            float hw=red?2.45f:arctic?2.95f:2.75f;
            // One continuous eye-bearing surface, face lies at u=.5.
            head.loft(1,32,-4.25f,0,.1f,1.05f,1.15f,-3.8f,0,0,hw*.83f,2.25f,-2.65f,0,-.15f,hw,2.60f,-.9f,0,-.25f,hw*.97f,2.53f,.65f,0,-.15f,hw*.83f,2.15f,1.8f,0,.05f,1.35f,1.4f);
            // Tapered snout, a separate nose and lower jaw with no eyes.
            Part snout=head.child(0,-.1f,-1.8f);snout.rx=-(float)Math.PI/2;
            float len=red?4.0f:3.5f;
            snout.loft(3,24,-.35f,0,0,1.65f,1.1f,1.0f,0,.15f,1.48f,.94f,len*.78f,0,.35f,1.03f,.76f,len,0,.4f,.84f,.63f);
            head.oval(4,0,-.52f,-1.8f-len,.90f,.60f,.59f);
            Part jaw=head.child(0,.95f,-1.65f);jaw.rx=-(float)Math.PI/2;
            jaw.loft(2,18,0,0,0,1.35f,.61f,1.6f,0,0,1.15f,.46f,len-.25f,0,0,.80f,.33f);
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;ears[i]=head.child(s*(hw-.4f),-3.3f,.45f);ears[i].rz=s*.23f;
                float eh=red?3.85f:arctic?2.65f:3.3f;
                ears[i].loft(0,18,-eh,0,0,.045f,.055f,-eh*.68f,0,0,.58f,.36f,-.75f,0,0,1.04f,.65f,.25f,0,0,1.12f,.71f);
                ears[i].blade(5,0,-eh*.78f,-.34f,0,-.25f,-.68f,1.10f);
                Part cheek=head.child(s*(hw-.45f),-.9f,.7f);cheek.rz=-s*.18f;
                cheek.loft(0,12,-.65f,0,0,.78f,.9f,.45f,s*.38f,.2f,.87f,.8f,2.0f,s*.2f,1.05f,.05f,.08f);
            }
            for(int i=0;i<4;i++){
                int s=i/2==0?-1:1;boolean front=i%2==0;
                Part leg=legs[i]=root.child(s*(width*.66f),legHeight,front?-4.0f:4.5f);
                leg.loft(0,18,-1.15f,0,0,front?1.12f:1.55f,front?1.20f:1.65f,1.0f,0,0,front?1.0f:1.35f,front?1.1f:1.4f,4.25f,0,front?0:.55f,.70f,.76f);
                Part shin=shins[i]=leg.child(0,4.05f,front?0:.55f);
                shin.loft(6,18,-.20f,0,0,.73f,.78f,2.35f,0,-.1f,.55f,.59f,5.15f,0,-.23f,.65f,.72f,24-legHeight-4.05f,0,-.38f,.89f,1.14f);
            }
            tail.rx=1.02f;float tw=red?1.25f:arctic?1.85f:1.6f;
            tail.loft(0,20,-.35f,0,0,1.0f,1.0f,1.2f,0,0,tw,tw,4.8f,0,0,tw*.92f,tw*.95f,5.6f,0,0,tw*.83f,tw*.85f);
            tailTip.loft(7,20,0,0,0,tw*.83f,tw*.85f,2.7f,0,0,tw*.65f,tw*.70f,4.6f,0,0,.06f,.07f);
            // White atlas material is tinted by the actual vanilla collar dye.
            collar.rx=-.36f;
            collar.loft(8,28,-3.0f,0,-.50f,2.34f,2.39f,-2.35f,0,-.32f,2.48f,2.58f);
        }
        @Override public void setupAnim(BreedWolf e,float limb,float amount,float age,float yaw,float pitch){
            boolean sit=e.isInSittingPose();tame=e.isTame();young=e.isBaby();dye=e.getCollarColor().getTextureDiffuseColors();
            torso.y=bodyHeight+(sit?3.6f:0);torso.rx=sit?-.26f:0;
            head.y=headHeight+(sit?1.1f:0);head.ry=yaw*.01745f;head.rx=pitch*.01745f;
            tail.rx=sit?1.55f:1.02f;tail.ry=e.isAngry()?0:(float)Math.sin(age*.25)*(.21f+amount*.22f);tailTip.rx=.16f+(float)Math.sin(age*.25-.6f)*.09f;
            for(int i=0;i<4;i++){boolean front=i%2==0;
                legs[i].y=legHeight+(sit?(front?1.1f:3.7f):0);
                legs[i].rx=sit?(front?-.09f:1.19f):(float)Math.cos(limb*.666+(i/2+i%2)*Math.PI)*amount*.65f;
                shins[i].rx=sit?(front?0:-1.70f):Math.max(0,-legs[i].rx)*.35f;
            }
            for(int i=0;i<2;i++)ears[i].rz=(i==0?-1:1)*(.23f+(float)Math.sin(age*.11+i)*.045f+(e.isAngry()?.25f:0));
            collar.y=torso.y-1;collar.z=-4.8f;collar.rx=-.36f+torso.rx;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){
            p.pushPose();if(young){p.translate(0,.75f,0);p.scale(.5f,.5f,.5f);}
            root.draw(p,v,light,overlay,r,g,b,a);
            if(tame)collar.draw(p,v,light,overlay,r*dye[0],g*dye[1],b*dye[2],a);p.popPose();
        }
    }
    static class R extends MobRenderer<BreedWolf,M>{
        final int k;R(EntityRendererProvider.Context c,int k){super(c,new M(k),.39f);this.k=k;}
        @Override protected void scale(BreedWolf e,PoseStack p,float partial){float s=k==2?.86f:k==0?.94f:k==3?.97f:.91f;p.scale(s,s,s);}
        @Override public ResourceLocation getTextureLocation(BreedWolf e){return new ResourceLocation(Noctis.ID,"textures/entity/"+IDS[k]+"_sculpted.png");}
    }
}''',encoding='utf-8')
W,H=1024,512
def clamp(v):return max(0,min(1,v))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
specs=[
 ('arctic_wolf',(228,229,224),(247,246,237),(165,173,174),(159,133,66)),
 ('black_wolf',(39,42,47),(88,84,83),(22,25,32),(205,158,62)),
 ('red_wolf',(160,85,47),(223,181,126),(79,55,46),(190,151,65)),
 ('timber_wolf',(114,113,108),(191,180,156),(62,61,59),(201,157,64)),
 ('silver_wolf',(139,149,162),(215,220,224),(68,83,105),(147,167,180))]
for n,base,cream,dark,iris in specs:
    pix=bytearray(W*H*4)
    for m in range(9):
        for y in range(128):
            v=clamp((y-3)/121)
            for x in range(128):
                u=clamp((x-3)/121);front=abs(u-.5)
                grain=.5+.5*math.sin(u*102+math.sin(v*49)*1.5)*math.sin(v*103+u*15)
                c=blend(base,dark,.12+.12*grain)
                if m==0:
                    c=blend(c,dark,.27*(1-v)+.09*math.sin(u*math.pi*4)**2)
                if m==1:
                    # Eye centers at +/- 32.4 degrees from the front.
                    c=blend(c,cream,.75*clamp((v-.46)*3)*(1-clamp((front-.18)*3)))
                    c=blend(c,dark,.37*math.exp(-((v-.22)/.17)**2))
                    for ex in (.410,.590):
                        dx=(u-ex)/.047;dy=(v-.515+(.06*dx if ex<.5 else -.06*dx))/.086
                        d=dx*dx+dy*dy
                        if d<1:c=(37,28,26)
                        if d<.76:c=iris
                        if abs(dx)<.27 and abs(dy)<.70 and d<.78:c=(19,18,20)
                        if (dx+.16)**2+(dy+.22)**2<.075:c=(241,236,215)
                        if abs(dx)<.9 and abs(dy+.92)<.09:c=dark
                if m==2:c=blend(cream,base,.12+.12*grain)
                if m==3:
                    c=blend(cream,base,.22+.16*grain)
                    if front>.26:c=blend(c,dark,.20)
                if m==4:c=blend((22,23,25),(86,85,83),.25*math.exp(-((v-.25)/.20)**2))
                if m==5:c=blend(base,(104,61,58),.50)
                if m==6:c=blend(base,cream,.36*v);c=blend(c,dark,.45*clamp((v-.82)*6))
                if m==7:c=blend(base,dark,.30+.62*v)
                if m==8:c=(245,245,245)
                off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
    (assets/(n+'_sculpted.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Five wolves rebuilt: single forward eye pair, tapered snouts, distinct coats and silhouettes, preserved vanilla wolf behavior')
