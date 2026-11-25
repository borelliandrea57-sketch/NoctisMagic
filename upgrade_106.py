"""1.0.6: talking vanilla horses, Italian voice clips and contextual dialogue."""
from pathlib import Path
import sys,json,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
groups=[
    ["Ue', finalmente qualcuno con cui parlare!", "Hai una carota? Ho una fame da cavallo!", "Non guardarmi cosi', pure io tengo un'opinione.", "Oggi non lavoro, sciopero degli zoccoli.", "Mi chiamo Cavallo. Piacere, umano."],
    ["Ehi, piano con quelle redini!", "Ma dove stiamo andando?", "Allaccia la cintura, si parte!", "Io corro, tu ti prendi tutti i meriti!", "Hai visto che motore? Altro che macchina!"],
    ["Finalmente si mangia!", "Grazie, compare!", "Questa si' che e' roba buona!", "Ne hai un'altra?"],
    ["Ahi! Ma che ti ho fatto?", "Oh, rispetto per gli equini!", "Mi sa che ti lascio a piedi!"],
    ["Che bella giornata per una passeggiata!", "Umano, tutto a posto?", "Meno male che qua nessuno mi chiede quanto vale la mia auto."]
]
flat=[x for group in groups for x in group]
p=java/'FallenEncounter.java';s=p.read_text(encoding='utf-8')
a='static final RegistryObject<SoundEvent> THEME='
assert a in s
s=s.replace(a,'''static final java.util.List<RegistryObject<SoundEvent>> HORSE_VOICES=registerHorseVoices();
    static java.util.List<RegistryObject<SoundEvent>> registerHorseVoices(){
        java.util.List<RegistryObject<SoundEvent>> result=new java.util.ArrayList<>();
        for(int i=0;i<'''+str(len(flat))+''';i++){String id="horse_voice_"+i;result.add(SOUNDS.register(id,()->SoundEvent.createVariableRangeEvent(new ResourceLocation(Noctis.ID,id))));}
        return java.util.List.copyOf(result);
    }
    '''+a,1);p.write_text(s,encoding='utf-8')
arrays=',\n        '.join('{'+','.join(json.dumps(x,ensure_ascii=False) for x in g)+'}' for g in groups)
(java/'TalkingHorses.java').write_text('''package it.noctis.magic;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.animal.horse.Horse;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class TalkingHorses{
    private static final String[][] LINES={
        '''+arrays+'''
    };
    static boolean food(ItemStack s){
        return s.is(Items.WHEAT)||s.is(Items.SUGAR)||s.is(Items.HAY_BLOCK)||s.is(Items.APPLE)||s.is(Items.GOLDEN_CARROT)||s.is(Items.GOLDEN_APPLE)||s.is(Items.ENCHANTED_GOLDEN_APPLE);
    }
    static void speak(Horse h,ServerPlayer p,int group,int delay){
        if(!(h.level() instanceof ServerLevel l)||!h.isAlive()||p.isSpectator())return;
        var data=h.getPersistentData();long now=l.getGameTime();
        if(data.getLong("NoctisHorseVoiceUntil")>now)return;
        if(p.getPersistentData().getLong("NoctisHorseChatUntil")>now)return;
        data.putLong("NoctisHorseVoiceUntil",now+delay);
        p.getPersistentData().putLong("NoctisHorseChatUntil",now+100);
        int n=h.getRandom().nextInt(LINES[group].length),id=n;
        for(int i=0;i<group;i++)id+=LINES[i].length;
        p.sendSystemMessage(Component.literal(h.getDisplayName().getString()+": "+LINES[group][n]));
        float pitch=.90f+(Math.floorMod(h.getUUID().hashCode(),21)/100f);
        h.playSound(FallenEncounter.HORSE_VOICES.get(id).get(),.85f,pitch);
    }
    @SubscribeEvent public static void interact(PlayerInteractEvent.EntityInteract e){
        if(e.getHand()!=InteractionHand.MAIN_HAND||!(e.getEntity() instanceof ServerPlayer p)||!(e.getTarget() instanceof Horse h))return;
        if(food(e.getItemStack()))speak(h,p,2,140);
        else if(e.getItemStack().isEmpty())speak(h,p,0,140);
    }
    @SubscribeEvent public static void riding(LivingEvent.LivingTickEvent e){
        if(!(e.getEntity() instanceof Horse h)||!(h.level() instanceof ServerLevel l)||h.tickCount%200!=0)return;
        if(h.getControllingPassenger() instanceof ServerPlayer p){
            if(h.getRandom().nextInt(3)==0)speak(h,p,1,600);
        }else if(h.getRandom().nextInt(12)==0&&l.getNearestPlayer(h,5) instanceof ServerPlayer p&&h.hasLineOfSight(p)){
            speak(h,p,4,1200);
        }
    }
    @SubscribeEvent public static void hurt(LivingHurtEvent e){
        if(e.getEntity() instanceof Horse h&&e.getSource().getEntity() instanceof ServerPlayer p)speak(h,p,3,140);
    }
}''',encoding='utf-8')
sounds=assets/'sounds';sounds.mkdir(parents=True,exist_ok=True)
p=assets/'sounds.json';d=json.loads(p.read_text(encoding='utf-8'))
for i,line in enumerate(flat):
    name=f'horse_voice_{i}';wav=sounds/(name+'.wav')
    subprocess.run(['espeak-ng','-v','it','-s','150','-p',str(39+i%5*2),'-a','120','-w',str(wav),line],check=True)
    subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','4',str(sounds/(name+'.ogg'))],check=True)
    wav.unlink()
    d[name]={"sounds":[{"name":"noctismagic:"+name}]}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 1.0.6: 20 contextual Italian horse dialogues with voice audio')
