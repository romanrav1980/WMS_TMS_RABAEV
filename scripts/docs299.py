from pathlib import Path
import json,re
out={};d=Path("db/migrations/2026-10-11_ni061_loss_recovery");page="wiki/database/nicora_ni061_loss_recovery_decisions_20261011.md"
out[page]="""# Согласование найденного ранее отсутствовавшего товара
299 implements first decision phase of [[nicora_ni061_loss_recovery_design_20261011]]. Existing sole root now dispatches INTERWARE_RECOVERY_REPORT/APPROVE to private RRL_STOCK_IW_RECOVERY_PLAN. Current targetWARE/right, independent report author/approver beforecache andafterwait; exact whole confirmed shortqty2/current recorded issued lost units+versions/sourcecell/UOM/lossbook. Sharedpolicy and sortedROW20/UNIT60/unique70; no stock effects.

Native immutable recoveryrequest/approval plus future receipt/unit tables added. RRL_IW_SHORTAGE_GUARD checks captured current nativeOP/state/transaction for decision inserts; update/delete forbidden. API /recovery-reports /recovery-approvals typed evidence; current shortage read shows recoveryphase. Existing raw interwarehouse panel saves exact intent beforeHTTP, actor/API/receipt scoped retries. Report/approval never announce warehouse receipt, P or GovACK.

Actual existing291ordinary/292marked confirmedlost2: reportrollback, selfapproval20882, actual CAL264 targetreport restoredretired/currentWARE/rights; independent approvalouterrollback. Published admin approval race200/409, exactreplay/collision; recoveryreceiptcount0/protected20-20. tmp/context299_291.json and _292 approvedactual, no new goods/codes. Native allVALID; same sparse loss/receipt/key scopes bounded10000; targetedSQL evidence in tmp/slow299.json.

Next300 nativephysicalreceive through original balance/leg/unit helpers with exact QR/current source/predeclared stock50, cloneLotprovenance, newP2+unitmove atomic; losshistory staysimmutable. Whole missing remainder only in this slice; partial recovery/repeatedloss lifecycle and final supplementalcustomer delivery remain explicit work. No independent/browser/hardware/external acceptance.
"""
for path,line in[
("wiki/index.md","- [Согласование найденного товара](database/nicora_ni061_loss_recovery_decisions_20261011.md):299 exact wholelost2/currentunits/report+otherapproval, no stock beforephysicalreceive."),
("wiki/index.md","- [Проект корректирующей приёмки найденного товара](database/nicora_ni061_loss_recovery_design_20261011.md):299-300 preserveloss history/sourcecodes/one nativeUOW; next actualP2."),
("wiki/log.md","2026-10-11:299 privatecore recoveryreport+independentapprove, immutable request/approval/future receipt-unit schema/capturedguards/currenttargetWARE beforecache-afterwait/exactlost2/currentissuedbook versions; rawdurable existingpanel/API/scopedread. Actual291/292 reportrollback/selfapproval20882/distinctCal264reporter restoredretired/approvalrollback/race/replay/collision/noP/protected20-20. Next300 physicalreceive; no fake goods orGovACK."),
("wiki/runbooks/nicora_active_work.md","LatestNative/app299/serv299 actualrecovery2 approvals for291ordinary/292marked, tmp/context299_291/_292. Recoveryreceipts0, no P/codesnew. Do NOT rerun case299_native afterpublishedapprovals; exactreplay case299_commit safe. Canonical rootdecision299/latestlossunitguard297/helpers295/nativecustody296/sourceindex298. Next300 same core physicalP2/newpallet/oldkeys; whole-loss-only slice first, partial/recurrent/finalredelivery pending."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","11.10.2026:299 Report of found wholelost2 +independent approval implemented/currentexact markedkeys/versions/source. Ordinary291/marked292 approvals actual; P remains0 untilphysicalreceiving300. Partial/recurrent/corrective redelivery not accepted.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));x=next(x for x in j["increments"]if x["id"]=="NI06.1");x.setdefault("implementedSlices",[]).append("299 foundwholelost2 report-independentapprove exactissued sourcekeys/version, actual291-292 noP until300");x["remainingScope"]=["nested and aggregation interwarehouse cargo","physical consolidation and packing into one upper place","partial and recurrent confirmed-loss recovery/corrective redelivery","independent acceptance/hardware/current real ERP andgovernment ACK"]
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));base="../2026-10-11_ni061_loss_recovery/"
sources=[n for n in j["components"]if re.search(r"create\s+or\s+replace\s+package\s+RRL_STOCK_POSTING_API\s",(p.parent/n).read_text(encoding="utf-8"),re.I)];assert len(sources)==1
out[(d/"005_decision_root_current.sql").as_posix()]=(d/"000_before_rrl_stock_posting_api_package.sql").read_text(encoding="utf-8")+"\n"+(d/"004_decision_root_body.sql").read_text(encoding="utf-8")
index=j["components"].index(sources[0]);j["components"][index:index+1]=[base+"002_decision.sql",base+"005_decision_root_current.sql"]
j["packages"].append("RRL_STOCK_IW_RECOVERY_PLAN");j["startup_scripts"].append(base+"001_schema.sql")
j["additional_scripts"]+=[base+n for n in["002_decision.sql","003_decision_guards.sql","004_decision_root_body.sql"]];out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
out[(d/"006_decision_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-299-loss-recovery-decisions'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Found confirmed-lost goods report and independent approval',sysdate,user,'db/migrations/2026-10-11_ni061_loss_recovery/001_schema.sql','db/migrations/2026-10-11_ni061_loss_recovery/rollback_decisions.sql','APPLIED','Actual ordinary/marked wholelost2 report/independentapproval/rollback/race/replay; no stock before physicalreceive300. CurrentWARE/exactunitversions/lossbook; noGovACK/hardware/industrialclaim.');
commit;
"""
out[(d/"rollback_decisions.sql").as_posix()]="""declare n number;begin
 select count(*)into n from RRL_INTERWARE_RECOVERY_REQUEST;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_RECOVERY_HISTORY');end if;
end;
/
@@000_before_rrl_stock_posting_api_package_body.sql
-- Preserve additive tables for current readers; remove app before empty schema removal.
"""
print(json.dumps(out,ensure_ascii=True))
