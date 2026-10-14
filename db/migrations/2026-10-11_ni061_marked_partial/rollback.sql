declare n number;begin
 select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID where r.ORIGINAL_ROOT_UID is not null and json_exists(o.RESOLVED_PLAN_JSON,'$.domain.source_units[0]');
 if n>0 then raise_application_error(-20886,'INTERWARE_MARKED_PARTIAL_HISTORY_RETAINED');end if;
end;
/
@@../2026-10-11_ni061_partial_receiving/000_before_rrl_stock_unit_core_spec.sql
@@../2026-10-11_ni061_partial_receiving/000_before_rrl_stock_unit_core_body.sql
@@../2026-10-11_ni061_partial_receiving/002_partial_helper.sql
@@000_before_mark_scan.sql
@@../2026-10-11_ni061_partial_receiving/003_receiving_body.sql
@@../2026-10-11_ni061_partial_receiving/004_put_body.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
