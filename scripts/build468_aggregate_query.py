import json
from pathlib import Path
p=Path("db/migrations/2026-10-12_ni043_aggregation_lifecycle/001_lifecycle.sql");s=p.read_text(encoding="utf-8")
s=s.replace("expected_members number;blocked json_array_t;","expected_members number;v_manifest varchar2(100);v_node varchar2(100);blocked json_array_t;")
s=s.replace("select a.UNITS_JSON into members_wire from RRL_TRACE_SENDER_AGG","select a.UNITS_JSON,a.MANIFEST_OPERATION_ID,a.AGGREGATION_ID into members_wire,v_manifest,v_node from RRL_TRACE_SENDER_AGG")
a=s.index(" select json_arrayagg(json_object('code_hash'value x.CODE_HASH)")
b=s.index(" blocked:=json_array_t.parse(blocked_wire);",a)
new=""" if v_manifest is not null then
 select json_arrayagg(json_object('code_hash'value x.CODE_HASH)returning clob)into blocked_wire from(
 select v_hash CODE_HASH from dual
 union
 select a.CODE_HASH from RRL_TRACE_SENDER_AGG a
 where a.MANIFEST_OPERATION_ID=v_manifest and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile
 and a.AGGREGATION_ID in(
 select e.PARENT_ID from(
 select j.PARENT_ID,j.CHILD_ID from RRL_TRACE_SENDER_MANIFEST manifest
 cross join json_table(manifest.RAW_JSON,'$.aggregations[*]'columns(PARENT_ID varchar2(100)path '$.aggregation_id',
 nested path '$.children[*]'columns(CHILD_ID varchar2(100)path '$')))j
 where manifest.OPERATION_ID=v_manifest and j.CHILD_ID is not null)e
 start with e.CHILD_ID=v_node connect by nocycle prior e.PARENT_ID=e.CHILD_ID))x;
 else
 select json_arrayagg(json_object('code_hash'value x.CODE_HASH)returning clob)into blocked_wire from(
 select v_hash CODE_HASH from dual
 union
 select parent.CODE_HASH from RRL_SAP_TRACE_AGG parent join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=parent.ORDER_ID and rec.LINE_NUMBER=parent.LINE_NUMBER
 join RRL_SAP_TRACE_AGG child on child.ORDER_ID=parent.ORDER_ID and child.LINE_NUMBER=parent.LINE_NUMBER and child.SYSTEM_CODE=parent.SYSTEM_CODE and child.PROFILE_CODE=parent.PROFILE_CODE
 where rec.UID_PALLET=v_origin and parent.SYSTEM_CODE=v_system and parent.PROFILE_CODE=v_profile and child.CODE_HASH=v_hash
 and child.AGG_LEVEL='BOX'and parent.AGG_LEVEL='PALLET'
 and not exists(select 1 from json_table(child.UNITS_JSON,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))cu
 where not exists(select 1 from json_table(parent.UNITS_JSON,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))pu where pu.UNIT_ID=cu.UNIT_ID)))x;
 end if;
"""
s=s[:a]+new+s[b:]
idx="""begin execute immediate 'create index RRL_TRACE_USE_UID_IX on RRL_TRACE_MANIFEST_USE(UID_PALLET)';exception when others then if sqlcode not in(-955,-1408)then raise;end if;end;
/
begin execute immediate 'create index RRL_TRACE_AGG_BLOCK_OP_IX on RRL_TRACE_AGG_BLOCK(INVALIDATION_OPERATION_ID)';exception when others then if sqlcode not in(-955,-1408)then raise;end if;end;
/
"""
apply=Path(p.parent/"apply.sql").read_text(encoding="utf-8").replace("@@003_ledger.sql","@@004_indexes.sql\n@@003_ledger.sql")
js=Path("wiki-raw/wms_admin_ui_reference/aggregate-lifecycle.js");j=js.read_text(encoding="utf-8")
j=j.replace('const scope = () => JSON.stringify([base(), auth().state.user?.username]);','const actorScope = () => JSON.stringify([base(), auth().state.user?.username]);\n  const scope = () => JSON.stringify([actorScope(), [...(auth().state.user?.permissions || [])].sort()]);')
j=j.replace('"wms.aggregate-invalidation.v1:" + scope()','"wms.aggregate-invalidation.v1:" + actorScope()')
print(json.dumps({str(p):s,str(p.parent/"004_indexes.sql"):idx,str(p.parent/"apply.sql"):apply,str(js):j}))
