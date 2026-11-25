"""1.6.7: Black Swordsman, Geass spell and enigmatic quest journal."""
from pathlib import Path
import sys,json,math,struct,zlib,re
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
 p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(n,s):(java/n).write_text(s,encoding='utf-8')
def j(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
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
 j(base/(id+'.json'),{'parent':'noctismagic:rituals/'+parent,'display':{'icon':{'item':icon},'title':{'translate':'advancement.noctismagic.rituals.'+id+'.title'},'description':{'translate':'advancement.noctismagic.rituals.'+id+'.description'},'frame':'goal','show_toast':True,'announce_to_chat':True,'hidden':False},'criteria':{'ritual':{'trigger':'minecraft:impossible'}},'rewards':{'experience':xp}})
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
j(assets/'models/item/dragon_slayer.json',{'parent':'minecraft:item/handheld','textures':{'layer0':'noctismagic:item/dragon_slayer'},'display':{'thirdperson_righthand':{'rotation':[0,-90,55],'translation':[0,4,0],'scale':[1.65,1.65,1.65]},'thirdperson_lefthand':{'rotation':[0,90,-55],'translation':[0,4,0],'scale':[1.65,1.65,1.65]}}})
j(assets/'models/item/guts_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for i,lang in enumerate(('it_it','en_us')):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for id,t in clues.items():
  d['advancement.noctismagic.rituals.'+id+'.title']=t[i]
  d['advancement.noctismagic.rituals.'+id+'.description']=t[i+2]
 d['item.noctismagic.guts_spawn_egg']='Uovo generatore: Guts' if i==0 else 'Guts Spawn Egg'
 d['item.noctismagic.dragon_slayer']='Dragon Slayer'
 j(p,d)
print('Guts detailed model, safe eclipse arrival, Dragon Slayer, Geass and enigmatic quests installed.')
