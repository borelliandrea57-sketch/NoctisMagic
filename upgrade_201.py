"""Jinshi: animated hand-held folding fan, independent from serving."""
from pathlib import Path
import sys
root=Path(sys.argv[1]);p=root/'src/main/java/it/noctis/magic/SushiGuestClient.java'
s=p.read_text(encoding='utf-8')
def replace(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b,1)
replace('final Part tray;','final Part tray,fan;')
replace('tray=arms[1].child(0,10.8f,-.7f);tray.rx=1.2f;', '''fan=arms[0].child(0,10.45f,-.8f);
            if(!mao){
                fan.blade(5,0,.9f,0,0,-1.3f,0,.42f);
                for(int i=0;i<14;i++){
                    double a=-1.22+i*2.44/14,b=-1.22+(i+1)*2.44/14;
                    float x=(float)Math.sin(a)*3.7f,y=-1.2f-(float)Math.cos(a)*3.7f;
                    float X=(float)Math.sin(b)*3.7f,Y=-1.2f-(float)Math.cos(b)*3.7f;
                    float z=(i%2==0?-.18f:.18f),Z=-z;
                    var center=new SculptedGuestsClient.V(0,-1.2f,0,.5f,1,0,0,-1);
                    var left=new SculptedGuestsClient.V(x,y,z,i/14f,0,0,0,-1);
                    var right=new SculptedGuestsClient.V(X,Y,Z,(i+1)/14f,0,0,0,-1);
                    fan.faces.add(new SculptedGuestsClient.Q(center,left,right,center, i%2==0?3:9));
                    var backCenter=new SculptedGuestsClient.V(0,-1.2f,.06f,.5f,1,0,0,1);
                    var backL=new SculptedGuestsClient.V(x,y,z+.06f,i/14f,0,0,0,1);
                    var backR=new SculptedGuestsClient.V(X,Y,Z+.06f,(i+1)/14f,0,0,0,1);
                    fan.faces.add(new SculptedGuestsClient.Q(backCenter,backR,backL,backCenter,i%2==0?3:9));
                    fan.blade(5,0,-1.2f,0,x,y,z-.08f,.13f);
                    fan.blade(5,x,y,z,X,Y,Z,.16f);
                }
            }
            tray=arms[1].child(0,10.8f,-.7f);tray.rx=1.2f;''')
replace('tray.rx=1.12f*a;', '''fan.rx=.20f;fan.ry=.25f;fan.rz=-.35f;
            if(!mao&&a<.04f&&amount<.10f){
                float time=(age+Math.floorMod(e.getId()*43,240))%240;
                if(time<58){
                    float t=Math.min(1f,Math.min(time,58-time)/8f);
                    arms[0].rx=-1.18f*t;arms[0].rz=.28f*t;
                    fan.rx=.45f+(float)Math.sin(age*.48f)*.27f*t;
                    fan.ry=.30f+(float)Math.sin(age*.48f)*.30f*t;
                    fan.rz=-.25f+(float)Math.sin(age*.48f)*.14f*t;
                    head.rz=.045f*t;
                }
            }
            if(a>=.04f){fan.rx=1.2f;fan.rz=-.65f;}
            tray.rx=1.12f*a;''')
p.write_text(s,encoding='utf-8')
print('Jinshi: folding fan with fourteen pleats and gold ribs; periodic wrist and arm animation while idle.')
