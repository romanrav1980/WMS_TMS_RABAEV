exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY','RRL_TT_TIME_API',user)from dual");raw=q.fetchone()[0].read()
 raw=raw.replace("\r\n","\n").replace("\r","\n").strip()+"\n/\n"
 sbody=raw
 old="ID,ST_NUMBER,WARE_ID,CONDITION,PALLET_UID"
 assert old in sbody
 sbody=sbody.replace(old,old+",ADDR,STDATE,ORD",1)
 sbody=sbody.replace("b.put('source_contract_version',2);","b.put('source_contract_version',3);",1)
 needle="o.put('pallet_identifier',member.PALLET_UID);a.append(o);"
 assert needle in sbody
 sbody=sbody.replace(needle,"o.put('pallet_identifier',member.PALLET_UID);o.put('address',member.ADDR);o.put('st_date',to_char(member.STDATE,'YYYY-MM-DD HH24:MI:SS'));o.put('route_ordinal',member.ORD);a.append(o);",1)
 assert sbody!=raw
 out["db/migrations/2026-10-11_ni081_route_material_v3/000_before_body.sql"]=raw
 out["db/migrations/2026-10-11_ni081_route_material_v3/001_body.sql"]=sbody
 out["db/migrations/2026-10-11_ni081_route_material_v3/rollback.sql"]="@@000_before_body.sql\n"
print(json.dumps(out,ensure_ascii=True))
