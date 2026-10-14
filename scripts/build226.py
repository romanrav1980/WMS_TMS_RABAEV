raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_marked_receive");out={}
def old(n):return(f/("000_before_"+n+".sql")).read_text(encoding="utf-8")
qc=old("rrl_stock_qc_mark").replace("RRL_STOCK_QC_MARK","RRL_INTERWARE_MARK_SCAN").replace("STOCK_STATUS='AVAILABLE'","STOCK_STATUS='ISSUED'")
# Dedicated transit validator reuses exact native code/profile matrix; no stock writer.
qc=qc.replace("if v_profiles<1 or v_profiles>50", """select count(*) into v_count from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article and (SCAN_MODE is null or SCAN_MODE!='UNIT');
   if v_count>0 then raise_application_error(-20887,'INTERWARE_UNIT_SCAN_MODE_REQUIRED');end if;
   if v_profiles<1 or v_profiles>50""")
out[str(f/"001_mark_scan.sql")]=qc
u=old("rrl_stock_unit_core").replace("accessible by(","accessible by(package RRL_STOCK_INTERWARE_REC,")
decl=" procedure receive_issued(p_uid varchar2,p_source_cell varchar2,p_target_cell varchar2,p_qty number,p_units clob);"
u=u.replace(" procedure restore_issued(",decl+"\n procedure restore_issued(",1)
method=""" procedure receive_issued(p_uid varchar2,p_source_cell varchar2,p_target_cell varchar2,p_qty number,p_units clob)is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;expected_count number;actual_count number;total number;locked_version number;
 begin
  require_context;RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain'columns(U varchar2(150)path '$.uid',S varchar2(60)path '$.source_cell',T varchar2(60)path '$.receive_cell',Q varchar2(60)path '$.quantity',A clob format json path '$.source_units'))d
   on d.U=p_uid and d.S=p_source_cell and d.T=p_target_cell and d.Q=RRL_STOCK_PLAN_HELPER.decimal_text(p_qty) and dbms_lob.compare(d.A,p_units)=0
   where o.OPERATION_ID=op and o.COMMAND_TYPE='INTERWARE_RECEIVE'and o.STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'INTERWARE_UNIT_RECEIPT_PLAN_REQUIRED');end if;
  select count(*),count(distinct K)into expected_count,n from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'));
  if expected_count<1 or expected_count>10000 or n!=expected_count then raise_application_error(-20884,'INTERWARE_UNIT_SET_REQUIRED');end if;
  select count(*),sum(BASE_QTY)into actual_count,total from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid;
  if actual_count!=expected_count or total!=p_qty then raise_application_error(-20884,'INTERWARE_WHOLE_UNIT_SET_REQUIRED');end if;
  actual_count:=0;
  for x in(select u.PHYSICAL_UNIT_KEY,u.UNIT_VERSION,u.STOCK_STATUS,u.HARD_RESERVATION_ID,u.BASE_QTY,u.BASE_UOM,j.V,j.Q,j.B
   from RRL_WMS_RECEIPT_UNIT u join json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key',V number path '$.version',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j on j.K=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_source_cell order by u.PHYSICAL_UNIT_KEY)loop
   own_unit(x.PHYSICAL_UNIT_KEY);
   select UNIT_VERSION into locked_version from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=x.PHYSICAL_UNIT_KEY for update;
   if locked_version!=x.V or x.UNIT_VERSION!=x.V or x.STOCK_STATUS!='ISSUED'or x.HARD_RESERVATION_ID is not null or x.BASE_QTY!=RRL_STOCK_MATH.quantity(x.Q)or x.BASE_UOM!=x.B then raise_application_error(-20890,'CLOSURE_CHANGED: interware original unit');end if;
   actual_count:=actual_count+1;
  end loop;
  if actual_count!=expected_count then raise_application_error(-20884,'INTERWARE_UNIT_SOURCE_CONFLICT');end if;
  -- Guard checks OLD source binding; update keeps birth provenance and every code unchanged.
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_source_cell);
  update RRL_WMS_RECEIPT_UNIT set CURRENT_CELL=p_target_cell,STOCK_STATUS='AVAILABLE',HARD_RESERVATION_ID=null,UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_source_cell and STOCK_STATUS='ISSUED';
  if sql%rowcount!=expected_count then raise_application_error(-20890,'CLOSURE_CHANGED: interware unit count');end if;
  RRL_STOCK_CTX_API.end_effect;assert_composition(p_uid,p_target_cell);
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
"""
u=u.rsplit("end;\n/",1)[0]+method+"end;\n/\n"
out[str(f/"002_unit_core.sql")]=u
r=old("rrl_stock_interware_rec")
r=r.replace(" procedure compile_command("," procedure assert_scope(p_plan varchar2,p_actor varchar2);\n procedure compile_command(",1)
r=r.replace("package body RRL_STOCK_INTERWARE_REC as","""package body RRL_STOCK_INTERWARE_REC as
 procedure assert_scope(p_plan varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=p_actor where p.OPERATION_ID=p_plan and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 and(u.WARE_ID=p.TARGET_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'INTERWARE_TARGET_RECEIVER_REQUIRED');end if;
 end;""")
r=r.replace("v_scan_uom varchar2(20);n number;","v_scan_uom varchar2(20);n number;manifest clob;source_units json_object_t;scan_domain json_object_t;scan_legs json_array_t;scan_leg json_object_t;unit_count number;")
r=r.replace("if n!=0 then raise_application_error(-20886,'INTERWARE_MARKED_UNIT_FLOW_REQUIRED');end if;","""manifest:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(plan.SOURCE_LOAD_OPERATION_ID,plan.ROOT_UID,plan.SOURCE_COMPOSITION_JSON);
 source_units:=json_object_t.parse(manifest);
 if source_units.get_number('physical_unit_count')>0 then
  select MANIFEST_JSON into manifest from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=v_plan;
  if dbms_lob.compare(manifest,source_units.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_FROZEN_UNIT_SOURCE_CHANGED');end if;
 end if;""")
needle="p_domain.put('unload_operation_id',v_unload);"
r=r.replace(needle,"""if source_units.get_number('physical_unit_count')>0 then
   scan_leg:=json_object_t();scan_leg.put('article',lot.ARTICUL);scan_leg.put('uid',plan.ROOT_UID);scan_leg.put('cell',source_units.get_string('source_cell'));scan_leg.put('base_uom',v_uom);scan_leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
   scan_legs:=json_array_t();scan_legs.append(scan_leg);scan_domain:=json_object_t();scan_domain.put('legs',scan_legs);
   if RRL_INTERWARE_MARK_SCAN.required_for_article(lot.ARTICUL)=1 then RRL_INTERWARE_MARK_SCAN.validate_scan(scan_domain.to_clob,m.to_clob,unit_count);end if;
  elsif m.has('unit_scans') and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'INTERWARE_UNEXPECTED_UNIT_SCANS');end if;
  """+needle)
r=r.replace("if v_kind='INTERWARE_UNLOAD' then","""if source_units.get_number('physical_unit_count')>0 then
  p_domain.put('source_units',source_units.get_array('units'));p_domain.put('source_cell',source_units.get_string('source_cell'));p_domain.put('original_unit_signature',source_units.get_string('unit_signature'));
 end if;
 if v_kind='INTERWARE_UNLOAD' then""",1)
r=r.replace("r json_array_t:=json_array_t();","r json_array_t:=json_array_t();units json_array_t;unit_value json_object_t;",1)
r=r.replace("p_policies:=f.to_clob;","""if v.has('source_units')then
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_UNIT_MANIFEST',v.get_string('plan_operation_id'));
  units:=v.get_array('source_units');
  for i in 0..units.get_size-1 loop unit_value:=treat(units.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',unit_value.get_string('key'));end loop;
 end if;
 p_policies:=f.to_clob;""")
r=r.replace("insert into RRL_INTERWARE_RECEIPT(OPERATION_ID","""if v.has('source_units')then
   RRL_STOCK_UNIT_CORE.receive_issued(v_uid,v.get_string('source_cell'),v_cell,v_qty,v.get_array('source_units').to_clob);
   j.put('physical_unit_count',v.get_array('source_units').get_size);j.put('original_unit_signature',v.get_string('original_unit_signature'));j.put('regulatory_ack_verified',false);
  end if;
  insert into RRL_INTERWARE_RECEIPT(OPERATION_ID""")
out[str(f/"003_receiving.sql")]=r
root=old("rrl_stock_posting_api")
needle="  if g_kind='LOAD_SHIPMENT'then"
root=root.replace(needle,"  if g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE')then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_INTERWARE_REC.assert_scope(doc.get_object('source').get_string('plan_operation_id'),p_actor);end;end if;\n"+needle)
out[str(f/"004_root.sql")]=root
out["wiki/database/nicora_ni061_marked_receive_design_20261011.md"]="# NI06.1: приёмка прежнего маркированного состава\n226 extends existing receipt/unit owner. Frozen225 source and original shipping fingerprint match current ISSUED units under ordered STOCK/UNIT locks; exact current SKU UNIT profile/code matrix required. Same units move to target receiving cell AVAILABLE/no HARD/version+1, birth/code identities retained. Existing +P/event/receipt/SAP outbox stay one native transaction; unload custody0. Current target scope before saved replay/after lock wait. No real government ACK; aggregation/nested loads remain separate scope. Recovery fresh captured owners before application, forward repair after committed marked receipt.\n"
print(json.dumps(out,ensure_ascii=True))
