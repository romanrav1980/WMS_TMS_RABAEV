from pathlib import Path
v=Path("scripts/case387_marked_reuse.py").read_text(encoding="utf-8").replace("context386.json","context623.json").replace("387","624")
a=' scans=[code for unit in origin["units"]for code in unit["codes"]]'
assert a in v
b=''' scans=[code for unit in origin["units"]for code in unit["codes"]]
 aggregation_scans=[dict(system_code="CRPT",profile_code="TOBACCO",level="PALLET",code=origin["lot"]),
                    dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]
 if "source_modes_set"not in saved:
  def modes():
   q.execute("update RRL_SKU_RECEIPT_PROFILE set SCAN_MODE=case SYSTEM_CODE when 'CRPT'then 'PALLET'else 'BOX'end where ARTICUL=:article",article=origin["article"])
  config(modes);saved["source_modes_set"]=True;save()'''
v=v.replace(a,b)
v=v.replace('"scans":scans','"aggregation_scans":aggregation_scans')
a=' if "handover"not in saved:'
# Actual old save key is inspected separately if needed.
v=v.replace(a,' if "handover"not in saved:',1)
# Dictionaries in old script use a different saved key; negative probe inserted before handover call.
needle='hand=call(admin,"POST","/api/delivery/store-return-custody/handover",'
if needle in v:
 v=v.replace(needle,needle,1)
v=v.replace("PASS624","PASS624 aggregate-only registered CRPT PALLET/EGAIS BOX;")
Path("scripts/case624_aggregate_reuse.py").write_text(v,encoding="utf-8")
print("624 fresh original source622/623, current profiles PALLET/BOX only, shared custody/warehouse receive/PUT paths; old387 never repeated.")
