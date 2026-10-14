from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-12_ni071_period_policy")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text())
for key,files in [("startup_scripts",["001_schema.sql"]),("additional_scripts",["002_policy_guard.sql","003_cost_guard.sql"])]:
 for file in files:
  value="../"+d.name+"/"+file
  if value not in m[key]:m[key].append(value)
for table,cols in {"RRL_LOGISTICS_COST_LINE":["RATE_DATE","PERIOD_MODE","PERIOD_TIME_ZONE","PERIOD_POLICY_VERSION"],"RRL_LOG_COST_PERIOD_HEAD":["WARE_ID","VERSION_NO"],"RRL_LOG_COST_PERIOD_HISTORY":["WARE_ID","VERSION_NO","OPERATION_ID","PERIOD_MODE","TIME_ZONE","RESULT_JSON"]}.items():
 target=m["required_columns"].setdefault(table,[])
 for col in cols:
  if col not in target:target.append(col)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
before=Path("db/migrations/2026-10-10_ni071_box_cost/002_guards.sql").read_text()
out[(d/"000_before_cost_guard.sql").as_posix()]=before[before.index("create or replace trigger RRL_LOG_COST_LINE_GUARD"):]
out[(d/"rollback.sql").as_posix()]="""declare n number;begin
 select count(*)into n from RRL_LOG_COST_PERIOD_HISTORY;if n>0 then raise_application_error(-20899,'FINANCIAL_PERIOD_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;
 select count(*)into n from RRL_LOGISTICS_COST_LINE where PERIOD_MODE is not null;if n>0 then raise_application_error(-20899,'FINANCIAL_PERIOD_CHARGE_REQUIRES_FORWARD_RECOVERY');end if;
end;
/
@@000_before_cost_guard.sql
drop trigger RRL_LOG_COST_PERIOD_HEAD_G;
drop trigger RRL_LOG_COST_PERIOD_HISTORY_G;
drop table RRL_LOG_COST_PERIOD_HISTORY;
drop table RRL_LOG_COST_PERIOD_HEAD;
"""
page="wiki/database/nicora_ni071_assembly_period_20261012.md"
out[page]="""# Источник и настройка расчётного периода
362–365, миграция2026-10-12-363-warehouse-financial-period APPLIED RABAEV/orcl, all current objects VALID. Это продолжение прежнего BOX cost run/lines и invoice. Количества и проводки товара не затронуты.

GET /api/finance/logistics-costs/trips/{id}/assembly-period?warehouse_id=&timezone_region= читает APPLIED frozen loads в одном readonly snapshot, до200 мест/200nodes/10000коробок, CASEclock batch500. Возвращает actualinstant/businessdate либо MISSING_ACTUAL_START/ASSEMBLY_SOURCE_NOT_LINKED. Обычной BOX пока не приписывается CASEclock. LegacyCASE1112 реально имеет naiveSTARTED_AT и NULLTSTZ: INCOMPLETE. Неверный регион422. Старый финансовый receipt357 неизменён.

GET/POST warehouses/{id}/period-policy: существующие transport_dispatch_view/create_tt_price, current RUSERS/WARE до replay и после rowlock. Head WAREPK/version0 defaultLOADED_UTC, nullable zone; immutable historyversion/op/hash/reason/reference. CASE_ASSEMBLY требует явного Oracle region. Пользовательское решение не объявляется подтверждением географии NICORA. Rowanchor0 создаётся для взаимного исключения калькулятора и изменения политики. Setter locks onlyWARE head; calculator locks trip thenWAREhead; setter does not request trip, so no reverse cycle. Idempotent repeat returns historical policy despite newer head; otherpayload rejected. Sameop concurrent recheck afterlock. Current read readonly.

Новые existing BOX начисления фиксируют RATE_DATE/PERIOD_MODE/PERIOD_TIME_ZONE/PERIOD_POLICY_VERSION в прежней COST_LINE и RESULT_JSON. ModeCASE требует exactCASE source каждой физической коробки, sameWARE/TSTZ, одного рабочего дня на грузовое место. Нет времени или несколько дней — отказ без run/lines/outbox. LOADED_UTC сохраняет прежний смысл. Native lineguard сверяет APPLIED load, current policy/history, archivedCASE IDs/fullboxcount/actualclock/date, result proof, latest effective RATE_HISTORY and rounded originaltableamount. Cached original runs не перепроводятся.

Actual364 existing departed SMALL207/trip33533/WARE35944973/CASE1105: policyCASE v1 Asia/Tbilisi -> missingactualstart refusal and zeroCOSTRUN; sameop differentregion conflict. ExplicitpolicyLOADEDUTC v2 -> oldmeasured1BOX2.50 once with actualperiodproof/replay. Actual365 competing version2 decisions ->one v3 and one conflict; retained3history/oldv1repeat; forged native cost date+1 denied20886, trialRUN rolledback. Existing goods/protected20/20 unchanged.

Raw logistics-costs UI: policy read/versioned explicit save using existing durablepending/reason/reference; preview with explicitregion/nocharge; identities/warehouse/trip changes invalidate proof. Case read models expose TSTZ as Oracle offset string (thin datetime tzinfo unreliable).

SQL365 operational historyinsert32.013ms cold and3.294ms warm, boundPKactor3.347ms, CASEclock batch6.873ms. DDL91/84ms excluded. Decision finance: retain indexedWARE/version/op anchors and bounded batches; review plan/batchload case-date lookup for large200-place runs, ownerfinance backlog. No million-operation benchmark claim.

Открыто: positive financialCASE_ASSEMBLY end-to-end on newly assembled physical boxes, ordinaryBOX assembly linkage, several days within one load need separate original cost-line dimensions, othernormativework/realfinancialSAP/independent Qwen. These gaps are not declared complete. Context362/364/365 retained; initial factories prohibited.
"""
for file,text in [
 ("wiki/index.md","- [Настройка расчётного периода и точные источники](database/nicora_ni071_assembly_period_20261012.md):362–365 explicitWAREpolicy/CASEclock/no naive date/currentversion/concurrentwinner/nativeforgeddate refusal; originalBOXcost reused.\n"),
 ("wiki/log.md","\n- 12.10.2026 362–365 NI07.1: readonly CASEclock source/unknown legacytime; versioned explicit financialWAREperiod, shared headlock/currentactor afterwait/replay; native source/date/rate proof. Actual missingstart zerocharge; oldmeasuredCASE1105 loadedUTC2.50 once; two controllers one winner/one409; forged date native20886/fullrollback. UIdurableintent; SQLwarm3.294ms/batch6.873ms boundedPK/financeplan backlog; positive newCASE assemblycharge remains.\n"),
 ("wiki/runbooks/nicora_active_work.md","\nCurrent366: migration363 nativeVALID, contexts362readonly/364oldCASE1105cost2.50/newpolicyWARE35944973 v3/365race. Old357/364 cost receipts remain cached. Next functional recovery consolidation or newphysicalCASE assembly-period positive; no factory207/211/361/365 rerun. RawUI365JS parsed; adminTS356PASS; encoding/architecture next.\n"),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md","\n362–365: explicit versionedWAREperiod LOADEDUTC/CASE_ASSEMBLY with timezone/currentfinance/native exact source/rate/date guard; preview perCASE actualclock and missingdates; concurrencyonewinner/replayhistorical/forgeddate denied. Missingstart nocharge; actualoldCASE1105LOADEDUTC1BOX2.50. Positive newly assembled CASE mode/ordinaryBOX linkage/multi-daydimensions remain.\n")]:
 p=Path(file);old=p.read_text(encoding="utf-8");out[file]=text+old if file=="wiki/index.md"else old+text
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI07.1/366_assembly_period.md").as_posix()]="# Qwen362–365\nReadonly actualclock/Oraclezone/legacyCASE1112INCOMPLETE. VersionedWAREfinancepolicy/headanchor/currentactor afterwait/sameop concurrent recheck. CASE mode missingtimestamp nocharge; differentdays reject; sourceBOXwithoutCASEreject. Actual oldCASE1105loadedUTCcost2.50 frozen v2; policyv3 concurrent one winner/one409; native date+1 trial refused/rollback. Cachedoldcost unchanged. Newly assembled CASE happy path and mixed-dayline extension are still pending, not passed. Contexts362/364/365; do not rerun initial fixtures.\n"
print(json.dumps(out))
