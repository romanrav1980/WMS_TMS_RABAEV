declare n number;begin select count(*)into n from RRL_TT_LOAD_BOX_WEIGHT where CASE_BOX_TASK_ID is not null;if n>0 then raise_application_error(-20863,'CASE_MASS_DEPARTURE_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_admission.sql
@@000_before_read.sql
@@000_before_boxes.sql
@@000_before_load.sql
@@000_before_store_weight.sql
@@000_before_guard.sql
@@000_before_store.sql
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_ORIGIN_C;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_COVER_C;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_CASE_F;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_SCALE_F;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_QC_F;
alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint RRL_LOAD_BOX_PALLET_F;
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_LEGACY_PALLET_F foreign key(BOX_UID)references RRL_PALLETS(UID_PALLET);
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_LEGACY_ORIGIN_C check(MEASUREMENT_ORIGIN='MANUAL_CONFIRMED');
alter table RRL_TT_LOAD_BOX_WEIGHT drop(PALLET_BOX_UID,CASE_BOX_TASK_ID,FINAL_SCALE_CAPTURE,WAREHOUSE_QC_OPERATION,TARE_WEIGHT_KG,NET_WEIGHT_KG,DEVICE_MODE,COMPOSITION_SIGNATURE,SIGNATURE_VERSION,MEASURED_CONTENT_VERSION,COVERAGE_COMPLETE);
