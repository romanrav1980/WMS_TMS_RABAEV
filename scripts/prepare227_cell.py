exec(open("scripts/inspect226.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_CELLS where CELL='QO22513508027ed'")
 if not q.fetchone()[0]:
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:
   q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values('QO22513508027ed',51365792,0,0,0,0,0,0,0,0,0,0)")
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL','QO22513508027ed'),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD")
   c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 print("Own227 outbound fixture cell prepared, existing target trip/dock retained")
