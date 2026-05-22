-- Rollback 047: удалить СТ, адреса, ТС и водителей «Добра Цен»
prompt [rollback 047] Добра Цен — удаление СТ, адресов, ТС, водителей

DELETE FROM RRL_SBORKA_PALLET_ROWS
 WHERE PALLET_UID LIKE 'ДЦПЛ%';

DELETE FROM RRL_SBORKA_PALLETS
 WHERE PALLET_UID LIKE 'ДЦПЛ%';

DELETE FROM RRL_ADDR
 WHERE ADDR LIKE 'Добра Цен #%';

DELETE FROM RRL_TR_VEHICLE
 WHERE ID BETWEEN 9201 AND 9215;

DELETE FROM RRL_TR_VODITEL
 WHERE ID BETWEEN 9201 AND 9215;

COMMIT;
prompt [rollback 047] done
