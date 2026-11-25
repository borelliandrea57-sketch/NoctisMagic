"""1.7.11: reciprocal affectionate lift, facial expressions and smoother embrace timing."""
from pathlib import Path
import sys,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(s,a,b):
 assert a in s,a
 return s.replace(a,b,1)
p=java/'DramaGuest.java';s=p.read_text(encoding='utf-8')
s=edit(s,'int mode=random.nextBoolean()?1:2;','int mode=1+random.nextInt(3);')
s=edit(s,'affectionTime=q.affectionTime=72;','affectionTime=q.affectionTime=mode==3?108:88;')
s=edit(s,'(72-affectionTime)/12f','((affectionMode==3?108:88)-affectionTime)/16f')
s=edit(s,'affectionTime/12f','affectionTime/16f')
s=edit(s,'(byte)(95+mode)','(byte)(mode==3?99:95+mode)')
s=edit(s,'(byte)(95+mode)','(byte)(mode==3?99:95+mode)')
s=edit(s,'if(id==96||id==97){affectionMode=id-95;affectionTime=72;return;}','if(id==96||id==97||id==99){affectionMode=id==99?3:id-95;affectionTime=id==99?108:88;return;}')
s=edit(s,'1800+random.nextInt(2400)','1000+random.nextInt(1400)')
s=edit(s,'if(kind()==1&&affectionTime==46)','if(kind()==1&&(affectionTime==46||affectionMode==3&&affectionTime==78))')
s=edit(s,'public int affectionMode(){','public int affectionRemaining(){return affectionTime;}\n    public int affectionMode(){')
p.write_text(s,encoding='utf-8')
p=java/'GeassSculptedClient.java';s=p.read_text(encoding='utf-8')
s=edit(s,'body.rx=0;root.rx=0;root.ry=0;root.rz=0;head.z=0;','body.rx=0;root.rx=0;root.ry=0;root.rz=0;root.y=0;root.z=0;head.z=0;')
s=edit(s,'if(affectionMode==2){','''if(affectionMode==3){
                        // A playful lifted hug: she holds his shoulders, he supports her back.
                        root.y=cc?-4.1f*f:0;
                        root.rx=(cc?-.065f:.065f)*f;
                        head.rx=(cc?.13f:-.12f)*f;head.rz=(cc?-.17f:.09f)*f;
                        arms[i].rx=(cc?-1.93f:-1.11f)*f;
                        arms[i].rz=-side*(cc?.18f:.29f)*f;
                        arms[i].ry=-side*(cc?.25f:.35f)*f;
                        fore[i].rx=(cc?-.71f:-.82f)*f;
                        fore[i].rz=side*(cc?.44f:.43f)*f;
                        legs[i].rx=cc?(.24f+(i==0?.10f:0))*f:0;
                        knees[i].rx=cc?-(.85f+(i==0?.20f:0))*f:0;
                    }else if(affectionMode==2){''')
s=edit(s,'+(cc?"cc":"lelouch")+"_sculpted.png"','+(cc?"cc":"lelouch")+"_sculpted"+(e.affectionProgress()>.55f?(e.affectionRemaining()%38<9?"_happy":"_soft"):"")+".png"')
p.write_text(s,encoding='utf-8')
# Preserve all the existing clothing and hair material islands.
for name in ('cc','lelouch'):
 base=Image.open(assets/'textures/entity'/f'{name}_sculpted.png').convert('RGBA')
 for expr in ('soft','happy'):
  im=base.copy()
  for y in range(128):
   v=max(0,min(1,(y-3)/121))
   for x in range(128):
    u=max(0,min(1,(x-3)/121));f=abs(u-.5)
    c=im.getpixel((768+x,y))[:3]
    for side in (-1,1):
     ex=.5+side*.17;dx=side*(u-ex)/.139
     if .36<v<.565 and abs(dx)<1.16:
      # Remove normal eyes in this facial texture only; draw expressive curved lids.
      skin=(239,191,157);shade=.94-.11*abs(u-.5)
      c=tuple(int(q*shade) for q in skin)
      arc=.465-(.034 if expr=='happy' else .017)*(1-dx*dx)-.018*dx
      if abs(dx)<1.03 and abs(v-arc)<.013:c=(43,28,42)
     blush=math.exp(-((u-ex)/.095)**2-((v-.61)/.065)**2)*(.24 if name=='cc' else .13)
     c=tuple(int(a+(b-a)*blush) for a,b in zip(c,(221,113,119)))
    if .73<v<.84 and f<.14:
     c=(235,186,154)
     curve=.771+.030*(1-(f/.14)**2)
     if abs(v-curve)<.012:c=(122,54,66)
     if expr=='happy' and f<.085 and curve-.019<v<curve:c=(248,224,209)
    im.putpixel((768+x,y),(*c,255))
  im.save(assets/'textures/entity'/f'{name}_sculpted_{expr}.png')
print('Lelouch and C.C.: new synchronized lifted hug, closed-eye smiles, blush and existing kiss/embrace modes.')
