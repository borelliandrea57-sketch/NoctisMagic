"""Noctis 0.9.0: dark demon geometry, flying familiars, animated boss and Masamune."""
from pathlib import Path
import sys,json,struct,zlib,random,math
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:100]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
def j(path,data):
    p=res/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Replace the humanoid Nether demon's entire model and renderer.
edit('Client.java',[
('e.registerLayerDefinition(DEMON,Client::demonMesh);','e.registerLayerDefinition(DEMON,DarkDemonModel::mesh);'),
('new HumanoidModel<>(c.bakeLayer(DEMON))','new DarkDemonModel(c.bakeLayer(DEMON))'),
('new FamiliarRenderer(c,IMP,"imp")','new FlyingFamiliarRenderer(c,IMP,"imp",0)'),
('new FamiliarRenderer(c,DEVIL,"devil")','new FlyingFamiliarRenderer(c,DEVIL,"devil",1)'),
('new FamiliarRenderer(c,FROST,"frost_familiar")','new FlyingFamiliarRenderer(c,FROST,"frost_familiar",2)'),
('new FamiliarRenderer(c,NIGHT,"night_familiar")','new FlyingFamiliarRenderer(c,NIGHT,"night_familiar",3)')
])
# Remove old wing/leg animation assumptions for the flying variants.
write('FlyingFamiliarRenderer.java','''package it.noctis.magic;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import com.mojang.blaze3d.vertex.*;
public class FlyingFamiliarRenderer extends MobRenderer<Familiar,FlyingFamiliarRenderer.Model>{
    private final ResourceLocation texture;
    public FlyingFamiliarRenderer(EntityRendererProvider.Context c,ModelLayerLocation layer,String tex,int variant){super(c,new Model(c.bakeLayer(layer),variant),.28f);texture=new ResourceLocation(Noctis.ID,"textures/entity/"+tex+".png");}
    @Override public ResourceLocation getTextureLocation(Familiar e){return texture;}
    static class Model extends EntityModel<Familiar>{
        final ModelPart root,head,body,tail;final ModelPart[] wings=new ModelPart[2],arms=new ModelPart[2],legs=new ModelPart[2];final int variant;
        Model(ModelPart r,int v){root=r;variant=v;head=r.getChild("head");body=r.getChild("body");tail=r.getChild("tail");for(int i=0;i<2;i++){wings[i]=r.getChild("wing"+i);arms[i]=r.getChild("arm"+i);legs[i]=r.getChild("leg"+i);}}
        @Override public void setupAnim(Familiar e,float limb,float amount,float age,float yaw,float pitch){
            boolean air=!e.onGround()&&!e.isInSittingPose();float beat=air?(float)Math.sin(age*(variant==0?.72f:.49f)):0;
            head.yRot=yaw*.0174533f;head.xRot=pitch*.012f;
            float bob=air?(float)Math.sin(age*.17)*.65f:0;
            head.y=(variant==1?10:variant==2?12:13)+bob;body.y=(variant==1?18:19)+bob;
            body.xRot=air?.10f:0;tail.xRot=-.3f+(float)Math.sin(age*.19)*.18f;tail.yRot=(float)Math.sin(age*.15)*.28f;
            for(int i=0;i<2;i++){int s=i==0?-1:1;
                wings[i].yRot=s*(air?.42f+beat*.88f:1.05f);
                wings[i].zRot=s*(air?.12f+beat*.38f:.12f);
                arms[i].xRot=air?-.36f+(float)Math.sin(age*.19+i)*.16f:(float)Math.cos(limb*.6662+i*Math.PI)*amount*.65f;
                arms[i].zRot=s*(air?.27f:.08f);legs[i].xRot=air?.5f+(float)Math.sin(age*.16+i)*.12f:(float)Math.cos(limb*.6662+i*Math.PI)*amount*.75f;
                legs[i].zRot=s*(air?.14f:0);
                if(e.isInSittingPose()){legs[i].xRot=-1.2f;arms[i].xRot=-.2f;}
            }
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer b,int l,int o,float r,float g,float bl,float a){root.render(p,b,l,o,r,g,bl,a);}
    }
}''')
write('DarkDemonModel.java','''package it.noctis.magic;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
public class DarkDemonModel extends HumanoidModel<Demon>{
    final ModelPart[] wings=new ModelPart[2],tips=new ModelPart[2];final ModelPart tail,tail2;
    public DarkDemonModel(ModelPart r){super(r);for(int i=0;i<2;i++){wings[i]=body.getChild("wing"+i);tips[i]=wings[i].getChild("outer");}tail=body.getChild("tail");tail2=tail.getChild("joint");}
    static CubeListBuilder c(int u,int v){return CubeListBuilder.create().texOffs(u,v);}
    static PartDefinition part(PartDefinition p,String n,CubeListBuilder b,float x,float y,float z){return p.addOrReplaceChild(n,b,PartPose.offset(x,y,z));}
    static LayerDefinition mesh(){
        MeshDefinition m=HumanoidModel.createMesh(CubeDeformation.NONE,0);PartDefinition r=m.getRoot();
        r.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        PartDefinition h=part(r,"head",c(0,0).addBox(-4,-8,-4,8,8,8),0,-2,0);
        part(h,"muzzle",c(64,0).addBox(-2.7f,-2,-5,5.4f,2.5f,2),0,0,0);
        part(h,"brow",c(78,0).addBox(-4,-6,-4.4f,8,1.5f,1),0,0,0);
        PartDefinition b=part(r,"body",c(16,16).addBox(-5,-1,-2.8f,10,6,5.6f).texOffs(16,32).addBox(-3.7f,5,-2.1f,7.4f,7,4.2f),0,0,0);
        part(b,"spine",c(64,20).addBox(-.7f,0,-.5f,1.4f,10,1),0,0,2.9f);
        for(int i=0;i<2;i++){
            int s=i==0?-1:1;
            PartDefinition horn=h.addOrReplaceChild("horn"+i,c(64,8).addBox(-1.6f,-5,-1.6f,3.2f,5,3.2f),PartPose.offsetAndRotation(s*3,-6,0,-.15f,0,s*.55f));
            PartDefinition horn2=horn.addOrReplaceChild("curve",c(80,8).addBox(-1.2f,-5,-1.2f,2.4f,5,2.4f),PartPose.offsetAndRotation(0,-4,0,-.25f,0,-s*.75f));
            horn2.addOrReplaceChild("tip",c(92,8).addBox(-.6f,-4,-.6f,1.2f,4,1.2f),PartPose.offsetAndRotation(0,-4,0,-.3f,0,-s*.7f));
            h.addOrReplaceChild("ear"+i,c(104,0).addBox(-1,-4,-.9f,2,5,2),PartPose.offsetAndRotation(s*4,-4,0,0,0,s*.9f));
            String an=i==0?"right_arm":"left_arm",ln=i==0?"right_leg":"left_leg";
            PartDefinition arm=part(r,an,c(40,16).addBox(-2.3f,-2,-2.3f,4.6f,6,4.6f).texOffs(40,32).addBox(-1.6f,4,-1.7f,3.2f,7,3.4f),s*6,1,0);
            part(arm,"hand",c(64,32).addBox(-2,10,-2,4,3.2f,4),0,0,0);
            for(int f=0;f<3;f++)part(arm,"claw"+f,c(84,32).addBox(-.45f,0,-.4f,.9f,3,1),-1.3f+f*1.25f,13,-1.4f);
            PartDefinition leg=part(r,ln,c(0,16).addBox(-2,-1,-2,4,7,4).texOffs(0,32).addBox(-1.4f,6,-1.6f,2.8f,6,3.2f),s*2,12,0);
            part(leg,"hoof",c(64,44).addBox(-1.7f,10,-3,3.4f,2,5),0,0,0);
            PartDefinition wing=b.addOrReplaceChild("wing"+i,c(64,56).addBox(s<0?-9:0,-1,-1,9,2,2),PartPose.offsetAndRotation(s*4,1,2.4f,0,s*.35f,-s*.65f));
            PartDefinition out=wing.addOrReplaceChild("outer",c(92,56).addBox(s<0?-10:0,-1,-1,10,2,2),PartPose.offsetAndRotation(s*8,0,0,0,0,s*.32f));
            // Stepped bat membrane silhouette: a high shoulder, pointed tip,
            // curved lower scallops and separate raised struts.
            for(int k=0;k<9;k++){float xx=s*(k+.5f);int height=7+k/2;part(wing,"mem"+k,c(0,64).addBox(-.55f,0,0,1.1f,height,.65f),xx,0,.4f);}
            for(int k=0;k<10;k++){float xx=s*(k+.5f);int height=15-k+(k%3==0?2:0);part(out,"mem"+k,c(32,64).addBox(-.55f,0,0,1.1f,height,.65f),xx,0,.4f);}
            for(int k=0;k<3;k++)out.addOrReplaceChild("rib"+k,c(64,72).addBox(-.45f,0,-.55f,.9f,12-k*3,1.1f),PartPose.offsetAndRotation(s*(1+k*3),0,0,0,0,-s*.22f));
        }
        PartDefinition tail=b.addOrReplaceChild("tail",c(96,0).addBox(-1,-1,0,2,2,8),PartPose.offsetAndRotation(0,10,2,-.25f,0,.1f));
        PartDefinition joint=tail.addOrReplaceChild("joint",c(96,14).addBox(-.8f,-.8f,0,1.6f,1.6f,8),PartPose.offsetAndRotation(0,0,7,.45f,.25f,0));
        joint.addOrReplaceChild("point",c(112,28).addBox(-1.7f,-1.5f,0,3.4f,3,2),PartPose.offsetAndRotation(0,0,7,0,0,.7f));
        return LayerDefinition.create(m,128,128);
    }
    @Override public void setupAnim(Demon e,float limb,float amount,float age,float yaw,float pitch){
        super.setupAnim(e,limb,amount,age,yaw,pitch);hat.visible=false;
        for(int i=0;i<2;i++){int s=i==0?-1:1;wings[i].yRot=s*(.65f+(float)Math.sin(age*.09)*.17f+amount*.18f);wings[i].zRot=-s*(.65f+(float)Math.sin(age*.08)*.06f);tips[i].zRot=s*(.32f+(float)Math.sin(age*.11)*.11f);}
        tail.yRot=(float)Math.sin(age*.13)*.28f;tail2.yRot=(float)Math.cos(age*.13)*.38f;tail2.xRot=.45f+(float)Math.sin(age*.1)*.13f;
    }
}''')
# Flying movement: retain ground navigation only for Umbreon/SirPiovra/shadows.
edit('Familiar.java',[
('private int lifetime=-1;','private int lifetime=-1; private int airHit=0; private net.minecraft.world.phys.Vec3 roamPoint;'),
('goalSelector.addGoal(1,new FloatGoal(this));','if(!eternal()){goalSelector.addGoal(1,new FloatGoal(this));'),
('goalSelector.addGoal(7,new RandomLookAroundGoal(this));targetSelector','goalSelector.addGoal(7,new RandomLookAroundGoal(this));}else{goalSelector.addGoal(1,new SitWhenOrderedToGoal(this));goalSelector.addGoal(2,new LookAtPlayerGoal(this,Player.class,8));}targetSelector'),
('if(getHealth()<getMaxHealth())setHealth(getMaxHealth());clearFire();','if(getHealth()<getMaxHealth())setHealth(getMaxHealth());clearFire();flyTick();')
])
p=java/'Familiar.java';s=p.read_text(encoding='utf-8');idx=s.rfind('}')
s=s[:idx]+'''    @Override public boolean causeFallDamage(float d,float m,net.minecraft.world.damagesource.DamageSource source){return !eternal()&&super.causeFallDamage(d,m,source);}
    private void flyTick(){
        if(airHit>0)airHit--;
        if(isOrderedToSit()){setNoGravity(false);getNavigation().stop();setDeltaMovement(getDeltaMovement().multiply(.5,1,.5));setTarget(null);return;}
        setNoGravity(true);resetFallDistance();setInSittingPose(false);getNavigation().stop();
        net.minecraft.world.phys.Vec3 goal=null;
        LivingEntity owner=getOwner(),enemy=getTarget();
        if(enemy!=null&&(!enemy.isAlive()||distanceTo(enemy)>24||!isTame())){setTarget(null);enemy=null;}
        if(enemy!=null){
            goal=enemy.position().add(0,enemy.getBbHeight()*.6,0);
            if(distanceTo(enemy)<2.1&&airHit==0&&hasLineOfSight(enemy)){doHurtTarget(enemy);airHit=16;setDeltaMovement(getDeltaMovement().add(0,.12,0));}
        }else if(owner!=null&&owner.level()==level()){
            double angle=tickCount*.045+(getId()%6);goal=owner.position().add(Math.cos(angle)*2.1,1.6+Math.sin(angle*1.7)*.35,Math.sin(angle)*2.1);
            if(distanceTo(owner)>16&&level() instanceof ServerLevel sl){
                for(int i=0;i<12;i++){double x=owner.getX()+random.nextInt(7)-3,y=owner.getY()+1.4,z=owner.getZ()+random.nextInt(7)-3;
                    net.minecraft.world.phys.Vec3 q=new net.minecraft.world.phys.Vec3(x,y,z);
                    if(sl.hasChunkAt(net.minecraft.core.BlockPos.containing(q))&&sl.noCollision(this,getBoundingBox().move(q.subtract(position())))){teleportTo(x,y,z);break;}}
            }
        }else{
            if(roamPoint==null||tickCount%100==0||position().distanceTo(roamPoint)<.8){
                net.minecraft.core.BlockPos base=blockPosition();int floor=base.getY();
                for(int y=0;y<8;y++)if(!level().getBlockState(base.below(y+1)).isAir()){floor=base.getY()-y;break;}
                roamPoint=new net.minecraft.world.phys.Vec3(getX()+random.nextInt(7)-3,floor+1.5+random.nextDouble(),getZ()+random.nextInt(7)-3);
            }
            goal=roamPoint;
        }
        if(goal==null)return;
        net.minecraft.world.phys.Vec3 diff=goal.subtract(position());
        net.minecraft.world.phys.Vec3 desired=diff.length()<.18?net.minecraft.world.phys.Vec3.ZERO:diff.normalize().scale(Math.min(enemy!=null?.43:.32,diff.length()*.18));
        net.minecraft.world.phys.Vec3 vel=getDeltaMovement().scale(.58).add(desired.scale(.42));
        if(!level().noCollision(this,getBoundingBox().move(vel))){vel=new net.minecraft.world.phys.Vec3(vel.x*.15,.15,vel.z*.15);if(!level().noCollision(this,getBoundingBox().move(vel)))vel=net.minecraft.world.phys.Vec3.ZERO;}
        setDeltaMovement(vel);if(diff.horizontalDistanceSqr()>.04){float yaw=(float)(Math.atan2(diff.z,diff.x)*180/Math.PI)-90;setYRot(yaw);yBodyRot=yaw;setYHeadRot(yaw);}
    }
''' +s[idx:];p.write_text(s,encoding='utf-8')
# Boss animation events are sent to clients during wind-up, thrust and casting.
edit('OneWinged.java',[
('private int cooldown=65,phase=0,attack=0;','''private int cooldown=65,phase=0,attack=0;
    private int dash=0;private boolean dashHit;private int visualTicks=0,visualMode=0;
    public int animationMode(){return visualMode;}
    public float animationProgress(float partial){return 1-Math.max(0,visualTicks-partial)/24f;}
    @Override public void handleEntityEvent(byte id){if(id>=70&&id<=72){visualMode=id-69;visualTicks=24;return;}super.handleEntityEvent(id);}
    private void animate(int mode){level().broadcastEntityEvent(this,(byte)(69+mode));}
    '''),
('super.tick();if(!(level() instanceof ServerLevel l)||!isAlive())return;','super.tick();if(visualTicks>0)visualTicks--;else visualMode=0;if(!(level() instanceof ServerLevel l)||!isAlive())return;'),
('double angle=tickCount*.035;','''if(dash>0){
            dash--;Vec3 aim=t.position().add(0,.65,0).subtract(position());
            float facing=(float)(Math.atan2(aim.z,aim.x)*180/Math.PI)-90;setYRot(facing);yBodyRot=facing;setYHeadRot(facing);
            if(dash>17){setDeltaMovement(getDeltaMovement().scale(.45));if(dash==18)playSound(SoundEvents.PLAYER_ATTACK_SWEEP,.9f,.55f);}
            else if(dash>5){
                Vec3 rush=aim.length()>.5?aim.normalize().scale(phase==2?1.18:.95):Vec3.ZERO;setDeltaMovement(rush);
                l.sendParticles(ParticleTypes.SWEEP_ATTACK,getX(),getY()+1.4,getZ(),1,.15,.15,.15,0);
                if(!dashHit&&distanceTo(t)<4.5&&hasLineOfSight(t)){dashHit=true;t.hurt(damageSources().mobAttack(this),28+phase*5);t.knockback(1.4, -aim.x,-aim.z);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,1.3f,.7f);}
            }else setDeltaMovement(getDeltaMovement().scale(.55).add(0,.08,0));
            return;
        }
        double angle=tickCount*.035;'''),
('if(dist<5&&hasLineOfSight(t)){t.hurt(damageSources().mobAttack(this),24+phase*4);t.knockback(1.2,to.x,to.z);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,1.3f,.65f);}\n            else{cooldown=12;attack--;setDeltaMovement(to.normalize().scale(.85));}','dash=24;dashHit=false;animate(1);setDeltaMovement(getDeltaMovement().scale(.2));'),
('Vec3 start=position().add(0,2,0),end=t.getEyePosition();','animate(2);Vec3 start=position().add(0,2,0),end=t.getEyePosition();'),
('for(int i=0;i<3+phase;i++){Vec3 aim=','animate(3);for(int i=0;i<3+phase;i++){Vec3 aim='),
('spawnAtLocation(net.minecraft.world.item.Items.NETHER_STAR);','spawnAtLocation(net.minecraft.world.item.Items.NETHER_STAR);spawnAtLocation(Noctis.MASAMUNE.get());')
])
edit('FallenClient.java',[
('final ModelPart wing,outer;','final ModelPart wing,outer,hairL,hairR,hairBack;'),
('outer=wing.getChild("outer");','outer=wing.getChild("outer");hairL=head.getChild("lock-1");hairR=head.getChild("lock1");hairBack=head.getChild("silver");'),
('leftLeg.xRot=.12f;rightLeg.xRot=-.12f;rightArm.xRot=-.7f+(float)Math.sin(age*.08)*.25f;leftArm.zRot=.15f;','''float p=e.animationProgress(age-e.tickCount);int mode=e.animationMode();
            leftLeg.xRot=.12f;rightLeg.xRot=-.12f;rightArm.xRot=-.7f+(float)Math.sin(age*.08)*.25f;leftArm.zRot=.15f;
            body.xRot=0;body.yRot=0;rightArm.zRot=0;leftArm.xRot=0;
            float wind=(float)Math.sin(age*.20)*.065f;hairL.xRot=wind;hairR.xRot=wind*.8f;hairL.zRot=-.055f+(float)Math.sin(age*.15)*.045f;hairR.zRot=.055f-(float)Math.sin(age*.15)*.045f;hairBack.xRot=wind*.5f;
            if(mode==1){
                float thrust=p<.25f?0:p<.42f?(p-.25f)/.17f:p<.76f?1:Math.max(0,(1-p)/.24f);
                float prep=p<.25f?(float)Math.sin(p/.25f*Math.PI):0;
                rightArm.xRot=-.55f-prep*.65f-thrust*1.05f;rightArm.zRot=-.1f-prep*.6f;body.xRot=thrust*.48f;body.yRot=prep*.25f;leftArm.xRot=thrust*.65f;rightLeg.xRot=-thrust*.75f;leftLeg.xRot=thrust*.35f;wing.yRot=-.35f-thrust*.9f;hairL.xRot=-thrust*.4f+wind;hairR.xRot=-thrust*.4f+wind;hairBack.xRot=-thrust*.22f;
            }else if(mode==2||mode==3){float power=(float)Math.sin(Math.PI*Math.min(1,p));leftArm.xRot=-1.5f*power;leftArm.zRot=.7f*power;rightArm.xRot=-.9f*power;wing.zRot=-.55f-power*.35f;hairL.xRot=-power*.2f;hairR.xRot=-power*.2f;}
            ''')
])
# The long sword is a real collectible weapon with durability and combat effects.
edit('Noctis.java',[
('public static final RegistryObject<Item> WINE=WineItem.WINE;','public static final RegistryObject<Item> MASAMUNE=ITEMS.register("masamune",MasamuneItem::new);\n    public static final RegistryObject<Item> WINE=WineItem.WINE;'),
('e.accept(WineItem.WINE.get());','e.accept(WineItem.WINE.get());'),
('if(e.getTabKey()==CreativeModeTabs.SPAWN_EGGS)','if(e.getTabKey()==CreativeModeTabs.COMBAT)e.accept(MASAMUNE.get());if(e.getTabKey()==CreativeModeTabs.SPAWN_EGGS)')
])
write('MasamuneItem.java','''package it.noctis.magic;
import net.minecraft.world.item.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.item.enchantment.Enchantments;
public class MasamuneItem extends SwordItem {
    public MasamuneItem(){super(Tiers.NETHERITE,19,-2.25f,new Item.Properties().durability(4096).rarity(Rarity.EPIC).fireResistant());}
    @Override public boolean hurtEnemy(ItemStack stack,LivingEntity victim,LivingEntity attacker){
        if(attacker.level() instanceof ServerLevel l){victim.addEffect(new MobEffectInstance(MobEffects.WITHER,60,1));l.sendParticles(ParticleTypes.SWEEP_ATTACK,victim.getX(),victim.getY()+victim.getBbHeight()*.6,victim.getZ(),1,0,0,0,0);l.sendParticles(ParticleTypes.END_ROD,victim.getX(),victim.getY()+.8,victim.getZ(),8,.25,.3,.25,.015);}
        return super.hurtEnemy(stack,victim,attacker);
    }
    @Override public boolean isFoil(ItemStack s){return true;}
}''')
# UV-conscious high contrast face and muscle/wing shading; all geometry uses custom atlas.
def png(path,w,h,pix):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for p in row for v in p) for row in pix)
    p=assets/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
rng=random.Random(909);pix=[[(35,27,35,255) for x in range(128)] for y in range(128)]
def R(x,y,w,h,col,noise=0):
    for yy in range(max(0,y),min(128,y+h)):
        for xx in range(max(0,x),min(128,x+w)):
            d=rng.randint(-noise,noise);pix[yy][xx]=tuple(max(0,min(255,v+d)) for v in col)+(255,)
R(0,0,32,16,(43,34,43),6);R(8,8,8,8,(57,39,47),5);R(8,8,8,2,(24,22,30),4)
R(9,10,2,1,(255,224,171));R(13,10,2,1,(255,224,171));R(10,10,1,1,(219,61,40));R(13,10,1,1,(219,61,40))
R(9,11,6,1,(31,23,31));R(11,12,2,1,(105,60,61));R(10,14,4,1,(21,18,25));R(10,14,1,1,(233,218,187));R(13,14,1,1,(233,218,187))
for x in [0,16,24]:R(x,8,8,8,(36,28,37),5)
R(16,16,28,14,(50,36,46),8);R(21,22,10,6,(74,45,50),4)
R(22,22,4,2,(105,61,61),4);R(27,22,4,2,(105,61,61),4);R(26,23,1,5,(20,16,25))
R(16,32,24,14,(46,32,41),5)
for y in [37,39,41]:R(21,y,3,1,(92,49,52));R(25,y,3,1,(92,49,52))
R(40,16,22,15,(54,37,45),7);R(46,22,4,4,(83,49,54),5);R(40,32,22,14,(42,30,39),7)
R(0,16,16,15,(45,32,42),6);R(0,32,16,13,(31,25,34),5)
R(64,0,30,7,(48,35,42),6);R(64,8,32,12,(24,22,29),7);R(66,8,2,10,(100,63,58),5);R(80,8,2,9,(80,52,53),4)
R(96,0,20,28,(49,33,43),7);R(112,28,12,8,(31,24,32),4)
R(64,32,18,11,(42,30,38),6);R(84,32,8,8,(124,105,88),6);R(64,44,18,12,(24,21,28),5)
R(64,56,56,10,(55,38,45),7)
for y in range(64,91):
    tone=(65+(y%6)*3,26+(y%5)*2,33+(y%4)*2)
    R(0,y,62,1,tone,5)
for x in range(2,62,6):R(x,64,1,24,(102,39,43),4)
R(64,72,24,22,(41,28,37),5)
png('textures/entity/demon.png',128,128,pix)
# 64x64 diagonal sword icon, silver blade with a black hilt and gold guard.
pix=[[(0,0,0,0) for x in range(64)] for y in range(64)]
for y in range(64):
    for x in range(64):
        u=x-y;v=x+y
        # from lower-left to upper-right in image coordinates
        if abs(v-63)<=1 and 7<=u<=57:pix[y][x]=(205,218,236,255) if v<=63 else (113,134,164,255)
        if v==62 and 7<=u<=56:pix[y][x]=(250,250,255,255)
        if abs(u-6)<=2 and abs(v-63)<=7:pix[y][x]=(187,149,79,255) if u>=6 else (105,76,43,255)
        if abs(v-63)<=2 and -14<=u<=3:pix[y][x]=(31,28,39,255) if u%4<2 else (101,83,70,255)
        if abs(u+15)<=1 and abs(v-63)<=3:pix[y][x]=(183,147,77,255)
png('textures/item/masamune.png',64,64,pix)
j('assets/noctismagic/models/item/masamune.json',{"parent":"minecraft:item/handheld","textures":{"layer0":"noctismagic:item/masamune"},"display":{"thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,5,1],"scale":[1.5,1.5,1.5]},"thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,5,1],"scale":[1.5,1.5,1.5]},"firstperson_righthand":{"rotation":[0,-90,25],"translation":[1.1,3.2,1.1],"scale":[1.25,1.25,1.25]},"firstperson_lefthand":{"rotation":[0,90,-25],"translation":[1.1,3.2,1.1],"scale":[1.25,1.25,1.25]}}})
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['item.noctismagic.masamune']='Masamune';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.9.0: flying companions, demon model, boss attacks and Masamune applied')
