from pathlib import Path
import json
d="db/migrations/2026-10-12_ni062_preserved_pallet/"
helper="""create or replace package RRL_RETURN_PALLET_IDENTITY authid definer
 accessible by(package RRL_STORE_RETURN_UNIT_CORE,package RRL_STOCK_STORE_RETURN_REC_CMD)as
 procedure assert_preserved(p_approval varchar2,p_uid varchar2);
end;
/
create or replace package body RRL_RETURN_PALLET_IDENTITY as
 procedure assert_preserved(p_approval varchar2,p_uid varchar2)is
 a RRL_STORE_RETURN_APPROVAL%rowtype;p RRL_PALLETS%rowtype;n number;qty number;
 begin
  select *into a from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=p_approval;
  if p_uid is null or p_uid!=a.LOT_UID then raise_application_error(-20886,'RETURN_PALLET_ORIGINAL_IDENTITY_REQUIRED');end if;
  select *into p from RRL_PALLETS where UID_PALLET=p_uid;
  if p.ARTICUL is null or p.ARTICUL!=a.ARTICLE or p.UNIT_COUNT is null or p.UNIT_COUNT!=a.BASE_QTY then
   raise_application_error(-20886,'RETURN_PALLET_FULL_ORIGINAL_QUANTITY_REQUIRED');
  end if;
  select count(*)into n from RRL_REMAINS where UID_POLETA=p_uid and(REMAIN!=0 or HARD_RESERVED_BASE!=0);
  if n!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: preserved pallet still has warehouse stock');end if;
  select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(PARENT_UID=p_uid or CHILD_PALLET_UID=p_uid);
  if n!=0 then raise_application_error(-20886,'RETURN_PALLET_EXPLICIT_HU_UNPACK_REQUIRED');end if;
  select count(*)into n from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if n!=0 then raise_application_error(-20886,'RETURN_PALLET_ORIGINAL_CASE_REPACKING_UNSUPPORTED');end if;
  select count(*)into n from RRL_WAREHOUSE_TASK where UID_PALLET=p_uid and STATUS not in('DONE','CANCELLED');
  if n!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: preserved pallet physical task issued');end if;
  select count(*),sum(BASE_QTY)into n,qty from RRL_WMS_RECEIPT_UNIT
   where UID_PALLET=p_uid and CURRENT_UID=p_uid and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null;
  if n<1 or qty!=a.BASE_QTY then raise_application_error(-20886,'RETURN_PALLET_UNCHANGED_ORIGINAL_UNITS_REQUIRED');end if;
  select count(*)into n from RRL_WMS_RECEIPT_UNIT u where u.UID_PALLET=p_uid
   and not exists(select 1 from RRL_STORE_RETURN_UNIT b where b.APPROVAL_OPERATION_ID=p_approval and b.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY);
  if n!=0 then raise_application_error(-20886,'RETURN_PALLET_FULL_APPROVED_COMPOSITION_REQUIRED');end if;
 end;
end;
/
"""
unit=Path("db/migrations/2026-10-12_ni062_return_aggregation/002_return_unit_core.sql").read_text(encoding="utf-8")
a="if bad_direct!=0 then raise_application_error(-20886,'RETURN_PALLET_AGGREGATION_REQUIRES_PRESERVED_CONTAINER_IDENTITY');end if;"
b="""if bad_direct!=0 then
    lot_value:=normalized.get_string('pallet_identifier');
    if lot_value is null then lot_value:=normalized.get_string('scan_pallet');end if;
    RRL_RETURN_PALLET_IDENTITY.assert_preserved(p_approval,lot_value);
   end if;"""
assert a in unit;new_unit=unit.replace(a,b)
rec=Path("tmp/628_return_rec_body.sql").read_text(encoding="utf-8")
a="if n!=0 then raise_application_error(-20886,'STORE_RETURN_FRESH_PALLET_REQUIRED');end if;"
b="""if n!=0 then
  RRL_RETURN_PALLET_IDENTITY.assert_preserved(approved.OPERATION_ID,v_uid);
 end if;"""
assert a in rec;new_rec=rec.replace(a,b)
a="p_domain:=json_object_t();"
b="""p_domain:=json_object_t();
 if v_uid=approved.LOT_UID then p_domain.put('preserved_pallet_identity',true);end if;"""
assert a in new_rec;new_rec=new_rec.replace(a,b)
a="insert into RRL_PALLETS(UID_PALLET"
assert a in new_rec;new_rec=new_rec.replace(a,"if not v.has('preserved_pallet_identity')then\n insert into RRL_PALLETS(UID_PALLET",1)
a="values(v_uid,v_article,systimestamp,v_expiry,v_produced,v_qty,v_price,v_origin,op,v_gross,v_naklad);"
assert a in new_rec;new_rec=new_rec.replace(a,a+"\n end if;",1)
a="j.put('receiving_document_id',v_naklad);"
assert a in new_rec;new_rec=new_rec.replace(a,"if v.has('preserved_pallet_identity')then j.put('preserved_pallet_identity',true);end if;"+a,1)
ledger="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-639-preserved-return-pallet'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Preserve unchanged whole original pallet on registered PALLET return using existing stock transaction',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out={d+"000_before_unit.sql":unit,d+"000_before_receipt.sql":rec,d+"001_identity.sql":helper,d+"002_unit.sql":new_unit,d+"003_receipt.sql":new_rec,d+"004_ledger.sql":ledger,d+"apply.sql":"@@001_identity.sql\n@@002_unit.sql\n@@003_receipt.sql\n@@004_ledger.sql\n",d+"rollback.sql":"@@000_before_receipt.sql\n@@000_before_unit.sql\ndrop package RRL_RETURN_PALLET_IDENTITY;\n/\n",d+"verify.sql":"select OBJECT_NAME,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_RETURN_PALLET_IDENTITY','RRL_STORE_RETURN_UNIT_CORE','RRL_STOCK_STORE_RETURN_REC_CMD');\nselect NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_RETURN_PALLET_IDENTITY','RRL_STORE_RETURN_UNIT_CORE','RRL_STOCK_STORE_RETURN_REC_CMD');\n"}
print(json.dumps(out,ensure_ascii=True))
