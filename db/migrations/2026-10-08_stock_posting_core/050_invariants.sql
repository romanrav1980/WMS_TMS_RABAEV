create or replace package RRL_STOCK_INVARIANT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot_stock(p_resources clob) return clob;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2);
end;
/
create or replace package body RRL_STOCK_INVARIANT_CORE as
 function stock_uid(p_key raw) return varchar2 is
  v_pos pls_integer:=1;v_len pls_integer;v_end pls_integer;v_hex varchar2(2000):=rawtohex(p_key);
  v_version varchar2(10);v_kind varchar2(20);v_uid varchar2(200);
  function next_part return varchar2 is v_out varchar2(2000);
  begin
   v_end:=instr(v_hex,'3A',v_pos);
   -- RAW bytes are traversed, so UTF-8 component lengths remain byte lengths.
   while v_end>0 and mod(v_end,2)=0 loop v_end:=instr(v_hex,'3A',v_end+1);end loop;
   if v_end=0 then raise_application_error(-20841,'RESOURCE_ENCODING_INVALID');end if;
   v_len:=to_number(utl_i18n.raw_to_char(hextoraw(substr(v_hex,v_pos,v_end-v_pos)),'AL32UTF8'));
   v_pos:=v_end+2;
   v_out:=utl_i18n.raw_to_char(hextoraw(substr(v_hex,v_pos,2*v_len)),'AL32UTF8');v_pos:=v_pos+2*v_len;
   return v_out;
  end;
 begin
  v_version:=next_part;v_kind:=next_part;v_uid:=next_part;
  if v_version!='2' or v_kind!='STOCK' or v_uid is null or v_pos!=length(v_hex)+1
   or RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid)!=p_key then raise_application_error(-20841,'STOCK_RESOURCE_ENCODING_INVALID');end if;
  return v_uid;
 end;
 function snapshot_stock(p_resources clob) return clob is
  v json_array_t:=json_array_t();u json_object_t;x json_array_t;k json_object_t;v_uid varchar2(200);v_count number:=0;
 begin
  for r in(select distinct KEY_HEX from json_table(p_resources,'$[*]'
   columns(RANK_NO number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex')) where RANK_NO=50 order by KEY_HEX) loop
   v_uid:=stock_uid(hextoraw(r.KEY_HEX));
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   u:=json_object_t();x:=json_array_t();u.put('uid',v_uid);
   for b in(select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM from RRL_REMAINS where UID_POLETA=v_uid order by CELL) loop
    v_count:=v_count+1;if v_count>20000 then raise_application_error(-20871,'STOCK_CLOSURE_TOO_LARGE');end if;
    k:=json_object_t();k.put('cell',b.CELL);k.put('p',RRL_STOCK_PLAN_HELPER.decimal_text(b.REMAIN));
    k.put('h',RRL_STOCK_PLAN_HELPER.decimal_text(b.HARD_RESERVED_BASE));k.put('version',b.STOCK_VERSION);k.put('base_uom',b.BASE_UOM);x.append(k);
   end loop;
   u.put('balances',x);v.append(u);
  end loop;
  return v.to_clob;
 end;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2) is
  v_uid varchar2(200);v_p number;v_h number;v_old number;v_delta number;v_sum number;v_bad number;v_base varchar2(20);v_unit_count number;
 begin
  if p_operation is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation then
   raise_application_error(-20863,'INVARIANT_CONTEXT_REQUIRED');end if;
  for r in(select distinct KEY_HEX from json_table(p_resources,'$[*]'
   columns(RANK_NO number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex')) where RANK_NO=50) loop
   v_uid:=stock_uid(hextoraw(r.KEY_HEX));
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   for c in(
    select CELL from RRL_REMAINS where UID_POLETA=v_uid
    union select j.CELL from json_table(p_before,'$[*]' columns(STOCK_UID_JSON varchar2(200) path '$.uid',
      nested path '$.balances[*]' columns(CELL varchar2(60) path '$.cell')))j where j.STOCK_UID_JSON=v_uid and j.CELL is not null
    union select nvl(CELL_FROM,CELL_TO) from RRL_EVENTS where OPERATION_ID=p_operation and UID_POLETA=v_uid
   ) loop
    v_p:=0;v_h:=0;v_base:=null;
    begin select REMAIN,HARD_RESERVED_BASE,BASE_UOM into v_p,v_h,v_base from RRL_REMAINS where UID_POLETA=v_uid and CELL=c.CELL;
    exception when no_data_found then null;end;
    select nvl(sum(to_number(j.QTY,'999999999999999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''')),0) into v_old
     from json_table(p_before,'$[*]' columns(STOCK_UID_JSON varchar2(200) path '$.uid',
      nested path '$.balances[*]' columns(CELL varchar2(60) path '$.cell',QTY varchar2(100) path '$.p')))j
      where j.STOCK_UID_JSON=v_uid and j.CELL=c.CELL;
    select nvl(sum(case when CELL_FROM is not null and CELL_TO is not null then
      case when CELL_FROM=c.CELL then -BASE_QTY else BASE_QTY end else BASE_QTY end),0) into v_delta
     from RRL_EVENTS where OPERATION_ID=p_operation and UID_POLETA=v_uid and (CELL_FROM=c.CELL or CELL_TO=c.CELL);
    if v_p-v_old!=v_delta or v_p<0 or v_h<0 or v_h>v_p then raise_application_error(-20868,'JOURNAL_BALANCE_INVARIANT_FAILED');end if;
    select nvl(sum(BASE_QTY),0),nvl(sum(case when BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!=v_base then 1 else 0 end),0)
      into v_sum,v_bad from RRL_STOCK_RESERVATION where UID_PALLET=v_uid and CELL=c.CELL
      and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
    if v_sum!=v_h or v_bad>0 then raise_application_error(-20869,'RESERVATION_BALANCE_INVARIANT_FAILED');end if;
    RRL_STOCK_UNIT_CORE.assert_composition(v_uid,c.CELL);
    select count(*) into v_unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=v_uid and CURRENT_CELL=c.CELL and STOCK_STATUS!='ISSUED';
    for z in(select RESERVATION_ID,BASE_QTY from RRL_STOCK_RESERVATION where UID_PALLET=v_uid and CELL=c.CELL
     and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')) loop
     select count(*),nvl(sum(BASE_QTY),0) into v_bad,v_sum from RRL_WMS_RECEIPT_UNIT
      where CURRENT_UID=v_uid and CURRENT_CELL=c.CELL and HARD_RESERVATION_ID=z.RESERVATION_ID and STOCK_STATUS!='ISSUED';
     if v_unit_count>0 and v_sum!=z.BASE_QTY then raise_application_error(-20869,'RESERVATION_UNIT_INVARIANT_FAILED');end if;
    end loop;
   end loop;
  end loop;
  -- Every journal leg belongs to a planned stock key.
  for e in(select distinct UID_POLETA from RRL_EVENTS where OPERATION_ID=p_operation) loop
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',e.UID_POLETA));
  end loop;
 end;
end;
/
