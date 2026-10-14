import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni043_aggregation_lifecycle")
p=d/"001_lifecycle.sql";s=p.read_text(encoding="utf-8")
s=s.replace("CREATE TABLE", "CREATE TABLE")
schema="""begin execute immediate q'[
create table RRL_TRACE_AGG_BLOCK(
 SYSTEM_CODE varchar2(40) not null,PROFILE_CODE varchar2(80) not null,CODE_HASH varchar2(64) not null,
 INVALIDATION_OPERATION_ID varchar2(100) not null references RRL_TRACE_AGG_INVALIDATION(OPERATION_ID),
 ORIGIN_UID varchar2(200) not null,
 constraint RRL_TRACE_AGG_BLOCK_PK primary key(SYSTEM_CODE,PROFILE_CODE,CODE_HASH)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
where=s.index("create or replace package RRL_TRACE_AGG_LIFECYCLE")
s=s[:where]+schema+s[where:]
s=s.replace("digest raw(32);old_digest raw(32);old_result clob;n number;body clob;","digest raw(32);old_digest raw(32);old_result clob;n number;body clob;blocked_wire clob;blocked json_array_t;blocked_item json_object_t;")
s=s.replace("v_reference is null or not regexp_like","trim(v_reference) is null or not regexp_like")
marker="result.put('operation_id',p_operation);"
derive="""select count(*)into n from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=v_system and PROFILE_CODE=v_profile and CODE_HASH=v_hash;
 if n!=0 then raise_application_error(-20886,'TRACE_AGG_ALREADY_INVALIDATED');end if;
 select json_arrayagg(json_object('code_hash'value x.CODE_HASH)returning clob)into blocked_wire from(
 select v_hash CODE_HASH from dual
 union
 select a.CODE_HASH from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE used on used.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 where used.UID_PALLET=v_origin and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile
 and a.AGGREGATION_ID in(
 select e.PARENT_ID from(
 select j.PARENT_ID,j.CHILD_ID from RRL_TRACE_SENDER_MANIFEST manifest
 cross join json_table(manifest.RAW_JSON,'$.aggregations[*]'columns(PARENT_ID varchar2(100)path '$.aggregation_id',
 nested path '$.children[*]'columns(CHILD_ID varchar2(100)path '$')))j
 where manifest.OPERATION_ID=a.MANIFEST_OPERATION_ID and j.CHILD_ID is not null)e
 start with e.CHILD_ID=(select target.AGGREGATION_ID from RRL_TRACE_SENDER_AGG target
 where target.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID and target.SYSTEM_CODE=v_system and target.PROFILE_CODE=v_profile and target.CODE_HASH=v_hash)
 connect by nocycle prior e.PARENT_ID=e.CHILD_ID)
 union
 select parent.CODE_HASH from RRL_SAP_TRACE_AGG parent join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=parent.ORDER_ID and rec.LINE_NUMBER=parent.LINE_NUMBER
 join RRL_SAP_TRACE_AGG child on child.ORDER_ID=parent.ORDER_ID and child.LINE_NUMBER=parent.LINE_NUMBER and child.SYSTEM_CODE=parent.SYSTEM_CODE and child.PROFILE_CODE=parent.PROFILE_CODE
 where rec.UID_PALLET=v_origin and parent.SYSTEM_CODE=v_system and parent.PROFILE_CODE=v_profile and child.CODE_HASH=v_hash
 and child.AGG_LEVEL='BOX'and parent.AGG_LEVEL='PALLET'
 and not exists(select 1 from json_table(child.UNITS_JSON,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))cu
 where not exists(select 1 from json_table(parent.UNITS_JSON,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))pu where pu.UNIT_ID=cu.UNIT_ID))
 )x;
 blocked:=json_array_t.parse(blocked_wire);
 if blocked.get_size<1 or blocked.get_size>1000 then raise_application_error(-20881,'TRACE_AGG_ANCESTOR_BOUND');end if;
 """
assert s.count(marker)==1;s=s.replace(marker,derive+marker)
s=s.replace("body:=result.to_clob;\n v_journal", "result.put('blocked_aggregate_count',blocked.get_size);result.put('blocked_aggregates',blocked);body:=result.to_clob;\n v_journal")
s=s.replace("g_writing:=false;return body;","""for i in 0..blocked.get_size-1 loop
 blocked_item:=treat(blocked.get(i)as json_object_t);
 declare v_block_hash varchar2(64):=blocked_item.get_string('code_hash');begin
 insert into RRL_TRACE_AGG_BLOCK(SYSTEM_CODE,PROFILE_CODE,CODE_HASH,INVALIDATION_OPERATION_ID,ORIGIN_UID)
 select v_system,v_profile,v_block_hash,p_operation,v_origin from dual
 where not exists(select 1 from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=v_system and PROFILE_CODE=v_profile and CODE_HASH=v_block_hash);
 end;
 end loop;
 g_writing:=false;return body;""")
s+="""
create or replace trigger RRL_TRACE_AGG_BLOCK_GUARD before insert or update or delete on RRL_TRACE_AGG_BLOCK for each row
begin
 if not inserting then raise_application_error(-20863,'TRACE_AGG_BLOCK_IMMUTABLE');end if;
 RRL_TRACE_AGG_LIFECYCLE.assert_write;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
"""
scan=(d/"002_scan_guard.sql").read_text(encoding="utf-8").replace("from RRL_TRACE_AGG_INVALIDATION where SYSTEM_CODE=v_system_code","from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=v_system_code")
print(json.dumps({str(p):s,str(d/"002_scan_guard.sql"):scan}))
