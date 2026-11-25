"""1.3.5: Phosphophyllite and Cinnabar, luminous crystalline hair and colored dialogue."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
ids=['phosphophyllite','cinnabar'];labels=['Phosphophyllite','Cinnabar']
decl=''
for n,c,d in zip(ids,['0x33d8b6','0xae183b'],['0xc7fff4','0xff8495']):
    r=n.upper();decl+=f'public static final RegistryObject<EntityType<GemGuest>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<GemGuest>of(GemGuest::new,MobCategory.CREATURE).sized(.6f,1.85f).clientTrackingRange(10).build(ID+":{n}"));\n    public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{c},{d},new Item.Properties()));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG=';edit('Noctis.java',a,decl+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,''.join(f'e.put({n.upper()}.get(),GemGuest.attributes().build());' for n in ids)+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+''.join(f'e.accept({n.upper()}_EGG.get());' for n in ids))
(java/'GemGuest.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
public class GemGuest extends PathfinderMob{
    UUID partner;int conversation=80,answer=0,pose=0;
    public GemGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public boolean phos(){return getType()==Noctis.PHOSPHOPHYLLITE.get();}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,65).add(Attributes.ARMOR,7).add(Attributes.MOVEMENT_SPEED,.28);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.7){@Override public boolean canUse(){return phos()&&answer==0&&conversation>40&&together()&&super.canUse();}@Override public boolean canContinueToUse(){return phos()&&answer==0&&conversation>40&&together()&&super.canContinueToUse();}});}
    GemGuest companion(ServerLevel l){return partner!=null&&l.getEntity(partner) instanceof GemGuest q&&q.isAlive()?q:null;}
    boolean together(){return level() instanceof ServerLevel l&&companion(l)!=null&&distanceTo(companion(l))<5;}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s).withStyle(phos()?ChatFormatting.GREEN:ChatFormatting.RED));}
    void pair(ServerLevel l){
        if(partner!=null)return;
        for(GemGuest q:l.getEntitiesOfClass(GemGuest.class,getBoundingBox().inflate(12),v->v!=this&&v.phos()!=phos()&&v.partner==null&&v.isAlive())){partner=q.getUUID();q.partner=getUUID();return;}
        for(int i=0;i<8;i++){double a=i*Math.PI/4;BlockPos p=BlockPos.containing(getX()+Math.cos(a)*2,getY(),getZ()+Math.sin(a)*2);
            if(!l.hasChunkAt(p)||!l.isEmptyBlock(p)||!l.isEmptyBlock(p.above())||!l.getBlockState(p.below()).isFaceSturdy(l,p.below(),Direction.UP))continue;
            GemGuest q=(phos()?Noctis.CINNABAR.get():Noctis.PHOSPHOPHYLLITE.get()).create(l);if(q==null)return;
            q.moveTo(p.getX()+.5,p.getY(),p.getZ()+.5);if(l.noCollision(q)){q.partner=getUUID();if(l.addFreshEntity(q)){partner=q.getUUID();setPersistenceRequired();q.setPersistenceRequired();return;}}
        }
    }
    void ask(ServerLevel l,GemGuest q){
        if(!phos()||conversation>0||q==null||distanceTo(q)>6)return;
        conversation=400;getNavigation().stop();q.getNavigation().stop();
        getLookControl().setLookAt(q,30,30);q.getLookControl().setLookAt(this,30,30);
        say(l,"Cinnabar, quando mi trovi un lavoro?");l.broadcastEntityEvent(this,(byte)113);q.answer=45;
    }
    @Override public void tick(){
        super.tick();if(pose>0)pose--;if(conversation>0)conversation--;
        if(!(level() instanceof ServerLevel l))return;
        if(tickCount%30==0&&l.getNearestPlayer(this,20)!=null){
            l.sendParticles(ParticleTypes.END_ROD,getX()+(random.nextDouble()-.5)*.55,getY()+1.65+random.nextDouble()*.25,getZ()+(random.nextDouble()-.5)*.55,1,0,0,0,.005);
        }
        if(partner==null&&tickCount%20==0)pair(l);
        GemGuest q=companion(l);
        if(q==null){getNavigation().stop();answer=0;return;}
        double d=distanceTo(q);
        if(answer>0){
            getNavigation().stop();getLookControl().setLookAt(q,30,30);
            if(--answer==0&&d<7){say(l,"Prima devi trovare te stesso, Phosphophyllite.");l.broadcastEntityEvent(this,(byte)113);}
            return;
        }
        if(!phos()){if(d>3)getNavigation().moveTo(q,1.1);else getNavigation().stop();}
        else if(d>5)getNavigation().stop();
        if(phos()&&conversation==0&&tickCount%20==0&&l.getNearestPlayer(this,12)!=null)ask(l,q);
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l){GemGuest q=companion(l);if(phos())ask(l,q);else if(q!=null)q.ask(l,this);}
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==113){pose=35;return;}super.handleEntityEvent(id);}
    public float gesture(){return pose<=0?0:(float)Math.sin(pose*Math.PI/35);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(partner!=null)t.putUUID("Partner",partner);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);partner=t.hasUUID("Partner")?t.getUUID("Partner"):null;}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(p.getRandom().nextInt(25)==0&&l.getEntitiesOfClass(GemGuest.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){GemGuest g=Noctis.PHOSPHOPHYLLITE.get().create(l);if(g!=null){g.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(g))l.addFreshEntity(g);}}
        }''')
# Custom crystal locks, angled facet geometry and separate emissive hair parts.
N=256;S=4;W=N*S;meshes=[]
for k,n in enumerate(ids):
    cx=cy=rh=0;islands=[];lines=[];hairparts=[]
    def cube(x,y,z,w,h,d,m):
        global cx,cy,rh
        ww=2*(w+d);hh=h+d
        if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
        u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
        for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,m,f))
        return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
    def part(var,parent,name,pos,rot,boxes):
        lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
    part('b','r','body',(0,0,0),(0,0,0),[(-3.5,0,-2,7,8,4,'cloth'),(-3,8,-2,6,3,4,'cloth'),(-3.5,10,-2.2,7,1,4,'belt'),(-1.5,0,-2.4,3,5,1,'white'),(-.5,1,-3,1,6,1,'tie')])
    part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face')])
    part('cap','h','cap',(0,0,0),(0,0,0),[(-4,-8,-3.9,8,2,8,'gem'),(-3,-9,-3,6,2,6,'gem')]);hairparts.append('cap')
    for i in range(7):
        part('bang'+str(i),'h','bang'+str(i),(-3+i,-7.5,-3.5),(0,0,(i-3)*(.24 if k==0 else .15)),[(-.9,0,-.7,2,4+i%3,2,'gem')]);hairparts.append('bang'+str(i))
        part('back'+str(i),'h','back'+str(i),(-3+i,-6,3),(0,0,(i-3)*.08),[(-.8,0,-.5,2,6+i%3+(7 if k else 0),3,'gem')]);hairparts.append('back'+str(i))
        part('tip'+str(i),'back'+str(i),'tip',(0,5+i%3+(7 if k else 0),0),(0,0,.23 if i%2 else -.23),[(-.6,0,-.6,1,3,2,'gem')])
    for i,s in enumerate((-1,1)):
        part('lock'+str(i),'h','lock'+str(i),(s*3.5,-6,-1),(0,0,s*.19),[(-1,0,-1,2,8+(5 if k else 0),3,'gem')]);hairparts.append('lock'+str(i))
        part('arm'+str(i),'r','arm'+str(i),(s*4.4,0,0),(0,0,-s*.09),[(-2,-1,-2,4,4,4,'cloth'),(-1.25,3,-1.25,2,8,2,'skin')])
        part('leg'+str(i),'r','leg'+str(i),(s*1.9,11,0),(0,0,0),[(-1.8,0,-1.8,3,4,4,'cloth'),(-1.2,4,-1.2,2,7,2,'skin'),(-1.5,11,-2,3,2,4,'cloth')])
    meshes.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,256,256);}')
    pix=bytearray(W*W*4)
    for x,y,w,h,m,f in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S)
                if m=='gem':
                    # Angular triangular facets and sharp white specular highlights.
                    a=int(u*4);b=int(v*5);z=(a*7+b*13+(1 if (u*4)%1+(v*5)%1>1 else 0))%7
                    shades=[.43,.62,.78,1,.86,.55,.95]
                    g=shades[z]*(.87+.13*math.sin(u*math.pi))
                    base=(49,232,199) if k==0 else (240,38,75)
                    c=tuple(int(t*g) for t in base)
                    if abs(u-.20-v*.32)<.033 or abs(v-.18-u*.18)<.018:c=(215,255,249) if k==0 else (255,209,209)
                else:
                    base={'cloth':(25,29,39),'white':(239,244,239),'tie':(20,23,31),'belt':(190,202,205),'face':(247,240,223),'skin':(245,239,222)}[m]
                    g=.88+.12*math.sin(u*math.pi);c=tuple(int(t*g) for t in base)
                    if m=='face' and f=='front':
                        for ex in (.26,.74):
                            dx=(u-ex)/.19;dy=(v-.48)/.17;d=dx*dx+dy*dy
                            if d<1:c=(46,69,66) if k==0 else (101,35,48)
                            if d<.8:c=(250,252,247)
                            if abs(dx)<.47 and abs(dy)<.85:c=(46,174,147) if k==0 else (207,39,65)
                            if abs(dx)<.18 and abs(dy)<.7:c=(23,47,47) if k==0 else (65,16,28)
                            if (dx+.18)**2+(dy+.27)**2<.10:c=(255,255,255)
                        if .43<u<.60 and abs(v-.79)<.018:c=(176,127,119)
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*c,255))
    def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    (assets/'textures/entity'/f'{n}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))))+ch(b'IEND',b''))
    (assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
(java/'GemGuestClient.java').write_text('''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class GemGuestClient{
    static final String[] N={"phosphophyllite","cinnabar"};
    static final ModelLayerLocation[] L={new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[0]),"main"),new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[1]),"main")};
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],GemGuestClient::mesh0);e.registerLayerDefinition(L[1],GemGuestClient::mesh1);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.PHOSPHOPHYLLITE.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.CINNABAR.get(),c->new Renderer(c,1));}
'''+ '\n'.join(meshes)+'''
    static class Model extends EntityModel<GemGuest>{
        final ModelPart r,h;final ModelPart[] hair;final int k;
        Model(ModelPart r,int k){this.r=r;this.k=k;h=r.getChild("head");hair=new ModelPart[17];hair[0]=h.getChild("cap");for(int i=0;i<7;i++){hair[1+i]=h.getChild("bang"+i);hair[8+i]=h.getChild("back"+i);}hair[15]=h.getChild("lock0");hair[16]=h.getChild("lock1");}
        @Override public void setupAnim(GemGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.gesture();h.yRot=yaw*.017f;h.xRot=pitch*.014f;h.zRot=(k==0?.12f:-.05f)*a;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;r.getChild("leg"+i).xRot=w*.65f;r.getChild("arm"+i).xRot=-w*.65f-(i==1?a*(k==0?1.1f:.4f):0);h.getChild("lock"+i).xRot=amount*.16f+(float)Math.sin(age*.10+i)*.035f;}
            for(int i=0;i<7;i++){ModelPart q=h.getChild("back"+i);q.xRot=amount*.2f+(float)Math.sin(age*.12+i*.4)*.05f;q.getChild("tip").xRot=(float)Math.sin(age*.12+i)*.06f;}
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float rr,float g,float bb,float a){
            // Draw normal body, then hair only at full light (without double drawing).
            for(ModelPart q:hair)q.visible=false;
            r.render(p,v,light,overlay,rr,g,bb,a);
            p.pushPose();r.translateAndRotate(p);h.translateAndRotate(p);
            for(ModelPart q:hair){q.visible=true;q.render(p,v,15728880,overlay,rr,g,bb,a);}
            p.popPose();
        }
    }
    static class Renderer extends MobRenderer<GemGuest,Model>{final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k]),k),.35f);this.k=k;}@Override public ResourceLocation getTextureLocation(GemGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}}
}''',encoding='utf-8')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for n,label in zip(ids,labels):d['entity.noctismagic.'+n]=label;d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Phosphophyllite and Cinnabar: paired guests, colored dialogue, luminous crystal hair')
