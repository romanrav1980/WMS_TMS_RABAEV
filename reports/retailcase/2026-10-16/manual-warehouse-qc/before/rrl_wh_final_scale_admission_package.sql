create or replace package RRL_WH_FINAL_SCALE_ADMISSION authid definer accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_QC_GATE,package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_READ,package RRL_STOCK_LOAD_BOX_CORE) as
 procedure assert_capture(p_request clob,p_domain clob);
 procedure claim_capture(p_request clob,p_domain clob,p_operation varchar2);
 function approved(p_domain clob,p_operation varchar2)return number;
 function preserve_case(p_task number)return number;
 function mass_json(p_task number)return clob;
end;
/
