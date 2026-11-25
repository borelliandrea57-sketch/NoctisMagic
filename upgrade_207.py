"""Creative spell access, tomato farming, pizza and Lelouch's Geass quest."""
from pathlib import Path
import sys,json,re,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,a,b):
 p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Creative access is enforced server-side, not merely in the menu.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
start=s.index('static void cast(ServerPlayer p,int id)')
a=s.index('{',start);b=a+1;depth=1
while depth:
 if s[b]=='{':depth+=1
 elif s[b]=='}':depth-=1
 b+=1
cast=s[a:b]
for expr in ['d.getInt("level")<s.level','d.getInt("mana")<s.cost','d.getInt("cooldown")>0']:
 if expr in cast:cast=cast.replace('if('+expr+')','if(!p.isCreative()&&'+expr+')',1)
assert '!p.isCreative()&&d.getInt("level")<s.level' in cast or 'p.isCreative()' in cast
assert '!p.isCreative()&&d.getInt("mana")<s.cost' in cast or 'p.isCreative()' in cast
cast,n=re.subn(r'd\.putInt\("mana",\s*d\.getInt\("mana"\)\s*-\s*s\.cost\);',r'if(!p.isCreative())d.putInt("mana",d.getInt("mana")-s.cost);',cast,count=1)
# Creative still performs targeting and safe teleport validation; no mana charge.
if n==0:
 cast=cast.replace('d.putInt("mana",Math.max(0,d.getInt("mana")-s.cost));','if(!p.isCreative())d.putInt("mana",Math.max(0,d.getInt("mana")-s.cost));')
s=s[:a]+cast+s[b:]
s=s.replace('GEASS("Geass - Controllo mentale",5,45)','GEASS("Geass - Controllo mentale",1,45)')
anchor='public static final RegistryObject<Item> PIZZA=ITEMS.register'
assert anchor in s
s=s.replace(anchor,'''public static final RegistryObject<net.minecraft.world.level.block.Block> TOMATO_CROP=VampireLife.BLOCKS.register("tomato_crop",()->new TomatoCrop(net.minecraft.world.level.block.state.BlockBehaviour.Properties.copy(net.minecraft.world.level.block.Blocks.CARROTS)));
    public static final RegistryObject<Item> TOMATO=ITEMS.register("tomato",()->new Item(new Item.Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(2).saturationMod(.3f).build())));
    public static final RegistryObject<Item> TOMATO_SEEDS=ITEMS.register("tomato_seeds",()->new net.minecraft.world.item.ItemNameBlockItem(TOMATO_CROP.get(),new Item.Properties()));
    '''+anchor,1)
anchor='e.accept(PIZZA.get());'
assert anchor in s
s=s.replace('if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS)e.accept(PIZZA.get());','if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS){e.accept(PIZZA.get());e.accept(TOMATO.get());}',1)
# Also list in Natural Blocks so the planting item is easy to find.
s=s.replace('if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)','if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)e.accept(TOMATO_SEEDS.get());if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)',1)
p.write_text(s,encoding='utf-8')
(java/'TomatoCrop.java').write_text('''package it.noctis.magic;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.ItemLike;
public final class TomatoCrop extends CropBlock {
 public TomatoCrop(BlockBehaviour.Properties p){super(p);}
 @Override protected ItemLike getBaseSeedId(){return Noctis.TOMATO_SEEDS.get();}
}''',encoding='utf-8')
(java/'TomatoHarvest.java').write_text('''package it.noctis.magic;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class TomatoHarvest {
 @SubscribeEvent(priority=EventPriority.LOWEST)
 public static void grass(BlockEvent.BreakEvent e){
  if(!(e.getLevel() instanceof ServerLevel l)||e.getPlayer().isCreative()||!l.getGameRules().getBoolean(GameRules.RULE_DOBLOCKDROPS))return;
  if((e.getState().is(Blocks.GRASS)||e.getState().is(Blocks.TALL_GRASS))&&l.random.nextInt(8)==0)
   Block.popResource(l,e.getPos(),new ItemStack(Noctis.TOMATO_SEEDS.get()));
 }
}''',encoding='utf-8')
# Direct offering to Lelouch grants the spell; C.C. can still accept her own pizza.
p=java/'DramaGuest.java';s=p.read_text(encoding='utf-8')
a=s.index('    @Override public InteractionResult mobInteract(Player p,InteractionHand h){')
s=s[:a]+'''    private int pizzaJoy=0;
    private void pizzaHearts(ServerLevel l){
        pizzaJoy=60;
        l.sendParticles(ParticleTypes.HEART,getX(),getEyeY()+.35,getZ(),16,.40,.33,.40,.035);
    }
    private void teachGeass(ServerPlayer sp,ServerLevel l){
        RitualQuests.award(sp,"lelouch");
        if(!Noctis.data(sp).getBoolean("GeassLearned")){
            Noctis.data(sp).putBoolean("GeassLearned",true);
            Noctis.data(sp).putBoolean("GeassPizza",true);
            RitualQuests.complete(sp,"lelouch");
            say(l,"La strega e' soddisfatta. In cambio, ti concedo il potere dei re: il Geass.");
            sp.sendSystemMessage(Component.literal("Nuova magia appresa: Geass - Controllo mentale.").withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));
        }else say(l,"Il patto e' gia' stretto. C.C. apprezzera' il pensiero.");
        Noctis.sync(sp);
    }
'''+s[a:]
anchor='if(h!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;'
# Restrict injection to mobInteract, avoiding changes to unrelated routines.
a=s.index(anchor,s.index('    @Override public InteractionResult mobInteract(Player p,InteractionHand h){'))
a+=len(anchor)
s=s[:a]+'''
        if((kind()==1||kind()==2)&&p.getItemInHand(h).is(Noctis.PIZZA.get())){
            if(level() instanceof ServerLevel l&&p instanceof ServerPlayer sp){
                if(pizzaCd>0)return InteractionResult.CONSUME;
                pizzaCd=60;
                if(!p.getAbilities().instabuild)p.getItemInHand(h).shrink(1);
                RitualQuests.award(sp,"lelouch");
                Noctis.data(sp).putBoolean("GeassPizza",true);
                if(kind()==1){
                    teachGeass(sp,l);
                    DramaGuest cc=partner!=null&&l.getEntity(partner) instanceof DramaGuest q&&q.kind()==2&&q.isAlive()?q:
                      l.getEntitiesOfClass(DramaGuest.class,getBoundingBox().inflate(14),q->q.kind()==2&&q.isAlive()).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
                    if(cc!=null){cc.say(l,"Pizza! Lelouch, questo si' che e' un ottimo piano.");cc.pizzaHearts(l);}
                }else{
                    say(l,"Finalmente una pizza!");pizzaHearts(l);
                    if(partner!=null&&l.getEntity(partner) instanceof DramaGuest q&&q.kind()==1&&q.isAlive())q.teachGeass(sp,l);
                    else sp.sendSystemMessage(Component.literal("Lo sguardo del re ti attende."));
                }
            }
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
'''+s[a:]
# Migrate previously earned pizza flags via existing dialogue without requiring a second payment.
s=s.replace('Noctis.data(sp).putBoolean("GeassLearned",true);say(l,"Il tuo gesto non mi e\' sfuggito. Il Geass ora ti appartiene.");','teachGeass(sp,l);',1)
s=s.replace('sp.sendSystemMessage(Component.literal("Nuova magia appresa: Geass (livello 5).").withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));','',1)
a=s.index('    @Override public void tick(){');a=s.index('super.tick();',a)+len('super.tick();')
s=s[:a]+'''if(pizzaJoy>0){pizzaJoy--;if(pizzaJoy%8==0&&level() instanceof ServerLevel joyLevel)joyLevel.sendParticles(ParticleTypes.HEART,getX(),getEyeY()+.30,getZ(),3,.35,.25,.35,.025);}'''+s[a:]
p.write_text(s,encoding='utf-8')
# The quest rewards the delivery, not an unrelated first successful cast.
p=java/'GeassMagic.java';s=p.read_text(encoding='utf-8');s=s.replace('RitualQuests.complete(p,"lelouch");return true;','return true;',1);p.write_text(s,encoding='utf-8')
# Client grimoire and HUD must respect creative mode without overwriting saved level/mana.
p=java/'Client.java';s=p.read_text(encoding='utf-8')
s=s.replace('private boolean unlocked(Noctis.Spell spell){return spell.level<=Noctis.View.level;}','private boolean unlocked(Noctis.Spell spell){return minecraft!=null&&minecraft.player!=null&&minecraft.player.isCreative()||spell.level<=Noctis.View.level;}',1)
s=s.replace('boolean ready=mana>=spell.cost&&lv>=spell.level&&cd==0;','boolean ready=mc.player.isCreative()||mana>=spell.cost&&lv>=spell.level&&cd==0;',1)
s=s.replace('String state=cd>0?','String state=mc.player.isCreative()?"FREE":cd>0?',1)
s=s.replace('String meta=spell.cost+" MP  |  Lv "+spell.level;','boolean creative=minecraft!=null&&minecraft.player!=null&&minecraft.player.isCreative();String meta=creative?"Gratis - Creativa":spell==Noctis.Spell.GEASS?"45 MP | Patto":spell.cost+" MP  |  Lv "+spell.level;',1)
s=s.replace('String info="Lv "+lv+"   |   MP "+mana+"/"+max;','String info=minecraft!=null&&minecraft.player!=null&&minecraft.player.isCreative()?"CREATIVA | Tutte le magie":"Lv "+lv+"   |   MP "+mana+"/"+max;',1)
p.write_text(s,encoding='utf-8')
# Tomato is both food and a planting item, like carrots.
dump(res/'data/noctismagic/recipes/pizza.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'minecraft:wheat'},{'item':'minecraft:wheat'},{'item':'noctismagic:tomato'},{'item':'minecraft:milk_bucket'}],'result':{'item':'noctismagic:pizza','count':2}})
dump(assets/'models/item/tomato_seeds.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/tomato_seeds'}})
dump(assets/'models/item/tomato.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/tomato'}})
dump(assets/'blockstates/tomato_crop.json',{'variants':{'age='+str(i):{'model':'noctismagic:block/tomato_stage'+str(i//2)} for i in range(8)}})
for i in range(4):
 dump(assets/('models/block/tomato_stage'+str(i)+'.json'),{'parent':'minecraft:block/crop','render_type':'minecraft:cutout','textures':{'crop':'noctismagic:block/tomato_stage'+str(i)}})
dump(res/'data/noctismagic/loot_tables/blocks/tomato_crop.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:tomato_seeds'}],'conditions':[{'condition':'minecraft:survives_explosion'}]},{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:tomato','functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':2,'max':4}},{'function':'minecraft:apply_bonus','enchantment':'minecraft:fortune','formula':'minecraft:uniform_bonus_count','parameters':{'bonusMultiplier':1}}]}],'conditions':[{'condition':'minecraft:block_state_property','block':'noctismagic:tomato_crop','properties':{'age':'7'}},{'condition':'minecraft:survives_explosion'}]}]})
# Hand-painted pixel art: edible ripe fruit and four visible growth stages.
def fruit(d,x,y,r):
 d.ellipse((x-r,y-r,x+r,y+r),fill=(102,27,23,255))
 d.ellipse((x-r+1,y-r+1,x+r-1,y+r-1),fill=(217,48,31,255))
 d.ellipse((x-r+2,y-r+2,x,y),fill=(255,111,59,255))
 d.line((x-2,y-r+1,x,y-r-2,x+3,y-r+1),fill=(47,109,42,255),width=2)
im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im);fruit(d,16,18,11)
d.polygon([(16,7),(11,5),(13,10),(7,10),(15,13),(21,9),(25,10),(19,5)],fill=(40,114,48,255))
d.rectangle((15,3,17,8),fill=(89,143,49,255))
(assets/'textures/item').mkdir(parents=True,exist_ok=True);im.save(assets/'textures/item/tomato.png')
(assets/'textures/block').mkdir(parents=True,exist_ok=True)
seed=Image.new('RGBA',(32,32));d=ImageDraw.Draw(seed)
for x,y in [(8,10),(19,7),(13,19),(23,20),(7,25),(21,27)]:
 d.ellipse((x-3,y-2,x+3,y+2),fill=(110,76,40,255));d.ellipse((x-2,y-2,x+2,y+1),fill=(224,192,119,255));d.point((x-1,y-1),fill=(255,230,165,255))
seed.save(assets/'textures/item/tomato_seeds.png')
for i in range(4):
 im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im);h=8+i*6
 d.line((16,31,16,31-h),fill=(54,110,42,255),width=2)
 for y in range(29,31-h,-5):
  d.line((16,y,10,y-3),fill=(52,116,43,255),width=2)
  d.line((16,y-2,23,y-5),fill=(70,137,46,255),width=2)
  d.polygon([(10,y-3),(5,y-5),(7,y-1),(12,y)],fill=(61,130,39,255))
  d.polygon([(23,y-5),(28,y-7),(26,y-2),(21,y-2)],fill=(80,155,48,255))
 if i==2:
  d.ellipse((9,17,13,21),fill=(227,213,89,255));d.ellipse((20,11,24,15),fill=(227,213,89,255))
 if i==3:
  fruit(d,10,20,4);fruit(d,23,14,4);fruit(d,15,8,3)
 im.save(assets/('textures/block/tomato_stage'+str(i)+'.png'))
for lang in ('it_it','en_us'):
 p=assets/('lang/'+lang+'.json');d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
 d['item.noctismagic.tomato']='Pomodoro' if it else 'Tomato'
 d['item.noctismagic.tomato_seeds']='Semi di pomodoro' if it else 'Tomato seeds'
 d['block.noctismagic.tomato_crop']='Pianta di pomodoro' if it else 'Tomato plant'
 d['advancement.noctismagic.rituals.lelouch.title']='La fame della strega' if it else 'The witch’s hunger'
 d['advancement.noctismagic.rituals.lelouch.description']='Un re mascherato, una strega affamata.' if it else 'A masked king, a hungry witch.'
 d['advancement.noctismagic.rituals.lelouch_complete.title']='Il patto del re' if it else 'The king’s pact'
 d['advancement.noctismagic.rituals.lelouch_complete.description']='La strega sorride. Una pupilla scarlatta ti concede il suo potere.' if it else 'The witch smiles. A crimson eye grants you its power.'
 dump(p,d)
for id in ('lelouch','lelouch_complete'):
 p=res/('data/noctismagic/advancements/rituals/'+id+'.json')
 d=json.loads(p.read_text(encoding='utf-8'))
 if 'display' in d:d['display']['icon']={'item':'noctismagic:pizza' if id=='lelouch' else 'minecraft:ender_eye'}
 dump(p,d)
print('Creative free spell casting, tomato cultivation, pizza recipe and Lelouch pact with C.C. heart particles.')
