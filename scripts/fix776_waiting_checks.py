from pathlib import Path
p=Path("scripts/check774_waiting_done.py");t=p.read_text(encoding="utf-8")
t=t.replace("assert q.fetchone()==(6,3)","assert q.fetchone()==(3,3)\n q.execute(\"select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid\",p_uid=ctx[\"lot\"]);assert q.fetchone()==(6,)")
p.write_text(t,encoding="utf-8")
