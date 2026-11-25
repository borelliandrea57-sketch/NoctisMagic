"""Align player pelvis with the cartoon pony's barrel, not the head."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic'
p=java/'FriendshipPony.java';s=p.read_text(encoding='utf-8')
def remove_method(s,name):
 # Remove a pre-existing override if a prior upgrade added one.
 m=re.search(r'(?m)^[ \t]*(?:@Override\s+)?(?:public|protected)\s+[^\n{;]+\b'+name+r'\s*\([^;{}]*\)\s*\{',s)
 if not m:return s
 a=m.end();depth=1;b=a
 while depth:
  if s[b]=='{':depth+=1
  elif s[b]=='}':depth-=1
  b+=1
 return s[:m.start()]+s[b:]
for name in ('getPassengersRidingOffset','positionRider'):
 s=remove_method(s,name)
# Seat coordinates refer to the mesh in PonyCartoonClient: back at y=10.4 model units,
# which is about 0.85 blocks from the floor. Vanilla player riding model raises the pelvis.
a=s.rfind('}')
s=s[:a]+'''    @Override public double getPassengersRidingOffset(){
        return .50;
    }
    @Override protected void positionRider(net.minecraft.world.entity.Entity passenger,net.minecraft.world.entity.Entity.MoveFunction move){
        if(!hasPassenger(passenger))return;
        if(!(passenger instanceof net.minecraft.world.entity.player.Player)){super.positionRider(passenger,move);return;}
        double yaw=Math.toRadians(getYRot());
        double rear=.20;
        double y=getY()+getPassengersRidingOffset()+passenger.getMyRidingOffset();
        // Shared server/client transform, with a centered seat just behind the shoulders.
        move.accept(passenger,getX()+Math.sin(yaw)*rear,y,getZ()-Math.cos(yaw)*rear);
    }
'''+s[a:]
p.write_text(s,encoding='utf-8')
p=java/'PonyCartoonClient.java';s=p.read_text(encoding='utf-8')
old='boolean sit=e.isInSittingPose(),flight=e.winged()&&!e.onGround()&&!sit;'
assert old in s
s=s.replace(old,'boolean sit=e.isInSittingPose()&&!e.isVehicle(),flight=e.winged()&&!e.onGround()&&!sit;',1)
old='float bob=(float)Math.sin(limb*1.32f)*amount*.15f;'
assert old in s
s=s.replace(old,'float bob=(float)Math.sin(limb*1.32f)*amount*(e.isVehicle()?.055f:.15f);',1)
p.write_text(s,encoding='utf-8')
print('All six ponies: low centered rider seat, rearward offset, stable mounted gait and flight.')
