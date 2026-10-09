create or replace package RRL_STOCK_MATH authid definer as
 function quantity(p_text varchar2,p_scale number default 9) return number;
 function convert_exact(p_text varchar2,p_numerator number,p_denominator number,p_scale number) return number;
 procedure assert_base(p_value number,p_scale number);
end;
/
create or replace package body RRL_STOCK_MATH as
 procedure assert_base(p_value number,p_scale number) is
 begin
  if p_value is null or p_scale is null or p_scale!=trunc(p_scale) or p_scale<0 or p_scale>9
     or abs(p_value)>=power(10,18) or trunc(p_value,p_scale)!=p_value then
   raise_application_error(-20830,'QUANTITY_PRECISION: exact bounded base quantity required');
  end if;
 end;
 function quantity(p_text varchar2,p_scale number default 9) return number is v number;
 begin
  if p_text is null or length(p_text)>28 or not regexp_like(p_text,'^[0-9]{1,18}([.][0-9]{1,9})?$','c') then
   raise_application_error(-20831,'QUANTITY_FORMAT: canonical decimal required');
  end if;
  v:=to_number(p_text,'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');
  assert_base(v,p_scale);
  if v<=0 then raise_application_error(-20832,'QUANTITY_POSITIVE: positive quantity required'); end if;
  return v;
 end;
 function convert_exact(p_text varchar2,p_numerator number,p_denominator number,p_scale number) return number is
  v number; v_a number; v_n number; v_d number; v_i number;
 begin
  v:=quantity(p_text);
  if p_numerator is null or p_denominator is null or p_numerator!=trunc(p_numerator)
   or p_denominator!=trunc(p_denominator) or p_numerator<1 or p_numerator>1000000000
   or p_denominator<1 or p_denominator>1000000000 then raise_application_error(-20833,'UOM_FACTOR_INVALID'); end if;
  assert_base(0,p_scale);
  v_a:=case when instr(p_text,'.')=0 then 0 else length(p_text)-instr(p_text,'.') end;
  v_i:=v*power(10,v_a);
  v_n:=v_i*p_numerator*power(10,greatest(p_scale-v_a,0));
  v_d:=p_denominator*power(10,greatest(v_a-p_scale,0));
  if mod(v_n,v_d)!=0 then raise_application_error(-20834,'UOM_ROUNDING_FORBIDDEN'); end if;
  v:=(v_n/v_d)/power(10,p_scale);
  assert_base(v,p_scale);
  return v;
 end;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-015-stock-exact-arithmetic' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Exact bounded stock arithmetic without rounding',sysdate,user,'015_math.sql','015_rollback.sql','APPLIED');
commit;
