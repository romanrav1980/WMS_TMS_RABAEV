declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_BALANCE_CORE authid definer
 accessible by(package RRL_STOCK_RECEIPT_REVERSE,package RRL_STOCK_INVENTORY_BIRTH,package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_EVENT_BRIDGE,package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,
  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null);
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number);
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null);
end;
/

create or replace package RRL_STOCK_PALLET_UOM authid definer
 accessible by(package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2);
end;
/

create or replace package body RRL_STOCK_BALANCE_CORE as
 procedure assert_context is v_tx varchar2(100);
 begin
  v_tx:=dbms_transaction.local_transaction_id(false);
  if v_tx is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=v_tx then
   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');
  end if;
 end;
 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,
   p_base_uom varchar2,p_uom_version number,p_expected_version number default null) is
  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_article varchar2(160);v_scale number;v_exists boolean:=true;
 begin
  assert_context;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  if p_cell is null or p_base_uom is null or p_delta_p is null or p_delta_h is null then
   raise_application_error(-20864,'STOCK_IDENTITY_OR_DELTA_MISSING');
  end if;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('SKU',v_article),4);
  begin
   select BASE_SCALE into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article
    and INPUT_UOM=p_base_uom and BASE_UOM=p_base_uom and POLICY_VERSION=p_uom_version
    and NUMERATOR=DENOMINATOR;
  exception when no_data_found then raise_application_error(-20865,'BASE_UOM_POLICY_REQUIRED');
  end;
  RRL_STOCK_MATH.assert_base(p_delta_p,v_scale);RRL_STOCK_MATH.assert_base(p_delta_h,v_scale);
  begin
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom
    from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell for update;
  exception when no_data_found then v_exists:=false;v_p:=0;v_h:=0;v_ver:=0;v_uom:=p_base_uom;
  end;
  if v_uom is null or v_uom!=p_base_uom then raise_application_error(-20866,'STOCK_BASE_UOM_CONFLICT'); end if;
  if p_expected_version is not null and p_expected_version!=v_ver then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
  RRL_STOCK_MATH.assert_base(v_p+p_delta_p,v_scale);RRL_STOCK_MATH.assert_base(v_h+p_delta_h,v_scale);
  if v_p+p_delta_p<0 then raise_application_error(-20868,'STOCK_INSUFFICIENT'); end if;
  if v_h+p_delta_h<0 or v_h+p_delta_h>v_p+p_delta_p then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;
  RRL_STOCK_CTX_API.begin_effect('STOCK',p_uid,p_cell);
  if v_exists then
   update RRL_REMAINS set REMAIN=REMAIN+p_delta_p,HARD_RESERVED_BASE=HARD_RESERVED_BASE+p_delta_h,
    STOCK_VERSION=STOCK_VERSION+1,TIME_OF_LAST_UPDATE=sysdate
    where UID_POLETA=p_uid and CELL=p_cell and STOCK_VERSION=v_ver;
   if sql%rowcount!=1 then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
  else
   insert into RRL_REMAINS(UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM,TIME_OF_LAST_UPDATE)
    values(p_uid,p_cell,p_delta_p,p_delta_h,1,p_base_uom,sysdate);
  end if;
  RRL_STOCK_CTX_API.end_effect;
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
 procedure write_event(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null) is
  v_prihod number;v_op varchar2(100);
 begin
  assert_context;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  if p_qty is null or p_qty=0 or p_base_uom is null or p_line is null or p_line<1 or p_leg is null or p_leg<1 then
   raise_application_error(-20870,'JOURNAL_FACT_INVALID');
  end if;
  v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
  select PRIHOD_NAKLAD_ID into v_prihod from RRL_PALLETS where UID_PALLET=p_uid;
  select RRL_EVENT_ID_SQ.nextval into p_event from dual;
  RRL_STOCK_CTX_API.begin_effect('JOURNAL',p_uid,nvl(p_from,p_to));
  insert into RRL_EVENTS(ID_EVENT,CELL_FROM,CELL_TO,DATE_EVENT,COUNT_EVENT,TYPE_EVENT,UID_POLETA,
   USER_ID,PRIHOD_NAKL_ID,OTHOD_NAKL_ID,PALLET_ROW_ID,OPERATION_ID,LINE_NO,LEG_NO,BASE_QTY,BASE_UOM,UOM_POLICY_VERSION)
   values(p_event,p_from,p_to,sysdate,abs(p_qty),p_type,p_uid,p_actor,v_prihod,p_outgoing_doc,p_pallet_row,v_op,p_line,p_leg,p_qty,p_base_uom,p_uom_version);
  RRL_STOCK_CTX_API.end_effect;
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number) is
 begin
  if p_from is null or p_to is null or p_from=p_to or p_qty is null or p_qty<=0 then raise_application_error(-20870,'MOVE_JOURNAL_CONTRACT');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_from),4);
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_to),4);
  write_event(p_uid,p_from,p_to,p_qty,p_base_uom,p_uom_version,p_line,1,2,p_actor,p_event);
 end;
 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,
   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null) is
 begin
  if p_signed_qty is null or p_signed_qty=0 or
   (p_signed_qty<0 and (p_from is null or p_to is not null)) or
   (p_signed_qty>0 and (p_to is null or p_from is not null)) then
   raise_application_error(-20870,'SIGNED_LEG_LOCATION_CONFLICT');
  end if;
  write_event(p_uid,p_from,p_to,p_signed_qty,p_base_uom,p_uom_version,p_line,p_leg,p_type,p_actor,p_event,p_outgoing_doc,p_pallet_row);
 end;
end;
/

create or replace package body RRL_STOCK_PALLET_UOM as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2) is
  p RRL_PALLETS%rowtype;v_input varchar2(20);v_stock_base varchar2(20);
  v_num number;v_den number;v_scale number;v_pack number;v_input_version number;v_provenance varchar2(1000);
  v json_object_t:=json_object_t();
 begin
  select * into p from RRL_PALLETS where UID_PALLET=p_uid;
  select min(BASE_UOM),max(BASE_UOM) into v_stock_base,p_base from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
  if v_stock_base is null then
   select min(BASE_UOM),max(BASE_UOM) into v_stock_base,p_base from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
  end if;
  if v_stock_base is null or p_base!=v_stock_base then raise_application_error(-20887,'PALLET_BASE_UOM_AMBIGUOUS');end if;
  v_input:=nvl(p_input,p_base);
  select max(POLICY_VERSION) into p_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=v_input;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE into p_base,v_num,v_den,v_scale,v_provenance
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=v_input and POLICY_VERSION=p_version;
  if p_base!=v_stock_base then raise_application_error(-20887,'PALLET_BASE_UOM_CONFLICT');end if;
  -- BOX arithmetic follows the actual pallet pack, never a rounded legacy box count.
  if upper(v_input) in ('BOX','CAR','CS','KAR','KOR','КОР') then
   if upper(p_base) not in ('EA','PCS','ST','ШТ') then
    raise_application_error(-20887,'PALLET_BOX_REQUIRES_EXACT_BASE_ALLOCATION');
   end if;
   if nvl(p.MOD_ID,0)!=0 then
    select SHT_IN_KOR into v_pack from RRL_ARTICUL_MODS where ID=p.MOD_ID and ARTICUL=p.ARTICUL;
    v_provenance:='PALLET.MOD_ID';
   else
    select COUNT_SHT_IN_KOR into v_pack from RRL_ARTICULS where ACTICUL=p.ARTICUL;
    v_provenance:='ARTICLE.DEFAULT_PACK';
   end if;
   if v_pack is null or v_pack<1 or v_pack!=trunc(v_pack) or v_pack>1000000000 then
    raise_application_error(-20887,'PALLET_PACK_FACTOR_INVALID');
   end if;
   v_num:=v_pack;v_den:=1;
  end if;
  p_quantity_base:=RRL_STOCK_MATH.convert_exact(p_quantity,v_num,v_den,v_scale);
  v_input_version:=p_version;
  select max(POLICY_VERSION) into p_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=p_base and BASE_UOM=p_base and NUMERATOR=1 and DENOMINATOR=1;
  if p_version is null then raise_application_error(-20868,'PALLET_BASE_POLICY_REQUIRED');end if;
  v.put('uid',p_uid);v.put('article',p.ARTICUL);v.put('mod_id',p.MOD_ID);
  v.put('input',v_input);v.put('base',p_base);v.put('version',v_input_version);v.put('base_version',p_version);
  v.put('numerator',v_num);v.put('denominator',v_den);v.put('scale',v_scale);v.put('provenance',v_provenance);
  p_signature:=rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
end;
/
