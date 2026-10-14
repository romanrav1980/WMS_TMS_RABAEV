from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for group,names in {"startup_scripts":["001_schema.sql"],"additional_scripts":["002_guards.sql","003_head_guard.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni071_box_cost/"+name
  if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Стоимость физической коробки рейса](database/nicora_ni071_box_cost_20261010.md):111 APPLIED, existing actual BOX1/frozen2.50GEL/v1 despite futurev2/replay/no second charge; original invoices preserved.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:111 new bounded finance module reuses original actual departed physical BOX proofs/load TT and existing billing invoice membership; versioned BOX norm/common work included, immutable charge and unique physical source/currency/costcode. Actual BOX1*2.50GEL/frozenv1 despite future9.00v2/replay/conflict/second denied/no P or carrier PRICE change PASS. Current bound non-admin own/foreign warehouse and original norm retry after new version passed. Cost UI plus small finance feature in existing invoice detail, admin tsc PASS. SQL41.677/15.339/28.269ms retain original load/box PK and bounded200/500. New domain outward dependency fixed; global architecture gate still fails prior debt223/1cycle, baseline unchanged."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md","Ticket111: [ставка физической коробки](../../../../database/nicora_ni071_box_cost_20261010.md), actual departed BOX1/frozen version2.50GEL/replay/no second charge/current warehouse rights; existing billing invoice detail extended via finance feature. Extra expenses/all bases/monthly revision/corrections remain."),
 ("wiki/requirements/nikora_delivery_v55/implementation_plan.md","10.10.2026:110 ordinary disposal through original core/loss original store and111 finance actual physical BOX norm/charge/version preservation delivered. Current functional NI07.1 extra expenses; marked/interwarehouse/other preserved residuals remain explicitly open.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/nicora_ni071_box_cost_20261010.md"]="""# NI07.1 — складская стоимость физической коробки,111
2026-10-10-111-actual-box-warehouse-cost APPLIED10/0 + guards3/0/head1/0 RABAEV/orcl. RRL_LOGISTICS_RATE_HEAD/HISTORY/COST_RUN/COST_LINE and guards valid. Legacy RRL_WARES lacks unique/PK: new warehouse identity validated by exact count, no fictitious FK/schema retrofit. Original failed FK DDL created no table.

Finance module owns pure Decimal rates/cent rounding, typed API port, infrastructure transactions. create_tt_price current warehouse-bound actor sets optimistic norm version/history, monotonically later effective date; original exact norm request can replay version+1 after future head changed, different content refuses. Common work included in BOX picking rate; no second common surcharge in this slice. Rates evaluated on UTC date of actual loading; assembly-start operating-day/monthly recalculation remain future scope.

calc_tt_price current bound actor conducts actual departed loads1..200, requires all container BOX nodes exactly backed by original RRL_TT_LOAD_BOX_WEIGHT proof count, no inferred box conversion. Immutable rates selected latest applicable, TT row locked first, no stock resources; immutable run/lines same short transaction, unique actual load+costcode+currency prevents second charge. Native goods journal unchanged. Frozen original rate/basis/quantity/version/amount retained. Initial COST_CODE WAREHOUSE_PICKING/basis BOX only; currencies separated and original untyped carrier PRICE not overwritten.

logistics-costs.html gives version/rate/actual calculation/durable retry. New finance/BillingWarehouseCosts public feature appears in existing invoice detail, using original TT.PAY_ORDER_ID. Read lines restricted to user warehouse orGLOBAL. No second invoice editor or invented carrier invoice total. Actual invoice source membership shown when existing billing links trip; author did not create/pay invoice.

## Actual author evidence
[Case](../../scripts/ni071_box_cost_case.py) PASS tag09a34d7dec: original departed FULL.HU.SHIP:22c5dc5ec4/trip33514/warehouse2378876 actual BOX1, norm2.50GEL/v1 from2026-01-01, cost2.50, exact retry/conflict/second denied; future9.00/v2 from2027 retained original charge. Original PRICE/PAY_ORDER_ID and goods events unchanged.
[Original continuation](../../scripts/ni071_box_cost_existing_case.py): original norm retry returnsv1 despite currentv2, changed content409, current bound finance user sees own rates/charge and foreign warehouse403. Own user retired.
SQL41.677/15.339/28.269ms: retain load/BOX PK, scoped200loads/500detail, finance owner checks repeated occupied history plan at growth. TypeScript admin PASS. Architecture398files/223debt/1cycle remains FAIL on prior debt; new finance domain→contracts dependency fixed, no threshold/baseline increase. No full finance or independent acceptance claim.

Extra cost articles/approval/distribution, operating-day calculation, monthly norms, currency policy/conversion, financial correcting entries remain open.
"""
out["задания на проведения тестов/NI07.1/111_складская_стоимость_коробки.md"]="""# Qwen — NI07.1,111
Use own actual departed BOX load/proofs and original billing membership. Separate current warehouse finance permissions. Missing departure/proof/rate refuses, no guessed box quantity.
Version norm before/new effective date, exact original norm retry after future version, payload/version conflicts. Calculate quantity*Decimal rate/cent rounding, freeze version and source TT; exact op replay/different payload/second op same source denied.
Different warehouse non-admin denied; original goods journal/carrier PRICE/PAY_ORDER_ID unchanged. Invoice detail displays warehouse lines separately and currencies not summed implicitly. Common work already included in BOX rate. No inferred actual invoice payment or independent acceptance.
Review effective UTC date/assembly operating day limitation; source uniques/VALID/slow query decision. Future extra expenses/monthly/reversal remain explicit.
"""
print(json.dumps(out,ensure_ascii=True))
