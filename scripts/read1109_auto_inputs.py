exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();r={}
 for table in("RRL_COMPL_SEQ","RRL_COMPL_SEQ_GR"):
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);r[table+"_columns"]=[list(x)for x in q]
 q.execute("select ID,MAXV,MAXM from RRL_COMPL_SEQ_GR order by ID fetch first 20 rows only");r["groups"]=[list(x)for x in q]
 q.execute("select c.CUSTOMER_ORDER_ID,c.WARE_ID,s.ADMISSION_STATUS,s.PREPARATION_HASH,s.PICKING_FINISH_AT from RRL_CUSTOMER_ORDER c join RRL_SAP_STORE_ORDER s on s.CUSTOMER_ORDER_ID=c.CUSTOMER_ORDER_ID where c.CUSTOMER_ORDER_ID between 2044 and 2049 order by c.CUSTOMER_ORDER_ID");r["known_sources"]=[list(x)for x in q]
 q.execute("select ARTICUL,WARE_ID,SEQ_GROUP,SEQ from RRL_COMPL_SEQ where WARE_ID in(select WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID between2044 and2049) fetch first20 rows only");r["known_sequences"]=[list(x)for x in q]
 Path("tmp/read1109_auto_inputs.json").write_text(json.dumps(r,indent=2,default=str),encoding="utf-8")
 print(json.dumps(r,ensure_ascii=True,default=str))
