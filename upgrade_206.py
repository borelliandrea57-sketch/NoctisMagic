"""Expressive Giorno and Bucciarati: distinct idle poses and animated facial atlases."""
from pathlib import Path
import math,sys
from PIL import Image
root=Path(sys.argv[1])
java=root/'src/main/java/it/noctis/magic'
assets=root/'src/main/resources/assets/noctismagic/textures/entity'
(java/'JojoExpressions.java').write_text('''package it.noctis.magic;
import it.noctis.magic.SculptedGuestsClient.Part;
final class JojoExpressions {
 private JojoExpressions(){}
 static int clock(JojoMob e){return Math.floorMod(e.tickCount+(e.getId()%97)*23,180);}
 static int pose(JojoMob e){return Math.floorMod((e.tickCount+(e.getId()%97)*23)/180,4);}
 static String face(JojoMob e){
  if(e.hurtTime>0||e.punchPose()>.03f)return "_resolve";
  if(Math.floorMod(e.tickCount+e.getId()%97*11,93)<4)return "_blink";
  if(e.getDeltaMovement().horizontalDistanceSqr()>.006)return "";
  int p=pose(e),t=clock(e);
  if(t<20||t>155)return "";
  return p==0?"_resolve":p==1?"_smirk":p==2?"_surprise":"";
 }
 static float mix(float a,float b,float t){return a+(b-a)*t;}
 static void apply(JojoMob e,boolean giorno,float amount,float age,Part body,Part head,Part[] arm,Part[] fore,Part[] leg,Part[] shin){
  body.rx=0;body.rz=0;head.rz=0;
  for(int i=0;i<2;i++){arm[i].ry=0;fore[i].ry=0;fore[i].rz=0;leg[i].rz=0;leg[i].ry=0;shin[i].rz=0;}
  if(amount>.10f||e.hurtTime>0||e.punchPose()>.03f||e.getDeltaMovement().horizontalDistanceSqr()>.006)return;
  float local=clock(e)+(age-e.tickCount);
  float t=Math.max(0,Math.min(1,Math.min((local-20)/18f,(155-local)/18f)));
  t=t*t*(3-2*t);
  int p=pose(e);
  // Torso tilt, head tilt, arm X/Z, elbow X/Z, leg X/Z and shin X.
  float[][] g={
   {-.06f,.12f,-.27f,-.13f, -.40f,.83f,-.72f,-1.12f, -.12f,-.15f,-.16f,0, -.17f,.08f,.18f,-.14f,.10f,.17f},
   {-.09f,-.12f,.28f,.15f, -.80f,.42f,-1.35f,-.90f, -.65f,-.55f,-1.04f,.68f, .15f,.14f,-.15f,-.12f,.15f,.10f},
   {.04f,.12f,.18f,-.11f, -1.30f,.30f,-.36f,-.26f, -.20f,-.76f,-.82f,.97f, -.18f,.13f,.20f,-.13f,.18f,.22f},
   {-.08f,-.13f,-.28f,.12f, -.25f,.78f,-.62f,-1.08f, -.90f,-.39f,-1.54f,.40f, .11f,.15f,-.20f,-.12f,.10f,.16f}
  };
  float[][] b={
   {-.04f,-.13f,.26f,.10f, -.12f,.82f,-.55f,-1.06f, -.15f,-.14f,-.22f,0, .17f,.12f,-.20f,-.12f,.12f,.16f},
   {-.09f,.10f,-.20f,-.12f, -.94f,.28f,-1.38f,-.42f, -.75f,-.67f,-1.13f,.72f, -.14f,.12f,.20f,-.16f,.12f,.23f},
   {.08f,-.15f,.30f,.15f, -.24f,.23f,-.32f,-.20f, -1.43f,-.70f,-.25f,.34f, .15f,.12f,-.24f,-.14f,.12f,.18f},
   {-.05f,.13f,-.32f,-.14f, -.72f,.85f,-1.12f,-1.17f, -.63f,-.49f,-1.30f,.89f, -.23f,.14f,.15f,-.12f,.18f,.13f}
  };
  float[] f=(giorno?g:b)[p];
  body.rx=f[0]*t;body.rz=f[1]*t;body.ry+=f[2]*t;head.rz=f[3]*t;head.ry-=f[2]*.55f*t;
  for(int i=0;i<2;i++){
   int j=4+i*4,k=12+i*2;
   arm[i].rx=mix(arm[i].rx,f[j],t);arm[i].rz=mix(arm[i].rz,f[j+1],t);
   fore[i].rx=mix(fore[i].rx,f[j+2],t);fore[i].rz=f[j+3]*t;
   leg[i].rx=mix(leg[i].rx,f[k],t);leg[i].rz=f[k+1]*t;
   shin[i].rx=mix(shin[i].rx,f[16+i],t);
  }
  if(giorno&&p==1){arm[0].ry=-.33f*t;arm[1].ry=.22f*t;}
  if(!giorno&&p==1){arm[0].ry=-.40f*t;arm[1].ry=.32f*t;}
 }
}''',encoding='utf-8')
for name in ('giorno','bucciarati'):
 p=java/('GiornoSculptedClient.java' if name=='giorno' else 'BucciaratiSculptedClient.java')
 s=p.read_text(encoding='utf-8')
 start=s.index('  @Override public void setupAnim(JojoMob')
 a=s.index('{',start)
 depth=1;b=a+1
 while depth:
  if s[b]=='{':depth+=1
  elif s[b]=='}':depth-=1
  b+=1
 body=s[a+1:b-1]
 # Remove the previous intermittent single pose but keep walking and hair/clothing motion.
 import re
 body,n=re.subn(r'float pose=amount<\.08f\?[^;]+;', 'float pose=0;',body,count=1)
 assert n==1,(name,'old pose')
 body+='\n   JojoExpressions.apply(e,'+('true' if name=='giorno' else 'false')+',amount,age,bodyPartPlaceholder,head,arm,fore,leg,shin);\n  '
 body=body.replace('bodyPartPlaceholder','body')
 s=s[:a+1]+body+s[b-1:]
 old='"textures/entity/'+name+'_sculpted.png"'
 new='"textures/entity/'+name+'_sculpted"+JojoExpressions.face(e)+".png"'
 assert old in s,name
 p.write_text(s.replace(old,new,1),encoding='utf-8')
# Build four high-resolution variants using each character's existing face UVs.
def blend(a,b,t):
 t=max(0,min(1,t));return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def gauss(x,y,cx,cy,sx,sy):return math.exp(-((x-cx)/sx)**2-((y-cy)/sy)**2)
for name in ('giorno','bucciarati'):
 path=assets/(name+'_sculpted.png')
 original=Image.open(path).convert('RGBA')
 giorno=name=='giorno'; eye_y=.474 if giorno else .485
 center=.175 if giorno else .161;ew=.132 if giorno else .103
 lip=.776 if giorno else .785
 X=5*128
 def pixel(u,v):
  return original.getpixel((X+max(0,min(127,round(u*121+3))),max(0,min(127,round(v*121+3)))))[:3]
 for style in ('','_resolve','_smirk','_surprise','_blink'):
  im=original.copy()
  for y in range(128):
   v=(y-3)/121
   for x in range(128):
    u=(x-3)/121
    c=original.getpixel((X+x,y))[:3]
    if style:
     for side in (-1,1):
      ex=.5+side*center;dx=(u-ex)/ew
      if abs(dx)>1.19 or not .315<v<.575:continue
      # Clear original eyes/brows by interpolating the surrounding facial color.
      edge=max(0,min(1,(1.19-abs(dx))*7))
      edge*=min(1,max(0,(v-.315)*85),max(0,(.575-v)*85))
      skin=blend(pixel(ex+side*ew*1.23,v),pixel(ex,.575),.40)
      c=blend(c,skin,edge)
      if abs(dx)>1.02:continue
      arch=math.sqrt(max(0,1-dx*dx))
      tilt=(.026 if style=='_resolve' else -.011 if style=='_smirk' else .0)
      cy=eye_y+side*dx*tilt
      eh=(.043 if style=='_resolve' else .071 if style=='_surprise' else .047)
      vv=v-cy
      if style=='_blink':
       if abs(v-(cy+.013*arch))<.010:c=(49,30,38)
      elif -eh*arch-.011<vv<eh*arch+.006:
       c=(43,29,36)
       if -eh*arch+.010<vv<eh*arch-.007:
        c=(247,239,223)
        iy=vv/max(.029,eh*.91)
        if (dx/.44)**2+iy*iy<1:
         c=blend((27,82,64) if giorno else (41,76,133),(117,193,146) if giorno else (119,173,224),.45+.40*iy)
         if (dx/.17)**2+(iy/.81)**2<1:c=(23,26,34)
         if ((dx+.13)/.12)**2+((iy+.37)/.16)**2<1:c=(255,251,239)
      brow=(.351 if giorno else .365)+(.022 if style=='_resolve' else -.019 if style=='_surprise' else .0)
      brow+=side*dx*(.028 if style=='_resolve' else .008)+.015*dx*dx
      if abs(dx)<.95 and abs(v-brow)<.014:c=(127,85,31) if giorno else (39,30,32)
     # Draw distinct mouth shapes without leaving the original lip line underneath.
     dx=(u-.5)/(.103 if giorno else .085)
     if abs(dx)<1.27 and .722<v<.831:
      edge=min(1,(1.27-abs(dx))*6,max(0,(v-.722)*70),max(0,(.831-v)*70))
      skin=blend(pixel(.5+.13,v),pixel(.5,.72),.28)
      c=blend(c,skin,edge)
      if abs(dx)<1:
       mid=lip+(.018*dx if style=='_smirk' else .014*dx*dx if style=='_resolve' else 0)
       half=(.024 if style=='_surprise' else .008)*math.sqrt(max(0,1-dx*dx))
       if abs(v-mid)<half+.003:c=(101,47,56)
       if style=='_surprise' and abs(v-mid)<half*.66:c=(65,30,41)
       if abs(v-mid-.014)<.009 and abs(dx)<.80:c=blend(c,(188,107,112),.68)
    # All variants, including the original: subtle shaded lower lip and manga chin plane.
    c=blend(c,(139,76,73),.42*gauss(u,v,.5,lip+.048,.065,.016))
    c=blend(c,(247,193,165),.35*gauss(u,v,.5,lip+.023,.064,.009))
    c=blend(c,(159,102,82),.13*gauss(u,v,.5,.91,.15,.052))
    im.putpixel((X+x,y),(*c,255))
  im.save(assets/(name+'_sculpted'+style+'.png'))
print('Giorno and Bucciarati: individual four-pose cycles, dynamic eyes and mouth, lower-lip shading; original abilities preserved.')
