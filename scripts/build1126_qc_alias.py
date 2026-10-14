from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py");s=p.read_text(encoding="utf-8")
old='''                    q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
                    q.execute("select RRL_STOCK_QC_GATE.status_json(:p_identifier) from dual",p_identifier=identifier)
                    return read_oracle_json(q.fetchone()[0])'''
new='''                    from .quality_identifier import quality_identifier
                    canonical = quality_identifier(q, identifier, actor)
                    q.execute("select RRL_STOCK_QC_GATE.status_json(:p_identifier) from dual",p_identifier=canonical)
                    result = read_oracle_json(q.fetchone()[0])
                    if canonical != identifier:
                        result["requested_identifier"] = identifier
                    return result'''
assert old in s;s=s.replace(old,new,1);f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/outgoing-quality.js");s=p.read_text(encoding="utf-8")
s=s.replace('if(data.shipment_identifier!==id)throw Error("Ответ относится к другой СТ.");',
 '''if(data.shipment_identifier!==id&&data.requested_identifier!==id)throw Error("Ответ относится к другой СТ.");
    if(typeof data.shipment_identifier!=="string"||!data.shipment_identifier)throw Error("Источник контроля не подтверждён.");
    el("id").value=data.shipment_identifier;''')
# Both readonly load/recovery take the canonical returned source; existing frozen writes unchanged.
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html");s=p.read_text(encoding="utf-8")
import re
s=re.sub(r'outgoing-quality.js\?v=[^"]+', 'outgoing-quality.js?v=20261013-1126',s)
f[str(p)]=s
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8")
s=s.replace("**Revision 51,","**Revision 52,")
s=s.replace("NI02.1–2 — оригинальный auto-split, поздние заказы/ограничения","NI02.1 exact auto через прежний writer реализован в dev; NI02.2 поздние заказы/ограничения")
s=s.replace("NI02.1 — Оригинальная автоматическая подготовка СТ","NI02.1 — Автоподготовка через существующие writers")
s=s.replace("Для auto-split нужен оригинальный source; при блокере сохраняется ручная подготовка.","По решению владельца13Oct auto-split реализован самостоятельно через прежний writer; архив2011 не применяется.")
s+="\nRevision52/1125: NI02.1 automatic_layout/shared writer/preview-run-resolve/durable UI delivered targeted dev. Actual2135 mixed2places/exact36EA/race/rollback/stale/replay, report30/screen41. Independent full acceptance отдельно; все18 не объявлены завершёнными. Следующий ticket: текущий physicalCASE label→готовыйQC источник, без нового контроля/проводки.\n"
f[str(p)]=s
p=Path("wiki/components/retailcase_ni051_control_label_20261012.md");s=p.read_text(encoding="utf-8")
s+="\n1126: prepared read-only physicalCASE alias resolver (SSCC/CASE:ID→existing LEGACY_SBORKA_PALLET_ID/PALLET_UID). FreshRUSERS/nativeQCpermissions beforelookup, currentnativeassert allcandidates, ambiguousrefusal. Status returns requested_identifier onlywhenresolved; UI freezescanonical logical identifier before any command. Commands and cached pending do not re-resolve physicalaliases; existingnativeQC/stock handler unchanged. Runtime pending.\n"
f[str(p)]=s
p=Path("wiki/index.md");f[str(p)]="- [QC physical CASE alias1126](components/retailcase_ni051_control_label_20261012.md): prepared readonly canonical source resolver/current rights/ambiguous refusal; native command unchanged.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1126: после NI02.1 реализован prepared readonly CASE SSCC/CASE:ID→existingQC resolver, nativecurrentactor/WARE/allcandidates/ambiguousguard; UI sends canonical source after currentGET. Commands/pending/native core untouched; live pending. PlanMD synced52.\n"
print(json.dumps(f,ensure_ascii=True))
