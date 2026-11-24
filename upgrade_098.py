"""0.9.8: visual overhaul, proper Gabumon model, Elvis fix and creative spells."""
from pathlib import Path
import sys,struct,zlib,math,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
edit('Noctis.java',[
('if(d.getInt("level")<s.level)','if(!p.isCreative()&&d.getInt("level")<s.level)'),
('if(d.getInt("mana")<s.cost)','if(!p.isCreative()&&d.getInt("mana")<s.cost)'),
('d.putInt("mana",d.getInt("mana")-s.cost);','if(!p.isCreative())d.putInt("mana",d.getInt("mana")-s.cost);')
])
edit('Client.java',[
('b.active=s.level<=Noctis.View.level;','boolean creative=Minecraft.getInstance().player!=null&&Minecraft.getInstance().player.isCreative();b.active=creative||s.level<=Noctis.View.level;if(creative)b.setMessage(Component.literal(s.label));')
])
edit('Elvis.java',[
('if(level() instanceof ServerLevel l&&l.dimension()==Level.OVERWORLD&&l.isDay()){l.sendParticles(ParticleTypes.NOTE,getX(),getY()+1,getZ(),8,.3,.6,.3,0);discard();}',''),
('public static AttributeSupplier.Builder attributes()','@Override public boolean removeWhenFarAway(double d){return d>128*128;}\n    public static AttributeSupplier.Builder attributes()')
])
# Fully clothed adult fantasy characters: distinct silhouettes and layered hairstyles.
edit('GlamourClient.java',[
('add(b,"bodice",c(0,64).addBox(-4.7f,1,-4.5f,9.4f,5,4.5f),0,0,0);','''r.addOrReplaceChild("body",c(16,16).addBox(-3.1f,0,-2,6.2f,12,4),PartPose.ZERO);b=r.getChild("body");
            add(b,"bodice",c(0,64).addBox(-4.2f,0,-2.5f,8.4f,5,5),0,0,0);'''),
('add(b,"bust"+i,c(32,64).addBox(-2.4f,-2,-2.3f,4.8f,4,3.5f),s*2.3f,3,-2.3f);','''add(b,"bust"+i,c(32,64).addBox(-2.7f,-2,-3.3f,5.4f,4.8f,4.8f),s*2.45f,3,-2.4f);
                add(b,"bodiceTrim"+i,c(88,80).addBox(-2.3f,-.4f,-.2f,4.6f,.65f,.7f),s*2.45f,1.5f,-5.55f);'''),
('add(b,"hip"+i,c(56,64).addBox(-2.9f,0,-2.7f,5.8f,4,5.4f),s*2.3f,9,0);','''add(b,"hip"+i,c(56,64).addBox(-3.2f,0,-2.5f,6.4f,4.6f,6.5f),s*2.6f,8.6f,.3f);
                add(b,"backPanel"+i,c(56,64).addBox(-2.6f,0,0,5.2f,4,3),s*2.65f,9,2.5f);'''),
('add(b,"skirt",c(0,82).addBox(-5,10,-3.2f,10,5,6.4f),0,0,0);','''add(b,"skirt",c(0,82).addBox(-5.8f,11,-3.2f,11.6f,3.7f,7.3f),0,0,0);
            for(int i=0;i<6;i++){float x=-3.5f+i*1.35f;
                h.addOrReplaceChild("bang"+i,c(108,0).addBox(-.8f,0,-.55f,1.6f,2+(i%3),1.1f),PartPose.offsetAndRotation(x,-8.2f,-4.05f,0,0,(i-2.5f)*.13f));}
            for(int i=0;i<5;i++){float x=-3.6f+i*1.8f;
                h.addOrReplaceChild("strand"+i,c(96,54).addBox(-1,0,-.9f,2,17+(i%2)*3,2),PartPose.offsetAndRotation(x,-6,4.2f,0,0,(i-2)*.04f));}
            for(int i=0;i<2;i++){int s=i==0?-1:1;PartDefinition arm=r.getChild(i==0?"right_arm":"left_arm");arm.addOrReplaceChild("puff",c(0,108).addBox(-2.2f,-2,-2.2f,4.4f,4,4.4f),PartPose.ZERO);}
            '''),
('l.zRot=-.08f+sway;r.zRot=.08f+sway;','l.zRot=-.08f+sway;r.zRot=.08f+sway;for(int i=0;i<5;i++)head.getChild("strand"+i).xRot=(float)Math.sin(age*.12+i*.3)*.045f-amount*.12f;')
])
# Replace Gabumon's humanoid mesh and renderer entirely.
edit('EclipseGuestsClient.java',[
('e.registerLayerDefinition(B,()->mesh(1));','e.registerLayerDefinition(B,GabumonModel::mesh);'),
('e.registerEntityRenderer(Noctis.GABUMON.get(),BRenderer::new);','e.registerEntityRenderer(Noctis.GABUMON.get(),GabumonModel.Renderer::new);')
])
(java/'GabumonModel.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
public class GabumonModel extends EntityModel<Gabumon>{
    final ModelPart root,body,head,jaw,tail,tailTip;final ModelPart[] arms=new ModelPart[2],feet=new ModelPart[2],ears=new ModelPart[2];
    GabumonModel(ModelPart r){root=r;body=r.getChild("body");head=r.getChild("head");jaw=head.getChild("jaw");tail=body.getChild("tail");tailTip=tail.getChild("tip");for(int i=0;i<2;i++){arms[i]=r.getChild("arm"+i);feet[i]=r.getChild("foot"+i);ears[i]=head.getChild("ear"+i);}}
    static CubeListBuilder c(int u,int v){return CubeListBuilder.create().texOffs(u,v);}
    static PartDefinition add(PartDefinition p,String n,CubeListBuilder c,float x,float y,float z){return p.addOrReplaceChild(n,c,PartPose.offset(x,y,z));}
    static LayerDefinition mesh(){
        MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
        PartDefinition b=add(r,"body",c(0,0).addBox(-4,-6,-3,8,8,6),0,18,0);
        add(b,"belly",c(32,0).addBox(-2.8f,-5,-3.6f,5.6f,7,1),0,0,0);
        add(b,"ruff",c(48,0).addBox(-4.6f,-7,-3.5f,9.2f,3,7),0,0,0);
        PartDefinition h=add(r,"head",c(0,20).addBox(-4.5f,-6,-4,9,7,7),0,10,-2);
        add(h,"pelt",c(36,20).addBox(-5,-7,-3.5f,10,2,8),0,0,0);
        add(h,"backfur",c(80,0).addBox(-4.8f,-4,2,9.6f,7,2),0,0,0);
        add(h,"muzzle",c(0,40).addBox(-3,-2,-8,6,3,5),0,0,0);
        add(h,"nose",c(24,40).addBox(-1.6f,-1.8f,-8.6f,3.2f,1.4f,.9f),0,0,0);
        PartDefinition jaw=add(h,"jaw",c(40,40).addBox(-2.7f,0,-4.7f,5.4f,1.6f,4.7f),0,1,-3);
        for(int s:new int[]{-1,1})add(jaw,"fang"+s,c(56,40).addBox(-.4f,-1,-.4f,.8f,1.2f,.8f),s*2,0,-3.8f);
        PartDefinition horn=h.addOrReplaceChild("horn",c(96,0).addBox(-1.7f,-3,-1.7f,3.4f,3.3f,3.4f).texOffs(96,10).addBox(-1.15f,-5,-1.15f,2.3f,2.4f,2.3f).texOffs(96,18).addBox(-.55f,-6.5f,-.55f,1.1f,1.8f,1.1f),PartPose.offsetAndRotation(0,-5,-2.8f,-.25f,0,0));
        for(int i=0;i<2;i++){int s=i==0?-1:1;
            PartDefinition ear=h.addOrReplaceChild("ear"+i,c(72,20).addBox(-1.5f,-5,-1,3,5,2).texOffs(84,20).addBox(-.85f,-7,-.7f,1.7f,2.5f,1.4f),PartPose.offsetAndRotation(s*4,-3,1.5f,0,0,s*.65f));
            PartDefinition a=r.addOrReplaceChild("arm"+i,c(0,60).addBox(-1.9f,-1,-2,3.8f,5,4).texOffs(20,60).addBox(-2,3,-2.5f,4,3,5),PartPose.offsetAndRotation(s*4.4f,13,0,0,0,-s*.18f));
            PartDefinition f=add(r,"foot"+i,c(40,60).addBox(-2,-1,-2,4,3,4).texOffs(60,60).addBox(-2.2f,1,-4,4.4f,3,6),s*2.2f,20,0);
            for(int k=0;k<3;k++){add(a,"claw"+k,c(80,60).addBox(-.4f,0,-.8f,.8f,1.3f,1.6f),-1.25f+k*1.25f,6,-1.8f);add(f,"toe"+k,c(80,60).addBox(-.4f,-.5f,-1.5f,.8f,1,1.5f),-1.4f+k*1.4f,3,-3.8f);}
        }
        PartDefinition t=b.addOrReplaceChild("tail",c(0,84).addBox(-2,-1.8f,0,4,3.6f,6),PartPose.offsetAndRotation(0,1,3,-.2f,0,0));
        t.addOrReplaceChild("tip",c(24,84).addBox(-1.3f,-1.3f,0,2.6f,2.6f,5).texOffs(44,84).addBox(-.6f,-.6f,4,1.2f,1.2f,2),PartPose.offsetAndRotation(0,0,5,-.35f,0,0));
        return LayerDefinition.create(m,128,128);
    }
    @Override public void setupAnim(Gabumon e,float limb,float amount,float age,float yaw,float pitch){
        boolean sit=e.isInSittingPose();float breath=e.breathPose(age-e.tickCount);
        body.y=sit?20:18;head.y=sit?12:10;head.yRot=yaw*.01745f;head.xRot=pitch*.01745f-breath*.23f;jaw.xRot=breath*.6f;
        tail.yRot=(float)Math.sin(age*.17)*.33f;tailTip.yRot=(float)Math.sin(age*.17-.6f)*.35f;
        for(int i=0;i<2;i++){int s=i==0?-1:1;float step=(float)Math.cos(limb*.6662+i*Math.PI)*amount;
            arms[i].xRot=-step*.65f;arms[i].zRot=-s*.18f;feet[i].xRot=sit?-1.15f:step*.85f;feet[i].y=sit?21:20;ears[i].zRot=s*(.65f+(float)Math.sin(age*.12+i)*.06f);}
    }
    @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    static class Renderer extends MobRenderer<Gabumon,GabumonModel>{
        Renderer(EntityRendererProvider.Context c){super(c,new GabumonModel(c.bakeLayer(EclipseGuestsClient.B)),.43f);}
        @Override public ResourceLocation getTextureLocation(Gabumon e){return new ResourceLocation(Noctis.ID,"textures/entity/gabumon.png");}
        @Override protected void scale(Gabumon e,PoseStack p,float partial){p.scale(.88f,.88f,.88f);}
    }
}''',encoding='utf-8')
# Refine the boss silhouette: narrow torso, layered coat, silver flowing hair, overlapping wing feathers.
edit('FallenClient.java',[
('h.addOrReplaceChild("silver",CubeListBuilder.create().texOffs(64,0).addBox(-4.5f,-9,-4.5f,9,2,9).texOffs(64,14).addBox(-4,-7,3.1f,8,21,2),PartPose.ZERO);','''h.addOrReplaceChild("silver",CubeListBuilder.create().texOffs(64,0).addBox(-4.4f,-8.9f,-4.3f,8.8f,1.8f,8.6f),PartPose.ZERO);
        for(int i=0;i<7;i++){float x=-3.7f+i*1.23f;
            h.getChild("silver").addOrReplaceChild("strand"+i,CubeListBuilder.create().texOffs(64,14).addBox(-.85f,0,-.85f,1.7f,23+(i%3)*2,1.7f),PartPose.offsetAndRotation(x,-7,4.0f+(i%2)*.45f,.08f,0,(i-3)*.035f));}
        '''),
('h.addOrReplaceChild("partedFringeL",CubeListBuilder.create().texOffs(108,0).addBox(-2,0,-.5f,3,3,1),PartPose.offsetAndRotation(-2.1f,-7.8f,-4.2f,0,0,.18f));','''h.addOrReplaceChild("partedFringeL",CubeListBuilder.create().texOffs(108,0).addBox(-.7f,0,-.5f,1.4f,4,1).texOffs(114,0).addBox(-1.1f,2,-.4f,.8f,4,.8f),PartPose.offsetAndRotation(-1.2f,-8.2f,-4.25f,0,0,.38f));'''),
('h.addOrReplaceChild("partedFringeR",CubeListBuilder.create().texOffs(108,0).addBox(-1,0,-.5f,3,2,1),PartPose.offsetAndRotation(2.1f,-7.8f,-4.2f,0,0,-.18f));','''h.addOrReplaceChild("partedFringeR",CubeListBuilder.create().texOffs(108,0).addBox(-.7f,0,-.5f,1.4f,4,1).texOffs(114,0).addBox(.3f,2,-.4f,.8f,4,.8f),PartPose.offsetAndRotation(1.2f,-8.2f,-4.25f,0,0,-.38f));'''),
('addBox(-1,-1,-1,2,17,3)','addBox(-.85f,-1,-.8f,1.7f,21,1.6f)'),
('PartPose.offsetAndRotation(15,-2,0,0,0,-.35f)','PartPose.offsetAndRotation(12,-1,0,0,0,-.22f)'),
('addBox(-1,0,-.6f,2.7f,11+i*.9f,1.2f)','addBox(-1.3f,0,-.6f,3.5f,13+i*.9f,1.2f)'),
('addBox(-1,0,-.5f,2.6f,18-i,1)','addBox(-1.3f,0,-.5f,3.5f,18-i,1)'),
('        r.getChild("right_arm").addOrReplaceChild("sword",','''        for(int i=0;i<2;i++){int s=i==0?-1:1;PartDefinition arm=r.getChild(i==0?"right_arm":"left_arm");arm.addOrReplaceChild("pauldron",CubeListBuilder.create().texOffs(64,98).addBox(-2.6f,-2.8f,-2.6f,5.2f,2.8f,5.2f).texOffs(64,110).addBox(-2.8f,-1,-2.7f,5.6f,2,5.4f),PartPose.ZERO);}
        b.addOrReplaceChild("lapels",CubeListBuilder.create().texOffs(0,112).addBox(-3,-.5f,-2.7f,1.5f,8,.8f).texOffs(8,112).addBox(1.5f,-.5f,-2.7f,1.5f,8,.8f),PartPose.ZERO);
        r.getChild("right_arm").addOrReplaceChild("sword",'''),
('addBox(-.9f,1,-.4f,1.8f,28,.8f)','addBox(-.48f,1,-.32f,.96f,36,.64f)'),
('hairBack.xRot=wind*.5f;','hairBack.xRot=wind*.5f;for(int i=0;i<7;i++)hairBack.getChild("strand"+i).xRot=(float)Math.sin(age*.19-i*.25)*.045f;')
])
# Texture tooling: upscale existing UV atlases, preserving all existing equipment
# and paint finer details on exact front-face UV rectangles.
def read(p):
    data=p.read_bytes();pos=8;comp=b''
    while pos<len(data):
        n=struct.unpack('>I',data[pos:pos+4])[0];k=data[pos+4:pos+8];b=data[pos+8:pos+8+n];pos+=12+n
        if k==b'IHDR':w,h,d,c,_,_,_=struct.unpack('>IIBBBBB',b);assert d==8 and c==6
        elif k==b'IDAT':comp+=b
    raw=zlib.decompress(comp);stride=w*4+1;assert all(raw[y*stride]==0 for y in range(h))
    return w,h,[[tuple(raw[y*stride+1+x*4:y*stride+5+x*4]) for x in range(w)] for y in range(h)]
def save(p,pix):
    h=len(pix);w=len(pix[0])
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for q in row for v in q) for row in pix)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
def color(c):return tuple(c)+(255,) if len(c)==3 else tuple(c)
def rect(p,x,y,w,h,c):
    c=color(c)
    for yy in range(max(0,y),min(len(p),y+h)):
        for xx in range(max(0,x),min(len(p[0]),x+w)):p[yy][xx]=c
def line(p,x1,y1,x2,y2,c,width=1):
    n=max(abs(x2-x1),abs(y2-y1),1)
    for i in range(n+1):
        x=round(x1+(x2-x1)*i/n);y=round(y1+(y2-y1)*i/n);rect(p,x,y,width,width,c)
def up(name):
    path=assets/(name+'.png');w,h,p=read(path);return path,[[p[y//4][x//4] for x in range(w*4)] for y in range(h*4)]
def uv(p,x,y,w,h,c):rect(p,x*4,y*4,w*4,h*4,c)
def face(p,skin,hair,eye,lip,style):
    # 32px front face, distinct eyes, lashes, nose, jaw shading and lips.
    ox=oy=32
    def r(x,y,w,h,c):rect(p,ox+x,oy+y,w,h,c)
    def l(x,y,x2,y2,c,w=1):line(p,ox+x,oy+y,ox+x2,oy+y2,c,w)
    def tint(v):return tuple(max(0,min(255,n+v)) for n in skin)
    r(0,0,32,32,skin)
    for y in range(32):
        r(0,y,2,1,tint(-24));r(30,y,2,1,tint(-28))
    r(2,29,28,3,tint(-15));r(14,14,3,8,tint(-13));r(15,16,2,5,tint(10));r(12,22,8,1,tint(-28))
    if style=='anime':
        for x in (4,19):
            r(x,10,9,9,(248,239,239));r(x,9,9,2,(44,28,42));r(x+1,18,7,1,tint(-25))
            r(x+3,11,5,7,eye);r(x+4,12,3,5,(38,24,46));r(x+3,11,2,2,(255,250,246));r(x+6,16,2,1,(230,168,224))
            l(x-1,9,x+2,11,(42,25,40),1);l(x,6,x+7,7,hair,1)
        r(4,21,4,2,tint(-10));r(24,21,4,2,tint(-10))
        r(12,25,8,2,lip);r(14,27,4,1,(236,118,142))
        for x in range(0,32):
            depth=3+int(4*abs(math.sin(x*.19)))
            for y in range(depth):r(x,y,1,1,tuple(min(255,v+(x%5)*3) for v in hair))
    else:
        for x in (4,19):
            l(x,9,x+8,11,(75,73,84),1)
            r(x,12,9,5,(232,232,224));r(x+3,12,4,5,eye);r(x+4,12,1,5,(18,52,40));r(x+3,12,1,1,(229,255,240))
            l(x,11,x+8,11,(64,62,73),1);l(x,17,x+8,17,tint(-26),1)
        r(12,25,8,1,lip);r(14,26,5,1,tint(-13))
        for x in range(32):
            depth=3+int(abs(x-16)*.15)
            r(x,0,1,depth,tuple(min(255,v+(x%5)*4) for v in hair))
    r(0,7,2,17,hair);r(30,7,2,17,hair)
for name,skin,hair,eye,lip,cloth,trim in [
 ('waifu',(238,189,178),(70,36,64),(136,61,150),(172,29,69),(91,34,72),(238,150,182)),
 ('glamour_ogre',(134,170,96),(39,48,34),(199,137,36),(163,29,77),(73,34,48),(222,177,79)),
 ('slime_lady',(109,207,177),(27,113,108),(117,55,170),(190,33,108),(37,88,113),(232,150,210))]:
    p,q=up(name);face(q,skin,hair,eye,lip,'anime')
    uv(q,96,54,20,26,hair);uv(q,108,0,16,13,hair)
    for x in range(96*4,116*4,5):line(q,x,54*4,x+2,79*4,tuple(min(255,v+28) for v in hair),1)
    uv(q,0,108,20,12,cloth);uv(q,88,80,16,5,trim)
    # richer tailoring, front panels with dark seams and fine gold/pink edging
    for x,y,w,h in [(32,64,24,12),(56,64,28,16),(0,82,38,14)]:
        uv(q,x,y,w,h,cloth)
        for k in range(0,w*4,7):
            shade=tuple(min(255,v+(k%14)*2) for v in cloth)
            line(q,x*4+k,y*4,x*4+k,(y+h)*4-1,shade,1)
        rect(q,x*4,(y+h)*4-3,w*4,2,trim)
    save(p,q)
p,q=up('one_winged_angel');face(q,(218,210,207),(188,194,210),(50,160,115),(112,78,90),'boss')
for x,y,w,h in [(64,0,40,13),(64,14,20,30),(92,0,14,28),(108,0,16,12)]:
    uv(q,x,y,w,h,(180,186,202))
    for k in range(0,w*4,5):
        col=(224,229,239) if k%10==0 else (142,151,174)
        line(q,x*4+k,y*4,x*4+k,(y+h)*4-1,col,1)
uv(q,64,98,24,22,(120,130,148));uv(q,0,112,16,12,(54,58,70))
for x in range(64*4,88*4,6):line(q,x,98*4,x,119*4,(184,191,204),1)
# Coat front: black leather, opening and crossing straps, silver buckle.
uv(q,20,20,8,12,(29,30,40));rect(q,22*4,20*4,16,35,(181,158,153))
line(q,20*4,20*4,27*4,28*4,(23,23,31),5);line(q,27*4,20*4,21*4,28*4,(23,23,31),5)
rect(q,23*4,27*4,8,5,(159,163,177));rect(q,24*4,27*4+1,4,3,(41,42,51))
save(p,q)
# Papi: trimmed beard and moustache, with individual hair pixels.
p,q=up('papi')
for y in range(22,32):
    for x in range(2,30):
        if y>=27 or x<6 or x>25 or (y in (22,23) and 9<=x<=22):
            if 12<=x<=19 and 24<=y<=26:continue
            v=(x*13+y*7)%18;rect(q,32+x,32+y,1,1,(65+v,45+v,32+v))
save(p,q)
# Gabumon custom atlas: cream fur with blue irregular stripes, yellow reptile
# snout and chest, red expressive eyes, ivory claws and horn.
rng=random.Random(982)
q=[[(220,219,203,255) for _ in range(512)] for _ in range(512)]
def fur(u,v,w,h):
    for y in range(v*4,(v+h)*4):
        for x in range(u*4,(u+w)*4):
            stripe=((y+(x//7)%7)//11)%4==1
            c=(47,83,161) if stripe else (224,225,212)
            d=rng.randint(-5,5);q[y][x]=(*[max(0,min(255,t+d)) for t in c],255)
for u,v,w,h in [(0,0,28,15),(48,0,34,10),(0,20,34,15),(36,20,38,10),(80,0,32,10),(72,20,24,10),(0,60,19,11),(20,60,20,10),(40,60,20,9),(60,60,24,10),(0,84,24,12),(24,84,24,10)]:fur(u,v,w,h)
uv(q,32,0,16,12,(244,199,91));uv(q,0,40,23,9,(235,187,74));uv(q,24,40,10,5,(106,61,41));uv(q,40,40,16,8,(225,171,60));uv(q,56,40,8,6,(246,230,192));uv(q,96,0,20,26,(235,220,166));uv(q,80,60,9,6,(246,236,207))
# head front UV = (7,27) width 9 height 7. yellow face beneath the pelt.
uv(q,7,27,9,7,(237,196,93))
for x in (31,49):
    rect(q,x,113,11,10,(62,39,32));rect(q,x+1,114,9,7,(251,242,222));rect(q,x+3,115,5,6,(171,40,48));rect(q,x+4,115,2,4,(42,27,34));rect(q,x+3,115,1,2,(255,255,242))
# dark blue triangular pelt edges on front.
for y in range(108,136):
    rect(q,28,y,max(1,4-(y-108)//9),1,(42,76,148));rect(q,60,y,4,1,(42,76,148))
# Belly blue emblem, claws and shaded nose.
for y in range(9,25):rect(q,32*4+9+(y%3),y,10,1,(49,87,161))
save(assets/'gabumon.png',q)
print('Noctis 0.9.8: creative spells, Elvis lifetime, redesigned character assets')
