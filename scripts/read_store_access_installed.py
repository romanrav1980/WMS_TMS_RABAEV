exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib
folder=Path('reports/nicora/2026-10-13/codex/STORE_ACCESS');bundle=Path('db/migrations/2026-10-14_ni022_store_access_dimensions');manifest={'source_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in bundle.glob('*.sql')}}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORE_ACCESS_RULES'and TYPE='PACKAGE BODY'order by LINE");source=''.join(x[0]for x in q.fetchall());assert source.count('leading(inputs) use_nl(p) index(p)')==2;manifest['installed_body_sha256']=hashlib.sha256(source.encode()).hexdigest();manifest['lookup_hints']=2
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STORE_ACCESS_RULES','RRL_TRANSPORT_PLAN_RULES','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD')");manifest['errors']=q.fetchall();assert not manifest['errors']
 q.execute("select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_ACCESS_RULES','RRL_TRANSPORT_PLAN_RULES','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD')order by OBJECT_NAME,OBJECT_TYPE");manifest['objects']=q.fetchall();assert all(x[2]=='VALID'for x in manifest['objects'])
 fixture=json.loads((folder/'native.json').read_text());out=q.var(oracledb.DB_TYPE_CLOB)
 from app.modules.platform.public import read_oracle_json
 q.callproc('RRL_STORE_ACCESS_RULES.check_sts',[fixture['vehicle'],json.dumps([fixture['st_number']]),0,out]);assert read_oracle_json(out.getvalue())['complete'];manifest['readonly_after_cleanup']='PASS no restriction after own limits cleared'
(folder/'installed_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print('PASS installed2hints/current sourcehash/changedobjectsVALID/read-only exactfixture')
