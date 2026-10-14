create or replace package RRL_STOCK_TARE_POLICY authid definer accessible by(package RRL_STOCK_TARE_CMD) as
 procedure describe_store(p_store varchar2,p_domain out json_object_t);
 procedure record_delivery(p_operation varchar2,p_domain json_object_t);
end;
/

create or replace package body RRL_STOCK_TARE_POLICY as
 procedure describe_store(p_store varchar2,p_domain out json_object_t) is
 policy RRL_TARE_RETURN_POLICY%rowtype;v_customer number;v_key varchar2(255);n number;
 begin
 select count(*) into n from RRL_TARE_RETURN_POLICY where SCOPE_KIND='STORE' and SCOPE_KEY=p_store;
 if n=1 then select * into policy from RRL_TARE_RETURN_POLICY where SCOPE_KIND='STORE' and SCOPE_KEY=p_store;
 else
  select count(distinct CUSTOMER_ID),min(CUSTOMER_ID) into n,v_customer from RRL_CUSTOMER_STORE_MAP where LEGACY_ADDR=p_store and ACTIVE=1;
  if n!=1 then raise_application_error(-20886,'TARE_EXPLICIT_STORE_POLICY_OR_SINGLE_CUSTOMER_REQUIRED');end if;
  v_key:=RRL_STOCK_PLAN_HELPER.decimal_text(v_customer);
  select * into policy from RRL_TARE_RETURN_POLICY where SCOPE_KIND='CUSTOMER' and SCOPE_KEY=v_key;
 end if;
 p_domain:=json_object_t();p_domain.put('scope_kind',policy.SCOPE_KIND);p_domain.put('scope_key',policy.SCOPE_KEY);p_domain.put('policy_version',policy.POLICY_VERSION);p_domain.put('return_mode',policy.RETURN_MODE);p_domain.put('return_days',policy.RETURN_DAYS);p_domain.put('timezone_region',policy.TIMEZONE_REGION);
 exception when no_data_found then raise_application_error(-20886,'TARE_RETURN_POLICY_REQUIRED');end;
 procedure record_delivery(p_operation varchar2,p_domain json_object_t) is
 v_scope varchar2(10):=p_domain.get_string('scope_kind');v_key varchar2(255):=p_domain.get_string('scope_key');v_version number:=p_domain.get_number('policy_version');
 v_mode varchar2(16):=p_domain.get_string('return_mode');v_days number:=p_domain.get_number('return_days');v_tz varchar2(64):=p_domain.get_string('timezone_region');
 v_accepted timestamp with time zone;v_due timestamp with time zone;v_day date;
 begin
 select ACCEPTED_AT into v_accepted from RRL_TARE_ACCEPT where OPERATION_ID=p_operation;
 if v_mode!='NEXT_DELIVERY' then
  select trunc(cast(v_accepted at time zone (v_tz) as date)) into v_day from dual;
  v_due:=from_tz(cast(v_day+1+case when v_mode='DAYS' then v_days else 0 end as timestamp),v_tz);
 end if;
 insert into RRL_TARE_DELIVERY_POLICY(ACCEPT_OPERATION_ID,SCOPE_KIND,SCOPE_KEY,POLICY_VERSION,RETURN_MODE,RETURN_DAYS,TIMEZONE_REGION,DUE_AT)
 values(p_operation,v_scope,v_key,v_version,v_mode,v_days,v_tz,v_due);
 end;
end;
/
