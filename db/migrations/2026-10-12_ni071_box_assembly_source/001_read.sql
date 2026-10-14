create or replace package RRL_BOX_ASSEMBLY_READ authid definer as
 function clocks_json(p_tree clob,p_ware number,p_region varchar2)return clob;
end;
/
create or replace package body RRL_BOX_ASSEMBLY_READ as
 function clocks_json(p_tree clob,p_ware number,p_region varchar2)return clob is
 tree json_object_t:=json_object_t.parse(p_tree);nodes json_array_t:=tree.get_array('nodes');
 result json_array_t:=json_array_t();node json_object_t;j json_object_t;packing json_object_t;
 uid varchar2(200);instant timestamp with time zone;clock_op varchar2(100);start_version number;latest_version number;case_id number;source_ware number;box_version number;wire_instant varchar2(40);region_check varchar2(64);
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
      source_ware:=packing.get_number('warehouse');box_version:=node.get_number('version');wire_instant:=packing.get_string('instant');
      begin
       select c.STARTED_AT_INSTANT into instant from RRL_HU_PACK_CYCLE c
       join RRL_STOCK_OPERATION op on op.OPERATION_ID=c.START_OPERATION_ID and op.STATE='APPLIED'
       where c.PARENT_UID=uid and c.START_OPERATION_ID=clock_op and c.START_CONTENT_VERSION=start_version
       and c.WARE_ID=p_ware and c.WARE_ID=source_ware
       and c.START_CONTENT_VERSION<=box_version
       and to_char(c.STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')=wire_instant;
       select max(START_CONTENT_VERSION)into latest_version from RRL_HU_PACK_CYCLE
       where PARENT_UID=uid and START_CONTENT_VERSION<=box_version;
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
