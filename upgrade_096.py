"""0.9.6: more friendly Nether demons, two distinct forms, real flying AI."""
from pathlib import Path
import sys,json,struct,zlib
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
edit('Noctis.java',[
('public static final RegistryObject<EntityType<Demon>> DEMON=', '''public static final RegistryObject<EntityType<Demon>> SKY_DEMON=ENTITIES.register("sky_demon",()->EntityType.Builder.<Demon>of(Demon::new,MobCategory.CREATURE).sized(.75f,2.05f).fireImmune().clientTrackingRange(10).build(ID+":sky_demon"));
    public static final RegistryObject<Item> SKY_DEMON_EGG=ITEMS.register("sky_demon_spawn_egg",()->new ForgeSpawnEggItem(SKY_DEMON,0x272337,0x9c78d1,new Item.Properties()));
    public static final RegistryObject<EntityType<Demon>> DEMON='''),
('e.put(DEMON.get(),Demon.attributes().build());','e.put(DEMON.get(),Demon.attributes().build());e.put(SKY_DEMON.get(),Demon.attributes().build());'),
('e.accept(DEMON_EGG.get());','e.accept(DEMON_EGG.get());e.accept(SKY_DEMON_EGG.get());')
])
p=java/'Encounter.java';s=p.read_text(encoding='utf-8');start=s.index('        if(l.dimension()==Level.NETHER');end=s.index('\n    }\n    static BlockPos',start)
s=s[:start]+'''        if(l.dimension()==Level.NETHER&&p.getRandom().nextInt(3)!=0){
            int nearby=l.getEntitiesOfClass(Demon.class,p.getBoundingBox().inflate(48)).size();
            int count=Math.min(2,Math.max(0,6-nearby));
            for(int spawn=0;spawn<count;spawn++){
                boolean flying=p.getRandom().nextInt(2)==0;
                for(int i=0;i<32;i++){
                    int dx=p.getRandom().nextInt(43)-21,dz=p.getRandom().nextInt(43)-21;
                    if(dx*dx+dz*dz<64)continue;
                    int x=p.getBlockX()+dx,z=p.getBlockZ()+dz;
                    int y=p.getBlockY()+p.getRandom().nextInt(15)-7;
                    BlockPos pos=new BlockPos(x,y,z);
                    if(!l.hasChunkAt(pos)||!l.getWorldBorder().isWithinBounds(pos))continue;
                    // Search for cave floors instead of the Nether roof heightmap.
                    for(int down=0;down<8;down++){
                        if(pos.getY()<=l.getMinBuildHeight()+2)break;
                        if(l.getBlockState(pos.below()).isFaceSturdy(l,pos.below(),Direction.UP))break;
                        pos=pos.below();
                    }
                    if(!l.getBlockState(pos.below()).isFaceSturdy(l,pos.below(),Direction.UP))continue;
                    if(flying&&l.isEmptyBlock(pos.above(3))&&l.isEmptyBlock(pos.above(4)))pos=pos.above(2);
                    if(!l.isEmptyBlock(pos)||!l.isEmptyBlock(pos.above())||!l.isEmptyBlock(pos.above(2))||!l.getFluidState(pos).isEmpty())continue;
                    Demon d=(flying?Noctis.SKY_DEMON.get():Noctis.DEMON.get()).create(l);
                    if(d!=null){d.moveTo(x+.5,pos.getY(),z+.5,p.getRandom().nextFloat()*360,0);if(l.noCollision(d)&&l.addFreshEntity(d))break;}
                }
            }
        }'''+s[end:];p.write_text(s,encoding='utf-8')
edit('Demon.java',[
('private boolean gifted; private int dialogue;','private boolean gifted; private int dialogue; private net.minecraft.world.phys.Vec3 flightGoal; private int flightTimer;'),
('public static AttributeSupplier.Builder attributes()','public boolean flyingForm(){return getType()==Noctis.SKY_DEMON.get();}\n    public static AttributeSupplier.Builder attributes()'),
('goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,1));','if(!flyingForm())goalSelector.addGoal(2,new WaterAvoidingRandomStrollGoal(this,1));'),
('    @Override public InteractionResult mobInteract','''    @Override public boolean causeFallDamage(float d,float m,net.minecraft.world.damagesource.DamageSource source){return !flyingForm()&&super.causeFallDamage(d,m,source);}
    @Override public void tick(){
        super.tick();
        if(!(level() instanceof net.minecraft.server.level.ServerLevel l)||!flyingForm())return;
        setNoGravity(true);resetFallDistance();getNavigation().stop();
        Player nearby=l.getNearestPlayer(this,10);
        boolean greeting=nearby!=null&&!nearby.isSpectator()&&distanceToSqr(nearby)<64&&hasLineOfSight(nearby);
        if(greeting){
            net.minecraft.world.phys.Vec3 delta=nearby.position().subtract(position());double horizontal=Math.sqrt(delta.x*delta.x+delta.z*delta.z);
            if(horizontal>3.5)flightGoal=nearby.position().add(-delta.x/Math.max(1,horizontal)*3,0.3,-delta.z/Math.max(1,horizontal)*3);
            else flightGoal=new net.minecraft.world.phys.Vec3(getX(),nearby.getY()+.3,getZ());
        }else if(flightGoal==null||--flightTimer<=0||position().distanceToSqr(flightGoal)<1||horizontalCollision||verticalCollision){
            flightTimer=60+random.nextInt(80);flightGoal=position();
            for(int i=0;i<18;i++){
                net.minecraft.world.phys.Vec3 q=position().add(random.nextInt(19)-9,random.nextInt(9)-4,random.nextInt(19)-9);
                if(q.y<l.getMinBuildHeight()+4||q.y>l.getMaxBuildHeight()-5||!l.hasChunkAt(net.minecraft.core.BlockPos.containing(q)))continue;
                if(!l.noCollision(this,getBoundingBox().move(q.subtract(position()))))continue;
                var hit=l.clip(new net.minecraft.world.level.ClipContext(position().add(0,1,0),q.add(0,1,0),net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,this));
                if(hit.getType()!=net.minecraft.world.phys.HitResult.Type.MISS)continue;
                flightGoal=q;break;
            }
        }
        var diff=flightGoal.subtract(position());
        var goal=diff.lengthSqr()<.08?net.minecraft.world.phys.Vec3.ZERO:diff.normalize().scale(Math.min(greeting?.18:.32,diff.length()*.15));
        var v=getDeltaMovement().scale(.55).add(goal.scale(.45));
        if(!l.noCollision(this,getBoundingBox().move(v))){flightTimer=0;flightGoal=null;v=net.minecraft.world.phys.Vec3.ZERO;}
        setDeltaMovement(v);
        if(!greeting&&diff.horizontalDistanceSqr()>.05){float yaw=(float)(Math.atan2(diff.z,diff.x)*180/Math.PI)-90;setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);}
        if(tickCount%9==0)l.sendParticles(net.minecraft.core.particles.ParticleTypes.SOUL_FIRE_FLAME,getX(),getY()+.7,getZ(),2,.25,.35,.25,.006);
    }
    @Override public InteractionResult mobInteract'''),
('else p.sendSystemMessage(Component.literal("Demone: "+LINES[(dialogue++)%LINES.length]));','else {String[] air={"Le correnti del Nether sono stranamente tranquille.","Non tutte le ali appartengono agli angeli.","Da quassu si vedono cose meravigliose.","Se cadi nella lava, fai attenzione."};p.sendSystemMessage(Component.literal("Demone: "+(flyingForm()?air[(dialogue++)%air.length]:LINES[(dialogue++)%LINES.length])));}')
])
edit('Client.java',[
('e.registerEntityRenderer(Noctis.DEMON.get(),DemonRenderer::new);','e.registerEntityRenderer(Noctis.DEMON.get(),DemonRenderer::new);e.registerEntityRenderer(Noctis.SKY_DEMON.get(),DemonRenderer::new);'),
('return tex("demon");','return tex(e.flyingForm()?"sky_demon":"demon");')
])
edit('DarkDemonModel.java',[
('part(b,"spine",','part(b,"groundArmor",c(16,32).addBox(-5.5f,-1,-3.4f,11,3,1),0,0,0);\n        part(h,"skyCrest",c(92,8).addBox(-.7f,-5,-.8f,1.4f,5,1.6f),0,-7,2);\n        part(b,"spine",'),
('super.setupAnim(e,limb,amount,age,yaw,pitch);hat.visible=false;','''super.setupAnim(e,limb,amount,age,yaw,pitch);hat.visible=false;
        boolean fly=e.flyingForm();body.getChild("groundArmor").visible=!fly;head.getChild("skyCrest").visible=fly;
        float beat=(float)Math.sin(age*.50);
        body.xRot=fly?.13f:0;body.xScale=fly?.85f:1.08f;body.zScale=fly?.87f:1.1f;
        rightArm.xRot=fly?-.3f: rightArm.xRot;leftArm.xRot=fly?-.3f:leftArm.xRot;
        rightLeg.xRot=fly?.6f:rightLeg.xRot;leftLeg.xRot=fly?.6f:leftLeg.xRot;
        '''),
('wings[i].yRot=s*(.65f+(float)Math.sin(age*.09)*.17f+amount*.18f);wings[i].zRot=-s*(.65f+(float)Math.sin(age*.08)*.06f);tips[i].zRot=s*(.32f+(float)Math.sin(age*.11)*.11f);','''wings[i].xScale=fly?1.23f:.82f;wings[i].yScale=fly?1.13f:.85f;
            wings[i].yRot=s*(fly?.22f+beat*.85f:1.0f+(float)Math.sin(age*.09)*.12f+amount*.1f);
            wings[i].zRot=-s*(fly?.36f+beat*.35f:.8f);tips[i].zRot=s*(fly?.2f-beat*.24f:.45f);''')
])
# Recolor the existing RGBA atlas into charcoal violet/blue, with pale horns and gold eyes.
p=assets/'textures/entity/demon.png';data=p.read_bytes();pos=8;compressed=b''
while pos<len(data):
    n=struct.unpack('>I',data[pos:pos+4])[0];k=data[pos+4:pos+8];b=data[pos+8:pos+8+n];pos+=12+n
    if k==b'IHDR':w,h,depth,color,_,_,_=struct.unpack('>IIBBBBB',b)
    elif k==b'IDAT':compressed+=b
raw=zlib.decompress(compressed);stride=w*4+1;out=bytearray(raw)
for y in range(h):
    assert raw[y*stride]==0
    for x in range(w):
        i=y*stride+1+x*4;r,g,b,a=raw[i:i+4]
        if 8<=x<16 and y==10 and r>170:rgb=(246,211,111)
        elif 64<=x<96 and 8<=y<20:rgb=(min(255,r+40),min(255,g+35),min(255,b+55))
        elif y>=64:rgb=(max(0,int(r*.66)),min(255,int(g*.88+12)),min(255,int(r*.78+b*.4+24)))
        else:rgb=(int(r*.72),min(255,int(g*.93+6)),min(255,int(b*1.2+25)))
        out[i:i+4]=bytes((*rgb,a))
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
(assets/'textures/entity/sky_demon.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(out))+chunk(b'IEND',b''))
(assets/'models/item/sky_demon_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
    d['entity.noctismagic.demon']='Demone delle braci' if it else 'Ember Demon'
    d['entity.noctismagic.sky_demon']='Demone del crepuscolo' if it else 'Twilight Demon'
    d['item.noctismagic.demon_spawn_egg']='Uovo generatore: Demone delle braci' if it else 'Ember Demon Spawn Egg'
    d['item.noctismagic.sky_demon_spawn_egg']='Uovo generatore: Demone del crepuscolo' if it else 'Twilight Demon Spawn Egg'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.9.6: more Nether demons and flying variant added')
