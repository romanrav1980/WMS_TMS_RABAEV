from pathlib import Path
import json
out={}
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Общая сверка исполнения](components/nicora_ni072_reconciliation_20261010.md):116 current consistent Oracle snapshot/day-aware facts/current queues/P-H-unit conflicts/ERP pending, no writes/day close.\n- [Часовые пояса Oracle и дневные факты](incidents/oracle_naive_timestamps_20261010.md): server−04/session+03/DB+00; naive fields excluded from daily counts, actual TZ facts used.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:116 read-only consistent Oracle snapshot joins exact current warehouse/day-aware actual load/store/returns/finance/tare and current tasks/returns/discrepancies/tare/expenses/current P-H/unit composition/source ERP statuses. Actual bound reader/Tbilisi20:00UTC day/loaded1/store1/no expense allocation pending/EXPORTED still10ERP obligations/current units0/no goods/foreign403/invalidzone422 PASS2f1a672158. Oracle timezone engine reused because local Python tzdata absent; no extra dependency/server clock assumption. SQL21.789/12.276/9.140/6.507ms retain scoped source indexes/current snapshot grouping, finance owner at growing volume. Full regulatory reconciliation and day closure remain."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni07_2.md","Ticket116: [общая сверка](../../../../components/nicora_ni072_reconciliation_20261010.md), single read-only snapshot/day-aware facts/current physical/return/tare/finance backlog/P-H/units/source ERP pending, actual current bound reader no writes. Regulatory linkage/full closure/operating-day work-start aggregation remain open.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/components/nicora_ni072_reconciliation_20261010.md"]="""# NI07.2 — общая сверка исполнения,116
Finance read model; no DDL or stock mutation. Single Oracle READ ONLY transaction snapshot, current warehouse/current transport_dispatch_view. Native Oracle timezone engine converts selected local day/IANA region to exact UTC interval; no external Python tzdata required. Daily immutable timezone-aware facts: loaded/departed places/trips/store receipts/return receipts/finance reports and warehouse costs/tare operations. Source scopes preserved, no sum of physical quantities across profiles.

Current backlog separately counts warehouse tasks/return placement/supplier handover/disposal/delivery case/tare offers/loss/expenses and distribution. Current P/H grouped in exact BASE units/invalid quantity rows; tracked physical units with current positive or tracked composition checked once, SKU multiple profiles never multiply physical quantity. This advisory report does not replace Root's authoritative command checks or external regulatory acknowledgement.

Source-linked existing SAP queue groups statuses; pending and EXPORTED unacknowledged remain outstanding. Supplier queue maps receipt IDs, finance maps expense IDs or warehouse payload. Events without provable source warehouse are not guessed; complete ERP source taxonomy remains later slice. No day closure endpoint or implicit stock correction. Operating-day work-start aggregates, full government lifecycle reconciliation and independent closure remain open.

day-reconciliation.html separates daily facts, current open obligations, current stock and ERP response; links existing handling pages. API timezone defaultAsia/Tbilisi explicit in response, operator may query another region. Legacy naive timestamps excluded from daily counts; current tasks unaffected. [[incidents/oracle_naive_timestamps_20261010]].

[Author case](../../scripts/ni072_reconciliation_case.py) PASS2f1a672158: warehouse2378876 bound non-admin/Tbilisi day10Oct UTC9Oct20→10Oct20, original loaded/store1, expense allocations pending0/current stock physical unit conflicts0; existing EXPORTED still ERP obligation and source current total10. Foreign warehouse403/unknown timezone422/no goods event. Source delivery discrepancy1 correctly visible, not hidden by finance approval. Actor retired.
SQL21.789/12.276/9.140/6.507ms: retain scoped source indexes/current grouping; finance owner checks current-stock/source history plans at growing volume. No full sprint or independent acceptance claim.
"""
out["wiki/incidents/oracle_naive_timestamps_20261010.md"]="""# Oracle naive timestamps and day reconciliation
Observed10Oct2026: SESSIONTIMEZONE+03:00, DBTIMEZONE+00:00, SYSTIMESTAMP−04:00. Actual UTC clocks agree; this is timezone representation difference. TIMESTAMP columns populated fromSYSTIMESTAMP retain local wall time without zone. They cannot be silently treated as API session timezone.

RRL_STOCK_OPERATION.CREATED_AT/APPLIED_AT and legacy warehouse task CREATED_AT/STARTED_AT/FINISHED_AT are naive. New warehouse STARTED_AT_INSTANT and modern physical load/store/returns/tare/finance facts are timezone-aware.116 daily report only uses proven timezone-aware facts; stock/tasks/current backlog remains current snapshot, no guessed historical conversion. Native Oracle TZR handles regional day boundaries and invalid region422.

Do not backfill ambiguous historical naive rows with current timestamp/offset. Future owner inventory/resources/integrations should introduce verified source instants and business warehouse timezone policy; historical rows without source remain explicitly unresolved. Existing legacy SYSDATE expiry/day calculations require separate warehouse timezone review before operational-day closure. No clock/VM/schema reset was performed.
"""
out["задания на проведения тестов/NI07.2/116_общая_сверка.md"]="""# Qwen — NI07.2,116
Own current bound warehouse reader; exact selected date/timezone including DST/invalid region. One READ ONLY consistent snapshot, no goods effect.
Daily timezone-aware source counts versus current backlog/stock explicit. Crosswarehouse denied. Modern source loaded/store/return/finance/tare identities reused.
ERP EXPORTED without real ACK still pending, rejected separately; no inferred SAP/regulatory success. Physical units counted once across profiles, current P/H/unit mismatches visible. No day close or stock UPDATE.
Validate legacy naive timestamp source exclusions and operational-day start limitation, exact source warehouse mapping/bounds/SQL. Independent evidence; do not rerun consumed source fixtures.
"""
print(json.dumps(out,ensure_ascii=True))
