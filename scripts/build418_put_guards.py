from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_placement';out={}
out[d+'/004_guards.sql']="""create or replace package RRL_IW_GROUP_PUT_GUARD authid definer as
 procedure assert_fact(p_operation varchar2,p_receipt varchar2,p_task number,p_uid varchar2,p_ware number,p_target varchar2,p_actor varchar2,p_planning number);
end;
/
create or replace package body RRL_IW_GROUP_PUT_GUARD as
 procedure assert_fact(p_operation varchar2,p_receipt varchar2,p_task number,p_uid varchar2,p_ware number,p_target varchar2,p_actor varchar2,p_planning number)is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_value varchar2(80);state_value varchar2(20);wire clob;d json_object_t;g json_object_t;n number;expected number;move_count number;
 begin
 if op is null or op!=p_operation or p_actor!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_GROUP_PUT_FACT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 d:=json_object_t.parse(wire).get_object('domain');g:=d.get_object('group_placement');
 if state_value!='IN_FLIGHT'or d.get_number('task_id')!=p_task or d.get_number('planning')!=p_planning or g is null or g.get_string('receipt_operation_id')!=p_receipt or g.get_string('uid')!=p_uid or g.get_number('warehouse_id')!=p_ware or g.get_string('target_cell')!=p_target then raise_application_error(-20863,'INTERWARE_GROUP_PUT_EXACT_DOMAIN_REQUIRED');end if;
 if(p_planning=1 and kind_value!='HU_PLAN_MOVE')or(p_planning=0 and kind_value!='TASK_COMPLETE')then raise_application_error(-20863,'INTERWARE_GROUP_PUT_EXACT_OWNER_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_GROUP_RECEIPT',p_receipt));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW',case when p_planning=1 then 'RRL_IW_GROUP_PUT_PLAN'else 'RRL_IW_GROUP_PLACEMENT'end,op));
 select count(*)into n from RRL_WAREHOUSE_TASK where TASK_ID=p_task and UID_PALLET=p_uid and FROM_WARE_ID=p_ware and TO_WARE_ID=p_ware and TO_CELL=p_target and SOURCE_DOC_TYPE='WAREHOUSE_HU'and QTY=1 and UNIT_CODE='HU'and STATUS=case when p_planning=1 then 'PLANNED'else 'DONE'end;
 if n!=1 then raise_application_error(-20863,'INTERWARE_GROUP_PUT_EXACT_TASK_REQUIRED');end if;
 if p_planning=0 then
  select count(*)into expected from RRL_IW_GROUP_RECEIPT_LINE where OPERATION_ID=p_receipt;
  select count(*)into move_count from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=p_task and OPERATION_ID=op;
  select count(*)into n from RRL_WAREHOUSE_TASK_STOCK_MOVE m join RRL_IW_GROUP_RECEIPT_LINE l on l.OPERATION_ID=p_receipt and l.ROOT_UID=m.UID_PALLET and m.TARGET_UID_PALLET=l.ROOT_UID and m.BASE_QTY=l.BASE_QTY and m.BASE_UOM=l.BASE_UOM
   where m.TASK_ID=p_task and m.OPERATION_ID=op and m.TO_CELL=p_target;
  if n!=expected or move_count!=expected then raise_application_error(-20863,'INTERWARE_GROUP_PUT_ALL_COMMODITY_EFFECTS_REQUIRED');end if;
 end if;
 end;
end;
/
create or replace trigger RRL_IW_GROUP_PUT_PLAN_GUARD before insert or update or delete on RRL_IW_GROUP_PUT_PLAN for each row
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_PUT_PLAN_IMMUTABLE');end if;
 RRL_IW_GROUP_PUT_GUARD.assert_fact(:new.OPERATION_ID,:new.RECEIPT_OPERATION_ID,:new.TASK_ID,:new.ROOT_UID,:new.WARE_ID,:new.TARGET_CELL,:new.ACTOR,1);
end;
/
create or replace trigger RRL_IW_GROUP_PLACEMENT_GUARD before insert or update or delete on RRL_IW_GROUP_PLACEMENT for each row
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_PLACEMENT_IMMUTABLE');end if;
 RRL_IW_GROUP_PUT_GUARD.assert_fact(:new.OPERATION_ID,:new.RECEIPT_OPERATION_ID,:new.TASK_ID,:new.ROOT_UID,:new.WARE_ID,:new.TARGET_CELL,:new.ACTOR,0);
end;
/
"""
out[d+'/005_recompile.sql']="""alter package RRL_STOCK_HU_TASK compile body;
alter package RRL_STOCK_TASK_CORE compile body;
alter package RRL_STOCK_TASK_CMD compile body;
alter package RRL_STOCK_POSTING_API compile body;
"""
out[d+'/006_ledger.sql']="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-417-grouped-interware-placement' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing whole HU task binds grouped receipt and exact perlot commodity effects, no parallel move owner',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
out[d+'/apply.sql']='\n'.join('@@'+f for f in ['001_schema.sql','002_core.sql','003_owner.sql','004_guards.sql','005_recompile.sql','006_ledger.sql'])+'\n'
out[d+'/rollback.sql']="""declare n number;begin select count(*)into n from RRL_IW_GROUP_PUT_PLAN;if n!=0 then raise_application_error(-20899,'GROUP_PLACEMENT_TASKS_REQUIRE_FORWARD_RECOVERY');end if;end;
/
@@000_before_hu_task.sql
drop trigger RRL_IW_GROUP_PLACEMENT_GUARD;
drop trigger RRL_IW_GROUP_PUT_PLAN_GUARD;
drop package RRL_IW_GROUP_PUT_GUARD;
drop package RRL_IW_GROUP_PUT;
drop table RRL_IW_GROUP_PLACEMENT;
drop table RRL_IW_GROUP_PUT_PLAN;
alter package RRL_STOCK_POSTING_API compile body;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-12-417-grouped-interware-placement';
commit;
"""
print(json.dumps(out))
