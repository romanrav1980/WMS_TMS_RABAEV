create or replace package RRL_STOCK_PALLET_UOM authid definer
 accessible by(package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2);
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
   if p.STOCK_PACK_FROZEN=1 then
    if p.STOCK_PACK_BASE_UOM!=p_base then raise_application_error(-20887,'PALLET_PACK_BASE_CONFLICT');end if;
    v_pack:=p.STOCK_BOX_FACTOR;v_provenance:='PALLET.FROZEN_PACK';
   else
    -- A lot already in stock must never silently adopt a later article factor.
    select count(*) into v_pack from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
    if v_pack>0 then raise_application_error(-20887,'PALLET_PACK_SNAPSHOT_REQUIRED');end if;
    if nvl(p.MOD_ID,0)!=0 then
     select SHT_IN_KOR into v_pack from RRL_ARTICUL_MODS where ID=p.MOD_ID and ARTICUL=p.ARTICUL;
     v_provenance:='PALLET.MOD_ID';
    else
     select COUNT_SHT_IN_KOR into v_pack from RRL_ARTICULS where ACTICUL=p.ARTICUL;
     v_provenance:='ARTICLE.DEFAULT_PACK_BEFORE_ADMISSION';
    end if;
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
