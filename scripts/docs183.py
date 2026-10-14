from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_weight_box_dimensions")
out[str(f/"002_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-183-physical-box-dimensions'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Per-physical-unit declared gross KG, volume, measurement reference and original GS1 label; exact net quantity unchanged',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_dimensions/apply.sql','db/migrations/2026-10-11_ni042_weight_box_dimensions/rollback.sql','APPLIED',
'Own weighted marked4.25KG/4.5gross/.03volume/code1/no legal ACK; own marked CASE1056 actual9.8KG/gross10.1/.03volume/current unit QR/no-QR409/replay/composition evidence/native cleanup; original135 P20H20 unchanged; additive columns/constraint/recompile0errors');
commit;
"""
p=f/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8")+"@@002_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["additional_scripts"].append("../2026-10-11_ni042_weight_box_dimensions/001_schema.sql")
for values in m.values():
 if isinstance(values,dict)and "RRL_WMS_RECEIPT_UNIT"in values:
  for name in ["GROSS_WEIGHT_KG","BOX_VOLUME_M3","MEASUREMENT_REFERENCE","WEIGHT_LABEL_SCAN"]:
   if name not in values["RRL_WMS_RECEIPT_UNIT"]:values["RRL_WMS_RECEIPT_UNIT"].append(name)
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_box_dimensions_20261011.md"]="""# NI04.2: фактические размеры маркированной весовой коробки
183 APPLIED. В прежнем RRL_WMS_RECEIPT_UNIT четыре nullable metadata поля: GROSS_WEIGHT_KG, BOX_VOLUME_M3, MEASUREMENT_REFERENCE, WEIGHT_LABEL_SCAN. BASE_QTY остаётся точным label netKG; второго quantity writer нет. Старые единицы сохраняются.
Capture принимает exact decimal strings gross/volume, positive bounded9-scale, gross>=net; явный measurement_reference обязателен при измерении. Источник — объявленное оператором/источником измерение; hardware scale evidence этим не заявлено. Raw GS1 label сохраняется. Nullable dimensions не подменяются средними весами/объёмом; UNKNOWN остаётся UNKNOWN.
ReceivingMarks сохраняет metadata при прежнем staged birth inventory/MES/SAP в одной root transaction. Числа bind Decimal, а не NLS-sensitive string. Реестр composition читает raw label/gross/volume/reference вместе с current unit/original receipt/code/quantity в прежнем READ ONLY snapshot.
scripts/ni042_weight_box_dimensions_case.py: QW183A36508C9/WEIGHT183.BIRTH:a36508c9 P4.25KG/H0/one physical box/one CRPT profile code, actual gross4.5/volume.03. Exact replay/duplicate refused/native count cleanup/original13520/20.
scripts/ni042_marked_weighted_case.py: own wave416/CASE1056/QM183E20F14B349/CASE.WEIGHT182:1056. Actual19.6KG/two physical boxes -> current reserved9.8KG onebox via existing CASE. No applicable QR409; matched CRPT unit identity allowed; exact replay/changed409. Gross10.1/volume.03/rawlabel remained on moved same physical unit, existing composition API shows10.1. Native carrier return/tare cancel/wave finish/count cleanup, history retained/original13520/20.
Synthetic CRPT signature in author fixture is not validated legal permission or actual government ACK. Only technical physical identity, preservation and profile requirement are proven.
Fresh additive checkpoint/paired guarded rollback; historical measurement evidence prevents column removal. Live application6 statements0errors/recompile; architecture541/0cycles/76existing debt PASS. Broad quality gate remained PASS182, no independent Qwen acceptance inferred.
Remaining: exact physical-box volume admission/replenishment, real scale stations/stability and order tolerance/last box. Full NI04.2 in_progress.
"""
for path,line in [
 ("wiki/index.md","- [Брутто, объём и маркированная весовая коробка](database/nicora_ni042_box_dimensions_20261011.md):183 existing physical metadata, exact4.25/4.5 and marked CASE9.8/gross10.1/current QR/composition/native cleanup; hardware/external ACK separate."),
 ("wiki/log.md","2026-10-11:183 APPLIED: additive physical-box gross/volume/source/raw GS1, exact Decimal binds/existing composition read. Author marked birth4.25/4.5 and marked CASE1056 9.8/gross10.1 passed, no-QR409/native cleanup. Architecture541/0/76; scale/volume admission pending."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:183 per-physical-box gross/volume/reference/raw label and existing composition read delivered. Actual marked birth4.25net/4.5gross and CASE9.8net/10.1gross/QR requirement/preserved physical identity/replay/native cleanup. Hardware stability/tolerance/lastbox/capacity remain open."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni04_3.md","11.10.2026:183 marked weighted physical unit retains one CRPT identity plus exact net/gross/dimensions through existing CASE movement, current QR required; synthetic signatures not government ACK. Regulatory external acceptance remains open.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"183_marked_box_dimensions.md")]="""# Qwen:183
Run scripts/ni042_weight_box_dimensions_case.py and scripts/ni042_marked_weighted_case.py with fresh owned tags. Confirm4.25net/4.5gross/.03volume and9.8net/10.1gross CASE, one physical unit/one current QR; no-QR409/duplicate/refusal/replay. Original GS1 label and measurement reference retained in composition. All cleanup native, original135 P20/H20. Reject gross below net, missing measurement reference, NaN/negative volume/overflow/float inputs. Claimed manual source is not hardware scale evidence, synthetic CRPT signature not legal ACK. Capacity fixture deliberately no volume cap; exact variable-box admission remains pending.
"""
out[str(f/"installed_sources.json")]=json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest().upper()for p in f.glob("*.sql")},indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
