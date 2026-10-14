create or replace trigger RRL_LOG_EXP_ALLOC_LINE_GUARD before insert or update or delete on RRL_LOGISTICS_EXP_ALLOC_LINE for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_ALLOCATION_SOURCE_IMMUTABLE');end if;
 select count(*)into n from RRL_LOGISTICS_EXP_ALLOCATION a join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=a.EXPENSE_OPERATION_ID
 join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and l.TT_ID=e.OBJECT_ID and l.WARE_ID=e.WARE_ID and l.STATUS='DEPARTED'
 join RRL_STOCK_OPERATION stock_op on stock_op.OPERATION_ID=l.LOAD_OPERATION_ID and stock_op.STATE='APPLIED'
 join json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',A varchar2(160)path '$.article',Q number path '$.quantity',B varchar2(20)path '$.base_uom'))leaf on leaf.K='STOCK'and leaf.U=:new.UID_PALLET and leaf.A=:new.ARTICLE and leaf.Q=:new.BASE_QTY and leaf.B=:new.BASE_UOM
 where a.OPERATION_ID=:new.OPERATION_ID and a.CURRENCY=:new.CURRENCY;
 if n!=1 then raise_application_error(-20886,'LOGISTICS_ALLOCATION_EXACT_LOAD_SOURCE_REQUIRED');end if;
 if :new.WEIGHT_SOURCE='MEASURED_CASE_NET'then
  select count(*)into n from RRL_TT_HU_LOAD_FACT l join RRL_TT_LOAD_BOX_WEIGHT b on b.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID and b.BOX_UID=:new.WEIGHT_BOX_UID
  join json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',CID number path '$.case_task_id',V number path '$.version',CAP varchar2(100)path '$.scale_qc.capture_key',QC varchar2(100)path '$.scale_qc.qc_operation_id',MV number path '$.scale_qc.measured_content_version',SIG number path '$.scale_qc.signature_version',NET number path '$.scale_qc.net_weight_kg',GROSS number path '$.scale_qc.gross_weight_kg',TARE number path '$.scale_qc.tare_weight_kg'))box on box.K='CASE'and box.U=b.BOX_UID and box.CID=b.CASE_BOX_TASK_ID and box.V=b.BOX_CONTENT_VERSION
  where l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and b.MEASUREMENT_ORIGIN='WAREHOUSE_SCALE_QC'and b.COVERAGE_COMPLETE=1
   and b.FINAL_SCALE_CAPTURE=box.CAP and b.WAREHOUSE_QC_OPERATION=box.QC and b.SIGNATURE_VERSION=box.SIG and b.MEASURED_CONTENT_VERSION=box.MV
   and b.NET_WEIGHT_KG=box.NET and b.GROSS_WEIGHT_KG=box.GROSS and b.TARE_WEIGHT_KG=box.TARE and box.NET=:new.WEIGHT_KG and :new.BASIS_VALUE=:new.WEIGHT_KG
   and(select count(*)from json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(K varchar2(20)path '$.kind',CID number path '$.case_task_id'))child where child.K='STOCK'and child.CID=b.CASE_BOX_TASK_ID)=1
   and exists(select 1 from json_table(l.COMPOSITION_JSON,'$.links[*]'columns(P varchar2(200)path '$.parent',C varchar2(200)path '$.child',M varchar2(40)path '$.membership'))membership where membership.P=b.BOX_UID and membership.C=:new.UID_PALLET and membership.M='CASE_CARRIER_LOT');
  if n!=1 then raise_application_error(-20886,'LOGISTICS_ALLOCATION_EXACT_CASE_NET_REQUIRED');end if;
 end if;

end;
/
