exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor();result={}
 for name,sql in [
 ('history',"select count(*) from RRL_QC_SCOPE_CHANGE where OPERATION_ID='QC.SCOPE:0c5816cc-22ed-4ef3-a904-612a248f6b0d'"),
 ('rule','select RULE_VERSION,ACTIVE_FLAG from RRL_QC_SCOPE_RULE where WARE_ID=6524567'),
 ('stock',"select sum(REMAIN) from RRL_REMAINS where UID_POLETA='LEGACY.SAP.688:e0ef17c2c03b427b9c5fc58d852c71a3'"),
 ('sql',"select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%' and (upper(SQL_TEXT) like '%FROM RRL_QC_SCOPE_RULE%' or upper(SQL_TEXT) like '%FROM RRL_QC_SCOPE_CHANGE%') order by ELAPSED_TIME desc fetch first 8 rows only")]:
  q.execute(sql);result[name]=q.fetchall()
 assert result['history']==[(1,)] and result['rule']==[(3,0)] and result['stock']==[(3,)],result
 Path('tmp/result1465.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
