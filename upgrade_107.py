"""1.0.7: private divine chat warning after a successful cabaret transaction."""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'src/main/java/it/noctis/magic/CabaretHealer.java'
s=p.read_text(encoding='utf-8')
a='        l.broadcastEntityEvent(this,(byte)81);'
assert s.count(a)==1
s=s.replace(a,'''        sp.sendSystemMessage(Component.literal("Gesù: GUARDA CHE TI VEDO!").withStyle(net.minecraft.ChatFormatting.GOLD,net.minecraft.ChatFormatting.BOLD));
'''+a,1)
p.write_text(s,encoding='utf-8')
print('Divine chat warning installed')
