# Qwen: общий read-only контроль автоплана и ручного рейса

Запусти scripts/ni081_transport_preflight_existing_case.py и scripts/ni081_transport_preflight_scope_case.py. Ожидания:633 отсутствующиеСТ/несовпадениеplate;632applied/retired;33523cancelled;HTTP200BLOCKED/422/404. Scope case временно меняет собственную metadata и делает rollback, без commit. Подтверди отсутствие измененийTT/ST/P/H.

Отдельно проверь дубли/невалидныйJSON/неизвестнуюнормумассы/гидроборт/типадреса/строгиеокна через существующие RRL_TRANSPORT_PLAN_RULES, не создавая второй rule engine. Чтение текущих СТ — порции200/общий5000, plan≤100routes/2000СТ; свежаяwarehouseauthorization до возврата source data. В UI русский reason и запоздалый ответ после plan change не должен показываться для нового плана.

Предварительная проверка не применяет план и не снимает native strict schedule gate. Даже CURRENT_NATIVE_RULES_CHECKED имеет operational_admission=false/driver+warehouse readiness unverified. Запиши реальные SQL/ответы/ошибки и ограничения независимой приёмки; промышленную готовность по авторским bounded случаям не объявлять.
