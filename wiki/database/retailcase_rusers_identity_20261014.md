# Уникальная идентичность RUSERS

По прямому поручению владельца 14.10.2026. Предварительно:1169 строк,1169 точных ID, NULL0; регистронезависимое совпадение только между активной и удалённой исторической записью, активных конфликтов0. ID уже NOT NULL и имел уникальный индекс, но не UK/PK constraint — поэтому Oracle не разрешал внешний ключ. Это различие существенно: данные были уникальны, отсутствовал декларативный ключ для ссылочной целостности.

Миграция2026-10-14-rusers-identity-constraints повторно использует существующий unique index для RUSERS_ID_UK, добавляет функциональный RUSERS_ACTIVE_LOGIN_UK по lower(trim(ID)) только для активных и FK RRL_ACCESS_ASSIGN_USER_FK. Пользователи не переименовываются/не удаляются; историческая запись сохраняется. Восстановление или создание активного конфликтующего логина отклоняется БД.

[Apply](../../db/migrations/2026-10-14_rusers_identity_constraints/apply.sql), [rollback](../../db/migrations/2026-10-14_rusers_identity_constraints/rollback.sql), [verify](../../db/migrations/2026-10-14_rusers_identity_constraints/verify.sql), checkpoint.json рядом. Статус PREPARED до live verify.

## Последующее прямое решение: удалить дубль

Владелец потребовал удалить найденный дубль. Миграция2026-10-14-rusers-deduplicate-login удаляет только soft-deleted KLAD_Uzenaliev, сохраняя активного KLAD_UZENALIEV. Связанных назначений0, иных декларативных FK на пользователя нет. Перед удалением исходная полная строка сохраняется в RRL_RUSERS_DEDUP_BAK без вывода credential-полей. После очистки RUSERS_LOGIN_UK запрещает lower(trim(ID)) дубли среди всех строк; предыдущий active-only индекс удаляется как избыточный. [Apply/verify/rollback](../../db/migrations/2026-10-14_rusers_deduplicate_login/apply.sql). Старое описание сохранения двух строк выше — история до нового решения владельца.

Live: обе миграции APPLIED, удалена1строка/backup1; RUSERS1168, normalized duplicates0, UK/FK ENABLED VALIDATED, RUSERS_LOGIN_UK VALID UNIQUE, INVALID0. Первоначальная схема уже имела unique index на ID, новый UK делает его пригодным для FK.
