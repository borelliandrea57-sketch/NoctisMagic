#version 120
// Noctis Arcane 2.0 - lightweight depth-aware cinematic finishing.
#define BLOOM 1 // [0 1]
#define CONTACT_AO 1 // [0 1]
#define ATMOSPHERE 1 // [0 1]
#define FXAA 1 // [0 1]
#define GRADE 1 // [0 1 2]
#define BLOOM_STRENGTH 0.18 // [0.0 0.08 0.12 0.18 0.25 0.35]
#define AO_STRENGTH 0.28 // [0.0 0.12 0.2 0.28 0.36 0.45]
#define FOG_STRENGTH 0.22 // [0.0 0.12 0.22 0.35 0.5]
uniform sampler2D colortex0;
uniform sampler2D depthtex0;
uniform mat4 gbufferProjectionInverse;
uniform float viewWidth;
uniform float viewHeight;
uniform float rainStrength;
uniform int worldTime;
uniform int isEyeInWater;
uniform vec3 fogColor;
varying vec2 uv;
vec2 safeUV(vec2 p){return clamp(p,vec2(.001),vec2(.999));}
vec3 scene(vec2 p){return texture2D(colortex0,safeUV(p)).rgb;}
float lum(vec3 c){return dot(c,vec3(.2126,.7152,.0722));}
float depth(vec2 p){return texture2D(depthtex0,safeUV(p)).r;}
vec3 positionAt(vec2 p,float d){
    vec4 v=gbufferProjectionInverse*vec4(p*2.0-1.0,d*2.0-1.0,1.0);
    return v.xyz/(abs(v.w)<.00001?.00001:v.w);
}
float aoTap(vec2 p,vec3 origin,vec3 normal,float radius){
    float d=depth(p);
    if(d>=.99998)return 0.0;
    vec3 delta=positionAt(p,d)-origin;
    float distance=length(delta);
    if(distance<.015||distance>radius)return 0.0;
    return max(dot(normal,delta/max(distance,.015))-.12,0.0)*(1.0-smoothstep(.03,radius,distance));
}
float contact(vec2 p,float d,vec2 px){
    if(d>=.99998)return 0.0;
    vec3 o=positionAt(p,d);
    vec3 dx=dFdx(o),dy=dFdy(o);
    vec3 crossN=cross(dx,dy);
    float normLen=length(crossN);
    if(normLen<.000001)return 0.0;
    vec3 n=crossN/normLen;
    if(dot(n,-o)<0.0)n=-n;
    float radius=clamp(length(o)*.035,.38,2.2);
    vec2 r=px*clamp(16.0/(max(length(o),1.0)*.10+1.0),3.0,12.0);
    float a=aoTap(safeUV(p+vec2(r.x,0.0)),o,n,radius)+aoTap(safeUV(p-vec2(r.x,0.0)),o,n,radius);
    a+=aoTap(safeUV(p+vec2(0.0,r.y)),o,n,radius)+aoTap(safeUV(p-vec2(0.0,r.y)),o,n,radius);
    a+=aoTap(safeUV(p+r*.72),o,n,radius)+aoTap(safeUV(p-r*.72),o,n,radius);
    a+=aoTap(safeUV(p+vec2(r.x,-r.y)*.72),o,n,radius)+aoTap(safeUV(p+vec2(-r.x,r.y)*.72),o,n,radius);
    return clamp(a*.30,0.0,1.0);
}
vec3 bright(vec3 c){
    float l=lum(c);
    float peak=max(c.r,max(c.g,c.b));
    float v=smoothstep(.68,1.0,peak)*smoothstep(.32,.78,l);
    return c*v;
}
vec3 bloom(vec2 p,vec2 px){
    vec3 b=bright(scene(p))*2.0;
    b+=bright(scene(p+px*vec2(4.0,0.0)))+bright(scene(p-px*vec2(4.0,0.0)));
    b+=bright(scene(p+px*vec2(0.0,4.0)))+bright(scene(p-px*vec2(0.0,4.0)));
    b+=bright(scene(p+px*vec2(9.0,6.0)))+bright(scene(p-px*vec2(9.0,6.0)));
    b+=bright(scene(p+px*vec2(9.0,-6.0)))+bright(scene(p-px*vec2(9.0,-6.0)));
    return b*.10;
}
vec3 antialias(vec2 p,vec2 px,vec3 center){
    vec3 a=scene(p+px*vec2(-1.0,-1.0)),b=scene(p+px*vec2(1.0,-1.0));
    vec3 c=scene(p+px*vec2(-1.0,1.0)),d=scene(p+px*vec2(1.0,1.0));
    float l=lum(center),la=lum(a),lb=lum(b),lc=lum(c),ld=lum(d);
    float lo=min(l,min(min(la,lb),min(lc,ld))),hi=max(l,max(max(la,lb),max(lc,ld)));
    if(hi-lo<max(.055,hi*.13))return center;
    vec2 dir=vec2(-((la+lb)-(lc+ld)),(la+lc)-(lb+ld));
    float reduce=max((la+lb+lc+ld)*.03125,.0078);
    dir=clamp(dir/(min(abs(dir.x),abs(dir.y))+reduce),vec2(-5.0),vec2(5.0))*px;
    vec3 x=.5*(scene(p+dir*(-.1667))+scene(p+dir*.1667));
    return mix(center,x,.68);
}
void main(){
    vec2 px=1.0/vec2(max(viewWidth,1.0),max(viewHeight,1.0));
    float d=depth(uv);
    vec3 c=scene(uv);
#if FXAA == 1
    c=antialias(uv,px,c);
#endif
#if CONTACT_AO == 1
    c*=1.0-AO_STRENGTH*contact(uv,d,px);
#endif
    float cycle=fract(float(worldTime)/24000.0);
    float day=clamp(cos((cycle-.25)*6.2831853)*.70+.45,0.0,1.0);
    float dusk=pow(1.0-abs(day*2.0-1.0),3.0)*(1.0-rainStrength);
#if ATMOSPHERE == 1
    if(d<.99998){
        float distance=length(positionAt(uv,d));
        float haze=(1.0-exp(-distance*(.003+.003*rainStrength)))*FOG_STRENGTH;
        vec3 tint=mix(vec3(.15,.20,.34),vec3(.69,.80,.90),day);
        tint=mix(tint,vec3(.88,.62,.43),dusk*.40);
        tint=mix(tint,clamp(fogColor,0.0,1.0),.60);
        c=mix(c,tint,haze);
    }
#endif
#if GRADE == 1
    float l=lum(c);
    c=mix(vec3(l),c,1.08);
    c=mix(c,c*vec3(1.04,1.01,.94),day*.65);
    c=mix(c,c*vec3(.92,.98,1.10),(1.0-day)*.60);
    c=clamp((c-.5)*1.06+.5,0.0,1.0);
#elif GRADE == 2
    float l=lum(c);
    c=mix(vec3(l),c,1.16);
    c=mix(c,c*vec3(1.07,.99,.92),day*.70);
    c=mix(c,c*vec3(.88,.96,1.14),(1.0-day)*.70);
    c=clamp((c-.5)*1.12+.5,0.0,1.0);
#endif
#if BLOOM == 1
    vec3 glow=bloom(uv,px);
    c+=glow*BLOOM_STRENGTH*(1.0-.35*c);
#endif
    // Keep underwater contrast without overbrightening the vanilla water tint.
    if(isEyeInWater==1)c=mix(c,c*vec3(.86,1.00,1.05),.23);
    gl_FragColor=vec4(clamp(c,0.0,1.0),1.0);
}
