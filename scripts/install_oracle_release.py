"""Install the release into an EMPTY RABAEV; never drop existing objects."""
import argparse, datetime, getpass, hashlib, json, os, re
from pathlib import Path
import oracledb
ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'db/releases/2026-10-14'


def statements(path):
    pending=[];plsql=False
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        t=line.strip()
        if not pending:
            if not t or t.startswith('--') or t.lower().startswith('set ') or t=='/':continue
            plsql=bool(re.match(r'^(create\s+(or\s+replace\s+)?(editionable\s+|noneditionable\s+)?(package|function|procedure|trigger|type)\b|declare\b|begin\b)',t,re.I))
        if plsql and t=='/':
            yield '\n'.join(pending);pending=[];continue
        pending.append(line)
        if not plsql and t.endswith(';'):
            yield '\n'.join(pending).rstrip()[:-1];pending=[]
    if pending and any(x.strip() for x in pending):raise ValueError('Unterminated SQL: '+path.name)


def require(condition, message):
    if not condition:raise RuntimeError(message)


def main():
    p=argparse.ArgumentParser();p.add_argument('--install-empty-rabaev',action='store_true');p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    manifest=json.loads((BUNDLE/'manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        path=BUNDLE/item['path']
        require(hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'], 'Hash mismatch: '+path.name)
        list(statements(path))
    if not a.install_empty_rabaev and not a.verify_only:
        print('Bundle hashes and SQL statement boundaries OK; no database writes.');return
    password=os.environ.get('WMS_ORACLE_PASSWORD') or getpass.getpass('RABAEV database password: ')
    dsn=os.environ['WMS_ORACLE_DSN']
    with oracledb.connect(user='RABAEV',password=password,dsn=dsn) as c:
        c.call_timeout=120000;q=c.cursor()
        q.execute('select user from dual');require(q.fetchone()[0]=='RABAEV','Unexpected schema')
        if a.install_empty_rabaev:
            q.execute("select count(*) from user_objects")
            require(q.fetchone()[0]==0,'REFUSED: RABAEV is not empty; no objects modified')
            admin_password=os.environ.get('NICORA_INITIAL_ADMIN_PASSWORD') or getpass.getpass('Initial application admin password (12+ characters): ')
            require(len(admin_password)>=12 and len(admin_password.encode('utf-8'))<=50,'Password must have 12+ characters and fit 50 UTF-8 bytes')
            for owner,obj,priv in manifest['required_direct_sys_grants']:
                q.execute('select count(*) from user_tab_privs_recd where owner=:o and table_name=:n and privilege=:p',o=owner,n=obj,p=priv)
                require(q.fetchone()[0], 'Missing direct grant: '+priv+' ON '+owner+'.'+obj)
            order=['10_sequences.sql','20_tables.sql','30_indexes.sql','50_packages.sql','51_functions.sql','52_procedures.sql','40_views.sql','53_package_bodies.sql','60_foreign_keys.sql','65_catalogues.sql','66_comments.sql']
            for name in order:
                for sql in statements(BUNDLE/name):
                    try:q.execute(sql)
                    except oracledb.DatabaseError as e:
                        if e.args[0].code!=24344:raise
                        # Cyclic PL/SQL dependencies are checked after all units exist.
                print('Installed',name,flush=True)
            q.execute("begin dbms_utility.compile_schema(schema=>'RABAEV',compile_all=>false); end;")
            # Installation-only seed: fresh empty baseline, not a claimed production cutover.
            q.execute("insert into RRL_STOCK_BASELINE(BASELINE_ID,SNAPSHOT_SCN,CREATED_BY,STATE,MANIFEST_HASH) values ('EMPTY-INSTALL-20261014',dbms_flashback.get_system_change_number,'INSTALL','READY',:h)",h=hashlib.sha256((BUNDLE/'manifest.json').read_bytes()).hexdigest())
            q.execute("insert into RRL_STOCK_RELEASE(RELEASE_ID,STATE,BASELINE_ID,CHANGED_BY) values (1,'ACTIVE','EMPTY-INSTALL-20261014','INSTALL')")
            for i,(kind,key) in enumerate([('RELEASE','STOCK'),('CONFIG','WAREHOUSE')],1):
                q.execute('insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID,POLICY_VERSION) values (RRL_STOCK_LOCK_API.resource_key(:k,:v),:i,1)',k=kind,v=key,i=900000000+i)
            q.execute("insert into USER_GROUP(ID,NAME) values ('GLOBAL_ADMIN','Global Administrator')")
            q.execute("insert into RRL_WARES(ID,NAME,OVERFLOW_CELL_NAME,PREFIX,FAKE_ART,SPIS_IF_HRAN_NO_EMPTY,ORD2) values (1,'Initial warehouse','OVERFLOW','C','Z0001','OVERFLOW',1)")
            q.execute("insert into RUSERS(ID,NAME,PASS,DELETED,PRAVO_ADMIN_LOGIN,USER_GROUP,WARE_ID) values ('admin','Administrator',:p,0,1,'GLOBAL_ADMIN',1)",p=admin_password)
            q.execute("insert into RRL_VERSIONS(VERSION,ALLOW) values ('xp12',1)")
            c.commit()
            for name in ['70_triggers.sql','71_trigger_states.sql']:
                for sql in statements(BUNDLE/name):q.execute(sql)
            q.execute("begin dbms_utility.compile_schema(schema=>'RABAEV',compile_all=>false); end;")
        q.execute("select object_type,object_name from user_objects where (object_name not like 'BIN$%' or object_name in (select index_name from user_indexes where table_name not like 'BIN$%' union all select trigger_name from user_triggers where table_name not like 'BIN$%'))")
        actual=set(q.fetchall());expected={(r['type'],r['name']) for r in manifest['objects'] if r['type'] not in ('LOB','INDEX')}
        missing=sorted(expected-actual)
        q.execute("select object_name,object_type from user_objects where status='INVALID' and object_name not like 'BIN$%'");invalid=q.fetchall()
        q.execute("select setting_value from RRL_SYSTEM_SETTINGS where setting_key='STOCK_LEGACY_TRIGGER_ENABLED'");setting=q.fetchone()
        result={'missing_objects':missing,'invalid_objects':invalid,'compatibility_off':setting==('0',),'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        print(json.dumps(result,indent=2));require(not missing and not invalid and result['compatibility_off'],'Release verification failed')
        print('Oracle release object verification passed.')


if __name__=='__main__':main()
