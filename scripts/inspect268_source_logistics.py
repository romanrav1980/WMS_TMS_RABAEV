exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for name,sql in [
 ("owned_source","select r.ARTICUL,r.ORDER_QTY,r.UNIT_CODE,c.WARE_ID from RRL_CUSTOMER_ORDER_ROW r join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=r.CUSTOMER_ORDER_ID where c.CUSTOMER_ORDER_ID=2044"),
 ("article","select a.ACTICUL,a.CELL,a.COUNT_SHT_IN_KOR,a.BRUTTO_WEIGHT_OF_KOR,a.DIMKOR_X,a.DIMKOR_Y,a.DIMKOR_Z,a.ROUND_TO,x.WARE_ID from RRL_ARTICULS a left join RRL_CELLS x on x.CELL=a.CELL where a.ACTICUL='QPB1991E8D6E32'"),
 ("owned_cells","select CELL,CELL_TYPE,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS from RRL_CELLS where WARE_ID=5265051 fetch first 12 rows only"),
 ("logistics_available","select a.ACTICUL,a.COUNT_SHT_IN_KOR,a.BRUTTO_WEIGHT_OF_KOR,a.DIMKOR_X,a.DIMKOR_Y,a.DIMKOR_Z,x.WARE_ID from RRL_ARTICULS a join RRL_CELLS x on x.CELL=a.CELL where a.COUNT_SHT_IN_KOR>0 and a.BRUTTO_WEIGHT_OF_KOR>0 and a.DIMKOR_X*a.DIMKOR_Y*a.DIMKOR_Z>0 fetch first 3 rows only")]:
  try:q.execute(sql);print(name,json.dumps(q.fetchall(),default=str))
  except oracledb.DatabaseError as e:print(name,str(e))
