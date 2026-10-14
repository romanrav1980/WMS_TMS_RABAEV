from pathlib import Path
import json
def append(name,text):
 p=Path(name);p.write_text(p.read_text(encoding="utf-8")+"\n"+text+"\n",encoding="utf-8")
append("wiki/database/retailcase_ni071_unload_norm_basis_20261012.md","Применена572:3 statements/0 errors, USER_ERRORS[]/INVALID[].574: явная PLACE и pallet4.125, одна версия при двух отправителях, внешний rollback восстанавливает head; старый14-полевый точный повтор сохраняет исходный результат. История UI показывает единицу и ставку паллеты.")
append("wiki/database/retailcase_ni071_vehicle_source_20261012.md","565/566: выполнен новый оригинальный LOAD/DEPART с READY profile1, source1 и одним точным clock; товарный эффект DEPART0.575: ранее созданный источник принят получателем BOX3 с завершённой MANUAL выгрузкой. Старый519 остаётся без выдуманного профиля. Manifest579 включает559/561/564; целиком на ACTIVE не применялся.")
append("wiki/database/retailcase_ni071_transport_cost_preview_20261012.md","SQL579: периодный выбор2.766ms/7.67buffers, выгрузка6.9ms/28buffers, архив адресов4.299ms/21buffers. Решение: сохранить source_price+ware фильтр и ограничение1 версии, LOAD/receipt bounds200; имеющиеся PK/версионные ключи достаточны для текущего случая. Owner finance: перед ростом проверить план сортировки effective_from/version и selective source joins; не создавать индекс без измеренного ухудшения.569 холодный LOAD-source30.947ms/343buffers занесён в тот же backlog для predicate pushdown/плана, не является результатом нагрузочного теста.")
p=Path("wiki/index.md");p.write_text("- [Checkpoint580: транспорт по фактам](database/retailcase_ni071_transport_cost_preview_20261012.md): archived departure/unload, explicit norm basis, exact107.25 rollback-only preview; paid hours/money recognition remain open.\n"+p.read_text(encoding="utf-8"),encoding="utf-8")
append("wiki/log.md","2026-10-12 checkpoint580:559–579 consolidation; native572 applied/VALID, norm574 concurrency/replay/rollback, retained575 original customer3/manual unloading,576 foreign warehouse norm rejection,578 actual immutable-source preview107.25 with all synthetic norms rolled back/hourly missing refuses total. Existing billing UI extended; TS577 PASS, architecture576668/0cycles/76debt. SQL579 bounded-query decision documented. Current API577 startup complete. Bundle579 maintained only, not applied on ACTIVE; NI07.1 and all18 not falsely closed.")
p=Path("wiki/runbooks/retailcase_active_work.md");p.write_text("""## Current checkpoint580 — 12Oct2026
- User: continue all sprints; full commit/GitHub only after completion, SAP excluded. No subagents / no broad repeated qualification.
- API577 actual startup complete; TS577 PASS; native572 VALID; architecture576668/0cycles/76debt.
- 574 explicit norm basis PLACE/pallet4.125 published to private old532 source, legacy14 replay preserved; ctx574 exact replay only, no recreation.
- 565 fresh private departure READY profile1 preserved,575 original customer accepted3/manual unload complete; no repeated stock debit. context565/context575 must not recreate original factories.
- 576–578 read-only transport preview exists in existing billing, exact norm period/type/class/carrier/region/ware guards, address vs place basis. Actual578 rollback-only synthetic100+5+2.25=107.25; hourly2 refuses total and all trial tariff/history rolled back. No permanent commercial tariff, no monetary recognition.
- Bundle579 contains vehicle559/hash561/config564/norm572; never apply whole ACTIVE snapshot. SQL5792.766/6.9/4.299ms; source56930.947ms retained finance plan/predicate backlog.
- Continue NI07.1: billable-time contractual source, money rounding/currency and recognition tied to archived original sources; preserve existing carrier billing and avoid duplicate tariff inclusion. Preview is not posted cost.
- Latest details [[database/retailcase_ni071_transport_cost_preview_20261012]], [[database/retailcase_ni071_unload_norm_basis_20261012]].
- All18 increments remain incomplete; external/legal/hardware/independent evidence must not be fabricated.

"""+p.read_text(encoding="utf-8"),encoding="utf-8")
append("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_1.md","559–580: immutable profile-on-departure plus original LOAD_ST addresses and customer unloading575 reused; norm572 explicit POINT/PLACE and pallet rate, old exact replay preserved. Existing billing read-only preview576–578 validates immutable period/class/route/warehouse; actual rollback-only norm107.25 and hourly-data refusal. Monetary recognition, paid-time/extra-loader contract and currency rounding still open; no closure or publication yet.")
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
(root/"NI07.1"/"580_transport_norm_preview.md").write_text("""# Задания Qwen: NI07.1, checkpoint580

Не запускать старые case532/535/543/563/565/574/575: их факты сохранены. Независимое ревью пока не выполнено. Не менять реальные договорные тарифы и историю.

1. Проверить source+class/type/carrier/region/warehouse и выбор latest effective_from/version на фактическую дату выезда. Норма другого склада должна отказать.
2. На собственном изолированном источнике проверить PLACE против POINT для двух мест одного адреса; смешанные методы POINT не дают итог.
3. Проверить старый14-полевый exact retry и новые16-полевые нормы, conflicting OP и rollback. Не переписывать старые результаты.
4. Проверить preview107.25 только в откатываемой транзакции; hourly>0 без подтверждённого времени возвращает total=null, без скрытого нуля.
5. Проверить текущие права, malformed/unknown pending publication exact retry, историю и восстановление UI после ошибки чтения. Контролировать исходные qty/резервы; preview не создаёт outbox и money journal.
6. Проверить SQL на связанных фильтрах/лимитах1/200 и неизменность существующего carrier invoice. Результат с файлами/ошибками/SQL и честными ограничениями.

Исходники: transport_cost_preview.py, transport_cost_facts.py, migration572, TransportCostPreview.tsx. Подготовка заданий не означает запуск модели или принятие спринта.
""",encoding="utf-8")
print("Checkpoint580 wiki/index/log/runbook/current sprint/Qwen tasks saved.")
