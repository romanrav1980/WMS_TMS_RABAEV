from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni061_marked_onward")
description="""228 APPLIED RABAEV/orcl. Existing INTERWARE_NEXT source helper admits exact225 keys/qty/UOM/current AVAILABLE/no HARD/sourcecell/versioned snapshot, retains original bind/receipt/placement/custody/whole stock/current ST/target trip/UOM. Existing ShippingCore/native unit issuance/QC/SINGLE loader unchanged, no duplicate writer/customer fulfillment.
Actual22513508027ed->226receive->227PUTAWAY953->IW228.CUSTODY current target/replay/foreign403/zero stock. Original onward ST constructor creates641364/IW.ST:bf84c8e9421494785dd2ab319e3dea0cf05d286e; explicit guarded legacy address Own full-pallet ST retained. Existing validated assignment first refused original vehicle10049/type10 because address requires15. Prepared own vehicle10050/QI22813508027ed/type15 and updated empty seeded targetTT33543 through original edit API as admin (nonadmin empty owner correctly refused). No shared address/first LF/vehicle reference rewritten. Existing assignment/current six-code QC/LOAD IW228.LOAD native-3/sourceP0H0/same3units6codes ISSUED/version10; originalFF ST641362 staysSHIPPED3/no newFF on secondST. Native departure IW228.DEPART retained currentDEPARTED10050/no stock events/replay/protected20/20.
Current custody actor check before saved replay/after wait. Manifest owner dispatch diagnostic found only missing existing RRL_STOCK_RETURN_DISPOSE compile/execute arms besides restored226 interware; restored same original implementation in current root, no duplicate disposal. Follow-up dispatcher structural guard should prevent source bundle replacements losing installed owners.
Native allVALID/no errors;226 unchanged API/TS/architecture gates reused. Custody cvn7usvcj627t16.295ms/1, onwarddispatch15fg9fr93xy7d11.522ms/1: retain original unique receipt/source/binding indexes and bounded10000units/200ownership; no duplicateindex/throughput claim.
Final recipient still explicitly refuses marked payload pending229 exact QR control; nested/aggregate/packing/temperature/partial/real externalACK remain open. Do not claim full NI06.1 acceptance.
"""
out[str(f/"005_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-228-original-marked-interwarehouse-onward'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original second leg issues same marked units without second customer fulfillment',sysdate,user,'db/migrations/2026-10-11_ni061_marked_onward/apply.sql','db/migrations/2026-10-11_ni061_marked_onward/rollback.sql','APPLIED','Actual225->226->227->228 custody0/old ST641364 constructor/existing assign/currentQC6/native LOAD-3/same3 units6codes ISSUED10/oldFF SHIPPED3/no secondFF/native targetTT33543 DEPARTED/vehicle10050 compatibletype15/protected20/20. Existing type conflict denied before native correction of own empty target trip. Final marked recipient remains next229. NativeVALID/226 API gates reused.');
commit;
"""
out[str(f/"apply.sql")]="@@001_onward.sql\n@@002_custody.sql\n@@003_root.sql\n@@004_recompile.sql\n@@005_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for package,sql in[("RRL_STOCK_INTERWARE_NEXT","001_onward.sql"),("RRL_STOCK_INTERWARE_CUSTODY","002_custody.sql"),("RRL_STOCK_POSTING_API","003_root.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+package+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 m["components"]=[x for x in m["components"]if x not in matches]+["../2026-10-11_ni061_marked_onward/"+sql]
m["additional_scripts"].append("../2026-10-11_ni061_marked_onward/004_recompile.sql");out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni061_marked_onward_20261011.md"]="# NI06.1: второе плечо исходной маркированной паллеты\n[[nicora_ni061_marked_placement_20261011]]; [[nicora_ni061_marked_onward_design_20261011]].\n"+description
for path,line in[
("wiki/index.md","- [Маркированная паллета во втором плече](database/nicora_ni061_marked_onward_20261011.md):228 original ST641364/QC6/nativeLOAD-3/sameunits3codes6/ISSUED10/TT33543DEPARTED/no secondFF."),
("wiki/log.md","2026-10-11:228 existing onward source helper accepts exact original marked whole units. Same225->226->953->custody0->old ST641364/assignment/QC6/nativeLOAD-3/units3codes6ISSUED10/TT33543DEPARTED/oldFF3 unchanged/protected20/20. Wrong address type refused; own compatible vehicle10050 via existing admin empty trip edit, first original10049 and sharedADDR unchanged. NativeVALID/226 API gates reused. SQL16.295/11.522ms retain unique/bounds. Missing original disposal routing restored based manifest-owner coverage. Final marked recipient229 next."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","11.10.2026:228 marked original same physical3/codes6 second ST641364 prepared/assigned/currentQC6/nativeLoad-3/depart through existing owners, originalcustomerFFSHIPPED3 unchanged. Final marked recipient still refuses until229; whole nested/aggregation/packing/temperature/externalACK not accepted.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("228 original marked onward ST641364/currentQC6/validated assignment/compatible own vehicle10050/nativeLOAD-3/sameunits3codes6ISSUED10/TT33543departure/no repeatedFF; marked recipient remains229");out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"));out[str(root/"NI06.1"/"228_marked_original_onward.md")]="""# Qwen:228 — второе плечо исходной маркированной паллеты
Создать новую изолированную исходную225->226приёмку->227штатное размещение. Не повторять уже отправленную13508027ed.
Original custody release: stock0effect/current target actor/replay/foreign403/history firstDEPARTED retained.
Original onward ST constructor/rows/current original fulfillment frozen/no duplicate order fulfillment; wrongaddress/typedvehicle/incompleteweights/targettrip ->refusal. Use existing validated assignment. Do not edit shared address to make fixture pass. Empty trip ownership restriction retained/admin owns seeded empty trip setup.
Exact225 frozen physical keys/qty/UOM currentAVAILABLE/sourcecell/noHARD/version snapshot. Partial/missing/foreign units/profile changes ->refusal under native closure.
Mandatory QC QR matrix3physical/6codes(currentUNIT profiles) then original SINGLE loading; source-3/P0H0/originalsameunits ISSUED/version+1/codes6/no unit inserts/originalfirstFFSHIPPED3/no secondFF.
Saved loading replay/no second movement, native transaction rollback/concurrency on fresh fixture; native departure is separate/no goods event.
Existing root original STORE_RETURN_DISPOSE restored, package presence must match routing. No new disposal owner.
Final STORE_RECEIPT marked scope still refuses pending229; do not claim final acceptance/GovACK/nested/fullNI06.1 from this slice.
Review slowSQL original PK/unique source/bounded10000unit matrix; explicit decision.
"""
print(json.dumps(out,ensure_ascii=True))
