exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_WMS_RECEIPT_AGG","RRL_REGULATORY_JOURNAL"]:
  q.execute("select column_name,data_type,data_length from user_tab_columns where table_name=:t order by column_id",t=table)
  print(table,q.fetchall())
 q.execute("select a.system_code,a.profile_code,a.code_hash,a.uid_pallet,a.agg_level from RRL_WMS_RECEIPT_AGG a where a.uid_pallet='100007031097593489'")
 print("FIXTURE",q.fetchall())
