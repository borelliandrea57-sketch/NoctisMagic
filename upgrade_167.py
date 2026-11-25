"""1.6.7: Black Swordsman, Geass spell and enigmatic quest journal."""
from pathlib import Path
import sys,json,math,struct,zlib,re
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
 p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
def write_noctis_json_resource(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
# New items and magic.
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<Item> GUTS_EGG=ITEMS.register("guts_spawn_egg",()->new ForgeSpawnEggItem(GUTS,0x202027,0x9c9693,new Item.Properties()));
    public static final RegistryObject<Item> DRAGON_SLAYER=ITEMS.register("dragon_slayer",()->new net.minecraft.world.item.SwordItem(net.minecraft.world.item.Tiers.NETHERITE,24,-3.45f,new Item.Properties().rarity(net.minecraft.world.item.Rarity.EPIC).fireResistant()));
    '''+a)
a='e.accept(CATHEDRAL_EGG.get());';edit('Noctis.java',a,a+'e.accept(GUTS_EGG.get());e.accept(DRAGON_SLAYER.get());')
edit('Noctis.java','BAYONETTA("Evoca Bayonetta",9,120);','BAYONETTA("Evoca Bayonetta",9,120),GEASS("Geass - Controllo mentale",5,45);')
edit('Noctis.java','case BAYONETTA ->','case GEASS -> {if(!GeassMagic.cast(p))return;}\n            case BAYONETTA ->')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');s,n=re.subn(r'(ENTITIES.register\("guts",[^\n]*?\.sized\()[^)]*(\))',r'\g<1>1.0f,2.5f\2',s,count=1);assert n==1;p.write_text(s,encoding='utf-8')
# Guaranteed attempt every second, fallback nearby level/cave search. No blocks destroyed.
p=java/'Eclipse.java';s=p.read_text(encoding='utf-8')
a=s.index('        if(p.isCreative())return;\n        if(data.getLong("gutsDay")!=day){')
b=s.index('        if(p.tickCount%240!=0)return;',a)
s=s[:a]+'''        if(data.getLong("gutsDay")!=day){
            if(!l.getEntitiesOfClass(Guts.class,p.getBoundingBox().inflate(64),g->g.isAlive()&&g.isOwnedBy(p)).isEmpty())data.putLong("gutsDay",day);
            else if(GutsArrival.arrive(p,day))data.putLong("gutsDay",day);
        }
        if(p.isCreative())return;
'''+s[b:];p.write_text(s,encoding='utf-8')
write('GutsArrival.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.*;
import net.minecraft.network.chat.Component;
public class GutsArrival{
 static boolean arrive(ServerPlayer p,long day){
  ServerLevel l=p.serverLevel();Guts g=Noctis.GUTS.get().create(l);if(g==null)return false;
  BlockPos center=p.blockPosition();
  for(int i=0;i<160;i++){
   BlockPos q=i<12?Eclipse.spot(p,3,10):center.offset(p.getRandom().nextInt(19)-9,p.getRandom().nextInt(9)-4,p.getRandom().nextInt(19)-9);
   if(q==null||q.distSqr(center)<6||!l.hasChunkAt(q)||!l.getWorldBorder().isWithinBounds(q)||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP))continue;
   g.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,p.getYRot(),0);
   if(!l.noCollision(g)||l.containsAnyLiquid(g.getBoundingBox()))continue;
   g.tame(p);g.setEclipseDay(day);
   if(!l.addFreshEntity(g))return false;
   g.roar(l);RitualQuests.award(p,"guts");
   l.sendParticles(ParticleTypes.SMOKE,g.getX(),g.getY()+1,g.getZ(),45,.45,.75,.45,.07);return true;
  }
  return false;
 }
}''')
# A creative egg persists outside the eclipse; summoned Guts still leaves at its end.
p=java/'Guts.java';s=p.read_text(encoding='utf-8')
s=s.replace('private int swing=0;','private int swing=0,shout=0;')
s=s.replace('Attributes.MAX_HEALTH,200','Attributes.MAX_HEALTH,280').replace('Attributes.ATTACK_DAMAGE,36','Attributes.ATTACK_DAMAGE,44')
s=s.replace('Eclipse.hostile(e)&&getOwner()!=null&&e.distanceToSqr(getOwner())<1024','enemy(e)&&(getOwner()==null||e.distanceToSqr(getOwner())<1600)')
s=s.replace('!Eclipse.hostile(le)','!enemy(le)').replace('m!=e&&Eclipse.hostile(m)','m!=e&&enemy(m)')
s=s.replace('public void setEclipseDay(long day){eclipseDay=day;}','''public void setEclipseDay(long day){eclipseDay=day;}
    boolean enemy(LivingEntity e){return Eclipse.hostile(e)||e instanceof Griffith g&&g.eclipsed();}
    void roar(ServerLevel l){shout=220;NpcDialogue.say(l,net.minecraft.network.chat.Component.literal("Guts: GRIFFISSS!!!").withStyle(net.minecraft.ChatFormatting.DARK_RED,net.minecraft.ChatFormatting.BOLD));playSound(SoundEvents.RAVAGER_ROAR,1.5f,.72f);}
    @Override public net.minecraft.world.InteractionResult mobInteract(Player p,net.minecraft.world.InteractionHand h){
        if(h==net.minecraft.world.InteractionHand.MAIN_HAND&&p.getItemInHand(h).isEmpty()&&level() instanceof ServerLevel l&&getOwner()==null){tame(p);roar(l);return net.minecraft.world.InteractionResult.CONSUME;}
        return super.mobInteract(p,h);
    }
    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource source,int looting,boolean hit){
        super.dropCustomDeathLoot(source,looting,hit);spawnAtLocation(Noctis.DRAGON_SLAYER.get());
    }''')
s=s.replace('if(!Eclipse.active(l)||Eclipse.day(l)!=eclipseDay)','if(eclipseDay>=0&&(!Eclipse.active(l)||Eclipse.day(l)!=eclipseDay))')
s=s.replace('if(tickCount%100==0&&getHealth()<getMaxHealth())heal(3);','''if(shout>0)shout--;
        if(shout==0&&getTarget()!=null&&(getTarget() instanceof Griffith||random.nextInt(90)==0))roar(l);
        if(tickCount%100==0&&getHealth()<getMaxHealth())heal(3);''')
s=s.replace('eclipseDay=t.getLong("EclipseDay");','eclipseDay=t.contains("EclipseDay")?t.getLong("EclipseDay"):-1;')
p.write_text(s,encoding='utf-8')
edit('EclipseGuestsClient.java','e.registerEntityRenderer(Noctis.GUTS.get(),GRenderer::new);','')
# Sculpted black swordsman: angled steel plates, scars, mechanical left arm, cape, gigantic slab sword.
write('GutsSculptedClient.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class GutsSculptedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.GUTS.get(),R::new);}
 static V face(V v,boolean f){return new V(v.x(),v.y(),v.z(),f?.5f+v.x()/7.6f:.04f,v.v(),v.nx(),v.ny(),v.nz());}
 static void project(Part p){for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=5)continue;boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;p.faces.set(i,new Q(face(q.a(),f),face(q.b(),f),face(q.c(),f),face(q.d(),f),5));}}
 static class M extends EntityModel<Guts>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shin=new Part[2],cape=new Part[3];
  M(){
   body.loft(0,40,-1.4f,0,0,2.45f,1.6f,-.1f,0,0,5.1f,2.75f,2.8f,0,-.1f,4.85f,2.78f,5.7f,0,0,3.7f,2.2f,9.0f,0,0,3.18f,1.95f,11.0f,0,0,3.72f,2.15f);
   body.loft(2,32,-1.5f,0,0,1.4f,1.4f,.5f,0,0,1.75f,1.6f);
   for(int s:new int[]{-1,1}){
    body.blade(1,s*4.25f,.55f,-1.6f,s*.35f,3.7f,-2.82f,2.1f);
    body.blade(3,s*3.0f,.5f,-2.25f,s*.25f,8.7f,-1.92f,1.15f);
    for(int j=0;j<3;j++)body.blade(1,s*3.55f,4.0f+j*1.35f,-1.52f,s*.45f,5.0f+j*1.30f,-2.25f,.72f);
    for(int j=0;j<4;j++)body.oval(4,s*3.25f,1.9f+j*1.65f,-1.8f,.20f,.23f,.16f);
   }
   body.loft(3,32,8.8f,0,0,3.23f,2.05f,10.35f,0,0,3.72f,2.20f);
   body.oval(4,0,9.55f,-2.28f,.78f,.66f,.25f);
   for(int j=0;j<3;j++){
    Part c=cape[j]=body.child((j-1)*2.65f,-.4f,2.15f);
    c.loft(6,24,0,0,0,1.65f,.31f,4.0f,(j-1)*.35f,.7f,1.85f,.35f,10,(j-1)*.75f,1.85f,2.13f,.28f,17.5f,(j-1)*1.12f,3.05f,1.75f,.17f,20+(j%2), (j-1)*1.22f,3.5f,.08f,.05f);
   }
   head.loft(5,64,-7.7f,0,.12f,1.55f,1.65f,-7.15f,0,.05f,2.75f,2.52f,-5.45f,0,0,3.2f,2.75f,-3.8f,0,-.1f,3.15f,2.70f,-2.0f,0,-.16f,2.86f,2.35f,-.55f,0,-.22f,2.02f,1.7f,0,0,-.22f,1.15f,1.0f);project(head);
   head.loft(7,32,-8.85f,0,.15f,1.2f,1.1f,-8.3f,0,.2f,2.6f,2.4f,-7.35f,0,.35f,3.44f,3.0f,-6.0f,0,.5f,3.35f,2.95f);
   for(int j=0;j<9;j++){Part p=head.child(-2.8f+j*.7f,-7.8f,-1.4f+(j%3)*.4f);p.loft(7,16,-.2f,0,0,.6f,.7f,-1.65f,(j-4)*.08f,.25f,.51f,.48f,-3.0f-(j%3)*.36f,(j-4)*.17f,.75f,.04f,.06f);}
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    head.oval(2,s*3.05f,-3.4f,.1f,.40f,.84f,.51f);
    arms[i]=body.child(s*5.1f,.35f,0);
    arms[i].loft(0,28,-.9f,0,0,1.70f,1.72f,.8f,0,0,2.30f,2.15f,3.1f,0,0,1.94f,1.80f,4.9f,0,0,1.4f,1.43f);
    for(int j=0;j<3;j++)arms[i].loft(1,28,-.8f+j*1.18f,0,0,2.25f-j*.18f,2.12f-j*.12f,.2f+j*1.18f,0,0,2.45f-j*.23f,2.32f-j*.19f);
    fore[i]=arms[i].child(0,4.8f,0);
    fore[i].loft(i==0?1:0,32,-.2f,0,0,1.43f,1.45f,1.45f,0,0,1.77f,1.70f,3.95f,0,0,1.27f,1.30f);
    for(int j=0;j<3;j++)fore[i].loft(i==0?4:3,24,.6f+j*1.05f,0,0,1.77f-j*.13f,1.72f-j*.10f,.90f+j*1.05f,0,0,1.78f-j*.13f,1.73f-j*.10f);
    fore[i].oval(i==0?1:2,0,4.95f,-.08f,1.23f,1.30f,1.03f);
    for(int j=0;j<4;j++)fore[i].oval(i==0?4:0,-.85f+j*.55f,5.6f,-.62f,.26f,.53f,.34f);
    legs[i]=root.child(s*1.95f,11.0f,0);
    legs[i].loft(0,28,-.3f,0,0,1.92f,1.89f,2.5f,0,0,1.73f,1.70f,5.5f,0,0,1.28f,1.32f);
    shin[i]=legs[i].child(0,5.35f,0);
    shin[i].oval(1,0,0,-.72f,1.5f,1.45f,1.12f);
    shin[i].loft(0,28,-.2f,0,0,1.3f,1.34f,1.7f,0,0,1.56f,1.51f,4.6f,0,0,1.16f,1.21f,5.5f,0,0,1.32f,1.38f);
    shin[i].blade(1,0,.85f,-1.45f,0,5.4f,-1.35f,1.65f);
    shin[i].loft(1,28,5.2f,0,0,1.33f,1.42f,6.5f,0,-.7f,1.57f,2.05f,7.6f,0,-.7f,1.61f,2.12f);
   }
   Part sword=fore[1].child(0,4.9f,-.6f);sword.rx=-1.3f;sword.rz=.13f;
   sword.loft(3,16,-3.0f,0,0,.46f,.50f,2.0f,0,0,.46f,.50f);
   sword.loft(4,20,1.5f,0,0,1.85f,.60f,2.2f,0,0,2.1f,.65f);
   sword.loft(8,8,2.1f,0,0,2.18f,.45f,5.2f,0,0,2.52f,.55f,22.0f,0,0,2.52f,.55f,25.6f,0,0,.08f,.12f);
   sword.loft(9,8,2.3f,0,-.36f,1.72f,.12f,22.0f,0,-.42f,1.92f,.13f,25.0f,0,-.07f,.07f,.06f);
  }
  @Override public void setupAnim(Guts e,float limb,float amount,float age,float yaw,float pitch){
   float hit=e.swingPose(age-e.tickCount);head.ry=yaw*.012f;head.rx=pitch*.012f;body.ry=hit*.48f;
   for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666f+i*Math.PI)*amount;arms[i].rx=i==1?-.55f-hit*1.65f:-w*.55f-hit*.56f;arms[i].rz=-s*.14f+(i==1?hit*.80f:0);fore[i].rx=i==1?-.28f-hit*.32f:-hit*.43f;legs[i].rx=w*.62f;shin[i].rx=Math.max(0,-w)*.30f;}
   for(int j=0;j<3;j++){cape[j].rx=.14f+amount*.35f+hit*.32f+(float)Math.sin(age*.13f+j*.5f)*.08f;cape[j].rz=(j-1)*.07f+(float)Math.sin(age*.08f+j)*.04f;}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<Guts,M>{R(EntityRendererProvider.Context c){super(c,new M(),.53f);}@Override protected void scale(Guts e,PoseStack p,float partial){p.scale(1.23f,1.22f,1.23f);}@Override public ResourceLocation getTextureLocation(Guts e){return new ResourceLocation(Noctis.ID,"textures/entity/guts_sculpted.png");}}
}''')
# Geass is a native mana spell. Nonboss hostile mobs only; control expires.
write('GeassMagic.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class GeassMagic{
 static final String OWNER="NoctisGeassOwner",UNTIL="NoctisGeassUntil";
 static final TagKey<EntityType<?>> BOSSES=TagKey.create(Registries.ENTITY_TYPE,new ResourceLocation("forge","bosses"));
 static boolean eligible(LivingEntity e){return e instanceof Monster&&Eclipse.hostile(e)&&e.getMaxHealth()<=100&&!e.getType().is(BOSSES)&&!(e instanceof OneWinged);}
 static boolean controlled(Mob m,ServerLevel l){return m.getPersistentData().hasUUID(OWNER)&&m.getPersistentData().getLong(UNTIL)>l.getGameTime();}
 static boolean cast(ServerPlayer p){
  if(!p.isCreative()&&!Noctis.data(p).getBoolean("GeassLearned")){p.sendSystemMessage(Component.literal("Un occhio rosso custodisce un potere che ancora non ti appartiene."));return false;}
  ServerLevel l=p.serverLevel();Vec3 eye=p.getEyePosition(),look=p.getLookAngle();
  Mob target=l.getEntitiesOfClass(Mob.class,p.getBoundingBox().inflate(18),m->eligible(m)&&p.hasLineOfSight(m)&&m.isAlive()).stream().filter(m->{Vec3 d=m.getEyePosition().subtract(eye);return d.lengthSqr()<=324&&look.dot(d.normalize())>.965;}).min(Comparator.comparingDouble(p::distanceToSqr)).orElse(null);
  if(target==null){p.sendSystemMessage(Component.literal("Il Geass non incontra uno sguardo vulnerabile."));return false;}
  if(controlled(target,l)&&!target.getPersistentData().getUUID(OWNER).equals(p.getUUID()))return false;
  target.getPersistentData().putUUID(OWNER,p.getUUID());target.getPersistentData().putLong(UNTIL,l.getGameTime()+600);
  target.setTarget(null);target.getNavigation().stop();
  l.sendParticles(ParticleTypes.DRAGON_BREATH,target.getX(),target.getEyeY(),target.getZ(),36,.30,.25,.30,.035);
  p.playSound(SoundEvents.BEACON_POWER_SELECT,1,.7f);RitualQuests.complete(p,"lelouch");return true;
 }
 @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent ev){
  if(!(ev.getEntity() instanceof Mob m)||!(m.level() instanceof ServerLevel l)||!m.getPersistentData().hasUUID(OWNER))return;
  if(!controlled(m,l)){m.getPersistentData().remove(OWNER);m.getPersistentData().remove(UNTIL);m.setTarget(null);return;}
  ServerPlayer p=l.getServer().getPlayerList().getPlayer(m.getPersistentData().getUUID(OWNER));
  if(p==null||p.level()!=l||!p.isAlive()){m.setTarget(null);return;}
  if(m.getTarget()==p)m.setTarget(null);
  if(m.tickCount%5!=0)return;
  LivingEntity t=l.getEntitiesOfClass(LivingEntity.class,m.getBoundingBox().inflate(14),e->e!=m&&eligible(e)&&(!(e instanceof Mob other)||!controlled(other,l))&&m.hasLineOfSight(e)).stream().min(Comparator.comparingDouble(m::distanceToSqr)).orElse(null);
  m.setTarget(t);if(t!=null)m.getNavigation().moveTo(t,1.1);else if(m.distanceTo(p)>5)m.getNavigation().moveTo(p,1.1);else m.getNavigation().stop();
  l.sendParticles(ParticleTypes.WITCH,m.getX(),m.getEyeY()+.18,m.getZ(),2,.18,.08,.18,.01);
 }
 @SubscribeEvent public static void protect(LivingAttackEvent ev){
  if(ev.getSource().getEntity() instanceof Mob m&&m.level() instanceof ServerLevel l&&controlled(m,l)){
   if(ev.getEntity() instanceof net.minecraft.world.entity.player.Player||ev.getEntity() instanceof Mob other&&controlled(other,l))ev.setCanceled(true);
  }
 }
}''')
# Lelouch: earn his trust via C.C. then receive the learned spell. Quest completion by first cast.
edit('DramaGuest.java','if(kind()==0)perform(l);','''if(kind()==1&&p instanceof ServerPlayer sp&&item.isEmpty()){
                RitualQuests.award(sp,"lelouch");
                if(Noctis.data(sp).getBoolean("GeassPizza")&&!Noctis.data(sp).getBoolean("GeassLearned")){
                    Noctis.data(sp).putBoolean("GeassLearned",true);say(l,"Il tuo gesto non mi e' sfuggito. Il Geass ora ti appartiene.");
                    sp.sendSystemMessage(Component.literal("Nuova magia appresa: Geass (livello 5).").withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));
                }else if(!Noctis.data(sp).getBoolean("GeassLearned"))say(l,"Anche un re deve saper placare la fame di una strega.");
                else say(l,"Un ordine puo' cambiare il corso della battaglia.");
                return InteractionResult.CONSUME;
            }
            if(kind()==0)perform(l);''')
edit('DramaGuest.java','pizzaCd=200;if(!p.getAbilities().instabuild)item.shrink(1);','pizzaCd=200;if(p instanceof ServerPlayer sp)Noctis.data(sp).putBoolean("GeassPizza",true);if(!p.getAbilities().instabuild)item.shrink(1);')
# Joker: existing mechanics, no numeric objectives or explicit instruction in quest.
edit('Joker.java','data.putInt("PhantomChallenge",1);','RitualQuests.award(sp,"joker");data.putInt("PhantomChallenge",1);')
edit('Joker.java','data.putInt("PhantomChallenge",2);','RitualQuests.award(sp,"joker");RitualQuests.complete(sp,"joker");data.putInt("PhantomChallenge",2);')
edit('Joker.java','Take your time. Elimina cinque Ombre e torna da me.','Take your time. Cinque ombre custodiscono la strada per il mio covo.')
edit('Joker.java','p.displayClientMessage(Component.literal("Calling Card: "+data.getInt("PhantomKills")+"/5"),true);','')
edit('PhantomChallenge.java','p.displayClientMessage(Component.literal("Calling Card: "+k+"/5"+(k==5?" - torna da Joker!":"")),true);','p.displayClientMessage(Component.literal(k==5?"La Calling Card ora pulsa di luce.":"La Calling Card si scalda."),true);')
# Lucy: lunar relic from the night sky, phantom membrane. Courtesans: all three healers.
edit('MoonGuest.java','if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;','''if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        if(kind()==1&&p instanceof ServerPlayer sp){
            RitualQuests.award(sp,"lucy");
            if(p.getItemInHand(h).is(net.minecraft.world.item.Items.PHANTOM_MEMBRANE)&&!RitualQuests.done(sp,"lucy_complete")){
                if(!p.getAbilities().instabuild)p.getItemInHand(h).shrink(1);
                RitualQuests.complete(sp,"lucy");say(sp.serverLevel(),"Un frammento del cielo... grazie. Un giorno arriveremo lassu'.");
                net.minecraft.world.item.ItemStack reward=new net.minecraft.world.item.ItemStack(Noctis.CRYSTAL.get(),6);if(!p.getInventory().add(reward))p.drop(reward,false);
                return InteractionResult.CONSUME;
            }
        }
        if(!p.getItemInHand(h).isEmpty())return InteractionResult.PASS;''')
edit('MoonGuest.java','"Mi porterai sulla luna?"','"Mi porterai sulla luna? Le ali di chi non dorme sfiorano il cielo."')
edit('CabaretHealer.java','if(p instanceof ServerPlayer sp)speak(sp);','if(p instanceof ServerPlayer sp){RitualQuests.award(sp,"cabaret");speak(sp);}')
edit('CabaretHealer.java','data.putLong("cabaretUntil",l.getGameTime()+600);','''data.putLong("cabaretUntil",l.getGameTime()+600);
        RitualQuests.award(sp,"cabaret");
        int mask=data.getInt("NoctisCabaretMask")|(1<<variant());data.putInt("NoctisCabaretMask",mask);
        if((mask&7)==7)RitualQuests.complete(sp,"cabaret");''')
# All entries use riddles; retain existing ids and criterion keys so progress is not reset.
base=res/'data/noctismagic/advancements/rituals'
clues={
'root':('Le pagine senza nome','Nameless pages','La verita si nasconde tra le righe.','Truth hides between the lines.'),
'jesus':('Una voce nel silenzio','A voice in silence','Una richiesta sincera attraversa il cielo. Anche il nome conta.','A sincere plea crosses the sky. The name matters too.'),
'jesus_complete':('Pane per gli affamati','Bread for the hungry','Chi risponde alla preghiera non arriva a mani vuote.','He who answers the prayer does not come empty-handed.'),
'shenron':('Sette stelle','Seven stars','Sette luci arancioni, una sola promessa.','Seven orange lights, one promise.'),
'shenron_complete':('Un solo desiderio','One wish','Il cielo ascolta una sola volta. Scegli con saggezza.','The sky listens only once. Choose wisely.'),
'sephiroth':('Una sola ala','One wing','Incidi il nome di colui che ha una sola ala. La musica fara il resto.','Inscribe the name of the one-winged angel. Music will do the rest.'),
'sephiroth_complete':('Il silenzio dopo il canto','Silence after the song','Anche un angelo puo precipitare.','Even an angel can fall.'),
'miaugusto':('Nove vite, cinque legami','Nine lives, five bonds','Cinque piccoli predatori fidati. Un grande miagolio risponde.','Five little trusted predators. One great meow answers.'),
'miaugusto_complete':('La ciotola vuota','The empty bowl','La fame del gigante non conosce sazieta.','The giant hunger knows no end.'),
'exodia':('Le catene dimenticate','Forgotten chains','Cinque reliquie dormono dove i viandanti cercano tesori.','Five relics sleep where travelers seek treasure.'),
'exodia_complete':('Oltre il proibito','Beyond the forbidden','Quando le catene cadono, perfino il sole trema.','When the chains fall, even the sun trembles.'),
'guts':('Il sole divorato','The devoured sun','Quando il sole muore, il marchiato brandisce una lastra di ferro.','When the sun dies, the branded man wields a slab of iron.'),
'lelouch':('La fame della strega','The witch hunger','Un re mascherato e una strega affamata. La sua debolezza ha forma rotonda.','A masked king and a hungry witch. Her weakness is round.'),
'lelouch_complete':('Lo sguardo del re','The king gaze','Una pupilla scarlatta. Una sola volonta.','A crimson pupil. A single will.'),
'joker':('La lettera rossa','The red letter','Una maschera bianca custodisce una promessa.','A white mask guards a promise.'),
'joker_complete':('Il cuore rubato','The stolen heart','Cinque ombre al calar della notte. La lettera attende il suo padrone.','Five shadows at dusk. The letter awaits its master.'),
'lucy':('Sogno di luna','Moon dream','Una ragazza osserva il cielo quando il mondo dorme.','A girl watches the sky when the world sleeps.'),
'lucy_complete':('Un frammento di cielo','A piece of sky','Chi sfida il sonno vede ali che lasciano tracce.','Those who defy sleep see wings that leave traces.'),
'cabaret':('Le tre lanterne','The three lanterns','Tre rose nella notte, una moneta dorata apre le porte.','Three roses in the night, a golden coin opens doors.'),
'cabaret_complete':('Tre benedizioni','Three blessings','Tre mani diverse possono alleviare lo stesso dolore.','Three different hands can ease the same pain.')}
for id,icon,parent,xp in [('guts','noctismagic:dragon_slayer','root',100),('lelouch','minecraft:ender_eye','root',50),('lelouch_complete','minecraft:ender_eye','lelouch',200),('joker','noctismagic:calling_card','root',50),('joker_complete','noctismagic:calling_card','joker',180),('lucy','minecraft:phantom_membrane','root',50),('lucy_complete','minecraft:phantom_membrane','lucy',150),('cabaret','minecraft:gold_nugget','root',50),('cabaret_complete','minecraft:gold_nugget','cabaret',150)]:
 write_noctis_json_resource(base/(id+'.json'),{'parent':'noctismagic:rituals/'+parent,'display':{'icon':{'item':icon},'title':{'translate':'advancement.noctismagic.rituals.'+id+'.title'},'description':{'translate':'advancement.noctismagic.rituals.'+id+'.description'},'frame':'goal','show_toast':True,'announce_to_chat':True,'hidden':False},'criteria':{'ritual':{'trigger':'minecraft:impossible'}},'rewards':{'experience':xp}})
# Art atlas and item icon.
def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
def png(p,W,H,pix):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+chunk(b'IEND',b''))
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def clamp(x):return max(0,min(1,x))
W,H=1024,512;pix=bytearray(W*H*4)
for m,b in enumerate([(28,30,36),(69,75,83),(218,176,145),(92,58,37),(158,145,118),(218,176,145),(20,22,29),(18,20,25),(111,120,132),(47,50,60)]):
 for y in range(128):
  v=clamp((y-3)/121)
  for x in range(128):
   u=clamp((x-3)/121);c=mix(b,(12,14,19),.14*v+.12*(1-math.sin(u*math.pi)))
   if m in (0,1,4,8):
    c=mix(c,(191,197,201),.25*math.exp(-((u-.33)/.13)**2))
    if abs(math.sin(u*170+v*29)*math.cos(v*43-u*9))>.97:c=mix(c,(178,179,181),.20)
   if m==5:
    c=mix(b,(145,88,76),.13*clamp((abs(u-.5)-.15)*4))
    for side in (-1,1):
     dx=(u-(.5+side*.16))/.10;dy=(v-.48-side*dx*.022)/.040
     if abs(dx)<1 and abs(v-(.367+side*dx*.018))<.015:c=(30,25,28)
     if dx*dx+dy*dy<1:
      c=(56,31,30) if side==-1 else (231,219,198)
      if side==1 and abs(dx)<.35:c=(68,45,35)
      if side==1 and abs(dx)<.17:c=(23,22,23)
     if side==-1 and abs(u-(.36+.10*(v-.48)))<.009 and .35<v<.67:c=(140,70,65)
    if abs(u-.5)<.065 and abs(v-.79)<.008:c=(86,44,39)
    if .51<v<.67 and abs(u-(.56+.16*(v-.51)))<.006:c=(151,86,74)
   off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/guts_sculpted.png',W,H,pix)
W=H=64;pix=bytearray(W*H*4)
for y in range(H):
 for x in range(W):
  t=(x+63-y)/2;d=x+y-63;c=None
  if 15<t<60 and abs(d)<(6 if t<53 else max(0,(60-t)*.85)):c=(165,174,186) if abs(d)>4 else (79,85,97)
  if 12<t<17 and abs(d)<8:c=(112,102,83)
  if 3<t<14 and abs(d)<2:c=(68,43,29)
  if 2<t<5 and abs(d)<3:c=(145,136,115)
  if c:pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
png(assets/'textures/item/dragon_slayer.png',W,H,pix)
write_noctis_json_resource(assets/'models/item/dragon_slayer.json',{'parent':'minecraft:item/handheld','textures':{'layer0':'noctismagic:item/dragon_slayer'},'display':{'thirdperson_righthand':{'rotation':[0,-90,55],'translation':[0,4,0],'scale':[1.65,1.65,1.65]},'thirdperson_lefthand':{'rotation':[0,90,-55],'translation':[0,4,0],'scale':[1.65,1.65,1.65]}}})
write_noctis_json_resource(assets/'models/item/guts_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for i,lang in enumerate(('it_it','en_us')):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for id,t in clues.items():
  d['advancement.noctismagic.rituals.'+id+'.title']=t[i]
  d['advancement.noctismagic.rituals.'+id+'.description']=t[i+2]
 d['item.noctismagic.guts_spawn_egg']='Uovo generatore: Guts' if i==0 else 'Guts Spawn Egg'
 d['item.noctismagic.dragon_slayer']='Dragon Slayer'
 write_noctis_json_resource(p,d)
print('Guts detailed model, safe eclipse arrival, Dragon Slayer, Geass and enigmatic quests installed.')


# 1.6.7 visual and mounted-flight hotfix (after all earlier upgrades).
edit('SynchroClient.java','e.registerEntityRenderer(Noctis.BLACK_ROSE.get(),c->new Renderer(c,true));','')
edit('SculptedGuestsClient.java','e.registerEntityRenderer(Noctis.JOKER.get(),c->new R<Joker>(c,0));','')

write('RoseDragonClient.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import static it.noctis.magic.StardustSculptedClient.spar;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class RoseDragonClient {
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.BLACK_ROSE.get(),R::new);}
 static Part petal(Part p,int mat,float x,float y,float z,float rx,float ry,float rz,float len,float w,float curve){
  Part q=p.child(x,y,z);q.rx=rx;q.ry=ry;q.rz=rz;
  q.loft(mat,18,0,0,0,w*.22f,.18f,len*.20f,0,-.15f,w*.65f,.38f,len*.46f,0,-curve*.30f,w,.46f,len*.72f,0,-curve*.65f,w*.72f,.28f,len,0,-curve,.035f,.035f);
  return q;
 }
 static class M extends EntityModel<SynchroDragon>{
  final Part root=new Part(0,0,0),body=root.child(0,9,0),neck=body.child(0,-1,-6),head=neck.child(0,-8,-5),jaw=head.child(0,.7f,-2);
  final Part[] wing=new Part[2],outer=new Part[2],front=new Part[2],fore=new Part[2],hind=new Part[2],shin=new Part[2],tail=new Part[11];
  M(){
   Part trunk=body.child(0,0,0);trunk.rx=(float)Math.PI/2;
   trunk.loft(0,28,-7,0,0,1.65f,1.8f,-5,0,0,3.7f,3.25f,-2,0,0,4.1f,3.55f,2,0,0,2.55f,2.45f,5.5f,0,0,2.8f,2.6f,7,0,0,1.65f,1.65f);
   for(int j=0;j<5;j++){Part q=body.child(0,1.6f,-5+j*2.25f);q.rx=(float)Math.PI/2;q.loft(1,24,-.7f,0,0,2.5f-j*.19f,1.7f,0,0,0,2.7f-j*.19f,1.8f,.65f,0,0,2.35f-j*.19f,1.55f);}
   neck.loft(0,26,-8.5f,0,-5,1.28f,1.48f,-7,0,-4,1.62f,1.65f,-4.5f,0,-2,1.93f,1.85f,-2,0,-.5f,2.28f,2.1f,0,0,0,2.6f,2.4f);
   // Distinctive overlapping rose corolla and thorny dark neck.
   for(int layer=0;layer<3;layer++)for(int i=0;i<8;i++){
    double a=i*Math.PI/4+layer*.36;float sx=(float)Math.sin(a),cz=(float)Math.cos(a);
    petal(neck,layer==0?2:layer==1?3:4,sx*(1.4f+layer*.32f),-6+layer*1.65f,-3.5f+cz*1.7f+layer*.8f,cz*.87f,0,-sx*(.85f+layer*.13f),5.2f+layer*.95f,1.45f+layer*.32f,1.4f+layer*.5f);
   }
   Part skull=head.child(0,-.2f,-.3f);skull.rx=-(float)Math.PI/2;
   skull.loft(0,32,-1.8f,0,0,1.15f,1.3f,-.7f,0,0,2.18f,1.85f,.8f,0,0,2.28f,1.7f,2.4f,0,.18f,1.5f,1.14f,4.2f,0,.24f,.66f,.61f,5.0f,0,.22f,.28f,.32f);
   jaw.blade(0,-.15f,0,-.1f,0,1.1f,-3.7f,2.25f);
   for(int s:new int[]{-1,1}){
    head.blade(3,s*1.25f,-1.3f,-.8f,s*3.4f,-.25f,2.1f,1.45f);
    spar(head,0,s*1.6f,-1.2f,.35f,s*3.3f,-6.2f,3.0f,.62f,.025f);
    spar(head,2,s*1.3f,-1.25f,.2f,s*2.0f,-4.6f,1.6f,.43f,.025f);
    head.oval(12,s*1.64f,-.55f,-1.95f,.40f,.27f,.64f);
    head.blade(0,s*1.25f,-1.1f,-2.5f,s*2.05f,-.95f,-.45f,.55f);
    for(int j=0;j<4;j++)spar(jaw,6,s*(.86f-j*.11f),.25f,-.6f-j*.58f,s*(.82f-j*.11f),-.47f,-.68f-j*.58f,.16f,.025f);
   }
   head.blade(3,0,-1.7f,-2.4f,0,-4.6f,1.5f,1.25f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    front[i]=body.child(s*3.0f,1,-4.4f);front[i].loft(0,20,-.6f,0,0,1.15f,1.3f,1.7f,s*.4f,0,1.3f,1.35f,5,s*.75f,-.2f,.68f,.78f);
    fore[i]=front[i].child(s*.75f,4.8f,-.2f);fore[i].loft(0,18,0,0,0,.76f,.8f,2.1f,0,.18f,.88f,.83f,7,0,-.2f,.53f,.7f);
    fore[i].oval(0,0,7,-.65f,.92f,.7f,1.26f);
    for(int j=0;j<3;j++)spar(fore[i],6,-.65f+j*.65f,7,-1.05f,-.75f+j*.75f,7.7f,-2.65f,.27f,.02f);
    hind[i]=body.child(s*2.55f,.9f,4.5f);hind[i].oval(0,s*.3f,1.5f,0,1.6f,2.3f,1.8f);
    hind[i].loft(0,20,1,0,0,1.45f,1.55f,3.3f,0,-.55f,1.05f,1.1f,5,0,-.9f,.69f,.75f);
    shin[i]=hind[i].child(0,5,-.9f);shin[i].loft(0,18,0,0,0,.85f,.9f,1.6f,0,.55f,.8f,.9f,7.1f,0,-.2f,.68f,.8f);
    shin[i].oval(0,0,7.2f,-.5f,1.12f,.72f,1.45f);
    for(int j=0;j<3;j++)spar(shin[i],6,-.75f+j*.75f,7.1f,-1.1f,-.86f+j*.86f,7.9f,-2.8f,.31f,.02f);
    petal(body,3,s*3.0f,-1.6f,-3.2f,-.5f,0,-s*1.5f,5.8f,1.8f,1.2f);
    Part w=wing[i]=body.child(s*3.3f,-2.1f,-1.7f);
    spar(w,0,0,0,0,s*7,-3.5f,0,1.05f,.66f);spar(w,0,s*7,-3.5f,0,s*11,-7,1,.72f,.35f);
    Part o=outer[i]=w.child(s*11,-7,1);
    // Petal wings rather than bat membrane: overlapping, tapered crimson blades with dark veins.
    for(int j=0;j<8;j++){
     float f=j/7f;
     petal(o,j%3==0?4:2,s*(-3+f*4),1.4f+f*.9f,1+f*1.6f,-.63f-f*.18f,s*.18f,-s*(1.95f-f*1.90f),18-f*3.4f,2.1f+f*.4f,2.4f+f*1.3f);
     petal(o,3,s*(-2+f*4),-.1f+f,1.1f+f*1.6f,-.60f-f*.1f,s*.18f,-s*(1.90f-f*1.85f),13-f*2,1.3f,1.85f);
    }
    for(int j=0;j<4;j++)petal(w,3,s*(.9f+j*1.65f),-.3f-j*.55f,.2f,-.68f,0,-s*.60f,10.2f-j*.35f,1.85f,2.15f);
    spar(o,0,0,0,0,s*5,-3,1,.55f,.02f);
   }
   Part prev=body;
   for(int i=0;i<tail.length;i++){
    float r=1.65f-i*.132f;Part t=tail[i]=prev.child(0,0,i==0?6:3.2f);
    Part seg=t.child(0,0,0);seg.rx=(float)Math.PI/2;seg.loft(0,18,-.25f,0,0,r,r,.85f,0,0,r,r,3.35f,0,0,r*.84f,r*.84f);
    spar(t,0,0,-r*.6f,.4f,0,-r*2.0f,2.3f,r*.36f,.02f);
    if(i%2==0)for(int s:new int[]{-1,1})spar(t,3,s*r*.8f,0,.3f,s*r*1.8f,-r*.7f,2.1f,r*.24f,.02f);
    prev=t;
   }
   for(int i=0;i<5;i++)petal(prev,i%2==0?2:3,0,0,2,(float)Math.PI/2,i*1.256f,(i-2)*.27f,4.8f,1.1f,1.25f);
  }
  @Override public void setupAnim(SynchroDragon e,float limb,float amount,float age,float yaw,float pitch){
   boolean air=!e.onGround()||e.isVehicle(),sit=e.isInSittingPose();float cast=e.casting();
   body.y=sit?12:9;body.rx=air?-.075f:0;neck.rx=-cast*.22f+(float)Math.sin(age*.10f)*.055f;neck.ry=yaw*.004f;
   head.ry=yaw*.009f;head.rx=pitch*.009f+cast*.14f;jaw.rx=cast*.6f;
   for(int i=0;i<2;i++){int s=i==0?-1:1;float flap=(float)Math.sin(age*(air?.23f:.075f))*(air?.54f:.10f);
    wing[i].rz=s*(flap+(air?-.10f:.36f));wing[i].ry=s*(air?.04f:.39f);outer[i].rz=s*flap*.33f;
    float w=(float)Math.cos(limb*.65f+i*Math.PI)*amount;front[i].rx=air?-.69f:sit?-.48f:w*.51f;fore[i].rx=air?-.57f:sit?.22f:-.09f;
    hind[i].rx=air?.72f:sit?-.61f:-w*.48f;shin[i].rx=air?-.83f:sit?.61f:Math.max(0,w)*.27f;
   }
   for(int i=0;i<tail.length;i++){tail[i].ry=(float)Math.sin(age*.11f-i*.46f)*.17f;tail[i].rx=-.04f+(float)Math.cos(age*.09f-i*.4f)*.095f;}
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<SynchroDragon,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),1.2f);}
  @Override protected void scale(SynchroDragon e,PoseStack p,float partial){p.scale(2.15f,2.15f,2.15f);}
  @Override public ResourceLocation getTextureLocation(SynchroDragon e){return new ResourceLocation(Noctis.ID,"textures/entity/black_rose_sculpted.png");}
 }
}''')
write('JokerDetailedClient.java','''package it.noctis.magic;
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
public class JokerDetailedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.JOKER.get(),R::new);}
 static class M extends EntityModel<Joker>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-.6f,0);
  final Part[] arm=new Part[2],elbow=new Part[2],leg=new Part[2],knee=new Part[2],coat=new Part[4];
  M(){
   body.loft(0,24,-.9f,0,0,2.35f,1.55f,.3f,0,0,3.3f,1.95f,2.8f,0,0,3.25f,1.95f,6.8f,0,0,2.30f,1.45f,9.4f,0,0,2.5f,1.6f,11.2f,0,0,2.85f,1.75f);
   body.loft(2,24,-.65f,0,-.1f,1.4f,1.34f,1.5f,0,-.38f,1.95f,1.55f,5.6f,0,-.15f,1.85f,1.35f,8.9f,0,-.1f,1.7f,1.40f);
   body.loft(1,20,-1.35f,0,0,.94f,.91f,.0f,0,0,1.05f,1.03f);
   for(int s:new int[]{-1,1}){
    body.blade(3,s*1.5f,-1.0f,-.7f,s*2.4f,-2.4f,.85f,1.8f);
    body.blade(3,s*2.25f,.05f,-1.48f,s*.24f,4.5f,-1.93f,1.8f);
    body.blade(3,s*1.95f,4.25f,-1.35f,s*.4f,9.3f,-1.63f,.9f);
    body.blade(5,s*2.18f,6.2f,-1.0f,s*2.1f,7.85f,-1.12f,.39f);
    for(int j=0;j<3;j++)body.oval(6,s*1.22f,3.8f+j*1.48f,-1.70f,.16f,.17f,.13f);
   }
   head.loft(7,32,-7.35f,0,.05f,1.7f,1.8f,-6.8f,0,0,2.65f,2.36f,-5.35f,0,0,2.92f,2.62f,-3.6f,0,-.09f,2.87f,2.53f,-2.0f,0,-.15f,2.25f,2.12f,-.72f,0,-.25f,1.55f,1.64f,-.15f,0,-.35f,.64f,.8f);
   // Raised sculpted porcelain edge on both sides of the angular domino mask.
   for(int s:new int[]{-1,1}){
    head.blade(8,s*1.58f,-4.1f,-2.04f,s*2.68f,-5.16f,-1.12f,.58f);
    head.blade(8,s*.58f,-3.9f,-2.53f,s*1.84f,-3.25f,-1.97f,.34f);
    head.oval(1,s*2.78f,-3.5f,.02f,.34f,.69f,.49f);
   }
   head.loft(9,24,-8.8f,0,.1f,.8f,1.05f,-8.45f,0,.2f,2.5f,2.2f,-7.35f,0,.20f,3.16f,2.86f,-6.2f,0,.28f,3.23f,2.91f);
   head.loft(9,20,-7.6f,0,1.0f,2.75f,2.13f,-5.7f,0,1.35f,2.97f,1.68f,-3.2f,0,1.68f,2.55f,1.26f,-1.5f,0,1.55f,1.58f,.23f);
   for(int j=0;j<9;j++){float x=-2.7f+j*.67f;Part h=head.child(x,-7.5f,-1.95f);
    h.loft(9,12,-.85f,0,.28f,.67f,.76f,.4f,-.28f,-.20f,.77f,.67f,1.48f,-.48f,-.57f,.52f,.33f,2.25f+(j%3)*.32f,-.70f,-.4f,.035f,.04f);
   }
   for(int s:new int[]{-1,1}){
    for(int j=0;j<3;j++)head.blade(9,s*(2.1f+j*.27f),-7.1f+j*.75f,.15f+j*.45f,s*(3.4f+j*.11f),-5.2f+j*.9f,1.05f+j*.2f,1.0f);
   }
   for(int i=0;i<2;i++){int s=i==0?-1:1;
    arm[i]=body.child(s*3.57f,.25f,0);
    arm[i].loft(0,18,-.72f,0,0,1.0f,1.14f,.5f,s*.08f,0,1.42f,1.34f,2.7f,0,0,1.15f,1.17f,5.0f,0,0,.91f,.94f);
    elbow[i]=arm[i].child(0,4.9f,0);elbow[i].loft(0,18,-.1f,0,0,.95f,.98f,1.8f,0,0,.92f,.93f,3.9f,0,0,.78f,.80f);
    elbow[i].loft(3,18,3.45f,0,0,.89f,.89f,4.0f,0,0,.93f,.91f,4.25f,0,0,.86f,.85f);
    elbow[i].loft(4,18,4.0f,0,0,.74f,.72f,5.25f,0,-.10f,.82f,.66f,5.8f,0,-.16f,.64f,.52f);
    for(int j=0;j<4;j++)elbow[i].oval(4,-.51f+j*.34f,5.95f,-.15f,.21f,.46f,.29f);
    elbow[i].oval(4,-s*.73f,5.05f,-.24f,.25f,.50f,.30f);
    if(i==1){Part d=elbow[i].child(0,5.55f,-.4f);d.rx=-1.25f;d.loft(5,12,0,0,0,.42f,.43f,2.0f,0,0,.44f,.45f);d.blade(10,0,1.85f,0,0,7.35f,0,1.33f);}
    leg[i]=root.child(s*1.54f,10.8f,0);leg[i].loft(0,18,0,0,0,1.40f,1.43f,2.7f,0,0,1.19f,1.23f,6.0f,0,0,.94f,1.0f);
    knee[i]=leg[i].child(0,5.95f,0);knee[i].loft(0,16,0,0,0,.97f,1.0f,3.65f,0,0,.75f,.84f,5.4f,0,0,.73f,.82f);
    knee[i].loft(5,20,4.75f,0,0,.83f,.89f,6.05f,0,-.43f,1.06f,1.45f,7.2f,0,-.65f,1.05f,1.67f);
    coat[i]=body.child(s*1.32f,7.9f,1.35f);coat[i].loft(0,16,0,0,0,1.40f,.38f,3.4f,s*.28f,.35f,1.65f,.28f,7.5f,s*.50f,.85f,1.57f,.22f,12.0f,s*.95f,1.55f,.06f,.08f);
    coat[i+2]=body.child(s*2.22f,8.1f,.25f);coat[i+2].blade(0,0,0,0,s*1.5f,10.35f,2.4f,2.22f);
   }
  }
  @Override public void setupAnim(Joker e,float limb,float amount,float age,float yaw,float pitch){
   float cast=e.summoning();head.ry=yaw*.01745f;head.rx=pitch*.016f;body.ry=cast*.12f;
   for(int i=0;i<2;i++){int s=i==0?-1:1;float w=(float)Math.cos(limb*.666f+i*Math.PI)*amount;
    arm[i].rx=-w*.65f-(i==1?cast*1.62f:cast*.24f);arm[i].rz=-s*(.10f+(i==1?cast*.24f:0));
    elbow[i].rx=-.15f-Math.max(0,-w)*.25f-(i==1?cast*.68f:0);leg[i].rx=w*.65f;knee[i].rx=Math.max(0,-w)*.46f;
    coat[i].rx=.08f+amount*.38f+cast*.22f+(float)Math.sin(age*.12f+i)*.08f;coat[i].rz=s*.13f;
    coat[i+2].rx=coat[i].rx*.81f;coat[i+2].rz=s*(.12f+amount*.13f);
   }
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<Joker,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.36f);}
  @Override public ResourceLocation getTextureLocation(Joker e){return new ResourceLocation(Noctis.ID,"textures/entity/joker_detailed.png");}
 }
}''')
# Dedicated atlases: do not modify textures used by the other sculpted guests.
def sat(v):return max(0,min(1,v))
def shade(a,f):return tuple(max(0,min(255,round(x*f))) for x in a)
def atlas(name,palette,is_rose):
 W,H=1024,512;pix=bytearray(W*H*4)
 for m,basecolor in palette.items():
  for y in range(128):
   v=sat((y-3)/121)
   for x in range(128):
    u=sat((x-3)/121);f=abs(u-.5);grain=.5+.5*math.sin(u*91+v*16)*math.sin(v*107-u*12)
    c=shade(basecolor,.88+.12*math.cos((u-.5)*math.pi*2)**2)
    if is_rose:
     if m==0:
      sc=(u*17+(.5 if int(v*16)%2 else 0))%1;sv=(v*16)%1
      c=mix(c,(57,35,51),.24*(1-abs(sc-.5)*2)+.15*grain)
      if sv<.065 or (sc<.035 and sv>.12):c=shade(c,.58)
     if m in (2,3,4):
      vein=abs(math.sin((u-.5)*math.pi*8+v*.95));edge=abs(math.sin(u*math.pi*2))
      c=mix(c,(237,66,106),.28*math.exp(-((v-.63)/.22)**2)+.16*edge)
      c=mix(c,(37,10,29),.52*(1-v)**2+.27*(1-vein)**12)
      if abs(u-.5)<.013:c=mix(c,(242,88,121),.42)
      if v>.96:c=mix(c,(79,9,37),.62)
     if m==1:c=mix(c,(112,46,65),.32*math.exp(-((v-.32)/.19)**2))
     if m==12:
      c=mix((251,85,117),(255,218,202),.7*math.exp(-((v-.38)/.17)**2))
      if f<.07:c=(20,8,20)
    else:
     if m in (0,2,3,5):
      c=shade(c,.96+.075*grain)
      if f<.012 and m in (0,2):c=mix(c,(93,94,110),.52)
      if m==3:c=mix(c,(113,115,134),.28*math.exp(-((u-.18)/.045)**2))
      if m==5:c=mix(c,(71,64,78),.32*math.exp(-((v-.18)/.10)**2))
     if m==4:
      c=mix(c,(249,73,78),.30*math.exp(-((u-.35)/.16)**2))
      if abs(v-.18)<.023:c=(82,9,24)
     if m==9:
      f1=(u*8+v*.65)%1;c=mix(c,(81,77,95),.38*math.exp(-((f1-.32)/.11)**2))
     if m==7:
      c=mix(basecolor,(182,121,110),.17*math.exp(-((v-.72)/.13)**2))
      # Angular white domino mask across the face: pointed temples, black eye sockets, gray lip.
      if f<.222 and abs(v-(.49+.30*f))<(.112-.23*f):c=(239,239,235)
      if f<.224 and abs(abs(v-(.49+.30*f))-(.112-.23*f))<.014:c=(35,31,40)
      for ex in (.405,.595):
       dx=(u-ex)/.068;dy=(v-.515+(.044*dx if ex<.5 else -.044*dx))/.066
       if abs(dx)+abs(dy)*.88<1.22:c=(20,18,27)
       if dx*dx+dy*dy<.69:c=(226,225,224)
       if abs(dx)<.34 and dx*dx+dy*dy<.69:c=(79,79,95)
       if abs(dx)<.16 and abs(dy)<.53:c=(21,19,28)
       if (dx+.12)**2+(dy+.21)**2<.045:c=(255,255,255)
      if f<.025 and .65<v<.73:c=mix(c,(163,107,105),.30)
      if f<.055 and abs(v-.84+.012*math.cos(f*45))<.010:c=(128,76,84)
    off=(((m//8)*128+y)*W+(m%8)*128+x)*4;pix[off:off+4]=bytes((*c,255))
 png(assets/'textures/entity'/name,W,H,pix)
atlas('black_rose_sculpted.png',{0:(29,19,34),1:(75,35,53),2:(146,15,51),3:(101,11,38),4:(186,27,67),6:(218,187,174),12:(251,62,98)},True)
atlas('joker_detailed.png',{0:(24,24,32),1:(234,196,174),2:(64,66,79),3:(35,34,45),4:(188,19,40),5:(16,15,23),6:(177,177,190),7:(236,204,180),8:(235,235,233),9:(19,18,26),10:(190,192,202)},False)

# Replace the old mounted travel method for both Synchro Dragons. Vanilla vehicle packets
# transmit the locally controlled position; do not run a second integration on the remote side.
p=java/'SynchroDragon.java';s=p.read_text(encoding='utf-8')
start=s.index('    @Override public void travel(Vec3 v)')
end=s.index('    @Override public boolean wantsToAttack',start)
s=s[:start]+'''    @Override public void travel(Vec3 v){
        if(isAlive()&&getControllingPassenger() instanceof Player rider){
            setYRot(rider.getYRot());yBodyRot=getYRot();yHeadRot=getYRot();setXRot(0);
            setNoGravity(true);resetFallDistance();getNavigation().stop();
            if(isControlledByLocalInstance()){
                double yaw=Math.toRadians(rider.getYRot()),pitch=Math.toRadians(rider.getXRot());
                double f=rider.zza,side=rider.xxa;
                Vec3 direction=new Vec3(-Math.sin(yaw)*Math.cos(pitch)*f+Math.cos(yaw)*side*.68,-Math.sin(pitch)*f,Math.cos(yaw)*Math.cos(pitch)*f+Math.sin(yaw)*side*.68);
                if(direction.lengthSqr()>1)direction=direction.normalize();
                double speed=rose()?.94:1.06;
                Vec3 target=direction.scale(speed);
                if(onGround()&&f>.05&&rider.getXRot()<18)target=target.add(0,.34,0);
                Vec3 next=getDeltaMovement().scale(.68).add(target.scale(.32));
                if(direction.lengthSqr()<.0001&&next.lengthSqr()<.0009)next=Vec3.ZERO;
                setDeltaMovement(next);move(MoverType.SELF,next);
                if(horizontalCollision)setDeltaMovement(new Vec3(0,getDeltaMovement().y,0));
                resetFallDistance();calculateEntityAnimation(false);
            }
            return;
        }
        if(isNoGravity())setNoGravity(false);
        super.travel(v);
    }
'''+s[end:]
s=s.replace('WASD per volare; guarda in alto/basso per salire/scendere; bacchetta di Blaze per il potere.','W per decollare e volare, A/D per spostarti di lato, S per arretrare. Usa il mouse per virare; guarda in alto o in basso mentre premi W per salire o atterrare. Rilascia W per librarti. Bacchetta di Blaze: potere.')
p.write_text(s,encoding='utf-8')

# Quest clues are now legible without spoiling other mysteries.
qtexts={
 'sephiroth':('Un cartello reca il nome dell angelo con una sola ala: scrivi One Winged Angel e rimani nei pressi.','A sign bears the name of the one-winged angel: write One Winged Angel and stay nearby.'),
 'sephiroth_complete':('Quando Sephiroth risponde al richiamo, affrontalo e sconfiggilo per spezzare il suo canto.','When Sephiroth answers the summons, confront and defeat him to silence his song.'),
 'joker':('Di notte cerca il ladro in nero con la maschera bianca. Parlagli a mano vuota: potrebbe affidarti una lettera rossa.','At night seek the thief in black with the white mask. Speak to him empty-handed: he may entrust you with a red letter.'),
 'joker_complete':('La Calling Card richiede cinque vittorie contro creature ostili comuni, come zombie e scheletri. Quando la lettera pulsa, torna da Joker a mano vuota.','The Calling Card demands five victories against ordinary hostile creatures such as zombies and skeletons. When it glows, return to Joker empty-handed.')
}
for idx,lang in enumerate(('it_it','en_us')):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for key,desc in qtexts.items():d['advancement.noctismagic.rituals.'+key+'.description']=desc[idx]
 write_noctis_json_resource(p,d)
edit('Joker.java','Take your time. Cinque ombre custodiscono la strada per il mio covo.','Take your time. La Calling Card reclama cinque ombre: sconfiggi cinque creature ostili, poi torna da me.')
edit('Joker.java','Le Ombre non si sconfiggono da sole.','La Calling Card non e ancora pronta. Sconfiggi altre creature ostili, poi torna qui.')
print('Black Rose and Joker dedicated detailed meshes, improved mounted flight, clarified quest hints.')

# Fix the compile failure from the previous workflow run.
p=java/'DramaGuest.java';s=p.read_text(encoding='utf-8')
if 'import net.minecraft.server.level.ServerPlayer;' not in s and 'import net.minecraft.server.level.*;' not in s:
 s=s.replace('package it.noctis.magic;', 'package it.noctis.magic;\nimport net.minecraft.server.level.ServerPlayer;',1)
 p.write_text(s,encoding='utf-8')


# More mystery-driven quest clues, with vampire pact and Cthulhu ritual tracking.
# Miaugusto is already tracked by RitualQuests from upgrade_165.
edit('CthulhuRitual.java','if(!l.addFreshEntity(boss))return;','if(!l.addFreshEntity(boss))return;\n        RitualQuests.summon(p,boss,"cthulhu");')
edit('RitualQuests.java','&&!id.equals("exodia"))return;','&&!id.equals("exodia")&&!id.equals("cthulhu"))return;')
edit('Vampire.java','String key=friendKey(p);int points=friendship.getInt(key);','RitualQuests.award(p,"vampire");\n            String key=friendKey(p);int points=friendship.getInt(key);')
edit('VampireLife.java','Noctis.data(p).putBoolean("vampire",true);marker(p,VAMPIRISM.get());','Noctis.data(p).putBoolean("vampire",true);marker(p,VAMPIRISM.get());\n        RitualQuests.award(p,"vampire");RitualQuests.complete(p,"vampire");')
base=res/'data/noctismagic/advancements/rituals'
for ident,icon,parent,xp in [
 ('vampire','minecraft:bat_spawn_egg','root',50),
 ('vampire_complete','noctismagic:blood_bucket','vampire',200),
 ('cthulhu','minecraft:ink_sac','root',75),
 ('cthulhu_complete','minecraft:nether_star','cthulhu',450)]:
 write_noctis_json_resource(base/(ident+'.json'),{'parent':'noctismagic:rituals/'+parent,'display':{'icon':{'item':icon},'title':{'translate':'advancement.noctismagic.rituals.'+ident+'.title'},'description':{'translate':'advancement.noctismagic.rituals.'+ident+'.description'},'frame':'challenge' if ident=='cthulhu_complete' else 'goal','show_toast':True,'announce_to_chat':True,'hidden':False},'criteria':{'ritual':{'trigger':'minecraft:impossible'}},'rewards':{'experience':xp}})
mysteries={
 'sephiroth':('Una sola ala','One wing','Incidi un nome nel legno. Non tutti gli angeli possiedono due ali.','Carve a name into wood. Not every angel has two wings.'),
 'sephiroth_complete':('Il silenzio dopo il canto','Silence after the song','Fa che il canto dell angelo si spenga per sempre.','Let the angel song fall silent forever.'),
 'joker':('Il RubaCuori gentiluomo','The gentleman heart thief','Cerca un RubaCuori gentiluomo: al calar della notte, il suo sorriso si cela dietro una maschera bianca.','Seek a gentleman heart thief: at nightfall, his smile hides behind a white mask.'),
 'joker_complete':('Il cuore rubato','The stolen heart','Cinque ombre oscurano la lettera scarlatta. Quando pulsa, cerca di nuovo il suo mittente.','Five shadows darken the scarlet letter. When it pulses, seek its sender again.'),
 'vampire':('Un cortese sconosciuto','A courteous stranger','Non tutti i figli della notte desiderano farti del male. Alcuni preferiscono le buone maniere.','Not all children of the night wish you harm. Some prefer good manners.'),
 'vampire_complete':('Il patto scarlatto','The scarlet pact','Dieci doni del colore della vita possono conquistare una fiducia immortale. Una scelta ti attende.','Ten gifts the color of life may earn immortal trust. A choice awaits you.'),
 'miaugusto':('Nove vite, cinque legami','Nine lives, five bonds','Conquista cinque piccoli cuori felini. Una fame ben piu grande potrebbe risvegliarsi.','Win five little feline hearts. A far greater hunger may awaken.'),
 'miaugusto_complete':('Il re delle crocchette','The kibble king','Nemmeno un sovrano dalle nove vite puo banchettare in eterno.','Even a nine-lived king cannot feast forever.'),
 'cthulhu':('Non farlo arrabbiare','Do not anger him','Il piccolo gentiluomo dagli otto tentacoli ti avvertira una volta. Ascoltarlo sarebbe saggio.','The little gentleman with eight tentacles will warn you once. Listening would be wise.'),
 'cthulhu_complete':('Il padre degli abissi','Father of the abyss','Quando il figlio grida, gli abissi rispondono. Riuscirai a farli tacere?','When the son cries out, the abyss answers. Can you silence it?')
}
for idx,lang in enumerate(('it_it','en_us')):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for key,t in mysteries.items():
  d['advancement.noctismagic.rituals.'+key+'.title']=t[idx]
  d['advancement.noctismagic.rituals.'+key+'.description']=t[idx+2]
 write_noctis_json_resource(p,d)
edit('Joker.java','Take your time. La Calling Card reclama cinque ombre: sconfiggi cinque creature ostili, poi torna da me.','Take your time. Cinque ombre gravano sulla lettera. Quando avra ripreso vita, sai dove trovarmi.')
edit('Joker.java','La Calling Card non e ancora pronta. Sconfiggi altre creature ostili, poi torna qui.','Le ombre non hanno ancora restituito il cuore della lettera.')
print('Mystery quest journal expanded: vampire blood pact, Miaugusto, Cthulhu and subtler Joker/Sephiroth hints.')


# Faputa: taller and broader, with squared, firm shoulder girdle and more restrained shoulder swing.
edit('FaputaSculptedClient.java','p.scale(.88f,.88f,.88f);','p.scale(1.09f,1.10f,1.04f);')
edit('FaputaSculptedClient.java','super(c,new M(),.39f);','super(c,new M(),.48f);')
edit('FaputaSculptedClient.java','-2.2f,0,0,1.55f,1.32f,-.8f,0,0,2.48f,1.65f,2.0f,0,0,2.30f,1.56f,4.8f,0,0,1.87f,1.44f','-2.2f,0,0,1.75f,1.43f,-1.25f,0,0,3.05f,1.87f,-.5f,0,0,3.28f,1.95f,1.6f,0,0,3.02f,1.80f,3.1f,0,0,2.52f,1.62f,4.8f,0,0,2.02f,1.52f')
edit('FaputaSculptedClient.java','s*1.32f,.05f,-1.48f','s*1.62f,.05f,-1.76f')
edit('FaputaSculptedClient.java','int k=i*2+j;Part arm=arms[k]=body.child(s*(j==0?2.30f:2.04f),j==0?.1f:2.45f,j==0?.28f:.72f);','''int k=i*2+j;Part arm=arms[k]=body.child(s*(j==0?3.05f:2.60f),j==0?-.10f:2.45f,j==0?.28f:.72f);
     if(j==0){
      Part shoulder=body.child(s*2.57f,-.25f,.20f);
      shoulder.loft(0,24,-1.10f,0,0,.70f,.83f,-.60f,s*.20f,0,1.05f,1.18f,.25f,s*.42f,0,1.14f,1.24f,1.10f,s*.32f,0,.92f,1.00f,1.75f,s*.15f,0,.62f,.72f);
     }''')
edit('FaputaSculptedClient.java','-.45f,0,0,.67f,.73f,.6f,0,0,.80f,.85f,2.7f,s*.28f,0,.67f,.69f,3.35f,s*.32f,0,.54f,.56f','-.45f,0,0,.79f,.82f,.6f,0,0,1.00f,1.03f,2.7f,s*.28f,0,.79f,.80f,3.35f,s*.32f,0,.59f,.63f')
edit('FaputaSculptedClient.java','body.y=8+(float)Math.sin(limb*1.32)*move*.36f;body.rx=rage?.17f:0;','body.y=8+(float)Math.sin(limb*1.32)*move*.22f;body.rx=rage?.09f:0;')
edit('FaputaSculptedClient.java','arms[k].rz=-s*(j==0?.24f:.57f)-(rage?s*.22f:0);arms[k].rx=-w*(j==0?.5f:-.33f)','arms[k].rz=-s*(j==0?.32f:.49f)-(rage?s*.12f:0);arms[k].rx=-w*(j==0?.26f:-.24f)')
# Match the larger body with a wider/taller collision box without changing other MoonGuests.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
s,n=re.subn(r'(FAPUTA=ENTITIES\.register\("faputa".*?\.sized\()[^)]*(\))',r'\g<1>1.10f,2.05f\2',s,count=1)
assert n==1,'Faputa entity dimensions not found'
p.write_text(s,encoding='utf-8')
print('Faputa enlarged: broader rigid shoulder girdle, stronger upper arms and matched collision dimensions.')


# C.C. and Lelouch: occasional reciprocal non-combat affection, synchronized to both clients.
edit('DramaGuest.java','UUID partner;int cd=40,dance=0,pizzaCd=0;','UUID partner;int cd=40,dance=0,pizzaCd=0;\n    private int affectionTime=0,affectionMode=0,affectionCooldown=900,approachTime=0;')
edit('DramaGuest.java','return dance==0&&kind()!=2&&canWanderTogether()&&super.canUse();','return affectionTime==0&&approachTime==0&&dance==0&&kind()!=2&&canWanderTogether()&&super.canUse();')
edit('DramaGuest.java','return dance==0&&kind()!=2&&canWanderTogether()&&super.canContinueToUse();','return affectionTime==0&&approachTime==0&&dance==0&&kind()!=2&&canWanderTogether()&&super.canContinueToUse();')
edit('DramaGuest.java','    @Override public void tick(){super.tick();','''    public int affectionMode(){return affectionTime>0?affectionMode:0;}
    public float affectionProgress(){return affectionTime<=0?0:Math.min(1f,Math.min((72-affectionTime)/12f,affectionTime/12f));}
    private void facePartner(DramaGuest q){
        double dx=q.getX()-getX(),dz=q.getZ()-getZ();
        if(dx*dx+dz*dz<.001)return;
        float yaw=(float)(Math.atan2(dz,dx)*180/Math.PI)-90;
        setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);setXRot(0);
    }
    private boolean safeAffection(DramaGuest q){
        return q.isAlive()&&isAlive()&&onGround()&&q.onGround()&&!isInWater()&&!q.isInWater()&&hurtTime==0&&q.hurtTime==0&&getTarget()==null&&q.getTarget()==null&&Math.abs(getY()-q.getY())<.38&&hasLineOfSight(q);
    }
    private void beginAffection(ServerLevel l,DramaGuest q){
        int mode=random.nextBoolean()?1:2;affectionMode=q.affectionMode=mode;
        affectionTime=q.affectionTime=72;approachTime=q.approachTime=0;
        affectionCooldown=q.affectionCooldown=1800+random.nextInt(2400);
        getNavigation().stop();q.getNavigation().stop();facePartner(q);q.facePartner(this);
        l.broadcastEntityEvent(this,(byte)(95+mode));l.broadcastEntityEvent(q,(byte)(95+mode));
    }
    private boolean affectionTick(ServerLevel l){
        if(kind()==0)return false;
        if(affectionCooldown>0)affectionCooldown--;
        DramaGuest q=partner!=null&&l.getEntity(partner) instanceof DramaGuest other?other:null;
        if(affectionTime>0){
            if(q==null||!safeAffection(q)||distanceTo(q)>1.55){
                affectionTime=0;affectionMode=0;approachTime=0;l.broadcastEntityEvent(this,(byte)98);
                if(q!=null&&q.affectionTime>0){q.affectionTime=0;q.affectionMode=0;l.broadcastEntityEvent(q,(byte)98);}
                return false;
            }
            getNavigation().stop();facePartner(q);setDeltaMovement(0,getDeltaMovement().y,0);
            if(kind()==1&&affectionTime==46)l.sendParticles(ParticleTypes.HEART,(getX()+q.getX())*.5,Math.max(getY(),q.getY())+1.95,(getZ()+q.getZ())*.5,3,.17,.15,.17,.025);
            return true;
        }
        if(q==null||!safeAffection(q)){approachTime=0;return false;}
        if(kind()==2&&q.approachTime>0){getNavigation().stop();facePartner(q);return true;}
        if(kind()!=1)return false;
        if(approachTime<=0){
            if(affectionCooldown>0||q.affectionCooldown>0||tickCount%100!=0||distanceTo(q)>3.4||random.nextInt(3)!=0)return false;
            approachTime=65;
        }
        if(--approachTime<=0){affectionCooldown=300;return false;}
        getNavigation().stop();q.getNavigation().stop();facePartner(q);q.facePartner(this);
        double dist=distanceTo(q);
        if(dist<=.92){beginAffection(l,q);return true;}
        Vec3 v=q.position().subtract(position());v=new Vec3(v.x,0,v.z).normalize().scale(Math.min(.075,Math.max(.0,dist-.84)));
        if(l.noCollision(this,getBoundingBox().move(v)))move(MoverType.SELF,v);
        else{approachTime=0;affectionCooldown=300;return false;}
        return true;
    }
    @Override public void tick(){super.tick();if(affectionTime>0)affectionTime--;''')
edit('DramaGuest.java','if(tickCount%10!=0)return;','if(affectionTick(l))return;\n        if(tickCount%10!=0)return;')
edit('DramaGuest.java','if(id==94){dance=60;return;}','if(id==96||id==97){affectionMode=id-95;affectionTime=72;return;}if(id==98){affectionTime=0;affectionMode=0;return;}if(id==94){dance=60;return;}')
# Layer a distinct kiss or embrace pose over the current articulated walk cycles.
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
a='            head.ry=yaw*.01745f;head.rx=pitch*.014f;head.rz=cc?.025f:0;'
assert a in s
s=s.replace(a,a+'\n            float affection=e.affectionProgress();int affectionMode=e.affectionMode();\n            body.rx=0;root.rx=0;root.ry=0;root.rz=0;head.z=0;',1)
a='            for(int i=0;i<hair.size();i++)hair.get(i).rx=amount*.13f+(float)Math.sin(age*.12+i*.55f)*.025f;'
assert a in s
s=s.replace(a,a+'''
            for(int i=0;i<2;i++){arms[i].ry=0;fore[i].ry=0;fore[i].rz=0;}
            if(affectionMode!=0&&affection>0){
                float f=affection;head.ry=(cc?.10f:-.10f)*f;head.rz=(cc?-.13f:.12f)*f;
                head.rx=(cc?-.16f:.12f)*f;root.rx=(cc?-.085f:-.035f)*f;head.z=-.40f*f;
                for(int i=0;i<2;i++){
                    int side=i==0?-1:1;legs[i].rx=0;knees[i].rx=0;
                    if(affectionMode==2){
                        // Lelouch reaches around C.C.; she returns the gesture more gently.
                        arms[i].rx=(cc?-.95f:-1.37f)*f;arms[i].rz=-side*.24f*f;arms[i].ry=-side*.30f*f;
                        fore[i].rx=(cc?-.55f:-.76f)*f;fore[i].rz=side*.46f*f;
                    }else{
                        // C.C. leans toward him and lifts one hand; he stays relaxed.
                        arms[i].rx=(cc?(i==1?-1.30f:-.30f):-.38f)*f;arms[i].rz=-side*.13f*f;
                        fore[i].rx=(cc&&i==1?-.95f:-.22f)*f;
                    }
                }
            }''',1)
p.write_text(s,encoding='utf-8')
print('Lelouch and C.C. spontaneous paired kiss/hug animations with cooldown and safety checks.')


# Adult cabaret performers: three non-explicit theatrical poses, manual and occasional idle.
edit('CabaretHealer.java','private int greeting;','''private int greeting,stagePose,stageTime,stageCooldown=200;
    public int stagePose(){return stageTime>0?stagePose:0;}
    private void startStagePose(ServerLevel l){
        stagePose=stagePose%3+1;stageTime=110;stageCooldown=600+random.nextInt(800);
        getNavigation().stop();l.broadcastEntityEvent(this,(byte)(100+stagePose));
    }''')
edit('CabaretHealer.java','if(h==InteractionHand.MAIN_HAND&&s.isEmpty()){','''if(h==InteractionHand.MAIN_HAND&&s.isEmpty()){
                if(p.isShiftKeyDown()){
                    if(level() instanceof ServerLevel l)startStagePose(l);
                    return InteractionResult.sidedSuccess(level().isClientSide);
                }''')
edit('CabaretHealer.java','if(id==81){greeting=30;return;}','if(id>=101&&id<=103){stagePose=id-100;stageTime=110;return;}if(id==104){stageTime=0;return;}if(id==81){greeting=30;return;}')
edit('CabaretHealer.java','if(greeting>0)greeting--;','''if(greeting>0)greeting--;
        if(stageTime>0)stageTime--;if(stageCooldown>0)stageCooldown--;
        if(level() instanceof ServerLevel l){
            if(stageTime>0){
                if(hurtTime>0||isInWater()||!onGround()){stageTime=0;l.broadcastEntityEvent(this,(byte)104);}
                else{getNavigation().stop();setDeltaMovement(0,getDeltaMovement().y,0);}
            }else if(stageCooldown==0&&greeting==0&&onGround()&&!isInWater()&&hurtTime==0&&getDeltaMovement().horizontalDistanceSqr()<.0025&&random.nextInt(80)==0){startStagePose(l);}
        }''')
edit('CabaretClient.java','body.zRot=(float)Math.sin(limb*.7)*amount*.045f;','body.zRot=(float)Math.sin(limb*.7)*amount*.045f;body.xRot=0;body.yRot=0;')
edit('CabaretClient.java','legs[i].xRot=step*.7f;locks[i].zRot','legs[i].xRot=step*.7f;legs[i].zRot=0;legs[i].yRot=0;arms[i].yRot=0;locks[i].zRot')
edit('CabaretClient.java','locks[i].xRot=-amount*.12f;\n            }','''locks[i].xRot=-amount*.12f;
            }
            int pose=e.stagePose();
            if(pose>0){
                float sway=(float)Math.sin(age*.07f)*.035f;
                head.zRot=pose==2?-.14f:.12f;head.yRot=yaw*.008f;body.zRot=pose==2?-.12f:.10f;
                for(int i=0;i<2;i++){legs[i].xRot=0;arms[i].xRot=0;}
                if(pose==1){ // hand at hip and playful wave
                    arms[0].zRot=.55f;arms[0].xRot=-.32f;arms[1].xRot=-1.25f+sway;arms[1].zRot=-.38f;
                    legs[0].zRot=.13f;legs[1].zRot=-.08f;
                }else if(pose==2){ // cabaret flourish and crossed-foot stance
                    body.yRot=.22f;arms[0].xRot=-2.20f;arms[0].zRot=.35f;arms[1].zRot=-.49f;
                    legs[0].yRot=.16f;legs[0].xRot=-.14f;legs[1].zRot=.10f;
                }else{ // two-arm stage flourish
                    body.yRot=-.18f;head.xRot=-.10f;arms[0].zRot=1.03f+sway;arms[1].zRot=-1.03f-sway;
                    arms[0].xRot=-.44f;arms[1].xRot=-.44f;legs[1].xRot=-.22f;
                }
            }''')
# Separate rounded dress geometry and strongly contrasting tailored materials for adult Waifu.
edit('GlamourClient.java','e.registerEntityRenderer(Noctis.WAIFU.get(),c->new LadyRenderer(c,0,"waifu"));','')
write('WaifuTailoredClient.java','''package it.noctis.magic;
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
public class WaifuTailoredClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.WAIFU.get(),R::new);}
 static class M extends EntityModel<Admirer>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=root.child(0,-1,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],knees=new Part[2],locks=new Part[2],ribbons=new Part[2];
  M(){
   // Neck and shoulders use a distinct warm skin material; the opaque bodice is a raised outer shell.
   body.loft(0,24,-1.15f,0,0,.95f,1.0f,.15f,0,0,2.6f,1.38f,1.6f,0,0,2.85f,1.65f);
   body.loft(1,32,.65f,0,0,2.83f,1.72f,2.0f,0,0,3.05f,2.10f,4.8f,0,0,2.75f,1.77f,6.7f,0,0,1.91f,1.48f,8.25f,0,0,2.15f,1.64f,10,0,0,3.60f,2.5f,12.5f,0,.28f,4.2f,2.9f);
   // Sculpted, fully clothed hourglass volumes, not skin-colored geometry.
   for(int side:new int[]{-1,1}){
    body.oval(1,side*1.97f,2.9f,-1.42f,2.20f,2.34f,2.14f);
    body.oval(1,side*2.05f,10.9f,1.40f,2.55f,2.15f,2.08f);
    body.blade(2,side*2.50f,1.1f,-1.49f,side*1.25f,-.45f,-.95f,.34f);
   }
   body.loft(2,32,6.6f,0,0,1.98f,1.56f,7.0f,0,0,2.01f,1.58f,7.45f,0,0,2.03f,1.6f);
   body.loft(3,32,10.4f,0,.4f,3.85f,3.03f,12.3f,0,.46f,4.45f,3.15f,14.4f,0,.45f,4.72f,3.20f);
   body.loft(2,32,14.0f,0,.45f,4.68f,3.20f,14.4f,0,.45f,4.75f,3.26f);
   body.oval(4,0,7.03f,-1.62f,.45f,.40f,.24f);
   head.loft(5,40,-7.4f,0,.1f,1.45f,1.5f,-6.6f,0,0,2.72f,2.5f,-5.1f,0,0,3.12f,2.75f,-3.4f,0,-.06f,3.08f,2.65f,-1.7f,0,-.15f,2.4f,2.1f,-.5f,0,-.21f,1.45f,1.45f,0,0,-.24f,.58f,.68f);
   head.loft(6,24,-8.65f,0,.1f,.45f,.60f,-8.35f,0,.1f,2.38f,2.2f,-7.4f,0,.15f,3.37f,3.0f,-6.1f,0,.25f,3.45f,3.03f);
   Part hair=head.child(0,-6.6f,1.9f);hair.loft(6,24,-.6f,0,0,2.8f,1.7f,4,0,.5f,3.4f,1.6f,9,0,1.3f,3.5f,1.45f,15,0,1.8f,2.4f,.55f);
   for(int j=0;j<6;j++){Part p=head.child(-2.65f+j*1.03f,-7.5f,-2.2f);p.loft(6,12,-.4f,0,0,.75f,.65f,1.1f,-.27f,-.3f,.82f,.56f,2.8f+(j%2)*.45f,-.62f,-.35f,.035f,.05f);}
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    locks[i]=head.child(s*2.8f,-5.9f,.1f);locks[i].loft(6,16,-.5f,0,0,.78f,1.10f,2,s*.4f,-.3f,.9f,1.07f,8,s*.6f,.15f,.76f,.9f,14,s*.45f,.65f,.05f,.07f);
    arms[i]=root.child(s*3.55f,.7f,0);arms[i].loft(0,20,-.8f,0,0,.82f,.96f,.8f,0,0,1.15f,1.15f,4.5f,0,0,.72f,.76f);
    fore[i]=arms[i].child(0,4.45f,0);fore[i].loft(0,18,0,0,0,.74f,.77f,2,0,0,.80f,.80f,4,0,0,.55f,.58f);
    fore[i].loft(3,20,2.4f,0,0,.78f,.78f,3.8f,0,0,.66f,.67f);fore[i].oval(0,0,4.8f,0,.63f,.86f,.54f);
    legs[i]=root.child(s*1.76f,12.4f,0);legs[i].loft(3,20,0,0,0,1.65f,1.55f,3.2f,0,0,1.27f,1.27f,5.5f,0,0,.91f,.96f);
    knees[i]=legs[i].child(0,5.4f,0);knees[i].loft(3,20,0,0,0,.94f,.95f,3.6f,0,0,.69f,.77f,4.9f,0,0,.67f,.72f);
    knees[i].loft(7,20,3.3f,0,0,.76f,.82f,5.0f,0,-.42f,1.05f,1.45f,6.05f,0,-.45f,1.08f,1.5f);
    ribbons[i]=body.child(s*2.8f,7.1f,1.55f);ribbons[i].blade(2,0,0,0,s*1.4f,7.0f,1.3f,.92f);
   }
  }
  @Override public void setupAnim(Admirer e,float limb,float amount,float age,float yaw,float pitch){
   boolean sit=e.isInSittingPose();body.zRotUnusedDummy();
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<Admirer,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.46f);}
  @Override public ResourceLocation getTextureLocation(Admirer e){return new ResourceLocation(Noctis.ID,"textures/entity/waifu_tailored.png");}
 }
}'''.replace('body.zRotUnusedDummy();','''body.rz=(float)Math.sin(limb*.7f)*amount*.035f;body.rx=sit?-.06f:0;head.ry=yaw*.01745f;head.rx=pitch*.015f;
   for(int i=0;i<2;i++){int side=i==0?-1:1;float step=(float)Math.cos(limb*.666f+i*Math.PI)*amount;
    arms[i].rx=-step*.52f;arms[i].rz=-side*.12f;fore[i].rx=-.10f-Math.max(0,step)*.28f;
    legs[i].rx=sit?-1.35f:step*.61f;knees[i].rx=sit?.12f:Math.max(0,-step)*.34f;
    locks[i].rx=amount*.15f+(float)Math.sin(age*.13f+i)*.035f;ribbons[i].rx=amount*.30f+(float)Math.sin(age*.12f+i)*.06f;
   }'''))
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(235,190,165),(99,22,75),(231,137,190),(59,24,57),(220,183,122),(235,190,165),(59,28,59),(27,19,31)]
for m,b in enumerate(pal):
 for yy in range(128):
  v=sat((yy-3)/121)
  for xx in range(128):
   u=sat((xx-3)/121);f=abs(u-.5);grain=.5+.5*math.sin(u*97+v*13)*math.sin(v*82)
   c=shade(b,.86+.14*math.cos((u-.5)*math.pi*2)**2)
   if m in (1,3,7):
    c=mix(c,(177,66,129),.20*math.exp(-((u-.30)/.12)**2)+.075*grain)
    if f<.009:c=mix(c,(234,130,183),.45)
   if m==2:c=mix(c,(252,201,225),.32*math.sin(u*math.pi)**2)
   if m==6:c=mix(c,(135,64,116),.34*math.exp(-(((u*8+v*.55)%1-.30)/.12)**2))
   if m==5:
    for ex in (.405,.595):
     dx=(u-ex)/.060;dy=(v-.52)/.096;d=dx*dx+dy*dy
     if d<1:c=(44,24,43)
     if d<.77:c=(251,242,239)
     if abs(dx)<.40 and d<.78:c=(145,55,160)
     if abs(dx)<.16 and abs(dy)<.69:c=(36,16,38)
     if (dx+.15)**2+(dy+.22)**2<.065:c=(255,255,255)
    if f<.055 and abs(v-.84)<.013:c=(157,53,87)
   off=(((m//8)*128+yy)*W+(m%8)*128+xx)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/waifu_tailored.png',W,H,pix)
print('Cabaret stage poses and separate fully clothed Waifu mesh with contrasting dress and skin.')


# Lucy: angular anime silhouette, original-style netrunner jacket, occasional smoking animation.
edit('MoonGuest.java','public MoonGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}','public MoonGuest(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}\n    private int smokeTicks=0,smokeCooldown=700;public int smokeTicks(){return smokeTicks;}')
edit('MoonGuest.java','super.tick();if(pose>0)pose--;','super.tick();if(smokeTicks>0)smokeTicks--;if(smokeCooldown>0)smokeCooldown--;if(pose>0)pose--;')
edit('MoonGuest.java','}else if(k==1){\n            if(tickCount%100','''}else if(k==1){
            boolean calm=onGround()&&!isInWater()&&hurtTime==0&&getTarget()==null;
            if(smokeTicks>0&&!calm){smokeTicks=0;l.broadcastEntityEvent(this,(byte)111);}
            if(smokeTicks==0&&smokeCooldown==0&&calm&&getDeltaMovement().horizontalDistanceSqr()<.003&&random.nextInt(60)==0){
                smokeTicks=150;smokeCooldown=1300+random.nextInt(2000);l.broadcastEntityEvent(this,(byte)110);
            }
            if(smokeTicks>0){
                getNavigation().stop();setDeltaMovement(0,getDeltaMovement().y,0);
                Vec3 at=getEyePosition().add(getLookAngle().scale(.35)).add(0,-.20,0);
                if(smokeTicks==122){l.playSound(null,blockPosition(),SoundEvents.FLINTANDSTEEL_USE,net.minecraft.sounds.SoundSource.NEUTRAL,.4f,1.15f);l.sendParticles(ParticleTypes.SMALL_FLAME,at.x,at.y,at.z,2,.025,.025,.025,.01);}
                if(smokeTicks<122&&smokeTicks%8==0)l.sendParticles(ParticleTypes.SMOKE,at.x,at.y,at.z,2,.025,.045,.025,.012);
            }
            if(tickCount%100''')
edit('MoonGuest.java','if(id==118||id==119){pose=24;','if(id==110){smokeTicks=150;return;}if(id==111){smokeTicks=0;return;}if(id==118||id==119){pose=24;')
edit('MoonGuest.java','return owner==null&&getTarget()==null&&super.canUse();','return smokeTicks==0&&owner==null&&getTarget()==null&&super.canUse();')
edit('MoonGuest.java','return owner==null&&getTarget()==null&&super.canContinueToUse();','return smokeTicks==0&&owner==null&&getTarget()==null&&super.canContinueToUse();')
edit('LucySculptedClient.java','final List<Part> strands=new ArrayList<>(); final Part longlock;','final List<Part> strands=new ArrayList<>(); final Part longlock;\n  final Part cigarette=new Part(.48f,-1.6f,-2.12f),lighter=new Part(.1f,5.1f,-.65f);')
edit('LucySculptedClient.java','head.loft(6,40,','head.loft(6,20,')
edit('LucySculptedClient.java','-3.0f,0,-.1f,2.95f,2.56f,-1.55f,0,-.16f,2.25f,2.08f,-.45f,0,-.25f,1.15f,1.33f','-3.0f,0,-.1f,2.92f,2.54f,-1.55f,0,-.16f,2.08f,1.99f,-.45f,0,-.25f,.95f,1.21f')
edit('LucySculptedClient.java','head.loft(9,36,','head.loft(9,18,')
edit('LucySculptedClient.java','back.loft(10,28,','back.loft(10,14,')
edit('LucySculptedClient.java','q.loft(9,18,','q.loft(9,8,')
edit('LucySculptedClient.java','longlock.loft(12,24,','longlock.loft(12,10,')
edit('LucySculptedClient.java','body.loft(0,32,','body.loft(0,20,')
edit('LucySculptedClient.java','body.blade(3,0,1.3f,-1.83f,0,4.7f,-1.9f,.28f);','''body.blade(3,0,1.3f,-1.83f,0,4.7f,-1.9f,.28f);
   body.blade(2,-1.13f,1.0f,-1.89f,-.22f,2.7f,-2.05f,.23f);
   body.blade(2,1.13f,1.0f,-1.89f,.22f,2.7f,-2.05f,.23f);
   for(int s:new int[]{-1,1}){
    body.blade(5,s*2.7f,2.4f,-.65f,s*1.8f,5.8f,-1.62f,.43f);
    body.blade(2,s*1.5f,6.5f,-1.50f,s*.65f,7.7f,-1.60f,.28f);
    body.blade(4,s*2.9f,1.2f,.15f,s*3.3f,4.6f,.35f,1.25f);
   }
   body.oval(3,0,5.15f,-1.54f,.39f,.22f,.09f);''')
edit('LucySculptedClient.java','arms[i].loft(4,22,1.3f,0,0,1.32f,1.32f,2.1f,0,0,1.53f,1.45f,4.2f,0,0,1.3f,1.31f,5.1f,0,0,1.12f,1.1f);','''arms[i].loft(4,12,1.3f,0,0,1.45f,1.43f,2.1f,0,0,1.76f,1.65f,4.2f,0,0,1.48f,1.45f,5.1f,0,0,1.16f,1.14f);
    arms[i].blade(5,s*.8f,2.0f,-1.24f,s*.78f,4.3f,-1.2f,.32f);
    arms[i].blade(3,-s*.65f,2.1f,-1.20f,-s*.58f,4.6f,-1.15f,.22f);''')
edit('LucySculptedClient.java','fore[i].loft(4,20,-.2f,0,0,1.15f,1.13f,1.55f,0,0,1.27f,1.22f,3.95f,0,0,.79f,.81f);','''fore[i].loft(4,12,-.2f,0,0,1.26f,1.22f,1.55f,0,0,1.42f,1.35f,3.95f,0,0,.79f,.81f);
    fore[i].blade(5,s*.72f,.4f,-1.05f,s*.48f,3.45f,-.83f,.32f);''')
edit('LucySculptedClient.java','legs[i].loft(13,22,-.25f,0,0,1.51f,1.47f,2.35f,0,0,1.43f,1.32f,5.8f,0,0,.96f,.98f);','''legs[i].loft(4,16,-.25f,0,0,1.56f,1.49f,1.5f,0,0,1.50f,1.41f,2.2f,0,0,1.43f,1.32f);
    legs[i].loft(13,16,2.18f,0,0,1.39f,1.29f,3.0f,0,0,1.28f,1.20f,5.8f,0,0,.96f,.98f);
    legs[i].loft(5,16,2.2f,0,0,1.45f,1.37f,2.55f,0,0,1.42f,1.34f);''')
edit('LucySculptedClient.java','  @Override public void setupAnim(MoonGuest e,','''  @Override public void setupAnim(MoonGuest e,''')
edit('LucySculptedClient.java','   for(int i=0;i<strands.size();i++)strands.get(i).rx=(float)Math.sin(age*.10+i*.6)*.009f;','''   for(int i=0;i<strands.size();i++)strands.get(i).rx=(float)Math.sin(age*.10+i*.6)*.009f;
   int sm=e.smokeTicks();head.children.remove(cigarette);fore[1].children.remove(lighter);
   if(sm>0){
    if(cigarette.faces.isEmpty()){
      cigarette.rx=-(float)Math.PI/2;cigarette.loft(14,10,0,0,0,.105f,.105f,1.50f,0,0,.105f,.105f);
      cigarette.loft(15,10,1.50f,0,0,.11f,.11f,1.78f,0,0,.08f,.08f);
      lighter.loft(3,8,-.6f,0,0,.37f,.23f,.30f,0,0,.37f,.23f,.45f,0,0,.30f,.20f);
      lighter.loft(5,8,-.86f,0,0,.31f,.22f,-.60f,0,0,.33f,.23f);
    }
    head.children.add(cigarette);
    float raise=sm>112?Math.min(1,(150-sm)/10f):sm>60&&sm<83?.88f:.15f;
    arms[1].rx=-.40f-raise*.95f;arms[1].rz=-.20f;fore[1].rx=-.18f-raise*1.32f;
    head.rx=-.08f-raise*.12f;head.ry=0;
    if(sm>112)fore[1].children.add(lighter);
   }''')
# Add two independent texture swatches for the cigarette to the existing custom Lucy atlas.
p=assets/'textures/entity/lucy_sculpted.png';blob=p.read_bytes();i=8;compressed=b''
while i<len(blob):
 size=struct.unpack('>I',blob[i:i+4])[0];typ=blob[i+4:i+8];data=blob[i+8:i+8+size];i+=size+12
 if typ==b'IDAT':compressed+=data
raw=zlib.decompress(compressed);W,H=1024,512;stride=W*4+1
assert len(raw)==H*stride and all(raw[y*stride]==0 for y in range(H))
pix=bytearray(b''.join(raw[y*stride+1:(y+1)*stride] for y in range(H)))
for tile,col in [(14,(237,229,213)),(15,(188,61,27))]:
 for yy in range(128):
  for xx in range(128):
   c=shade(col,.78+.22*math.sin(xx/127*math.pi))
   if tile==14 and yy<22:c=(170,123,77)
   if tile==15 and yy>60:c=(248,101,40)
   off=(((tile//8)*128+yy)*W+(tile%8)*128+xx)*4;pix[off:off+4]=bytes((*c,255))
png(p,W,H,pix)

# Friendly vampire: a rare idle red-liquid goblet, rendered as an independent held prop.
edit('Vampire.java','private int bowTicks=0;','''private int bowTicks=0,gobletTicks=0,gobletCooldown=500;
        public int gobletTicks(){return gobletTicks;}
        private void gobletTick(net.minecraft.server.level.ServerLevel l){
            if(gobletCooldown>0)gobletCooldown--;
            if(gobletTicks>0&&(hurtTime>0||bowTicks>0||isInWater()||getTarget()!=null)){
                gobletTicks=0;l.broadcastEntityEvent(this,(byte)64);
            }
            if(gobletTicks==0&&gobletCooldown==0&&onGround()&&!isInWater()&&hurtTime==0&&bowTicks==0&&getTarget()==null&&getDeltaMovement().horizontalDistanceSqr()<.003&&random.nextInt(55)==0){
                gobletTicks=180;gobletCooldown=1600+random.nextInt(2200);l.broadcastEntityEvent(this,(byte)63);
            }
        }''')
edit('Vampire.java','if(id==61){bowTicks=32;return;}','if(id==63){gobletTicks=180;return;}if(id==64){gobletTicks=0;return;}if(id==61){bowTicks=32;gobletTicks=0;return;}')
edit('Vampire.java','if(bowTicks>0)bowTicks--;','if(bowTicks>0)bowTicks--;if(gobletTicks>0)gobletTicks--;')
# Run the goblet logic after the established ServerLevel guard.
edit('Vampire.java','if(bowTicks>0){getNavigation().stop();return;}','gobletTick(l);if(bowTicks>0){getNavigation().stop();return;}')
edit('Client.java','rightArm.xRot=b*.7f;leftArm.xRot=b*.7f;rightArm.zRot=-.12f;leftArm.zRot=.12f;','''rightArm.xRot=b*.7f;leftArm.xRot=b*.7f;rightArm.zRot=-.12f;leftArm.zRot=.12f;
                if(f.gobletTicks()>0){rightArm.xRot=-1.36f;rightArm.zRot=-.10f;rightArm.yRot=-.12f;}else rightArm.yRot=0;''')
p=java/'Client.java';s=p.read_text(encoding='utf-8')
# The existing friendly-vampire renderer is a ZombieModel MobRenderer.
a=re.search(r'super\([^;]*?new BowZombieModel\(c\.bakeLayer\(f\?FRIENDLY:VAMPIRE\)\)[^;]*?\);',s)
assert a,'VampRenderer constructor not found'
s=s[:a.end()]+'if(f)addLayer(new VampireGobletLayer(this));'+s[a.end():]
p.write_text(s,encoding='utf-8')
write('VampireGobletLayer.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.ZombieModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.monster.Zombie;
import it.noctis.magic.SculptedGuestsClient.Part;
public class VampireGobletLayer extends RenderLayer<Zombie,ZombieModel<Zombie>>{
 static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/vampire_goblet.png");
 final Part cup=new Part(0,0,0);
 public VampireGobletLayer(RenderLayerParent<Zombie,ZombieModel<Zombie>> p){super(p);
  cup.loft(0,24,-.2f,0,0,.82f,.82f,0,0,0,.86f,.86f,.15f,0,0,.72f,.72f);
  cup.loft(0,16,-2.1f,0,0,.15f,.15f,-.2f,0,0,.16f,.16f);
  cup.loft(0,24,-4.7f,0,0,1.02f,1.02f,-4.5f,0,0,1.06f,1.06f,-3.4f,0,0,1.0f,1.0f,-2.5f,0,0,.64f,.64f,-2.0f,0,0,.22f,.22f);
  cup.loft(1,24,-4.56f,0,0,.91f,.91f,-3.35f,0,0,.91f,.91f,-2.65f,0,0,.57f,.57f);
  // Visible red surface and silver rim, independent materials.
  cup.oval(1,0,-4.54f,0,.91f,.045f,.91f);
  cup.loft(2,24,-4.73f,0,0,1.04f,1.04f,-4.61f,0,0,1.09f,1.09f);
 }
 @Override public void render(PoseStack p,MultiBufferSource buffers,int light,Zombie e,float limb,float amount,float partial,float age,float yaw,float pitch){
  if(!(e instanceof Vampire.Friendly f)||f.gobletTicks()==0)return;
  p.pushPose();var arm=getParentModel().rightArm;arm.translateAndRotate(p);
  p.translate(0,10.1f/16f,-.55f/16f);p.mulPose(Axis.XP.rotation(-arm.xRot));
  cup.draw(p,buffers.getBuffer(RenderType.entityTranslucent(TEX)),light,OverlayTexture.NO_OVERLAY,1,1,1,1);p.popPose();
 }
}''')
W,H=1024,512;pix=bytearray(W*H*4)
for m,col in [(0,(145,180,194)),(1,(137,12,35)),(2,(223,230,226))]:
 for yy in range(128):
  for xx in range(128):
   u=xx/127;c=shade(col,.70+.30*math.sin(u*math.pi)**2)
   if m==1:c=mix(c,(229,50,61),.32*math.exp(-((u-.28)/.11)**2))
   off=(yy*W+m*128+xx)*4;pix[off:off+4]=bytes((*c,130 if m==0 else 255))
png(assets/'textures/entity/vampire_goblet.png',W,H,pix)
print('Lucy angular anime netrunner outfit and occasional cigarette; friendly vampire goblet prop.')


# Six canonical pony hairstyles: layered locks, individual shapes, and matching fine satin highlights.
p=java/'PonyCartoonClient.java';s=p.read_text(encoding='utf-8')
start=s.index('  void hairstyle(){');end=s.index('  @Override public void setupAnim',start)
s=s[:start]+'''  void hairstyle(){
   if(k==4){
    // Pinkie Pie: inflated cloud-like curls, curled forelock and springy scalloped tail.
    mane.oval(24,0,-4.45f,.5f,3.75f,2.25f,3.15f);
    for(int i=0;i<3;i++){
     float x=-2.15f+i*2.05f;curl(mane,24,x,-5.15f+(i%2)*.45f,-1.85f,2.1f+i*.10f,3.2f+i*.65f,i==1?-1:1);
     curl(mane,24,x,-2.7f+(i%2)*.3f,2.3f,2.25f,2.5f+i*.72f,i==1?1:-1);
    }
    curl(mane,24,-3.05f,-.65f,.4f,1.85f,2.5f,-1);
    curl(mane,24,3.10f,-.15f,1.0f,1.95f,-.9f,1);
    for(int i=0;i<4;i++){Part q=mane.child(0,0,0);locks.add(q);curl(q,24,-2.4f+(i%2)*2.25f,2.25f+i*1.45f,2.7f+i*.48f,1.9f+(i%2)*.22f,2.5f+i*.6f,i%2==0?1:-1);}
    tail.oval(24,0,-.65f,3.0f,2.30f,2.4f,2.80f);
    for(int i=0;i<6;i++)curl(tail,24,(i%2==0?-1:1)*(1.15f+i*.10f),-1.7f+i*1.40f,4.6f+(float)Math.sin(i*.65)*2.1f,2.25f+(i%3)*.23f,3.1f+i*.7f,i%2==0?1:-1);
   }else if(k==5){
    // Twilight: straight navy bob, squared fringe and continuous violet/magenta stripes.
    mane.oval(24,0,-4.4f,.65f,3.67f,1.65f,3.08f);
    for(int j=0;j<9;j++){
     float x=-3.03f+j*.76f;int mat=j==5?26:j==6?27:24;
     lock(mane,mat,.57f,x,-5.15f,-.65f,.25f,x,-4.55f,-2.30f,.55f,x,-3.66f,-3.35f,.55f,x+.04f,-2.95f,-3.36f,.51f);
     Part q=mane.child(0,0,0);locks.add(q);
     lock(q,mat,.76f,x*.80f,-4.35f,1.75f,.45f,x*.87f,-2.0f,3.45f,.64f,x*.87f,1.7f,4.15f,.64f,x*.72f,5.9f,4.8f,.61f,x*.65f,8.2f,5.05f,.53f);
     lock(tail,mat,.82f,x*.25f,-1.30f,.10f,.40f,x*.66f,-1.05f,3.0f,.61f,x*.80f,1.8f,5.0f,.68f,x*.72f,5.3f,6.15f,.60f,x*.55f,8.0f,6.25f,.47f);
    }
   }else if(k==6){
    // Rainbow Dash: jagged wind-swept crest and six distinct colors, not blended into brown.
    for(int j=0;j<6;j++){
     float x=-2.75f+j*1.10f;int m=26+j;
     lock(mane,m,.75f,x-.40f,-3.7f,-2.45f,.16f,x-.7f,-5.1f,-1.25f,.73f,x-.40f,-6.2f,.1f,.98f,x+.05f,-5.25f,1.85f,.96f,x+.44f,-2.6f,3.35f,.79f,x+.85f,1.05f,4.75f,.66f,x+1.25f,4.25f,5.75f,.035f);
     lock(mane,m,.58f,x,-4.9f,.65f,.54f,x+.18f,-3.4f,2.3f,.58f,x+.74f,-.8f,3.75f,.42f,x+1.35f,2.7f,4.2f,.025f);
     lock(tail,m,.78f,x*.25f,-1.2f,.2f,.40f,x*.55f,-1.30f,2.6f,.69f,x*.80f,-.25f,5.0f,.86f,x*.87f,2.7f,7.8f,.69f,x*.73f,5.2f+(j%2)*.40f,8.85f,.40f,x*.64f,6.8f+(j%3)*.45f,9.0f,.025f);
    }
   }else if(k==7){
    // Fluttershy: long sweeping pink mane mostly on one side, gentle S waves and tapered ends.
    mane.oval(24,-.35f,-4.45f,.45f,3.62f,1.8f,3.05f);
    for(int j=0;j<7;j++){
     float f=j/6f;Part q=mane.child(0,0,0);locks.add(q);
     lock(q,24,.68f,1.75f-f*1.5f,-5.35f+f*.48f,-.75f,.18f,-.45f-f*.8f,-4.85f+f*.35f,-2.65f,.76f,-2.75f-f*.25f,-3.25f+f*.5f,-2.55f,.95f,-3.90f-f*.22f,.2f+f*.75f,-1.15f,.88f,-3.75f-f*.24f,4.2f+f*.5f,.45f,.76f,-2.75f-f*.40f,8.0f+f*.6f,2.7f,.50f,-2.1f-f*.45f,10.2f+f*.55f,3.4f,.035f);
     lock(tail,24,.77f,(j-3)*.22f,-1.1f,.10f,.32f,(j-3)*.52f,-.55f,3.35f,.65f,-.55f+(j-3)*.60f,2.15f,5.5f,.78f,-.65f+(j-3)*.52f,5.6f,6.85f,.75f,.7f+(j-3)*.44f,8.0f,7.55f,.56f,2.0f+(j-3)*.25f,9.6f,7.8f,.035f);
    }
    lock(mane,24,.82f,2.1f,-4.35f,1.4f,1.15f,3.3f,-1.7f,3.15f,1.55f,2.95f,3.8f,4.7f,1.5f,1.65f,8.6f,5.7f,1.1f,.5f,11.1f,5.9f,.04f);
   }else if(k==8){
    // Rarity: elegant purple side sweep, glossy spiral curls and sculpted ringlet layers.
    mane.oval(24,-.65f,-4.65f,.55f,3.55f,2.05f,3.05f);
    for(int j=0;j<4;j++){
     float f=j/3f;
     lock(mane,24,.72f,-2.7f,-4.3f+f*.35f,-.9f,.18f,-1.5f,-5.75f+f*.34f,-2.0f-f*.22f,.80f,1.25f,-5.0f+f*.48f,-2.5f-f*.18f,.99f,3.15f,-2.6f+f*.53f,-1.6f-f*.15f,.83f,3.65f,.65f+f*.45f,-.35f,.66f,2.0f,2.6f+f*.35f,-.10f,.035f);
     curl(mane,24,2.8f+f*.28f,.35f+f*.43f,.35f+f*.30f,1.75f+f*.23f,-1.15f,1);
     Part q=mane.child(0,0,0);locks.add(q);lock(q,24,.85f,-1.9f-f*.25f,-4.0f,1.5f,.67f,-3.1f-f*.30f,-.2f,3.05f,.88f,-3.0f-f*.40f,3.3f,4.15f,1.02f,-1.0f-f*.35f,6.6f,4.3f,.91f,.55f-f*.22f,7.9f,3.8f,.14f);
     curl(q,24,-.75f-f*.28f,6.75f+f*.35f,3.6f+f*.22f,2.0f+f*.15f,2.55f,-1);
     lock(tail,24,.83f,(j-1.5f)*.28f,-1.2f,0,.55f,-1.0f+(j-1.5f)*.32f,-1.9f,3.0f,.90f,-1.30f+(j-1.5f)*.45f,.4f,5.1f,1.12f,.40f+(j-1.5f)*.40f,3.6f,6.0f,1.10f,1.6f,5.7f,5.9f,.85f);
     curl(tail,24,.75f+(j-1.5f)*.35f,5.9f+f*.45f,5.8f+f*.18f,2.1f+f*.25f,1.8f,-1);
    }
   }else{
    // Applejack: golden side fringe and gathered ponytails tied with red bands under her hat.
    mane.oval(24,0,-4.3f,.45f,3.55f,1.6f,3.0f);
    for(int j=0;j<6;j++){
     float f=j/5f;
     lock(mane,24,.70f,2.2f,-4.9f+f*.30f,-.75f,.23f,.6f,-4.7f+f*.34f,-2.45f,.72f,-1.8f,-3.8f+f*.42f,-2.8f,.72f,-3.2f,-2.4f+f*.4f,-1.55f,.56f,-3.3f,-1.25f+f*.35f,-.8f,.035f);
     Part q=mane.child(0,0,0);locks.add(q);
     lock(q,24,.82f,(j-2.5f)*.46f,-4.1f,2.2f,.72f,(j-2.5f)*.60f,-.8f,3.65f,.88f,.45f+(j-2.5f)*.52f,3.3f,4.5f,.87f,.55f+(j-2.5f)*.23f,6.25f,4.9f,.34f,.45f+(j-2.5f)*.47f,8.5f,5.2f,.60f,.3f+(j-2.5f)*.26f,10.2f,5.4f,.035f);
     lock(tail,24,.82f,(j-2.5f)*.25f,-1.1f,0,.50f,-.25f+(j-2.5f)*.45f,-1.1f,2.8f,.75f,-.20f+(j-2.5f)*.50f,1.8f,5.1f,.90f,.1f+(j-2.5f)*.22f,4.4f,6.2f,.45f,.20f+(j-2.5f)*.20f,5.5f,6.7f,.33f,.65f+(j-2.5f)*.44f,7.3f,6.95f,.65f,1.45f+(j-2.5f)*.27f,9.15f,7.1f,.035f);
    }
    mane.oval(27,.55f,6.35f,4.9f,1.12f,.34f,1.0f);tail.oval(27,.2f,5.4f,6.7f,1.14f,.35f,1.05f);
    Part hat=head.child(0,-4.9f,.10f);hat.rz=.06f;
    hat.loft(28,40,-.52f,0,0,4.75f,3.80f,-.18f,0,0,5.20f,4.20f,.22f,0,0,5.12f,4.15f,.45f,0,0,4.65f,3.74f);
    hat.loft(28,36,-3.4f,0,.24f,1.95f,2.07f,-2.92f,0,.20f,2.55f,2.61f,-1.9f,0,.10f,2.78f,2.78f,-.28f,0,0,3.05f,3.03f);
    hat.loft(29,36,-.95f,0,0,2.99f,2.99f,-.40f,0,0,3.09f,3.09f);
   }
  }
'''+s[end:]
p.write_text(s,encoding='utf-8')
# Add fine, direction-following highlights to hair tiles without modifying the eyes or marks.
for k in range(4,10):
 p=assets/'textures/entity'/f'pony_cartoon_{k}.png';blob=p.read_bytes();i=8;compressed=b''
 while i<len(blob):
  size=struct.unpack('>I',blob[i:i+4])[0];typ=blob[i+4:i+8];data=blob[i+8:i+8+size];i+=size+12
  if typ==b'IDAT':compressed+=data
 raw=zlib.decompress(compressed);W,H=1024,512;stride=W*4+1
 assert len(raw)==H*stride and all(raw[y*stride]==0 for y in range(H))
 pix=bytearray(b''.join(raw[y*stride+1:(y+1)*stride] for y in range(H)))
 mats=[24,26,27] if k==5 else list(range(26,32)) if k==6 else [24]
 for m in mats:
  for yy in range(128):
   v=sat((yy-3)/121)
   for xx in range(128):
    u=sat((xx-3)/121);off=(((m//8)*128+yy)*W+(m%8)*128+xx)*4
    c=tuple(pix[off:off+3]);line=(u*10+.11*math.sin(v*5))%1
    c=mix(c,(255,255,255),.13*math.exp(-((line-.36)/.10)**2))
    c=shade(c,1-.09*math.exp(-((line-.84)/.09)**2))
    pix[off:off+4]=bytes((*c,255))
 png(p,W,H,pix)
# Malfoid: more tsundere dialogue, synchronized folded-arms pose and combat priority.
edit('Malfoid.java','private int speech,cast,cd=45,phase,attack,absent;','private int speech,cast,cd=45,phase,attack,absent,foldTicks=0,foldCooldown=180;\n    public boolean folded(){return foldTicks>0;}\n    void fold(ServerLevel l){if(boss||cast>0)return;foldTicks=105;foldCooldown=260+random.nextInt(320);getNavigation().stop();l.broadcastEntityEvent(this,(byte)105);}')
edit('Malfoid.java','return !boss&&partner==null&&!stay&&super.canUse();','return foldTicks==0&&!boss&&partner==null&&!stay&&super.canUse();')
edit('Malfoid.java','return !boss&&partner==null&&!stay&&super.canContinueToUse();','return foldTicks==0&&!boss&&partner==null&&!stay&&super.canContinueToUse();')
edit('Malfoid.java','speech=65;int a=points(p);','speech=65;int a=points(p);fold(l);')
edit('Malfoid.java','new String[]{"Non hai di meglio da fare?","Sai chi e\' mio padre?","Tsk. Stai attento a come mi parli."}','new String[]{"Tsk! Non credere che abbia tempo per te.","Sai chi e mio padre?","Ma guarda chi si rivede. Che seccatura.","N-non fissarmi!","Non ti ho certo aspettato, idiota."}')
edit('Malfoid.java','new String[]{"Non e\' che aspettassi proprio te.","Sei meno insopportabile del solito."}','new String[]{"Non e che aspettassi proprio te.","Sei meno insopportabile del solito.","Ti ho tenuto un posto. Solo perche era vuoto!","Non pensare che mi preoccupi per te. Baka!","E va bene, resta. Ma non disturbarmi."}')
edit('Malfoid.java','new String[]{"Non guardarmi cosi!","B-bene, puoi restare ancora un po\'.","Non e\' che mi mancassi, sia chiaro."}','new String[]{"Non guardarmi cosi!","B-bene, puoi restare ancora un po.","Non e che mi mancassi, sia chiaro.","Ti sei fatto male? Idiota... fammi vedere.","Non andare troppo lontano. Non perche mi interessi!","Sei in ritardo. Hmph... mi hai fatto preoccupare per niente."}')
edit('Malfoid.java','int mode=attack++%3;l.broadcastEntityEvent(this,(byte)89);','int mode=attack++%3;foldTicks=0;l.broadcastEntityEvent(this,(byte)106);l.broadcastEntityEvent(this,(byte)89);')
edit('Malfoid.java','super.tick();if(speech>0)speech--;','super.tick();if(foldTicks>0)foldTicks--;if(foldCooldown>0)foldCooldown--;if(speech>0)speech--;')
edit('Malfoid.java','        if(boss){\n            bar.setProgress','''        if(!boss&&cast==0&&hurtTime==0&&onGround()&&!isInWater()&&getDeltaMovement().horizontalDistanceSqr()<.0025&&foldCooldown==0&&l.getNearestPlayer(this,6)!=null&&random.nextInt(65)==0)fold(l);
        if(foldTicks>0){
            if(boss||hurtTime>0||isInWater()||!onGround()||(partner!=null&&l.getEntity(partner) instanceof Player q&&distanceTo(q)>4&&!stay)){foldTicks=0;l.broadcastEntityEvent(this,(byte)106);}
            else{getNavigation().stop();setDeltaMovement(0,getDeltaMovement().y,0);}
        }
        if(boss){
            bar.setProgress''')
edit('Malfoid.java','if(id==89){cast=24;return;}','if(id==105){foldTicks=105;return;}if(id==106){foldTicks=0;return;}if(id==89){cast=24;foldTicks=0;return;}')
# Articulated arms using the existing robe, cuff and skin UV islands. Move the wand to the forearm.
p=java/'MalfoidClient.java';s=p.read_text(encoding='utf-8')
for i in range(2):
 pat=r'(PartDefinition arm'+str(i)+r'=r\.addOrReplaceChild\("arm'+str(i)+r'",CubeListBuilder\.create\(\)\.texOffs\((\d+),(\d+)\))\.addBox\([^)]*\)\.texOffs\((\d+),(\d+)\)\.addBox\([^)]*\)\.texOffs\((\d+),(\d+)\)\.addBox\([^)]*\)(,PartPose\.offsetAndRotation\([^;]*\);)'
 m=re.search(pat,s);assert m,'Malfoid arm geometry '+str(i)
 upper=m.group(1)+'.addBox(-1.5f,-1f,-1.5f,3f,5.5f,3f)'+m.group(8)
 lower=f'PartDefinition fore{i}=arm{i}.addOrReplaceChild("fore{i}",CubeListBuilder.create().texOffs({m.group(2)},{m.group(3)+""}).addBox(-1.5f,0f,-1.5f,3f,4f,3f).texOffs({m.group(4)},{m.group(5)}).addBox(-1.5f,2.7f,-1.5f,3f,1.5f,3f).texOffs({m.group(6)},{m.group(7)}).addBox(-1f,4f,-1f,2f,2f,2f),PartPose.offset(0,4.4f,0));'
 s=s[:m.start()]+upper+'\n        '+lower+s[m.end():]
s=s.replace('PartDefinition wand=arm1.addOrReplaceChild','PartDefinition wand=fore1.addOrReplaceChild',1).replace('PartPose.offsetAndRotation(0.0f,10.0f,-1.0f','PartPose.offsetAndRotation(0.0f,5.6f,-1.0f',1)
a='            for(int j=0;j<7;j++)h.getChild("back"+j).xRot='
assert a in s
s=s.replace(a,'''            for(int i=0;i<2;i++){
                int side=i==0?-1:1;ModelPart arm=r.getChild("arm"+i),fore=arm.getChild("fore"+i);
                arm.yRot=0;arm.zRot=-side*.08f;fore.xRot=-.10f;fore.yRot=0;fore.zRot=0;
                if(e.folded()&&cast<=0&&amount<.15f&&!e.isAggressive()){
                    arm.xRot=-1.02f;arm.yRot=side*.12f;arm.zRot=-side*.16f;
                    fore.xRot=-.42f;fore.yRot=side*.32f;fore.zRot=-side*1.05f;
                    h.zRot=-.10f;h.xRot=-.09f;
                }
            }
            r.getChild("arm1").getChild("fore1").getChild("wand").visible=!e.folded()||cast>0;
'''+a,1)
p.write_text(s,encoding='utf-8')
print('Canonical six pony hair silhouettes and Malfoid tsundere dialogue with articulated folded arms.')


# Six rideable ponies, unique canon-inspired abilities and improved mounted flight.
p=java/'FriendshipPony.java';s=p.read_text(encoding='utf-8')
s=s.replace('private int speech,magic,pose;','private int speech,magic,pose,flightBoost;')
s=s.replace('if(speech>0)speech--;if(magic>0)magic--;if(pose>0)pose--;','if(speech>0)speech--;if(magic>0)magic--;if(pose>0)pose--;if(flightBoost>0)flightBoost--;')
a=s.index('    @Override public void travel(Vec3 v)');b=s.index('    @Override public void tick()',a)
s=s[:a]+'''    @Override public void travel(Vec3 v){
        if(isAlive()&&getControllingPassenger() instanceof Player rider){
            setYRot(rider.getYRot());yBodyRot=getYRot();yHeadRot=getYRot();setXRot(0);getNavigation().stop();
            if(winged()){
                setNoGravity(true);resetFallDistance();
                if(isControlledByLocalInstance()){
                    double yaw=Math.toRadians(rider.getYRot()),pitch=Math.toRadians(rider.getXRot()),f=rider.zza,side=rider.xxa;
                    Vec3 motion=new Vec3(-Math.sin(yaw)*Math.cos(pitch)*f+Math.cos(yaw)*side*.65,-Math.sin(pitch)*f,Math.cos(yaw)*Math.cos(pitch)*f+Math.sin(yaw)*side*.65);
                    if(motion.lengthSqr()>1)motion=motion.normalize();
                    double speed=kind()==1?(flightBoost>0?1.65:1.02):kind()==2?.58:.79;
                    Vec3 target=motion.scale(speed);
                    if(onGround()&&f>.05&&rider.getXRot()<18)target=target.add(0,.30,0);
                    Vec3 next=getDeltaMovement().scale(.68).add(target.scale(.32));
                    if(motion.lengthSqr()<.0001&&next.lengthSqr()<.0009)next=Vec3.ZERO;
                    setDeltaMovement(next);move(MoverType.SELF,next);resetFallDistance();calculateEntityAnimation(false);
                }
            }else{
                setNoGravity(false);setSpeed(kind()==4?.39f:kind()==5?.36f:.31f);
                if(isControlledByLocalInstance())super.travel(new Vec3(rider.xxa*.65,0,rider.zza<0?rider.zza*.5:rider.zza));
            }return;
        }
        if(isNoGravity())setNoGravity(false);
        super.travel(v);
    }
'''+s[b:]
a=s.index('    public void power(ServerLevel l,Player p)');b=s.index('    @Override public void handleEntityEvent',a)
s=s[:a]+'''    private java.util.List<LivingEntity> nearbyEnemies(ServerLevel l,double range){
        return l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(range),e->e!=this&&e.isAlive()&&Eclipse.hostile(e)&&e.getMaxHealth()<100);
    }
    public void power(ServerLevel l,Player p){
        if(!isOwnedBy(p)||isOrderedToSit())return;
        if(magic>0){p.displayClientMessage(Component.literal("Potere in ricarica: "+((magic+19)/20)+" s"),true);return;}
        magic=kind()==0?280:kind()==1?320:kind()==2?400:kind()==3?300:kind()==4?220:240;
        l.broadcastEntityEvent(this,(byte)93);
        String name;
        switch(kind()){
            case 0->{
                name="Magia dell amicizia";
                for(LivingEntity e:nearbyEnemies(l,9)){e.hurt(damageSources().magic(),18);e.addEffect(new MobEffectInstance(MobEffects.GLOWING,120,0));e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,80,1));}
                p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,180,0));
                l.sendParticles(ParticleTypes.WITCH,getX(),getY()+1,getZ(),55,1.2,.6,1.2,.06);
            }
            case 1->{
                name="Sonic Rainboom";flightBoost=140;l.broadcastEntityEvent(this,(byte)109);
                p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,140,2));
                l.sendParticles(ParticleTypes.FIREWORK,getX(),getY()+.7,getZ(),70,1.2,.6,1.2,.14);
                playSound(SoundEvents.FIREWORK_ROCKET_BLAST,1,.9f);
            }
            case 2->{
                name="Lo sguardo di Fluttershy";p.heal(6);p.addEffect(new MobEffectInstance(MobEffects.REGENERATION,100,0));
                for(LivingEntity e:nearbyEnemies(l,10)){
                    e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,140,2));
                    e.getPersistentData().putLong("NoctisPonyFear",l.getGameTime()+120);
                    e.getPersistentData().putUUID("NoctisPonyFearSource",getUUID());
                    if(e instanceof Mob m){m.setTarget(null);Vec3 away=m.position().subtract(position()).normalize();m.getNavigation().moveTo(m.getX()+away.x*9,m.getY(),m.getZ()+away.z*9,1.5);}
                    l.sendParticles(ParticleTypes.ANGRY_VILLAGER,e.getX(),e.getY()+e.getBbHeight(),e.getZ(),4,.2,.2,.2,.02);
                }
            }
            case 3->{
                name="Scudo di cristallo";
                p.addEffect(new MobEffectInstance(MobEffects.ABSORPTION,400,2));p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,220,0));
                p.addEffect(new MobEffectInstance(MobEffects.LUCK,600,1));p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,600,0));
                l.sendParticles(ParticleTypes.ENCHANT,getX(),getY()+1,getZ(),55,.65,.8,.65,.08);
            }
            case 4->{
                name="Calcio della fattoria";p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,220,1));p.addEffect(new MobEffectInstance(MobEffects.SATURATION,20,0));
                for(LivingEntity e:nearbyEnemies(l,5)){e.hurt(damageSources().mobAttack(this),10);e.knockback(2.0,getX()-e.getX(),getZ()-e.getZ());}
                l.sendParticles(ParticleTypes.POOF,getX(),getY()+.2,getZ(),36,1.1,.15,1.1,.07);
            }
            default->{
                name="Festa a sorpresa";p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,240,0));p.addEffect(new MobEffectInstance(MobEffects.JUMP,240,1));
                for(LivingEntity e:nearbyEnemies(l,8)){e.addEffect(new MobEffectInstance(MobEffects.BLINDNESS,100,0));e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,100,2));}
                l.sendParticles(ParticleTypes.NOTE,getX(),getY()+1,getZ(),50,1.2,.65,1.2,.08);
            }
        }
        p.displayClientMessage(Component.literal(name),true);
        l.sendParticles(kind()==5?ParticleTypes.HAPPY_VILLAGER:kind()==2?ParticleTypes.HEART:ParticleTypes.END_ROD,getX(),getY()+1,getZ(),24,.6,.6,.6,.04);
        playSound(SoundEvents.AMETHYST_BLOCK_CHIME,1,1.3f);
    }
'''+s[b:]
s=s.replace('if(id==93){pose=24;return;}','if(id==109){flightBoost=140;return;}if(id==93){pose=24;return;}')
p.write_text(s,encoding='utf-8')
# Server-side fear overrides normal targeting for a short period; only ordinary hostile mobs.
write('PonyFear.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class PonyFear{
 @SubscribeEvent public static void flee(LivingEvent.LivingTickEvent event){
  if(!(event.getEntity() instanceof Mob mob)||!(mob.level() instanceof ServerLevel l))return;
  var data=mob.getPersistentData();
  if(!data.contains("NoctisPonyFear"))return;
  if(data.getLong("NoctisPonyFear")<=l.getGameTime()||!data.hasUUID("NoctisPonyFearSource")){
   data.remove("NoctisPonyFear");data.remove("NoctisPonyFearSource");return;
  }
  if(!(l.getEntity(data.getUUID("NoctisPonyFearSource")) instanceof FriendshipPony pony))return;
  mob.setTarget(null);mob.setAggressive(false);
  if(mob.tickCount%5==0){Vec3 away=mob.position().subtract(pony.position()).normalize();
   mob.getNavigation().moveTo(mob.getX()+away.x*9,mob.getY(),mob.getZ()+away.z*9,1.45);}
 }
}''')
# Support activating a pony power while mounted or when right-clicking one's own pony.
p=java/'FriendshipPony.java';s=p.read_text(encoding='utf-8')
a='if(isTame()&&isOwnedBy(p)){\n            if(isFood(s))'
assert a in s
s=s.replace(a,'''if(isTame()&&isOwnedBy(p)){
            if(s.is(Items.BLAZE_ROD)){if(level() instanceof ServerLevel l)power(l,p);return InteractionResult.sidedSuccess(level().isClientSide);}
            if(isFood(s))''',1)
p.write_text(s,encoding='utf-8')
# Less exaggerated, natural and reserved Malfoid dialogue, while retaining her folded arms.
p=java/'Malfoid.java';s=p.read_text(encoding='utf-8')
a=s.index('            String[] lines=a<4?');b=s.index(';\n            say(l,lines',a)
s=s[:a]+'''            String[] lines=a<4?new String[]{"Cosa vuoi?","Non credo ci siamo gia presentati.","Hai bisogno di qualcosa?","Preferisco stare per conto mio.","Spero tu abbia un buon motivo."}:a<8?new String[]{"Ah, sei di nuovo qui.","Non mi dispiace la tua compagnia.","E una giornata piuttosto tranquilla.","Puoi restare, se vuoi.","Hai trovato qualcosa di interessante?"}:new String[]{"Mi fa piacere rivederti.","Come sta andando il viaggio?","Se hai bisogno di aiuto, dimmelo.","Cerchiamo di non perderci di vista.","Restiamo qui ancora un momento.","Non serve che tu faccia tutto da solo."}'''+s[b:]
for a,b in {
"Non devi comprarti il mio affetto, idiota.":"Hai gia fatto abbastanza. Conserva il regalo.",
"Tsk. Almeno hai un minimo di gusto.":"Un regalo? Non era necessario.",
"Non pensare che questo significhi qualcosa!":"Grazie. Lo apprezzo.",
"Forse... la tua compagnia non e' cosi terribile.":"Sei stato molto premuroso.",
"Forse mi piaci davvero. Non farmelo ripetere!":"Mi fido di te. Credo che potremmo viaggiare insieme.",
"Va bene, ti accompagnero'. Ma non montarti la testa!":"D accordo, ti accompagno.",
"Ti aspetto qui. Non tardare.":"Ti aspetto qui.",
"Andiamo, prima che cambi idea.":"Bene, possiamo andare."
}.items():s=s.replace(a,b)
p.write_text(s,encoding='utf-8')
print('All six ponies rideable with distinctive powers, flight and fear; neutral Malfoid dialogues.')


# Ace Attorney: recurring courtroom objections with a held, dramatic pointing pose.
edit('CrossoverGuest.java','int cooldown=40,speech=0,pose=0,animation=0,aimTicks=0;','int cooldown=40,speech=0,pose=0,animation=0,aimTicks=0,objectionCooldown=500;')
edit('CrossoverGuest.java','speech=180;lastVisitor=p.getUUID();l.broadcastEntityEvent(this,(byte)102);','''speech=180;objectionCooldown=700+random.nextInt(1000);lastVisitor=p==null?null:p.getUUID();
        pose=42;animation=0;getNavigation().stop();if(p!=null)getLookControl().setLookAt(p,40,40);
        l.broadcastEntityEvent(this,(byte)102);''')
edit('CrossoverGuest.java','say(l,"OBIEZIONE!");','say(l,"OBJECTION!");')
edit('CrossoverGuest.java','if(aimTicks>0)aimTicks--;if(pose>0)pose--;','if(aimTicks>0)aimTicks--;if(objectionCooldown>0)objectionCooldown--;if(pose>0)pose--;')
edit('CrossoverGuest.java','if(p==null){lastVisitor=null;}else if(speech==0&&!p.getUUID().equals(lastVisitor)){object(l,p);}','''if(p==null){lastVisitor=null;}else if(speech==0&&!p.getUUID().equals(lastVisitor)){object(l,p);}
            if(pose==0&&speech==0&&objectionCooldown==0&&onGround()&&!isInWater()&&hurtTime==0&&random.nextInt(65)==0){object(l,p);}
            if(pose>0&&animation==0){getNavigation().stop();return;}''')
edit('CrossoverGuest.java','pose=id==103?34:18;','pose=id==102?42:id==103?34:18;')
edit('CrossoverGuest.java','return pose<=0?0:(float)Math.sin(pose*Math.PI/(animation==1?34:18));','return pose<=0?0:animation==0?Math.min(1f,Math.min((42-pose)/7f,pose/8f)):(float)Math.sin(pose*Math.PI/(animation==1?34:18));')
edit('CrossoverClient.java','ModelPart arm=r.getChild("arm1");','ModelPart arm=r.getChild("arm1");arm.yRot=0;arm.zRot=-.08f;')
edit('CrossoverClient.java','if(a>0&&e.animation()==0){arm.xRot=-1.7f*a;r.getChild("arm0").xRot=-.3f;b.yRot=a*.14f;}','''if(a>0&&e.animation()==0){
                    arm.xRot=-.45f-1.10f*a;arm.yRot=-.12f*a;arm.zRot=-.08f-.10f*a;
                    r.getChild("arm0").xRot=-.26f*a;b.yRot=(k==1?.16f:-.10f)*a;
                    h.xRot=-.04f*a;h.yRot*=.3f;
                }''')
# Satirical baker: an occasional objection to the baking, with a distinct left-arm
# lateral gesticulation (not a salute), no political slogans or symbols.
edit('BakeryClerk.java','private int cooldown;','private int cooldown,bakerGesture=0,bakerGestureCd=600;\n    public float bakerGesture(){return bakerGesture<=0?0:Math.min(1f,Math.min((40-bakerGesture)/7f,bakerGesture/8f));}\n    @Override public void handleEntityEvent(byte id){if(id==107){bakerGesture=40;return;}super.handleEntityEvent(id);}')
edit('BakeryClerk.java','super.tick();if(cooldown>0)cooldown--;','''super.tick();if(bakerGesture>0)bakerGesture--;if(bakerGestureCd>0)bakerGestureCd--;if(cooldown>0)cooldown--;
        if(!stalin()&&level() instanceof ServerLevel l&&bakerGestureCd==0&&onGround()&&!isInWater()&&hurtTime==0&&l.getNearestPlayer(this,10)!=null&&random.nextInt(90)==0){
            bakerGesture=40;bakerGestureCd=900+random.nextInt(1400);cooldown=180;
            l.broadcastEntityEvent(this,(byte)107);say(l,"OBJECTION! Quel pane non e ancora pronto!");
            playSound(SoundEvents.VILLAGER_NO,.65f,1.1f);
        }''')
edit('BakeryClient.java','    static class Renderer extends MobRenderer<BakeryClerk,HumanoidModel<BakeryClerk>>{','''    static class GestureModel extends HumanoidModel<BakeryClerk>{
        GestureModel(ModelPart p){super(p);}
        @Override public void setupAnim(BakeryClerk e,float limb,float amount,float age,float yaw,float pitch){
            super.setupAnim(e,limb,amount,age,yaw,pitch);
            float a=e.bakerGesture();
            if(!e.stalin()&&a>0){
                leftArm.xRot=-.62f*a;leftArm.zRot=-1.18f*a;leftArm.yRot=.32f*a;
                rightArm.xRot=-.28f*a;head.zRot=.12f*a;
            }
        }
    }
    static class Renderer extends MobRenderer<BakeryClerk,HumanoidModel<BakeryClerk>>{''')
edit('BakeryClient.java','new HumanoidModel<>(c.bakeLayer(L))','new GestureModel(c.bakeLayer(L))')
print('Recurring Phoenix and Miles objections, plus distinct satirical baker protest gesture.')


# P is the dedicated pony power key, using the existing authenticated Cast packet.
# A reserved negative ID cannot be confused with normal spells or the bat key.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
a='if(id==-1){VampireLife.toggleBat(p);return;}'
assert a in s
s=s.replace(a,'''if(id==-201){
            if(p.getVehicle() instanceof FriendshipPony pony&&pony.getControllingPassenger()==p)pony.power(p.serverLevel(),p);
            return;
        }'''+a,1)
p.write_text(s,encoding='utf-8')
write('PonyPowerKey.java','''package it.noctis.magic;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
public class PonyPowerKey{
 static final KeyMapping POWER=new KeyMapping("key.noctismagic.pony_power",InputConstants.Type.KEYSYM,GLFW.GLFW_KEY_P,"key.categories.noctismagic");
 @Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
 public static class Registration{
  @SubscribeEvent public static void keys(RegisterKeyMappingsEvent e){e.register(POWER);}
 }
 @Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT)
 public static class Input{
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
   if(e.phase!=TickEvent.Phase.END)return;
   Minecraft mc=Minecraft.getInstance();
   while(POWER.consumeClick()){
    if(mc.player!=null&&mc.screen==null&&mc.player.getVehicle() instanceof FriendshipPony)Noctis.NET.sendToServer(new Noctis.Cast(-201));
   }
  }
 }
}''')
# P replaces the previous blaze-rod shortcut for ponies only; dragon powers are unaffected.
write('PonyEvents.java','''package it.noctis.magic;
// Pony abilities now use the rebindable P key and the Noctis Cast packet.
public class PonyEvents {}''')
edit('FriendshipPony.java','if(s.is(Items.BLAZE_ROD)){if(level() instanceof ServerLevel l)power(l,p);return InteractionResult.sidedSuccess(level().isClientSide);}','')
edit('FriendshipPony.java','if(!isTame()&&isFood(s)){','''if(!isTame()&&s.isEmpty()&&h==InteractionHand.MAIN_HAND){
            if(p instanceof net.minecraft.server.level.ServerPlayer sp)sp.displayClientMessage(Component.translatable("message.noctismagic.pony_tame"),true);
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if(!isTame()&&isFood(s)){''')
edit('FriendshipPony.java','l.broadcastEntityEvent(this,(byte)7);NpcDialogue.say','l.broadcastEntityEvent(this,(byte)7);p.displayClientMessage(Component.translatable("message.noctismagic.pony_tamed"),true);NpcDialogue.say')
edit('FriendshipPony.java','p.startRiding(this);if(speech==0)','if(p.startRiding(this))p.displayClientMessage(Component.translatable("message.noctismagic.pony_ride",net.minecraft.network.chat.Component.keybind("key.noctismagic.pony_power")),true);if(speech==0)')
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['key.noctismagic.pony_power']='Potere della pony' if it else 'Pony power'
 d['message.noctismagic.pony_tame']='Offrimi mele, carote o zucchero per diventare amici!' if it else 'Offer apples, carrots or sugar to become friends!'
 d['message.noctismagic.pony_tamed']='Amicizia conquistata! Tasto destro a mano vuota per cavalcare.' if it else 'Friendship gained! Right-click with an empty hand to ride.'
 d['message.noctismagic.pony_ride']='Premi %s per il potere speciale. Shift per scendere.' if it else 'Press %s to use the special power. Shift to dismount.'
 write_noctis_json_resource(p,d)
print('Dedicated rebindable P pony power key, server ownership validation and localized taming/riding hints.')


# Avoid the vanilla social-interactions P shortcut opening over a mounted pony.
edit('PonyPowerKey.java','  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){','''  @SubscribeEvent public static void key(net.minecraftforge.client.event.InputEvent.Key e){
   Minecraft mc=Minecraft.getInstance();
   if(e.getAction()==GLFW.GLFW_PRESS&&mc.player!=null&&mc.screen==null&&mc.player.getVehicle() instanceof FriendshipPony&&POWER.matches(e.getKey(),e.getScanCode())){
    if(mc.options.keySocialInteractions.matches(e.getKey(),e.getScanCode()))while(mc.options.keySocialInteractions.consumeClick()){}
   }
  }
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){''')


# Maomao's herbal remedy: permanent vanilla Poison immunity, including respawns.
write('MaomaoRemedy.java','''package it.noctis.magic;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.event.entity.living.MobEffectEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class MaomaoRemedy{
    static final String KEY="NoctisMaomaoPoisonImmunity";
    public static boolean herb(ItemStack s){
        return s.is(Items.FERN)||s.is(Items.LARGE_FERN)||s.is(Items.GRASS)||s.is(Items.DANDELION)||s.is(Items.ALLIUM)||s.is(Items.AZURE_BLUET)||s.is(Items.OXEYE_DAISY);
    }
    public static boolean immune(Player p){return p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).getBoolean(KEY);}
    public static void grant(ServerPlayer p){
        var data=p.getPersistentData();var keep=data.getCompound(Player.PERSISTED_NBT_TAG);keep.putBoolean(KEY,true);data.put(Player.PERSISTED_NBT_TAG,keep);
        p.removeEffect(MobEffects.POISON);
        p.displayClientMessage(Component.translatable("message.noctismagic.maomao_immunity"),false);
    }
    @SubscribeEvent public static void applicable(MobEffectEvent.Applicable e){
        if(e.getEntity() instanceof ServerPlayer p&&immune(p)&&e.getEffectInstance().getEffect()==MobEffects.POISON)e.setResult(net.minecraftforge.eventbus.api.Event.Result.DENY);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase==TickEvent.Phase.END&&e.player instanceof ServerPlayer p&&immune(p)&&p.hasEffect(MobEffects.POISON))p.removeEffect(MobEffects.POISON);
    }
    @SubscribeEvent public static void clone(PlayerEvent.Clone e){
        if(immune(e.getOriginal())){
            var data=e.getEntity().getPersistentData();var keep=data.getCompound(Player.PERSISTED_NBT_TAG);keep.putBoolean(KEY,true);data.put(Player.PERSISTED_NBT_TAG,keep);
        }
    }
}''')
edit('SushiGuest.java','ItemStack s=p.getItemInHand(h);if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET))return InteractionResult.PASS;','''ItemStack s=p.getItemInHand(h);
        if(maomao()&&MaomaoRemedy.herb(s)){
            if(p instanceof net.minecraft.server.level.ServerPlayer sp&&level() instanceof ServerLevel l){
                if(MaomaoRemedy.immune(sp)){sp.displayClientMessage(Component.translatable("message.noctismagic.maomao_already"),true);return InteractionResult.CONSUME;}
                int count=Noctis.data(sp).getInt("MaomaoHerbs");
                if(!p.getAbilities().instabuild)s.shrink(1);
                count++;Noctis.data(sp).putInt("MaomaoHerbs",count);
                l.broadcastEntityEvent(this,(byte)112);
                if(count>=5){MaomaoRemedy.grant(sp);say(l,"Ecco. Ora il veleno non dovrebbe piu avere effetto su di te.");l.sendParticles(ParticleTypes.HAPPY_VILLAGER,sp.getX(),sp.getY()+1,sp.getZ(),24,.35,.45,.35,.02);playSound(SoundEvents.PLAYER_LEVELUP,.65f,1.2f);}
                else{sp.displayClientMessage(Component.translatable("message.noctismagic.maomao_herbs",count,5),true);}
            }
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET))return InteractionResult.PASS;''')
edit('SushiGuest.java','if(s.isEmpty()){\n                if(p.isShiftKeyDown())','''if(s.isEmpty()){
                if(maomao()&&!MaomaoRemedy.immune(p)&&!p.isShiftKeyDown())p.displayClientMessage(Component.translatable("message.noctismagic.maomao_hint"),true);
                if(p.isShiftKeyDown())''')
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['message.noctismagic.maomao_hint']='Maomao cerca erbe medicinali. Portale 5 erbe o fiori comuni.' if it else 'Maomao seeks medicinal plants. Bring her 5 herbs or common flowers.'
 d['message.noctismagic.maomao_herbs']='Erbe consegnate a Maomao: %s/%s' if it else 'Herbs delivered to Maomao: %s/%s'
 d['message.noctismagic.maomao_immunity']='Rimedio di Maomao: immunita permanente al veleno!' if it else 'Maomao remedy: permanent poison immunity!'
 d['message.noctismagic.maomao_already']='Sei gia immune al veleno.' if it else 'You are already immune to poison.'
 write_noctis_json_resource(p,d)
print('Maomao herbal remedy: five common plants, permanent poison immunity saved across death.')


# Double the friendship points earned per blood bucket, retain old progress, cap at ten.
p=java/'Vampire.java';s=p.read_text(encoding='utf-8')
a='friendship.putInt(key,++points);'
assert a in s
s=s.replace(a,'points=Math.min(10,points+2);friendship.putInt(key,points);',1)
s=s.replace('if(points==10&&!VampireLife.isVampire(p))','if(points>=10&&!VampireLife.isVampire(p))')
p.write_text(s,encoding='utf-8')
# Register a collectible Behelit and guaranteed creature-specific drops.
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<Item> BEHELIT=ITEMS.register("behelit",()->new Item(new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.EPIC).fireResistant()));
    '''+a)
a='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',a,a+'e.accept(BEHELIT.get());')
edit('GemGuest.java','    @Override public void handleEntityEvent(byte id){','''    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource source,int looting,boolean hit){
        super.dropCustomDeathLoot(source,looting,hit);
        int amount=phos()?4+random.nextInt(5):6+random.nextInt(7);
        amount+=Math.max(0,looting)*2;
        spawnAtLocation(new net.minecraft.world.item.ItemStack(phos()?net.minecraft.world.item.Items.EMERALD:net.minecraft.world.item.Items.REDSTONE,amount));
    }
    @Override public void handleEntityEvent(byte id){''')
edit('Griffith.java','    @Override public void handleEntityEvent(byte id){','''    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource source,int looting,boolean hit){
        super.dropCustomDeathLoot(source,looting,hit);spawnAtLocation(Noctis.BEHELIT.get());
    }
    @Override public void handleEntityEvent(byte id){''')
# Hand-painted crimson egg with disordered human features, in Minecraft item format.
W=64;H=64;pix=bytearray(W*H*4)
for y in range(H):
 for x in range(W):
  u=(x-31.5)/20;v=(y-32)/27
  shape=(u/(.90+.16*v))**2+v*v
  if shape>1:continue
  light=max(0,1-((u+.34)**2+(v+.35)**2)*.8)
  c=mix((108,12,27),(227,77,77),light*.88)
  c=shade(c,1-.19*math.sin(u*31+v*9)**2-.055*math.sin(v*42)**2)
  if shape>.91:c=shade(c,.64)
  # Two displaced eyes, a nose ridge and a crooked mouth.
  for ex,ey in [(-.42,-.30),(.30,.06)]:
   dx=(u-ex)/.26;dy=(v-ey)/.105
   if dx*dx+dy*dy<1:c=(68,15,25)
   if dx*dx+(dy+.10)**2<.66:c=(218,165,135)
   if (dx+.04)**2+dy*dy<.26:c=(44,21,22)
  if abs(u+.08)<.11 and -.05<v<.44:c=mix(c,(235,114,97),.38)
  if abs(u+.08)<.36 and abs(v-(.62+.10*math.sin((u+.08)*7)))<.065:c=(62,14,25)
  off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/item/behelit.png',W,H,pix)
write_noctis_json_resource(assets/'models/item/behelit.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/behelit'}})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['item.noctismagic.behelit']='Behelit scarlatto' if it else 'Crimson Behelit'
 d['advancement.noctismagic.rituals.vampire_complete.description']='Cinque doni del colore della vita possono conquistare una fiducia immortale. Una scelta ti attende.' if it else 'Five gifts the color of life may earn immortal trust. A choice awaits you.'
 write_noctis_json_resource(p,d)
print('Blood gifts earn two hearts; Phos emeralds, Cinnabar redstone, Griffith guaranteed Crimson Behelit.')


# Xenomorph: neutral while wild, extremely dangerous when provoked; taming requires peace.
edit('Xenomorph.java','private int strike,acid;','private int strike,acid,anger;private java.util.UUID attacker;')
edit('Xenomorph.java','Attributes.MAX_HEALTH,100).add(Attributes.ATTACK_DAMAGE,19).add(Attributes.ARMOR,9)','Attributes.MAX_HEALTH,150).add(Attributes.ATTACK_DAMAGE,27).add(Attributes.ARMOR,13)')
edit('Xenomorph.java','    @Override public boolean wantsToAttack(LivingEntity target,LivingEntity owner){','''    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float amount){
        boolean hit=super.hurt(source,amount);
        if(hit&&isAlive()&&!isTame()&&level() instanceof ServerLevel l&&source.getEntity() instanceof LivingEntity enemy&&enemy!=this&&!(enemy instanceof Player p&&(p.isCreative()||p.isSpectator()))){
            attacker=enemy.getUUID();anger=900;setTarget(enemy);setAggressive(true);
            l.broadcastEntityEvent(this,(byte)83);playSound(SoundEvents.SPIDER_HURT,1,.45f);
        }
        return hit;
    }
    private boolean validPrey(LivingEntity e){
        if(e==null||!e.isAlive()||e==this)return false;
        if(e instanceof Player p&&(p.isCreative()||p.isSpectator()))return false;
        return isTame()?Eclipse.hostile(e):anger>0&&e.getUUID().equals(attacker);
    }
    @Override public boolean wantsToAttack(LivingEntity target,LivingEntity owner){''')
edit('Xenomorph.java','if(!isTame()&&isFood(s)){','''if(!isTame()&&h==InteractionHand.MAIN_HAND&&(s.isEmpty()||isFood(s))&&anger>0){
            if(p instanceof net.minecraft.server.level.ServerPlayer sp)sp.displayClientMessage(net.minecraft.network.chat.Component.literal("Lo Xenomorfo e ancora aggressivo. Aspetta che si calmi."),true);
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if(!isTame()&&s.isEmpty()&&h==InteractionHand.MAIN_HAND){
            if(p instanceof net.minecraft.server.level.ServerPlayer sp)sp.displayClientMessage(net.minecraft.network.chat.Component.literal("Offri carne cruda o carne marcia allo Xenomorfo, senza attaccarlo."),true);
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if(!isTame()&&isFood(s)){''')
edit('Xenomorph.java','tame(p);setPersistenceRequired();setHealth(getMaxHealth());','tame(p);anger=0;attacker=null;setTarget(null);setAggressive(false);setPersistenceRequired();setHealth(getMaxHealth());')
edit('Xenomorph.java','if(!isTame()||!(e instanceof LivingEntity le)||!Eclipse.hostile(le))return false;','if(!(e instanceof LivingEntity le)||!validPrey(le))return false;')
edit('Xenomorph.java','if(!(level() instanceof ServerLevel l)||!isTame()||isOrderedToSit())return;','''if(!(level() instanceof ServerLevel l)||isOrderedToSit())return;
        if(!isTame()){
            if(anger>0)anger--;
            LivingEntity enemy=attacker!=null&&l.getEntity(attacker) instanceof LivingEntity v?v:null;
            if(anger<=0||!validPrey(enemy)||distanceTo(enemy)>48){anger=0;attacker=null;setTarget(null);setAggressive(false);return;}
            setTarget(enemy);
        }''')
edit('Xenomorph.java','!Eclipse.hostile(v)||acid>0','!validPrey(v)||acid>0')
edit('Xenomorph.java','acid=110;','acid=75;')
edit('Xenomorph.java','v.hurt(damageSources().mobAttack(this),8);v.addEffect(new MobEffectInstance(MobEffects.POISON,100,0));','v.hurt(damageSources().mobAttack(this),14);v.addEffect(new MobEffectInstance(MobEffects.POISON,140,1));')
# Save anger and aggressor across chunk unloads.
edit('Xenomorph.java','    @Override public AgeableMob getBreedOffspring','''    @Override public void addAdditionalSaveData(net.minecraft.nbt.CompoundTag t){super.addAdditionalSaveData(t);t.putInt("AngerTicks",anger);if(attacker!=null)t.putUUID("AngerTarget",attacker);}
    @Override public void readAdditionalSaveData(net.minecraft.nbt.CompoundTag t){super.readAdditionalSaveData(t);anger=t.getInt("AngerTicks");attacker=t.hasUUID("AngerTarget")?t.getUUID("AngerTarget"):null;}
    @Override public AgeableMob getBreedOffspring''')
# Original horror creature, an uncanny six-limbed contorted living ossuary.
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,'''public static final RegistryObject<EntityType<OssuaryCrawler>> OSSUARY_CRAWLER=ENTITIES.register("ossuary_crawler",()->EntityType.Builder.<OssuaryCrawler>of(OssuaryCrawler::new,MobCategory.MONSTER).sized(2.0f,2.5f).clientTrackingRange(12).build(ID+":ossuary_crawler"));
    public static final RegistryObject<Item> OSSUARY_CRAWLER_EGG=ITEMS.register("ossuary_crawler_spawn_egg",()->new ForgeSpawnEggItem(OSSUARY_CRAWLER,0x33272f,0xbfb4a0,new Item.Properties()));
    '''+a)
edit('Noctis.java','e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());','e.put(OSSUARY_CRAWLER.get(),OssuaryCrawler.attributes().build());e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(OSSUARY_CRAWLER_EGG.get());')
write('OssuaryCrawler.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class OssuaryCrawler extends Monster{
 private int windup,cd=80,pose,mode;
 public OssuaryCrawler(EntityType<? extends Monster> t,Level l){super(t,l);setMaxUpStep(1f);}
 public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,220).add(Attributes.ATTACK_DAMAGE,23).add(Attributes.ARMOR,11).add(Attributes.MOVEMENT_SPEED,.30).add(Attributes.FOLLOW_RANGE,36).add(Attributes.KNOCKBACK_RESISTANCE,.65);}
 @Override protected void registerGoals(){
  goalSelector.addGoal(0,new FloatGoal(this));
  goalSelector.addGoal(1,new MeleeAttackGoal(this,1.25,true){@Override public boolean canUse(){return windup==0&&super.canUse();}@Override public boolean canContinueToUse(){return windup==0&&super.canContinueToUse();}});
  goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.7));
  goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,10));
  targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));
 }
 @Override public void tick(){
  super.tick();if(pose>0)pose--;if(cd>0)cd--;
  if(!(level() instanceof ServerLevel l))return;
  LivingEntity t=getTarget();
  if(t==null||!t.isAlive()){windup=0;return;}
  if(windup>0){
   getNavigation().stop();getLookControl().setLookAt(t,45,45);
   if(--windup==0){
    if(distanceTo(t)<9&&hasLineOfSight(t)){
     if(mode==0){
      for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(6),p->!p.isCreative()&&!p.isSpectator()&&hasLineOfSight(p))){p.addEffect(new MobEffectInstance(MobEffects.DARKNESS,120,0));p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,90,2));p.hurt(damageSources().magic(),9);}
      l.sendParticles(ParticleTypes.SMOKE,getX(),getY()+1.5,getZ(),60,1.6,.5,1.6,.08);playSound(SoundEvents.WARDEN_ROAR,1,.8f);
     }else{
      Vec3 d=t.position().subtract(position());Vec3 v=new Vec3(d.x,0,d.z).normalize().scale(.85);
      if(onGround())setDeltaMovement(v.x,.32,v.z);
      if(distanceTo(t)<4.8){t.hurt(damageSources().mobAttack(this),30);t.knockback(1.35,getX()-t.getX(),getZ()-t.getZ());}
      l.sendParticles(ParticleTypes.POOF,getX(),getY()+.25,getZ(),32,.7,.15,.7,.08);
     }
    }cd=100;return;
   }return;
  }
  if(cd==0&&distanceTo(t)<8&&hasLineOfSight(t)){mode=random.nextInt(2);windup=25;getNavigation().stop();l.broadcastEntityEvent(this,(byte)(mode==0?114:115));playSound(SoundEvents.ENDERMAN_STARE,.8f,.55f);}
 }
 @Override public boolean doHurtTarget(Entity target){boolean ok=super.doHurtTarget(target);if(ok&&level() instanceof ServerLevel l)l.broadcastEntityEvent(this,(byte)116);return ok;}
 @Override public void handleEntityEvent(byte id){if(id>=114&&id<=116){pose=id==116?16:32;mode=id==115?1:0;return;}super.handleEntityEvent(id);}
 public float action(){return pose>0?(float)Math.sin(Math.PI*pose/(pose>16?32f:32f)):0;}
 public int attackMode(){return mode;}
 @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource source,int looting,boolean hit){super.dropCustomDeathLoot(source,looting,hit);spawnAtLocation(Items.BONE,6+random.nextInt(7));spawnAtLocation(Items.ECHO_SHARD,1+random.nextInt(2));}
}''')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if((!l.isDay()||Eclipse.active(l))&&l.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL&&!p.isCreative()&&!p.isSpectator()&&p.getRandom().nextInt(Eclipse.active(l)?10:55)==0&&l.getEntitiesOfClass(OssuaryCrawler.class,p.getBoundingBox().inflate(96)).isEmpty()){
            BlockPos q=Eclipse.spot(p,20,32);if(q!=null){OssuaryCrawler m=Noctis.OSSUARY_CRAWLER.get().create(l);if(m!=null){m.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(m))l.addFreshEntity(m);}}
        }''')
write('OssuaryCrawlerClient.java','''package it.noctis.magic;
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
public class OssuaryCrawlerClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.OSSUARY_CRAWLER.get(),R::new);}
 static class M extends EntityModel<OssuaryCrawler>{
  final Part root=new Part(0,0,0),body=root.child(0,8,0),head=body.child(0,-4,-4),jaw=head.child(0,1.1f,-2.0f);
  final Part[] legs=new Part[6],shins=new Part[6],spines=new Part[7],masks=new Part[3];
  M(){
   Part barrel=body.child(0,0,0);barrel.rx=1.15f;
   barrel.loft(0,24,-9,0,0,1.25f,1.5f,-6,0,0,3.1f,3.4f,-2,0,0,4.9f,4.1f,3,0,0,4.0f,3.25f,7,0,0,2.6f,2.5f,9,0,0,.9f,1.0f);
   for(int j=0;j<7;j++){
    Part s=spines[j]=body.child(0,-3.2f-j*.22f,-4+j*1.45f);
    s.loft(1,12,-4.5f,0,.9f,.06f,.08f,-2,0,.45f,.55f,.70f,0,0,0,1.10f,.75f);
    for(int side:new int[]{-1,1}){
     Part rib=body.child(side*2.2f,-2.5f,-4.0f+j*1.30f);
     rib.loft(1,14,-.9f,0,0,.32f,.48f,.6f,side*1.65f,0,.45f,.55f,2.2f,side*2.0f,-.1f,.40f,.47f,3.7f,side*.8f,-.55f,.21f,.27f);
    }
   }
   head.loft(1,24,-5.4f,0,.5f,.7f,.8f,-4.8f,0,.2f,2.0f,1.7f,-2.8f,0,0,2.8f,2.2f,-1,0,0,2.5f,2.0f,.6f,0,-.2f,1.8f,1.35f);
   head.oval(2,-1.10f,-2.55f,-1.99f,.64f,.78f,.20f);head.oval(2,1.10f,-2.55f,-1.99f,.64f,.78f,.20f);
   jaw.loft(0,18,-.8f,0,0,1.8f,.6f,1.5f,0,-.45f,1.55f,1.05f,2.25f,0,-.70f,.62f,.35f);
   for(int i=0;i<7;i++){float x=-1.5f+i*.5f;head.blade(1,x,.35f,-1.9f,x,1.45f,-2.45f,.38f);jaw.blade(1,x,1.0f,-1.0f,x,-.5f,-1.40f,.34f);}
   for(int i=0;i<3;i++){
    Part m=masks[i]=body.child((i-1)*1.75f,-2.1f,-5.5f+i*.28f);m.ry=(i-1)*.25f;
    m.oval(3,0,0,0,.95f,1.55f,.65f);
    m.oval(2,-.35f,-.3f,-.54f,.20f,.26f,.09f);m.oval(2,.35f,-.3f,-.54f,.20f,.26f,.09f);
   }
   for(int i=0;i<6;i++){
    int side=i<3?-1:1;int j=i%3;
    Part leg=legs[i]=body.child(side*(3.2f+j*.25f),.65f,j*4.15f-4.1f);
    leg.loft(0,18,-.7f,0,0,1.0f,1.0f,1.5f,side*1.2f,0,1.3f,1.05f,5.0f,side*2.9f,.2f,.62f,.72f,7.0f,side*3.1f,0,.54f,.62f);
    Part shin=shins[i]=leg.child(side*3.1f,7,0);
    shin.loft(1,18,-.3f,0,0,.58f,.64f,3.7f,side*.6f,-.3f,.48f,.54f,7.2f,side*.25f,-.4f,.32f,.38f,8.6f,0,-.5f,.5f,.64f);
    for(int n=0;n<3;n++)shin.blade(1,-.4f+n*.4f,8.2f,-.35f,-.52f+n*.52f,9.0f,-2.0f,.33f);
   }
  }
  @Override public void setupAnim(OssuaryCrawler e,float limb,float amount,float age,float yaw,float pitch){
   float a=e.action();body.y=8+(float)Math.sin(limb*1.2f)*amount*.50f;body.rz=(float)Math.sin(limb*.7f)*amount*.045f;body.rx=-a*.10f;
   head.ry=yaw*.014f;head.rx=pitch*.012f-a*.24f;head.rz=(float)Math.sin(age*.12f)*.06f;jaw.rx=.10f+(float)Math.sin(age*.19f)*.08f+a*.85f;
   for(int i=0;i<6;i++){float w=(float)Math.cos(limb*.92f+(i/3+i%3)*Math.PI)*amount;int side=i<3?-1:1;legs[i].rz=-side*(.14f+w*.16f);legs[i].rx=w*.55f-a*.17f;shins[i].rx=-w*.60f;}
   for(int i=0;i<7;i++)spines[i].rz=(float)Math.sin(age*.17f-i*.65f)*(.065f+a*.10f);
   for(int i=0;i<3;i++)masks[i].rz=(float)Math.sin(age*.11f+i)*.10f;
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<OssuaryCrawler,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.85f);}
  @Override protected void scale(OssuaryCrawler e,PoseStack p,float partial){p.scale(1.4f,1.4f,1.4f);}
  @Override public ResourceLocation getTextureLocation(OssuaryCrawler e){return new ResourceLocation(Noctis.ID,"textures/entity/ossuary_crawler.png");}
 }
}''')
W,H=1024,512;pix=bytearray(W*H*4)
for m,base in enumerate([(72,48,57),(189,178,155),(20,12,24),(147,139,129)]):
 for yy in range(128):
  v=yy/127
  for xx in range(128):
   u=xx/127;grain=.5+.5*math.sin(u*89+v*14)*math.cos(v*93)
   c=shade(base,.74+.24*math.sin(u*math.pi)**2+.08*grain)
   if m==0:c=mix(c,(38,26,43),.38*math.exp(-(((u*7+v*.28)%1-.5)/.12)**2))
   if m in (1,3):c=mix(c,(92,75,78),.20*math.exp(-((u-.86)/.12)**2)+.10*grain)
   if m==2:c=mix(c,(134,74,100),.24*math.exp(-((u-.48)/.28)**2))
   off=(yy*W+m*128+xx)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/ossuary_crawler.png',W,H,pix)
write_noctis_json_resource(assets/'models/item/ossuary_crawler_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['entity.noctismagic.ossuary_crawler']='Ossario Strisciante' if it else 'Crawling Ossuary'
 d['item.noctismagic.ossuary_crawler_spawn_egg']='Uovo generatore: Ossario Strisciante' if it else 'Crawling Ossuary Spawn Egg'
 write_noctis_json_resource(p,d)
print('Neutral retaliatory Xenomorph and new six-legged Crawling Ossuary horror.')


# Jotaro's wearable black cap, gold emblem and decorative chain.
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<Item> JOTARO_CAP=ITEMS.register("jotaro_cap",()->new JotaroCap());
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(JOTARO_CAP.get());')
edit('JojoMob.java','    @Override public void handleEntityEvent(byte id){','''    @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource source,int looting,boolean hit){
        super.dropCustomDeathLoot(source,looting,hit);
        if(variant()==0)spawnAtLocation(Noctis.JOTARO_CAP.get());
    }
    @Override public void handleEntityEvent(byte id){''')
write('JotaroCap.java','''package it.noctis.magic;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.*;
import net.minecraft.world.level.Level;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import java.util.List;
import java.util.function.Consumer;
public class JotaroCap extends ArmorItem{
 static final ArmorMaterial MATERIAL=new ArmorMaterial(){
  public int getDurabilityForType(ArmorItem.Type t){return (switch(t){case HELMET->11;case CHESTPLATE->16;case LEGGINGS->15;case BOOTS->13;})*55;}
  public int getDefenseForType(ArmorItem.Type t){return t==ArmorItem.Type.HELMET?7:0;}
  public int getEnchantmentValue(){return 22;}
  public SoundEvent getEquipSound(){return SoundEvents.ARMOR_EQUIP_NETHERITE;}
  public Ingredient getRepairIngredient(){return Ingredient.of(Items.GOLD_INGOT);}
  public String getName(){return "noctismagic:jotaro_cap";}
  public float getToughness(){return 4f;}
  public float getKnockbackResistance(){return .15f;}
 };
 public JotaroCap(){super(MATERIAL,ArmorItem.Type.HELMET,new Item.Properties().rarity(Rarity.EPIC).fireResistant());}
 @Override public void onArmorTick(ItemStack stack,Level level,Player p){
  if(level.isClientSide||p.tickCount%10!=0||p.getItemBySlot(EquipmentSlot.HEAD)!=stack)return;
  MobEffectInstance effect=p.getEffect(MobEffects.DAMAGE_BOOST);
  if(effect==null||effect.getAmplifier()<1||(effect.getAmplifier()==1&&effect.getDuration()<30))p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,60,1,true,false,true));
 }
 @Override public void appendHoverText(ItemStack stack,Level level,List<Component> text,TooltipFlag flag){
  super.appendHoverText(stack,level,text,flag);
  text.add(Component.translatable("item.noctismagic.jotaro_cap.desc").withStyle(net.minecraft.ChatFormatting.GOLD));
 }
 @Override public void initializeClient(Consumer<IClientItemExtensions> consumer){JotaroCapClient.register(consumer);}
}''')
# Cap model uses vanilla armor rendering, with real projecting visor and independent gold links.
write('JotaroCapClient.java','''package it.noctis.magic;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import java.util.function.Consumer;
public final class JotaroCapClient{
 static HumanoidModel<LivingEntity> create(){
  MeshDefinition mesh=HumanoidModel.createMesh(CubeDeformation.NONE,0);
  PartDefinition root=mesh.getRoot();
  PartDefinition head=root.addOrReplaceChild("head",CubeListBuilder.create()
   .texOffs(0,0).addBox(-4.55f,-9.8f,-4.35f,9.1f,3.5f,8.7f)
   .texOffs(0,16).addBox(-4.3f,-10.2f,-4.0f,8.6f,1.0f,8.0f)
   .texOffs(0,28).addBox(-4.4f,-6.9f,-7.0f,8.8f,.65f,4.0f)
   .texOffs(0,40).addBox(-4.6f,-6.7f,-4.4f,9.2f,.6f,8.8f),PartPose.ZERO);
  root.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
  head.addOrReplaceChild("emblem",CubeListBuilder.create().texOffs(48,0).addBox(-2.9f,-8.9f,-4.6f,1.65f,1.65f,.35f)
   .texOffs(56,0).addBox(.8f,-8.85f,-4.60f,2f,1.45f,.35f)
   .texOffs(56,5).addBox(1.05f,-9.15f,-4.61f,.30f,.55f,.35f),PartPose.ZERO);
  for(int i=0;i<5;i++){
   PartDefinition link=head.addOrReplaceChild("chain"+i,CubeListBuilder.create()
    .texOffs(64,0).addBox(-.45f,-.6f,-.16f,.90f,.20f,.32f)
    .texOffs(64,4).addBox(-.45f,.4f,-.16f,.90f,.20f,.32f)
    .texOffs(64,8).addBox(-.45f,-.4f,-.16f,.20f,.8f,.32f)
    .texOffs(64,12).addBox(.25f,-.4f,-.16f,.20f,.8f,.32f),
    PartPose.offsetAndRotation(4.62f+i*.08f,-6.75f+i*.87f,-1.8f+i*.20f,0,i%2==0?.15f:1.25f,-.12f));
  }
  return new HumanoidModel<>(LayerDefinition.create(mesh,128,128).bakeRoot());
 }
 public static void register(Consumer<IClientItemExtensions> consumer){
  consumer.accept(new IClientItemExtensions(){
   private HumanoidModel<LivingEntity> cap;
   @Override public HumanoidModel<?> getHumanoidArmorModel(LivingEntity entity,ItemStack stack,EquipmentSlot slot,HumanoidModel<?> original){
    if(cap==null)cap=create();
    cap.head.copyFrom(original.head);cap.hat.copyFrom(original.hat);
    cap.head.visible=true;cap.hat.visible=false;cap.body.visible=false;cap.rightArm.visible=false;cap.leftArm.visible=false;cap.rightLeg.visible=false;cap.leftLeg.visible=false;
    cap.young=original.young;cap.riding=original.riding;cap.crouching=original.crouching;
    return cap;
   }
  });
 }
}''')
W=128;H=128;pix=bytearray(W*H*4)
for y in range(H):
 for x in range(W):
  if x<40 and y<52:
   c=(27+int(9*math.sin(x*.33)**2),28+int(8*math.sin(x*.33)**2),38+int(11*math.sin(x*.33)**2))
   if 39<=y<=50:c=(34,34,44)
  elif 48<=x<82 and y<18:c=(int(190+48*math.sin(x*.75)**2),int(132+58*math.sin(x*.75)**2),int(37+43*math.sin(x*.75)**2))
  else:c=(24,24,33)
  off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/models/armor/jotaro_cap_layer_1.png',W,H,pix)
# Inventory icon, dark peaked cap and gold chain.
W=64;H=64;pix=bytearray(W*H*4)
for y in range(H):
 for x in range(W):
  c=None
  if 10<=x<=51 and 14<=y<=36 and ((x-31)/22)**2+((y-28)/19)**2<1:
   c=shade((33,34,46),.82+.30*(1-y/64))
  if 5<=x<=51 and 33<=y<=40 and ((x-29)/25)**2+((y-36)/5)**2<1:c=(27,28,40)
  if 13<=x<=49 and 31<=y<=34:c=(67,62,61)
  if 17<=x<=23 and 23<=y<=29:c=(231,180,65)
  if 34<=x<=41 and 23<=y<=28:c=(207,155,45)
  for n in range(5):
   dx=(x-(49+n*.4))/3.0;dy=(y-(36+n*4.0))/3.0;d=dx*dx+dy*dy
   if .32<d<1.15:c=(242,190,70) if dx<0 else (164,111,30)
  if c is not None:
   off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/item/jotaro_cap.png',W,H,pix)
write_noctis_json_resource(assets/'models/item/jotaro_cap.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/jotaro_cap'}})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['item.noctismagic.jotaro_cap']='Cappello di Jotaro' if it else "Jotaro's Cap"
 d['item.noctismagic.jotaro_cap.desc']='Forza II mentre indossato.' if it else 'Strength II while worn.'
 write_noctis_json_resource(p,d)
print('Jotaro guaranteed wearable epic cap with gold chain, 7 armor and Strength II.')


# Bucciarati's spatial zipper and Giorno's occasional plant growth.
edit('JojoMob.java','private int punch,ability,dialogue;','''private int punch,ability,dialogue;
    private int lifeCooldown=1000,zipCooldown=600,zipTicks;
    private Vec3 zipDestination;
    private Vec3 zipOrigin;
    private float zipYaw;''')
edit('JojoMob.java','return !stand()&&super.canUse();','return !stand()&&zipTicks==0&&super.canUse();')
edit('JojoMob.java','if(!(level() instanceof ServerLevel l)||!stand())return;','''if(!(level() instanceof ServerLevel l))return;
        if(!stand()){JojoWorldPowers.tick(this,l);return;}''')
edit('JojoMob.java','private int lifeCooldown=1000,zipCooldown=600,zipTicks;','int lifeCooldown=1000,zipCooldown=600,zipTicks;')
edit('JojoMob.java','private Vec3 zipDestination;\n    private Vec3 zipOrigin;\n    private float zipYaw;','Vec3 zipDestination;\n    Vec3 zipOrigin;\n    float zipYaw;')
# Trigger a quicker escape when attacked, without altering existing stand defense.
edit('JojoMob.java','if(activeStand!=null&&l.getEntity(activeStand) instanceof JojoMob st&&st.isAlive()){','''if(variant()==1&&zipCooldown==0&&zipTicks==0)JojoWorldPowers.beginZip(this,l);
            if(activeStand!=null&&l.getEntity(activeStand) instanceof JojoMob st&&st.isAlive()){''')
write('JojoWorldPowers.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.BoneMealItem;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
public final class JojoWorldPowers{
 static final DustParticleOptions DARK=new DustParticleOptions(new Vector3f(.07f,.04f,.15f),1.65f);
 static final DustParticleOptions GOLD=new DustParticleOptions(new Vector3f(1f,.70f,.16f),1.2f);
 static final DustParticleOptions BLUE=new DustParticleOptions(new Vector3f(.25f,.65f,.98f),.85f);
 static void tick(JojoMob m,ServerLevel l){
  if(m.variant()==1){
   if(m.zipCooldown>0)m.zipCooldown--;
   if(m.zipTicks>0){
    m.getNavigation().stop();m.setDeltaMovement(0,m.getDeltaMovement().y,0);
    if(m.zipTicks%3==0&&m.zipOrigin!=null&&m.zipDestination!=null){
     zipper(l,m.zipOrigin,m.zipYaw,Math.min(1,(25-m.zipTicks)/9f));zipper(l,m.zipDestination,m.zipYaw,.8f);
    }
    if(m.zipTicks==12&&m.zipDestination!=null){
     Vec3 q=m.zipDestination;
     if(safe(m,l,q)){m.teleportTo(q.x,q.y,q.z);m.setDeltaMovement(Vec3.ZERO);m.resetFallDistance();m.playSound(SoundEvents.ENDERMAN_TELEPORT,1,.85f);}
    }
    if(--m.zipTicks==0){m.zipOrigin=null;m.zipDestination=null;}
    return;
   }
   if(m.zipCooldown==0&&m.onGround()&&!m.isInWater()&&l.getNearestPlayer(m,18)!=null&&m.getRandom().nextInt(100)==0)beginZip(m,l);
  }else if(m.variant()==2){
   if(m.lifeCooldown>0)m.lifeCooldown--;
   if(m.lifeCooldown==0&&m.onGround()&&l.getNearestPlayer(m,18)!=null&&m.getRandom().nextInt(120)==0){
    int grown=0;
    for(int i=0;i<24&&grown<5;i++){
     BlockPos q=m.blockPosition().offset(m.getRandom().nextInt(13)-6,m.getRandom().nextInt(5)-2,m.getRandom().nextInt(13)-6);
     if(!l.hasChunkAt(q))continue;
     Block b=l.getBlockState(q).getBlock();
     if(!(b instanceof CropBlock||b instanceof StemBlock||b instanceof SaplingBlock||b instanceof SweetBerryBushBlock||b instanceof GrassBlock))continue;
     if(BoneMealItem.growCrop(new ItemStack(Items.BONE_MEAL),l,q)){
      grown++;l.levelEvent(1505,q,0);l.sendParticles(ParticleTypes.HAPPY_VILLAGER,q.getX()+.5,q.getY()+.8,q.getZ()+.5,12,.3,.35,.3,.03);
     }
    }
    m.lifeCooldown=grown>0?1800+m.getRandom().nextInt(1800):240;
    if(grown>0){m.playSound(SoundEvents.AMETHYST_BLOCK_CHIME,.75f,1.4f);l.sendParticles(GOLD,m.getX(),m.getY()+1,m.getZ(),24,.4,.5,.4,.04);}
   }
  }
 }
 static boolean safe(JojoMob m,ServerLevel l,Vec3 q){
  BlockPos p=BlockPos.containing(q);
  if(!l.hasChunkAt(p)||p.getY()<l.getMinBuildHeight()+1||p.getY()>l.getMaxBuildHeight()-3||!l.getWorldBorder().isWithinBounds(p))return false;
  if(!l.getBlockState(p.below()).isFaceSturdy(l,p.below(),Direction.UP)||!l.getFluidState(p).isEmpty()||!l.getFluidState(p.above()).isEmpty())return false;
  return l.noCollision(m,m.getBoundingBox().move(q.x-m.getX(),q.y-m.getY(),q.z-m.getZ()));
 }
 static void beginZip(JojoMob m,ServerLevel l){
  if(m.zipTicks>0||!m.onGround()||m.isInWater())return;
  for(int i=0;i<28;i++){
   double angle=m.getRandom().nextDouble()*Math.PI*2,range=6+m.getRandom().nextInt(8);
   int x=(int)Math.floor(m.getX()+Math.cos(angle)*range),z=(int)Math.floor(m.getZ()+Math.sin(angle)*range);
   for(int dy:new int[]{0,1,-1,2,-2,3,-3}){
    Vec3 q=new Vec3(x+.5,m.getBlockY()+dy,z+.5);
    if(!safe(m,l,q))continue;
    m.zipOrigin=m.position();m.zipDestination=q;m.zipYaw=m.getYRot();m.zipTicks=24;m.zipCooldown=900+m.getRandom().nextInt(1000);
    m.getNavigation().stop();m.playSound(SoundEvents.ARMOR_EQUIP_CHAIN,.9f,.8f);
    zipper(l,m.zipOrigin,m.zipYaw,.2f);return;
   }
  }
  m.zipCooldown=200;
 }
 // Large vertical zipper with two opening rows of golden teeth, dark seam and moving slider.
 static void zipper(ServerLevel l,Vec3 pos,float yaw,float open){
  double r=Math.toRadians(yaw),ax=Math.cos(r),az=Math.sin(r),nx=-Math.sin(r),nz=Math.cos(r);
  for(int i=0;i<15;i++){
   double y=.08+i*.19,w=.12+open*.48*Math.sin(Math.PI*i/14);
   for(int s:new int[]{-1,1}){
    double x=pos.x+ax*s*w,z=pos.z+az*s*w;
    l.sendParticles(DARK,x,pos.y+y,z,1,0,0,0,0);
    l.sendParticles(GOLD,x+ax*s*.12,pos.y+y,z+az*s*.12,1,0,0,0,0);
    if(i%2==0)l.sendParticles(BLUE,x+ax*s*.24,pos.y+y,z+az*s*.24,1,0,0,0,0);
   }
   l.sendParticles(DARK,pos.x,pos.y+y,pos.z,1,0,0,0,0);
  }
  double sy=pos.y+2.8-open*1.9;
  for(int a=0;a<10;a++){double t=a*Math.PI/5;l.sendParticles(GOLD,pos.x+ax*.19*Math.cos(t)+nx*.04,sy+.23*Math.sin(t),pos.z+az*.19*Math.cos(t)+nz*.04,1,0,0,0,0);}
 }
}''')
print('Bucciarati spatial zipper teleportation with opening particles and Giorno rare vegetation growth.')


# Lelouch's defensive Geass: force an aggressor to walk away, never damage them or teleport them.
edit('VampireLife.java','public static final RegistryObject<MobEffect> BAT=EFFECTS.register','''public static final RegistryObject<MobEffect> GEASS_EXILE=EFFECTS.register("geass_exile",()->new MobEffect(MobEffectCategory.NEUTRAL,0xb52b64){});
    public static final RegistryObject<MobEffect> BAT=EFFECTS.register''')
write('GeassExile.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class GeassExile{
 static class Order{
  final UUID caster;final ServerLevel level;final Vec3 origin;Vec3 last;double walked;int ticks=2400,dir=-1,blocked;
  Order(DramaGuest g,ServerPlayer p){caster=g.getUUID();level=p.serverLevel();origin=g.position();last=p.position();}
 }
 static final Map<UUID,Order> orders=new HashMap<>();
 static boolean valid(ServerPlayer p){return p.isAlive()&&!p.isSpectator();}
 @SubscribeEvent public static void defend(LivingAttackEvent e){
  if(!(e.getEntity() instanceof DramaGuest victim)||victim.kind()==0||!(victim.level() instanceof ServerLevel l)||!(e.getSource().getEntity() instanceof ServerPlayer p)||!valid(p))return;
  DramaGuest lelouch=victim.kind()==1?victim:victim.partner!=null&&l.getEntity(victim.partner) instanceof DramaGuest q&&q.kind()==1&&q.isAlive()?q:null;
  if(lelouch==null||!lelouch.isAlive()||lelouch.distanceTo(p)>24)return;
  e.setCanceled(true);
  if(orders.containsKey(p.getUUID()))return;
  lelouch.getNavigation().stop();lelouch.getLookControl().setLookAt(p,60,60);
  lelouch.say(l,"Io, Lelouch vi Britannia, ti ordino: vattene!");
  l.sendParticles(ParticleTypes.WITCH,lelouch.getX(),lelouch.getEyeY(),lelouch.getZ(),30,.18,.12,.18,.025);
  p.playSound(SoundEvents.BEACON_POWER_SELECT,1,.65f);p.stopRiding();
  orders.put(p.getUUID(),new Order(lelouch,p));
  p.displayClientMessage(Component.translatable("message.noctismagic.geass_order"),false);
 }
 static Vec3 direction(int i){double a=i*Math.PI/8;return new Vec3(-Math.sin(a),0,Math.cos(a));}
 static boolean safe(ServerPlayer p,Vec3 d){
  ServerLevel l=p.serverLevel();
  for(double step:new double[]{.65,1.25}){
   Vec3 q=p.position().add(d.scale(step));BlockPos b=BlockPos.containing(q);
   if(!l.hasChunkAt(b)||!l.getWorldBorder().isWithinBounds(b))return false;
   boolean ok=false;
   for(int dy:new int[]{0,1,-1}){
    BlockPos v=b.offset(0,dy,0),floor=v.below();var state=l.getBlockState(floor);
    if(!state.isFaceSturdy(l,floor,Direction.UP)||state.is(Blocks.MAGMA_BLOCK)||state.is(Blocks.CAMPFIRE)||state.is(Blocks.SOUL_CAMPFIRE)||state.is(Blocks.CACTUS))continue;
    if(!l.getFluidState(v).isEmpty()||!l.getFluidState(v.above()).isEmpty())continue;
    if(l.noCollision(p,p.getBoundingBox().move(d.x*step,dy,d.z*step))){ok=true;break;}
   }if(!ok)return false;
  }return true;
 }
 static void release(ServerPlayer p,boolean done){
  orders.remove(p.getUUID());p.removeEffect(VampireLife.GEASS_EXILE.get());
  p.displayClientMessage(Component.translatable(done?"message.noctismagic.geass_free":"message.noctismagic.geass_break"),false);
 }
 @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
  if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
  Order o=orders.get(p.getUUID());
  if(o==null){if(p.hasEffect(VampireLife.GEASS_EXILE.get()))p.removeEffect(VampireLife.GEASS_EXILE.get());return;}
  if(!valid(p)||p.serverLevel()!=o.level||--o.ticks<=0){release(p,false);return;}
  Vec3 now=p.position(),delta=now.subtract(o.last);o.last=now;
  double moved=Math.sqrt(delta.x*delta.x+delta.z*delta.z);
  if(moved<1.2&&o.dir>=0&&delta.dot(direction(o.dir))>0)o.walked+=moved;
  if(o.walked>=200){release(p,true);return;}
  if(p.isPassenger())p.stopRiding();
  if(p.getAbilities().flying){p.getAbilities().flying=false;p.onUpdateAbilities();}
  if(o.dir<0||p.tickCount%5==0||!safe(p,direction(o.dir))){
   Vec3 away=now.subtract(o.origin);away=new Vec3(away.x,0,away.z);
   if(away.lengthSqr()<.01)away=p.getLookAngle();
   away=away.normalize();
   int best=-1;double score=-2;
   for(int i=0;i<16;i++){
    Vec3 d=direction(i);double s=d.dot(away)+(i==o.dir?.22:0);
    if(s>score&&safe(p,d)){best=i;score=s;}
   }
   if(best<0){o.blocked++;if(o.blocked>80){release(p,false);return;}best=16;}
   else o.blocked=0;
   if(o.dir!=best||!p.hasEffect(VampireLife.GEASS_EXILE.get())){
    o.dir=best;p.removeEffect(VampireLife.GEASS_EXILE.get());p.addEffect(new MobEffectInstance(VampireLife.GEASS_EXILE.get(),o.ticks+20,best,false,false,false));
   }
  }
  if(o.dir<16){p.setYRot(o.dir*22.5f);p.setYHeadRot(o.dir*22.5f);}
  if(p.tickCount%20==0){p.displayClientMessage(Component.translatable("message.noctismagic.geass_progress",Math.min(200,(int)o.walked)),true);}
 }
 @SubscribeEvent public static void preventAttack(AttackEntityEvent e){if(e.getEntity() instanceof ServerPlayer p&&orders.containsKey(p.getUUID()))e.setCanceled(true);}
 @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){orders.remove(e.getEntity().getUUID());if(e.getEntity() instanceof ServerPlayer p)p.removeEffect(VampireLife.GEASS_EXILE.get());}
}''')
write('GeassExileClient.java','''package it.noctis.magic;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.MovementInputUpdateEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT)
public class GeassExileClient{
 @SubscribeEvent public static void move(MovementInputUpdateEvent e){
  var p=Minecraft.getInstance().player;if(p==null||e.getEntity()!=p)return;
  var effect=p.getEffect(VampireLife.GEASS_EXILE.get());if(effect==null)return;
  int dir=effect.getAmplifier();var input=e.getInput();
  input.leftImpulse=0;input.forwardImpulse=dir<16?1:0;input.up=dir<16;input.down=false;input.left=false;input.right=false;input.shiftKeyDown=false;input.jumping=dir<16&&p.horizontalCollision&&p.onGround();
  if(dir<16){p.setYRot(dir*22.5f);p.setYHeadRot(dir*22.5f);}
 }
}''')
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['effect.noctismagic.geass_exile']='Ordine del Geass' if it else 'Geass command'
 d['message.noctismagic.geass_order']='Il Geass controlla il tuo corpo: allontanati!' if it else 'Geass controls your body: walk away!'
 d['message.noctismagic.geass_progress']='Geass: %s/200 blocchi percorsi' if it else 'Geass: %s/200 blocks walked'
 d['message.noctismagic.geass_free']='Il comando e terminato. Hai ripreso il controllo.' if it else 'The command is over. You are in control again.'
 d['message.noctismagic.geass_break']='Il comando del Geass si interrompe.' if it else 'The Geass command is interrupted.'
 write_noctis_json_resource(p,d)
print('Defensive Lelouch Geass: controlled 200-block walk, safe terrain and temporary input override.')


# Individual character loot and three new wearable/usable/collectible items.
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<Item> LEON_PISTOL=ITEMS.register("leon_pistol",LeonPistol::new);
    public static final RegistryObject<Item> LEON_JACKET=ITEMS.register("leon_jacket",LeonJacket::new);
    public static final RegistryObject<Item> HOPE=ITEMS.register("hope",()->new Item(new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.RARE)){
        @Override public void appendHoverText(net.minecraft.world.item.ItemStack stack,net.minecraft.world.level.Level l,java.util.List<net.minecraft.network.chat.Component> lines,net.minecraft.world.item.TooltipFlag flag){lines.add(net.minecraft.network.chat.Component.translatable("item.noctismagic.hope.desc").withStyle(net.minecraft.ChatFormatting.GRAY));}
    });
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(LEON_PISTOL.get());e.accept(LEON_JACKET.get());e.accept(HOPE.get());')
write('CharacterLoot.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.Turtle;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.*;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class CharacterLoot{
 static void add(LivingDropsEvent e,ItemStack s){LivingEntity m=e.getEntity();e.getDrops().add(new ItemEntity(m.level(),m.getX(),m.getY()+.25,m.getZ(),s));}
 static void add(LivingDropsEvent e,Item i,int count){add(e,new ItemStack(i,count));}
 static void suit(LivingDropsEvent e,int color){
  for(Item i:new Item[]{Items.LEATHER_HELMET,Items.LEATHER_CHESTPLATE,Items.LEATHER_LEGGINGS,Items.LEATHER_BOOTS}){
   ItemStack stack=new ItemStack(i);((DyeableLeatherItem)i).setColor(stack,color);add(e,stack);
  }
 }
 @SubscribeEvent public static void loot(LivingDropsEvent e){
  LivingEntity m=e.getEntity();if(!(m.level() instanceof ServerLevel l))return;
  if(m instanceof CrossoverGuest g){
   if(g.kind()==0){add(e,Noctis.LEON_PISTOL.get(),1);add(e,Noctis.LEON_JACKET.get(),1);}
   else{add(e,Items.PAPER,5+m.getRandom().nextInt(6));suit(e,g.kind()==1?0x254DAD:0xA42D49);}
  }else if(m instanceof JojoMob j&&!j.stand()){
   if(j.variant()==1)add(e,Noctis.PIZZA.get(),1);
   else if(j.variant()==2){
    add(e,Items.WHEAT_SEEDS,4+m.getRandom().nextInt(5));add(e,Items.PUMPKIN_SEEDS,2);add(e,Items.MELON_SEEDS,2);add(e,Items.OAK_SAPLING,2);add(e,Items.POPPY,2);add(e,Items.DANDELION,2);
    Turtle t=EntityType.TURTLE.create(l);
    if(t!=null){t.moveTo(m.getX(),m.getY(),m.getZ(),m.getYRot(),0);if(l.noCollision(t)){t.setPersistenceRequired();l.addFreshEntity(t);}else add(e,Items.TURTLE_SPAWN_EGG,1);}
   }
  }else if(m instanceof SushiGuest s){
   if(s.maomao()){add(e,Items.FERN,3);add(e,Items.ALLIUM,2);add(e,Items.AZURE_BLUET,2);add(e,Items.DANDELION,2);}
   else{add(e,Items.GOLD_INGOT,2+m.getRandom().nextInt(3));add(e,Items.AMETHYST_SHARD,3);add(e,Items.EMERALD,2);add(e,Items.PEONY,1);}
  }else if(m instanceof Vincent)add(e,Noctis.HOPE.get(),1);
 }
}''')
write('LeonJacket.java','''package it.noctis.magic;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
public class LeonJacket extends ArmorItem{
 static final ArmorMaterial MATERIAL=new ArmorMaterial(){
  public int getDurabilityForType(ArmorItem.Type t){return (switch(t){case HELMET->11;case CHESTPLATE->16;case LEGGINGS->15;case BOOTS->13;})*48;}
  public int getDefenseForType(ArmorItem.Type t){return t==ArmorItem.Type.CHESTPLATE?10:0;}
  public int getEnchantmentValue(){return 19;}public SoundEvent getEquipSound(){return SoundEvents.ARMOR_EQUIP_LEATHER;}
  public Ingredient getRepairIngredient(){return Ingredient.of(Items.LEATHER);}
  public String getName(){return "noctismagic:leon_jacket";}public float getToughness(){return 4;}public float getKnockbackResistance(){return .15f;}
 };
 public LeonJacket(){super(MATERIAL,ArmorItem.Type.CHESTPLATE,new Item.Properties().rarity(Rarity.EPIC));}
}''')
# Fictional ranged weapon uses game resources, block line-of-sight and cooldown.
write('LeonPistol.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
public class LeonPistol extends Item{
 public LeonPistol(){super(new Item.Properties().durability(640).rarity(Rarity.EPIC));}
 @Override public InteractionResultHolder<ItemStack> use(Level level,Player p,InteractionHand hand){
  ItemStack gun=p.getItemInHand(hand);
  if(!(level instanceof ServerLevel l))return InteractionResultHolder.sidedSuccess(gun,true);
  int slot=-1;for(int i=0;i<p.getInventory().getContainerSize();i++)if(p.getInventory().getItem(i).is(Items.IRON_NUGGET)){slot=i;break;}
  if(!p.getAbilities().instabuild&&slot<0){p.displayClientMessage(Component.translatable("message.noctismagic.leon_ammo"),true);return InteractionResultHolder.fail(gun);}
  if(!p.getAbilities().instabuild){p.getInventory().getItem(slot).shrink(1);gun.hurtAndBreak(1,p,x->x.broadcastBreakEvent(hand));}
  p.getCooldowns().addCooldown(this,12);
  Vec3 a=p.getEyePosition(),end=a.add(p.getLookAngle().scale(28));
  HitResult wall=l.clip(new ClipContext(a,end,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,p));Vec3 b=wall.getLocation();
  LivingEntity target=null;double best=a.distanceToSqr(b);
  for(LivingEntity e:l.getEntitiesOfClass(LivingEntity.class,new AABB(a,b).inflate(1),e->e!=p&&e.isAlive()&&!(e instanceof Player q&&q.isSpectator()))){
   var hit=e.getBoundingBox().inflate(.15).clip(a,b);if(hit.isPresent()&&a.distanceToSqr(hit.get())<best){best=a.distanceToSqr(hit.get());target=e;}
  }
  if(target!=null){target.hurt(p.damageSources().playerAttack(p),14);b=a.add(p.getLookAngle().scale(Math.sqrt(best)));}
  for(int i=1;i<=12;i++){Vec3 v=a.lerp(b,i/12.0);l.sendParticles(ParticleTypes.CRIT,v.x,v.y-.08,v.z,1,.012,.012,.012,0);}
  p.playSound(SoundEvents.FIREWORK_ROCKET_BLAST,.8f,1.8f);return InteractionResultHolder.success(gun);
 }
 @Override public void appendHoverText(ItemStack s,Level l,java.util.List<Component> lines,TooltipFlag flag){lines.add(Component.translatable("item.noctismagic.leon_pistol.desc").withStyle(net.minecraft.ChatFormatting.GRAY));}
}''')
# Detailed brown leather and shearling jacket, using vanilla 64x32 armor UV scaled 4x.
W,H=256,128;pix=bytearray(W*H*4)
for y in range(H):
 for x in range(W):
  u=x/4;v=y/4
  # Main body and sleeves; draw leather panels, cuffs and shearling collar.
  if 16<=u<40 and 16<=v<32 or 40<=u<56 and 16<=v<32:
   grain=.5+.5*math.sin(x*1.91+y*.72)*math.cos(y*2.03-x*.31)
   c=shade((93,61,40),.72+.31*grain+.12*math.sin(u*.9)**2)
   if 20<=u<28 and 20<=v<32:
    if v<23 and abs(u-24)<(23-v)*.80+1.1:c=shade((204,185,143),.82+.15*grain)
    if abs(u-24)<.28 and v>=23:c=(145,121,81)
    if 25<=v<=28 and (21<=u<=22.5 or 25.5<=u<=27):c=shade(c,.65)
   if v>30 or 40<=u<56 and v>29:c=shade((207,184,145),.77+.25*grain)
   if abs(u-round(u/4)*4)<.18:c=shade(c,.68)
   off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/models/armor/leon_jacket_layer_1.png',W,H,pix)
# Three distinct pixel-art inventory icons.
for name in ['leon_jacket','leon_pistol','hope']:
 W=64;H=64;pix=bytearray(W*H*4)
 for y in range(H):
  for x in range(W):
   c=None
   if name=='leon_jacket':
    if (19<=x<=44 and 13<=y<=53) or (8<=x<19 and 15<=y<=43) or (44<x<=55 and 15<=y<=43):
     c=shade((108,68,45),.72+.26*math.sin(x*.4)**2)
     if y<24 and abs(x-32)<(25-y)*.72+2:c=(213,192,151)
     if 31<=x<=32 and y>23:c=(160,139,103)
     if y>49 or y>39 and (x<19 or x>44):c=(199,179,145)
   elif name=='leon_pistol':
    if 7<=x<=56 and 17<=y<=28:c=shade((65,69,78),.80+.25*math.sin(y*.8)**2)
    if 30<=x<=54 and 28<=y<=33:c=(40,42,49)
    if 40<=x<=51 and 32<=y<=52:c=(45,38,36)
    if 25<=x<=40 and 32<=y<=40 and (x in (25,26,39,40) or y>=38):c=(65,69,78)
   else:
    u=(x-31.5)/19;v=(y-31.5)/24
    if abs(u)+abs(v)<1:
     c=mix((125,140,184),(255,248,210),max(0,1-abs(u)-abs(v)))
    if abs(u)<.10 and abs(v)<1.1 or abs(v)<.08 and abs(u)<1.1:c=(255,246,203)
   if c is not None:
    off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
 png(assets/'textures/item'/f'{name}.png',W,H,pix)
 write_noctis_json_resource(assets/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':f'noctismagic:item/{name}'}})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['item.noctismagic.leon_jacket']='Giubbotto di Leon' if it else "Leon's Jacket"
 d['item.noctismagic.leon_pistol']='Pistola di Leon' if it else "Leon's Pistol"
 d['item.noctismagic.hope']='Speranza' if it else 'Hope'
 d['item.noctismagic.hope.desc']='Non ha alcun potere.' if it else 'It has no power.'
 d['item.noctismagic.leon_pistol.desc']='Tasto destro per sparare. Consuma una pepita di ferro.' if it else 'Right-click to fire. Uses one iron nugget.'
 d['message.noctismagic.leon_ammo']='Servono pepite di ferro.' if it else 'Iron nuggets required.'
 write_noctis_json_resource(p,d)
print('Character loot, colored court suits, Leon jacket and pistol, medicinal herbs, gifts, and Hope.')


# Art furniture drops, horse meat and varied dragon treasures.
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<Item> HORSE_MEAT=ITEMS.register("horse_meat",()->new Item(new Item.Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(3).saturationMod(.3f).meat().build())));
    public static final RegistryObject<Item> COOKED_HORSE_MEAT=ITEMS.register("cooked_horse_meat",()->new Item(new Item.Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(8).saturationMod(.8f).meat().build())));
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(HORSE_MEAT.get());e.accept(COOKED_HORSE_MEAT.get());')
edit('CharacterLoot.java','  }else if(m instanceof Vincent)add(e,Noctis.HOPE.get(),1);','''  }else if(m instanceof Vincent)add(e,Noctis.HOPE.get(),1);
  else if(m instanceof ArtGuest a)add(e,a.maelle()?Furniture.EASEL_ITEM.get():Furniture.PIANO_ITEM.get(),1);
  else if(m instanceof FriendshipPony pony){
   add(e,Items.LEATHER,2+m.getRandom().nextInt(3)+Math.max(0,e.getLootingLevel()));
   add(e,pony.isOnFire()?Noctis.COOKED_HORSE_MEAT.get():Noctis.HORSE_MEAT.get(),2+m.getRandom().nextInt(4)+Math.max(0,e.getLootingLevel()));
  }else if(m instanceof SynchroDragon){
   Item[] treasure={Items.GOLD_INGOT,Items.IRON_INGOT,Items.DIAMOND,Items.EMERALD,Items.AMETHYST_SHARD,Items.ENDER_PEARL,Items.BLAZE_ROD,Items.OBSIDIAN,Items.EXPERIENCE_BOTTLE,Items.PHANTOM_MEMBRANE,Items.GOLDEN_APPLE,Items.REDSTONE,Items.QUARTZ,Items.BONE};
   int rolls=2+m.getRandom().nextInt(4)+Math.max(0,e.getLootingLevel());
   for(int i=0;i<rolls;i++){
    Item item=treasure[m.getRandom().nextInt(treasure.length)];
    int count=item==Items.DIAMOND||item==Items.GOLDEN_APPLE?1:1+m.getRandom().nextInt(4);
    add(e,item,count);
   }
   if(m.getRandom().nextInt(30)==0)add(e,Items.NETHERITE_SCRAP,1);
  }''')
# Food can be cooked in a furnace, smoker or campfire.
for name,kind,time in [('smelt_horse_meat','smelting',200),('smoke_horse_meat','smoking',100),('campfire_horse_meat','campfire_cooking',600)]:
 write_noctis_json_resource(res/'data/noctismagic/recipes'/f'{name}.json',{'type':'minecraft:'+kind,'category':'food','ingredient':{'item':'noctismagic:horse_meat'},'result':'noctismagic:cooked_horse_meat','experience':.35,'cookingtime':time})
for cooked,name in [(False,'horse_meat'),(True,'cooked_horse_meat')]:
 W,H=64,64;pix=bytearray(W*H*4)
 for y in range(H):
  for x in range(W):
   u=(x-31.5)/24;v=(y-32)/17
   t=(u+.12*v)**2+v*v+.09*math.sin(u*9+v*4)
   if t>1:continue
   c=mix((82,40,25) if cooked else (136,39,56),(157,89,45) if cooked else (218,100,116),.42+.32*math.cos(v*2.4))
   if abs(math.sin(u*11+v*3.2))<.12 and t<.84:c=shade(c,.72 if cooked else 1.12)
   if .83<t<1:c=mix(c,(171,122,79) if cooked else (238,185,162),.66)
   c=shade(c,.94+.07*math.sin(x*1.7+y*2.3))
   off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
 png(assets/'textures/item'/f'{name}.png',W,H,pix)
 write_noctis_json_resource(assets/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':f'noctismagic:item/{name}'}})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['item.noctismagic.horse_meat']='Carne di cavallo cruda' if it else 'Raw Horse Meat'
 d['item.noctismagic.cooked_horse_meat']='Carne di cavallo cotta' if it else 'Cooked Horse Meat'
 write_noctis_json_resource(p,d)
print('Maelle easel, Verso piano, pony leather and edible horse meat, randomized Synchro dragon treasure.')


# Separate vampire loot: garlic and bottled blood.
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<Item> GARLIC=ITEMS.register("garlic",()->new Item(new Item.Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(1).saturationMod(.2f).build())));
    public static final RegistryObject<Item> BLOOD_VIAL=ITEMS.register("blood_vial",()->new Item(new Item.Properties().stacksTo(16)));
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(GARLIC.get());e.accept(BLOOD_VIAL.get());')
edit('CharacterLoot.java','  if(m instanceof CrossoverGuest g){','''  if(m instanceof Vampire.Friendly){add(e,Noctis.BLOOD_VIAL.get(),1);}
  else if(m.getClass().getSimpleName().equals("Vampire")||new net.minecraft.resources.ResourceLocation(Noctis.ID,"vampire").equals(net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(m.getType()))){add(e,Noctis.GARLIC.get(),1+m.getRandom().nextInt(3)+Math.max(0,e.getLootingLevel()));}
  else if(m instanceof CrossoverGuest g){''')
for name in ['garlic','blood_vial']:
 W,H=64,64;pix=bytearray(W*H*4)
 for y in range(H):
  for x in range(W):
   c=None
   if name=='garlic':
    for ex,ey,rx,ry in [(21,39,12,17),(32,39,13,19),(43,39,12,17)]:
     u=(x-ex)/rx;v=(y-ey)/ry
     if u*u+v*v<1:c=shade((231,215,186),.78+.22*math.cos(u*1.4)**2)
    if 28<=x<=35 and 9<=y<=25:c=shade((168,145,100),.85+.15*math.sin(x)**2)
    if 22<=y<=50 and x in (24,39) and c is not None:c=shade(c,.86)
   else:
    if 24<=x<=40 and 8<=y<=16:c=(145,104,64)
    if (25<=x<=39 and 17<=y<=23) or (18<=x<=46 and 25<=y<=54):
     c=(164,191,202) if x in (18,19,45,46) or y==54 else (63,22,36) if y>=32 else (87,112,128)
     if 21<=x<=25 and y>=26:c=mix(c,(212,224,223),.38)
     if 26<=x<=42 and 34<=y<=50:c=shade((155,18,42),.80+.20*math.sin(x*.13)**2)
   if c is not None:
    off=(y*W+x)*4;pix[off:off+4]=bytes((*c,255))
 png(assets/'textures/item'/f'{name}.png',W,H,pix)
 write_noctis_json_resource(assets/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':f'noctismagic:item/{name}'}})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['item.noctismagic.garlic']='Aglio' if it else 'Garlic'
 d['item.noctismagic.blood_vial']='Ampolla di sangue' if it else 'Blood Vial'
 write_noctis_json_resource(p,d)
print('Hostile vampire garlic drops and friendly vampire blood vials.')


# Nether demons: varied Nether mineral loot, including the mod's own amethyst ore.
edit('CharacterLoot.java','  if(m instanceof Vampire.Friendly){','''  if(m instanceof Demon){
   Item[] common={Items.QUARTZ,Items.GOLD_NUGGET,Items.NETHER_GOLD_ORE,Items.NETHER_QUARTZ_ORE};
   int first=m.getRandom().nextInt(common.length);
   int second=(first+1+m.getRandom().nextInt(common.length-1))%common.length;
   add(e,common[first],2+m.getRandom().nextInt(4)+Math.max(0,e.getLootingLevel()));
   add(e,common[second],1+m.getRandom().nextInt(3)+Math.max(0,e.getLootingLevel()));
   add(e,Items.AMETHYST_SHARD,2+m.getRandom().nextInt(4)+Math.max(0,e.getLootingLevel()));
   if(m.getRandom().nextInt(2)==0)add(e,VampireLife.ORE_ITEM.get(),1+m.getRandom().nextInt(3));
   if(m.getRandom().nextInt(3)==0)add(e,Items.NETHERITE_SCRAP,1+m.getRandom().nextInt(2));
  }
  else if(m instanceof Vampire.Friendly){''')
print('Both Nether demon variants now drop a mixed selection of Nether minerals.')


# Exodia's joke victory: one-time disconnect on a successful invocation, not a ban.
edit('ExodiaRitual.java','l.sendParticles(ParticleTypes.TOTEM_OF_UNDYING,boss.getX(),boss.getY()+4,boss.getZ(),180,2.7,4,2.7,.18);','''l.sendParticles(ParticleTypes.TOTEM_OF_UNDYING,boss.getX(),boss.getY()+4,boss.getZ(),180,2.7,4,2.7,.18);
  RitualQuests.award(p,"exodia");RitualQuests.complete(p,"exodia");
  p.connection.disconnect(Component.literal("Hai vinto il duello.").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));''')
print('Exodia successful invocation awards victory and disconnects summoner once, without banning or deleting the world.')


# The same one-time duel victory when using Exodia's creative spawn egg.
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<Item> EXODIA_EGG=ITEMS.register("exodia_spawn_egg",ExodiaEgg::new);
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(EXODIA_EGG.get());')
write('ExodiaEgg.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.ForgeSpawnEggItem;
public class ExodiaEgg extends ForgeSpawnEggItem{
 public ExodiaEgg(){super(Noctis.EXODIA,0x9c642a,0xf4d16b,new Item.Properties());}
 static Set<UUID> before(Player p){Set<UUID> ids=new HashSet<>();for(Exodia x:p.level().getEntitiesOfClass(Exodia.class,p.getBoundingBox().inflate(32)))ids.add(x.getUUID());return ids;}
 static void victory(ServerPlayer p,Set<UUID> ids){
  Exodia boss=p.serverLevel().getEntitiesOfClass(Exodia.class,p.getBoundingBox().inflate(32),x->!ids.contains(x.getUUID())).stream().min(Comparator.comparingDouble(p::distanceToSqr)).orElse(null);
  if(boss==null)return;
  boss.bind(p);boss.setPersistenceRequired();
  RitualQuests.award(p,"exodia");RitualQuests.complete(p,"exodia");
  p.connection.disconnect(Component.literal("Hai vinto il duello.").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));
 }
 @Override public InteractionResult useOn(UseOnContext ctx){
  if(!(ctx.getPlayer() instanceof ServerPlayer p))return super.useOn(ctx);
  Set<UUID> ids=before(p);InteractionResult result=super.useOn(ctx);
  if(result.consumesAction())victory(p,ids);return result;
 }
 @Override public InteractionResultHolder<ItemStack> use(Level l,Player p,InteractionHand h){
  if(!(p instanceof ServerPlayer sp))return super.use(l,p,h);
  Set<UUID> ids=before(p);InteractionResultHolder<ItemStack> result=super.use(l,p,h);
  if(result.getResult().consumesAction())victory(sp,ids);return result;
 }
}''')
write_noctis_json_resource(assets/'models/item/exodia_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['item.noctismagic.exodia_spawn_egg']='Uovo generatore: Exodia' if it else 'Exodia Spawn Egg';write_noctis_json_resource(p,d)
print('Exodia spawn egg triggers a one-time victory disconnect only when it spawns a new Exodia.')


# Metal Sonic uses his central thruster for genuine low-altitude hover.
edit('SonicGuest.java','int speech,hit;','int speech,hit,hoverTurn;float hoverYaw;')
edit('SonicGuest.java','super.tick();if(speech>0)speech--;if(hit>0)hit--;','''super.tick();if(speech>0)speech--;if(hit>0)hit--;
        if(!shadow()&&level() instanceof ServerLevel hoverLevel)hover(hoverLevel);''')
edit('SonicGuest.java','    @Override public boolean doHurtTarget(Entity e){','''    void hover(ServerLevel l){
        if(isInWater()||isInLava()){setNoGravity(false);return;}
        setNoGravity(true);resetFallDistance();
        var a=position().add(0,.15,0);
        var b=l.clip(new net.minecraft.world.level.ClipContext(a,a.add(0,-8,0),net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,this));
        double desired=neo()?1.15:.70;
        double dy=b.getType()==net.minecraft.world.phys.HitResult.Type.MISS?-.12:Math.max(-.18,Math.min(.20,(desired-(getY()-b.getLocation().y))*.28));
        var v=getDeltaMovement();
        LivingEntity target=getTarget();
        if(target!=null&&target.isAlive()&&distanceTo(target)<20&&hasLineOfSight(target)){
            var d=target.position().subtract(position());var horizontal=new net.minecraft.world.phys.Vec3(d.x,0,d.z);
            if(horizontal.length()>1.6){var q=horizontal.normalize().scale(neo()?.27:.21);v=new net.minecraft.world.phys.Vec3(q.x,dy,q.z);}
        }else{
            if(hoverTurn--<=0){hoverTurn=55+random.nextInt(120);hoverYaw=getYRot()+random.nextFloat()*140-70;}
            if(tickCount%240<120&&getNavigation().isDone()){
                double angle=Math.toRadians(hoverYaw);var q=new net.minecraft.world.phys.Vec3(-Math.sin(angle)*.065,dy,Math.cos(angle)*.065);
                if(l.noCollision(this,getBoundingBox().move(q.x*5,0,q.z*5)))v=q;
                else hoverTurn=0;
            }
        }
        if(!l.noCollision(this,getBoundingBox().move(0,dy,0)))dy=0;
        setDeltaMovement(v.x,dy,v.z);
        if(tickCount%3==0){
            double angle=Math.toRadians(yBodyRot),x=getX()-Math.sin(angle)*.23,z=getZ()+Math.cos(angle)*.23;
            l.sendParticles(ParticleTypes.ELECTRIC_SPARK,x,getY()+1.0,z,3,.05,.06,.05,.035);
            l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+.12,getZ(),1,.10,.06,.10,.015);
        }
    }
    @Override public boolean causeFallDamage(float distance,float multiplier,net.minecraft.world.damagesource.DamageSource source){return shadow()&&super.causeFallDamage(distance,multiplier,source);}
    @Override public boolean doHurtTarget(Entity e){''')
edit('SonicGuestClient.java','arm.xRot=k==0?-1.25f-hit*.5f:-walk*.7f-hit*1.4f;leg.xRot=k==0?-.80f:walk*.7f;leg.zRot=k==0?(i==0?-.38f:.38f):0;','''arm.xRot=k==0?-1.25f-hit*.5f:-.15f-amount*.25f-hit*1.4f;leg.xRot=k==0?-.80f:.15f+amount*.22f;leg.zRot=k==0?(i==0?-.38f:.38f):(i==0?-.10f:.10f);''')
edit('SonicGuestClient.java','if(k==0){for(int i=0;i<2;i++)r.getChild("bike").getChild("wheel"+i).xRot=limb*1.3f;b.xRot=.18f;}','''if(k==0){for(int i=0;i<2;i++)r.getChild("bike").getChild("wheel"+i).xRot=limb*1.3f;b.xRot=.18f;}
            else{b.y=5+(float)Math.sin(age*.13f)*.5f;b.xRot=.06f+amount*.15f;b.zRot=(float)Math.sin(age*.09f)*.035f;}''')
# Improve the original central turbine's front UV (first body box 22 UV pixels wide, next starts at 23).
for name in ['metal_sonic','neo_metal_sonic']:
 p=assets/'textures/entity'/f'{name}.png'
 raw=p.read_bytes();chunks=[];off=8;compressed=b''
 while off<len(raw):
  n=int.from_bytes(raw[off:off+4],'big');tag=raw[off+4:off+8];data=raw[off+8:off+8+n];off+=n+12
  if tag==b'IHDR':W,H=struct.unpack('>II',data[:8])
  if tag==b'IDAT':compressed+=data
 scan=zlib.decompress(compressed);stride=W*4+1
 assert all(scan[y*stride]==0 for y in range(H))
 pix=bytearray(b''.join(scan[y*stride+1:(y+1)*stride] for y in range(H)))
 # chest core front UV x=24..27, y=1..4 of the 256 atlas
 for y in range(4,20):
  for x in range(96,112):
   u=(x-103.5)/7.5;v=(y-11.5)/7.5;d=math.sqrt(u*u+v*v);ang=math.atan2(v,u)
   if d>.97:c=(33,42,80)
   elif d>.71:c=shade((231,184,45),.83+.16*math.cos(ang*3))
   elif d>.53:c=(66,74,91)
   elif d>.24:c=mix((20,43,67),(83,199,255),.27+.30*math.sin(ang*6+d*12)**2)
   else:c=(191,241,255)
   q=(y*W+x)*4;pix[q:q+4]=bytes((*c,255))
 png(p,W,H,pix)
print('Metal Sonic and Neo Metal Sonic hover with no gravity, a central detailed turbine, thrust particles and airborne poses.')


# Gennaro: blue cap and blue shirt with red lettering; golden rosary and crucifix.
edit('ScrapThiefClient.java','        return LayerDefinition.create(m,128,64);','''        PartDefinition body=r.getChild("body");
        for(int side:new int[]{-1,1}){
            for(int i=0;i<8;i++){
                float t=i/7f;
                body.addOrReplaceChild("rosary"+side+"_"+i,CubeListBuilder.create().texOffs(108,32).addBox(-.23f,-.23f,-.23f,.46f,.46f,.46f),PartPose.offsetAndRotation(side*(2.95f-2.65f*t),.3f+t*4.8f,-2.13f-.12f*t,0,0,side*.17f));
            }
        }
        body.addOrReplaceChild("crucifix",CubeListBuilder.create().texOffs(108,38).addBox(-.19f,0,-.20f,.38f,2.6f,.4f).texOffs(112,38).addBox(-.95f,.76f,-.22f,1.9f,.39f,.44f),PartPose.offset(0,5.05f,-2.25f));
        return LayerDefinition.create(m,128,64);''')
p=assets/'textures/entity/scrap_thief.png'
raw=p.read_bytes();off=8;compressed=b''
while off<len(raw):
 n=int.from_bytes(raw[off:off+4],'big');tag=raw[off+4:off+8];data=raw[off+8:off+8+n];off+=n+12
 if tag==b'IHDR':ow,oh=struct.unpack('>II',data[:8])
 if tag==b'IDAT':compressed+=data
scan=zlib.decompress(compressed);stride=ow*4+1
assert all(scan[y*stride]==0 for y in range(oh))
old=b''.join(scan[y*stride+1:(y+1)*stride] for y in range(oh))
W,H=ow*4,oh*4;pix=bytearray(W*H*4)
for y in range(H):
 for x in range(W):
  u,v=x//4,y//4;q=(v*ow+u)*4;c=tuple(old[q:q+3]);alpha=old[q+3]
  if (16<=u<40 and 16<=v<32) or (40<=u<56 and 16<=v<32 and not (44<=u<48 and v>=24)) or (64<=u<104 and v<14) or (64<=u<92 and 16<=v<23):
   grain=.92+.08*math.sin(x*1.7+y*2.1)**2
   c=shade((24,62,159),grain*(.90+.13*math.sin(u*.8)**2));alpha=255
  if 108<=u<124 and 32<=v<46:
   c=shade((226,172,46),.80+.22*math.sin(x*.66+y*.19)**2);alpha=255
  q=(y*W+x)*4;pix[q:q+4]=bytes((*c,alpha))
letters={'L':['100','100','100','100','111'],'E':['111','100','110','100','111'],'T':['111','010','010','010','010']}
def word(x,y,scale):
 for i,ch in enumerate('LETE'):
  for dy,row in enumerate(letters[ch]):
   for dx,b in enumerate(row):
    if b=='1':
     for a in range(scale):
      for z in range(scale):
       xx=x+(i*4+dx)*scale+z;yy=y+dy*scale+a;q=(yy*W+xx)*4
       pix[q:q+4]=bytes((235,35,47,255))
word(81,93,2)
word(296,38,2)
png(p,W,H,pix)
print('Gennaro blue cap and shirt, red LETE lettering, golden 3D rosary and crucifix.')


# Exclusive time manipulation spell for shesoldtheworld, authenticated on the server.
edit('Noctis.java','GEASS("Geass - Controllo mentale",5,45);','GEASS("Geass - Controllo mentale",5,45),TIME_ACCELERATION("Accelerazione temporale",1,0);')
edit('Noctis.java','case GEASS -> {if(!GeassMagic.cast(p))return;}','case TIME_ACCELERATION -> {if(!TimeAcceleration.cast(p))return;}\n            case GEASS -> {if(!GeassMagic.cast(p))return;}')
write('TimeAcceleration.java','''package it.noctis.magic;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.level.Level;
import net.minecraft.world.Difficulty;
public final class TimeAcceleration{
 public static boolean allowed(ServerPlayer p){return "shesoldtheworld".equalsIgnoreCase(p.getGameProfile().getName());}
 public static boolean cast(ServerPlayer p){
  if(!allowed(p)){p.displayClientMessage(Component.translatable("message.noctismagic.time_forbidden"),true);return false;}
  ServerLevel l=p.serverLevel();
  if(l.dimension()!=Level.OVERWORLD||!p.isAlive()||p.isSpectator()){p.displayClientMessage(Component.translatable("message.noctismagic.time_overworld"),true);return false;}
  if(l.getDifficulty()==Difficulty.PEACEFUL){p.displayClientMessage(Component.translatable("message.noctismagic.time_peaceful"),true);return false;}
  if(Eclipse.active(l)){p.displayClientMessage(Component.translatable("message.noctismagic.time_eclipse"),true);return false;}
  long now=l.getDayTime(),day=Math.floorDiv(now,24000L),next=Math.max(1,day+1),eclipse=(Math.floorDiv(Math.max(0,day),7)+1)*7;
  // Advance to the next dawn; never skip the approaching eclipse.
  long target=Math.min(next,eclipse)*24000L;
  if(target<=now)return false;
  l.setDayTime(target);
  p.playSound(SoundEvents.BEACON_POWER_SELECT,1,.55f);
  l.sendParticles(ParticleTypes.PORTAL,p.getX(),p.getY()+1,p.getZ(),65,.6,.9,.6,.2);
  long remaining=Math.max(0,eclipse-Math.floorDiv(target,24000L));
  p.displayClientMessage(Component.translatable(remaining==0?"message.noctismagic.time_arrived":"message.noctismagic.time_days",remaining).withStyle(ChatFormatting.LIGHT_PURPLE),false);
  return true;
 }
}''')
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['message.noctismagic.time_forbidden']='Solo shesoldtheworld puo dominare il tempo.' if it else 'Only shesoldtheworld can command time.'
 d['message.noctismagic.time_overworld']='Il tempo puo essere alterato solo nel mondo normale.' if it else 'Time can only be altered in the Overworld.'
 d['message.noctismagic.time_peaceful']='Le eclissi non avvengono in modalita Pacifica.' if it else 'Eclipses do not occur in Peaceful mode.'
 d['message.noctismagic.time_eclipse']='L’eclissi e gia in corso. Il tempo si rifiuta di avanzare.' if it else 'The eclipse is already underway. Time refuses to advance.'
 d['message.noctismagic.time_days']='Il tempo avanza. Giorni mancanti all’eclissi: %s.' if it else 'Time advances. Days until the eclipse: %s.'
 d['message.noctismagic.time_arrived']='Il tempo ha ceduto. L’eclissi e arrivata.' if it else 'Time has yielded. The eclipse has arrived.'
 write_noctis_json_resource(p,d)
print('Exclusive server-validated time acceleration spell, advancing one dawn without skipping the eclipse.')


# Nonsexual pain vocalizations for the adult NPCs, and an absurd secret dinosaur miniboss.
write('NpcPain.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class NpcPain{
 @SubscribeEvent(priority=EventPriority.HIGHEST) public static void hurt(LivingAttackEvent e){
  var m=e.getEntity();
  if(!(m.level() instanceof ServerLevel l)||e.getAmount()<=0||m.getType()!=Noctis.WAIFU.get()&&!(m instanceof CabaretHealer)&&!(m instanceof DramaGuest g&&g.kind()==2))return;
  var tag=m.getPersistentData();if(tag.getLong("NoctisPainUntil")>l.getGameTime())return;
  tag.putLong("NoctisPainUntil",l.getGameTime()+12);
  l.playSound(null,m.blockPosition(),SoundEvents.PLAYER_HURT,SoundSource.NEUTRAL,.85f,1.35f+m.getRandom().nextFloat()*.25f);
 }
}''')
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<Item> OLD_BOOK=ITEMS.register("old_book",()->new Item(new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.RARE)));
    public static final RegistryObject<EntityType<MustacheRex>> MUSTACHE_REX=ENTITIES.register("mustache_rex",()->EntityType.Builder.<MustacheRex>of(MustacheRex::new,MobCategory.MONSTER).sized(3.2f,4.8f).clientTrackingRange(12).build(ID+":mustache_rex"));
    public static final RegistryObject<Item> MUSTACHE_REX_EGG=ITEMS.register("mustache_rex_spawn_egg",()->new ForgeSpawnEggItem(MUSTACHE_REX,0x635139,0x30241c,new Item.Properties()));
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());','e.put(MUSTACHE_REX.get(),MustacheRex.attributes().build());e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(OLD_BOOK.get());e.accept(MUSTACHE_REX_EGG.get());')
edit('BakeryClerk.java','ItemStack s=p.getItemInHand(h);if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET))return InteractionResult.PASS;','''ItemStack s=p.getItemInHand(h);
        if(!stalin()&&s.is(Noctis.OLD_BOOK.get())){
            if(level() instanceof ServerLevel l&&p instanceof net.minecraft.server.level.ServerPlayer sp)RexRitual.begin(this,sp,s);
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if(!s.isEmpty()&&!s.is(Items.GOLD_NUGGET))return InteractionResult.PASS;''')
edit('BakeryClerk.java','public float bakerGesture(){','''public int rexTransform=0;
    public float rexGrowth(){return rexTransform<=0?0:1-rexTransform/80f;}
    public float bakerGesture(){''')
edit('BakeryClerk.java','super.tick();if(bakerGesture>0)','super.tick();if(rexTransform>0)rexTransform--;if(level() instanceof ServerLevel l&&RexRitual.tick(this,l))return;if(bakerGesture>0)')
edit('BakeryClerk.java','public void handleEntityEvent(byte id){','public void handleEntityEvent(byte id){if(id==112){rexTransform=80;return;}if(id==113){rexTransform=0;return;}')
edit('BakeryClient.java','@Override public ResourceLocation getTextureLocation(BakeryClerk e)','''@Override protected void scale(BakeryClerk e,com.mojang.blaze3d.vertex.PoseStack p,float partial){
            float g=e.rexGrowth();if(g>0){float sh=(float)Math.sin(g*65)*.055f;p.scale(1+g*.85f+sh,1+g*1.25f,1+g*.85f-sh);p.mulPose(com.mojang.math.Axis.ZP.rotation((float)Math.sin(g*51)*.09f));}
        }
        @Override public ResourceLocation getTextureLocation(BakeryClerk e)''')
write('RexRitual.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.*;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.minecraftforge.event.LootTableLoadEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class RexRitual{
 @SubscribeEvent public static void loot(LootTableLoadEvent e){
  if(!e.getName().getPath().startsWith("chests/"))return;
  e.getTable().addPool(LootPool.lootPool().name("noctis_old_book").setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(.035f)).add(LootItem.lootTableItem(Noctis.OLD_BOOK.get())).build());
 }
 static void begin(BakeryClerk m,ServerPlayer p,ItemStack book){
  if(m.getPersistentData().getInt("RexTicks")>0)return;
  ServerLevel l=p.serverLevel();BlockPos dest=null;
  MustacheRex probe=Noctis.MUSTACHE_REX.get().create(l);if(probe==null)return;
  for(int i=0;i<64;i++){
   BlockPos q=Eclipse.spot(p,5,20);if(q==null)continue;
   probe.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);
   if(l.noCollision(probe)&&!l.containsAnyLiquid(probe.getBoundingBox())){dest=q;break;}
  }
  probe.discard();
  if(dest==null){p.displayClientMessage(Component.literal("Serve un'area aperta per la trasformazione."),true);return;}
  if(!p.getAbilities().instabuild)book.shrink(1);
  var tag=m.getPersistentData();tag.putInt("RexTicks",80);tag.putLong("RexDestination",dest.asLong());tag.putUUID("RexSummoner",p.getUUID());
  m.rexTransform=80;m.getNavigation().stop();l.broadcastEntityEvent(m,(byte)112);
  m.say(l,"Quel libro? ...Oh no. NON DI NUOVO!");m.playSound(SoundEvents.WARDEN_ROAR,1,.9f);
 }
 static boolean tick(BakeryClerk m,ServerLevel l){
  var tag=m.getPersistentData();int t=tag.getInt("RexTicks");if(t<=0)return false;
  m.getNavigation().stop();tag.putInt("RexTicks",--t);
  if(t%5==0){l.sendParticles(ParticleTypes.POOF,m.getX(),m.getY()+1.1,m.getZ(),12,.5,.8,.5,.05);l.sendParticles(ParticleTypes.SMOKE,m.getX(),m.getY()+.8,m.getZ(),18,.6,.7,.6,.03);}
  if(t==40)m.playSound(SoundEvents.RAVAGER_ROAR,1,.65f);
  if(t==0){
   BlockPos q=BlockPos.of(tag.getLong("RexDestination"));MustacheRex rex=Noctis.MUSTACHE_REX.get().create(l);
   if(rex!=null&&l.hasChunkAt(q)){
    rex.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,m.getYRot(),0);
    if(l.noCollision(rex)&&!l.containsAnyLiquid(rex.getBoundingBox())&&l.addFreshEntity(rex)){
     rex.setPersistenceRequired();rex.playSound(SoundEvents.RAVAGER_ROAR,2,.55f);
     if(tag.hasUUID("RexSummoner")&&l.getPlayerByUUID(tag.getUUID("RexSummoner")) instanceof ServerPlayer p&&!p.isCreative())rex.setTarget(p);
     l.sendParticles(ParticleTypes.POOF,rex.getX(),rex.getY()+2,rex.getZ(),85,1.5,1.7,1.5,.1);
     m.discard();return true;
    }
   }
   m.spawnAtLocation(Noctis.OLD_BOOK.get());m.rexTransform=0;l.broadcastEntityEvent(m,(byte)113);
  }
  return true;
 }
}''')
write('MustacheRex.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
public class MustacheRex extends Monster{
 final ServerBossEvent bar=new ServerBossEvent(Component.literal("Baffosauro Rex"),BossEvent.BossBarColor.YELLOW,BossEvent.BossBarOverlay.NOTCHED_10);
 int cooldown=80,windup,pose;
 public MustacheRex(EntityType<? extends Monster> t,Level l){super(t,l);setMaxUpStep(1.5f);}
 public static AttributeSupplier.Builder attributes(){return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,350).add(Attributes.ATTACK_DAMAGE,25).add(Attributes.ARMOR,12).add(Attributes.MOVEMENT_SPEED,.27).add(Attributes.FOLLOW_RANGE,40).add(Attributes.KNOCKBACK_RESISTANCE,.85);}
 @Override protected void registerGoals(){
  goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.15,true));
  goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,.75));goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,12));
  targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));
 }
 @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);bar.addPlayer(p);}
 @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);bar.removePlayer(p);}
 @Override public void remove(RemovalReason reason){bar.removeAllPlayers();super.remove(reason);}
 @Override public boolean removeWhenFarAway(double d){return false;}
 @Override public void tick(){
  super.tick();if(pose>0)pose--;if(cooldown>0)cooldown--;
  if(!(level() instanceof ServerLevel l))return;bar.setProgress(getHealth()/getMaxHealth());
  if(windup>0){getNavigation().stop();if(--windup==0){
   for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(5),p->!p.isCreative()&&!p.isSpectator()&&hasLineOfSight(p))){
    p.hurt(damageSources().mobAttack(this),20);p.knockback(1.5,getX()-p.getX(),getZ()-p.getZ());p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,65,1));}
   l.sendParticles(ParticleTypes.POOF,getX(),getY()+.25,getZ(),60,2,.1,2,.06);playSound(SoundEvents.RAVAGER_ROAR,1.8f,.6f);
  }return;}
  if(cooldown==0&&getTarget()!=null&&distanceTo(getTarget())<8){cooldown=110;windup=24;l.broadcastEntityEvent(this,(byte)114);playSound(SoundEvents.RAVAGER_ATTACK,1.2f,.6f);}
 }
 @Override public boolean doHurtTarget(Entity e){boolean hit=super.doHurtTarget(e);if(hit&&level() instanceof ServerLevel l)l.broadcastEntityEvent(this,(byte)115);return hit;}
 @Override public void handleEntityEvent(byte id){if(id==114||id==115){pose=id==114?30:15;return;}super.handleEntityEvent(id);}
 public float motion(){return pose<=0?0:(float)Math.sin(Math.PI*pose/32f);}
 @Override protected void dropCustomDeathLoot(net.minecraft.world.damagesource.DamageSource s,int looting,boolean hit){super.dropCustomDeathLoot(s,looting,hit);spawnAtLocation(Items.BONE,10);spawnAtLocation(Items.BREAD,8);spawnAtLocation(Items.EMERALD,4);}
}''')
write('MustacheRexClient.java','''package it.noctis.magic;
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
public class MustacheRexClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MUSTACHE_REX.get(),R::new);}
 static class M extends EntityModel<MustacheRex>{
  final Part root=new Part(0,0,0),body=root.child(0,1,0),neck=body.child(0,-2,-4),head=neck.child(0,-5,-2),jaw=head.child(0,1,-2);
  final Part[] legs=new Part[2],feet=new Part[2],arms=new Part[2],tail=new Part[7],mustache=new Part[2];
  M(){
   Part torso=body.child(0,0,0);torso.rx=1.25f;
   torso.loft(0,24,-7,0,0,1.2f,1.2f,-4,0,0,4.0f,4.0f,1,0,0,4.9f,4.4f,6,0,0,3.7f,3.3f,9,0,0,1.3f,1.4f);
   neck.loft(0,20,-6,0,0,2.4f,2.6f,-3,0,0,2.8f,2.7f,1,0,0,3.2f,3.4f);
   head.loft(0,24,-4,0,-1.4f,3.3f,3.2f,-2,0,-2,4.3f,5.5f,0,0,-2.8f,4,5.8f,1,0,-2.6f,3.3f,5);
   jaw.loft(1,20,0,0,-1.0f,3.2f,4.7f,1.5f,0,-1.3f,3.0f,4.5f,2.2f,0,-1.1f,2.0f,3.8f);
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    head.oval(3,s*3.3f,-1.8f,-3.4f,.55f,.75f,1.0f);
    head.blade(0,s*2,-3.0f,-3.7f,s*4,-2.0f,-4.5f,1.5f);
    mustache[i]=head.child(s*.55f,-.2f,-8.1f);
    mustache[i].loft(2,16,-.9f,s*.55f,0,.75f,.45f,-.45f,s*1.2f,0,1.4f,.65f,.1f,s*2.3f,.1f,1.7f,.6f,.65f,s*2.7f,.25f,1.1f,.4f,1.0f,s*3.4f,.3f,.25f,.12f);
    mustache[i].blade(2,s*2.4f,.2f,0,s*4.8f,-.9f,.35f,1.35f);
    for(int j=0;j<6;j++){float z=-6.0f+j*1.2f;head.blade(4,s*(2.7f+j*.08f),.75f,z,s*(2.6f+j*.08f),2.0f,z,.65f);}
    Part leg=legs[i]=body.child(s*3.3f,3,1);
    leg.loft(0,20,-1,0,0,2.1f,2.1f,3,0,.4f,2.6f,2.5f,6,0,.8f,1.5f,1.4f,9,0,0,1.1f,1.0f);
    Part foot=feet[i]=leg.child(0,8.5f,0);foot.loft(0,16,0,0,0,1.2f,1.2f,5,0,-1,1.4f,2.8f,6,0,-1.2f,1.3f,2.5f);
    for(int j=0;j<3;j++)foot.blade(4,-1+j,5,-2.3f,-1+j,6.0f,-4,.65f);
    Part arm=arms[i]=body.child(s*2.8f,0,-3);arm.loft(0,14,0,0,0,.8f,.8f,2,0,-.6f,.6f,.6f,4,0,-1.3f,.45f,.5f);
    for(int j=0;j<2;j++)arm.blade(4,-.25f+j*.5f,4,-1.3f,-.3f+j*.6f,4.8f,-2.8f,.4f);
   }
   Part p=body;
   for(int i=0;i<7;i++){Part t=tail[i]=p.child(0,i==0?2:0,i==0?6:3.1f);Part mesh=t.child(0,0,0);mesh.rx=1.5708f;float r=2.6f-i*.33f;mesh.loft(0,16,0,0,0,r,r,3.3f,0,0,Math.max(.08f,r-.35f),Math.max(.08f,r-.35f));p=t;}
  }
  @Override public void setupAnim(MustacheRex e,float limb,float amount,float age,float yaw,float pitch){
   float h=e.motion();body.y=1+(float)Math.sin(limb)*amount*.5f;body.rx=-h*.16f;neck.rx=-h*.25f;head.ry=yaw*.012f;head.rx=pitch*.01f-h*.25f;jaw.rx=.08f+h*.75f;
   for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.65+i*Math.PI)*amount;legs[i].rx=w*.55f;feet[i].rx=-w*.30f;arms[i].rx=-.6f+w*.12f;mustache[i].rz=(float)Math.sin(age*.19+i)*.06f;}
   for(int i=0;i<7;i++)tail[i].ry=(float)Math.sin(age*.14-i*.65)*(.10f+amount*.16f);
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer b,int l,int o,float r,float g,float bl,float a){root.draw(p,b,l,o,r,g,bl,a);}
 }
 static class R extends MobRenderer<MustacheRex,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),1.25f);}
  @Override protected void scale(MustacheRex e,PoseStack p,float partial){p.scale(2.9f,2.9f,2.9f);}
  @Override public ResourceLocation getTextureLocation(MustacheRex e){return new ResourceLocation(Noctis.ID,"textures/entity/mustache_rex.png");}
 }
}''')
W,H=1024,512;pix=bytearray(W*H*4)
for m,base in enumerate([(102,113,70),(154,143,97),(47,28,18),(230,170,43),(231,222,184)]):
 for y in range(128):
  for x in range(128):
   u=x/127;v=y/127;g=.72+.25*math.sin(u*math.pi)**2+.09*math.sin(x*1.2+y*.8)**2
   c=shade(base,g)
   if m==0:c=shade(c,.76+.24*abs(math.sin(u*32+math.sin(v*33)) * math.cos(v*34)))
   if m==2:c=shade(c,.7+.3*math.sin(u*74+v*3)**2)
   if m==3 and abs(u-.5)<.13:c=(16,12,8)
   off=(y*W+m*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/mustache_rex.png',W,H,pix)
write_noctis_json_resource(assets/'models/item/mustache_rex_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
write_noctis_json_resource(assets/'models/item/old_book.json',{'parent':'minecraft:item/generated','textures':{'layer0':'minecraft:item/book'}})
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['entity.noctismagic.mustache_rex']='Baffosauro Rex'
 d['item.noctismagic.mustache_rex_spawn_egg']='Uovo generatore: Baffosauro Rex' if it else 'Mustache Rex Spawn Egg'
 d['item.noctismagic.old_book']='Mein Kampf (libro maledetto)' if it else 'Mein Kampf (cursed book)'
 write_noctis_json_resource(p,d)
print('NPC pain sounds and absurd nonpolitical mustached dinosaur boss, secret loot book and animated transformation.')


# Jesus instantly defeats the secret dinosaur boss when invoked nearby.
edit('MiracleEncounter.java','if(s.equals("gesu aiutami")){','''if(s.equals("gesu aiutami")){
            if(DivineRexJudgment.smite(p))return;''')
write('DivineRexJudgment.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
public final class DivineRexJudgment{
 static boolean smite(ServerPlayer p){
  var l=p.serverLevel();
  var rex=l.getEntitiesOfClass(MustacheRex.class,p.getBoundingBox().inflate(80),x->x.isAlive()&&x.distanceToSqr(p)<=6400);
  if(rex.isEmpty())return false;
  for(MustacheRex boss:rex){
   var bolt=EntityType.LIGHTNING_BOLT.create(l);
   if(bolt!=null){bolt.moveTo(boss.getX(),boss.getY(),boss.getZ());bolt.setVisualOnly(true);l.addFreshEntity(bolt);}
   l.sendParticles(ParticleTypes.END_ROD,boss.getX(),boss.getY()+2,boss.getZ(),100,1.1,1.8,1.1,.12);
   boss.hurt(p.damageSources().genericKill(),Float.MAX_VALUE);
  }
  p.playSound(SoundEvents.NOTE_BLOCK_CHIME.value(),1,1);
  p.sendSystemMessage(Component.literal("Gesù: Non temete, figli miei. Finché sarò con voi, vi proteggerò dal male."));
  return true;
 }
}''')
print('Jesus invocation instantly defeats nearby Baffosauro Rex with a visual lightning miracle.')


# Two vulgar magical crops; seeds drop from ordinary and modded mobs.
edit('Noctis.java','public static final RegistryObject<Item> CATHEDRAL_EGG=','''public static final RegistryObject<net.minecraft.world.level.block.Block> VAFF_CROP=VampireLife.BLOCKS.register("vaffanculo_crop",()->new InsultCrop(false));
    public static final RegistryObject<net.minecraft.world.level.block.Block> SUCA_CROP=VampireLife.BLOCKS.register("suca_crop",()->new InsultCrop(true));
    public static final RegistryObject<Item> VAFF_SEEDS=ITEMS.register("vaffanculo_seeds",()->new net.minecraft.world.item.ItemNameBlockItem(VAFF_CROP.get(),new Item.Properties()));
    public static final RegistryObject<Item> SUCA_SEEDS=ITEMS.register("suca_seeds",()->new net.minecraft.world.item.ItemNameBlockItem(SUCA_CROP.get(),new Item.Properties()));
    public static final RegistryObject<Item> VAFF_FRUIT=ITEMS.register("vaffanculo_fruit",()->new InsultFruit(false));
    public static final RegistryObject<Item> SUCA_FRUIT=ITEMS.register("suca_fruit",()->new InsultFruit(true));
    public static final RegistryObject<Item> CATHEDRAL_EGG=''')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(VAFF_SEEDS.get());e.accept(SUCA_SEEDS.get());e.accept(VAFF_FRUIT.get());e.accept(SUCA_FRUIT.get());')
write('InsultCrop.java','''package it.noctis.magic;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.ItemLike;
public class InsultCrop extends CropBlock{
 final boolean suca;
 public InsultCrop(boolean s){super(BlockBehaviour.Properties.copy(Blocks.WHEAT));suca=s;}
 @Override protected ItemLike getBaseSeedId(){return suca?Noctis.SUCA_SEEDS.get():Noctis.VAFF_SEEDS.get();}
}''')
# Separate deferred sound registry (wired to existing mod bus).
edit('Noctis.java','VampireLife.register(bus);','VampireLife.register(bus);InsultFruit.SOUNDS.register(bus);')
write('InsultFruit.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.sounds.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.registries.*;
public class InsultFruit extends Item{
 static final DeferredRegister<SoundEvent> SOUNDS=DeferredRegister.create(ForgeRegistries.SOUND_EVENTS,Noctis.ID);
 static final RegistryObject<SoundEvent> VAFF=SOUNDS.register("fruit_vaffanculo",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"fruit_vaffanculo")));
 static final RegistryObject<SoundEvent> SUCA=SOUNDS.register("fruit_suca",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"fruit_suca")));
 final boolean suca;
 public InsultFruit(boolean s){super(new Item.Properties().stacksTo(32));suca=s;}
 @Override public InteractionResultHolder<ItemStack> use(Level level,Player p,InteractionHand hand){
  ItemStack item=p.getItemInHand(hand);
  if(!(level instanceof ServerLevel l))return InteractionResultHolder.sidedSuccess(item,level.isClientSide);
  Vec3 a=p.getEyePosition(),b=a.add(p.getLookAngle().scale(24));
  var block=l.clip(new ClipContext(a,b,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,p));
  if(block.getType()!=HitResult.Type.MISS)b=block.getLocation();
  Vec3 center=b;double nearest=a.distanceToSqr(b);
  for(LivingEntity m:l.getEntitiesOfClass(LivingEntity.class,new AABB(a,b).inflate(1),m->m!=p&&m.isAlive()&&!m.isSpectator())){
   var hit=m.getBoundingBox().inflate(.25).clip(a,b);
   if(hit.isPresent()&&a.distanceToSqr(hit.get())<nearest){nearest=a.distanceToSqr(hit.get());center=hit.get();}
  }
  double radius=suca?3.5:4.5;
  l.playSound(null,center.x,center.y,center.z,(suca?SUCA:VAFF).get(),SoundSource.PLAYERS,2f,1f);
  l.sendParticles(ParticleTypes.SONIC_BOOM,center.x,center.y,center.z,1,0,0,0,0);
  l.sendParticles(suca?ParticleTypes.HAPPY_VILLAGER:ParticleTypes.FLAME,center.x,center.y,center.z,45,radius*.45,.55,radius*.45,.03);
  for(LivingEntity m:l.getEntitiesOfClass(LivingEntity.class,new AABB(center,center).inflate(radius),m->m!=p&&m.isAlive()&&!m.isSpectator())){
   if(m.getBoundingBox().getCenter().distanceToSqr(center)>radius*radius)continue;
   Vec3 eye=m.getEyePosition();
   if(l.clip(new ClipContext(center,eye,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,p)).getType()!=HitResult.Type.MISS)continue;
   if(m.hurt(p.damageSources().playerAttack(p),suca?10:16))m.knockback(suca?1.2:1.8,center.x-m.getX(),center.z-m.getZ());
  }
  p.getCooldowns().addCooldown(this,30);
  if(!p.getAbilities().instabuild)item.shrink(1);
  return InteractionResultHolder.success(item);
 }
}''')
write('InsultSeedLoot.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class InsultSeedLoot{
 @SubscribeEvent public static void drops(LivingDropsEvent e){
  if(!(e.getEntity() instanceof Mob m)||!(m.level() instanceof ServerLevel l))return;
  float chance=Math.min(.95f,.65f+.08f*Math.max(0,e.getLootingLevel()));
  for(var seed:java.util.List.of(Noctis.VAFF_SEEDS,Noctis.SUCA_SEEDS)){
   if(m.getRandom().nextFloat()<chance)e.getDrops().add(new ItemEntity(l,m.getX(),m.getY()+.3,m.getZ(),new ItemStack(seed.get(),1+m.getRandom().nextInt(3))));
  }
 }
}''')
# Explicit cutout render layer for the crop cross planes.
write('InsultCropClient.java','''package it.noctis.magic;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class InsultCropClient{
 @SubscribeEvent public static void setup(FMLClientSetupEvent e){e.enqueueWork(()->{
  ItemBlockRenderTypes.setRenderLayer(Noctis.VAFF_CROP.get(),RenderType.cutout());
  ItemBlockRenderTypes.setRenderLayer(Noctis.SUCA_CROP.get(),RenderType.cutout());
 });}
}''')
import subprocess
sounds=assets/'sounds.json';sd=json.loads(sounds.read_text(encoding='utf-8')) if sounds.exists() else {}
for name,label,color in [('vaffanculo','Vaffanculo',(231,49,45)),('suca','Suca',(159,90,235))]:
 crop=name+'_crop';fruit=name+'_fruit';seed=name+'_seeds'
 for stage in range(8):
  tex=f'{crop}_{stage}';W=H=32;pix=bytearray(W*H*4)
  for y in range(H):
   for x in range(W):
    c=None
    h=5+stage*3
    if y>=31-h and abs(x-16)<=1:c=(42,112,45)
    for i in range(1+stage//2):
     yy=30-i*5;xx=16+(-1 if i%2==0 else 1)*(3+i)
     if ((x-xx)/5)**2+((y-yy)/2.3)**2<=1 and y>=31-h:c=shade((62,163,55),.8+.2*math.sin(x*.8+y*.5)**2)
    if stage>=5:
     for xx,yy in [(11,14),(21,18),(16,7)]:
      if (x-xx)**2+(y-yy)**2<=(3+stage-5)**2:c=shade(color,.7+.3*math.sin((x-xx+4)*.3))
    if c:
     q=(y*W+x)*4;pix[q:q+4]=bytes((*c,255))
  p=assets/'textures/block'/f'{tex}.png';p.parent.mkdir(parents=True,exist_ok=True);png(p,W,H,pix)
  write_noctis_json_resource(assets/'models/block'/f'{tex}.json',{'parent':'minecraft:block/crop','textures':{'crop':f'noctismagic:block/{tex}'}})
 write_noctis_json_resource(assets/'blockstates'/f'{crop}.json',{'variants':{f'age={i}':{'model':f'noctismagic:block/{crop}_{i}'} for i in range(8)}})
 for item,isfruit in [(seed,False),(fruit,True)]:
  W=H=32;pix=bytearray(W*H*4)
  for y in range(H):
   for x in range(W):
    c=None
    if isfruit:
     if ((x-15.5)/10)**2+((y-18)/10)**2<=1:c=shade(color,.65+.35*math.exp(-((x-11)**2+(y-13)**2)/95))
     if 4<=y<=9 and 14<=x<=16:c=(68,112,45)
     if ((x-20)/5)**2+((y-7)/2.5)**2<=1:c=(72,171,56)
     if 13<=y<=22 and x in (10,11,20,21) or 23<=y<=24 and 11<=x<=20:c=(65,22,34)
    else:
     if ((x-12)/5)**2+((y-17)/7)**2<=1 or ((x-21)/4)**2+((y-12)/5)**2<=1:c=shade(color,.7+.3*math.sin(x*.4)**2)
    if c:
     q=(y*W+x)*4;pix[q:q+4]=bytes((*c,255))
  png(assets/'textures/item'/f'{item}.png',W,H,pix)
  write_noctis_json_resource(assets/'models/item'/f'{item}.json',{'parent':'minecraft:item/generated','textures':{'layer0':f'noctismagic:item/{item}'}})
 mature={'condition':'minecraft:block_state_property','block':f'noctismagic:{crop}','properties':{'age':'7'}}
 write_noctis_json_resource(res/'data/noctismagic/loot_tables/blocks'/f'{crop}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':f'noctismagic:{seed}'}]},{'rolls':{'type':'minecraft:uniform','min':1,'max':3},'conditions':[mature],'entries':[{'type':'minecraft:item','name':f'noctismagic:{fruit}'}]},{'rolls':{'type':'minecraft:uniform','min':1,'max':2},'conditions':[mature],'entries':[{'type':'minecraft:item','name':f'noctismagic:{seed}'}]}]})
 snd='fruit_vaffanculo' if name=='vaffanculo' else 'fruit_suca';target=assets/'sounds'/f'{snd}.ogg';target.parent.mkdir(parents=True,exist_ok=True)
 wav=root/f'{snd}.wav'
 subprocess.run(['espeak-ng','-v','it','-s','148','-p','38','-a','170','-w',str(wav),label+'!'],check=True)
 subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(wav),'-ac','1','-c:a','libvorbis','-q:a','5',str(target)],check=True);wav.unlink()
 sd[snd]={'subtitle':f'subtitles.noctismagic.{snd}','sounds':[f'noctismagic:{snd}']}
 for lang in ('it_it','en_us'):
  p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d[f'item.noctismagic.{seed}']=f'Semi di {label}';d[f'block.noctismagic.{crop}']=f'Pianta di {label}';d[f'item.noctismagic.{fruit}']=f'Frutto di {label}';d[f'subtitles.noctismagic.{snd}']=label+'!';write_noctis_json_resource(p,d)
write_noctis_json_resource(sounds,sd)
print('Vaffanculo and Suca crops, renewable fruits, mob seed drops, aimed area attacks and synthesized Italian voice clips.')


# Giorno second sculpt: independent UVs for the face, chest and clothing.
n='GiornoSculptedClient.java'
p=java/n;s=p.read_text(encoding='utf-8')
a=s.index(' static V face(');b=s.index(' static class M',a)
s=s[:a]+''' static float clamp(float v){return Math.max(.025f,Math.min(.975f,v));}
 static V uv(V v,boolean front,boolean chest){
  float u=front?clamp(.5f+v.x()/(chest?8.65f:6.65f)):.025f;
  float t=chest?clamp((v.y()+.85f)/12f):clamp((v.y()+7.8f)/7.8f);
  return new V(v.x(),v.y(),v.z(),u,t,v.nx(),v.ny(),v.nz());
 }
 static void project(Part p,int tile,boolean chest){
  for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=tile)continue;
   boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
   p.faces.set(i,new Q(uv(q.a(),f,chest),uv(q.b(),f,chest),uv(q.c(),f,chest),uv(q.d(),f,chest),tile));}
 }
 static void strand(Part p,float x,float y,float z,float X,float Y,float Z,float width){
  Part q=p.child(0,0,0);
  for(int i=0;i<5;i++){
   float t=i/4f,curve=(float)Math.sin(t*Math.PI)*.42f;
   q.oval(6,x+(X-x)*t+curve,y+(Y-y)*t,z+(Z-z)*t,width*(1-.90f*t),width*.89f*(1-.85f*t),width*.76f*(1-.88f*t));
  }
  p.blade(6,x,y,z,X,Y,Z,width*1.25f);
  p.blade(9,x-.14f,y,z-.30f,X,Y,Z-.06f,width*.24f);
 }
 static void patch(Part p,int m,float x,float y,float z,float w,float h){
  V a=new V(x-w,y-h,z,0,0,0,0,-1),b=new V(x-w,y+h,z,0,1,0,0,-1),c=new V(x+w,y+h,z,1,1,0,0,-1),d=new V(x+w,y-h,z,1,0,0,0,-1);
  p.faces.add(new Q(a,b,c,d,m));
 }
'''+s[b:]
s=s.replace('body.loft(0,40,-1,0,0,1.75f,1.40f,.15f,0,0,4.12f,2.20f,2.6f,0,-.10f,3.96f,2.28f,5.6f,0,0,3.12f,1.85f,8.6f,0,0,2.55f,1.60f,10.8f,0,0,3.0f,1.85f);','''body.loft(8,64,-1,0,0,1.75f,1.42f,.15f,0,0,4.35f,2.30f,1.7f,0,-.10f,4.13f,2.43f,3.2f,0,-.10f,3.88f,2.48f,5.6f,0,0,3.04f,1.90f,8.6f,0,0,2.53f,1.62f,10.8f,0,0,3.15f,1.93f);
   project(body,8,true);
   // Tall upright collar and gold embroidered leaf motifs.
   body.loft(2,36,-1.55f,0,0,1.55f,1.43f,.25f,0,0,1.93f,1.64f);
   for(int side:new int[]{-1,1}){
    body.blade(0,side*1.22f,-1.8f,-.8f,side*1.89f,.55f,-1.24f,1.35f);
    for(int k=0;k<5;k++)body.blade(3,side*(1.27f+k*.09f),-1.35f+k*.33f,-1.54f,side*(1.84f+k*.035f),-1.1f+k*.33f,-1.57f,.38f);
    body.blade(2,side*3.85f,.45f,-1.35f,side*3.35f,2.15f,-1.83f,.55f);
    body.blade(2,side*2.99f,5.7f,-1.35f,side*.80f,7.3f,-1.76f,.55f);
    body.blade(0,side*3.0f,8.1f,-1.1f,side*3.6f,13.8f,-.45f,2.15f);
    body.blade(2,side*2.7f,9.6f,-1.67f,side*3.3f,13.3f,-.95f,.32f);
   }
   body.blade(3,0,6.65f,-1.88f,0,10.5f,-1.79f,.16f);''')
s=s.replace('project(head);','''project(head,5,false);
   // Sculpted angular nose, lower lip, cheek and eyelid ridges.
   head.loft(1,24,-4.9f,0,-2.68f,.20f,.13f,-3.9f,0,-2.92f,.32f,.25f,-3.03f,0,-3.20f,.46f,.39f,-2.78f,0,-2.94f,.31f,.18f);
   head.oval(10,0,-2.05f,-2.20f,.60f,.13f,.18f);
   for(int side:new int[]{-1,1}){
    head.blade(11,side*.80f,-4.40f,-2.66f,side*2.22f,-4.75f,-2.03f,.13f);
    head.blade(11,side*.72f,-4.04f,-2.71f,side*2.10f,-4.18f,-2.10f,.10f);
    head.blade(10,side*1.60f,-3.17f,-2.23f,side*2.30f,-2.58f,-1.48f,.20f);
   }''')
s=s.replace('for(int j=0;j<3;j++){Part q=head.child(-2.15f+j*2.15f,-6.9f,-2.64f);q.rz=(j-1)*.13f;curl(q,.80f,.95f);q.oval(7,0,0,.06f,.42f,.55f,.20f);}','''// Voluminous swept spikes behind the signature three rolls.
   for(int i=0;i<9;i++){
    float x=(i-4)*.76f;
    strand(head,x,-7.25f,.2f,x*.76f+(i%2==0?.55f:-.32f),-11.3f+(float)Math.abs(i-4)*.42f,.45f+Math.abs(i-4)*.10f,1.18f);
    strand(head,x*.80f,-8.25f,1.6f,x*1.12f,-10.65f+Math.abs(i-4)*.29f,2.45f,1.05f);
   }
   for(int side:new int[]{-1,1}){
    strand(head,side*2.8f,-5.55f,.02f,side*3.55f,-8.8f,1.16f,.82f);
    strand(head,side*2.6f,-5.85f,1.65f,side*2.8f,-8.7f,3.3f,1.1f);
   }
   for(int j=0;j<3;j++){
    Part q=head.child(-2.08f+j*2.08f,-6.68f,-2.69f);q.rz=(j-1)*.12f;curl(q,.79f,.90f);
    q.oval(7,0,0,.09f,.44f,.49f,.19f);
    for(int k=0;k<7;k++){float a=k*.66f;float x=(float)Math.cos(a)*.68f,y=(float)Math.sin(a)*.78f;q.blade(9,x,y,-.37f,x*.80f,y*.78f,-.42f,.17f);}
   }''')
s=s.replace('prev.child(0,j==0?-5.9f:1.65f,j==0?2.6f:.25f)','prev.child(j==0?-1.8f:j<3?-.25f:.14f,j==0?-5.9f:1.48f,j==0?2.9f:.15f)')
s=s.replace('q.oval(6,-.46f,.65f,0,1.05f,1.21f,.85f);q.oval(3,.46f,1.10f,.12f,1.0f,1.18f,.83f);','''q.oval(6,-.46f,.65f,0,1.05f,1.21f,.85f);q.oval(6,.46f,1.10f,.12f,1.0f,1.18f,.83f);
    q.blade(9,-.96f,.22f,-.52f,.76f,1.16f,-.58f,.21f);q.blade(9,.95f,.75f,-.55f,-.72f,1.63f,-.56f,.21f);''')
s=s.replace('fore[i].oval(1,0,4.95f,-.12f,.89f,1.1f,.72f);','''fore[i].oval(1,0,4.76f,-.10f,.65f,.74f,.43f);
    for(int j=0;j<4;j++)fore[i].loft(1,12,4.96f,-.48f+j*.31f,-.13f,.15f,.22f,5.75f-(j==3?.20f:0),-.48f+j*.31f,-.20f,.13f,.15f,5.92f-(j==3?.20f:0),-.48f+j*.31f,-.21f,.05f,.07f);
    fore[i].oval(1,s*.66f,4.80f,-.30f,.22f,.48f,.22f);
    arm[i].blade(2,0,1.55f,-1.55f,s*.75f,3.5f,-.95f,.43f);
    arm[i].blade(0,-s*.60f,.25f,-1.15f,-s*.45f,2.25f,-1.47f,.59f);
    fore[i].blade(2,s*.65f,.5f,-.88f,s*.20f,3.6f,-.85f,.28f);''')
s=s.replace('shin[i].blade(3,0,5.6f,-.95f,0,6.9f,-1.65f,.23f);','''shin[i].blade(3,0,5.6f,-.95f,0,6.9f,-1.65f,.23f);
    leg[i].blade(2,s*.58f,.25f,-1.30f,s*.12f,5.15f,-.95f,.29f);
    shin[i].blade(2,0,.2f,-1.10f,s*.35f,4.3f,-.88f,.31f);
    shin[i].loft(2,24,7.35f,0,-.64f,1.17f,1.71f,7.57f,0,-.64f,1.19f,1.74f);''')
s=s.replace('arm[i].rz=-s*.12f+(i==0?pose*.8f:0);','arm[i].rz=s*.07f+(i==0?pose*.46f:0);')
p.write_text(s,encoding='utf-8')
# Material atlas: no exposed skin anywhere on sleeves or trousers; heart only on projected chest.
W,H=1024,512;pix=bytearray(W*H*4)
def seg(u,v,x,y,X,Y):
 dx=X-x;dy=Y-y;t=max(0,min(1,((u-x)*dx+(v-y)*dy)/max(.0001,dx*dx+dy*dy)))
 return math.hypot(u-x-dx*t,v-y-dy*t)
def sat(v):return max(0,min(1,v))
bases=[(150,67,153),(232,178,143),(65,28,81),(223,169,54),(41,109,177),(232,178,143),(232,189,65),(111,70,29),(150,67,153),(255,225,126),(163,94,88),(47,31,43)]
for m,base in enumerate(bases):
 for y in range(128):
  for x in range(128):
   u=sat((x-3)/121);v=sat((y-3)/121);f=abs(u-.5)
   c=shade(base,.79+.20*math.sin(u*math.pi)+.07*math.sin(u*15+v*7)**2)
   if m in (0,8):
    fold=min(seg(u,v,.10,.12,.27,.65),seg(u,v,.85,.23,.69,.83),seg(u,v,.31,.56,.46,.78),seg(u,v,.65,.07,.60,.24))
    c=mix(c,(55,23,74),.42*math.exp(-(fold/.033)**2))
    c=mix(c,(207,126,203),.22*math.exp(-((u-.33)/.11)**2))
   if m==8:
    # Heart equation with broad lobes and a pointed bottom, skin only on the torso front.
    X=(u-.5)/.245;Y=(.29-v)/.245
    h=(X*X+Y*Y-1)**3-X*X*Y**3
    if .09<u<.91 and .08<v<.66 and h<=0:
     c=mix((237,184,151),(143,82,89),.18*abs(X)+.15*max(0,-Y))
     c=mix(c,(250,212,182),.20*math.exp(-((abs(X)-.48)/.22)**2))
     if abs(X)<.06:c=mix(c,(143,78,83),.35)
    if abs(h)<.09 and .19<u<.81 and .08<v<.66:c=(222,164,49)
    if abs(u-.5)<.007 and v>.67:c=(229,181,70)
   if m in (3,6,9):
    c=mix(c,(255,239,159),.38*math.sin(u*math.pi)**2)
    if m==6:
     t=math.sin(u*math.pi*12+v*1.9)
     c=mix(c,(146,95,30),.34*max(0,-t)**5)
     c=mix(c,(255,233,137),.36*max(0,t)**3)
   if m==4:
    if min((u-.27)**2+(v-.25)**2,(u-.73)**2+(v-.25)**2,(u-.27)**2+(v-.75)**2,(u-.73)**2+(v-.75)**2)<.026:c=(24,26,46)
   if m==5:
    c=mix(base,(122,65,77),.32*sat((f-.20)*4)+.20*v)
    c=mix(c,(255,217,185),.36*math.exp(-((u-.5)/.11)**2))
    for side in (-1,1):
     xx=side*(u-(.5+side*.17));dx=xx/.127;ey=.493-.035*dx;dy=(v-ey)/.047
     d=abs(dx)**1.6+abs(dy)**1.3
     if d<1.2:c=(39,25,39)
     if d<.78:c=(250,239,219)
     if d<.76 and abs(dx+.05)<.40:c=(57,137,121)
     if d<.73 and abs(dx+.05)<.16:c=(15,29,35)
     if d<.70 and (dx+.21)**2+(dy+.22)**2<.034:c=(255,255,243)
     if abs(dx)<1.12 and abs(v-(.402-.044*dx))<.018:c=(102,63,34)
     if abs(dx)<.96 and abs(v-(.425-.037*dx))<.008:c=(64,36,43)
     if seg(u,v,.5+side*.095,.57,.5+side*.065,.66)<.009:c=(165,93,91)
     if seg(u,v,.5+side*.25,.59,.5+side*.17,.66)<.013:c=mix(c,(138,79,87),.48)
    if f<.065 and abs(v-(.793-.018*(1-f/.065)))<.012:c=(110,52,65)
    if f<.045 and abs(v-.815)<.009:c=(203,119,111)
    if f<.065 and abs(v-.713)<.009:c=(146,80,80)
   if m==10:c=mix(c,(107,49,66),.35)
   q=(y*W+(m%8)*128+x+(m//8)*128*W)*4;pix[q:q+4]=bytes((*c,255))
png(assets/'textures/entity/giorno_sculpted.png',W,H,pix)
print('Giorno Giovanna resculpted: angular face, layered swept blonde hair, rolls, braid, tailored purple suit and dedicated chest material.')


# Defensive Geass lasts 60 seconds, not a fixed distance.
edit('GeassExile.java','int ticks=2400,dir=-1,blocked;','int ticks=1200,dir=-1,blocked;')
edit('GeassExile.java','if(!valid(p)||p.serverLevel()!=o.level||--o.ticks<=0){release(p,false);return;}','if(!valid(p)||p.serverLevel()!=o.level){release(p,false);return;}if(--o.ticks<=0){release(p,true);return;}')
edit('GeassExile.java','if(o.walked>=200){release(p,true);return;}','// Continue the order until the full minute expires.')
edit('GeassExile.java','if(best<0){o.blocked++;if(o.blocked>80){release(p,false);return;}best=16;}','if(best<0){o.blocked++;best=16;}')
edit('GeassExile.java','Math.min(200,(int)o.walked)','(o.ticks+19)/20')
for lang,it in [('it_it',True),('en_us',False)]:
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['message.noctismagic.geass_progress']='Geass: %s secondi rimanenti' if it else 'Geass: %s seconds remaining'
 write_noctis_json_resource(p,d)
# Lelouch: preserve C.C. and paired animations, rebuild the male costume and hair.
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
a='            float w=cc?3.08f:3.02f;'
assert a in s
s=s.replace(a,a+'''
            if(!cc){
                body.loft(0,32,10.1f,0,0,2.62f,1.87f,11.95f,0,0,2.75f,1.88f,13.0f,0,0,2.9f,1.83f);
                for(int side:new int[]{-1,1}){
                    // Rigid upswept Zero collar, dark exterior and crimson lining, gold piping.
                    Part collar=body.child(side*1.62f,-.35f,.80f);
                    collar.loft(11,32,-7.0f,side*2.0f,1.0f,.04f,.05f,-5.6f,side*2.18f,.8f,.78f,.30f,-3.6f,side*1.63f,.55f,1.03f,.52f,-1.2f,side*.65f,.12f,1.15f,.65f,.55f,0,0,.65f,.4f);
                    collar.blade(4,side*2.0f,-7.0f,.68f,side*2.52f,-4.6f,.30f,.22f);
                    collar.blade(4,side*2.52f,-4.6f,.30f,side*.38f,-.2f,-.55f,.25f);
                    collar.blade(10,side*1.73f,-5.8f,.23f,side*.42f,-.6f,-.56f,1.20f);
                    body.blade(4,side*3.15f,1.2f,-1.28f,side*1.2f,3.1f,-1.92f,.85f);
                    body.blade(4,side*1.2f,3.1f,-1.92f,0,3.6f,-1.97f,.48f);
                    body.blade(12,side*2.65f,5.0f,-1.22f,side*1.75f,8.6f,-1.55f,.6f);
                }
            }''',1)
# Replace only Lelouch's facial silhouette and hair geometry, retaining C.C. untouched.
a=s.index('            head.loft(6,64,');b=s.index('            projectFace(head);',a)
old=s[a:b]
s=s[:a]+'            if(cc){\n'+old+'            }else head.loft(6,80,-7.8f,0,.2f,1.25f,1.5f,-7.2f,0,.1f,2.47f,2.35f,-5.6f,0,0,2.92f,2.70f,-4.2f,0,-.1f,2.84f,2.72f,-2.8f,0,-.13f,2.39f,2.30f,-1.25f,0,-.32f,1.48f,1.70f,-.35f,0,-.45f,.68f,1.0f,0,0,-.48f,.28f,.60f);\n'+s[b:]
s=s.replace('            projectFace(head);','''            projectFace(head);
            if(!cc){
                head.loft(7,24,-4.8f,0,-2.55f,.15f,.10f,-3.9f,0,-2.75f,.27f,.21f,-3.05f,0,-3.13f,.41f,.34f,-2.78f,0,-2.94f,.27f,.16f);
                for(int t:new int[]{-1,1}){
                    head.blade(13,t*.75f,-4.52f,-2.64f,t*2.18f,-4.80f,-2.02f,.12f);
                    head.blade(14,t*1.65f,-3.12f,-2.16f,t*2.20f,-2.51f,-1.62f,.15f);
                }
            }''',1)
s=s.replace('for(int i=0;i<(cc?8:6);i++){','for(int i=0;i<(cc?8:0);i++){',1)
a='            Part back=head.child(0,-6.3f,1.9f);hair.add(back);'
assert a in s
s=s.replace(a,'''            if(!cc){
                // Thin layered swept strands, asymmetric tips across the forehead.
                for(int i=0;i<11;i++){
                    float t=i/10f,x=-2.8f+t*5.5f;
                    Part q=head.child(x,-7.9f,-1.3f);
                    float end=2.0f+(float)Math.sin(t*Math.PI)*2.15f;
                    float dx=-1.7f+t*.6f;
                    q.loft(8,24,-.60f,0,.75f,.55f,.63f,.35f,.15f,-.30f,.65f,.46f,1.65f,dx*.24f,-1.11f,.54f,.30f,2.7f,dx*.65f,-1.47f,.36f,.21f,end,dx,-1.22f,.035f,.045f);
                    q.blade(15,.12f,.20f,-.74f,dx*.78f,end*.85f,-1.40f,.15f);
                }
                for(int i=0;i<7;i++){
                    float t=i/6f;
                    Part q=head.child(-2.5f+t*4.8f,-7.4f,.6f);
                    q.loft(8,20,-.3f,0,0,.82f,.79f,.8f,-.28f,.3f,.84f,.72f,2.4f,-.85f,.55f,.55f,.4f,3.7f,-1.4f,.74f,.04f,.045f);
                    q.blade(15,-.05f,.4f,-.50f,-1.2f,3.3f,.32f,.17f);
                }
            }
'''+a,1)
# More layered side locks and sharper taper.
s=s.replace('cc?7:3.2f,s*.65f,-.15f,.69f,.72f,cc?16.8f:5.5f,s*.4f,.5f,.035f,.045f','cc?7:3.2f,s*.65f,-.15f,.69f,.72f,cc?16.8f:6.15f,s*.4f,.5f,.035f,.045f',1)
a='                fore[i].oval(cc?0:7,0,4.98f,-.08f,.67f,.91f,.55f);'
assert a in s
s=s.replace(a,'''                if(cc)fore[i].oval(0,0,4.98f,-.08f,.67f,.91f,.55f);
                else{
                    fore[i].oval(12,0,4.78f,-.08f,.65f,.68f,.45f);
                    for(int k=0;k<4;k++)fore[i].loft(12,12,4.98f,-.48f+k*.30f,-.13f,.15f,.20f,5.8f-(k==3?.18f:0),-.48f+k*.30f,-.18f,.13f,.14f,5.96f-(k==3?.18f:0),-.48f+k*.30f,-.18f,.04f,.05f);
                    fore[i].oval(12,s*.65f,4.79f,-.21f,.22f,.48f,.22f);
                    arms[i].blade(4,-s*.4f,.0f,-1.03f,s*.55f,1.1f,-1.18f,.26f);
                    fore[i].blade(4,s*.62f,2.95f,-.65f,s*.68f,3.85f,-.59f,.34f);
                }''',1)
# Fix collar/cape shape by using separate dark exterior and red lining on Lelouch.
s=s.replace('c.loft(5,18,0,0,0,cc?1.5f:2.7f,.32f,len*.24f,s*.6f,.4f,cc?2.0f:3.4f,.37f,len*.54f,s*1.25f,1.2f,cc?2.4f:4.1f,.4f,len*.80f,s*2.0f,2.0f,cc?1.7f:3.6f,.34f,len,s*2.7f,3.3f,.08f,.10f);','''if(cc)c.loft(5,18,0,0,0,1.5f,.32f,len*.24f,s*.6f,.4f,2.0f,.37f,len*.54f,s*1.25f,1.2f,2.4f,.4f,len*.80f,s*2.0f,2.0f,1.7f,.34f,len,s*2.7f,3.3f,.08f,.10f);
                else c.loft(5,36,0,0,0,2.4f,.22f,len*.24f,s*.50f,.65f,3.15f,.28f,len*.54f,s*1.15f,1.55f,3.6f,.37f,len*.80f,s*1.65f,2.4f,3.65f,.32f,len,s*1.8f,3.0f,2.9f,.13f);''',1)
s=s.replace('float s=cc?.94f:1.02f;p.scale(s,s,s);','if(cc)p.scale(.94f,.94f,.94f);else p.scale(1.12f,1.16f,1.10f);',1)
p.write_text(s,encoding='utf-8')
# New Lelouch-only atlas, C.C. unchanged.
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(27,28,43),(165,115,44),(17,18,30),(224,224,238),(218,168,47),(27,25,44),(233,178,145),(233,178,145),(31,26,32),(140,135,166),(123,23,44),(27,24,40),(20,21,30),(39,24,37),(158,91,78),(100,78,80)]
def clamp01(v):return max(0,min(1,v))
for m,base in enumerate(pal):
 for y in range(128):
  for x in range(128):
   u=clamp01((x-3)/121);v=clamp01((y-3)/121);f=abs(u-.5)
   c=shade(base,.80+.24*math.sin(math.pi*u)+.08*math.sin(u*23+v*8)**2)
   if m in (0,2,12):
    c=mix(c,(68,70,112),.34*math.exp(-((u-.34+.07*math.sin(v*9))/.14)**2))
    c=mix(c,(8,10,21),.32*math.sin(u*math.pi*3+v*3)**8)
   if m in (5,11):
    c=mix((115,22,43) if f<.24 else (23,22,35),(69,50,87),.19*math.sin(u*math.pi*7+v*3)**2)
    if v>.966:c=(207,155,49)
   if m==4:c=mix(base,(255,221,120),.36*math.sin(math.pi*u)**2)
   if m==8:
    wave=math.sin(u*math.pi*12+v*3)
    c=mix(base,(113,88,84),.26*max(0,wave)**5+.18*math.exp(-((v-.33)/.20)**2))
   if m==6:
    c=mix(base,(142,79,75),.28*clamp01((f-.19)*4)+.13*v)
    c=mix(c,(255,214,179),.30*math.exp(-((u-.49)/.11)**2))
    for side in (-1,1):
     dx=side*(u-(.5+side*.165))/.117
     dy=(v-(.47-.044*dx))/.055
     d=abs(dx)**1.7+abs(dy)**1.4
     if d<1.2:c=(36,22,35)
     if d<.80:c=(247,235,224)
     if d<.78 and abs(dx+.06)<.46:c=mix((76,33,114),(186,81,193),clamp01((dy+.7)/1.4))
     if d<.76 and abs(dx+.06)<.20:c=(26,18,40)
     if d<.76 and (dx+.20)**2+(dy+.25)**2<.052:c=(255,250,240)
     if abs(dx)<1.04 and abs(v-(.365-.049*dx))<.016:c=(38,27,34)
     if abs(dx)<.9 and abs(v-(.398-.045*dx))<.006:c=(123,69,66)
    if f<.04 and abs(v-.685)<.012:c=(157,87,77)
    if f<.065 and abs(v-(.79-.021*(1-f/.065)))<.010:c=(106,47,56)
    if f<.045 and abs(v-.81)<.009:c=(208,120,107)
   off=((m//8*128+y)*W+m%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/lelouch_sculpted.png',W,H,pix)
print('Lelouch rebuilt with angular face, sharp swept hair, layered Zero collar, dark uniform, crimson cape, gloves; Geass lasts one minute.')


# Joker: dedicated sculpted domino mask with actual eye openings, swept curls, tailored coat.
p=java/'JokerDetailedClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('import it.noctis.magic.SculptedGuestsClient.Part;','import it.noctis.magic.SculptedGuestsClient.Part;\nimport it.noctis.magic.SculptedGuestsClient.V;\nimport it.noctis.magic.SculptedGuestsClient.Q;',1)
s=s.replace(' static class M extends EntityModel<Joker>{',''' static float cl(float a){return Math.max(.025f,Math.min(.975f,a));}
 static V face(V v,boolean f){return new V(v.x(),v.y(),v.z(),f?cl(.5f+v.x()/6.4f):.025f,cl((v.y()+7.65f)/7.65f),v.nx(),v.ny(),v.nz());}
 static void project(Part p){
  for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=7)continue;boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
   p.faces.set(i,new Q(face(q.a(),f),face(q.b(),f),face(q.c(),f),face(q.d(),f),7));}
 }
 // Shaped eyewear with open eye holes, not a painted band or opaque oval.
 static V maskV(int side,float t,float r,float z){
  float dx=(float)Math.cos(t),dy=(float)Math.sin(t);
  float x=side*(1.12f+dx*(.77f+.53f*r));
  float y=-3.98f+dy*(.34f+.29f*r)-.16f*dx-.38f*r*Math.max(0,dx);
  return new V(x,y,-2.78f+.145f*x*x+z,.5f+.45f*dx,.5f+.45f*dy,0,0,-1);
 }
 static void mask(Part p,int side){
  for(int i=0;i<40;i++){
   float a=i*(float)Math.PI/20,b=(i+1)*(float)Math.PI/20;
   p.faces.add(new Q(maskV(side,a,0,.03f),maskV(side,b,0,.03f),maskV(side,b,.18f,-.01f),maskV(side,a,.18f,-.01f),11));
   p.faces.add(new Q(maskV(side,a,.18f,-.015f),maskV(side,b,.18f,-.015f),maskV(side,b,.86f,-.02f),maskV(side,a,.86f,-.02f),8));
   p.faces.add(new Q(maskV(side,a,.86f,-.02f),maskV(side,b,.86f,-.02f),maskV(side,b,1,0),maskV(side,a,1,0),11));
  }
 }
 static void curl(Part p,float x,float y,float z,float dx,float dy,float dz,float width){
  Part q=p.child(x,y,z);
  q.loft(9,24,-.65f,0,.38f,width*.50f,width*.58f,0,0,0,width,width*.85f,.65f,dx*.08f,-.24f,width*.91f,width*.70f,1.25f,dx*.40f,-.42f,width*.68f,width*.51f,1.70f,dx*.82f,dz*.75f,width*.38f,width*.28f,Math.max(1.75f,dy),dx,dz,.035f,.035f);
  q.blade(12,-.15f,0,-width*.65f,dx*.73f,1.52f,-.37f,.17f);
 }
 static class M extends EntityModel<Joker>{''',1)
a=s.index('   head.loft(7,32,');b=s.index('   for(int i=0;i<2;i++){int s=i==0?-1:1;',a)
s=s[:a]+'''   head.loft(7,80,-7.65f,0,.12f,1.35f,1.5f,-7.1f,0,.04f,2.50f,2.34f,-5.4f,0,0,2.94f,2.72f,-4.0f,0,-.1f,2.85f,2.58f,-2.65f,0,-.2f,2.40f,2.24f,-1.25f,0,-.3f,1.48f,1.68f,-.2f,0,-.4f,.42f,.7f);
   project(head);
   head.loft(1,24,-4.8f,0,-2.50f,.15f,.12f,-3.9f,0,-2.72f,.25f,.23f,-3.02f,0,-3.00f,.40f,.32f,-2.77f,0,-2.82f,.25f,.17f);
   head.oval(13,0,-1.9f,-1.94f,.47f,.11f,.12f);
   for(int side:new int[]{-1,1}){
    mask(head,side);
    head.oval(1,side*2.77f,-3.54f,.05f,.35f,.77f,.52f);
    head.blade(11,side*2.22f,-4.16f,-1.94f,side*2.86f,-4.64f,-.70f,.24f);
   }
   head.blade(8,-.50f,-4.12f,-2.79f,.50f,-4.12f,-2.79f,.26f);
   head.loft(9,40,-9.05f,0,.35f,.60f,.55f,-8.70f,0,.23f,2.34f,2.10f,-7.6f,0,.20f,3.14f,2.93f,-6.25f,0,.30f,3.35f,3.01f);
   head.loft(9,32,-7.65f,0,1.0f,2.75f,2.15f,-5.7f,0,1.35f,3.04f,1.85f,-3.2f,0,1.68f,2.60f,1.26f,-1.4f,0,1.55f,1.45f,.23f);
   // Irregular layered wavy locks, individual sculpted tufts with bent tips.
   for(int j=0;j<11;j++){
    float x=-2.85f+j*.55f;float dx=(j%3==0?.8f:-.83f)+(j-5)*.07f;
    float end=1.88f+(j%4)*.36f;
    curl(head,x,-7.85f+(float)Math.sin(j*1.1)*.28f,-2.03f,dx,end,-.63f,.60f+(j%3)*.13f);
   }
   for(int j=0;j<9;j++){
    float x=-2.65f+j*.64f;
    curl(head,x,-8.9f+(float)Math.cos(j*.9)*.30f,.04f,(j%2==0?-.75f:.65f),1.55f+(j%3)*.25f,-1.50f,.77f);
   }
   for(int side:new int[]{-1,1}){
    for(int j=0;j<5;j++){
     Part q=head.child(side*(2.42f+j*.13f),-7.1f+j*.62f,.05f+j*.40f);q.rz=-side*(.46f+j*.14f);
     curl(q,0,0,0,side*(.5f+j*.12f),1.85f+(j%2)*.35f,.54f,.63f);
    }
   }
'''+s[b:]
s=s.replace('body.blade(3,s*1.5f,-1.0f,-.7f,s*2.4f,-2.4f,.85f,1.8f);','''body.blade(3,s*1.5f,-1.0f,-.7f,s*3.6f,-3.0f,1.15f,2.9f);
    body.blade(5,s*2.1f,-1.15f,-.35f,s*3.5f,-2.9f,.94f,.23f);
    body.blade(14,s*2.5f,1.2f,-1.25f,s*1.6f,3.15f,-1.95f,.65f);
    body.blade(14,s*2.25f,5.4f,-1.15f,s*.6f,7.05f,-1.48f,.36f);
    body.blade(5,s*2.0f,8.0f,-.95f,s*2.55f,9.2f,-.85f,.25f);''',1)
s=s.replace('for(int j=0;j<4;j++)elbow[i].oval(4,-.51f+j*.34f,5.95f,-.15f,.21f,.46f,.29f);','''for(int j=0;j<4;j++){
     float x=-.48f+j*.32f;
     elbow[i].loft(4,16,5.35f,x,-.13f,.17f,.23f,5.93f,x,-.22f,.16f,.18f,6.24f-(j==3?.16f:0),x,-.35f,.11f,.13f,6.39f-(j==3?.16f:0),x,-.38f,.04f,.05f);
     elbow[i].blade(15,x,5.38f,-.48f,x,5.92f,-.42f,.10f);
    }
    elbow[i].blade(15,-.45f,4.45f,-.60f,.40f,4.65f,-.64f,.17f);
    arm[i].blade(14,0,.7f,-1.28f,s*.55f,3.9f,-.92f,.46f);
    elbow[i].blade(14,s*.48f,.5f,-.83f,0,3.55f,-.80f,.35f);''',1)
s=s.replace('coat[i].loft(0,16,0,0,0,1.40f,.38f,3.4f,s*.28f,.35f,1.65f,.28f,7.5f,s*.50f,.85f,1.57f,.22f,12.0f,s*.95f,1.55f,.06f,.08f);','''coat[i].loft(0,32,0,0,0,1.65f,.34f,3.4f,s*.38f,.44f,2.02f,.28f,7.5f,s*.72f,1.10f,2.18f,.22f,12.6f,s*1.42f,2.5f,1.02f,.16f,14.1f,s*2.15f,2.9f,.035f,.045f);
    coat[i].blade(14,s*.56f,1.0f,-.35f,s*1.33f,11.3f,1.60f,.4f);''',1)
s=s.replace('coat[i+2].blade(0,0,0,0,s*1.5f,10.35f,2.4f,2.22f);','''coat[i+2].loft(3,24,0,0,0,.95f,.27f,3.6f,s*.33f,.72f,1.36f,.20f,7.0f,s*.85f,1.6f,1.45f,.18f,12.1f,s*1.8f,2.55f,.04f,.06f);''',1)
s=s.replace('float cast=e.summoning();head.ry=yaw*.01745f;head.rx=pitch*.016f;body.ry=cast*.12f;','''float cast=e.summoning();float idle=amount<.08f?(float)Math.pow(Math.max(0,Math.sin(age*.024f)),10)*(1-cast):0;
   head.ry=yaw*.01745f;head.rx=pitch*.016f;head.rz=-.055f-idle*.06f;body.ry=cast*.12f+idle*.12f;''',1)
s=s.replace('arm[i].rz=-s*(.10f+(i==1?cast*.24f:0));','arm[i].rz=s*(.07f+(i==1?cast*.24f:0));if(i==0){arm[i].rx-=idle*.75f;arm[i].rz+=idle*.18f;}',1)
s=s.replace('leg[i].rx=w*.65f;knee[i].rx=Math.max(0,-w)*.46f;','if(i==0)elbow[i].rx-=idle*1.40f;leg[i].rx=w*.65f;knee[i].rx=Math.max(0,-w)*.46f;',1)
s=s.replace('  @Override public ResourceLocation getTextureLocation(Joker e)','  @Override protected void scale(Joker e,PoseStack p,float partial){p.scale(1.08f,1.10f,1.08f);}\n  @Override public ResourceLocation getTextureLocation(Joker e)',1)
p.write_text(s,encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(24,23,30),(235,190,162),(70,65,79),(37,33,43),(183,12,35),(17,16,22),(150,146,158),(235,190,162),(247,246,241),(17,17,24),(185,190,200),(14,12,19),(105,78,73),(149,73,73),(65,60,75),(104,8,26)]
def sat2(v):return max(0,min(1,v))
for m,base in enumerate(pal):
 for y in range(128):
  for x in range(128):
   u=sat2((x-3)/121);v=sat2((y-3)/121);f=abs(u-.5)
   c=shade(base,.79+.21*math.sin(math.pi*u)+.06*math.sin(u*87+v*23)**2)
   if m in (0,2,3,5,14):
    ridge=math.sin(u*math.pi*4+v*6+math.sin(v*9)*.9)
    c=mix(c,(91,79,102),.32*max(0,ridge)**8)
    c=mix(c,(8,7,15),.30*max(0,-ridge)**7)
    if m==2 and abs((u*4)%1-.5)<.024:c=mix(c,(111,102,119),.28)
   if m==4:
    c=mix(c,(249,52,65),.45*math.exp(-((u-.32)/.19)**2))
    c=mix(c,(75,5,20),.30*(1-math.sin(u*math.pi)))
   if m==9:
    wave=math.sin(u*math.pi*14+v*3)
    c=mix(c,(75,73,91),.27*max(0,wave)**5+.09*math.exp(-((v-.25)/.17)**2))
   if m==7:
    c=mix(base,(155,86,78),.28*sat2((f-.19)*4)+.15*v)
    c=mix(c,(255,222,189),.30*math.exp(-((u-.5)/.14)**2))
    for side in (-1,1):
     dx=side*(u-(.5+side*.179))/.105;dy=(v-(.48-.018*dx))/.043
     d=abs(dx)**1.8+abs(dy)**1.45
     if d<1.17:c=(37,22,32)
     if d<.80:c=(245,235,223)
     if d<.78 and abs(dx+.045)<.44:c=(84,75,87)
     if d<.76 and abs(dx+.045)<.18:c=(21,18,27)
     if d<.76 and (dx+.18)**2+(dy+.22)**2<.046:c=(255,250,238)
     if abs(dx)<.96 and abs(v-(.39-.035*dx))<.013:c=(49,32,36)
    if f<.076 and abs(v-(.765-.018*(1-f/.076)+.025*(u-.5)))<.009:c=(105,48,55)
    if f<.043 and abs(v-.782)<.008:c=(213,130,119)
   if m==8:c=mix(base,(255,254,250),.55*math.sin(u*math.pi)**2)
   if m==10:c=mix(base,(246,246,250),.60*math.exp(-((u-.58)/.15)**2))
   q=((m//8*128+y)*W+m%8*128+x)*4;pix[q:q+4]=bytes((*c,255))
png(assets/'textures/entity/joker_detailed.png',W,H,pix)
print('Joker revised with open sculpted white mask, angular face, irregular curls, long layered coat and articulated red gloves.')


# Guts: muscular asymmetrical Black Swordsman armor, cropped spiky hair, enormous slab sword.
p=java/'GutsSculptedClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('f?.5f+v.x()/7.6f:.04f,v.v()','f?Math.max(.03f,Math.min(.97f,.5f+v.x()/6.9f)):.03f,Math.max(.03f,Math.min(.97f,(v.y()+7.7f)/7.7f))',1)
a=s.index('   head.loft(5,64,');b=s.index('   for(int i=0;i<2;i++){',a)
s=s[:a]+'''   // Adult angular skull, broad cheekbones and square jaw.
   head.loft(5,36,-7.72f,0,.10f,1.55f,1.65f,-7.12f,0,.02f,2.55f,2.42f,-5.55f,0,-.02f,3.08f,2.76f,-4.55f,0,-.10f,3.12f,2.66f,-3.60f,0,-.13f,2.97f,2.58f,-2.32f,0,-.19f,2.72f,2.40f,-1.15f,0,-.32f,2.53f,1.96f,-.48f,0,-.45f,1.87f,1.54f,-.12f,0,-.48f,1.45f,1.13f);project(head);
   head.loft(2,16,-4.88f,0,-2.56f,.25f,.18f,-4.08f,0,-2.80f,.30f,.30f,-3.36f,0,-3.06f,.41f,.42f,-2.83f,0,-3.13f,.48f,.36f,-2.61f,0,-2.94f,.32f,.18f);
   for(int side:new int[]{-1,1}){
    head.oval(14,side*.30f,-2.74f,-3.06f,.10f,.065f,.10f);
    head.loft(2,12,-5.14f,side*1.15f,-2.48f,.70f,.10f,-4.92f,side*1.35f,-2.51f,.91f,.18f,-4.75f,side*1.45f,-2.45f,.63f,.10f);
    head.blade(2,side*1.93f,-3.12f,-1.89f,side*2.35f,-2.38f,-1.35f,.43f);
   }
   head.loft(7,32,-8.25f,0,.20f,1.70f,1.60f,-7.88f,0,.22f,2.82f,2.60f,-7.10f,0,.30f,3.16f,2.80f,-6.08f,0,.60f,3.12f,2.65f);
   for(int row=0;row<8;row++)for(int col=0;col<13;col++){
    float x=(col-6)*.47f,z=-2.17f+row*.62f;
    float rad=x*x/9.5f+z*z/7.9f;
    if(rad>1.12f)continue;
    float y=-7.87f+.82f*rad;
    float h=1.35f+.62f*((row*11+col*7)%7)/6f+.35f*(1-rad);
    boolean white=(col>=2&&col<=4&&row<=2)||(col==4&&row==3);
    Part q=head.child(x,y,z);
    q.rz=(col-6)*.047f;q.rx=.25f+row*.045f;
    float dx=(col-6)*.047f;
    int mat=white?15:7;
    q.loft(mat,8,-h,dx,.56f,.018f,.018f,-h*.73f,dx*.82f,.39f,.13f,.18f,-h*.38f,dx*.38f,.20f,.27f,.29f,.16f,0,0,.34f,.40f);
   }
   for(int j=0;j<14;j++){
    float x=-2.73f+j*.42f;
    int mat=(j>=2&&j<=5)?15:7;
    Part q=head.child(x,-7.58f+(float)Math.sin(j*1.7)*.13f,-2.04f);
    float len=(j>=2&&j<=5)?2.10f+(j%3)*.19f:1.25f+(j%4)*.27f;
    float drift=(j-6.5f)*.04f;
    q.loft(mat,10,-.32f,0,.18f,.28f,.39f,.35f,drift,-.28f,.32f,.32f,1.03f,drift*.8f,-.45f,.24f,.23f,len*.84f,drift+.05f,-.42f,.11f,.12f,len,drift+.12f,-.28f,.018f,.018f);
   }
   for(int side:new int[]{-1,1})for(int k=0;k<8;k++){
    Part q=head.child(side*(2.60f+.12f*(k%3)),-7.35f+(k%3)*.22f,-1.85f+k*.54f);
    q.rz=-side*.32f;
    q.loft(7,8,-.65f,side*.16f,.15f,.03f,.04f,-.16f,0,.08f,.26f,.32f,.54f,0,0,.34f,.37f,1.24f+(k%3)*.16f,side*.09f,.18f,.045f,.055f);
   }
'''+s[b:]
s=s.replace('arms[i].loft(0,28,-.9f,0,0,1.70f,1.72f,.8f,0,0,2.30f,2.15f,3.1f,0,0,1.94f,1.80f,4.9f,0,0,1.4f,1.43f);','''arms[i].loft(i==1?2:0,36,-.9f,0,0,1.92f,1.94f,.8f,0,0,2.50f,2.32f,2.8f,0,0,2.26f,2.14f,4.9f,0,0,1.5f,1.55f);
    if(i==1){
     arms[i].oval(2,-.28f,2.85f,-1.23f,1.63f,1.70f,.98f);
     arms[i].blade(14,.10f,1.35f,-2.05f,.62f,4.1f,-1.48f,.44f);
    }
    Part pauldron=arms[i].child(0,-.8f,0);
    pauldron.loft(1,36,-.95f,s*.35f,0,.64f,.70f,-.48f,s*.22f,0,2.14f,1.96f,.42f,s*.37f,0,2.88f,2.48f,1.0f,s*.42f,0,2.60f,2.20f);
    pauldron.blade(4,s*.4f,-.55f,-1.98f,s*2.85f,.25f,-1.15f,.30f);
    for(int j=0;j<4;j++)pauldron.oval(4,s*(.2f+j*.61f),.40f,-2.05f+j*.12f,.13f,.13f,.13f);''',1)
s=s.replace('for(int j=0;j<3;j++)arms[i].loft(1,28,-.8f+j*1.18f,0,0,2.25f-j*.18f,2.12f-j*.12f,.2f+j*1.18f,0,0,2.45f-j*.23f,2.32f-j*.19f);','''for(int j=0;j<(i==1?2:4);j++)arms[i].loft(1,32,-.6f+j*.89f,0,0,2.45f-j*.12f,2.32f-j*.12f,.32f+j*.89f,0,0,2.65f-j*.17f,2.44f-j*.14f);''',1)
s=s.replace('fore[i].loft(i==0?1:0,32','fore[i].loft(i==0?1:10,32',1)
s=s.replace('for(int j=0;j<3;j++)fore[i].loft(i==0?4:3,24','for(int j=0;j<5;j++)fore[i].loft(i==0?4:10,24',1)
s=s.replace('for(int j=0;j<4;j++)fore[i].oval(i==0?4:0,-.85f+j*.55f,5.6f,-.62f,.26f,.53f,.34f);','''for(int j=0;j<4;j++){
     float x=-.84f+j*.55f;
     fore[i].loft(i==0?4:2,16,5.20f,x,-.52f,.26f,.38f,5.86f,x,-.66f,.25f,.31f,6.18f,x,-.82f,.14f,.19f);
     if(i==0)fore[i].oval(4,x,5.25f,-.91f,.23f,.25f,.17f);
    }
    if(i==0){
     fore[i].loft(11,24,.15f,0,0,1.51f,1.53f,.50f,0,0,1.58f,1.61f);
     fore[i].blade(11,-.92f,.6f,-1.29f,-.95f,3.7f,-1.16f,.41f);
     fore[i].blade(11,.92f,.6f,-1.29f,.95f,3.7f,-1.16f,.41f);
     for(int j=0;j<4;j++)fore[i].oval(4,1.27f,.70f+j*.79f,-.48f,.19f,.17f,.17f);
    }''',1)
s=s.replace('sword.loft(8,8,2.1f,0,0,2.18f,.45f,5.2f,0,0,2.52f,.55f,22.0f,0,0,2.52f,.55f,25.6f,0,0,.08f,.12f);','sword.loft(8,8,2.1f,0,0,3.25f,.50f,5.0f,0,0,3.92f,.62f,30.0f,0,0,3.92f,.62f,34.0f,0,0,.08f,.12f);',1)
s=s.replace('sword.loft(9,8,2.3f,0,-.36f,1.72f,.12f,22.0f,0,-.42f,1.92f,.13f,25.0f,0,-.07f,.07f,.06f);','''sword.loft(9,8,2.3f,0,-.49f,2.62f,.13f,30.0f,0,-.52f,3.05f,.14f,33.6f,0,-.07f,.07f,.06f);
   sword.loft(9,8,2.3f,0,.49f,2.62f,.13f,30.0f,0,.52f,3.05f,.14f,33.6f,0,.07f,.07f,.06f);
   for(int i=0;i<11;i++)sword.loft(10,16,-2.8f+i*.43f,0,0,.53f,.54f,-2.58f+i*.43f,0,0,.52f,.53f);
   for(int side:new int[]{-1,1}){
    Part pouch=body.child(side*2.85f,9.15f,-.85f);pouch.rz=side*.18f;
    pouch.loft(3,24,0,0,0,.85f,.65f,.4f,0,0,1.1f,.82f,3.65f,0,0,1.15f,.85f,4.2f,0,0,.85f,.61f);
    pouch.loft(11,20,.40f,0,-.05f,1.16f,.88f,.72f,0,-.05f,1.13f,.89f);
    pouch.oval(4,0,1.10f,-.86f,.22f,.27f,.12f);
   }''',1)
s=s.replace('arms[i].rz=-s*.14f+(i==1?hit*.80f:0);','arms[i].rz=s*.08f+(i==1?hit*.65f:0);',1)
s=s.replace('p.scale(1.23f,1.22f,1.23f);','p.scale(1.36f,1.29f,1.29f);',1)
p.write_text(s,encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(34,37,42),(75,79,87),(193,137,99),(99,63,39),(145,148,150),(192,136,99),(25,22,29),(31,28,27),(155,158,165),(74,78,86),(161,151,133),(115,119,123),(166,165,157),(50,35,32),(127,76,61),(216,213,204)]
for m,base in enumerate(pal):
 for y in range(128):
  for x in range(128):
   u=sat2((x-3)/121);v=sat2((y-3)/121);f=abs(u-.5)
   c=shade(base,.78+.24*math.sin(math.pi*u)+.07*math.sin(u*83+v*21)**2)
   if m in (0,1,4,8,9,11):
    c=mix(c,(184,190,199),(.31 if m in (1,8,11) else .14)*math.exp(-((u-.3)/.10)**2))
    c=shade(c,.88+.12*math.sin(u*17+v*4)**2)
    if math.sin(u*127+v*38)>.96 and math.sin(v*112-u*8)>.70:c=mix(c,(199,200,205),.40)
    if v<.024 or v>.97:c=shade(c,.57)
   if m==6:
    c=mix((22,19,26) if f>.20 else (65,23,31),(88,67,78),.23*math.sin(u*math.pi*7+v*3)**2)
   if m in (7,15):
    strand=math.sin(u*math.pi*20+v*3.6+math.sin(v*5)*.38)
    c=mix(c,(113,103,94) if m==7 else (255,251,238),(.38 if m==7 else .51)*max(0,strand)**4)
    c=mix(c,(14,12,14) if m==7 else (114,111,109),.42*max(0,-strand)**6)
    c=shade(c,.77+.23*math.sin(math.pi*min(1,v+.16)))
   if m==10:
    if abs(v*12-round(v*12))<.075:c=shade(c,.57)
   if m==5:
    def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
    c=mix(base,(83,43,35),.44*sat2((f-.17)*4)+.13*v)
    c=mix(c,(239,185,139),.32*g(.50,.34,.13,.19)+.24*g(.50,.65,.09,.13))
    for side in (-1,1):
     ex=.5+side*.177
     dx=side*(u-ex)/.115;dy=(v-(.476-.041*dx))/.040
     c=mix(c,(70,40,36),.53*g(ex,.46,.13,.074)+.18*g(ex,.54,.11,.045))
     c=mix(c,(226,157,109),.29*g(.5+side*.20,.584,.10,.065))
     c=mix(c,(92,48,37),.32*g(.5+side*.255,.68,.085,.10))
     if side==1:
      d=abs(dx)**1.8+abs(dy)**1.32
      if d<1.14:c=(48,30,27)
      if d<.74:c=(202,197,185)
      if d<.72 and abs(dx+.13)<.40:c=mix((53,47,42),(116,112,101),.45*sat2(dy+.5))
      if d<.70 and abs(dx+.13)<.17:c=(20,18,20)
      if d<.70 and (dx+.29)**2+(dy+.18)**2<.045:c=(244,241,233)
     elif abs(dx)<1.04 and abs(v-(.480-.010*dx+.010*dx*dx))<.011:c=(51,28,27)
     brow=.383-.041*dx+.013*dx*dx
     if abs(dx)<1.13 and abs(v-brow)<(.022-.007*min(1,abs(dx))):
      c=mix((31,25,24),(77,54,45),.30*max(0,math.sin(u*480+v*51)))
     if abs(dx)<1.0 and abs(v-(brow+.030))<.008:c=mix(c,(85,42,34),.53)
    scar=.322+.044*(v-.50)
    if .395<v<.673 and abs(u-scar)<.012:c=mix(c,(101,47,40),.78)
    if .398<v<.673 and abs(u-scar-.012)<.005:c=mix(c,(228,157,116),.60)
    if .564<v<.645 and abs(u-(.71-.35*(v-.565)))<.008:c=mix(c,(110,55,44),.74)
    if .596<v<.666 and abs(u-(.245+.40*(v-.596)))<.006:c=mix(c,(130,67,52),.65)
    c=mix(c,(105,54,43),.27*g(.39,.716,.035,.078)+.27*g(.61,.716,.035,.078))
    if f<.105 and abs(v-(.778-.018*(1-f/.105)+.011*math.sin(u*30)))<.010:c=(69,37,32)
    if f<.080 and abs(v-(.805-.008*math.cos(f*31)))<.009:c=mix(c,(203,129,105),.75)
    c=mix(c,(86,49,41),.30*g(.5,.844,.13,.028))
    c=mix(c,(226,170,124),.26*g(.5,.895,.16,.042))
    if v>.79 and f<.29:
     grain=math.sin(x*17.13+y*31.71)*math.sin(x*9.27-y*12.59)
     if grain>.64:c=mix(c,(65,42,36),.32)
   q=((m//8*128+y)*W+m%8*128+x)*4;pix[q:q+4]=bytes((*c,255))
png(assets/'textures/entity/guts_sculpted.png',W,H,pix)
print('Guts revised: shorter irregular hair, scarred angular face, asymmetric armor, prosthetic arm and much wider Dragon Slayer.')


# Griffith White Falcon: dedicated sculptural revision with plated feathers, flowing curls and cape.
p=java/'GriffithClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('import it.noctis.magic.SculptedGuestsClient.Part;','import it.noctis.magic.SculptedGuestsClient.Part;\nimport it.noctis.magic.SculptedGuestsClient.V;\nimport it.noctis.magic.SculptedGuestsClient.Q;',1)
s=s.replace('    static class M extends EntityModel<Griffith>{','''    static float clamp(float x){return Math.max(.025f,Math.min(.975f,x));}
    static V face(V v,boolean front){return new V(v.x(),v.y(),v.z(),front?clamp(.5f+v.x()/6.7f):.025f,clamp((v.y()+7.65f)/7.65f),v.nx(),v.ny(),v.nz());}
    static void project(Part p){
        for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=4)continue;boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
            p.faces.set(i,new Q(face(q.a(),f),face(q.b(),f),face(q.c(),f),face(q.d(),f),4));}
    }
    static void feather(Part p,int material,float x,float y,float z,float angle,float length,float width){
        Part q=p.child(x,y,z);q.rz=angle;
        q.loft(material,16,-.15f,0,0,width*.42f,.15f,length*.24f,0,-.10f,width*.58f,.23f,length*.64f,0,-.19f,width*.39f,.16f,length,0,-.31f,.035f,.035f);
        q.blade(10,0,.08f,-.23f,0,length*.84f,-.44f,width*.13f);
    }
    static void wave(Part q,float length,float width,float phase,float drift,float depth){
        float[] a=new float[65];
        for(int j=0;j<13;j++){float t=j/12f,amp=(float)Math.sin(t*Math.PI*.93);
            a[j*5]=length*t;
            a[j*5+1]=drift*t+amp*.78f*(float)Math.sin(t*13+phase);
            a[j*5+2]=depth*t+amp*.32f*(float)Math.cos(t*13+phase);
            float r=j==12?.035f:width*(.76f+.22f*(float)Math.sin(t*Math.PI))*(1-.30f*t);
            a[j*5+3]=r;a[j*5+4]=r*.83f;
        }
        q.loft(6,24,a);
    }
    static class M extends EntityModel<Griffith>{''',1)
s=s.replace('final Part[] arm=new Part[2],fore=new Part[2],leg=new Part[2],shin=new Part[2];','final Part[] arm=new Part[2],fore=new Part[2],leg=new Part[2],shin=new Part[2],cape=new Part[3];',1)
a=s.index('            // Delicate face:');b=s.index('                arm[i]=body.child',a)
s=s[:a]+'''            for(int side:new int[]{-1,1}){
                body.blade(10,side*3.28f,.55f,-1.90f,side*.35f,2.65f,-2.70f,.22f);
                for(int j=0;j<5;j++){
                    feather(body,0,side*(.58f+j*.55f),2.30f+j*.16f,-2.40f+j*.12f,-side*(.66f+j*.07f),1.45f-j*.065f,.55f);
                    feather(body,0,side*(2.15f+j*.23f),9.95f+j*.28f,-1.62f,-side*.28f,2.7f-j*.11f,.64f);
                }
                body.oval(9,side*2.04f,.82f,-2.08f,.55f,.59f,.24f);
                feather(body,9,side*2.13f,.70f,-2.25f,side*2.7f,2.55f,.68f);
                body.blade(9,side*1.92f,3.8f,-2.20f,side*.45f,4.92f,-2.22f,.5f);
            }
            for(int j=0;j<3;j++){
                Part c=cape[j]=body.child((j-1)*2.05f,.12f,2.12f);
                c.loft(11,32,0,0,0,1.52f,.17f,5,(j-1)*.40f,.5f,1.85f,.24f,12,(j-1)*1.0f,1.5f,2.12f,.26f,20.7f,(j-1)*1.65f,2.7f,2.02f,.20f,23,(j-1)*1.75f,3.1f,1.6f,.10f);
            }
            head.loft(4,80,-7.65f,0,.12f,1.4f,1.6f,-7.1f,0,.04f,2.55f,2.36f,-5.55f,0,0,3.02f,2.73f,-4.0f,0,-.08f,2.89f,2.60f,-2.45f,0,-.2f,2.32f,2.13f,-1.05f,0,-.32f,1.37f,1.53f,-.15f,0,-.39f,.38f,.66f);
            project(head);
            head.loft(5,24,-4.8f,0,-2.48f,.13f,.10f,-3.85f,0,-2.66f,.24f,.20f,-3.0f,0,-2.97f,.38f,.32f,-2.75f,0,-2.75f,.24f,.15f);
            head.oval(12,0,-1.94f,-1.88f,.43f,.11f,.11f);
            for(int side:new int[]{-1,1}){
                head.oval(5,side*2.88f,-3.45f,.1f,.36f,.76f,.49f);
                head.blade(13,side*.66f,-4.30f,-2.60f,side*2.02f,-4.58f,-1.93f,.11f);
            }
            head.loft(6,40,-9.45f,0,.2f,.65f,.70f,-9.0f,0,.1f,2.5f,2.4f,-7.7f,0,.2f,3.56f,3.15f,-6.12f,0,.38f,3.48f,3.05f);
            for(int j=0;j<11;j++){
                float x=-3.0f+j*.57f;Part q=head.child(x,-8.5f+(float)Math.sin(j*.84f)*.35f,-1.87f);
                wave(q,2.6f+(j%4)*.47f,.48f+(j%3)*.075f,j*1.09f,(j-5)*.10f,-.61f);
                curls.add(q);
            }
            Part back=head.child(0,-6.8f,1.9f);
            back.loft(6,32,-.7f,0,0,2.9f,1.8f,1.4f,0,.5f,3.5f,1.65f,4.6f,0,1.15f,3.6f,1.65f,8.2f,0,1.55f,3.55f,1.45f,14f,0,1.7f,3.2f,1.05f,18f,0,1.6f,1.5f,.25f);
            for(int j=0;j<13;j++){
                Part q=head.child(-3.15f+j*.52f,-6.55f,2.53f);curls.add(q);
                wave(q,13.8f+(j%5)*.80f,.63f+(j%3)*.09f,j*1.32f,(j-6)*.14f,1.25f);
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                for(int j=0;j<5;j++){
                    Part q=head.child(s*(2.52f+j*.18f),-6.22f+j*.28f,-.60f+j*.61f);curls.add(q);
                    wave(q,13.5f+j*.67f,.56f+(j%3)*.10f,j*1.43f+i*.91f,s*(.18f+j*.20f),-1.35f+j*.28f);
                }
'''+s[b:]
s=s.replace('                arm[i]=body.child(s*4.05f,.35f,0);','''                arm[i]=body.child(s*4.23f,.28f,0);
                for(int j=0;j<5;j++){
                    float x=s*(.62f+j*.30f),y=-.75f+j*.56f;
                    feather(arm[i],0,x,y,-1.85f+j*.06f,-s*(.25f+j*.12f),2.1f-j*.13f,.79f);
                    feather(arm[i],0,x,y+.55f,1.95f,s*.20f,1.85f,.73f);
                }
                if(i==1){
                    Part wing=arm[i].child(s*1.1f,-.40f,.36f);
                    for(int j=0;j<7;j++)feather(wing,0,s*(.32f+j*.28f),.30f+j*.30f,.03f-j*.11f,s*(2.28f+j*.105f),5.15f-j*.31f,.72f);
                    for(int j=0;j<6;j++)feather(wing,1,s*(.15f+j*.23f),.32f+j*.32f,-.34f,s*(1.58f+j*.17f),2.25f,.51f);
                }''',1)
s=s.replace('                fore[i].oval(0,0,5.12f,-.15f,.91f,1.03f,.69f);','''                for(int j=0;j<5;j++){
                    feather(fore[i],0,s*(.80f-j*.11f),.6f+j*.53f,-1.24f,-s*.38f,1.30f,.54f);
                    feather(fore[i],1,-s*(.78f-j*.10f),.65f+j*.53f,-1.19f,s*.34f,1.22f,.42f);
                }
                feather(fore[i],0,s*1.04f,.72f,.12f,s*2.62f,3.3f,.75f);
                fore[i].oval(0,0,5.12f,-.15f,.91f,.82f,.54f);''',1)
s=s.replace('                for(int j=0;j<3;j++)fore[i].oval(0,-.45f+j*.45f,5.72f,-.36f,.22f,.52f,.26f);','''                for(int j=0;j<4;j++){
                    float x=-.54f+j*.36f;
                    fore[i].loft(0,16,5.33f,x,-.24f,.18f,.23f,5.95f,x,-.31f,.17f,.19f,6.25f,x,-.41f,.075f,.10f);
                    fore[i].oval(1,x,5.66f,-.42f,.18f,.16f,.09f);
                }
                fore[i].oval(0,s*.83f,5.11f,-.22f,.23f,.54f,.26f);''',1)
s=s.replace('                shin[i].oval(0,0,0,-.4f,1.28f,1.1f,1.10f);','''                for(int j=0;j<5;j++)for(int side:new int[]{-1,1})feather(leg[i],0,side*(.53f+j*.11f),.1f+j*.74f,-1.49f+j*.045f,-side*.27f,1.44f,.67f);
                shin[i].oval(0,0,0,-.4f,1.28f,1.1f,1.10f);
                shin[i].blade(10,0,.35f,-1.42f,0,5.7f,-1.1f,.20f);''',1)
s=s.replace('            helm.blade(0,0,-2.2f,-1.65f,0,1.65f,-3.0f,.85f);','''            helm.blade(0,0,-2.2f,-1.65f,0,1.65f,-3.0f,.85f);
            for(int side:new int[]{-1,1})for(int j=0;j<5;j++)feather(helm,0,side*(1.40f+j*.13f),-1.8f+j*.52f,.16f,side*(2.46f+j*.12f),2.55f-j*.26f,.53f);
            helm.blade(10,0,-3.2f,-1.35f,0,.75f,-2.55f,.21f);''',1)
s=s.replace('arm[i].rz=-s*.13f;','arm[i].rz=s*.055f;',1)
s=s.replace('            if(e.eclipsed()){','            for(int j=0;j<3;j++){cape[j].rx=.11f+amount*.29f+hit*.20f+(float)Math.sin(age*.11f+j*.6f)*.08f;cape[j].rz=(j-1)*.06f;}\n            if(e.eclipsed()){',1)
s=s.replace('        @Override public ResourceLocation getTextureLocation(Griffith e)','        @Override protected void scale(Griffith e,PoseStack p,float partial){p.scale(1.10f,1.15f,1.10f);}\n        @Override public ResourceLocation getTextureLocation(Griffith e)',1)
p.write_text(s,encoding='utf-8')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(201,214,231),(145,163,190),(69,58,51),(172,185,201),(244,217,195),(244,217,195),(231,232,246),(92,103,126),(28,35,50),(199,166,91),(106,130,167),(224,232,245),(181,112,108),(88,75,96)]
for m,base in enumerate(pal):
 for y in range(128):
  for x in range(128):
   u=sat2((x-3)/121);v=sat2((y-3)/121);f=abs(u-.5)
   c=shade(base,.84+.16*math.sin(u*math.pi))
   if m in (0,1,3,10):
    c=mix(c,(255,255,255),.52*math.exp(-((u-.29)/.13)**2))
    c=mix(c,(82,101,149),.40*math.exp(-((u-.78)/.13)**2))
    if v<.035 or v>.955:c=mix(c,(70,91,133),.34)
    if m==0:c=mix(c,(113,133,173),.13*math.sin(u*math.pi*6)**8)
   if m==6:
    waveval=math.sin(u*math.pi*12+v*2+math.sin(v*8)*.9)
    c=mix(c,(145,156,201),.37*max(0,-waveval)**3)
    c=mix(c,(255,255,255),.45*max(0,waveval)**2)
   if m==9:c=mix(c,(255,229,156),.48*math.sin(u*math.pi)**2)
   if m==11:c=mix(c,(117,141,195),.45*math.sin(u*math.pi*4+v*2)**8)
   if m==4:
    c=mix(base,(163,113,130),.27*sat2((f-.18)*4)+.09*v)
    c=mix(c,(255,239,224),.27*math.exp(-((u-.48)/.12)**2))
    for side in (-1,1):
     dx=side*(u-(.5+side*.173))/.119;dy=(v-(.47-.025*dx))/.043
     d=abs(dx)**1.8+abs(dy)**1.5
     if d<1.17:c=(78,66,93)
     if d<.78:c=(248,245,241)
     if d<.76 and abs(dx+.04)<.47:c=mix((66,104,160),(164,207,237),sat2((dy+.7)/1.4))
     if d<.74 and abs(dx+.04)<.17:c=(33,47,79)
     if d<.72 and (dx+.17)**2+(dy+.22)**2<.055:c=(255,255,255)
     if abs(dx)<1 and abs(v-(.382-.025*dx))<.010:c=(150,142,161)
    if f<.068 and abs(v-(.755-.012*(1-f/.068)))<.009:c=(139,80,91)
    if f<.048 and abs(v-.775)<.011:c=(224,159,148)
   q=((m//8*128+y)*W+m%8*128+x)*4;pix[q:q+4]=bytes((*c,255))
png(assets/'textures/entity/griffith_sculpted.png',W,H,pix)
print('Griffith White Falcon revision: individually sculpted armor feathers, shoulder wing, animated cape and hair, angular face and steel atlas.')


# Exaggerated black toothbrush moustache, a single broad central block split into two animated halves.
edit('MustacheRexClient.java','mustache[i]=head.child(s*.55f,-.2f,-8.1f);','mustache[i]=head.child(s*1.82f,.10f,-8.60f);')
edit('MustacheRexClient.java','mustache[i].loft(2,16,-.9f,s*.55f,0,.75f,.45f,-.45f,s*1.2f,0,1.4f,.65f,.1f,s*2.3f,.1f,1.7f,.6f,.65f,s*2.7f,.25f,1.1f,.4f,1.0f,s*3.4f,.3f,.25f,.12f);','''mustache[i].loft(2,32,-1.45f,0,0,1.85f,.72f,-1.27f,0,-.15f,2.03f,1.03f,.65f,0,-.24f,2.05f,1.05f,.97f,0,-.18f,1.86f,.80f);
    for(int k=0;k<9;k++){
     float x=-1.68f+k*.42f;
     mustache[i].loft(2,12,-1.29f,x,-.83f,.23f,.26f,-.20f,x,-1.20f,.25f,.23f,.82f,x,-.94f,.19f,.16f,1.08f,x,-.72f,.04f,.05f);
    }''')
edit('MustacheRexClient.java','mustache[i].blade(2,s*2.4f,.2f,0,s*4.8f,-.9f,.35f,1.35f);','mustache[i].blade(2,s*1.68f,-1.18f,-.76f,s*1.80f,.90f,-.88f,.40f);')
edit('MustacheRexClient.java','mustache[i].rz=(float)Math.sin(age*.19+i)*.06f;','mustache[i].rz=(float)Math.sin(age*.19)*.012f*signedSide(i);')
edit('MustacheRexClient.java',' static class M extends EntityModel<MustacheRex>{',' static int signedSide(int i){return i==0?-1:1;}\n static class M extends EntityModel<MustacheRex>{')
# Darken only the moustache material; preserve the rest of the dinosaur atlas.
p=assets/'textures/entity/mustache_rex.png';raw=p.read_bytes();off=8;compressed=b''
while off<len(raw):
 n=int.from_bytes(raw[off:off+4],'big');tag=raw[off+4:off+8];data=raw[off+8:off+8+n];off+=n+12
 if tag==b'IHDR':W,H=struct.unpack('>II',data[:8])
 if tag==b'IDAT':compressed+=data
scan=zlib.decompress(compressed);stride=W*4+1
pix=bytearray(b''.join(scan[y*stride+1:(y+1)*stride] for y in range(H)))
for y in range(128):
 for x in range(128):
  g=.5+.5*math.sin(x*.65+math.sin(y*.07)*.35)
  c=(int(12+20*g),int(10+17*g),int(9+15*g))
  q=(y*W+256+x)*4;pix[q:q+4]=bytes((*c,255))
png(p,W,H,pix)
print('Baffosauro Rex: oversized dark rectangular central toothbrush moustache with sculpted bristles.')


# Courtroom voices: use the uploaded recordings, compressed for transport, instead of synthesized speech.
import base64,subprocess
court_audio={
'miles_objection':'/+MUxAAFCAXANUAQAN9BAH/k/4gBD8pbwf8Qfl/8o78TqvJeweb/B4w0/dygRjwa/+MUxA4KulLUAYE4AP/HS4TqT//MVzF//6jdH2///RjT3Jz////7SRkv++hgzMjC/+MUxAYJYMrwAcEYAEGEYx66K4sOmLCBRQhXMsDCAwM0mmZs/+j9eipH/L6VLxrU/+MUxAMIWMr8AABGFINucwZQ9Je0SFAmfIzq4MKokO1dLdXv//2Xep3xUyrBD3iv/+MUxAQIoH70wAjGCJFAyeSwOWDCK8KQxUjBl0oXnSn3qX8vchg+n/v/RvrlI76+/+MUxAQImLb0ABhHAICpJVZzxhOxXMwRNSNZMwax6m1Wv3/uekXHf///XXVIYmQ4/+MUxAQH0AL4AAjGJGUg2Lh8obDLqk69p1ZWl/631z/DFGpfp0J/+hXm2yWcilEG/+MUxAcHmJ78AAmEgAJrv/crdFFvp1XinuoXR1nHvlLWM//9atLbJrMBADvMzyER/+MUxAsGwKdKWAhEHvJBc3t4T/CCxISGEGf/1huQSSCKSCSRVKWFxCGejbUeYw3u/+MUxBMHiAM+WAiElkVL//3oNHvZiMzIVa+8NSha4O4uQpvKnHMEBpw4IJa5Mxxb/+MUxBcG8Ab8yAgAAHZhPFep+7gsG71PY+xpkewQNxO1o0ZVUVPCz+/qfqV+hUZQ/+MUxB4G4AL4yBgAACmB0HGKJb7Vh4h1x1Ve17iru3+5j2df0XqboU1Tv0BN8PIy/+MUxCUHMAb0AAgAAHf/Pi+XgZP98v8p0AB2ekNbDP1GVdrbrLZawAxyeV2HZ9LM/+MUxCsHEU74ABBEnKFDSsMAALGXeLA5saIiZJ3llZJJNBkoVIASH1IU4s2gmEng/+MUxDEH0HNKWAlMphu5Wlv2xxF1/rd39mkMqv9tvtttQFJFDFNm0E6NNYTZbCHi/+MUxDQHyAcOMAhEALQui42YvVRufETp6ipSHpukugcMiG9se42XEJdLbwXYSoaO/+MUxDcIEHNSWBhGSlSSJlghCQblU2b9qd3+v+Bn1bttttttbZ1i2/BTQOA4uDxF/+MUxDkJyDbkAAjMCM4RDDbWxUxW7mB6AKf7P/X12oWnEFEpwZeUMzINF8dFjCdX/+MUxDQI4DdGWAjCCsDLgMVpNnTCdmmpFR9UcLdn/SqGd3d4d4H4AdjzRURnQbWw/+MUxDMImDLkAAhEBEAYcDogZ0Ej7Kfi/0ULUVeoQEVog0KErxZXijVbFWJ9TPa//+MUxDMHKAtXGBgGAv0Uf/61jBlNgQMweFCTwqkYFFBMy4XaKqZTq/6Dv+lT/1e1/+MUxDkGoArYABDGAApEqKrNYq1UrnBwZYCnQGLjbxqyz/6fUi//Y3/0VWOUcwRG/+MUxEEHmDbQABjEBEM6baxydZxZt9Ft3ZbKnbLcHIM8Z7KfqtUOEH0AkoYOIASc/+MUxEUHCFbIAAjGABPaLaIOnGEOCmUtFSSjIh+LP93//WpnGUEUKaBpdGxPsC0I/+MUxEsHYKrAAEGEOKjBFrFDFDBg4ex5IcC8Bddv0w8hOhgjFsu1RERiAjQGIOwP/+MUxFAH2Hq8ABiGoA6fMHZVbyDTTNxiM/Qq5VLNVgKaRHKWspYxP6iFsHnOIBQE/+MUxFMHuIa0AEjEpJvPISKNaye2KoqAQEOQAAAAAuULeJQGM3hGHDN4lAeiOZHz/+MUxFcHiHa4KBjENB5mttbfSdaL//L5oYn0srx40k8FfxPeKrK/wSeAgSpMQU1F/+MUxFsHoH6wAUYQADMuMTAwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxF8N4PKcNYhoAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxEoAAANIAcAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq',
'phoenix_objection':'/+MUxAAHoSoIAUEQAOMYxuf/kvI5z/yEJ////1O8hxYPg+//+sEOCYf4PvXwEAnq/+MUxAQH4W6UAYUoAAnnT8Dv/xTF//Pn/////+4cYv/44BpOf/KAOUWpDAgtrK3r/+MUxAcIiNLcAYI4AP3n/2YmYE/38geWIem4YGP5QbZ/l3uav/9DCioP/Nf/M9VL/+MUxAcIgR8AycEwAEKoj5H7GsFApUptF3u47PBhdmEIa3s84+LZSP/vtrbZsMAB/+MUxAgJgBNWXhBEAmEIiQMtGAEE3xZLkgY0/xqgrypYGmAIWlv/7//66Ptttdvt/+MUxAUIgLdOWDBEPrDnDXP0lxNwGxlN+5K0z0F7wQfXD/jFAZ6aO7vp/22t332o/+MUxAYIiGNWWDBEKvgc2DqMgSeebIACKFhMciROEyeBTRQlIUJ+rwxVoKnu16d//+MUxAYGwWcAABAFQFYOAkXp//ABif9v//JVYR5UOfRGmXeYICXN+/J1p/y+wBsp/+MUxA4HsV8AyABKGJpyERrp6aK/r/8soAm/26+pmqphEqCRbiJiVPPrnrs3i0qN/+MUxBIHuBcFkBDEAKgLc3qPf7Crf8qp/DqgRghQWgbD6xwD+9kiiv+u1V1vqWn//+MUxBYGCCbwABFGAH/MVVBU4gHjVdtL6EqWikmtKWWTHexv9Z/s/+rX7Yoqe9yR/+MUxCAHCAL0AAAAAACLCvhpyjkc59R1q7ZZdw19PXauwv/U7opz/7rkglopnvC4/+MUxCYG4Br8yAiCAKB0/SSHKjxYVcXuO1GbPn7flvHV///PDMNkSbXqcy1Q5X/U/+MUxC0HWBsJkBDGAPMZ2f/fP7f6+jgjEm22222W2iCYUVzUOInj8iLAy0HTTm2x/+MUxDIG8W8ZkDgFZbpRqq/1QqFFV4iYhnZ//xmpixoCrgDItN7xG3k1Xdbn7HLs/+MUxDkHYHNOWAjCpvulVdPttbbrgNW8QLMWojM3esUHmSQ0Z5a5SnTIkQdC8O+4/+MUxD4HUB9zGAjCArS2vloWHPPrmfmB9g+haXZb385Jq44CU+RKvhpoAA9N6AtJ/+MUxEMJOSNKWBhEu6zTLHGhzSpgXe5H7WdFDf/6UEYT5GulXSQURAAThMXWLoHF/+MUxEEK6HsBkEhGUGLLcseEbSjsOnWOhM6HaMp/Y7Z3vd/rBv62GwGjghcqwMC4/+MUxDgLAD79kgmGBB3RO5zKQNbJou5GPKtfnfelpP3/azKKAP/+ABZgJMSQOsSL/+MUxC8ImCcBiAjEAKTuS4OC0c7Y2/SainPM/7fe7rqO7bDXW4WVEMYgIQOD57bi/+MUxC8HoAcBkADEAK3UOQmHuz0Pxoq69v/XqrDLAmWNiCbrFZb0p0CFhBye8KnZ/+MUxDMHsB9CWAhEAgC4CEMqcYkv+6FSv/9Nb43/+utwglERczU5klkQdDiqzqG+/+MUxDcIaDrkAEJEAJBG/U41+v+hPgGEEAPioayshjaB4vpJl7oDtNNZb6MLLrzy/+MUxDgHMA8+WBDEAgLHJJyf2bLf/1KQDpS8fU6j0Z2Rru/oeF/SpBnuXtFnqPDZ/+MUxD4JKOLYykhEPNfLFWIHN/I5ljklMIJSxkIZY8WtSCm28io5TOYL/EUkRTvw/+MUxDwIuRbQAGCGPe577plDGDpKutXBTHEvoRIZkFl3jcqnteIfQT2LQKaA7gkr/+MUxDwIkQ7IyHhEXJ95a9zNbujI4GYxnHUFLQgyxvuRgHNytymA0iK+CupFB2rD/+MUxDwIAIK8AHiGLA9/2I5/mWORWrUVrdub/ebe966XG//r3uFFhnavxTVqEGgk/+MUxD8HuIKwAHjMTJAAVlJVMJtp7ysaun1x/7sbxq/4BYQg8coC1wAADaExETL9/+MUxEMHQIKwAU8QAKzr/5OPiVnPsn/Jzhkh/rGf/VVCDBgMCAQAAAAKJ8y+Uvob/+MUxEkOGSacy5hQAP0DF/wEBR1/8xgxSt//lMYy//5UUoCYGv/BkFRETEFNRTMu/+MUxDMLOY5wX4IQAjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxCkAAANIAcAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq'}
for name,encoded in court_audio.items():
 tmp=root/(name+'_recording.mp3')
 tmp.write_bytes(base64.b64decode(encoded,validate=True))
 subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(tmp),'-ac','1','-c:a','libvorbis','-q:a','4',str(assets/'sounds'/f'{name}.ogg')],check=True)
 tmp.unlink()
edit('CrossoverGuest.java','void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}','''void say(ServerLevel l,String s){
        var msg=Component.literal(getDisplayName().getString()+": "+s);
        if(kind()==1)msg.withStyle(net.minecraft.ChatFormatting.BLUE);
        else if(kind()==2)msg.withStyle(net.minecraft.ChatFormatting.RED);
        NpcDialogue.say(l,msg);
    }''')
print('Uploaded English Objection recordings and distinct blue/red courtroom dialogue.')


# Client-side facial expressions and smooth, varied idle poses for Waifu and Slime Lady.
write('AdmirerExpressions.java','''package it.noctis.magic;
public final class AdmirerExpressions{
 private static int cycle(Admirer e){return Math.floorMod(e.tickCount+e.getId()*47,240);}
 public static int pose(Admirer e){return Math.floorMod(Math.floorDiv(e.tickCount+e.getId()*47,240),5)+1;}
 public static float blend(Admirer e,float amount){
  if(e.isInSittingPose()||e.hurtTime>0||amount>.09f)return 0;
  int t=cycle(e);if(t>90)return 0;
  float f=Math.min(1f,Math.min(t/12f,(90-t)/12f));return f*f*(3-2*f);
 }
 public static int expression(Admirer e){
  if(e.hurtTime>0)return 4;
  if(e.isInSittingPose())return 1;
  if(cycle(e)<90&&e.getDeltaMovement().horizontalDistanceSqr()<.003){return switch(pose(e)){case 1,4->1;case 2->3;case 3->2;default->0;};}
  return Math.floorMod(e.tickCount+e.getId()*13,97)<3?4:0;
 }
}''')
p=java/'WaifuTailoredClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('import it.noctis.magic.SculptedGuestsClient.Part;','import it.noctis.magic.SculptedGuestsClient.Part;\nimport it.noctis.magic.SculptedGuestsClient.V;\nimport it.noctis.magic.SculptedGuestsClient.Q;',1)
s=s.replace(' static class M extends EntityModel<Admirer>{',''' static V facial(V v,boolean f){return new V(v.x(),v.y(),v.z(),f?Math.max(.025f,Math.min(.975f,.5f+v.x()/6.75f)):.025f,Math.max(.025f,Math.min(.975f,(v.y()+7.4f)/7.4f)),v.nx(),v.ny(),v.nz());}
 static void face(Part p){for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=5)continue;boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;p.faces.set(i,new Q(facial(q.a(),f),facial(q.b(),f),facial(q.c(),f),facial(q.d(),f),5));}}
 static class M extends EntityModel<Admirer>{''',1)
s=s.replace('   head.loft(6,24,-8.65f','   face(head);\n   head.loft(6,24,-8.65f',1)
a=s.index('   boolean sit=e.isInSittingPose();',s.index('public void setupAnim'))
b=s.index('\n  }',a)
s=s[:a]+'''   boolean sit=e.isInSittingPose();float f=AdmirerExpressions.blend(e,amount),breath=(float)Math.sin(age*.12f);
   int pose=AdmirerExpressions.pose(e);
   body.rz=(float)Math.sin(limb*.7f)*amount*.035f;body.rx=sit?-.06f:0;body.ry=0;
   head.ry=yaw*.01745f;head.rx=pitch*.015f;head.rz=0;
   for(int i=0;i<2;i++){int side=i==0?-1:1;float step=(float)Math.cos(limb*.666f+i*Math.PI)*amount;
    arms[i].rx=-step*.52f;arms[i].rz=side*.10f;arms[i].ry=0;fore[i].rx=-.10f-Math.max(0,step)*.28f;fore[i].rz=0;fore[i].ry=0;
    legs[i].rx=sit?-1.35f:step*.61f;legs[i].rz=0;knees[i].rx=sit?.12f:Math.max(0,-step)*.34f;
    locks[i].rx=amount*.15f+breath*.035f;ribbons[i].rx=amount*.30f+(float)Math.sin(age*.12f+i)*.06f;
   }
   if(f>0){
    if(pose==1){arms[1].rx=-.9f*f;arms[1].rz=.55f*f;fore[1].rx=-1.45f*f;fore[1].rz=(float)Math.sin(age*.38f)*.35f*f;head.rz=.10f*f;}
    if(pose==2){for(int i=0;i<2;i++){int side=i==0?-1:1;arms[i].rz=side*.55f*f;fore[i].rz=-side*.95f*f;fore[i].rx=-.32f*f;}body.ry=.12f*f;head.rz=-.07f*f;}
    if(pose==3){arms[0].rx=-.64f*f;fore[0].rx=-1.78f*f;arms[0].rz=-.32f*f;head.rz=-.19f*f;head.rx+=.10f*f;}
    if(pose==4){arms[0].rz=-1.75f*f;arms[1].rz=1.75f*f;fore[0].rx=-.31f*f;fore[1].rx=-.31f*f;body.rx=-.08f*f;}
    if(pose==5){arms[0].rx=-.66f*f;arms[1].rx=-.66f*f;fore[0].rx=-1.23f*f;fore[1].rx=-1.23f*f;fore[0].rz=.30f*f;fore[1].rz=-.30f*f;head.rz=.13f*f;}
   }
   if(e.hurtTime>0){head.rx-=.15f;body.rx=.13f;arms[0].rx=-.40f;arms[1].rx=-.40f;}
'''+s[b:]
s=s.replace('return new ResourceLocation(Noctis.ID,"textures/entity/waifu_tailored.png");','return new ResourceLocation(Noctis.ID,"textures/entity/waifu_expression_"+AdmirerExpressions.expression(e)+".png");',1)
p.write_text(s,encoding='utf-8')
# Slime retains all twelve flowing-water frames and gains facial variants and five gestures.
p=java/'SlimeLadyModel.java';s=p.read_text(encoding='utf-8')
a='        for(int i=0;i<12;i++){ModelPart p=skirt.getChild("pleat"+i);'
assert a in s
s=s.replace(a,'''        float f=AdmirerExpressions.blend(e,amount);int pose=AdmirerExpressions.pose(e);head.zRot=0;body.yRot=0;
        for(int i=0;i<2;i++){arms[i].yRot=0;arms[i].getChild("hand").xRot=0;arms[i].getChild("hand").zRot=0;legs[i].zRot=0;}
        if(f>0){
          if(pose==1){arms[1].xRot=-1.45f*f;arms[1].zRot=-.65f*f;arms[1].getChild("hand").zRot=(float)Math.sin(age*.35f)*.42f*f;head.zRot=.13f*f;}
          if(pose==2){arms[0].zRot=.38f*f;arms[1].zRot=-.38f*f;arms[0].xRot=-.35f*f;arms[1].xRot=-.35f*f;body.yRot=.15f*f;}
          if(pose==3){arms[0].xRot=-1.15f*f;arms[0].zRot=.35f*f;head.zRot=-.17f*f;head.xRot+=.12f*f;}
          if(pose==4){arms[0].zRot=1.7f*f;arms[1].zRot=-1.7f*f;head.yScale+=.04f*f;body.xRot=-.08f*f;}
          if(pose==5){arms[0].xRot=-1.0f*f;arms[1].xRot=-1.0f*f;arms[0].yRot=.22f*f;arms[1].yRot=-.22f*f;head.zRot=.12f*f;}
        }
        if(e.hurtTime>0){head.xRot-=.15f;body.xRot=.14f;}
'''+a,1)
s=s.replace('return FRAMES[(e.tickCount/3)%FRAMES.length];','return new ResourceLocation(Noctis.ID,"textures/entity/slime_expression_"+AdmirerExpressions.expression(e)+"_"+(e.tickCount/3%12)+".png");',1)
p.write_text(s,encoding='utf-8')
def read_rgba(p):
 raw=p.read_bytes();i=8;compressed=b''
 while i<len(raw):
  n=int.from_bytes(raw[i:i+4],'big');tag=raw[i+4:i+8];data=raw[i+8:i+8+n];i+=n+12
  if tag==b'IHDR':w,h=struct.unpack('>II',data[:8])
  if tag==b'IDAT':compressed+=data
 scan=zlib.decompress(compressed);stride=w*4+1
 assert all(scan[y*stride]==0 for y in range(h)),p
 return w,h,bytearray(b''.join(scan[y*stride+1:(y+1)*stride] for y in range(h)))
def expression_color(u,v,kind,slime,frame=0):
 base=(43,188,212) if slime else (235,190,165)
 shadow=(12,111,155) if slime else (171,95,100)
 c=mix(base,shadow,.14*abs(u-.5)*2+.08*v)
 if slime:c=mix(c,(75,222,235),.11*(1+math.sin(u*10+v*8-frame*math.pi/6)))
 ink=(19,49,65) if slime else (62,30,48)
 eyes=[.72] if slime else [.33,.67]
 for ex in eyes:
  dx=(u-ex)/(.20 if slime else .125);ey=.43 if slime else .49
  dy=(v-ey)/(.18 if slime else .077)
  if kind==4 or kind==1:
   if abs(dx)<1 and abs(dy-(.45 if kind==4 else -.30)*(1-dx*dx))<.13:c=ink
  else:
   if kind==2:dy*=.75
   if kind==3:dy=(dy+.40*dx*(1 if ex>.5 else -1))*1.4
   d=dx*dx+dy*dy
   if d<1.04:c=ink
   if d<.79:c=(247,247,235)
   if d<.76 and abs(dx+.04)<.46:c=(218,158,35) if slime else (157,68,173)
   if d<.72 and abs(dx+.04)<.18:c=ink
   if d<.7 and (dx+.18)**2+(dy+.23)**2<.06:c=(255,255,250)
  if kind==3 and abs(dx)<.92 and abs(v-(ey-.12+dx*.055*(1 if ex>.5 else -1)))<.012:c=ink
 center=.59 if slime else .5;mx=u-center;my=v-(.75 if slime else .79)
 if kind==2:
  if (mx/.058)**2+(my/.071)**2<1:c=ink
 elif kind==1:
  if abs(mx)<.10 and abs(my-.028*(1-(mx/.10)**2))<.012:c=ink
 elif kind==3:
  if abs(mx)<.07 and abs(my+.018*(1-(mx/.07)**2))<.012:c=ink
 elif kind==4:
  if abs(mx)<.075 and abs(my+.014*(1-(mx/.075)**2))<.015:c=ink
 elif abs(mx)<.06 and abs(my)<.010:c=ink
 return c
w,h,base=read_rgba(assets/'textures/entity/waifu_tailored.png')
for kind in range(5):
 pix=bytearray(base)
 for y in range(128):
  for x in range(128):
   u=max(0,min(1,(x-3)/121));v=max(0,min(1,(y-3)/121))
   c=expression_color(u,v,kind,False);off=(y*w+5*128+x)*4;pix[off:off+4]=bytes((*c,255))
 png(assets/'textures/entity'/f'waifu_expression_{kind}.png',w,h,pix)
# Locate the actual front face UV island from the generated model rather than guessing.
m=re.search(r'PartDefinition h=r\.addOrReplaceChild\("head",CubeListBuilder\.create\(\)\.texOffs\((\d+),(\d+)\)',s)
assert m,'slime head UV not found'
sx,sy=(int(m.group(1))+6)*3,(int(m.group(2))+6)*3
for frame in range(12):
 w,h,base=read_rgba(assets/'textures/entity'/f'slime_flow_{frame}.png')
 for kind in range(5):
  pix=bytearray(base)
  for y in range(21):
   for x in range(24):
    c=expression_color((x+.5)/24,(y+.5)/21,kind,True,frame);off=((sy+y)*w+sx+x)*4;pix[off:off+4]=bytes((*c,255))
  png(assets/'textures/entity'/f'slime_expression_{kind}_{frame}.png',w,h,pix)
print('Waifu and Slime Girl: five facial states, five smooth idle gestures, preserved gel-flow animation.')


# Guts: actual uploaded scream (mono compressed copy), huge Dragon Slayer and devastating melee.
edit('FallenEncounter.java','static final RegistryObject<SoundEvent> PHOENIX_OBJECTION=','''static final RegistryObject<SoundEvent> GUTS_GRIFFITH=SOUNDS.register("guts_griffith",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"guts_griffith")));
    static final RegistryObject<SoundEvent> PHOENIX_OBJECTION=''')
edit('Guts.java','playSound(SoundEvents.RAVAGER_ROAR,1.5f,.72f);','playSound(FallenEncounter.GUTS_GRIFFITH.get(),2.0f,1f);')
edit('Guts.java','Attributes.ATTACK_DAMAGE,44','Attributes.ATTACK_DAMAGE,140')
edit('Guts.java','e.getBoundingBox().inflate(2),m->m!=e&&enemy(m)&&distanceToSqr(m)<25','e.getBoundingBox().inflate(4),m->m!=e&&enemy(m)&&distanceToSqr(m)<64')
edit('Guts.java','other.hurt(damageSources().mobAttack(this),18);','other.hurt(damageSources().mobAttack(this),85);')
edit('Noctis.java','net.minecraft.world.item.Tiers.NETHERITE,24,-3.45f','net.minecraft.world.item.Tiers.NETHERITE,95,-3.45f')
# New sword shape: 50 model units from hilt, wide angular blade and stepped bevels.
edit('GutsSculptedClient.java','sword.loft(8,8,2.1f,0,0,3.25f,.50f,5.0f,0,0,3.92f,.62f,30.0f,0,0,3.92f,.62f,34.0f,0,0,.08f,.12f);','''sword.loft(8,8,2.1f,0,0,4.4f,.7f,6.0f,0,0,5.1f,.87f,43.0f,0,0,5.1f,.87f,50.0f,0,0,.08f,.12f);
   for(int side:new int[]{-1,1}){
    sword.blade(8,side*4.55f,6.2f,-.20f,side*4.55f,43.0f,-.20f,.52f);
    sword.blade(4,side*4.65f,6.2f,.20f,side*4.65f,43.0f,.20f,.28f);
    sword.blade(9,side*3.12f,7.0f,-.85f,side*3.12f,41.5f,-.85f,.12f);
   }''')
edit('GutsSculptedClient.java','sword.loft(9,8,2.3f,0,-.49f,2.62f,.13f,30.0f,0,-.52f,3.05f,.14f,33.6f,0,-.07f,.07f,.06f);','sword.loft(9,8,2.3f,0,-.70f,3.30f,.17f,43.0f,0,-.77f,3.90f,.16f,49.4f,0,-.07f,.07f,.06f);')
edit('GutsSculptedClient.java','sword.loft(9,8,2.3f,0,.49f,2.62f,.13f,30.0f,0,.52f,3.05f,.14f,33.6f,0,.07f,.07f,.06f);','sword.loft(9,8,2.3f,0,.70f,3.30f,.17f,43.0f,0,.77f,3.90f,.16f,49.4f,0,.07f,.07f,.06f);')
# Large item artwork, with heavy dark core, bright worn steel bevels and wrapped handle.
W=H=128;pix=bytearray(W*H*4)
for y in range(H):
 for x in range(W):
  t=(x+127-y)/2;d=x+y-127;c=None
  half=12.5 if t<112 else max(0,(123-t)*1.14)
  if 25<t<123 and abs(d)<half:
   edge=abs(d)>max(0,half-3.3)
   c=shade((179,188,201) if edge else (72,77,85),.84+.12*math.sin(t*.21)**2+.09*math.sin(d*.7)**2)
   if abs(math.sin(t*1.73+d*.49)*math.cos(d*1.11))>.93:c=mix(c,(209,218,225),.36)
  if 20<t<28 and abs(d)<14:c=shade((109,112,117),.65+.35*math.sin(t*.49)**2)
  if 6<t<22 and abs(d)<3.5:c=shade((157,145,126),.56+.44*math.sin(t*1.85)**2)
  if 2<t<8 and abs(d)<5:c=(119,118,110)
  if c:
   q=(y*W+x)*4;pix[q:q+4]=bytes((*c,255))
png(assets/'textures/item/dragon_slayer.png',W,H,pix)
p=assets/'models/item/dragon_slayer.json';d=json.loads(p.read_text(encoding='utf-8'))
for hand,angle in [('righthand',55),('lefthand',-55)]:
 d['display']['thirdperson_'+hand]={'rotation':[0,-90 if angle>0 else 90,angle],'translation':[0,5,0],'scale':[3.4,3.4,3.4]}
 d['display']['firstperson_'+hand]={'rotation':[0,-90 if angle>0 else 90,angle*.45],'translation':[1.1 if angle>0 else -1.1,1.5,0],'scale':[1.7,1.7,1.7]}
write_noctis_json_resource(p,d)
import base64,subprocess
encoded='/+MUxAAAAANIAAAAAExBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVMQU1FMy4xMDBV/+MUxCMAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy4xMDBV/+MUxEYAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUz8x3MnC6uTLz7/+MUxGkAAANIAAAAAA+MkKIyPj4kJ2J5uTnn//jr3TgdoS0/OFx4Sx4II5BSG4GA/+MUxIwAAANIAAAAAKD+q5aqUmw+D4W1l6Xye6+batnUaty4G5VZFnQjZCHoRvO//+MUxK8AAANIAAAAAP0JPqACDn/IUBwDFg4KHB4CPBAq///UoaOd5QpxBMSg18py/+MUxNIAAANIAAAAAGgH8oCGJwGOLg+f/30FyFUgfod//m4gic+J/gg/pUCDpLsh/+MUxNwAAANIAAAAAIo8Rh+5ResGMOO3yIyl/59MtXpJPoOPdCroFFpkHCTDEThg/+MUxNwAAANIAAAAAC2ohc9SrUryHeqlb6WN/+s/KGehs44CYxzjGMpitrqtT+Vt/+MUxNwAAANIAAAAANSgCKiqOw+MFX/QWv/y75wwEBDu5e5U//yl+VtNUL15iof0/+MUxP8RsZlcMAJYmUvVtSq378kUXVWWlSskn1KxgzJ5fsn9vau+QMOiCV89Hvxj/+MUxNsHCSH0ABALJeloaadfb9Pb9u3V3z/PH43lBgXgMFYIAHujOZerkn0cnkno/+MUxOEHiAIcAABElKBmEK+EYCJuQsoHYB1XI7E/xPcWf/6IgBQMz6naw+z8f1iG/+MUxOUF8KpQAABHAJMBbkH6m9EGeCcP+O2m6nDqEwQaseVm3mr/IKtkZYAA4gt8/+MUxPAJKXpYAACHDMtispV4vuRAKIQA/yD+JxxwwFYuZgs+i/N5g/Q2Dw5eJK57/+MUxO4J8fJUAACLFOU8Kc+AhAiXirCaeQq2FcoDS2eJWBijTHomAyOT2x9z58OC/+MUxOkIGfJMAAgEjGi6U3PKz/2srSgGdZOt9djFFwvNhwz33RJ//X60WqFPYWJz/+MUxOsG8Xo4AACHEFQ/W50uKiiFMqE5/DD/96CBiYMkNR8JJ126bkeolwfFqZP//+MUxPIKKgZMAAHFFKHiMNAUm9+6uxMAJu8EoDMRjCuBMRkDYJwcKX71vl2fa0kT/+MUxOwI+LaIAAMGZD/uuVs9TWzi3PLVWutS2l1sotAHSGJlp94450ABsp+42Jh+/+MUxOsJeNqsyAPSaOawb0u//97Vqo+iAA9kKdMWAD0/mjiwn9EhnDAR2M3CNQwE/+MUxOgJQN6wKAMMdCr7HsepZrKUY794x4IBEgI0sNwaVLPPf4iWCxUEhERhrBkw/+MUxOYImOq8AAIMYEQo+kC0DEYP/uJOdA4BCgQqziEed64gIoKYEq0/c9sEihna/+MUxOYIOP7MAADEcCJ+ZSSr3uX5oUWxp2f2fB30OdYkZf9bFlqikg97w47YrIlL/+MUxOgH+SrUAAgFJP1/SbTCdgcjjeS9tXQlDoSp0J/ysNDQ4VTlf8p1GBB+GOcE/+MUxOsJuH7hlABSiG99PRAEzLwu+tK3vBERCcayoE3f91HYuaZvoTXIRv/3CI7K/+MUxOcH8IcofgJEokCfxIABIJQYQSUWuit37P/YTy6sgQ6GB5/07ALKCISnfrkl/+MUxOoPYSrSVgGGaMKsw+X//nv9zUDVDXpqEYKkUAJv0P4IyjMAlkHB10aTBwQ3/+MUxM8OMdqQUgFGrYuxHxAhDoY/q0V10QLCbYD/601dreora9Osa5HyEYILsJ+T/+MUxLkKwTa0UAPKrOl3/LFntCyV1gMuRo7SWCmXFh0QjSqioJnljMuIh7tVL05L/+MUxLEHWJbUAACQqOz7HD9a9YAuiBzyhePtWCbZB0mokg+6LRjXe4wpllP/sTvq/+MUxLYGeKrcAABGqLaBSHUM2WWX/3hwJWmQ9Cs4JWSWacQTR///WmvJgARyD62z/+MUxL8HUPbkYgFEpOVAaRY0hA3POzpbU8vOOovZixJ/8vqT8CHIv/k+dqDqJcZ7/+MUxMQH2KrscADEwA+h1B1vGBpSH/Xyin0xyU1qiGQ5YLQAOGHIMPJ2IBDXCqSN/+MUxMcH4SLocAFGtC29iMDZH/679yHjq9oTX2Af5qMN4zmhP1Quj3tfV/1qzeqh/+MUxMoH6GbsaABMoAFwUKkgaJGb/+vVTI3V/YBId+wQk7m6PJlUMDwJBEHToVBa/+MUxM0HUGLoaAAOELeI2JeNNoQy067//9jEqtYklGMA/gHpdb1onRkTdlDK/+jq/+MUxNIHAKrsagCGpI38yh2PYiSN6Gf/7BlNKQKIBBP6dBJjy1woxBZArg66sSAU/+MUxNkHeMrocABGrGEsYOfypu3L87GDWDhI8oqattyCAAcA8yLlz2RvJtDWGcHm/+MUxN4HGL7kSABGqK1n1mPC30r//EsyKxwAbhhh1MtfwRUkedDtnMC5r5Xn67Tg/+MUxOQHgGMwngCMohp4ITfXu0t/WmZOm7zaVTsQTUJhjrmEdm0td6iJq8Yaq6Y7/+MUxOkJGSMIdAJEpuZwclHlD1gBe2//yIiVdh+p7Z833ToA4AF1soawjnVOS0G5/+MUxOcIyJroagGEpBGk603TnvkX1/+W/vNSTvrVdhGgKmTV9GRHIR6inf2MyuDu/+MUxOYIaSMMfAIEpq6ZBP5lbYMAF0+j/TllLV6SGHwaFQnQaLbforqK/UhawhrW/+MUxOcJGL7gUgAKTLjemX3L7///95C6/owluEU9kfHEFY+t0/Lk/ATVX/Z6Gf29/+MUxOUHuF8YfgBMoissF4d3BNzWiVP/9joOIUrKAYhgv39TprQfR6g2ogUEr3NC/+MUxOkJUQ7caACMsBXUUS4lFXaavb/qNdkAOAJQKsYlXfzlRkaUGBVSh9j6/2yN/+MUxOYJgQrcaAFMtORVENJj2IMCh0D0/K8mvcevVMqSkYBYAxXsno962MGCxACk/+MUxOMIUHMMdgCQog4G3pMEa+sVeGEP/P1efatkn120AQnFbUT+0k10hJaDQKS2/+MUxOQIMTbgYAFEoAGE5r5RkSLR/Z+j9y6ViDAKEgAwJzrnG/ndOaE4R50EAWHB/+MUxOYI8ebkagDEqNYKJkkJuDhAwz5C///6FQAB/o4444ABlhGBOtNfJIQYHjoi/+MUxOUImOrgYADMrAaCg11wmR47kTDuWTNRX7Nn6ATykFf9jpYVQR2UsqXORhQT/+MUxOUHuK7oUgCGqA39QlouYJRQW7lxFkfxVyohP/+kSJu8pxJwWDoGDQ9a1HYl/+MUxOkKuPrcbAHMrEtVrw63+71pXeqTTQBh//g+7wgblvJ2A0dYflw55er+SWwx/+MUxOEIaKbobAAEEGXbEIXqHFCp3iO1qv9N+RK4AKhgMbMM1ww4VIvLAylQSA1T/+MUxOIHYMrkYgCGqNQZ76RF1ffUVSMrBiGD/8XhwnUg6YNl1UkoJB5Cx89PNyuR/+MUxOcI0K7olAGGoJkORBb514SVQjyhdfYOACo8C/5qBiWRTCsqyU1JowaD9Xz+/+MUxOYJgI8aXgIEghepbv60NWvd7/OWMDq9FRIh9S1MJnKFlKMR5oohCZtiKAom/+MUxOMICM7IyACGiMJOvcv8Ee6z0U3pVrAml7IsAEckkoAACL3wb9ffcQbqFDWi/+MUxOUHQKqkAABEgIlovcBhwEualA1WhSOKL6wwJu1WuX/loyLJBJXENtrDcF0S/+MUxOsJqUKgNABGqF+XRkhpAbIq68uLVgsrKoWqms1/5vOf9Iaiq/4dQfOXVvY3/+MUxOcIAM6QAABG4Em7gKcEMgJRbdbpzdO3LfhQCqjVEqrmzLzzgEmRRxkh0NQ1/+MUxOoJyTqQEgBGqDxY6HRE89uqPSLeVR+RIX/xj/7xErDaaFIiD5IfJVq1mVwe/+MUxOUIWT6UCgBGxISygePUfgVgCu4q6LJMQU1FMy4xMDCqqgpMQU1FMy4xMDCq/+MUxOYJOTaMKgFG6Kqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxOQJQOrEfgCHAqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxOIIYQqEEABGqKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxOMH+N5oAABYqKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxOYIgOJMAACM4Kqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxOcIaN3cAAgSFKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MUxN0AQAQAADAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq'
tmp=root/'guts_griffith_recording.mp3';tmp.write_bytes(base64.b64decode(encoded,validate=True))
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(tmp),'-ac','1','-c:a','libvorbis','-q:a','4',str(assets/'sounds/guts_griffith.ogg')],check=True)
tmp.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['guts_griffith']={'sounds':[{'name':'noctismagic:guts_griffith'}]};write_noctis_json_resource(p,d)
print('Guts uploaded Griffith scream, 140 melee and 85 splash damage, enormous Dragon Slayer with worn steel bevels.')


# Shared uploaded Waifu voice on interaction.
edit('FallenEncounter.java','static final RegistryObject<SoundEvent> PHOENIX_OBJECTION=','''static final RegistryObject<SoundEvent> WAIFU_VOICE=SOUNDS.register("waifu_voice",()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,"waifu_voice")));
    static final RegistryObject<SoundEvent> PHOENIX_OBJECTION=''')
write('AdmirerVoice.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class AdmirerVoice{
 @SubscribeEvent public static void interact(PlayerInteractEvent.EntityInteract e){
  if(e.getHand()!=InteractionHand.MAIN_HAND||!(e.getTarget().level() instanceof ServerLevel l))return;
  var m=e.getTarget();var key=ForgeRegistries.ENTITY_TYPES.getKey(m.getType());
  if(key==null||!key.getNamespace().equals(Noctis.ID))return;
  String path=key.getPath();
  if(m.getType()!=Noctis.WAIFU.get()&&m.getType()!=Noctis.SLIME_LADY.get()&&!path.contains("ogre")&&!path.contains("ogress"))return;
  var tag=m.getPersistentData();if(tag.getLong("NoctisVoiceUntil")>l.getGameTime())return;
  tag.putLong("NoctisVoiceUntil",l.getGameTime()+60);
  l.playSound(null,m.getX(),m.getY(),m.getZ(),FallenEncounter.WAIFU_VOICE.get(),net.minecraft.sounds.SoundSource.NEUTRAL,1f,1f);
 }
}''')
import base64,subprocess
voice_b64='/+MYxAAHeAFcMAhEKCMh////mjNaDbv/36TD9Pm3RU0ZFRVBt38w8WaZNDP///9lJkVmRoqgBiv//v/////oNC01/wNouA0Q/+MYxB0FuAG4AUEYAOCzBS/zEn3b9S01k2T/5IY3HghIhAowa///FsoSIPBYQVP//8Qg3GAsBeGSMfk///7P557i2C+DWAmR/+MYxEEYM45gAZRQADACAKg0///1OJPuVJzy6iwMRuPy5g0P//////MPxYch5L/kgXZKawbcbN/6f/3/9Eb6bfOx1ed6Ieh9/+MYxBsUApbIyYooAL/Sv9ET/8joyBxkq61B1EhEauiPGiA4SYjRwm7k/MsLYNnDki8HhEJhQY3n/vBCl/UHBUIr33/+2+jE/+MYxAYOWUcWWccQAgDBh+TMXVkpREHirMg6iOdmoeOEe+1kc775ade309HEjRFHBQFr/u/rGPsXv/+7///i3eqXDaDRo8gA/+MYxAcO0BbKeGBEAHKy0VUvDpJT/C/WEA2PFmT9YeE4EJhFosJhYLkbFMARFAUCroHMeu7XnoVrlmqZUpino2KqgFotcttY/+MYxAYOiN8SWBAMghX//yf8jR/GYfZhwKP1P6eTzh93rB96RA6IHKOcgXP8P8ufhiq85f5Ph9YP/B8Tg45uX4pVgz4/UBDf/+MYxAYNGYLpkBBGPP//P/3w81kyMVPLr4UdhQ1CVHvTDtCqDOcADCFLk0ijf8v7QwNeEAwh0+8tVd3qgggL+5VQGCWRvlIV/+MYxAwMUk7cyBAEEAy+///oZlorOiuVvltoZe/9dWdCjnQKBAJi0JfKjhQYwYGmleRqgA1becacCYv/f5n+qKeYIMKIAQNC/+MYxBULuYcOWDgUCjJ6//tr/v//VDS4YBD//6S0yAP///gMQZc/Z5mXznF4AFSBsf/xIRiAHh4obTKJwUDssWcwb1PK3/8//+MYxCEMINMq+UgQAvKioqaZYd8DU9f+JTq3frViAD/z/8fASB10Dznc7rf///+yUj4LwjygOAXkRASGH/ITbf/61/0MYWyA/+MYxCsXa4bhkYdQAP9RbNVvtf81Fb6df5QX/ssnMbNUuegzUaj4LonKtICZaUnuQTRWt//80fk7LT/1Atc7Qnve13Vf/////+MYxAgOs1rgKYFQAGAcC084QpAPnoK3+f9W//83+v/N//+n//+n/mp52n+9f/VCFioBzVWjr/nKyD04tkXorggaW+2wfgFP/+MYxAgPKr7QyYIQAO/////1YGyIn//EHQdn////r9///JOc4hqnc7scqugF//vkIQ7+jFCiRgSICI8EiDf7/69FN53DD////+MYxAYOClbYAYc4AP/1Hwf6KNQW1PEghEcJSP/9v/88fL/oaab7fJmHGm/1///xLJvxwwPGu1T+s/L9/f/LKl/X////mGjp/+MYxAgO4s7sAYE4AKyN81//X+J/6uzm/k2/xoQM/+rux3z0/9Tl/7uYYcYf/HAoJh43b85BGGocHznT/Lf9Qnq7YATCQIAR/+MYxAcNAPMiWcd4AgWj71fdKMfPPoOEFP///0NNOQbhICYIh5aoyPBboLCzv75HEQVcFXFm////mLt/pJRaAEE3Rr4+f8Zg/+MYxA4MCHsWWU8IAkh3s0dtbEAXK6dJqdmx8GQiHGKhwCgMCo4cEYkf93//7fXVXhqY9tKCfX3Vn/1PWyq7r1yeI2VWX9Jv/+MYxBgSMtrMAYVoAMsNP///6vTTNzxsvr/1Nb/SNkug1B0NdDf/rTZPbxJAPQL4NpJMkZOeM7f//A4fUGnAfhkaHEv///2f/+MYxAoMGXs+YcJ4A//9S/y1La1t11jOc02sM5fC2h1nYQtHyx4jI5s+7bh1xinxq+Jh6nAKoBhf/R1///5CF+nQBA4T//6//+MYxBQLiate+AgKhu8t/u3sciHEgIUPn//9VDkhEgHgf////DAOVXiIh+hXAgDoNDh9yPVmEkDCQonLpNAMgZp5lTIpyIAU/+MYxCAMoLcy+EjGKstCoK/6PZ4oLEh4CAUq7///4dXf/77Z0BgDVoLItBYLURaJ3reyqXPqGW2U26gENiNKKuJq1teuMrMK/+MYxCgM0NMiWEjSFkfqd/9f////+tP6FVJJGpJICAHm7QOXdYKMVZs8DLBVLIcPCpdz2WN3UEouPSEwSaW/k//////9bqtS/+MYxC8LqAr2WChEAlZ4ePt+MAxdpa7wy7Sd9Hj4y0S8fsZhbHU1VB0RNFnW73jlITOLGin/62P//////7dNTkkkkkYIUWpC/+MYxDsMaJMa+EhGAtiiRoc0oIxI/Poah5IwhZGysOC71XngDQssBtL22/X9FYnP////+CpG2lWC2i2y2MAIiHzP9by9I//P/+MYxEQM0ArmWBiEAsC+VGDkv+SeRqEa5BDPE+Tf/2v5mfRvLvTykvhjSpbaLbaGAzP/ou399///Wi+X/30QrTWAxQVBmqAq/+MYxEsLaVMCWDBEHhfYWTSYoY////2MNBQkYe9dAd/JwB74PtCZBm8+yG6qzSjHsk5KmL/9FU9g+geQxWZC2a7JNYQVRyo2/+MYxFgLaVMSUUIYAsr7+a3t6aDjkFxAMFvcTHTQMTRFVUSOMIlAUPOgjM3gEZ2IWm/KguqkT13KKlNzv62rQAF2k4WCsse//+MYxGUXAvrAyYcoAP////BoOFg74Kgq7+DR5QdWCrxKGuoGj3EobWCri3Bo8oOrBU9+oGkQsLCwsKiorV/FRQWFjUFhYWFh/+MYxEQMMAKpGcEQAHFRX/+LCwuKs/////xYXFRUVFfxUVFfiwsqTEFNRTMuMTAwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq/+MYxE4LCAU0AAgAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq'
tmp=root/'waifu_recording.mp3';tmp.write_bytes(base64.b64decode(voice_b64,validate=True))
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(tmp),'-ac','1','-c:a','libvorbis','-q:a','4',str(assets/'sounds/waifu_voice.ogg')],check=True)
tmp.unlink()
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'));d['waifu_voice']={'sounds':[{'name':'noctismagic:waifu_voice'}]};write_noctis_json_resource(p,d)
print('Shared uploaded Waifu voice on interaction, with three-second cooldown.')


# Central spawn density guard. Existing saved mobs are never deleted or blocked from loading.
write('CharacterSpawnLimit.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class CharacterSpawnLimit{
 private static final int CHUNK_RADIUS=2;
 private static final String CHECKED="NoctisSpawnLimitAccepted";
 @SubscribeEvent(priority=EventPriority.LOWEST)
 public static void join(EntityJoinLevelEvent event){
  if(!(event.getLevel() instanceof ServerLevel level)||!(event.getEntity() instanceof Mob incoming))return;
  var key=ForgeRegistries.ENTITY_TYPES.getKey(incoming.getType());
  if(key==null||!Noctis.ID.equals(key.getNamespace()))return;
  // Never delete old mobs, prevent chunk reloads or break dimension travel.
  if(event.loadedFromDisk()||incoming.getPersistentData().getBoolean(CHECKED)){
   incoming.getPersistentData().putBoolean(CHECKED,true);return;
  }
  ChunkPos c=new ChunkPos(incoming.blockPosition());
  double minX=(double)(c.x-CHUNK_RADIUS)*16,minZ=(double)(c.z-CHUNK_RADIUS)*16;
  double maxX=(double)(c.x+CHUNK_RADIUS+1)*16,maxZ=(double)(c.z+CHUNK_RADIUS+1)*16;
  AABB area=new AABB(minX,level.getMinBuildHeight(),minZ,maxX,level.getMaxBuildHeight(),maxZ);
  // Entity queries use the loaded entity index; never force-load surrounding chunks.
  boolean exists=!level.getEntitiesOfClass(Mob.class,area,m->{
   if(m==incoming||!m.isAlive()||m.getType()!=incoming.getType())return false;
   ChunkPos other=new ChunkPos(m.blockPosition());
   return Math.abs(other.x-c.x)<=CHUNK_RADIUS&&Math.abs(other.z-c.z)<=CHUNK_RADIUS;
  }).isEmpty();
  if(exists){event.setCanceled(true);return;}
  incoming.getPersistentData().putBoolean(CHECKED,true);
 }
}''')
print('One new mob per exact NoctisMagic entity type within a two-chunk radius; existing mobs and vanilla unaffected.')


# Explicit exceptions: both Nether demons and the three original Gothic Horror enemies.
edit('CharacterSpawnLimit.java','if(key==null||!Noctis.ID.equals(key.getNamespace()))return;','''if(key==null||!Noctis.ID.equals(key.getNamespace()))return;
  if(incoming instanceof Demon||incoming instanceof GothicHorror)return;''')
print('Spawn density exceptions: both Nether demon forms, Crimson Lady, Iron Midwife and Skull Stalker. All original spawn rules remain intact.')


# Post-build-source correction: Phantom Thief design and Leon combat, also during daylight.
p=java/'JokerDetailedClient.java';s=p.read_text(encoding='utf-8')
def change(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b,1)
change('v.x()/6.4f','v.x()/5.8f')
change('float x=side*(1.12f+dx*(.77f+.53f*r));','float x=side*(1.04f+dx*(.64f+.68f*r));')
change('float y=-3.98f+dy*(.34f+.29f*r)-.16f*dx-.38f*r*Math.max(0,dx);','float y=-3.97f+dy*(.32f+.49f*r)-.13f*dx-.58f*r*Math.max(0,dx);')
change('-2.78f+.145f*x*x+z','-3.10f+.13f*x*x+z')
change('head.loft(7,80,-7.65f,0,.12f,1.35f,1.5f,-7.1f,0,.04f,2.50f,2.34f,-5.4f,0,0,2.94f,2.72f,-4.0f,0,-.1f,2.85f,2.58f,-2.65f,0,-.2f,2.40f,2.24f,-1.25f,0,-.3f,1.48f,1.68f,-.2f,0,-.4f,.42f,.7f);','head.loft(7,48,-7.65f,0,.12f,1.25f,1.45f,-7.1f,0,.04f,2.15f,2.24f,-5.4f,0,0,2.56f,2.60f,-4.0f,0,-.1f,2.48f,2.47f,-2.65f,0,-.2f,2.05f,2.16f,-1.25f,0,-.3f,1.36f,1.55f,-.2f,0,-.4f,.52f,.72f);')
change('head.oval(1,side*2.77f,-3.54f,.05f,.35f,.77f,.52f);','head.oval(1,side*2.46f,-3.54f,.05f,.30f,.65f,.43f);')
change('head.blade(8,-.50f,-4.12f,-2.79f,.50f,-4.12f,-2.79f,.26f);','head.blade(8,-.58f,-4.08f,-3.13f,.58f,-4.08f,-3.13f,.39f);')
a=s.index('   head.loft(9,40,-9.05f');b=s.index('   for(int i=0;i<2;i++){int s=i==0?-1:1;',a)
s=s[:a]+'''   // Shorter, asymmetric black hair with bent tufts instead of a tall round crown.
   head.loft(9,24,-8.52f,-.15f,.35f,1.05f,1.0f,-8.22f,0,.22f,2.28f,2.12f,-7.48f,0,.20f,2.84f,2.72f,-6.18f,0,.24f,2.88f,2.80f);
   head.loft(9,24,-7.55f,0,1.0f,2.55f,2.0f,-5.7f,0,1.32f,2.65f,1.73f,-3.2f,0,1.65f,2.20f,1.16f,-1.8f,0,1.50f,1.22f,.20f);
   for(int j=0;j<8;j++){
    float x=-2.35f+j*.65f;float dx=(j<4?-.80f:.55f)+(j%3)*.18f;
    curl(head,x,-7.92f+(float)Math.sin(j*1.23)*.35f,-1.78f,dx,2.05f+(j%4)*.41f,-.68f,.58f+(j%3)*.10f);
   }
   for(int j=0;j<6;j++){
    Part q=head.child(-2.05f+j*.83f,-8.05f+(float)Math.cos(j*1.7)*.33f,.1f);
    q.rz=(j-2.5f)*.16f;
    q.loft(9,12,-.82f,(j%2==0?-.6f:.45f),.1f,.04f,.06f,-.35f,-.25f,.05f,.52f,.66f,.45f,0,0,.79f,.80f,1.7f,.18f,-.65f,.43f,.40f,2.35f,.48f,-1.15f,.03f,.03f);
   }
   for(int side:new int[]{-1,1}){
    for(int j=0;j<3;j++){
     Part q=head.child(side*(2.12f+j*.12f),-6.91f+j*.69f,.05f+j*.40f);q.rz=-side*(.23f+j*.12f);
     curl(q,0,0,0,side*(.40f+j*.13f),1.65f+(j%2)*.30f,.38f,.52f);
    }
   }
'''+s[b:]
change('body.blade(3,s*1.5f,-1.0f,-.7f,s*3.6f,-3.0f,1.15f,2.9f);','body.blade(3,s*1.5f,-1.0f,-.7f,s*3.05f,-2.85f,.70f,2.35f);')
change('p.scale(1.08f,1.10f,1.08f)','p.scale(1.12f,1.16f,1.08f)')
p.write_text(s,encoding='utf-8')

p=java/'CrossoverGuest.java';s=p.read_text(encoding='utf-8')
a=s.index('            if(l.isDay()||l.dimension()!=Level.OVERWORLD)')
b=s.index('        }else{',a)
s=s[:a]+'''            if(tickCount%5==0||!validEnemy(getTarget())){
                LivingEntity current=getTarget();
                if(!validEnemy(current)||!hasLineOfSight(current)||distanceTo(current)>24){
                    LivingEntity next=l.getEntitiesOfClass(Mob.class,getBoundingBox().inflate(36),m->validEnemy(m)).stream()
                        .min(java.util.Comparator.comparingDouble((Mob m)->distanceToSqr(m)+(hasLineOfSight(m)?0:1600))).orElse(null);
                    setTarget(next);
                }
            }
            LivingEntity t=getTarget();
            if(validEnemy(t)){
                double range=distanceTo(t);boolean sight=hasLineOfSight(t);
                getLookControl().setLookAt(t,45,45);
                if(sight&&range<=24){
                    getNavigation().stop();
                    double dx=t.getX()-getX(),dz=t.getZ()-getZ();
                    float yaw=(float)(Math.atan2(dz,dx)*180/Math.PI)-90f;
                    setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);
                    if(tickCount%4==0)l.broadcastEntityEvent(this,(byte)105);
                    if(cooldown<=0){
                        cooldown=16;l.broadcastEntityEvent(this,(byte)104);
                        Vec3 b=t.getBoundingBox().getCenter(),dir=b.subtract(getEyePosition()).normalize();
                        Vec3 a=getEyePosition().add(dir.scale(.78)).add(0,-.28,0);
                        l.sendParticles(ParticleTypes.FLAME,a.x,a.y,a.z,5,.06,.06,.06,.018);
                        l.sendParticles(ParticleTypes.SMOKE,a.x,a.y,a.z,4,.06,.06,.06,.01);
                        for(int i=1;i<=18;i++){Vec3 q=a.lerp(b,i/18.0);l.sendParticles(ParticleTypes.CRIT,q.x,q.y,q.z,1,.012,.012,.012,0);}
                        t.hurt(damageSources().mobAttack(this),22);
                        playSound(SoundEvents.FIREWORK_ROCKET_BLAST,.85f,1.65f);
                    }
                }else if(tickCount%5==0)getNavigation().moveTo(t,1.20);
            }
'''+s[b:]
change('    @Override public InteractionResult mobInteract(Player p,InteractionHand h){','''    private boolean validEnemy(LivingEntity e){
        if(!(e instanceof net.minecraft.world.entity.monster.Enemy)||!e.isAlive()||e==this||isAlliedTo(e)||distanceToSqr(e)>42*42)return false;
        if(e instanceof net.minecraft.world.entity.TamableAnimal pet&&pet.isTame())return false;
        if(e instanceof net.minecraft.world.entity.monster.ZombifiedPiglin pig)return pig.getTarget()==this;
        return true;
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){''')
change('l.isDay()?"Di giorno mi prendo una pausa.":"Resta lontano dagli zombie."','"Resta dietro di me. Tengo d’occhio i mostri."')
# Preserve both distinct client states; an aiming refresh must not reset the shot recoil.
p.write_text(s,encoding='utf-8')

p=java/'LeonSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('            head.loft(7,32,');b=s.index('\n            head.loft(3,16,',a)
s=s[:a]+'''            head.loft(7,28,-7.6f,0,.12f,1.3f,1.65f,-7.0f,0,.06f,2.28f,2.34f,-5.4f,0,0,2.78f,2.65f,-3.55f,0,-.08f,2.77f,2.54f,-1.9f,0,-.17f,2.48f,2.23f,-.82f,0,-.24f,1.86f,1.58f,-.25f,0,-.25f,1.12f,1.04f);'''+s[b:]
change('s*3.12f,-3.25f,.1f,.40f,.83f,.56f','s*2.72f,-3.25f,.1f,.33f,.68f,.46f')
a=s.index('            head.loft(8,24,');b=s.index('            for(int i=0;i<2;i++){int s=i==0?-1:1;',a)
s=s[:a]+'''            head.loft(8,24,-8.42f,.35f,.10f,.78f,.76f,-8.05f,.15f,.15f,2.22f,2.18f,-7.32f,0,.25f,2.94f,2.79f,-6.15f,0,.35f,2.92f,2.72f);
            Part back=head.child(0,-6.8f,1.7f);
            back.loft(8,20,-.75f,0,0,2.45f,1.42f,1.1f,0,.3f,2.67f,1.42f,3.8f,0,.6f,2.40f,1.15f,5.0f,0,.5f,1.3f,.24f);
            for(int j=0;j<8;j++){
                float x=-2.20f+j*.59f;Part lock=head.child(x,-7.88f+.08f*j,-1.73f);hair.add(lock);
                float end=j<5?4.25f-j*.30f:2.15f+(j%2)*.25f;
                lock.loft(j<5?9:8,14,-.45f,0,.65f,.58f,.63f,.5f,-.35f,-.35f,.78f,.69f,1.50f,-.80f,-.92f,.73f,.53f,end*.76f,-1.06f,-.75f,.41f,.30f,end,-1.15f,-.45f,.035f,.06f);
            }
'''+s[b:]
change('s*2.92f,-6.2f,.2f','s*2.55f,-6.2f,.2f')
change('1.18f,1.15f,1.15f','1.22f,1.19f,1.16f')
change('if(pose>.10f){if(!fore[1].children.contains(weapon))fore[1].children.add(weapon);}\n            else fore[1].children.remove(weapon);','if(!fore[1].children.contains(weapon))fore[1].children.add(weapon);\n            if(pose<=.10f){arms[1].rx=-.35f;fore[1].rx=-.27f;}')
change('fore[i].rx=-pose*(i==0?.78f:.15f);','fore[i].rx=-pose*(i==0?.78f:.15f)-(i==1?a*.14f:0);')
change('slide.loft(11,16,-.7f,0,0,.53f,.62f,0,0,0,.57f,.63f,3.4f,0,0,.50f,.55f);','''slide.loft(11,8,-.7f,0,0,.53f,.62f,0,0,0,.57f,.63f,3.4f,0,0,.50f,.55f);
            slide.loft(5,8,3.35f,0,0,.37f,.39f,3.85f,0,0,.37f,.39f);
            slide.blade(5,0,.15f,-.57f,0,2.95f,-.57f,.37f);''')
p.write_text(s,encoding='utf-8')
print('Corrective patch: angular Phantom mask and hair; Leon active during daylight, hostile targeting, firing and visible pistol.')


# Code Geass refinement: independent angular heads, layered hair, tailored outfits and colored dialogue.
p=java/'DramaGuest.java';s=p.read_text(encoding='utf-8')
a='void say(ServerLevel l,String s){NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+s));}'
assert a in s,a
s=s.replace(a,'''void say(ServerLevel l,String s){
        var msg=Component.literal(getDisplayName().getString()+": "+s);
        if(kind()==2)msg.withStyle(net.minecraft.ChatFormatting.GREEN);
        NpcDialogue.say(l,msg);
    }''',1)
p.write_text(s,encoding='utf-8')

p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
def geass_replace(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b,1)
# Keep the shared animations; replace just the head construction for each character.
a=s.index('            if(cc){\n            head.loft(6,64,')
b=s.index('                arms[i]=root.child(',a)
s=s[:a]+'''            if(cc){
                head.loft(6,40,-7.65f,0,.10f,1.25f,1.45f,-7.12f,0,.05f,2.25f,2.15f,-5.60f,0,0,2.73f,2.50f,-4.05f,0,-.08f,2.64f,2.43f,-2.65f,0,-.19f,2.11f,2.03f,-1.23f,0,-.34f,1.20f,1.42f,-.28f,0,-.48f,.48f,.75f,0,0,-.50f,.25f,.51f);
            }else{
                head.loft(6,40,-7.85f,0,.11f,1.20f,1.40f,-7.25f,0,.03f,2.28f,2.27f,-5.65f,0,0,2.71f,2.58f,-4.20f,0,-.10f,2.64f,2.50f,-2.85f,0,-.17f,2.19f,2.12f,-1.45f,0,-.34f,1.40f,1.57f,-.45f,0,-.48f,.62f,.91f,0,0,-.50f,.29f,.56f);
            }
            projectFace(head);
            head.loft(7,16,-4.8f,0,-2.36f,.14f,.10f,-3.9f,0,-2.55f,.24f,.23f,-3.05f,0,cc?-2.78f:-2.96f,.33f,.29f,-2.80f,0,-2.62f,.23f,.15f);
            for(int side:new int[]{-1,1}){
                head.oval(7,side*2.62f,-3.60f,.06f,.30f,.66f,.42f);
            }
            // A low tapered hair shell with independent swept, sharply pointed layered strands.
            head.loft(8,28,-8.70f,0,.15f,.82f,.88f,-8.34f,0,.12f,2.11f,2.08f,-7.55f,0,.18f,2.95f,2.74f,-6.3f,0,.27f,3.05f,2.77f);
            for(int j=0;j<13;j++){
                float t=j/12f;
                Part q=head.child(-2.53f+t*5.05f,-7.91f+(float)Math.sin(j*.83f)*.21f,-1.80f);
                float len=cc?2.15f+2.05f*(float)Math.pow(Math.sin(t*Math.PI),1.7):2.0f+1.82f*(float)Math.sin(t*Math.PI)+(j%3)*.12f;
                float dx=cc?(t-.52f)*1.55f-.20f:-1.2f+t*.72f;
                q.loft(8,12,-.50f,0,.52f,.43f,.49f,.24f,dx*.10f,-.18f,.54f,.51f,1.15f,dx*.33f,-.72f,.47f,.35f,len*.70f,dx*.72f,-.91f,.29f,.20f,len,dx,-.69f,.025f,.035f);
                q.blade(15,-.15f,.15f,-.48f,dx*.75f,len*.78f,-.92f,.14f);
            }
            for(int j=0;j<9;j++){
                float t=j/8f;
                Part q=head.child(-2.44f+t*4.88f,-8.25f+(float)Math.cos(j*1.1f)*.14f,.24f);
                float dx=cc?(t-.5f)*1.2f:-.9f+t*.6f;
                q.loft(8,12,-.64f,0,.22f,.32f,.43f,.1f,0,0,.52f,.56f,1.35f,dx*.45f,-.42f,.42f,.37f,2.25f,dx,-.84f,.025f,.03f);
            }
            if(cc){
                // Long flowing green locks, sculpted as tapered ribbons with a dark inner layer.
                for(int j=0;j<13;j++){
                    float t=j/12f,x=-2.82f+t*5.64f,spread=(t-.5f)*6.2f;
                    Part q=head.child(x,-6.65f,1.75f+.7f*(float)Math.sin(t*Math.PI));hair.add(q);
                    float len=21.8f+2.7f*(float)Math.sin(t*Math.PI)+(j%3)*.4f;
                    q.loft(j%4==0?11:8,12,-.32f,0,0,.36f,.44f,2,0,.39f,.51f,.51f,6,spread*.23f,.76f,.65f,.44f,12,spread*.55f,1.36f,.72f,.35f,18,spread*.87f,2.15f,.62f,.25f,len,spread,2.60f,.026f,.035f);
                    q.blade(15,0,2,-.48f,spread*.85f,len*.87f,1.91f,.15f);
                }
            }else{
                Part back=head.child(0,-6.8f,1.57f);hair.add(back);
                back.loft(8,24,-.45f,0,0,2.45f,1.45f,1.25f,0,.39f,2.73f,1.53f,3.65f,0,.40f,2.45f,1.25f,5.4f,0,.65f,1.47f,.25f);
            }
            for(int i=0;i<2;i++){
                int s=i==0?-1:1;
                for(int j=0;j<(cc?4:3);j++){
                    Part lock=head.child(s*(2.34f+j*.14f),-6.95f+j*.27f,-.70f+j*.48f);hair.add(lock);
                    float len=cc?16.9f+j*1.4f:4.0f+j*.55f;
                    lock.loft(8,12,-.28f,0,.1f,.38f,.45f,1.2f,s*.30f,-.34f,.50f,.49f,len*.33f,s*.40f,-.48f,.49f,.37f,len*.68f,s*(cc?1.0f:.34f),-.08f,.36f,.22f,len,s*(cc?1.36f:.26f),.34f,.025f,.035f);
                    if(cc)lock.blade(15,0,.65f,-.45f,s*.95f,len*.88f,-.15f,.13f);
                }
'''+s[b:]
geass_replace('float u=front?.5f+v.x()/7.5f:.035f;','float u=front?Math.max(.025f,Math.min(.975f,.5f+v.x()/6.25f)):.035f;')
geass_replace('return new V(v.x(),v.y(),z,u,v.v(),v.nx(),v.ny(),v.nz());','return new V(v.x(),v.y(),z,u,Math.max(.025f,Math.min(.975f,(v.y()+7.8f)/7.8f)),v.nx(),v.ny(),v.nz());')
# C.C.'s high-neck black/purple uniform with silver seam motif and three separate burgundy belts.
a=s.index('            }else{\n                body.blade(4,0,-.8f')
b=s.index('            // Separate head silhouette',a)
s=s[:a]+'''            }else{
                body.loft(0,28,-1.35f,0,0,1.08f,1.02f,-.7f,0,0,1.16f,1.12f,.15f,0,0,1.38f,1.27f);
                body.loft(4,24,-1.37f,0,0,1.10f,1.04f,-1.19f,0,0,1.10f,1.04f);
                body.blade(4,0,-1.17f,-1.07f,0,1.13f,-1.56f,.19f);
                for(int side:new int[]{-1,1}){
                    body.blade(4,side*.25f,.72f,-1.43f,side*2.42f,.12f,-1.35f,.24f);
                    body.blade(10,side*.16f,1.25f,-1.79f,side*1.65f,2.52f,-2.15f,.45f);
                    body.blade(10,side*2.65f,2.22f,-1.42f,0,5.18f,-1.91f,.66f);
                    body.blade(10,side*.64f,5.08f,-1.89f,side*.14f,6.90f,-1.62f,.41f);
                    body.blade(12,side*2.25f,5.60f,-1.15f,side*1.65f,8.75f,-1.48f,.48f);
                }
                body.blade(10,0,1.20f,-1.82f,0,4.15f,-2.22f,.23f);
                body.loft(3,24,10.25f,0,0,2.55f,1.73f,11.40f,0,0,2.79f,1.83f,12.70f,0,0,2.62f,1.62f);
                for(int k=0;k<3;k++){
                    float y=8.85f+k*.77f;
                    body.loft(1,28,y,0,0,2.55f+k*.13f,1.81f+k*.04f,y+.58f,0,0,2.56f+k*.13f,1.83f+k*.04f);
                    Part buckle=body.child(.50f,y+.29f,-1.96f-k*.04f);
                    buckle.loft(4,8,-.30f,0,0,.43f,.14f,.30f,0,0,.43f,.14f);
                    buckle.loft(13,8,-.18f,0,-.13f,.28f,.05f,.18f,0,-.13f,.28f,.05f);
                    for(int side:new int[]{-1,1})body.oval(4,side*1.95f,y+.29f,-1.35f,.11f,.12f,.09f);
                }
            }
'''+s[b:]
# Narrow the collar of Lelouch to its silhouette, refine front uniform details rather than oversized trim.
geass_replace('side*2.0f,1.0f,.04f,.05f,-5.6f,side*2.18f,.8f,.78f,.30f','side*1.65f,1.0f,.04f,.05f,-5.6f,side*1.85f,.8f,.70f,.30f')
geass_replace('side*3.15f,1.2f,-1.28f,side*1.2f,3.1f,-1.92f,.85f','side*3.15f,1.2f,-1.28f,side*1.2f,3.1f,-1.92f,.46f')
geass_replace('side*1.2f,3.1f,-1.92f,0,3.6f,-1.97f,.48f','side*1.2f,3.1f,-1.92f,0,3.6f,-1.97f,.28f')
geass_replace('fore[i].oval(0,0,4.98f,-.08f,.67f,.91f,.55f);','''{
                    fore[i].oval(7,0,4.75f,-.08f,.59f,.65f,.42f);
                    for(int k=0;k<4;k++)fore[i].loft(7,10,4.98f,-.42f+k*.28f,-.10f,.12f,.15f,5.72f-(k==3?.17f:0),-.42f+k*.28f,-.18f,.10f,.12f,5.91f-(k==3?.17f:0),-.42f+k*.28f,-.18f,.035f,.045f);
                    fore[i].blade(12,-.48f,.30f,-.72f,.20f,3.53f,-.64f,.40f);
                    arms[i].blade(1,s*.48f,2.10f,-.82f,s*.36f,3.1f,-.81f,.44f);
                }''')
# C.C. boots and open long split tails: separate dark exterior, burgundy inside and fine gold edge.
geass_replace('knees[i].blade(4,0,5.6f,-.81f,0,7.0f,-1.8f,.68f);','''knees[i].blade(4,0,5.6f,-.81f,0,7.0f,-1.8f,.68f);
                if(cc){
                    legs[i].loft(9,24,3.65f,0,0,1.05f,1.08f,4.06f,0,0,1.08f,1.10f,5.40f,0,0,.90f,.95f);
                    knees[i].blade(10,0,.10f,-1.02f,0,4.1f,-.76f,.30f);
                    knees[i].blade(4,0,1.35f,-1.03f,0,2.85f,-.94f,.87f);
                    knees[i].blade(12,s*.55f,2.80f,-.69f,s*.40f,5.00f,-.69f,.23f);
                }''')
geass_replace('float len=cc?15.4f:23.8f;','float len=cc?17.1f:23.8f;')
geass_replace('if(cc)c.loft(5,18,0,0,0,1.5f,.32f,len*.24f,s*.6f,.4f,2.0f,.37f,len*.54f,s*1.25f,1.2f,2.4f,.4f,len*.80f,s*2.0f,2.0f,1.7f,.34f,len,s*2.7f,3.3f,.08f,.10f);','''if(cc){
                    c.loft(0,20,0,0,0,1.35f,.18f,len*.24f,s*.48f,.45f,1.65f,.21f,len*.54f,s*1.05f,1.05f,1.78f,.20f,len*.80f,s*1.70f,1.80f,1.38f,.16f,len,s*2.30f,2.60f,.05f,.06f);
                    c.loft(5,20,0,0,.19f,1.29f,.09f,len*.24f,s*.48f,.67f,1.56f,.11f,len*.54f,s*1.05f,1.25f,1.68f,.10f,len*.80f,s*1.70f,1.97f,1.29f,.08f,len,s*2.30f,2.66f,.04f,.04f);
                }''')
p.write_text(s,encoding='utf-8')

# Both atlases receive expressive eyes, controlled face shadows, directional strands and fabric detail.
W,H=1024,512
for cc in (True,False):
 pix=bytearray(W*H*4)
 pal=[(28,29,45),(123,20,54),(34,29,45),(218,222,235),(211,167,65),(103,23,51),(247,206,182),(245,204,181),(114,177,64) if cc else (28,24,36),(190,203,221),(155,165,194),(49,105,62) if cc else (27,24,40),(65,67,93) if cc else (21,23,35),(95,57,31) if cc else (44,26,41),(161,96,84),(185,224,110) if cc else (69,58,83)]
 for m,base in enumerate(pal):
  for y in range(128):
   v=sat2((y-3)/121)
   for x in range(128):
    u=sat2((x-3)/121);f=abs(u-.5)
    c=shade(base,.83+.19*math.sin(math.pi*u)+.045*math.sin(u*55+v*23)**2)
    if m in (0,5,12):
     fold=math.sin(u*math.pi*4+v*4+math.sin(v*7)*.5)
     c=mix(c,(104,111,145) if m!=5 else (168,51,82),.27*max(0,fold)**6)
     c=mix(c,(12,13,23) if m!=5 else (57,12,31),.30*max(0,-fold)**6)
    if m==1:
     c=mix(c,(196,42,89),.33*math.exp(-((u-.36)/.17)**2))
     if v<.08 or v>.93:c=shade(c,.55)
    if m==4:c=mix(c,(255,229,128),.43*math.sin(math.pi*u)**2)
    if m in (9,10):
     c=mix(c,(245,249,255),.42*math.exp(-((u-.33)/.14)**2))
     c=mix(c,(71,83,112),.27*math.exp(-((u-.80)/.15)**2))
    if m in (8,11,15) and (cc or m!=11):
     wave=math.sin(u*math.pi*15+v*2.7+.4*math.sin(v*6))
     c=mix(c,(221,249,140) if cc else (87,76,107),.38*max(0,wave)**5+.13*math.exp(-((v-.28)/.16)**2))
     c=mix(c,(37,88,45) if cc else (11,12,20),.34*max(0,-wave)**4)
    if m==6:
     def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
     c=mix(base,(153,82,79),.26*sat2((f-.19)*4)+.10*v)
     c=mix(c,(255,231,206),.38*g(.50,.38,.12,.20))
     for side in (-1,1):
      ex=.5+side*.175;dx=side*(u-ex)/(.124 if cc else .119)
      dy=(v-(.474-.038*dx))/(.052 if cc else .046)
      d=abs(dx)**1.7+abs(dy)**1.28
      c=mix(c,(175,102,109),.23*g(ex,.46,.12,.078)+.16*g(ex,.61,.10,.055))
      if d<1.19:c=(43,25,36)
      if d<.80:c=(249,240,224)
      if d<.77 and abs(dx+.05)<.44:c=mix((136,87,29) if cc else (62,32,106),(247,198,72) if cc else (170,92,209),sat2((dy+.60)/1.3))
      if d<.74 and abs(dx+.05)<.18:c=(28,20,32)
      if d<.73 and (dx+.22)**2+(dy+.23)**2<.053:c=(255,251,241)
      if abs(dx)<1.10 and abs(v-(.372-.034*dx))<.013:c=(66,99,41) if cc else (35,25,38)
      if cc and .78<dx<1.16 and abs(v-(.443-.025*dx))<.012:c=(40,26,36)
     if f<.04 and abs(v-.675)<.009:c=mix(c,(164,89,81),.66)
     if f<.07 and abs(v-(.793-.014*(1-f/.07)))<.008:c=(145,74,80) if cc else (101,47,56)
     if f<.045 and abs(v-.812)<.007:c=(222,142,128)
    off=((m//8*128+y)*W+m%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
 png(assets/'textures/entity'/('cc_sculpted.png' if cc else 'lelouch_sculpted.png'),W,H,pix)
print('Code Geass: new angular heads, fine layered hair, detailed C.C. outfit and light-green chat.')


# Exodia: rebuilt from Egyptian giant / sealed monster reference, independent high-relief mesh.
p=java/'ExodiaClient.java';s=p.read_text(encoding='utf-8')
a=s.index('  M(){');b=s.index('  @Override public void setupAnim',a)
s=s[:a]+'''  // Raised curved golden ornaments, with a continuous swept tube.
  static void scroll(Part parent,int side,float x,float y,float z,float size){
   Part p=parent.child(x,y,z);
   for(int i=0;i<23;i++){
    float t=i/22f,ang=(float)(t*Math.PI*2.0),rad=size*(1-t*.83f);
    p.oval(1,side*rad*(float)Math.cos(ang),rad*(float)Math.sin(ang),0,.115f,.115f,.115f);
   }
  }
  static void stripe(Part p,int tile,float x,float y,float z,float endX,float endY,float endZ,float width){
   p.blade(tile,x,y,z,endX,endY,endZ,width);
  }
  static void shackle(Part p,float y,float w,float d){
   p.loft(6,28,y-.64f,0,0,w*.94f,d*.94f,y-.49f,0,0,w,d,y+.48f,0,0,w,d,y+.64f,0,0,w*.94f,d*.94f);
   for(float h:new float[]{y-.52f,y+.52f})p.loft(7,24,h-.10f,0,0,w*1.015f,d*1.015f,h+.10f,0,0,w*1.015f,d*1.015f);
   for(int k=0;k<10;k++){
    float t=k*(float)Math.PI/5;
    p.oval(7,(w-.03f)*(float)Math.sin(t),y,(d-.03f)*(float)Math.cos(t),.23f,.23f,.23f);
   }
  }
  M(){
   // A squat, colossal physique: huge chest and back, narrow waist, separated abdominal muscles.
   body.loft(0,36,-1.3f,0,0,3.40f,2.30f,-.55f,0,0,5.85f,3.25f,1.2f,0,-.12f,6.30f,3.60f,3.3f,0,-.13f,5.80f,3.43f,5.3f,0,0,4.65f,2.80f,7.8f,0,0,3.53f,2.20f,9.6f,0,0,3.62f,2.18f,11.0f,0,0,4.35f,2.62f);
   for(int side:new int[]{-1,1}){
    body.oval(0,side*2.74f,1.92f,-2.10f,2.88f,1.83f,1.78f);
    stripe(body,2,side*.38f,3.65f,-3.45f,side*4.85f,3.30f,-2.31f,.26f);
    for(int j=0;j<3;j++){
     float y=4.32f+j*1.45f;
     body.oval(0,side*1.47f,y,-2.52f+j*.17f,1.48f-j*.10f,.80f,.64f);
     stripe(body,2,side*.16f,y+.72f,-3.06f+j*.16f,side*2.62f,y+.63f,-2.16f+j*.13f,.18f);
     stripe(body,2,side*3.70f-j*.19f,4.0f+j*1.12f,-1.70f,side*2.75f-j*.14f,4.9f+j*1.12f,-2.10f,.30f);
    }
    // Iconic spirals above the chest; no blue shoulder gems.
    scroll(body,side,side*2.48f,2.15f,-3.84f,.87f);
    stripe(body,1,side*2.90f,2.78f,-3.53f,side*1.62f,5.08f,-3.04f,.27f);
   }
   body.oval(1,0,1.25f,-3.49f,.63f,.73f,.20f);
   body.oval(3,0,1.25f,-3.65f,.39f,.46f,.12f);
   body.blade(9,0,1.80f,-3.68f,0,5.75f,-3.07f,.95f);
   body.blade(1,0,1.82f,-3.80f,0,2.82f,-3.48f,.24f);
   body.loft(6,32,9.2f,0,0,3.72f,2.26f,10.13f,0,0,4.27f,2.55f,10.55f,0,0,4.30f,2.58f);
   body.oval(1,0,10.04f,-2.60f,.77f,.70f,.26f);
   body.oval(7,0,10.04f,-2.82f,.41f,.47f,.12f);
   // Back anatomy, modelled in relief: trapezius, shoulder blades, lats and spinal muscles.
   for(int side:new int[]{-1,1}){
    body.loft(0,24,-1.75f,side*.95f,1.08f,.84f,.70f,-.55f,side*2.03f,1.77f,1.52f,1.00f,.80f,side*3.13f,2.28f,1.93f,1.06f,2.30f,side*3.16f,2.56f,1.45f,.88f,3.22f,side*2.65f,2.47f,.52f,.40f);
    body.loft(0,24,1.68f,side*3.35f,2.25f,1.58f,1.01f,3.22f,side*3.83f,2.37f,1.77f,1.12f,4.68f,side*3.14f,2.17f,1.58f,1.02f,6.45f,side*2.49f,1.82f,1.13f,.76f,8.00f,side*1.54f,1.77f,.45f,.42f);
    body.loft(0,18,3.3f,side*.85f,2.83f,.45f,.39f,5.30f,side*.79f,2.55f,.66f,.60f,7.50f,side*.74f,2.01f,.62f,.61f,9.1f,side*.75f,1.95f,.37f,.30f);
    body.blade(2,side*1.34f,.67f,3.28f,side*3.36f,2.62f,3.38f,.19f);
    body.blade(2,side*3.05f,3.25f,3.48f,side*1.34f,5.68f,2.74f,.22f);
    body.blade(2,side*.20f,4.0f,3.16f,side*.29f,8.75f,2.37f,.12f);
    body.oval(0,side*1.87f,10.53f,1.78f,1.91f,1.16f,1.05f);
   }
   // Central spine and rear belt clasp.
   for(int j=0;j<6;j++){
    float y=2.10f+j*1.02f,z=3.51f-j*.20f;
    body.oval(0,0,y,z,.27f,.29f,.23f);
   }
   body.oval(7,0,10.04f,2.64f,.73f,.66f,.22f);
   body.oval(1,0,10.04f,2.82f,.45f,.43f,.14f);
   // Small deeply recessed demonic face, huge flared Egyptian nemes and two golden crown prongs.
   head.y=-.50f;
   // Broad neck joins the skull to the trapezius; do not leave a floating mask.
   head.y=-2.55f;
   body.loft(0,28,-4.72f,0,.08f,.89f,.95f,-4.20f,0,.12f,1.18f,1.15f,-3.25f,0,.15f,1.47f,1.40f,-2.05f,0,.18f,1.81f,1.62f,-.80f,0,.19f,2.38f,1.94f,.40f,0,.13f,2.86f,2.18f);
   body.loft(1,32,-1.55f,0,0,1.92f,1.77f,-1.34f,0,0,2.04f,1.88f,-.95f,0,0,2.19f,1.98f,-.73f,0,0,2.24f,2.03f);
   for(int side:new int[]{-1,1}){
    body.loft(0,16,-3.72f,side*.69f,-.48f,.49f,.48f,-2.5f,side*1.02f,-.77f,.63f,.56f,-1.10f,side*1.60f,-.94f,.75f,.60f,.32f,side*2.15f,-1.14f,.47f,.40f);
    body.blade(2,side*.61f,-3.15f,-1.04f,side*1.71f,-.94f,-1.53f,.14f);
    body.blade(1,side*.53f,-.92f,-1.94f,side*2.90f,.72f,-2.03f,.31f);
   }
   // Rear of the nemes: a real shaped gold and purple headcloth with a raised central seam.
   head.loft(8,24,-6.32f,0,1.12f,1.74f,.76f,-5.37f,0,1.34f,2.21f,1.01f,-3.79f,0,1.48f,2.02f,.86f,-2.04f,0,1.61f,1.54f,.59f,-.52f,0,1.76f,.78f,.23f);
   for(int side:new int[]{-1,1})for(int j=0;j<5;j++){
    float x=side*(.24f+j*.35f);
    head.blade(1,x,-5.63f,2.10f-j*.045f,x*.52f,-1.16f,2.02f-j*.06f,.19f);
   }
   head.blade(1,0,-6.24f,2.05f,0,-.60f,2.03f,.28f);
   head.loft(4,24,-6.78f,0,.2f,.80f,.86f,-6.02f,0,0,1.57f,1.46f,-4.76f,0,-.06f,1.72f,1.63f,-3.55f,0,-.18f,1.45f,1.36f,-2.35f,0,-.35f,1.0f,1.0f,-1.94f,0,-.37f,.60f,.63f);
   head.loft(1,28,-8.1f,0,.26f,.55f,.61f,-7.65f,0,.12f,1.95f,1.75f,-6.65f,0,.06f,2.88f,2.32f,-5.90f,0,.13f,2.70f,2.12f);
   for(int side:new int[]{-1,1}){
    Part horn=head.child(side*.65f,-7.45f,-.13f);horn.rz=side*.25f;
    horn.loft(1,14,-4.0f,side*.58f,.35f,.035f,.045f,-3.2f,side*.33f,.24f,.32f,.35f,-2.05f,side*.09f,.10f,.61f,.57f,-.75f,0,0,.75f,.72f,.35f,0,.04f,.80f,.74f);
    // Upper headcloth wings, curled upward at the outside, purple-red/gold ribs.
    Part upper=head.child(side*.56f,-6.08f,-1.59f);
    upper.rz=-side*.70f;
    upper.loft(8,16,-.42f,0,0,.52f,.28f,.55f,side*.48f,0,1.25f,.43f,1.60f,side*.88f,.18f,1.78f,.46f,2.92f,side*1.28f,.48f,1.45f,.38f,3.68f,side*1.55f,.75f,.09f,.11f);
    for(int j=0;j<7;j++){
     float t=j/6f;
     stripe(upper,1,side*(.10f+1.26f*t),.02f+2.95f*t,-.40f+ .78f*t,side*(.97f+1.30f*t),.48f+2.82f*t,-.28f+.76f*t,.18f);
    }
    Part lower=head.child(side*1.10f,-4.67f,-1.31f);lower.rz=-side*.22f;
    lower.loft(8,20,-.3f,0,0,.68f,.41f,.8f,side*.36f,.18f,1.27f,.53f,2.05f,side*.90f,.45f,1.29f,.47f,3.38f,side*1.50f,.69f,1.12f,.36f,4.33f,side*1.93f,.91f,.09f,.08f);
    for(int j=0;j<7;j++){
     float t=j/6f;
     stripe(lower,1,side*(.02f+1.76f*t),-.05f+3.52f*t,-.46f+.78f*t,side*(.84f+1.65f*t),.45f+3.61f*t,-.29f+.72f*t,.18f);
    }
    // Recessed dark eye sockets, slanted eyes and angular gilded eyebrow ridges.
    Part eye=head.child(side*.72f,-4.92f,-1.54f);eye.rz=-side*.23f;eye.ry=-side*.18f;
    eye.oval(10,0,0,0,.58f,.36f,.21f);
    eye.oval(12,0,.02f,-.17f,.38f,.15f,.085f);
    stripe(head,1,side*.14f,-5.25f,-1.76f,side*1.34f,-5.57f,-1.16f,.36f);
    stripe(head,1,side*.24f,-4.06f,-1.63f,side*1.36f,-4.49f,-1.30f,.37f);
    stripe(head,1,side*.66f,-2.64f,-1.12f,side*1.45f,-4.05f,-1.31f,.38f);
   }
   head.blade(1,0,-6.96f,-2.07f,0,-4.10f,-1.89f,.62f);
   head.blade(3,0,-6.31f,-2.28f,0,-5.44f,-2.13f,.40f);
   head.oval(10,0,-3.58f,-1.53f,.94f,.65f,.21f);
   for(int j=0;j<7;j++){
    float x=-.72f+j*.24f;
    head.loft(9,8,-4.05f,x,-1.69f,.12f,.10f,-3.77f,x,-1.76f,.10f,.10f,-3.63f,x,-1.75f,.035f,.05f);
    head.loft(9,8,-3.48f,x,-1.72f,.03f,.04f,-3.35f,x,-1.74f,.105f,.095f,-3.18f,x,-1.68f,.11f,.09f);
   }
   head.loft(3,12,-2.94f,0,-1.08f,.30f,.30f,-2.42f,0,-1.25f,.36f,.35f,-1.48f,0,-1.32f,.24f,.24f);
   for(int j=0;j<3;j++)head.loft(1,12,-2.80f+j*.36f,0,-1.23f,.36f-j*.035f,.34f,-2.70f+j*.36f,0,-1.24f,.35f-j*.035f,.33f);
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;
    arms[i]=body.child(side*5.96f,.20f,0);
    // Huge domed pauldrons with broad upward flared rims, layered hammered bronze.
    Part shoulder=arms[i].child(side*.75f,-.60f,0);shoulder.rz=-side*.15f;
    shoulder.loft(1,40,-3.00f,side*.30f,.10f,.75f,.82f,-2.70f,side*.40f,.07f,2.32f,2.35f,-1.95f,side*.70f,0,3.36f,3.02f,-.75f,side*1.0f,0,4.24f,3.56f,.05f,side*1.17f,0,4.72f,3.78f,.45f,side*1.14f,0,4.36f,3.54f,.86f,side*.72f,0,2.80f,2.63f);
    shoulder.loft(1,36,-.12f,side*1.18f,0,4.70f,3.77f,.21f,side*1.21f,0,4.83f,3.83f,.50f,side*1.14f,0,4.40f,3.55f);
    shoulder.blade(1,side*3.23f,.05f,0,side*5.65f,-1.10f,.25f,2.02f);
    // Engraved ribs wrap around the posterior rim as well as the front.
    for(int j=0;j<10;j++){
     float a=(j+.5f)*(float)Math.PI/10;
     float x=side*1.17f+4.45f*(float)Math.cos(a),z=3.50f*(float)Math.sin(a);
     shoulder.blade(7,x,.18f,z,x*.92f,-.60f,z*.86f,.10f);
    }
    shoulder.blade(7,side*.10f,-.16f,3.57f,side*2.95f,-.15f,3.35f,.16f);
    for(int k=0;k<11;k++){
     float angle=k*(float)Math.PI/10;
     float x=side*1.17f+4.53f*(float)Math.cos(angle);
     float z=-3.58f*(float)Math.sin(angle);
     shoulder.blade(7,x,.17f,z,x*.89f,-.39f,z*.86f,.10f);
    }
    // Pronounced biceps, triceps and tendon relief.
    arms[i].loft(0,32,-.5f,0,0,2.30f,2.25f,.65f,0,0,2.68f,2.56f,2.7f,0,0,2.49f,2.28f,4.0f,0,0,1.97f,1.94f,5.25f,0,0,1.72f,1.67f);
    arms[i].oval(0,side*.04f,2.60f,-1.43f,1.93f,2.01f,1.25f);
    arms[i].oval(0,side*.37f,2.17f,1.36f,1.81f,1.80f,1.16f);
    arms[i].loft(0,20,.82f,-side*.61f,1.54f,.76f,.64f,2.10f,-side*.53f,1.72f,1.04f,.94f,3.55f,-side*.26f,1.45f,.86f,.69f,4.72f,0,1.23f,.35f,.32f);
    arms[i].blade(2,-side*.55f,1.58f,2.48f,side*.06f,4.37f,1.76f,.16f);
    stripe(arms[i],2,side*1.50f,1.08f,-1.31f,side*1.72f,4.35f,-.72f,.22f);
    fore[i]=arms[i].child(0,5.1f,0);
    fore[i].loft(0,28,-.25f,0,0,1.79f,1.70f,1.08f,0,0,2.24f,2.08f,2.22f,0,0,1.97f,1.85f,3.62f,0,0,1.63f,1.53f);
    fore[i].oval(0,-side*.61f,1.6f,-1.03f,1.28f,1.5f,1.07f);
    stripe(fore[i],2,side*.88f,.46f,-1.68f,side*.42f,2.81f,-1.62f,.18f);
    shackle(fore[i],3.20f,2.02f,1.90f);
    fore[i].loft(0,16,.12f,side*.62f,1.10f,.49f,.45f,1.34f,side*.65f,1.49f,1.03f,.91f,2.47f,side*.30f,1.44f,.70f,.65f,2.73f,side*.14f,1.30f,.35f,.28f);
    fore[i].blade(2,-side*.35f,.54f,1.75f,side*.16f,2.67f,1.71f,.17f);
    // Wide open hands, separated knuckles, bent individual fingers and thumb.
    fore[i].oval(0,0,4.53f,-.12f,1.66f,1.30f,1.02f);
    for(int j=0;j<4;j++){
     float x=-1.15f+j*.76f;
     float len=j==0?1.24f:j==3?1.34f:1.65f;
     Part finger=fore[i].child(x,5.16f,-.25f);
     finger.rz=(j-1.5f)*-.16f;finger.rx=-.22f;
     finger.loft(0,12,-.15f,0,0,.38f,.40f,.50f,0,-.12f,.42f,.40f,len*.72f,0,-.35f,.33f,.30f,len,0,-.54f,.20f,.20f);
     finger.oval(1,0,.34f,-.40f,.30f,.25f,.11f);
    }
    Part thumb=fore[i].child(-side*1.45f,4.35f,-.36f);thumb.rz=side*.62f;
    thumb.loft(0,14,-.15f,0,0,.39f,.42f,.65f,0,-.20f,.51f,.44f,1.38f,0,-.48f,.32f,.30f,1.65f,0,-.55f,.17f,.20f);
    // Massive hanging rusty chain; last link ends open.
    Part prev=fore[i];for(int j=0;j<5;j++){
     Part link=chains[i][j]=prev.child(j==0?side*1.90f:0,j==0?3.43f:1.53f,j==0?.55f:0);
     link.ry=(j%2)*1.57f;
     if(j<4)loop(link,5,.59f,.96f,.19f);
     else{
      for(int k=0;k<14;k++)for(int v=0;v<8;v++){
       float t0=k*(float)Math.PI/9,t1=(k+1)*(float)Math.PI/9,b0=v*(float)Math.PI/4,b1=(v+1)*(float)Math.PI/4;
       link.faces.add(new Q(ring(t0,b0,.59f,.96f,.19f,k/18f,v/8f),ring(t1,b0,.59f,.96f,.19f,(k+1)/18f,v/8f),ring(t1,b1,.59f,.96f,.19f,(k+1)/18f,(v+1)/8f),ring(t0,b1,.59f,.96f,.19f,k/18f,(v+1)/8f),5));
      }
     }
     prev=link;
    }
    // Dark segmented Egyptian kilt, not long gold trousers.
    skirts[i]=body.child(side*1.85f,10.3f,0);
    for(int j=0;j<5;j++){
     float ang=side*(.16f+j*.37f);
     Part panel=skirts[i].child((float)Math.sin(ang)*1.60f,0,-(float)Math.cos(ang)*2.39f);
     panel.ry=-ang;
     panel.loft(11,12,-.12f,0,0,.72f,.27f,1.25f,side*.14f,.14f,.94f,.26f,3.30f,side*.56f,.39f,.87f,.23f,4.80f,side*.83f,.63f,.045f,.07f);
     stripe(panel,7,0,.38f,-.28f,side*.60f,3.84f,.14f,.10f);
    }
    legs[i]=root.child(side*2.70f,11.3f,0);
    // Rear and side kilt panels overlap; animate on the existing skirt pivots.
    for(int j=0;j<5;j++){
     float a=side*(.16f+j*.29f);
     Part panel=skirts[i].child((float)Math.sin(a)*1.55f,0,(float)Math.cos(a)*2.37f);
     panel.ry=a;
     panel.loft(11,12,-.14f,0,0,.67f,.26f,1.05f,side*.10f,-.08f,.88f,.26f,3.10f,side*.33f,-.21f,.83f,.23f,4.62f,side*.60f,-.44f,.06f,.08f);
     panel.blade(7,0,.27f,.28f,side*.43f,3.83f,-.01f,.11f);
    }
    legs[i].loft(0,28,-.48f,0,0,2.37f,2.29f,.9f,0,0,2.62f,2.48f,2.8f,0,0,2.31f,2.20f,5.25f,0,0,1.59f,1.57f);
    legs[i].oval(0,side*.55f,2.12f,-1.34f,1.64f,2.14f,1.37f);
    legs[i].oval(0,-side*.74f,2.81f,-.97f,1.31f,1.70f,1.11f);
    // Posterior thigh: distinct inner and outer hamstrings taper into knee tendons.
    legs[i].loft(0,22,-.20f,side*.61f,1.05f,1.11f,1.11f,.85f,side*.81f,1.45f,1.52f,1.31f,2.63f,side*.68f,1.57f,1.27f,1.19f,4.10f,side*.48f,1.34f,.74f,.79f,5.11f,side*.40f,1.02f,.29f,.33f);
    legs[i].loft(0,20,.18f,-side*.74f,1.03f,.86f,.88f,1.55f,-side*.77f,1.52f,1.19f,1.08f,3.12f,-side*.56f,1.49f,.99f,.89f,4.72f,-side*.40f,1.13f,.42f,.40f,5.18f,-side*.31f,.96f,.21f,.25f);
    legs[i].blade(2,0,.99f,2.72f,side*.12f,4.89f,1.69f,.18f);
    legs[i].blade(2,side*2.05f,1.22f,.64f,side*1.39f,4.31f,.53f,.20f);
    stripe(legs[i],2,side*.08f,.75f,-2.38f,side*.56f,4.59f,-1.86f,.20f);
    shin[i]=legs[i].child(0,5.12f,0);
    shin[i].oval(0,0,.12f,-.91f,1.66f,1.41f,1.26f);
    shin[i].loft(0,28,.28f,0,0,1.62f,1.60f,2.1f,0,.14f,1.91f,1.76f,4.0f,0,0,1.45f,1.41f,5.75f,0,0,1.45f,1.45f);
    stripe(shin[i],2,0,1.01f,-1.52f,0,4.74f,-1.46f,.24f);
    // Calves, Achilles tendon, posterior knee and ankle relief.
    shin[i].oval(0,side*.67f,2.02f,1.19f,1.14f,1.76f,1.16f);
    shin[i].oval(0,-side*.60f,2.26f,1.27f,1.02f,1.66f,1.08f);
    shin[i].loft(0,16,2.66f,0,1.44f,.40f,.42f,3.56f,0,1.51f,.52f,.43f,4.69f,0,1.43f,.33f,.30f,5.77f,0,1.35f,.24f,.26f);
    shin[i].blade(2,0,.81f,2.12f,0,3.55f,2.10f,.16f);
    shin[i].blade(2,side*.92f,3.17f,1.52f,side*.27f,4.75f,1.55f,.14f);
    shin[i].oval(0,0,6.36f,1.18f,1.31f,.76f,.92f);
    shackle(shin[i],5.10f,1.87f,1.80f);
    shin[i].loft(0,28,5.75f,0,0,1.45f,1.41f,6.40f,0,-.54f,1.86f,2.35f,7.40f,0,-.72f,1.99f,2.54f);
    for(int j=0;j<4;j++)shin[i].oval(0,-1.27f+j*.80f,6.95f,-2.66f,.44f,.48f,.62f);
    for(int j=0;j<5;j++){
     float x=-1.31f+j*.63f;
     shin[i].oval(1,x,6.92f,-3.08f+(j==4?.25f:0),.25f,.13f,.22f);
    }
    shin[i].oval(0,0,6.88f,1.33f,1.42f,.42f,.71f);
    for(int j=0;j<4;j++){Part link=shin[i].child(side*(1.85f+j*.80f),5.4f+j*.40f,.45f+j*.42f);link.rz=side*1.13f;link.ry=j%2*1.57f;loop(link,5,.55f,.83f,.17f);}
   }
   Part apron=body.child(0,10.25f,-2.52f);apron.loft(11,12,-.1f,0,0,1.30f,.26f,1.8f,0,.10f,1.48f,.24f,4.3f,0,.38f,1.12f,.21f,5.4f,0,.61f,.04f,.05f);
   apron.blade(7,0,.25f,-.24f,0,4.3f,.23f,.15f);
   Part rear=body.child(0,10.34f,2.55f);
   rear.loft(11,12,-.10f,0,0,1.03f,.26f,1.35f,0,.10f,1.27f,.25f,3.50f,0,.32f,.91f,.20f,4.82f,0,.47f,.045f,.07f);
   rear.blade(7,0,.20f,.26f,0,3.83f,.49f,.13f);
  }
'''+s[b:]
s=s.replace('arms[i].rz=-s*(.13f+hit*(mode==2?1.15f:.35f));','arms[i].rz=-s*(.34f+hit*(mode==2?.82f:.30f));',1)
s=s.replace('fore[i].rx=-hit*(mode==0?.65f:.30f);','fore[i].rx=-.16f-hit*(mode==0?.65f:.30f);fore[i].ry=s*(.16f+hit*.20f);',1)
s=s.replace('legs[i].rx=w*.38f;shin[i].rx=Math.max(0,-w)*.18f;','legs[i].rx=w*.38f;legs[i].rz=-s*.13f;shin[i].rx=Math.max(0,-w)*.18f;',1)
p.write_text(s,encoding='utf-8')

# Hammered bronze, patina, gold and purple headcloth, leather, rust and bone-white teeth.
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(185,115,48),(224,164,72),(97,49,27),(29,109,132),(64,39,34),(78,40,31),(87,45,34),(145,90,48),(117,28,62),(232,219,184),(23,15,20),(60,40,34),(255,227,116)]
for m,base in enumerate(pal):
 for y in range(128):
  v=sat2((y-3)/121)
  for x in range(128):
   u=sat2((x-3)/121)
   grain=(math.sin(x*7.13+y*9.71)*math.cos(x*11.29-y*5.17)+1)*.5
   c=shade(base,.78+.22*math.sin(u*math.pi)+.09*grain)
   if m in (0,1,2,7):
    c=mix(c,(255,224,151),(.46 if m==1 else .27)*math.exp(-((u-.33)/.13)**2))
    c=mix(c,(91,40,22),.24*math.exp(-((u-.82)/.14)**2)+.10*v)
    c=shade(c,.93+.10*grain)
    scratch=math.sin(u*183+v*29+math.sin(v*17))
    if scratch>.975 and math.sin(v*51+u*73)>.4:c=mix(c,(104,59,34),.37)
    if m==1 and v<.045:c=mix(c,(255,221,133),.48)
   if m==8:
    rib=math.sin((u+.025*math.sin(v*5))*math.pi*16)
    c=mix(c,(247,187,76),.91*max(0,rib)**4)
    c=mix(c,(45,15,38),.30*max(0,-rib)**3)
   if m in (5,6):
    c=mix(c,(168,89,50),.29*grain+.18*math.exp(-((u-.28)/.12)**2))
    c=mix(c,(31,23,23),.22*(1-grain))
   if m==11:
    c=mix(c,(113,83,67),.25*max(0,math.sin(u*math.pi*3+v*2))**4)
    if v>.92:c=shade(c,.55)
   if m==3:c=mix(c,(103,217,219),.37*math.exp(-((u-.33)/.15)**2))
   if m==12:c=mix((255,178,52),(255,252,203),.40+.50*math.sin(math.pi*u))
   off=((m//8*128+y)*W+m%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/exodia.png',W,H,pix)
print('Exodia remade: massive anatomy, domed shoulders, striped nemes, horns, demonic teeth, open hands, dark kilt and broken chains.')


# One visible quest per character, retaining legacy advancement IDs and saved progress.
base=res/'data/noctismagic/advancements/rituals'
for f in sorted(base.glob('*_complete.json')):
 ident=f.stem[:-9];start=base/(ident+'.json')
 if not start.exists():continue
 first=json.loads(start.read_text(encoding='utf-8'));last=json.loads(f.read_text(encoding='utf-8'))
 if 'display' not in first or 'display' not in last:continue
 # Non-displayed discovery advancement still grants its original reward and gates existing logic.
 first.pop('display');last['parent']='noctismagic:rituals/root'
 write_noctis_json_resource(start,first);write_noctis_json_resource(f,last)
 for lang in ('it_it','en_us'):
  lp=assets/'lang'/f'{lang}.json';d=json.loads(lp.read_text(encoding='utf-8'))
  pre='advancement.noctismagic.rituals.'
  first_desc=d.get(pre+ident+'.description','');last_desc=d.get(pre+ident+'_complete.description','')
  d[pre+ident+'_complete.title']=d.get(pre+ident+'.title',d.get(pre+ident+'_complete.title',ident))
  d[pre+ident+'_complete.description']=' '.join(dict.fromkeys(x for x in (first_desc,last_desc) if x))
  write_noctis_json_resource(lp,d)

# Giorno: visibly angular adult head, slimmer temples, smaller swept crown and tighter signature rolls.
p=java/'GiornoSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   head.loft(5,64,');b=s.index('   project(head,5,false);',a)
s=s[:a]+'''   head.loft(5,32,-7.85f,0,.12f,1.15f,1.45f,-7.25f,0,.05f,2.17f,2.17f,-5.65f,0,-.03f,2.72f,2.55f,-4.36f,0,-.11f,2.68f,2.50f,-3.22f,0,-.19f,2.37f,2.30f,-2.12f,0,-.28f,1.92f,1.98f,-.75f,0,-.43f,1.20f,1.35f,-.10f,0,-.48f,.55f,.75f);
'''+s[b:]
s=s.replace('chest?8.65f:6.65f','chest?8.65f:5.85f',1)
s=s.replace('head.loft(6,32,-9.1f,0,.16f,.5f,.6f,-8.75f,0,.18f,2.55f,2.40f,-7.55f,0,.35f,3.48f,3.10f,-6.1f,0,.5f,3.45f,3.0f);','head.loft(6,24,-8.85f,0,.16f,.70f,.75f,-8.38f,0,.18f,2.18f,2.19f,-7.55f,0,.35f,2.99f,2.79f,-6.1f,0,.5f,2.96f,2.69f);',1)
s=s.replace('float x=(i-4)*.76f;','float x=(i-4)*.65f;',1)
s=s.replace('q=head.child(-2.08f+j*2.08f,-6.68f,-2.69f);q.rz=(j-1)*.12f;curl(q,.79f,.90f);','q=head.child(-1.84f+j*1.84f,-6.70f,-2.55f);q.rz=(j-1)*.12f;curl(q,.68f,.78f);',1)
s=s.replace('q.oval(7,0,0,.09f,.44f,.49f,.19f);','q.oval(6,0,0,.10f,.44f,.49f,.21f);',1)
s=s.replace('s*3.0f,-3.25f,.13f,.4f,.82f,.54f','s*2.62f,-3.25f,.13f,.31f,.67f,.43f',1)
s=s.replace('s*3.19f,-2.65f,.02f,.19f,.25f,.18f','s*2.79f,-2.65f,.02f,.15f,.22f,.15f',1)
s=s.replace('head.oval(10,0,-2.05f,-2.20f,.60f,.13f,.18f);','head.oval(10,0,-1.85f,-1.97f,.49f,.08f,.10f);',1)
p.write_text(s,encoding='utf-8')

# Spawnable buildings also appear automatically in newly generated Overworld regions.
# Use the existing structure plans and finish callbacks, not copies of their geometry.
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8')
assert 'this.player=player.getUUID();' in s
s=s.replace('this.player=player.getUUID();','this.player=player==null?null:player.getUUID();',1)
s=s.replace('void msg(String s){ServerPlayer pl=','void msg(String s){if(player==null)return;ServerPlayer pl=',1)
s=s.replace('void refund(){ServerPlayer pl=','void refund(){if(player==null)return;ServerPlayer pl=',1)
s=s.replace('if(!l.hasChunkAt(at)||!l.getBlockState(at).isAir()){msg','if(!l.hasChunkAt(at)||(!l.getBlockState(at).isAir()&&!(player==null&&l.getBlockState(at).canBeReplaced()&&l.getFluidState(at).isEmpty()))){msg',1)
s=s.replace('if(!l.getBlockState(at).isAir())continue;','if(!l.getBlockState(at).isAir()&&!(player==null&&l.getBlockState(at).canBeReplaced()&&l.getFluidState(at).isEmpty()))continue;',1)
p.write_text(s,encoding='utf-8')
write('NaturalMonuments.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class NaturalMonuments extends SavedData{
 static final int REGION=24;
 final Set<Long> pending=new LinkedHashSet<>(),finished=new HashSet<>();
 static final Map<ServerLevel,GothicEgg.Job> active=new HashMap<>();
 static final Map<ServerLevel,Long> activeKey=new HashMap<>();
 static NaturalMonuments get(ServerLevel l){return l.getDataStorage().computeIfAbsent(NaturalMonuments::load,NaturalMonuments::new,"noctis_natural_monuments");}
 static NaturalMonuments load(CompoundTag tag){NaturalMonuments d=new NaturalMonuments();for(long x:tag.getLongArray("Pending"))d.pending.add(x);for(long x:tag.getLongArray("Finished"))d.finished.add(x);return d;}
 @Override public CompoundTag save(CompoundTag tag){tag.putLongArray("Pending",pending.stream().mapToLong(Long::longValue).toArray());tag.putLongArray("Finished",finished.stream().mapToLong(Long::longValue).toArray());return tag;}
 static Random random(ServerLevel l,int rx,int rz){return new Random(l.getSeed()^((long)rx*341873128712L)^((long)rz*132897987541L)^0x46F4347L);}
 static int[] candidate(ServerLevel l,int rx,int rz){
  Random r=random(l,rx,rz);if(r.nextInt(100)>=76)return null;
  return new int[]{rx*REGION+4+r.nextInt(12),rz*REGION+4+r.nextInt(12),r.nextInt(4)};
 }
 @SubscribeEvent public static void generated(ChunkEvent.Load e){
  if(!e.isNewChunk()||!(e.getLevel() instanceof ServerLevel l)||l.dimension()!=Level.OVERWORLD)return;
  ChunkPos cp=e.getChunk().getPos();int rx=Math.floorDiv(cp.x,REGION),rz=Math.floorDiv(cp.z,REGION);
  int[] c=candidate(l,rx,rz);if(c==null||cp.x!=c[0]||cp.z!=c[1])return;
  long key=ChunkPos.asLong(cp.x,cp.z);
  // Defer all world writes to the server tick, never access neighbouring chunks in this event.
  l.getServer().execute(()->{NaturalMonuments d=get(l);if(!d.finished.contains(key)&&d.pending.add(key))d.setDirty();});
 }
 static boolean loaded(ServerLevel l,int x,int z,int w,int d){
  for(int cx=x>>4;cx<=(x+w-1)>>4;cx++)for(int cz=z>>4;cz<=(z+d-1)>>4;cz++)
   if(!l.hasChunk(cx,cz))return false;
  return true;
 }
 static GothicEgg.Plan plan(int type){return switch(type){case 0->GothicEgg.bakery(false);case 1->GothicEgg.bakery(true);case 2->GothicEgg.cathedral();default->GothicEgg.castle();};}
 static void finish(NaturalMonuments d,long key){d.pending.remove(key);d.finished.add(key);d.setDirty();}
 @SubscribeEvent public static void tick(TickEvent.LevelTickEvent event){
  if(event.phase!=TickEvent.Phase.END||!(event.level instanceof ServerLevel l)||l.dimension()!=Level.OVERWORLD)return;
  if(!GothicEgg.Jobs.queue.isEmpty())return;
  NaturalMonuments data=get(l);
  GothicEgg.Job job=active.get(l);
  if(job!=null){
   if(!loaded(l,job.origin.getX(),job.origin.getZ(),job.p.w,job.p.d))return;
   if(job.step()){finish(data,activeKey.remove(l));active.remove(l);}return;
  }
  if(l.getGameTime()%40!=0||data.pending.isEmpty())return;
  for(long key:new ArrayList<>(data.pending)){
   ChunkPos cp=new ChunkPos(key);int[] c=candidate(l,Math.floorDiv(cp.x,REGION),Math.floorDiv(cp.z,REGION));
   if(c==null){finish(data,key);continue;}
   int x=cp.getMinBlockX(),z=cp.getMinBlockZ();
   if(!l.hasChunk(cp.x,cp.z))continue;
   GothicEgg.Plan p=plan(c[2]);if(!loaded(l,x,z,p.w,p.d))continue;
   // Search only safe, reasonably flat land. Never flatten houses, forests or cliffs.
   int low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;boolean wet=false;
   for(int dx=0;dx<p.w;dx+=4)for(int dz=0;dz<p.d;dz+=4){
    int h=l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x+dx,z+dz);
    low=Math.min(low,h);high=Math.max(high,h);
    if(!l.getFluidState(new BlockPos(x+dx,h-1,z+dz)).isEmpty())wet=true;
   }
   if(wet||high-low>3||high<l.getSeaLevel()||high+p.h>=l.getMaxBuildHeight()){finish(data,key);continue;}
   job=new GothicEgg.Job(l,null,p,new BlockPos(x,high,z),Direction.SOUTH);
   active.put(l,job);activeKey.put(l,key);return;
  }
 }
 @SubscribeEvent public static void stop(ServerStoppedEvent event){active.clear();activeKey.clear();}
}''')

# Exodia attacks any living mob, not only players; plasma projectiles and radial shockwaves.
p=java/'Exodia.java';s=p.read_text(encoding='utf-8')
a=' boolean valid(Player p){return p!=null&&p.isAlive()&&!p.isCreative()&&!p.isSpectator()&&distanceTo(p)<100;}'
assert a in s
s=s.replace(a,''' boolean valid(LivingEntity e){return e!=null&&e!=this&&e.isAlive()&&distanceTo(e)<100&&(e instanceof Mob||e instanceof Player)&&(!(e instanceof Player p)||(!p.isCreative()&&!p.isSpectator()));}
 Vec3 plasma=null,plasmaVelocity=Vec3.ZERO;int plasmaLife=0;
 void burst(ServerLevel l,Vec3 at,float radius){
  l.sendParticles(ParticleTypes.EXPLOSION_EMITTER,at.x,at.y,at.z,1,0,0,0,0);
  l.sendParticles(ParticleTypes.ELECTRIC_SPARK,at.x,at.y,at.z,45,radius*.35,radius*.35,radius*.35,.18);
  l.explode(this,at.x,at.y,at.z,radius,Level.ExplosionInteraction.MOB);
 }
 void tickPlasma(ServerLevel l){
  if(plasma==null)return;
  Vec3 end=plasma.add(plasmaVelocity);
  var wall=l.clip(new net.minecraft.world.level.ClipContext(plasma,end,net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,this));
  boolean impact=wall.getType()!=net.minecraft.world.phys.HitResult.Type.MISS;
  Vec3 next=impact?wall.getLocation():end;
  l.sendParticles(ParticleTypes.END_ROD,next.x,next.y,next.z,18,.44,.44,.44,.08);
  l.sendParticles(ParticleTypes.ELECTRIC_SPARK,next.x,next.y,next.z,24,.60,.60,.60,.13);
  l.sendParticles(ParticleTypes.SOUL_FIRE_FLAME,next.x,next.y,next.z,13,.36,.36,.36,.04);
  for(int i=0;i<12;i++){double a=i*Math.PI/6;l.sendParticles(ParticleTypes.FLAME,next.x+Math.cos(a)*.64,next.y+Math.sin(a)*.64,next.z,1,0,0,0,0);}
  var hit=l.getEntitiesOfClass(LivingEntity.class,new net.minecraft.world.phys.AABB(plasma,next).inflate(1.4),this::valid);
  if(impact||!hit.isEmpty()||--plasmaLife<=0){
   for(LivingEntity e:l.getEntitiesOfClass(LivingEntity.class,new net.minecraft.world.phys.AABB(next,next).inflate(6),this::valid))
    if(e.position().distanceTo(next)<6)e.hurt(damageSources().magic(),26+phase*7);
   burst(l,next,4.5f+phase*.75f);plasma=null;
  }else plasma=next;
 }
 void launchPlasma(ServerLevel l,Vec3 target){
  plasma=position().add(0,5.8,0);plasmaVelocity=target.subtract(plasma).normalize().scale(1.15);plasma=plasma.add(plasmaVelocity.scale(2.0));plasmaLife=42;
  playSound(SoundEvents.BLAZE_SHOOT,2,.55f);
 }''',1)
a=s.index('  Player t=summoner==null?null:l.getPlayerByUUID(summoner);')
b=s.index('  if(!valid(t)){setDeltaMovement',a)
s=s[:a]+'''  tickPlasma(l);
  LivingEntity t=getTarget();
  if(!valid(t)||tickCount%12==0){
   t=l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(80),this::valid).stream()
    .min(Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
  }
'''+s[b:]
# Use all valid mobs for damage but keep warning text for players.
s=s.replace('for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(40),this::valid)){','for(LivingEntity p:l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(40),this::valid)){',1)
s=s.replace('for(Player p:l.getEntitiesOfClass(Player.class,getBoundingBox().inflate(45),this::valid)){','for(LivingEntity p:l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(45),this::valid)){',1)
s=s.replace('mode=cycle++%3;','mode=cycle++%4;',1)
s=s.replace('charge=mode==0?38:mode==1?30:24;','charge=mode==0?38:mode==1?30:mode==3?20:24;',1)
s=s.replace('l.broadcastEntityEvent(this,(byte)(90+mode));','l.broadcastEntityEvent(this,(byte)(90+(mode==3?0:mode)));',1)
s=s.replace('mode==1?"Sigillo di distruzione: esci dal cerchio!":"Onda delle catene: allontanati!"','mode==1?"Sigillo di distruzione: esci dal cerchio!":mode==3?"Sfera di plasma!":"Onda delle catene: allontanati!"',1)
s=s.replace(' void strike(ServerLevel l){\n  if(mode==0){',''' void strike(ServerLevel l){
  if(mode==3){launchPlasma(l,aim.add(0,1,0));l.broadcastEntityEvent(this,(byte)94);return;}
  if(mode==0){''',1)
s=s.replace('   playSound(SoundEvents.WARDEN_SONIC_BOOM,3,.7f);','   burst(l,end,4.0f+phase*.5f);playSound(SoundEvents.WARDEN_SONIC_BOOM,3,.7f);',1)
s=s.replace('   playSound(SoundEvents.GENERIC_EXPLODE,3,.7f);','''   if(mode==2){
    for(int ring=1;ring<=3;ring++)for(int i=0;i<32;i++){
     double a=i*Math.PI/16,r=radius*ring/3.0;
     l.sendParticles(ParticleTypes.ELECTRIC_SPARK,aim.x+Math.cos(a)*r,aim.y+.65,aim.z+Math.sin(a)*r,2,.18,.18,.18,.10);
    }
    for(int i=0;i<4;i++){double a=i*Math.PI/2;burst(l,aim.add(Math.cos(a)*4,1,Math.sin(a)*4),3.6f+phase*.4f);}
   }else burst(l,aim.add(0,.7,0),4.6f+phase*.5f);
   playSound(SoundEvents.GENERIC_EXPLODE,3,.7f);''',1)
p.write_text(s,encoding='utf-8')
# Remove the former joke disconnect: spawning Exodia must leave the player in-game to fight.
for n in ('ExodiaRitual.java','ExodiaEgg.java'):
 p=java/n;s=p.read_text(encoding='utf-8')
 s=s.replace('p.connection.disconnect(Component.literal("Hai vinto il duello.").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));','')
 # Actual victory is awarded by the existing death listener, not merely by using the egg.
 s=s.replace('RitualQuests.award(p,"exodia");RitualQuests.complete(p,"exodia");','RitualQuests.summon(p,boss,"exodia");')
 p.write_text(s,encoding='utf-8')
print('Single visible quests; natural monuments in new regions; angular Giorno; hostile Exodia with plasma and terrain damage.')


# Inventory texture pass: named seeds/fruits and individually sculpted-looking Exodia fragments.
# Pure Python RGBA sprite rasterizer; no extra graphics dependency.
class Icon64:
 def __init__(self):
  self.n=64;self.p=bytearray(64*64*4)
 def put(self,x,y,c):
  if 0<=x<64 and 0<=y<64:
   i=(y*64+x)*4;self.p[i:i+4]=bytes((*[max(0,min(255,round(v))) for v in c],255))
 def rect(self,x,y,w,h,c):
  for yy in range(y,y+h):
   for xx in range(x,x+w):self.put(xx,yy,c)
 def ell(self,cx,cy,rx,ry,base,angle=0,lit=True):
  co=math.cos(angle);si=math.sin(angle);r=math.ceil(max(rx,ry))+1
  for y in range(max(0,int(cy-r)),min(64,int(cy+r+1))):
   for x in range(max(0,int(cx-r)),min(64,int(cx+r+1))):
    dx=x+.5-cx;dy=y+.5-cy;u=(co*dx+si*dy)/rx;v=(-si*dx+co*dy)/ry
    d=u*u+v*v
    if d>1:continue
    if not lit:c=base
    elif d>.89:c=shade(base,.48)
    else:
     c=shade(base,.74+.24*math.sqrt(max(0,1-d))+.17*math.exp(-((u+.37)**2+(v+.42)**2)/.25)-.14*max(0,u+v)/2)
     if (x*17+y*31)%23==0:c=mix(c,(245,214,159),.10)
    self.put(x,y,c)
 def poly(self,points,c):
  for y in range(max(0,math.floor(min(q[1] for q in points))),min(64,math.ceil(max(q[1] for q in points))+1)):
   for x in range(max(0,math.floor(min(q[0] for q in points))),min(64,math.ceil(max(q[0] for q in points))+1)):
    inside=False
    for i,(a,b) in enumerate(points):
     d,e=points[i-1]
     if (b>y+.5)!=(e>y+.5) and x+.5<(d-a)*(y+.5-b)/(e-b)+a:inside=not inside
    if inside:self.put(x,y,c)
 def line(self,x,y,X,Y,r,c):
  n=max(1,math.ceil(math.hypot(X-x,Y-y)*2))
  for i in range(n+1):
   t=i/n;self.ell(x+(X-x)*t,y+(Y-y)*t,r,r,c,lit=False)
 def label(self,word,y,scale=2,col=(255,247,222)):
  glyph={'A':('010','101','111','101','101'),'C':('111','100','100','100','111'),'F':('111','100','110','100','100'),'L':('100','100','100','100','111'),'N':('101','111','111','111','101'),'O':('111','101','101','101','111'),'S':('111','100','111','001','111'),'U':('101','101','101','101','111'),'V':('101','101','101','101','010')}
  width=(len(word)*4-1)*scale;x0=(64-width)//2
  for i,ch in enumerate(word):
   for yy,row in enumerate(glyph[ch]):
    for xx,bit in enumerate(row):
     if bit=='1':self.rect(x0+i*4*scale+xx*scale,y+yy*scale,scale,scale,col)
 def save(self,name):png(assets/'textures/item'/f'{name}.png',64,64,self.p)

for name,color in [('vaffanculo',(226,44,47)),('suca',(153,71,225))]:
 for fruit in (False,True):
  im=Icon64();long=name=='vaffanculo'
  # Use an ivory inscription on the object itself; long word wraps at a syllable.
  label_y=38 if long else 44
  if fruit:
   im.ell(32,30,24,25,(45,24,41))
   im.ell(27,29,18,24,color,-.12)
   im.ell(38,30,17,23,color,.18)
   im.line(31,13,34,3,2,(85,64,34))
   im.ell(42,8,10,4,(76,170,49),-.42)
   im.line(36,10,48,5,0.9,(157,222,82))
   im.ell(19,18,5,8,mix(color,(255,237,205),.36),.30)
  else:
   # Seed packet with large matching seeds pictured on its face.
   im.poly([(7,4),(57,4),(60,10),(56,59),(8,59),(4,10)],(48,29,38))
   im.poly([(9,7),(55,7),(57,11),(53,56),(11,56),(7,11)],shade(color,.61))
   im.rect(9,9,46,3,mix(color,(255,226,171),.46))
   im.rect(12,14,40,22,(251,218,162))
   im.ell(24,26,7,10,color,.48);im.ell(39,24,6,9,color,-.42)
   im.line(23,20,21,26,1,mix(color,(255,246,192),.48))
   im.line(40,19,42,24,1,mix(color,(255,246,192),.48))
  # Dark high-contrast lettering field, stays inside the fruit/packet silhouette.
  im.rect(6 if long else 12,label_y-2,52 if long else 40,24 if long else 14,(47,20,31) if long else (42,22,68))
  if long:
   im.label('VAFFAN',label_y,2);im.label('CULO',label_y+12,2)
  else:im.label('SUCA',label_y,2)
  im.save(name+('_fruit' if fruit else '_seeds'))

# All five relics: matching ornate bronze frames, individual anatomical shapes,
# gold shading, purple-and-gold nemes, muscle contours and rusted chain shackles.
gold=(221,155,64);bright=(255,216,128);skin=(192,119,53);dark=(84,40,25);rust=(117,64,45);violet=(116,32,77)
def link_icon(im,x,y,ang):
 im.ell(x,y,3.8,5.4,(53,30,26),ang)
 im.ell(x,y,2.9,4.6,rust,ang)
 im.ell(x,y,1.5,2.9,(31,22,35),ang,False)
def cuff_icon(im,x,y):
 im.ell(x,y,10,4.8,(61,31,26))
 im.ell(x,y-1,9.2,3.6,rust)
 im.line(x-8,y-3,x+8,y-3,1.1,(189,119,75))
 for d in (-6,-2,2,6):im.ell(x+d,y-1,1.3,1.3,(205,147,93))
for k,id in enumerate(('head','left_arm','right_arm','left_leg','right_leg')):
 im=Icon64()
 # Rounded chamfered plaque; dark field allows gold silhouettes to read at GUI scale.
 outer=[(9,2),(55,2),(62,9),(62,55),(55,62),(9,62),(2,55),(2,9)]
 im.poly(outer,(52,30,29));im.poly([(10,4),(54,4),(60,10),(60,54),(54,60),(10,60),(4,54),(4,10)],gold)
 im.poly([(11,8),(53,8),(56,11),(56,53),(53,56),(11,56),(8,53),(8,11)],(50,29,45))
 for x in (7,57):
  for y in (7,57):im.ell(x,y,2.1,2.1,bright)
 im.line(12,6,51,6,.9,bright)
 if k==0:
  # Horns, fan-shaped striped Egyptian headdress, recessed eyes, teeth and blue beard.
  for s in (-1,1):
   im.poly([(32+s*5,21),(32+s*8,8),(32+s*13,4),(32+s*13,15),(32+s*10,24)],dark)
   im.poly([(32+s*6,21),(32+s*9,9),(32+s*12,6),(32+s*11,16),(32+s*9,23)],gold)
   im.poly([(32+s*5,20),(32+s*18,15),(32+s*24,24),(32+s*18,45),(32+s*7,40)],gold)
   im.poly([(32+s*5,23),(32+s*16,18),(32+s*21,25),(32+s*16,42),(32+s*7,37)],violet)
   for j in range(5):
    im.line(32+s*(7+j*2.5),22-j*.6,32+s*(7+j*2.0),37+j*.7,1.05,bright)
  im.ell(32,31,10,13,skin)
  im.poly([(22,25),(32,21),(42,25),(39,39),(32,46),(25,39)],dark)
  im.poly([(23,26),(31,29),(29,33),(24,30)],(255,237,138))
  im.poly([(41,26),(33,29),(35,33),(40,30)],(255,237,138))
  im.line(32,24,32,34,1.5,gold)
  im.ell(32,37,7,3,(28,17,23),lit=False)
  for i in range(6):im.rect(26+i*2,35,1,3,(247,230,191))
  im.poly([(29,42),(35,42),(34,50),(30,50)],(37,121,142))
  for y in (44,47,50):im.line(30,y,34,y,.8,gold)
 else:
  # Left/right pieces deliberately mirror one another but have different silhouettes.
  s=-1 if k in (1,3) else 1
  if k in (1,2):
   im.ell(32+s*5,16,14,9,gold,-s*.30)
   im.line(32+s*17,17,32-s*6,22,1.3,bright)
   im.ell(32+s*5,28,8,12,skin,s*.24)
   im.ell(32+s*7,27,4.6,8.5,gold,s*.25)
   im.ell(32-s*1,37,7.0,11,skin,-s*.30)
   im.line(32+s*2,34,32+s*3,41,1.2,dark)
   cuff_icon(im,32-s*3,43)
   im.ell(32-s*4,49,7.0,4.7,skin)
   for j in range(4):im.ell(27-s*3+j*3.0,52,1.8,3.2,gold,.12*(j-1))
   im.ell(32-s*10,48,2.4,3.7,skin,-.55*s)
   link_icon(im,32+s*10,48,.30);link_icon(im,32+s*12,55,-.50)
  else:
   im.ell(32+s*4,20,10,13,skin,s*.19)
   im.ell(32+s*6,17,5.0,9,gold,s*.16)
   im.ell(32,31,6.9,6.0,skin)
   im.line(27,30,33,34,1.1,dark)
   im.ell(32-s*2,39,7.2,11,skin,-s*.17)
   im.ell(31-s*3,37,3.6,7.7,gold,-s*.17)
   cuff_icon(im,32-s*3,45)
   im.ell(32-s*7,52,12,5.5,skin,s*.08)
   for j in range(4):im.ell(23-s*4+j*4,52.5,2.3,2.5,gold)
   link_icon(im,32+s*9,48,.65);link_icon(im,32+s*14,54,1.12)
 im.save('exodia_'+id)
print('Inventory textures: 64px labeled Vaffanculo/Suca seeds and fruits, five shaded Egyptian Exodia relics.')


# Miles Edgeworth: dedicated sculpted renderer, with an independent articulated tea grip.
edit('CrossoverClient.java','e.registerEntityRenderer(Noctis.MILES_EDGEWORTH.get(),c->new Renderer(c,2));','')
write('EdgeworthSculptedClient.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class EdgeworthSculptedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MILES_EDGEWORTH.get(),R::new);}
 static float clamp(float v){return Math.max(.025f,Math.min(.975f,v));}
 static V face(V v,boolean f){return new V(v.x(),v.y(),v.z(),f?clamp(.5f+v.x()/6.35f):.025f,clamp((v.y()+7.75f)/7.75f),v.nx(),v.ny(),v.nz());}
 static void project(Part p){for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);if(q.tile()!=5)continue;boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;p.faces.set(i,new Q(face(q.a(),f),face(q.b(),f),face(q.c(),f),face(q.d(),f),5));}}
 static V handleV(float a,float b,float u,float v){
  float ca=(float)Math.cos(a),sa=(float)Math.sin(a),cb=(float)Math.cos(b),sb=(float)Math.sin(b);
  return new V((.45f+.13f*cb)*ca,(.57f+.13f*cb)*sa,.13f*sb,u,v,ca*cb,sa*cb,sb);
 }
 static void handle(Part p){
  for(int i=0;i<20;i++)for(int j=0;j<8;j++){
   float a=i*(float)Math.PI/10,A=(i+1)*(float)Math.PI/10,b=j*(float)Math.PI/4,B=(j+1)*(float)Math.PI/4;
   p.faces.add(new Q(handleV(a,b,i/20f,j/8f),handleV(A,b,(i+1)/20f,j/8f),handleV(A,B,(i+1)/20f,(j+1)/8f),handleV(a,B,i/20f,(j+1)/8f),9));
  }
 }
 static class M extends EntityModel<CrossoverGuest>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shins=new Part[2];
  final Part wrist,cup;
  M(){
   // Tailored crimson three-piece suit, narrow waist and broad, defined shoulders.
   body.loft(0,24,-.75f,0,0,1.75f,1.35f,.15f,0,0,4.15f,2.12f,2.45f,0,-.08f,3.83f,2.24f,5.2f,0,0,3.18f,1.83f,8.15f,0,0,2.88f,1.65f,10.75f,0,0,3.37f,1.94f);
   body.loft(4,24,-1.35f,0,0,1.30f,1.23f,.4f,0,0,1.49f,1.30f);
   body.blade(1,0,.30f,-1.98f,0,7.65f,-1.85f,3.20f);
   // Folded white cravat, separate cascading fabric lobes.
   body.loft(2,20,-.40f,0,-1.48f,1.23f,.38f,.5f,0,-1.63f,1.36f,.41f,1.0f,0,-1.76f,.75f,.30f);
   for(int j=0;j<4;j++){
    float y=.64f+j*.86f,w=1.17f-j*.14f;
    body.loft(2,20,y,0,-2.06f,w*.76f,.24f,y+.28f,0,-2.23f,w,.29f,y+.73f,0,-2.28f,w*.53f,.14f);
    body.blade(3,-w*.67f,y+.36f,-2.43f,w*.58f,y+.57f,-2.43f,.10f);
   }
   for(int s:new int[]{-1,1}){
    body.blade(6,s*2.96f,.35f,-1.67f,s*.68f,6.45f,-1.93f,1.50f);
    body.blade(0,s*3.15f,.4f,-1.53f,s*1.85f,2.4f,-2.11f,1.13f);
    body.blade(7,s*2.98f,6.9f,-1.24f,s*1.65f,7.05f,-1.66f,.14f);
    body.blade(6,s*2.73f,8.2f,-1.15f,s*3.02f,12.25f,-.70f,1.30f);
    body.blade(7,s*.14f,8.7f,-1.69f,s*.60f,11.8f,-1.74f,.08f);
   }
   for(int j=0;j<3;j++)body.oval(7,.19f,5.3f+j*1.32f,-1.89f,.14f,.16f,.10f);
   body.blade(7,-3.2f,3.33f,-1.46f,-1.98f,3.47f,-2.01f,.16f);
   // Angular, adult face, narrower jaw and visibly sculpted nose.
   head.loft(5,36,-7.75f,0,.12f,1.25f,1.55f,-7.18f,0,.06f,2.34f,2.25f,-5.55f,0,0,2.78f,2.61f,-4.1f,0,-.09f,2.73f,2.51f,-2.55f,0,-.17f,2.26f,2.15f,-1.12f,0,-.36f,1.55f,1.59f,-.30f,0,-.44f,.82f,.96f,0,0,-.46f,.50f,.63f);
   project(head);
   head.loft(4,16,-4.80f,0,-2.43f,.20f,.14f,-3.98f,0,-2.69f,.30f,.24f,-3.08f,0,-2.99f,.42f,.33f,-2.78f,0,-2.72f,.29f,.16f);
   for(int s:new int[]{-1,1}){
    head.oval(4,s*2.67f,-3.40f,.12f,.32f,.69f,.45f);
    head.blade(4,s*1.72f,-3.24f,-2.07f,s*2.14f,-2.54f,-1.48f,.19f);
   }
   // Signature parted gray hair: swept raised crown, two tapered forehead locks, trimmed back.
   head.loft(8,28,-8.83f,0,.10f,.65f,.75f,-8.45f,0,.12f,2.12f,2.03f,-7.65f,0,.24f,2.94f,2.80f,-6.48f,0,.45f,2.97f,2.73f);
   Part back=head.child(0,-6.88f,1.47f);
   back.loft(8,24,-.50f,0,0,2.36f,1.36f,1.10f,0,.27f,2.65f,1.28f,3.20f,0,.36f,2.42f,.95f,4.9f,0,.20f,1.62f,.20f);
   for(int s:new int[]{-1,1}){
    for(int j=0;j<7;j++){
     float t=j/6f;
     Part lock=head.child(s*(.20f+t*2.25f),-8.13f+.49f*t,-1.67f+.30f*t);
     float len=2.15f+1.82f*t+(j%2)*.20f;
     float drift=s*(.67f+.28f*t);
     lock.loft(8,12,-.55f,0,.55f,.43f,.53f,.32f,drift*.28f,-.27f,.54f,.49f,1.34f,drift*.62f,-.76f,.48f,.33f,len*.74f,drift,-.74f,.29f,.20f,len,drift*.90f,-.40f,.025f,.035f);
     lock.blade(11,0,.12f,-.40f,drift*.85f,len*.82f,-.72f,.13f);
    }
    for(int j=0;j<4;j++){
     Part lock=head.child(s*(2.41f+j*.08f),-6.97f+j*.26f,.05f+j*.47f);
     lock.loft(8,12,-.45f,0,.12f,.34f,.49f,.58f,s*.24f,.03f,.43f,.50f,1.77f,s*.14f,.24f,.30f,.34f,3.30f-j*.24f,s*.02f,.43f,.035f,.05f);
    }
   }
   for(int i=0;i<2;i++){
    int s=i==0?-1:1;
    arms[i]=body.child(s*4.20f,.35f,0);
    arms[i].loft(0,20,-.58f,0,0,1.05f,1.11f,.55f,0,0,1.38f,1.35f,2.65f,0,0,1.17f,1.15f,4.75f,0,0,.91f,.94f);
    arms[i].blade(6,s*.53f,.38f,-1.02f,s*.60f,3.92f,-.75f,.23f);
    fore[i]=arms[i].child(0,4.65f,0);
    fore[i].loft(0,20,-.16f,0,0,.94f,.96f,1.6f,0,0,1.04f,1.04f,3.8f,0,0,.74f,.77f);
    fore[i].loft(2,20,3.66f,0,0,.76f,.78f,4.23f,0,0,.69f,.71f);
    for(int j=0;j<3;j++)fore[i].oval(7,s*.72f,2.45f+j*.33f,-.43f,.10f,.10f,.09f);
    if(i==0){
     fore[i].oval(4,0,4.96f,-.05f,.66f,.78f,.46f);
     for(int j=0;j<4;j++){
      float x=-.44f+j*.29f,len=j==1?1.25f:.65f;
      fore[i].loft(4,10,5.00f,x,-.16f,.15f,.19f,5.50f,x,-.22f,.13f,.15f,5.00f+len+.31f,x,-.25f,.05f,.07f);
     }
     fore[i].oval(4,-.66f,4.83f,-.26f,.21f,.46f,.22f);
    }
    legs[i]=root.child(s*1.65f,11.0f,0);
    legs[i].loft(0,24,-.25f,0,0,1.51f,1.52f,2.55f,0,0,1.42f,1.40f,5.7f,0,0,1.10f,1.14f);
    legs[i].blade(6,0,.45f,-1.43f,0,5.35f,-1.13f,.16f);
    shins[i]=legs[i].child(0,5.5f,0);
    shins[i].loft(0,24,-.25f,0,0,1.12f,1.14f,2.0f,0,0,1.14f,1.16f,5.75f,0,0,.93f,1.02f,6.50f,0,0,1.05f,1.09f);
    shins[i].blade(6,0,.22f,-1.14f,0,6.0f,-1.04f,.13f);
    shins[i].loft(7,24,6.0f,0,0,.94f,1.06f,6.90f,0,-.55f,1.12f,1.72f,7.5f,0,-.61f,1.16f,1.83f);
   }
   // Real wrist pivot and fingers gripping the cup's loop. Cup stays upright as elbow moves.
   wrist=fore[1].child(0,4.23f,0);
   wrist.oval(4,.25f,.52f,0,.52f,.69f,.44f);
   cup=wrist.child(-1.30f,-.52f,-.06f);
   cup.loft(9,24,-.72f,0,0,1.02f,1.02f,-.55f,0,0,1.04f,1.04f,.62f,0,0,.77f,.77f,1.02f,0,0,.56f,.56f);
   cup.loft(9,24,.99f,0,0,.65f,.65f,1.16f,0,0,.65f,.65f);
   // Visible dark tea surface and a thin porcelain rim above it.
   cup.loft(10,24,-.76f,0,0,.88f,.88f,-.71f,0,0,.88f,.88f);
   Part rim=cup.child(0,-.79f,0);rim.rx=(float)Math.PI/2;
   for(int j=0;j<32;j++){
    float a=j*(float)Math.PI/16;rim.oval(9,.99f*(float)Math.cos(a),.99f*(float)Math.sin(a),0,.075f,.075f,.075f);
   }
   Part grip=cup.child(1.21f,.04f,0);handle(grip);
   for(int j=0;j<3;j++){
    float y=-.52f+j*.28f;
    wrist.loft(4,10,y,.36f,-.33f,.19f,.20f,y+.19f,.09f,-.37f,.20f,.18f,y+.25f,-.16f,-.24f,.15f,.14f);
   }
   wrist.oval(4,.17f,-.18f,.17f,.24f,.40f,.24f);
  }
  @Override public void setupAnim(CrossoverGuest e,float limb,float amount,float age,float yaw,float pitch){
   float a=e.action(),obj=e.animation()==0?a:0,tea=e.animation()==1?a:0;
   head.ry=yaw*.017f*(1-obj*.55f);head.rx=pitch*.012f+tea*.09f-obj*.04f;
   body.ry=0;
   for(int i=0;i<2;i++){
    float s=i==0?-1:1,w=(float)Math.cos(limb*.666f+i*Math.PI)*amount;
    legs[i].rx=w*.62f;shins[i].rx=Math.max(0,-w)*.25f;
    arms[i].ry=0;arms[i].rz=0;
    arms[i].rx=-w*.48f;fore[i].rx=-.08f-Math.max(0,w)*.25f;
   }
   // Opposite arm points, so the other hand never throws or clips its cup.
   arms[0].rx=-.12f-1.40f*obj;arms[0].rz=.10f-.12f*obj;fore[0].rx=-.20f*(1-obj);
   arms[1].rx=-.34f-.52f*tea;fore[1].rx=-1.05f-.48f*tea;
   wrist.rx=-(arms[1].rx+fore[1].rx);
   wrist.ry=0;wrist.rz=0;
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<CrossoverGuest,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.36f);}
  @Override protected void scale(CrossoverGuest e,PoseStack p,float partial){p.scale(1.08f,1.10f,1.08f);}
  @Override public ResourceLocation getTextureLocation(CrossoverGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/edgeworth_sculpted.png");}
 }
}''')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(135,34,65),(42,29,38),(245,240,230),(163,161,165),(232,190,164),(232,190,164),(98,25,49),(29,26,32),(115,113,125),(245,239,223),(130,76,38),(179,177,187)]
for m,base in enumerate(pal):
 for y in range(128):
  v=sat2((y-3)/121)
  for x in range(128):
   u=sat2((x-3)/121);f=abs(u-.5)
   c=shade(base,.82+.19*math.sin(u*math.pi)+.035*math.sin(u*57+v*19)**2)
   if m in (0,6):
    fold=math.sin(u*math.pi*4+v*2.6+.5*math.sin(v*8))
    c=mix(c,(191,69,102),.30*max(0,fold)**5)
    c=mix(c,(46,13,32),.29*max(0,-fold)**5)
   if m in (8,11):
    wave=math.sin(u*math.pi*16+v*3.2+.4*math.sin(v*5))
    c=mix(c,(211,207,220),.41*max(0,wave)**4+.11*math.exp(-((v-.27)/.17)**2))
    c=mix(c,(43,40,52),.33*max(0,-wave)**5)
   if m in (2,9):c=mix(c,(255,255,251),.26*math.exp(-((u-.32)/.13)**2))
   if m==9 and (.07<v<.10 or .90<v<.93):c=mix(c,(173,133,67),.70)
   if m==10:c=mix(c,(201,143,73),.27*math.sin(u*math.pi)**2)
   if m==5:
    def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
    c=mix(base,(126,70,66),.22*sat2((f-.19)*4)+.11*v)
    c=mix(c,(255,222,195),.32*g(.5,.36,.15,.19))
    for side in (-1,1):
     ex=.5+side*.174;dx=side*(u-ex)/.124;dy=(v-(.478-.036*dx))/.043
     d=abs(dx)**1.6+abs(dy)**1.25
     c=mix(c,(141,84,83),.24*g(ex,.47,.13,.07))
     if d<1.18:c=(48,30,39)
     if d<.78:c=(244,235,223)
     if d<.75 and abs(dx+.08)<.39:c=mix((62,60,66),(150,149,162),sat2((dy+.6)/1.2))
     if d<.72 and abs(dx+.08)<.16:c=(25,23,30)
     if d<.70 and (dx+.22)**2+(dy+.25)**2<.045:c=(255,250,241)
     if abs(dx)<1.10 and abs(v-(.375-.037*dx))<.015:c=(76,68,78)
     if abs(dx)<.91 and abs(v-(.405-.036*dx))<.008:c=mix(c,(128,80,78),.75)
    if f<.033 and abs(v-.677)<.009:c=mix(c,(137,77,70),.62)
    if f<.078 and abs(v-(.786-.009*(1-f/.078)))<.009:c=(110,55,64)
    if f<.05 and abs(v-.805)<.007:c=(207,131,115)
   off=((m//8*128+y)*W+m%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/edgeworth_sculpted.png',W,H,pix)
print('Miles Edgeworth: sculpted angular face, parted silver hair, magenta suit and cravat, upright tea cup with articulated hand and independent objection arm.')


# Leon RE4 remake: angular adult facial planes, ash-blond side fringe, stable aimed gunfire.
p=java/'LeonSculptedClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('import it.noctis.magic.SculptedGuestsClient.Part;','''import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;''',1)
s=s.replace('    static class M extends EntityModel<CrossoverGuest>{','''    static float clampFace(float x){return Math.max(.025f,Math.min(.975f,x));}
    static V face(V v,boolean front){
        return new V(v.x(),v.y(),v.z(),front?clampFace(.5f+v.x()/5.8f):.025f,clampFace((v.y()+7.75f)/7.75f),v.nx(),v.ny(),v.nz());
    }
    static void project(Part p){
        for(int i=0;i<p.faces.size();i++){
            Q q=p.faces.get(i);if(q.tile()!=7)continue;
            boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
            p.faces.set(i,new Q(face(q.a(),f),face(q.b(),f),face(q.c(),f),face(q.d(),f),7));
        }
    }
    static class M extends EntityModel<CrossoverGuest>{''',1)
a=s.index('            head.loft(7,28,');b=s.index('            for(int i=0;i<2;i++){int s=i==0?-1:1;',a)
s=s[:a]+'''            // Long adult face, narrower temples, strong cheekbones and a defined chin.
            head.loft(7,24,-7.75f,0,.12f,1.22f,1.46f,-7.10f,0,.06f,2.08f,2.18f,-5.65f,0,0,2.54f,2.46f,-4.35f,0,-.09f,2.50f,2.42f,-3.22f,0,-.17f,2.34f,2.24f,-2.10f,0,-.25f,2.06f,1.98f,-1.12f,0,-.40f,1.75f,1.58f,-.38f,0,-.48f,1.18f,1.08f,0,0,-.51f,.80f,.77f);
            project(head);
            head.loft(3,16,-4.86f,0,-2.20f,.18f,.12f,-3.92f,0,-2.48f,.27f,.23f,-3.02f,0,-2.86f,.39f,.35f,-2.68f,0,-2.67f,.29f,.15f);
            for(int side:new int[]{-1,1}){
                head.oval(3,side*2.44f,-3.35f,.10f,.30f,.66f,.39f);
                head.blade(3,side*1.55f,-3.32f,-2.00f,side*2.03f,-2.79f,-1.45f,.15f);
            }
            // Low asymmetric crown; long layered sweep passes IN FRONT of left eye.
            head.loft(8,24,-8.60f,.20f,.12f,.78f,.81f,-8.22f,.13f,.18f,2.00f,2.06f,-7.45f,0,.26f,2.70f,2.65f,-6.20f,0,.38f,2.72f,2.65f);
            Part back=head.child(0,-6.78f,1.58f);
            back.loft(8,20,-.64f,0,0,2.27f,1.31f,1.05f,0,.22f,2.45f,1.39f,3.35f,0,.42f,2.18f,1.05f,4.9f,0,.46f,1.36f,.19f);
            // Long swept diagonal locks with independent roots and pointed ends.
            for(int j=0;j<13;j++){
                float t=j/12f;
                float x=-2.12f+t*4.12f;
                Part lock=head.child(x,-7.92f+.12f*t,-2.04f);
                float end=j<8?4.95f-.12f*j:2.35f+(12-j)*.17f;
                float drift=j<8?-.94f-.72f*t:.55f+.16f*t;
                lock.loft(j%3==0?8:9,12,-.42f,0,.40f,.34f,.43f,.35f,drift*.15f,-.30f,.47f,.43f,1.45f,drift*.42f,-.91f,.48f,.33f,end*.69f,drift*.78f,-1.12f,.35f,.20f,end,drift,-.84f,.023f,.032f);
                lock.blade(12,-.10f,.28f,-.58f,drift*.83f,end*.81f,-1.11f,.09f);
            }
            for(int j=0;j<8;j++){
                float t=j/7f;
                Part lock=head.child(-2.2f+t*4.4f,-8.18f+.18f*t,.08f);
                float drift=j<5?-.80f:.55f;
                lock.loft(8,12,-.48f,0,.15f,.34f,.41f,.15f,0,0,.49f,.46f,1.15f,drift*.43f,-.56f,.38f,.31f,2.25f,drift,-1.55f,.025f,.038f);
            }
'''+s[b:]
s=s.replace('s*2.55f,-6.2f,.2f','s*2.30f,-6.2f,.2f',1)
a=s.index('            float a=e.animation()==2?e.action():0;');b=s.index('            for(int i=0;i<hair.size();i++)',a)
s=s[:a]+'''            float a=e.animation()==2?e.action():0;
            float pose=e.aiming()?1:a;
            float aimPitch=Math.max(-1.05f,Math.min(1.05f,pitch*.0174533f));
            body.ry=0;head.ry=yaw*.01745f*(1-pose);head.rx=aimPitch*.82f;
            for(int i=0;i<2;i++){
                int side=i==0?-1:1;float w=(float)Math.cos(limb*.666+i*Math.PI)*amount;
                arms[i].rx=-w*.55f*(1-pose)+pose*(i==1?-1.47f+aimPitch:-1.03f+aimPitch);
                arms[i].rz=-side*.09f*(1-pose)+pose*(i==0?-.28f:0);
                arms[i].ry=pose*(i==0?-.42f:0);
                fore[i].rx=-pose*(i==0?.65f:.10f)-(i==1?a*.055f:0);
                legs[i].rx=w*.65f;calves[i].rx=Math.max(0,-w)*.35f;
            }
'''+s[b:]
# Correct the barrel pivot direction; +Y of slide follows extended forearm toward the target.
s=s.replace('weapon=new Part(0,5.0f,-.55f);','weapon=new Part(0,5.0f,-.30f);',1)
p.write_text(s,encoding='utf-8')
# Rewrite the complete Leon atlas so the projected face is realistic rather than large anime eyes.
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(98,72,57),(166,144,116),(34,34,36),(222,181,153),(137,106,76),(37,36,39),(155,145,131),(222,181,153),(112,95,75),(145,126,100),(53,54,57),(76,80,84),(185,163,130)]
for m,base in enumerate(pal):
 for y in range(128):
  v=sat2((y-3)/121)
  for x in range(128):
   u=sat2((x-3)/121);f=abs(u-.5)
   c=shade(base,.81+.21*math.sin(math.pi*u)+.03*math.sin(x*9.13+y*3.71))
   if m in (0,1,2,5,10):
    grain=(math.sin(x*11.31+y*17.77)*math.cos(x*7.29-y*13.97)+1)*.5
    fold=math.sin(u*math.pi*4+v*3+.4*math.sin(v*7))
    c=mix(c,(38,27,24) if m==0 else (30,27,28),.23*max(0,-fold)**5)
    c=mix(c,(171,129,96) if m==0 else (226,211,185) if m==1 else (98,99,103),(.34 if m==1 else .18)*grain)
   if m in (8,9,12):
    wave=math.sin(u*math.pi*27+v*3+.55*math.sin(v*6))
    c=mix(c,(212,191,157),.37*max(0,wave)**5+.10*math.exp(-((v-.27)/.16)**2))
    c=mix(c,(48,37,31),.44*max(0,-wave)**5)
   if m==7:
    def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
    c=mix(base,(108,65,56),.34*sat2((f-.17)*3.7)+.10*v)
    c=mix(c,(246,210,178),.35*g(.5,.37,.12,.21))
    for side in (-1,1):
     ex=.5+side*.175;dx=side*(u-ex)/.112;dy=(v-(.480-.018*dx))/.031
     c=mix(c,(104,65,62),.45*g(ex,.46,.12,.066)+.25*g(ex,.53,.10,.047))
     c=mix(c,(239,193,157),.25*g(.5+side*.20,.595,.09,.064))
     d=abs(dx)**1.65+abs(dy)**1.25
     if d<1.15:c=(50,36,36)
     if d<.77:c=(210,204,192)
     if d<.74 and abs(dx+.05)<.37:c=mix((53,78,91),(108,142,153),sat2((dy+.6)/1.2))
     if d<.71 and abs(dx+.05)<.15:c=(22,27,34)
     if d<.70 and (dx+.19)**2+(dy+.18)**2<.037:c=(239,237,228)
     if abs(dx)<1.07 and abs(v-(.402-.024*dx))<.014:c=mix((71,50,43),(112,82,62),.30*max(0,math.sin(x*2.3)))
    c=mix(c,(119,69,58),.30*g(.39,.702,.036,.081)+.30*g(.61,.702,.036,.081))
    if f<.055 and abs(v-.679)<.009:c=mix(c,(129,76,66),.68)
    if f<.090 and abs(v-(.779-.009*(1-f/.09)))<.009:c=(96,52,49)
    if f<.071 and abs(v-.803)<.009:c=mix(c,(183,112,101),.70)
    c=mix(c,(119,75,64),.23*g(.5,.844,.11,.022))
    if v>.75 and f<.28 and math.sin(x*17.13+y*19.71)*math.sin(x*13.21-y*7.15)>.7:c=mix(c,(75,57,49),.16)
   off=((m//8*128+y)*W+m%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/leon_sculpted.png',W,H,pix)

# Leon: keep a locked target, aim from the actual shoulder/weapon side, and require an unobstructed shot.
p=java/'CrossoverGuest.java';s=p.read_text(encoding='utf-8')
a=s.index('            if(tickCount%5==0||!validEnemy(getTarget())){');b=s.index('        }else{',a)
s=s[:a]+'''            LivingEntity t=getTarget();
            if(!validEnemy(t)||distanceTo(t)>30){
                if(t!=null)setTarget(null);
                t=null;aimLock=0;
                if(tickCount%6==0){
                    t=l.getEntitiesOfClass(Mob.class,getBoundingBox().inflate(30),m->validEnemy(m)&&hasLineOfSight(m)).stream()
                      .min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
                    setTarget(t);
                }
            }
            if(!validEnemy(t)){
                if(aimLock>0)l.broadcastEntityEvent(this,(byte)106);
                aimLock=0;return;
            }
            Vec3 point=t.getBoundingBox().getCenter();
            double range=distanceTo(t);
            if(!hasLineOfSight(t)||range>22){
                if(aimLock>0)l.broadcastEntityEvent(this,(byte)106);
                aimLock=0;
                if(tickCount%5==0)getNavigation().moveTo(t,1.15);
                return;
            }
            getNavigation().stop();
            Vec3 eye=getEyePosition();
            Vec3 shoulder=eye.add(0,-.34,0);
            Vec3 flat=point.subtract(shoulder);
            double horizontal=Math.max(.15,flat.horizontalDistance());
            // Offset aim to compensate for the weapon held on the right side.
            double yawRad=Math.atan2(-flat.x,flat.z)+Math.asin(Math.min(.75,.35/horizontal));
            Vec3 right=new Vec3(Math.cos(yawRad),0,Math.sin(yawRad));
            shoulder=shoulder.add(right.scale(.35));
            Vec3 dir=point.subtract(shoulder).normalize();
            float yaw=(float)(yawRad*180/Math.PI);
            float pitch=(float)(-Math.atan2(dir.y,dir.horizontalDistance())*180/Math.PI);
            setYRot(yaw);setYHeadRot(yaw);yBodyRot=yaw;setXRot(pitch);
            getLookControl().setLookAt(point.x,point.y,point.z,45,45);
            Vec3 muzzle=shoulder.add(dir.scale(.91));
            var block=l.clip(new net.minecraft.world.level.ClipContext(shoulder,point,net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,this));
            boolean clear=block.getType()==net.minecraft.world.phys.HitResult.Type.MISS;
            if(clear){
                // Don't shoot through neutral mobs, friendly NPCs or other players.
                for(LivingEntity other:l.getEntitiesOfClass(LivingEntity.class,new net.minecraft.world.phys.AABB(shoulder,point).inflate(.20),e->e!=this&&e!=t&&e.isAlive()&&!e.isSpectator())){
                    if(other.getBoundingBox().inflate(.04).clip(shoulder,point).isPresent()){clear=false;break;}
                }
            }
            if(!clear||range<1.15){
                if(aimLock>0)l.broadcastEntityEvent(this,(byte)106);
                aimLock=0;
                if(range<1.15){
                    Vec3 away=position().subtract(t.position()).normalize().scale(.13);
                    if(l.noCollision(this,getBoundingBox().move(away)))setDeltaMovement(away.x,getDeltaMovement().y,away.z);
                }else if(tickCount%5==0)getNavigation().moveTo(t,1.12);
                return;
            }
            aimLock=Math.min(30,aimLock+1);
            if(aimLock==1||tickCount%4==0)l.broadcastEntityEvent(this,(byte)105);
            if(aimLock>=10&&cooldown<=0&&validEnemy(t)){
                cooldown=23;l.broadcastEntityEvent(this,(byte)104);
                l.sendParticles(ParticleTypes.SMALL_FLAME,muzzle.x,muzzle.y,muzzle.z,3,.035,.035,.035,.008);
                l.sendParticles(ParticleTypes.SMOKE,muzzle.x,muzzle.y,muzzle.z,2,.025,.025,.025,.006);
                for(int i=1;i<=12;i++){Vec3 q=muzzle.lerp(point,i/12.0);l.sendParticles(ParticleTypes.CRIT,q.x,q.y,q.z,1,0,0,0,0);}
                t.hurt(damageSources().mobAttack(this),22);
                playSound(SoundEvents.FIREWORK_ROCKET_BLAST,.85f,1.65f);
                if(!t.isAlive()){setTarget(null);aimLock=0;l.broadcastEntityEvent(this,(byte)106);}
            }
'''+s[b:]
# Java lambda uses a final snapshot, not the reassigned local variable.
s=s.replace('            if(clear){\n                // Don','            final LivingEntity locked=t;\n            if(clear){\n                // Don',1)
s=s.replace('e->e!=this&&e!=t&&e.isAlive()','e->e!=this&&e!=locked&&e.isAlive()',1)
s=s.replace('objectionCooldown=500;','objectionCooldown=500;int aimLock=0;',1)
s=s.replace('if(id==105){aimTicks=9;return;}','if(id==106){aimTicks=0;if(animation==2)pose=0;return;}if(id==105){aimTicks=9;return;}',1)
# Avoid idle look-at-player goal pulling the head away while aiming.
s=s.replace('goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));','goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8){@Override public boolean canUse(){return (kind()!=0||getTarget()==null)&&super.canUse();}@Override public boolean canContinueToUse(){return (kind()!=0||getTarget()==null)&&super.canContinueToUse();}});',1)
p.write_text(s,encoding='utf-8')

# Restore requested Yu-Gi-Oh victory joke on both actual ritual and creative egg.
# It triggers only after a successful new spawn; no deletion, ban or repeated kick on rejoin.
for n in ('ExodiaRitual.java','ExodiaEgg.java'):
 p=java/n;s=p.read_text(encoding='utf-8')
 marker='RitualQuests.summon(p,boss,"exodia");'
 i=s.rfind(marker);assert i>=0,n
 s=s[:i]+s[i:].replace(marker,marker+'\n  RitualQuests.complete(p,"exodia");\n  p.connection.disconnect(Component.literal("Hai vinto il duello.").withStyle(ChatFormatting.GOLD,ChatFormatting.BOLD));',1)
 p.write_text(s,encoding='utf-8')
print('Leon: adult projected face, long swept fringe, locked line-of-fire and controlled aim; Exodia victory disconnect restored.')


# Dedicated Arsene mesh: long angular masquerade demon, layered articulated raven wings.
edit('SculptedGuestsClient.java','e.registerEntityRenderer(Noctis.ARSENE.get(),c->new R<Arsene>(c,1));','')
write('ArseneDetailedClient.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class ArseneDetailedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.ARSENE.get(),R::new);}
 static void feather(Part p,int tile,float x,float y,float z,float X,float Y,float Z,float w){
  Part f=p.child(x,y,z);
  float dx=X-x,dy=Y-y,dz=Z-z;
  f.rz=-(float)Math.atan2(dx,dy);
  float length=(float)Math.sqrt(dx*dx+dy*dy);
  f.loft(tile,10,0,0,0,w*.26f,.16f,length*.18f,0,dz*.15f,w*.58f,.29f,length*.48f,.15f,dz*.42f,w*.49f,.22f,length*.79f,.25f,dz*.75f,w*.29f,.14f,length,.45f,dz,.016f,.025f);
  f.blade(5,0,.45f,-.28f,.32f,length*.88f,dz*.84f-.12f,.12f);
 }
 static void cord(Part p,float x,float y,float X,float Y,float z,float sag){
  for(int j=0;j<24;j++){
   float t=j/23f;
   p.oval(4,x+(X-x)*t,y+(Y-y)*t+sag*(float)Math.sin(t*Math.PI),z-.12f*(float)Math.sin(t*Math.PI),.105f,.105f,.105f);
  }
 }
 static class M extends EntityModel<Arsene>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-.9f,0);
  final Part[] arms=new Part[2],elbows=new Part[2],legs=new Part[2],knees=new Part[2],wings=new Part[2],tips=new Part[2],tails=new Part[2];
  M(){
   body.loft(0,20,-.9f,0,0,1.28f,1.05f,.15f,0,0,3.03f,1.57f,2.0f,0,-.10f,2.66f,1.58f,4.3f,0,0,1.80f,1.14f,7.1f,0,0,1.38f,.99f,9.2f,0,0,1.85f,1.26f,10.7f,0,0,2.06f,1.34f);
   body.loft(6,20,-.4f,0,0,1.09f,.98f,.75f,0,-.10f,1.42f,1.21f);
   body.loft(6,20,3.5f,0,-.14f,1.93f,1.34f,5.0f,0,-.16f,1.53f,1.19f,8.5f,0,-.1f,1.48f,1.13f,10.45f,0,-.3f,.78f,.78f);
   for(int side:new int[]{-1,1}){
    body.blade(1,side*1.08f,-.35f,.25f,side*2.37f,-4.2f,.95f,1.64f);
    body.blade(0,side*2.48f,.25f,-1.03f,side*.72f,3.26f,-1.43f,1.63f);
    body.blade(1,side*2.57f,.15f,-.86f,side*2.54f,3.74f,-.55f,1.27f);
    body.blade(3,side*.32f,3.23f,-1.50f,side*1.40f,10.70f,-.73f,.37f);
    for(int j=0;j<4;j++){
     body.blade(1,side*.72f,4.15f+j*.85f,-1.42f,0,4.83f+j*.85f,-1.39f,.26f);
     body.oval(4,side*.74f,4.18f+j*.85f,-1.48f,.10f,.10f,.08f);
    }
    body.blade(6,side*1.42f,8.2f,-.75f,side*.58f,14.0f,.20f,1.7f);
   }
   // Layered white jabot and twin sagging gold chains.
   for(int j=0;j<4;j++){
    float y=.15f+j*.68f,w=1.20f-j*.14f;
    body.loft(2,14,y,0,-1.58f,w*.76f,.23f,y+.24f,0,-1.80f,w,.30f,y+.64f,0,-1.92f,w*.44f,.12f);
    body.blade(9,-w*.70f,y+.31f,-2.02f,w*.55f,y+.48f,-2.01f,.09f);
   }
   cord(body,-2.38f,.22f,2.30f,-.38f,-1.61f,2.90f);
   cord(body,-2.23f,.78f,2.13f,.10f,-1.72f,3.23f);
   // Narrow black mask, sculpted angular red cheek plates, two luminous eye slits.
   head.loft(6,8,-6.3f,0,.17f,.80f,.84f,-5.8f,0,0,1.86f,1.43f,-4.8f,0,-.05f,1.94f,1.53f,-3.1f,0,-.25f,1.37f,1.27f,-.75f,0,-.68f,.30f,.51f,-.45f,0,-.73f,.035f,.08f);
   for(int side:new int[]{-1,1}){
    head.blade(1,side*1.65f,-5.32f,-.87f,side*.31f,-1.20f,-1.38f,.78f);
    head.blade(3,side*1.52f,-5.50f,-1.04f,side*.12f,-1.14f,-1.41f,.22f);
    Part eye=head.child(side*.77f,-3.85f,-1.41f);eye.rz=-side*.38f;
    eye.blade(12,-.65f,0,0,.65f,0,0,.29f);
    head.blade(6,side*.62f,-5.65f,.03f,side*3.9f,-9.1f,.35f,.68f);
    Part ornament=head.child(side*3.32f,-7.05f,.24f);ornament.rz=side*.62f;
    ornament.loft(6,12,-.40f,0,0,.21f,.25f,.0f,0,0,1.36f,.77f,.38f,0,0,.24f,.30f);
    ornament.blade(1,-.85f,0,-.47f,.88f,.12f,-.47f,.29f);
    ornament.blade(3,0,.02f,-.55f,side*.48f,-.12f,-.55f,.19f);
   }
   // The tall hexagonal chimney crown is open-looking, not a conventional top hat.
   head.loft(6,6,-19.35f,0,.40f,1.29f,1.18f,-19.0f,0,.40f,1.30f,1.20f,-12.0f,0,.25f,1.08f,1.09f,-6.04f,0,.06f,.77f,.91f);
   for(int side:new int[]{-1,1})head.blade(3,side*.90f,-18.80f,-.63f,side*.56f,-6.20f,-.70f,.17f);
   head.loft(10,6,-19.38f,0,.40f,.98f,.88f,-19.31f,0,.40f,.98f,.88f);
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;
    arms[i]=body.child(side*3.10f,.15f,0);
    arms[i].loft(0,16,-.30f,0,0,.90f,.92f,.6f,0,0,1.17f,1.09f,2.2f,0,0,.94f,.92f,5.05f,0,0,.67f,.68f);
    arms[i].blade(1,side*.83f,.40f,-.65f,side*.54f,4.88f,-.45f,.27f);
    elbows[i]=arms[i].child(0,5.0f,0);
    elbows[i].loft(0,16,-.15f,0,0,.67f,.68f,1.5f,0,0,.96f,.92f,4.2f,0,0,.60f,.61f);
    elbows[i].loft(1,12,3.48f,0,0,.81f,.78f,4.15f,0,0,.75f,.74f);
    elbows[i].oval(0,0,4.89f,-.10f,.75f,.83f,.53f);
    for(int j=0;j<4;j++){
     float x=-.48f+j*.32f;
     Part finger=elbows[i].child(x,5.2f,-.16f);finger.rz=(j-1.5f)*.19f;
     finger.loft(0,8,0,0,0,.16f,.19f,.52f,0,-.18f,.17f,.16f,.92f,0,-.40f,.11f,.11f);
     finger.loft(6,8,.77f,0,-.33f,.12f,.12f,1.22f,0,-.68f,.10f,.08f,1.56f,0,-.79f,.025f,.025f);
    }
    elbows[i].blade(6,-side*.55f,4.62f,-.22f,-side*.96f,5.63f,-.89f,.40f);
    legs[i]=body.child(side*1.52f,9.75f,0);
    legs[i].loft(0,16,-.46f,0,0,1.36f,1.30f,.95f,0,0,1.43f,1.32f,3.45f,0,0,1.10f,1.06f,7.05f,0,0,.65f,.68f);
    for(int j=0;j<3;j++)legs[i].blade(1,side*(.50f+j*.26f),.65f,-1.12f,side*(.30f+j*.15f),6.32f,-.66f,.46f);
    knees[i]=legs[i].child(0,6.9f,0);
    knees[i].loft(0,14,-.24f,0,0,.66f,.65f,1.5f,0,0,.76f,.74f,4.5f,0,.07f,.53f,.54f,7.2f,0,-.09f,.36f,.40f,8.6f,0,-.55f,.18f,.27f);
    knees[i].loft(6,10,7.7f,0,-.18f,.37f,.40f,8.7f,0,-.67f,.36f,.50f,9.5f,0,-1.29f,.035f,.07f);
    knees[i].blade(3,side*.47f,4.7f,.34f,side*.88f,2.87f,1.43f,.61f);
    knees[i].blade(6,side*.44f,6.0f,.30f,side*.88f,4.85f,1.18f,.52f);
    tails[i]=body.child(side*1.38f,7.5f,1.1f);
    tails[i].blade(0,0,0,0,side*1.7f,10.5f,2.35f,2.2f);
    tails[i].blade(6,0,1.8f,.21f,side*.75f,9.4f,2.42f,1.2f);
    // Two joints per wing, with independent curved primaries and three rows of overlapping coverts.
    Part wing=wings[i]=body.child(side*2.18f,.25f,1.62f);
    feather(wing,7,0,0,.3f,side*12.2f,-3.0f,1.0f,4.4f);
    for(int j=0;j<12;j++){
     float t=j/11f;
     feather(wing,7,side*(.8f+10.7f*t),-.35f-2.6f*t,.4f,side*(2.4f+11.4f*t),11.6f-4.4f*t,1.55f,1.65f+1.0f*t);
    }
    for(int row=0;row<3;row++)for(int j=0;j<11;j++){
     float t=j/10f;
     feather(wing,row%2==0?8:7,side*(.75f+10.8f*t),-.9f-2.4f*t+row*1.38f,-.40f-row*.14f,side*(1.9f+11.1f*t),2.7f+row*1.8f-1.65f*t,.10f,1.72f);
    }
    Part tip=tips[i]=wing.child(side*10.8f,-2.7f,1.15f);
    feather(tip,7,0,0,0,side*10.2f,5.8f,.6f,3.3f);
    for(int j=0;j<13;j++){
     float t=j/12f;
     feather(tip,7,side*(.10f+9.4f*t),.12f+4.9f*t,.1f,side*(1.5f+11.3f*t),12.8f+7.2f*t,1.40f+1.3f*t,2.35f-.54f*t);
    }
    for(int row=0;row<3;row++)for(int j=0;j<10;j++){
     float t=j/9f;
     feather(tip,row==1?7:8,side*(.1f+9.0f*t),.1f+4.1f*t+row*1.40f,-.4f-.14f*row,side*(1.1f+10.0f*t),3.4f+6.0f*t+row*1.80f,.2f,1.66f);
    }
   }
  }
  @Override public void setupAnim(Arsene e,float limb,float amount,float age,float yaw,float pitch){
   float cast=e.casting(),wave=(float)Math.sin(age*.095f);
   root.y= -1.0f+wave*.38f;body.rz=.09f+cast*.07f;
   head.ry=yaw*.012f;head.rx=pitch*.009f;head.rz=-.10f;
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;
    arms[i].rx=i==0?-.12f-cast*.72f:-.70f-cast*.53f;
    arms[i].rz=-side*(i==0?.78f:1.13f)-side*cast*.28f;
    elbows[i].rx=i==0?-.38f:-.80f;
    legs[i].rz=side*(i==0?.32f:.24f);legs[i].rx=i==0?-.58f:.20f;
    knees[i].rx=i==0?.88f:.13f;
    tails[i].rx=.18f+wave*.10f;tails[i].rz=side*.13f;
    wings[i].ry=side*(.13f+wave*.25f+cast*.20f);wings[i].rz=side*(.06f+wave*.11f);
    tips[i].ry=side*(.14f+wave*.23f);tips[i].rz=side*(-.10f+wave*.11f);
   }
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<Arsene,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.70f);}
  @Override protected void scale(Arsene e,PoseStack p,float partial){p.scale(1.33f,1.33f,1.33f);}
  @Override public ResourceLocation getTextureLocation(Arsene e){return new ResourceLocation(Noctis.ID,"textures/entity/arsene_detailed.png");}
 }
}''')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(155,15,39),(210,30,49),(235,233,225),(99,104,125),(218,168,65),(74,80,102),(27,29,41),(22,25,39),(39,43,61),(128,130,145),(9,11,19),(72,10,27),(255,57,36)]
for m,base in enumerate(pal):
 for y in range(128):
  v=sat2((y-3)/121)
  for x in range(128):
   u=sat2((x-3)/121)
   c=shade(base,.72+.28*math.sin(math.pi*u))
   if m in (0,1,6):
    c=mix(c,(242,92,91) if m<2 else (108,116,143),.32*math.exp(-((u-.33)/.12)**2))
    c=mix(c,(43,7,21) if m<2 else (7,10,18),.36*math.exp(-((u-.78)/.15)**2))
    c=shade(c,.93+.07*math.sin(u*48+v*19)**2)
   if m in (7,8):
    vein=math.sin((u-.5)*math.pi*28+v*14)
    c=mix(c,(88,103,134),.27*max(0,vein)**5+.15*math.exp(-((u-.48)/.07)**2))
    c=mix(c,(7,9,16),.35*max(0,-vein)**5+.15*v)
   if m==4:c=mix(c,(255,233,153),.55*math.sin(math.pi*u)**2)
   if m==12:c=mix((255,40,27),(255,193,122),.70*math.sin(math.pi*u)**2)
   off=((m//8*128+y)*W+m%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/arsene_detailed.png',W,H,pix)

# Sculpt narrower heads with real profile changes, not merely a new skin.
write('AngularHeads.java','''package it.noctis.magic;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
final class AngularHeads{
 static V shape(V v,float width,float length,float depth,float taper,boolean face){
  float y=v.y(),lower=Math.max(0,Math.min(1,(y+4.0f)/4.0f));
  float k=width*(face?1-taper*lower:1);
  return new V(v.x()*k,y*length,v.z()*depth,v.u(),v.v(),v.nx(),v.ny(),v.nz());
 }
 static void apply(Part p,int faceTile,float width,float length,float depth,float taper){
  for(int i=0;i<p.faces.size();i++){
   Q q=p.faces.get(i);boolean face=q.tile()==faceTile;
   p.faces.set(i,new Q(shape(q.a(),width,length,depth,taper,face),shape(q.b(),width,length,depth,taper,face),shape(q.c(),width,length,depth,taper,face),shape(q.d(),width,length,depth,taper,face),q.tile()));
  }
  for(Part child:p.children){
   child.x*=width;child.y*=length;child.z*=depth;
   apply(child,-1,width,1,depth,0);
  }
 }
}''')
for file,tile,expr in [('JokerDetailedClient.java',7,'AngularHeads.apply(head,7,.86f,.96f,.94f,.17f);'),('GeassSculptedClient.java',6,'AngularHeads.apply(head,6,cc?.85f:.82f,.98f,.94f,cc?.16f:.19f);'),('GiornoSculptedClient.java',5,'AngularHeads.apply(head,5,.86f,.97f,.93f,.15f);')]:
 p=java/file;s=p.read_text(encoding='utf-8')
 # apply once at the end of the mesh constructor, after all hair and facial features exist.
 a=s.index('@Override public void setupAnim')
 b=s.rfind('}',0,a);assert b>=0,file
 s=s[:b]+expr+'\n  '+s[b:]
 p.write_text(s,encoding='utf-8')
# More refined face shading and individual hair striations; preserve the existing eye positions and mask.
for name,face_tile,hair_tile in [('joker_detailed',7,9),('cc_sculpted',6,8),('lelouch_sculpted',6,8),('giorno_sculpted',5,6)]:
 p=assets/'textures/entity'/f'{name}.png';w,h,pix=read_rgba(p)
 for y in range(128):
  v=sat2((y-3)/121)
  for x in range(128):
   u=sat2((x-3)/121);f=abs(u-.5)
   off=((face_tile//8*128+y)*w+face_tile%8*128+x)*4
   c=tuple(pix[off:off+3])
   # cheeks and temples receive directional contour; do not paint over eye/lip ink.
   if c[0]>c[1]*1.08 and c[1]>100 and .54<v<.76:
    g=math.exp(-((f-(.22-.29*(v-.55)))/.06)**2)
    c=mix(c,(110,61,66),.23*g*math.sin(math.pi*sat2((v-.54)/.22)))
    c=mix(c,(255,219,190),.16*math.exp(-((f-.11)/.055)**2))
   pix[off:off+4]=bytes((*c,255))
   off=((hair_tile//8*128+y)*w+hair_tile%8*128+x)*4
   c=tuple(pix[off:off+3]);wave=math.sin(u*math.pi*40+v*4.2+.46*math.sin(v*8))
   c=shade(c,.90+.15*max(0,wave)**5+.04*math.sin(v*13))
   pix[off:off+4]=bytes((*c,255))
 png(p,w,h,pix)

# Leon crouches while fighting, advances on distant enemies and strafes around nearby ones.
p=java/'CrossoverGuest.java';s=p.read_text(encoding='utf-8')
s=s.replace('int aimLock=0;','int aimLock=0;int strafeSide=1;',1)
s=s.replace('aimLock=0;return;\n            }\n            Vec3 point=', 'aimLock=0;setShiftKeyDown(false);return;\n            }\n            setShiftKeyDown(true);\n            Vec3 point=',1)
s=s.replace('            getNavigation().stop();\n            Vec3 eye=getEyePosition();','''            // Approach until firing distance, then periodically flank on traversable ground.
            if(tickCount%12==0){
                if(range>9.0)getNavigation().moveTo(t,1.08);
                else if(range>2.4){
                    if(tickCount%60==0)strafeSide=-strafeSide;
                    Vec3 toward=t.position().subtract(position()).multiply(1,0,1).normalize();
                    Vec3 side=new Vec3(-toward.z,0,toward.x).scale(strafeSide*2.4);
                    Vec3 dest=position().add(side).add(toward.scale(range>6?1.4:range<4?-1.3:0));
                    var path=getNavigation().createPath(net.minecraft.core.BlockPos.containing(dest.x,dest.y,dest.z),0);
                    if(path!=null&&path.canReach())getNavigation().moveTo(path,.86);
                    else{strafeSide=-strafeSide;getNavigation().stop();}
                }else getNavigation().stop();
            }
            Vec3 eye=getEyePosition();''',1)
# Synchronize sneak pose via existing entity flag; clear it immediately when no target remains.
s=s.replace('if(!t.isAlive()){setTarget(null);aimLock=0;l.broadcastEntityEvent(this,(byte)106);}','if(!t.isAlive()){setTarget(null);aimLock=0;setShiftKeyDown(false);l.broadcastEntityEvent(this,(byte)106);}',1)
p.write_text(s,encoding='utf-8')
p=java/'LeonSculptedClient.java';s=p.read_text(encoding='utf-8')
s=s.replace('float pose=e.aiming()?1:a;','float pose=e.aiming()?1:a;\n            float crouch=e.isShiftKeyDown()?1:0;\n            root.y=1.8f*crouch;body.rx=.13f*crouch;head.rx=-.10f*crouch;',1)
s=s.replace('head.rx=aimPitch*.82f;','head.rx=aimPitch*.82f-.13f*crouch;',1)
s=s.replace('arms[i].rx=-w*.55f*(1-pose)+pose*(i==1?-1.47f+aimPitch:-1.03f+aimPitch);','arms[i].rx=-w*.55f*(1-pose)+pose*(i==1?-1.47f+aimPitch:-1.03f+aimPitch)-.13f*crouch;',1)
s=s.replace('legs[i].rx=w*.65f;calves[i].rx=Math.max(0,-w)*.35f;','legs[i].rx=w*.58f-.33f*crouch;calves[i].rx=Math.max(0,-w)*.35f+.60f*crouch;',1)
p.write_text(s,encoding='utf-8')
print('Dedicated Arsene, narrower non-chibi heads, refined facial and hair textures, Leon combat crouch/approach/flank.')


# Faputa: connected neck, lower feral stance, angular face and narrower predatory eyes.
p=java/'FaputaSculptedClient.java';s=p.read_text(encoding='utf-8')
def fap_replace(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b,1)
fap_replace('import it.noctis.magic.SculptedGuestsClient.Part;', '''import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;''')
fap_replace('  M(){','''  static V faceV(V v,boolean front){
   float u=front?Math.max(.025f,Math.min(.975f,.5f+v.x()/6.4f)):.025f;
   float y=Math.max(.025f,Math.min(.975f,(v.y()+6.9f)/6.9f));
   return new V(v.x(),v.y(),v.z(),u,y,v.nx(),v.ny(),v.nz());
  }
  static void projectFace(Part p){
   for(int i=0;i<p.faces.size();i++){
    Q q=p.faces.get(i);if(q.tile()!=5)continue;
    boolean front=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
    p.faces.set(i,new Q(faceV(q.a(),front),faceV(q.b(),front),faceV(q.c(),front),faceV(q.d(),front),5));
   }
  }
  M(){
   // Continuous neck reaches inside the skull and blends into the shoulder girdle.
   body.loft(0,24,-4.40f,0,-.40f,.76f,.82f,-3.75f,0,-.36f,.91f,.95f,-3.0f,0,-.22f,1.05f,1.08f,-2.15f,0,-.05f,1.46f,1.20f,-1.30f,0,.05f,1.80f,1.40f);
   for(int side:new int[]{-1,1}){
    body.loft(0,16,-3.72f,side*.48f,-.24f,.37f,.45f,-2.44f,side*.85f,-.12f,.59f,.55f,-1.15f,side*1.72f,.16f,.73f,.73f);
   }''')
a=s.index('   head.loft(5,48,');b=s.index('   // Cream crown',a)
s=s[:a]+'''   // Tapered cheekbones, less spherical muzzle and a pointed chin.
   head.loft(5,32,-6.8f,0,.15f,1.08f,1.22f,-6.2f,0,.09f,2.23f,2.12f,-4.85f,0,0,2.82f,2.52f,-3.40f,0,-.09f,2.73f,2.49f,-2.25f,0,-.17f,2.29f,2.19f,-1.18f,0,-.32f,1.68f,1.74f,-.33f,0,-.39f,.96f,1.04f,0,0,-.40f,.49f,.63f);
   projectFace(head);
   head.oval(0,0,-2.35f,-2.48f,.23f,.18f,.20f);
   for(int side:new int[]{-1,1}){
    // Small sculpted outer brow ridge adds a permanent predatory expression.
    head.blade(0,side*.56f,-3.82f,-2.45f,side*1.91f,-4.40f,-1.91f,.24f);
   }
'''+s[b:]
fap_replace('body.y=8+(float)Math.sin(limb*1.32)*move*.22f;body.rx=rage?.09f:0;', '''// Hunched shoulders and lowered hips at rest; deeper crouch when enraged.
   body.y=9.25f+(rage?.45f:0)+(float)Math.sin(limb*1.32)*move*.24f;
   body.rx=rage?-.32f:-.20f-move*.06f;
   head.z=-.35f-(rage?.38f:.14f);
   head.y=-3.5f;''')
# Model coordinates: negative local Z is forward, so positive torso rotation brings the upper torso forward.
# Pivot is high on the torso; set a positive lean, not a backward lean.
s=s.replace('body.rx=rage?-.32f:-.20f-move*.06f;','body.rx=rage?.32f:.20f+move*.06f;')
fap_replace('head.ry=yaw*.01745f;head.rx=pitch*.012f-(rage?.13f:0);','head.ry=yaw*.01745f;head.rx=pitch*.010f-body.rx+(rage?.06f:.02f);head.rz=(float)Math.sin(age*.065f)*.025f;')
fap_replace('legs[i].rx=w*.72f;feet[i].rx=Math.max(0,-w)*.32f;', '''legs[i].rx=w*.57f-.40f-(rage?.12f:0);
    legs[i].rz=s*.11f;
    feet[i].rx=.62f+Math.max(0,-w)*.24f-body.rx;''')
fap_replace('arms[k].rx=-w*(j==0?.26f:-.24f)-hit*(j==0?1.25f:.80f)-(rage?.35f:0);','arms[k].rx=-.30f-w*(j==0?.26f:-.24f)-hit*(j==0?1.25f:.80f)-(rage?.32f:0);')
fap_replace('fore[k].rx=-hit*.75f+(j==0?-.12f:-.35f);','fore[k].rx=-hit*.75f+(j==0?-.28f:-.52f);')
p.write_text(s,encoding='utf-8')
# Repaint only the facial tile; retain the existing fur, markings, claws, jewelry and other materials.
for rage in (False,True):
 p=assets/'textures/entity'/('faputa_rage.png' if rage else 'faputa_sculpted.png')
 W,H,pix=read_rgba(p)
 for y in range(128):
  v=sat2((y-3)/121)
  for x in range(128):
   u=sat2((x-3)/121);f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   c=mix((128,99,76),(73,47,43),.23*sat2((f-.14)*4)+.10*v)
   c=mix(c,(173,133,95),.22*g(.50,.47,.13,.24))
   for side in (-1,1):
    ex=.5+side*.184;dx=side*(u-ex)/.108
    ey=.515-.067*dx
    dy=(v-ey)/(.066 if rage else .077)
    d=abs(dx)**1.65+abs(dy)**1.35
    c=mix(c,(58,36,35),.38*g(ex,.50,.13,.088))
    c=mix(c,(162,115,84),.20*g(.5+side*.22,.64,.075,.065))
    if d<1.15:c=(44,23,26)
    if d<.82:c=(229,210,170)
    if d<.79 and abs(dx+.045)<.46:
     c=mix((143,28,24) if rage else (149,97,26),(255,144,53) if rage else (248,202,82),sat2((dy+.75)/1.5))
     if abs(dx+.045)<(.085 if rage else .12):c=(27,19,19)
     if (dx+.18)**2+(dy+.24)**2<.032:c=(255,243,209)
    if abs(dx)<1.08 and abs(v-(ey-.050))<.017:c=(46,27,27)
    if abs(dx)<1.13 and abs(v-(.421-.067*dx))<.017:c=(67,40,37)
    if abs(dx)<.90 and abs(v-(ey+.074))<.008:c=mix(c,(72,42,38),.63)
   if f<.036 and abs(v-.677)<.010:c=mix(c,(69,39,35),.70)
   # Tight asymmetric snarl; berserk exposes a small sharp ivory fang.
   mouth=.783-.023*(1-min(1,f/.11))+.042*(u-.5)
   if f<.112 and abs(v-mouth)<(.027 if rage else .012):c=(49,23,27)
   if rage and .047<f<.083 and mouth-.015<v<mouth+.018:c=(241,226,195)
   if f<.072 and abs(v-.821)<.009:c=mix(c,(174,109,83),.68)
   off=(y*W+5*128+x)*4;pix[off:off+4]=bytes((*c,255))
 png(p,W,H,pix)
print('Faputa: neck joins head and shoulders, feral crouched stance, angular face, narrow golden/red predatory eyes.')


# Lucy: planar face UV projection prevents the cylindrical mesh from stretching the eyes outward.
p=java/'LucySculptedClient.java';s=p.read_text(encoding='utf-8')
assert 'import it.noctis.magic.SculptedGuestsClient.Part;' in s
s=s.replace('import it.noctis.magic.SculptedGuestsClient.Part;','''import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;''',1)
a=s.index('   head.loft(6,20,');b=s.index('   head.oval(7,0,-2.75f',a)
s=s[:a]+'''   head.loft(6,64,-7.65f,0,.18f,1.2f,1.55f,-7.15f,0,.10f,2.40f,2.30f,-5.8f,0,0,3.02f,2.70f,-4.25f,0,-.05f,3.04f,2.74f,-3.0f,0,-.10f,2.73f,2.49f,-1.55f,0,-.16f,2.08f,1.99f,-.45f,0,-.25f,.95f,1.21f,0,0,-.30f,.42f,.65f);
   for(int i=0;i<head.faces.size();i++){
    Q q=head.faces.get(i);if(q.tile()!=6)continue;
    boolean front=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;
    head.faces.set(i,new Q(faceUV(q.a(),front),faceUV(q.b(),front),faceUV(q.c(),front),faceUV(q.d(),front),6));
   }
'''+s[b:]
s=s.replace('  M(){','''  static V faceUV(V v,boolean front){
   float u=front?Math.max(.025f,Math.min(.975f,.5f+v.x()/6.5f)):.025f;
   float y=Math.max(.025f,Math.min(.975f,(v.y()+7.65f)/7.65f));
   return new V(v.x(),v.y(),v.z(),u,y,v.nx(),v.ny(),v.nz());
  }
  M(){''',1)
# The original round raised nose looked like a button; replace with a small tapered bridge.
s=s.replace('head.oval(7,0,-2.75f,-2.61f,.29f,.41f,.34f);','head.loft(7,16,-4.12f,0,-2.63f,.12f,.08f,-3.30f,0,-2.73f,.19f,.15f,-2.72f,0,-2.88f,.26f,.19f,-2.46f,0,-2.65f,.16f,.10f);',1)
p.write_text(s,encoding='utf-8')

p=assets/'textures/entity/lucy_sculpted.png';W,H,pix=read_rgba(p)
# Both eye centers share exactly the same height and pupil offset, with mirror-symmetric makeup.
# Supersample the face tile to soften aliasing while keeping the original atlas dimensions.
def lucy_face(u,v):
 f=abs(u-.5)
 def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
 c=mix((250,226,212),(169,111,128),.18*sat2((f-.17)*4)+.12*g(.5,.77,.25,.18))
 c=mix(c,(255,241,227),.20*g(.5,.40,.18,.21))
 for side in (-1,1):
  ex=.5+side*.171
  dx=(u-ex)/.116;out=side*dx
  ey=.472-.018*out
  dy=(v-ey)/.049
  d=abs(dx)**1.65+abs(dy)**1.35
  c=mix(c,(185,133,157),.20*g(ex,.45,.125,.077))
  # Coral liner is narrow and follows the same mirrored lower lid on both sides.
  if abs(dx)<1.02 and .86<dy<1.27-.26*abs(dx):
   c=mix(c,(203,65,83),.86)
  if d<1.12:c=(42,28,49)
  if d<.81:c=(245,243,239)
  # A matched centered gaze, not outward-facing pupils.
  if d<.79 and (dx/.40)**2+(dy/.88)**2<1:
   t=sat2((dy+.65)/1.3)
   c=mix((99,91,160),(113,209,188),t)
   if (dx/.155)**2+(dy/.74)**2<1:c=(30,29,54)
   if (dx+.12)**2+(dy+.23)**2<.035:c=(255,254,249)
  if abs(dx)<1.05 and abs(dy+.72-.12*out)<.11:c=(38,25,47)
  if abs(dx)<.97 and abs(v-(.367-.017*out))<.010:c=(127,111,156)
 if f<.027 and abs(v-.678)<.008:c=mix(c,(165,103,120),.55)
 if f<.060 and abs(v-(.793-.011*(1-f/.06)))<.008:c=(139,65,86)
 if f<.045 and abs(v-.810)<.008:c=mix(c,(213,118,139),.74)
 return c
for y in range(128):
 for x in range(128):
  samples=[lucy_face(sat2((x+dx-3)/121),sat2((y+dy-3)/121)) for dx,dy in ((-.25,-.25),(.25,-.25),(-.25,.25),(.25,.25))]
  c=tuple(round(sum(t[k] for t in samples)/4) for k in range(3))
  off=(y*W+6*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(p,W,H,pix)
print('Lucy: projected face UVs, matched centered pupils, symmetrical smaller almond eyes and subtle coral makeup.')


# Reliable rebindable cast input and diagnostics; preserve all spell restrictions and server-side validation.
p=java/'Client.java';s=p.read_text(encoding='utf-8')
a='while(CAST.consumeClick())Noctis.NET.sendToServer(new Noctis.Cast(selected));'
assert a in s,a
s=s.replace(a,'while(CAST.consumeClick()){}',1)
a='while(MENU.consumeClick())mc.setScreen(new SpellScreen());'
assert a in s,a
s=s.replace(a,'while(MENU.consumeClick()){}',1)
# Raw Forge key event avoids lost key presses when other mod key mappings share R/G.
a='public static class Input {'
assert a in s,a
s=s.replace(a,'''public static class Input {
        @SubscribeEvent public static void magicKey(InputEvent.Key e){
            Minecraft mc=Minecraft.getInstance();
            if(e.getAction()!=GLFW.GLFW_PRESS||mc.player==null||mc.screen!=null||mc.getConnection()==null)return;
            if(CAST.matches(e.getKey(),e.getScanCode())){
                selected=Math.max(0,Math.min(Noctis.Spell.values().length-1,selected));
                Noctis.NET.sendToServer(new Noctis.Cast(selected));
                return;
            }
            if(MENU.matches(e.getKey(),e.getScanCode()))mc.setScreen(new SpellScreen());
        }
''',1)
a=s.index('    @SubscribeEvent public static void overlay(RegisterGuiOverlaysEvent');b=s.index('    @Mod.EventBusSubscriber',a)
s=s[:a]+'''    static float displayMana=-1;static int lastLevel=-1;
    static int limit(int v,int lo,int hi){return Math.max(lo,Math.min(hi,v));}
    static void diamond(GuiGraphics g,int cx,int cy,int r,int color){
        for(int j=-r;j<=r;j++){int w=r-Math.abs(j);g.fill(cx-w,cy+j,cx+w+1,cy+j+1,color);}
    }
    @SubscribeEvent public static void overlay(RegisterGuiOverlaysEvent e){
        e.registerAboveAll("mana",(gui,g,partial,w,h)->{
            Minecraft mc=Minecraft.getInstance();if(mc.player==null||mc.options.hideGui||mc.player.isSpectator())return;
            int lv=limit(Noctis.View.level,1,10),max=Math.max(1,Noctis.max(lv)),mana=limit(Noctis.View.mana,0,max);
            int x=20,y=h-64,bw=Math.max(100,Math.min(158,w/2-32)),bh=11;
            if(displayMana<0||lastLevel!=lv){displayMana=mana;lastLevel=lv;}
            displayMana+=(mana-displayMana)*.16f;
            int fill=limit(Math.round(bw*displayMana/max),0,bw);
            int real=limit(bw*mana/max,0,bw);
            selected=limit(selected,0,Noctis.Spell.values().length-1);
            Noctis.Spell spell=Noctis.Spell.values()[selected];
            int cd=Math.max(0,Noctis.View.cooldown);
            boolean ready=mana>=spell.cost&&lv>=spell.level&&cd==0;
            // Dark grimoire plaque with brass double border, beveled purple core, arcane endcaps.
            g.fill(x-9,y-17,x+bw+9,y+33,0xB00D0B18);
            g.fill(x-7,y-1,x+bw+7,y+bh+3,0xFF47334B);
            g.fill(x-6,y-2,x+bw+6,y+bh+2,0xFFB69A67);
            g.fill(x-4,y-1,x+bw+4,y+bh+1,0xFF211B32);
            g.fill(x,y,x+bw,y+bh,0xFF100D25);
            if(fill>0){
                g.fillGradient(x,y,x+fill,y+bh,0xFF6845B8,0xFF291A64);
                g.fillGradient(x,y+1,x+fill,y+5,0xFFC5ABFF,0xFF8156E4);
                g.fill(x,y+1,x+fill,y+2,0xFFDED1FF);
                for(int j=0;j<fill;j+=8)g.fill(x+j,y+3,x+j+1,y+bh-1,0x3077DDFF);
            }
            if(real>1){int spark=x+real-1;g.fill(spark,y+1,spark+1,y+bh-1,0xFFF0E4FF);}
            for(int j=1;j<5;j++){int k=x+bw*j/5;g.fill(k,y+bh-3,k+1,y+bh,0xFF735D98);}
            diamond(g,x-6,y+5,8,0xFF594263);diamond(g,x-6,y+5,6,0xFFCEAD70);
            diamond(g,x-6,y+5,4,ready?0xFFC8A5FF:0xFF5A426F);diamond(g,x-6,y+5,1,0xFFF8E8FF);
            diamond(g,x+bw+5,y+5,5,0xFFB69A67);diamond(g,x+bw+5,y+5,3,0xFF573C91);
            g.drawString(mc.font,"MANA  "+mana+"/"+max,x,y-12,0xFFEADFFF);
            String lvl="Lv "+lv;g.drawString(mc.font,lvl,x+bw-mc.font.width(lvl),y-12,0xFFFFDA91);
            int exp=lv==10?bw:limit(bw*Noctis.View.xp/Math.max(1,Noctis.needed(lv)),0,bw);
            g.fill(x,y+14,x+bw,y+17,0xFF302538);g.fillGradient(x,y+14,x+exp,y+17,0xFFFBE3A1,0xFF9A663E);
            String label=spell.label;
            if(mc.font.width(label)>bw+2)label=mc.font.plainSubstrByWidth(label,bw-9)+"...";
            g.drawString(mc.font,label,x,y+20,ready?0xFFEBDFFF:0xFFBCADC9);
            String state=cd>0?String.format(java.util.Locale.ROOT,"%.1fs",cd/20f):lv<spell.level?"Lv "+spell.level:mana<spell.cost?"Mana!":spell.cost+" MP";
            String keys=CAST.getTranslatedKeyMessage().getString()+"/"+MENU.getTranslatedKeyMessage().getString();
            g.drawString(mc.font,keys+"  "+state,x,y+31,ready?0xFFBDEBC9:0xFFFFB58D);
        });
    }
'''+s[b:]
p.write_text(s,encoding='utf-8')
# Recover old/incomplete player records and make all rejected casts visible to the player.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
a='return all.getCompound(ID);'
assert a in s,a
s=s.replace(a,'''CompoundTag d=all.getCompound(ID);
        if(!d.contains("level")||d.getInt("level")<1)d.putInt("level",1);
        if(d.getInt("level")>10)d.putInt("level",10);
        if(!d.contains("mana"))d.putInt("mana",max(d.getInt("level")));
        if(d.getInt("mana")<0)d.putInt("mana",0);
        if(d.getInt("mana")>max(d.getInt("level")))d.putInt("mana",max(d.getInt("level")));
        if(d.getInt("cooldown")<0||d.getInt("cooldown")>1200)d.putInt("cooldown",0);
        return d;''',1)
a='if(d.getInt("cooldown")>0)return;'
assert a in s,a
s=s.replace(a,'if(d.getInt("cooldown")>0){tell(p,"Magia in ricarica: "+((d.getInt("cooldown")+19)/20)+" s");sync(p);return;}',1)
p.write_text(s,encoding='utf-8')

# Play a short nonsexual hurt vocalization on each accepted hit (no interaction cooldown).
p=java/'NpcPain.java';s=p.read_text(encoding='utf-8')
s=s.replace('e.getAmount()<=0||m.getType()!=Noctis.WAIFU.get()&&!(m instanceof CabaretHealer)','e.getAmount()<=0||!(m instanceof CabaretHealer)',1)
p.write_text(s,encoding='utf-8')
write('AdmirerHurtVoice.java','''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class AdmirerHurtVoice{
 @SubscribeEvent(priority=EventPriority.LOWEST) public static void hurt(LivingHurtEvent e){
  var m=e.getEntity();if(!(m.level() instanceof ServerLevel l)||e.getAmount()<=0)return;
  boolean slime=m.getType()==Noctis.SLIME_LADY.get();
  if(!slime&&m.getType()!=Noctis.WAIFU.get())return;
  float pitch=(slime?1.55f:1.25f)+m.getRandom().nextFloat()*.24f;
  l.playSound(null,m.getX(),m.getY(),m.getZ(),SoundEvents.PLAYER_HURT,SoundSource.NEUTRAL,1f,pitch);
 }
}''')

# Michael Jackson: dedicated adult sculpted Billie Jean stage outfit and articulated dance.
edit('DramaClient.java','e.registerEntityRenderer(Noctis.MICHAEL_JACKSON.get(),c->new Renderer(c,0));','')
write('MoonwalkSculptedClient.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class MoonwalkSculptedClient{
 @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.MICHAEL_JACKSON.get(),R::new);}
 static float cl(float n){return Math.max(.025f,Math.min(.975f,n));}
 static V uv(V v,boolean front){return new V(v.x(),v.y(),v.z(),front?cl(.5f+v.x()/6.1f):.025f,cl((v.y()+7.8f)/7.8f),v.nx(),v.ny(),v.nz());}
 static class M extends EntityModel<DramaGuest>{
  final Part root=new Part(0,0,0),body=root.child(0,0,0),head=body.child(0,-1.4f,0),hat=head.child(0,-7.3f,0);
  final Part[] arms=new Part[2],fore=new Part[2],legs=new Part[2],shins=new Part[2],shoes=new Part[2];
  M(){
   body.loft(0,24,-.9f,0,0,1.45f,1.13f,.20f,0,0,3.68f,1.77f,2.7f,0,-.06f,3.15f,1.70f,5.3f,0,0,2.54f,1.40f,8.6f,0,0,2.38f,1.32f,10.9f,0,0,2.88f,1.64f);
   body.loft(5,20,-2.15f,0,0,.92f,.91f,-.55f,0,0,1.14f,1.04f);
   body.blade(1,0,.05f,-1.48f,0,9.25f,-1.45f,2.80f);
   body.blade(1,-.90f,-.15f,-1.08f,0,1.60f,-1.70f,.93f);
   body.blade(1,.90f,-.15f,-1.08f,0,1.60f,-1.70f,.93f);
   for(int side:new int[]{-1,1}){
    body.blade(2,side*2.91f,.50f,-1.36f,side*.82f,5.6f,-1.73f,1.15f);
    body.blade(0,side*2.67f,5.8f,-1.05f,side*2.45f,11.55f,-.82f,1.4f);
    body.blade(4,side*2.78f,6.9f,-1.18f,side*1.61f,7.06f,-1.32f,.13f);
   }
   for(int j=0;j<4;j++)body.oval(4,0,2.2f+j*1.35f,-1.72f,.10f,.12f,.06f);
   body.loft(2,24,9.65f,0,0,2.61f,1.43f,10.18f,0,0,2.73f,1.54f);
   body.oval(4,0,9.94f,-1.59f,.44f,.28f,.14f);
   // Adult face with cheekbones, defined jaw, tapered nose and dark eyes.
   head.loft(6,48,-7.8f,0,.18f,1.10f,1.34f,-7.2f,0,.08f,2.25f,2.13f,-5.65f,0,0,2.69f,2.44f,-4.15f,0,-.10f,2.59f,2.37f,-2.65f,0,-.19f,2.12f,2.07f,-1.2f,0,-.36f,1.43f,1.47f,-.30f,0,-.47f,.81f,.89f,0,0,-.47f,.53f,.65f);
   for(int j=0;j<head.faces.size();j++){Q q=head.faces.get(j);if(q.tile()!=6)continue;boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.05f;head.faces.set(j,new Q(uv(q.a(),f),uv(q.b(),f),uv(q.c(),f),uv(q.d(),f),6));}
   head.loft(5,16,-4.68f,0,-2.26f,.15f,.12f,-3.75f,0,-2.49f,.22f,.21f,-3.0f,0,-2.83f,.32f,.28f,-2.74f,0,-2.60f,.22f,.14f);
   for(int side:new int[]{-1,1}){head.oval(5,side*2.55f,-3.52f,.04f,.30f,.63f,.38f);}
   // Glossy black curls at the temples, nape and iconic loose forehead lock.
   head.loft(3,24,-8.25f,0,.1f,1.64f,1.48f,-7.7f,0,.15f,2.62f,2.45f,-6.2f,0,.55f,2.88f,2.47f);
   for(int side:new int[]{-1,1})for(int j=0;j<8;j++){
    Part q=head.child(side*(2.23f+.16f*(j%3)),-6.65f+(j%3)*.29f,-.42f+j*.37f);q.rz=-side*.21f;
    q.loft(3,12,-.25f,0,.12f,.30f,.41f,.63f,side*.18f,0,.49f,.45f,1.42f,side*.04f,.20f,.40f,.37f,2.23f,-side*.24f,.30f,.16f,.20f,2.52f,-side*.36f,.18f,.03f,.04f);
   }
   for(int j=0;j<6;j++){Part q=head.child(-2.05f+j*.82f,-5.62f,1.60f);q.loft(3,12,-.5f,0,0,.43f,.50f,.65f,.13f,.42f,.56f,.53f,2.2f,-.15f,.30f,.45f,.38f,3.5f,.27f,.12f,.07f,.08f);}
   Part curl=head.child(-.88f,-7.12f,-2.04f);
   curl.loft(3,12,-.35f,0,.40f,.38f,.40f,.60f,-.38f,-.37f,.43f,.36f,1.35f,-.25f,-.52f,.30f,.24f,2.0f,.10f,-.52f,.22f,.17f,2.80f,.23f,-.24f,.025f,.035f);
   // Fedora: separate thin curved brim, pinched crown and satin hatband.
   hat.rz=-.12f;hat.rx=.08f;
   hat.loft(2,48,-.16f,0,.07f,4.02f,3.56f,0,0,.05f,4.16f,3.69f,.16f,0,.03f,4.02f,3.55f);
   hat.loft(2,32,-3.1f,0,.19f,1.90f,2.05f,-2.73f,0,.15f,2.36f,2.33f,-1.25f,0,.08f,2.60f,2.49f,-.10f,0,.08f,2.73f,2.62f);
   hat.loft(4,32,-.73f,0,.08f,2.65f,2.54f,-.13f,0,.08f,2.75f,2.65f);
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;arms[i]=body.child(side*3.65f,.45f,0);
    arms[i].loft(0,18,-.50f,0,0,1.02f,1.02f,.7f,0,0,1.19f,1.15f,3.05f,0,0,.94f,.96f,4.8f,0,0,.74f,.78f);
    fore[i]=arms[i].child(0,4.7f,0);
    fore[i].loft(0,18,-.2f,0,0,.76f,.79f,1.3f,0,0,.90f,.94f,3.8f,0,0,.59f,.66f);
    fore[i].loft(1,16,3.62f,0,0,.66f,.70f,4.13f,0,0,.62f,.65f);
    int mat=i==0?7:5; // only one white rhinestone glove
    fore[i].oval(mat,0,4.85f,-.10f,.57f,.76f,.43f);
    for(int j=0;j<4;j++){float x=-.43f+j*.29f;fore[i].loft(mat,10,5.07f,x,-.17f,.14f,.18f,5.60f,x,-.28f,.13f,.15f,5.99f-(j==3?.2f:0),x,-.37f,.04f,.05f);}
    fore[i].oval(mat,-side*.55f,4.86f,-.20f,.19f,.43f,.20f);
    legs[i]=root.child(side*1.41f,10.65f,0);
    legs[i].loft(2,20,-.20f,0,0,1.34f,1.36f,2.5f,0,0,1.28f,1.22f,6.0f,0,0,.94f,.96f);
    legs[i].blade(4,0,.55f,-1.29f,0,5.7f,-.99f,.11f);
    shins[i]=legs[i].child(0,5.8f,0);
    shins[i].loft(2,20,-.15f,0,0,.97f,.99f,2.8f,0,0,.91f,.93f,5.15f,0,0,.80f,.87f);
    shins[i].loft(7,20,5.03f,0,0,.80f,.88f,6.26f,0,0,.75f,.83f);
    shoes[i]=shins[i].child(0,6.2f,0);
    shoes[i].loft(8,24,-.20f,0,0,.80f,.92f,.42f,0,-.58f,1.0f,1.61f,1.1f,0,-.61f,1.01f,1.68f);
    shoes[i].blade(4,-.66f,.21f,-1.32f,.66f,.21f,-1.32f,.22f);
   }
  }
  @Override public void setupAnim(DramaGuest e,float limb,float amount,float age,float yaw,float pitch){
   boolean dance=e.dancing();float beat=(float)Math.sin(age*.32f);
   body.ry=dance?beat*.14f:0;body.rz=dance?beat*.055f:0;body.rx=dance?.07f:0;
   head.ry=yaw*.012f;head.rx=pitch*.012f+(dance?.16f:0);head.rz=dance?-.12f:0;
   for(int i=0;i<2;i++){
    int side=i==0?-1:1;float w=(float)Math.cos(limb*.666f+i*Math.PI)*amount;
    arms[i].rx=-w*.55f;arms[i].rz=-side*.10f;fore[i].rx=-.15f;
    legs[i].rx=w*.60f;shins[i].rx=Math.max(0,-w)*.30f;shoes[i].rx=0;
    if(dance){
     float step=beat*side;
     legs[i].rx=step*.40f-.14f;shins[i].rx=Math.max(0,-step)*.85f;shoes[i].rx=-shins[i].rx*.72f;
     arms[i].rx=i==0?-1.48f:-.40f+beat*.23f;arms[i].rz=i==0?.35f:-.42f;fore[i].rx=i==0?-.95f:-.32f;
    }
   }
  }
  @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.draw(p,v,light,overlay,r,g,b,a);}
 }
 static class R extends MobRenderer<DramaGuest,M>{
  R(EntityRendererProvider.Context c){super(c,new M(),.35f);}
  @Override public ResourceLocation getTextureLocation(DramaGuest e){return new ResourceLocation(Noctis.ID,"textures/entity/moonwalk_sculpted.png");}
 }
}''')
W,H=1024,512;pix=bytearray(W*H*4)
pal=[(30,29,39),(232,227,221),(22,21,29),(19,17,24),(66,61,76),(224,183,157),(224,183,157),(235,232,234),(20,20,29)]
for m,base in enumerate(pal):
 for y in range(128):
  v=sat2((y-3)/121)
  for x in range(128):
   u=sat2((x-3)/121);f=abs(u-.5)
   c=shade(base,.81+.19*math.sin(math.pi*u))
   if m in (0,7):
    n=(x*17+y*31+x*y*7)%43
    if n<3:c=mix(c,(194,192,211) if m==0 else (255,255,255),.76)
    elif n<8:c=mix(c,(85,83,105) if m==0 else (157,151,176),.43)
   if m in (2,8):c=mix(c,(101,100,117),.33*math.exp(-((u-.28)/.12)**2))
   if m==3:
    wave=math.sin(u*math.pi*21+v*5+.8*math.sin(v*9))
    c=mix(c,(91,82,103),.40*max(0,wave)**5)
   if m==6:
    def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
    c=mix(base,(138,79,78),.27*sat2((f-.16)*4)+.10*v)
    c=mix(c,(247,213,186),.28*g(.5,.38,.15,.2))
    for side in (-1,1):
     ex=.5+side*.174;dx=side*(u-ex)/.113;dy=(v-(.474-.013*dx))/.042
     c=mix(c,(128,75,79),.30*g(ex,.48,.12,.074))
     c=mix(c,(245,201,174),.20*g(.5+side*.21,.60,.07,.06))
     d=abs(dx)**1.65+abs(dy)**1.3
     if d<1.16:c=(37,24,33)
     if d<.77:c=(236,224,211)
     if d<.75 and abs(dx)<.43:c=(76,46,39)
     if d<.71 and abs(dx)<.19:c=(23,17,25)
     if d<.69 and (dx+.16)**2+(dy+.22)**2<.035:c=(255,246,232)
     if abs(dx)<1.08 and abs(v-(.379-.025*dx))<.015:c=(47,30,34)
    if f<.039 and abs(v-.674)<.010:c=mix(c,(143,78,74),.64)
    if f<.092 and abs(v-(.784-.012*(1-f/.092)))<.012:c=(120,48,56)
    if f<.073 and abs(v-.807)<.010:c=(178,86,90)
   off=((m//8*128+y)*W+m%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(assets/'textures/entity/moonwalk_sculpted.png',W,H,pix)
print('Magic input and mana HUD restored; hit vocalizations for both admirers; dedicated Michael Jackson moonwalk model.')


# More open temperate landscapes, opt-in world preset (no change to saved vanilla generators).
write('OpenPlainsSource.java','''package it.noctis.magic;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.stream.Stream;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.biome.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegisterEvent;
@Mod.EventBusSubscriber(modid=Noctis.ID,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class OpenPlainsSource extends BiomeSource {
 private final BiomeSource original;
 private final Holder<Biome> plains;
 public static final Codec<OpenPlainsSource> CODEC=RecordCodecBuilder.create(i->i.group(
  BiomeSource.CODEC.fieldOf("original").forGetter(s->s.original),
  Biome.CODEC.fieldOf("plains").forGetter(s->s.plains)
 ).apply(i,OpenPlainsSource::new));
 public OpenPlainsSource(BiomeSource original,Holder<Biome> plains){this.original=original;this.plains=plains;}
 @SubscribeEvent public static void register(RegisterEvent e){
  e.register(Registries.BIOME_SOURCE,helper->helper.register(new net.minecraft.resources.ResourceLocation(Noctis.ID,"open_plains"),CODEC));
 }
 @Override protected Codec<? extends BiomeSource> codec(){return CODEC;}
 @Override protected Stream<Holder<Biome>> collectPossibleBiomes(){return Stream.concat(original.possibleBiomes().stream(),Stream.of(plains)).distinct();}
 @Override public Holder<Biome> getNoiseBiome(int x,int y,int z,Climate.Sampler sampler){
  Holder<Biome> b=original.getNoiseBiome(x,y,z,sampler);
  // Only expand temperate open country; leave cave biomes, oceans, rivers,
  // deserts, jungles, mountains, snowy biomes and all mod-added biomes alone.
  if(!b.is(Biomes.FOREST)&&!b.is(Biomes.BIRCH_FOREST)&&!b.is(Biomes.DARK_FOREST))return b;
  Climate.TargetPoint climate=sampler.sample(x,y,z);
  // The climate sampler's quantized values are scaled by 10,000.
  // Favor lower-relief terrain and moderately dry areas instead of replacing all forests.
  if(climate.erosion()>=-500&&climate.humidity()<4800&&climate.depth()<5500)return plains;
  return b;
 }
}''')
preset={'dimensions':{
 'minecraft:overworld':{'type':'minecraft:overworld','generator':{'type':'minecraft:noise','settings':'minecraft:overworld','biome_source':{'type':'noctismagic:open_plains','original':{'type':'minecraft:multi_noise','preset':'minecraft:overworld'},'plains':'minecraft:plains'}}},
 'minecraft:the_nether':{'type':'minecraft:the_nether','generator':{'type':'minecraft:noise','settings':'minecraft:nether','biome_source':{'type':'minecraft:multi_noise','preset':'minecraft:nether'}}},
 'minecraft:the_end':{'type':'minecraft:the_end','generator':{'type':'minecraft:noise','settings':'minecraft:end','biome_source':{'type':'minecraft:the_end'}}}
}}
write_noctis_json_resource(res/'data/noctismagic/worldgen/world_preset/open_plains.json',preset)
write_noctis_json_resource(res/'data/minecraft/tags/worldgen/world_preset/normal.json',{'replace':False,'values':['noctismagic:open_plains']})
for lang in ('it_it','en_us'):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['generator.noctismagic.open_plains']='Noctis - Grandi pianure' if lang=='it_it' else 'Noctis - Open plains'
 write_noctis_json_resource(p,d)

# A candidate may try several neighboring footprints instead of being discarded at
# the first unsuitable height sample. Keep the original 24-chunk region and seed.
p=java/'NaturalMonuments.java';s=p.read_text(encoding='utf-8')
a=s.index('   int x=cp.getMinBlockX(),z=cp.getMinBlockZ();')
b=s.index('   active.put(l,job);activeKey.put(l,key);return;',a)
s=s[:a]+'''   int x0=cp.getMinBlockX(),z0=cp.getMinBlockZ();
   if(!l.hasChunk(cp.x,cp.z))continue;
   GothicEgg.Plan p=plan(c[2]);
   int[][] offsets={{0,0},{16,0},{0,16},{-16,0},{0,-16},{32,16},{-32,16},{16,-32},{-16,-32}};
   boolean waiting=false;BlockPos chosen=null;
   for(int[] o:offsets){
    int x=x0+o[0],z=z0+o[1];
    if(!loaded(l,x,z,p.w,p.d)){waiting=true;continue;}
    if(!l.getWorldBorder().isWithinBounds(new BlockPos(x,64,z))||!l.getWorldBorder().isWithinBounds(new BlockPos(x+p.w-1,64,z+p.d-1)))continue;
    int low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;boolean bad=false;
    for(int dx=0;dx<p.w&&!bad;dx+=3)for(int dz=0;dz<p.d;dz+=3){
     int h=l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x+dx,z+dz);
     BlockPos ground=new BlockPos(x+dx,h-1,z+dz);
     low=Math.min(low,h);high=Math.max(high,h);
     if(!l.getFluidState(ground).isEmpty()||!l.getBlockState(ground).isFaceSturdy(l,ground,Direction.UP)||l.getHeight(Heightmap.Types.MOTION_BLOCKING,x+dx,z+dz)>h){bad=true;break;}
    }
    if(bad||high-low>2||high<l.getSeaLevel()||high+p.h>=l.getMaxBuildHeight())continue;
    // The queued Job checks the complete volume again before placing anything.
    chosen=new BlockPos(x,high,z);break;
   }
   if(chosen==null){if(!waiting)finish(data,key);continue;}
   job=new GothicEgg.Job(l,null,p,chosen,Direction.SOUTH);
'''+s[b:]
# Persist successful/failed candidate once; do not overwrite existing structures.
p.write_text(s,encoding='utf-8')
print('Open plains world preset and multiple safe natural monument placement candidates.')


# Denser natural monuments: one deterministic candidate per 16x16 chunk region.
# Keep a safety margin for the largest (91x101) building and the alternate footprints.
p=java/'NaturalMonuments.java';s=p.read_text(encoding='utf-8')
def monuments_change(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b,1)
monuments_change('static final int REGION=24;','static final int REGION=16;')
monuments_change('Random r=random(l,rx,rz);if(r.nextInt(100)>=76)return null;','Random r=random(l,rx,rz);')
monuments_change('rx*REGION+4+r.nextInt(12),rz*REGION+4+r.nextInt(12),r.nextInt(4)','rx*REGION+3+r.nextInt(4),rz*REGION+3+r.nextInt(4),r.nextInt(4)')
# More possible nearby footprints within the same region (including diagonals).
monuments_change('int[][] offsets={{0,0},{16,0},{0,16},{-16,0},{0,-16},{32,16},{-32,16},{16,-32},{-16,-32}};',
'''int[][] offsets={{0,0},{16,0},{0,16},{-16,0},{0,-16},{16,16},{-16,16},{16,-16},{-16,-16},{32,0},{0,32},{-32,0},{0,-32},{32,16},{-32,16},{16,-32},{-16,-32}};''')
# Keep all candidate placements in their own region, even for pending entries from older saves.
monuments_change('    if(!loaded(l,x,z,p.w,p.d)){waiting=true;continue;}',
'''    int regionX=Math.floorDiv(cp.x,REGION)*REGION*16,regionZ=Math.floorDiv(cp.z,REGION)*REGION*16;
    if(x<regionX||z<regionZ||x+p.w>regionX+REGION*16||z+p.d>regionZ+REGION*16)continue;
    if(!loaded(l,x,z,p.w,p.d)){waiting=true;continue;}''')
# Skip a suspended preflight when a player leaves; keep the candidate pending for a later visit.
monuments_change('if(!loaded(l,job.origin.getX(),job.origin.getZ(),job.p.w,job.p.d))return;',
'''if(!loaded(l,job.origin.getX(),job.origin.getZ(),job.p.w,job.p.d)){
    if(!job.ready){active.remove(l);activeKey.remove(l);}return;
   }''')
p.write_text(s,encoding='utf-8')

# Allow crafted building eggs to be used in survival without operator privileges.
# Existing placement validation, no-overwrite behavior, consumption and refund remain intact.
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8')
a='        if(!p.isCreative()&&!p.hasPermissions(2)){p.sendSystemMessage(Component.literal("Per evocare un monumento serve la modalita Creativa o il permesso operatore."));return InteractionResult.FAIL;}'
assert a in s,a
s=s.replace(a,'',1)
# Prevent simultaneous natural and manually triggered jobs.
a='if(!Jobs.queue.isEmpty()){'
assert a in s,a
s=s.replace(a,'if(!Jobs.queue.isEmpty()||NaturalMonuments.active.containsKey(l)){',1)
p.write_text(s,encoding='utf-8')

# Survival recipes, all nine slots use ordinary obtainable vanilla ingredients.
# More expensive materials for larger monuments; one consumed egg per building.
recipes={
 'bakery_egg':('SWS','WEW','SBS',{'S':'minecraft:stone_bricks','W':'minecraft:wheat','E':'minecraft:egg','B':'minecraft:bread'}),
 'pastry_egg':('SCS','WEW','SPS',{'S':'minecraft:stone_bricks','C':'minecraft:cake','W':'minecraft:wheat','E':'minecraft:egg','P':'minecraft:pumpkin_pie'}),
 'cathedral_egg':('DGD','QEQ','DAD',{'D':'minecraft:deepslate_bricks','G':'minecraft:gold_block','Q':'minecraft:quartz_block','E':'minecraft:egg','A':'minecraft:amethyst_block'}),
 'castle_egg':('DOD','IEI','DGD',{'D':'minecraft:deepslate_bricks','O':'minecraft:obsidian','I':'minecraft:iron_block','E':'minecraft:egg','G':'minecraft:gold_block'})
}
for name,(*pattern,ingredients) in recipes.items():
 recipe={'type':'minecraft:crafting_shaped','category':'misc','pattern':pattern,'key':{k:{'item':v} for k,v in ingredients.items()},'result':{'item':'noctismagic:'+name,'count':1}}
 assert all(len(row)==3 for row in pattern) and len(pattern)==3
 assert set(''.join(pattern))==set(ingredients)
 write_noctis_json_resource(res/'data/noctismagic/recipes'/f'{name}.json',recipe)
 # Recipe book discovers it upon collecting an egg; these internal advancements have no visible tab.
 write_noctis_json_resource(res/'data/noctismagic/advancements/recipes/misc'/f'{name}.json',{
  'parent':'minecraft:recipes/root',
  'criteria':{'has_egg':{'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':['minecraft:egg']}]}},'has_recipe':{'trigger':'minecraft:recipe_unlocked','conditions':{'recipe':'noctismagic:'+name}}},
  'requirements':[['has_egg','has_recipe']],
  'rewards':{'recipes':['noctismagic:'+name]}
 })
print('Natural structures: candidate every 16x16 chunks, 17 placement attempts; all four monument eggs craftable and usable in survival.')


# Final face rebuild: remove the compounded head scaling, build matched mask/face surfaces.
p=java/'JokerDetailedClient.java';s=p.read_text(encoding='utf-8')
a=s.index(' static V maskV(');b=s.index(' static void curl(',a)
s=s[:a]+''' // The same cross sections drive the skin and the raised mask. No guessed Z offset
 // or independent face scaling that can turn the mask into floating spectacles.
 static final float[] SKULL={
  -7.80f,0,.12f,1.19f,1.43f,-7.28f,0,.07f,2.18f,2.10f,
  -6.25f,0,0,2.65f,2.45f,-5.25f,0,-.02f,2.72f,2.50f,
  -4.20f,0,-.08f,2.63f,2.45f,-3.45f,0,-.12f,2.55f,2.39f,
  -2.55f,0,-.20f,2.20f,2.14f,-1.65f,0,-.29f,1.82f,1.84f,
  -.76f,0,-.42f,1.24f,1.35f,-.16f,0,-.48f,.61f,.77f
 };
 static float frontZ(float x,float y){
  int i=0;while(i+5<SKULL.length-5&&y>SKULL[i+5])i+=5;
  float t=Math.max(0,Math.min(1,(y-SKULL[i])/(SKULL[i+5]-SKULL[i])));
  float w=SKULL[i+3]+t*(SKULL[i+8]-SKULL[i+3]);
  float d=SKULL[i+4]+t*(SKULL[i+9]-SKULL[i+4]);
  float z=SKULL[i+2]+t*(SKULL[i+7]-SKULL[i+2]);
  return z-d*(float)Math.sqrt(Math.max(.02f,1-x*x/(w*w)));
 }
 // Ordered, sharp outer contour and almond-shaped inner aperture, mirrored on both sides.
 static final float[][] MASK_OUT={{2.53f,-5.22f},{2.47f,-4.72f},{2.39f,-4.21f},{2.12f,-3.76f},{1.76f,-3.42f},{1.23f,-3.21f},{.75f,-3.29f},{.36f,-3.57f},{.13f,-4.03f},{.36f,-4.40f},{.76f,-4.69f},{1.24f,-4.80f},{1.80f,-4.93f},{2.23f,-5.08f}};
 static final float[][] MASK_IN={{1.88f,-4.29f},{1.85f,-4.13f},{1.70f,-3.99f},{1.50f,-3.89f},{1.26f,-3.82f},{1.04f,-3.80f},{.81f,-3.86f},{.58f,-3.97f},{.44f,-4.12f},{.63f,-4.26f},{.88f,-4.37f},{1.15f,-4.43f},{1.45f,-4.41f},{1.70f,-4.37f}};
 static V maskPoint(int side,int i,float t,float r,float lift){
  int j=(i+1)%MASK_IN.length;
  float x1=MASK_IN[i][0]+(MASK_IN[j][0]-MASK_IN[i][0])*t;
  float y1=MASK_IN[i][1]+(MASK_IN[j][1]-MASK_IN[i][1])*t;
  float x2=MASK_OUT[i][0]+(MASK_OUT[j][0]-MASK_OUT[i][0])*t;
  float y2=MASK_OUT[i][1]+(MASK_OUT[j][1]-MASK_OUT[i][1])*t;
  float x=side*(x1+(x2-x1)*r),y=y1+(y2-y1)*r;
  return new V(x,y,frontZ(x,y)-lift,.5f+x*.16f,.5f+(y+4.1f)*.36f,0,0,-1);
 }
 static void mask(Part p,int side){
  float[] rings={0,.075f,.16f,.88f,.96f,1};
  float[] lift={.045f,.10f,.145f,.145f,.09f,.03f};
  int[] mats={11,8,8,8,11};
  for(int i=0;i<MASK_IN.length;i++)for(int k=0;k<4;k++)for(int n=0;n<5;n++){
   float t=k/4f,T=(k+1)/4f;
   V A=maskPoint(side,i,t,rings[n],lift[n]),B=maskPoint(side,i,T,rings[n],lift[n]),C=maskPoint(side,i,T,rings[n+1],lift[n+1]),D=maskPoint(side,i,t,rings[n+1],lift[n+1]);
   p.faces.add(side>0?new Q(A,B,C,D,mats[n]):new Q(D,C,B,A,mats[n]));
   p.faces.add(side>0?new Q(D,C,B,A,mats[n]):new Q(A,B,C,D,mats[n]));
  }
 }
'''+s[b:]
a=s.index('   head.loft(7,48,');b=s.index('   for(int i=0;i<2;i++){int s=i==0?-1:1;',a)
s=s[:a]+'''   // Angular but natural skull, with cheek planes and defined lips; no chibi squash.
   head.loft(7,64,SKULL);project(head);
   body.loft(1,24,-1.30f,0,.03f,.83f,.85f,-.42f,0,0,.98f,.98f,.45f,0,0,1.13f,1.08f);
   head.loft(1,20,-4.45f,0,-2.46f,.12f,.07f,-3.69f,0,-2.66f,.22f,.19f,-2.95f,0,-2.89f,.33f,.30f,-2.70f,0,-2.70f,.24f,.13f);
   for(int side:new int[]{-1,1}){
    head.oval(1,side*2.55f,-3.62f,.05f,.29f,.63f,.42f);
    head.oval(1,side*2.59f,-3.54f,-.18f,.13f,.36f,.13f);
    mask(head,side);
   }
   head.loft(8,12,-4.30f,0,-2.48f,.22f,.08f,-4.12f,0,-2.61f,.33f,.10f,-3.90f,0,-2.56f,.18f,.07f);
   // Dark messy hair: overlapping S-shaped locks sweep in multiple directions.
   head.loft(9,40,-8.52f,0,.17f,1.02f,1.16f,-8.16f,0,.18f,2.34f,2.28f,-7.42f,0,.20f,2.86f,2.72f,-6.24f,0,.40f,2.86f,2.69f);
   head.loft(9,32,-7.72f,0,1.02f,2.52f,1.96f,-5.56f,0,1.35f,2.73f,1.65f,-3.28f,0,1.67f,2.32f,1.25f,-1.78f,0,1.46f,1.37f,.18f);
   for(int row=0;row<3;row++)for(int j=0;j<11;j++){
    float t=j/10f,x=-2.50f+t*5.0f,drift=(j%3==0?.69f:-.68f)+(t-.5f)*.35f;
    float y=-8.24f+row*.32f+(float)Math.sin(j*1.37f+row)*.23f;
    float z=.88f-row*1.38f;
    Part q=head.child(x,y,z);
    float len=1.72f+(j%4)*.29f+(row==2?.26f:0),w=.43f+(j%3)*.08f;
    q.loft(9,16,-.63f,0,.36f,w*.48f,w*.57f,.06f,-drift*.10f,0,w,w*.92f,.57f,drift*.17f,-.36f,w*.88f,w*.68f,1.08f,drift*.68f,-.62f,w*.64f,w*.46f,len*.77f,drift*.98f,-.76f,w*.35f,w*.25f,len,drift*.70f,-.47f,.022f,.030f);
    q.blade(9,-w*.30f,.10f,-.43f,drift*.68f,len*.80f,-.83f,.10f);
   }
   for(int side:new int[]{-1,1})for(int j=0;j<7;j++){
    Part q=head.child(side*(2.27f+.11f*(j%3)),-7.13f+j*.39f,.11f+j*.26f);
    q.rz=-side*(.20f+j*.065f);
    curl(q,0,0,0,side*(.40f+j*.07f),1.60f+(j%3)*.33f,.42f,.45f+(j%2)*.10f);
   }
'''+s[b:]
s=s.replace('AngularHeads.apply(head,7,.86f,.96f,.94f,.17f);','',1)
# Align the actual texture with the shared physical mask dimensions.
a='f?cl(.5f+v.x()/5.8f):.025f,cl((v.y()+7.65f)/7.65f)'
assert a in s
s=s.replace(a,'f?cl(.5f+v.x()/6.1f):.025f,cl((v.y()+7.80f)/7.80f)',1)
p.write_text(s,encoding='utf-8')

# Paint skin and eyes in the same coordinates used by the open mask; no baked duplicate mask.
p=assets/'textures/entity/joker_detailed.png';W,H,pix=read_rgba(p)
def phantom_skin(u,v):
 x=(u-.5)*6.1;y=v*7.8-7.8;f=abs(x)
 def g(cx,cy,sx,sy):return math.exp(-((x-cx)/sx)**2-((y-cy)/sy)**2)
 c=mix((242,205,183),(148,88,84),.28*sat2((f-1.15)/1.45)+.10*v)
 c=mix(c,(255,228,209),.34*g(0,-4.35,.78,1.85))
 for side in (-1,1):
  dx=(x-side*1.13)/.72;out=side*dx
  ey=-4.12-.08*out;dy=(y-ey)/.29
  d=abs(dx)**1.65+abs(dy)**1.38
  c=mix(c,(141,81,85),.26*g(side*1.15,-3.92,.81,.43))
  if d<1.18:c=(37,24,34)
  if d<.82:c=(241,234,226)
  if d<.80 and (dx/.38)**2+(dy/.93)**2<1:
   c=mix((51,48,61),(137,129,149),sat2((dy+.72)/1.44))
   if (dx/.15)**2+(dy/.80)**2<1:c=(21,17,27)
   if (dx+.13)**2+(dy+.19)**2<.055:c=(255,252,246)
  if abs(dx)<1.05 and abs(y-(ey-.31+.05*out))<.055:c=(42,28,37)
  c=mix(c,(174,101,101),.17*g(side*1.38,-2.83,.52,.35))
  c=mix(c,(254,216,195),.16*g(side*.95,-2.60,.44,.32))
 if f<.10 and abs(y+2.62)<.055:c=mix(c,(130,72,71),.68)
 if f<.55:
  lip=-1.82-.07*(1-f/.55)+.045*x
  if abs(y-lip)<.051:c=(111,53,66)
  if f<.42 and abs(y-lip-.12)<.044:c=mix(c,(212,135,129),.66)
 c=mix(c,(148,83,81),.22*g(0,-1.36,.48,.14))
 return c
for y in range(128):
 for x in range(128):
  samples=[phantom_skin(sat2((x+dx-3)/121),sat2((y+dy-3)/121)) for dx,dy in ((-.28,-.28),(.28,-.28),(-.28,.28),(.28,.28))]
  c=tuple(round(sum(z[k] for z in samples)/4) for k in range(3))
  off=(y*W+7*128+x)*4;pix[off:off+4]=bytes((*c,255))
  u=sat2((x-3)/121);v=sat2((y-3)/121)
  # Black hair with restrained anisotropic sheen, no brown highlights.
  wave=math.sin(u*math.pi*32+v*5.3+.55*math.sin(v*7))
  c=mix((15,15,23),(69,68,88),.20+.42*max(0,wave)**7)
  c=mix(c,(6,7,12),.36*max(0,-wave)**5)
  off=((128+y)*W+128+x)*4;pix[off:off+4]=bytes((*c,255))
png(p,W,H,pix)

# Arsene's demonic face: a broad upper mask tapering to a pointed chin, red engraved
# planes, distinct brow/cheek plates, split gold-red eye slits and hollow crown.
p=java/'ArseneDetailedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   // Narrow black mask');b=s.index('   for(int i=0;i<2;i++){',a)
s=s[:a]+'''   body.loft(6,16,-1.15f,0,0,.66f,.65f,-.18f,0,0,.88f,.82f,.60f,0,0,1.06f,.97f);
   head.loft(6,24,-6.90f,0,.16f,.93f,.93f,-6.35f,0,.04f,1.66f,1.42f,-5.50f,0,-.03f,2.02f,1.58f,-4.58f,0,-.10f,1.89f,1.59f,-3.36f,0,-.24f,1.45f,1.42f,-2.12f,0,-.38f,.93f,1.04f,-.92f,0,-.57f,.40f,.62f,-.55f,0,-.68f,.075f,.12f);
   // Each side is built as shaped layered metal, not a blank cone.
   for(int side:new int[]{-1,1}){
    head.blade(14,side*1.90f,-5.58f,-.75f,side*.53f,-2.05f,-1.54f,1.15f);
    head.blade(1,side*1.74f,-5.18f,-1.08f,side*.37f,-1.42f,-1.41f,.79f);
    head.blade(15,side*1.42f,-4.85f,-1.46f,side*.20f,-1.25f,-1.53f,.45f);
    head.blade(1,side*1.79f,-3.75f,-.90f,side*.32f,-.90f,-1.16f,.38f);
    head.blade(14,side*1.70f,-5.85f,-.80f,side*.37f,-4.75f,-1.64f,.67f);
    head.blade(6,side*.44f,-5.95f,-1.35f,side*1.94f,-5.37f,-.90f,.42f);
    Part socket=head.child(side*.94f,-4.58f,-1.63f);socket.rz=-side*.35f;socket.ry=-side*.18f;
    socket.oval(10,0,0,0,.83f,.39f,.16f);
    socket.blade(1,-.72f,-.16f,-.19f,.74f,.10f,-.19f,.48f);
    socket.blade(12,-.62f,-.03f,-.26f,.65f,.02f,-.26f,.29f);
    socket.blade(13,-.48f,-.02f,-.34f,.47f,.01f,-.34f,.12f);
    for(int j=0;j<3;j++){
     head.blade(1,side*(1.51f-j*.21f),-3.95f+j*.58f,-1.05f-j*.11f,side*(.93f-j*.23f),-3.39f+j*.58f,-1.56f,.19f);
    }
    head.blade(6,side*.69f,-6.38f,.07f,side*3.78f,-8.90f,.32f,.77f);
    head.blade(14,side*.96f,-6.53f,-.31f,side*3.58f,-8.58f,-.04f,.24f);
    Part crest=head.child(side*3.29f,-7.92f,-.02f);crest.rz=side*.60f;crest.ry=-side*.12f;
    crest.loft(6,20,-.41f,0,0,.26f,.30f,-.19f,0,0,1.18f,.66f,.03f,0,0,1.47f,.79f,.36f,0,0,.94f,.54f,.49f,0,0,.18f,.18f);
    crest.blade(1,-1.18f,0,-.35f,1.22f,0,-.35f,.48f);
    crest.blade(12,-.88f,.015f,-.46f,.91f,.015f,-.46f,.16f);
    crest.blade(6,side*.30f,-.1f,.12f,side*.64f,-1.28f,.22f,.56f);
   }
   // Central raised nose/forehead ridge and a sharp red chin seam.
   head.blade(14,0,-6.63f,-1.04f,0,-4.71f,-1.76f,.65f);
   head.blade(6,0,-5.45f,-1.75f,0,-2.85f,-1.86f,.64f);
   head.blade(1,0,-3.45f,-1.84f,0,-.76f,-1.25f,.28f);
   head.blade(14,0,-3.08f,-1.94f,0,-1.17f,-1.44f,.12f);
   // Faceted high crown, dark inner top and contrasting longitudinal ribs.
   head.loft(6,8,-19.35f,0,.40f,1.29f,1.18f,-19.0f,0,.40f,1.30f,1.20f,-12.0f,0,.25f,1.08f,1.09f,-6.04f,0,.06f,.77f,.91f);
   head.loft(10,8,-19.41f,0,.40f,1.04f,.95f,-19.36f,0,.40f,1.04f,.95f);
   for(int j=0;j<8;j++){
    float t=j*(float)Math.PI/4;
    head.blade(14,1.27f*(float)Math.sin(t),-19.26f,.40f+1.17f*(float)Math.cos(t),.78f*(float)Math.sin(t),-6.27f,.06f+.88f*(float)Math.cos(t),.12f);
   }
'''+s[b:]
# Give the two rows of wings less uniform silhouettes, without changing the rig.
s=s.replace('11.6f-4.4f*t,1.55f,1.65f+1.0f*t','11.6f-4.4f*t+(float)Math.sin(j*1.4f)*.40f,1.55f,1.65f+1.0f*t',1)
s=s.replace('12.8f+7.2f*t,1.40f+1.3f*t,2.35f-.54f*t','12.8f+7.2f*t+(float)Math.sin(j*1.6f)*.66f,1.40f+1.3f*t,2.35f-.54f*t',1)
p.write_text(s,encoding='utf-8')
p=assets/'textures/entity/arsene_detailed.png';W,H,pix=read_rgba(p)
for tile,base in [(6,(24,25,35)),(10,(8,9,16)),(12,(255,68,36)),(13,(255,178,87)),(14,(83,89,111)),(15,(30,18,31))]:
 for y in range(128):
  for x in range(128):
   u=sat2((x-3)/121);v=sat2((y-3)/121)
   c=shade(base,.76+.24*math.sin(math.pi*u))
   if tile in (6,14,15):
    c=mix(c,(157,167,191) if tile==14 else (70,75,98),.28*math.exp(-((u-.30)/.12)**2))
    c=mix(c,(9,10,18),.30*math.exp(-((u-.82)/.11)**2))
    c=shade(c,.97+.03*math.sin(u*132+v*31))
   if tile in (12,13):c=mix(base,(255,235,179),.52*math.sin(math.pi*u)**2)
   off=((tile//8*128+y)*W+tile%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
png(p,W,H,pix)

# Joker reacts immediately to damage, even when the attacker is not a normal low-HP Shadow.
p=java/'Joker.java';s=p.read_text(encoding='utf-8')
a=s.index('    @Override public void tick(){');b=s.index('    @Override public void handleEntityEvent',a)
s=s[:a]+'''    private UUID retaliator;
    private long defendUntil;
    boolean defensiveTarget(LivingEntity e){
        return e!=null&&e!=this&&e.isAlive()&&!(e instanceof Arsene)&&retaliator!=null&&retaliator.equals(e.getUUID())&&level().getGameTime()<defendUntil;
    }
    boolean personaTarget(LivingEntity e){
        if(e==null||!e.isAlive()||e==this||e instanceof Arsene)return false;
        if(e instanceof Player p&&(p.isCreative()||p.isSpectator()))return false;
        return defensiveTarget(e)||shadow(e);
    }
    private void callPersona(ServerLevel l,LivingEntity t){
        if(t==null||!t.isAlive())return;
        Arsene a=persona==null?null:l.getEntity(persona) instanceof Arsene ar?ar:null;
        // Recover our already-loaded Persona after rejoining, rather than duplicating it.
        if(a==null||!a.isAlive())a=l.getEntitiesOfClass(Arsene.class,getBoundingBox().inflate(32),ar->ar.isAlive()&&getUUID().equals(ar.owner)).stream().findFirst().orElse(null);
        if(a==null){
            a=Noctis.ARSENE.get().create(l);
            if(a!=null){
                a.moveTo(getX(),getY()+.5,getZ(),getYRot(),0);
                a.bind(this,t);
                if(l.addFreshEntity(a)){
                    persona=a.getUUID();say(l,"Persona! Arsene!");
                    l.broadcastEntityEvent(this,(byte)90);
                    l.sendParticles(ParticleTypes.SOUL_FIRE_FLAME,getX(),getY()+1,getZ(),45,.6,.8,.6,.08);
                }
            }
        }else{persona=a.getUUID();a.bind(this,t);}
    }
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float amount){
        boolean hit=super.hurt(source,amount);
        if(hit&&isAlive()&&level() instanceof ServerLevel l&&source.getEntity() instanceof LivingEntity attacker&&attacker!=this&&!(attacker instanceof Arsene)&&attacker.isAlive()){
            retaliator=attacker.getUUID();defendUntil=l.getGameTime()+240;
            getNavigation().stop();getLookControl().setLookAt(attacker,50,50);
            callPersona(l,attacker);cd=12;
        }
        return hit;
    }
    @Override public void tick(){
        super.tick();if(cd>0)cd--;if(speech>0)speech--;if(pose>0)pose--;
        if(!(level() instanceof ServerLevel l)||!isAlive()||cd>0)return;
        LivingEntity t=retaliator!=null&&l.getEntity(retaliator) instanceof LivingEntity e&&defensiveTarget(e)&&distanceTo(e)<40?e:null;
        if(t==null)t=l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(20),Joker::shadow).stream().filter(this::hasLineOfSight).min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
        if(t==null){cd=20;return;}
        cd=75;getNavigation().stop();getLookControl().setLookAt(t,50,50);
        callPersona(l,t);
        if(personaTarget(t)&&distanceTo(t)<3&&hasLineOfSight(t)){t.hurt(damageSources().mobAttack(this),16);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,.8f,1.4f);}
    }
'''+s[b:]
p.write_text(s,encoding='utf-8')
p=java/'Arsene.java';s=p.read_text(encoding='utf-8')
a='!Joker.shadow(t)'
assert a in s
s=s.replace(a,'!j.personaTarget(t)',1)
p.write_text(s,encoding='utf-8')
# A bound Persona is limited by its owner instead of blocking another Joker's defense.
p=java/'CharacterSpawnLimit.java';s=p.read_text(encoding='utf-8')
a='  ChunkPos c=new ChunkPos(incoming.blockPosition());'
assert a in s
s=s.replace(a,'''  if(incoming instanceof Arsene a&&a.owner!=null){
   boolean duplicate=!level.getEntitiesOfClass(Arsene.class,incoming.getBoundingBox().inflate(48),other->other.isAlive()&&other!=a&&a.owner.equals(other.owner)).isEmpty();
   if(duplicate)event.setCanceled(true);
   else incoming.getPersistentData().putBoolean(CHECKED,true);
   return;
  }
'''+a,1)
p.write_text(s,encoding='utf-8')
print('Phantom faces: matched open mask, detailed eyes and hair, layered demonic metal face; Joker summons on damage and retargets his own Persona.')


# Strongly readable character dialogue, preserving custom styles for all other messages.
write('NpcDialogue.java','''package it.noctis.magic;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TextColor;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
public final class NpcDialogue {
 static Component styled(Component message){
  String s=message.getString();int split=s.indexOf(':');if(split<0)return message;
  String name=s.substring(0,split);String line=s.substring(split+1).stripLeading();
  int color=switch(name){
   case "Joker"->0xFF4059;
   case "Lelouch"->0xCF8CFF;
   case "C.C.","CC"->0xA8FF81;
   case "Lucy"->0x95E7FF;
   case "Faputa"->0xFFCA62;
   case "Giorno Giovanna","Giorno"->0xFFE16D;
   case "Leon Kennedy","Leon"->0xB9D8F4;
   case "Miles Edgeworth"->0xFF5555;
   case "Phoenix Wright"->0x5599FF;
   case "Guts"->0xFF5555;
   case "Griffith"->0xE6E5FF;
   default->-1;
  };
  if(color<0)return message;
  return Component.literal(name+": ").withStyle(st->st.withColor(TextColor.fromRgb(color)).withBold(true))
   .append(Component.literal(line).withStyle(st->st.withColor(TextColor.fromRgb(color)).withBold(name.equals("Joker")&&line.contains("Persona")||name.equals("Lelouch")&&line.contains("ti ordino")||line.contains("OBJECTION")||name.equals("Guts"))));
 }
 public static void say(Player p,Component message){if(p.getServer()!=null)p.getServer().getPlayerList().broadcastSystemMessage(styled(message),false);}
 public static void say(ServerLevel l,Component message){l.getServer().getPlayerList().broadcastSystemMessage(styled(message),false);}
}''')

# Shared safety check for forced Geass movement. No forced jump, cliff or liquid crossing.
write('GeassWalkSafety.java','''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
final class GeassWalkSafety{
 static Vec3 direction(int i){double a=i*Math.PI/8;return new Vec3(-Math.sin(a),0,Math.cos(a));}
 static boolean hazardous(Level l,BlockPos p){
  var s=l.getBlockState(p);
  return !l.getFluidState(p).isEmpty()||s.is(Blocks.CACTUS)||s.is(Blocks.MAGMA_BLOCK)||s.is(Blocks.CAMPFIRE)||s.is(Blocks.SOUL_CAMPFIRE)||s.is(Blocks.FIRE)||s.is(Blocks.SOUL_FIRE)||s.is(Blocks.POWDER_SNOW)||s.is(Blocks.SWEET_BERRY_BUSH)||s.is(Blocks.COBWEB);
 }
 static boolean safe(Player p,Vec3 d,double distance){
  Level l=p.level();
  if(p.isInWater()||p.isInLava()||!p.onGround())return false;
  for(double step=.25;step<=distance+.001;step+=.25){
   AABB box=p.getBoundingBox().move(d.x*step,0,d.z*step);
   BlockPos low=BlockPos.containing(box.minX+.015,box.minY+.02,box.minZ+.015);
   BlockPos high=BlockPos.containing(box.maxX-.015,box.maxY-.02,box.maxZ-.015);
   for(int x=low.getX();x<=high.getX();x++)for(int z=low.getZ();z<=high.getZ();z++){
    BlockPos feet=new BlockPos(x,low.getY(),z);
    if(!l.hasChunkAt(feet)||!l.getWorldBorder().isWithinBounds(feet))return false;
    BlockPos floor=BlockPos.containing(x+.5,box.minY-.10,z+.5);
    if(hazardous(l,floor)||!l.getBlockState(floor).isFaceSturdy(l,floor,Direction.UP))return false;
    for(int y=low.getY();y<=high.getY();y++)if(hazardous(l,new BlockPos(x,y,z)))return false;
   }
   if(!l.noCollision(p,box))return false;
  }
  return true;
 }
}''')
p=java/'GeassExile.java';s=p.read_text(encoding='utf-8')
s=s.replace('int ticks=1200,dir=-1,blocked;','int ticks=1200,dir=-1,blocked,stuck,avoid=-1;Vec3 checkpoint;',1)
s=s.replace('origin=g.position();last=p.position();','origin=g.position();last=p.position();checkpoint=last;',1)
s=s.replace('Component.translatable("message.noctismagic.geass_order")','Component.translatable("message.noctismagic.geass_order").withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE,net.minecraft.ChatFormatting.BOLD)',1)
a=s.index(' static boolean safe(ServerPlayer p,Vec3 d){');b=s.index(' static void release',a)
s=s[:a]+''' static boolean safe(ServerPlayer p,Vec3 d){return GeassWalkSafety.safe(p,d,1.25);}
'''+s[b:]
a=s.index('  if(o.dir<0||p.tickCount%5==0');b=s.index('  if(o.dir<16){p.setYRot',a)
s=s[:a]+'''  if(p.tickCount%20==0){
   double progress=now.subtract(o.checkpoint).horizontalDistance();
   if(o.dir>=0&&o.dir<16&&progress<.28){o.stuck++;o.avoid=o.dir;}
   else if(progress>.60){o.stuck=0;o.avoid=-1;}
   o.checkpoint=now;
   if(o.stuck>=4){release(p,false);return;}
  }
  if(o.dir<0||o.dir==16||p.tickCount%5==0||!safe(p,direction(o.dir))){
   Vec3 away=now.subtract(o.origin).multiply(1,0,1);
   if(away.lengthSqr()<.01)away=p.getLookAngle().multiply(1,0,1);
   away=away.normalize();
   int best=-1;double score=-Double.MAX_VALUE;
   for(int i=0;i<16;i++){
    if(i==o.avoid)continue;
    Vec3 d=direction(i);if(!safe(p,d))continue;
    // Prefer an open escape corridor; permit a sideways detour around obstacles.
    double v=d.dot(away)+(i==o.dir?.28:0)+(GeassWalkSafety.safe(p,d,2.5)?.60:0)+(GeassWalkSafety.safe(p,d,4.0)?.35:0);
    if(v>score){best=i;score=v;}
   }
   if(best<0){best=16;o.blocked++;if(o.blocked>=60){release(p,false);return;}}
   else o.blocked=0;
   if(o.dir!=best||!p.hasEffect(VampireLife.GEASS_EXILE.get())){
    o.dir=best;p.removeEffect(VampireLife.GEASS_EXILE.get());p.addEffect(new MobEffectInstance(VampireLife.GEASS_EXILE.get(),o.ticks+20,best,false,false,false));
   }
  }
'''+s[b:]
s=s.replace('Component.translatable("message.noctismagic.geass_progress",(o.ticks+19)/20)','Component.translatable("message.noctismagic.geass_progress",(o.ticks+19)/20).withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE,net.minecraft.ChatFormatting.BOLD)',1)
p.write_text(s,encoding='utf-8')
p=java/'GeassExileClient.java';s=p.read_text(encoding='utf-8')
a=s.index('  input.leftImpulse=');b=s.index('  if(dir<16){',a)
s=s[:a]+'''  boolean walk=dir<16&&GeassWalkSafety.safe(p,GeassWalkSafety.direction(dir),.75);
  input.leftImpulse=0;input.forwardImpulse=walk?.72f:0;input.up=walk;input.down=false;input.left=false;input.right=false;input.shiftKeyDown=false;input.jumping=false;
'''+s[b:]
p.write_text(s,encoding='utf-8')
for lang in ('it_it','en_us'):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['message.noctismagic.geass_break']='Il Geass perde la presa: movimento interrotto.' if lang=='it_it' else 'Geass loses its hold: movement interrupted.'
 write_noctis_json_resource(p,d)

# Chamfered Minecraft-style heads with real flat front planes and matching UVs.
# Each ring has a short corner bevel, unlike the former egg-shaped radial loft.
write('VoxelPortrait.java','''package it.noctis.magic;
import it.noctis.magic.SculptedGuestsClient.Part;
import it.noctis.magic.SculptedGuestsClient.V;
import it.noctis.magic.SculptedGuestsClient.Q;
final class VoxelPortrait{
 static float clamp(float x){return Math.max(.025f,Math.min(.975f,x));}
 static float[][] ring(float y,float w,float d,float z,float c){
  return new float[][]{{-w+c,y,z-d},{w-c,y,z-d},{w,y,z-d+c},{w,y,z+d-c},{w-c,y,z+d},{-w+c,y,z+d},{-w,y,z+d-c},{-w,y,z-d+c}};
 }
 static V v(float[] a,float nx,float ny,float nz,boolean front,float uvWidth,float uvHeight){
  return new V(a[0],a[1],a[2],front?clamp(.5f+a[0]/uvWidth):.025f,clamp((a[1]+uvHeight)/uvHeight),nx,ny,nz);
 }
 static void head(Part p,int face,int skin,float uvWidth,float uvHeight,float... data){
  int n=data.length/5;float[][][] rings=new float[n][][];
  for(int i=0;i<n;i++){int k=i*5;rings[i]=ring(data[k],data[k+1],data[k+2],data[k+3],data[k+4]);}
  for(int i=0;i<n-1;i++)for(int j=0;j<8;j++){
   int k=(j+1)%8;float[] a=rings[i][j],b=rings[i+1][j],c=rings[i+1][k],d=rings[i][k];
   float nx=d[2]-a[2],nz=-(d[0]-a[0]),m=(float)Math.hypot(nx,nz);
   nx/=m;nz/=m;boolean f=j==0||j==1||j==7;
   p.faces.add(new Q(v(a,nx,0,nz,f,uvWidth,uvHeight),v(b,nx,0,nz,f,uvWidth,uvHeight),v(c,nx,0,nz,f,uvWidth,uvHeight),v(d,nx,0,nz,f,uvWidth,uvHeight),f?face:skin));
  }
  for(int end:new int[]{0,n-1}){
   float[][] r=rings[end];float[] center={0,r[0][1],(r[0][2]+r[4][2])*.5f};float ny=end==0?-1:1;
   V C=v(center,0,ny,0,false,uvWidth,uvHeight);
   for(int j=0;j<8;j++){
    V A=v(r[j],0,ny,0,false,uvWidth,uvHeight),B=v(r[(j+1)%8],0,ny,0,false,uvWidth,uvHeight);
    p.faces.add(end==0?new Q(C,B,A,C,skin):new Q(C,A,B,C,skin));
   }
  }
 }
 static V scale(V v,float x,float y,float z){
  return new V(v.x()*x,v.y()*y,v.z()*z,v.u(),v.v(),v.nx(),v.ny(),v.nz());
 }
 static void enlarge(Part p,float x,float y,float z){
  for(int i=0;i<p.faces.size();i++){Q q=p.faces.get(i);p.faces.set(i,new Q(scale(q.a(),x,y,z),scale(q.b(),x,y,z),scale(q.c(),x,y,z),scale(q.d(),x,y,z),q.tile()));}
  for(Part c:p.children){c.x*=x;c.y*=y;c.z*=z;enlarge(c,x,y,z);}
 }
}''')
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('            }else{\n                head.loft(6,40,');b=s.index('            // A low tapered hair shell',a)
s=s[:a]+'''            }else{
                VoxelPortrait.head(head,6,7,6.25f,7.8f,-7.85f,2.36f,2.12f,.10f,.36f,-7.25f,2.80f,2.53f,.02f,.46f,-5.00f,2.85f,2.53f,0,.46f,-3.00f,2.73f,2.45f,-.05f,.42f,-1.00f,2.34f,2.14f,-.13f,.48f,-.15f,1.92f,1.76f,-.12f,.41f);
            }
            if(cc){
                projectFace(head);
                head.loft(7,16,-4.8f,0,-2.36f,.14f,.10f,-3.9f,0,-2.55f,.24f,.23f,-3.05f,0,-2.78f,.33f,.29f,-2.80f,0,-2.62f,.23f,.15f);
            }else{
                // Shallow pixel-scale bridge and sculpted neck; no needle-shaped chin.
                head.loft(7,8,-4.30f,0,-2.43f,.12f,.08f,-3.45f,0,-2.58f,.24f,.17f,-2.94f,0,-2.70f,.30f,.18f,-2.70f,0,-2.48f,.21f,.10f);
                head.loft(7,8,-.65f,0,.03f,.79f,.80f,.55f,0,.03f,.97f,.95f,1.50f,0,.03f,1.12f,1.04f);
            }
            for(int side:new int[]{-1,1})head.oval(7,side*(cc?2.62f:2.82f),-3.60f,.06f,.30f,.66f,.42f);
'''+s[b:]
s=s.replace('AngularHeads.apply(head,6,cc?.85f:.82f,.98f,.94f,cc?.16f:.19f);','if(cc)AngularHeads.apply(head,6,.85f,.98f,.94f,.16f);',1)
# More layered block-like hair in front, without replacing the existing animated rear and side locks.
s=s.replace('q.loft(8,12,-.50f,0,.52f','q.loft(8,cc?12:8,-.50f,0,.52f',1)
p.write_text(s,encoding='utf-8')

p=java/'LucySculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   head.loft(6,64,');b=s.index('   head.oval(7,-3.02f',a)
s=s[:a]+'''   VoxelPortrait.head(head,6,7,6.5f,7.65f,-7.65f,2.43f,2.22f,.08f,.40f,-7.10f,2.92f,2.60f,.02f,.45f,-4.30f,3.03f,2.68f,-.02f,.48f,-2.10f,2.75f,2.45f,-.09f,.48f,-.65f,2.35f,2.08f,-.15f,.52f,0,1.91f,1.72f,-.15f,.43f);
   head.loft(7,8,-4.05f,0,-2.62f,.12f,.07f,-3.24f,0,-2.73f,.19f,.13f,-2.72f,0,-2.86f,.25f,.17f,-2.46f,0,-2.66f,.16f,.08f);
'''+s[b:]
p.write_text(s,encoding='utf-8')

p=java/'FaputaSculptedClient.java';s=p.read_text(encoding='utf-8')
a=s.index('   head.loft(5,32,');b=s.index('   // Cream crown',a)
s=s[:a]+'''   VoxelPortrait.head(head,5,0,6.4f,6.9f,-6.8f,2.45f,2.10f,.13f,.37f,-6.10f,2.90f,2.47f,.05f,.44f,-3.70f,2.88f,2.51f,-.04f,.46f,-2.0f,2.52f,2.23f,-.13f,.43f,-.48f,1.99f,1.75f,-.20f,.46f,0,1.59f,1.38f,-.23f,.35f);
   // A head-attached neck overlaps the body-attached neck across all pitch/yaw angles.
   head.loft(0,12,-.75f,0,.15f,.87f,.90f,0,0,.15f,1.02f,1.04f,1.12f,0,.19f,1.18f,1.13f,2.35f,0,.27f,1.30f,1.26f);
   body.loft(0,12,-4.05f,0,-.41f,1.03f,1.10f,-2.55f,0,-.29f,1.31f,1.28f,-1.00f,0,0,1.85f,1.47f);
   head.loft(0,8,-2.74f,0,-2.40f,.16f,.11f,-2.35f,0,-2.57f,.24f,.19f,-2.08f,0,-2.36f,.15f,.09f);
   for(int side:new int[]{-1,1}){
    head.blade(0,side*.60f,-3.78f,-2.54f,side*1.92f,-4.34f,-2.50f,.20f);
    // Multiple layered fur tufts along the cheeks and behind the ears.
    for(int j=0;j<5;j++)head.blade(1,side*(2.50f+.04f*j),-4.05f+j*.36f,.34f+j*.12f,side*(3.34f+.12f*j),-2.07f+j*.40f,.48f+j*.15f,.63f);
   }
'''+s[b:]
# Reposition and enlarge all four independent forelimbs; maintain their own animation pivots.
a='    // Thick furred haunches'
assert a in s
s=s.replace(a,'''    for(int j=0;j<2;j++){
     int k=i*2+j;
     for(int n=0;n<7;n++){
      float y=.68f+n*.48f,x=s*(.70f+.12f*(n%3));
      fore[k].blade(1,x,y,.35f,x+s*.64f,y+1.14f,.72f,.73f);
      fore[k].blade(1,-x*.8f,y,.48f,-x*.8f-s*.42f,y+1.02f,.88f,.50f);
     }
     VoxelPortrait.enlarge(arms[k],1.27f,1.14f,1.23f);
     arms[k].x+=s*(j==0?.24f:.16f);
    }
    // Thick furred haunches''',1)
a='   // Three individually animated'
s=s.replace(a,'''   // Jagged cream tufts on back, shoulders and hips, visible from behind.
   for(int side:new int[]{-1,1})for(int j=0;j<7;j++){
    float y=5.0f+j*.87f;
    body.blade(1,side*(1.40f+.18f*(j%3)),y,1.63f,side*(2.47f+.10f*(j%3)),y+1.35f,2.48f,.83f);
   }
   // Three individually animated''',1)
s=s.replace('head.z=-.35f-(rage?.38f:.14f);','head.z=-.35f-(rage?.18f:.08f);',1)
s=s.replace('head.y=-3.5f;','head.y=-3.15f;',1)
p.write_text(s,encoding='utf-8')

# More deliberately pixel-defined eye details, shading and hair, keeping each original palette.
for name,tile,hair,base,iris in [
 ('lelouch_sculpted',6,8,(233,178,145),(168,91,219)),
 ('lucy_sculpted',6,9,(250,226,212),(116,206,194)),
 ('faputa_sculpted',5,1,(128,99,76),(248,197,77)),
 ('faputa_rage',5,1,(128,99,76),(255,112,51))]:
 p=assets/'textures/entity'/f'{name}.png';W,H,pix=read_rgba(p)
 fap=name.startswith('faputa');lucy=name.startswith('lucy');rage=name.endswith('rage')
 for y in range(128):
  for x in range(128):
   u=sat2((x-3)/121);v=sat2((y-3)/121);f=abs(u-.5)
   # Pixel art planes: deliberate 2px clusters, not smooth sphere shading.
   U=round(u*60)/60;V=round(v*60)/60
   c=mix(base,(75,43,45) if fap else (151,91,93),.14*sat2((abs(U-.5)-.16)*4)+.09*V)
   c=mix(c,(180,135,96) if fap else (255,233,213),.17*math.exp(-((U-.50)/.17)**2-((V-.46)/.31)**2))
   for side in (-1,1):
    ex=.5+side*.174;dx=side*(U-ex)/(.111 if fap else .121);ey=.49-(.045 if fap else .024)*dx
    dy=(V-ey)/(.053 if fap else .055)
    d0=abs(dx)**1.6+abs(dy)**1.45
    if d0<1.17:c=(39,24,33)
    if d0<.82:c=(229,211,172) if fap else (247,240,231)
    if d0<.81 and abs(dx+.04)<.41:
     c=mix(shade(iris,.46),iris,sat2((dy+.7)/1.4))
     if abs(dx+.04)<(.10 if fap else .16):c=(24,17,28)
     if (dx+.16)**2+(dy+.20)**2<.055:c=(255,246,217)
    if abs(dx)<1.04 and abs(V-(.397-(.045 if fap else .025)*dx))<.011:c=(51,30,33) if fap else (62,39,48)
    if lucy and abs(dx)<.99 and .88<dy<1.20-.23*abs(dx):c=(194,62,86)
   if f<.028 and abs(V-.674)<.012:c=mix(c,(91,48,43) if fap else (167,99,100),.65)
   mouth=.787-(.024 if fap else .009)*(1-min(1,f/.09))+.025*(U-.5)
   if f<(.095 if fap else .066) and abs(V-mouth)<(.019 if rage else .009):c=(52,23,27) if fap else (123,57,74)
   if rage and .035<f<.067 and abs(V-mouth)<.013:c=(239,225,194)
   off=((tile//8*128+y)*W+tile%8*128+x)*4;pix[off:off+4]=bytes((*c,255))
   off=((hair//8*128+y)*W+hair%8*128+x)*4;c=tuple(pix[off:off+3])
   wave=math.sin(u*math.pi*(22 if fap else 33)+v*7+.32*math.sin(v*13))
   c=shade(c,.91+.16*max(0,wave)**5)
   pix[off:off+4]=bytes((*c,255))
 png(p,W,H,pix)
print('Colored NPC dialogue, safer Geass forced walking, voxel portrait heads and enlarged four-armed Faputa with overlapping neck geometry.')
