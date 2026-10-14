from pathlib import Path
import json
out={};base=Path("db/migrations/2026-10-11_ni061_partial_receiving")
p=base/"007_sap_clone_guard.sql"
# Generated source is still in the unapplied builder output.
j=json.loads(Path("tmp/native291.json").read_text(encoding="utf-16"))
s=j[p.as_posix()]
s=s.replace("     join RRL_PALLETS source_lot on source_lot.UID_PALLET=d.SOURCE_UID\n","")
s=s.replace("      and nvl(source_lot.STOCK_ORIGIN_UID,source_lot.UID_PALLET)=d.ORIGIN_UID\n","")
s=s.replace("      and source_lot.PRIHOD_NAKLAD_ID=:new.PRIHOD_NAKLAD_ID and d.NAKLAD_ID=:new.PRIHOD_NAKLAD_ID","      and d.SOURCE_UID!=d.TARGET_UID and d.NAKLAD_ID=:new.PRIHOD_NAKLAD_ID")
j[p.as_posix()]=s
print(json.dumps(j,ensure_ascii=True))
