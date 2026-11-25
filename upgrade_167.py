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
 j(p,d)
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
 j(base/(ident+'.json'),{'parent':'noctismagic:rituals/'+parent,'display':{'icon':{'item':icon},'title':{'translate':'advancement.noctismagic.rituals.'+ident+'.title'},'description':{'translate':'advancement.noctismagic.rituals.'+ident+'.description'},'frame':'challenge' if ident=='cthulhu_complete' else 'goal','show_toast':True,'announce_to_chat':True,'hidden':False},'criteria':{'ritual':{'trigger':'minecraft:impossible'}},'rewards':{'experience':xp}})
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
 j(p,d)
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
edit('MoonGuest.java','UUID owner,aggressor;long expires;int rage,cd=20,witch=0,pose,animation,speech;','UUID owner,aggressor;long expires;int rage,cd=20,witch=0,pose,animation,speech;\n    private int smokeTicks=0,smokeCooldown=700;public int smokeTicks(){return smokeTicks;}')
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
 j(p,d)
print('Dedicated rebindable P pony power key, server ownership validation and localized taming/riding hints.')


# Avoid the vanilla social-interactions P shortcut opening over a mounted pony.
edit('PonyPowerKey.java','  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){','''  @SubscribeEvent public static void key(net.minecraftforge.client.event.InputEvent.Key e){
   Minecraft mc=Minecraft.getInstance();
   if(e.getAction()==GLFW.GLFW_PRESS&&mc.player!=null&&mc.screen==null&&mc.player.getVehicle() instanceof FriendshipPony&&POWER.matches(e.getKey(),e.getScanCode())){
    if(mc.options.keySocialInteractions.matches(e.getKey(),e.getScanCode()))while(mc.options.keySocialInteractions.consumeClick()){}
   }
  }
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){''')
