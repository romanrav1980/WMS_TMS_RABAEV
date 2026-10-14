from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni062_marked_custody");out={}
s=(f/"000_before_rrl_store_mark_core.sql").read_text(encoding="utf-8").replace("package RRL_STOCK_STORE_RECEIPT_CMD)","package RRL_STOCK_STORE_RECEIPT_CMD,package RRL_STORE_RETURN_UNIT_CORE)",1);out[str(f/"001_mark_access.sql")]=s
s=(f/"000_before_rrl_store_return_unit_core.sql").read_text(encoding="utf-8")
s=s.replace(" function accepted_units", " function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob;\n function accepted_units",1)
i=s.index(" function accepted_units",s.index("package body"))
addition=""" function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob is
  a RRL_STORE_RETURN_APPROVAL%rowtype;n number;bad number;eligible number;total number;profiles clob;units clob;proof json_object_t;lines json_array_t:=json_array_t();line_value json_object_t:=json_object_t();resolved json_array_t;
 begin
  select *into a from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=p_approval;
  select count(*)into n from RRL_STORE_RETURN_UNIT where APPROVAL_OPERATION_ID=p_approval;
  select count(*),sum(case when SCAN_MODE='UNIT'then 0 else 1 end),json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into eligible,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=a.ARTICLE;
  if n=0 and eligible=0 then
   if p_metadata.has('unit_scans')and p_metadata.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'STORE_RETURN_ORDINARY_UNEXPECTED_UNIT_SCANS');end if;
   return null;
  end if;
  if n<1 or n>10000 or eligible<1 or eligible>50 or bad!=0 or n*eligible>20000 then raise_application_error(-20886,'STORE_RETURN_APPROVED_CURRENT_UNIT_PROFILES_REQUIRED');end if;
  select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
   into eligible,total,units from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY
   where b.APPROVAL_OPERATION_ID=p_approval and u.CURRENT_UID=b.ORIGINAL_UID and u.CURRENT_CELL=b.SOURCE_CELL and u.BASE_QTY=b.BASE_QTY and u.BASE_UOM=b.BASE_UOM and u.UNIT_VERSION=b.SOURCE_UNIT_VERSION and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null;
  if eligible!=n or total!=a.BASE_QTY then raise_application_error(-20890,'CLOSURE_CHANGED: exact approved return units');end if;
  proof:=json_object_t();proof.put('units',json_array_t.parse(units));proof.put('profiles',json_array_t.parse(profiles));proof.put('physical_unit_count',n);
  line_value.put('accepted',RRL_STOCK_PLAN_HELPER.decimal_text(a.BASE_QTY));line_value.put('missing','0');line_value.put('refused','0');line_value.put('damaged','0');line_value.put('extra','0');lines.append(line_value);
  RRL_STORE_MARK_CORE.resolve_disposition(proof,p_metadata,lines,resolved);
  proof.put('units',resolved);return proof.to_clob;
 end;
"""
s=s[:i]+addition+s[i:];out[str(f/"002_unit_source.sql")]=s
s=(f/"000_before_rrl_stock_store_return_cust_cmd.sql").read_text(encoding="utf-8")
s=s.replace(" procedure compile_command"," procedure assert_scope(p_request clob,p_actor varchar2);\n procedure compile_command",1)
i=s.index(" procedure describe_context")
scope=""" procedure assert_scope(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);source json_object_t:=d.get_object('source');tr varchar2(100);addr_text varchar2(255);driver number;handed_by varchar2(50);n number;
 begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_ACTIVE_ACTOR_REQUIRED');end if;
  if d.get_string('command_type')='STORE_RETURN_HANDOVER'then
   tr:=source.get_string('transport_operation_id');
   select STORE_ADDR into addr_text from RRL_STORE_RETURN_TRANSPORT where OPERATION_ID=tr;
   if RRL_HAS_WRIGHT(p_actor,'store_return_handover')!=1 then raise_application_error(-20882,'STORE_RETURN_HANDOVER_FORBIDDEN');end if;
   RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,addr_text);
  else
   tr:=source.get_string('handover_operation_id');
   select t.DRIVER_ID,h.HANDED_BY into driver,handed_by from RRL_STORE_RETURN_HANDOVER h join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID where h.OPERATION_ID=tr;
   select count(*)into n from RRL_TRANSPORT_DRIVER_USER b join RUSERS u on u.ID=b.USER_ID where b.DRIVER_ID=driver and b.USER_ID=p_actor and b.ACTIVE=1 and nvl(u.DELETED,0)=0 and upper(trim(u.USER_GROUP))!='GLOBAL_ADMIN';
   if n!=1 or handed_by=p_actor or RRL_HAS_WRIGHT(p_actor,'driver_return_accept')!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_SEPARATE_BOUND_DRIVER_REQUIRED');end if;
  end if;
 exception when no_data_found then raise_application_error(-20882,'STORE_RETURN_CURRENT_CUSTODY_SCOPE_REQUIRED');
 end;
"""
s=s[:i]+scope+s[i:]
s=s.replace("n number;v_mass number;","unit_proof clob;n number;v_mass number;",1)
s=s.replace(" select * into approved from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=transport.APPROVAL_OPERATION_ID;"," select * into approved from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=transport.APPROVAL_OPERATION_ID;\n assert_scope(p_request,p_actor);unit_proof:=RRL_STORE_RETURN_UNIT_CORE.custody_proof(approved.OPERATION_ID,m);",1)
s=s.replace(" if v_kind='STORE_RETURN_PICKUP' then p_domain.put('handover_operation_id'"," if unit_proof is not null then p_domain.put('return_unit_proof',json_object_t.parse(unit_proof));end if;\n if v_kind='STORE_RETURN_PICKUP' then p_domain.put('handover_operation_id'",1)
s=s.replace("v_kind varchar2(80):=d.get_string('command_type');\n begin\n describe_context","v_kind varchar2(80):=d.get_string('command_type');unit_value json_object_t;unit_wire clob;\n begin\n describe_context",1)
s=s.replace(" p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;", """ RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_APPROVAL',v.get_string('approval_operation_id'));
 if v.has('return_unit_proof')then
  unit_wire:=v.get_object('return_unit_proof').get_array('units').to_clob;
  for z in(select K from json_table(unit_wire,'$[*]'columns(K varchar2(64)path '$.key')))loop
   RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',z.K);
  end loop;
 end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;""",1)
s=s.replace(" j.put('operation_id',op);"," if v.has('return_unit_proof')then j.put('physical_unit_count',v.get_object('return_unit_proof').get_number('physical_unit_count'));j.put('mark_scan_confirmed',true);end if;\n j.put('operation_id',op);",1)
out[str(f/"003_custody.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
needle="  if g_kind='STORE_CUSTODY_RELEASE'"
s=s.replace(needle,"  if g_kind in('STORE_RETURN_HANDOVER','STORE_RETURN_PICKUP')then RRL_STOCK_STORE_RETURN_CUST_CMD.assert_scope(p_request,p_actor);end if;\n"+needle)
out[str(f/"004_root.sql")]=s
out[str(f/"005_recompile.sql")]="\n".join("alter package "+p+" compile body;\n/"for p in["RRL_STORE_MARK_CORE","RRL_STORE_RETURN_UNIT_CORE","RRL_STOCK_STORE_RETURN_CMD","RRL_STOCK_STORE_RETURN_CUST_CMD","RRL_STOCK_POSTING_API"])+"\n"
out[str(f/"rollback.sql")]="@@000_before_rrl_stock_posting_api.sql\n@@000_before_rrl_stock_store_return_cust_cmd.sql\n@@000_before_rrl_store_return_unit_core.sql\n@@000_before_rrl_store_mark_core.sql\n"
out["wiki/database/retailcase_ni062_marked_custody_design_20261011.md"]="# NI06.2: сканирование точных согласованных единиц при возврате\n233 preserves original handover/pickup owners/two actors/current driver binding/trip/capacity. Native exact approved issued keys/source/version/current UNIT profiles validated by existing store marked scanner (no new parser/quantity writer). Frozen proof rechecked under UNIT60 locks and CONFIG fence. Current scope before cached result/after wait. No stock/code birth at pickup. Warehouse receipt separately next.\n"
print(json.dumps(out,ensure_ascii=True))
