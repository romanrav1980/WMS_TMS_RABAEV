exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_STORE_RETURN_HANDOVER","RRL_STORE_RETURN_PICKUP","RRL_STORE_RETURN_RECEIPT","RRL_STORE_RETURN_PLACEMENT","RRL_STORE_RETURN_DISPOSAL","RRL_STORE_RETURN_SUP_DISPATCH"]:
  q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);print(table,[r[0]for r in q])
 q.execute("select a.RECEIPT_OPERATION_ID,a.OPERATION_ID,a.DISPOSITION,s.WARE_ID from RRL_STORE_RETURN_APPROVAL a left join RRL_STORE_RETURN_SAP s on s.APPROVAL_OPERATION_ID=a.OPERATION_ID order by a.APPROVED_AT desc fetch first 6 rows only");print(json.dumps(q.fetchall(),default=str))
