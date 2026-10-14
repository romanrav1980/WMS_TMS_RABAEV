exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
root=Path("db/migrations/2026-10-12_ni072_shipping_inspection")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where OBJECT_NAME in('RRL_DAY_INSPECTION','RRL_DAY_INSPECT_API','RRL_DAY_INSPECT_GUARD')");objects=q.fetchall()
 if objects:raise RuntimeError("Existing inspection objects: do not blindly reapply schema")
 q.execute("select count(*)from RIGHTS where upper(RIGHT1)='WAREHOUSE_DAY_INSPECT'and USER_GROUP='GLOBAL_ADMIN'");prior_permission=int(q.fetchone()[0])
checkpoint=dict(schema="RABAEV",service="127.0.0.1:1521/orcl",before_objects=objects,prior_global_permission_rows=prior_permission,recovery="empty additive metadata rollback; nonempty history blocks rollback",sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in root.glob("*.sql")})
(root/"checkpoint.json").write_text(json.dumps(checkpoint,indent=2)+"\n",encoding="utf-8")
if prior_permission:
 p=root/"rollback.sql";p.write_text(p.read_text(encoding="utf-8").replace(" delete from RIGHTS where upper(RIGHT1)='WAREHOUSE_DAY_INSPECT'and USER_GROUP='GLOBAL_ADMIN';"," -- Preserve pre-existing permission rows."),encoding="utf-8")
print("694 inspection additive source checkpoint captured; no stock writes")
