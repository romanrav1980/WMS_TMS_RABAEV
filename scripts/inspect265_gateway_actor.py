exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,DELETED,WARE_ID,USER_GROUP,RRL_HAS_WRIGHT(ID,'sap_store_order_import'),RRL_HAS_WRIGHT(ID,'sap_article_import')from RUSERS where ID='SAP_FILE_GATEWAY'");print("GATEWAY_ACTOR",q.fetchall())
