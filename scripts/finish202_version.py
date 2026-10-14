from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_small_final_weight");out={}
out[str(f/"007_version.sql")]="alter table RRL_PALLET_TYPE add(TYPE_VERSION number(10)default 1 not null constraint RRL_PT_VERSION_CK check(TYPE_VERSION>=1));\n"
p=f/"002_api.sql";s=p.read_text(encoding="utf-8")
s=s.replace("v_required number;n number;","v_required number;n number;current_version number:=0;expected_version number;old_required number;")
anchor="  v_required:=null;"
assert anchor in s
s=s.replace(anchor,"""  expected_version:=j.get_number('expected_version');
  begin select TYPE_VERSION,FINAL_WEIGHT_REQUIRED into current_version,old_required from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_id;
  exception when no_data_found then current_version:=0;old_required:=0;end;
  if expected_version is not null and expected_version!=current_version then raise_application_error(-20873,'PALLET_TYPE_VERSION_CHANGED');end if;
"""+anchor)
anchor="  dbms_session.set_context('RRL_PALLET_TYPE_CTX','TX_ID'"
s=s.replace(anchor,"  if v_required is not null and v_required!=old_required and expected_version is null then raise_application_error(-20886,'PALLET_TYPE_EXPECTED_VERSION_REQUIRED_FOR_FINAL_WEIGHT');end if;\n"+anchor,1)
s=s.replace("ACTIVE=v_active,FINAL_WEIGHT_REQUIRED=nvl(v_required,d.FINAL_WEIGHT_REQUIRED),UPDATED_AT=","ACTIVE=v_active,FINAL_WEIGHT_REQUIRED=nvl(v_required,d.FINAL_WEIGHT_REQUIRED),TYPE_VERSION=d.TYPE_VERSION+1,UPDATED_AT=")
out[str(p)]=s;out[str(f/"002_recompile_api.sql")]=s[:s.index("create context ")]
out[str(f/"008_finish.sql")]="@@007_version.sql\n@@006_recompile.sql\n"
p=Path("api/wms_api_server/app/modules/inventory/contracts_pallet_types.py");s=p.read_text(encoding="utf-8")
s=s.replace("    final_weight_required:","    expected_version: int | None = Field(default=None,ge=0,strict=True)\n    final_weight_required:")
out[str(p)]=s
p=Path("api/wms_api_server/app/services/case_pick_service.py");s=p.read_text(encoding="utf-8").replace("FINAL_WEIGHT_REQUIRED,ACTIVE","FINAL_WEIGHT_REQUIRED,TYPE_VERSION,ACTIVE",1);out[str(p)]=s
p=f/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8").replace("@@002_api.sql","@@007_version.sql\n@@002_api.sql")+"alter package RRL_STOCK_PALLET_QC_CMD compile body;\nalter package RRL_STOCK_TARE_CMD compile body;\nalter package RRL_STOCK_TARE_RESOLVE compile body;\nalter package RRL_STOCK_TARE_BOOK_CMD compile body;\n"
p=f/"rollback.sql";out[str(p)]=p.read_text(encoding="utf-8")+"alter table RRL_PALLET_TYPE drop column TYPE_VERSION;\n"
print(json.dumps(out,ensure_ascii=True))
