from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-12_ni053_marked_case_receipt")
out[(d/"000_before_units.sql").as_posix()]=Path("tmp/379_before_units.sql").read_text()
out[(d/"000_before_store.sql").as_posix()]=Path("tmp/379_before_store.sql").read_text()
helper=""" procedure assert_case_archive(p_load varchar2,p_tree json_object_t)is
 nodes clob:=p_tree.get_array('nodes').to_clob;cases number;n number;leafs number;
 begin
 select count(*)into cases from json_table(nodes,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind'))where NODE_KIND='CASE';
 if cases=0 then return;end if;
 select count(*)into n from json_table(nodes,'$[*]'columns(
 NODE_KIND varchar2(20)path '$.kind',NODE_UID varchar2(160)path '$.uid',CASE_ID number path '$.case_task_id',CASE_SSCC varchar2(32)path '$.sscc',CASE_VERSION number path '$.version'))j
 join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=j.CASE_ID
 join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=p_load and lf.WARE_ID=t.WARE_ID
 where j.NODE_KIND='CASE'and j.NODE_UID='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(t.CASE_PICK_TASK_ID)
 and t.STATUS='SHIPPED'and t.SHIPPED_OPERATION=p_load and t.SSCC=j.CASE_SSCC and t.CONTENT_VERSION=j.CASE_VERSION+1;
 if n!=cases then raise_application_error(-20884,'STORE_CASE_EXACT_FROZEN_SHIPMENT_REQUIRED');end if;
 select count(*)into leafs from json_table(nodes,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))where NODE_KIND='STOCK'and CASE_ID is not null;
 select count(*)into n from json_table(nodes,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind',NODE_UID varchar2(160)path '$.uid',CASE_ID number path '$.case_task_id'))j
 join RRL_CASE_CARRIER_LOT c on c.CASE_PICK_TASK_ID=j.CASE_ID and c.LOT_UID=j.NODE_UID
 where j.NODE_KIND='STOCK'and exists(select 1 from json_table(nodes,'$[*]'columns(PARENT_KIND varchar2(20)path '$.kind',PARENT_CASE number path '$.case_task_id'))p where p.PARENT_KIND='CASE'and p.PARENT_CASE=j.CASE_ID);
 if n!=leafs or leafs<cases then raise_application_error(-20884,'STORE_CASE_EXACT_CARRIER_LOTS_REQUIRED');end if;
 end;
"""
t=out[(d/"000_before_units.sql").as_posix()];at=t.index(" function issued_manifest");t=t[:at]+helper+t[at:];t=t.replace("root_op.COMMAND_TYPE='HU_SHIP'","root_op.COMMAND_TYPE in('HU_SHIP','LOAD_SHIPMENT')")
t=t.replace("candidate.get_string('kind')!='CONTAINER'","candidate.get_string('kind')not in('CONTAINER','CASE')")
t=t.replace("cell_value:=tree.get_string('cell');","assert_case_archive(p_load,tree);\ncell_value:=tree.get_string('cell');")
out[(d/"001_units.sql").as_posix()]=t
t=out[(d/"000_before_store.sql").as_posix()].replace("candidate.get_string('kind')!='CONTAINER'","candidate.get_string('kind')not in('CONTAINER','CASE')")
t=t.replace(" begin\n for i in 0..leaves.get_size-1 loop node:=",''' begin
 for v in(select CASE_ID from json_table(p_domain.get_object('snapshot').get_array('nodes').to_clob,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))where NODE_KIND='CASE')loop
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.CASE_ID));end loop;
 for i in 0..leaves.get_size-1 loop node:=''')
# PL/SQL object method expressions must be evaluated before SQL JSON_TABLE.
t=t.replace("is node json_object_t;leaves json_array_t:=stock_leaves(p_domain.get_object('snapshot'));","is node json_object_t;leaves json_array_t:=stock_leaves(p_domain.get_object('snapshot'));nodes clob:=p_domain.get_object('snapshot').get_array('nodes').to_clob;")
t=t.replace("json_table(p_domain.get_object('snapshot').get_array('nodes').to_clob,","json_table(nodes,")
out[(d/"002_store.sql").as_posix()]=t
out[(d/"003_recompile.sql").as_posix()]=Path("db/migrations/2026-10-12_ni061_marked_consolidation/004_recompile.sql").read_text()
out[(d/"004_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-379-marked-CASE-recipient' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing unit disposition receipt accepts exact frozen shipped CASE/carrier lots and source fingerprints, no duplicate stock',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="@@001_units.sql\n@@002_store.sql\n@@003_recompile.sql\n@@004_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="""declare n number;begin select count(*)into n from RRL_STORE_RECEIPT_FACT f join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
 where exists(select 1 from json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(NODE_KIND varchar2(20)path '$.kind'))where NODE_KIND='CASE')
 and exists(select 1 from RRL_STORE_RECEIPT_UNIT u where u.OPERATION_ID=f.OPERATION_ID);
 if n>0 then raise_application_error(-20899,'MARKED_CASE_RECEIPT_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_units.sql
@@000_before_store.sql
"""
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_INTERWARE_UNIT_SOURCE','RRL_STORE_MARK_CORE');\n"
print(json.dumps(out))
