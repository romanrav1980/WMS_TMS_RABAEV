from pathlib import Path
import json
d=Path("db/migrations/2026-10-11_ni053_partial_final_receipt")
s=(d/"000_before_rrl_stock_unit_guard.sql").read_text(encoding="utf-8")
s=s.replace("for each row \nbegin","for each row \ndeclare v_loss_count number;\nbegin",1)
needle="  RRL_STOCK_WRITE_GUARD.require_unit(:old.PHYSICAL_UNIT_KEY,:old.CURRENT_UID);"
assert needle in s
s=s.replace(needle,needle+"\n  select count(*)into v_loss_count from RRL_INTERWARE_SHORTAGE_UNIT where PHYSICAL_UNIT_KEY=:old.PHYSICAL_UNIT_KEY;\n  if v_loss_count!=0 then raise_application_error(-20886,'UNIT_CONFIRMED_CARRIER_LOSS_REQUIRES_CORRECTION');end if;",1)
assert "declare v_loss_count"in s
print(json.dumps({(d/"001_unit_loss_guard.sql").as_posix():s}))
