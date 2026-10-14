from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni062_marked_disposal")
s=(f/"000_before_rrl_stock_return_dispose.sql").read_text(encoding="utf-8").replace(" procedure compile_command"," procedure assert_scope(p_request varchar2,p_actor varchar2);\n procedure compile_command",1)
i=s.index(" procedure describe(")
scope=""" procedure assert_scope(p_request varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_RETURN_DISPOSAL_REQUEST q join RRL_STORE_RETURN_RECEIPT r on r.OPERATION_ID=q.RECEIPT_OPERATION_ID join RUSERS u on u.ID=p_actor
   where q.OPERATION_ID=p_request and q.ACTOR!=p_actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'store_return_approve')=1 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'RETURN_DISPOSAL_CURRENT_INDEPENDENT_ACTOR_REQUIRED');end if;
 end;
"""
s=s[:i]+scope+s[i:]
s=s.replace("n number;j json_object_t", "n number;actual number;total number;unit_wire clob;key_wire clob;profiles clob;leg json_object_t;legs json_array_t;scan_domain json_object_t;unit_count number;j json_object_t",1)
s=s.replace(" if n!=0 then raise_application_error(-20886,'RETURN_DISPOSAL_MARKED_REGULATORY_UNITS_REQUIRED');end if;", """ if n!=0 then
  select count(*),sum(case when SCAN_MODE='UNIT'and lengthb(SYSTEM_CODE)<=30 then 0 else 1 end),json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into n,actual,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=rec.ARTICLE;
  if n<1 or n>50 or actual!=0 then raise_application_error(-20886,'RETURN_DISPOSAL_CURRENT_UNIT_PROFILES_REQUIRED');end if;
  select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION,'origin_uid'value u.UID_PALLET,'unit_id'value u.UNIT_ID)order by u.PHYSICAL_UNIT_KEY returning clob),json_arrayagg(u.PHYSICAL_UNIT_KEY order by u.PHYSICAL_UNIT_KEY returning clob)
   into n,total,unit_wire,key_wire from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY
   where b.APPROVAL_OPERATION_ID=rec.APPROVAL_OPERATION_ID and u.CURRENT_UID=rec.UID_PALLET and u.CURRENT_CELL=v_cell and u.BASE_QTY=b.BASE_QTY and u.BASE_UOM=b.BASE_UOM and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null;
  select count(*)into actual from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=rec.UID_PALLET and CURRENT_CELL=v_cell;
  if n<1 or n>10000 or actual!=n or total!=rec.BASE_QTY then raise_application_error(-20886,'RETURN_DISPOSAL_EXACT_ORIGINAL_APPROVED_UNITS_REQUIRED');end if;
  leg:=json_object_t();leg.put('uid',rec.UID_PALLET);leg.put('article',rec.ARTICLE);leg.put('cell',v_cell);leg.put('base_uom',v_uom);leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));legs:=json_array_t();legs.append(leg);scan_domain:=json_object_t();scan_domain.put('legs',legs);
  RRL_STOCK_QC_MARK.validate_scan(scan_domain.to_clob,m.to_clob,unit_count);
  if unit_count!=n then raise_application_error(-20886,'RETURN_DISPOSAL_EXACT_SCANNED_UNIT_COUNT_REQUIRED');end if;
  j.put('disposal_units',json_array_t.parse(unit_wire));j.put('disposal_unit_keys',json_array_t.parse(key_wire));j.put('disposal_profiles',json_array_t.parse(profiles));
 elsif m.has('unit_scans')and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'RETURN_DISPOSAL_ORDINARY_UNEXPECTED_SCANS');end if;""",1)
s=s.replace(" RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'", """ if v.has('disposal_profiles')then
  declare wire clob:=v.get_array('disposal_profiles').to_clob;begin
   for x in(select distinct S from json_table(wire,'$[*]'columns(S varchar2(30)path '$.system_code')))loop
    RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','RETURN.DISPOSAL.GOV:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation||chr(0)||x.S,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
   end loop;
  end;
 end if;
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'""",1)
s=s.replace("v_event varchar2(100);\n begin", "v_event varchar2(100);keys clob;unit_wire clob;profile_wire clob;code_wire clob;gov json_object_t;gov_id number;gov_key varchar2(100);gov_ids json_array_t:=json_array_t();\n begin",1)
s=s.replace(" RRL_STOCK_EFFECT_CORE.consume(v_uid", " if v.has('disposal_unit_keys')then keys:=v.get_array('disposal_unit_keys').to_clob;end if;\n RRL_STOCK_EFFECT_CORE.consume(v_uid",1)
s=s.replace("p_disposal_receipt=>v_receipt);", "p_units=>keys,p_disposal_receipt=>v_receipt);",1)
needle=" payload:=json_object_t.parse(v.to_clob);"
queue=""" if v.has('disposal_profiles')then
  unit_wire:=v.get_array('disposal_units').to_clob;profile_wire:=v.get_array('disposal_profiles').to_clob;
  for target in(select distinct S from json_table(profile_wire,'$[*]'columns(S varchar2(30)path '$.system_code'))order by S)loop
   select json_arrayagg(json_object('physical_unit_key'value u.PHYSICAL_UNIT_KEY,'origin_uid'value u.UID_PALLET,'unit_id'value u.UNIT_ID,'code_hash'value c.CODE_HASH,'canonical_code'value c.CANONICAL_CODE,'profiles'value c.PROFILES_JSON format json)order by u.PHYSICAL_UNIT_KEY,c.CODE_HASH returning clob)into code_wire
    from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
    where c.SYSTEM_CODE=target.S and u.PHYSICAL_UNIT_KEY in(select K from json_table(unit_wire,'$[*]'columns(K varchar2(64)path '$.key')));
   gov:=json_object_t.parse(v.to_clob);gov.put('contract_version',1);gov.put('operation_id',op);gov.put('operation_type','DISPOSAL');gov.put('system_code',target.S);gov.put('codes',json_array_t.parse(code_wire));gov.put('physical_disposal_recorded',true);gov.put('external_ack_verified',false);
   gov_key:='RETURN.DISPOSAL.GOV:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op||chr(0)||target.S,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
   RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE',gov_key));
   gov_id:=RRL_TRACEABILITY_API.enqueue_event('MARKED_GOODS_DISPOSED','STOCK_OPERATION',op,gov_key,gov.to_clob,target.S,op);gov_ids.append(gov_id);
  end loop;
  j.put('physical_unit_count',v.get_array('disposal_units').get_size);j.put('regulatory_event_ids',gov_ids);j.put('regulatory_status','PENDING');j.put('external_regulatory_ack',false);
 end if;
"""
s=s.replace(needle,queue+needle,1);out[str(f/"001_disposal.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8");needle="  if g_kind='STORE_RETURN_PUTAWAY_PLAN'"
s=s.replace(needle,"  if g_kind='STORE_RETURN_DISPOSE'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_RETURN_DISPOSE.assert_scope(doc.get_object('source').get_string('request_operation_id'),p_actor);end;end if;\n"+needle);out[str(f/"002_root.sql")]=s
out[str(f/"003_recompile.sql")]="alter package RRL_STOCK_EFFECT_CORE compile body;\n/\nalter package RRL_STOCK_POSTING_API compile body;\n/\n"
out[str(f/"rollback.sql")]="@@000_before_rrl_stock_posting_api.sql\n@@000_before_rrl_stock_return_dispose.sql\n@@003_recompile.sql\n"
out["wiki/database/retailcase_ni062_marked_disposal_design_20261011.md"]="# NI06.2: физический акт и маркированные единицы возврата\n236 existing independent destruction owner/act/current whole blocked P/version preserved. Same original approved keys/current AVAILABLE/native QC all UNIT profiles/frozen unit versions; existing EffectCore consumes exact keys (no new writer). Same transaction stock event/immutable disposal/SAP/common outbox plus canonical per-system MARKED_GOODS_DISPOSED notifications via existing Traceability queue. Codes/birth identity retained; government circulation never marked completed by physical fact; adapter disabled preserves PENDING/no fake ACK. Native current independent actor/WARE before cached replay/after waits. Only bounded standalone full source supported.\n"
print(json.dumps(out,ensure_ascii=True))
