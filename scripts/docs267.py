from pathlib import Path
import json
out={}
out["wiki/database/nicora_ni022_erp_admission_20261011.md"]="""# Решение ERP по допуску исходного заказа
267 APPLIED RABAEV/orcl. RRL_SAP_STORE_DECISION — неизменяемый журнал; RRL_SAP_STORE_ADMISSION_API — единственный исполнитель изменения допуска. Предполагаемый WarehouseCustomerOrderDecision version1 содержит Sender/MessageId/DecisionId/OrderNumber/OriginalContentHash/ExpectedVersion/Decision/Reason/Reference. Это согласуемый XML шлюза, не объявленный стандартный IDoc SAP.

ACCEPT разрешён только для PENDING_LATE/PENDING_CALENDAR, действующего открытого календаря с прежним смещением UTC и ещё не истёкшего срока окончания отбора. REJECT отменяет только источник до начала исполнения. Наличие подготовки СТ, действующего плана, исполнения или резерва запрещает изменение. Исходные количества, даты, raw XML и результат первого импорта сохраняются. Поэтому старый импорт может возвращать первоначальный PENDING_CALENDAR, а отдельное текущее состояние уже ACCEPTED. Повтор решения возвращает сохранённый результат; новое содержимое под прежним MessageId или повтор DecisionId с другим MessageId отвергается.

Текущий активный actor/right/WARE проверяется до кэша и после ожидания. METADATA CONFIG6 предшествует CO и SAP source row locks; журнал и оба состояния обновляются одной транзакцией без внутреннего commit. Native кэш дополнительно сравнивает фактические raw XML/код/версию/хэш источника/reason/reference, поэтому поддельный заявленный payload_hash не маскирует другое содержание. Прямые изменения ADMISSION и удаление журнала запрещены. Stock writer не вызывается.

Единое native delivery_rule используется импортом и прежней подготовкой СТ; исходный pick guard требует текущего открытого календаря. Служебный SAP_FILE_GATEWAY получает только дополнительное sap_store_decision_import, всего пять SAP-source прав без UI/приёмки/подготовки СТ. Existing worker поддерживает kind store-decision и exchange/sap_store_decisions. В существующем customer-orders.html добавлены отдельный список источников, текущий допуск/версия, исходная потребность и импорт исходного файла.

Авторский case267 использовал только два уже существовавших источника264: заказ2044 ACCEPTED/v1, заказ2045 REJECTED/v1/CANCELLED, по1 единице исходной потребности. Native rollback, конкурентные HTTP202/409, неизменяемый повтор через реального служебного actor и существующий файловый worker, запреты прямой записи и body collision подтверждены. Дополнительный case267_replay_boundary подтвердил forged native reason/reference/raw с прежним payload_hash и лишние поля отвергаются; точный HTTP replay202. P20/H20 защищённого склада неизменны; новых источников, СТ, резервов и запасов нет. Это локальные XML-пробы, не реальный SAP ACK и не независимая приёмка Qwen.

Native все VALID. SQL decision PK lookup: 0.577/0.964/0.653ms; первая компиляция34.977ms. Решение owner fulfillment: сохранить уникальные source/message и source/version ключи, ограниченный detail; новый индекс или cache не нужен. Архитектура594 файлов/0 циклов/76 зарегистрированного долга. Canonical manifest267 и generated bundle отражают новые схемы/guards/roles; bundle целиком на ACTIVE не применять. Rollback запрещён при непустом журнале решений и не удаляет историю.
"""
items=[
("wiki/index.md","- [Решения ERP по исходным заказам](database/nicora_ni022_erp_admission_20261011.md):267 native atomic admission/rejection, immutable source demand, file gateway and current worklist."),
("wiki/log.md","2026-10-11:267 ERP admission/rejection native journal/current actor-WARE/CONFIG6 then CO+source/current native calendar and deadline/planning-reservation freeze. Two original264 sources only:2044 ACCEPTED/v1,2045 REJECTED/v1,qty1 unchanged; concurrent202-409/rollback/exact service-file replay/native forged declaredhash denied/direct guards/P20H20. No realSAPACK/independent acceptance. NativeVALID/594files0cycles76debt/PK SQL<1ms steady, retain bounded keys ownerfulfillment."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni02_2.md","11.10.2026:267 explicit ERP ACCEPT/REJECT through immutable native journal/current calendar+deadline/version/sourcehash/planning freeze. Existing two264 sources used, initial import result preserved separately from current admission. Existing gateway kind store-decision and raw current source UI. No stock changes or realERP network ACK."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni02_1.md","11.10.2026:267 original ST preparation now uses same native current calendar as SAP source import/decision and preserves saved preparation replay. Admission source2044 now accepted but ST not prepared yet; actual logistics parameters and original writers remain required.")
]
for path,line in items:
 out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/runbooks/nicora_active_work.md")
text=p.read_text(encoding="utf-8").replace("Native manifest259:","Native manifest267:").replace("App261/APIserv261,","App267/APIserv267b,")
text+="\nLatest267 source2044 ACCEPTED/v1 and2045 REJECTED/v1, original qty1/times/import result retained; tmp/context267.json. No newsource/stock/ST. Service has5SAPsource rights, decisionworker and sourceworklist ready. NativeVALID/cache forged declaredhash protection passed. Do not rerun case267 initial state or duplicate source creation; next connect accepted source to original preparation with actual legacy logistics data.\n"
out[str(p)]=text
out["wiki/index.md"]=out["wiki/index.md"].replace("current native259/app261/","current native267/app267/")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"] if x["id"]=="NI02.2").setdefault("implementedSlices",[]).append("267 native versioned ERP source ACCEPT/REJECT/current calendar and deadline/frozen planning/immutable original demand/existing gateway/current source UI")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI02.2"/"267_erp_admission.md")]="# Qwen:267 — решение ERP\nПроверить точный replay и коллизию MessageId/DecisionId, source hash/version/current actor-WARE до кэша и после ожидания; native actual material comparison даже с поддельным payload_hash. Конкурентные решения expected0: один успех, один конфликт. Общий календарь/UTC offset/deadline и запрет после ST/plan/fulfillment/reservation. Atomic rollback сохраняет source и журнал. Исходная потребность/даты/raw/первый import result не меняются. Список показывает текущее состояние отдельно. Прямые записи/удаление запрещены. Worker store-decision архивирует один исходный файл и повторяет прежний результат. Авторские context267 уже version1: не повторять setup как version0, создавать изолированные тестовые данные. Отдельно реальный SAP контракт и независимая приёмка пока не подтверждены.\n"
out["db/migrations/2026-10-11_ni022_admission/007_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-267-erp-source-admission'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Versioned ERP source admission and rejection without rewriting source demand',sysdate,user,
'db/migrations/2026-10-11_ni022_admission/apply.sql','db/migrations/2026-10-11_ni022_admission/rollback.sql','APPLIED',
'Two original264 sources only/atomic rollback/concurrent202-409/immutable exact replay/forged declaredhash refused/current calendar-deadline-planning freeze/raw source retained/no stock/source birth/P20H20/nativeVALID. Local gateway result is not real SAP acknowledgment.');
commit;
"""
print(json.dumps(out,ensure_ascii=True))
