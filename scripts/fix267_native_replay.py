from pathlib import Path
import json
p=Path("db/migrations/2026-10-11_ni022_admission/003_api.sql");s=p.read_text(encoding="utf-8").replace("b:=json_object_t.parse(p_body);v_sender:=", "b:=json_object_t.parse(p_body);\n  if b.get_size!=11 or b.get_number('expected_version')is null or b.get_number('expected_version')<0 or trunc(b.get_number('expected_version'))!=b.get_number('expected_version')then raise_application_error(-20886,'STORE_ADMISSION_INPUT_FIELDS_INVALID');end if;\n  v_sender:=")
s=s.replace("if saved.PAYLOAD_HASH!=v_hash or saved.CUSTOMER_ORDER_ID!=v_id then", """if saved.PAYLOAD_HASH!=v_hash or saved.CUSTOMER_ORDER_ID!=v_id
    or saved.DECISION_ID!=v_decision or saved.DECISION_CODE!=v_code or saved.ORIGINAL_CONTENT_HASH!=v_original
    or saved.VERSION_NO!=b.get_number('expected_version')+1 or dbms_lob.compare(saved.RAW_XML,v_raw)!=0
    or json_object_t.parse(saved.RESULT_JSON).get_string('reason')!=v_reason
    or json_object_t.parse(saved.RESULT_JSON).get_string('reference')!=v_ref then""")
# Oracle PL/SQL requires assigning parsed object before method access.
s=s.replace("v_finish timestamp with time zone;r json_object_t:=json_object_t();","v_finish timestamp with time zone;cached json_object_t;r json_object_t:=json_object_t();")
s=s.replace("begin select *into saved from RRL_SAP_STORE_DECISION where SENDER=v_sender and MESSAGE_ID=v_message;","begin select *into saved from RRL_SAP_STORE_DECISION where SENDER=v_sender and MESSAGE_ID=v_message;\n   cached:=json_object_t.parse(saved.RESULT_JSON);")
s=s.replace("json_object_t.parse(saved.RESULT_JSON).get_string('reason')","cached.get_string('reason')").replace("json_object_t.parse(saved.RESULT_JSON).get_string('reference')","cached.get_string('reference')")
print(json.dumps({str(p):s},ensure_ascii=True))
