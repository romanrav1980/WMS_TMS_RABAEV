exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select s.ORDER_ID,s.ORDER_NUMBER,l.LINE_NUMBER,l.ARTICUL,l.PLANNED_QTY,
  (select nvl(sum(POSTED_BASE_QTY),0)from RRL_SAP_PALLET_RECEIPT rec where rec.ORDER_ID=l.ORDER_ID and rec.LINE_NUMBER=l.LINE_NUMBER) POSTED,
  (select nvl(sum(UNIT_COUNT),0)from RRL_PALLETS p where p.PRIHOD_NAKLAD_ID=s.NAKLAD_ID and p.ARTICUL=l.ARTICUL) LEGACY_PALLET
  from RRL_SAP_SUPPLY_LINE l join RRL_SAP_SUPPLY_ORDER s on s.ORDER_ID=l.ORDER_ID
  where l.ARTICUL=:a order by s.UPDATED_AT desc fetch first 6 rows only""",a="QIW6696207F7B382");print(q.fetchall())
 q.execute("select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY'and TEXT like '%POSTED_BASE_QTY%' order by NAME,LINE");print("POSTED_USES",q.fetchall()[:30])
