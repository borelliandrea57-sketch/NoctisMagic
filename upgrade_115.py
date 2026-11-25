"""1.1.5: replace random Synchro dragon encounters with deterministic altar rituals."""
from pathlib import Path
import sys,re
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic'
p=java/'NightGuests.java';s=p.read_text(encoding='utf-8')
pattern=r'        if\(p\.getRandom\(\)\.nextInt\(48\)==0&&l\.getEntitiesOfClass\(SynchroDragon\.class,p\.getBoundingBox\(\)\.inflate\(96\)\)\.isEmpty\(\)\)\{\n.*?\n        \}\n'
s,n=re.subn(pattern,'',s,count=1,flags=re.S);assert n==1,'Synchro random encounter anchor';p.write_text(s,encoding='utf-8')
(java/'SynchroRitual.java').write_text('''package it.noctis.magic;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class SynchroRitual{
    static boolean rose(BlockState s){
        return s.is(Blocks.POPPY)||s.is(Blocks.ROSE_BUSH)||s.is(Blocks.WITHER_ROSE)||s.is(Blocks.POTTED_POPPY)||s.is(Blocks.POTTED_WITHER_ROSE);
    }
    @SubscribeEvent public static void altar(PlayerInteractEvent.RightClickBlock e){
        if(e.getHand()!=InteractionHand.MAIN_HAND||!e.getItemStack().isEmpty()||!(e.getEntity() instanceof ServerPlayer p)||!(e.getLevel() instanceof ServerLevel l))return;
        BlockPos center=e.getPos();if(!l.getBlockState(center).is(Blocks.DRAGON_EGG))return;
        if(!l.dimension().equals(Level.OVERWORLD))return;
        // Eight neighbors on the same horizontal plane as the egg.
        int roses=0,lights=0;
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
            if(dx==0&&dz==0)continue;
            BlockPos q=center.offset(dx,0,dz);BlockState s=l.getBlockState(q);
            if(rose(s))roses++;
            if(s.getLightEmission(l,q)>=10)lights++;
        }
        // Prevent vanilla egg teleport during deliberate ritual interactions.
        e.setCanceled(true);e.setCancellationResult(InteractionResult.SUCCESS);
        if(roses!=8&&lights!=8){p.sendSystemMessage(Component.literal("Rituale incompleto: circonda l'uovo con 8 rose (papaveri, roseti o rose del Wither), oppure 8 fonti di luce di livello 10 o superiore. Tutte alla stessa altezza dell'uovo. Rose "+roses+"/8, luci "+lights+"/8."));return;}
        boolean black=roses==8;
        String key=black?"NoctisRoseAltarUntil":"NoctisStardustAltarUntil";
        long now=l.getGameTime();var data=p.getPersistentData();
        if(data.getLong(key)>now){p.sendSystemMessage(Component.literal("Il rituale deve ricaricarsi: "+((data.getLong(key)-now+19)/20)+" secondi."));return;}
        if(!l.getEntitiesOfClass(SynchroDragon.class,new net.minecraft.world.phys.AABB(center).inflate(48),d->d.rose()==black&&d.isAlive()).isEmpty()){p.sendSystemMessage(Component.literal("Un drago di questo tipo e' gia nelle vicinanze."));return;}
        SynchroDragon dragon=(black?Noctis.BLACK_ROSE.get():Noctis.STARDUST.get()).create(l);
        if(dragon==null)return;
        BlockPos spawn=null;
        // Start above the altar, then try open spaces nearby. Never destroy blocks.
        for(int dy=3;dy<=7&&spawn==null;dy+=2){
            for(int radius=0;radius<=8&&spawn==null;radius+=4){
                for(int i=0;i<(radius==0?1:8);i++){
                    double a=i*Math.PI/4;BlockPos q=center.offset((int)Math.round(Math.cos(a)*radius),dy,(int)Math.round(Math.sin(a)*radius));
                    if(q.getY()+4>=l.getMaxBuildHeight()||!l.hasChunkAt(q)||!l.getWorldBorder().isWithinBounds(q))continue;
                    dragon.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5,p.getYRot()+180,0);
                    if(l.noCollision(dragon)){spawn=q;break;}
                }
            }
        }
        if(spawn==null){p.sendSystemMessage(Component.literal("Non c'e spazio per il drago. Libera l'area sopra l'altare."));return;}
        dragon.setPersistenceRequired();
        // The summoner receives an untamed dragon, so the normal taming items still matter.
        if(!l.addFreshEntity(dragon))return;
        data.putLong(key,now+6000);
        for(int i=0;i<48;i++){double a=i*Math.PI/24;double x=center.getX()+.5+Math.cos(a)*2,z=center.getZ()+.5+Math.sin(a)*2;
            l.sendParticles(black?ParticleTypes.CRIMSON_SPORE:ParticleTypes.END_ROD,x,center.getY()+.8,z,4,.1,.35,.1,.03);}
        l.sendParticles(black?ParticleTypes.CRIMSON_SPORE:ParticleTypes.END_ROD,dragon.getX(),dragon.getY()+1.7,dragon.getZ(),90,1.7,1.5,1.7,.08);
        l.playSound(null,center,black?SoundEvents.ENDER_DRAGON_GROWL:SoundEvents.BEACON_ACTIVATE,SoundSource.NEUTRAL,1.6f,black?.8f:1.2f);
        NpcDialogue.say(l,Component.literal(black?"Il Drago Rosa Nera emerge dal cerchio di rose!":"Il Drago Polvere di Stelle discende dal cerchio luminoso!").withStyle(black?net.minecraft.ChatFormatting.LIGHT_PURPLE:net.minecraft.ChatFormatting.AQUA));
        p.sendSystemMessage(Component.literal(black?"Offrigli rose del Wither per addomesticarlo.":"Offrigli frammenti di ametista per addomesticarlo."));
    }
}''',encoding='utf-8')
print('Synchro altars installed: eight roses or eight light sources, no random spawn')
