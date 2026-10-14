from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_thermal';out={}
out[d+'/001_core.sql']="""create or replace package RRL_IW_GROUP_THERMAL authid definer as
 procedure assert_cell(p_ware number,p_article varchar2,p_cell varchar2);
end;
/
create or replace package body RRL_IW_GROUP_THERMAL as
 procedure assert_cell(p_ware number,p_article varchar2,p_cell varchar2)is
 lo number;hi number;j json_object_t:=json_object_t();wire clob;
 begin
 begin select TEMP_MIN,TEMP_MAX into lo,hi from RRL_RECEIPT_SKU_RULE where WARE_ID=p_ware and ARTICUL=p_article;
 exception when no_data_found then lo:=null;hi:=null;end;
 if(lo is null and hi is not null)or(lo is not null and hi is null)or lo>hi then raise_application_error(-20886,'INTERWARE_GROUP_SKU_TEMPERATURE_RANGE_INVALID');end if;
 j.put('task_temp_min',lo);j.put('task_temp_max',hi);wire:=j.to_clob;
 RRL_INTERWARE_THERMAL.assert_cell(wire,p_ware,p_cell);
 end;
end;
/
"""
for original,name,needle,addition in [
 ('db/migrations/2026-10-12_ni061_group_receive/003_core.sql','002_receive.sql',"  select max(POLICY_VERSION)into v_version","  RRL_IW_GROUP_THERMAL.assert_cell(plan.TARGET_WARE_ID,v_article,v_cell);\n"),
 ('db/migrations/2026-10-12_ni061_group_placement/002_core.sql','003_placement.sql',"   select count(*)into n from RRL_IW_GROUP_RECEIPT_LINE","   RRL_IW_GROUP_THERMAL.assert_cell(receipt.WARE_ID,lot_article,p_target);\n"),
 ('db/migrations/2026-10-12_ni061_group_onward/002_next.sql','004_onward.sql'," select max(POLICY_VERSION)into v_policy"," RRL_IW_GROUP_THERMAL.assert_cell(p_ware,receipt.ARTICLE,bind.SOURCE_CELL);\n")]:
 p=Path(original);t=p.read_text(encoding='utf-8');assert needle in t
 out[d+'/000_before_'+name]=t
 out[d+'/'+name]=t.replace(needle,addition+needle,1)
out[d+'/005_index.sql']="""begin execute immediate 'create index RRL_IW_GROUP_DISPATCH_REC_IX on RRL_IW_GROUP_DISPATCH(RECEIPT_OPERATION_ID,OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[d+'/006_ledger.sql']="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-442-grouped-current-temperature' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'PerSKU group receive/placement/onward reuse original thermal cell rules; receipt index for bounded group phase',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
out[d+'/apply.sql']='\n'.join('@@'+f for f in ['001_core.sql','002_receive.sql','003_placement.sql','004_onward.sql','005_index.sql','006_ledger.sql'])+'\n'
out[d+'/rollback.sql']="declare begin raise_application_error(-20899,'GROUP_THERMAL_OWNER_REQUIRES_FORWARD_RECOVERY');end;\n/\n"
print(json.dumps(out))
