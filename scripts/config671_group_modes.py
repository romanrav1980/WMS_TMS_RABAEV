exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
first=json.loads(Path("tmp/context669.json").read_text());second=json.loads(Path("tmp/context670.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  for ctx,system,mode in((first,"EGAIS","BOX"),(second,"CRPT","PALLET")):
   q.execute("update RRL_SKU_RECEIPT_PROFILE set SCAN_MODE=:p_mode where ARTICUL=:article and SYSTEM_CODE=:p_system",p_mode=mode,article=ctx["article"],p_system=system);assert q.rowcount==1
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
print("Private source cards: mixed UNIT_OR + BOX / separate SKU PALLET; no stock changes")
