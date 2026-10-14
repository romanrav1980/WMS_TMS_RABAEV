from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_small_final_weight")
out[str(f/"010_context.sql")]="create context RRL_PALLET_TYPE_CTX using RRL_PALLET_TYPE_API;\n"
out[str(f/"011_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-202-small-box-final-weight'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Per-carrier type mandatory child final weight with existing QC owner',sysdate,user,
'db/migrations/2026-10-11_ni042_small_final_weight/apply.sql','db/migrations/2026-10-11_ni042_small_final_weight/rollback.sql','APPLIED',
'Own QPB202E0AA707B small type7/customer-specific CASE6/original warehouse NONE but child WEIGHT; measured gross.400/wood.100/net.300/native QC/replay/source14 unchanged. Precise DTO/version/old omission preserveflag/rawwrite20863/current owner. Addressed hardware archive next; no measured-reference claim.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@011_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
# Locate the original QC policy component by its source content, not a guessed filename.
root=p.parent
policy=[x for x in m["components"]if "create or replace package RRL_STOCK_QC_POLICY" in (root/x).read_text(encoding="utf-8")]
assert len(policy)==1,policy
m["components"]=[x.replace(policy[0],"../2026-10-11_ni042_small_final_weight/004_policy.sql").replace("../2026-10-10_ni042_composition_epoch/007_qc_gate.sql","../2026-10-11_ni042_small_final_weight/005_gate.sql")for x in m["components"]]
m["components"].append("../2026-10-11_ni042_small_final_weight/002_recompile_api.sql");m["packages"].append("RRL_PALLET_TYPE_API")
m["startup_scripts"].extend(["../2026-10-11_ni042_small_final_weight/001_schema.sql","../2026-10-11_ni042_small_final_weight/007_version.sql"])
m["additional_scripts"].extend(["../2026-10-11_ni042_small_final_weight/010_context.sql","../2026-10-11_ni042_small_final_weight/003_guard.sql"])
m["required_columns"]["RRL_PALLET_TYPE"]=["PALLET_TYPE_ID","FINAL_WEIGHT_REQUIRED","TYPE_VERSION"];out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_small_final_weight_20261011.md"]="""# NI04.2: обязательный финальный вес отдельной коробки
202 APPLIED. [[retailcase_ni042_small_final_weight_design_20261011]]. Existing global RRL_PALLET_TYPE now FINAL_WEIGHT_REQUIRED default0 and TYPE_VERSION1+. Existing CASE QC policy upgrades NONE/ANY→WEIGHT, SCAN→BOTH only for specific child; parent/warehouse exemption cannot approve child without its own current weight proof. Existing root QC/current content signature/journal gross/wood/net remain authoritative. No reference weight claimed measured.
Legacy pallet-type URI/DTO/service preserved through passive public contracts barrel and inventory metadata adapter. Physical numeric fields Decimal, native exact JSON→NUMBER, expected_version conflict; changing final requirement needs explicit current version, old client omission preservesflag. Native currentactive RUSERS/case_pick_manage/business CONFIG X+metadata anchor/own TYPE/TX/actor context guardsflag, no stock context or config-right widening. Existing actor caller now authenticated user, no updated_by spoof. Raw management module exposes type/reference fields/mandatory checkbox/current version; unknown save outcome requires refreshed card, no blind duplicate edit.
Own QPB202E0AA707B/type7/isolated cloned customer/currentCASE6: original SAP20/sourceDIRECT, source14 remains. WARE mode NONE still CASE QC required WEIGHT and initiallynotready. Current configured EA reference.05 and actual controller gross.400/wood.100 → net.300/currentQC/replay ready; archived TRIAL_WEIGHT/WOOD_WEIGHT exact, tare counted once. No scale hardware commissioning or addressed packet yet.
First small-type metadata assert incorrectly treated CONFIG mode6 as resource rank6; corrected assert_policy(CONFIG,6), original held ROW20 retained. Initial MERGE PL/SQL variable names width/height/active shadowed SQL columns, prefixed current variables. DDL invalidated tare/QC bodies: recompiled explicit four plus policy; current USER_ERRORS clear/VALID. Legacy DTO extraction first imported private contract, corrected passive public barrel/tightened decreased debt; architecture551/0cycles/76debt. Full quality gate24 architecture/tooling cases and bothTS checks; raw JS syntax/encoding separately.
Native type upsert9mqfjx89qvs7v11.397ms4; retain type/code keys/short rare metadata fence; inventory owner bulk read/plan review before large type history. 201 markedDIRECT proof source unchanged.
Next203 own standard BOX SSCC using existing label generator/counter;204/205 addressed final scale/tare archive and current once-only QC use. NS40 not claimedcomplete until those flows; independent physical pilot remains open.
"""
for path,line in[("wiki/index.md","- [Финальный вес малой коробки](database/retailcase_ni042_small_final_weight_20261011.md):202 child type requires current WEIGHT under warehouse NONE/gross.400/tare.100/net.300/exact DTO/version; standard box label and addressed capture next."),
("wiki/log.md","2026-10-11:202 type FINAL_WEIGHT_REQUIRED/version installed/current native metadata owner/exact DTO/legacy URI/barrel. Own e0aa707b CASE6/source14 underWARENONE stillWEIGHT, actualgross.400 wood.100 net.300/currentQC/replay passed. Variable shadow/configpolicy assertion fixed; invalid dependents recompiled; architecture5510cycles76debt. Type upsert11.397ms4 retained/bounded inventory owner.203 standardlabel204/205 addressedcapture next."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:202 NS40 child-specific mandatory WEIGHT regardless warehouse/parent exemption, precise type card/version/current metadata owner/UI; actual six-unit smallbox gross.400/tare.100/net.300 current QC/replay passed.203 standard SSCC label,204/205 final addressed measurements pending; not full NS40 acceptance.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"202_small_box_final_weight.md")]="""# Qwen:202
Run ni042_small_final_weight_case.py dedicated dev. Original carrier type/card version/current role/global metadata fence/DTO precise decimals, updated_by cannot spoof. Old omission keeps flag, changing flag requires currentversion/directDML refuses. CASE childtype mandatory WEIGHT despite warehouse/parentNONE, current signature proof needed; actualgross.400/wood.100/net.300/tareonce/source14 preserved/replay. Reference DEFAULT_WEIGHT_KG is not a measurement. Standard BOXlabel203 and addressedscale204/205 pending. Browser role/version/unknown-save refresh/precision. Existing type exports/private boundaries remain. Short indexed native upsert/current sparse scope/bounded QC legs, not production load.
"""
print(json.dumps(out,ensure_ascii=True))
