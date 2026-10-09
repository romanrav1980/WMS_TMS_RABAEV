create or replace package RRL_STOCK_UOM_CONFIG authid definer as
 procedure publish(p_article varchar2,p_input varchar2,p_base varchar2,p_numerator number,p_denominator number,p_scale number,p_provenance varchar2);
end;
/
create or replace package body RRL_STOCK_UOM_CONFIG as
 procedure require_configuration is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG' or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
   raise_application_error(-20863,'CONFIGURATION_CONTEXT_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 end;
 procedure publish(p_article varchar2,p_input varchar2,p_base varchar2,p_numerator number,p_denominator number,p_scale number,p_provenance varchar2) is
  n number;v_version number;v_key raw(1000);v_id number;v_old RRL_STOCK_UOM_CONVERSION%rowtype;
 begin
  require_configuration;
  if p_article is null or p_input is null or p_base is null or p_provenance is null or length(p_input)>20 or length(p_base)>20 then raise_application_error(-20833,'UOM_POLICY_IDENTITY_INVALID');end if;
  select count(*) into n from RRL_ARTICULS where ACTICUL=p_article;
  if n!=1 then raise_application_error(-20887,'ARTICLE_IDENTITY_AMBIGUOUS');end if;
  RRL_STOCK_MATH.assert_base(0,p_scale);
  if p_numerator is null or p_denominator is null or p_numerator<1 or p_denominator<1 or p_numerator>1000000000 or p_denominator>1000000000 or
   p_numerator!=trunc(p_numerator) or p_denominator!=trunc(p_denominator) then raise_application_error(-20833,'UOM_FACTOR_INVALID');end if;
  if p_input=p_base and (p_numerator!=1 or p_denominator!=1) then raise_application_error(-20833,'BASE_UOM_IDENTITY_REQUIRED');end if;
  select count(*) into n from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and BASE_UOM!=p_base;
  if n>0 then raise_application_error(-20866,'BASE_CHANGE_REQUIRES_EXPLICIT_CONVERSION');end if;
  select count(*) into n from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and BASE_SCALE!=p_scale;
  if n>0 then raise_application_error(-20866,'BASE_PRECISION_CHANGE_REQUIRES_EXPLICIT_CONVERSION');end if;
  select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=p_input;
  if v_version is not null then
   select * into v_old from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=p_input and POLICY_VERSION=v_version;
   if v_old.NUMERATOR=p_numerator and v_old.DENOMINATOR=p_denominator and v_old.BASE_SCALE=p_scale then return;end if;
  end if;
  -- Global configuration X fence serializes publication; posting never creates policy identities.
  v_key:=RRL_STOCK_LOCK_API.resource_key('SKU',p_article);
  select count(*) into n from RRL_STOCK_POLICY_GUARD where POLICY_KEY=v_key;
  if n=0 then
   select nvl(max(LOCK_ID),900000000)+1 into v_id from RRL_STOCK_POLICY_GUARD;
   if v_id>949999999 then raise_application_error(-20808,'POLICY_ID_RANGE_EXHAUSTED');end if;
   insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID,POLICY_VERSION) values(v_key,v_id,1);
  end if;
  insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)
   values(p_article,p_input,p_base,nvl(v_version,0)+1,p_numerator,p_denominator,p_scale,p_provenance);
  update RRL_STOCK_POLICY_GUARD set POLICY_VERSION=POLICY_VERSION+1 where POLICY_KEY=v_key;
 end;
end;
/
