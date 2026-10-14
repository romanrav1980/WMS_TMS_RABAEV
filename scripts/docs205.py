from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni042_final_qc")
out[str(f/"012_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-205-final-scale-qc-use'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing native QC mandatory addressed whole CASE weight and once-use',sysdate,user,
'db/migrations/2026-10-11_ni042_final_qc/apply.sql','db/migrations/2026-10-11_ni042_final_qc/rollback.sql','APPLIED',
'Own QPB205F0C461FA/type12/CASE6/SSCC090000000000000100/gross.400/tare.100/net.300: native late rollback, distinct concurrentOP one winner, sameOP replay, manual bypass403/409, current WARE before saved native replay, immutable use, original source14/nativecleanup13520/20. Existing root/QC/gate reused; TEST visible in result/UI, no real hardware claim.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@012_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
root=p.parent
for name,new in[("RRL_STOCK_PALLET_QC_CMD","004_qc.sql"),("RRL_STOCK_QC_GATE","005_gate.sql"),("RRL_WH_SCALE_API","006_archive.sql"),("RRL_STOCK_POSTING_API","007_root.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+name+r"\s",(root/x).read_text(encoding="utf-8"),re.I)]
 assert matches,(name,matches)
 m["components"]=[("../2026-10-11_ni042_final_qc/"+new)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
 # Required native specs already emitted before components; place helper body before its first actual caller.
 if name=="RRL_STOCK_PALLET_QC_CMD":
  at=m["components"].index("../2026-10-11_ni042_final_qc/"+new)
  m["components"].insert(at,"../2026-10-11_ni042_final_qc/002_admission.sql")
 if name=="RRL_STOCK_POSTING_API":
  at=m["components"].index("../2026-10-11_ni042_final_qc/"+new)
  m["components"].insert(at,"../2026-10-11_ni042_final_qc/008_scope.sql")
m["packages"].extend(["RRL_WH_FINAL_SCALE_ADMISSION","RRL_OUTGOING_QC_ACCESS"]);m["startup_scripts"].append("../2026-10-11_ni042_final_qc/001_schema.sql")
m["additional_scripts"].append("../2026-10-11_ni042_final_qc/003_guard.sql")
m["required_columns"]["RRL_WH_FINAL_SCALE_USE"]=["CAPTURE_KEY","STOCK_OPERATION_ID","TARE_CAPTURE_KEY","CASE_PICK_TASK_ID","CASE_CONTENT_VERSION","COMPOSITION_SIGNATURE","ACTOR"]
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_final_qc_20261011.md"]="""# NI04.2: финальное взвешивание через исходный QC
205 APPLIED; [[retailcase_ni042_final_qc_design_20261011]]. Existing OUTGOING_PALLET_CHECK/root/QC/gate use immutable FINAL_GROSS+EMPTY_TARE. CONTAINER FINAL_WEIGHT_REQUIRED manual gross/tare does not approve; current archived values/version/composition/device/sender/calibration/freshness120s required. One UNIQUE70 capture-use lock and append-only use PK/uniqueOP are in original transaction with QC approval/CASE/outbox. No P/H effect or loading performed.
A new precise final-weight DTO accepts OP/key/current signature only; server derives original gross/tare, caller cannot override quantity/mass. Read-only final list joins bounded51 archive rows to PK use rows, controllers need only current outgoing_pallet_check. Status/current archive/API/native root enforce active RUSERS/current WARE/GLOBAL_ADMIN and old three QC permissions. Native check before APPLIED replay and after actual lock wait preserves current authorization. Other root branches retained from fresh live source.
Accepted QC history must link to actual used GROSS/current content signature and CASE version. Later loading does not repeat the120s freshness/calibration checks on a completed historical fact. A new measurement requires fresh current device. Same empty physical carrier may be reweighed using a new GROSS with the original immutable tare; GROSS cannot be used by two different QC commands. Net is gross minus actual tare once. Current QC expected weight/tolerance/independent-controller/mark/item gates retained. Full CASE control states WAIT_CONTROL/CONTROL_IN_PROGRESS/CONTROLLED/READY_TO_SHIP support reweighing.
Own QPB205F0C461FA/type12/SSCC090000000000000100/CASE6: tare671B08AA17B559D5462A334E30CC218778C9788D66ABCF566812DE746BED690E=.100, GROSSBDDDB5DD7595C5A60F61612250AC26B752383E228B210DA03D8AC27D428B4136=.400/net.300/current source; controller QC205f0c461fa differs from picker/gateway. Native late rollback removes use/op/approval/restores WAIT_CONTROL. Concurrent two distinct OPs →one200/one409, winning SMALL205.QC:f0c461fa replay exact, use1, directDELETE20863, foreign currentWARE403 even saved native prepare replay. Manual bypass409/quantity override422; current role-only status/list/result include TEST/source masses; source14H0 preserved. Native return/tare-zero/count cleanup/currentactors retired/original135 P20H20.
First approved() SQL used dbms_transaction.local_transaction_id(false) directly inside SQL, Oracle19 rejected SQL boolean FALSE; assigned native tx scalar before SELECT. Explicit client stale composition signature changed20890→20873 to avoid pointless retry; genuine closure revalidation still20890. Current native errorsclear/VALID.
Raw QC panel selects current signature/version unused FINAL_GROSS, disables manual mass override for requiredbox, durable sameOP retry remains. TSD shows actual empty tare and refresh action only for requiredsmall type. No browser manufactures device packets. Middleware applies32KB stream bound to final packet, entire scale namespace nonreplayable. TEST marked visibly; no hardware/government ACK claim.
Slow decisions: initial proof INSERT21a9thn21944958.016ms2 (cold guard/JSON), bounded archive/use listb1v9qxts88rk718.85ms1, accepted-proof lookupfz50fbkaw696u3.785ms3. Retain PK/uniqueOP/time-purpose indexes/51-row limit; inventory owner profile trigger full canonical/resolved JSON parse and QC repeated signature work before high-volume gate, batch/archive retention plan. No extra index guessed from two cold cases.
NS40 software sequence now standard SSCC→measured empty tare→existing physical CASE→closed/boundCASE→fresh whole GROSS→original QC once-use. Hardware pilot/full mixed small-container shipping/route heavy-first still need actual cases; whole NI04.2 not closed.
"""
for path,line in[
("wiki/index.md","- [Финальное показание в исходном QC](database/retailcase_ni042_final_qc_20261011.md):205 native once-use/rollback/concurrent one winner/current WARE before replay/actual.400−.100=.300/TEST visible/TSD+controller UI; no P-H."),
("wiki/log.md","2026-10-11:205 original root/QC/gate plus append-only FINAL_GROSS use/current QC WARE applied. Own QPB205F0C461FA CASE6/gross.400 measuredtare.100/net.300/native outer rollback/concurrent distinctOP one winner/replay/manual bypass/current WARE before native saved replay/immutableuse/API role-onlystatus+list/source14/cleanup13520/20. TEST explicit. SQL booleanFALSE fixed native tx scalar, deterministic stale input20873. Proof INSERT58.016ms2 cold retain keys/bounds, inventory owner profile JSON/signature before highvolume. UI selects archive/TSD actualtare/32KB packetbound. Further NI04.2 gaps remain."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:205 NS40 software SSCC→measuredemptytara→CASEpick→closed/boundCASE→GROSSarchive→originalnativeQC once-use delivered. Actual6/.400−.100=.300/native outerrollback/concurrentdistinctOPone/replay/manualbypass/currentWAREbeforereplay/source14/nativecleanup. TSD and role-only QC archive UI/TEST provenance. Hardware commissioning/full mixed small-container shipping/routeheavy-first remain; NI04.2 in_progress.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");plan=json.loads(p.read_text(encoding="utf-8"))
sprint=next(x for x in plan["increments"]if x["id"]=="NI04.2")
sprint.setdefault("implementedSlices",[]).extend(["203 original CASE standard GS1 SSCC/immutable CP history/shared allocator/TSD attached scan admission","204 existing addressed scale archive explicit EMPTY_TARE/FINAL_GROSS/current CASE/signature/first fill gate","205 existing native QC mandatory final packet/once-use/rollback/concurrent winner/current WARE before replay/role-only current archive UI"])
out[str(p)]=json.dumps(plan,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"205_final_scale_qc.md")]="""# Qwen:205 original native QC final packet
Run scripts/ni042_final_qc_case.py dedicated dev. First fill requires actual emptytare, original ordinary types unchanged. Standard SSCC/current type/wholeCASE composition/version/device/cal/current sender/fresh stablepacket, GROSS linked to same measuredtare; exact net once. Manual legacy weight cannot bypass, final DTO rejects quantity/gross override. Late originalroot rollback restores use/op/approval/outbox/CASE WAIT_CONTROL. Two different OPs same GROSS exactly1winner; saved winner repeat exact; changedbody conflict; history immutable. Currentactive WARE/role native before APPLIED replay and after lockwait, API status/readings scoped even controller lacks CASEexecute. After acceptedQC history age alone must not invalidate load; changedcomposition invalidates. TARE may support repeated independent GROSS samecarrier, GROSS used once. Raw QC/ТСД durable original command/reprint/tare/latest unused matchingcapture/unknown sameOP retry/TEST visibly distinguished. Hardware not accepted. Review slow proof trigger JSON/signature cost; no broad load unless scoped.
"""
print(json.dumps(out,ensure_ascii=True))
