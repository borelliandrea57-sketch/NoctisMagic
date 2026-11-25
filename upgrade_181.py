"""1.7.14: Cinnabar-specific face and swept crystalline hair, no clipping fringe."""
from pathlib import Path
import sys,math,re
from PIL import Image
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'SculptedGuestsClient.java';s=p.read_text(encoding='utf-8')
a=s.index('if(gem){\n                    VoxelPortrait.head(head,face,17,')
s=s[:a]+'''if(k==3){
                    int first=head.faces.size();
                    // Beveled, sculpted face with a taller forehead, narrow cheekbones and a clean jaw.
                    head.loft(15,16,-7.55f,0,.20f,1.76f,1.68f,-7.08f,0,.13f,2.57f,2.34f,
                        -6.1f,0,.02f,2.85f,2.65f,-4.90f,0,-.05f,2.92f,2.68f,
                        -3.75f,0,-.07f,2.76f,2.61f,-2.60f,0,-.19f,2.42f,2.37f,
                        -1.48f,0,-.31f,1.87f,1.86f,-.52f,0,-.39f,1.12f,1.20f,0,0,-.42f,.74f,.80f);
                    for(int j=first;j<head.faces.size();j++){
                        Q q=head.faces.get(j);
                        boolean f=q.a().nz()+q.b().nz()+q.c().nz()+q.d().nz()<-.08f;
                        head.faces.set(j,new Q(cinnabarFace(q.a(),f),cinnabarFace(q.b(),f),cinnabarFace(q.c(),f),cinnabarFace(q.d(),f),f?15:17));
                    }
                    // A shallow sculpted nose and neck.
                    head.loft(17,8,-3.88f,0,-2.55f,.12f,.08f,-3.08f,0,-2.68f,.20f,.17f,-2.68f,0,-2.79f,.29f,.21f,-2.45f,0,-2.52f,.18f,.11f);
                    head.loft(17,8,-.45f,0,.10f,.80f,.80f,.50f,0,.10f,.96f,.92f,1.12f,0,.10f,1.10f,1.04f);
                }else '''+s[a:]
# Add the UV helper to the shared model; only Cinnabar invokes it.
a='        void build(){'
assert a in s
s=s.replace(a,'''        static V cinnabarFace(V v,boolean front){
            float u=front?Math.max(.025f,Math.min(.975f,.5f+v.x()/6.3f)):.025f;
            float y=Math.max(.025f,Math.min(.975f,(v.y()+7.55f)/7.55f));
            return new V(v.x(),v.y(),v.z(),u,y,v.nx(),v.ny(),v.nz());
        }
'''+a,1)
a=s.index('int h=k==0?3:k==2?12:13;')+len('int h=k==0?3:k==2?12:13;')
b=s.index('if(k==3)for(int i=0;i<4;i++)',a)
end=s.index('\n',b)
old=s[a:end]
s=s[:a]+'''
                if(k==3){
                    // Deep red crystalline crown, above the forehead and behind the temples.
                    head.loft(13,12,-9.03f,-.38f,.32f,.52f,.50f,-8.63f,-.20f,.25f,1.84f,1.60f,
                         -8.02f,0,.19f,2.86f,2.50f,-7.06f,0,.27f,3.26f,2.89f,-6.42f,0,.40f,3.28f,2.74f);
                    // A full rear curtain of separate faceted crystal locks.
                    for(int j=0;j<11;j++){
                        float x=(j-5)*.52f;float spread=(j-5)*.25f;
                        Part q=head.child(x,-7.5f,2.35f);hair.add(q);
                        float len=14.2f+2.2f*(float)Math.sin(j*Math.PI/10)+(j%3)*.45f;
                        q.loft(13,6,-.4f,0,.05f,.43f,.53f,1.5f,spread*.12f,.25f,.70f,.72f,
                           5.5f,spread*.46f,.75f,.62f,.53f,10.4f,spread*.85f,1.25f,.49f,.36f,len,spread*1.25f,1.5f,.035f,.045f);
                    }
                    // Swept fringe: tips terminate above the brows, front surfaces remain ahead of the skull.
                    for(int j=0;j<7;j++){
                        float x=-2.58f+j*.82f,drift=.48f+j*.10f;
                        Part q=head.child(x,-7.95f,-2.54f);
                        float len=1.17f+(j==0||j==6?.23f:.45f)+(j%3)*.12f;
                        q.loft(13,6,-.22f,0,.28f,.41f,.39f,.27f,drift*.21f,-.30f,.59f,.34f,
                             len*.63f,drift*.60f,-.55f,.37f,.20f,len,drift,-.56f,.035f,.045f);
                    }
                    // Long locks beside the cheeks, outside the facial volume and kept clear of the eyes.
                    for(int side:new int[]{-1,1})for(int j=0;j<4;j++){
                        float x=side*(3.04f+j*.23f);
                        Part q=head.child(x,-6.85f+j*.52f,-.20f+j*.50f);hair.add(q);
                        float len=(side<0?12.6f:10.8f)+j*.82f;
                        q.loft(13,6,-.35f,side*.14f,.10f,.40f,.60f,1.7f,side*.56f,-.03f,.56f,.56f,
                             5.4f,side*.90f,.03f,.51f,.44f,len*.76f,side*.71f,.26f,.34f,.31f,len,side*.39f,.53f,.035f,.045f);
                    }
                }else{
'''+old+'''
                }'''+s[end:]
# The original animation swings long strands into the face. Reduce only Cinnabar's motion.
s=s.replace('(k==3?amount*.12f:amount*.04f)','(k==3?amount*.025f:amount*.04f)',1)
p.write_text(s,encoding='utf-8')
# Paint the Cinnabar-specific tiles only; preserve Phosphophyllite and all other guests.
p=assets/'textures/entity/sculpted_guests.png';im=Image.open(p).convert('RGBA')
def mix(a,b,t):
 t=max(0,min(1,t));return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
for tile in (13,15):
 for y in range(128):
  v=(y-3)/121
  for x in range(128):
   u=(x-3)/121;f=abs(u-.5)
   def g(cx,cy,sx,sy):return math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2)
   if tile==13:
    # Dark ruby facets with long diagonal glints, not a white checker grid.
    angle=u*9+v*2.2
    facet=int(angle)%5
    c=mix((90,9,31),(213,35,64),.32+.12*facet+.15*math.sin(v*7)**2)
    c=mix(c,(250,92,111),.30*math.exp(-((angle%1-.13)/.12)**2))
    c=mix(c,(255,177,153),.52*math.exp(-((angle%1-.12)/.035)**2)*g(.52,.31,.40,.19))
    c=mix(c,(52,7,26),.27*math.exp(-((angle%1-.90)/.12)**2))
   else:
    c=mix((246,233,219),(159,118,127),.18*min(1,f*2.1)+.045*v)
    c=mix(c,(249,240,226),.28*g(.5,.42,.16,.30))
    for side in (-1,1):
     ex=.5+side*.182;dx=side*(u-ex)/.125
     ey=.484-.019*dx
     dy=(v-ey)/(.065 if side<0 else .069)
     d=abs(dx)**1.65+abs(dy)**1.65
     c=mix(c,(136,76,83),.14*g(ex,.49,.15,.09))
     if d<1.08:c=(66,31,42)
     if d<.86:c=(250,242,231)
     if d<.83 and abs(dx+.025)<.48:
      c=mix((101,19,43),(216,62,76),(dy+.7)/1.4)
      if abs(dx+.025)<.19:c=(42,22,34)
      if (dx+.19)**2+(dy+.30)**2<.048:c=(255,248,238)
     if abs(dx)<1.06 and abs(v-(ey-.051+.009*dx*dx))<.012:c=(92,39,51)
     # Subtle, melancholic brows rather than aggressive V-shaped marks.
     if abs(dx)<.95 and abs(v-(.380+.024*dx-.009*dx*dx))<.011:c=(129,34,57)
     c=mix(c,(208,132,130),.11*g(ex,.64,.09,.06))
    c=mix(c,(170,121,125),.25*g(.5,.666,.035,.016))
    mouth=.775+.012*(1-min(1,f/.085))
    if f<.084 and abs(v-mouth)<.007:c=(138,72,83)
    c=mix(c,(222,159,157),.23*g(.50,.795,.07,.013))
   im.putpixel((tile%8*128+x,tile//8*128+y),(*c,255))
im.save(p)
print('Cinnabar: isolated volumetric facial mesh, ruby hair with independent swept locks, reduced strand swing, melancholic eyes and expression.')
