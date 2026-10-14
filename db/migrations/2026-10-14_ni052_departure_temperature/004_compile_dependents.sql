begin
 execute immediate 'alter package RRL_STOCK_HU_LOAD_CORE compile body';
 execute immediate 'alter trigger RRL_LOAD_THERMAL_FACT_GUARD compile';
 execute immediate 'alter package RRL_STOCK_POSTING_API compile body';
end;
/
