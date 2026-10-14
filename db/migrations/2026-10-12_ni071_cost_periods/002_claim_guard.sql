create or replace trigger RRL_LOG_COST_CLAIM_GUARD before insert or update or delete on RRL_LOG_COST_SOURCE_CLAIM for each row
declare body clob;n number;quantity number;physical number;distinct_days number;currency_value varchar2(3);
begin
 if not inserting then raise_application_error(-20863,'COST_SOURCE_CLAIM_IMMUTABLE');end if;
 select r.RESULT_JSON,r.CURRENCY into body,currency_value from RRL_LOGISTICS_COST_RUN r
 join RRL_TT_HU_LOAD_FACT l on l.TT_ID=r.TT_ID and l.WARE_ID=r.WARE_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=l.LOAD_OPERATION_ID and op.STATE='APPLIED'
 where r.OPERATION_ID=:new.OPERATION_ID and l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and l.STATUS='DEPARTED';
 if currency_value!=:new.CURRENCY or :new.COST_CODE!='WAREHOUSE_PICKING'then raise_application_error(-20886,'COST_SOURCE_CLAIM_SCOPE_REQUIRED');end if;
 select count(*),sum(j.QTY),count(distinct j.RATE_DAY)into n,quantity,distinct_days
 from json_table(body,'$.lines[*]'columns(LOAD_ID varchar2(100)path '$.load_operation_id',QTY number path '$.quantity',RATE_DAY varchar2(10)path '$.rate_date',CODE varchar2(40)path '$.cost_code'))j
 where j.LOAD_ID=:new.LOAD_OPERATION_ID and j.CODE=:new.COST_CODE;
 select count(*)into physical from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
 if n=0 or n>200 or distinct_days!=n or quantity!=physical or physical=0 then raise_application_error(-20886,'COST_COMPLETE_SOURCE_PERIOD_PARTITION_REQUIRED');end if;
exception when no_data_found then raise_application_error(-20886,'COST_SOURCE_CLAIM_FACT_REQUIRED');
end;
/
