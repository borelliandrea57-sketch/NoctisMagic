"""Noctis Magic 0.8.2: repair opaque head overlays and redraw three NPC faces."""
from pathlib import Path
import sys, struct, zlib, random
root=Path(sys.argv[1])
java=root/'src/main/java/it/noctis/magic'
assets=root/'src/main/resources/assets/noctismagic/textures/entity'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing head fix anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
# HumanoidModel normally renders an inflated second head cube ("hat").
# The previous atlases have opaque pixels there. Remove that cube, retaining
# the named part for vanilla animation and leaving the custom hair geometry.
mesh='MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);'
for name in ['FallenClient.java','SoraClient.java','MiracleClient.java']:
    edit(name,[(mesh,mesh+'\n        m.getRoot().addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);')])
edit('FallenClient.java',[
('h.addOrReplaceChild("silver",CubeListBuilder.create().texOffs(64,0).addBox(-4.6f,-9,-4.5f,9.2f,3,9).texOffs(64,14).addBox(-4,-6,3,8,22,2),PartPose.ZERO);',
'''h.addOrReplaceChild("silver",CubeListBuilder.create().texOffs(64,0).addBox(-4.5f,-9,-4.5f,9,2,9).texOffs(64,14).addBox(-4,-7,3.1f,8,21,2),PartPose.ZERO);
        h.addOrReplaceChild("partedFringeL",CubeListBuilder.create().texOffs(108,0).addBox(-2,0,-.5f,3,3,1),PartPose.offsetAndRotation(-2.1f,-7.8f,-4.2f,0,0,.18f));
        h.addOrReplaceChild("partedFringeR",CubeListBuilder.create().texOffs(108,0).addBox(-1,0,-.5f,3,2,1),PartPose.offsetAndRotation(2.1f,-7.8f,-4.2f,0,0,-.18f));'''),
('PartPose.offsetAndRotation(s*4,-5,-1,0,0,s*.08f)','PartPose.offsetAndRotation(s*4.6f,-6,.1f,0,0,s*.055f)')])
edit('SoraClient.java',[
('h.addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.5f,-9,-4.5f,9,3,9).texOffs(64,15).addBox(-4,-7,2.6f,8,5,2),PartPose.ZERO);',
'''h.addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.5f,-9,-4.5f,9,2,9).texOffs(64,15).addBox(-4,-7,3.1f,8,5,2),PartPose.ZERO);
        h.addOrReplaceChild("fringe",CubeListBuilder.create().texOffs(108,0).addBox(-1,0,-.5f,2,3,1),PartPose.offsetAndRotation(-2,-8,-4.2f,0,0,-.3f));''')])
edit('MiracleClient.java',[
('h.addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.4f,-8.7f,-4.3f,8.8f,2.5f,8.6f).texOffs(64,14).addBox(-4,-7,3,8,12,2),PartPose.ZERO);',
'''h.addOrReplaceChild("hair",CubeListBuilder.create().texOffs(64,0).addBox(-4.5f,-9,-4.5f,9,2,9).texOffs(64,14).addBox(-4,-7,3.1f,8,12,2),PartPose.ZERO);'''),
('PartPose.offset(s*4,-6,1)','PartPose.offset(s*4.5f,-6,1.5f)'),
('h.addOrReplaceChild("beard",CubeListBuilder.create().texOffs(96,16).addBox(-3,-1.9f,-4.25f,6,3,1.4f),PartPose.ZERO);','h.addOrReplaceChild("beard",CubeListBuilder.create().texOffs(96,16).addBox(-2.5f,-1.2f,-4.35f,5,2.5f,1.0f),PartPose.ZERO);')])
# Face the recipient, not away from them, during the miracle.
edit('MiracleVisitor.java',[
('getLookControl().setLookAt(p,30,30);','''getLookControl().setLookAt(p,30,30);
            double dx=p.getX()-getX(),dz=p.getZ()-getZ();
            if(dx*dx+dz*dz>.04){float yaw=(float)(Math.atan2(dz,dx)*180/Math.PI)-90f;setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);}''')])
# Decode the existing generated RGBA PNGs (the original writer uses filter 0).
def load(p):
    data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    pos=8;compressed=b'';w=h=None
    while pos<len(data):
        n=struct.unpack('>I',data[pos:pos+4])[0];k=data[pos+4:pos+8];b=data[pos+8:pos+8+n];pos+=12+n
        if k==b'IHDR':
            w,h,depth,ctype,_,_,interlace=struct.unpack('>IIBBBBB',b);assert (depth,ctype,interlace)==(8,6,0)
        elif k==b'IDAT':compressed+=b
        elif k==b'IEND':break
    raw=zlib.decompress(compressed);stride=w*4+1
    assert len(raw)==h*stride and all(raw[y*stride]==0 for y in range(h))
    return w,h,[bytearray(raw[y*stride+1:(y+1)*stride]) for y in range(h)]
def save(p,w,h,pix):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(row) for row in pix)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
def paint(name,skin,hair,highlight,iris):
    p=assets/(name+'.png');w,h,pix=load(p);rng=random.Random(name+'-082')
    def pixel(x,y,c):
        if len(c)==3:c=(*c,255)
        pix[y][4*x:4*x+4]=bytes(c)
    def rect(x,y,ww,hh,c,noise=0):
        for yy in range(y,y+hh):
            for xx in range(x,x+ww):
                d=rng.randint(-noise,noise) if noise else 0
                q=tuple(max(0,min(255,v+d)) for v in c[:3])
                pixel(xx,yy,(*q,c[3] if len(c)==4 else 255))
    # Standard head UV: top (8,0), bottom (16,0), face (8,8),
    # sides (0,8)/(16,8), back (24,8). The separate hat uses (32,0).
    rect(0,0,32,16,skin,4)
    rect(32,0,32,16,(0,0,0,0))
    for x in (0,16):
        rect(x,8,8,8,skin,4)
        rect(x,8,8,2,hair,5);rect(x+5,10,3,5,hair,5)
        rect(x+2,11,2,3,tuple(max(0,v-18) for v in skin),2)
    rect(24,8,8,8,hair,6);rect(8,0,8,8,hair,6)
    rect(16,0,8,8,skin,3)
    # Deliberate, readable 8x8 Minecraft face. Dark brows, two separate
    # eyes with white sclera and colored pupils, nose, mouth and jaw.
    shade=tuple(max(0,v-20) for v in skin)
    lip=tuple(max(0,v-48) for v in skin)
    rect(8,8,8,8,skin)
    rect(8,8,8,1,hair);rect(8,9,1,2,hair);rect(15,9,1,2,hair)
    rect(9,10,2,1,hair);rect(13,10,2,1,hair)
    for x in (9,13):
        rect(x,11,2,1,(247,245,235));pixel(x+1 if x==9 else x,11,iris)
    pixel(12,12,shade);pixel(12,13,shade)
    rect(11,14,2,1,lip)
    pixel(8,13,shade);pixel(15,13,shade)
    rect(9,15,6,1,shade)
    if name=='one_winged_angel':
        pixel(9,9,highlight);pixel(14,9,highlight)
        pixel(10,10,(102,110,120));pixel(13,10,(102,110,120))
        pixel(10,11,(27,142,104));pixel(13,11,(27,142,104))
        rect(11,14,2,1,(119,78,89))
    elif name=='sora':
        pixel(9,9,hair);pixel(10,9,highlight);pixel(11,8,highlight)
        pixel(10,11,(28,105,205));pixel(13,11,(28,105,205))
        pixel(9,13,(skin[0],max(0,skin[1]-13),max(0,skin[2]-10)))
        pixel(14,13,(skin[0],max(0,skin[1]-13),max(0,skin[2]-10)))
        rect(11,14,2,1,(143,71,55))
    else:
        rect(9,14,6,2,hair,3);pixel(9,13,hair);pixel(14,13,hair)
        rect(11,13,2,1,(115,64,42));rect(11,14,2,1,(151,95,63))
    # Hair-only UV regions: do not overwrite clothing or sword UVs below.
    rect(64,0,44,13,hair,6)
    for x in range(65,106,3):rect(x,1,1,10,highlight,5)
    rect(64,14,20,23,hair,7)
    for x in range(65,84,3):rect(x,15,1,21,highlight,4)
    rect(92,0,16,15,hair,6)
    for x in range(93,108,3):rect(x,1,1,12,highlight,4)
    rect(108,0,12,8,hair,5);rect(111,1,1,5,highlight,4)
    if name=='jesus':
        rect(96,16,17,8,hair,5)
        for x in range(98,112,3):rect(x,17,1,5,highlight,4)
    save(p,w,h,pix)
    assert all(pix[y][4*x+3]==0 for y in range(16) for x in range(32,64))
paint('one_winged_angel',(223,211,202),(181,185,202),(238,239,246),(36,144,106))
paint('sora',(231,181,139),(105,62,34),(173,111,58),(37,113,220))
paint('jesus',(210,159,119),(91,54,32),(140,88,49),(62,42,29))
print('Noctis 0.8.2: all three head overlays removed and face UVs verified')
