# Исходные OPC данные сборки · протокол1.1

Миграция `2026-10-15-assembly-evidence-binding` **APPLIED** после применения assembly schema:6 statements/0 errors; source3 exact/USER_ERRORS0/INVALID0. Native binding acceptance в работе. Добавляет `WAREHOUSE_ASSEMBLY` в существующий append-only архив и заменяет только body `RRL_OPC_EVIDENCE_API`. [Комплект](../../db/migrations/2026-10-15_assembly_evidence_binding/apply.sql), before/checkpoint/rollback/verify рядом. Live source до применения совпал с v1.0; RABAEV/orcl, INVALID0.

В1.0 три существующих контекста и canonical bytes сохраняются. В1.1 continuous GROSS не выдаёт начальную тару за новое наблюдение нуля: вместо zero_observation передаётся zero_reference (session_id, step_id, phase, tare_capture_key). Native сверяет их с настоящими RRL_ASSEMBLY_CAPTURE/SESSION, текущим sender, исходным SOURCE_SHA, WARE/post и исходным автором capture. До появления capture архив PENDING; несовпадающая ссылка после появления capture вызывает конфликт. Товарный эффект здесь не создаётся.

Сертификат/профиль/сырые DataValue архивируются как GATEWAY_REPORTED, без утверждения криптографической аттестации сервера. HTTP header должен совпадать с protocol_version тела. Ошибочные quality/timestamps могут храниться для диагностики, но не допускают товарную операцию.

Recovery: обратная смена constraint/body допустима только при остановленных отправителях и отсутствии записей WAREHOUSE_ASSEMBLY. При сохранённой истории — forward fix; удаление evidence запрещено. Старые записи не переписываются.

Native compile/readback и тесты реальных ссылок выполняются после применения; физические весы не проверены.

[[retailcase_incremental_assembly_20261015]], [[retailcase_opc_scale_evidence_20261015]].

## Native shape correction

Первый реальный binding-тест выявил ORA40565: Oracle JSON_OBJECT_T.HAS на отсутствующем optional поле тоже бросает исключение при on_error(1). Валидный v1.1 не содержит zero_observation. Forward migration `2026-10-15-assembly-evidence-shape-fix` сохраняет strict required getters, но выполняет только проверки формы в default on_error(0); затем возвращает strict1. Исходный применённый комплект не переписан, before/checkpoint/rollback сохранены. Тестовая попытка полностью rollback, stock effects отсутствовали.

Shape fix APPLIED4/0; source3 exact/INVALID0. Native обеих фаз PASS:4 неверных ссылки на фазу, неправильный hash, exact read/replay, changed-body conflict, чужой/отозванный sender, append-only. Caller rollback восстановил число evidence, sourceP20/H20. Archive19.1/15.6мс: существующие адресные ключи сохранены, индекс не нужен. Повтор старого v1.0 native smoke PASS для всех трёх контекстов после новой версии. [Отчёт](../../reports/retailcase/2026-10-15/assembly-scale/evidence-native.json).

Аудит инструмента: ad-hoc preapply normalizer пропустил удаление CR; проверка упала, а PowerShell продолжил следующую команду. Сохранённый before-image затем проверен нормализатором штатного verifier и совпал с предыдущим применённым/прочитанным live source. Повторные зависимые apply/verify выполняются отдельными tool calls с проверкой результата; это не доказательство корректного первоначального gate.
