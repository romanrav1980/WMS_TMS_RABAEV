declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_PACK_ROLLBACK');end if;end;
/
drop trigger RRL_PALLET_PACK_GUARD;
alter table RRL_PALLETS drop constraint RRL_PALLET_PACK_CHK;
alter table RRL_PALLETS drop(STOCK_BOX_FACTOR,STOCK_PACK_BASE_UOM,STOCK_PACK_FROZEN);
@@014b_recompile.sql
