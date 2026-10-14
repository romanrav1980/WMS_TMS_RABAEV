-- Additive evidence retained; do not remove weight/dimension history.
declare n number;begin select count(*)into n from RRL_WMS_RECEIPT_UNIT where WEIGHT_LABEL_SCAN is not null;
 if n>0 then raise_application_error(-20886,'PHYSICAL_BOX_MEASUREMENT_HISTORY_PREVENTS_COLUMN_REMOVAL');end if;
end;
/
alter table RRL_WMS_RECEIPT_UNIT drop constraint RRL_UNIT_BOX_MEASURES_CK;
alter table RRL_WMS_RECEIPT_UNIT drop (GROSS_WEIGHT_KG,BOX_VOLUME_M3,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN);
@@../2026-10-08_stock_posting_core/014b_recompile.sql
