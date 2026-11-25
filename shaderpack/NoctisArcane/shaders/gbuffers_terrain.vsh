#version 120
#define LEAF_WIND 1 // [0 1]
#define WIND_STRENGTH 0.65 // [0.0 0.35 0.65 1.0]
attribute vec4 mc_Entity;
attribute vec4 mc_midTexCoord;
uniform mat4 gbufferModelViewInverse;
uniform mat4 gbufferModelView;
uniform vec3 cameraPosition;
uniform float frameTimeCounter;
uniform float rainStrength;
varying vec2 texcoord;
varying vec2 lmcoord;
varying vec4 tint;
varying vec3 normalView;
varying float foliage;
varying vec3 worldPos;
void main(){
 vec4 view=gl_ModelViewMatrix*gl_Vertex;
 vec4 world=gbufferModelViewInverse*view;
 worldPos=world.xyz+cameraPosition;
 foliage=mc_Entity.x==10001.0?1.0:mc_Entity.x==10002.0?2.0:0.0;
 #if LEAF_WIND == 1
 if(foliage>.5){
  float phase=frameTimeCounter*1.7+worldPos.x*.39+worldPos.z*.31+worldPos.y*.16;
  float gust=sin(phase*.55)+.38*sin(phase*1.93);
  float weight=foliage>1.5?step(gl_MultiTexCoord0.t,mc_midTexCoord.t):.75;
  world.x+=gust*.063*weight*WIND_STRENGTH*(1.0+rainStrength*.75);
  world.z+=cos(phase*.85)*.044*weight*WIND_STRENGTH;
  world.y+=sin(phase*1.25)*.018*weight*WIND_STRENGTH;
  view=gbufferModelView*world;
 }
 #endif
 texcoord=(gl_TextureMatrix[0]*gl_MultiTexCoord0).xy;
 lmcoord=(gl_TextureMatrix[1]*gl_MultiTexCoord1).xy;
 tint=gl_Color;
 normalView=normalize(gl_NormalMatrix*gl_Normal);
 gl_Position=gl_ProjectionMatrix*view;
}
