create or replace trigger RRL_LOG_COST_LINE_GUARD before insert or update or delete on RRL_LOGISTICS_COST_LINE for each row
declare n number;ware number;run_body clob;archive_body clob;loaded_day date;policy_mode varchar2(20);policy_zone varchar2(64);latest_version number;expected_day date;rate_key varchar2(64);rate_version number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_COST_LINE_IMMUTABLE');end if;
 select r.WARE_ID,r.RESULT_JSON,l.COMPOSITION_JSON,trunc(cast(sys_extract_utc(l.LOADED_AT)as date))
 into ware,run_body,archive_body,loaded_day
 from RRL_LOGISTICS_COST_RUN r join RRL_TT_HU_LOAD_FACT l on l.TT_ID=r.TT_ID and l.WARE_ID=r.WARE_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=l.LOAD_OPERATION_ID and op.STATE='APPLIED'
 where r.OPERATION_ID=:new.OPERATION_ID and l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and l.STATUS='DEPARTED'and r.CURRENCY=:new.CURRENCY;
 if :new.RATE_DATE is null or :new.RATE_DATE!=trunc(:new.RATE_DATE)or :new.PERIOD_POLICY_VERSION is null then raise_application_error(-20886,'COST_EXPLICIT_FINANCIAL_PERIOD_REQUIRED');end if;
 select VERSION_NO into latest_version from RRL_LOG_COST_PERIOD_HEAD where WARE_ID=ware;
 if latest_version!=:new.PERIOD_POLICY_VERSION then raise_application_error(-20886,'COST_CURRENT_PERIOD_POLICY_REQUIRED');end if;
 if latest_version=0 then policy_mode:='LOADED_UTC';policy_zone:=null;
 else select PERIOD_MODE,TIME_ZONE into policy_mode,policy_zone from RRL_LOG_COST_PERIOD_HISTORY where WARE_ID=ware and VERSION_NO=latest_version;end if;
 if :new.PERIOD_MODE!=policy_mode or :new.PERIOD_MODE is null or nvl(:new.PERIOD_TIME_ZONE,'~')!=nvl(policy_zone,'~')then raise_application_error(-20886,'COST_PERIOD_POLICY_PROOF_REQUIRED');end if;
 if :new.PERIOD_KEY!=to_char(:new.RATE_DATE,'YYYY-MM-DD')then raise_application_error(-20886,'COST_EXPLICIT_PERIOD_KEY_REQUIRED');end if;
 select count(*)into n from RRL_LOG_COST_SOURCE_CLAIM where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID
 and COST_CODE=:new.COST_CODE and CURRENCY=:new.CURRENCY and OPERATION_ID=:new.OPERATION_ID;
 if n!=1 then raise_application_error(-20886,'COST_SINGLE_SOURCE_CLAIM_REQUIRED');end if;
 if policy_mode='LOADED_UTC'then
  expected_day:=loaded_day;
  select count(*)into n from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
 else
  select count(*)into n
  from RRL_TT_LOAD_BOX_WEIGHT b join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=b.CASE_BOX_TASK_ID
  and t.WARE_ID=ware and t.STARTED_AT_INSTANT is not null
  join json_table(archive_body,'$.nodes[*]'columns(UID_VALUE varchar2(160)path '$.uid',KIND_VALUE varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))j
  on j.UID_VALUE=b.BOX_UID and j.KIND_VALUE='CASE'and j.CASE_ID=t.CASE_PICK_TASK_ID
  where b.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
  select count(*)into latest_version from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
  if n!=latest_version then raise_application_error(-20886,'COST_EACH_CASE_ACTUAL_START_REQUIRED');end if;
  select count(*)into n from RRL_TT_LOAD_BOX_WEIGHT b join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=b.CASE_BOX_TASK_ID
  and t.WARE_ID=ware and t.STARTED_AT_INSTANT is not null
  where b.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID
  and trunc(cast(t.STARTED_AT_INSTANT at time zone(policy_zone)as timestamp))=:new.RATE_DATE;
  expected_day:=case when n>0 then :new.RATE_DATE else null end;
 end if;
 if n!=:new.QUANTITY then raise_application_error(-20886,'COST_PERIOD_PHYSICAL_BOX_COUNT_REQUIRED');end if;
 select VERSION_NO into latest_version from RRL_LOG_COST_PERIOD_HEAD where WARE_ID=ware;
 if :new.RATE_DATE!=expected_day or expected_day is null then raise_application_error(-20886,'COST_ACTUAL_PERIOD_DATE_REQUIRED');end if;
 select count(*)into n from json_table(run_body,'$.lines[*]'columns(
 LOAD_ID varchar2(100)path '$.load_operation_id',RATE_DAY varchar2(10)path '$.rate_date',PERIOD_KIND_VALUE varchar2(20)path '$.period_mode',
 ZONE_TEXT varchar2(64)path '$.period_timezone',POLICY_VERSION number path '$.period_policy_version',QTY number path '$.quantity',RATE_KEY_VALUE varchar2(64)path '$.rate_key',RATE_VERSION number path '$.version',RATE_NUMBER number path '$.rate',AMOUNT_NUMBER number path '$.amount'))j
 where j.LOAD_ID=:new.LOAD_OPERATION_ID and j.RATE_DAY=to_char(expected_day,'YYYY-MM-DD')and j.PERIOD_KIND_VALUE=policy_mode
 and nvl(j.ZONE_TEXT,'~')=nvl(policy_zone,'~')and j.POLICY_VERSION=latest_version and j.QTY=:new.QUANTITY and j.RATE_KEY_VALUE=:new.RATE_KEY and j.RATE_VERSION=:new.VERSION_NO and j.RATE_NUMBER=:new.RATE_VALUE and j.AMOUNT_NUMBER=:new.AMOUNT;
 if n!=1 then raise_application_error(-20886,'COST_FROZEN_PERIOD_RESULT_REQUIRED');end if;
 select h.RATE_KEY,h.VERSION_NO into rate_key,rate_version from RRL_LOGISTICS_RATE_HISTORY h join RRL_LOGISTICS_RATE_HEAD rh on rh.RATE_KEY=h.RATE_KEY
 where rh.WARE_ID=ware and rh.CURRENCY=:new.CURRENCY and rh.COST_CODE=:new.COST_CODE
 and h.EFFECTIVE_FROM<=expected_day order by h.EFFECTIVE_FROM desc,h.VERSION_NO desc fetch first 1 row only;
 select count(*)into n from RRL_LOGISTICS_RATE_HISTORY h where h.RATE_KEY=:new.RATE_KEY and h.VERSION_NO=:new.VERSION_NO
 and h.RATE_KEY=rate_key and h.VERSION_NO=rate_version and h.RATE_VALUE=:new.RATE_VALUE and h.BASIS=:new.BASIS
;
 if n!=1 then raise_application_error(-20886,'LOGISTICS_COST_ACTUAL_SOURCE_RATE_REQUIRED');end if;
exception when no_data_found then raise_application_error(-20886,'COST_FINANCIAL_SOURCE_PROOF_MISSING');
end;


/
