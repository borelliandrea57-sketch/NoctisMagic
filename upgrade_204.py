"""1.7.41: armored Sticky Fingers, large geometric zippers and wheelchair Johnny."""
from pathlib import Path
import sys,math,json
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(file,a,b):
 p=java/file;s=p.read_text(encoding='utf-8');assert a in s,(file,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
# Sticky Fingers: maintain existing combat AI and replace the small effect with a full-height portal.
f='StickyFingersClient.java'
edit(f,'p.scale(1.13f,1.13f,1.13f);','p.scale(1.53f,1.53f,1.53f);')
edit(f,'final Part aura=new Part(0,0,0);','final Part aura=new Part(0,0,0),portal=new Part(0,0,0);')
edit(f,'float glow,opacity=1;','float glow,opacity=1,opening;')
edit(f,'   zip(head,0,-7.95f,-2.30f,4.05f,.82f);','''   // Solid lower visor with a projecting angular brow: no exposed eyes.
   shell(head,0,-6.25f,0,-.40f,2.53f,2.36f,-5.10f,0,-.60f,2.72f,2.30f,-3.45f,0,-.67f,2.60f,2.14f,-2.90f,0,-.67f,2.30f,1.94f);
   for(int sign:new int[]{-1,1}){
    blade(head,2,sign*.72f,-6.45f,-2.65f,sign*1.95f,-3.15f,-2.02f,.56f);
    blade(head,3,sign*1.72f,-4.86f,-2.27f,sign*1.90f,-3.32f,-2.02f,.17f);
    blade(head,4,sign*1.78f,-2.88f,-1.56f,sign*.92f,-1.72f,-1.62f,.22f);
    for(int j=0;j<4;j++)tooth(head,4,sign*(1.71f-j*.19f),-2.95f+j*.30f,-1.66f,.24f,.15f);
   }
   zip(head,0,-7.95f,-2.87f,4.8f,.92f);
   shell(head,4,-9.00f,0,-.10f,.06f,.08f,-8.25f,0,-.15f,.46f,.44f,-7.95f,0,-.20f,.53f,.48f);
   shell(head,4,-7.30f,0,-2.20f,.08f,.10f,-6.95f,0,-2.62f,.38f,.28f,-6.62f,0,-2.65f,.45f,.25f);
   ''')
edit(f,'    Part f=fore[i]=a.child(0,5.75f,0);','''    for(int j=0;j<4;j++){
     float y=-.60f+j*.72f;
     shell(a,1,y,s*.12f,0,1.53f-j*.10f,1.49f-j*.08f,y+.46f,s*.12f,0,1.59f-j*.10f,1.55f-j*.08f);
    }
    Part f=fore[i]=a.child(0,5.75f,0);''')
edit(f,'    zip(sh,s*.47f,1.56f,-1.04f,4.1f,.65f);','''    for(int j=0;j<4;j++){
     float x=-.66f+j*.44f;blade(sh,1,x,-.15f,-1.30f,x*.88f,1.25f,-1.40f,.39f);
    }
    zip(sh,0,1.56f,-1.20f,4.1f,.84f);
    pull(f,0,4.95f,-.88f,1.0f);pull(sh,0,6.85f,-1.78f,.85f);''')
edit(f,'   for(int i=0;i<6;i++){\n    double a=i*Math.PI/3;', '''   // The opening is a dark, flat slit edged by actual gold teeth, never an orb.
   for(int j=0;j<28;j++){
    float y=-9+j*1.20f;float Y=y+1.20f;
    float x=.35f+2.7f*(float)Math.sin(Math.PI*j/28);
    float X=.35f+2.7f*(float)Math.sin(Math.PI*(j+1)/28);
    blade(portal,3,0,y,0,0,Y,0,2*Math.max(x,X));
    for(int sign:new int[]{-1,1}){
     blade(portal,4,sign*x,y,-.18f,sign*X,Y,-.18f,.38f);
     tooth(portal,4,sign*(x-.14f),y+.38f,-.30f,.75f,.33f);
     blade(portal,2,sign*(x+.38f),y,.06f,sign*(X+.38f),Y,.06f,.22f);
    }
   }
   pull(portal,0,5.5f,-.55f,1.60f);
   for(int i=0;i<6;i++){
    double a=i*Math.PI/3;''')
edit(f,'opacity=1-.70f*z;glow=', 'opening=z;opacity=1-.40f*z;glow=')
edit(f,'   aura.draw(p,v,LightTexture.FULL_BRIGHT,overlay,.67f,.86f,1,a*glow);','''   if(opening>0){
    p.pushPose();p.translate(0,0,.24);p.scale(Math.max(.20f,opening),1,1);
    portal.drawStyled(p,v,LightTexture.FULL_BRIGHT,overlay,r,g,b,a,2);
    p.popPose();
   }''')
edit(f,'overlay,r,g,b,a*.88f*opacity,2);','overlay,r,g,b,a*opacity,2);')
# Keep the entry/exit effect visible at the old position as well, with no scattered blue balls.
edit('JojoMob.java','l.sendParticles(ZIP_BLUE,at.x,at.y+1.3,at.z,7,.44,.70,.44,.01);','')
edit('JojoMob.java','for(int i=0;i<=22;i++){\n            double y=.12+i*.13,spread=.09+.65*Math.sin(Math.PI*i/22)*open;','for(int i=0;i<=28;i++){\n            double y=.10+i*.14,spread=.13+.92*Math.sin(Math.PI*i/28)*open;')
# Johnny: independent registry, existing world-compatible mob and a custom seated renderer.
edit('Noctis.java','public static final RegistryObject<EntityType<Kakyoin>> KAKYOIN=','''public static final RegistryObject<EntityType<JohnnyJoestar>> JOHNNY=ENTITIES.register("johnny_joestar",()->EntityType.Builder.<JohnnyJoestar>of(JohnnyJoestar::new,MobCategory.CREATURE).sized(1.22f,1.86f).clientTrackingRange(10).build(ID+":johnny_joestar"));
    public static final RegistryObject<Item> JOHNNY_EGG=ITEMS.register("johnny_joestar_spawn_egg",()->new ForgeSpawnEggItem(JOHNNY,0xeee7dc,0x394cba,new Item.Properties()));
    public static final RegistryObject<EntityType<Kakyoin>> KAKYOIN=''')
edit('Noctis.java','e.put(KAKYOIN.get(),Kakyoin.attributes().build());','e.put(JOHNNY.get(),JohnnyJoestar.attributes().build());e.put(KAKYOIN.get(),Kakyoin.attributes().build());')
edit('Noctis.java','e.accept(KAKYOIN_EGG.get());','e.accept(KAKYOIN_EGG.get());e.accept(JOHNNY_EGG.get());')
(java/'JohnnyJoestar.java').write_text('''package it.noctis.magic;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
public final class JohnnyJoestar extends PathfinderMob{
 private int talk;
 public JohnnyJoestar(EntityType<? extends JohnnyJoestar> t,Level l){super(t,l);setMaxUpStep(.35f);}
 public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,55).add(Attributes.ARMOR,2).add(Attributes.MOVEMENT_SPEED,.22).add(Attributes.FOLLOW_RANGE,24);}
 @Override protected void registerGoals(){
  goalSelector.addGoal(0,new FloatGoal(this));
  goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.85));
  goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));
  goalSelector.addGoal(4,new RandomLookAroundGoal(this));
 }
 @Override public void tick(){super.tick();if(talk>0)talk--;}
 @Override public InteractionResult mobInteract(Player p,InteractionHand h){
  if(h==InteractionHand.MAIN_HAND&&p.getItemInHand(h).isEmpty()){
   if(level() instanceof ServerLevel l&&talk==0){talk=100;NpcDialogue.say(l,Component.literal("Johnny Joestar: Voglio andare avanti. Non importa quanto sia difficile."));}
   return InteractionResult.sidedSuccess(level().isClientSide);
  }
  return super.mobInteract(p,h);
 }
}''',encoding='utf-8')
(java/'JohnnyClient.java').write_text('''package it.noctis.magic;
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
public final class JohnnyClient{
 @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.JOHNNY.get(),Renderer::new);}
 static class Renderer extends MobRenderer<JohnnyJoestar,Model>{
  Renderer(EntityRendererProvider.Context c){super(c,new Model(),.60f);}
  @Override public ResourceLocation getTextureLocation(JohnnyJoestar e){return new ResourceLocation(Noctis.ID,"textures/entity/johnny_wheelchair.png");}
 }
 static class Model extends EntityModel<JohnnyJoestar>{
  final Part root=new Part(0,0,0),chair=root.child(0,0,0),body=root.child(0,3.5f,.9f),head=body.child(0,0,0);
  final Part[] wheel=new Part[2],caster=new Part[2],arms=new Part[2],fore=new Part[2];
  void tube(Part p,int m,float... a){p.loft(m,8,a);}
  void bar(Part p,int m,float x,float y,float z,float X,float Y,float Z,float w){p.blade(m,x,y,z,X,Y,Z,w);}
  void ring(Part p,int m,float x,float r,float width,int n){
   for(int j=0;j<n;j++){
    double a=j*2*Math.PI/n,b=(j+1)*2*Math.PI/n;
    bar(p,m,x,(float)Math.cos(a)*r,(float)Math.sin(a)*r,x,(float)Math.cos(b)*r,(float)Math.sin(b)*r,width);
   }
  }
  void star(Part p,int m,float x,float y,float z,float r){
   for(int j=0;j<5;j++){
    double a=-Math.PI/2+j*2*Math.PI/5;
    bar(p,m,x,y,z,x+(float)Math.cos(a)*r,y+(float)Math.sin(a)*r,z,.20f);
   }
  }
  Model(){
   // Wooden high back, seat, padded leather and footrest.
   tube(chair,7,2.8f,0,3.55f,3.45f,.46f,11.5f,0,3.55f,3.45f,.46f);
   tube(chair,8,3.3f,0,3.03f,3.15f,.25f,11.2f,0,3.03f,3.15f,.25f);
   tube(chair,7,11.6f,0,.18f,3.65f,3.34f,12.65f,0,.18f,3.65f,3.34f);
   tube(chair,8,11.28f,0,.12f,3.42f,3.13f,11.85f,0,.12f,3.42f,3.13f);
   tube(chair,7,21.6f,0,-5.02f,3.10f,1.60f,22.45f,0,-5.02f,3.10f,1.60f);
   for(int s:new int[]{-1,1}){
    bar(chair,7,s*3.34f,2.2f,3.72f,s*3.34f,17.5f,3.72f,.62f);
    bar(chair,7,s*3.45f,12.1f,-2.9f,s*2.8f,22.0f,-5.5f,.67f);
    bar(chair,7,s*3.45f,8.8f,-2.65f,s*3.45f,8.8f,3.0f,.56f);
    bar(chair,6,s*3.45f,9.0f,-2.65f,s*3.45f,15.5f,-2.65f,.37f);
    bar(chair,6,s*3.3f,17.0f,3.0f,s*3.3f,21.6f,-4.8f,.46f);
   }
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    Part wh=wheel[i]=chair.child(s*4.4f,16.5f,1.15f);
    ring(wh,5,0,7.05f,.86f,28);ring(wh,6,0,6.62f,.27f,28);ring(wh,6,s*.44f,6.13f,.25f,28);
    for(int j=0;j<14;j++){
     double a=j*2*Math.PI/14;
     bar(wh,6,0,0,0,0,(float)Math.cos(a)*6.55f,(float)Math.sin(a)*6.55f,.15f);
    }
    bar(wh,7,-.52f,0,0,.52f,0,0,1.08f);
    Part cast=caster[i]=chair.child(s*2.65f,22.1f,-4.45f);
    ring(cast,5,0,1.45f,.60f,16);ring(cast,6,0,1.10f,.24f,16);
    for(int j=0;j<4;j++){double a=j*Math.PI/2;bar(cast,6,0,0,0,0,(float)Math.cos(a),(float)Math.sin(a),.24f);}
   }
   // Seated torso, white sailor shirt, blue trim, pink stripes.
   tube(body,0,-.4f,0,0,1.55f,.95f,.7f,0,0,2.58f,1.48f,3.2f,0,0,2.33f,1.42f,6.8f,0,0,1.82f,1.34f,8.5f,0,0,2.08f,1.54f);
   tube(body,2,-1.65f,0,0,.82f,.78f,0,0,0,1.03f,.95f);
   for(int s:new int[]{-1,1}){
    bar(body,1,s*2.08f,.1f,-1.17f,s*.08f,3.15f,-1.60f,.45f);
    bar(body,9,s*1.95f,.65f,-1.20f,s*.08f,3.68f,-1.51f,.22f);
    bar(body,1,s*.42f,5.2f,-1.42f,s*1.66f,5.8f,-1.30f,.26f);
    // Bent thighs, shins and boots remain seated during movement.
    tube(chair,1,10.2f,s*1.28f,.4f,1.10f,1.22f,11.5f,s*1.30f,-1.4f,1.16f,2.7f,13.0f,s*1.40f,-3.70f,1.03f,1.08f);
    tube(chair,1,12.4f,s*1.40f,-4.20f,.95f,.91f,15.2f,s*1.40f,-4.35f,.88f,.91f,19.9f,s*1.41f,-4.64f,.69f,.76f);
    tube(chair,5,19.4f,s*1.41f,-4.78f,.78f,.83f,20.6f,s*1.41f,-5.08f,.95f,1.50f,21.45f,s*1.41f,-5.13f,.95f,1.53f);
    bar(chair,1,s*1.41f,21.38f,-6.49f,s*1.41f,21.38f,-3.93f,1.58f);
   }
   tube(head,2,-6.8f,0,0,1.42f,1.25f,-6.0f,0,0,2.07f,1.72f,-4.3f,0,-.06f,2.15f,1.78f,-2.5f,0,-.16f,1.46f,1.36f,-1.65f,0,-.18f,.68f,.75f);
   // Long blond layered hair, white star-pattern cap.
   tube(head,3,-7.0f,0,.50f,1.64f,1.40f,-5.75f,0,.80f,2.26f,1.62f,-4.1f,0,1.02f,2.17f,1.29f,-2.2f,0,1.00f,1.80f,.77f);
   for(int s:new int[]{-1,1})for(int j=0;j<3;j++){
    float x=s*(1.57f+j*.20f);float z=-.45f+j*.69f;
    tube(head,3,-6.0f,x,z,.48f,.54f,-4.9f,x+s*.32f,z,.46f,.43f,-3.2f,x+s*.30f,z+.16f,.40f,.43f,-1.05f,x+s*.62f,z+.25f,.04f,.06f);
   }
   tube(head,0,-8.1f,0,.15f,1.2f,1.10f,-7.65f,0,0,2.03f,1.73f,-6.2f,0,0,2.35f,1.89f,-5.55f,0,-.12f,2.17f,1.77f);
   tube(head,0,-5.95f,0,-1.04f,2.12f,1.52f,-5.52f,0,-1.10f,2.16f,1.60f);
   for(int j=0;j<3;j++)star(head,1,(j-1)*1.13f,-6.65f,-1.74f,.45f);
   bar(head,1,-.42f,-2.82f,-1.58f,.42f,-2.82f,-1.58f,.18f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    Part a=arms[i]=body.child(s*2.60f,.9f,0);
    tube(a,0,-.5f,0,0,.83f,.84f,.65f,0,0,1.05f,1.03f,2.1f,0,0,.93f,.88f);
    tube(a,9,1.86f,0,0,.94f,.91f,2.45f,0,0,.89f,.87f);
    tube(a,2,2.42f,0,0,.72f,.73f,4.1f,0,0,.60f,.64f);
    Part f=fore[i]=a.child(0,4.0f,0);
    tube(f,2,-.2f,0,0,.64f,.66f,2.6f,0,0,.49f,.50f,3.2f,0,0,.46f,.46f);
    for(int j=0;j<3;j++)tube(f,j%2==0?0:9,.45f+j*.68f,0,0,.66f-j*.035f,.67f-j*.035f,.82f+j*.68f,0,0,.66f-j*.035f,.67f-j*.035f);
    tube(f,2,3.05f,0,0,.52f,.46f,3.95f,0,-.12f,.64f,.44f,4.34f,0,-.16f,.38f,.30f);
   }
  }
  @Override public void setupAnim(JohnnyJoestar e,float limb,float amount,float age,float yaw,float pitch){
   float move=Math.min(1,amount*3.5f),phase=limb*.95f;
   float push=(float)Math.sin(phase),reach=(float)Math.cos(phase);
   body.rx=move*(.13f+.10f*push);body.ry=move*.035f*reach;
   head.ry=yaw*.01745f;head.rx=pitch*.01745f-body.rx*.8f;
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    wheel[i].rx=-limb*.53f;caster[i].rx=-limb*2.4f;
    arms[i].rz=-s*(.31f+.09f*move);arms[i].rx=.14f+move*(.35f+.44f*push);
    fore[i].rx=-.45f-move*(.52f+.45f*reach);fore[i].rz=-s*.09f;
   }
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.drawStyled(p,v,light,overlay,r,g,b,a,4);}
 }
}''',encoding='utf-8')
im=Image.new('RGBA',(1024,512))
pal={0:(233,230,219),1:(56,68,157),2:(239,194,157),3:(204,155,66),5:(36,39,48),6:(174,184,187),7:(131,83,48),8:(143,69,49),9:(186,51,102)}
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for m,base in pal.items():
 for y in range(128):
  v=y/127
  for x in range(128):
   u=x/127
   c=mix(base,(22,26,37),.28*abs(u-.5)+.18*v)
   c=mix(c,(255,245,224),.20*math.exp(-((u-.30)/.17)**2-((v-.25)/.45)**2))
   if m in (3,7):c=mix(c,(63,39,29),.25*max(0,math.sin(u*44+v*5))**6)
   if m==6:c=mix(c,(255,255,247),.50*math.exp(-((u-.26)/.07)**2))
   if m==2:
    for sign in (-1,1):
     ex=.5+sign*.22;dx=(u-ex)/.105;dy=(v-.41)/.045
     if abs(dx)**1.7+abs(dy)**1.4<1:c=(48,40,48)
     if abs(dx)**1.7+abs(dy)**1.4<.67:c=(244,239,227)
     if abs(dx)<.30 and abs(dy)<.72:c=(66,125,161)
     if abs(dx)<.11 and abs(dy)<.55:c=(26,37,56)
     if abs(dx)<1.2 and abs(v-(.33-sign*dx*.02))<.014:c=(132,88,43)
   im.putpixel((m%8*128+x,m//8*128+y),(*c,255))
im.save(assets/'textures/entity/johnny_wheelchair.png')
(assets/'models/item/johnny_joestar_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}',encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.johnny_joestar']='Johnny Joestar';d['item.noctismagic.johnny_joestar_spawn_egg']='Uovo di Johnny Joestar' if loc=='it_it' else 'Johnny Joestar Spawn Egg';p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
print('Sticky Fingers visor and giant zipper geometry; Johnny seated wheelchair, rotating wheels and hand propulsion.')
