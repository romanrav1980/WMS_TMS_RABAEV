-- Проверка применения: таблица существует, пакет VALID.
SELECT table_name FROM user_tables WHERE table_name = 'RRL_TRIP_CREATE_RESULT';
SELECT object_name, object_type, status
  FROM user_objects
 WHERE object_name IN ('RRL_TRANSPORT_IDEMPOTENT_API')
 ORDER BY object_type;
-- Ожидание: одна строка таблицы; пакет и тело VALID (2 строки, status='VALID').
