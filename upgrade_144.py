"""1.4.4: complete six-pony polygon redesign, exactly one eye pair per head."""
from pathlib import Path
import sys,math,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
(java/'PonyClient.java').unlink()
p=java/'SculptedGuestsClient.java';s=p.read_text(encoding='utf-8')
def edit(a,b):
    global s
    assert a in s,a
    s=s.replace(a,b,1)
a='e.registerEntityRenderer(Noctis.PINKIE_PIE.get(),c->new R<FriendshipPony>(c,4));'
edit(a,a+''.join(f'\n        e.registerEntityRenderer(Noctis.{n}.get(),c->new R<FriendshipPony>(c,{k}));' for k,n in enumerate(['TWILIGHT_SPARKLE','RAINBOW_DASH','FLUTTERSHY','RARITY','APPLEJACK'],5)))
edit('if(k==4)pony();else build();','if(k>=4)pony();else build();')
edit('            // Large interlocking curls, not narrow rectangular mane strips.','            if(k==4){\n            // Large interlocking curls, not narrow rectangular mane strips.')
edit('            for(int i=0;i<4;i++){int side=i/2==0?-1:1;', '''            }else{
                Part mane=head.child(0,-4.8f,0);hair.add(mane);
                if(k==5){ // Twilight: smooth straight fringe and purple/pink streaks
                    mane.loft(24,20,-2.6f,0,0,1.3f,1.5f,-2,0,0,2.8f,2.8f,0,0,.1f,3.7f,3.2f,1.7f,0,.7f,3.4f,2.7f);
                    for(int j=0;j<4;j++){float x=-2.5f+j*1.55f;int m=j==2?26:j==3?27:24;
                        mane.loft(m,12,-.8f,x,-2,1,.85f,.7f,x,-2.8f,1,.65f,2.1f,x+.18f,-2.8f,.9f,.42f);}
                    mane.loft(24,18,0,0,2,3,1.75f,4,0,3.1f,3.2f,1.7f,8,0,4.4f,2.7f,1.2f,10,0,4.6f,2.2f,.65f);
                    mane.blade(26,1,-.4f,3.6f,1.2f,9.7f,5.1f,1.3f);
                }else if(k==6){ // Rainbow: swept rainbow locks
                    for(int j=0;j<6;j++){float x=-2.8f+j*1.12f;
                        mane.loft(26+j,12,-2.8f,x,-.9f,.2f,.3f,-1.2f,x,-.4f,1.3f,2.4f,.6f,x,.4f,1.2f,2.9f,3.5f,x,3.3f,.85f,1.8f,7.0f,x,5.4f,.07f,.12f);}
                    for(int j=0;j<3;j++)mane.blade(26+j,-3+j*1.6f,-.6f,-2.7f,-1.8f+j*1.8f,2.4f,-3.3f,2);
                }else if(k==7){ // Fluttershy: long soft pink sweep to the side
                    mane.oval(24,0,-.9f,0,3.5f,2.2f,3.2f);
                    mane.loft(24,18,-1.2f,-2.4f,-.9f,1.7f,1.8f,1.5f,-3.1f,-1.4f,1.5f,1.8f,5,-3.7f,-.35f,1.65f,2.2f,9,-3.3f,1.6f,1.8f,2.1f,12,-2.0f,3.7f,.12f,.15f);
                    mane.loft(24,18,0,2,2,2,2,4,2.5f,2.5f,2,2,8,1.7f,4,1.65f,1.75f,11,.4f,5.5f,.1f,.1f);
                }else if(k==8){ // Rarity: sculpted violet curls
                    mane.oval(24,-.9f,-1.3f,-.15f,3.6f,2.5f,3.1f);
                    mane.oval(24,2.8f,.5f,-.4f,1.85f,2.9f,2.25f);
                    mane.loft(24,20,-.4f,2.9f,1.7f,1.6f,1.7f,3,3.2f,2.1f,1.65f,1.8f,7,2.6f,2.5f,1.9f,2.1f,9,1.25f,3.1f,1.9f,2,10.2f,.7f,2.3f,.15f,.15f);
                    mane.oval(24,1,7.6f,2.8f,2.4f,2.1f,2.4f);
                    mane.blade(26,-2.7f,-1.3f,-2.2f,1.4f,1.25f,-3.0f,1.3f);
                }else{ // Applejack: swept blonde forelock and tied mane
                    mane.oval(24,0,-.9f,.3f,3.4f,1.8f,3);
                    mane.loft(24,16,-.4f,-1.1f,-1.8f,2.6f,1.4f,1.1f,-1.8f,-2.1f,2.1f,1.5f,2.8f,-2.7f,-1.7f,.2f,.3f);
                    mane.loft(24,16,0,0,2,2.4f,1.8f,4,0,3,2.2f,1.9f,7,0,4,1.25f,1.2f,10,0,5,1.4f,1.15f,11,0,5.4f,.2f,.25f);
                    mane.oval(27,0,7.5f,4.2f,1.34f,.4f,1.25f);
                    Part hat=head.child(0,-6.7f,.1f);hat.rz=.08f;
                    hat.loft(28,28,-.45f,0,0,5.3f,4.2f,0,0,0,5.45f,4.35f,.38f,0,0,5.0f,4.0f);
                    hat.loft(28,20,-3.25f,0,.15f,2.6f,2.65f,-2.75f,0,.15f,3.0f,3.0f,-.2f,0,0,3.2f,3.2f);
                    hat.loft(29,24,-1.1f,0,0,3.17f,3.18f,-.35f,0,0,3.3f,3.28f);
                }
                if(k==5||k==8){
                    Part horn=head.child(0,-5.5f,-2.2f);horn.rx=-.28f;
                    horn.loft(20,16,-4.1f,0,0,.03f,.03f,-3.1f,0,0,.32f,.32f,-1.8f,0,0,.56f,.56f,0,0,0,.85f,.85f);
                }
                if(k<=7)for(int i=0;i<2;i++){
                    int side=i==0?-1:1;Part wing=wings[i]=body.child(side*3.4f,-2.4f,-.4f);
                    wing.oval(20,side*1.4f,0,0,2.3f,1.3f,2.7f);
                    for(int j=0;j<7;j++){
                        float t=j/6f;wing.blade(20,side*(.8f+2.1f*t),-.8f+t, -1.5f+3.9f*t,side*(8.4f-3*t),-3.6f+8.0f*t,1.0f+5*t,2.15f);
                    }
                }
            }
            for(int i=0;i<4;i++){int side=i/2==0?-1:1;''')
edit('            ponyTail.oval(24,0,-1,2,2.3f,2.6f,3.0f);','            if(k==4){ponyTail.oval(24,0,-1,2,2.3f,2.6f,3.0f);')
edit('            // Two flank marks; separate oval patches, one on each side.','''            }else if(k==6){
                for(int j=0;j<6;j++)ponyTail.loft(26+j,10,-2,(j-2.5f)*.65f,0,.45f,.5f,0,(j-2.5f)*.8f,3.1f,.9f,1.5f,4,(j-2.5f)*.8f,6.8f,.75f,1.4f,8,(j-2.5f)*.7f,8.4f,.05f,.09f);
            }else{
                ponyTail.loft(24,20,-2,0,0,1,1.3f,-.2f,0,3.5f,2.1f,2.2f,3,0,5.4f,2.3f,2.2f,6,0,6.4f,k==9?1.1f:2.0f,1.4f,9,0,7.6f,1.5f,1.2f,10.8f,0,8.2f,.08f,.13f);
                if(k==5)ponyTail.blade(26,.55f,-.4f,4.7f,.65f,9.6f,8.5f,1.15f);
                if(k==8)ponyTail.oval(24,-.4f,5.5f,6,2.4f,2.4f,2.1f);
                if(k==9)ponyTail.oval(27,0,6.3f,6.6f,1.28f,.43f,1.55f);
            }
            // Two flank marks; separate oval patches, one on each side.''')
edit('if(k==4){head.ry=yaw*.012f;','if(k>=4){head.ry=yaw*.012f;')
edit('for(int i=0;i<4;i++)ponyLegs[i].rx=sit?(i%2==0?-.6f:1): (float)Math.cos(limb*.66+(i/2+i%2)*Math.PI)*amount*.65f;', '''boolean flight=e instanceof FriendshipPony fp&&fp.winged()&&!fp.onGround()&&!sit;
                for(int i=0;i<4;i++)ponyLegs[i].rx=sit?(i%2==0?-.6f:1):flight?.35f:(float)Math.cos(limb*.66+(i/2+i%2)*Math.PI)*amount*.65f;
                for(int i=0;i<2;i++)if(wings[i]!=null){int sign=i==0?-1:1;wings[i].rz=sign*(flight?(float)Math.sin(age*.35)*.75f:.95f);wings[i].ry=sign*(flight?.05f:.8f);}''')
edit('k==4?.48f','k>=4?.48f')
edit('return new ResourceLocation(Noctis.ID,"textures/entity/sculpted_guests.png");','return new ResourceLocation(Noctis.ID,k>=4?"textures/entity/sculpted_pony_"+k+".png":"textures/entity/sculpted_guests.png");')
p.write_text(s,encoding='utf-8')
# Read the shared atlas generated by 143 (filter zero PNG). All six use the exact same face layout.
raw=(assets/'textures/entity/sculpted_guests.png').read_bytes();i=8;data=b''
while i<len(raw):
    size=struct.unpack('>I',raw[i:i+4])[0];t=raw[i+4:i+8]
    if t==b'IDAT':data+=raw[i+8:i+8+size]
    i+=size+12
W,H=1024,512;decoded=zlib.decompress(data);stride=W*4
assert len(decoded)==H*(stride+1)
original=b''.join(decoded[y*(stride+1)+1:(y+1)*(stride+1)] for y in range(H))
def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
def clamp(x):return max(0,min(1,x))
def blend(a,b,t):return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
specs=[
 ((244,143,186),(223,42,129),(55,157,218)),
 ((167,124,203),(47,41,91),(114,57,159)),
 ((108,193,235),(239,66,65),(191,56,133)),
 ((250,231,151),(242,159,191),(52,155,157)),
 ((244,242,249),(89,46,145),(50,113,210)),
 ((241,164,78),(246,216,107),(61,151,74))]
rainbow=[(232,55,61),(250,139,52),(250,218,56),(65,183,93),(64,124,231),(151,75,194)]
for k,(body,mane,eye) in enumerate(specs,4):
    pix=bytearray(original)
    for m in range(20,32):
        for y in range(128):
            v=clamp((y-3)/121)
            for x in range(128):
                u=clamp((x-3)/121);front=abs(u-.5)
                c=body
                if m in (20,21,22,25):
                    c=blend(body,(255,255,255),.10*(1-v));c=blend(c,(56,39,61),.09*v)
                    if m==21:
                        for ex in (.33,.67):
                            dx=(u-ex)/.090;dy=(v-.48)/.255;d=dx*dx+dy*dy
                            if d<1:c=(52,31,65)
                            if d<.92:c=(255,252,249)
                            if ((dx-(.17 if ex<.5 else -.17))/.60)**2+(dy/.86)**2<1 and d<.9:c=eye
                            if ((dx-(.17 if ex<.5 else -.17))/.33)**2+(dy/.71)**2<1 and d<.85:c=(22,25,40)
                            if (dx+.13)**2+(dy+.30)**2<.095 or (dx-.24)**2+(dy-.27)**2<.027:c=(255,255,255)
                            # Fine lashes, only above the existing pair.
                            if k!=9 and -.30<dx<.75 and abs(dy+1.04+.35*dx)<.055:c=(52,31,65)
                        if k==9 and .46<v<.72:
                            for ex in (.44,.46,.48,.52,.54,.56):
                                if ((u-ex)/.007)**2+((v-(.59+.035*math.cos(ex*55)))/.012)**2<1:c=(166,90,48)
                    if m==22:
                        if front<.13 and abs(v-.70-.06*math.cos(front*16))<.024:c=blend(body,(79,36,66),.65)
                        if any(((u-ex)/.022)**2+((v-.4)/.035)**2<1 for ex in (.40,.60)):c=blend(body,(86,45,67),.55)
                    if m==25:
                        # Symbols appear on the two flank patches only.
                        a=(u-.5)*2;b=(v-.5)*2
                        if k==5:
                            if abs(a)<.12 and abs(b)<.6 or abs(b)<.11 and abs(a)<.46 or abs(abs(a)-abs(b))<.10 and abs(a)<.34:c=(220,61,157)
                            if (a+.49)**2+(b+.38)**2<.025 or (a-.49)**2+(b-.38)**2<.025:c=(255,252,243)
                        elif k==6:
                            if abs(a)<.54 and -.55<b<-.12 and (a*a+(b+.28)**2<.29):c=(248,248,248)
                            if -.15<b<.63 and abs(a+.38*b)<.20:c=(229,57,55) if b<.12 else (244,204,61) if b<.37 else (65,140,230)
                        elif k==8:
                            for ax,by in ((-.34,-.29),(.34,-.29),(0,.32)):
                                if abs(a-ax)+abs(b-by)*.65<.26:c=(86,170,231)
                        elif k==9:
                            for ax,by in ((-.34,-.29),(.34,-.29),(0,.32)):
                                if (a-ax)**2+(b-by)**2<.055:c=(211,42,43)
                                if abs(a-ax)<.075 and -.30<b-by<-.17:c=(69,126,54)
                        elif k==7:
                            for ax,by in ((-.32,-.29),(.32,-.29),(0,.31)):
                                if ((a-ax-.09)/.11)**2+((b-by)/.19)**2<1 or ((a-ax+.09)/.11)**2+((b-by)/.19)**2<1:c=(232,106,163)
                                if abs(a-ax)<.035 and abs(b-by)<.2:c=(95,174,192)
                        else:
                            for ex,ey,col in ((.37,.31,(94,187,236)),(.63,.31,(94,187,236)),(.5,.58,(255,220,65))):
                                if ((u-ex)/.087)**2+((v-ey)/.13)**2<1:c=col
                                if abs(u-ex-.025*math.sin(v*14))<.007 and ey+.10<v<ey+.30:c=(113,75,143)
                elif m==23:c=blend(body,(166,61,96),.32)
                else:
                    base=mane
                    if k==6 and m>=26:base=rainbow[m-26]
                    elif k==5 and m==26:base=(222,70,156)
                    elif k==5 and m==27:base=(137,66,183)
                    elif k==8 and m==26:base=(141,81,193)
                    elif k==9 and m==27:base=(180,43,42)
                    elif k==9 and m==28:base=(142,88,47)
                    elif k==9 and m==29:base=(97,58,33)
                    c=blend(base,(255,255,255),.15*math.sin(u*math.pi*3+v*1.4)**2)
                    c=blend(c,(40,28,43),.14*(1-math.sin(u*math.pi)**2))
                off=(((m//8)*128+y)*W+(m%8)*128+x)*4
                pix[off:off+4]=bytes((*c,255))
    out=b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*stride:(y+1)*stride] for y in range(H))))+ch(b'IEND',b'')
    (assets/'textures/entity'/f'sculpted_pony_{k}.png').write_bytes(out)
print('All six ponies now use continuous polygon heads with exactly two painted eyes, individual manes, tails, horns, wings and marks')
