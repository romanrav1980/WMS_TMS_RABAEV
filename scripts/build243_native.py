from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_incident")
s=(f/"000_before_rrl_interware_routing.sql").read_text(encoding="utf-8")
s=s.replace("ref varchar2(60):=d.get_string('decision_reference');","ref varchar2(60):=d.get_string('decision_reference');incident_kind varchar2(30):=d.get_string('incident_kind');incident_detail nvarchar2(1000):=d.get_string('incident_detail');evidence_reference nvarchar2(200):=d.get_string('evidence_reference');",1)
anchor="arrival:=to_timestamp_tz(d.get_string('expected_arrival')"
s=s.replace(anchor,"""if incident_kind is null then
   if d.has('incident_detail')or d.has('evidence_reference')then raise_application_error(-20871,'INTERWARE_INCIDENT_KIND_REQUIRED');end if;
  elsif incident_kind not in('TRANSPORT_DELAY','MISSING_PALLET','IDENTIFIER_MISMATCH')or trim(incident_detail)is null or trim(evidence_reference)is null then raise_application_error(-20871,'INTERWARE_INCIDENT_DETAIL_EVIDENCE_REQUIRED');end if;
  """+anchor,1)
s=s.replace("j.put('stock_changed',false);p_result:=j.to_clob;","""j.put('stock_changed',false);
  if incident_kind is not null then j.put('incident_kind',incident_kind);j.put('incident_detail',incident_detail);j.put('evidence_reference',evidence_reference);j.put('incident_basis','OPERATOR_REPORT');j.put('quantity_adjusted',false);end if;
  p_result:=j.to_clob;""",1)
s=s.replace("ACTOR,PAYLOAD_HASH,CANONICAL_REQUEST,RESULT_JSON)","ACTOR,PAYLOAD_HASH,CANONICAL_REQUEST,RESULT_JSON,INCIDENT_KIND,INCIDENT_DETAIL,EVIDENCE_REFERENCE)",1)
s=s.replace("p_actor,hash_value,p_request,p_result);","p_actor,hash_value,p_request,p_result,incident_kind,incident_detail,evidence_reference);",1)
assert "INTERWARE_INCIDENT_DETAIL_EVIDENCE_REQUIRED"in s
print(json.dumps({str(f/"002_routing.sql"):s},ensure_ascii=True))
