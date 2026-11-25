"""Compact paginated grimoire screen, independent of the vanilla gray buttons."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'src/main/java/it/noctis/magic/Client.java'
s=p.read_text(encoding='utf-8')
start=s.index('    static class SpellScreen extends Screen')
opening=s.index('{',start)
depth=1;end=opening+1
while depth:
 if s[end]=='{':depth+=1
 elif s[end]=='}':depth-=1
 end+=1
s=s[:start]+'''    static class SpellScreen extends Screen {
        private int page,focus=-1;
        private int left,top,pw,ph,cols,rows,cardW,cardH,gridY,footerY;
        private static final int GOLD=0xFFD7AE68,PURPLE=0xFFCEB4FA,PALE=0xFFF4E9FF,DIM=0xFFAAA0B8;
        SpellScreen(){super(Component.literal("Grimorio innato"));}
        @Override protected void init(){layout();page=Math.min(page,pages()-1);}
        private void layout(){
            pw=Math.min(340,width-12);ph=Math.min(236,height-10);
            left=(width-pw)/2;top=(height-ph)/2;
            cols=pw>=218?2:1;
            cardW=(pw-20-(cols-1)*6)/cols;
            gridY=top+49;footerY=top+ph-24;
            rows=Math.max(1,(footerY-gridY-4)/35);
            cardH=31;
        }
        private int per(){return Math.max(1,cols*rows);}
        private int pages(){return Math.max(1,(Noctis.Spell.values().length+per()-1)/per());}
        private int first(){return page*per();}
        private int last(){return Math.min(Noctis.Spell.values().length,first()+per());}
        private boolean inside(double x,double y,int l,int t,int w,int h){return x>=l&&x<l+w&&y>=t&&y<t+h;}
        private int cardX(int n){return left+10+(n%cols)*(cardW+6);}
        private int cardY(int n){return gridY+(n/cols)*35;}
        private void change(int delta){page=Math.max(0,Math.min(pages()-1,page+delta));focus=-1;}
        private boolean unlocked(Noctis.Spell spell){return spell.level<=Noctis.View.level;}
        private void choose(int index){
            if(index<0||index>=Noctis.Spell.values().length)return;
            if(unlocked(Noctis.Spell.values()[index])){selected=index;onClose();}
        }
        private int color(Noctis.Spell s){
            String n=s.name()+" "+s.label.toLowerCase(java.util.Locale.ROOT);
            if(n.contains("fuoco")||n.contains("FIRE")||n.contains("Dante"))return 0xFFFF9C54;
            if(n.contains("cura")||n.contains("HEAL"))return 0xFF8BE1B1;
            if(n.contains("tele")||n.contains("volo")||n.contains("FLY"))return 0xFF8EC7FF;
            if(n.contains("evoca")||n.contains("SUMMON"))return 0xFFE6BD78;
            return 0xFFC2A2FF;
        }
        private void border(GuiGraphics g,int x,int y,int w,int h,int c){
            g.fill(x,y,x+w,y+1,c);g.fill(x,y+h-1,x+w,y+h,c);
            g.fill(x,y+1,x+1,y+h-1,c);g.fill(x+w-1,y+1,x+w,y+h-1,c);
        }
        private void sigil(GuiGraphics g,int x,int y,int r,int c,int k){
            // Tiny arcane symbols made of pixel geometry; no texture pack needed.
            for(int a=-r;a<=r;a++){
                int reach=r-Math.abs(a);
                g.fill(x-reach,y+a,x+reach+1,y+a+1,c);
            }
            for(int a=-r+2;a<=r-2;a++){
                int reach=r-2-Math.abs(a);
                g.fill(x-reach,y+a,x+reach+1,y+a+1,0xFF252039);
            }
            if(k%4==0){g.fill(x-1,y-4,x+2,y+5,c);g.fill(x-4,y-1,x+5,y+2,c);}
            else if(k%4==1){g.fill(x-3,y-1,x+4,y+2,c);g.fill(x-1,y-3,x+2,y+4,c);}
            else if(k%4==2){for(int a=-3;a<=3;a++)g.fill(x+a,y+a,x+a+2,y+a+1,c);}
            else{g.fill(x-2,y-2,x+3,y+3,c);g.fill(x-1,y-1,x+2,y+2,0xFFF4E7FF);}
        }
        private void arrow(GuiGraphics g,int x,int y,String label,boolean active,boolean hover){
            g.fill(x,y,x+18,y+16,hover&&active?0xFF574064:0xFF272039);
            border(g,x,y,18,16,active?GOLD:0xFF51445D);
            g.drawCenteredString(font,label,x+9,y+4,active?PALE:DIM);
        }
        @Override public void render(GuiGraphics g,int mx,int my,float pt){
            layout();page=Math.min(page,pages()-1);
            renderBackground(g);
            g.fillGradient(left,top,left+pw,top+ph,0xFA20172F,0xFA100F20);
            border(g,left,top,pw,ph,GOLD);border(g,left+3,top+3,pw-6,ph-6,0xFF62496A);
            sigil(g,left+17,top+16,7,GOLD,0);sigil(g,left+pw-17,top+16,7,GOLD,0);
            g.drawCenteredString(font,"GRIMORIO INNATO",width/2,top+9,PURPLE);
            int lv=Noctis.View.level,max=Math.max(1,Noctis.max(lv)),mana=Math.max(0,Math.min(max,Noctis.View.mana));
            String info="Lv "+lv+"   |   MP "+mana+"/"+max;
            g.drawCenteredString(font,info,width/2,top+22,PALE);
            int bx=left+12,bw=pw-24;
            g.fill(bx,top+34,bx+bw,top+39,0xFF35253E);
            if(mana>0)g.fillGradient(bx,top+34,bx+bw*mana/max,top+39,0xFFE0C3FF,0xFF7354BF);
            int xp=lv>=10?bw:Math.max(0,Math.min(bw,bw*Noctis.View.xp/Math.max(1,Noctis.needed(lv))));
            g.fill(bx,top+41,bx+bw,top+43,0xFF3B303E);
            if(xp>0)g.fill(bx,top+41,bx+xp,top+43,GOLD);
            int hovered=-1;
            for(int i=first();i<last();i++){
                Noctis.Spell spell=Noctis.Spell.values()[i];
                int n=i-first(),x=cardX(n),y=cardY(n),c=color(spell);
                boolean over=inside(mx,my,x,y,cardW,cardH),open=unlocked(spell),sel=i==selected;
                if(over)hovered=i;
                g.fillGradient(x,y,x+cardW,y+cardH,open?(over||focus==i?0xFF4E3861:0xFF352842):0xFF25212D,0xFF20192F);
                border(g,x,y,cardW,cardH,sel?GOLD:over?PURPLE:0xFF62506D);
                g.fill(x+1,y+1,x+3,y+cardH-1,open?c:0xFF625769);
                sigil(g,x+15,y+14,8,open?c:0xFF655B70,i);
                String label=font.plainSubstrByWidth(spell.label,Math.max(1,cardW-30));
                g.drawString(font,label,x+27,y+5,open?PALE:DIM);
                String meta=spell.cost+" MP  |  Lv "+spell.level;
                g.drawString(font,font.plainSubstrByWidth(meta,Math.max(1,cardW-29)),x+27,y+18,open?c:0xFFADA0B0);
                if(!open){g.fill(x+8,y+18,x+15,y+25,0xFF63576B);g.fill(x+9,y+15,x+14,y+18,0xFF8F8298);}
            }
            int ay=footerY+2;
            arrow(g,left+10,ay,"<",page>0,inside(mx,my,left+10,ay,18,16));
            arrow(g,left+pw-28,ay,">",page+1<pages(),inside(mx,my,left+pw-28,ay,18,16));
            String status=(page+1)+"/"+pages()+"   |   "+CAST.getTranslatedKeyMessage().getString()+": lancia";
            g.drawCenteredString(font,status,width/2,ay+4,DIM);
            if(hovered>=0){
                Noctis.Spell spell=Noctis.Spell.values()[hovered];
                String detail=spell.label+"  |  "+spell.cost+" MP  |  "+(unlocked(spell)?"Seleziona":"Richiede Lv "+spell.level);
                // Full spell name, shown in a small clamped tooltip instead of covering the other cards.
                int tw=Math.min(width-8,font.width(detail)+8),tx=Math.max(4,Math.min(mx+8,width-tw-4)),ty=Math.max(4,my-17);
                g.fill(tx,ty,tx+tw,ty+13,0xF51B1426);border(g,tx,ty,tw,13,GOLD);
                g.drawString(font,font.plainSubstrByWidth(detail,tw-8),tx+4,ty+2,PALE);
            }
        }
        @Override public boolean mouseClicked(double x,double y,int button){
            if(button!=0)return super.mouseClicked(x,y,button);
            int ay=footerY+2;
            if(inside(x,y,left+10,ay,18,16)){change(-1);return true;}
            if(inside(x,y,left+pw-28,ay,18,16)){change(1);return true;}
            for(int i=first();i<last();i++){int n=i-first();if(inside(x,y,cardX(n),cardY(n),cardW,cardH)){focus=i;choose(i);return true;}}
            return super.mouseClicked(x,y,button);
        }
        @Override public boolean mouseScrolled(double x,double y,double delta){if(delta!=0){change(delta>0?-1:1);return true;}return false;}
        @Override public boolean keyPressed(int key,int scan,int mods){
            if(key==263||key==266){change(-1);return true;}
            if(key==262||key==267){change(1);return true;}
            if(key==264||key==265||key==258){
                if(focus<first()||focus>=last())focus=first();
                else focus=Math.max(first(),Math.min(last()-1,focus+(key==265?-cols:key==264?cols:1)));
                return true;
            }
            if((key==257||key==335)&&focus>=0){choose(focus);return true;}
            return super.keyPressed(key,scan,mods);
        }
        @Override public boolean isPauseScreen(){return false;}
    }'''+s[end:]
p.write_text(s,encoding='utf-8')
print('Paginated grimoire: responsive purple and gold spell cards, locked levels, mana cost, keyboard and scroll navigation.')
