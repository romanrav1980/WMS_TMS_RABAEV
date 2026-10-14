exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_WAVE_LAUNCH_CMD'and TYPE='PACKAGE BODY'and LINE<=65 order by LINE")
 print("".join(x[0]for x in q))
 q.execute("select CUSTOMER_ORDER_ROW_ID,ARTICUL,UNIT_CODE from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=2135");print(json.dumps({"order_rows":q.fetchall()}))
 q.execute("select UID_PALLET,ARTICUL from RRL_PALLETS where UID_PALLET like 'B01.1238:%'");print(json.dumps({"pallets":q.fetchall()}))
 q.execute("select ARTICUL,INPUT_UOM,BASE_UOM,NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION where upper(ARTICUL) like 'QAUTOC0C2A00C0B%'");print(json.dumps({"uom":q.fetchall()}))
