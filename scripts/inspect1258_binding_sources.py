exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TEXT like '%PICK_PALLET_BIND_SHIPMENT%' order by LINE")
 print(json.dumps(q.fetchall()))
 q.execute("select OBJECT_NAME from USER_OBJECTS where OBJECT_TYPE='PACKAGE'and (OBJECT_NAME like '%PALLET%SHIP%'or OBJECT_NAME like '%FULLPAL%')");print(json.dumps(q.fetchall()))
 q.execute("select ID,PALLET_UID,ST_NUMBER,TRANSTASK_ID from RRL_SBORKA_PALLETS where ID in(641507,641508)");print(json.dumps(q.fetchall()))
 q.execute("select PALLET_UID,ARTICUL,QUANTITY from RRL_SBORKA_PALLET_ROWS where PALLET_UID in('OP_SAP_2135_1','OP_SAP_2135_2')");print(json.dumps(q.fetchall()))
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,130)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(lower(SQL_TEXT) like '%cell_pallets%'or lower(SQL_TEXT) like '%current_pallets%')
 order by LAST_ACTIVE_TIME desc fetch first 6 rows only""");print(json.dumps({"placement_sql":q.fetchall()}))
