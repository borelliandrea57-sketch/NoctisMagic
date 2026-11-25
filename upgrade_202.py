"""Kakyoin: a dedicated angular model with perpetual cherry trick."""
from pathlib import Path
import sys,math,json
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(file,a,b):
 p=java/file;s=p.read_text(encoding='utf-8');assert a in s,(file,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<EntityType<Kakyoin>> KAKYOIN=ENTITIES.register("kakyoin",()->EntityType.Builder.<Kakyoin>of(Kakyoin::new,MobCategory.CREATURE).sized(.76f,2.20f).clientTrackingRange(10).build(ID+":kakyoin"));
    public static final RegistryObject<Item> KAKYOIN_EGG=ITEMS.register("kakyoin_spawn_egg",()->new ForgeSpawnEggItem(KAKYOIN,0x235943,0xb14c36,new Item.Properties()));
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());','e.put(KAKYOIN.get(),Kakyoin.attributes().build());e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(KAKYOIN_EGG.get());')
(java/'Kakyoin.java').write_text('''package it.noctis.magic;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
public final class Kakyoin extends PathfinderMob{
 private int talk;
 public Kakyoin(EntityType<? extends Kakyoin> t,Level l){super(t,l);}
 public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,60).add(Attributes.ARMOR,5).add(Attributes.MOVEMENT_SPEED,.24).add(Attributes.FOLLOW_RANGE,32);}
 @Override protected void registerGoals(){
  goalSelector.addGoal(0,new FloatGoal(this));
  goalSelector.addGoal(2,new LookAtPlayerGoal(this,Player.class,9));
  goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.55));
  goalSelector.addGoal(4,new RandomLookAroundGoal(this));
 }
 @Override public void tick(){super.tick();if(talk>0)talk--;}
 @Override public InteractionResult mobInteract(Player p,InteractionHand h){
  if(h==InteractionHand.MAIN_HAND&&p.getItemInHand(h).isEmpty()){
   if(level() instanceof ServerLevel l&&talk==0){
    talk=100;NpcDialogue.say(l,Component.literal("Kakyoin: Rero rero rero rero..."));
   }
   return InteractionResult.sidedSuccess(level().isClientSide);
  }
  return super.mobInteract(p,h);
 }
}''',encoding='utf-8')
(java/'KakyoinClient.java').write_text('''package it.noctis.magic;
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
public final class KakyoinClient{
 @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.KAKYOIN.get(),Renderer::new);}
 static class Renderer extends MobRenderer<Kakyoin,Model>{
  Renderer(EntityRendererProvider.Context c){super(c,new Model(),.36f);}
  @Override protected void scale(Kakyoin e,PoseStack p,float f){p.scale(1.07f,1.07f,1.07f);}
  @Override public ResourceLocation getTextureLocation(Kakyoin e){return new ResourceLocation(Noctis.ID,"textures/entity/kakyoin_cherry.png");}
 }
 static class Model extends EntityModel<Kakyoin>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-.5f,0);
  final Part bang=head.child(-1.65f,-7.5f,-2.05f),bangTip=bang.child(-.48f,3.2f,-.45f);
  final Part jaw=head.child(0,-1.24f,-1.2f),tongue=head.child(0,-1.9f,-2.35f),cherry=head.child(0,-2.1f,-3.52f),stem=cherry.child(0,0,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shins=new Part[2],earrings=new Part[2],coatFront=new Part[2],coatBack=new Part[2];
  void shape(Part p,int m,int f,float width,float... a){CinnabarClient.Model.angular(p,m,f,width,a[0],a[a.length-5],a);}
  Model(){
   // Fitted green school uniform with structured shoulders, stand-up collar and gold buttons.
   shape(body,0,0,8,-.4f,0,0,2.95f,1.55f,.7f,0,0,3.8f,2.0f,3,0,0,3.45f,1.9f,7,0,0,2.65f,1.55f,10.9f,0,0,2.8f,1.65f);
   shape(body,1,1,4,-1.65f,0,0,1.45f,1.25f,-.35f,0,0,1.65f,1.5f);
   body.blade(2,-1.26f,-1.38f,-1.47f,1.26f,-1.38f,-1.47f,.29f);
   body.blade(1,0,.2f,-2.02f,0,9.5f,-1.66f,.17f);
   for(int i=0;i<5;i++)body.oval(2,.14f,1.05f+i*1.72f,-1.95f+i*.07f,.25f,.25f,.14f);
   for(int s:new int[]{-1,1}){
    body.blade(1,s*2.72f,2.5f,-1.72f,s*1.78f,7.4f,-1.54f,.24f);
    body.blade(0,s*.55f,4.4f,-2.01f,s*2.25f,4.5f,-1.91f,.58f);
   }
   // Beveled adult-style manga portrait with angular cheekbones and narrow chin.
   shape(head,4,3,6.4f,-7.55f,0,.13f,1.84f,1.69f,-6.75f,0,.07f,2.8f,2.35f,-4.65f,0,0,2.92f,2.54f,-3.0f,0,-.08f,2.56f,2.28f,-1.2f,0,-.18f,1.72f,1.64f,-.45f,0,-.2f,.85f,1.0f);
   shape(jaw,4,4,3.8f,-.10f,0,-.15f,1.30f,.72f,.65f,0,-.1f,1.53f,.80f,1.15f,0,0,.92f,.55f);
   head.loft(4,8,-4.5f,0,-2.35f,.13f,.12f,-3.55f,0,-2.57f,.20f,.15f,-2.90f,0,-2.96f,.29f,.23f,-2.62f,0,-2.51f,.16f,.08f);
   shape(head,5,5,7.4f,-9.0f,-.15f,.65f,1.6f,1.25f,-8.3f,0,.35f,2.55f,2.3f,-7.4f,0,.25f,3.12f,2.60f,-6.45f,0,.45f,3.01f,2.40f);
   for(int i=0;i<10;i++){
    float x=-2.45f+i*.54f;
    Part q=head.child(x,-8.0f,.30f);
    q.loft(5,8,-.20f,0,.25f,.42f,.48f,.80f,-.16f,.85f,.62f,.56f,2.2f,-.25f,1.34f,.49f,.47f,3.65f,-.17f,1.65f,.24f,.20f,4.5f,0,1.42f,.035f,.04f);
   }
   // Full auburn scalp: continuous rear cap and overlapping angular locks.
   head.loft(11,12,-8.65f,0,.83f,2.05f,1.85f,-7.55f,0,1.15f,3.00f,2.02f,-6.20f,0,1.43f,3.03f,1.93f,-4.60f,0,1.66f,2.80f,1.58f,-3.05f,0,1.55f,2.30f,1.32f,-1.65f,0,1.31f,1.40f,.70f);
   for(int side:new int[]{-1,1}){
    head.loft(5,8,-7.85f,side*1.88f,-.72f,1.07f,1.53f,-6.85f,side*2.48f,-.38f,.83f,1.65f,-5.55f,side*2.72f,.03f,.59f,1.30f,-4.30f,side*2.71f,.33f,.35f,.87f,-3.35f,side*2.38f,.51f,.10f,.26f);
    for(int i=0;i<5;i++){
     float y=-8.65f+i*.92f;
     float x=side*(1.45f+i*.14f);
     head.loft(i%2==0?5:12,6,y,x,.12f,.65f,.70f,y+.65f,x+side*.77f,.72f,.78f,.82f,y+1.24f,x+side*.84f,1.69f,.64f,.80f,y+1.98f,x+side*.63f,2.72f,.41f,.49f,y+2.34f,x+side*.35f,3.33f,.035f,.035f);
    }
   }
   for(int i=0;i<7;i++){
    float x=(i-3)*.84f;float offset=Math.abs(i-3)*.18f;
    head.loft(i%2==0?12:5,6,-10.05f+offset,x,-.03f,.44f,.49f,-9.35f+offset,x*.93f,.55f,.77f,.84f,-8.48f+offset,x,.98f,.84f,1.05f,-7.48f+offset,x*1.06f,2.05f,.64f,.88f,-6.88f+offset,x*1.17f,3.24f,.38f,.43f,-6.63f+offset,x*1.24f,3.84f,.035f,.035f);
    head.loft(i%2==0?5:11,6,-6.5f,x,1.77f,.56f,.71f,-4.7f,x*.97f,2.40f,.54f,.65f,-3.0f,x*.78f,2.59f,.40f,.52f,-1.0f+offset,x*.56f,2.39f,.025f,.035f);
   }
   // Iconic long red forelock: connected curved sections with independent tip movement.
   bang.loft(5,12,-.6f,0,.3f,.6f,.68f,.2f,-.65f,-.20f,1.12f,.72f,1.5f,-.86f,-.63f,.97f,.65f,2.8f,-.56f,-.55f,.72f,.48f,3.4f,-.48f,-.45f,.56f,.36f);
   bangTip.loft(5,12,-.35f,0,0,.59f,.38f,.45f,.24f,-.05f,.50f,.30f,1.25f,.76f,.02f,.39f,.24f,2.12f,1.01f,.11f,.23f,.15f,2.7f,.58f,.20f,.035f,.045f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    head.oval(4,s*2.75f,-3.6f,.04f,.53f,.84f,.48f);
    earrings[i]=head.child(s*2.86f,-3.05f,-.04f);
    earrings[i].blade(2,0,0,0,0,1.45f,0,.12f);
    earrings[i].oval(8,0,1.65f,0,.34f,.33f,.34f);
    Part a=arms[i]=body.child(s*3.83f,.65f,0);
    shape(a,0,0,3.5f,-.65f,0,0,1.22f,1.32f,.4f,0,0,1.53f,1.45f,2.0f,0,0,1.34f,1.20f,5.8f,0,0,.94f,.93f);
    Part f=fore[i]=a.child(0,5.75f,0);
    shape(f,0,0,3,-.35f,0,0,.99f,.98f,1.5f,0,0,1.06f,1.04f,4.1f,0,0,.85f,.83f);
    shape(f,1,1,2.5f,3.3f,0,0,.92f,.89f,4.15f,0,0,.88f,.87f);
    f.oval(4,0,4.9f,-.12f,.82f,1.0f,.68f);
    Part l=legs[i]=root.child(s*1.43f,10.8f,0);
    shape(l,0,0,3.3f,-.45f,0,0,1.38f,1.45f,1.2f,0,0,1.47f,1.4f,4.9f,0,0,1.04f,1.03f,6.3f,0,0,.94f,.94f);
    Part sh=shins[i]=l.child(0,6.2f,0);
    shape(sh,0,0,3,-.3f,0,0,.95f,.94f,1.6f,0,0,1.08f,1.10f,5.6f,0,0,.79f,.83f);
    shape(sh,1,1,3,5.35f,0,-.14f,.84f,.95f,6.1f,0,-.54f,1.04f,1.55f,7.05f,0,-.56f,1.04f,1.56f,7.35f,0,-.51f,.90f,1.39f);
   }
   // Long school uniform with separately swinging coat tails.
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;
    Part cf=coatFront[i]=body.child(side*1.32f,9.0f,-1.15f);
    shape(cf,0,13,3.5f,0,0,0,1.28f,.63f,2.1f,side*.08f,-.09f,1.36f,.60f,5.0f,side*.32f,-.24f,1.40f,.42f,8.1f,side*.55f,-.50f,1.48f,.28f);
    cf.blade(1,-side*1.15f,.1f,-.50f,-side*.84f,7.85f,-.76f,.18f);
    cf.blade(13,side*.35f,.5f,-.65f,side*.93f,7.95f,-.79f,.32f);
    Part cb=coatBack[i]=body.child(side*1.32f,9.0f,1.10f);
    shape(cb,0,13,3.5f,0,0,0,1.29f,.66f,2.0f,side*.1f,.06f,1.40f,.61f,5.1f,side*.28f,.24f,1.52f,.43f,8.25f,side*.44f,.50f,1.60f,.28f);
    cb.blade(1,-side*1.15f,.1f,.55f,-side*1.12f,8.0f,.82f,.18f);
    fore[i].oval(2,side*.78f,3.53f,-.25f,.18f,.19f,.16f);
    fore[i].oval(2,side*.78f,3.97f,-.25f,.18f,.19f,.16f);
    Part sh=shins[i];
    shape(sh,14,14,3,5.4f,0,-.13f,.87f,.97f,6.12f,0,-.55f,1.07f,1.58f,7.08f,0,-.56f,1.08f,1.60f,7.38f,0,-.51f,.95f,1.43f);
    sh.blade(14,-.90f,7.14f,-1.76f,.90f,7.14f,-1.76f,.17f);
   }
   // Mouth cavity, tongue and cherry are individual geometry, not a painted prop.
   head.oval(6,0,-1.93f,-2.43f,1.05f,.46f,.14f);
   head.blade(9,-.72f,-2.27f,-2.59f,.72f,-2.27f,-2.59f,.19f);
   tongue.loft(7,12,-.27f,0,0,.61f,.30f,.06f,0,-.31f,.78f,.66f,.33f,0,-.69f,.67f,.64f,.45f,0,-.91f,.34f,.34f);
   cherry.oval(8,0,0,0,.39f,.37f,.39f);
   cherry.oval(8,.19f,-.05f,0,.31f,.34f,.30f);
   stem.blade(10,.04f,-.27f,0,.10f,-.63f,.07f,.08f);
   stem.blade(10,.10f,-.63f,.07f,.34f,-.91f,.12f,.08f);
  }
  @Override public void setupAnim(Kakyoin e,float limb,float amount,float age,float yaw,float pitch){
   float phase=age*1.22f+(e.getId()%17)*.23f;
   float slow=(float)Math.sin(age*.12f);
   head.ry=yaw*.01745f;head.rx=pitch*.012f-.025f+(float)Math.sin(phase)*.022f;head.rz=.055f+slow*.025f;
   body.ry=slow*.045f;
   jaw.rx=.07f+.04f*(float)Math.sin(phase);
   tongue.x=.46f*(float)Math.sin(phase);tongue.y=-1.9f+.10f*(float)Math.cos(phase);tongue.rz=.25f*(float)Math.sin(phase);tongue.rx=-.10f+.16f*(float)Math.cos(phase);
   cherry.x=.64f*(float)Math.sin(phase);cherry.y=-1.96f-.22f*(float)Math.cos(phase);cherry.z=-3.48f-.12f*(float)Math.cos(phase);
   cherry.ry=phase;cherry.rz=.42f*(float)Math.sin(phase);stem.rx=.17f*(float)Math.sin(phase);
   bang.rz=.06f+.075f*(float)Math.sin(age*.18f);bang.rx=.045f*(float)Math.cos(age*.18f);
   bangTip.rz=.12f+.09f*(float)Math.sin(age*.18f-.55f);bangTip.rx=.05f*(float)Math.cos(age*.18f-.55f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;float walk=(float)Math.cos(limb*.666f+i*Math.PI)*amount;
    arms[i].rx=-walk*.55f;arms[i].rz=-s*.13f;
    fore[i].rx=-.12f;fore[i].rz=0;
    legs[i].rx=walk*.66f;shins[i].rx=Math.max(0,-walk)*.3f;
    earrings[i].rz=slow*.10f+s*.07f;earrings[i].rx=walk*.16f;
    coatFront[i].rx=walk*.43f-.055f;coatBack[i].rx=walk*.37f+.06f;
    coatFront[i].rz=s*(.035f+.028f*slow);coatBack[i].rz=s*(.035f-.028f*slow);
   }
   if(amount<.08f){arms[0].rz=.30f;arms[0].rx=-.15f;fore[0].rx=-.72f;fore[0].rz=.24f;arms[1].rx=-.15f;arms[1].rz=-.34f;fore[1].rx=-.28f;fore[1].rz=.32f;}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.drawStyled(p,v,light,overlay,r,g,b,a,3);}
 }
}''',encoding='utf-8')
# Material atlas with hand-authored brow, narrow lavender eyes, cheek hatching and open mouth.
im=Image.new('RGBA',(1024,512))
pal={0:(39,89,61),1:(23,49,37),2:(209,166,65),3:(232,195,169),4:(232,195,169),5:(153,65,46),6:(56,20,26),7:(208,105,122),8:(166,25,49),9:(240,214,196),10:(80,111,45),11:(100,35,31),12:(181,72,49),13:(63,111,63),14:(88,45,28)}
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for m,base in pal.items():
 for y in range(128):
  v=max(0,min(1,(y-3)/121))
  for x in range(128):
   u=max(0,min(1,(x-3)/121));f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   c=mix(base,(28,25,30),.28*f+.11*v)
   c=mix(c,(255,231,203) if m in (3,4) else (252,214,176),.18*g(.30,.25,.18,.45))
   if m in (0,13):
    c=mix(c,(12,32,23),.38*max(0,math.sin(u*22+v*3))**7)
    c=mix(c,(105,143,78),.24*max(0,math.sin(u*22+v*3+.85))**9)
   if m==14:
    c=mix(c,(37,22,18),.37*max(0,math.sin(v*25+u*2))**8)
    c=mix(c,(156,83,48),.32*g(.35,.26,.34,.20))
   if m in (5,11,12):
    c=mix(c,(231,123,75),.47*max(0,math.sin(u*40+v*4+.5*math.sin(v*8)))**5)
    c=mix(c,(66,27,30),.28*max(0,math.sin(u*62-v*2))**10)
   if m==3:
    for side in (-1,1):
     ex=.5+side*.203;dx=(u-ex)/.112;outer=side*dx;ey=.41-.023*outer;dy=(v-ey)/.042
     eye=abs(dx)**1.7+abs(dy)**1.4
     c=mix(c,(132,82,77),.27*g(ex,.375,.12,.065))
     if eye<1.25:c=(56,35,43)
     if eye<.79:c=(244,238,231)
     if eye<.75 and abs(dx+.08)<.39:
      c=mix((83,80,125),(162,154,198),(dy+1)*.5)
      if abs(dx+.08)<.17:c=(43,36,57)
      if (dx+.18)**2+(dy+.24)**2<.035:c=(255,250,244)
     brow=.32-.040*outer+.019*outer*outer
     if abs(dx)<1.12 and abs(v-brow)<.019:c=(93,44,38)
     if abs(dx)<1.06 and abs(v-(ey-.038))<.008:c=(54,33,38)
     if .18<f<.39 and .58<v<.72 and int((u+v*.58)*115)%7==0:c=mix(c,(142,94,77),.43)
    if f<.19 and abs(v-(.76+.03*(f/.19)**2))<.038:c=(86,37,43)
    if f<.14 and abs(v-.725)<.010:c=(241,212,196)
    c=mix(c,(160,102,84),.18*g(.5,.63,.055,.05))
   if m==7:
    c=mix(c,(249,170,170),.45*g(.33,.3,.22,.4))
    if abs(u-.5)<.018:c=mix(c,(131,54,72),.48)
   if m==8:
    c=mix(c,(240,40,71),.6*g(.38,.35,.35,.38))
    c=mix(c,(255,225,226),.92*g(.28,.21,.09,.11))
   im.putpixel((m%8*128+x,m//8*128+y),(*c,255))
im.save(assets/'textures/entity/kakyoin_cherry.png')
(assets/'models/item/kakyoin_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}',encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.kakyoin']='Noriaki Kakyoin';d['item.noctismagic.kakyoin_spawn_egg']='Uovo di Noriaki Kakyoin' if loc=='it_it' else 'Noriaki Kakyoin Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
# Rare natural encounter via existing nighttime guest logic, with same global per-type limit.
p=java/'NightGuests.java';s=p.read_text(encoding='utf-8')
a='if(l.dimension()!=Level.OVERWORLD)return;'
if a in s:
 s=s.replace(a,a+'''
        if(!p.isCreative()&&p.getRandom().nextInt(32)==0&&l.getEntitiesOfClass(Kakyoin.class,p.getBoundingBox().inflate(80)).isEmpty()){
            BlockPos spot=Eclipse.spot(p,12,24);
            if(spot!=null){Kakyoin guest=Noctis.KAKYOIN.get().create(l);if(guest!=null){guest.moveTo(spot.getX()+.5,spot.getY(),spot.getZ()+.5);if(l.noCollision(guest))l.addFreshEntity(guest);}}
        }
''',1);p.write_text(s,encoding='utf-8')
print('Kakyoin: original beveled green uniform, red S-shaped forelock, animated tongue, cherry and earrings, egg and rare encounter.')
