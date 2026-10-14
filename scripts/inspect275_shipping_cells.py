exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_CASE_PICK_TASK","RRL_CASE_CARRIER_LOT","RRL_PALLETS","RRL_TOPOLOGY_CELL"]:
  q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME=:table_name order by COLUMN_ID",table_name=table);print(table,[r[0]for r in q])
 q.execute("select WARE_ID,max(TOPOLOGY_ID),count(*)from RRL_WAREHOUSE_TOPOLOGY where STATUS='PUBLISHED'group by WARE_ID fetch first 6 rows only");print("PUBLISHED",q.fetchall())
 q.execute("select WARE_ID,CELL_KIND,count(*)from RRL_TOPOLOGY_CELL where ACTIVE=1 and CELL_KIND in('TRANSPORT_STAGING','GATE')group by WARE_ID,CELL_KIND fetch first 8 rows only");print("STAGING",q.fetchall())
