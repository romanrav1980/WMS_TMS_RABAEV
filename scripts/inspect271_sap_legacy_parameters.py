exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select m.ARTICUL,m.BASE_UOM,m.SENDER,a.CELL,a.COUNT_SHT_IN_KOR,a.BRUTTO_WEIGHT_OF_KOR,a.DIMKOR_X,a.DIMKOR_Y,a.DIMKOR_Z,x.WARE_ID from RRL_SAP_ARTICLE_META m join RRL_ARTICULS a on a.ACTICUL=m.ARTICUL join RRL_CELLS x on x.CELL=a.CELL where a.COUNT_SHT_IN_KOR>0 and a.BRUTTO_WEIGHT_OF_KOR>0 and a.DIMKOR_X*a.DIMKOR_Y*a.DIMKOR_Z>0 fetch first 5 rows only")
 print("READY_SAP_ARTICLES",json.dumps(q.fetchall(),default=str,ensure_ascii=True))
 q.execute("select ARTICUL,BASE_UOM,SENDER from RRL_SAP_ARTICLE_META where ARTICUL='QPOOL2e9b6614d9'");print("POOL_META",json.dumps(q.fetchall()))
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_STORE_MAP'order by COLUMN_ID");print("MAP_COLS",q.fetchall())
