"""1.0.8: monumental gothic structure eggs, non-destructive queued construction."""
from pathlib import Path
import sys,json,struct,zlib,math
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
p=java/'Noctis.java';s=p.read_text(encoding='utf-8')
a='public static final RegistryObject<EntityType<ScrapThief>> SCRAP_THIEF='
assert a in s
s=s.replace(a,'''public static final RegistryObject<Item> CATHEDRAL_EGG=ITEMS.register("cathedral_egg",()->new GothicEgg(false));
    public static final RegistryObject<Item> CASTLE_EGG=ITEMS.register("castle_egg",()->new GothicEgg(true));
    '''+a,1)
a='e.accept(SCRAP_THIEF_EGG.get());';assert a in s
s=s.replace(a,a+'e.accept(CATHEDRAL_EGG.get());e.accept(CASTLE_EGG.get());',1);p.write_text(s,encoding='utf-8')
(java/'GothicEgg.java').write_text('''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
public class GothicEgg extends Item{
    private final boolean castle;
    public GothicEgg(boolean castle){super(new Item.Properties().stacksTo(1));this.castle=castle;}
    @Override public boolean isFoil(net.minecraft.world.item.ItemStack s){return true;}
    @Override public InteractionResult useOn(UseOnContext c){
        if(c.getLevel().isClientSide)return InteractionResult.SUCCESS;
        if(!(c.getPlayer() instanceof ServerPlayer p)||!(c.getLevel() instanceof ServerLevel l))return InteractionResult.FAIL;
        if(!p.isCreative()&&!p.hasPermissions(2)){p.sendSystemMessage(Component.literal("Per evocare un monumento serve la modalita Creativa o il permesso operatore."));return InteractionResult.FAIL;}
        if(c.getClickedFace()!=Direction.UP){p.sendSystemMessage(Component.literal("Usa il sigillo sulla superficie superiore del terreno."));return InteractionResult.FAIL;}
        if(!Jobs.queue.isEmpty()){p.sendSystemMessage(Component.literal("Una struttura e' gia in costruzione."));return InteractionResult.FAIL;}
        Plan plan=castle?castle():cathedral();
        Direction front=p.getDirection();if(front.getAxis()==Direction.Axis.Y)front=Direction.SOUTH;
        BlockPos start=c.getClickedPos().above();
        // Click marks the forecourt, outside the building. Local +Z follows the player's view.
        BlockPos origin=start.relative(front,4).relative(front.getCounterClockWise(),-plan.w/2);
        if(origin.getY()+plan.h>=l.getMaxBuildHeight()||origin.getY()-3<l.getMinBuildHeight()){p.sendSystemMessage(Component.literal("Altezza insufficiente."));return InteractionResult.FAIL;}
        Job job=new Job(l,p,plan,origin,front);
        // Do not generate missing chunks or replace terrain, plants, buildings or liquids.
        for(int x=0;x<plan.w;x+=8)for(int z=0;z<plan.d;z+=8)if(!l.hasChunkAt(job.pos(x,0,z))){p.sendSystemMessage(Component.literal("Area non caricata: aumenta la distanza di simulazione o esplora prima la zona."));return InteractionResult.FAIL;}
        p.sendSystemMessage(Component.literal("Verifica spazio per "+plan.name+" ("+plan.w+" x "+plan.d+" x "+plan.h+")."));
        Jobs.queue.add(job);
        if(!p.getAbilities().instabuild)c.getItemInHand().shrink(1);
        return InteractionResult.CONSUME;
    }
    static final Block STONE=Blocks.DEEPSLATE_BRICKS,TRIM=Blocks.POLISHED_BLACKSTONE_BRICKS,EDGE=Blocks.CHISELED_STONE_BRICKS,LIGHT=Blocks.POLISHED_ANDESITE,ROOF=Blocks.DEEPSLATE_TILES;
    static final Block[] GLASS={Blocks.RED_STAINED_GLASS,Blocks.BLUE_STAINED_GLASS,Blocks.PURPLE_STAINED_GLASS,Blocks.YELLOW_STAINED_GLASS,Blocks.CYAN_STAINED_GLASS};
    static final Block[] MOSAIC={Blocks.BLACKSTONE,Blocks.POLISHED_DIORITE,Blocks.RED_TERRACOTTA,Blocks.BLUE_TERRACOTTA,Blocks.YELLOW_TERRACOTTA};
    static class Plan{
        final int w,d,h;final String name;final LinkedHashMap<Integer,BlockState> blocks=new LinkedHashMap<>();
        Plan(int w,int d,int h,String n){this.w=w;this.d=d;this.h=h;name=n;}
        int key(int x,int y,int z){return (y+3)*w*d+z*w+x;}
        void put(int x,int y,int z,Block b){put(x,y,z,b.defaultBlockState());}
        void put(int x,int y,int z,BlockState b){if(x>=0&&z>=0&&x<w&&z<d&&y>=-3&&y<h){if(b.isAir())blocks.remove(key(x,y,z));else blocks.put(key(x,y,z),b);}}
        void box(int x1,int y1,int z1,int x2,int y2,int z2,Block b){for(int y=y1;y<=y2;y++)for(int z=z1;z<=z2;z++)for(int x=x1;x<=x2;x++)put(x,y,z,b);}
        void ring(int x1,int y,int z1,int x2,int z2,Block b){box(x1,y,z1,x2,y,z1,b);box(x1,y,z2,x2,y,z2,b);box(x1,y,z1,x1,y,z2,b);box(x2,y,z1,x2,y,z2,b);}
        void walls(int x1,int y1,int z1,int x2,int y2,int z2,Block b){for(int y=y1;y<=y2;y++)ring(x1,y,z1,x2,z2,b);}
        void stair(int x,int y,int z,Block stair,Direction dir){put(x,y,z,stair.defaultBlockState().setValue(StairBlock.FACING,dir));}
        void slab(int x,int y,int z,Block slab){put(x,y,z,slab);}
        void lantern(int x,int y,int z){put(x,y,z,Blocks.LANTERN);}
    }
    static void floor(Plan p,int x1,int z1,int x2,int z2){
        for(int x=x1;x<=x2;x++)for(int z=z1;z<=z2;z++){
            int a=Math.floorMod(x,8),b=Math.floorMod(z,8);int m=Math.abs(a-4)+Math.abs(b-4);
            p.put(x,0,z,m==3?MOSAIC[2]:m==2?MOSAIC[3]:m==0?MOSAIC[4]:(x+z)%2==0?MOSAIC[0]:MOSAIC[1]);
        }
    }
    static void column(Plan p,int x,int z,int base,int top){
        p.box(x-1,base,z-1,x+1,base,z+1,TRIM);
        p.box(x,base+1,z,x,top-1,z,LIGHT);
        for(int y=base+3;y<top;y+=5)p.put(x,y,z,EDGE);
        p.box(x-1,top,z-1,x+1,top,z+1,TRIM);
    }
    // pointed Gothic openings; arch outline follows the taper above the rectangular shaft.
    static void opening(Plan p,int cx,int base,int fixed,int half,int height,boolean alongZ,boolean glass){
        for(int y=0;y<height;y++){int h=y<height/2?half:Math.max(0,half-(y-height/2)* (half+1)/Math.max(1,height-height/2));
            for(int x=-h;x<=h;x++){int a=alongZ?fixed:cx+x,b=alongZ?cx+x:fixed;
                Block mat=glass?(x==0||y==height/2?TRIM:GLASS[Math.floorMod(Math.abs(x)+y/3,GLASS.length)]):Blocks.AIR;
                p.put(a,base+y,b,mat);
            }
            for(int sign:new int[]{-1,1})p.put(alongZ?fixed:cx+sign*(h+1),base+y,alongZ?cx+sign*(h+1):fixed,EDGE);
        }
    }
    static void rose(Plan p,int cx,int cy,int z,int r){
        for(int x=-r-1;x<=r+1;x++)for(int y=-r-1;y<=r+1;y++){
            double d=Math.sqrt(x*x+y*y);if(d>r+1)continue;
            double a=Math.atan2(y,x);Block b=d>r-.3||d<1.5||Math.abs(Math.sin(a*6))*d<.55?TRIM:GLASS[Math.floorMod((int)Math.floor((a+Math.PI)*6/Math.PI)+(int)(d/3),5)];
            p.put(cx+x,cy+y,z,b);
        }
    }
    static void statue(Plan p,int x,int y,int z){
        p.box(x-1,y,z-1,x+1,y,z+1,TRIM);p.put(x,y+1,z,Blocks.POLISHED_DIORITE);p.put(x,y+2,z,Blocks.QUARTZ_PILLAR);p.put(x,y+3,z,Blocks.SMOOTH_QUARTZ);p.put(x,y+4,z,Blocks.CHISELED_QUARTZ_BLOCK);
        p.stair(x-1,y+3,z,Blocks.QUARTZ_STAIRS,Direction.WEST);p.stair(x+1,y+3,z,Blocks.QUARTZ_STAIRS,Direction.EAST);
        p.put(x,y+5,z,Blocks.QUARTZ_SLAB);
    }
    static void spire(Plan p,int cx,int cz,int y,int radius,int height){
        for(int k=0;k<height;k++){
            int r=Math.max(0,radius-(k*radius)/Math.max(1,height-2));
            if(r==0)p.put(cx,y+k,cz,TRIM);
            else{for(int dx=-r;dx<=r;dx++)for(int dz=-r;dz<=r;dz++)if(Math.abs(dx)+Math.abs(dz)>=r&&Math.abs(dx)+Math.abs(dz)<=r+1)p.put(cx+dx,y+k,cz+dz,ROOF);
                if(k%4==0)p.ring(cx-r,y+k,cz-r,cx+r,cz+r,TRIM);}
        }
        p.put(cx,y+height,cz,Blocks.LIGHTNING_ROD);
    }
    static void tower(Plan p,int cx,int cz,int r,int height,int base){
        p.box(cx-r,base,cz-r,cx+r,base,cz+r,STONE);
        p.walls(cx-r,base+1,cz-r,cx+r,base+height,cz+r,STONE);
        for(int x:new int[]{cx-r,cx+r})for(int z:new int[]{cz-r,cz+r})p.box(x,base+1,z,x,base+height,z,TRIM);
        for(int y=base+6;y<base+height-5;y+=9){
            p.ring(cx-r,y,cz-r,cx+r,cz+r,EDGE);
            opening(p,cx,y+2,cz-r,1,5,false,true);opening(p,cx,y+2,cz+r,1,5,false,true);
            opening(p,cz,y+2,cx-r,1,5,true,true);opening(p,cz,y+2,cx+r,1,5,true,true);
        }
        // Spiral staircase, one block rise each step, with central pillar and landings.
        p.box(cx,base+1,cz,cx,base+height-1,cz,TRIM);
        int[][] steps={{-2,-2},{-1,-2},{0,-2},{1,-2},{2,-2},{2,-1},{2,0},{2,1},{2,2},{1,2},{0,2},{-1,2},{-2,2},{-2,1},{-2,0},{-2,-1}};
        for(int i=0;i<height-2;i++){int[] a=steps[i%16],b=steps[(i+1)%16];Direction dir=b[0]>a[0]?Direction.EAST:b[0]<a[0]?Direction.WEST:b[1]>a[1]?Direction.SOUTH:Direction.NORTH;p.stair(cx+a[0],base+1+i,cz+a[1],Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS,dir);}
        p.ring(cx-r-1,base+height,cz-r-1,cx+r+1,cz+r+1,TRIM);
        for(int a=-r;a<=r;a+=2){p.put(cx+a,base+height+1,cz-r,EDGE);p.put(cx+a,base+height+1,cz+r,EDGE);p.put(cx-r,base+height+1,cz+a,EDGE);p.put(cx+r,base+height+1,cz+a,EDGE);}
        spire(p,cx,cz,base+height+2,r,Math.min(17,p.h-base-height-4));
    }
    static void pews(Plan p,int x1,int x2,int z1,int z2,int y){
        for(int z=z1;z<=z2;z+=4){
            for(int x=x1;x<=x2;x++)p.stair(x,y,z,Blocks.DARK_OAK_STAIRS,Direction.NORTH);
            p.put(x1,y,z,Blocks.DARK_OAK_LOG);p.put(x2,y,z,Blocks.DARK_OAK_LOG);
        }
    }
    static void altar(Plan p,int cx,int z,int y){
        p.box(cx-4,y,z-2,cx+4,y,z+2,LIGHT);p.box(cx-3,y+1,z,cx+3,y+1,z+1,Blocks.CHISELED_QUARTZ_BLOCK);p.box(cx-4,y+2,z,cx+4,y+2,z+1,Blocks.QUARTZ_SLAB);
        for(int x:new int[]{cx-3,cx+3})p.put(x,y+3,z,Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.LIT,true));
        p.box(cx,y+2,z+3,cx,y+8,z+3,Blocks.GOLD_BLOCK);p.box(cx-2,y+6,z+3,cx+2,y+6,z+3,Blocks.GOLD_BLOCK);
    }
    static Plan cathedral(){
        Plan p=new Plan(61,91,66,"Cattedrale di Santa Lacrimosa");int cx=30;
        p.box(4,-1,4,56,-1,86,STONE);floor(p,4,4,56,86);
        // central nave + two lower aisles
        p.walls(14,1,10,46,32,79,STONE);p.walls(5,1,14,55,16,75,STONE);
        // open shared side walls below triforium, retaining arcades
        for(int z=17;z<=73;z+=8){
            opening(p,z,2,14,3,14,true,false);opening(p,z,2,46,3,14,true,false);
            opening(p,z,5,5,2,10,true,true);opening(p,z,5,55,2,10,true,true);
            opening(p,z,20,14,2,11,true,true);opening(p,z,20,46,2,11,true,true);
            for(int x:new int[]{11,49}){column(p,x,z,1,16);statue(p,x,1,z+3);}
            for(int x:new int[]{3,57}){p.box(x,1,z-1,x,12,z+1,TRIM);p.box(x==3?3:55,12,z-1,x==3?5:57,14,z+1,EDGE);spire(p,x,z,14,1,6);}
            // pointed transverse stone ribs under the roof
            for(int k=0;k<=15;k++){int y=22+k;int lx=14+k,rx=46-k;p.put(lx,y,z,LIGHT);p.put(rx,y,z,LIGHT);p.put(lx,y+1,z,TRIM);p.put(rx,y+1,z,TRIM);}
            p.box(cx,28,z,cx,35,z,Blocks.CHAIN);p.lantern(cx,27,z);
        }
        // Side aisle roofs and soaring central pitched roof.
        for(int z=12;z<=77;z++)for(int k=0;k<=9;k++){p.put(5+k,17+k/2,z,ROOF);p.put(55-k,17+k/2,z,ROOF);}
        for(int z=9;z<=80;z++)for(int k=0;k<=16;k++){p.put(14+k,32+k,z,ROOF);p.put(46-k,32+k,z,ROOF);}
        for(int z=9;z<=80;z+=3)p.put(cx,49,z,EDGE);
        for(int k=0;k<=16;k++){p.box(14+k,32,10,14+k,32+k,10,STONE);p.box(46-k,32,10,46-k,32+k,10,STONE);p.box(14+k,32,79,14+k,32+k,79,STONE);p.box(46-k,32,79,46-k,32+k,79,STONE);}
        // west facade and triple portal
        p.box(11,1,8,49,32,8,STONE);opening(p,cx,1,8,5,15,false,false);
        opening(p,17,1,8,2,9,false,false);opening(p,43,1,8,2,9,false,false);
        opening(p,cx,1,10,5,15,false,false);opening(p,17,1,10,2,9,false,false);opening(p,43,1,10,2,9,false,false);
        rose(p,cx,24,8,7);rose(p,cx,24,10,7);
        for(int x:new int[]{11,20,40,49}){p.box(x,1,7,x,30,7,TRIM);spire(p,x,8,31,1,9);}
        tower(p,9,10,6,46,0);tower(p,51,10,6,46,0);
        opening(p,9,1,16,2,8,false,false);opening(p,51,1,16,2,8,false,false);
        // rear sanctuary with tall stained glass
        for(int x=18;x<=42;x+=6)opening(p,x,6,79,2,18,false,true);
        p.box(15,1,80,45,1,85,TRIM);floor(p,17,81,43,84);
        for(int x=17;x<=43;x+=6)statue(p,x,2,83);
        pews(p,17,25,19,63,1);pews(p,35,43,19,63,1);
        altar(p,cx,71,1);
        for(int z=20;z<=65;z+=10){p.put(cx-4,1,z,Blocks.RED_CARPET);p.put(cx+4,1,z,Blocks.RED_CARPET);}
        for(int z=12;z<=78;z++)for(int x=27;x<=33;x++)p.put(x,0,z,Math.abs(x-30)==3?Blocks.GOLD_BLOCK:(z%7==0?MOSAIC[3]:MOSAIC[2]));
        // decorative recessed side shrines within aisles
        for(int z=23;z<=65;z+=14)for(int x:new int[]{7,53}){p.box(x-1,1,z-2,x+1,1,z+2,TRIM);p.box(x-1,2,z-2,x-1,6,z+2,EDGE);p.box(x-1,6,z-2,x+1,6,z+2,EDGE);statue(p,x,2,z);p.lantern(x,2,z-3);}
        return p;
    }
    static void room(Plan p,int x1,int z1,int x2,int z2,int y,int type){
        floorAt(p,x1,z1,x2,z2,y);
        for(int z=z1+2;z<z2;z+=4)p.lantern(x1+2,y+1,z);
        if(type==0){for(int z=z1+1;z<z2;z++){p.box(x1+1,y+1,z,x1+1,y+4,z,Blocks.BOOKSHELF);p.box(x2-1,y+1,z,x2-1,y+4,z,Blocks.BOOKSHELF);}
            for(int z=z1+3;z<z2-1;z+=5){p.box(x1+4,y+1,z,x2-4,y+1,z,Blocks.DARK_OAK_FENCE);p.box(x1+4,y+2,z,x2-4,y+2,z,Blocks.DARK_OAK_SLAB);}}
        else if(type==1){int cx=(x1+x2)/2;p.box(cx-1,y+1,z1+3,cx+1,y+1,z2-3,Blocks.DARK_OAK_LOG);p.box(cx-2,y+2,z1+3,cx+2,y+2,z2-3,Blocks.DARK_OAK_SLAB);
            for(int z=z1+3;z<=z2-3;z+=3){p.stair(cx-3,y+1,z,Blocks.DARK_OAK_STAIRS,Direction.WEST);p.stair(cx+3,y+1,z,Blocks.DARK_OAK_STAIRS,Direction.EAST);p.lantern(cx,y+3,z);}}
        else {for(int z=z1+2;z<z2-3;z+=7){p.box(x1+2,y+1,z,x1+4,y+1,z+3,Blocks.DARK_OAK_PLANKS);p.box(x1+2,y+2,z,x1+4,y+2,z+3,Blocks.RED_WOOL);p.box(x1+2,y+2,z,x1+4,y+2,z,Blocks.WHITE_WOOL);p.box(x2-3,y+1,z,x2-1,y+3,z+1,Blocks.BOOKSHELF);}}
    }
    static void floorAt(Plan p,int x1,int z1,int x2,int z2,int y){for(int x=x1;x<=x2;x++)for(int z=z1;z<=z2;z++)p.put(x,y,z,(x+z)%2==0?Blocks.POLISHED_BLACKSTONE:Blocks.POLISHED_DEEPSLATE);}
    static Plan castle(){
        Plan p=new Plan(91,101,76,"Castello di Valdracula");int cx=45;
        p.box(5,-1,5,85,-1,95,STONE);floorAt(p,5,5,85,95,0);
        p.walls(7,1,7,83,14,93,STONE);
        for(int y:new int[]{1,7,14})p.ring(6,y,6,84,94,TRIM);
        for(int x=7;x<=83;x+=3){p.put(x,15,7,EDGE);p.put(x,15,93,EDGE);}
        for(int z=7;z<=93;z+=3){p.put(7,15,z,EDGE);p.put(83,15,z,EDGE);}
        opening(p,cx,1,7,5,11,false,false);opening(p,cx,1,6,5,11,false,false);
        for(int x:new int[]{9,81})for(int z:new int[]{9,91})tower(p,x,z,7,35,0);
        tower(p,34,9,5,30,0);tower(p,56,9,5,30,0);
        // Broad entrance boulevard with alternating statues and lamps.
        for(int z=8;z<=35;z++)for(int x=40;x<=50;x++)p.put(x,0,z,x==40||x==50?EDGE:z%6==0?MOSAIC[2]:MOSAIC[0]);
        for(int z=16;z<=30;z+=7)for(int x:new int[]{36,54}){statue(p,x,1,z);p.lantern(x,1,z+3);}
        // Main keep, flanking wings, central hall remains double height.
        p.walls(18,1,34,72,37,87,STONE);p.box(18,0,34,72,0,87,TRIM);
        p.walls(18,1,34,31,30,87,STONE);p.walls(59,1,34,72,30,87,STONE);
        opening(p,cx,1,34,5,14,false,false);
        for(int x:new int[]{18,72})for(int z=40;z<=82;z+=8){
            opening(p,z,5,x,2,9,true,true);opening(p,z,18,x,2,9,true,true);opening(p,z,30,x,1,6,true,true);p.box(x==18?17:73,1,z-3,x==18?17:73,29,z-3,TRIM);
        }
        for(int x=23;x<=67;x+=7){opening(p,x,16,34,2,13,false,true);opening(p,x,15,87,2,15,false,true);}
        rose(p,cx,30,34,6);
        // Broad central nave, throne, red carpet, balconies with stairs.
        floor(p,32,35,58,86);
        for(int z=35;z<=80;z++)for(int x=43;x<=47;x++)p.put(x,1,z,Blocks.RED_CARPET);
        for(int z=40;z<=80;z+=8)for(int x:new int[]{33,57}){column(p,x,z,1,26);statue(p,x+(x==33?2:-2),1,z);p.lantern(x+(x==33?2:-2),1,z+2);}
        p.box(39,1,77,51,1,85,TRIM);p.box(42,2,80,48,2,84,EDGE);p.box(43,3,82,47,7,83,TRIM);p.box(44,3,81,46,3,81,Blocks.RED_WOOL);p.box(44,4,81,46,6,81,Blocks.RED_WOOL);
        for(int x:new int[]{43,47})p.put(x,4,80,Blocks.GOLD_BLOCK);
        for(int x:new int[]{35,55}){p.box(x-2,12,37,x+2,12,84,TRIM);for(int z=38;z<=84;z++)p.put(x==35?37:53,13,z,Blocks.IRON_BARS);}
        for(int x=35;x<=55;x++)p.put(x,12,84,TRIM);
        // two interior stairs to the balcony, side room door openings
        for(int k=0;k<12;k++)for(int x:new int[]{34,35,55,56})p.stair(x,1+k,37+k,Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS,Direction.SOUTH);
        for(int x:new int[]{31,59})for(int z:new int[]{44,64,80}){opening(p,z,1,x,2,7,true,false);opening(p,z,13,x,2,7,true,false);}
        room(p,19,35,30,58,0,0);room(p,19,59,30,86,0,1);
        room(p,60,35,71,58,0,1);room(p,60,59,71,86,0,2);
        room(p,19,35,30,58,12,2);room(p,19,59,30,86,12,0);
        room(p,60,35,71,58,12,2);room(p,60,59,71,86,12,2);
        for(int x:new int[]{19,60}){p.box(x,24,35,x+11,24,86,TRIM);for(int z=40;z<=82;z+=8)p.lantern(x+5,25,z);}
        // Chapel annex at rear, pews and stained glass, no chests.
        p.box(36,0,87,54,0,97,TRIM);p.walls(36,1,87,54,16,97,STONE);opening(p,cx,1,87,3,8,false,false);opening(p,cx,3,97,5,12,false,true);opening(p,cx,1,93,7,13,false,false);
        pews(p,38,42,90,94,1);pews(p,48,52,90,94,1);altar(p,cx,95,1);
        for(int z=87;z<=97;z++)for(int k=0;k<=9;k++){p.put(36+k,16+k,z,ROOF);p.put(54-k,16+k,z,ROOF);}
        // Keep roof, flying buttresses, towers with tapered Gothic spires.
        for(int z=33;z<=88;z++)for(int k=0;k<=27;k++){p.put(18+k,37+k/2,z,ROOF);p.put(72-k,37+k/2,z,ROOF);}
        for(int k=0;k<=27;k++){p.box(18+k,37,34,18+k,37+k/2,34,STONE);p.box(72-k,37,34,72-k,37+k/2,34,STONE);p.box(18+k,37,87,18+k,37+k/2,87,STONE);p.box(72-k,37,87,72-k,37+k/2,87,STONE);}
        for(int x:new int[]{20,70})for(int z:new int[]{36,85}){tower(p,x,z,6,53,0);opening(p,x,1,z==36?42:79,2,8,false,false);}
        for(int z=42;z<=81;z+=10){p.put(cx,36,z,Blocks.CHAIN);p.box(cx,29,z,cx,35,z,Blocks.CHAIN);p.lantern(cx,28,z);for(int x:new int[]{26,64})spire(p,x,z,43,2,12);}
        // Highest central turret is a decorative spire above the roof.
        spire(p,cx,61,50,6,23);
        return p;
    }
    static class Job{
        final ServerLevel l;final UUID player;final Plan p;final BlockPos origin;final Direction forward,right;
        int scan=0,built=0;boolean ready=false;Iterator<Map.Entry<Integer,BlockState>> it;
        Job(ServerLevel l,ServerPlayer player,Plan p,BlockPos origin,Direction forward){this.l=l;this.player=player.getUUID();this.p=p;this.origin=origin;this.forward=forward;right=forward.getCounterClockWise();}
        BlockPos pos(int x,int y,int z){return origin.offset(right.getStepX()*x+forward.getStepX()*z,y,right.getStepZ()*x+forward.getStepZ()*z);}
        void msg(String s){ServerPlayer pl=l.getServer().getPlayerList().getPlayer(player);if(pl!=null)pl.sendSystemMessage(Component.literal(s));}
        void refund(){ServerPlayer pl=l.getServer().getPlayerList().getPlayer(player);if(pl!=null&&!pl.getAbilities().instabuild){var item=new net.minecraft.world.item.ItemStack(p.w==91?Noctis.CASTLE_EGG.get():Noctis.CATHEDRAL_EGG.get());if(!pl.getInventory().add(item))pl.drop(item,false);}}
        boolean step(){
            int area=p.w*p.d,total=area*p.h;
            if(!ready){
                for(int n=0;n<18000&&scan<total;n++,scan++){
                    int y=scan/area,z=scan%area/p.w,x=scan%p.w;BlockPos at=pos(x,y,z);
                    if(!l.hasChunkAt(at)||!l.getBlockState(at).isAir()){msg("Evocazione annullata: area occupata o non caricata a "+at.toShortString()+". Cerca una pianura libera.");refund();return true;}
                }
                if(scan<total)return false;
                // Foundation must not replace non-air blocks: existing ground remains untouched.
                for(int x=8;x<p.w-8;x+=10)for(int z=8;z<p.d-8;z+=10){
                    boolean support=false;for(int y=-1;y>=-3;y--)if(l.getBlockState(pos(x,y,z)).isFaceSturdy(l,pos(x,y,z),Direction.UP)){support=true;break;}
                    if(!support){msg("Terreno troppo irregolare o sospeso. Scegli una pianura.");refund();return true;}
                }
                ready=true;it=p.blocks.entrySet().iterator();msg("Spazio libero. Inizia l'evocazione di "+p.name+"...");
            }
            for(int n=0;n<1800&&it.hasNext();n++){
                var e=it.next();int k=e.getKey(),y=k/area-3,z=k%area/p.w,x=k%p.w;BlockPos at=pos(x,y,z);
                if(!l.hasChunkAt(at)){msg("Costruzione interrotta: un chunk non e' piu caricato. La parte gia costruita rimane.");return true;}
                if(!l.getBlockState(at).isAir())continue;
                // Rotate directional states with placement orientation (local north = opposite forward).
                BlockState state=e.getValue();Rotation rotation=switch(forward){case SOUTH->Rotation.NONE;case WEST->Rotation.CLOCKWISE_90;case NORTH->Rotation.CLOCKWISE_180;case EAST->Rotation.COUNTERCLOCKWISE_90;default->Rotation.NONE;};
                l.setBlock(at,state.rotate(rotation),2);built++;
            }
            if(it.hasNext())return false;
            msg(p.name+" completato! "+built+" blocchi posati. Nessun bottino aggiunto.");
            return true;
        }
    }
    @Mod.EventBusSubscriber(modid=Noctis.ID)
    public static class Jobs{
        static final ArrayDeque<Job> queue=new ArrayDeque<>();
        @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(e.phase==TickEvent.Phase.END&&!queue.isEmpty()&&queue.peek().step())queue.remove();}
        @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){queue.clear();}
    }
}''',encoding='utf-8')
for name,castle in [('cathedral_egg',False),('castle_egg',True)]:
    W=32;pix=bytearray()
    for y in range(W):
        pix.append(0)
        for x in range(W):
            u=(x-15.5)/13;v=(y-16)/15
            if u*u+v*v>1 or y<3:pix.extend((0,0,0,0));continue
            c=(28,24,39) if castle else (49,45,62)
            if u*u+v*v>.81:c=(163,135,83)
            elif 7<x<25 and 8<y<25:
                if castle:
                    if (x in (9,10,21,22) and y>9) or (12<=x<=19 and y>13):c=(185,177,194)
                    if y<15 and abs(x-15)<(y-7)/2:c=(120,113,142)
                else:
                    if (x in (9,10,21,22) and y>8) or (11<x<21 and y>11):c=(207,196,181)
                    if (x-16)**2+(y-15)**2<9:c=(137,58,137)
                if 14<=x<=17 and y>=20:c=(32,27,48)
            pix.extend((*c,255))
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    (assets/'textures/item'/f'{name}.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(pix))+chunk(b'IEND',b''))
    (assets/'models/item'/f'{name}.json').write_text(json.dumps({"parent":"minecraft:item/generated","textures":{"layer0":"noctismagic:item/"+name}}))
for lang in ('it_it','en_us'):
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'))
    d['item.noctismagic.cathedral_egg']='Uovo della Cattedrale di Santa Lacrimosa' if lang=='it_it' else 'Santa Lacrimosa Cathedral Egg'
    d['item.noctismagic.castle_egg']='Uovo del Castello di Valdracula' if lang=='it_it' else 'Valdracula Castle Egg'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Gothic monuments: cathedral 61x91x66, castle 91x101x76; staged safe placement')
