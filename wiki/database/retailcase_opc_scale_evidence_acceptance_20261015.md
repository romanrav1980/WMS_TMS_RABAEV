# OPC raw evidence: native приёмка · 15.10.2026

Миграция `2026-10-15-opc-scale-evidence` APPLIED root:8statements/0errors. [Комплект](../../db/migrations/2026-10-15_opc_scale_evidence/apply.sql), checkpoint и paired rollback рядом. Независимая от написания SQL native проверка выполнила [exact-source verifier](../../scripts/opc_scale_evidence_verify_oracle.py): live body/spec/trigger полностью совпали с SQL, USER_ERRORS0/globalINVALID0, constraints ENABLED, ledger APPLIED. До функционального прогона source проверен отдельно; тексты SQL при приёмке не менялись.

## Что доказано

[Native script](../../scripts/opc_scale_evidence_native_smoke.py), [результат](../../reports/retailcase/2026-10-15/scale-evidence/native-acceptance.json): STORE_RECEIPT, WAREHOUSE_PICK и WAREHOUSE_FINAL привязались к существующим исходным capture через точный capture SHA и исходного sender. Archive/read/exact replay совпадают; изменённый body, неверный capture hash, NULL protocol отвергаются. Чужой actor и временно отозванный sender не читают/не повторяют архив. Отсутствующий capture даёт PENDING; создание нового измерения для искусственного перехода в MATCHED не выполнялось. Прямые INSERT/UPDATE/DELETE запрещены guard.

Все raw zero/observations в этом сценарии — явно `TEST_FIXTURE_NOT_HARDWARE`, основанные на API fixture, не показания реального OPC устройства. Native archive принимает исходный bad quality и NULL SourceTimestamp для диагностики: это GATEWAY_REPORTED provenance, не решение о стабильности/приёмке/товарном эффекте. Существующие warehouse captures имеют TEST mode; магазинный старый архив отдельного DEVICE_MODE поля не хранит, использован известный исторический QA sender, без утверждения аппаратного происхождения.

Исторические dedicated QA sender были DELETED=1 намеренно. Только caller transaction временно возвращала DELETED=0; затем finally rollback восстановил каждое исходное значение. Отдельная согласованная root отрицательная проверка в config context временно сменила store-device sender на другого действующего dedicated QA и подняла policy version по существующему guard. Даже текущий новый sender не смог привязать evidence к старому capture: ORIGINAL_SENDER_REQUIRED. Finally rollback восстановил sender/version/actor flags точно. COMMIT в скрипте отсутствует; количество evidence вернулось к исходному, исходные capture и товарные строки не менялись.

11 API contract tests повторно PASS; они используют MemoryArchive и не выдаются за live HTTP→Oracle proof. Native caller-owned TX не виден отдельному HTTP connection; отдельные постоянные fixture ради этого не создавались. [Oracle verifier evidence](../../reports/retailcase/2026-10-15/scale-evidence/oracle-verification.json).

Archive17/8/12мс; slow log за час пуст. Решение integrations/Codex: оставить unique identity/capture lookup, новых индексов не добавлять. При повторе >1000мс — атрибуция SQL и execution plan. Native прямые вызовы не создавали HTTP API audit. Реальный OPC/server certificate/raw archive end-to-end на физическом посту и PENDING→MATCHED на новом настоящем измерении остаются отдельным пилотом.

[[components/retailcase_warehouse_scale_gateway_20261015]], [[roadmap/retailcase_access_knowledge_plan]].
