"""1.0.9: detailed Valdracula interiors and three Stand users."""
from pathlib import Path
import sys,json,struct,zlib,math
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,a,b):
    p=java/name;s=p.read_text(encoding='utf-8');assert a in s,(name,a[:100]);p.write_text(s.replace(a,b,1),encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
# Replace generic repeated rooms with individual architectural schemes.
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static void room(');b=s.index('    static void floorAt(',a)
s=s[:a]+'''    static void rug(Plan p,int x1,int z1,int x2,int z2,int y,Block middle,Block edge){
        for(int x=x1;x<=x2;x++)for(int z=z1;z<=z2;z++)p.put(x,y,z,x==x1||x==x2||z==z1||z==z2?edge:middle);
    }
    static void chandelier(Plan p,int x,int y,int z){
        p.box(x,y+1,z,x,y+4,z,Blocks.CHAIN);p.put(x,y,z,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
        for(int i=-2;i<=2;i++){p.put(x+i,y-1,z,Blocks.DARK_OAK_SLAB);p.put(x,y-1,z+i,Blocks.DARK_OAK_SLAB);}
        for(int i:new int[]{-2,2}){p.lantern(x+i,y,z);p.lantern(x,y,z+i);}
    }
    static void fireplace(Plan p,int x,int y,int z){
        p.box(x-2,y+1,z,x+2,y+5,z+1,TRIM);
        p.box(x-1,y+1,z,x+1,y+2,z,Blocks.AIR);
        p.put(x,y+1,z+1,Blocks.SHROOMLIGHT);p.box(x-3,y+3,z-1,x+3,y+3,z,Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);
        p.box(x-1,y+5,z,x+1,y+8,z+1,EDGE);p.put(x,y+4,z-1,Blocks.CHISELED_STONE_BRICKS);
    }
    static void room(Plan p,int x1,int z1,int x2,int z2,int y,int type){
        int cx=(x1+x2)/2,cz=(z1+z2)/2;
        // each chamber has its own floor inlay, cornice and stone arch entrance
        Block[] floors={Blocks.DARK_OAK_PLANKS,Blocks.POLISHED_DIORITE,Blocks.SPRUCE_PLANKS,Blocks.POLISHED_BLACKSTONE,Blocks.CALCITE,Blocks.DARK_OAK_PLANKS,Blocks.POLISHED_ANDESITE,Blocks.DEEPSLATE_TILES};
        p.box(x1,y,z1,x2,y,z2,floors[type]);p.ring(x1,y,z1,x2,z2,EDGE);
        p.box(x1,y+1,z1,x2,y+10,z1,STONE);p.box(x1,y+1,z2,x2,y+10,z2,STONE);
        opening(p,cx,y+1,z1,2,7,false,false);opening(p,cx,y+1,z2,2,7,false,false);
        for(int z=z1+3;z<z2;z+=6){p.put(x1,y+5,z,Blocks.CHISELED_STONE_BRICKS);p.lantern(x1+1,y+5,z);p.put(x2,y+5,z,Blocks.CHISELED_STONE_BRICKS);p.lantern(x2-1,y+5,z);}
        for(int z=z1+6;z<z2;z+=10)chandelier(p,cx,y+6,z);
        if(type==0){ // two-storey library, lecterns and reading alcoves
            for(int z=z1+2;z<z2-1;z++){p.box(x1+1,y+1,z,x1+1,y+8,z,Blocks.BOOKSHELF);p.box(x2-1,y+1,z,x2-1,y+8,z,Blocks.BOOKSHELF);}
            for(int z=z1+4;z<z2-3;z+=7){p.box(cx-1,y+1,z,cx+1,y+1,z,Blocks.DARK_OAK_FENCE);p.box(cx-1,y+2,z,cx+1,y+2,z,Blocks.DARK_OAK_SLAB);p.put(cx,y+3,z,Blocks.LECTERN);p.stair(cx,y+1,z+2,Blocks.DARK_OAK_STAIRS,Direction.SOUTH);}
            p.box(x1+2,y+5,z1+1,x1+3,y+5,z2-1,Blocks.DARK_OAK_PLANKS);p.box(x2-3,y+5,z1+1,x2-2,y+5,z2-1,Blocks.DARK_OAK_PLANKS);
            for(int z=z1+2;z<z2;z++){p.put(x1+3,y+6,z,Blocks.DARK_OAK_FENCE);p.put(x2-3,y+6,z,Blocks.DARK_OAK_FENCE);}
            for(int k=0;k<5;k++)p.stair(x1+2,y+1+k,z1+2+k,Blocks.DARK_OAK_STAIRS,Direction.SOUTH);
        }else if(type==1){ // banquet hall
            rug(p,cx-3,z1+3,cx+3,z2-3,y+1,Blocks.RED_CARPET,Blocks.BLACK_CARPET);
            p.box(cx-1,y+1,z1+4,cx+1,y+1,z2-4,Blocks.DARK_OAK_PLANKS);p.box(cx-2,y+2,z1+4,cx+2,y+2,z2-4,Blocks.DARK_OAK_SLAB);
            for(int z=z1+4;z<=z2-4;z+=3){p.stair(cx-3,y+1,z,Blocks.DARK_OAK_STAIRS,Direction.WEST);p.stair(cx+3,y+1,z,Blocks.DARK_OAK_STAIRS,Direction.EAST);p.put(cx,y+3,z,Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.LIT,true));}
            fireplace(p,cx,y,z2-2);
        }else if(type==2){ // portrait gallery and sculptural niches
            rug(p,cx-2,z1+2,cx+2,z2-2,y+1,Blocks.PURPLE_CARPET,Blocks.BLACK_CARPET);
            for(int z=z1+4;z<z2-2;z+=7)for(int x:new int[]{x1+2,x2-2}){statue(p,x,y+1,z);p.box(x-1,y+7,z-1,x+1,y+7,z+1,EDGE);}
            for(int z=z1+5;z<z2-1;z+=7){p.box(x1+1,y+2,z-1,x1+1,y+5,z+1,Blocks.GOLD_BLOCK);p.box(x1+2,y+3,z,x1+2,y+4,z,Blocks.PURPLE_GLAZED_TERRACOTTA);}
        }else if(type==3){ // gothic bedroom suite and canopy bed
            rug(p,cx-3,z1+4,cx+3,z2-4,y+1,Blocks.RED_CARPET,Blocks.BLACK_CARPET);
            p.box(cx-2,y+1,cz-3,cx+2,y+1,cz+3,Blocks.DARK_OAK_PLANKS);
            p.box(cx-1,y+2,cz-2,cx+1,y+2,cz+2,Blocks.RED_WOOL);p.box(cx-1,y+2,cz+2,cx+1,y+2,cz+3,Blocks.WHITE_WOOL);
            for(int x:new int[]{cx-2,cx+2})for(int z:new int[]{cz-3,cz+3})p.box(x,y+2,z,x,y+7,z,Blocks.DARK_OAK_FENCE);
            p.box(cx-3,y+7,cz-4,cx+3,y+7,cz+4,Blocks.RED_WOOL);p.ring(cx-3,y+8,cz-4,cx+3,cz+4,TRIM);
            p.box(x1+1,y+1,z1+3,x1+2,y+5,z1+6,Blocks.DARK_OAK_PLANKS);p.put(x2-2,y+2,z1+4,Blocks.FLOWER_POT);fireplace(p,cx,y,z2-2);
        }else if(type==4){ // alchemy laboratory, empty decorative equipment
            for(int z=z1+3;z<z2-2;z+=5){p.put(x1+2,y+1,z,Blocks.CAULDRON);p.put(x2-2,y+1,z,Blocks.DARK_OAK_PLANKS);p.put(x2-2,y+2,z,Blocks.BREWING_STAND);p.put(cx,y+1,z,Blocks.AMETHYST_BLOCK);}
            for(int z=z1+2;z<z2;z++)p.box(x1+1,y+4,z,x1+1,y+5,z,Blocks.BOOKSHELF);
            p.box(cx-1,y+1,cz-2,cx+1,y+1,cz+2,Blocks.POLISHED_ANDESITE);p.put(cx,y+2,cz,Blocks.AMETHYST_CLUSTER);
        }else if(type==5){ // music room with organ and harpsichord
            rug(p,cx-3,z1+3,cx+3,z2-3,y+1,Blocks.BLUE_CARPET,Blocks.BLACK_CARPET);
            for(int k=-4;k<=4;k++){p.box(cx+k,y+2,z2-2,cx+k,y+8-Math.abs(k),z2-2,Blocks.IRON_BARS);p.put(cx+k,y+1,z2-3,k%2==0?Blocks.QUARTZ_BLOCK:Blocks.BLACKSTONE);}
            p.box(cx-3,y+1,cz,cx+3,y+1,cz+2,Blocks.DARK_OAK_PLANKS);for(int k=-3;k<=3;k++)p.put(cx+k,y+2,cz,k%2==0?Blocks.QUARTZ_SLAB:Blocks.BLACKSTONE);p.stair(cx,y+1,cz-2,Blocks.DARK_OAK_STAIRS,Direction.NORTH);
        }else if(type==6){ // observatory with astral mosaic and miniature orrery
            for(int x=x1+1;x<x2;x++)for(int z=z1+1;z<z2;z++){int d=Math.abs(x-cx)+Math.abs(z-cz);p.put(x,y,z,d==4||d==7?Blocks.GOLD_BLOCK:d%3==0?Blocks.BLUE_TERRACOTTA:Blocks.POLISHED_BLACKSTONE);}
            p.box(cx,y+1,cz,cx,y+4,cz,Blocks.QUARTZ_PILLAR);p.put(cx,y+5,cz,Blocks.GOLD_BLOCK);for(int k=-3;k<=3;k++){p.put(cx+k,y+4,cz,Blocks.IRON_BARS);p.put(cx,y+4,cz+k,Blocks.IRON_BARS);}p.put(cx+3,y+5,cz,Blocks.LAPIS_BLOCK);p.put(cx,y+5,cz-3,Blocks.AMETHYST_BLOCK);
            for(int z=z1+4;z<z2;z+=7)p.put(x1+2,y+1,z,Blocks.LECTERN);
        }else{ // vampire memorial, empty ceremonial sarcophagi
            rug(p,cx-2,z1+2,cx+2,z2-2,y+1,Blocks.BLACK_CARPET,Blocks.RED_CARPET);
            for(int z=z1+4;z<z2-2;z+=7)for(int x:new int[]{x1+2,x2-2}){p.box(x-1,y+1,z-1,x+1,y+1,z+2,TRIM);p.box(x-1,y+2,z,x+1,y+2,z+1,Blocks.POLISHED_BLACKSTONE_SLAB);p.put(x,y+2,z+1,EDGE);p.put(x,y+3,z-1,Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.LIT,true));}
            statue(p,cx,y+1,z2-3);
        }
    }
'''+s[b:]
s=s.replace('room(p,60,35,71,58,0,1);room(p,60,59,71,86,0,2);','room(p,60,35,71,58,0,2);room(p,60,59,71,86,0,3);')
s=s.replace('room(p,19,35,30,58,12,2);room(p,19,59,30,86,12,0);','room(p,19,35,30,58,12,4);room(p,19,59,30,86,12,5);')
s=s.replace('room(p,60,35,71,58,12,2);room(p,60,59,71,86,12,2);','room(p,60,35,71,58,12,6);room(p,60,59,71,86,12,7);')
a='        // Chapel annex at rear'
s=s.replace(a,'''        // Upper gallery accesses and central bridge; avoid blocking stair exits.
        for(int x=31;x<=35;x++)p.box(x,12,43,x,12,46,TRIM);
        for(int x=55;x<=59;x++)p.box(x,12,43,x,12,46,TRIM);
        for(int x=35;x<=55;x++)p.box(x,12,69,x,12,71,TRIM);
        for(int x=38;x<=52;x++){p.put(x,13,69,Blocks.IRON_BARS);p.put(x,13,71,Blocks.IRON_BARS);}
        // additional ornamental arches over the throne hall
        for(int z=43;z<78;z+=9){for(int k=0;k<=12;k++){p.put(33+k,25+k/2,z,LIGHT);p.put(57-k,25+k/2,z,LIGHT);}chandelier(p,45,22,z);}
        // Formal courtyards: two dry fountains and geometrical hedges.
        for(int x:new int[]{22,68}){p.box(x-5,0,19,x+5,0,29,Blocks.POLISHED_DIORITE);p.ring(x-4,1,20,x+4,28,TRIM);p.box(x-1,1,23,x+1,3,25,EDGE);p.put(x,4,24,Blocks.SEA_LANTERN);for(int z=17;z<=30;z+=13)for(int i=-5;i<=5;i++)p.put(x+i,1,z,Blocks.AZALEA_LEAVES);}
'''+a,1)
p.write_text(s,encoding='utf-8')
# Six types, three peaceful characters and their retaliation-only stands.
ids=['jotaro','bucciarati','giorno','star_platinum','sticky_fingers','gold_experience']
regs=[n.upper() for n in ids]
colors=[('0x202036','0xd6b450'),('0xeae5d9','0x263348'),('0xc62a89','0xe9bb52'),('0x6848a7','0x49bfa8'),('0x629fc5','0xeae4d9'),('0xe3bb37','0x7850a4')]
decl=''
for i,(n,r,(a,b)) in enumerate(zip(ids,regs,colors)):
    decl+=f'public static final RegistryObject<EntityType<JojoMob>> {r}=ENTITIES.register("{n}",()->EntityType.Builder.<JojoMob>of(JojoMob::new,MobCategory.CREATURE).sized(.7f,{2.05 if i<3 else 2.35}f).clientTrackingRange(10).build(ID+":{n}"));\n    '
    if i<3:decl+=f'public static final RegistryObject<Item> {r}_EGG=ITEMS.register("{n}_spawn_egg",()->new ForgeSpawnEggItem({r},{a},{b},new Item.Properties()));\n    '
anchor='public static final RegistryObject<Item> CATHEDRAL_EGG='
edit('Noctis.java',anchor,decl+anchor)
anchor='e.put(SCRAP_THIEF.get(),ScrapThief.attributes().build());'
edit('Noctis.java',anchor,''.join(f'e.put({r}.get(),JojoMob.attributes({str(i>=3).lower()}).build());' for i,r in enumerate(regs))+anchor)
anchor='e.accept(CATHEDRAL_EGG.get());'
edit('Noctis.java',anchor,anchor+''.join(f'e.accept({r}_EGG.get());' for r in regs[:3]))
write('JojoMob.java','''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.*;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
public class JojoMob extends PathfinderMob{
    private UUID owner,aggressor,activeStand;
    private long expires,callAfter;
    private int punch,ability,dialogue;
    public JojoMob(EntityType<? extends PathfinderMob> t,Level l){super(t,l);}
    public int variant(){var t=getType();return t==Noctis.JOTARO.get()?0:t==Noctis.BUCCIARATI.get()?1:t==Noctis.GIORNO.get()?2:t==Noctis.STAR_PLATINUM.get()?3:t==Noctis.STICKY_FINGERS.get()?4:5;}
    public boolean stand(){return variant()>=3;}
    static final String[] CALL={"Star Platinum!","Sticky Fingers!","Gold Experience!"};
    static final String[] TALK={"Yare yare daze.","Arrivederci. Non cercare guai.","Io, Giorno Giovanna, ho un sogno."};
    public static AttributeSupplier.Builder attributes(boolean stand){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,stand?120:60).add(Attributes.ARMOR,stand?12:5).add(Attributes.MOVEMENT_SPEED,stand?.42:.25).add(Attributes.ATTACK_DAMAGE,stand?16:1).add(Attributes.FOLLOW_RANGE,48).add(Attributes.KNOCKBACK_RESISTANCE,stand?.8:.1);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(1,new MeleeAttackGoal(this,1.4,true){
        @Override public boolean canUse(){return stand()&&super.canUse();}
        @Override public boolean canContinueToUse(){return stand()&&super.canContinueToUse();}
    });goalSelector.addGoal(3,new LookAtPlayerGoal(this,Player.class,8));goalSelector.addGoal(4,new WaterAvoidingRandomStrollGoal(this,.6){@Override public boolean canUse(){return !stand()&&super.canUse();}});}
    @Override public boolean hurt(DamageSource source,float damage){
        if(!(level() instanceof ServerLevel l)||stand())return super.hurt(source,damage);
        if(source.getEntity() instanceof LivingEntity attacker&&attacker!=this&&!(attacker instanceof JojoMob)&&(!(attacker instanceof Player p)||!p.isCreative()&&!p.isSpectator())){
            if(activeStand!=null&&l.getEntity(activeStand) instanceof JojoMob st&&st.isAlive()){st.aggressor=attacker.getUUID();st.setTarget(attacker);st.expires=l.getGameTime()+600;return false;}
            if(l.getGameTime()>=callAfter){
                JojoMob st=(variant()==0?Noctis.STAR_PLATINUM.get():variant()==1?Noctis.STICKY_FINGERS.get():Noctis.GOLD_EXPERIENCE.get()).create(l);
                if(st!=null){st.moveTo(getX(),getY(),getZ());st.owner=getUUID();st.aggressor=attacker.getUUID();st.expires=l.getGameTime()+600;st.setTarget(attacker);
                    if(l.addFreshEntity(st)){activeStand=st.getUUID();callAfter=l.getGameTime()+100;NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+CALL[variant()]));l.sendParticles(ParticleTypes.ENCHANT,getX(),getY()+1,getZ(),65,.7,.8,.7,.2);return false;}}
            }
        }
        return super.hurt(source,damage);
    }
    @Override public boolean doHurtTarget(Entity target){
        if(!stand()||aggressor==null||!aggressor.equals(target.getUUID())||!(target instanceof LivingEntity victim))return false;
        boolean hit=super.doHurtTarget(target);
        if(hit&&level() instanceof ServerLevel l){
            l.broadcastEntityEvent(this,(byte)82);
            l.sendParticles(ParticleTypes.CRIT,target.getX(),target.getY()+1,target.getZ(),12,.35,.55,.35,.2);
            if(ability<=0){
                ability=100;
                if(variant()==3){victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,50,5));victim.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,50,1));NpcDialogue.say(l,Component.literal("Star Platinum: ORA ORA ORA!"));}
                else if(variant()==4){victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,80,2));NpcDialogue.say(l,Component.literal("Sticky Fingers: ARI ARI ARI!"));l.sendParticles(ParticleTypes.END_ROD,target.getX(),target.getY()+1,target.getZ(),20,.4,.5,.4,.07);}
                else{victim.addEffect(new MobEffectInstance(MobEffects.CONFUSION,100,0));if(l.getEntity(owner) instanceof LivingEntity master)master.heal(8);NpcDialogue.say(l,Component.literal("Gold Experience: MUDA MUDA MUDA!"));l.sendParticles(ParticleTypes.HAPPY_VILLAGER,getX(),getY()+1,getZ(),22,.4,.5,.4,.1);}
            }
            playSound(SoundEvents.PLAYER_ATTACK_STRONG,1,1.15f);
        }
        return hit;
    }
    @Override public void tick(){super.tick();if(punch>0)punch--;if(ability>0)ability--;if(dialogue>0)dialogue--;
        if(!(level() instanceof ServerLevel l)||!stand())return;
        if(owner==null||aggressor==null||l.getGameTime()>=expires||!(l.getEntity(owner) instanceof JojoMob master)||!master.isAlive()||!(l.getEntity(aggressor) instanceof LivingEntity victim)||!victim.isAlive()||victim.distanceToSqr(master)>2304||(victim instanceof Player p&&(p.isCreative()||p.isSpectator()))){discard();return;}
        if(getTarget()!=victim)setTarget(victim);
        if(distanceToSqr(victim)>144&&distanceToSqr(master)<2304){Vec3 v=victim.position().subtract(position()).normalize().scale(.25);setDeltaMovement(getDeltaMovement().add(v.x,0,v.z));}
        if(tickCount%8==0)l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+1,getZ(),2,.35,.65,.35,0);
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){if(!stand()&&h==InteractionHand.MAIN_HAND&&p.getItemInHand(h).isEmpty()){if(level() instanceof ServerLevel l&&dialogue<=0){dialogue=100;NpcDialogue.say(l,Component.literal(getDisplayName().getString()+": "+TALK[variant()]));}return InteractionResult.sidedSuccess(level().isClientSide);}return super.mobInteract(p,h);}
    @Override public void handleEntityEvent(byte id){if(id==82){punch=10;return;}super.handleEntityEvent(id);}
    public float punchPose(){return punch>0?(float)Math.sin(punch*Math.PI/10):0;}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(owner!=null)t.putUUID("Owner",owner);if(aggressor!=null)t.putUUID("Aggressor",aggressor);if(activeStand!=null)t.putUUID("Stand",activeStand);t.putLong("Expires",expires);t.putLong("CallAfter",callAfter);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;aggressor=t.hasUUID("Aggressor")?t.getUUID("Aggressor"):null;activeStand=t.hasUUID("Stand")?t.getUUID("Stand"):null;expires=t.getLong("Expires");callAfter=t.getLong("CallAfter");}
}''')
# Rare world encounters, with no automatic placement inside the monument.
edit('NightGuests.java','if(l.dimension()!=Level.OVERWORLD)return;','''if(l.dimension()!=Level.OVERWORLD)return;
        if(!p.isCreative()&&p.getRandom().nextInt(16)==0&&l.getEntitiesOfClass(JojoMob.class,p.getBoundingBox().inflate(64),m->!m.stand()).isEmpty()){
            BlockPos q=Eclipse.spot(p,12,24);if(q!=null){int k=p.getRandom().nextInt(3);JojoMob j=(k==0?Noctis.JOTARO.get():k==1?Noctis.BUCCIARATI.get():Noctis.GIORNO.get()).create(l);if(j!=null){j.moveTo(q.getX()+.5,q.getY(),q.getZ()+.5);if(l.noCollision(j))l.addFreshEntity(j);}}
        }''')
# Separate silhouette geometry, six atlases, individual ornament UVs.
N=128;S=4;W=N*S
models=[]
for k in range(6):
    cx=cy=rh=0;islands=[];lines=[]
    def cube(x,y,z,w,h,d,mat):
        global cx,cy,rh
        ww=2*(w+d);hh=h+d
        if cx+ww+1>N:cx=0;cy+=rh+1;rh=0
        u,v=cx,cy;cx+=ww+1;rh=max(rh,hh);assert v+hh<=N,(k,mat,u,v)
        for fx,fy,fw,fh,face in [(u+d,v,w,d,'top'),(u+d+w,v,w,d,'bottom'),(u,v+d,d,h,'right'),(u+d,v+d,w,h,'front'),(u+d+w,v+d,d,h,'left'),(u+2*d+w,v+d,w,h,'back')]:islands.append((fx,fy,fw,fh,mat,face))
        return f'.texOffs({u},{v}).addBox('+','.join(str(float(n))+'f' for n in (x,y,z,w,h,d))+')'
    def part(var,parent,name,pos,rot,boxes):
        lines.append(f'        PartDefinition {var}={parent}.addOrReplaceChild("{name}",CubeListBuilder.create()'+''.join(cube(*b) for b in boxes)+',PartPose.offsetAndRotation('+','.join(str(float(n))+'f' for n in (*pos,*rot))+'));')
    part('b','r','body',(0,0,0),(0,0,0),[(-4,0,-2.5,8,7,5,'suit'),(-3,7,-2,6,5,4,'suit')])
    part('h','r','head',(0,0,0),(0,0,0),[(-3.5,-7,-3.5,7,7,7,'face')])
    for i,side in enumerate((-1,1)):
        part('arm'+str(i),'r','arm'+str(i),(side*5,0,0),(0,0,-side*.12),[(-2,-1,-2,4,6,4,'suit'),(-1.5,5,-1.5,3,5,3,'suit'),(-1.5,10,-1.5,3,2,3,'glove')])
        part('leg'+str(i),'r','leg'+str(i),(side*2,12,0),(0,0,0),[(-2,0,-2,4,9,4,'suit'),(-2,9,-3,4,3,5,'boot')])
    if k==0:
        part('cap','h','cap',(0,-7,0),(0,0,0),[(-4,-2,-3.5,8,3,7,'hair'),(-3.5,0,-5.5,7,1,3,'hair'),(-1,-1,-4,2,2,1,'gold')])
        for i,side in enumerate((-1,1)):
            part('coat'+str(i),'b','coat'+str(i),(side*2.4,10,1),(.12,0,side*.12),[(-2,0,-2,4,11,3,'suit')])
            part('lapel'+str(i),'b','lapel'+str(i),(side*2,0,-2.8),(0,0,side*.24),[(-.5,0,-.3,1,7,1,'gold')])
        for i in range(5):part('chain'+str(i),'b','chain'+str(i),(-3+i*.7,1+i*.5,-3.3),(0,0,.25),[(-.4,-.4,-.3,1,1,1,'gold')])
    elif k==1:
        part('bob','h','bob',(0,-7,0),(0,0,0),[(-4,-1,-3.5,8,2,7,'hair'),(-4,0,2.5,8,7,2,'hair')])
        for i,side in enumerate((-1,1)):part('lock'+str(i),'h','lock'+str(i),(side*3.4,-6.4,-.5),(0,0,side*.09),[(-1,0,-1,2,7,3,'hair'),(-.5,1,-2,1,4,1,'gold')])
        part('zip','b','zip',(0,0,-2.7),(0,0,0),[(-.5,0,-.3,1,10,1,'gold')])
    elif k==2:
        part('hair','h','hair',(0,-7,0),(0,0,0),[(-4,-2,-3,8,3,6,'hair'),(-3,0,2.5,6,4,2,'hair')])
        for i in range(3):
            part('curl'+str(i),'h','curl'+str(i),(-2.5+i*2.5,-7,-3.7),(0,0,0),[(-1,-1,-1,2,3,2,'hair'),(-.5,-.5,-1.3,1,2,1,'gold')])
        part('braid','h','braid',(0,-3,3.5),(.15,0,0),[(-1,0,-1,2,7,2,'hair')])
        for i,side in enumerate((-1,1)):part('badge'+str(i),'b','badge'+str(i),(side*2.3,2,-2.9),(0,0,0),[(-.6,-.6,-.4,1,2,1,'gold')])
    else:
        # distinctive armored shoulders and helmet
        for i,side in enumerate((-1,1)):
            part('pad'+str(i),'arm'+str(i),'pad'+str(i),(0,0,0),(0,0,-side*.16),[(-2.7,-2,-2.5,5,4,5,'trim')])
            part('shin'+str(i),'leg'+str(i),'shin'+str(i),(0,5,-2),(0,0,0),[(-1.5,0,-.5,3,5,1,'trim')])
        part('belt','b','belt',(0,9,0),(0,0,0),[(-4,0,-3,8,2,6,'trim')])
        if k==3:
            part('hair','h','hair',(0,-7,0),(0,0,0),[(-4,-2,-3.5,8,3,7,'hair')])
            for i in range(5):part('spike'+str(i),'h','spike'+str(i),(-3+i*1.5,-8,1),(-.4,0,(i-2)*.25),[(-.7,-3,-.7,1,3,2,'hair')])
            part('band','h','band',(0,-6,-3.6),(0,0,0),[(-3.5,0,-.3,7,1,1,'gold')])
            part('scarf','b','scarf',(0,-1,0),(0,0,0),[(-4,0,-3,8,2,6,'trim')])
        elif k==4:
            part('helmet','h','helmet',(0,-7,0),(0,0,0),[(-4,-1,-3.5,8,2,7,'trim'),(-4,1,2,8,6,2,'trim')])
            part('visor','h','visor',(0,-5,-3.6),(0,0,0),[(-3,0,-.5,6,2,1,'gold')])
            part('zip','b','zip',(0,0,-2.8),(0,0,0),[(-.5,0,-.5,1,10,1,'gold')])
            part('pull','b','pull',(0,5,-3.2),(0,0,.2),[(-.6,0,-.5,1,3,1,'trim')])
        else:
            part('helmet','h','helmet',(0,-7,0),(0,0,0),[(-4,-1,-3.5,8,2,7,'gold'),(-4,1,2.5,8,6,2,'gold')])
            part('crest','h','crest',(0,-8,0),(0,0,0),[(-1,-3,-1,2,4,3,'trim')])
            for i,side in enumerate((-1,1)):part('antenna'+str(i),'h','antenna'+str(i),(side*3,-6,-1),(0,0,-side*.35),[(-.5,-3,-.5,1,4,1,'gold')])
            part('chest','b','chest',(0,1,-2.8),(0,0,0),[(-2,0,-.5,4,5,1,'trim')])
    models.append('    static LayerDefinition mesh'+str(k)+'(){MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();\n'+'\n'.join(lines)+'\n        return LayerDefinition.create(m,128,128);}')
    palettes=[((218,177,145),(27,26,39),(21,21,28),(199,158,55),(60,65,97)),((225,182,157),(237,232,221),(21,21,32),(207,167,73),(40,50,70)),((237,196,155),(167,37,109),(234,193,65),(249,211,80),(28,119,96)),((151,104,198),(102,67,168),(33,26,50),(220,175,60),(48,167,147)),((198,222,225),(65,139,192),(43,95,151),(226,227,224),(227,227,220)),((229,184,64),(217,163,42),(210,167,51),(246,211,90),(119,68,153))]
    skin,suit,hair,gold,trim=palettes[k]
    pix=bytearray(W*W*4)
    def mix(a,b,t):return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
    for x,y,w,h,mat,face in islands:
        for j in range(h*S):
            v=(j+.5)/(h*S)
            for i in range(w*S):
                u=(i+.5)/(w*S)
                base={'face':skin,'suit':suit,'hair':hair,'gold':gold,'trim':trim,'glove':skin if k<3 else trim,'boot':hair}.get(mat,suit)
                shade=.68+.28*math.sin(u*math.pi)+.04*math.cos(v*17)
                c=tuple(round(b*shade) for b in base)
                if mat=='face' and face=='front':
                    for ex in (.26,.74):
                        dx=(u-ex)/.19;dy=(v-.42+(u-ex)*.1)/.085
                        if abs(dx)<1 and abs(dy)<.9-.4*abs(dx):c=(27,25,39) if abs(dy)>.45 else (238,232,219)
                        if abs(dx)<.32 and abs(dy)<.5:c=(39,99,82) if k<3 else (235,212,88)
                        if abs(dx)<.13 and abs(dy)<.5:c=(25,26,32)
                        if abs(dx)<.95 and abs(v-.29+.04*dx)<.022:c=(39,30,42)
                    if abs(u-.5)<.055 and .48<v<.66:c=mix(skin,(99,62,67),.22)
                    if .38<u<.62 and abs(v-.79)<.018:c=(91,45,54)
                elif mat=='hair':c=mix(tuple(round(b*.56) for b in hair),hair,.5+.4*math.sin(u*34+v*3)**2)
                elif mat=='gold':c=mix(tuple(round(b*.5) for b in gold),gold,.3+.65*math.sin(u*math.pi))
                elif mat=='suit':
                    if min(u,1-u)<.06:c=mix(c,(19,19,27),.5)
                    if k==1 and (int(u*5)+int(v*6))%2==0 and abs((u*5)%1-.5)<.13 and abs((v*6)%1-.5)<.16:c=(27,35,51)
                    if k==2 and face=='front' and .3<u<.7 and v<.5:c=mix(c,skin,.85) if abs(u-.5)<.20*(1-v*2) else c
                    if k>=3 and abs(v-.17)<.04:c=trim
                off=((y*S+j)*W+x*S+i)*4;pix[off:off+4]=bytes((*[max(0,min(255,z)) for z in c],255))
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    raw=b''.join(b'\0'+pix[y*W*4:(y+1)*W*4] for y in range(W))
    (assets/'textures/entity'/f'{ids[k]}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
write('JojoClient.java','''package it.noctis.magic;
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
public class JojoClient{
    static final String[] N={"jotaro","bucciarati","giorno","star_platinum","sticky_fingers","gold_experience"};
    static final ModelLayerLocation[] L=new ModelLayerLocation[6];
    static{for(int i=0;i<6;i++)L[i]=new ModelLayerLocation(new ResourceLocation(Noctis.ID,N[i]),"main");}
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(L[0],JojoClient::mesh0);e.registerLayerDefinition(L[1],JojoClient::mesh1);e.registerLayerDefinition(L[2],JojoClient::mesh2);e.registerLayerDefinition(L[3],JojoClient::mesh3);e.registerLayerDefinition(L[4],JojoClient::mesh4);e.registerLayerDefinition(L[5],JojoClient::mesh5);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){
        e.registerEntityRenderer(Noctis.JOTARO.get(),c->new Renderer(c,0));e.registerEntityRenderer(Noctis.BUCCIARATI.get(),c->new Renderer(c,1));e.registerEntityRenderer(Noctis.GIORNO.get(),c->new Renderer(c,2));e.registerEntityRenderer(Noctis.STAR_PLATINUM.get(),c->new Renderer(c,3));e.registerEntityRenderer(Noctis.STICKY_FINGERS.get(),c->new Renderer(c,4));e.registerEntityRenderer(Noctis.GOLD_EXPERIENCE.get(),c->new Renderer(c,5));}
'''+ '\n'.join(models)+'''
    static class Model extends EntityModel<JojoMob>{
        final ModelPart root,head,body;final ModelPart[] arms=new ModelPart[2],legs=new ModelPart[2];
        Model(ModelPart r){root=r;head=r.getChild("head");body=r.getChild("body");for(int i=0;i<2;i++){arms[i]=r.getChild("arm"+i);legs[i]=r.getChild("leg"+i);}}
        @Override public void setupAnim(JojoMob e,float limb,float amount,float age,float yaw,float pitch){
            head.yRot=yaw*.01745f;head.xRot=pitch*.01745f;float punch=e.punchPose();body.yRot=punch*.30f;
            for(int i=0;i<2;i++){float walk=(float)Math.cos(limb*.6662+i*Math.PI)*amount;arms[i].xRot=-walk*.75f;arms[i].zRot=i==0?.12f:-.12f;legs[i].xRot=walk*.75f;}
            if(e.stand()){arms[0].xRot=-.55f-punch*1.2f;arms[1].xRot=-.55f-punch*(float)Math.abs(Math.sin(age*2))*1.4f;body.y=-.3f+(float)Math.sin(age*.18)*.2f;}
            if(e.variant()==0)for(int i=0;i<2;i++)body.getChild("coat"+i).xRot=.12f+amount*.16f+(float)Math.sin(age*.12+i)*.03f;
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    }
    static class Renderer extends MobRenderer<JojoMob,Model>{
        final int k;Renderer(EntityRendererProvider.Context c,int k){super(c,new Model(c.bakeLayer(L[k])),.4f);this.k=k;}
        @Override public ResourceLocation getTextureLocation(JojoMob e){return new ResourceLocation(Noctis.ID,"textures/entity/"+N[k]+".png");}
        @Override protected void scale(JojoMob e,PoseStack p,float partial){float a=k>=3?1.18f:1.04f;p.scale(a,a,a);}
    }
}''')
for n in ids[:3]:(assets/'models/item'/f'{n}_spawn_egg.json').write_text('{"parent":"minecraft:item/template_spawn_egg"}')
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    for i,(n,label) in enumerate(zip(ids,['Jotaro Kujo','Bruno Bucciarati','Giorno Giovanna','Star Platinum','Sticky Fingers','Gold Experience'])):
        d['entity.noctismagic.'+n]=label
        if i<3:d['item.noctismagic.'+n+'_spawn_egg']=('Uovo generatore: ' if lang=='it_it' else 'Spawn Egg: ')+label
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Valdracula unique interiors and six JoJo entities added')
