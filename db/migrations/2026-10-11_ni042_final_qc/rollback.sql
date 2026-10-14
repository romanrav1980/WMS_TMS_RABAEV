declare n number;begin select count(*)into n from RRL_WH_FINAL_SCALE_USE;if n>0 then raise_application_error(-20863,'FINAL_QC_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_root.sql
@@000_before_qc.sql
@@000_before_gate.sql
@@000_before_archive.sql
drop trigger RRL_WH_FINAL_SCALE_USE_GUARD;
drop package RRL_WH_FINAL_SCALE_ADMISSION;
drop table RRL_WH_FINAL_SCALE_USE;
drop package RRL_OUTGOING_QC_ACCESS;
