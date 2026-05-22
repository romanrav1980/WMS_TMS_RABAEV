-- Rollback 046: удалить склады, ячейки и артикулы «Добра Цен»
prompt [rollback 046] Добра Цен — удаление складов, ячеек, артикулов

-- Сначала 047 (паллеты/адреса), потом этот
DELETE FROM RRL_CELLS
 WHERE WARE_ID IN (9201, 9202, 9203);

DELETE FROM RRL_ARTICULS
 WHERE ACTICUL LIKE 'ДЦ-%';

DELETE FROM RRL_WARES
 WHERE ID IN (9201, 9202, 9203);

COMMIT;
prompt [rollback 046] done
