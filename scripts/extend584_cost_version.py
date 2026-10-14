from pathlib import Path
p=Path("db/migrations/2026-10-12_ni071_transport_recognition/002_api.sql");v=p.read_text(encoding="utf-8")
assert "expected_norm_version"not in v
v=v.replace("trip number;ware number;price number;currency_value","trip number;ware number;price number;expected_norm_version number;currency_value")
v=v.replace("if k.count!=5","if k.count!=6").replace("'source_price_id','currency')","'source_price_id','currency','expected_norm_version')")
v=v.replace("currency_value:=d.get_string('currency');","currency_value:=d.get_string('currency');expected_norm_version:=d.get_number('expected_norm_version');")
v=v.replace("or trip is null","or expected_norm_version is null or expected_norm_version<1 or expected_norm_version!=trunc(expected_norm_version)or trip is null")
v=v.replace("hash_values.append(price);","hash_values.append(price);hash_values.append(expected_norm_version);")
v=v.replace("v_version:=norm.get_number('version');","v_version:=norm.get_number('version');\n  if v_version!=expected_norm_version then raise_application_error(-20867,'TRANSPORT_NORM_VERSION_CONFLICT');end if;")
p.write_text(v,encoding="utf-8")
p=Path("scripts/case583_native_cost_trial.py");v=p.read_text(encoding="utf-8")
v=v.replace('source_price_id=price,currency="GEL")','source_price_id=price,currency="GEL",expected_norm_version=2)')
p.write_text(v,encoding="utf-8")
print("584 expected norm version guard added before monetary effects.")
