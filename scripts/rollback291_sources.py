from pathlib import Path
import json
out={};base=Path("db/migrations/2026-10-11_ni061_partial_receiving")
s=(base/"000_before_rrl_sap_pallet_write_guard.sql").read_text(encoding="utf-8")
s=s[:s.index("ALTER TRIGGER")].strip()+"\n/\n"
out[(base/"010_before_sap_guard.sql").as_posix()]=s
s=(base/"000_before_rrl_stock_interware_rec_body.sql").read_text(encoding="utf-8")
needle=" select * into plan from RRL_INTERWARE_PLAN where OPERATION_ID=v_plan;"
assert needle in s;s=s.replace(needle," if m.get_boolean('partial_receipt')then raise_application_error(-20886,'INTERWARE_PARTIAL_ROLLBACK_DISABLED');end if;\n"+needle,1)
out[(base/"011_rollback_receiving_body.sql").as_posix()]=s
out[(base/"rollback.sql").as_posix()]="""declare n number;begin select count(*)into n from RRL_INTERWARE_RECEIPT where ORIGINAL_ROOT_UID is not null;if n>0 then raise_application_error(-20886,'INTERWARE_PARTIAL_HISTORY_RETAINED');end if;end;
/
@@011_rollback_receiving_body.sql
@@000_before_rrl_stock_interware_put_body.sql
@@000_before_rrl_stock_interware_custody_body.sql
@@000_before_rrl_interware_depart_gate_body.sql
@@010_before_sap_guard.sql
drop package RRL_STOCK_INTERWARE_PART;
@@008_recompile.sql
-- Nullable additive columns are retained for paired application readers.
-- Native rollback explicitly refuses partial payloads; no silent full-mode reinterpretation.
"""
p=Path("wiki/database/retailcase_ni061_partial_receiving_20261011.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nSQL rollback rejects retainedpartialhistory BEFORE any body change; restores oldcloneguard/PUT/custody/depart, oldreceivingbody explicitlyrejectspartialpayload, dropsprivatehelper. Nullablecolumns retainedforpairedcurrentreaders; no blindfulldata reinterpretation.\n"
for path,line in [("wiki/index.md","291 rollback clarified: retainedhistory refuses beforechanges; oldnativepayloadguard/cloneguard restored, additivecolumns retained."),("wiki/log.md","2026-10-11:291 rollback completepairedSQL behavior: reject retainedpartialhistory first, restoreoldSAPcloneguard/nativePUT-custody-depart, oldreceiving refusespartialpayload insteadofignoringit; nullablecolumnsmirroredretainedforreaders. No rollback applied/currentactualP1history retained.")]:
 out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
