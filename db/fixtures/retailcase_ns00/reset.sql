-- NS00 fixture data only. Execute through provenance-checking runner, not directly.
-- No commit: caller owns the complete fixture transaction.

-- TABLE: RRL_CUSTOMER_ORDER_ROW
delete from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=:CUSTOMER_ORDER_ROW_ID;

-- TABLE: RRL_CUSTOMER_ORDER
delete from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:CUSTOMER_ORDER_ID;

-- TABLE: RRL_REMAINS
delete from RRL_REMAINS where UID_POLETA=:UID_POLETA and CELL=:CELL;

-- TABLE: RRL_PALLETS
delete from RRL_PALLETS where UID_PALLET=:UID_PALLET;

-- TABLE: RRL_PRIHOD_NAKLAD
delete from RRL_PRIHOD_NAKLAD where ID=:ID;

-- TABLE: RRL_CUSTOMER
delete from RRL_CUSTOMER where CUSTOMER_ID=:CUSTOMER_ID;

-- TABLE: RRL_ARTICULS
delete from RRL_ARTICULS where ACTICUL=:ACTICUL;

-- TABLE: RRL_CELLS
delete from RRL_CELLS where CELL=:CELL;

-- TABLE: RRL_WARES
delete from RRL_WARES where ID=:ID;
