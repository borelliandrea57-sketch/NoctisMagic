"""1.6.5: ritual quest advancements, larger paired NPCs, denser friendly vampires, bakery clerk egg."""
from pathlib import Path
import sys,json,re
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,a,b):
 p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def j(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
# Only actual successful ritual summons count, not spawn eggs or /summon.
edit('MiracleEncounter.java','if(!l.noCollision(v)||!l.addFreshEntity(v))continue;','if(!l.noCollision(v)||!l.addFreshEntity(v))continue;\n                RitualQuests.summon(p,v,"jesus");')
edit('MiracleVisitor.java','if(visit==35){','if(visit==35){RitualQuests.complete(p,"jesus");')
edit('DragonWish.java','data.putUUID("dragonWishId",d.getUUID());','RitualQuests.summon(p,d,"shenron");data.putUUID("dragonWishId",d.getUUID());')
edit('DragonWish.java','d.fulfill();','d.fulfill();RitualQuests.complete(p,"shenron");')
edit('FallenEncounter.java','if(!l.noCollision(boss)||!l.addFreshEntity(boss))continue;','if(!l.noCollision(boss)||!l.addFreshEntity(boss))continue;\n            RitualQuests.summon(p,boss,"sephiroth");')
edit('CatRitual.java','boss.bind(p);if(l.addFreshEntity(boss)){','boss.bind(p);if(l.addFreshEntity(boss)){\n                RitualQuests.summon(p,boss,"miaugusto");')
edit('ExodiaRitual.java','if(!l.addFreshEntity(boss))return;','if(!l.addFreshEntity(boss))return;\n  RitualQuests.summon(p,boss,"exodia");')
(java/'RitualQuests.java').write_text('''package it.noctis.magic;
import net.minecraft.advancements.Advancement;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class RitualQuests {
 static Advancement find(ServerPlayer p,String id){return p.serverLevel().getServer().getAdvancements().getAdvancement(new ResourceLocation(Noctis.ID,"rituals/"+id));}
 static boolean done(ServerPlayer p,String id){Advancement a=find(p,id);return a!=null&&p.getAdvancements().getOrStartProgress(a).isDone();}
 static void award(ServerPlayer p,String id){
  Advancement a=find(p,id);if(a==null||p.getAdvancements().getOrStartProgress(a).isDone())return;
  p.getAdvancements().award(a,"ritual");
 }
 public static void summon(ServerPlayer p,Entity e,String id){
  e.getPersistentData().putUUID("NoctisQuestSummoner",p.getUUID());
  e.getPersistentData().putString("NoctisQuestRitual",id);
  award(p,id);
 }
 public static void complete(ServerPlayer p,String id){if(done(p,id))award(p,id+"_complete");}
 @SubscribeEvent public static void defeat(LivingDeathEvent ev){
  Entity boss=ev.getEntity();var d=boss.getPersistentData();
  String id=d.getString("NoctisQuestRitual");
  if(!id.equals("sephiroth")&&!id.equals("miaugusto")&&!id.equals("exodia"))return;
  if(!d.hasUUID("NoctisQuestSummoner"))return;
  Entity killer=ev.getSource().getEntity();
  if(!(killer instanceof ServerPlayer)&&!(killer instanceof TamableAnimal tame&&tame.getOwner() instanceof ServerPlayer))return;
  if(!(boss.level() instanceof net.minecraft.server.level.ServerLevel l))return;
  ServerPlayer owner=l.getServer().getPlayerList().getPlayer(d.getUUID("NoctisQuestSummoner"));
  if(owner!=null&&owner.level()==l&&owner.distanceToSqr(boss)<128*128)complete(owner,id);
 }
}''',encoding='utf-8')
base=res/'data/noctismagic/advancements/rituals'
def advancement(id,title,desc,icon,parent=None,xp=0,frame='task',auto=False):
 display={'icon':{'item':icon},'title':{'translate':'advancement.noctismagic.rituals.'+id+'.title'},'description':{'translate':'advancement.noctismagic.rituals.'+id+'.description'},'frame':frame,'show_toast':not auto,'announce_to_chat':not auto,'hidden':False}
 d={'display':display,'criteria':{'ritual':{'trigger':'minecraft:tick' if auto else 'minecraft:impossible'}}}
 if parent:d['parent']='noctismagic:rituals/'+parent
 else:display['background']='minecraft:textures/gui/advancements/backgrounds/stone.png'
 if xp:d['rewards']={'experience':xp}
 j(base/(id+'.json'),d)
 strings[id]=(title,desc)
strings={}
advancement('root',('Rituali di Noctis','Noctis Rituals'),('Scopri le cinque evocazioni segrete.','Discover the five secret summons.'),'minecraft:enchanted_book',auto=True)
quests=[
 ('jesus','Una preghiera ascoltata','An answered prayer','Scrivi Gesu aiutami in chat e invoca Gesu.','Say Gesu aiutami in chat to summon Jesus.','minecraft:bread','Il miracolo','The miracle','Ricevi il dono di Gesu.','Receive the gift from Jesus.',75),
 ('shenron','Le sette sfere','The seven balls','Riunisci le sette Sfere del Drago e invoca Shenron.','Collect all seven Dragon Balls and summon Shenron.','minecraft:dragon_egg','Desiderio esaudito','Wish granted','Esprimi un desiderio a Shenron.','Make a wish to Shenron.',150),
 ('sephiroth','One Winged Angel','One Winged Angel','Evoca Sephiroth tramite il cartello One Winged Angel.','Summon Sephiroth with a One Winged Angel sign.','minecraft:netherite_sword','L angelo caduto','The fallen angel','Sconfiggi Sephiroth evocato dal rituale.','Defeat Sephiroth summoned by your ritual.',350),
 ('miaugusto','Il patto felino','The feline pact','Addomestica cinque gatti e invoca Miaugusto.','Tame five cats and summon Miaugusto.','minecraft:cod','Il re delle crocchette','The kibble king','Sconfiggi Miaugusto dopo il rituale.','Defeat Miaugusto after the ritual.',300),
 ('exodia','Il Proibito','The Forbidden One','Raccogli le cinque parti nei bauli e libera Exodia.','Find the five chest relics and release Exodia.','noctismagic:exodia_head','Obliterazione','Obliteration','Sconfiggi Exodia dopo averlo liberato.','Defeat Exodia after releasing him.',500)]
for id,it,en,di,de,icon,ct,ce,ci,cd,xp in quests:
 advancement(id,(it,en),(di,de),icon,'root',50,'goal')
 advancement(id+'_complete',(ct,ce),(ci,cd),'noctismagic:exodia_seal' if id=='exodia' else icon,id,xp,'challenge' if id in ('sephiroth','miaugusto','exodia') else 'goal')
# More frequent friendly vampires, including the unique protective visitor.
edit('VampireSpacing.java','x*x+z*z<1000000','x*x+z*z<9216')
edit('VincentTerritory.java','dx*dx+dz*dz<1000000L','dx*dx+dz*dz<25600L')
p=java/'Vincent.java';s=p.read_text(encoding='utf-8')
# Some releases place spawning in a separate event class. Search only the original explicit conditions.
for f in java.glob('*.java'):
 s=f.read_text(encoding='utf-8')
 if 'VincentTerritory.available(l,p.blockPosition(),null)' in s and 'p.getRandom().nextInt(12)!=0' in s:
  s=s.replace('p.getRandom().nextInt(12)!=0','p.getRandom().nextInt(4)!=0',1);f.write_text(s,encoding='utf-8')
# Geometry and entity hitboxes: increase height 14-18% and shoulder width around 8%.
edit('GeassSculptedClient.java','float s=cc?.94f:1.02f;p.scale(s,s,s);','float s=cc?1.10f:1.17f;p.scale(s*1.04f,s,s);')
edit('GeassSculptedClient.java','cc?3.0f:3.65f,1.8f,2.6f,0,-.1f,cc?3.0f:3.45f','cc?3.22f:3.92f,1.8f,2.6f,0,-.1f,cc?3.21f:3.68f')
edit('GeassSculptedClient.java','s*(cc?3.8f:4.15f)','s*(cc?4.02f:4.43f)')
edit('SculptedGuestsClient.java','float s=k==1?1.38f:k==2?.92f:k==3?.98f:1;p.scale(s,s,s);','float s=k==1?1.38f:k==2?1.09f:k==3?1.14f:1;float w=k==2||k==3?1.04f:1;p.scale(s*w,s,s);')
edit('SculptedGuestsClient.java','0,0,0,3.6f,2,2,0,0,3.7f,2.1f','0,0,0,gem?3.88f:3.6f,2,2,0,0,gem?3.96f:3.7f,2.1f')
edit('SculptedGuestsClient.java','root.child(s*4,0,0)','root.child(s*(gem?4.25f:4f),0,0)')
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
for kind,width,height in [('lelouch',.75,2.23),('cc',.72,2.20),('phosphophyllite',.70,2.18),('cinnabar',.72,2.20)]:
 pattern=r'(ENTITIES.register\("'+kind+r'",[^\n]*?\.sized\()[^)]*(\))'
 s,n=re.subn(pattern,lambda m:m.group(1)+str(width)+'f,'+str(height)+'f'+m.group(2),s,count=1)
 assert n==1,kind
# Existing satirical baker NPC, now also individually available in creative.
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
assert a in s
s=s.replace(a,'public static final RegistryObject<Item> BAKER_HITLER_EGG=ITEMS.register("baker_hitler_spawn_egg",()->new ForgeSpawnEggItem(BAKER_HITLER,0x665c4a,0xe4d7bd,new Item.Properties()));\n    '+a,1)
a='e.accept(CATHEDRAL_EGG.get());';assert a in s;s=s.replace(a,a+'e.accept(BAKER_HITLER_EGG.get());',1)
p.write_text(s,encoding='utf-8')
j(assets/'models/item/baker_hitler_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for index,lang in enumerate(('it_it','en_us')):
 p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
 for id,(t,desc) in strings.items():
  d['advancement.noctismagic.rituals.'+id+'.title']=t[index]
  d['advancement.noctismagic.rituals.'+id+'.description']=desc[index]
 d['item.noctismagic.baker_hitler_spawn_egg']='Uovo generatore: Hitler panettiere' if index==0 else 'Baker Hitler Spawn Egg'
 j(p,d)
print('Ritual quest tab (10 quests), friendly vampire spacing, larger Geass/gem guests, individual bakery clerk egg.')
