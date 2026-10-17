# OPC1.2: свидетельство физической сверки после расхождения

MIGRATION_ID `2026-10-15-assembly-reconciliation-evidence`. **APPLIED** после применения recovery schema:6 statements/0 errors; source3 exact/USER_ERRORS0/INVALID0. [SQL комплект](../../db/migrations/2026-10-15_assembly_reconciliation_evidence/apply.sql), точный before/manifest/rollback/verify рядом. Владелец integrations; товарный writer не меняется.

Отдельный capture_kind WAREHOUSE_ASSEMBLY_RECON и protocol_version1.2 сохраняют canonical bytes прежних1.0/1.1. zero_reference содержит session_id/step_id/RECONCILE/initial tare_capture_key/reconciliation_id. Нет нового искусственного zero_observation под загруженной тарой. Native связывает сырое OPC наблюдение с RRL_ASM_RECON_CAPTURE и неизменяемой начальной тарой сессии, actualWARE/post, исходным sender и sourceSHA. Возврат к последнему принятому весу разрешает только native recovery owner; raw archive не изменяет ни количество, ни состояние укладки.

Текущий sender и права проверяются до/после device lock; profile/certificate остаются GATEWAY_REPORTED. Отдельные capture/raw HTTP транзакции не выдаются за одну атомарную поставку. Локальный bundle journal сохраняет оба исходных тела перед отправкой и восстанавливает очередь без повторного измерения.

Независимое read-only review scale_protocol: дополнительных blockers не найдено. После apply обязательны exact source/USER_ERRORS/INVALID, настоящее native binding/negative refs и регрессия старых контекстов. Обратная смена body/constraint только при остановленных отправителях и пустой новой истории; иначе forward recovery без удаления evidence.

[[retailcase_assembly_recovery_20261015]], [[retailcase_assembly_evidence_binding_20261015]].

Реальная интеграционная приёмка с зашифрованным локальным OPC сервером→production HTTP→native PASS: GROSS0.5, recovery COMPLETED/stepCANCELLED/sessionOPEN, raw1.2MATCHED, исходный P/H/version без изменений, stockop/STEP_USE отсутствуют. Это протокольная TEST-симуляция, не физические весы. [Отчёт](../../reports/retailcase/2026-10-15/assembly-scale/opc-reconciliation-http-report.json).
