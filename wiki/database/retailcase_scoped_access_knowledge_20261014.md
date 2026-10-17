# Scoped access и локальные знания — Oracle

MIGRATION_ID: 2026-10-14-scoped-access-knowledge. Подготовлено по принятому решению владельца; перед apply checkpoint.json фиксирует целевой RABAEV/orcl, INVALID0, отсутствие новых объектов и SHA256 скриптов. Additive metadata, legacy-пользователи/RIGHTS/RRL_HAS_WRIGHT не меняются. Кодовые изменения checkpoint сохранены без публикации GitHub.

Объекты: RRL_ACCESS_REV/ROLE/ROLE_RIGHT/OBJECT/GROUP/GROUP_MEMBER/BRANCH_MEMBER/ASSIGNMENT/AUDIT; RRL_PLATFORM_COMMAND; RRL_KNOWLEDGE_SPACE/ARTICLE/REV; пакеты RRL_ACCESS_API/RRL_KNOWLEDGE_API. Native допуск и запись метаданных — авторитет Oracle; UOW коммитит данные, аудит и квитанцию вместе. Scoped admission удерживает shared lock конфигурации до завершения транзакции; админ-команды — exclusive lock. Срок/область делегируются одним покрывающим назначением, а не независимо.

[SQL](../../db/migrations/2026-10-14_scoped_access_knowledge/apply.sql), [checkpoint](../../db/migrations/2026-10-14_scoped_access_knowledge/checkpoint.json), [rollback](../../db/migrations/2026-10-14_scoped_access_knowledge/rollback.sql), [verify](../../db/migrations/2026-10-14_scoped_access_knowledge/verify.sql). Перед rollback после начала эксплуатации экспортировать новые метаданные. Старые таблицы этим rollback не затрагиваются.

Исходное состояние перед применением — PREPARED; фактический APPLIED и подтверждения записаны ниже в разделе Live. ORG_BRANCH идентифицируется KIND:ID; snapshot ветви материализует текущий состав в рамках access revision. Текущие рабочие endpoints пока не переведены автоматически на новый допуск.

## Live результат 15.10.2026

APPLIED: native пакеты скомпилированы, USER_ERRORS0/INVALID0. Первое применение остановилось на отсутствующем declarative UK RUSERS.ID; prefix6таблиц проверен и продолжен resume_apply. Позднее по прямому поручению владельца добавлены UK/FK и normalized login uniqueness, удалён один soft-deleted дубль с backup. Native smoke11сценариев PASS, live HTTP admin/ordinary/replay/conflict/receipt PASS; fixtureusers и метаданные удалены. Регистр складов сопоставляет RRL_WARES.ID без назначения ролей. /api/help читает опубликованную Oracle-редакцию; черновик не подменяет её. Native explanation возвращает источники GLOBAL_ADMIN/LEGACY_GROUP/ASSIGNMENT. [Evidence](../../reports/retailcase/2026-10-14/access-knowledge/native-smoke.json). Перевод бизнес-операций склада/транспорта на scoped-допуск ещё отдельный интеграционный блок; это не завершение всех8спринтов.
