"""1.4.2: Bayonetta prioritizes Ophanim and uses unique angel-hunting dialogue."""
from pathlib import Path
import sys
java=Path(sys.argv[1])/'src/main/java/it/noctis/magic'
p=java/'MoonGuest.java';s=p.read_text(encoding='utf-8')
def edit(a,b):
    global s
    assert a in s,a
    s=s.replace(a,b,1)
edit('UUID owner,aggressor;','UUID owner,aggressor,lastAngel;int angelSpeech;')
edit('if(speech>0)speech--;','if(speech>0)speech--;if(angelSpeech>0)angelSpeech--;')
edit('boolean enemy(LivingEntity t){return t!=null&&t.isAlive()&&(kind()==0?Eclipse.hostile(t):','boolean angel(LivingEntity t){return t instanceof Angel;}\n    boolean enemy(LivingEntity t){return t!=null&&t.isAlive()&&(kind()==0?(angel(t)||Eclipse.hostile(t)):')
edit('if(tickCount%10==0){var area=p==null?getBoundingBox():p.getBoundingBox();setTarget(l.getEntitiesOfClass(LivingEntity.class,area.inflate(24),e->e!=this&&enemy(e)).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null));}', '''if(tickCount%10==0){
                var area=p==null?getBoundingBox():p.getBoundingBox();
                LivingEntity old=getTarget();
                LivingEntity next=l.getEntitiesOfClass(Angel.class,getBoundingBox().inflate(32),e->e.isAlive()&&distanceToSqr(e)<=32*32).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
                if(next==null)next=l.getEntitiesOfClass(LivingEntity.class,area.inflate(24),e->e!=this&&enemy(e)).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);
                if(next!=old){getNavigation().stop();setTarget(next);}
                if(angel(next)&&!next.getUUID().equals(lastAngel)&&angelSpeech==0){
                    lastAngel=next.getUUID();angelSpeech=160;
                    String[] lines={"Oh, un angelo. Finalmente qualcuno che vale una pallottola, tesoro.","Che delizia... un altro messaggero del Paradiso da rispedire al mittente.","Mi dispiace, piume d'oro. Oggi il Paradiso resta chiuso."};
                    say(l,lines[random.nextInt(lines.length)]);l.broadcastEntityEvent(this,(byte)118);
                }
                if(angel(next)&&(!hasLineOfSight(next)||distanceTo(next)>30)){
                    getNavigation().moveTo(next.getX(),getY(),next.getZ(),1.15);
                }
                if(!angel(next))lastAngel=null;
            }''')
edit('if(enemy(t)&&distanceTo(t)<22&&hasLineOfSight(t)&&cd==0){','if(enemy(t)&&distanceTo(t)<(angel(t)?32:22)&&hasLineOfSight(t)&&cd==0){')
edit('cd=24;l.broadcastEntityEvent(this,(byte)119);','cd=angel(t)?16:24;l.broadcastEntityEvent(this,(byte)119);')
edit('t.hurt(damageSources().mobAttack(this),34);','t.hurt(damageSources().mobAttack(this),angel(t)?52:34);')
edit('say(l,"Witch Time!");','say(l,angel(t)?"Witch Time! Il Paradiso puo aspettare.":"Witch Time!");')
p.write_text(s,encoding='utf-8')
print('Bayonetta: Ophanim priority, special dialogue, enhanced anti-angel ranged attacks')
