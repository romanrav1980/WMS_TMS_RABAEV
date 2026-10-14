from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni081_time_source_contract")
p=Path("db/migrations/2026-10-11_ni081_time_resource_gate/001_api.sql");s=p.read_text(encoding="utf-8")
out[str(f/"000_before_rrl_tt_time_api.sql")]=s
s=s.replace("  b.put('condition',w.CONDITION);b.put('deleted',w.DELETED);b.put('pay_order_id',w.PAY_ORDER_ID);","  b.put('source_contract_version',2);b.put('transport_type',w.TRANSTYPE);")
s=s.replace("   o.put('condition',member.CONDITION);o.put('pallet_identifier',member.PALLET_UID);a.append(o);","   o.put('pallet_identifier',member.PALLET_UID);a.append(o);")
s=s.replace("   o.put('fact_start',to_char(op.FACT_START,'YYYY-MM-DD HH24:MI:SS'));o.put('fact_end',to_char(op.FACT_END,'YYYY-MM-DD HH24:MI:SS'));a.append(o);","   a.append(o);")
needle="  result.put('time_zone',v_zone);result.put('reason',v_reason);result.put('actor',p_actor);"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n  result.put('source_contract_version',2);result.put('plan_source',json_object_t.parse(v_source));")
needle="   if saved.SOURCE_HASH=hash then b.put('approval_status','APPROVED');else b.put('approval_status','SOURCE_CHANGED');end if;"
assert s.count(needle)==1
s=s.replace(needle,"""   if not json_object_t.parse(saved.RESULT_JSON).has('source_contract_version')then b.put('approval_status','LEGACY_SOURCE_CONTRACT');
   elsif saved.SOURCE_HASH=hash then b.put('approval_status','APPROVED');else b.put('approval_status','SOURCE_CHANGED');end if;""")
out[str(f/"001_api.sql")]=s;out[str(f/"apply.sql")]="@001_api.sql\n";out[str(f/"rollback.sql")]="@000_before_rrl_tt_time_api.sql\n"
out["wiki/database/retailcase_ni081_time_source_design_20261011.md"]="# NI08.1: плановый ключ времени —256\nCurrent250 snapshot included ST executionCONDITION andOPS FACT timestamps, so unchanged planned schedule became stale afterphysical load. V2 plan-only hash includes explicit version/TTID/type/vehicle/driver/dock/date-clock/memberID-WARE-UID/operationID-code-ordinal-duration-plannedtimes; live execution state checked separately, never partof material plan. Result freezesfull plan_source forfuture exactchange review. OldV1 decisions immutable and explicitly LEGACY_SOURCE_CONTRACT, no reinterpretation orguess of lostsourcefields. Reconfirm unstarted sameoriginal plan undercurrentlocks, no implicit legacy endorsement. Currentown255 sourcealreadyLOADED must useoriginalnativeunload/reconfirm/reload as controlledreversal, no new birth. Implementation in progress.\n"
for path,line in[
("wiki/index.md","- [Плановый ключ времени: проект256](database/retailcase_ni081_time_source_design_20261011.md): execution state separates from materialplan/V2 fullsource/legacy notendorsed; implementation pending."),
("wiki/log.md","2026-10-11:255 same snapshot combined original time/loading/incoming/readers exposed250 sourcehash included executionstate: normalLOAD invalidated unchanged time approval. 256 design separates planmaterial fromactualphase, retainsold immutabledecision asLEGACY_SOURCE_CONTRACT/freeze fullV2source; no inferredlegacy source. Existing255 sourceLOADED tobe explicitnativeunload/reconfirm/reload withoutbirth.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
