import json
from pathlib import Path
out={}
out["wiki/database/retailcase_outbox_clob_response_20261010.md"]="""# Большой исходящий ответ сохраняется как CLOB,159

RRL_OUTBOX_DELIVERY_API.finish_attempt now extracts response_json with native JSON_OBJECT_T.get_clob, not get_string VARCHAR2<=32767. Same event/request/hash/lease/generation/atomic finalize and local response recovery remain. No payload decoding/rounding/reserialization inside original response string. Versioned migration2026-10-10_outbox_clob_response body-only1 statement, specinterface unchanged/live USER_ERRORS empty/currentcontract manifest replaced/fullbundle generatedonly. Old154 source evidence retained.

Actual own2308/Q159_cd12a920b9 simulated response40077chars/80077UTF8bytes, Cyrillic40000chars and exact38digit decimal text: stored original RESPONSE_JSON byte-equivalent text, requestDONE200/hash64/eventDONE, mocknotlegalACK/stockjournalunchanged. Explicit body journal bound8MiB unchanged. This is no realprovider/production batch limit proof.

Traceability event list/detail render aware LEASE_UNTIL explicitUTCtext, preserving offsetratherthan drivernaive timestamp presentation. Legacy DATE nextretry/created remainlegacy, not declaredUTC. Adapterrequest CLOB and nativefinalization contracts preserved. SQL finish11.456ms/20, requestPKlock0.449ms/20/hash0.362ms/16; same indexedshortUOW retained/no newindex. Architecture513/0/79PASS. Provider outcome classification and legalACK separation unchanged.
"""
p=Path("wiki/index.md");out[str(p)]="- [Большой ответ внешней доставки](database/retailcase_outbox_clob_response_20261010.md):159 native CLOB over32K/exactnumeric+Unicode/aware leaseUTC/no realACK.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:159 nativefinish get_clob response, noVARCHAR32K limit. Own2308 simulated40077chars/80077bytes/exact38digit+Cyrillic/DONE200/hash/mockACKfalse/no stock. Body-only1stmt/nativeUSER_ERRORSempty/manifestgenerated; leaseUTCread explicit. Architecture513/0/79PASS; SQLfinish11.456ms/PK0.449/hash0.362 keep/no newindex.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")in{"NI04.3","NI07.2"}:row.setdefault("implementedSlices",[]).append("159 >32K native CLOB response/exact text/aware leaseUTC")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI04.3/159_большой_ответ_адаптера.md"]="""# Qwen —159
Native response_json get_clob, samegeneration/worker/hash/atomicjournal. >32K Unicode/numerictext/escapedquote/backslash preserved exactly. Own2308 response40077chars/80077UTF8bytes, unchanged38digit text/hash/DONE200/mocknotrealACK/journalunchanged. Defaultdisabled no claim. Localspool bound8MiB explicit, no biggerprovider limit assumed; stale lease/commit response loss recover samebody withoutresend. Lease list/detail UTCoffset field explicit; oldDATEfieldsnotUTCguessed. No broadload/GovACK acceptance.
"""
print(json.dumps(out,ensure_ascii=True))
