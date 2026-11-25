"""1.0.1: fully custom Raiden cyborg mesh, hand-painted UV islands, animated katana."""
from pathlib import Path
import sys,math,struct,zlib,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
N=256;S=4;W=N*S;pix=bytearray(W*W*4);rng=random.Random(101)
cx=cy=rh=0
def put(x,y,c):
    p=(y*W+x)*4;pix[p:p+4]=bytes((*[max(0,min(255,round(v))) for v in c],255))
def mix(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def paint(x,y,w,h,mat,side):
    if not w or not h:return
    x*=S;y*=S;w*=S;h*=S
    for j in range(h):
        v=(j+.5)/h
        for i in range(w):
            u=(i+.5)/w;edge=min(u,v,1-u,1-v)
            if mat in ('steel','darksteel','chrome','blade','guard'):
                if mat=='steel':lo,hi=(28,31,35),(160,170,178)
                elif mat=='darksteel':lo,hi=(13,15,19),(83,90,99)
                elif mat=='chrome':lo,hi=(42,48,53),(222,229,234)
                elif mat=='blade':lo,hi=(80,91,104),(239,248,255)
                else:lo,hi=(20,21,26),(104,112,121)
                t=.17+.53*math.exp(-((u-.27)/.18)**2)+.24*math.exp(-((u-.84)/.055)**2)
                t+=.09*math.sin(v*7+u*3)
                col=mix(lo,hi,max(0,min(1,t)))
                if edge<.045:col=mix(col,hi,.55)
                elif edge<.09:col=mix(col,lo,.78)
                if mat in ('steel','darksteel') and ((u-.19)**2+(v-.16)**2<.007 or (u-.81)**2+(v-.84)**2<.007):col=(161,169,177)
                if mat=='blade':
                    if u<.18 or u>.82:col=(238,246,255)
                    elif .42<u<.54:col=(82,98,112)
            elif mat=='carbon':
                stripe=(int(u*max(4,w//2))+int(v*max(4,h//2)))%3
                col=(18+stripe*5,20+stripe*5,24+stripe*6)
            elif mat=='joint':
                t=.22+.52*abs(math.sin(u*math.pi*3))
                col=mix((12,14,18),(93,103,112),t)
                if int(v*10)%2==0:col=mix(col,(14,16,19),.5)
            elif mat=='red':
                col=mix((68,12,20),(197,45,52),.35+.65*math.sin(u*math.pi))
            elif mat=='hair':
                # Ash silver, fine strands and cool dark roots.
                t=.26+.35*math.sin(u*math.pi)+.16*math.sin(u*31+v*5)+.19*v
                col=mix((48,53,59),(208,215,220),max(0,min(1,t)))
            elif mat=='face':
                col=(194,174,162)
                if side=='front':
                    col=mix((145,124,120),(222,201,186),max(0,1-abs(u-.46)*1.25-v*.25))
                    # unobstructed visible eye on right side of face; black eyepatch over other eye
                    if .48<u<.89 and .35<v<.53:
                        col=(36,35,41)
                        if .52<u<.86 and .39<v<.49:col=(229,226,222)
                        if .65<u<.78 and .39<v<.49:col=(88,128,147)
                        if .69<u<.74 and .39<v<.49:col=(18,24,34)
                    if .49<u<.9 and abs(v-(.29+.12*(u-.49)))<.027:col=(65,58,57)
                    if .15<u<.47 and .34<v<.57:col=(18,20,25)
                    if abs(v-(.34+.13*u))<.035:col=(25,26,31)
                    if .47<u<.54 and .5<v<.69:col=(151,127,117)
                    if .37<u<.65 and .79<v<.83:col=(94,65,65)
                    if v>.87:col=mix(col,(109,101,100),.55)
                elif side in ('left','right') and .29<v<.39:col=(22,24,30)
            elif mat=='hilt':
                col=(26,27,32) if (int((u+v)*10)%3) else (81,85,92)
            else:col=(34,36,41)
            light={'top':1.1,'bottom':.72,'left':.89,'right':.97,'front':1,'back':.82}.get(side,1)
            n=rng.randint(-2,2);put(x+i,y+j,tuple(c*light+n for c in col))
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+2>N:cx=0;cy+=rh+2;rh=0
    u,v=cx,cy;cx+=ww+2;rh=max(rh,hh)
    assert v+hh<=N,(mat,u,v,ww,hh)
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:paint(fx,fy,fw,fh,mat,face)
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
lines=[]
def part(var,parent,name,pos,rot,boxes):
    shape='CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)
    pose='PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+')'
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",{shape},{pose});')
# Sculpted exoskeleton: tapered ribs, abdominal segments, separate pelvic shell.
part('b','r','body',(0,0,0),(0,0,0),[(-3,-1,-2,6,8,4,'carbon'),(-2.5,7,-1.5,5,4,3,'joint')])
part('ch','b','chest',(0,0,0),(0,0,0),[(-4,-1,-2.8,8,4,5,'darksteel'),(-3,2,-3.1,6,3,5,'steel'),(-2,5,-2.6,4,2,4,'chrome')])
for i,s in enumerate((-1,1)):
    part('rib'+str(i),'b','rib'+str(i),(s*2.2,4,-2.1),(0,s*.24,s*.23),[(-1,-1,-1,2,4,2,'steel'),(-.5,2,-1,1,2,2,'darksteel')])
    part('pec'+str(i),'ch','pec'+str(i),(s*2.1,0,-2.7),(0,s*.16,s*.13),[(-1.5,0,-.5,3,3,2,'steel'),(-1,1,-.9,2,1,1,'chrome')])
for i in range(3):part('abd'+str(i),'b','abd'+str(i),(0,5.3+i*1.8,-2),(0,0,0),[(-1.5,0,-.7,3,1,1,'steel')])
part('pel','b','pelvis',(0,10,0),(0,0,0),[(-3,-1,-2,6,3,4,'darksteel'),(-1.5,0,-2.5,3,3,1,'steel')])
part('sp','b','spine',(0,0,2),(0,0,0),[(-1,0,0,2,10,2,'joint')])
part('neck','b','neck',(0,-2,0),(0,0,0),[(-1.5,-1,-1.5,3,3,3,'joint')])
# Narrow face, lower cyborg jaw, diagonal eyepatch and sculpted silver fringe.
part('h','r','head',(0,-2,0),(0,0,0),[(-3,-6,-3,6,6,6,'face'),(-2,-1,-2.6,4,2,5,'face')])
part('jaw','h','jaw',(0,0,0),(0,0,0),[(-2,-.3,-2.6,4,1,5,'darksteel')])
for i,s in enumerate((-1,1)):
    part('tem'+str(i),'h','temple'+str(i),(s*2.9,-2,0),(0,0,0),[(-.5,-1,-2,1,3,4,'chrome'),(-.6,1,-1,1,2,2,'darksteel')])
part('cap','h','hair',(0,-5.8,0),(0,0,0),[(-3.5,-2,-3,7,3,6,'hair'),(-3,-1,2,6,5,2,'hair')])
for i in range(9):
    part('spike'+str(i),'cap','spike'+str(i),(-3+i*.72,-1.1,.6+(i%3)*.7),(-.45-(i%3)*.12,0,(i-4)*.13),[(-.75,-4,-1,2,4,2,'hair'),(-.45,-5.5,-.5,1,2,1,'hair')])
for i in range(5):
    part('fr'+str(i),'h','fringe'+str(i),(-2.9+i*1.1,-6.2,-3.05),(0,0,-.22-i*.11),[(-.55,0,-.55,1,3+(i%3),1,'hair')])
# Cyborg shoulder assembly with separate upper arms, elbows, gauntlets and fingers.
for i,s in enumerate((-1,1)):
    part('arm'+str(i),'r','arm'+str(i),(s*4.7,0,0),(0,0,-s*.10),[(-1.5,0,-1.5,3,6,3,'carbon')])
    part('pad'+str(i),'arm'+str(i),'pauldron',(0,.4,0),(0,0,-s*.16),[(-2.4,-2,-2,5,3,4,'darksteel'),(-2,-2.6,-1.6,4,2,3,'steel')])
    part('bicep'+str(i),'arm'+str(i),'bicep',(0,2,0),(0,0,0),[(-1.7,-.3,-1.9,3,3,4,'steel')])
    part('fore'+str(i),'arm'+str(i),'fore',(0,5.6,0),(-.12,0,0),[(-1.4,-.5,-1.4,3,2,3,'joint'),(-1.9,1,-1.9,4,4,4,'darksteel'),(-1.4,1.1,-2.2,3,3,1,'chrome')])
    part('hand'+str(i),'fore'+str(i),'hand',(0,5,0),(0,0,0),[(-1.4,0,-1.1,3,2,2,'darksteel'),(-1.1,1,-1.4,2,1,3,'joint')])
    for k in range(3):part('finger'+str(i)+str(k),'hand'+str(i),'finger'+str(k),(-1+k,1.3,-.7),(-.35,0,0),[(-.4,0,-.4,1,1,1,'steel')])
    # articulated thighs, knees, tapering shin shells and armored feet
    part('leg'+str(i),'r','leg'+str(i),(s*2,11.8,0),(0,0,0),[(-1.8,0,-1.8,4,6,4,'carbon'),(-2,.3,-2.1,4,4,4,'darksteel')])
    part('thigh'+str(i),'leg'+str(i),'thigh',(0,0,-.9),(0,s*.13,0),[(-1.5,0,-1.1,3,5,2,'steel')])
    part('shin'+str(i),'leg'+str(i),'shin',(0,5.5,0),(0,0,0),[(-1.6,-.8,-1.7,3,2,4,'joint'),(-1.8,1,-1.8,4,5,4,'darksteel'),(-1.2,1,-2,2,5,1,'chrome'),(-1.5,5,-1.4,3,1,3,'joint')])
    part('knee'+str(i),'shin'+str(i),'knee',(0,0,-1.7),(0,0,0),[(-1.5,-1,-.7,3,2,2,'steel')])
    part('foot'+str(i),'shin'+str(i),'foot',(0,5.5,0),(0,0,0),[(-1.7,-.4,-3,4,2,5,'darksteel'),(-1.4,0,-3.4,3,1,2,'steel')])
# High-frequency sword: hand pivot, dark textured grip, silver blade,
# offset tip and guard, plus a narrow scabbard on the lower back.
part('sword','hand0','sword',(0,1,-.4),(-1.57,0,.06),[(-.6,-4,-.6,1,5,1,'hilt'),(-1.5,-4.5,-.6,3,1,1,'guard'),(-.7,-25,-.35,1,21,1,'blade'),(-.7,-27,-.35,1,2,1,'chrome')])
part('sheath','b','sheath',(0,8,2.7),(0,0,-.64),[(-.8,0,-.7,2,19,2,'darksteel'),(-1,0,-.9,2,2,2,'steel')])
assert cy+rh<=N
src='''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
public class RaidenModel extends EntityModel<Raiden>{
    final ModelPart root,body,head,sword;final ModelPart[] arms=new ModelPart[2],fore=new ModelPart[2],legs=new ModelPart[2],shins=new ModelPart[2];
    RaidenModel(ModelPart r){root=r;body=r.getChild("body");head=r.getChild("head");
        for(int i=0;i<2;i++){arms[i]=r.getChild("arm"+i);fore[i]=arms[i].getChild("fore");legs[i]=r.getChild("leg"+i);shins[i]=legs[i].getChild("shin");}
        sword=fore[0].getChild("hand").getChild("sword");
    }
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);
    }
    @Override public void setupAnim(Raiden e,float limb,float amount,float age,float yaw,float pitch){
        float hit=e.slashPose(age-e.tickCount),run=Math.min(1,amount);
        head.yRot=yaw*.01745f;head.xRot=pitch*.01745f;body.xRot=run*.17f+hit*.19f;body.yRot=hit*.45f;
        body.y= (float)Math.sin(age*.15)*.045f;head.y=-2+body.y;
        for(int i=0;i<2;i++){
            int sign=i==0?-1:1;float walk=(float)Math.cos(limb*.9+i*Math.PI)*run;
            arms[i].xRot=-walk*.7f;arms[i].zRot=-sign*.10f;fore[i].xRot=-.16f-Math.max(0,-walk)*.45f;
            legs[i].xRot=walk*.85f;shins[i].xRot=Math.max(0,-walk)*.75f;
        }
        arms[0].xRot=-.38f-hit*1.6f-run*.3f;arms[0].zRot=.12f+hit*.95f;
        fore[0].xRot=-.7f+hit*.65f;arms[1].xRot-=hit*.65f;
        sword.xRot=-1.57f+hit*.6f;sword.zRot=.06f-hit*.28f;
        ModelPart cap=head.getChild("hair");for(int i=0;i<9;i++)cap.getChild("spike"+i).xRot=-.45f-(i%3)*.12f-run*.18f+(float)Math.sin(age*.19+i)*.045f;
        for(int i=0;i<5;i++)head.getChild("fringe"+i).zRot=-.22f-i*.11f+(float)Math.sin(age*.14+i)*.025f;
    }
    @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    static class Renderer extends MobRenderer<Raiden,RaidenModel>{
        Renderer(EntityRendererProvider.Context c){super(c,new RaidenModel(c.bakeLayer(GlamourClient.LAYERS[3])),.42f);}
        @Override public ResourceLocation getTextureLocation(Raiden e){return new ResourceLocation(Noctis.ID,"textures/entity/raiden.png");}
        @Override protected void scale(Raiden e,PoseStack p,float partial){p.scale(1.04f,1.04f,1.04f);}
    }
}'''
(java/'RaidenModel.java').write_text(src,encoding='utf-8')
p=java/'GlamourClient.java';s=p.read_text(encoding='utf-8')
a='e.registerLayerDefinition(LAYERS[i],()->mesh(k));';assert a in s
s=s.replace(a,'e.registerLayerDefinition(LAYERS[i],()->k==3?RaidenModel.mesh():mesh(k));',1)
a='e.registerEntityRenderer(Noctis.RAIDEN.get(),RRenderer::new);';assert a in s
s=s.replace(a,'e.registerEntityRenderer(Noctis.RAIDEN.get(),RaidenModel.Renderer::new);',1);p.write_text(s,encoding='utf-8')
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
(assets/'raiden.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
print('Raiden: new custom segmented cyborg geometry, independent 1024px UV atlas, animated sword and joints')
