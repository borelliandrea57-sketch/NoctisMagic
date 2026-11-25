"""Kakyoin's supplied voice loop, local positional sound."""
from pathlib import Path
import sys,json,hashlib,subprocess
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
audio=Path(__file__).resolve().with_name('kakyoin_rero.opus')
assert hashlib.sha256(audio.read_bytes()).hexdigest()=='70db671d1f2a2d54747b1919dcf9cb768f7342cfc24159fe504e03725a238d43','Kakyoin audio integrity mismatch'
target=assets/'sounds/kakyoin_rero.ogg';target.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(audio),'-vn','-ac','1','-ar','44100','-c:a','libvorbis','-q:a','5',str(target)],check=True)
assert target.read_bytes().startswith(b'OggS')
p=assets/'sounds.json';s=json.loads(p.read_text(encoding='utf-8'))
s['kakyoin_rero']={'sounds':[{'name':'noctismagic:kakyoin_rero','stream':False,'attenuation_distance':16}]}
p.write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8')
(java/'KakyoinRero.java').write_text('''package it.noctis.magic;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegisterEvent;
import net.minecraftforge.registries.ForgeRegistries;
@Mod.EventBusSubscriber(modid=Noctis.ID,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class KakyoinRero{
 public static final ResourceLocation ID=new ResourceLocation(Noctis.ID,"kakyoin_rero");
 public static final SoundEvent SOUND=SoundEvent.createVariableRangeEvent(ID);
 @SubscribeEvent public static void register(RegisterEvent e){e.register(ForgeRegistries.Keys.SOUND_EVENTS,h->h.register(ID,SOUND));}
}''',encoding='utf-8')
(java/'KakyoinReroClient.java').write_text('''package it.noctis.magic;
import java.util.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class KakyoinReroClient{
 private static final Map<UUID,Voice> active=new HashMap<>();
 private static ClientLevel current;
 static class Voice extends AbstractTickableSoundInstance{
  final Kakyoin entity;
  int ticks;
  Voice(Kakyoin entity){
   super(KakyoinRero.SOUND,SoundSource.NEUTRAL,RandomSource.create());
   this.entity=entity;looping=true;delay=0;volume=.85f;pitch=1f;follow();
  }
  void follow(){x=entity.getX();y=entity.getEyeY();z=entity.getZ();}
  @Override public void tick(){ticks++;Minecraft mc=Minecraft.getInstance();if(entity.isRemoved()||!entity.isAlive()||mc.level!=entity.level()||mc.player==null||mc.player.distanceToSqr(entity)>324||entity.isSilent()){stop();return;}follow();}
 }
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
  if(event.phase!=TickEvent.Phase.END)return;
  Minecraft mc=Minecraft.getInstance();
  if(current!=mc.level||mc.player==null){
   for(Voice v:active.values())mc.getSoundManager().stop(v);
   active.clear();current=mc.level;
  }
  if(mc.level==null||mc.player==null||mc.isPaused())return;
  active.entrySet().removeIf(entry->{
   Voice v=entry.getValue();
   if(v.isStopped()||v.entity.isRemoved()||!v.entity.isAlive()||v.entity.isSilent()||mc.player.distanceToSqr(v.entity)>324){
    mc.getSoundManager().stop(v);return true;
   }
   if(v.ticks>10&&!mc.getSoundManager().isActive(v)&&mc.options.getSoundSourceVolume(SoundSource.NEUTRAL)>0){mc.getSoundManager().stop(v);return true;}
   return false;
  });
  if(mc.options.getSoundSourceVolume(SoundSource.NEUTRAL)<=0)return;
  for(Kakyoin e:mc.level.getEntitiesOfClass(Kakyoin.class,mc.player.getBoundingBox().inflate(16),m->m.isAlive()&&!m.isSilent()&&mc.player.distanceToSqr(m)<=256)){
   if(!active.containsKey(e.getUUID())){
    Voice v=new Voice(e);active.put(e.getUUID(),v);mc.getSoundManager().play(v);
   }
  }
 }
}''',encoding='utf-8')
print('Kakyoin original provided recording: checksum verified, Vorbis converted, single positional loop per living NPC.')
