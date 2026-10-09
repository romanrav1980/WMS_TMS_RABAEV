create or replace package RRL_STOCK_REVISION_ENTRY authid definer
 accessible by(package REVIZION) as
 function count_row(p_article varchar2,p_cell varchar2,p_quantity number,p_unit varchar2,p_row number,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2;
 function birth_legacy(p_facts clob,p_actor varchar2,p_operation varchar2) return varchar2;
end;
/

-- Existing initial inventory import creates a declared lot; ordinary receipt remains SAP-only.
create or replace package RRL_STOCK_INVENTORY_BIRTH authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
