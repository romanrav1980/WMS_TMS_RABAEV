create or replace package RRL_STOCK_HU_READ authid definer as
 function snapshot_json(p_uid varchar2,p_ignore_task number default null) return clob;
 function case_snapshot_json(p_task number) return clob;
 procedure assert_quantity_write(p_uid varchar2);
end;
/
