from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-10_ni063_holder_loss")
out[str(f/"001_schema.sql")]=r"""declare n number;begin
select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TARE_LOSS_CLAIM' and COLUMN_NAME='SOURCE_CLAIM_ID';
if n=0 then execute immediate 'alter table RRL_TARE_LOSS_CLAIM add(SOURCE_CLAIM_ID varchar2(100) references RRL_STOCK_OPERATION(OPERATION_ID),TRANSPORT_TASK_ID number references RRL_TRANSPORT_TASK(ID))';end if;
end;
/
begin execute immediate 'create index RRL_TARE_LOSS_SOURCE_IX on RRL_TARE_LOSS_CLAIM(SOURCE_CLAIM_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
s=Path("db/migrations/2026-10-10_ni063_warehouse_tare_loss/004_command.sql").read_text(encoding="utf-8-sig")
s=s.replace("v_outcome varchar2(12);","v_outcome varchar2(12);v_holder varchar2(12);v_id varchar2(255);v_source_claim varchar2(100);v_delivery varchar2(100);v_tt number;v_vehicle number;v_plate varchar2(50);v_outstanding number;v_pending number;trip RRL_TRANSPORT_TASK%rowtype;",1)
s=s.replace("  RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_owner);","""  v_holder:=nvl(m.get_string('custodian_kind'),'WAREHOUSE');v_id:=nvl(m.get_string('custodian_id'),RRL_STOCK_PLAN_HELPER.decimal_text(v_owner));
  if v_holder not in('WAREHOUSE','VEHICLE','STORE')then raise_application_error(-20886,'TARE_LOSS_CURRENT_HOLDER_REQUIRED');end if;
  if v_holder='WAREHOUSE' and v_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_owner)then raise_application_error(-20886,'TARE_LOSS_WAREHOUSE_ID_CONFLICT');end if;
  if v_holder='VEHICLE' then
   v_tt:=s.get_number('task_id');select * into trip from RRL_TRANSPORT_TASK where ID=v_tt and nvl(DELETED,0)=0;
   select ID,NUM into v_vehicle,v_plate from RRL_TR_VEHICLE where NUM=trip.TRANSPORT and nvl(DELETED,0)=0 and nvl(BLOCKED,0)=0;
   if v_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_vehicle)or m.get_string('scan_vehicle') is null or m.get_string('scan_vehicle')!=v_plate then raise_application_error(-20886,'TARE_LOSS_CURRENT_VEHICLE_SCAN_REQUIRED');end if;
  end if;
  RRL_TARE_PARTICIPANT.holder_actor(p_actor,v_holder,v_id,v_owner,trip,'tare_loss_report');
  if v_holder='STORE' then v_source_claim:=s.get_string('source_claim_id');end if;""",1)
s=s.replace("  v_outcome:=m.get_string('outcome');","""  select CUSTODIAN_KIND,CUSTODIAN_ID into v_holder,v_id from RRL_TARE_BALANCE where BALANCE_KEY=claim.BALANCE_KEY;
  v_source_claim:=claim.SOURCE_CLAIM_ID;v_tt:=claim.TRANSPORT_TASK_ID;
  v_outcome:=m.get_string('outcome');""",1)
s=s.replace("v_condition,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(v_owner)","v_condition,v_holder,v_id",1)
s=s.replace(" v_held:=RRL_TARE_PLANNING.held_quantity(v_key);",""" v_held:=RRL_TARE_PLANNING.held_quantity(v_key);
 if v_holder='STORE' then
  select OUTSTANDING_QTY,ACCEPT_OPERATION_ID into v_outstanding,v_delivery from RRL_TARE_STORE_DEBT where CLAIM_KEY=v_source_claim and OWNER_WARE_ID=v_owner and PALLET_TYPE_ID=v_type and STORE_ADDR=v_id and CONDITION_CODE=v_condition;
  select nvl(sum(c.QUANTITY),0) into v_pending from RRL_TARE_LOSS_CLAIM c where c.SOURCE_CLAIM_ID=v_source_claim and not exists(select 1 from RRL_TARE_LOSS_DECISION x where x.CLAIM_OPERATION_ID=c.OPERATION_ID);
  if v_qty>v_outstanding-case when kind='TARE_LOSS_REPORT' then v_pending else 0 end then raise_application_error(-20886,'TARE_LOSS_ORIGINAL_STORE_CLAIM_EXCEEDED');end if;
 end if;""",1)
s=s.replace("p_domain.put('balance_key'","p_domain.put('custodian_kind',v_holder);p_domain.put('custodian_id',v_id);p_domain.put('source_claim_id',v_source_claim);p_domain.put('task_id',v_tt);p_domain.put('vehicle_id',v_vehicle);p_domain.put('vehicle_number',v_plate);p_domain.put('delivery_accept_operation_id',v_delivery);p_domain.put('store_outstanding',v_outstanding);p_domain.put('store_pending',v_pending);\n p_domain.put('balance_key'",1)
s=s.replace(" p_policies:=f.to_clob;",""" if v.get_string('source_claim_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_OPERATION',v.get_string('source_claim_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_ACCEPT',v.get_string('delivery_accept_operation_id'));end if;
 if v.get_number('task_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));end if;
 if v.get_number('vehicle_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('vehicle_id')));end if;
 p_policies:=f.to_clob;""",1)
s=s.replace("v_ref varchar2(255);n number;","v_ref varchar2(255);n number;v_source_claim varchar2(100);v_tt number;",1)
s=s.replace(" select QUANTITY into n from RRL_TARE_BALANCE",""" if v.get_number('task_id') is not null then n:=v.get_number('task_id');select ID into n from RRL_TRANSPORT_TASK where ID=n for update;end if;
 if v.get_number('vehicle_id') is not null then n:=v.get_number('vehicle_id');select ID into n from RRL_TR_VEHICLE where ID=n for update;end if;
 select QUANTITY into n from RRL_TARE_BALANCE""",1)
s=s.replace(" if kind='TARE_LOSS_REPORT' then\n insert into"," v_source_claim:=v.get_string('source_claim_id');v_tt:=v.get_number('task_id');\n if kind='TARE_LOSS_REPORT' then\n insert into",1)
s=s.replace("DECISION_REFERENCE,ACTOR)values(op,v_key","DECISION_REFERENCE,ACTOR,SOURCE_CLAIM_ID,TRANSPORT_TASK_ID)values(op,v_key",1).replace("v_qty,v_reason,v_ref,p_actor);","v_qty,v_reason,v_ref,p_actor,v_source_claim,v_tt);",1)
out[str(f/"002_command.sql")]=s
s=Path("db/migrations/2026-10-10_ni063_tare_resolution/004_debt_view.sql").read_text(encoding="utf-8-sig")
s=s.replace("),loans as(", """),loss_totals as(
 select c.SOURCE_CLAIM_ID,sum(c.QUANTITY) QTY from RRL_TARE_LOSS_CLAIM c join RRL_TARE_LOSS_DECISION d on d.CLAIM_OPERATION_ID=c.OPERATION_ID and d.OUTCOME='WRITE_OFF'
 where c.SOURCE_CLAIM_ID is not null group by c.SOURCE_CLAIM_ID
),loans as(""",1)
s=s.replace("a.ACCEPTED_QTY-nvl(dt.QTY,0) LOAN_QTY","a.ACCEPTED_QTY-nvl(dt.QTY,0)-nvl(lt.QTY,0) LOAN_QTY",1)
s=s.replace(" where o.TO_KIND='STORE'"," left join loss_totals lt on lt.SOURCE_CLAIM_ID=a.OPERATION_ID where o.TO_KIND='STORE'",1)
s=s.replace("r.QUANTITY-nvl(wt.QTY,0),","r.QUANTITY-nvl(wt.QTY,0)-nvl(lt.QTY,0),",1)
s=s.replace("\n where r.RESOLUTION_KIND='DAMAGE'"," left join loss_totals lt on lt.SOURCE_CLAIM_ID=r.OPERATION_ID\n where r.RESOLUTION_KIND='DAMAGE'",1)
out[str(f/"003_debt.sql")]=s
s=Path("db/migrations/2026-10-10_ni063_booked_handover/003_tare_command.sql").read_text(encoding="utf-8-sig").replace("if v_from_kind='WAREHOUSE' then RRL_TARE_PLANNING.assert_available","RRL_TARE_PLANNING.assert_available").replace("v_from_qty+v_books.get_size,v_qty);end if;end if;","v_from_qty+v_books.get_size,v_qty);end if;",1)
out[str(f/"004_tare_command.sql")]=s
s=Path("db/migrations/2026-10-10_ni063_warehouse_tare_loss/007_resolution_command.sql").read_text(encoding="utf-8-sig").replace("if v_holder='WAREHOUSE' then RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);end if;","RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);",1);out[str(f/"005_resolution_command.sql")]=s
out[str(f/"apply.sql")]="\n".join("@@"+n for n in ["001_schema.sql","003_debt.sql","002_command.sql","004_tare_command.sql","005_resolution_command.sql"])+r"""
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TARE_LOSS','RRL_STOCK_TARE_CMD','RRL_STOCK_TARE_RESOLVE','RRL_TARE_STORE_DEBT')and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_HOLDER_LOSS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-106-store-vehicle-tare-loss' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Current store/driver loss observation, original store claim/custody/balance caps, pending unusable quantity and independent decision',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[str(f/"rollback.sql")]=r"""declare n number;begin select count(*)into n from RRL_TARE_LOSS_CLAIM where SOURCE_CLAIM_ID is not null or TRANSPORT_TASK_ID is not null;if n>0 then raise_application_error(-20808,'HOLDER_LOSS_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-10_ni063_tare_resolution/004_debt_view.sql
@@../2026-10-08_stock_posting_core/417_before106_loss.sql
@@../2026-10-08_stock_posting_core/418_before106_tare.sql
@@../2026-10-08_stock_posting_core/419_before106_resolution.sql
"""
print(json.dumps(out,ensure_ascii=True))
