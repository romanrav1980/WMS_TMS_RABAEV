from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-10_ni063_warehouse_tare_loss")
out[str(f/"001_schema.sql")]=r"""begin execute immediate q'[create table RRL_TARE_LOSS_CLAIM(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 OWNER_WARE_ID number not null,PALLET_TYPE_ID number not null,
 CONDITION_CODE varchar2(10) not null check(CONDITION_CODE in('GOOD','DAMAGED')),
 QUANTITY number(18,0) not null check(QUANTITY>0),
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TARE_LOSS_DECISION(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 CLAIM_OPERATION_ID varchar2(100) not null unique references RRL_TARE_LOSS_CLAIM(OPERATION_ID),
 OUTCOME varchar2(12) not null check(OUTCOME in('WRITE_OFF','REJECT')),
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_LOSS_BALANCE_IX on RRL_TARE_LOSS_CLAIM(BALANCE_KEY,CREATED_AT)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
create or replace view RRL_TARE_LOSS_PENDING as
select c.BALANCE_KEY,sum(c.QUANTITY) QUANTITY from RRL_TARE_LOSS_CLAIM c
where not exists(select 1 from RRL_TARE_LOSS_DECISION d where d.CLAIM_OPERATION_ID=c.OPERATION_ID) group by c.BALANCE_KEY;
/
"""
s=Path("db/migrations/2026-10-10_ni063_tare_assembly/002_planning.sql").read_text(encoding="utf-8-sig")
s=s.replace("q number;","q number;loss number;",1).replace("return q;end;","select nvl(max(QUANTITY),0) into loss from RRL_TARE_LOSS_PENDING where BALANCE_KEY=p_key;return q+loss;end;",1)
out[str(f/"002_planning.sql")]=s
out[str(f/"003_availability.sql")]=r"""create or replace view RRL_TARE_AVAILABILITY as
select b.BALANCE_KEY,b.OWNER_WARE_ID,b.PALLET_TYPE_ID,b.CUSTODIAN_ID,b.QUANTITY PHYSICAL_QTY,b.BALANCE_VERSION,
 nvl(h.QTY,0) ASSEMBLY_QTY,b.QUANTITY-nvl(h.QTY,0)-nvl(l.QUANTITY,0) AVAILABLE_QTY,nvl(l.QUANTITY,0) LOSS_PENDING_QTY
from RRL_TARE_BALANCE b left join(select BALANCE_KEY,sum(QUANTITY) QTY from RRL_TARE_BOOK where STATUS='HELD' group by BALANCE_KEY)h on h.BALANCE_KEY=b.BALANCE_KEY
left join RRL_TARE_LOSS_PENDING l on l.BALANCE_KEY=b.BALANCE_KEY
where b.CUSTODIAN_KIND='WAREHOUSE' and b.CONDITION_CODE='GOOD';
/
"""
out[str(f/"004_command.sql")]=r"""create or replace package RRL_STOCK_TARE_LOSS authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_TARE_LOSS as
 procedure describe_command(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');kind varchar2(80):=d.get_string('command_type');
 v_claim varchar2(100);claim RRL_TARE_LOSS_CLAIM%rowtype;v_owner number;v_type number;v_condition varchar2(10);v_qty number;v_key raw(32);v_p number;v_version number;v_held number;n number;
 v_reason varchar2(32767):=m.get_string('reason');v_ref varchar2(32767):=m.get_string('decision_reference');v_outcome varchar2(12);
 begin
 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;if n!=1 then raise_application_error(-20882,'TARE_ACTIVE_ACTOR_REQUIRED');end if;
 if trim(v_reason) is null or lengthb(v_reason)>2000 or trim(v_ref) is null or lengthb(v_ref)>255 then raise_application_error(-20886,'TARE_LOSS_REASON_DECISION_REQUIRED');end if;
 if kind='TARE_LOSS_REPORT' then
  if RRL_HAS_WRIGHT(p_actor,'tare_loss_report')!=1 then raise_application_error(-20882,'TARE_LOSS_REPORT_PERMISSION_REQUIRED');end if;
  v_owner:=m.get_number('owner_ware_id');v_type:=m.get_number('pallet_type_id');v_condition:=m.get_string('condition');
  if v_owner is null or v_type is null or v_condition is null or v_condition not in('GOOD','DAMAGED') then raise_application_error(-20886,'TARE_WAREHOUSE_LOSS_TYPE_REQUIRED');end if;
  if not regexp_like(m.get_string('quantity'),'^[0-9]{1,18}$') then raise_application_error(-20886,'TARE_INTEGER_QUANTITY_REQUIRED');end if;
  v_qty:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));
  RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_owner);
 else
  if RRL_HAS_WRIGHT(p_actor,'tare_writeoff')!=1 then raise_application_error(-20882,'TARE_LOSS_DECISION_PERMISSION_REQUIRED');end if;
  v_claim:=s.get_string('claim_operation_id');select * into claim from RRL_TARE_LOSS_CLAIM where OPERATION_ID=v_claim;
  if claim.ACTOR=p_actor then raise_application_error(-20882,'TARE_INDEPENDENT_LOSS_DECISION_REQUIRED');end if;
  v_owner:=claim.OWNER_WARE_ID;v_type:=claim.PALLET_TYPE_ID;v_condition:=claim.CONDITION_CODE;v_qty:=claim.QUANTITY;
  v_outcome:=m.get_string('outcome');if v_outcome is null or v_outcome not in('WRITE_OFF','REJECT') then raise_application_error(-20886,'TARE_LOSS_EXPLICIT_OUTCOME_REQUIRED');end if;
  select count(*) into n from RRL_TARE_LOSS_DECISION where CLAIM_OPERATION_ID=v_claim;if n!=0 then raise_application_error(-20886,'TARE_LOSS_ALREADY_DECIDED');end if;
 end if;
 v_key:=RRL_TARE_BALANCE_KEY(v_owner,v_type,v_condition,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(v_owner));
 select QUANTITY,BALANCE_VERSION into v_p,v_version from RRL_TARE_BALANCE where BALANCE_KEY=v_key;
 v_held:=RRL_TARE_PLANNING.held_quantity(v_key);
 if kind='TARE_LOSS_REPORT' then
  if m.get_number('expected_version') is null or m.get_number('expected_version')!=v_version then raise_application_error(-20886,'TARE_LOSS_BALANCE_VERSION_CONFLICT');end if;
  RRL_TARE_PLANNING.assert_available(v_key,v_p,v_qty);
 elsif v_p<v_held or v_qty>v_p then raise_application_error(-20886,'TARE_LOSS_PENDING_PHYSICAL_BALANCE_CONFLICT');end if;
 p_domain:=json_object_t();p_domain.put('claim_operation_id',v_claim);p_domain.put('owner_ware_id',v_owner);p_domain.put('pallet_type_id',v_type);p_domain.put('condition',v_condition);
 p_domain.put('balance_key',rawtohex(v_key));p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));p_domain.put('physical_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_p));p_domain.put('balance_version',v_version);p_domain.put('held_quantity',v_held);
 p_domain.put('outcome',v_outcome);p_domain.put('reason',v_reason);p_domain.put('decision_reference',v_ref);
 exception when no_data_found then raise_application_error(-20886,'TARE_LOSS_EXISTING_BALANCE_CLAIM_REQUIRED');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_command(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',v.get_string('balance_key'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOSS_CLAIM',case when d.get_string('command_type')='TARE_LOSS_REPORT' then p_operation else v.get_string('claim_operation_id')end);
 if d.get_string('command_type')='TARE_LOSS_DECIDE' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOSS_DECISION',p_operation);end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');kind varchar2(80):=d.get_string('command_type');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_key raw(32);v_claim varchar2(100);v_owner number;v_type number;v_condition varchar2(10);v_qty number;v_outcome varchar2(12);v_reason varchar2(2000);v_ref varchar2(255);n number;
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');v_key:=hextoraw(v.get_string('balance_key'));v_claim:=v.get_string('claim_operation_id');
 select QUANTITY into n from RRL_TARE_BALANCE where BALANCE_KEY=v_key for update;
 if v_claim is not null then select QUANTITY into n from RRL_TARE_LOSS_CLAIM where OPERATION_ID=v_claim for update;end if;
 describe_command(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare loss');end if;
 v_owner:=v.get_number('owner_ware_id');v_type:=v.get_number('pallet_type_id');v_condition:=v.get_string('condition');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));v_outcome:=v.get_string('outcome');v_reason:=v.get_string('reason');v_ref:=v.get_string('decision_reference');
 if kind='TARE_LOSS_REPORT' then
 insert into RRL_TARE_LOSS_CLAIM(OPERATION_ID,BALANCE_KEY,OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,QUANTITY,REASON_TEXT,DECISION_REFERENCE,ACTOR)values(op,v_key,v_owner,v_type,v_condition,v_qty,v_reason,v_ref,p_actor);
 else
 insert into RRL_TARE_LOSS_DECISION(OPERATION_ID,CLAIM_OPERATION_ID,OUTCOME,REASON_TEXT,DECISION_REFERENCE,ACTOR)values(op,v_claim,v_outcome,v_reason,v_ref,p_actor);
 end if;
 update RRL_TARE_BALANCE set QUANTITY=QUANTITY-case when v_outcome='WRITE_OFF' then v_qty else 0 end,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp where BALANCE_KEY=v_key;
 j.put('operation_id',op);j.put('status',case when kind='TARE_LOSS_REPORT' then 'REPORTED' else v_outcome end);j.put('quantity',v.get_string('quantity'));j.put('total_tare_changed',v_outcome='WRITE_OFF');j.put('goods_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
"""
s=Path("db/migrations/2026-10-10_ni063_tare_assembly/006_root.sql").read_text(encoding="utf-8-sig")
s=s.replace("  elsif g_kind in('TARE_BOOK'","  elsif g_kind in('TARE_LOSS_REPORT','TARE_LOSS_DECIDE') then RRL_STOCK_TARE_LOSS.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  elsif g_kind in('TARE_BOOK'",1)
s=s.replace("  elsif g_kind in('TARE_BOOK'","  elsif g_kind in('TARE_BOOK'",1)
needle="  elsif g_kind in('TARE_BOOK','TARE_BOOK_CANCEL') then RRL_STOCK_TARE_BOOK_CMD.execute_command"
s=s.replace(needle,"  elsif g_kind in('TARE_LOSS_REPORT','TARE_LOSS_DECIDE') then RRL_STOCK_TARE_LOSS.execute_command(g_request,g_actor,p_result);\n"+needle,1)
out[str(f/"005_root.sql")]=s
s=Path("db/migrations/2026-10-10_ni063_tare_assembly/007_balance_guards.sql").read_text(encoding="utf-8-sig").replace("'TARE_BOOK_CANCEL'","'TARE_BOOK_CANCEL','TARE_LOSS_REPORT','TARE_LOSS_DECIDE'",1)
out[str(f/"006_guards.sql")]=s+r"""
create or replace trigger RRL_TARE_LOSS_CLAIM_GUARD before insert or update or delete on RRL_TARE_LOSS_CLAIM for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_LOSS_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_LOSS_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_LOSS_CLAIM',:new.OPERATION_ID,'TARE_LOSS_REPORT');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(:new.BALANCE_KEY)));
end;
/
create or replace trigger RRL_TARE_LOSS_DEC_GUARD before insert or update or delete on RRL_TARE_LOSS_DECISION for each row
declare original_actor nvarchar2(50);v_key raw(32);
begin
 if not inserting then raise_application_error(-20863,'TARE_LOSS_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_LOSS_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_LOSS_DECISION',:new.OPERATION_ID,'TARE_LOSS_DECIDE');
 select ACTOR,BALANCE_KEY into original_actor,v_key from RRL_TARE_LOSS_CLAIM where OPERATION_ID=:new.CLAIM_OPERATION_ID;
 if original_actor=:new.ACTOR then raise_application_error(-20882,'TARE_INDEPENDENT_LOSS_DECISION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_LOSS_CLAIM',:new.CLAIM_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(v_key)));
end;
/
"""
out[str(f/"apply.sql")]="\n".join("@@"+n for n in ["001_schema.sql","002_planning.sql","003_availability.sql","004_command.sql","005_root.sql","006_guards.sql"]) + r"""
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TARE_LOSS','RRL_STOCK_POSTING_API','RRL_TARE_PLANNING','RRL_TARE_AVAILABILITY','RRL_TARE_LOSS_PENDING','RRL_TARE_LOSS_CLAIM_GUARD','RRL_TARE_LOSS_DEC_GUARD') and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_LOSS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-105-warehouse-tare-loss' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Warehouse tare loss claim excludes suspected quantity from availability; independent full decision writeoff or rejection, immutable Root history',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[str(f/"rollback.sql")]=r"""declare n number;begin select count(*) into n from RRL_TARE_LOSS_CLAIM;if n>0 then raise_application_error(-20808,'LOSS_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@../2026-10-08_stock_posting_core/414_before105_root.sql
@@../2026-10-08_stock_posting_core/415_before105_planning.sql
@@../2026-10-10_ni063_tare_assembly/001_schema.sql
@@../2026-10-10_ni063_tare_assembly/007_balance_guards.sql
"""
out[str(f/"007_resolution_command.sql")]=Path("db/migrations/2026-10-10_ni063_warehouse_tare_loss/007_resolution_command.sql").read_text(encoding="utf-8-sig")
out[str(f/"apply.sql")]=out[str(f/"apply.sql")].replace("@@006_guards.sql","@@006_guards.sql\n@@007_resolution_command.sql")
print(json.dumps(out,ensure_ascii=True))
