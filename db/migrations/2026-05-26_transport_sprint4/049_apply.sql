-- =============================================================================
-- Migration 049 — Sprint 4: нет изменений схемы БД
-- =============================================================================
-- Sprint 4 (Редактирование и закрытие рейса) выполнен полностью на уровне
-- Python (FastAPI) и TypeScript (React). Изменения БД не требуются:
--   — PATCH /tasks/{id} расширен полями shipment_date и transtype
--     (UPDATE RRL_TRANSPORT_TASK — таблица уже содержит эти колонки)
-- =============================================================================

prompt [049] Sprint 4 — нет изменений схемы, no-op migration

-- Подтверждение: таблица RRL_TRANSPORT_TASK содержит все нужные колонки
SELECT COLUMN_NAME
  FROM ALL_TAB_COLUMNS
 WHERE TABLE_NAME = 'RRL_TRANSPORT_TASK'
   AND OWNER = 'RABAEV'
   AND COLUMN_NAME IN ('TRANSTYPE', 'SHIPMENT_DATE', 'TRANSPORT', 'VODITEL_ID',
                       'DOCK', 'SHIPMENT_TIME', 'PRIMECHANIE')
 ORDER BY COLUMN_NAME;

COMMIT;
