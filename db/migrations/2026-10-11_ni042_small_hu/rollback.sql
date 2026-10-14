declare n number;begin select count(*)into n from RRL_WH_FINAL_SCALE_USE where SIGNATURE_VERSION=3;if n>0 then raise_application_error(-20863,'SMALL_CASE_V3_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_hu.sql
@@000_before_gate.sql
@@000_before_admission.sql
@@000_before_qc.sql
@@000_before_archive.sql
@@000_before_use_guard.sql
alter table RRL_WH_FINAL_SCALE_USE drop constraint RRL_WH_FINAL_USE_VERSION_C;
alter table RRL_WH_FINAL_SCALE_USE drop(SIGNATURE_VERSION);
