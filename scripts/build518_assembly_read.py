import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni071_box_assembly_source");out={}
out[str(d/"001_read.sql")]='''create or replace package RRL_BOX_ASSEMBLY_READ authid definer as
 function clocks_json(p_tree clob,p_ware number,p_region varchar2)return clob;
end;
/
create or replace package body RRL_BOX_ASSEMBLY_READ as
 function clocks_json(p_tree clob,p_ware number,p_region varchar2)return clob is
 tree json_object_t:=json_object_t.parse(p_tree);nodes json_array_t:=tree.get_array('nodes');
 result json_array_t:=json_array_t();node json_object_t;j json_object_t;packing json_object_t;
 uid varchar2(200);instant timestamp with time zone;clock_op varchar2(100);start_version number;latest_version number;case_id number;region_check varchar2(64);
 type keys is table of boolean index by varchar2(200);seen keys;
 begin
  select to_char(systimestamp at time zone(p_region),'TZR')into region_check from dual;
  if nodes is null or nodes.get_size<1 or nodes.get_size>200 then raise_application_error(-20886,'COST_FROZEN_TREE_BOUND');end if;
  for i in 0..nodes.get_size-1 loop
   node:=treat(nodes.get(i)as json_object_t);uid:=node.get_string('uid');
   if uid is null or seen.exists(uid)then raise_application_error(-20886,'COST_FROZEN_TREE_IDENTITY');end if;seen(uid):=true;
   if (node.get_string('kind')='CASE'and node.has('scale_qc'))or
    (node.get_string('kind')='CONTAINER'and node.get_string('type')='BOX')then
    j:=json_object_t();j.put('box_identifier',uid);j.put('content_version',node.get_number('version'));
    instant:=null;clock_op:=null;start_version:=null;case_id:=null;
    if node.get_string('kind')='CASE'then
     case_id:=node.get_number('case_task_id');j.put('case_task_id',case_id);
     begin select STARTED_AT_INSTANT into instant from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id and WARE_ID=p_ware;
     exception when no_data_found then null;end;
     j.put('source_kind','CASE_START');j.put('state','MISSING_ACTUAL_START');
    else
     j.put('source_kind','BOX_PACKING');j.put('state','ASSEMBLY_SOURCE_NOT_LINKED');
     if node.has('packing_start')then
      packing:=node.get_object('packing_start');clock_op:=packing.get_string('operation_id');start_version:=packing.get_number('content_version');
      begin
       select c.STARTED_AT_INSTANT into instant from RRL_HU_PACK_CYCLE c
       join RRL_STOCK_OPERATION op on op.OPERATION_ID=c.START_OPERATION_ID and op.STATE='APPLIED'
       where c.PARENT_UID=uid and c.START_OPERATION_ID=clock_op and c.START_CONTENT_VERSION=start_version
       and c.WARE_ID=p_ware and c.WARE_ID=packing.get_number('warehouse')
       and c.START_CONTENT_VERSION<=node.get_number('version')
       and to_char(c.STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')=packing.get_string('instant');
       select max(START_CONTENT_VERSION)into latest_version from RRL_HU_PACK_CYCLE
       where PARENT_UID=uid and START_CONTENT_VERSION<=node.get_number('version');
       if latest_version!=start_version then instant:=null;end if;
      exception when no_data_found then instant:=null;end;
     end if;
     j.put('start_operation_id',clock_op);j.put('start_content_version',start_version);
    end if;
    if instant is not null then
     j.put('instant',to_char(instant,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
     j.put('business_date',to_char(instant at time zone(p_region),'YYYY-MM-DD'));j.put('state','READY');
    end if;
    result.append(j);
   end if;
  end loop;
  return result.to_clob;
 end;
end;
/
'''
# JSON_OBJECT_T methods are not SQL expressions: move payload scalars to locals.
v=out[str(d/"001_read.sql")].replace("case_id number;region_check","case_id number;source_ware number;box_version number;wire_instant varchar2(40);region_check")
v=v.replace("      begin\n       select", "      source_ware:=packing.get_number('warehouse');box_version:=node.get_number('version');wire_instant:=packing.get_string('instant');\n      begin\n       select")
v=v.replace("packing.get_number('warehouse')","source_ware",1) if False else v
v=v.replace("c.WARE_ID=packing.get_number('warehouse')","c.WARE_ID=source_ware").replace("c.START_CONTENT_VERSION<=node.get_number('version')","c.START_CONTENT_VERSION<=box_version").replace("=packing.get_string('instant');","=wire_instant;").replace("START_CONTENT_VERSION<=node.get_number('version');","START_CONTENT_VERSION<=box_version;")
out[str(d/"001_read.sql")]=v
src=Path("db/migrations/2026-10-12_ni071_cost_periods/003_guard.sql").read_text(encoding="utf-8")
out[str(d/"000_before_guard.sql")]=src
src=src.replace("rate_version number;","rate_version number;clock_body clob;ready_count number;")
a=src.index(" else\n  select count(*)into n",src.index(" if policy_mode='LOADED_UTC'"));b=src.index("  expected_day:=case",a)
src=src[:a]+""" else
  clock_body:=RRL_BOX_ASSEMBLY_READ.clocks_json(archive_body,ware,policy_zone);
  select count(*),sum(case when j.STATE_VALUE='READY'then 1 else 0 end)into n,ready_count
  from json_table(clock_body,'$[*]'columns(STATE_VALUE varchar2(40)path '$.state'))j;
  select count(*)into latest_version from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
  if n!=latest_version or ready_count!=n then raise_application_error(-20886,'COST_EACH_BOX_ACTUAL_START_REQUIRED');end if;
  select count(*)into n from json_table(clock_body,'$[*]'columns(DAY_VALUE varchar2(10)path '$.business_date'))j
  where j.DAY_VALUE=to_char(:new.RATE_DATE,'YYYY-MM-DD');
""" +src[b:]
out[str(d/"002_guard.sql")]=src
out[str(d/"003_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-518-shared-box-assembly-date-source' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'One readonly native clock resolver for actual CASE/BOX start used by finance preview and posting guards',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out[str(d/"apply.sql")]="@@001_read.sql\n@@002_guard.sql\n@@003_ledger.sql\n"
out[str(d/"rollback.sql")]="@@000_before_guard.sql\n-- Restore Python clock resolver together; original posted facts remain immutable.\n"
out["api/wms_api_server/app/modules/finance/infrastructure/box_assembly_clocks.py"]='''"""Use one native readonly assembly clock authority for CASE and ordinary BOX."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json


def box_assembly_clocks(cursor: Any,tree: dict[str,Any],ware: int,region: str)->list[dict[str,Any]]:
    cursor.setinputsizes(tree_body=oracledb.DB_TYPE_CLOB)
    cursor.execute("select RRL_BOX_ASSEMBLY_READ.clocks_json(:tree_body,:ware,:region)from dual",
                   tree_body=json.dumps(tree),ware=ware,region=region)
    return read_oracle_json(cursor.fetchone()[0])
'''
p=Path("api/wms_api_server/app/modules/finance/infrastructure/cost_period_lines.py");v=p.read_text(encoding="utf-8")
v=v.replace("from ..domain.amount import cost_amount","from ..domain.amount import cost_amount\nfrom .box_assembly_clocks import box_assembly_clocks")
a=v.index("        case_ids=");b=v.index("    # Rate revisions",a)
v=v[:a]+'''        clocks=box_assembly_clocks(cursor,tree,ware,policy["timezone_region"])
        if len(clocks)!=boxes or any(row["state"]!="READY"for row in clocks):
            raise LogisticsCostError("COST_ACTUAL_ASSEMBLY_START_REQUIRED","Каждой коробке нужен достоверный источник начала сборки на этом складе")
        counts=Counter(row["business_date"]for row in clocks)
''' +v[b:]
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/infrastructure/assembly_period.py");v=p.read_text(encoding="utf-8")
v=v.replace("from .cost_access import require_warehouse","from .cost_access import require_warehouse\nfrom .box_assembly_clocks import box_assembly_clocks")
a=v.index("        case_ids=");b=v.index("        if len(lines)>10000:",a)
v=v[:a]+'''        lines=[]
        for load,composition,status in loads:
            tree=read_oracle_json(composition)
            for clock in box_assembly_clocks(cursor,tree,ware,region):
                if status!="DEPARTED"and clock["state"]=="READY":
                    clock={**clock,"state":"ACTUAL_DEPARTURE_REQUIRED"}
                lines.append({"load_operation_id":load,**clock})
''' +v[b:]
out[str(p)]=v
print(json.dumps(out))
