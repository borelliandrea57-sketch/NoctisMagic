"""1.1.0: weeping stone angels, crimson particle fountains and baroque Gothic interiors."""
from pathlib import Path
import sys
root=Path(sys.argv[1]);p=root/'src/main/java/it/noctis/magic/GothicEgg.java';s=p.read_text(encoding='utf-8')
def edit(a,b):
    global s
    assert a in s,a[:120];s=s.replace(a,b,1)
# Persist visual emitter coordinates as part of the generated monument plan.
edit('final LinkedHashMap<Integer,BlockState> blocks=new LinkedHashMap<>();','''final LinkedHashMap<Integer,BlockState> blocks=new LinkedHashMap<>();
        final java.util.ArrayList<int[]> crimson=new java.util.ArrayList<>();''')
a='    static Plan cathedral(){'
edit(a,'''    static void angel(Plan p,int x,int y,int z){
        // 15 block tall sculpture, carved ivory robes, bowed face and layered wings.
        p.box(x-3,y,z-2,x+3,y,z+2,TRIM);
        p.box(x-2,y+1,z-2,x+2,y+2,z+2,Blocks.CHISELED_QUARTZ_BLOCK);
        p.box(x-2,y+3,z-1,x+2,y+5,z+1,Blocks.CALCITE);
        p.box(x-1,y+6,z-1,x+1,y+9,z+1,Blocks.SMOOTH_QUARTZ);
        for(int dy=3;dy<=8;dy++){p.put(x-2,y+dy,z,Blocks.QUARTZ_PILLAR);p.put(x+2,y+dy,z,Blocks.QUARTZ_PILLAR);}
        p.box(x-2,y+9,z-1,x+2,y+10,z+1,Blocks.CALCITE);
        p.box(x-1,y+11,z-1,x+1,y+13,z+1,Blocks.SMOOTH_QUARTZ);
        p.put(x,y+12,z-2,Blocks.QUARTZ_SLAB);
        // Dark eyes under a projecting sculpted brow.
        for(int side:new int[]{-1,1}){
            p.put(x+side,y+12,z-2,Blocks.POLISHED_BLACKSTONE_BUTTON.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING,Direction.NORTH));
            p.put(x+side,y+11,z-2,Blocks.RED_STAINED_GLASS);
            p.put(x+side,y+10,z-2,Blocks.RED_STAINED_GLASS_PANE);
            p.crimson.add(new int[]{x+side,y+12,z-2,0});
            // arms incline downward, separate folds of sleeves
            p.box(x+side*3,y+8,z-1,x+side*3,y+10,z,Blocks.QUARTZ_PILLAR);
            p.put(x+side*2,y+7,z-2,Blocks.CALCITE);p.put(x+side,y+7,z-2,Blocks.SMOOTH_QUARTZ);
            // silhouette of wing, stepped rows of individual feather ribs
            for(int k=0;k<6;k++){
                int wx=x+side*(2+k),wy=y+10+k;
                p.box(wx,wy-4,z+2,wx,wy,z+2,Blocks.CALCITE);
                p.put(wx,wy+1,z+2,Blocks.QUARTZ_SLAB);
                for(int n=0;n<3;n++)p.put(wx,wy-1-n,z+1,Blocks.QUARTZ_PILLAR);
                if(k<4)p.put(wx,wy-5,z+2,Blocks.QUARTZ_SLAB);
            }
        }
        // open halo with a gold edge.
        for(int dx=-2;dx<=2;dx++)for(int dy=-2;dy<=2;dy++)if(Math.abs(dx)+Math.abs(dy)>=2&&Math.abs(dx)+Math.abs(dy)<=3)p.put(x+dx,y+14+dy,z+1,Blocks.GOLD_BLOCK);
        for(int side:new int[]{-1,1})p.lantern(x+side*3,y+1,z-2);
    }
    static void bloodFountain(Plan p,int x,int y,int z){
        // Circular stone basin, red-glass liquid illusion and harmless animated jets.
        for(int dx=-5;dx<=5;dx++)for(int dz=-5;dz<=5;dz++){
            double r=Math.sqrt(dx*dx+dz*dz);
            if(r<=5.25)p.put(x+dx,y,z+dz,Blocks.POLISHED_BLACKSTONE);
            if(r>=4.3&&r<=5.25)p.put(x+dx,y+1,z+dz,Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);
            else if(r<4.3)p.put(x+dx,y+1,z+dz,Blocks.RED_STAINED_GLASS);
        }
        p.box(x-1,y+2,z-1,x+1,y+2,z+1,EDGE);p.box(x,y+3,z,x,y+5,z,Blocks.QUARTZ_PILLAR);
        p.box(x-2,y+6,z-1,x+2,y+6,z+1,Blocks.CHISELED_QUARTZ_BLOCK);p.box(x-1,y+6,z-2,x+1,y+6,z+2,Blocks.CHISELED_QUARTZ_BLOCK);
        p.put(x,y+7,z,Blocks.RED_STAINED_GLASS);p.put(x,y+8,z,Blocks.RED_STAINED_GLASS_PANE);
        p.crimson.add(new int[]{x,y+7,z,1});
        for(int dx:new int[]{-3,3})for(int dz:new int[]{-3,3})p.put(x+dx,y+1,z+dz,Blocks.REDSTONE_LAMP);
    }
'''+a)
a='        // decorative recessed side shrines within aisles'
edit(a,'''        // Pair of monumental weeping angels guarding the sanctuary, and fore-nave fountain.
        angel(p,22,1,68);angel(p,38,1,68);
        bloodFountain(p,30,0,16);
        // Preserve a free passage around the font.
'''+a)
# More wall relief, paneling, pointed decorative alcoves; preserve existing openings.
a='        if(type==0){ // two-storey library'
edit(a,'''        // Interior stone dado, pilasters, engraved wall panels and upper cornices.
        for(int z=z1+2;z<z2-1;z++){
            if(z%6==0){for(int x:new int[]{x1,x2}){p.put(x,y+2,z,EDGE);p.put(x,y+3,z,Blocks.POLISHED_BLACKSTONE_BRICK_WALL);p.put(x,y+8,z,EDGE);}}
            p.put(x1,y+10,z,Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);p.put(x2,y+10,z,Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);
        }
        for(int x=x1+1;x<x2;x++)if(Math.abs(x-cx)>3){
            p.put(x,y+2,z1,Blocks.DARK_OAK_PLANKS);p.put(x,y+3,z1,Blocks.CHISELED_STONE_BRICKS);
            p.put(x,y+2,z2,Blocks.DARK_OAK_PLANKS);p.put(x,y+3,z2,Blocks.CHISELED_STONE_BRICKS);
            p.put(x,y+9,z1,EDGE);p.put(x,y+9,z2,EDGE);
        }
'''+a)
start=s.index('            rug(p,cx-3,z1+4,cx+3,z2-4,y+1,Blocks.RED_CARPET,Blocks.BLACK_CARPET);',s.index('}else if(type==3)'))
end=s.index('        }else if(type==4)',start)
s=s[:start]+'''            rug(p,cx-4,z1+3,cx+4,z2-3,y+1,Blocks.RED_CARPET,Blocks.BLACK_CARPET);
            // Raised carved platform, steps, golden feet and wide crimson mattress.
            p.box(cx-3,y+1,cz-4,cx+3,y+1,cz+4,Blocks.DARK_OAK_PLANKS);
            p.ring(cx-3,y+2,cz-4,cx+3,cz+4,Blocks.POLISHED_BLACKSTONE_BRICKS);
            p.box(cx-2,y+2,cz-3,cx+2,y+2,cz+3,Blocks.RED_WOOL);
            p.box(cx-2,y+3,cz-2,cx+2,y+3,cz+1,Blocks.RED_CARPET);
            p.box(cx-2,y+3,cz+2,cx-1,y+3,cz+3,Blocks.WHITE_WOOL);
            p.box(cx+1,y+3,cz+2,cx+2,y+3,cz+3,Blocks.WHITE_WOOL);
            p.stair(cx,y+1,cz-5,Blocks.DARK_OAK_STAIRS,Direction.SOUTH);
            // Carved headboard with Gothic pointed inlays.
            p.box(cx-3,y+3,cz+4,cx+3,y+5,cz+4,Blocks.DARK_OAK_PLANKS);
            for(int dx=-2;dx<=2;dx++){p.put(cx+dx,y+5,cz+4,dx%2==0?Blocks.GOLD_BLOCK:EDGE);p.put(cx+dx,y+6-Math.abs(dx)/2,cz+4,Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);}
            for(int x:new int[]{cx-3,cx+3})for(int z:new int[]{cz-4,cz+4}){
                p.put(x,y+2,z,Blocks.GOLD_BLOCK);p.box(x,y+3,z,x,y+8,z,Blocks.DARK_OAK_FENCE);p.put(x,y+9,z,Blocks.GOLD_BLOCK);
                // crimson velvet drapes gathered at the posts
                int sx=x<cx?1:-1,sz=z<cz?1:-1;
                p.box(x+sx,y+4,z,x+sx,y+7,z,Blocks.RED_WOOL);
                p.put(x+sx,y+5,z,Blocks.GOLD_BLOCK);
                p.put(x,y+6,z+sz,Blocks.RED_WOOL);p.put(x,y+7,z+sz,Blocks.RED_WOOL);
            }
            p.box(cx-3,y+8,cz-4,cx+3,y+8,cz+4,Blocks.RED_WOOL);p.ring(cx-4,y+9,cz-5,cx+4,cz+5,TRIM);
            for(int x=cx-3;x<=cx+3;x++){p.put(x,y+8,cz-5,x%2==0?Blocks.GOLD_BLOCK:Blocks.RED_WOOL);p.put(x,y+8,cz+5,x%2==0?Blocks.GOLD_BLOCK:Blocks.RED_WOOL);}
            for(int z=cz-4;z<=cz+4;z++){p.put(cx-4,y+8,z,z%2==0?Blocks.GOLD_BLOCK:Blocks.RED_WOOL);p.put(cx+4,y+8,z,z%2==0?Blocks.GOLD_BLOCK:Blocks.RED_WOOL);}
            // matching decorative furniture and gilded wall tapestries
            for(int x:new int[]{cx-4,cx+4}){p.put(x,y+1,cz+3,Blocks.DARK_OAK_PLANKS);p.put(x,y+2,cz+3,Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.LIT,true));}
            for(int z=z1+4;z<z2-2;z+=7)for(int x:new int[]{x1+1,x2-1}){
                p.box(x,y+3,z-1,x,y+7,z+1,Blocks.RED_WOOL);
                p.box(x,y+8,z-1,x,y+8,z+1,Blocks.GOLD_BLOCK);p.put(x,y+5,z,Blocks.YELLOW_GLAZED_TERRACOTTA);
            }
            p.box(x1+1,y+1,z1+3,x1+2,y+5,z1+6,Blocks.DARK_OAK_PLANKS);p.put(x2-2,y+2,z1+4,Blocks.FLOWER_POT);fireplace(p,cx,y,z2-2);
'''+s[end:]
# Persist effects in SavedData on successful build. Each marker also checks its source block.
edit('            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");','''            for(int[] fx:p.crimson)CrimsonMonuments.get(l).add(pos(fx[0],fx[1],fx[2]),fx[3],forward);
            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");''')
p.write_text(s,encoding='utf-8')
(root/'src/main/java/it/noctis/magic/CrimsonMonuments.java').write_text('''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.core.particles.*;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class CrimsonMonuments extends SavedData{
    record Marker(BlockPos pos,int type,Direction front){}
    final ArrayList<Marker> markers=new ArrayList<>();
    static CrimsonMonuments load(CompoundTag t){CrimsonMonuments d=new CrimsonMonuments();ListTag list=t.getList("Crimson",10);for(int i=0;i<list.size();i++){CompoundTag n=list.getCompound(i);d.markers.add(new Marker(BlockPos.of(n.getLong("Pos")),n.getInt("Type"),Direction.from2DDataValue(n.getInt("Front"))));}return d;}
    @Override public CompoundTag save(CompoundTag t){ListTag list=new ListTag();for(Marker m:markers){CompoundTag n=new CompoundTag();n.putLong("Pos",m.pos.asLong());n.putInt("Type",m.type);n.putInt("Front",m.front.get2DDataValue());list.add(n);}t.put("Crimson",list);return t;}
    static CrimsonMonuments get(ServerLevel l){return l.getDataStorage().computeIfAbsent(CrimsonMonuments::load,CrimsonMonuments::new,"noctis_crimson_monuments");}
    void add(BlockPos pos,int type,Direction front){markers.add(new Marker(pos,type,front));setDirty();}
    static final DustParticleOptions BLOOD=new DustParticleOptions(new Vector3f(.63f,.008f,.025f),1.05f);
    static final DustParticleOptions DARK=new DustParticleOptions(new Vector3f(.32f,.005f,.018f),.85f);
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.level instanceof ServerLevel l)||l.getGameTime()%4!=0)return;
        CrimsonMonuments d=get(l);Iterator<Marker> it=d.markers.iterator();
        while(it.hasNext()){
            Marker m=it.next();BlockPos b=m.pos;if(!l.hasChunkAt(b))continue;
            if(m.type==0&&!l.getBlockState(b).is(Blocks.POLISHED_BLACKSTONE_BUTTON)||m.type==1&&!l.getBlockState(b).is(Blocks.RED_STAINED_GLASS)){it.remove();d.setDirty();continue;}
            double x=b.getX()+.5,z=b.getZ()+.5,y=b.getY()+.5;
            if(l.getNearestPlayer(x,y,z,64,false)==null)continue;
            if(m.type==0){
                x-=m.front.getStepX()*.55;z-=m.front.getStepZ()*.55;
                double fall=(l.getGameTime()%40)/40.0*2.7;
                l.sendParticles(BLOOD,x,y-fall,z,2,.035,.08,.035,0);
                l.sendParticles(DARK,x,y-fall-.18,z,1,.025,.06,.025,0);
            }else{
                double phase=(l.getGameTime()%40)/40.0;
                for(int i=0;i<8;i++){
                    double a=i*Math.PI/4;
                    for(int j=0;j<4;j++){
                        double t=(phase+j*.25)%1,r=.35+3.45*t,h=2.2*Math.sin(Math.PI*t)-5.6*t*t;
                        l.sendParticles(j%2==0?BLOOD:DARK,x+Math.cos(a)*r,y+h,z+Math.sin(a)*r,1,.055,.09,.055,0);
                    }
                }
            }
        }
    }
}''',encoding='utf-8')
print('Crimson monuments: weeping angels, persistent red particle fountains, decorative castle walls and royal canopy')
