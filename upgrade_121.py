"""1.2.1: Griffith's eclipse hostility, collectible energy drinks, Ultra White gear."""
from pathlib import Path
import sys,json,struct,zlib,math
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,w,h,pix):
    p.parent.mkdir(parents=True,exist_ok=True)
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+pix[y*w*4:(y+1)*w*4] for y in range(h))))+chunk(b'IEND',b''))
flavors=[('original','Original',(24,26,30),(120,212,43)),('ultra_white','Ultra White',(236,239,243),(133,148,159)),('mango_loco','Mango Loco',(33,157,186),(244,165,49)),('pipeline_punch','Pipeline Punch',(233,108,151),(96,39,72)),('ultra_violet','Ultra Violet',(113,67,158),(226,217,244)),('ultra_red','Ultra Red',(188,34,50),(240,223,226)),('pacific_punch','Pacific Punch',(228,206,167),(180,40,42))]
gear=[('helmet','HELMET'),('chestplate','CHESTPLATE'),('leggings','LEGGINGS'),('boots','BOOTS')]
decl='public static final RegistryObject<EntityType<Griffith>> GRIFFITH=ENTITIES.register("griffith",()->EntityType.Builder.<Griffith>of(Griffith::new,MobCategory.CREATURE).sized(.65f,1.95f).clientTrackingRange(12).build(ID+":griffith"));\n    public static final RegistryObject<Item> GRIFFITH_EGG=ITEMS.register("griffith_spawn_egg",()->new ForgeSpawnEggItem(GRIFFITH,0xe9e9ef,0x7a889f,new Item.Properties()));\n    '
for i,(n,*_) in enumerate(flavors):decl+=f'public static final RegistryObject<Item> ENERGY_{n.upper()}=ITEMS.register("monster_{n}",()->new EnergyDrink({i}));\n    '
for n,t in gear:decl+=f'public static final RegistryObject<Item> WHITE_{n.upper()}=ITEMS.register("ultra_white_{n}",()->new ArmorItem(EnergyGear.MATERIAL,ArmorItem.Type.{t},new Item.Properties().rarity(net.minecraft.world.item.Rarity.RARE)));\n    '
for n,cls,damage,speed in [('sword','SwordItem',4,-2.4),('axe','AxeItem',6,-3),('pickaxe','PickaxeItem',1,-2.8),('shovel','ShovelItem',1.5,-3)]:
    decl+=f'public static final RegistryObject<Item> WHITE_{n.upper()}=ITEMS.register("ultra_white_{n}",()->new {cls}(EnergyGear.TIER,{damage if n in ("sword","pickaxe") else str(float(damage))+"f"},{float(speed)}f,new Item.Properties().rarity(net.minecraft.world.item.Rarity.RARE)));\n    '
a='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',a,decl+a)
# Fully qualify item classes to avoid relying on imports in the original project.
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
for c in ['ArmorItem','SwordItem','AxeItem','PickaxeItem','ShovelItem']:
    s=s.replace('()->new '+c+'(EnergyGear','()->new net.minecraft.world.item.'+c+'(EnergyGear')
s=s.replace('EnergyGear.MATERIAL,ArmorItem.Type.','EnergyGear.MATERIAL,net.minecraft.world.item.ArmorItem.Type.')
p.write_text(s,encoding='utf-8')
edit('Noctis.java','e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());','e.put(GRIFFITH.get(),Griffith.attributes().build());e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());')
edit('Noctis.java','e.accept(CATHEDRAL_EGG.get());','e.accept(CATHEDRAL_EGG.get());e.accept(GRIFFITH_EGG.get());')
edit('Noctis.java','if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)','if(e.getTabKey()==CreativeModeTabs.FOOD_AND_DRINKS){'+''.join(f'e.accept(ENERGY_{n.upper()}.get());' for n,*_ in flavors)+'}if(e.getTabKey()==CreativeModeTabs.COMBAT){'+''.join(f'e.accept(WHITE_{n.upper()}.get());' for n in ['helmet','chestplate','leggings','boots','sword','axe'])+'}if(e.getTabKey()==CreativeModeTabs.TOOLS_AND_UTILITIES){e.accept(WHITE_PICKAXE.get());e.accept(WHITE_SHOVEL.get());}if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)')
write('EnergyDrink.java','''package it.noctis.magic;
import net.minecraft.world.item.*;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
public class EnergyDrink extends Item{
    final int flavor;
    EnergyDrink(int flavor){super(new Properties().stacksTo(16).food(new FoodProperties.Builder().nutrition(2).saturationMod(.15f).alwaysEat().build()));this.flavor=flavor;}
    @Override public UseAnim getUseAnimation(ItemStack s){return UseAnim.DRINK;}
    @Override public int getUseDuration(ItemStack s){return 24;}
    @Override public ItemStack finishUsingItem(ItemStack s,Level l,LivingEntity e){
        if(!l.isClientSide){
            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,1200,0));
            switch(flavor){
                case 0->e.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,900,0));
                case 1->{e.addEffect(new MobEffectInstance(MobEffects.DIG_SPEED,1200,1));e.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,600,0));}
                case 2->e.addEffect(new MobEffectInstance(MobEffects.REGENERATION,160,1));
                case 3->e.addEffect(new MobEffectInstance(MobEffects.JUMP,1200,1));
                case 4->e.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,3600,0));
                case 5->e.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE,1200,0));
                case 6->e.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING,1200,0));
            }
        }return super.finishUsingItem(s,l,e);
    }
}''')
write('EnergyGear.java','''package it.noctis.magic;
import net.minecraft.sounds.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.Ingredient;
public final class EnergyGear{
    static final Tier TIER=new Tier(){
        public int getUses(){return 1800;}public float getSpeed(){return 9f;}public float getAttackDamageBonus(){return 4f;}public int getLevel(){return 4;}public int getEnchantmentValue(){return 18;}public Ingredient getRepairIngredient(){return Ingredient.of(Noctis.ENERGY_ULTRA_WHITE.get());}
    };
    static final ArmorMaterial MATERIAL=new ArmorMaterial(){
        public int getDurabilityForType(ArmorItem.Type t){return (switch(t){case HELMET->11;case CHESTPLATE->16;case LEGGINGS->15;case BOOTS->13;})*37;}
        public int getDefenseForType(ArmorItem.Type t){return switch(t){case HELMET,BOOTS->3;case CHESTPLATE->8;case LEGGINGS->6;};}
        public int getEnchantmentValue(){return 18;}public SoundEvent getEquipSound(){return SoundEvents.ARMOR_EQUIP_IRON;}
        public Ingredient getRepairIngredient(){return Ingredient.of(Noctis.ENERGY_ULTRA_WHITE.get());}
        public String getName(){return "noctismagic:ultra_white";}public float getToughness(){return 2.5f;}public float getKnockbackResistance(){return .08f;}
    };
}''')
write('EnergyDrops.java','''package it.noctis.magic;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public final class EnergyDrops{
    @SubscribeEvent public static void drop(LivingDropsEvent e){
        if(!(e.getEntity() instanceof Mob m)||m.level().isClientSide||m.getRandom().nextInt(10)!=0)return;
        var choices=java.util.List.of('''+','.join('Noctis.ENERGY_'+n.upper() for n,*_ in flavors)+''');
        e.getDrops().add(new net.minecraft.world.entity.item.ItemEntity(m.level(),m.getX(),m.getY()+.35,m.getZ(),new ItemStack(choices.get(m.getRandom().nextInt(choices.size())).get())));
    }
}''')
write('Griffith.java','''package it.noctis.magic;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.effect.*;
public class Griffith extends PathfinderMob{
    static final EntityDataAccessor<Boolean> ECLIPSED=SynchedEntityData.defineId(Griffith.class,EntityDataSerializers.BOOLEAN);
    int speech,slash;
    public Griffith(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(Items.IRON_SWORD));setDropChance(EquipmentSlot.MAINHAND,0);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(ECLIPSED,false);}
    public boolean eclipsed(){return entityData.get(ECLIPSED);}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,240).add(Attributes.ARMOR,15).add(Attributes.ATTACK_DAMAGE,24).add(Attributes.MOVEMENT_SPEED,.31).add(Attributes.FOLLOW_RANGE,48).add(Attributes.KNOCKBACK_RESISTANCE,.55);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.3,true){@Override public boolean canUse(){return eclipsed()&&super.canUse();}@Override public boolean canContinueToUse(){return eclipsed()&&super.canContinueToUse();}});goalSelector.addGoal(2,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(3,new WaterAvoidingRandomStrollGoal(this,.7));}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){if(h!=InteractionHand.MAIN_HAND||!p.getItemInHand(h).isEmpty()||eclipsed())return InteractionResult.PASS;if(level() instanceof ServerLevel l&&speech==0){speech=100;String[] lines={"Ho un sogno. Nulla mi distogliera' da esso.","Ogni uomo deve trovare il proprio cammino.","Un giorno, avro' il mio regno."};NpcDialogue.say(l,Component.literal("Griffith: "+lines[random.nextInt(lines.length)]));}return InteractionResult.sidedSuccess(level().isClientSide);}
    @Override public void tick(){super.tick();if(speech>0)speech--;if(slash>0)slash--;if(!(level() instanceof ServerLevel l))return;
        boolean active=Eclipse.active(l);
        if(active!=eclipsed()){entityData.set(ECLIPSED,active);setAggressive(active);getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(active?36:24);getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(active?.40:.31);
            if(active){NpcDialogue.say(l,Component.literal("Griffith: Io sacrifico.").withStyle(net.minecraft.ChatFormatting.DARK_RED));l.sendParticles(ParticleTypes.SMOKE,getX(),getY()+1,getZ(),65,.6,.9,.6,.08);playSound(SoundEvents.WITHER_AMBIENT,1,.7f);}
            else{setTarget(null);getNavigation().stop();NpcDialogue.say(l,Component.literal("Griffith: L'eclissi e' terminata."));}
        }
        if(!active){if(getTarget()!=null)setTarget(null);return;}
        if(tickCount%10==0){LivingEntity t=l.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(40),e->e.isAlive()&&(e instanceof Guts||e instanceof Player p&&!p.isCreative()&&!p.isSpectator())).stream().min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(null);setTarget(t);}
        if(tickCount%12==0)l.sendParticles(ParticleTypes.CRIMSON_SPORE,getX(),getY()+1,getZ(),5,.45,.7,.45,.03);
    }
    @Override public boolean doHurtTarget(Entity e){if(!eclipsed())return false;boolean hit=super.doHurtTarget(e);if(hit&&level() instanceof ServerLevel l){l.broadcastEntityEvent(this,(byte)95);if(e instanceof LivingEntity v)v.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,100,1));l.sendParticles(ParticleTypes.SWEEP_ATTACK,e.getX(),e.getY()+1,e.getZ(),3,.3,.3,.3,0);playSound(SoundEvents.PLAYER_ATTACK_SWEEP,1,.7f);}return hit;}
    @Override public void handleEntityEvent(byte id){if(id==95){slash=14;return;}super.handleEntityEvent(id);}
    public float slashing(){return slash<=0?0:(float)Math.sin(slash*Math.PI/14);}
}''')
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if((Eclipse.active(l)||p.getRandom().nextInt(24)==0)&&l.getEntitiesOfClass(Griffith.class,p.getBoundingBox().inflate(96)).isEmpty()){
            long day=Eclipse.day(l);var data=Noctis.data(p);
            if(!Eclipse.active(l)||!data.contains("GriffithEclipseDay")||data.getLong("GriffithEclipseDay")!=day){
                BlockPos q=Eclipse.spot(p,12,24);if(q!=null){Griffith g=Noctis.GRIFFITH.get().create(l);if(g!=null){g.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(g)&&l.addFreshEntity(g)&&Eclipse.active(l))data.putLong("GriffithEclipseDay",day);}}
            }
        }''')
# New standalone mesh: plated shoulders, curled hair, articulated locks, sword.
N=128;S=8;W=N*S;cx=cy=rh=0;islands=[];lines=[]
def cube(x,y,z,w,h,d,m):
    global cx,cy,rh
    ww=2*(w+d);hh=h+d
    if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
    u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N
    for X,Y,A,B,f in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((X,Y,A,B,m,f))
    return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
def part(var,parent,name,pos,rot,boxes):lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
part('b','r','body',(0,0,0),(0,0,0),[(-4,-1,-2.5,8,8,5,'steel'),(-3,7,-2,6,4,4,'steel'),(-4,9,-2.5,8,2,5,'belt')])
part('h','r','head',(0,-1,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face'),(-4,-8,-3.5,8,2,7,'hair')])
for i in range(7):
    part('bang'+str(i),'h','bang'+str(i),(-3+i, -7.7,-3.5),(0,0,(i-3)*.13),[(-.6,0,-.5,1,3+i%2,1,'hair')])
    part('back'+str(i),'h','back'+str(i),(-3+i,-6,2.8),(0,0,(i-3)*.06),[(-.6,0,-.5,2,7+i%3,2,'hair')])
    part('tip'+str(i),'back'+str(i),'tip',(0,7+i%3,0),(0,0,.22 if i%2 else -.22),[(-.6,0,-.5,1,4,2,'hair')])
for i,sgn in enumerate((-1,1)):
    part('lock'+str(i),'h','lock'+str(i),(sgn*3.5,-6,-.2),(0,0,sgn*.1),[(-1,0,-1,2,7,3,'hair')])
    part('curl'+str(i),'lock'+str(i),'curl',(0,6,0),(0,0,-sgn*.3),[(-.8,0,-.8,2,5,2,'hair')])
    part('a'+str(i),'r','arm'+str(i),(sgn*4.8,0,0),(0,0,-sgn*.1),[(-2,-1,-2,4,4,4,'steel'),(-1.8,3,-1.8,3,4,3,'steel'),(-1.5,7,-1.5,3,4,3,'steel')])
    part('pad'+str(i),'a'+str(i),'pad',(0,0,0),(0,0,-sgn*.14),[(-2.5,-2,-2.5,5,3,5,'steel'),(-2.3,1,-2,4,2,4,'steel')])
    part('l'+str(i),'r','leg'+str(i),(sgn*2,11,0),(0,0,0),[(-2,0,-2,4,7,4,'steel'),(-1.5,7,-1.5,3,5,3,'steel'),(-2,11,-3,4,2,5,'steel')])
part('sword','a1','sword',(0,10,-1),(-.2,0,0),[(-.5,0,-.5,1,3,1,'belt'),(-2,3,-.5,4,1,1,'steel'),(-.5,4,-.5,1,13,1,'steel')])
write('GriffithClient.java','''package it.noctis.magic;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public class GriffithClient{
    static final ModelLayerLocation L=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"griffith"),"main");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L,GriffithClient::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.GRIFFITH.get(),Renderer::new);}
    static LayerDefinition mesh(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
'''+ '\n'.join(lines)+'''
        return LayerDefinition.create(m,128,128);}
    static class Model extends EntityModel<Griffith>{
        final ModelPart r,h,b;Model(ModelPart r){this.r=r;h=r.getChild("head");b=r.getChild("body");}
        @Override public void setupAnim(Griffith e,float limb,float amount,float age,float yaw,float pitch){float hit=e.slashing();h.yRot=yaw*.01745f;h.xRot=pitch*.01745f;b.yRot=hit*.35f;
            for(int i=0;i<2;i++){float w=(float)Math.cos(limb*.6662+i*Math.PI)*amount;r.getChild("leg"+i).xRot=w*.7f;r.getChild("arm"+i).xRot=-w*.7f-(i==1?hit*1.8f:0);h.getChild("lock"+i).xRot=amount*.24f+(float)Math.sin(age*.13+i)*.10f;h.getChild("lock"+i).getChild("curl").zRot=(i==0?.3f:-.3f)+(float)Math.sin(age*.15+i)*.12f;}
            for(int i=0;i<7;i++){ModelPart p=h.getChild("back"+i);p.xRot=amount*.22f+(float)Math.sin(age*.12+i*.5)*.09f;p.getChild("tip").xRot=(float)Math.sin(age*.16+i)*.12f;}}
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r1,float g,float b1,float a){r.render(p,v,light,overlay,r1,g,b1,a);}
    }
    static class Renderer extends MobRenderer<Griffith,Model>{Renderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(L)),.35f);}@Override public ResourceLocation getTextureLocation(Griffith e){return new ResourceLocation(Noctis.ID,"textures/entity/griffith.png");}}
}''')
pix=bytearray(W*W*4)
for x,y,w,h,m,face in islands:
    for j in range(h*S):
        v=(j+.5)/(h*S)
        for i in range(w*S):
            u=(i+.5)/(w*S);edge=min(u,v,1-u,1-v)
            if m=='steel':
                a=.50+.48*math.exp(-((u-.36)/.25)**2)+.10*math.sin(v*math.pi);a*=.58 if edge<.045 else 1
                c=(int(210*a),int(220*a),int(235*a))
                if edge<.14 and (u<.14 or u>.86) and abs(v-.18)<.035:c=(65,72,91)
            elif m=='hair':
                a=.77+.21*math.sin(u*32+math.sin(v*8)*1.5)**2;c=(int(246*a),int(243*a),int(255*a))
            elif m=='belt':c=(73,57,52) if u<.85 else (175,180,195)
            else:
                c=(int(238-20*abs(u-.5)),int(209-25*abs(u-.5)),int(185-25*abs(u-.5)))
                if face=='front':
                    for ex in (.27,.73):
                        dx=(u-ex)/.20;dy=(v-.46)/.14
                        if dx*dx+dy*dy<1:c=(62,55,70)
                        if dx*dx+dy*dy<.78:c=(248,245,240)
                        if abs(dx)<.45 and abs(dy)<.82:c=(83,131,190)
                        if abs(dx)<.19 and abs(dy)<.75:c=(22,35,57)
                        if (dx+.14)**2+(dy+.3)**2<.065:c=(255,255,255)
                        if abs(dx)<.9 and abs(v-.26)<.024:c=(119,110,132)
                    if .40<u<.62 and abs(v-.79)<.02:c=(148,83,90)
            off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,z)) for z in c],255))
png(assets/'textures/entity/griffith.png',W,W,pix)
dump(assets/'models/item/griffith_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
# Original pixel-art cans with claw motif, aluminum lid and individual flavor colors.
for n,label,base,mark in flavors:
    W=32;pix=bytearray(W*W*4)
    for y in range(2,30):
        for x in range(8,24):
            if (y in (2,29) and x in (8,23)):continue
            a=.72+.28*math.sin((x-8)/15*math.pi)
            c=tuple(int(z*a) for z in base)
            if y<5 or y>27:c=(177,185,192) if x not in (8,23) else (94,101,111)
            elif 9<=y<=21:
                for t in (11,15,19):
                    if abs(x-t-((y-9)//4)%2)<1.2:c=mark
            elif y in (23,24) and 11<x<21:c=mark
            pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
    name='monster_'+n;png(assets/'textures/item'/f'{name}.png',W,W,pix);dump(assets/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'noctismagic:item/'+name}})
# Equipment item icons drawn with simple silhouettes, custom white/silver armor layers.
patterns={'helmet':['MMM','M M'],'chestplate':['M M','MMM','MMM'],'leggings':['MMM','M M','M M'],'boots':['M M','M M'],'sword':[' M ',' M ',' S '],'axe':['MM ','MS ',' S '],'pickaxe':['MMM',' S ',' S '],'shovel':[' M ',' S ',' S ']}
for name,pat in patterns.items():
    dump(res/'data/noctismagic/recipes'/f'ultra_white_{name}.json',{'type':'minecraft:crafting_shaped','pattern':pat,'key':{a:v for a,v in {'M':{'item':'noctismagic:monster_ultra_white'},'S':{'item':'minecraft:stick'}}.items() if any(a in row for row in pat)},'result':{'item':'noctismagic:ultra_white_'+name}})
    W=32;pix=bytearray(W*W*4)
    # draw based on item shape in 3x3 grid, rotate sword/tools naturally in hand by handheld model.
    for row,line in enumerate(pat):
        for col,ch in enumerate(line):
            if ch==' ':continue
            for y in range(3+row*8,11+row*8):
                for x in range(3+col*8,11+col*8):
                    c=(99,80,67) if ch=='S' else (224,232,240) if x%8 in (4,5,6) else (147,162,177)
                    pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
    n='ultra_white_'+name;png(assets/'textures/item'/f'{n}.png',W,W,pix);dump(assets/'models/item'/f'{n}.json',{'parent':'minecraft:item/generated' if name in dict(gear) else 'minecraft:item/handheld','textures':{'layer0':'noctismagic:item/'+n}})
for layer in (1,2):
    W=128;H=64;pix=bytearray(W*H*4)
    # Vanilla armor UV: transparent areas remain empty; covered cuboids use bright metallic trim.
    regions=[(0,0,64,32),(32,32,48,24),(80,32,48,24),(0,32,32,24)]
    for X,Y,A,B in regions:
        for y in range(Y,min(H,Y+B)):
            for x in range(X,min(W,X+A)):
                g=.78+.20*math.sin((x%16)/15*math.pi);c=(int(227*g),int(235*g),int(243*g))
                if y%16 in (0,15):c=(121,140,155)
                if x%16 in (6,9) and y%16 in range(5,12):c=(112,130,144)
                pix[(y*W+x)*4:(y*W+x)*4+4]=bytes((*c,255))
    png(assets/'textures/models/armor'/f'ultra_white_layer_{layer}.png',W,H,pix)
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));d['entity.noctismagic.griffith']='Griffith';d['item.noctismagic.griffith_spawn_egg']='Uovo generatore: Griffith' if lang=='it_it' else 'Griffith Spawn Egg'
    for n,label,*_ in flavors:d['item.noctismagic.monster_'+n]='Monster Energy - '+label
    for n,it,en in [('helmet','Elmo','Helmet'),('chestplate','Corazza','Chestplate'),('leggings','Gambali','Leggings'),('boots','Stivali','Boots'),('sword','Spada','Sword'),('axe','Ascia','Axe'),('pickaxe','Piccone','Pickaxe'),('shovel','Pala','Shovel')]:d['item.noctismagic.ultra_white_'+n]=(it if lang=='it_it' else en)+' Ultra White'
    dump(p,d)
print('Griffith, seven energy drink variants and Ultra White equipment installed')
