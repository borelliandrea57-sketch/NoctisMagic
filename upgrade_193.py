"""1.7.26: muddy brown swamp, animated flies and supported rotten timber outhouse."""
from pathlib import Path
import sys,math,json,random
from PIL import Image,ImageDraw
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
# Preserve the original block ID so all existing swamp ponds change color too.
im=Image.new('RGBA',(64,64));rng=random.Random(1234)
for y in range(64):
 for x in range(64):
  t=.5+.19*math.sin(x*.28+y*.13)+.17*math.sin(y*.35-x*.12)+rng.uniform(-.08,.08)
  c=tuple(round(a+(b-a)*max(0,min(1,t))) for a,b in zip((52,37,22),(129,104,57)))
  im.putpixel((x,y),(*c,245))
d=ImageDraw.Draw(im)
for i in range(26):
 x,y=rng.randrange(64),rng.randrange(64)
 d.line((x,y,min(63,x+rng.randrange(2,8)),y),fill=(119,99,52,245),width=1)
im.save(assets/'textures/block/atelier_purple.png')
# New rotten planks and mossy split shingles, with cracks and damp streaks.
for n in ('rotwood','shingle','beam'):
 im=Image.new('RGBA',(64,64));rng=random.Random(n)
 for y in range(64):
  for x in range(64):
   row=y//16;u=(x+(row%2)*12)%32;v=y%16
   g=.5+.18*math.sin(x*.8+math.sin(y*.3))+rng.uniform(-.09,.09)
   base=(92,75,46) if n=='rotwood' else (64,70,40) if n=='shingle' else (62,49,32)
   c=tuple(max(0,min(255,round(q*(.75+.5*g)))) for q in base)
   if n!='beam' and (v==0 or u==0):c=(32,29,18)
   if n=='shingle' and v in (1,2):c=tuple(min(255,q+23) for q in c)
   if math.sin(x*.23+y*.13)+math.sin(y*.41-x*.17)>1.30:c=(67,78,39)
   im.putpixel((x,y),(*c,255))
 d=ImageDraw.Draw(im)
 for i in range(10):
  x,y=rng.randrange(3,60),rng.randrange(3,60)
  d.line([(x,y),(min(63,x+3),y),(min(63,x+5),min(63,y+2))],fill=(35,30,20),width=1)
 im.save(assets/'textures/block'/f'swamp_{n}_new.png')
items={'swamp_rotten_planks':('Assi marcescenti','Rotten planks','rotwood'),'swamp_rotten_beam':('Trave marcescente','Rotten timber beam','beam'),'swamp_moss_shingle':('Scandole muschiose','Mossy shingles','shingle')}
decl=[]
for n,(it,en,tex) in items.items():
 decl += [f'    public static final RegistryObject<Block> {n.upper()}=VampireLife.BLOCKS.register("{n}",()->new Block(BlockBehaviour.Properties.of().strength(1.4f,3f)));',f'    public static final RegistryObject<Item> {n.upper()}_ITEM=Noctis.ITEMS.register("{n}",()->new BlockItem({n.upper()}.get(),new Item.Properties()));']
 dump(assets/'models/block'/f'{n}.json',{'parent':'minecraft:block/cube_all','textures':{'all':'noctismagic:block/swamp_'+tex+'_new'}})
 dump(assets/'models/item'/f'{n}.json',{'parent':'noctismagic:block/'+n})
 dump(assets/'blockstates'/f'{n}.json',{'variants':{'':{'model':'noctismagic:block/'+n}}})
 dump(res/'data/noctismagic/loot_tables/blocks'/f'{n}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'noctismagic:'+n}]}]})
p=java/'Furniture.java';s=p.read_text(encoding='utf-8');a='public class Furniture{';assert a in s
s=s.replace(a,a+'\n'+'\n'.join(decl)+'\n',1)
a='new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.065f,.055f,.04f),.45f)';assert a in s
s=s.replace(a,'SwampFlies.FLY',1).replace('for(int i=0;i<4;i++){\n                double a=r.nextDouble()', 'for(int i=0;i<2;i++){\n                double a=r.nextDouble()',1)
s=s.replace('.42,.08,.60);','.37,.28,.12);',1)
a='if(r.nextInt(6)==0)l.addParticle(net.minecraft.core.particles.ParticleTypes.ENTITY_EFFECT'
assert a in s
s=s.replace(a,'if(r.nextInt(4)==0)l.addParticle(SwampFlies.FLY,p.getX()+r.nextDouble(),p.getY()+1.2+r.nextDouble()*.4,p.getZ()+r.nextDouble(),0,.01,0);\n            '+a,1)
p.write_text(s,encoding='utf-8')
# A real custom animated insect particle, registered through the Forge MOD event bus.
(java/'SwampFlies.java').write_text('''package it.noctis.magic;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegisterEvent;
import net.minecraftforge.registries.ForgeRegistries;
@Mod.EventBusSubscriber(modid=Noctis.ID,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class SwampFlies{
 public static final SimpleParticleType FLY=new SimpleParticleType(false);
 @SubscribeEvent public static void register(RegisterEvent e){
  e.register(ForgeRegistries.Keys.PARTICLE_TYPES,h->h.register(new ResourceLocation(Noctis.ID,"swamp_fly"),FLY));
 }
}''',encoding='utf-8')
(java/'SwampFliesClient.java').write_text('''package it.noctis.magic;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.*;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class SwampFliesClient{
 @SubscribeEvent public static void register(RegisterParticleProvidersEvent e){e.registerSpriteSet(SwampFlies.FLY,Provider::new);}
 static final class Provider implements ParticleProvider<SimpleParticleType>{
  private final SpriteSet sprites;
  Provider(SpriteSet sprites){this.sprites=sprites;}
  @Override public Particle createParticle(SimpleParticleType type,ClientLevel level,double x,double y,double z,double dx,double dy,double dz){return new Fly(level,x,y,z,dx,dy,dz,sprites);}
 }
 static final class Fly extends TextureSheetParticle{
  private final SpriteSet sprites;
  private final double cx,cy,cz,phase,radius;
  Fly(ClientLevel l,double x,double y,double z,double dx,double dy,double dz,SpriteSet s){
   super(l,x,y,z,0,0,0);sprites=s;cx=x;cy=y;cz=z;phase=random.nextDouble()*Math.PI*2;radius=.12+random.nextDouble()*.30;
   lifetime=32+random.nextInt(30);quadSize=.075f+random.nextFloat()*.025f;hasPhysics=false;setSpriteFromAge(sprites);
  }
  @Override public void tick(){
   xo=x;yo=y;zo=z;
   if(age++>=lifetime){remove();return;}
   double a=phase+age*.36;
   setPos(cx+radius*Math.sin(a),cy+.16*Math.sin(a*1.7),cz+radius*Math.cos(a));
   setSprite(sprites.get(age%4,3));
  }
  @Override public ParticleRenderType getRenderType(){return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;}
 }
}''',encoding='utf-8')
for i in range(4):
 im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im)
 # Wings flap visibly on alternating frames.
 if i%2==0:
  d.ellipse((1,3,7,8),fill=(201,208,190,190),outline=(110,126,110,170));d.ellipse((9,3,15,8),fill=(201,208,190,190),outline=(110,126,110,170))
 else:
  d.ellipse((3,1,7,10),fill=(214,222,205,190));d.ellipse((9,1,13,10),fill=(214,222,205,190))
 d.ellipse((6,4,10,13),fill=(24,29,23,255));d.ellipse((5,3,11,7),fill=(35,43,28,255));d.point((6,4),fill=(142,42,30,255));d.point((10,4),fill=(142,42,30,255))
 p=assets/'textures/particle'/f'swamp_fly_{i}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
dump(assets/'particles/swamp_fly.json',{'textures':[f'noctismagic:swamp_fly_{i}' for i in range(4)]})
p=java/'Noctis.java';s=p.read_text(encoding='utf-8');a='if(e.getTabKey()==CreativeModeTabs.NATURAL_BLOCKS)';assert a in s
s=s.replace(a,'if(e.getTabKey()==CreativeModeTabs.FUNCTIONAL_BLOCKS){'+''.join('e.accept(Furniture.'+n.upper()+'_ITEM.get());' for n in items)+'}'+a,1);p.write_text(s,encoding='utf-8')
for loc in ('it_it','en_us'):
 p=assets/'lang'/f'{loc}.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['block.noctismagic.swamp_purple_water']='Acqua fangosa della palude' if loc=='it_it' else 'Muddy swamp water'
 for n,(it,en,_) in items.items():d['block.noctismagic.'+n]=it if loc=='it_it' else en
 dump(p,d)
p=java/'GothicEgg.java';s=p.read_text(encoding='utf-8');a=s.index('    static Plan shrekSwamp(){');b=s.index('        return p;',a);sub=s[a:b]
old='for(int k=0;k<3;k++)for(int z=4;z<=10;z++){p.put(23+k,5+k,z,Blocks.SPRUCE_SLAB);p.put(29-k,5+k,z,Blocks.SPRUCE_SLAB);}'
assert old in sub
sub=sub.replace(old,'''// Closed, supported gable: each raised strip stands on a continuous solid row.
        Block rot=Furniture.SWAMP_ROTTEN_PLANKS.get(),beam=Furniture.SWAMP_ROTTEN_BEAM.get(),shingle=Furniture.SWAMP_MOSS_SHINGLE.get();
        p.box(24,0,5,28,0,9,rot);p.walls(24,1,5,28,4,9,rot);
        for(int x:new int[]{24,28})for(int z:new int[]{5,9})p.box(x,1,z,x,4,z,beam);
        swampDoor(p,26,5,Blocks.SPRUCE_DOOR,net.minecraft.world.level.block.state.properties.DoorHingeSide.LEFT);
        p.put(26,3,5,Blocks.OAK_FENCE);
        p.box(24,5,5,28,5,9,beam);
        for(int z=4;z<=10;z++)for(int x=23;x<=29;x++){
            int rise=3-Math.abs(x-26);
            for(int y=5;y<5+rise;y++)p.put(x,y,z,rot);
            p.put(x,5+rise,z,shingle);
        }
        for(int z:new int[]{5,9})for(int x=24;x<=28;x++)p.box(x,4,z,x,4,z,beam);
        for(int z=4;z<=10;z++)if(z%2==0)p.put(26,9,z,Blocks.MOSS_CARPET);
        ''',1)
# Prevent the old interior ceiling line from replacing the supported roof's center.
sub=sub.replace('p.box(25,5,5,27,5,9,Blocks.SPRUCE_PLANKS);','p.box(25,5,5,27,5,9,beam);',1)
# Replace exposed structural timber on the main hut as well, not its furniture or door.
sub=sub.replace('p.box(12,1,10,12,4,10,Blocks.DARK_OAK_LOG);p.box(18,1,10,18,4,10,Blocks.DARK_OAK_LOG);','p.box(12,1,10,12,4,10,Furniture.SWAMP_ROTTEN_BEAM.get());p.box(18,1,10,18,4,10,Furniture.SWAMP_ROTTEN_BEAM.get());')
sub=sub.replace('p.box(12,4,10,18,4,10,Blocks.DARK_OAK_LOG);','p.box(12,4,10,18,4,10,Furniture.SWAMP_ROTTEN_BEAM.get());').replace('p.box(14,3,10,15,3,10,Blocks.DARK_OAK_PLANKS);','p.box(14,3,10,15,3,10,Furniture.SWAMP_ROTTEN_PLANKS.get());')
s=s[:a]+sub+s[b:];p.write_text(s,encoding='utf-8')
print('Brown swamp water (existing ID), animated fly particles, rotten planks and beams, supported moss shingle roof.')
