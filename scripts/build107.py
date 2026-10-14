from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-10_ni062_reuse_boxes")
out[str(f/"001_schema.sql")]=r"""declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RETURN_WARE_POLICY' and COLUMN_NAME='REUSE_RECEIVE_CELL';
 if n=0 then execute immediate 'alter table RRL_STORE_RETURN_WARE_POLICY add(REUSE_RECEIVE_CELL varchar2(60 byte))';end if;
 for r in(select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_STORE_RETURN_RECEIPT' and CONSTRAINT_TYPE='C' and SEARCH_CONDITION_VC like '%DISPOSITION%' and SEARCH_CONDITION_VC like '%SUPPLIER%')loop execute immediate 'alter table RRL_STORE_RETURN_RECEIPT drop constraint '||dbms_assert.simple_sql_name(r.CONSTRAINT_NAME);end loop;
 execute immediate q'[alter table RRL_STORE_RETURN_RECEIPT add constraint RRL_STORE_RETURN_DISPOSITION_CK check(DISPOSITION in('REUSE','SUPPLIER','DISPOSAL'))]';
end;
/
begin execute immediate q'[create table RRL_RETURN_REUSE_PROOF(
 OPERATION_ID varchar2(100) primary key references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 BOX_COUNT number(18,0) not null check(BOX_COUNT>0),
 BOX_BASE_QTY number(27,9) not null check(BOX_BASE_QTY>0),
 UOM_POLICY_VERSION number(19) not null,
 ARTICLE_BARCODE varchar2(128 byte) not null,
 SOURCE_BATCH varchar2(100 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[str(f/"002_reuse.sql")]=r"""create or replace package RRL_STOCK_RETURN_REUSE authid definer accessible by(package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_STORE_RETURN_PUT) as
 procedure describe_boxes(p_approval RRL_STORE_RETURN_APPROVAL%rowtype,p_metadata json_object_t,p_scan_uom varchar2,p_batch_source varchar2,p_proof out json_object_t);
 procedure persist_boxes(p_operation varchar2,p_actor varchar2,p_proof json_object_t);
 procedure assert_pick_target(p_receipt RRL_STORE_RETURN_RECEIPT%rowtype,p_target varchar2);
end;
/
create or replace package body RRL_STOCK_RETURN_REUSE as
 procedure describe_boxes(p_approval RRL_STORE_RETURN_APPROVAL%rowtype,p_metadata json_object_t,p_scan_uom varchar2,p_batch_source varchar2,p_proof out json_object_t) is
 v_count number;v_num number;v_den number;v_scale number;v_version number;v_base varchar2(20);v_box number;v_quantity number;v_good boolean;
 begin
 if p_approval.COMPLETE_GOOD_BOX!=1 or p_batch_source!='ORIGINAL_SAP_VERIFIED' then raise_application_error(-20886,'RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED');end if;
 v_good:=p_metadata.get_boolean('complete_good_boxes');
 if v_good is null or not v_good or p_scan_uom!='BOX' or not regexp_like(p_metadata.get_string('full_box_count'),'^[1-9][0-9]{0,17}$')then raise_application_error(-20886,'RETURN_REUSE_PHYSICAL_COMPLETE_BOX_BARCODE_COUNT_REQUIRED');end if;
 v_count:=RRL_STOCK_MATH.quantity(p_metadata.get_string('full_box_count'));
 select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION into v_base,v_num,v_den,v_scale,v_version from RRL_STOCK_UOM_CONVERSION
 where ARTICUL=p_approval.ARTICLE and INPUT_UOM='BOX' and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_approval.ARTICLE and INPUT_UOM='BOX');
 v_box:=RRL_STOCK_MATH.convert_exact('1',v_num,v_den,v_scale);v_quantity:=RRL_STOCK_MATH.convert_exact(p_metadata.get_string('full_box_count'),v_num,v_den,v_scale);
 if v_base!=p_approval.BASE_UOM or v_quantity!=p_approval.BASE_QTY then raise_application_error(-20886,'RETURN_REUSE_FULL_BOX_BASE_QUANTITY_CONFLICT');end if;
 p_proof:=json_object_t();p_proof.put('box_count',RRL_STOCK_PLAN_HELPER.decimal_text(v_count));p_proof.put('box_base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_box));p_proof.put('uom_policy_version',v_version);p_proof.put('barcode',p_metadata.get_string('scan_article'));p_proof.put('supplier_batch',p_metadata.get_string('supplier_batch'));
 exception when no_data_found then raise_application_error(-20886,'RETURN_REUSE_CURRENT_BOX_UOM_REQUIRED');end;
 procedure persist_boxes(p_operation varchar2,p_actor varchar2,p_proof json_object_t) is v_count number;v_box number;v_version number;v_code varchar2(128);v_batch varchar2(100);
 begin
 if p_proof is null then return;end if;
 v_count:=RRL_STOCK_MATH.quantity(p_proof.get_string('box_count'));v_box:=RRL_STOCK_MATH.quantity(p_proof.get_string('box_base_quantity'));v_version:=p_proof.get_number('uom_policy_version');v_code:=p_proof.get_string('barcode');v_batch:=p_proof.get_string('supplier_batch');
 insert into RRL_RETURN_REUSE_PROOF(OPERATION_ID,BOX_COUNT,BOX_BASE_QTY,UOM_POLICY_VERSION,ARTICLE_BARCODE,SOURCE_BATCH,ACTOR)values(p_operation,v_count,v_box,v_version,v_code,v_batch,p_actor);
 end;
 procedure assert_pick_target(p_receipt RRL_STORE_RETURN_RECEIPT%rowtype,p_target varchar2) is n number;v_min_days number;v_tmin number;v_tmax number;v_cell_min number;v_cell_max number;
 begin
 select count(*)into n from RRL_RETURN_REUSE_PROOF where OPERATION_ID=p_receipt.OPERATION_ID and BOX_COUNT*BOX_BASE_QTY=p_receipt.BASE_QTY and SOURCE_BATCH=p_receipt.OBSERVED_BATCH;
 if n!=1 or p_receipt.BATCH_SOURCE!='ORIGINAL_SAP_VERIFIED'then raise_application_error(-20886,'RETURN_REUSE_RECEIVED_FULL_BOX_PROOF_REQUIRED');end if;
 select count(*)into n from RRL_CELLS where CELL=p_target and WARE_ID=p_receipt.WARE_ID and OTBOR=1 and nvl(IS_SYSTEM,0)=0 and nvl(BLOCKED_FOR_ACCEPT,0)=0 and nvl(BLOCKED_FOR_REMAINS,0)=0 and nvl(BLOCKED_FOR_POPOLNENIE,0)=0;
 if n!=1 then raise_application_error(-20886,'RETURN_REUSE_CURRENT_PICKING_CELL_REQUIRED');end if;
 select nvl(max(MIN_SHELF_DAYS),0),max(TEMP_MIN),max(TEMP_MAX)into v_min_days,v_tmin,v_tmax from RRL_RECEIPT_SKU_RULE where WARE_ID=p_receipt.WARE_ID and ARTICUL=p_receipt.ARTICLE;
 if trunc(p_receipt.EXPIRY_DATE)<trunc(sysdate)+v_min_days then raise_application_error(-20886,'RETURN_REUSE_SHELF_LIFE_REQUIRED');end if;
 if v_tmin is not null or v_tmax is not null then
  select TEMP_MIN,TEMP_MAX into v_cell_min,v_cell_max from RRL_RECEIPT_CELL_RULE where WARE_ID=p_receipt.WARE_ID and CELL=p_target;
  if v_cell_min is null or v_cell_max is null or(v_tmin is not null and v_cell_min<v_tmin)or(v_tmax is not null and v_cell_max>v_tmax)then raise_application_error(-20886,'RETURN_REUSE_PICKING_TEMPERATURE_REQUIRED');end if;
 end if;
 RRL_STOCK_REPL_ADMISSION.assert_target(p_receipt.UID_PALLET,p_target,p_receipt.WARE_ID,p_receipt.ARTICLE);
 exception when no_data_found then raise_application_error(-20886,'RETURN_REUSE_PICKING_POLICY_REQUIRED');end;
end;
/
"""
s=Path("db/migrations/2026-10-10_ni062_return_receiving/002_command.sql").read_text(encoding="utf-8-sig")
s=s.replace("v_scan_code varchar2(128);","v_scan_code varchar2(128);v_proof json_object_t;",1)
s=s.replace(" if approved.DISPOSITION not in('SUPPLIER','DISPOSAL') then raise_application_error(-20886,'STORE_RETURN_REUSE_COMPLETE_BOX_PLACEMENT_FLOW_REQUIRED');end if;","",1)
s=s.replace("when 'SUPPLIER' then policy.SUPPLIER_RECEIVE_CELL else policy.DISPOSAL_RECEIVE_CELL","when 'SUPPLIER' then policy.SUPPLIER_RECEIVE_CELL when 'REUSE' then policy.REUSE_RECEIVE_CELL else policy.DISPOSAL_RECEIVE_CELL",1)
s=s.replace(" p_domain:=json_object_t();"," if approved.DISPOSITION='REUSE' then RRL_STOCK_RETURN_REUSE.describe_boxes(approved,m,v_scan_uom,v_batch_source,v_proof);end if;\n p_domain:=json_object_t();",1)
s=s.replace("p_domain.put('pickup_operation_id'","if v_proof is not null then p_domain.put('reuse_boxes',v_proof);end if;p_domain.put('pickup_operation_id'",1)
s=s.replace(" p_policies:=f.to_clob;"," if v.has('reuse_boxes')then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RETURN_REUSE_PROOF',p_operation);end if;\n p_policies:=f.to_clob;",1)
# Receipt row must exist before FK-backed proof.
needle=" j.put('operation_id'"
assert needle in s
s=s.replace(needle," if v.has('reuse_boxes')then RRL_STOCK_RETURN_REUSE.persist_boxes(op,p_actor,v.get_object('reuse_boxes'));end if;\n"+needle,1)
out[str(f/"003_receiving.sql")]=s
s=Path("db/migrations/2026-10-10_ni062_return_putaway/002_helper.sql").read_text(encoding="utf-8-sig")
s=s.replace("v_target:=case receipt.DISPOSITION when 'SUPPLIER' then policy.SUPPLIER_TARGET_CELL else policy.DISPOSAL_TARGET_CELL end;","""if receipt.DISPOSITION='REUSE' then
 select nvl(r.PICK_CELL,a.CELL) into v_target from RRL_ARTICULS a left join RRL_RECEIPT_SKU_RULE r on r.ARTICUL=a.ACTICUL and r.WARE_ID=receipt.WARE_ID where a.ACTICUL=receipt.ARTICLE;
 RRL_STOCK_RETURN_REUSE.assert_pick_target(receipt,v_target);
 else v_target:=case receipt.DISPOSITION when 'SUPPLIER' then policy.SUPPLIER_TARGET_CELL else policy.DISPOSAL_TARGET_CELL end;end if;""",1)
s=s.replace(" select count(*) into n from RRL_CELLS where CELL=v_target"," if receipt.DISPOSITION!='REUSE' then\n select count(*) into n from RRL_CELLS where CELL=v_target",1)
s=s.replace("if n!=1 then raise_application_error(-20886,'STORE_RETURN_BLOCKED_TARGET_REQUIRED');end if;","if n!=1 then raise_application_error(-20886,'STORE_RETURN_BLOCKED_TARGET_REQUIRED');end if;end if;",1)
out[str(f/"004_putaway.sql")]=s
out[str(f/"005_guards.sql")]=r"""create or replace trigger RRL_RETURN_REUSE_ZONE_GUARD before insert or update of REUSE_RECEIVE_CELL,SUPPLIER_RECEIVE_CELL,DISPOSAL_RECEIVE_CELL on RRL_STORE_RETURN_WARE_POLICY for each row
declare n number;
begin
 if :new.REUSE_RECEIVE_CELL is null then return;end if;
 select count(*)into n from RRL_CELLS where CELL=:new.REUSE_RECEIVE_CELL and WARE_ID=:new.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 or :new.REUSE_RECEIVE_CELL in(:new.SUPPLIER_RECEIVE_CELL,:new.DISPOSAL_RECEIVE_CELL)then raise_application_error(-20886,'RETURN_REUSE_SEPARATE_BLOCKED_RECEIVE_ZONE_REQUIRED');end if;
end;
/
create or replace trigger RRL_RETURN_REUSE_PROOF_GUARD before insert or update or delete on RRL_RETURN_REUSE_PROOF for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'RETURN_REUSE_PROOF_IMMUTABLE');end if;
 if :new.OPERATION_ID!=op or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'RETURN_REUSE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_RECEIVE'or v_state!='IN_FLIGHT'then raise_application_error(-20863,'RETURN_REUSE_RECEIVE_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RETURN_REUSE_PROOF',op));
end;
/
"""
out[str(f/"apply.sql")]="\n".join("@@"+n for n in ["001_schema.sql","002_reuse.sql","003_receiving.sql","004_putaway.sql","005_guards.sql"])+r"""
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_RETURN_REUSE','RRL_STOCK_STORE_RETURN_REC_CMD','RRL_STOCK_STORE_RETURN_PUT','RRL_RETURN_REUSE_ZONE_GUARD','RRL_RETURN_REUSE_PROOF_GUARD')and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'RETURN_REUSE_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-107-return-full-good-box-reuse' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Full ordinary good BOX return source batch and exact BOX UOM proof, separate blocked receiving, existing warehouse task to current configured picking/batch/expiry policy',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[str(f/"rollback.sql")]=r"""declare n number;begin select count(*)into n from RRL_RETURN_REUSE_PROOF;if n>0 then raise_application_error(-20808,'REUSE_STOCK_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/420_before107_return_receive.sql
@@../2026-10-08_stock_posting_core/421_before107_return_put.sql
"""
for name in ["002_reuse.sql","003_receiving.sql","005_guards.sql","006_repl_policy.sql","apply.sql","refine.sql"]:
 out[str(f/name)]=(f/name).read_text(encoding="utf-8-sig")
print(json.dumps(out,ensure_ascii=True))
