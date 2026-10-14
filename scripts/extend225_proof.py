raise SystemExit("Retired authoring generator: use final225 SQL/fresh checkpoints; never overwrite live source or proof schema")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_marked_source");out={}
out[str(f/"003_manifest_schema.sql")]="""create table RRL_INTERWARE_UNIT_MANIFEST(
 PLAN_OPERATION_ID varchar2(100)primary key references RRL_INTERWARE_PLAN(OPERATION_ID),
 UNIT_SIGNATURE varchar2(64)not null,
 MANIFEST_JSON clob not null check(MANIFEST_JSON is json),
 CREATED_BY nvarchar2(50)not null,
 CREATED_AT timestamp with time zone default systimestamp not null
);
"""
s=(f/"001_unit_source.sql").read_text(encoding="utf-8");anchor=" function issued_manifest(p_load";idx=s.index(anchor);s=s[:idx]+""" procedure capture_plan(p_plan varchar2,p_actor varchar2);
 function plan_manifest(p_plan varchar2,p_actor varchar2)return clob;
"""+s[idx:]
idx=s.rfind("end;\n/");assert idx>0
body=""" procedure capture_plan(p_plan varchar2,p_actor varchar2)is
  plan RRL_INTERWARE_PLAN%rowtype;wire clob;signature_value varchar2(64);n number;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=p_plan;
  assert_scope(plan.SOURCE_LOAD_OPERATION_ID,p_actor);
  select count(*)into n from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=p_plan;
  if n>0 then return;end if;
  select count(*)into n from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=p_plan;
  if n>0 then raise_application_error(-20886,'INTERWARE_MANIFEST_CAPTURE_BEFORE_RECEIPT_REQUIRED');end if;
  select count(*)into n from RRL_REMAINS where UID_POLETA=plan.ROOT_UID and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0);
  if n>0 then raise_application_error(-20886,'INTERWARE_SOURCE_STOCK_ALREADY_PRESENT');end if;
  wire:=issued_manifest(plan.SOURCE_LOAD_OPERATION_ID,plan.ROOT_UID,plan.SOURCE_COMPOSITION_JSON);
  if json_object_t.parse(wire).get_number('physical_unit_count')=0 then return;end if;
  signature_value:=json_object_t.parse(wire).get_string('unit_signature');
  insert into RRL_INTERWARE_UNIT_MANIFEST(PLAN_OPERATION_ID,UNIT_SIGNATURE,MANIFEST_JSON,CREATED_BY)values(p_plan,signature_value,wire,p_actor);
 end;
 function plan_manifest(p_plan varchar2,p_actor varchar2)return clob is n number;wire clob;
 begin
  select count(*)into n from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=p_actor where p.OPERATION_ID=p_plan and nvl(u.DELETED,0)=0
   and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'or(u.WARE_ID=p.SOURCE_WARE_ID and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1)or(u.WARE_ID=p.TARGET_WARE_ID and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1));
  if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_MANIFEST_READER_REQUIRED');end if;
  begin select MANIFEST_JSON into wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=p_plan;
  exception when no_data_found then return '{"units":[],"physical_unit_count":0,"unit_capture_required":false}';end;
  return wire;
 end;
"""
s=s[:idx]+body+s[idx:];out[str(f/"004_unit_source.sql")]=s
out[str(f/"005_manifest_guard.sql")]="""create or replace trigger RRL_INTERWARE_UNIT_MANIFEST_G before insert or update or delete on RRL_INTERWARE_UNIT_MANIFEST for each row
declare plan RRL_INTERWARE_PLAN%rowtype;wire clob;j json_object_t;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_UNIT_MANIFEST_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=:new.PLAN_OPERATION_ID;
 RRL_INTERWARE_UNIT_SOURCE.assert_scope(plan.SOURCE_LOAD_OPERATION_ID,:new.CREATED_BY);
 wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(plan.SOURCE_LOAD_OPERATION_ID,plan.ROOT_UID,plan.SOURCE_COMPOSITION_JSON);j:=json_object_t.parse(wire);
 if j.get_number('physical_unit_count')=0 or j.get_string('unit_signature')!=:new.UNIT_SIGNATURE or dbms_lob.compare(wire,:new.MANIFEST_JSON)!=0 then raise_application_error(-20863,'INTERWARE_UNIT_MANIFEST_EXACT_SOURCE_REQUIRED');end if;
end;
/
"""
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
anchor="                return result\n        except oracledb.DatabaseError"
assert anchor in s;s=s.replace(anchor,'                cur.callproc("RRL_INTERWARE_UNIT_SOURCE.capture_plan",[operation_id,actor])\n'+anchor,1);out[str(p)]=s
out[str(f/"apply.sql")]="@@001_unit_source.sql\n@@002_plan_guard.sql\n@@003_manifest_schema.sql\n@@004_unit_source.sql\n@@005_manifest_guard.sql\n"
p=f/"rollback.sql";s=p.read_text(encoding="utf-8").replace("drop package RRL_INTERWARE_UNIT_SOURCE;","drop table RRL_INTERWARE_UNIT_MANIFEST;\ndrop package RRL_INTERWARE_UNIT_SOURCE;");out[str(p)]=s
out[str(f/"apply_manifest.sql")]="@@003_manifest_schema.sql\n@@004_unit_source.sql\n@@005_manifest_guard.sql\n"
print(json.dumps(out,ensure_ascii=True))
