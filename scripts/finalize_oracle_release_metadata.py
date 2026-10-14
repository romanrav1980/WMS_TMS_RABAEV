from pathlib import Path
import sys,json,hashlib,importlib.metadata as md
from packaging.requirements import Requirement
sys.path.insert(0,str(Path('scripts').resolve()))
exec(Path('scripts/ni063_slow_queries.py').read_text(encoding='utf-8').split('with oracledb.connect',1)[0])
out=Path('db/releases/2026-10-14');m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
parts=['set define off'];bad=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for kind,query in [('TABLE',"select table_name,null,comments from user_tab_comments where comments is not null and table_name not like 'BIN$%'"),('COLUMN',"select table_name,column_name,comments from user_col_comments where comments is not null and table_name not like 'BIN$%'")]:
  q.execute(query)
  for t,col,comment in q:
   if '\ufffd' in comment:bad.append([t,col]);continue
   target='"RABAEV"."'+t+'"'+('."'+col+'"' if col else '')
   parts.append('COMMENT ON '+kind+' '+target+" IS '"+comment.replace("'","''")+"';")
 m['omitted_corrupt_comments']=bad
 m['other_object_counts']={}
 for view in ['USER_JOBS','USER_SCHEDULER_JOBS','USER_DB_LINKS','USER_SYNONYMS','USER_MVIEWS']:
  q.execute('select count(*) from '+view);m['other_object_counts'][view]=q.fetchone()[0]
(out/'66_comments.sql').write_text('\n'.join(parts)+'\n',encoding='utf-8',newline='\n')
for sql_file in out.glob('*.sql'):
 sql_file.write_bytes(sql_file.read_bytes().replace(b'\r',b''))
m['files']=[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(out.glob('*.sql'))]
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
queue=['fastapi','sqlalchemy','oracledb','uvicorn','openpyxl','httpx','Pillow','ortools'];versions={}
while queue:
 name=queue.pop();dist=md.distribution(name);key=dist.metadata['Name']
 if key in versions:continue
 versions[key]=dist.version
 for text in dist.requires or []:
  r=Requirement(text)
  if r.marker is None or r.marker.evaluate({'extra':''}):queue.append(r.name)
Path('api/wms_api_server/requirements-release-20261014.txt').write_text('# Observed Python 3.13.3 / Windows dependency closure; npm uses package-lock.json.\n'+'\n'.join(k+'=='+v for k,v in sorted(versions.items(),key=lambda x:x[0].lower()))+'\n',encoding='utf-8',newline='\n')
print('comments',len(parts)-1,'damaged omitted',len(bad),'pinned packages',len(versions))
