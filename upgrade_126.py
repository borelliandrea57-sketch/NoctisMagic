"""1.2.6: washing machine and dishwasher, persistent upgrade cycles and enchantments."""
from pathlib import Path
import sys,json,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
edit('Furniture.java','    static final RegistryObject<BlockEntityType<StorageEntity>> STORAGE=', '''    public static final RegistryObject<Block> WASHING_MACHINE=VampireLife.BLOCKS.register("washing_machine",()->new UpgradeAppliance(true));
    public static final RegistryObject<Block> DISHWASHER=VampireLife.BLOCKS.register("dishwasher",()->new UpgradeAppliance(false));
    public static final RegistryObject<Item> WASHING_MACHINE_ITEM=Noctis.ITEMS.register("washing_machine",()->new BlockItem(WASHING_MACHINE.get(),new Item.Properties()));
    public static final RegistryObject<Item> DISHWASHER_ITEM=Noctis.ITEMS.register("dishwasher",()->new BlockItem(DISHWASHER.get(),new Item.Properties()));
    static final RegistryObject<BlockEntityType<UpgradeAppliance.Cycle>> APPLIANCE=TYPES.register("upgrade_appliance",()->BlockEntityType.Builder.of(UpgradeAppliance.Cycle::new,WASHING_MACHINE.get(),DISHWASHER.get()).build(null));
    static final RegistryObject<BlockEntityType<StorageEntity>> STORAGE=''')
edit('Noctis.java','if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){','if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){e.accept(Furniture.WASHING_MACHINE_ITEM.get());e.accept(Furniture.DISHWASHER_ITEM.get());')
(java/'UpgradeAppliance.java').write_text('''package it.noctis.magic;
import java.util.UUID;
import java.util.Map;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.item.enchantment.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
public class UpgradeAppliance extends Furniture.FurnitureBlock implements EntityBlock{
    final boolean washing;
    static final String MARK="NoctisWashLevel";
    UpgradeAppliance(boolean washing){super(0);this.washing=washing;}
    @Override public BlockEntity newBlockEntity(BlockPos pos,BlockState state){return new Cycle(pos,state);}
    @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level l,BlockState s,BlockEntityType<T> t){
        return l.isClientSide?null:(world,pos,state,be)->{if(be instanceof Cycle c)c.run(world,pos,state);};
    }
    static boolean clothing(ItemStack s){return s.getItem() instanceof ArmorItem||s.getItem() instanceof ElytraItem;}
    boolean accepts(ItemStack s){return !s.isEmpty()&&s.getCount()==1&&s.isDamageableItem()&&(washing?clothing(s):!clothing(s));}
    static int countShards(Player p){int n=0;for(int i=0;i<p.getInventory().getContainerSize();i++){ItemStack s=p.getInventory().getItem(i);if(s.is(Items.AMETHYST_SHARD))n+=s.getCount();}return n;}
    static void takeShards(Player p,int n){for(int i=0;i<p.getInventory().getContainerSize()&&n>0;i++){ItemStack s=p.getInventory().getItem(i);if(s.is(Items.AMETHYST_SHARD)){int k=Math.min(n,s.getCount());s.shrink(k);n-=k;}}p.getInventory().setChanged();}
    @Override public InteractionResult use(BlockState s,Level l,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit){
        if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        if(l.isClientSide)return InteractionResult.SUCCESS;
        if(!(l.getBlockEntity(pos) instanceof Cycle c))return InteractionResult.FAIL;
        if(!c.stack.isEmpty()){
            if(c.owner!=null&&!c.owner.equals(p.getUUID())&&!p.hasPermissions(2)){p.displayClientMessage(Component.literal("Ciclo riservato a un altro giocatore."),true);return InteractionResult.CONSUME;}
            if(!c.finished){p.displayClientMessage(Component.literal("Ciclo in corso: "+Math.max(1,(c.end-l.getGameTime()+19)/20)+" s"),true);return InteractionResult.CONSUME;}
            ItemStack out=c.stack;c.stack=ItemStack.EMPTY;c.owner=null;c.finished=false;c.end=0;c.setChanged();
            if(!p.getInventory().add(out))p.drop(out,false);
            p.displayClientMessage(Component.literal("Oggetto potenziato ritirato!"),true);return InteractionResult.CONSUME;
        }
        ItemStack held=p.getItemInHand(hand);
        if(!accepts(held)){p.displayClientMessage(Component.literal(washing?"Lavatrice: tieni in mano un'armatura o elitre.":"Lavastoviglie: tieni in mano un'arma o un attrezzo con durabilita'."),true);return InteractionResult.CONSUME;}
        int grade=held.hasTag()?held.getTag().getInt(MARK):0;
        if(grade>=3){p.displayClientMessage(Component.literal("Questo oggetto ha gia' raggiunto il livello III."),true);return InteractionResult.CONSUME;}
        int price=grade+1;
        if(!p.getAbilities().instabuild&&(p.experienceLevel<price||countShards(p)<price)){p.displayClientMessage(Component.literal("Servono "+price+" livelli XP e "+price+" frammenti di ametista."),true);return InteractionResult.CONSUME;}
        if(!p.getAbilities().instabuild){takeShards(p,price);p.giveExperienceLevels(-price);}
        c.stack=held.copy();held.shrink(1);c.owner=p.getUUID();c.end=l.getGameTime()+120;c.finished=false;c.setChanged();
        l.setBlock(pos,s.setValue(LIT,true),3);l.playSound(null,pos,SoundEvents.BUCKET_EMPTY,SoundSource.BLOCKS,.8f,1.2f);
        p.displayClientMessage(Component.literal("Ciclo di potenziamento "+(grade+1)+"/3: 6 secondi."),true);return InteractionResult.CONSUME;
    }
    static boolean boost(ItemStack stack,Map<Enchantment,Integer> map,Enchantment enchant,int cap){
        if(!enchant.canEnchant(stack)||map.getOrDefault(enchant,0)>=cap)return false;
        for(Enchantment existing:map.keySet())if(existing!=enchant&&!existing.isCompatibleWith(enchant))return false;
        map.put(enchant,Math.min(cap,map.getOrDefault(enchant,0)+1));return true;
    }
    static void upgrade(ItemStack stack,boolean washing){
        int grade=stack.getOrCreateTag().getInt(MARK);Map<Enchantment,Integer> map=EnchantmentHelper.getEnchantments(stack);
        boost(stack,map,Enchantments.UNBREAKING,3);
        if(washing){
            if(stack.getItem() instanceof ArmorItem){
                if(!boost(stack,map,Enchantments.ALL_DAMAGE_PROTECTION,3)){
                    for(Enchantment e:new Enchantment[]{Enchantments.FIRE_PROTECTION,Enchantments.BLAST_PROTECTION,Enchantments.PROJECTILE_PROTECTION})
                        if(map.containsKey(e)){boost(stack,map,e,3);break;}
                }
            }
        }else if(stack.getItem() instanceof BowItem)boost(stack,map,Enchantments.POWER_ARROWS,3);
        else if(stack.getItem() instanceof CrossbowItem)boost(stack,map,Enchantments.QUICK_CHARGE,3);
        else if(stack.getItem() instanceof TridentItem)boost(stack,map,Enchantments.IMPALING,3);
        else if(stack.getItem() instanceof SwordItem||stack.getItem() instanceof AxeItem){
            if(!boost(stack,map,Enchantments.SHARPNESS,3))for(Enchantment e:new Enchantment[]{Enchantments.SMITE,Enchantments.BANE_OF_ARTHROPODS})if(map.containsKey(e)){boost(stack,map,e,3);break;}
            if(stack.getItem() instanceof AxeItem)boost(stack,map,Enchantments.BLOCK_EFFICIENCY,3);
        }else boost(stack,map,Enchantments.BLOCK_EFFICIENCY,3);
        EnchantmentHelper.setEnchantments(map,stack);
        stack.setDamageValue(Math.max(0,stack.getDamageValue()-Math.max(1,stack.getMaxDamage()/4)));
        stack.getOrCreateTag().putInt(MARK,Math.min(3,grade+1));
    }
    @Override public void onRemove(BlockState old,Level l,BlockPos pos,BlockState next,boolean moving){
        if(!old.is(next.getBlock())&&l instanceof ServerLevel&&l.getBlockEntity(pos) instanceof Cycle c&&!c.stack.isEmpty()){
            ItemStack out=c.stack;c.stack=ItemStack.EMPTY;c.setChanged();Containers.dropItemStack(l,pos.getX()+.5,pos.getY()+.5,pos.getZ()+.5,out);
        }super.onRemove(old,l,pos,next,moving);
    }
    public static class Cycle extends BlockEntity{
        ItemStack stack=ItemStack.EMPTY;UUID owner;long end;boolean finished;
        public Cycle(BlockPos p,BlockState s){super(Furniture.APPLIANCE.get(),p,s);}
        void run(Level l,BlockPos pos,BlockState s){
            if(!(l instanceof ServerLevel sl)||stack.isEmpty()||finished)return;
            if(l.getGameTime()>=end){
                if(s.getBlock() instanceof UpgradeAppliance machine)upgrade(stack,machine.washing);
                finished=true;setChanged();l.setBlock(pos,s.setValue(LIT,false),3);
                l.playSound(null,pos,SoundEvents.PLAYER_LEVELUP,SoundSource.BLOCKS,.8f,1.4f);
                sl.sendParticles(ParticleTypes.ENCHANT,pos.getX()+.5,pos.getY()+1,pos.getZ()+.5,24,.35,.3,.35,.08);
            }else if(l.getGameTime()%10==0){
                Direction front=s.getValue(FACING);sl.sendParticles(ParticleTypes.SPLASH,pos.getX()+.5+front.getStepX()*.52,pos.getY()+.65,pos.getZ()+.5+front.getStepZ()*.52,6,.16,.16,.16,.04);
                if(l.getGameTime()%20==0)l.playSound(null,pos,SoundEvents.WATER_AMBIENT,SoundSource.BLOCKS,.25f,1.1f);
            }
        }
        @Override public void load(CompoundTag t){super.load(t);stack=t.contains("Stack")?ItemStack.of(t.getCompound("Stack")):ItemStack.EMPTY;owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;end=t.getLong("End");finished=t.getBoolean("Finished");}
        @Override protected void saveAdditional(CompoundTag t){super.saveAdditional(t);if(!stack.isEmpty())t.put("Stack",stack.save(new CompoundTag()));if(owner!=null)t.putUUID("Owner",owner);t.putLong("End",end);t.putBoolean("Finished",finished);}
    }
}''',encoding='utf-8')
(java/'ApplianceTooltip.java').write_text('''package it.noctis.magic;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class ApplianceTooltip{
    @SubscribeEvent public static void tooltip(ItemTooltipEvent e){
        var stack=e.getItemStack();if(stack.hasTag()&&stack.getTag().contains(UpgradeAppliance.MARK)){
            int n=Math.max(0,Math.min(3,stack.getTag().getInt(UpgradeAppliance.MARK)));
            if(n>0)e.getToolTip().add(Component.literal("Lavaggio: "+new String[]{"","I","II","III"}[n]).withStyle(ChatFormatting.AQUA));
        }
    }
}''',encoding='utf-8')
# Detailed 3D models using the furniture material palette; active cycle has a turquoise display.
for n,washer in [('washing_machine',True),('dishwasher',False)]:
    base=[(1,0,1,15,16,15,'white'),(1,13,0,15,15,1,'steel'),(11,13,0,14,14,1,'dark'),(3,13,0,5,15,1,'dark'),(2,0,1,14,1,15,'dark')]
    if washer:
        # Octagonal front door, layered bezel and glass center.
        base += [(3,3,0,13,11,1,'steel'),(4,2,0,12,12,1,'steel'),(4,4,-.25,12,10,.25,'dark'),(5,3,-.25,11,11,.25,'dark'),(5,4,-.5,11,10,0,'blue'),(6,3,-.5,10,11,0,'blue'),(11,6,-1,13,8,0,'steel')]
    else:
        base += [(2,2,0,14,12,1,'steel'),(3,9,-1,13,10,0,'dark'),(3,2,-.25,13,3,0,'gray'),(3,11,-.25,13,12,0,'gray')]
    for lit in (False,True):
        boxes=base+[(7,13,-.25,10,14,0,'blue' if lit else 'dark')]
        if lit and washer:boxes += [(6,5,-.75,8,8,-.5,'light'),(8,7,-.75,10,9,-.5,'white')]
        name=n+('_active' if lit else '')
        textures={m:'noctismagic:block/furniture_'+m for m in ('white','steel','dark','gray','blue','light')};textures['particle']=textures['steel']
        elements=[{'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+m,'uv':[0,0,16,16]} for f in ('north','south','east','west','up','down')}} for x,y,z,X,Y,Z,m in boxes]
        dump(assets/'models/block'/f'{name}.json',{'textures':textures,'elements':elements,'display':{'gui':{'rotation':[30,225,0],'scale':[.75,.75,.75]},'ground':{'translation':[0,3,0],'scale':[.25,.25,.25]},'fixed':{'scale':[.5,.5,.5]}}})
    dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
    dump(assets/'blockstates'/f'{n}.json',{'variants':{f'facing={d},lit={lit}':{'model':'noctismagic:block/'+n+('_active' if lit=='true' else ''),'y':a} for d,a in [('north',0),('east',90),('south',180),('west',270)] for lit in ('false','true')}})
    dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
    dump(res/'data/noctismagic/recipes'/f'{n}.json',{'type':'minecraft:crafting_shaped','pattern':['IRI','IBI','IGI'],'key':{'I':{'item':'minecraft:iron_ingot'},'R':{'item':'minecraft:redstone'},'B':{'item':'minecraft:bucket'},'G':{'item':'minecraft:glass_pane' if washer else 'minecraft:blast_furnace'}},'result':{'item':'noctismagic:'+n}})
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['block.noctismagic.washing_machine']='Lavatrice incantatrice' if lang=='it_it' else 'Enchanted washing machine';d['block.noctismagic.dishwasher']='Lavastoviglie incantatrice' if lang=='it_it' else 'Enchanted dishwasher';dump(p,d)
print('Two functional appliances with timed persistent item upgrades, repair and enchantments installed')
