# Архив исходных OPC показаний весов

MIGRATION_ID: `2026-10-15-opc-scale-evidence`. **APPLIED**:8 statements/0 errors, source3 exact/INVALID0; [приёмка](retailcase_opc_scale_evidence_acceptance_20261015.md). Дополнение [assembly v1.1](retailcase_assembly_evidence_binding_20261015.md) применено отдельно, исходные три v1.0 контекста сохранены. Решение владельца:
[[../components/retailcase_weighing_gateway]]. Владелец — integrations, товарные
команды остаются inventory/delivery. SQL: [комплект](../../db/migrations/2026-10-15_opc_scale_evidence).

Новая RRL_OPC_SCALE_EVIDENCE хранит неизменяемый envelope v1: namespace/model,
реальные ExpandedNodeId по профилю, DataValue variant/value/statusCode/source и
server timestamps, observed_at, ноль и 5–25 наблюдений, отпечатки профиля/сертификата,
станцию и SHA256 канонического capture. HTTP max128KiB, строгий DTO; bad/null quality
сохраняется для диагностики и само не разрешает товарную команду.

RRL_OPC_EVIDENCE_API проверяет dedicated текущего sender зарегистрированного прибора,
legacy ingest право и WARE для складского прибора; GLOBAL_ADMIN не притворяется sender.
Revision SHARE до device FOR UPDATE WAIT2, повторная проверка после lock.
Физическая готовность/поверка не выводится из доступности исторического архива:
инактивный прибор может иметь доказательства прошлых измерений при действующем sender.

Identity: kind+device+capture. Exact body replay возвращает тот же digest; другое тело
конфликтует. Append-only trigger допускает insert только из package/TX context.
Native binding читает фактический capture: scope/post/purpose, original sender,
SOURCE_SHA256 должны совпасть. До появления capture состояние PENDING, после MATCHED;
это вычисляемая связь, а не новый редактируемый stock факт.

Provenance явно GATEWAY_REPORTED: сохранение сертификатного отпечатка не является
серверной криптографической аттестацией устройства. API архива и capture сейчас
раздельны; ни MATCHED, ни ARCHIVED не подтверждают отбор, QC, отгрузку или приёмку.
Для обязательной atomic evidence admission в будущих новых сценариях нужен отдельный
native guard единственного stock writer. Существующие strict capture DTO не расширены.

Проверки до apply: новый namespace объектов отсутствует, INVALID0. Checkpointmanifest
и rollback запрещает удаление непустого архива. API contract11 tests PASS, fake service
не считается Oracle или аппаратной приёмкой. Следующий этап — native rollback и realHTTP.
