"""Emit final source corrections and canonical installer references."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"db/migrations/2026-10-08_stock_posting_core"
files={}
path="db/migrations/2026-10-08_stock_posting_core/131_receipt_reverse.sql"
text=(ROOT/path).read_text(encoding="utf-8")
old="where p.PRIHOD_NAKLAD_ID=doc and (p.STOCK_ORIGIN_UID=p.UID_PALLET or p.STOCK_ORIGIN_UID is null)) loop"
new="""where p.PRIHOD_NAKLAD_ID=doc and (p.STOCK_ORIGIN_UID=p.UID_PALLET or p.STOCK_ORIGIN_UID is null)
    and (p.CREATED_BY_STOCK_OP is not null or exists(select 1 from RRL_EVENTS e
     where e.UID_POLETA=p.UID_PALLET and e.TYPE_EVENT=1 and e.COUNT_EVENT>0))) loop"""
assert text.count(old)==1
text=text.replace(old,new)
text=text.replace("  for born in(select p.UID_PALLET,p.UNIT_COUNT", "  expected:=0;\n  for born in(select p.UID_PALLET,p.UNIT_COUNT")
text=text.replace("if born.UNIT_COUNT is null or born.UNIT_COUNT<=0 or actual!=born.UNIT_COUNT then", "expected:=expected+nvl(born.UNIT_COUNT,0);\n   if born.UNIT_COUNT is null or born.UNIT_COUNT<=0 or actual!=born.UNIT_COUNT then")
text=text.replace("  if a.get_size=0 then", """  select nvl(sum(s.REMAIN),0) into actual from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where p.PRIHOD_NAKLAD_ID=doc and s.REMAIN>0;
  if actual!=expected then raise_application_error(-20886,'RECEIPT_REVERSE_UNPROVEN_ORIGIN');end if;
  if a.get_size=0 then""")
files[path]=text
path="db/migrations/2026-10-08_stock_posting_core/136_inventory_native_api.sql"
text=(ROOT/path).read_text(encoding="utf-8")
text=text.replace("wire clob;old_wire clob;\n begin", "wire clob;old_wire clob;lot_expiry date;\n begin",1)
old="""   wire:=requested.to_clob;old_wire:=d.get_object('metadata').get_object('requested_legacy').to_clob;"""
new="""   if not d.has('metadata') or not d.get_object('metadata').has('requested_legacy') then
    raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   wire:=requested.to_clob;old_wire:=d.get_object('metadata').get_object('requested_legacy').to_clob;"""
assert text.count(old)==1
text=text.replace(old,new)
old="""  else
   begin select STOCK_VERSION into version"""
new="""  else
   select EXPIRY_DATE into lot_expiry from RRL_PALLETS where UID_PALLET=uid;
   if p_expiry is not null and (lot_expiry is null or trunc(lot_expiry)!=trunc(p_expiry)) then
    raise_application_error(-20871,'INVENTORY_LOT_EXPIRY_CONFLICT');end if;
   begin select STOCK_VERSION into version"""
assert text.count(old)==1
files[path]=text.replace(old,new)
manifest=json.loads((D/"current_runtime_manifest.json").read_text(encoding="utf-8"))
for item in ["147_receipt_legacy.sql","147_receipt_entrypoints.sql"]:
    if item not in manifest["additional_scripts"]:manifest["additional_scripts"].append(item)
files["db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]=json.dumps(manifest,indent=2)+"\n"
files["db/migrations/2026-10-08_stock_posting_core/"+manifest["bundle"]]="@@"+manifest["contracts"]+"\n"+"\n".join("@@"+f for f in manifest["components"]+manifest["additional_scripts"])+"\n@@014b_recompile.sql\n"
path="scripts/stock_posting_install.py";text=(ROOT/path).read_text(encoding="utf-8")
old='"RRL_STORNO_ORDER3", "RRL_STORNO_ORDER3_SP_OLD",'
new=old+"\n                    "+", ".join('"'+name+suffix+'"' for name in ["RRL_ACCEPT_ORDER2","RRL_ACCEPT_ORDER2_2","RRL_ACCEPT_ORDER2_3","RRL_ACCEPT_ORDER3","RRL_OTKAT_ORDER2"] for suffix in ["","_SP_OLD"])+","
assert text.count(old)==1
files[path]=text.replace(old,new)
print(json.dumps(files,ensure_ascii=True))
