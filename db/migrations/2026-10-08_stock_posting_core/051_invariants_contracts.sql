create or replace package RRL_STOCK_UNIT_CORE authid definer
 accessible by(package RRL_STOCK_INVARIANT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_TRANSFER_CORE,
 package RRL_STOCK_EFFECT_CORE,package RRL_STOCK_RECEIPT_CORE) as
 procedure assert_composition(p_uid varchar2,p_cell varchar2);
 procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob);
 procedure release_units(p_id number,p_qty number,p_units clob,p_issue number default 0);
end;
/

create or replace package RRL_STOCK_INVARIANT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot_stock(p_resources clob) return clob;
 procedure verify_posting(p_resources clob,p_before clob,p_operation varchar2);
end;
/

-- Private compiler: derives all anchors from a typed command, never from caller-supplied lock lists.
create or replace package RRL_STOCK_COMMAND_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob);
end;
/

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/
