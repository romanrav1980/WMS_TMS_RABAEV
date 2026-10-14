declare n number;begin select count(*)into n from RRL_WH_SCALE_CAPTURE where CAPTURE_PURPOSE!='PICK';if n>0 then raise_application_error(-20863,'FINAL_SCALE_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_archive.sql
@@000_before_admission.sql
drop index RRL_WH_SCALE_CASE_PURPOSE_I;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_SOURCE_C;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_TARE_F;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_TYPE_F;
alter table RRL_WH_SCALE_CAPTURE drop constraint RRL_WH_SCALE_PURPOSE_C;
alter table RRL_WH_SCALE_CAPTURE modify(CASE_PICK_LINE_ID not null,ARTICLE not null,SOURCE_CELL not null,SCANNED_PRODUCT not null);
alter table RRL_WH_SCALE_CAPTURE drop(CAPTURE_PURPOSE,TARE_CAPTURE_KEY,PALLET_TYPE_ID,TYPE_VERSION,COMPOSITION_SIGNATURE);
