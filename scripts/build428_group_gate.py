from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_promises';out={}
p=Path('tmp/native426_rrl_interware_depart_gate_package_body.sql');t=p.read_text(encoding='utf-8');out[d+'/000_before_gate.sql']=t
needle='  return a.to_clob;'
addition="""  for gp in(select OPERATION_ID,SOURCE_JSON from RRL_IW_GROUP_PLAN where TARGET_TT_ID=p_trip order by OPERATION_ID fetch first 201 rows only)loop
   count_value:=count_value+1;if count_value>200 then raise_application_error(-20881,'INTERWARE_DEPART_PROMISE_BOUND_200');end if;
   select count(*)into n from json_table(gp.SOURCE_JSON,'$.lots[*]'columns(SOURCE_UID varchar2(200)path '$.uid',SOURCE_QTY varchar2(60)path '$.quantity',SOURCE_UOM varchar2(20)path '$.base_uom'))expected
   where not exists(
    select 1 from RRL_TT_HU_LOAD_FACT lf join RRL_STOCK_OPERATION o on o.OPERATION_ID=lf.LOAD_OPERATION_ID and o.STATE='APPLIED'
    join json_table(o.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
     GROUP_PLAN varchar2(100)path '$.domain.interwarehouse_onward_source.group_plan_operation_id',
     LOT_UID varchar2(200)path '$.domain.interwarehouse_onward_source.uid',
     QTY_TEXT varchar2(60)path '$.domain.interwarehouse_onward_source.quantity',
     UOM_TEXT varchar2(20)path '$.domain.interwarehouse_onward_source.base_uom'))loaded
     on loaded.GROUP_PLAN=gp.OPERATION_ID and loaded.LOT_UID=expected.SOURCE_UID and loaded.QTY_TEXT=expected.SOURCE_QTY and loaded.UOM_TEXT=expected.SOURCE_UOM
    where lf.TT_ID=p_trip and lf.STATUS='LOADED'and o.COMMAND_TYPE='HU_SHIP');
   j:=json_object_t();j.put('plan_operation_id',gp.OPERATION_ID);j.put('grouped_cargo',true);j.put('physically_loaded',n=0);a.append(j);
  end loop;
"""+needle
assert needle in t;t=t.replace(needle,addition,1)
out[d+'/001_gate.sql']=t
out[d+'/002_ledger.sql']="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-428-grouped-interware-promises' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Grouped source promises participate in original departure readiness; exact whole perlot native load proof required',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
out[d+'/apply.sql']='@@001_gate.sql\nalter package RRL_STOCK_TRANSPORT_TASK compile body;\n@@002_ledger.sql\n'
out[d+'/rollback.sql']='@@000_before_gate.sql\n'
print(json.dumps(out))
