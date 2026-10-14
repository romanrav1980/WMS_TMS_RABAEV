from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8")
d="db/migrations/2026-10-13_ni072_case_wait/"
files={}
p=d+"002_case_wait.sql";body=read(p)
needle="  if tid is null then return;end if;\n  select RESOLVED_PLAN_JSON"
assert body.count(needle)==1
body=body.replace(needle,"""  if tid is null then return;end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=op or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20886,'DEFER_CASE_ROOT_POSTING_REQUIRED');end if;
  select RESOLVED_PLAN_JSON""")
needle="  update RRL_CUSTOMER_ORDER_FULFILLMENT set"
body=body.replace(needle,"""  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(frozen.get_number('fulfillment_id'))));
"""+needle)
needle="  insert into RRL_WAREHOUSE_TASK_SYNC"
body=body.replace(needle,"""  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK_SYNC',RRL_STOCK_PLAN_HELPER.decimal_text(sync_id)));
"""+needle)
files[p]=body
files[d+"009_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-004-ni072-case-waiting'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Standalone prepared CASE waiting task through existing CASE_CARRIER_MOVE root with exact owned lots/reservations and same-transaction completion','"""+"'"+"""||null, user,'apply.sql','rollback.sql','APPLIED');
/
"""
# Use the established migration ledger columns and DATE type.
files[d+"009_ledger.sql"]=files[d+"009_ledger.sql"].replace("'"+ "'||null, user","sysdate,user")
page="""# NI07.2 — подготовленный CASE в ожидание, 953–954

PREPARED, live apply ещё не выполнен. RABAEV/orcl. Migration2026-10-13-004-ni072-case-waiting.

Добавляется nullable CASE_TASK_ID к существующему append-only RRL_ST_DEFER_WAIT_PLAN. Старые FULLPAL-планы сохраняются. Для первой поддержанной ветви: один ST-member, один связанный завершённый CASE и один PICKED fulfillment; до200 физических партий, каждая полностью зарезервирована тем же заказом. Количества разных артикулов/единиц не суммируются: само задание1CASE, партии хранят собственные quantity/base. NestedCASE, ресурсный сеанс, опубликованные slots и ограничения высоты/массы требуют отдельного плана и отказа.

RRL_ST_DEFER_PHYSICAL сначала обнаруживает физический CASE, включая случай без скалярного FACT_QTY, и формирует PREPARED_CASE. Переназначение ST использует прежний RRL_TRANSPORT_PLAN_API; только подготовленный source snapshot допускает CASE. Существующий plan_waiting регистрирует PUTAWAY/MANUAL/ST_DEFER_CASE и immutable origin в прежних WAIT_RUN/WAIT_PLAN.

Task completion bridge выбирает существующую CASE_CARRIER_MOVE по зарегистрированному CASE_TASK_ID. В metadata сохраняются physical_task_id, исходный content_version из плана, сканы исходника/приёмника/CASE и quantity1. Root проверяет текущий warehouse_task_execute/scope/assignee до cached replay и после получения locks. CASE_CARRIER_MOVE декларирует WHT/WAIT_PLAN/RUN/decision/ST/FF/trip/config/sync resources вместе с прежними lot/reservation/units locks, перечитывает frozen source до перемещения. Обычная storage-ячейка разрешается только typed waiting task.

Все партии перемещает прежний TRANSFER_CORE в одной Root транзакции: сохраняет UID/количество/HARD/состав маркировки. CASE CURRENT_CELL/content_version, fulfillment picked version, WHT DONE/FACT1 и SYNCED меняются в этой же транзакции; обязательный Root outbox остаётся прежним. Исходные pick events/facts не переписываются, старый QC допуск по старой версии требует повторного контроля.

Capture948/949 + SHA manifest/checkpoint + paired rollback, без копииБД. Rollback отказывается при зарегистрированных CASE планах; не испытан. Сначала compile/current native scenario, затем actual own-fixture flow и slow SQL решение. ПолныйNI07.2 не объявляется завершённым.
"""
files["wiki/database/retailcase_ni072_case_wait_20261013.md"]=page
p="wiki/index.md";files[p]="- [NI07.2 CASE ожидание953](database/retailcase_ni072_case_wait_20261013.md): prepared additive CASE_TASK_ID/existing CASE_CARRIER_MOVE + WHT same TX, live pending.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint954 PREPARED CASEwaiting migration953/helper/nativeAPI/root/bridge; captured948949/proportional rollback/SHA, no DB copy. Current exact source and root resources, actual apply pending.\n"
p=d+"checkpoint.json";v=json.loads(read(p));v["sha256"].update({p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()});files[p]=json.dumps(v,indent=2)
print(json.dumps(files,ensure_ascii=True))
