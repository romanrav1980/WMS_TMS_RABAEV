exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
result={}
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=90)as client:
 def read(name,params):
  started=time.perf_counter();r=client.get('/api/admin/transport/available-sts',params=params);r.raise_for_status();rows=r.json();result[name]={'seconds':round(time.perf_counter()-started,3),'count':len(rows)};return rows
 base={'unassigned_only':'false','ware_id':9807}
 full=read('scoped_full',base)
 pages=[]
 for page in range(1,4):pages.extend(read('scoped_page'+str(page),{**base,'page':page,'page_size':2}))
 assert pages==full[:6], 'SQL pages differ from unpaged slice'
 assert not any('PAGE_ROW_NUMBER'in row for row in pages)
 bounded=read('all_page200',{'unassigned_only':'false','page_size':200})
 assert len(bounded)<=200
 empty=read('empty',{'ware_id':9807,'st_mask':'NO_SUCH_1376','page_size':2});assert empty==[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT like 'select * from (select page_rows.%' order by LAST_ACTIVE_TIME desc fetch first 5 rows only""");result['sql']=q.fetchall()
print(json.dumps(result,default=str));Path('tmp/result1376.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')