from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8")
before=read("tmp/924_scope_body.sql")
old="('customer_order_view','sap_store_order_import','customer_order_import','sap_store_decision_import','sap_supply_import')"
assert before.count(old)==1
after=before.replace(old,"('customer_order_view','customer_fulfillment_view','sap_store_order_import','customer_order_import','sap_store_decision_import','sap_supply_import')")
mid="2026-10-13-925-ni033-order-execution-scope";d="db/migrations/2026-10-13_ni033_order_execution_scope/"
files={d+"000_before.sql":before,d+"001_scope.sql":after,d+"apply.sql":"@@001_scope.sql\n@@002_ledger.sql\n",d+"rollback.sql":f"@@000_before.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='{mid}';\n/\n",
d+"002_ledger.sql":f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing current warehouse read scope for customer fulfillment view; no source write permission expansion',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",
d+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STORE_ORDER_SCOPE';\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STORE_ORDER_SCOPE';\n",
d+"checkpoint.json":json.dumps({"migration_id":mid,"target":"RABAEV/orcl","state":"PREPARED","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"after_sha256":hashlib.sha256(after.encode()).hexdigest()},indent=2)}
page="""# NI03.3: фактическое исполнение исходного заказа

922/925 PREPARED. Existing OrderExecution считает CASE+FULLPAL физические факты отдельно от подготовленныхСТ, bounded2000 lines/exact native numbers. Найден confirmed gap: header и строки читались через независимые connection snapshots и без current native warehouse. Новый get(order,actor) объединяет metadata/scope/header/facts в одну READ ONLY transaction. Existing RRL_STORE_ORDER_SCOPE.assert_scope использует active RUSERS/current WARE/GLOBAL_ADMIN/current customer_fulfillment_view.925 расширяет только whitelist этой read permission; begin_source whitelist и все writes/locks не меняются. Первыйread923 отказал admin на старом whitelist, не PASS; live caller inspected924, source/SHA/paired rollback saved.

API передаёт authenticated username и mapping403. Source quantities/CASE facts/old journals не изменяются. UI order-execution имеет scope(API/actor)/generation/currentorder guards, clears old quantities whileloading/authchange, понятные статусы; подготовленнаяСТ по-прежнему не означает PICKED. API oldJSON fields preserved +warehouse_id/consistent_snapshot. Старый trusted internal get безactor заменён явным actor; исторические case scripts не запускать без адаптации.

[Migration](../../db/migrations/2026-10-13_ni033_order_execution_scope/apply.sql). Apply/livepositive/scope/slowSQL pending, root stockACTIVE unchanged. Не закрытие NI03.3/независимых терминалов.
"""
files["wiki/database/nicora_ni033_order_execution_20261013.md"]=page
files["wiki/index.md"]="- [NI03.3 execution925](database/nicora_ni033_order_execution_20261013.md): prepared current native order/warehouse/single readonly snapshot; quantity writer unchanged.\n"+read("wiki/index.md")
files["wiki/log.md"]=read("wiki/log.md")+"\n- 2026-10-13 prepared925 orderexecution922 currentactor/single READONLY/header+physicalfacts. Old nativewhitelist refused923 admin; capture924 extends onlyread customer_fulfillment_view, writes untouched. SHA/pairedrollback, livepending.\n"
print(json.dumps(files,ensure_ascii=True))
