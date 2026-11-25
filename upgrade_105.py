"""1.0.5: randomized courtesan dialogue, with anti-spam cooldown."""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'src/main/java/it/noctis/magic/CabaretHealer.java'
s=p.read_text(encoding='utf-8')
def edit(a,b):
    global s
    assert a in s,a
    s=s.replace(a,b,1)
edit('    @Override public InteractionResult mobInteract(Player p,InteractionHand h){','''    private int dialogueCooldown;
    private static final String[] LINES={
        "Cun tre euru faccio tutte cose!",
        "Con 50 pure bocca!",
        "Ue', tesoro, tieni na pepita d'oro?",
        "Vieni qua, ti rimetto in sesto!",
        "Na pepita e passa ogni dolore!",
        "Oggi faccio pure lo sconto!"
    };
    private void speak(ServerPlayer p){
        if(dialogueCooldown>0)return;
        dialogueCooldown=100;
        p.sendSystemMessage(Component.literal(getDisplayName().getString()+": "+LINES[random.nextInt(LINES.length)]));
    }
    @Override public InteractionResult mobInteract(Player p,InteractionHand h){''')
edit('if(!s.is(Items.GOLD_NUGGET)){if(p instanceof ServerPlayer sp&&h==InteractionHand.MAIN_HAND&&s.isEmpty())sp.displayClientMessage(Component.literal("Una pepita d\'oro per cure e benedizioni."),true);return InteractionResult.PASS;}','''if(!s.is(Items.GOLD_NUGGET)){
            if(h==InteractionHand.MAIN_HAND&&s.isEmpty()){
                if(p instanceof ServerPlayer sp)speak(sp);
                return InteractionResult.sidedSuccess(level().isClientSide);
            }
            return InteractionResult.PASS;
        }''')
edit('sp.sendSystemMessage(Component.literal(getDisplayName().getString()+": Ecco le tue cure, tesoro."));','''sp.sendSystemMessage(Component.literal(getDisplayName().getString()+": Ecco le tue cure, tesoro."));''')
edit('if(greeting>0)greeting--;','if(greeting>0)greeting--;if(dialogueCooldown>0)dialogueCooldown--;')
p.write_text(s,encoding='utf-8')
print('Courtesan dialogue installed')
