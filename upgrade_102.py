"""1.0.2: separate adult slime lady model, animated liquid atlas and falling droplets."""
from pathlib import Path
import sys, math, struct, zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
N=256;S=3;W=N*S
cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,mat):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+2>N:cx=0;cy+=rh+2;rh=0
    u,v=cx,cy;cx+=ww+2;rh=max(rh,hh)
    assert v+hh<=N,(mat,u,v)
    for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:
        islands.append((fx,fy,fw,fh,mat,face))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    shape='CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)
    pose='PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+')'
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",{shape},{pose});')
# Adult fantasy sea-inspired dress: fitted bodice, layered flared skirt,
# contrasting white/navy collar, rose brooch. No school uniform.
part('b','r','body',(0,0,0),(0,0,0),[(-3,-1,-2,6,12,4,'gel'),(-4,0,-3,8,6,6,'silk'),(-3,6,-2,6,4,4,'silk')])
part('bod','b','bodice',(0,1,-2),(0,0,0),[(-4,0,-2,8,5,3,'silk'),(-3,5,-1,6,3,2,'silk')])
part('belt','b','belt',(0,9,0),(0,0,0),[(-4,-1,-3,8,2,6,'navy')])
part('brooch','b','brooch',(0,3,-4.2),(0,0,.15),[(-1,-1,-.5,2,2,1,'pink')])
part('sk','b','skirt',(0,10,0),(0,0,0),[(-4,0,-3,8,3,6,'navy'),(-5,2,-4,10,2,8,'navy')])
for i in range(12):
    a=i*math.pi/6
    part('pleat'+str(i),'sk','pleat'+str(i),(math.sin(a)*4,1,math.cos(a)*3),(-.24,a,0),[(-1.5,0,0,3,5,2,'pleat')])
# Distinct, softly stepped head and asymmetric wave of gel hair.
part('h','r','head',(0,-1,0),(0,0,0),[(-4,-7,-3,8,7,6,'face'),(-3,-8,-3,6,2,6,'gel'),(-3,-1,-2.5,6,2,5,'gel')])
part('cap','h','hair',(0,-6,0),(0,0,0),[(-4,-3,-4,8,3,8,'hair'),(-5,-1,-3,10,3,6,'hair'),(-4,-2,2,8,8,3,'hair')])
for i in range(7):
    x=-4+i*1.3
    part('strand'+str(i),'h','strand'+str(i),(x,-5,3.6),(0,0,(i-3)*.055),[(-1,0,-1,2,8+i%3,3,'hair'),(-.5,7+i%3,-.5,1,4,2,'hair'),(-.5,10+i%3,0,1,2,1,'drop')])
# Side locks with rounded, stepped drips, one long asymmetric bang.
for i,s in enumerate((-1,1)):
    part('lock'+str(i),'h','lock'+str(i),(s*4.2,-5,-.5),(0,0,-s*.10),[(-1,0,-1,3,7,3,'hair'),(-1,6,-.5,2,5,2,'hair'),(-.5,10,0,1,3,1,'drop')])
part('bang','h','bang',(-2.2,-6.3,-3.3),(0,0,.30),[(-1.5,0,-.6,3,4,2,'hair'),(-1,3,-.8,2,3,1,'hair'),(-.5,5,-.6,1,2,1,'drop')])
part('fringe','h','fringe',(1.1,-7,-3.2),(0,0,-.25),[(-1,0,-.5,2,3,1,'hair'),(-.5,2,-.5,1,2,1,'hair')])
part('bow','h','bow',(3.9,-3.8,-2.7),(0,0,-.27),[(-2,-1,-.5,2,2,1,'pink'),(.1,-1,-.5,2,2,1,'pink'),(-.5,-.5,-1,1,1,1,'pink')])
for i,s in enumerate((-1,1)):
    part('arm'+str(i),'r','arm'+str(i),(s*4.6,0,0),(0,0,-s*.12),[(-1.5,-1,-1.5,3,4,3,'silk'),(-1.5,3,-1.5,3,2,3,'navy'),(-1,5,-1,2,5,2,'gel')])
    part('hand'+str(i),'arm'+str(i),'hand',(0,9.2,0),(0,0,0),[(-1.5,0,-1,3,2,2,'gel'),(-.5,1.4,-.5,1,2,1,'drop')])
    for k in range(3):part('finger'+str(i)+str(k),'hand'+str(i),'finger'+str(k),(-1+k,1,-.7),(0,0,(k-1)*.11),[(-.4,0,-.4,1,2,1,'gel')])
    part('leg'+str(i),'r','leg'+str(i),(s*2.1,12,0),(0,0,0),[(-1.7,0,-1.6,3,6,3,'gel'),(-1.4,5,-1.5,3,5,3,'gel'),(-1.5,9,-2.3,3,3,4,'gel')])
assert cy+rh<=N
src='''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
public class SlimeLadyModel extends EntityModel<Admirer>{
    final ModelPart root,body,head,skirt,bang,fringe;final ModelPart[] arms=new ModelPart[2],legs=new ModelPart[2],locks=new ModelPart[2],strands=new ModelPart[7];
    SlimeLadyModel(ModelPart r){root=r;body=r.getChild("body");head=r.getChild("head");skirt=body.getChild("skirt");bang=head.getChild("bang");fringe=head.getChild("fringe");
        for(int i=0;i<2;i++){arms[i]=r.getChild("arm"+i);legs[i]=r.getChild("leg"+i);locks[i]=head.getChild("lock"+i);}
        for(int i=0;i<7;i++)strands[i]=head.getChild("strand"+i);
    }
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,256,256);
    }
    @Override public void setupAnim(Admirer e,float limb,float amount,float age,float yaw,float pitch){
        boolean sit=e.isInSittingPose();float wave=(float)Math.sin(age*.15f),step=Math.min(1,amount);
        head.yRot=yaw*.01745f;head.xRot=pitch*.01745f;head.y=(sit?1:-1)+wave*.13f;
        body.y=sit?2:wave*.13f;body.xRot=sit?-.12f:step*.06f;body.zRot=(float)Math.sin(limb*.75f)*step*.035f;
        head.xScale=1+wave*.018f;head.yScale=1-wave*.025f;body.xScale=1+wave*.012f;body.yScale=1-wave*.015f;
        bang.zRot=.30f+(float)Math.sin(age*.13)*.055f;fringe.zRot=-.25f+(float)Math.sin(age*.14+1)*.045f;
        for(int i=0;i<7;i++){strands[i].xRot=-step*.14f+(float)Math.sin(age*.14-i*.55)*.085f;strands[i].zRot=(i-3)*.055f+(float)Math.sin(age*.10+i*.4)*.045f;strands[i].yScale=1+(float)Math.sin(age*.16+i*.8)*.045f;}
        for(int i=0;i<2;i++){int s=i==0?-1:1;float walk=(float)Math.cos(limb*.6662+i*Math.PI)*step;
            arms[i].xRot=-walk*.65f;arms[i].zRot=-s*.12f+(float)Math.sin(age*.11+i)*.04f;
            legs[i].xRot=sit?-1.25f:walk*.75f;legs[i].y=sit?14:12;locks[i].zRot=-s*.10f+(float)Math.sin(age*.13+i)*.07f;
        }
        for(int i=0;i<12;i++){ModelPart p=skirt.getChild("pleat"+i);p.xRot=-.24f+(float)Math.sin(age*.15+i*.65f)*.045f+step*.06f;}
    }
    @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    static class Renderer extends MobRenderer<Admirer,SlimeLadyModel>{
        static final ResourceLocation[] FRAMES=new ResourceLocation[12];
        static{for(int i=0;i<FRAMES.length;i++)FRAMES[i]=new ResourceLocation(Noctis.ID,"textures/entity/slime_flow_"+i+".png");}
        Renderer(EntityRendererProvider.Context c){super(c,new SlimeLadyModel(c.bakeLayer(GlamourClient.LAYERS[2])),.43f);}
        @Override public ResourceLocation getTextureLocation(Admirer e){return FRAMES[(e.tickCount/3)%FRAMES.length];}
    }
}'''
(java/'SlimeLadyModel.java').write_text(src,encoding='utf-8')
p=java/'GlamourClient.java';s=p.read_text(encoding='utf-8')
a='()->k==3?RaidenModel.mesh():mesh(k)';assert a in s;s=s.replace(a,'()->k==3?RaidenModel.mesh():k==2?SlimeLadyModel.mesh():mesh(k)',1)
a='c->new LadyRenderer(c,2,"slime_lady")';assert a in s;s=s.replace(a,'SlimeLadyModel.Renderer::new',1);p.write_text(s,encoding='utf-8')
p=java/'Admirer.java';s=p.read_text(encoding='utf-8')
a='@Override public void tick(){super.tick();';assert a in s
s=s.replace(a,'''@Override public void tick(){super.tick();
        if(getType()==Noctis.SLIME_LADY.get()&&level() instanceof ServerLevel gel&&tickCount%7==0){
            double x=getX()+(random.nextDouble()-.5)*.60,z=getZ()+(random.nextDouble()-.5)*.48;
            gel.sendParticles(ParticleTypes.FALLING_WATER,x,getY()+getBbHeight()*.84,z,1,0,0,0,0);
            if(tickCount%21==0)gel.sendParticles(ParticleTypes.FALLING_WATER,getX()+.28,getY()+getBbHeight()*.56,getZ(),1,.05,0,.05,0);
        }
        ''',1);p.write_text(s,encoding='utf-8')
# UV islands with periodic flowing highlights. Clothes remain opaque and static.
def mix(a,b,t):return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def shade(mat,u,v,face,t):
    if mat in ('gel','hair','face','drop'):
        flow=math.sin((u*2.0+math.sin(v*5-t)*.25)*math.pi*2-t)
        ripple=math.sin(v*13+u*5-t*2)
        q=.40+.20*flow+.13*ripple
        c=mix((5,77,129),(45,207,230),max(0,min(1,q)))
        if mat=='hair':c=mix((5,86,146),(38,198,226),max(0,min(1,q+.04)))
        if flow>.84 and ripple>-.15:c=mix(c,(156,246,250),.66)
        if flow>.94 and ripple>.28:c=(209,250,250)
        if mat=='drop':c=mix(c,(148,239,248),.27)
        if mat=='face' and face=='front':
            c=mix((21,155,192),(61,206,222),.6+.10*flow)
            # One visible golden eye (the other is under the asymmetric gel bang).
            dx=(u-.72)/.205;dy=(v-.43)/.20
            d=dx*dx+(dy+dx*.12)**2
            if d<1:
                c=(15,41,71)
                if d<.78:
                    c=(244,249,237)
                    if (dx+.08)**2/.46+dy*dy/.80<1:
                        c=(215,136+int(max(0,dy)*70),32)
                        if (dx+.06)**2/.16+dy*dy/.55<1:c=(49,35,25)
                        if (dx+.29)**2+(dy+.38)**2<.10:c=(255,252,230)
            if abs(dy+.9+dx*.15)<.12 and abs(dx)<.93:c=(17,50,72)
            if abs(v-(.74+.18*(u-.53)**2))<.027 and .48<u<.72:c=(26,68,95)
            if abs(v-(.79-.12*(u-.60)**2))<.025 and .54<u<.66:c=(231,105,145)
            if .73<u<.88 and .65<v<.70:c=mix(c,(132,157,217),.5)
    elif mat=='silk':
        c=mix((159,187,209),(251,251,245),.65+.25*math.sin(u*math.pi))
        if v<.13 or (face=='front' and v<.52 and abs(abs(u-.5)-(.42-v*.65))<.07):c=(22,63,120)
        if face=='front' and v<.52 and abs(abs(u-.5)-(.42-v*.65))<.025:c=(237,245,251)
    elif mat in ('navy','pleat'):
        c=mix((12,35,81),(37,95,169),.25+.55*math.sin(u*math.pi))
        if v>.74 and v<.81 or v>.88 and v<.94:c=(223,241,245)
    elif mat=='pink':c=mix((152,60,107),(250,172,201),.25+.65*math.sin(u*math.pi))
    else:c=(40,150,190)
    factor={'top':1.07,'bottom':.8,'left':.91,'right':.95,'front':1,'back':.87}[face]
    return tuple(max(0,min(255,round(i*factor))) for i in c)
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
for frame in range(12):
    pix=bytearray(W*W*4);t=frame*math.pi*2/12
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            for i in range(w*S):
                c=shade(mat,(i+.5)/(w*S),(j+.5)/(h*S),face,t)
                pos=((y*S+j)*W+x*S+i)*4;pix[pos:pos+4]=bytes((*c,255))
    raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
    (assets/f'slime_flow_{frame}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
print('Slime lady: separate gel model, 12 animated UV frames, water droplets')
