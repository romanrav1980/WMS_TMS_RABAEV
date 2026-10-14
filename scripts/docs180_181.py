from pathlib import Path
import json,hashlib
out={}; Path.write_text=lambda self,content,**kwargs: out.__setitem__(str(self),content)
folder=Path("db/migrations/2026-10-11_ni042_sap_task_identity")
ledger="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-181-sap-putaway-identity'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Preserve non-SAP residual task identity; distinguish SAP putaway by immutable pallet UID',sysdate,user,
'db/migrations/2026-10-11_ni042_sap_task_identity/apply.sql','db/migrations/2026-10-11_ni042_sap_task_identity/rollback.sql','APPLIED',
'Fresh original index DDL/checkpoint; replacement built before old removal; live UNIQUE VALID; actual two distinct SAP putaway task facts coexist, weighted ARTMAS/gateway supply/P9.8/unit1/replay; cleanup by existing cancel/native count, no stock DML');
commit;
"""
(folder/"002_ledger.sql").write_text(ledger,encoding="utf-8")
p=folder/"apply.sql";p.write_text(p.read_text(encoding="utf-8")+"@@002_ledger.sql\n",encoding="utf-8")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["additional_scripts"].append("../2026-10-11_ni042_sap_task_identity/001_index.sql");p.write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
p=Path("wiki/database/nicora_ni042_weight_box_sap_20261011.md");p.write_text("""# NI04.2: SAP capture180 и идентичность задания181
180 API сохраняет weighted-box capture в прежнем SAP_RECEIPT. Детерминированный physical key совпадает с inventory/MES; exact KG/одна коробка. Новые optional поля при None исключаются из canonical metadata, прежний immutable replay сохраняется. Маркировка определяется SKU profiles, product-weight label не government ACK.
Живой scripts/ni042_weight_box_sap_case.py: ARTMAS10 KG -> WarehouseSupplyOrder XML/current recipient -> QW180BDDA2C42 / WEIGHT180.RECEIVE:bdda2c42 P9.8KG/H0/unit1/physical_boxes1/marking_units0/NOT_APPLICABLE/replay/PUTAWAY. Cleanup прежним Receiving.cancel + native INVENTORY_COUNT.
Первый запрос500 выявил регрессию старого индекса RRL_WAREHOUSE_TASK_U2 из NI03.2 recovery: все SAP_RECEIPT имели null SOURCE_TASK_ID/SOURCE_MOVEMENT_ID/PARENT_TASK_ID и сталкивались с прежним task827. 181 APPLIED: последняя часть уникального ключа для SAP_RECEIPT — immutable UID_PALLET; остальные источники сохраняют тот же NVL parent identity. Новый UNIQUE индекс построен до удаления старого, переименован в прежнее имя, live VALID. Fresh DDL/checkpoint/guarded rollback; восстановление старого ключа запрещено при нескольких SAP putaway facts. Количество/движения не переписывались.
Первый восстановленный receipt task881 и последующий самостоятельный receipt успешно сосуществуют с историческим827; third fresh run полностью PASS. Авторский cleanup сначала вызвал отсутствующий API route; заменён существующим сервисом. Receiving.cancel/replan также исправлены на общий read_oracle_json для native dict/CLOB, прежний json.loads(dict) давалTypeError. Оба первых own stock fixtures затем сняты штатным native count.
Slow SQL: placement candidate46b9rn96gzagm avg57.474ms/3 (малый холодный sample). Решение: bounded warehouse filtering оставлено; inventory owner должен пакетировать occupancy/reservations по кандидатам и проверить план на реальной топологии в NI08.1 performance backlog. Промышленная производительность не подтверждена.
CASE weighted scanner, marked weighted full profiles, scales и last-box policy ещё не приняты. Полный спринт остаётся открытым.
""",encoding="utf-8")
for path,line in [
 ("wiki/index.md","- [SAP-приёмка весовой коробки и ключ задания](database/nicora_ni042_weight_box_sap_20261011.md):180 actual XML→P9.8/unit1/replay;181 fixes global SAP PUTAWAY collision, non-SAP uniqueness preserved."),
 ("wiki/log.md","2026-10-11:180 SAP weighted capture implemented/native end-to-end PASS;181 SAP putaway identity index APPLIED VALID. Existing JSON reader cancel/replan fixed; own fixtures native cleanup. Placement57.474ms/3 requires owner inventory batching/plan backlog."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:180 SAP weighted-box birth confirmed using actual ARTMAS10+gateway XML/native receipt/unit1/P9.8KG/replay;181 fixes existing SAP putaway unique index. CASE scanner/scale/last-box remaining; sprint in_progress.")]:
 p=Path(path);p.write_text(p.read_text(encoding="utf-8")+"\n"+line+"\n",encoding="utf-8")
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:
 p=roots[0]/"NI04.2"/"180_181_sap_weighted_box.md";p.parent.mkdir(parents=True,exist_ok=True);p.write_text("""# Qwen: 180/181
Run scripts/ni042_weight_box_sap_case.py with isolated tagged ARTMAS10 SKU and warehouse. Confirm XML order recipient/no inventory at import, SAP receipt exact9.8KG/physical unit1/box1/marking0/replay/putaway/native cleanup. Confirm old historical SAP task827 unchanged and distinct new pallets produce distinct putaway tasks. Reject duplicate physical box/wrong net mass/current policy. Inspect RRL_WAREHOUSE_TASK_U2 expression: SAP final key UID_PALLET, non-SAP parent-key semantics unchanged; index VALID. Verify source native JSON dict/CLOB works in cancel/replan. Do not run guarded rollback with historical multiple SAP facts; do not delete them. CASE/scales/marked variants not accepted by this slice.
""",encoding="utf-8")
(folder/"installed_sources.json").write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest().upper()for p in folder.glob("*.sql")},indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,ensure_ascii=True))
