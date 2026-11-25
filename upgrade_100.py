"""Noctis 1.0.0: Gabumon sculpted Digimon-inspired model and face-specific UV atlas."""
from pathlib import Path
import sys,math,struct,zlib,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
# Each cuboid gets its own nonoverlapping, face-aware UV island.
N=256;S=4;W=N*S
pixels=bytearray(W*W*4);rng=random.Random(1000)
cursor_x=cursor_y=row_h=0
palette={'skin':(242,191,63),'fur':(226,233,244),'blue':(48,64,146),'purple':(152,42,96),'ivory':(245,239,211),'horn':(232,178,56),'mouth':(103,27,48),'tongue':(218,72,105),'nose':(30,32,43),'belly':(69,184,210)}
def pixel(x,y,c):
    if 0<=x<W and 0<=y<W:
        p=(y*W+x)*4;pixels[p:p+4]=bytes((*c,255))
def blend(a,b,t):return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def paint_face(x,y,w,h,mat,face):
    if w<=0 or h<=0:return
    x*=S;y*=S;w*=S;h*=S
    base=palette.get(mat,palette['fur'])
    for j in range(h):
        v=(j+.5)/h
        for i in range(w):
            u=(i+.5)/w
            col=base
            if mat in ('fur','pelt','mask','ear','mitt','tailfur'):
                # Deep blue irregular tiger markings on ivory pelt, rather than uniform stripes.
                stripe=math.sin((v*2.6+u*.38+math.sin(u*8)*.15)*math.pi*2)
                isblue=stripe>.48 and (mat not in ('mask','ear') or v<.3 or u<.18 or u>.82)
                if mat=='ear':isblue=v<.26 or (u>.72 and v<.63)
                if mat=='mask' and face=='front':
                    isblue=(v<.32 and abs(u-.5)<.36-v*.45) or (v>.65 and (u<.25 or u>.75))
                col=palette['blue'] if isblue else palette['fur']
            elif mat=='belly':
                # Rounded blue disc with pink curling emblem, dark outline.
                xx=(u-.5)*2;yy=(v-.5)*2;rr=xx*xx+yy*yy
                col=palette['skin'] if rr>.92 else (42,75,115) if rr>.79 else palette['belly']
                if rr<.72:
                    a=math.atan2(yy,xx);r=math.sqrt(rr)
                    swirl=abs(r-(.22+.10*(a+math.pi)))<.115
                    if swirl or (xx<-.15 and abs(yy+.23)<.13) or (yy>.22 and abs(xx-.18)<.12):col=(198,66,116)
            elif mat=='horn':
                col=blend((164,112,32),(255,218,106),.35+.5*math.sin(u*math.pi))
                if int(v*7.5)%2==0 and (v*7.5)%1<.13:col=(153,103,37)
            elif mat=='purple':
                col=blend((92,22,67),(201,64,130),.4+.5*math.sin(u*math.pi))
            elif mat=='skin':
                col=blend((212,143,37),(255,210,87),.35+.5*math.sin(u*math.pi))
            if mat=='mask' and face in ('front','left','right'):
                # Anime eye silhouette: dark outline, white sclera, red iris, highlight.
                eyes=[(.26,.47),(.74,.47)] if face=='front' else [(.52,.47)]
                for ex,ey in eyes:
                    dx=(u-ex)/(.19 if face=='front' else .25);dy=(v-ey)/.26
                    # slightly slanted, large red eyes, no square eye frames
                    if dx*dx+(dy+dx*.15)**2<1:
                        col=(34,28,43)
                        if dx*dx+(dy+dx*.15)**2<.77:
                            col=(252,249,239)
                            if (dx+.06)**2/.42+(dy+.02)**2/.78<1:
                                col=(158+int(55*max(0,dy+.7)),40,52)
                                if (dx+.07)**2/.13+(dy+.02)**2/.53<1:col=(31,22,36)
                                if (dx+.30)**2+(dy+.39)**2<.095:col=(255,255,249)
                    if abs(dy+.89+dx*.2)<.10 and abs(dx)<.85:col=(33,30,46)
            if mat=='muzzle':
                col=palette['fur'] if v<.78 else (171,185,216)
                if face=='front' and v<.34 and abs(u-.5)<.26:col=palette['nose']
            light={'top':1.09,'bottom':.78,'left':.95,'right':.88,'front':1.02,'back':.87}.get(face,1)
            noise=rng.randint(-2,2)
            col=tuple(max(0,min(255,round(c*light)+noise)) for c in col)
            pixel(x+i,y+j,col)
def cube(x,y,z,w,h,d,mat):
    global cursor_x,cursor_y,row_h
    # Minecraft cuboid UV dimensions are integral; dimensions deliberately integer.
    ww=2*(w+d);hh=h+d
    if cursor_x+ww+2>N:cursor_x=0;cursor_y+=row_h+2;row_h=0
    u,v=cursor_x,cursor_y;cursor_x+=ww+2;row_h=max(row_h,hh)
    assert v+hh<=N,(mat,u,v,ww,hh)
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:
        paint_face(fx,fy,fw,fh,mat,face)
    fmt=lambda n:str(float(n))+'f'
    return f'.texOffs({u},{v}).addBox('+','.join(fmt(n) for n in (x,y,z,w,h,d))+')'
lines=[]
def part(var,parent,name,pos,rot,boxes):
    shape='CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)
    fmt=lambda n:str(float(n))+'f'
    pose='PartPose.offsetAndRotation('+','.join(fmt(x) for x in (*pos,*rot))+')'
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",{shape},{pose});')
# Broad, rounded yellow dinosaur body, low hips and pelt draped over the back.
part('b','r','body',(0,16,0),(0,0,0),[(-4,-6,-4,8,11,8,'skin'),(-5,-4,-3,10,7,6,'skin'),(-3,-7,-3,6,2,6,'skin')])
part('belly','b','belly',(0,0,-4.2),(0,0,0),[(-4,-4,-1,8,9,1,'belly')])
part('cloak','b','cloak',(0,-5,3),(-.10,0,0),[(-5,0,-1,10,7,3,'pelt'),(-4,6,0,8,4,3,'pelt')])
# Wolf pelt hood covers head; yellow jaw and neck are visible below.
part('h','r','head',(0,8,-2),(0,0,0),[(-5,-6,-4,10,7,8,'mask'),(-4,-7,-3,8,2,6,'pelt'),(-4,0,-3,8,3,6,'skin')])
part('snout','h','snout',(0,0,-4),(0,0,0),[(-3,-3,-4,6,3,5,'muzzle'),(-2,-2,-6,4,2,3,'muzzle')])
part('nose','h','nose',(0,-2,-9.6),(0,0,0),[(-1.5,0,-1,3,1,2,'nose')])
part('jaw','h','jaw',(0,1,-3),(0,0,0),[(-3,0,-6,6,2,6,'skin'),(-2,-.2,-5,4,1,5,'mouth'),(-1,-.5,-4,2,1,3,'tongue')])
for i,s in enumerate((-1,1)):
    part('cheek'+str(i),'h','cheek'+str(i),(s*4.2,-1,-1),(0,0,s*.32),[(-1,-1,-3,2,4,6,'pelt'),(-1,2,0,2,3,3,'pelt')])
    part('fang'+str(i),'h','fang'+str(i),(s*2.3,-.4,-6.9),(0,0,s*.14),[(-.5,0,-.5,1,2,1,'ivory')])
    part('ear'+str(i),'h','ear'+str(i),(s*3.8,-5,1),(-.24,0,s*.46),[(-1.5,-5,-1,3,5,2,'ear'),(-1,-8,-.5,2,3,1,'blue')])
# Gold, slanted, tapered horn rather than a plain vertical block.
part('horn','h','horn',(0,-5,-4),(.48,0,0),[(-2,-3,-2,4,3,4,'horn'),(-1.5,-5,-1.5,3,2,3,'horn'),(-1,-7,-1,2,2,2,'horn'),(-.5,-9,-.5,1,2,1,'horn')])
for i,s in enumerate((-1,1)):
    # Yellow arms and clenched fingers emerging from enormous fur paws.
    part('a'+str(i),'r','arm'+str(i),(s*4.7,12,0),(0,0,-s*.28),[(-2,-1,-2,4,6,4,'skin'),(-2.5,3,-2.5,5,4,5,'skin')])
    part('mitt'+str(i),'a'+str(i),'mitt',(0,3,2),(0,0,0),[(-3.5,-1,-1,7,6,5,'mitt'),(-3,3,-1,6,3,4,'mitt')])
    for k in range(3):
        part(f'claw{i}{k}','mitt'+str(i),'claw'+str(k),(-2+k*2,5,1),(.10,0,(k-1)*.14),[(-.8,0,-.8,2,3,2,'purple'),(-.5,2,-.5,1,2,1,'purple')])
        part(f'finger{i}{k}','a'+str(i),'finger'+str(k),(-1.5+k*1.5,5,-2.5),(-.12,0,0),[(-.6,0,-1,1,2,2,'skin')])
    # thick reptilian thighs, broad yellow feet, white claws
    part('f'+str(i),'r','foot'+str(i),(s*3,20,0),(0,0,0),[(-2.5,-2,-2.5,5,4,5,'skin'),(-3,1,-5,6,3,7,'skin')])
    for k in range(3):
        part(f'toe{i}{k}','f'+str(i),'toe'+str(k),(-2+k*2,2,-4.5),(-.22,0,(k-1)*.14),[(-.75,0,-2,2,2,3,'ivory'),(-.5,0,-3,1,1,1,'ivory')])
# Yellow reptile tail with distinct striped pelt flap.
part('t','b','tail',(0,3,3),(-.42,0,0),[(-2,-2,0,4,4,6,'skin')])
part('tip','t','tip',(0,0,5),(-.45,0,0),[(-1.5,-1.5,0,3,3,5,'skin'),(-.5,-.5,4,1,1,2,'skin')])
part('flap','cloak','flap',(0,6,2),(-.48,0,0),[(-3,-1,0,6,3,7,'tailfur'),(-2,0,6,4,2,3,'tailfur')])
for k in range(3):part('flapclaw'+str(k),'flap','claw'+str(k),(-2+k*2,0,8),(0,0,(k-1)*.12),[(-.5,-.5,0,1,2,3,'purple')])
assert cursor_y+row_h<=N
src='''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
public class GabumonModel extends EntityModel<Gabumon>{
    final ModelPart root,body,head,jaw,tail,tip,cloak,flap;final ModelPart[] arms=new ModelPart[2],feet=new ModelPart[2],ears=new ModelPart[2],mitts=new ModelPart[2];
    GabumonModel(ModelPart r){root=r;body=r.getChild("body");head=r.getChild("head");jaw=head.getChild("jaw");tail=body.getChild("tail");tip=tail.getChild("tip");cloak=body.getChild("cloak");flap=cloak.getChild("flap");for(int i=0;i<2;i++){arms[i]=r.getChild("arm"+i);feet[i]=r.getChild("foot"+i);ears[i]=head.getChild("ear"+i);mitts[i]=arms[i].getChild("mitt");}}
    static LayerDefinition mesh(){
        MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);
    }
    @Override public void setupAnim(Gabumon e,float limb,float amount,float age,float yaw,float pitch){
        boolean sit=e.isInSittingPose(),air=!e.onGround()&&!sit;float breath=e.breathPose(age-e.tickCount);
        float bob=sit?0:(float)Math.sin(limb*1.33)*amount*.5f;
        body.y=(sit?18:16)+bob;body.xRot=sit?-.12f:air?-.10f:amount*.08f;
        head.y=(sit?10:8)+bob;head.yRot=yaw*.01745f;head.xRot=pitch*.01745f-breath*.24f;
        jaw.xRot=.06f+breath*.72f;tail.yRot=(float)Math.sin(age*.15)*.38f;tip.yRot=(float)Math.sin(age*.15-.7f)*.31f;
        cloak.xRot=-.1f-amount*.12f;flap.xRot=-.48f+(float)Math.sin(age*.15)*.10f-amount*.15f;
        for(int i=0;i<2;i++){int s=i==0?-1:1;float step=(float)Math.cos(limb*.6662+i*Math.PI)*amount;
            arms[i].y=(sit?14:12)+bob;arms[i].xRot=air?-1.2f:-step*.67f-breath*.65f;arms[i].zRot=-s*(.28f+breath*.45f+(air?.35f:0));
            feet[i].xRot=sit?-1.10f:air?-.45f:step*.7f;feet[i].y=sit?21:20;ears[i].zRot=s*(.46f+(float)Math.sin(age*.13+i)*.07f);ears[i].xRot=-.24f+breath*.22f;
            mitts[i].xRot=step*.16f;
        }
    }
    @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    static class Renderer extends MobRenderer<Gabumon,GabumonModel>{
        Renderer(EntityRendererProvider.Context c){super(c,new GabumonModel(c.bakeLayer(EclipseGuestsClient.B)),.46f);}
        @Override public ResourceLocation getTextureLocation(Gabumon e){return new ResourceLocation(Noctis.ID,"textures/entity/gabumon.png");}
        @Override protected void scale(Gabumon e,PoseStack p,float partial){p.scale(.82f,.82f,.82f);}
    }
}'''
(java/'GabumonModel.java').write_text(src,encoding='utf-8')
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
raw=b''.join(b'\0'+pixels[y*W*4:(y+1)*W*4] for y in range(W))
(assets/'gabumon.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
# Adjust physical dimensions to new wider, lower stance while preserving entity ID.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='of(Gabumon::new,MobCategory.CREATURE).sized(.8f,1.35f)';assert a in s;s=s.replace(a,'of(Gabumon::new,MobCategory.CREATURE).sized(.95f,1.65f)',1);p.write_text(s,encoding='utf-8')
print('Gabumon: custom sculpted mesh, nonoverlapping per-face UV atlas, animations')
