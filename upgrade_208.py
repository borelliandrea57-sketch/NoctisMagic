"""Material-specific model shading and texture microdetail, applied after all character scripts."""
from pathlib import Path
import sys,math
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
# Only known material tiles; leave projected faces, jewels and eyes untouched.
models=[
 ('GiornoSculptedClient.java',5,'giorno_sculpted',(6,7,9),(0,2,8)),
 ('BucciaratiSculptedClient.java',6,'bucciarati_sculpted',(7,),(0,1,8)),
 ('KakyoinClient.java',7,'kakyoin_cherry',(5,6,11,12),(0,1,13,14)),
 ('JohnnyClient.java',8,'johnny_wheelchair',(3,10),(0,1,9,14)),
 ('GeassSculptedClient.java',9,'lelouch_sculpted',(8,),(0,1,2,3,5))
]
for name,style,atlas,hair,cloth in models:
 p=java/name;s=p.read_text(encoding='utf-8')
 import re
 s,n=re.subn(r'root\.draw(?:Styled)?\(p,v,light,overlay,r,g,b,a(?:,\d+)?\)',f'root.drawStyled(p,v,light,overlay,r,g,b,a,{style})',s)
 assert n>0,name
 p.write_text(s,encoding='utf-8')
 for ap in assets.glob(atlas+'*.png'):
  im=Image.open(ap).convert('RGBA')
  if im.size!=(1024,512):continue
  for tile in hair+cloth:
   for y in range(128):
    for x in range(128):
     px=tile%8*128+x;py=tile//8*128+y
     R,G,B,A=im.getpixel((px,py))
     if A==0:continue
     u=x/127;v=y/127
     if tile in hair:
      strand=math.sin(u*math.pi*36+math.sin(v*4.1)*1.4)
      secondary=math.sin(u*math.pi*68+v*3.7)
      gleam=math.exp(-((v-.38-.12*math.sin(u*4))/.16)**2)
      gain=1+.055*strand+.022*secondary+.095*gleam*max(0,strand)
      bias=3.5*gleam*max(0,strand)
     else:
      weave=math.cos(x*math.pi/2)*math.cos(y*math.pi/2)
      fine=math.sin((x+y)*math.pi/3)
      fold=math.sin(u*19+v*5.5)
      gain=1+.025*weave+.016*fine+.035*fold
      bias=1.2*weave
     im.putpixel((px,py),tuple(max(0,min(255,round(c*gain+bias))) for c in (R,G,B))+(A,))
  im.save(ap)
print('Hair satin highlights and cloth fibre roughness on five sculpted character renderers.')
