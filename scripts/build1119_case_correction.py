from pathlib import Path
import json
p=Path("scripts/case1118_auto_preparation.py");s=p.read_text(encoding="utf-8")
s=s.replace('   assert LegacyPreparation(TransactionGateway(q)).auto_prepare(order,data["body"],"admin")["idempotent"]','   assert r["status"]=="ST_PREPARED"')
start=s.index(' # A modified current SKU')
end=s.index(' data["phase"]="VERIFIED_ROLLBACK";save()',start)
s=s[:start]+''' # Commit a change only to our new synthetic SKU, verify stale rejection, restore it.
 with g.transaction("Own1118 change own norm")as q:
  q.execute("update RRL_ARTICULS set NORMA_UKLADKI=12 where ACTICUL=:a",a=data["articles"][0])
 try:
  try:service.auto_prepare(order,data["body"],"admin")
  except ValueError as exc:assert "SOURCE_CHANGED" in str(exc),str(exc)
  else:raise AssertionError("Stale preview accepted")
 finally:
  with g.transaction("Own1118 restore own norm")as q:
   q.execute("update RRL_ARTICULS set NORMA_UKLADKI=24 where ACTICUL=:a",a=data["articles"][0])
'''+s[end:]
start=s.index('# Replay must not recompute')
end=s.index('with oracledb.connect',start)
s=s[:start]+'''# Replay must not recompute after master changes, on our own synthetic card only.
with g.transaction("Own1118 change saved-result norm")as q:
 q.execute("update RRL_ARTICULS set NORMA_UKLADKI=0 where ACTICUL=:a",a=data["articles"][0])
try:assert service.auto_prepare(order,data["body"],"admin")["idempotent"]
finally:
 with g.transaction("Own1118 restore saved-result norm")as q:
  q.execute("update RRL_ARTICULS set NORMA_UKLADKI=24 where ACTICUL=:a",a=data["articles"][0])
'''+s[end:]
print(json.dumps({str(p):s},ensure_ascii=True))
