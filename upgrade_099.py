"""0.9.9: cinematic physical Shenron and a responsive wish catalogue."""
from pathlib import Path
import sys,struct,zlib,math
root=Path(sys.argv[1]);java=root/'src/main/java/it/noctis/magic';assets=root/'src/main/resources/assets/noctismagic'
def edit(name,pairs):
    p=java/name;s=p.read_text(encoding='utf-8')
    for a,b in pairs:
        if a not in s:raise ValueError(f'Missing anchor {name}: {a[:120]}')
        s=s.replace(a,b,1)
    p.write_text(s,encoding='utf-8')
edit('Noctis.java',[('.sized(7f,9f).clientTrackingRange(16)','.sized(2.5f,3.5f).clientTrackingRange(16)')])
edit('DragonWish.java',[
('Vec3 dest=p.position().add(horizontal.normalize().scale(10)).add(0,7,0);','''Vec3 dest=null;
        for(int distance:new int[]{22,18,26}){
            Vec3 candidate=p.position().add(horizontal.normalize().scale(distance)).add(0,1,0);
            net.minecraft.core.BlockPos q=net.minecraft.core.BlockPos.containing(candidate);
            if(!l.hasChunkAt(q)||!l.getWorldBorder().isWithinBounds(q))continue;
            if(l.dimension()==Level.OVERWORLD){
                int surface=l.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,q.getX(),q.getZ());
                if(surface>p.getY()+7)continue;
                candidate=new Vec3(candidate.x,Math.max(candidate.y,surface+1),candidate.z);
                if(!l.canSeeSky(net.minecraft.core.BlockPos.containing(candidate)))continue;
            }
            if(candidate.y+29>=l.getMaxBuildHeight())continue;
            dest=candidate;break;
        }
        if(dest==null){Noctis.tell(p,"Trova una pianura o uno spazio aperto davanti a te. Le sfere non sono state consumate.");return;}'''),
('if(!l.noCollision(d)||!l.addFreshEntity(d))','if(!l.addFreshEntity(d))'),
('d.moveTo(dest.x,dest.y,dest.z,p.getYRot()+180,0);','d.moveTo(dest.x,dest.y,dest.z,p.getYRot()+180,0);d.yBodyRot=d.getYRot();d.setYHeadRot(d.getYRot());'),
('p.sendSystemMessage(Component.literal("Shenron: Hai riunito le sette sfere. Esprimi il tuo desiderio. Scrivi shenron in chat per riaprire il menu."));\n        open(p,d);','''p.sendSystemMessage(Component.literal("Le sette sfere risplendono. Shenron sta arrivando..."));
        p.displayClientMessage(Component.literal("SHENRON - Il Drago Divino").withStyle(net.minecraft.ChatFormatting.GOLD),true);'''),
('if(data.hasUUID("dragonWishId")&&l.getEntity(data.getUUID("dragonWishId")) instanceof Shenron d&&d.canWish(p)){open(p,d);return;}','if(data.hasUUID("dragonWishId")&&l.getEntity(data.getUUID("dragonWishId")) instanceof Shenron d){if(d.canWish(p))open(p,d);else Noctis.tell(p,"Shenron sta arrivando...");return;}')
])
edit('Shenron.java',[
('private UUID owner;private long expires;private boolean wished;','private UUID owner;private long expires,revealAt;private boolean wished,announced;'),
('owner=p.getUUID();expires=until;','owner=p.getUUID();expires=until;revealAt=level().getGameTime()+120;announced=false;'),
('&&level().getGameTime()<expires;','&&level().getGameTime()<expires&&level().getGameTime()>=revealAt;'),
('super.tick();setNoGravity(true);setDeltaMovement(0,0,0);','super.tick();setNoGravity(true);noPhysics=true;setDeltaMovement(0,0,0);yBodyRot=getYRot();yBodyRotO=getYRot();'),
('if(tickCount%8==0)l.sendParticles','''if(!announced&&l.getGameTime()>=revealAt&&owner!=null&&l.getPlayerByUUID(owner) instanceof ServerPlayer sp&&canWish(sp)){
            announced=true;
            sp.sendSystemMessage(net.minecraft.network.chat.Component.literal("Shenron: Hai riunito le sette sfere. Esprimi il tuo desiderio. Scrivi shenron in chat per riaprire il menu."));
            sp.displayClientMessage(net.minecraft.network.chat.Component.literal("Esprimi un desiderio").withStyle(net.minecraft.ChatFormatting.GOLD),true);
            DragonWish.open(sp,this);
        }
        if(!announced&&tickCount%4==0){
            double a=tickCount*.22;
            l.sendParticles(ParticleTypes.ELECTRIC_SPARK,getX()+Math.cos(a)*5,getY()+Math.min(18,tickCount*.17),getZ()+Math.sin(a)*5,12,1,1,1,.08);
            l.sendParticles(ParticleTypes.END_ROD,getX(),getY()+3,getZ(),12,2,3,2,.06);
        }
        if(tickCount%8==0)l.sendParticles'''),
('t.putLong("Expires",expires);','t.putLong("Expires",expires);t.putLong("RevealAt",revealAt);t.putBoolean("Announced",announced);'),
('expires=t.getLong("Expires");','expires=t.getLong("Expires");revealAt=t.getLong("RevealAt");announced=t.getBoolean("Announced");')
])
edit('ShenronRenderer.java',[
('pose.scale(2.7f,2.7f,2.7f);','float t=Math.min(1,(e.tickCount+partial)/85f);float scale=5.4f*(.12f+.88f*(1-(1-t)*(1-t)));pose.scale(scale,scale,scale);'),
('    static CubeListBuilder c(int u,int v)','''    @Override public boolean shouldRender(Shenron e,net.minecraft.client.renderer.culling.Frustum f,double x,double y,double z){return x*x+y*y+z*z<16384;}
    static CubeListBuilder c(int u,int v)'''),
('float[] point(float n,float age){double a=n*.40+age*.012;float radius=21-n*.29f;return new float[]{(float)Math.sin(a)*radius,-29+n*2.15f+(float)Math.sin(age*.08+n*.3)*1.6f,(float)Math.cos(a)*radius};}','''float[] point(float n,float age){
            if(n<=3)return new float[]{(float)Math.sin(age*.055+n*.2)*.6f,8-n*4+(float)Math.sin(age*.06)*.6f,-22+n*6};
            float k=n-3;double a=k*.36;float radius=20-k*.23f;
            return new float[]{(float)Math.sin(a)*radius+(float)Math.sin(age*.055+k*.3)*.9f,-4-k*1.8f+(float)Math.sin(age*.065+k*.2)*1.4f,16-(float)Math.cos(a)*radius};
        }'''),
('head.setPos(p[0],p[1]-2,p[2]);head.yRot=(float)Math.atan2(q[0]-p[0],q[2]-p[2]);','head.setPos(p[0],p[1]-2,p[2]-1);head.yRot=0;'),
('for(int s:new int[]{-1,1})head.getChild("whisker"+s).zRot','for(int s:new int[]{-1,1})head.getChild("whisker"+s).zRot'),
('h.addOrReplaceChild("jaw",','''for(int i=0;i<6;i++){float x=-4+i*1.6f;h.addOrReplaceChild("mane"+i,c(40,0).addBox(-.75f,-3,-.8f,1.5f,5,1.6f),PartPose.offsetAndRotation(x,-4,3,-.65f,0,(i-2.5f)*.11f));}
        h.addOrReplaceChild("jaw",''')
])
# Responsive icon grid, keyboard search, selected item preview, page controls,
# deliberately translucent backdrop so the real entity remains visible behind it.
p=java/'DragonClient.java';s=p.read_text(encoding='utf-8');start=s.index('    static class WishScreen');s=s[:start]+'''    static class WishScreen extends Screen{
        final UUID dragon;EditBox search;Button prev,next,confirm,close;
        List<Item> all,filtered;Item selected;int page=0,cols,rows,capacity,x,y,w,h,gx,gy,detailX;boolean compact;
        static final int CELL=22;
        WishScreen(UUID id){super(Component.literal("SHENRON"));}
        {dragon=null;}
        @Override protected void init(){
            all=ForgeRegistries.ITEMS.getValues().stream().filter(i->i!=Items.AIR).sorted(Comparator.comparing(i->new ItemStack(i).getHoverName().getString(),String.CASE_INSENSITIVE_ORDER)).toList();
            filtered=all;compact=width<420;w=Math.min(width-16,compact?340:430);h=Math.min(height-12,252);x=(width-w)/2;y=(height-h)/2;
            int detail=compact?0:128;cols=Math.max(3,(w-24-detail)/CELL);rows=Math.max(1,(h-(compact?129:101))/CELL);capacity=cols*rows;gx=x+12;gy=y+66;detailX=gx+cols*CELL+8;
            search=new EditBox(font,x+12,y+42,w-24,19,Component.literal("Cerca oggetto"));search.setMaxLength(100);search.setHint(Component.literal("Cerca nome o ID della mod..."));addRenderableWidget(search);
            int navY=gy+rows*CELL+3;
            prev=addRenderableWidget(Button.builder(Component.literal("<"),b->{page--;refresh();}).bounds(gx,navY,24,18).build());
            next=addRenderableWidget(Button.builder(Component.literal(">"),b->{page++;refresh();}).bounds(gx+cols*CELL-24,navY,24,18).build());
            confirm=addRenderableWidget(Button.builder(Component.literal("ESAUDISCI IL DESIDERIO"),b->{if(selected!=null){ResourceLocation id=ForgeRegistries.ITEMS.getKey(selected);if(id!=null){Noctis.NET.sendToServer(new DragonWish.Wish(dragon,id.toString()));onClose();}}}).bounds(x+12,y+h-26,w-54,20).build());
            close=addRenderableWidget(Button.builder(Component.literal("X"),b->onClose()).bounds(x+w-36,y+h-26,24,20).build());
            search.setResponder(s->{String q=s.toLowerCase(Locale.ROOT).trim();filtered=all.stream().filter(i->{ResourceLocation id=ForgeRegistries.ITEMS.getKey(i);return new ItemStack(i).getHoverName().getString().toLowerCase(Locale.ROOT).contains(q)||id!=null&&id.toString().contains(q);}).toList();page=0;selected=null;refresh();});
            refresh();
        }
        void refresh(){page=Math.max(0,Math.min(page,Math.max(0,(filtered.size()-1)/capacity)));prev.active=page>0;next.active=(page+1)*capacity<filtered.size();confirm.active=selected!=null;}
        int indexAt(double mx,double my){if(mx<gx||my<gy||mx>=gx+cols*CELL||my>=gy+rows*CELL)return -1;int n=page*capacity+(int)((my-gy)/CELL)*cols+(int)((mx-gx)/CELL);return n<filtered.size()?n:-1;}
        @Override public boolean mouseClicked(double mx,double my,int b){int n=indexAt(mx,my);if(b==0&&n>=0){selected=filtered.get(n);search.setFocused(false);refresh();return true;}return super.mouseClicked(mx,my,b);}
        @Override public boolean mouseScrolled(double mx,double my,double delta){if(indexAt(mx,my)>=0||(mx>=gx&&mx<gx+cols*CELL&&my>=gy&&my<gy+rows*CELL)){page+=delta<0?1:-1;refresh();return true;}return super.mouseScrolled(mx,my,delta);}
        @Override public void render(GuiGraphics g,int mx,int my,float partial){
            g.fill(0,0,width,height,0x35000D08);
            g.fill(x-2,y-2,x+w+2,y+h+2,0xAA07120D);
            g.fill(x,y,x+w,y+h,0xE90A211A);
            g.renderOutline(x,y,w,h,0xFFBC934C);g.renderOutline(x+3,y+3,w-6,h-6,0xFF416A4B);
            g.drawCenteredString(font,"S H E N R O N",width/2,y+9,0xFFFFD987);
            g.drawCenteredString(font,"Le sette sfere hanno risposto al tuo richiamo.",width/2,y+22,0xFFCFD9B9);
            for(int i=0;i<7;i++)g.renderItem(new ItemStack(Noctis.DRAGON_BALLS.get(i).get()),x+w/2-56+i*16,y+29);
            int hover=indexAt(mx,my);
            for(int i=0;i<capacity;i++){
                int n=page*capacity+i,sx=gx+i%cols*CELL,sy=gy+i/cols*CELL;
                g.fill(sx,sy,sx+20,sy+20,0xFF193D30);g.renderOutline(sx,sy,20,20,0xFF456B50);
                if(n>=filtered.size())continue;
                Item item=filtered.get(n);if(item==selected||n==hover){g.fill(sx,sy,sx+20,sy+20,0xFF4A5834);g.renderOutline(sx,sy,20,20,item==selected?0xFFFFD270:0xFFB3D1A0);}
                g.renderItem(new ItemStack(item),sx+2,sy+2);
            }
            if(filtered.isEmpty())g.drawCenteredString(font,"Nessun oggetto trovato",gx+cols*CELL/2,gy+5,0xFFFFD987);
            int navY=gy+rows*CELL+3;
            g.drawCenteredString(font,(page+1)+" / "+Math.max(1,(filtered.size()+capacity-1)/capacity),gx+cols*CELL/2,navY+5,0xFFE3D5A8);
            if(!compact){
                int dw=x+w-12-detailX;g.fill(detailX,gy,detailX+dw,y+h-33,0xFF102C22);g.renderOutline(detailX,gy,dw,y+h-33-gy,0xFF55764D);
                g.drawCenteredString(font,"IL TUO DESIDERIO",detailX+dw/2,gy+7,0xFFFFD987);
                if(selected!=null){
                    g.pose().pushPose();g.pose().translate(detailX+dw/2f-20,gy+22,0);g.pose().scale(2.5f,2.5f,1);g.renderItem(new ItemStack(selected),0,0);g.pose().popPose();
                    g.drawWordWrap(font,new ItemStack(selected).getHoverName(),detailX+6,gy+66,dw-12,0xFFFAEBD0);
                    ResourceLocation id=ForgeRegistries.ITEMS.getKey(selected);if(id!=null)g.drawWordWrap(font,Component.literal(id.getNamespace()),detailX+6,gy+91,dw-12,0xFF9FBFA0);
                }else g.drawWordWrap(font,Component.literal("Scegli un oggetto nella griglia. Potrai riceverne uno solo."),detailX+6,gy+26,dw-12,0xFFB6C8A4);
            }else if(selected!=null)g.drawCenteredString(font,font.plainSubstrByWidth(new ItemStack(selected).getHoverName().getString(),w-24),width/2,navY+22,0xFFFFD987);
            super.render(g,mx,my,partial);
            if(hover>=0)g.renderTooltip(font,new ItemStack(filtered.get(hover)),mx,my);
        }
        @Override public boolean isPauseScreen(){return false;}
    }
}
''';s=s.replace('WishScreen(UUID id){super(Component.literal("SHENRON"));}\n        {dragon=null;}','WishScreen(UUID id){super(Component.literal("SHENRON"));dragon=id;}');p.write_text(s,encoding='utf-8')
# detailed scaled atlas; UVs remain 128x128, image is 512x512.
p=assets/'textures/entity/shenron.png';pix=[]
for y in range(512):
    row=[]
    for x in range(512):
        u,v=x//4,y//4
        if 80<=u<96 and 48<=v<56:
            rgb=(250,46,33) if x%12<9 else (100,5,12)
        elif 96<=u<112 and v<24:
            rgb=(219-(x%9)*3,175-(x%9)*2,101-(x%9)*2)
        elif u>=112 and v<20:rgb=(178,204,149)
        elif 40<=u<72 and v<24:rgb=(156+(x%7)*4,105+(x%7)*3,49)
        elif (v>=24 and v<41 and u<40) or (42<=u<77 and 64<=v<77):
            seam=y%9==0;rgb=(125,87,33) if seam else (234-(y%9)*4,189-(y%9)*4,92-(y%9)*3)
        else:
            sx=(x+(y//9%2)*6)%12;sy=y%9;seam=sy==0 or sx==0 or (sy==8 and sx<3)
            rgb=(20,62,38) if seam else (31+sy*3,103+sy*5,58+sy*2)
        row.append(bytes((*rgb,255)))
    pix.append(b'\0'+b''.join(row))
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',512,512,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(pix)))+chunk(b'IEND',b''))
print('Noctis 0.9.9: physical cinematic Shenron and wish grid installed')
