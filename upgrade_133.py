"""1.3.3: Batman, sarcastic billionaire NPC and daily gifts."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<BatmanGuest>> BATMAN=ENTITIES.register("batman",()->EntityType.Builder.<BatmanGuest>of(BatmanGuest::new,MobCategory.CREATURE).sized(.75f,2.05f).clientTrackingRange(10).build(ID+":batman"));
    public static final RegistryObject<Item> BATMAN_EGG=ITEMS.register("batman_spawn_egg",()->new ForgeSpawnEggItem(BATMAN,0x252630,0xe4bf4a,new Item.Properties()));
    '''+a)
a='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());';edit('Noctis.java',a,'e.put(BATMAN.get(),BatmanGuest.attributes().build());'+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(BATMAN_EGG.get());')
(java/'BatmanGuest.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
public class BatmanGuest extends PathfinderMob{
    int speech,gesture;
    static final String[] GIFTS={"Tieni, pezzente. Comprati un'armatura decente.","Ho visto scheletri con un patrimonio superiore al tuo.","Prendi questi soldi. Il tuo inventario mi deprime.","Il mio maggiordomo guadagna piu' di te.","Non ringraziarmi. Investi in qualcosa che non sia terra."};
    static final String[] LINES={"Sono Batman, non la tua banca personale.","Ancora qui? Persino il Joker ha un lavoro.","Con quella casa non spaventeresti nemmeno un pollo."};
    public BatmanGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,100).add(Attributes.ARMOR,12).add(Attributes.MOVEMENT_SPEED,.31).add(Attributes.KNOCKBACK_RESISTANCE,.5);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.8));}
    void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal("Batman: "+s));}
    boolean give(ServerPlayer p,ServerLevel l){
        var data=Noctis.data(p);long now=l.getServer().overworld().getGameTime();
        if(data.contains("BatmanGiftNext")&&data.getLong("BatmanGiftNext")>now)return false;
        data.putLong("BatmanGiftNext",now+24000);
        ItemStack[] gifts={new ItemStack(Items.EMERALD,4+random.nextInt(5)),new ItemStack(Items.GOLD_INGOT,2+random.nextInt(4))};
        for(ItemStack s:gifts)if(!p.getInventory().add(s))p.drop(s,false);
        speech=160;l.broadcastEntityEvent(this,(byte)111);say(l,GIFTS[random.nextInt(GIFTS.length)]);
        l.sendParticles(ParticleTypes.HAPPY_VILLAGER,p.getX(),p.getY()+1,p.getZ(),9,.4,.5,.4,.02);
        playSound(SoundEvents.EXPERIENCE_ORB_PICKUP,.7f,.8f);return true;
    }
    @Override public void tick(){super.tick();if(speech>0)speech--;if(gesture>0)gesture--;
        if(level() instanceof ServerLevel l&&speech==0&&!l.isDay()&&tickCount%40==0){
            Player p=l.getNearestPlayer(this,5);if(p instanceof ServerPlayer sp&&!sp.isSpectator()&&!sp.isCreative()&&hasLineOfSight(sp))give(sp,l);
        }
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){
        if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;
        if(level() instanceof ServerLevel l&&p instanceof ServerPlayer sp&&speech==0){if(!give(sp,l)){speech=100;say(l,LINES[random.nextInt(LINES.length)]);}}
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    @Override public void handleEntityEvent(byte id){if(id==111){gesture=24;return;}super.handleEntityEvent(id);}
    public float giving(){return gesture<=0?0:(float)Math.sin(gesture*Math.PI/24);}
}''',encoding='utf-8')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!l.isDay()&&p.getRandom().nextInt(18)==0&&l.getEntitiesOfClass(BatmanGuest.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos q=Eclipse.spot(p,10,24);if(q!=null){BatmanGuest b=Noctis.BATMAN.get().create(l);if(b!=null){b.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(b))l.addFreshEntity(b);}}
        }''')
# Individual UV islands for a sculpted dark armored suit, pointed ears and cape panels.
N=128;S=8;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,m):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N,(m,v,hh)
    for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,m,f))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(a))+'f' for a in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):
    lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(a))+'f' for a in (*pos,*rot))+'));')
part('b','r','body',(0,0,0),(0,0,0),[(-4.8,0,-2.5,9,7,5,'chest'),(-3.7,7,-2.2,7,4,4,'armor'),(-4,10,-2.7,8,2,5,'gold')])
part('h','r','head',(0,-1,0),(0,0,0),[(-3.8,-7.5,-3.7,7,8,7,'mask')])
for i,s in enumerate((-1,1)):
    part('ear'+str(i),'h','ear'+str(i),(s*2.9,-7,0),(0,0,s*.12),[(-.7,-4,-1,1,4,2,'black')])
    part('arm'+str(i),'r','arm'+str(i),(s*5.3,0,0),(0,0,-s*.12),[(-2,-1,-2,4,5,4,'armor'),(-2,4,-2,4,5,4,'black'),(-1.5,9,-1.5,3,2,3,'black')])
    for j in range(3):part(f'fin{i}{j}','arm'+str(i),f'fin{j}',(s*2,5+j*1.4,1),(0,0,s*.25),[(-.5,0,0,1,2,2,'black')])
    part('leg'+str(i),'r','leg'+str(i),(s*2.1,12,0),(0,0,0),[(-2,0,-2,4,6,4,'armor'),(-2,6,-2,4,6,4,'black'),(-2,11,-3,4,1,5,'black')])
    part('pouch'+str(i),'b','pouch'+str(i),(s*3,10,-3),(0,0,0),[(-1,0,-.5,2,2,1,'gold')])
for i in range(5):
    part('cape'+str(i),'b','cape'+str(i),(-4+i*2,-.2,2.8),(.10,0,(i-2)*.05),[(-1,0,0,3,20+(i%2)*2,1,'cape')])
(java/'BatmanClient.java').write_text('''package it.noctis.magic;
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
public class BatmanClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"batman"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,BatmanClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.BATMAN.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,128,128);}
    static class Model extends EntityModel<BatmanGuest>{
        final ModelPart r,h,b;Model(ModelPart r){this.r=r;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(BatmanGuest e,float limb,float amount,float age,float yaw,float pitch){
            float a=e.giving();h.yRot=yaw*.017f;h.xRot=pitch*.017f-a*.1f;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;r.getChild("leg"+i).xRot=w*.65f;r.getChild("arm"+i).xRot=-w*.65f-(i==1?a*1.25f:0);}
            for(int i=0;i<5;i++)b.getChild("cape"+i).xRot=.1f+amount*.48f+(float)Math.sin(age*.15+i*.55)*.06f;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<BatmanGuest,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.45f);}@Override public ResourceLocation getTextureLocation(BatmanGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/batman.png");}}
}''',encoding='utf-8')
palette={'chest':(73,76,84),'armor':(66,70,80),'black':(27,29,37),'mask':(32,34,43),'gold':(185,149,63),'cape':(23,25,34)}
pix=bytearray(W*W*4)
for x,y,w,h,m,f in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);base=palette[m];g=.73+.26*math.sin(u*math.pi)+.04*math.cos(v*9)
            if m=='cape':g=.65+.32*math.sin(u*math.pi)**2
            c=tuple(int(a*g) for a in base)
            if m in ('armor','chest') and (min(u,1-u)<.04 or abs(v-.77)<.022):c=(37,39,47)
            if m=='mask' and f=='front':
                if v>.66 and .20<u<.80:c=(193,148,121)
                if .4<u<.63 and abs(v-.86)<.023:c=(77,48,46)
                for ex in (.27,.73):
                    dx=(u-ex)/.16;dy=(v-.43+(u-.5)*.06)/.07
                    if abs(dx)<1 and abs(dy)<1-abs(dx)*.6:c=(235,242,247)
            if m=='chest' and f=='front':
                dx=(u-.5)/.36;dy=(v-.38)/.24
                if dx*dx+dy*dy<1:
                    c=(197,159,67)
                    if abs(dy)<.25+.16*abs(dx) or (abs(dx)<.16 and -.62<dy<.55) or (.2<abs(dx)<.8 and abs(dy+.15)<.25):c=(25,26,33)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,a)) for a in c],255))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
(assets/'textures/entity/batman.png').write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))))+ch(b'IEND',b''))
(assets/'models/item/batman_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.batman']='Batman';d['item.noctismagic.batman_spawn_egg']='Uovo generatore: Batman' if lang=='it_it' else 'Batman Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Batman: sarcastic billionaire, daily gifts, custom suit and animated cape')
