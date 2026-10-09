-- Snapshot only planned keys in set SQL; outbox retains only changed unit/reservation rows.
create or replace package RRL_STOCK_CHANGE_AUDIT authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 function snapshot(p_resources clob) return clob;
 function differences(p_before clob,p_after clob) return clob;
end;
/

-- No COMMIT/ROLLBACK or remote I/O: transaction belongs to the application command runner.
create or replace package RRL_STOCK_POSTING_API authid definer as
 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);
 procedure execute_prepared(p_result out clob);
 procedure reset_connection;
end;
/
