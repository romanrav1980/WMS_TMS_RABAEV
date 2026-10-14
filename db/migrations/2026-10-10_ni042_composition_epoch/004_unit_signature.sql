create or replace package RRL_STOCK_HU_UNIT_SIGNATURE authid definer as
 procedure describe_units(p_uid varchar2,p_cell varchar2,p_signature out varchar2,p_count out number);
 function signature_for(p_uid varchar2,p_cell varchar2) return varchar2;
end;
/
create or replace package body RRL_STOCK_HU_UNIT_SIGNATURE as
 procedure describe_units(p_uid varchar2,p_cell varchar2,p_signature out varchar2,p_count out number) is
  j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;n number:=0;
 begin
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY,BASE_UOM from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and (p_cell is null or CURRENT_CELL=p_cell) and STOCK_STATUS!='ISSUED' order by PHYSICAL_UNIT_KEY fetch first 10001 rows only) loop
   n:=n+1;if n>10000 then raise_application_error(-20881,'PLACEMENT_PHYSICAL_UNIT_BOUND_10000');end if;
   if u.PHYSICAL_UNIT_KEY is null or u.BASE_QTY is null or u.BASE_QTY<=0 or u.BASE_UOM is null then raise_application_error(-20884,'PHYSICAL_UNIT_SIGNATURE_DATA_REQUIRED');end if;
   x:=json_object_t();x.put('key',u.PHYSICAL_UNIT_KEY);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));x.put('base_uom',u.BASE_UOM);a.append(x);
  end loop;j.put('units',a);
  p_signature:=rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));p_count:=n;
 end;
 function signature_for(p_uid varchar2,p_cell varchar2) return varchar2 is s varchar2(64);n number;begin describe_units(p_uid,p_cell,s,n);return s;end;
end;
/
