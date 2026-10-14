import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni041_box_packing_clock");out={}
out[str(d/"001_schema.sql")]="""begin execute immediate q'[create table RRL_HU_PACK_CYCLE(
 PARENT_UID varchar2(200)not null references RRL_PALLETS(UID_PALLET),
 START_CONTENT_VERSION number(19)not null check(START_CONTENT_VERSION>0),
 START_OPERATION_ID varchar2(100)not null references RRL_STOCK_OPERATION(OPERATION_ID),
 WARE_ID number not null,ACTOR nvarchar2(50)not null,
 STARTED_AT_INSTANT timestamp with time zone not null,
 primary key(PARENT_UID,START_CONTENT_VERSION),unique(PARENT_UID,START_OPERATION_ID))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[str(d/"002_clock.sql")]="""create or replace package RRL_HU_PACK_CLOCK authid definer as
 procedure begin_empty_box(p_uid varchar2,p_operation varchar2,p_actor varchar2);
 function clock_json(p_uid varchar2,p_version number)return json_object_t;
 function writing return boolean;
end;
/
create or replace package body RRL_HU_PACK_CLOCK as
 g_writing boolean:=false;
 function writing return boolean is begin return g_writing;end;
 procedure begin_empty_box(p_uid varchar2,p_operation varchar2,p_actor varchar2)is
 p RRL_PALLETS%rowtype;n number;ware number;kind varchar2(80);state varchar2(20);actor nvarchar2(50);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'BOX_PACKING_ROOT_CONTEXT_REQUIRED');end if;
  select COMMAND_TYPE,STATE,ACTOR_ID into kind,state,actor from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  if kind not in('HU_ATTACH','HU_REPACK')or state!='IN_FLIGHT'or actor!=p_actor then raise_application_error(-20863,'BOX_PACKING_ATTACH_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
  select *into p from RRL_PALLETS where UID_PALLET=p_uid;
  if p.HU_KIND!='CONTAINER'or p.HU_TYPE!='BOX'then return;end if;
  select count(*)into n from RRL_WMS_HU_LINK where PARENT_UID=p_uid and ACTIVE_FLAG=1;
  if n!=0 then return;end if;
  select WARE_ID into ware from RRL_CELLS where CELL=p.HU_CURRENT_CELL;
  g_writing:=true;
  insert into RRL_HU_PACK_CYCLE(PARENT_UID,START_CONTENT_VERSION,START_OPERATION_ID,WARE_ID,ACTOR,STARTED_AT_INSTANT)
  values(p_uid,p.HU_CONTENT_VERSION+1,p_operation,ware,p_actor,systimestamp);
  g_writing:=false;
 exception when others then g_writing:=false;raise;
 end;
 function clock_json(p_uid varchar2,p_version number)return json_object_t is
 j json_object_t;r RRL_HU_PACK_CYCLE%rowtype;
 begin
  select *into r from RRL_HU_PACK_CYCLE where PARENT_UID=p_uid and START_CONTENT_VERSION<=p_version
   order by START_CONTENT_VERSION desc fetch first 1 row only;
  j:=json_object_t();j.put('operation_id',r.START_OPERATION_ID);j.put('content_version',r.START_CONTENT_VERSION);
  j.put('warehouse',r.WARE_ID);
  j.put('instant',to_char(r.STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
  return j;
 exception when no_data_found then return null;
 end;
end;
/
create or replace trigger RRL_HU_PACK_CYCLE_GUARD before insert or update or delete on RRL_HU_PACK_CYCLE for each row
begin
 if not inserting or not RRL_HU_PACK_CLOCK.writing then raise_application_error(-20863,'BOX_PACKING_CLOCK_IMMUTABLE');end if;
end;
/
"""
for name,target in [("RRL_STOCK_HU_CMD","003_command.sql"),("RRL_STOCK_HU_READ","004_read.sql")]:
 src=Path("tmp/packing516/"+name+".sql").read_text(encoding="utf-8")
 out[str(d/("000_before_"+name.lower()+".sql"))]=src
 if name=="RRL_STOCK_HU_CMD":
  needle="   if v_kind='HU_ATTACH' then\n    insert into RRL_WMS_HU_LINK"
  assert src.count(needle)==1
  src=src.replace(needle,"   if v_kind='HU_ATTACH' then\n    RRL_HU_PACK_CLOCK.begin_empty_box(v_uid,v_op,p_actor);\n    insert into RRL_WMS_HU_LINK")
 else:
  needle="   if p.HU_KIND='CONTAINER' then\n    cell_name:=p.HU_CURRENT_CELL;"
  assert src.count(needle)==1
  src=src.replace(needle,"""   if p.HU_KIND='CONTAINER' then
    if p.HU_TYPE='BOX'then
     declare packing json_object_t:=RRL_HU_PACK_CLOCK.clock_json(p_id,p.HU_CONTENT_VERSION);begin
      if packing is not null then a.put('packing_start',packing);end if;
     end;
    end if;
    cell_name:=p.HU_CURRENT_CELL;""")
 out[str(d/target)]=src
out[str(d/"005_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-516-box-physical-packing-clock' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'First scanned child attachment into empty BOX starts immutable packing cycle; no legacy clock inference',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out[str(d/"apply.sql")]="@@001_schema.sql\n@@002_clock.sql\n@@003_command.sql\n@@004_read.sql\n@@005_ledger.sql\n"
out[str(d/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_HU_PACK_CYCLE;
 if n!=0 then raise_application_error(-20886,'BOX_PACKING_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_hu_cmd.sql
@@000_before_rrl_stock_hu_read.sql
drop trigger RRL_HU_PACK_CYCLE_GUARD;
drop package RRL_HU_PACK_CLOCK;
drop table RRL_HU_PACK_CYCLE;
-- Preserve all APPLIED inventory and shipping facts; no historical clock deletion.
"""
print(json.dumps(out))
