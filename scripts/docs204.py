from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_final_scale")
out[str(f/"005_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-204-final-scale-archive'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Whole CASE addressed empty tare and final gross in existing scale archive',sysdate,user,
'db/migrations/2026-10-11_ni042_final_scale/apply.sql','db/migrations/2026-10-11_ni042_final_scale/rollback.sql','APPLIED',
'Own QPB2044F9A6052/type10: confirmed SSCC/currentCASE6/EMPTY_TARE.100/FINAL_GROSS.400/net.300/current signature/TEST device/dedicated sender/old PICK list excludes final/append-only/no P-H/native cleanup13520/20. Original packet validator/device/archive reused; first-pick empty-tare gate. 205 same root QC mandatory once use next.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@005_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
root=p.parent
for name,new in[("RRL_WH_SCALE_API","002_body.sql"),("RRL_CASE_SCALE_ADMISSION","003_admission.sql")]:
 matches=[x for x in m["components"]if ("create or replace package "+name+" ")in(root/x).read_text(encoding="utf-8")];assert len(matches)==1 or(name=="RRL_CASE_SCALE_ADMISSION"and len(matches)==2),(name,matches)
 m["components"]=[("../2026-10-11_ni042_final_scale/"+new)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
m["startup_scripts"].append("../2026-10-11_ni042_final_scale/001_schema.sql")
m["required_columns"]["RRL_WH_SCALE_CAPTURE"].extend(["CAPTURE_PURPOSE","TARE_CAPTURE_KEY","PALLET_TYPE_ID","TYPE_VERSION","COMPOSITION_SIGNATURE"])
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_final_scale_20261011.md"]="""# NI04.2: исходные показания финальной коробки
204 APPLIED; [[nicora_ni042_final_scale_design_20261011]]. Existing scale archive/device/validator/context/current dedicated sender reused; capture purpose PICK/EMPTY_TARE/FINAL_GROSS. Whole CASE readings have no article/line/source-product; same device/capture identity prevents second-purpose reuse. Old PICK API/result/replays retained; native PICK rejects any other purpose and old list filters PICK.
EMPTY_TARE requires confirmed SSCC/current empty CASE before first pick. FINAL_GROSS requires closed/bound CASE/current version+composition signature/same earlier measured SSCC/type/warehouse/post/device/mode tare within24h. Calibration checked at each measurement; historical tare is an immutable physical fact, future type-name/calibration metadata does not rewrite its measured mass. GROSS records current metadata versions. Exact net = gross minus measured tare once; reference default weight not substituted.
Native CASE now refuses first fill without EMPTY_TARE; after first accepted physical pick the same carrier tare remains archived. New final archive endpoints use precise string/sample DTO/current role; perCASE bounded51 index; single native original packet function supports both contracts. Input bound as ASCII VARCHAR instead of an unnecessary temporary input CLOB. Archive itself neither changes P/H nor approves loading.
Own QPB2044F9A6052/type10/SSCC090000000000000063/CASE6: empty.100 archiveB01A5C363D20B5E0C7167ABC84C19E857C80041E9E14AEFE911ED783FB494960, final.400 archiveCA1599E39B7CA40AD927D90D3D8FAC38255FA2B383BC3780CC1FC1404A6D2B23/net.300/current composition/replay, wrong version/tare/unstable/body/role refused, direct archive update20863. PICK list0/final list2/current single read; source14H0 unchanged. Existing QC/source6/native return/tare-zero/cleanup, original135 P20H20 preserved. First fixture hit reserved Oracle bind :uid in an author-only verification SELECT after archiving; fixed :p_uid, native cleanup passed and actor retired.
Current packages allVALID/USERERRORclear/architecture554/0/76. final bounded list8ja49c55pxqp03.098ms2; old PICK bounded list5mcmgnk24yqct7.147ms2; retain case-purpose/time and old line indexes/current50+1 bounds. Inventory owner batch/plan review if scale history grows; cold fixture not throughput evidence.
Hardware packets are synthetic TEST; no equipment commissioning claim. 205 mandatory native QC once-only final capture and current gate next; NS40 remains open.
"""
for path,line in[
("wiki/index.md","- [Архив финального веса коробки](database/nicora_ni042_final_scale_20261011.md):204 existing archive/current SSCC/empty.100+final.400/net.300/current composition/first-fill tare gate;205 native QC once-use next."),
("wiki/log.md","2026-10-11:204 shared warehouse scale archive explicit PICK/EMPTY_TARE/FINAL_GROSS applied, current device/source/stable validator reused. Own QPB2044F9A6052/CASE6/archive.100+.400=.300 net/current signature/replay/refusals/source14/native cleanup13520/20; synthetic TEST. First author reserved :uid fixed; allVALID/errors0/architecture5540/76. PerCASE list3.098ms2 retain indexed51 bound/inventory plan owner.205 QC once-use next."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:204 NS40 archive explicit empty tare+final GROSS in existing addressed device/archive/validator; current SSCC/case version/signature/type; first fill requires measured empty tare. Actual6/gross.400/tare.100/net.300/currentscope/refusals/replay/nativecleanup.205 mandatory QC originalroot/once use still pending; syntheticTEST not physicalpilot.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"204_final_scale_archive.md")]="""# Qwen:204 whole CASE scales
Run scripts/ni042_final_scale_case.py in dedicated dev. Same physical device/capture ID namespace across PICK/final; current sender/WARE rights and immutable original replay; changed packet rejected. EMPTY_TARE only confirmed SSCC/emptyCASE before filling, first pick without tare must refuse atomically. Final GROSS only closed+boundCASE/currentversion/currentcomposition/same real tare/source/mode/post; current calibration, stable5samples/2sec/zero/resolution. Actual .400−.100=.300 exact. Default type weight is reference only. PerSKU PICK list excludes final/null line; nativePICK cannot consume final capture. Current final bounded list/read foreignWARE403, immutable archive. Hardware TEST remains explicit. 205 native once-use/QC still pending.
"""
print(json.dumps(out,ensure_ascii=True))
