from pathlib import Path
import json
p=Path("db/migrations/2026-10-12_ni072_prepared_st_deferral/001_physical.sql");s=p.read_text(encoding="utf-8")
anchor="  select count(*),sum(case when nvl(f.FACT_QTY,0)>0"
addition="""  select count(*)into bad from RRL_SBORKA_PALLETS p where p.ST_NUMBER=p_st and(
   exists(select 1 from RRL_INTERWARE_ONWARD_BIND b where b.ST_ID=p.ID)
   or exists(select 1 from RRL_IW_GROUP_ST_BIND b where b.ST_ID=p.ID)
   or exists(select 1 from RRL_IW_RECOVERY_ST_BIND b where b.ST_ID=p.ID));
  if bad!=0 then raise_application_error(-20886,'ST_DEFER_INTERWARE_REVISION_REQUIRED');end if;
"""
assert s.count(anchor)==1;s=s.replace(anchor,addition+anchor)
s=s.replace("t.STATUS TASK_STATUS,t.TASK_TYPE,t.TO_WARE_ID,t.TO_CELL,nvl","t.STATUS TASK_STATUS,t.TASK_TYPE,t.TO_WARE_ID,t.TO_CELL PICKED_CELL,r.CELL TO_CELL,nvl")
s=s.replace("left join RRL_REMAINS r on r.UID_POLETA=f.PICKED_PALLET_UID and r.CELL=t.TO_CELL","left join RRL_REMAINS r on r.UID_POLETA=f.PICKED_PALLET_UID and(r.REMAIN>0 or r.HARD_RESERVED_BASE>0)")
s=s.replace("left join RRL_CELLS cell on cell.CELL=t.TO_CELL","left join RRL_CELLS cell on cell.CELL=r.CELL")
s=s.replace("item.put('cell',x.TO_CELL);","item.put('cell',x.TO_CELL);item.put('original_picked_cell',x.PICKED_CELL);")
print(json.dumps({str(p):s}))
