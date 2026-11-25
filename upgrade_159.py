"""1.5.9: natural, restrained face art for Maomao and Jinshi; clean eye silhouettes."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic/textures/entity'
p=java/'SushiGuestClient.java';s=p.read_text(encoding='utf-8')
def edit(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b,1)
# Shorter, thinner fringe: keep the eyebrows and upper eyelids unobstructed.
edit('2.5f+(i%2)*.3f,(i-3)*.14f,-.27f,.04f,.07f','1.95f+(i%2)*.18f,(i-3)*.14f,-.18f,.045f,.065f')
edit('float x=-2.8f+i*1.4f;','float x=-2.85f+i*1.40f;')
edit('2.0f,(i<2?-1:1)*.45f,-.9f,.85f,.42f,3.65f,(i<2?-1:1)*.82f,-.42f,.10f,.10f','1.65f,(i<2?-1:1)*.63f,-.64f,.70f,.34f,2.45f+(i==0||i==4?.65f:0),(i<2?-1:1)*1.0f,-.25f,.045f,.065f')
# Subtle nose, not a protruding ball, and denser surface to avoid faceted cheeks.
edit('head.loft(6,32,','head.loft(6,64,')
edit('head.oval(7,0,-2.7f,-2.70f,.34f,.46f,.37f);','head.oval(7,0,-2.65f,-2.63f,.25f,.37f,.25f);')
p.write_text(s,encoding='utf-8')
W,H=1024,512
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
def read_png(p):
 raw=p.read_bytes();i=8;compressed=b''
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8];data=raw[i+8:i+8+n];i+=12+n
  if kind==b'IHDR':assert struct.unpack('>IIBBBBB',data)==(W,H,8,6,0,0,0)
  if kind==b'IDAT':compressed+=data
 rows=zlib.decompress(compressed);stride=W*4+1
 assert len(rows)==H*stride and all(rows[y*stride]==0 for y in range(H))
 return bytearray(b''.join(rows[y*stride+1:(y+1)*stride] for y in range(H)))
def face(u,v,mao):
 base=(241,205,177) if mao else (245,209,185)
 f=abs(u-.5)
 # Low contrast blush and warm shaded sides, no procedural high-frequency skin detail.
 c=blend(base,(184,130,122),.10*math.exp(-((v-.69)/.15)**2)+.20*clamp((f-.14)*3))
 c=blend(c,(234,159,151),.11*math.exp(-((f-.094)/.045)**2-((v-.67)/.10)**2))
 # Narrower and calmer eye outlines. Upper eyelid has a gentle arch and a single highlight.
 for side in (-1,1):
  ex=.5+side*.078
  dx=(u-ex)/(.051 if mao else .056)
  vv=v-(.506 if mao else .515)+side*dx*.012
  if abs(dx)<1.05:
   arch=math.sqrt(max(0,1-min(1,abs(dx))**1.8))
   top=-(.070 if mao else .049)*arch
   bot=(.064 if mao else .042)*arch
   if top-.009<vv<bot+.005:
    c=(65,47,54)
    if top+.009<vv<bot-.005 and abs(dx)<.96:
     c=(248,239,226)
     # Solid circular iris in projected eye space. Keep it centered vertically.
     ix=dx/.54;iy=(vv+.004)/(.063 if mao else .047)
     if ix*ix+iy*iy<1:
      c=blend((93,73,133) if mao else (125,65,106),(136,137,168) if mao else (174,104,139),clamp((iy+.2)*.65))
      if (dx/.24)**2+((vv+.005)/(.048 if mao else .036))**2<1:c=(44,34,53)
      if ((dx+.15)/.13)**2+((vv+.023)/.012)**2<1:c=(250,246,237)
   # One thin, restrained eyebrow, with no additional lash or shine marks.
   brow=(.401 if mao else .414)-.017*(1-dx*dx)+side*dx*.012
   if abs(dx)<.92 and abs(v-brow)<.009:c=(54,74,65) if mao else (79,44,62)
 # Tiny mouth, neutral for Maomao, lightly curved for Jinshi.
 if f<(.028 if mao else .033) and abs(v-(.790+(.002 if mao else -.006)*(f/.033)**2))<.008:
  c=(143,86,85)
 if mao:
  for x,y in ((.451,.645),(.469,.66),(.481,.639),(.519,.641),(.534,.66),(.55,.646)):
   if ((u-x)/.0038)**2+((v-y)/.0055)**2<1:c=blend(c,(146,91,70),.66)
 return c
for mao in (True,False):
 p=assets/(('maomao' if mao else 'jinshi')+'_sculpted.png')
 pix=read_png(p)
 # Supersample face tile to avoid harsh stair-step outlines at ordinary in-game distances.
 for y in range(128):
  for x in range(128):
   samples=[face(clamp((x+dx-3)/121),clamp((y+dy-3)/121),mao) for dx in (.25,.75) for dy in (.25,.75)]
   c=tuple(round(sum(t[k] for t in samples)/4) for k in range(3))
   off=(y*W+6*128+x)*4;pix[off:off+4]=bytes((*c,255))
 p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(H))))+ch(b'IEND',b''))
print('Maomao/Jinshi: reduced eye size, restrained iris highlights, clean face texture and shorter fringe')
