from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni051_physical_box_mass")
out[str(f/"002_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-185-actual-box-quality-mass'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing outgoing QC reads actual physical weighted-box gross masses, half-lightest actual box tolerance; normal SI policy retained',sysdate,user,
'db/migrations/2026-10-11_ni051_physical_box_mass/apply.sql','db/migrations/2026-10-11_ni051_physical_box_mass/rollback.sql','APPLIED',
'Actual marked CASE1059 net9.8/gross10.1/minhalf5.05; mismatched partial9.7 refused; existing closed carrier/ST binding/current independent controller native WEIGHT2 passes/replay, SCAN remains pending; native cleanup/original13520/20; SQL0.701ms/8');
commit;
"""
p=f/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8")+"@@002_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["components"]=[x.replace("../2026-10-10_ni051_weight_policy/002_weight.sql","../2026-10-11_ni051_physical_box_mass/001_weight_contract.sql")for x in m["components"]];out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni051_physical_box_mass_20261011.md"]="""# NI05.1: QC по брутто физических весовых коробок
185 APPLIED: существующий RRL_STOCK_QC_WEIGHT.calculate signature и control caller retained. Для SERIALIZED_WEIGHT_BOXES=1 ожидаемая масса — SUM(actual unit GROSS_WEIGHT_KG), допуск — половина самой лёгкой фактической коробки; отдельно взвешенная тара места вычитается прежним QC caller. Average kg/BASE и QC_BASE_WEIGHT_KG не применяются к этой ветке. Для обычного SKU прежняя SI policy остаётся.
Proof: current UID/one physical registry/nonISSUED/KG, sum(BASE_QTY)=actual leg quantity, full gross>=net, measurement reference/raw weight label, bound10000 units. Частичный leg одной неделимой коробки/неполное evidence отказаны; не создаётся новая масса из среднего веса.
scripts/ni051_physical_box_mass_case.py: own wave419/CASE1059/QM1850DBDAE44CE/actual net9.8/gross10.1. Native calculator gives expected10.1/tolerance5.05; partial9.7 refuses20887. Actual closed carrier and existing KG ST QC185.ST:0dbdae44ce bound by prior mechanism; current own-warehouse independent controller QW1850dbdae44ce confirms native WEIGHT2 gross10.1/wood0 with applicable CRPT identity. Exact replay, verified1/readyfalse: separate SCAN remains required. No real governmental signature/ACK or hardware-scale evidence claimed.
First own author fixture used a16-character USER_GROUP ID; legacy max15 correctly refused. Fixed fixture prefix, first native return/count cleanup succeeded. Second full case PASS; own carrier/tare/wave/count cleanup/history retained, original135 P20H20 unchanged.
Fresh native source/checkpoint/paired rollback, live5 statements0errors and USER_ERRORS empty. SQL actual mass gfq53n2bf0h5j0.701ms/8. Decision: existing current-UID index and10000 bound retained, no extra index; batching beyond supported bounds inventory owner backlog.
Order quantity deviation15%/last-box exception is distinct from measurement accuracy/QC half-box threshold and not changed here. Full NI05.1/NI04.2 independent/equipment/modes remain open.
"""
for path,line in [
 ("wiki/index.md","- [QC по фактическому брутто коробок](database/nicora_ni051_physical_box_mass_20261011.md):185 native expected10.1 for actual net9.8/current independent WEIGHT2/replay; partial-box mass refused, SCAN still required."),
 ("wiki/log.md","2026-10-11:185 APPLIED original QC mass calculator weighted branch actual gross sum/half-lightest physical box. Independent native WEIGHT2 actual10.1 passes, no norm substitute/partial-box forbidden/native cleanup. SQL0.701ms/8 indexed bound retained."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni05_1.md","11.10.2026:185 actual weighted physical-box gross branch replaces normative KG/BASE for serialized weighted SKU in existing QC; current independent controller actual10.1 for9.8 net/replay/partial9.7 refused. Actual half-lightest5.05 unchanged business kind; hardware scale and independent full acceptance separate."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:185 current outgoing QC reads actual gross of weighted physical units; expected10.1 for net9.8 and original independent WEIGHT2 verified. Order tolerance/lastbox/scale stations not conflated with QC accuracy.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI05.1"/"185_actual_box_gross.md")]="""# Qwen:185
Run scripts/ni051_physical_box_mass_case.py with own tag. Verify actual unit net9.8/gross10.1 gives QC expected10.1/tolerance5.05 without normative KG weight; partial9.7 denied. Existing close/bind/current independent controller/WEIGHT2 verified1 and exact replay; readyfalse until SCAN. Native cleanup/original13520/20. Unknown gross/ref/label or mixed/nonKG composition must fail. Ordinary SKU uses original SI policy. This does not confirm real scales, government signature or order15%/last-box exception. Review SQL actual-mass bound/index, no broad stock reset.
"""
out[str(f/"installed_sources.json")]=json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest().upper()for p in f.glob("*.sql")},indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
