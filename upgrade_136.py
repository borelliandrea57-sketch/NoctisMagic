"""1.3.6: permanent sushi restaurant kittens, cherry garden, corrected three-line gem dialogue."""
from pathlib import Path
import sys
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic'
def edit(n,a,b):
    p=java/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8')
# Expand only the sushi building's rear garden, keeping existing width/egg dispatch.
edit('GothicEgg.java','new Plan(29,25,14,"Ristorante Sushi del Gatto di Giada")','new Plan(29,35,14,"Ristorante Sushi del Gatto di Giada")')
edit('GothicEgg.java','        p.put(3,1,20,Furniture.FRIDGE.get());p.put(25,1,20,Furniture.DISHWASHER.get());p.put(14,1,22,Blocks.CRAFTING_TABLE);p.put(16,1,22,Blocks.CAULDRON);','''        p.put(3,1,20,Furniture.FRIDGE.get());p.put(25,1,20,Furniture.DISHWASHER.get());p.put(12,1,21,Blocks.CRAFTING_TABLE);p.put(17,1,21,Blocks.CAULDRON);
        p.box(12,1,23,16,4,23,Blocks.AIR);
        // Rear sakura garden with an unobstructed central path and four full cherry trees.
        for(int x=0;x<29;x++)for(int z=24;z<35;z++){
            boolean path=x>=12&&x<=16;
            p.put(x,0,z,path?Blocks.POLISHED_ANDESITE:Blocks.GRASS_BLOCK);
            if(!path&&x>1&&x<27&&z>24&&(x*7+z*3)%4!=0)
                p.put(x,1,z,Blocks.PINK_PETALS.defaultBlockState().setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.FLOWER_AMOUNT,1+Math.floorMod(x+z,4)));
        }
        p.put(14,0,29,Blocks.CHISELED_STONE_BRICKS);
        for(int x:new int[]{5,10,19,24}){
            int z=x==5||x==24?30:28;
            p.box(x,1,z,x,5,z,Blocks.CHERRY_LOG);
            for(int dx=-3;dx<=3;dx++)for(int dz=-3;dz<=3;dz++)for(int y=4;y<=8;y++){
                if(Math.abs(dx)+Math.abs(dz)+Math.abs(y-6)<=6&&!(dx==0&&dz==0&&y<=5))
                    p.put(x+dx,y,z+dz,Blocks.CHERRY_LEAVES.defaultBlockState().setValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT,true));
            }
        }
        for(int x:new int[]{2,26})for(int z:new int[]{25,33}){p.put(x,1,z,Blocks.STONE_BRICK_WALL);p.put(x,2,z,Blocks.LANTERN);}
        for(int x:new int[]{6,22}){p.box(x-1,1,33,x+1,1,33,Blocks.CHERRY_SLAB);p.put(x,2,33,Blocks.FLOWER_POT);}
        for(int x:new int[]{4,8,20,24})p.put(x,1,2,Blocks.POTTED_CHERRY_SAPLING);
        for(int x:new int[]{5,14,23})for(int z:new int[]{8,12})p.put(x,2,z,Blocks.POTTED_CHERRY_SAPLING);''')
edit('GothicEgg.java','            if(p.w==29){','''            if(p.w==29){
                SushiCats.get(l).add(l,pos(14,0,29),forward);''')
(java/'SushiCats.java').write_text('''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.Cat;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class SushiCats extends SavedData{
    static final String HOME="NoctisSushiCatHome";
    static final int COUNT=8;
    static final String[] COATS={"tabby","black","red","siamese","british_shorthair","calico","persian","ragdoll"};
    record Restaurant(BlockPos marker,Direction front){
        BlockPos pos(int x,int y,int z){Direction right=front.getCounterClockWise();return marker.offset(right.getStepX()*(x-14)+front.getStepX()*(z-29),y,right.getStepZ()*(x-14)+front.getStepZ()*(z-29));}
    }
    final List<Restaurant> restaurants=new ArrayList<>();
    static SushiCats load(CompoundTag t){SushiCats d=new SushiCats();ListTag list=t.getList("Restaurants",10);for(int i=0;i<list.size();i++){CompoundTag n=list.getCompound(i);d.restaurants.add(new Restaurant(BlockPos.of(n.getLong("Marker")),Direction.from2DDataValue(n.getInt("Front"))));}return d;}
    @Override public CompoundTag save(CompoundTag t){ListTag list=new ListTag();for(Restaurant r:restaurants){CompoundTag n=new CompoundTag();n.putLong("Marker",r.marker.asLong());n.putInt("Front",r.front.get2DDataValue());list.add(n);}t.put("Restaurants",list);return t;}
    static SushiCats get(ServerLevel l){return l.getDataStorage().computeIfAbsent(SushiCats::load,SushiCats::new,"noctis_sushi_cats");}
    void add(ServerLevel l,BlockPos p,Direction front){Restaurant r=new Restaurant(p,front);if(!restaurants.contains(r)){restaurants.add(r);setDirty();}maintain(l,r);}
    static final int[][] SPOTS={{9,6},{19,6},{9,10},{19,10},{11,15},{17,15},{13,26},{15,31},{12,25},{16,33},{10,32},{19,32}};
    static boolean loaded(ServerLevel l,Restaurant r){
        // All chunks in the restaurant footprint, with a margin for wandering cats.
        BlockPos a=r.pos(-8,0,-8),b=r.pos(36,0,42);
        for(int x=Math.min(a.getX(),b.getX())>>4;x<=Math.max(a.getX(),b.getX())>>4;x++)
            for(int z=Math.min(a.getZ(),b.getZ())>>4;z<=Math.max(a.getZ(),b.getZ())>>4;z++)
                if(!l.hasChunk(x,z))return false;
        return true;
    }
    static boolean place(ServerLevel l,Restaurant r,Cat c){
        int start=l.random.nextInt(SPOTS.length);
        for(int i=0;i<SPOTS.length;i++){int[] s=SPOTS[(start+i)%SPOTS.length];BlockPos q=r.pos(s[0],1,s[1]);
            if(!l.hasChunkAt(q)||!l.getBlockState(q.below()).isFaceSturdy(l,q.below(),Direction.UP)||!l.getBlockState(q).getCollisionShape(l,q).isEmpty())continue;
            double x=q.getX()+.5,y=q.getY(),z=q.getZ()+.5;
            if(!l.noCollision(c,c.getBoundingBox().move(x-c.getX(),y-c.getY(),z-c.getZ())))continue;
            c.moveTo(x,y,z,l.random.nextFloat()*360,0);return true;
        }return false;
    }
    static void maintain(ServerLevel l,Restaurant r){
        if(!loaded(l,r))return;
        BlockPos center=r.pos(14,1,17);
        List<Cat> cats=l.getEntitiesOfClass(Cat.class,new AABB(center).inflate(31),c->c.isAlive()&&c.getPersistentData().contains(HOME)&&c.getPersistentData().getLong(HOME)==r.marker.asLong());
        int count=0;
        for(Cat c:cats){
            if(c.isTame()){c.getPersistentData().remove(HOME);c.clearRestriction();continue;}
            c.setAge(-24000);c.restrictTo(center,15);count++;
            if(c.distanceToSqr(center.getX()+.5,center.getY(),center.getZ()+.5)>225)place(l,r,c);
        }
        for(int i=count;i<COUNT;i++){
            Cat c=EntityType.CAT.create(l);if(c==null)break;
            c.setAge(-24000);c.setPersistenceRequired();c.getPersistentData().putLong(HOME,r.marker.asLong());c.restrictTo(center,15);
            var coat=BuiltInRegistries.CAT_VARIANT.get(new ResourceLocation("minecraft",COATS[i%COATS.length]));if(coat!=null)c.setVariant(coat);
            if(place(l,r,c))l.addFreshEntity(c);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.level instanceof ServerLevel l)||l.getGameTime()%100!=0)return;
        SushiCats d=get(l);Iterator<Restaurant> it=d.restaurants.iterator();
        while(it.hasNext()){
            Restaurant r=it.next();if(!l.hasChunkAt(r.marker))continue;
            if(!l.getBlockState(r.marker).is(Blocks.CHISELED_STONE_BRICKS)){it.remove();d.setDirty();continue;}
            if(l.getNearestPlayer(r.marker.getX()+.5,r.marker.getY()+1,r.marker.getZ()+.5,64,false)!=null)maintain(l,r);
        }
    }
    @SubscribeEvent public static void catTick(net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent e){
        if(!(e.getEntity() instanceof Cat c)||!(c.level() instanceof ServerLevel l)||!c.getPersistentData().contains(HOME))return;
        if(c.isTame()){c.getPersistentData().remove(HOME);c.clearRestriction();return;}
        if(c.tickCount%20==0)c.setAge(-24000);
    }
}''',encoding='utf-8')
# Third line gets its own timer; prevent strolling during the whole exchange.
edit('GemGuest.java','int conversation=80,answer=0,pose=0;','int conversation=80,answer=0,reply=0,pose=0;')
edit('GemGuest.java','phos()&&answer==0&&conversation>40&&together()','phos()&&answer==0&&reply==0&&(conversation<300||conversation>390)&&conversation>40&&together()')
edit('GemGuest.java','phos()&&answer==0&&conversation>40&&together()','phos()&&answer==0&&reply==0&&(conversation<300||conversation>390)&&conversation>40&&together()')
edit('GemGuest.java','if(q==null){getNavigation().stop();answer=0;return;}','if(q==null){getNavigation().stop();answer=0;reply=0;return;}')
edit('GemGuest.java','        if(answer>0){','''        if(phos()&&reply>0){
            getNavigation().stop();getLookControl().setLookAt(q,30,30);
            if(--reply==0&&d<7){say(l,"Se! Allora dovrò aspettare 10 mila anni!");l.broadcastEntityEvent(this,(byte)113);}
            return;
        }
        if(answer>0){''')
edit('GemGuest.java','say(l,"Prima devi trovare te stesso, Phosphophyllite.");l.broadcastEntityEvent(this,(byte)113);','say(l,"Prima devo trovare me stesso.");l.broadcastEntityEvent(this,(byte)113);q.reply=40;')
print('Sakura garden, eight persistent kitten residents and corrected gem dialogue installed')
