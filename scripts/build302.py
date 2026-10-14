from pathlib import Path
import json,re
d=Path("db/migrations/2026-10-11_ni061_recovery_redelivery");out={}
def put(n,s):out[(d/n).as_posix()]=s
put("001_schema.sql","""declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_ST_BIND';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_ST_BIND(
 OPERATION_ID varchar2(100)primary key,PAYLOAD_HASH raw(32)not null,
 RECOVERY_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 ST_ID number not null unique,ST_IDENTIFIER varchar2(50)not null unique,SOURCE_ST_ID number not null,SOURCE_LOAD_OPERATION_ID varchar2(100)not null,
 TARGET_TT_ID number not null,WARE_ID number not null,ROOT_UID varchar2(200)not null,STOCK_VERSION number not null,SOURCE_CELL varchar2(60)not null,
 FINAL_ADDRESS varchar2(255)not null,ORIGINAL_FULFILLMENT_JSON clob not null check(ORIGINAL_FULFILLMENT_JSON is json),
 REASON_TEXT varchar2(500 CHAR)not null,DECISION_REFERENCE varchar2(255 CHAR)not null,ACTOR varchar2(100)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 FINAL_ADDRESS_SOURCE varchar2(30)not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_DISPATCH';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_DISPATCH(
 OPERATION_ID varchar2(100)primary key,BIND_OPERATION_ID varchar2(100)not null unique references RRL_IW_RECOVERY_ST_BIND(OPERATION_ID),
 RECOVERY_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 SOURCE_LOAD_OPERATION_ID varchar2(100)not null,ST_ID number not null,ROOT_UID varchar2(200)not null,BASE_QTY number not null check(BASE_QTY>0),
 BASE_UOM varchar2(20)not null,ACTOR varchar2(100)not null,CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_REC_DISPATCH_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_IW_REC_DISPATCH_SOURCE_IX on RRL_IW_RECOVERY_DISPATCH(SOURCE_LOAD_OPERATION_ID,OPERATION_ID)';end if;
end;
/
""")
spec=(d/"000_before_rrl_stock_interware_next_package.sql").read_text(encoding="utf-8")
s=(d/"000_before_rrl_stock_interware_next_package_body.sql").read_text(encoding="utf-8")
s=s.replace("RRL_STOCK_INTERWARE_NEXT","RRL_STOCK_IW_RECOVERY_NEXT")
s=s.replace("RRL_INTERWARE_ONWARD_BIND","RRL_IW_RECOVERY_ST_BIND").replace("RRL_INTERWARE_ONWARD_DISPATCH","RRL_IW_RECOVERY_DISPATCH")
s=s.replace("receipt RRL_INTERWARE_RECEIPT%rowtype;placed RRL_INTERWARE_PLACEMENT%rowtype;","receipt RRL_INTERWARE_RECOVERY_RECEIPT%rowtype;placed RRL_IW_RECOVERY_PLACEMENT%rowtype;")
s=s.replace("select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=bind.RECEIPT_OPERATION_ID;","select *into receipt from RRL_INTERWARE_RECOVERY_RECEIPT where OPERATION_ID=bind.RECOVERY_OPERATION_ID;")
s=s.replace("select *into placed from RRL_INTERWARE_PLACEMENT where RECEIPT_OPERATION_ID=receipt.OPERATION_ID;","select *into placed from RRL_IW_RECOVERY_PLACEMENT where RECOVERY_OPERATION_ID=receipt.OPERATION_ID;")
s=s.replace("where RECEIPT_OPERATION_ID=receipt.OPERATION_ID;if n!=1","where RECEIPT_OPERATION_ID=bind.RECEIPT_OPERATION_ID;if n!=1",1)
a=s.index("  if receipt.ORIGINAL_ROOT_UID is not null then");b=s.index("  select count(*),sum(u.BASE_QTY)",a)
s=s[:a]+"""  receipt_domain:=json_object_t.parse(receipt.SOURCE_JSON);subset_wire:=json_object_t();
  subset_wire.put('units',receipt_domain.get_array('source_units'));subset_wire.put('physical_unit_count',receipt_domain.get_array('source_units').get_size);unit_wire:=subset_wire.to_clob;
"""+s[b:]
s=s.replace("j.put('receipt_operation_id',receipt.OPERATION_ID);","j.put('receipt_operation_id',bind.RECEIPT_OPERATION_ID);j.put('recovery_operation_id',receipt.OPERATION_ID);",1)
s=s.replace("row_key(p_resources,'RRL_INTERWARE_RECEIPT',p_source.get_string('receipt_operation_id'));","row_key(p_resources,'RRL_INTERWARE_RECOVERY_RECEIPT',p_source.get_string('recovery_operation_id'));",1)
s=s.replace("v_receipt varchar2(100):=p_source.get_string('receipt_operation_id');","v_receipt varchar2(100):=p_source.get_string('receipt_operation_id');v_recovery varchar2(100):=p_source.get_string('recovery_operation_id');",1)
s=s.replace("OPERATION_ID,BIND_OPERATION_ID,RECEIPT_OPERATION_ID,SOURCE_LOAD_OPERATION_ID","OPERATION_ID,BIND_OPERATION_ID,RECOVERY_OPERATION_ID,RECEIPT_OPERATION_ID,SOURCE_LOAD_OPERATION_ID",1)
s=s.replace("values(op,v_bind,v_receipt,v_source","values(op,v_bind,v_recovery,v_receipt,v_source",1)
s=s.replace("'IW.ONWARD:'","'IW.RECOVERY.ONWARD:'").replace("'INTERWARE_ONWARD_DISPATCHED'","'INTERWARE_RECOVERY_DISPATCHED'")
put("002_recovery_next.sql",spec.replace("RRL_STOCK_INTERWARE_NEXT","RRL_STOCK_IW_RECOVERY_NEXT").replace("RRL_STOCK_SHIPPING_CORE","RRL_STOCK_INTERWARE_NEXT")+"\n"+s)
s=(d/"000_before_rrl_stock_interware_next_package_body.sql").read_text(encoding="utf-8")
s=s.replace("exception when no_data_found then return null;end;","exception when no_data_found then return RRL_STOCK_IW_RECOVERY_NEXT.describe_source(p_st,p_ware);end;",1)
for name,args in [
("declare_source","p_source,p_operation,p_resources"),
("validate_load","p_source,p_actor"),
("dispatched","p_source,p_actor")]:
 start=s.index(" procedure "+name+"(");at=s.index(" begin",start)+len(" begin")
 s=s[:at]+"\n if p_source.has('recovery_operation_id')then RRL_STOCK_IW_RECOVERY_NEXT."+name+"("+args+");return;end if;"+s[at:]
put("003_next_body.sql",s)
put("004_dispatch_guard.sql","""create or replace trigger RRL_IW_REC_DISPATCH_GUARD before insert or update or delete on RRL_IW_RECOVERY_DISPATCH for each row
begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_DISPATCH_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'LOAD_SHIPMENT');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_DISPATCH',:new.OPERATION_ID));
end;
/
create or replace trigger RRL_IW_REC_ST_IMMUTABLE before update or delete on RRL_IW_RECOVERY_ST_BIND for each row
begin raise_application_error(-20878,'RECOVERY_ST_BIND_IMMUTABLE');end;
/
""")
put("apply.sql","@@001_schema.sql\n@@002_recovery_next.sql\n@@003_next_body.sql\n@@004_dispatch_guard.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n")
put("rollback.sql","""declare n number;begin select count(*)into n from RRL_IW_RECOVERY_ST_BIND;if n>0 then raise_application_error(-20878,'RETAINED_RECOVERY_DELIVERY_REQUIRES_FORWARD_FIX');end if;end;
/
@@000_before_rrl_stock_interware_next_package_body.sql
drop trigger RRL_IW_REC_DISPATCH_GUARD;
drop trigger RRL_IW_REC_ST_IMMUTABLE;
drop package RRL_STOCK_IW_RECOVERY_NEXT;
drop table RRL_IW_RECOVERY_DISPATCH;
drop table RRL_IW_RECOVERY_ST_BIND;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
""")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_INTERWARE_NEXT','RRL_STOCK_IW_RECOVERY_NEXT');\n")
print(json.dumps(out))
