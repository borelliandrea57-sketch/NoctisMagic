"""1.7.35: improved mesh normals and material-aware cinematic entity lighting."""
from pathlib import Path
import sys
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic'
p=java/'SculptedGuestsClient.java';s=p.read_text(encoding='utf-8')
a='return new V(a[j+1]+sx*a[j+3],a[j],a[j+2]+cz*a[j+4],i/(float)n,v,sx,0,cz);'
assert a in s,a
s=s.replace(a,'''// A true surface normal includes the vertical taper and the elliptical cross-section.
            int prev=Math.max(0,j-5),next=Math.min(a.length-5,j+5);
            float dy=a[next]-a[prev];
            float rx=Math.max(.01f,Math.abs(a[j+3])),rz=Math.max(.01f,Math.abs(a[j+4]));
            float nx=sx/rx,nz=cz/rz,ny=0;
            if(Math.abs(dy)>.0001f){
                float tx=(a[next+1]-a[prev+1]+sx*(a[next+3]-a[prev+3]))/dy;
                float tz=(a[next+2]-a[prev+2]+cz*(a[next+4]-a[prev+4]))/dy;
                ny=-(nx*tx+nz*tz);
            }
            float len=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
            if(len<.0001f){nx=sx;ny=0;nz=cz;len=1;}
            return new V(a[j+1]+sx*a[j+3],a[j],a[j+2]+cz*a[j+4],i/(float)n,v,nx/len,ny/len,nz/len);''',1)
a='void draw(PoseStack p,VertexConsumer buf,int light,int overlay,float red,float green,float blue,float alpha){'
assert a in s,a
s=s.replace(a,'''void draw(PoseStack p,VertexConsumer buf,int light,int overlay,float red,float green,float blue,float alpha){
            drawStyled(p,buf,light,overlay,red,green,blue,alpha,0);
        }
        void drawStyled(PoseStack p,VertexConsumer buf,int light,int overlay,float red,float green,float blue,float alpha,int style){''',1)
a='int l=(f.tile==12||f.tile==13)?(Math.max(light&65535,11<<4)|Math.max(light&0xffff0000,11<<20)):light;'
assert a in s,a
s=s.replace(a,'''int l=style==1&&f.tile==15?0x00F000F0:style==0&&(f.tile==12||f.tile==13)?(Math.max(light&65535,11<<4)|Math.max(light&0xffff0000,11<<20)):light;
                boolean metal=ArcaneShading.metal(style,f.tile);''',1)
a='buf.vertex(mat,v.x/16f,v.y/16f,v.z/16f).color(red,green,blue,alpha).uv(u,vv).overlayCoords(overlay).uv2(l).normal(norm,v.nx,v.ny,v.nz).endVertex();'
assert a in s,a
s=s.replace(a,'''float shade=style==1&&f.tile==15?1f:ArcaneShading.shade(norm,v.nx,v.ny,v.nz,metal,style,alpha);
                    buf.vertex(mat,v.x/16f,v.y/16f,v.z/16f).color(red*shade,green*shade,blue*shade,alpha).uv(u,vv).overlayCoords(overlay).uv2(l).normal(norm,v.nx,v.ny,v.nz).endVertex();''',1)
a='for(Part c:children)c.draw(p,buf,light,overlay,red,green,blue,alpha);'
assert a in s,a
s=s.replace(a,'for(Part c:children)c.drawStyled(p,buf,light,overlay,red,green,blue,alpha,style);',1)
p.write_text(s,encoding='utf-8')
(java/'ArcaneShading.java').write_text('''package it.noctis.magic;
import org.joml.Matrix3f;
final class ArcaneShading{
 private ArcaneShading(){}
 static boolean metal(int style,int t){
  return switch(style){
   case 1 -> t==0||t==1||t==2||t==3||t==7||t==8||t==10||t==11||t==12||t==13||t==14;
   case 2 -> t==0||t==1||t==2||t==4;
   case 3 -> t==4;
   default -> false;
  };
 }
 static float shade(Matrix3f m,float x,float y,float z,boolean metal,int style,float alpha){
  if(alpha<.60f)return 1f; // Preserve the energy ribbons and transparent effects.
  float nx=m.m00()*x+m.m10()*y+m.m20()*z;
  float ny=m.m01()*x+m.m11()*y+m.m21()*z;
  float nz=m.m02()*x+m.m12()*y+m.m22()*z;
  float len=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
  if(len<.0001f)return 1;
  nx/=len;ny/=len;nz/=len;
  float key=Math.max(0,nx*.42f+ny*.76f+nz*.49f);
  float fill=Math.max(0,-nx*.70f+ny*.21f+nz*.68f);
  float rim=1-Math.abs(nz);rim*=rim;
  float h=Math.max(0,nx*.25f+ny*.45f+nz*.856f);
  float spec=h*h;spec*=spec;spec*=spec;spec*=spec;
  float shade=metal?.64f+.23f*key+.07f*fill+.06f*rim+.18f*spec:
      .84f+.11f*key+.04f*fill+.035f*rim+.025f*spec;
  return Math.max(.58f,Math.min(1,shade));
 }
}''',encoding='utf-8')
for file,style in [('GoldExperienceClient.java',1),('StickyFingersClient.java',2),('WitchHunterClient.java',3),('SushiGuestClient.java',4)]:
 p=java/file;s=p.read_text(encoding='utf-8')
 if style in (1,2):
  import re
  s,n=re.subn(r'root\.draw\((p,v,LightTexture\.pack\([^\n]+?),overlay,r,g,b,([^\n;]+)\);',r'root.drawStyled(\1,overlay,r,g,b,\2,'+str(style)+');',s,count=1);assert n==1,file
 else:
  a='root.draw(p,v,light,overlay,r,g,b,a)'
  assert a in s,file
  s=s.replace(a,'root.drawStyled(p,v,light,overlay,r,g,b,a,'+str(style)+')')
 p.write_text(s,encoding='utf-8')
print('Arcane shading: slope-aware normals, subtle fill and rim light, higher metallic contrast, preserved spectral transparency.')
