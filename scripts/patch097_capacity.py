from pathlib import Path
import json
p=Path("db/migrations/2026-10-10_ni062_return_putaway/002_helper.sql")
s=p.read_text(encoding="utf-8-sig")
start=s.index("  from RRL_PALLETS pp where")
end=s.index("  if v_unknown>",start)
s=s[:start]+"""  from (
   select r.UID_POLETA UID_PALLET from RRL_REMAINS r where r.CELL=v_target and r.REMAIN>0 and r.UID_POLETA!=receipt.UID_PALLET
   union
   select wt.UID_PALLET from RRL_WAREHOUSE_TASK wt where wt.TO_CELL=v_target and wt.STATUS not in('DONE','CANCELLED')
    and wt.UID_PALLET!=receipt.UID_PALLET and(p_task is null or wt.TASK_ID!=p_task)
  ) occupants join RRL_PALLETS pp on pp.UID_PALLET=occupants.UID_PALLET;
"""+s[end:]
print(json.dumps({str(p):s},ensure_ascii=True))
