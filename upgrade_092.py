"""0.9.2: moonlit Umbreon and persistent Vincent territory spacing."""
from pathlib import Path
import sys,struct,zlib,random
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
edit('VincentEncounter.java',[
('Noctis.data(p).getBoolean("metVincent")||','!VincentTerritory.available(l,p.blockPosition(),null)||'),
('if(l.noCollision(v)&&l.addFreshEntity(v)){Noctis.data(p).putBoolean("metVincent",true);return;}','if(VincentTerritory.available(l,q,null)&&l.noCollision(v)&&l.addFreshEntity(v))return;')
])
edit('Vincent.java',[
('if(!level().isClientSide&&tickCount%120==0&&getHealth()<getMaxHealth())heal(2);','if(level() instanceof ServerLevel l){if(tickCount%40==0)VincentTerritory.track(this);if(tickCount%120==0&&getHealth()<getMaxHealth())heal(2);}')
])
write('VincentTerritory.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class VincentTerritory extends SavedData {
    private final Map<UUID,BlockPos> residents=new HashMap<>();
    static VincentTerritory load(CompoundTag tag){
        VincentTerritory d=new VincentTerritory();ListTag list=tag.getList("Residents",10);
        for(int i=0;i<list.size();i++){CompoundTag n=list.getCompound(i);if(n.hasUUID("Id"))d.residents.put(n.getUUID("Id"),BlockPos.of(n.getLong("Pos")));}return d;
    }
    @Override public CompoundTag save(CompoundTag tag){ListTag list=new ListTag();for(var e:residents.entrySet()){CompoundTag n=new CompoundTag();n.putUUID("Id",e.getKey());n.putLong("Pos",e.getValue().asLong());list.add(n);}tag.put("Residents",list);return tag;}
    static VincentTerritory get(ServerLevel l){return l.getDataStorage().computeIfAbsent(VincentTerritory::load,VincentTerritory::new,"noctis_vincent_territories");}
    static boolean available(ServerLevel l,BlockPos p,UUID except){
        for(var e:get(l).residents.entrySet()){if(e.getKey().equals(except))continue;long dx=(long)e.getValue().getX()-p.getX(),dz=(long)e.getValue().getZ()-p.getZ();if(dx*dx+dz*dz<1000000L)return false;}return true;
    }
    static void track(Vincent v){if(!(v.level() instanceof ServerLevel l))return;VincentTerritory d=get(l);BlockPos pos=v.blockPosition();BlockPos previous=d.residents.get(v.getUUID());if(previous==null||previous.distSqr(pos)>4){d.residents.put(v.getUUID(),pos);d.setDirty();}}
    @SubscribeEvent public static void join(EntityJoinLevelEvent e){
        if(!(e.getLevel() instanceof ServerLevel l)||!(e.getEntity() instanceof Vincent v))return;
        if(!e.loadedFromDisk()&&!available(l,v.blockPosition(),v.getUUID())){e.setCanceled(true);return;}track(v);
    }
    @SubscribeEvent public static void death(LivingDeathEvent e){if(e.getEntity() instanceof Vincent v&&v.level() instanceof ServerLevel l){VincentTerritory d=get(l);d.residents.remove(v.getUUID());d.setDirty();}}
}''')
edit('Client.java',[
('e.registerLayerDefinition(UMBREON,()->ShapeModel.mesh(0));','e.registerLayerDefinition(UMBREON, UmbreonRenderer::mesh);e.registerLayerDefinition(SHADOW_LAYER,()->ShapeModel.mesh(0));'),
('static ModelLayerLocation layer(String s)','static final ModelLayerLocation SHADOW_LAYER=layer("shadow_original");\n    static ModelLayerLocation layer(String s)'),
('c->new FamiliarRenderer(c,UMBREON,"umbreon")','UmbreonRenderer::new'),
('c->new FamiliarRenderer(c,UMBREON,"shadow")','c->new FamiliarRenderer(c,SHADOW_LAYER,"shadow")')
])
edit('Familiar.java',[
('private int lifetime=-1;','private int lifetime=-1;private int moonAttack=0;'),
('if(hit&&octopus()','if(hit&&getType()==Noctis.UMBREON.get()&&!level().isClientSide)level().broadcastEntityEvent(this,(byte)74);if(hit&&octopus()'),
('public void tick(){super.tick();','public void tick(){super.tick();if(moonAttack>0)moonAttack--;'),
('public void setLifetime(int n)','''@Override public void handleEntityEvent(byte id){if(id==74){moonAttack=12;return;}super.handleEntityEvent(id);}
    public float moonAttackPose(float partial){return moonAttack<=0?0:(float)Math.sin(Math.PI*(1-Math.max(0,moonAttack-partial)/12f));}
    public void setLifetime(int n)''')
])
write('UmbreonRenderer.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
public class UmbreonRenderer extends MobRenderer<Familiar,UmbreonRenderer.Model>{
    static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/umbreon.png");
    static final ResourceLocation GLOW=new ResourceLocation(Noctis.ID,"textures/entity/umbreon_glow.png");
    public UmbreonRenderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(Client.UMBREON)),.32f);addLayer(new Rings(this));}
    @Override public ResourceLocation getTextureLocation(Familiar e){return TEX;}
    static LayerDefinition mesh(){
        MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
        r.addOrReplaceChild("body",CubeListBuilder.create().texOffs(0,0).addBox(-3,-4,-5,6,6,10),PartPose.offset(0,18,0));
        PartDefinition h=r.addOrReplaceChild("head",CubeListBuilder.create().texOffs(0,24).addBox(-4,-5,-5,8,7,6).texOffs(64,24).addBox(-2,-1,-6,4,3,2),PartPose.offset(0,15,-5));
        for(int i=0;i<2;i++){int s=i==0?-1:1;PartDefinition ear=h.addOrReplaceChild("ear"+i,CubeListBuilder.create().texOffs(36+i*12,24).addBox(-1,-7,-1,2,7,2),PartPose.offsetAndRotation(s*2.5f,-4,-1,0,0,s*.12f));}
        r.addOrReplaceChild("tail",CubeListBuilder.create().texOffs(40,0).addBox(-1,-1.5f,0,2,3,8).texOffs(64,0).addBox(-.7f,-1,7,1.4f,2,3),PartPose.offsetAndRotation(0,17,4,-.65f,0,0));
        for(int i=0;i<4;i++)r.addOrReplaceChild("leg"+i,CubeListBuilder.create().texOffs(i*10,48).addBox(-1,0,-1,2,5,2).texOffs(48+i*10,48).addBox(-1.2f,4,-1.8f,2.4f,1,3),PartPose.offset(i%2==0?-2:2,19,i<2?-3:3));
        return LayerDefinition.create(m,128,64);
    }
    static class Model extends EntityModel<Familiar>{
        final ModelPart root,body,head,tail;final ModelPart[] ears=new ModelPart[2],legs=new ModelPart[4];
        Model(ModelPart r){root=r;body=r.getChild("body");head=r.getChild("head");tail=r.getChild("tail");for(int i=0;i<2;i++)ears[i]=head.getChild("ear"+i);for(int i=0;i<4;i++)legs[i]=r.getChild("leg"+i);}
        @Override public void setupAnim(Familiar e,float limb,float amount,float age,float yaw,float pitch){
            float attack=e.moonAttackPose(age-e.tickCount);
            boolean sit=e.isInSittingPose();boolean air=!e.onGround()&&!sit;
            float breath=(float)Math.sin(age*.13)*.10f;
            body.y=(sit?20:18)+breath;body.xRot=sit?-.27f:air?-.10f:attack*.12f;
            head.y=sit?16:15;head.z=-5-attack*1.1f;head.xRot=pitch*.01745f-attack*.20f+(amount<.05f?(float)Math.sin(age*.09)*.035f:0);head.yRot=yaw*.01745f;
            tail.y=sit?20:17;tail.xRot=sit?-.15f:air?-.95f:-.65f;tail.yRot=(float)Math.sin(age*(amount>.25?.25:.11))*(sit?.18f:.32f);
            for(int i=0;i<2;i++){int s=i==0?-1:1;float twitch=(float)Math.pow(Math.max(0,Math.sin(age*.075+i*2)),20)*.35f;ears[i].zRot=s*(.12f+twitch);ears[i].xRot=attack*.45f+(air?.25f:0)+(float)Math.sin(age*.16+i)*.045f;}
            for(int i=0;i<4;i++){legs[i].y=sit&&i>=2?21:19;legs[i].xRot=sit?(i>=2?-1.25f:.06f):air?(i<2?-.55f:.5f):(float)Math.cos(limb*.6662+(i%3==0?0:Math.PI))*amount*1.15f;if(i<2&&!sit)legs[i].xRot-=attack*.35f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    }
    static class Rings extends RenderLayer<Familiar,Model>{
        Rings(UmbreonRenderer r){super(r);}
        @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,Familiar e,float limb,float amount,float partial,float age,float yaw,float pitch){
            if(e.isInvisible()||e.level().dimension()!=Level.OVERWORLD)return;
            long time=e.level().getDayTime()%24000L;if(time<12500||time>23500)return;
            float pulse=.86f+(float)Math.sin(age*.11f)*.14f;
            getParentModel().renderToBuffer(pose,buffers.getBuffer(RenderType.eyes(GLOW)),0xF000F0,OverlayTexture.NO_OVERLAY,pulse,pulse,pulse,1);
        }
    }
}''')
# Base and emissive mask use exactly the same UVs. Only yellow markings emit light.
rng=random.Random(92);w,h=128,64
base=[[(25,26,37,255) for x in range(w)] for y in range(h)]
glow=[[(0,0,0,0) for x in range(w)] for y in range(h)]
def rect(x,y,ww,hh,col,noise=0):
    for yy in range(y,y+hh):
        for xx in range(x,x+ww):
            d=rng.randint(-noise,noise);base[yy][xx]=tuple(max(0,min(255,v+d)) for v in col)+(255,)
def mark(x,y,col=(219,177,48)):
    base[y][x]=(*col,255);glow[y][x]=(255,224,85,255)
def ring(x,y,ww,hh):
    for yy in range(hh):
        for xx in range(ww):
            # Rounded pixel ring, with the dark interior retained.
            if (yy in (0,hh-1) and 0<xx<ww-1) or (xx in (0,ww-1) and 0<yy<hh-1):mark(x+xx,y+yy)
rect(0,0,32,16,(30,31,44),6)
# two lateral body faces: 10x6 each.
ring(2,10,6,5);ring(18,10,6,5)
rect(0,24,28,13,(29,30,43),5)
# front head face starts at (6,30)
ring(8,30,4,3)
for x in (7,12):
    rect(x,34,1,2,(201,36,53));rect(x,34,1,1,(250,91,93))
rect(9,35,2,1,(13,14,20))
rect(64,24,12,7,(36,36,49),5)
rect(66,26,4,1,(13,14,20))
# ear bands on all four side faces
for u in (36,48):
    rect(u,24,8,9,(27,29,41),5)
    for x in range(u,u+8):
        for y in (28,29):mark(x,y)
# tail band across both sides, top and bottom
rect(40,0,20,11,(27,29,43),6)
for x in (43,44,53,54):
    for y in range(8,11):mark(x,y)
for y in (3,4):
    for x in list(range(48,50))+list(range(50,52)):mark(x,y)
rect(64,0,12,8,(26,28,40),5)
for i in range(4):
    u=i*10;rect(u,48,8,7,(30,31,43),5)
    for x in range(u,u+8):mark(x,51)
    rect(48+i*10,48,10,5,(22,24,34),4)
def png(path,pix):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for p in row for v in p) for row in pix)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
png(assets/'textures/entity/umbreon.png',base)
png(assets/'textures/entity/umbreon_glow.png',glow)
print('Noctis 0.9.2: Vincent territories and emissive animated Umbreon applied')
