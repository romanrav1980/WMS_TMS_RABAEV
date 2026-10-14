exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};f="db/migrations/2026-10-11_ni081_trip_time/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();parts=[]
 for kind in["PACKAGE","PACKAGE BODY"]:
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_EDIT_API'and TYPE=:kind order by LINE",kind=kind)
  parts.append("create or replace "+"".join(r[0]for r in q.fetchall()).strip()+"\n/\n")
 source="\n".join(parts);out[f+"000_before_rrl_transport_edit_api.sql"]=source
 old="update RRL_TRANSPORT_TASK set USER_ID=p_actor where ID=p_trip"
 assert source.count(old)==1
 out[f+"004_create_status.sql"]=source.replace(old,"update RRL_TRANSPORT_TASK set USER_ID=p_actor,CONDITION='Спланирован' where ID=p_trip")
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRASPORT_TASK_ADD'order by LINE")
 legacy="".join(r[0]for r in q.fetchall())
 out[f+"000_legacy_add_evidence.sql"]=legacy
print(json.dumps(out,ensure_ascii=True))
