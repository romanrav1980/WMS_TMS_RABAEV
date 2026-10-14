create or replace package RRL_STOCK_QC_POLICY authid definer as
 procedure settings(p_warehouse number,p_mode out varchar2,p_independent out number);
 procedure settings_for_plan(p_domain clob,p_mode out varchar2,p_independent out number);
 function controller_allowed(p_domain clob,p_actor varchar2) return number;
 procedure assert_controller(p_domain clob,p_actor varchar2);
 procedure sampling(p_domain clob,p_bucket out number,p_percent out number,p_selected out number,p_rescan out number);
 function full_scan_required(p_domain clob) return number;
 procedure assign_sampling(p_domain clob);
end;

/
