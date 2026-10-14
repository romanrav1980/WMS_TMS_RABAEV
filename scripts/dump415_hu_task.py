exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
files={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ['RRL_STOCK_HU_TASK','RRL_STOCK_INTERWARE_PUT']:
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE='PACKAGE BODY'order by LINE",name=name)
  files['tmp/native415_'+name.lower()+'.sql']='create or replace '+'\n'.join(x[0].rstrip('\r\n')for x in q)+'\n/\n'
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,150)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%RRL_IW_GROUP%'or SQL_TEXT like 'SELECT%RRL_WMS_RECEIPT_CODE%')order by ELAPSED_TIME desc fetch first 8 rows only")
 files['tmp/slow415.json']=json.dumps(q.fetchall(),default=str)
print(json.dumps(files))
