from pathlib import Path
import json
f={}
p=Path("wiki/database/nicora_ni052_departure_temperature_20261014.md");f[str(p)]=p.read_text(encoding="utf-8")+"""
1172: native positive sameoriginal33636/LOAD3.125→DEPART3.75/replay; missing/new20°C denied, outerrollback restores LOADED/no departure-source, finalRootresult/currentstatus captures both values; DEPARTquantity journal0, protectedP20H20. Helper/core/root/depart/triggererrors empty/VALID. Currenttemperature on departure is manual confirmation, not sensor or continuous control.

Actual longest thermalquery675.298ms/13575buffers despite JOIN hints. Prepared1173 replacement uses DBMS_SQL with ≤200 named numeric IN binds and ≤1000SKU rows; at most200 query shapes, IDs never embedded as literals. Every success/failure closes cursor. Existing1171 guard/range semantics and histories preserved. Paired performance rollback returns1171 protected code; data retained. Apply/measurement pending; physical flow1172 predates query rewrite.
"""
p=Path("wiki/index.md");f[str(p)]="- [Departure1172 /SQL1173](database/nicora_ni052_departure_temperature_20261014.md): actual one-clock3.75/manual confirm/replay/rollback/DEPARTqty0; slow675ms rewrite prepared.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1172–1174 prepared: exact same33636 actual thermal departure3.75 distinctfromload3.125, missing/20denied, rollbackLOADED/no departsource, final/replay/no quantityjournal/protectedP20H20. Slowthermal675.298ms13575buffers →prepared DBMS_SQL200boundIN query/1000SKU/cursor cleanup/paired performance rollback; no literalIDs/index. Nativephysical flow predatesrewrite; nextboundedread measurement.\n"
print(json.dumps(f))
