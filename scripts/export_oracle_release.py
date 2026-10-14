"""Read-only release export: DDL and explicitly selected technical catalogues."""
import datetime, hashlib, json, sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'db/releases/2026-10-14'
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/'api/wms_api_server'))
from app.config import get_settings
s=get_settings()
OUT.mkdir(parents=True,exist_ok=True)
m={'schema':'RABAEV','exported_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'business_data_included':False}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=120000;q=c.cursor()
 q.execute('select user from dual');assert q.fetchone()[0]=='RABAEV'
 inventory="select object_type,object_name,status,last_ddl_time from user_objects where (object_name not like 'BIN$%' or object_name in (select index_name from user_indexes where table_name not like 'BIN$%' union all select trigger_name from user_triggers where table_name not like 'BIN$%')) order by object_type,object_name"
 q.execute(inventory);objects=q.fetchall();assert all(r[2]=='VALID' for r in objects)
 m['objects']=[dict(zip(('type','name','status','last_ddl_time'),r)) for r in objects]
 q.execute("""begin
 dbms_metadata.set_transform_param(dbms_metadata.session_transform,'STORAGE',false);
 dbms_metadata.set_transform_param(dbms_metadata.session_transform,'SEGMENT_ATTRIBUTES',false);
 dbms_metadata.set_transform_param(dbms_metadata.session_transform,'REF_CONSTRAINTS',false);
 dbms_metadata.set_transform_param(dbms_metadata.session_transform,'SQLTERMINATOR',true);
 end;""")
 q.execute("select index_name from user_indexes where index_type='LOB' union select index_name from user_constraints where constraint_type in ('P','U') and index_name is not null")
 implicit={r[0] for r in q}
 for filename,kind in [('10_sequences','SEQUENCE'),('20_tables','TABLE'),('30_indexes','INDEX'),('40_views','VIEW'),('50_packages','PACKAGE'),('51_functions','FUNCTION'),('52_procedures','PROCEDURE'),('53_package_bodies','PACKAGE BODY'),('70_triggers','TRIGGER')]:
  parts=['set define off\n'];names=[n for t,n,_,_ in objects if t==kind and not(kind=='INDEX' and n in implicit)]
  for name in names:
   if kind in ('PACKAGE','PACKAGE BODY','PROCEDURE','FUNCTION','TRIGGER'):
    q.execute('select text from user_source where type=:t and name=:n order by line',t=kind,n=name)
    source=''.join(r[0] for r in q).rstrip()
    if kind=='TRIGGER':
     import re
     source=re.sub(r'^\s*trigger\s+(?:"[^"]+"\.)?(?:"[^"]+"|[^\s]+)',lambda _: 'TRIGGER "RABAEV"."'+name+'"',source,count=1,flags=re.I)
    ddl='CREATE OR REPLACE '+source+'\n/\n'
   else:
    q.execute('select dbms_metadata.get_ddl(:t,:n,user) from dual',t=kind,n=name);ddl=q.fetchone()[0].read()
   parts.append(ddl+'\n')
  (OUT/(filename+'.sql')).write_text('\n'.join(parts),encoding='utf-8',newline='\n');print(filename,len(names),flush=True)
 q.execute("select constraint_name from user_constraints where constraint_type='R' order by constraint_name")
 names=[r[0] for r in q];parts=['set define off\n']
 for name in names:
  q.execute("select dbms_metadata.get_ddl('REF_CONSTRAINT',:n,user) from dual",n=name);parts.append(q.fetchone()[0].read())
 (OUT/'60_foreign_keys.sql').write_text('\n'.join(parts),encoding='utf-8',newline='\n')
 q.execute('select trigger_name,status from user_triggers order by trigger_name')
 (OUT/'71_trigger_states.sql').write_text('\n'.join('ALTER TRIGGER "RABAEV"."'+n+'" '+('ENABLE' if st=='ENABLED' else 'DISABLE')+';' for n,st in q)+'\n',encoding='utf-8',newline='\n')
 q.execute("select owner,table_name,privilege from user_tab_privs_recd where owner='SYS' order by table_name,privilege")
 m['required_direct_sys_grants']=[list(r) for r in q]
 q.execute("select distinct referenced_owner,referenced_name from user_dependencies where referenced_owner not in ('SYS','PUBLIC','SYSTEM','RABAEV')")
 m['external_compile_dependencies']=[list(r) for r in q]
 q.execute("select namespace,schema,package from all_context where schema='RABAEV'")
 (OUT/'05_contexts.sql').write_text('\n'.join('CREATE OR REPLACE CONTEXT "'+n+'" USING "'+o+'"."'+p+'";' for n,o,p in q)+'\n',encoding='utf-8',newline='\n')
 parts=['set define off\n'];m['catalogue_rows']={}
 def lit(v):
  if v is None:return 'NULL'
  if isinstance(v,datetime.datetime):return "TO_TIMESTAMP('"+v.strftime('%Y-%m-%d %H:%M:%S.%f')+"','YYYY-MM-DD HH24:MI:SS.FF6')"
  if isinstance(v,(int,float)):return str(v)
  if isinstance(v,str):return "'"+v.replace("'","''")+"'"
  raise TypeError(type(v).__name__)
 for table in ('RRL_RESOURCE_TYPE','RRL_PALLET_TYPE','RRL_TYPE_PALL','RRL_TRANSPORT_TYPE','RRL_VEHICLE_TYPE'):
  q.execute('select * from '+table);cols=[d[0] for d in q.description];rows=q.fetchall();m['catalogue_rows'][table]=len(rows)
  for row in rows:parts.append('INSERT INTO '+table+' ('+','.join('"'+v+'"' for v in cols)+') VALUES ('+','.join(lit(v) for v in row)+');')
 parts.append("INSERT INTO RRL_SYSTEM_SETTINGS (SETTING_KEY,SETTING_VALUE,DESCRIPTION) VALUES ('STOCK_LEGACY_TRIGGER_ENABLED','0','Compatibility disabled; explicit stock commands only');\nCOMMIT;")
 (OUT/'65_catalogues.sql').write_text('\n'.join(parts)+'\n',encoding='utf-8',newline='\n')
 q.execute(inventory);assert q.fetchall()==objects,'DDL changed during export; retry when writers idle'
for sql_file in OUT.glob('*.sql'):
 sql_file.write_bytes(sql_file.read_bytes().replace(b'\r',b''))
m['files']=[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(OUT.glob('*.sql'))]
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8',newline='\n')
print('Export complete',len(objects),'objects')
