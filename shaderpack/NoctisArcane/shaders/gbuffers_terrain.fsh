#version 120
#define LEAF_LIGHT 1 // [0 1]
#define LEAF_SCATTER 0.24 // [0.0 0.12 0.24 0.36]
uniform sampler2D texture;
uniform sampler2D lightmap;
uniform vec3 sunPosition;
uniform int worldTime;
uniform float rainStrength;
varying vec2 texcoord;
varying vec2 lmcoord;
varying vec4 tint;
varying vec3 normalView;
varying float foliage;
varying vec3 worldPos;
/* DRAWBUFFERS:0 */
void main(){
 vec4 albedo=texture2D(texture,texcoord)*tint;
 if(albedo.a<.1)discard;
 vec3 lm=texture2D(lightmap,lmcoord).rgb;
 vec3 c=albedo.rgb*lm;
 #if LEAF_LIGHT == 1
 if(foliage>.5){
  float phase=fract(float(worldTime)/24000.0);
  float day=clamp(sin(phase*6.2831853)*1.4+.15,0.0,1.0);
  vec3 sun=sunPosition/max(length(sunPosition),.001);
  float back=pow(max(0.0,-dot(normalize(normalView),sun)),1.7);
  float sky=smoothstep(.40,.95,lmcoord.y);
  float transmission=back*day*sky*(1.0-rainStrength*.65)*LEAF_SCATTER;
  c+=albedo.rgb*vec3(.60,.83,.27)*transmission;
  float veins=smoothstep(.18,.60,dot(albedo.rgb,vec3(.2126,.7152,.0722)));
  c*=.96+.08*veins;
 }
 #endif
 gl_FragData[0]=vec4(clamp(c,0.0,1.0),albedo.a);
}
