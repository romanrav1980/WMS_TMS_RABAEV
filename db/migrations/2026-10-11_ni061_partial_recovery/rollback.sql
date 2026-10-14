declare n number;begin
 select count(*)into n from(select LOSS_OPERATION_ID from RRL_INTERWARE_RECOVERY_REQUEST group by LOSS_OPERATION_ID having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_PARTIAL_RECOVERY_REQUESTS_PREVENT_SINGLE_LOSS_ROLLBACK');end if;
 select count(*)into n from(select LOSS_OPERATION_ID from RRL_INTERWARE_RECOVERY_RECEIPT group by LOSS_OPERATION_ID having count(*)>1);
 if n>0 then raise_application_error(-20878,'RETAINED_PARTIAL_RECOVERY_RECEIPTS_PREVENT_SINGLE_LOSS_ROLLBACK');end if;
end;
/
@@000_before_rrl_stock_iw_recovery_plan_package_body.sql
@@000_before_rrl_stock_iw_recovery_rec_package_body.sql
alter table RRL_INTERWARE_RECOVERY_REQUEST add constraint RRL_IW_REC_REQ_SINGLE_LOSS unique(LOSS_OPERATION_ID);
alter table RRL_INTERWARE_RECOVERY_RECEIPT add constraint RRL_IW_REC_REC_SINGLE_LOSS unique(LOSS_OPERATION_ID);
@@../2026-10-08_stock_posting_core/014b_recompile.sql
