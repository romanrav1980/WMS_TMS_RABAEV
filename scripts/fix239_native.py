from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_dispatch_decision")
out={}
p=f/"002_routing.sql";s=p.read_text(encoding="utf-8").replace("if arrival<systimestamp","if arrival is null or arrival<systimestamp").replace("or tt.CONDITION!='Спланирован'","or tt.CONDITION is null or tt.CONDITION!='Спланирован'");out[str(p)]=s
p=f/"004_depart_gate.sql";s=p.read_text(encoding="utf-8").replace("select OPERATION_ID from RRL_INTERWARE_PLAN where RRL_INTERWARE_ROUTING.target_trip(OPERATION_ID)=p_trip order by OPERATION_ID fetch first 201 rows only","""select candidate.OPERATION_ID from(
   select OPERATION_ID from RRL_INTERWARE_PLAN where TARGET_TT_ID=p_trip
   union select PLAN_OPERATION_ID from RRL_INTERWARE_DECISION where TARGET_TT_ID=p_trip
  )candidate where RRL_INTERWARE_ROUTING.target_trip(candidate.OPERATION_ID)=p_trip order by candidate.OPERATION_ID fetch first 201 rows only""")
s=s.replace("join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID where","join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID and o.STATE='APPLIED' where")
out[str(p)]=s
out[str(f/"009_candidate_indexes.sql")]="""declare n number;
begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_PLAN_TARGET_I';
 if n=0 then execute immediate 'create index RRL_IW_PLAN_TARGET_I on RRL_INTERWARE_PLAN(TARGET_TT_ID,OPERATION_ID)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_DEC_TARGET_I';
 if n=0 then execute immediate 'create index RRL_IW_DEC_TARGET_I on RRL_INTERWARE_DECISION(TARGET_TT_ID,PLAN_OPERATION_ID,REVISION_NO)';end if;
end;
/
"""
print(json.dumps(out,ensure_ascii=True))
