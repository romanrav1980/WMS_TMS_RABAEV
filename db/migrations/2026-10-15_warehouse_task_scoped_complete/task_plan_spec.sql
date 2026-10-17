create or replace package RRL_STOCK_TASK_PLAN authid definer
 accessible by(package RRL_STOCK_HU_TASK,package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_CORE, PACKAGE RRL_WAREHOUSE_TASK_ACCESS) as
 procedure compile_task(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 function signature(p_task RRL_WAREHOUSE_TASK%rowtype) return varchar2;
end;
/
