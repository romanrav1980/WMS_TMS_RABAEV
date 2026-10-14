from pathlib import Path
import json
out={}
page="wiki/database/retailcase_ni072_st_defer_20261011.md"
text="""# Перенос всей неотобранной СТ на существующий рейс
276 / NI07.2: RRL_ST_DEFER_API использует прежние RRL_TT_ADD_PALL и RRL_TRANSPORT_PLAN_API.assign_sts. Привязка остаётся в RRL_SBORKA_PALLETS.TRANSTASK_ID. Новая таблица RRL_ST_DEFER_DECISION — неизменяемый журнал решения, а не вторая таблица назначений.

Все паллеты одной СТ, один текущий склад/рейс; текущие права до повтора и после блокировки. Переносятся только неотобранные и непогруженные СТ: любое CASE-задание, фактическое исполнение или действующая погрузка запрещают команду. Оба рейса спланированы, не удалены и не выставлены в счёте; целевая дата не раньше исходной даты рейса и STDATE. Объём и обещанные даты заказа SAP не переписываются.

Порядок: общий METADATA_TX CONFIG6, транспорт по ID, рейсы по ID, все исходные и целевые строки СТ по ID. Статус рейса повторно проверяется уже под блокировкой. Источник хешируется с составом строк, количеством/единицами, упаковкой/массой, датами и заголовком рейса. Ограничения 200 исходных паллет, 400 суммарных строк, 10000 строк товара. Версия и source_hash обязательны. Прежнее снятие назначения, проверенное назначение, пересчёт адресов и запись причины проходят в одной транзакции без внутреннего COMMIT. Поздняя ошибка откатывает изменения к savepoint. Корневое ядро остатка не вызывается.

Повтор сверяет фактический JSON и хеш/пользователя/СТ и возвращает сохранённый результат, даже если текущее назначение позже изменилось. Текущий доступ к складу обязателен. Причина и ссылка на решение обязательны. История только READ ONLY, текущий склад, курсор версии, максимум 50 записей. API /api/transport/st-deferrals: context/history/POST. Панель на прежней дневной сверке, сохранение команды до отправки, повтор прежнего operation_id, выбор СТ из реестра. Реестр и снимок дневной сверки показывают версию переноса. Это не физическая отгрузка и не закрытие дня.

Фактический авторский сценарий: SAP_2046 / WARE9807 / две паллеты / 48 EA, 20 kg / source33571 03.11 → существующий целевой рейс 04.11. Полный outer rollback восстановил обе привязки и удалил неподтверждённый журнал; затем две конкурентные команды дали 200/409, точный повтор 200, другой текст того же ID — 409. Исходные 48 EA сохранены, fulfillment 2 PLANNED/FACT0, защищённый P20/H20 неизменён. История одна запись, следующая страница пустая; SAP_FILE_GATEWAY denied403. Дневной снимок содержит две строки версии1 и открытый пункт отсутствующего выезда.

SQL: новая bounded версия реестра cold55.042ms/117 buffers и57.473ms/168 buffers, прежняя steady14.507ms/26 buffers. Решение владельца Oracle/finance: оставить boundedIDs/индекс WARE-STDATE-ID и уникальный ST-version; проверить steady при реальной нагрузке, не увеличивать timeout и не добавлять cache. Общий CONFIG6 делает перенос редкой последовательной операцией планирования; массовый параллельный перенос не заявлен. Независимое Qwen/browser и поздний отказ по вместимости после снятия назначения — отдельные задания, не объявлены пройденными. Полный NS58 и перенос уже отобранных мест остаются открыты.
"""
out[page]=text
for path,line in [
("wiki/index.md","- [Атомарный перенос неотобранной СТ](database/retailcase_ni072_st_defer_20261011.md):276 прежнее назначение/неизменяемая причина/версия/исходный SAP сохранён; фактические две паллеты и конкурентный победитель."),
("wiki/log.md","2026-10-11:276 NI07.2 native ST deferral reuses original unassign/assign, immutable reason/source/cargo hash/currentWARE/version; sorted vehicle/TT/ST underCONFIG6; no stock writer. ActualSAP_2046 2pallet48EA source33571 Nov3->targetNov4; outer rollback, concurrent200/409, exact replay/collision, history50/service403/daily snapshot2v1/P20H20. Raw durable command panel. Bounded SQL cold55/57ms117/168buf; retainexistingdateindex+STversion uniqueness. Independent late capacity failure/browser/fullNS58 remains."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_2.md","11.10.2026:276 Перенос всей неотобранной СТ на существующий рейс реализован через прежнее назначение, без второго реестра. Причина/основание/версия/история, исходные SAP даты и объём сохранены; фактический SAP_2046 две паллеты/48EA, rollback/конкурентный победитель/повтор/P20H20. Не разрешает перенос CASE/погруженного товара. Полный NS58/независимая приёмка остаются открыты."),
("wiki/runbooks/retailcase_active_work.md","Latest276 native RRL_ST_DEFER_API/schema VALID; app609/zero cycles76 baseline. tmp/context276.json: SAP_2046 2 planned pallets48EA source33571 Nov3 -> target recorded in context Nov4, onev1 decision, FACT0/P20H20 unchanged. Original unassign/assign atomic outer rollback/concurrent winner/exact replay. History and shipping snapshot version wired. UI durable command/reason/reference; no physical dispatch. CONFIG6 rare-plan serialisation. Full NS58 and independent latecapacity/browser pending. Native manifest/bundle276 generated locally, never fullbundle applied.")
]:
 out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native275/app275/","current native276/app276/")
design="wiki/database/retailcase_ni072_st_defer_design_20261011.md"
out["wiki/index.md"]+="\n- [Граница переноса СТ](database/retailcase_ni072_st_defer_design_20261011.md): первоначальный проект276; окончательная реализация и ограничения описаны в странице переноса.\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
j["startup_scripts"].append("../2026-10-11_ni072_st_defer/001_schema.sql")
j["components"].append("../2026-10-11_ni072_st_defer/002_api.sql");j["packages"].append("RRL_ST_DEFER_API")
out[str(p)]=json.dumps(j,indent=2)+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI07.2").setdefault("implementedSlices",[]).append("276 original atomic unpicked-ST deferral/currentWARE/version/immutable reason/source/cargo preserved/actualSAP2pallets/noStock/durableUI/history/dayregister")
out[str(p)]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI07.2"/"276_st_deferral.md")]="# Qwen: перенос СТ276\nПроверить старое назначение, все паллеты одной СТ, исходный SAP объём/даты сохранены. Текущие WARE/права до cached replay и после ожидания. Sortedvehicle/TT/ST locks, rereread planned/unbilled/date under locks. Source hash includes cargo exactUOM/pack/mass. Late capacity failure after original unassign must rollback both assignments+reason; concurrent source mutation rejected; stale version one winner; exact operation replay independent of later binding, collision actualJSON rejected. CASE/fact/activeLOADED-DEPARTED prohibited. History immutable/cursor<=50/currentWare; originalSTregister+sameDayReview snapshot versions; source date vsactual target separately. Browser durable beforefetch/reload/authswitch/oldpending command. No stock writer/no false departure/closed day. Author2pallet48EA source33571Nov3->Nov4/P20H20; independent tests not yet executed.\n"
out["db/migrations/2026-10-11_ni072_st_defer/003_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-276-unpicked-st-deferral'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Atomic original unpicked ST reassignment and immutable reason',sysdate,user,
'db/migrations/2026-10-11_ni072_st_defer/002_api.sql','db/migrations/2026-10-11_ni072_st_defer/rollback.sql','APPLIED',
'Original unassign/validated assign one UOW; currentWARE/version/cargo hash/sorted locks; actualSAP2046 two planned48EA Nov3-Nov4; outerrollback/concurrent winner/replay/collision/P20H20. No stock/physicaldispatch/fullNS58 acceptance.');
commit;
"""
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");out[str(p)]=p.read_text(encoding="utf-8").replace("<th>Корневое место погрузки</th>","<th>Корневое место погрузки</th><th>Перенос</th>")
print(json.dumps(out,ensure_ascii=True))
