create or replace package RRL_IW_GROUP_THERMAL authid definer as
 procedure assert_cell(p_ware number,p_article varchar2,p_cell varchar2);
end;
/
create or replace package body RRL_IW_GROUP_THERMAL as
 procedure assert_cell(p_ware number,p_article varchar2,p_cell varchar2)is
 lo number;hi number;j json_object_t:=json_object_t();wire clob;
 begin
 begin select TEMP_MIN,TEMP_MAX into lo,hi from RRL_RECEIPT_SKU_RULE where WARE_ID=p_ware and ARTICUL=p_article;
 exception when no_data_found then lo:=null;hi:=null;end;
 if(lo is null and hi is not null)or(lo is not null and hi is null)or lo>hi then raise_application_error(-20886,'INTERWARE_GROUP_SKU_TEMPERATURE_RANGE_INVALID');end if;
 j.put('task_temp_min',lo);j.put('task_temp_max',hi);wire:=j.to_clob;
 RRL_INTERWARE_THERMAL.assert_cell(wire,p_ware,p_cell);
 end;
end;
/
