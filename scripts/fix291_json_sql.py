from pathlib import Path
import json
p=Path("db/migrations/2026-10-11_ni061_partial_receiving/003_receiving_body.sql");s=p.read_text(encoding="utf-8")
needle="v_payload clob;"
assert needle in s;s=s.replace(needle,"v_payload clob;v_original_root varchar2(200);v_expected_qty number;v_short_reason varchar2(4000);v_short_ref varchar2(2000);",1)
needle="  insert into RRL_INTERWARE_RECEIPT("
assert needle in s;s=s.replace(needle,"""  v_original_root:=v.get_string('original_root_uid');v_expected_qty:=v.get_number('expected_quantity');
  v_short_reason:=v.get_string('discrepancy_reason');v_short_ref:=v.get_string('discrepancy_reference');
"""+needle,1)
s=s.replace("v.get_string('original_root_uid'),v.get_number('expected_quantity'),v.get_string('discrepancy_reason'),v.get_string('discrepancy_reference')","v_original_root,v_expected_qty,v_short_reason,v_short_ref")
print(json.dumps({p.as_posix():s},ensure_ascii=True))
