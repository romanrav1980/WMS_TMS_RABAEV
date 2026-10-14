drop package RRL_ORDER_WEIGHT_READ;
declare n number;begin select count(*)into n from RRL_SKU_RECEIPT_POLICY where ORDER_WEIGHT_TOLERANCE_PCT!=15;if n>0 then raise_application_error(-20863,'ORDER_WEIGHT_POLICY_RETAIN_CONFIGURED_VALUES');end if;end;
/
alter table RRL_SKU_RECEIPT_POLICY drop constraint RRL_SKU_ORDER_WT_PCT_CK;
alter table RRL_SKU_RECEIPT_POLICY drop column ORDER_WEIGHT_TOLERANCE_PCT;
