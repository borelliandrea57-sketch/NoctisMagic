"""Noctis 0.9.4: seven Dragon Balls, giant Shenron and a searchable item wish."""
from pathlib import Path
import sys,json,struct,zlib,math
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';res=root/'src/main/resources';assets=res/'assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
def write(name,s):(java/name).write_text(s,encoding='utf-8')
def j(path,d):
    p=res/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
edit('Noctis.java',[
('public static final RegistryObject<EntityType<Admirer>> WAIFU=', '''public static final RegistryObject<EntityType<Shenron>> SHENRON=ENTITIES.register("shenron",()->EntityType.Builder.<Shenron>of(Shenron::new,MobCategory.MISC).sized(7f,9f).clientTrackingRange(16).build(ID+":shenron"));
    public static final java.util.List<RegistryObject<Item>> DRAGON_BALLS=DragonWish.registerBalls();
    public static final RegistryObject<EntityType<Admirer>> WAIFU='''),
('e.put(WAIFU.get(),Admirer.attributes(30).build());','e.put(SHENRON.get(),Shenron.attributes().build());e.put(WAIFU.get(),Admirer.attributes(30).build());'),
('e.accept(CRYSTAL.get());','for(var ball:DRAGON_BALLS)e.accept(ball.get());e.accept(CRYSTAL.get());'),
('NET.messageBuilder(State.class,1,','DragonWish.registerNetwork();\n        NET.messageBuilder(State.class,1,'),
('()->"2","2"::equals,"2"::equals','()->"3","3"::equals,"3"::equals')
])
write('DragonWish.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.animal.TamableAnimal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.*;
import net.minecraftforge.registries.*;
@Mod.EventBusSubscriber(modid=Noctis.ID)
public class DragonWish {
    static java.util.List<RegistryObject<Item>> registerBalls(){
        java.util.List<RegistryObject<Item>> list=new ArrayList<>();
        for(int n=1;n<=7;n++){final int stars=n;list.add(Noctis.ITEMS.register("dragon_ball_"+n,()->new Ball(stars)));}
        return java.util.List.copyOf(list);
    }
    record Open(UUID dragon){}
    record Wish(UUID dragon,String item){}
    public static class ClientState{public static UUID pending;}
    static void registerNetwork(){
        Noctis.NET.messageBuilder(Open.class,2,NetworkDirection.PLAY_TO_CLIENT).encoder((m,b)->b.writeUUID(m.dragon())).decoder(b->new Open(b.readUUID())).consumerMainThread((m,c)->{ClientState.pending=m.dragon();c.get().setPacketHandled(true);}).add();
        Noctis.NET.messageBuilder(Wish.class,3,NetworkDirection.PLAY_TO_SERVER).encoder((m,b)->{b.writeUUID(m.dragon());b.writeUtf(m.item(),256);}).decoder(b->new Wish(b.readUUID(),b.readUtf(256))).consumerMainThread((m,c)->{ServerPlayer p=c.get().getSender();if(p!=null)grant(p,m);c.get().setPacketHandled(true);}).add();
    }
    static void open(ServerPlayer p,Shenron d){Noctis.NET.send(PacketDistributor.PLAYER.with(()->p),new Open(d.getUUID()));}
    @SubscribeEvent public static void drops(LivingDropsEvent e){
        if(!(e.getEntity() instanceof Mob mob)||mob instanceof Shenron||mob instanceof Raiden||mob.level().isClientSide)return;
        Entity killer=e.getSource().getEntity();ServerPlayer p=null;
        if(killer instanceof ServerPlayer sp)p=sp;else if(killer instanceof TamableAnimal tame&&tame.getOwner() instanceof ServerPlayer sp)p=sp;
        if(p==null||mob.getRandom().nextFloat()>=.05f)return;
        ItemStack stack=new ItemStack(Noctis.DRAGON_BALLS.get(mob.getRandom().nextInt(7)).get());
        e.getDrops().add(new ItemEntity(mob.level(),mob.getX(),mob.getY()+.3,mob.getZ(),stack));
    }
    static class Ball extends Item{
        final int stars;Ball(int n){super(new Item.Properties().rarity(Rarity.RARE).stacksTo(16));stars=n;}
        @Override public boolean isFoil(ItemStack s){return true;}
        @Override public InteractionResultHolder<ItemStack> use(Level l,Player p,InteractionHand h){
            if(p instanceof ServerPlayer sp)invoke(sp);
            return InteractionResultHolder.sidedSuccess(p.getItemInHand(h),l.isClientSide);
        }
    }
    static int count(Player p,Item item){int n=0;for(int i=0;i<p.getInventory().getContainerSize();i++){ItemStack s=p.getInventory().getItem(i);if(s.is(item))n+=s.getCount();}return n;}
    static void take(Player p,Item item){for(int i=0;i<p.getInventory().getContainerSize();i++){ItemStack s=p.getInventory().getItem(i);if(s.is(item)){s.shrink(1);p.getInventory().setChanged();return;}}}
    static void invoke(ServerPlayer p){
        if(p.isSpectator()||!p.isAlive())return;
        ServerLevel l=p.serverLevel();var data=Noctis.data(p);
        if(data.getLong("dragonWishUntil")>l.getGameTime()){if(data.hasUUID("dragonWishId")&&l.getEntity(data.getUUID("dragonWishId")) instanceof Shenron d&&d.canWish(p)){open(p,d);return;}Noctis.tell(p,"Shenron e' gia' stato evocato.");return;}
        int missing=0;StringBuilder sb=new StringBuilder();
        for(int i=0;i<7;i++)if(count(p,Noctis.DRAGON_BALLS.get(i).get())==0){if(missing++>0)sb.append(", ");sb.append(i+1);}
        if(missing>0){Noctis.tell(p,"Sfere mancanti: "+sb+" stelle.");return;}
        Vec3 look=p.getLookAngle();Vec3 horizontal=new Vec3(look.x,0,look.z);if(horizontal.lengthSqr()<.001)horizontal=new Vec3(0,0,1);
        Vec3 dest=p.position().add(horizontal.normalize().scale(10)).add(0,7,0);
        if(dest.y+10>l.getMaxBuildHeight()||!l.hasChunkAt(net.minecraft.core.BlockPos.containing(dest))){Noctis.tell(p,"Trova uno spazio aperto per evocare Shenron.");return;}
        Shenron d=Noctis.SHENRON.get().create(l);if(d==null)return;
        d.moveTo(dest.x,dest.y,dest.z,p.getYRot()+180,0);d.bind(p,l.getGameTime()+3600);
        if(!l.noCollision(d)||!l.addFreshEntity(d)){Noctis.tell(p,"Non c'e' abbastanza spazio per il drago.");return;}
        for(var ball:Noctis.DRAGON_BALLS)take(p,ball.get());
        data.putUUID("dragonWishId",d.getUUID());data.putLong("dragonWishUntil",l.getGameTime()+3600);
        l.sendParticles(ParticleTypes.END_ROD,d.getX(),d.getY()+4,d.getZ(),130,3,4,3,.15);
        l.sendParticles(ParticleTypes.ELECTRIC_SPARK,d.getX(),d.getY()+3,d.getZ(),100,3,3,3,.15);
        d.playSound(net.minecraft.sounds.SoundEvents.ENDER_DRAGON_GROWL,2,.65f);
        p.sendSystemMessage(Component.literal("Shenron: Hai riunito le sette sfere. Esprimi il tuo desiderio."));
        open(p,d);
    }
    static void grant(ServerPlayer p,Wish wish){
        ServerLevel l=p.serverLevel();if(p.isSpectator()||!p.isAlive())return;
        if(!(l.getEntity(wish.dragon()) instanceof Shenron d)||!d.canWish(p))return;
        ResourceLocation id=ResourceLocation.tryParse(wish.item());if(id==null)return;
        Item item=ForgeRegistries.ITEMS.getValue(id);if(item==null||item==Items.AIR)return;
        d.fulfill();ItemStack reward=new ItemStack(item,1);Component name=reward.getHoverName();
        if(!p.getInventory().add(reward))p.drop(reward,false);
        Noctis.data(p).putLong("dragonWishUntil",l.getGameTime()+60);
        p.sendSystemMessage(Component.literal("Shenron: Il tuo desiderio e' stato esaudito: ").append(name));
        l.sendParticles(ParticleTypes.TOTEM_OF_UNDYING,p.getX(),p.getY()+1,p.getZ(),55,.7,.8,.7,.05);
        d.playSound(net.minecraft.sounds.SoundEvents.ENDER_DRAGON_GROWL,1.5f,.9f);
    }
}'''.replace('import net.minecraft.world.entity.animal.TamableAnimal;','import net.minecraft.world.entity.TamableAnimal;'))
write('Shenron.java','''package it.noctis.magic;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
public class Shenron extends PathfinderMob{
    private UUID owner;private long expires;private boolean wished;
    public Shenron(EntityType<? extends PathfinderMob> t,Level l){super(t,l);setNoGravity(true);setPersistenceRequired();noPhysics=true;}
    public static AttributeSupplier.Builder attributes(){return Mob.createMobAttributes().add(Attributes.MAX_HEALTH,500).add(Attributes.MOVEMENT_SPEED,0);}
    @Override protected void registerGoals(){}
    public void bind(ServerPlayer p,long until){owner=p.getUUID();expires=until;}
    public boolean canWish(ServerPlayer p){return owner!=null&&owner.equals(p.getUUID())&&!wished&&isAlive()&&distanceToSqr(p)<4096&&level().getGameTime()<expires;}
    public void fulfill(){wished=true;expires=level().getGameTime()+60;}
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){if(p instanceof ServerPlayer sp&&canWish(sp))DragonWish.open(sp,this);return InteractionResult.sidedSuccess(level().isClientSide);}
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource s,float amount){return false;}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public void tick(){super.tick();setNoGravity(true);setDeltaMovement(0,0,0);if(level() instanceof ServerLevel l){
        if(tickCount%8==0)l.sendParticles(ParticleTypes.ELECTRIC_SPARK,getX(),getY()+3,getZ(),8,3,3,3,.025);
        if(expires<=0||l.getGameTime()>=expires){l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+4,getZ(),110,3,4,3,.09);discard();}
    }}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(owner!=null)t.putUUID("Owner",owner);t.putLong("Expires",expires);t.putBoolean("Wished",wished);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);if(t.hasUUID("Owner"))owner=t.getUUID("Owner");expires=t.getLong("Expires");wished=t.getBoolean("Wished");}
}''')
write('DragonClient.java','''package it.noctis.magic;
import java.util.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.*;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid=Noctis.ID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
public class DragonClient{
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;Minecraft mc=Minecraft.getInstance();
        if(mc.player==null){DragonWish.ClientState.pending=null;return;}
        if(DragonWish.ClientState.pending!=null&&mc.screen==null){UUID id=DragonWish.ClientState.pending;DragonWish.ClientState.pending=null;mc.setScreen(new WishScreen(id));}
    }
    static class WishScreen extends Screen{
        final UUID dragon;EditBox search;Button prev,next,confirm;
        final List<Button> rows=new ArrayList<>();List<Item> all,filtered;Item selected;int page=0;
        WishScreen(UUID id){super(Component.literal("Shenron - Esprimi un desiderio"));dragon=id;}
        @Override protected void init(){
            all=ForgeRegistries.ITEMS.getValues().stream().filter(i->i!=Items.AIR).sorted(Comparator.comparing(i->new ItemStack(i).getHoverName().getString(),String.CASE_INSENSITIVE_ORDER)).toList();
            filtered=all;rows.clear();int w=Math.min(300,width-24),x=(width-w)/2,y=height/2-88;
            search=new EditBox(font,x,y,w,20,Component.literal("Cerca oggetto"));search.setMaxLength(100);search.setHint(Component.literal("Cerca nome o ID..."));addRenderableWidget(search);
            for(int i=0;i<6;i++){final int idx=i;Button b=Button.builder(Component.empty(),b0->{int n=page*6+idx;if(n<filtered.size()){selected=filtered.get(n);refresh();}}).bounds(x,y+25+i*21,w,20).build();rows.add(b);addRenderableWidget(b);}
            prev=addRenderableWidget(Button.builder(Component.literal("<"),b->{page--;refresh();}).bounds(x,y+153,30,20).build());
            next=addRenderableWidget(Button.builder(Component.literal(">"),b->{page++;refresh();}).bounds(x+w-30,y+153,30,20).build());
            confirm=addRenderableWidget(Button.builder(Component.literal("Esprimi il desiderio"),b->{if(selected!=null){ResourceLocation id=ForgeRegistries.ITEMS.getKey(selected);if(id!=null){Noctis.NET.sendToServer(new DragonWish.Wish(dragon,id.toString()));onClose();}}}).bounds(x,y+178,w,20).build());
            search.setResponder(s->{String q=s.toLowerCase(Locale.ROOT).trim();filtered=all.stream().filter(i->{ResourceLocation id=ForgeRegistries.ITEMS.getKey(i);return new ItemStack(i).getHoverName().getString().toLowerCase(Locale.ROOT).contains(q)||id!=null&&id.toString().contains(q);}).toList();page=0;refresh();});refresh();
        }
        void refresh(){
            page=Math.max(0,Math.min(page,Math.max(0,(filtered.size()-1)/6)));
            for(int i=0;i<rows.size();i++){int n=page*6+i;Button b=rows.get(i);b.visible=n<filtered.size();if(b.visible){Item item=filtered.get(n);b.setMessage(Component.literal(item==selected?"[X] ":"").append(new ItemStack(item).getHoverName()));}}
            prev.active=page>0;next.active=(page+1)*6<filtered.size();confirm.active=selected!=null;
        }
        @Override public void render(GuiGraphics g,int mx,int my,float partial){
            renderBackground(g);g.drawCenteredString(font,title,width/2,height/2-105,0xFFDF88);
            super.render(g,mx,my,partial);
            g.drawCenteredString(font,Component.literal((page+1)+" / "+Math.max(1,(filtered.size()+5)/6)+"  |  "+filtered.size()+" oggetti"),width/2,height/2+70,0xFFFFFF);
            for(int i=0;i<rows.size();i++){int n=page*6+i;Button b=rows.get(i);if(b.visible)g.renderItem(new ItemStack(filtered.get(n)),b.getX()+5,b.getY()+2);}
            if(selected!=null)g.drawCenteredString(font,Component.literal("Desiderio: ").append(new ItemStack(selected).getHoverName()),width/2,height/2+114,0xFFDF88);
        }
        @Override public boolean isPauseScreen(){return false;}
    }
}''')
write('ShenronRenderer.java','''package it.noctis.magic;
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
public class ShenronRenderer extends MobRenderer<Shenron,ShenronRenderer.Model>{
    static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation(Noctis.ID,"shenron"),"main");
    static final ResourceLocation TEX=new ResourceLocation(Noctis.ID,"textures/entity/shenron.png");
    @SubscribeEvent public static void layers(EntityRenderersEvent.RegisterLayerDefinitions e){e.registerLayerDefinition(LAYER,ShenronRenderer::mesh);}
    @SubscribeEvent public static void renderers(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(Noctis.SHENRON.get(),ShenronRenderer::new);}
    ShenronRenderer(EntityRendererProvider.Context c){super(c,new Model(c.bakeLayer(LAYER)),0);}
    @Override public ResourceLocation getTextureLocation(Shenron e){return TEX;}
    @Override protected void scale(Shenron e,PoseStack pose,float partial){pose.scale(2.7f,2.7f,2.7f);}
    static CubeListBuilder c(int u,int v){return CubeListBuilder.create().texOffs(u,v);}
    static LayerDefinition mesh(){
        MeshDefinition m=new MeshDefinition();PartDefinition r=m.getRoot();
        for(int i=0;i<30;i++){
            float size=6.5f-i*.12f;
            PartDefinition b=r.addOrReplaceChild("coil"+i,c(0,0).addBox(-size/2,-size/2,-4,size,size,8).texOffs(0,24).addBox(-size*.37f,size/2-.5f,-4,size*.74f,1,8),PartPose.ZERO);
            b.addOrReplaceChild("spine",c(40,0).addBox(-1,-size/2-2,-2,2,3,4),PartPose.offsetAndRotation(0,0,0,-.3f,0,0));
            if(i==4||i==9)for(int s:new int[]{-1,1}){
                PartDefinition leg=b.addOrReplaceChild("claw"+s,c(40,16).addBox(-1,0,-1,2,5,2).texOffs(52,16).addBox(-1,4,-3,2,2,3),PartPose.offsetAndRotation(s*size*.45f,1,0,-.45f,0,-s*.9f));
                for(int k=0;k<3;k++)leg.addOrReplaceChild("toe"+k,c(64,16).addBox(-.35f,0,-2,.7f,1,2),PartPose.offset(-.8f+k*.8f,5,-2));
            }
        }
        PartDefinition h=r.addOrReplaceChild("head",c(0,48).addBox(-5,-5,-5,10,9,10).texOffs(42,48).addBox(-4,-1,-11,8,4,7),PartPose.ZERO);
        h.addOrReplaceChild("jaw",c(42,64).addBox(-4,0,-10,8,2,7),PartPose.offset(0,3,0));
        for(int s:new int[]{-1,1}){
            h.addOrReplaceChild("eye"+s,c(80,48).addBox(-1.5f,-1.5f,-.6f,3,3,1.2f),PartPose.offsetAndRotation(s*3.5f,-2,-5,0,s*.27f,0));
            h.addOrReplaceChild("brow"+s,c(40,0).addBox(-2,-1,-1,4,2,2),PartPose.offsetAndRotation(s*3.5f,-3.8f,-4.7f,0,0,s*.18f));
            PartDefinition horn=h.addOrReplaceChild("horn"+s,c(96,0).addBox(-1,-6,-1,2,7,2),PartPose.offsetAndRotation(s*3.7f,-4,1,-.6f,0,s*.4f));
            horn.addOrReplaceChild("tip",c(96,12).addBox(-.6f,-4,-.6f,1.2f,5,1.2f),PartPose.offsetAndRotation(0,-5,0,.45f,0,-s*.5f));
            h.addOrReplaceChild("whisker"+s,c(112,0).addBox(s<0?-9:0,-.4f,-.4f,9,.8f,.8f),PartPose.offsetAndRotation(s*4,1,-9,0,s*.25f,s*.35f));
            h.addOrReplaceChild("fang"+s,c(64,16).addBox(-.5f,0,-.5f,1,2.8f,1),PartPose.offset(s*2.8f,2,-9));
        }
        return LayerDefinition.create(m,128,128);
    }
    static class Model extends EntityModel<Shenron>{
        final ModelPart root,head,jaw;final ModelPart[] body=new ModelPart[30];
        Model(ModelPart r){root=r;head=r.getChild("head");jaw=head.getChild("jaw");for(int i=0;i<30;i++)body[i]=r.getChild("coil"+i);}
        float[] point(float n,float age){double a=n*.40+age*.012;float radius=21-n*.29f;return new float[]{(float)Math.sin(a)*radius,-29+n*2.15f+(float)Math.sin(age*.08+n*.3)*1.6f,(float)Math.cos(a)*radius};}
        @Override public void setupAnim(Shenron e,float limb,float amount,float age,float yaw,float pitch){
            for(int i=0;i<30;i++){float[] p=point(i,age),q=point(i+1,age);ModelPart b=body[i];b.setPos(p[0],p[1],p[2]);float dx=q[0]-p[0],dy=q[1]-p[1],dz=q[2]-p[2];b.yRot=(float)Math.atan2(dx,dz);b.xRot=-(float)Math.atan2(dy,Math.sqrt(dx*dx+dz*dz));}
            float[] p=point(-.5f,age),q=point(.5f,age);head.setPos(p[0],p[1]-2,p[2]);head.yRot=(float)Math.atan2(q[0]-p[0],q[2]-p[2]);head.xRot=.08f+(float)Math.sin(age*.07)*.09f;head.yRot+=.15f*(float)Math.sin(age*.05);jaw.xRot=.10f+(float)(1+Math.sin(age*.15))*.07f;
            for(int s:new int[]{-1,1})head.getChild("whisker"+s).zRot=s*(.35f+(float)Math.sin(age*.12)*.18f);
        }
        @Override public void renderToBuffer(PoseStack p,VertexConsumer v,int light,int overlay,float r,float g,float b,float a){root.render(p,v,light,overlay,r,g,b,a);}
    }
}''')
# Pixel art assets: numbered orange spheres and green/gold dragon.
def png(path,w,h,fn):
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    raw=b''.join(b'\0'+bytes(v for x in range(w) for v in fn(x,y)) for y in range(h))
    p=assets/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
positions={1:[(16,16)],2:[(11,16),(21,16)],3:[(16,10),(10,20),(22,20)],4:[(11,11),(21,11),(11,21),(21,21)],5:[(10,10),(22,10),(16,16),(10,22),(22,22)],6:[(10,9),(22,9),(10,16),(22,16),(10,23),(22,23)],7:[(16,16),(16,7),(8,11),(24,11),(8,21),(24,21),(16,25)]}
def ball(x,y,n):
    d=math.hypot(x-15.5,y-15.5)
    if d>14:return (0,0,0,0)
    if d>12.9:return (157,69,12,255)
    for cx,cy in positions[n]:
        dx,dy=x-cx,y-cy
        if (dy==-2 and dx==0) or (dy==-1 and abs(dx)<=2) or (dy==0 and abs(dx)<=1) or (dy==1 and abs(dx)<=1) or (dy==2 and abs(dx)==2):return (164,27,20,255)
    k=max(0,1-math.hypot(x-10,y-7)/22)
    if (x-9)**2+(y-7)**2<5:return (255,248,191,255)
    return (255,int(128+86*k),int(19+68*k),255)
for n in range(1,8):
    png(f'textures/item/dragon_ball_{n}.png',32,32,lambda x,y,n=n:ball(x,y,n))
    j(f'assets/noctismagic/models/item/dragon_ball_{n}.json',{"parent":"minecraft:item/generated","textures":{"layer0":f"noctismagic:item/dragon_ball_{n}"}})
def scales(x,y):
    if 80<=x<96 and 48<=y<55:return (239,48,32,255) if x%4!=2 else (40,10,12,255)
    if 96<=x<128 and y<32:return (215-(x%4)*12,173-(x%4)*10,102-(x%4)*5,255)
    if 40<=x<72 and y<24:return (174,122,53,255)
    if y>=24 and y<40 and x<40:return (223-(y%4)*10,180-(y%4)*9,81-(y%4)*4,255)
    if 42<=x<77 and 64<=y<77:return (190,141,65,255)
    seam=(x+(y//3)*2)%5==0 or y%3==0
    return (32,87,45,255) if seam else (52+(x+y)%4*8,134+(x*y)%4*9,65+(x+y)%3*7,255)
png('textures/entity/shenron.png',128,128,scales)
for lang in ['it_it','en_us']:
    p=assets/'lang'/f'{lang}.json';d=json.loads(p.read_text(encoding='utf-8'));it=lang=='it_it'
    d['entity.noctismagic.shenron']='Shenron'
    for n in range(1,8):d[f'item.noctismagic.dragon_ball_{n}']=f'Sfera del Drago - {n} '+('stella' if n==1 else 'stelle') if it else f'{n}-Star Dragon Ball'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Noctis 0.9.4: Dragon Balls, Shenron, and registry wish screen installed')
