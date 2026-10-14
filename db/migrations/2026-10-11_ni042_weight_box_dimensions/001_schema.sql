-- MIGRATION_ID:2026-10-11-183-physical-box-dimensions
alter table RRL_WMS_RECEIPT_UNIT add
 (GROSS_WEIGHT_KG number(27,9),BOX_VOLUME_M3 number(27,9),MEASUREMENT_REFERENCE varchar2(200 char),WEIGHT_LABEL_SCAN varchar2(512 char));
alter table RRL_WMS_RECEIPT_UNIT add constraint RRL_UNIT_BOX_MEASURES_CK check
 ((GROSS_WEIGHT_KG is null or (GROSS_WEIGHT_KG>0 and (BASE_UOM!='KG' or GROSS_WEIGHT_KG>=BASE_QTY)))
  and (BOX_VOLUME_M3 is null or BOX_VOLUME_M3>0)
  and ((GROSS_WEIGHT_KG is null and BOX_VOLUME_M3 is null)or MEASUREMENT_REFERENCE is not null));
