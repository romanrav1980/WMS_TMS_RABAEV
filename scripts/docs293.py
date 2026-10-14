from pathlib import Path
import json
out={};base="db/migrations/2026-10-11_ni061_incident_close/"
page="wiki/database/nicora_ni061_incident_close_20261011.md"
out[page]="""# Явное закрытие расследования после полной приёмки
Нативный RRL_INTERWARE_INCIDENT_API.close_case пишет неизменяемое решение в RRL_INTERWARE_INCIDENT_CLOSE. Текущий активный диспетчер склада назначения или GLOBAL_ADMIN проверяется до повтора и после ожидания существующего CFG6. Точный канонический запрос/actor/opID обеспечивают повтор; другой запрос или второе закрытие одного сообщения отклоняются. Причина и подтверждающий документ обязательны.

Основание — исходное сообщение о проблеме, его точная редакция и последующая APPLIED INTERWARE_RECEIVE по тому же плану, исходной паллете и полному количеству, подтверждённая реальным RRL_EVENTS. Частичная291/292 приёмка не является полным восстановлением. Запас, резервы, ответственность рейса, исходное сообщение и государственный ACK этим решением не изменяются. Диспетчер явно закрывает расследование; автоматического закрытия нет.

POST /api/inventory/interwarehouse/incident-closures; история и очередь показывают сохранённое закрытие. Существующий raw interwarehouse UI использует ту же сохранённую команду до HTTP, actor/API scope и повтор с неизменным OPID. Форма выбирает сообщение из пагинированной истории и требует причину/документ.

Фактический dev-кейс293 использовал существующий243 план с полным последующим получением: outer rollback удалил решение; параллельные HTTP200/409 дали одно закрытие; точный повтор вернул результат; изменение запроса отклонено; неверная редакция, SAP_FILE_GATEWAY и receipt292 другого/частичного плана отклонены. История сохранила исходное сообщение и закрытие; protected P20/H20 неизменны. Browser/hardware/независимая приёмка не проведены.

SQL: история ограничена51/50, закрытие по PK incident unique, план/receipt PK; не добавлять cache или глобальную блокировку запаса. CFG6 сериализует только короткие административные решения. Измерения текущих V$SQL отражены в tmp/slow293.json; выбранные запросы сохраняют PK и границы. Полное разрешение действительной частичной недостачи и переход ответственности остаются отдельной работой.
"""
for path,line in [
("wiki/index.md","- [Закрытие расследования после полной приёмки](database/nicora_ni061_incident_close_20261011.md):293 explicitcurrentTargetDispatcher/reason/evidence/native append-only/no stock; old243 full recovery, partial292 refused."),
("wiki/index.md","- [Проект закрытия расследования](database/nicora_ni061_incident_close_design_20261011.md):293 one incident/one closure, full applied receipt required."),
("wiki/log.md","2026-10-11:293 native explicit incident closure/currenttargetscope/canonicalreplay/immutable journal/full applied receipt+event; queue/history/raw durable command. Actual243 full recovery outerrollback/concurrent200-409/replay/collision/partial292 refusal/gateway403/protected20-20. No stock/custody/GovACK change. Actual shortage resolution remains."),
("wiki/runbooks/nicora_active_work.md","LatestNative/app293 explicit recovered incident closure; tmp/context293.json existing243 full followup closed once, preserved history/no stock. Never rerun case293 outerrollback phase after committed closure (use replay/history). Native allVALID/app628/serv293. Current291/292 actualshort2 still unresolved; next explicit disposition/recovered goods using existing core; no broad uniqueness relaxation."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","11.10.2026:293 Явное закрытие сообщения о недостаче после полной приёмки реализовано: обязательные причина/документ, актуальные права склада назначения, проверка реального события, повтор/конкуренция/история. Dev243 закрыт по полной последующей приёмке. Частичная291/292 и ответственность перевозчика остаются открытыми; полная независимая приёмка NI06.1 не объявляется.")
]:out[path]=out.get(path,Path(path).read_text(encoding="utf-8"))+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native292/app292/","current native293/app293/")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("293 explicit full-recovery incident closure/currenttargetscope/immutable evidence/actual243/no stock; partial shortage remains");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["components"].append("../2026-10-11_ni061_incident_close/002_api.sql");j["packages"].append("RRL_INTERWARE_INCIDENT_API");j.setdefault("startup_scripts",[]).append("../2026-10-11_ni061_incident_close/001_schema.sql");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/293_incident_close.md").as_posix()]="""# Qwen:293 закрытие расследования по полной приёмке
Прочитать wiki/database/nicora_ni061_incident_close_20261011.md и tmp/context293.json. Не создавать снова243/291/292 источники и не менять protected6667491.
1. Повторить сохранённую293 HTTP-команду: тот же результат, одна строка журнала.
2. Новый OPID для уже закрытого сообщения:409. Содержимое с прежним OPID изменить:409.
3. Под SAP_FILE_GATEWAY запрет; текущий склад и права после ожидания проверяются.
4. Новый незакрытый собственный fixture: неверная редакция, чужой план, partial receipt, отсутствие applied event/полного количества не закрывают сообщение. Outer rollback не оставляет решение.
5. Browser: history pagination/currentauth/pending recovery/exact retry/reason/evidence. Closed history immutable, no stock/custody/GovACK altered.
Отчёт различает реальные проверки, статический анализ и непроведённые случаи; не объявлять весь NI06.1 завершённым.
"""
out[base+"003_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-293-interware-incident-close'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Explicit incident closure after full actual interwarehouse receipt',sysdate,user,'db/migrations/2026-10-11_ni061_incident_close/001_schema.sql','db/migrations/2026-10-11_ni061_incident_close/rollback.sql','APPLIED','Current target dispatcher, immutable evidence/canonical replay; full receipt+APPLIED event. Existing243 recovery/rollback/race/replay; partial292 blocked. No stock or custody change.');
commit;
"""
out[base+"rollback.sql"]="""declare n number;begin
 select count(*)into n from RRL_INTERWARE_INCIDENT_CLOSE;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_INCIDENT_CLOSURES');end if;
end;
/
drop trigger RRL_INTERWARE_INCIDENT_CLOSE_G;
drop package RRL_INTERWARE_INCIDENT_API;
-- Keep empty additive table for current read projections; revert API/UI before dropping schema.
"""
print(json.dumps(out,ensure_ascii=True))
