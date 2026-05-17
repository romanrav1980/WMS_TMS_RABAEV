prompt [migration 2026-05-17-013] smoke cleanup

delete from RRL_PROD_BATCH
 where PROD_BATCH_NO = 'SMOKE-BATCH-013-AGING'
    or SOURCE_SYSTEM = 'SMOKE-013';

delete from RRL_ARTICULS
 where ACTICUL = 'FG-AGING-SMOKE-013';

commit;

prompt [migration 2026-05-17-013] smoke cleanup done
