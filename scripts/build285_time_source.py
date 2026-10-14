exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY','RRL_TT_TIME_API',user)from dual");raw=q.fetchone()[0].read()
 raw=raw.replace("\r\n","\n").replace("\r","\n").strip()+"\n/\n"
 body=raw.replace("put('source_contract_version',3)","put('source_contract_version',4)")
 needle="  b.put('members',a);a:=json_array_t();n:=0;"
 assert needle in body
 body=body.replace(needle,"""  b.put('members',a);a:=json_array_t();n:=0;
  for warehouse in(select distinct WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip order by WARE_ID)loop
   declare origin_wire clob;begin
    RRL_WARE_DEPOT_API.material(warehouse.WARE_ID,origin_wire);a.append(json_object_t.parse(origin_wire));
   end;
  end loop;
  b.put('warehouse_origins',a);a:=json_array_t();
""",1)
 out["db/migrations/2026-10-11_ni081_warehouse_depot/004_before_time_body.sql"]=raw
 out["db/migrations/2026-10-11_ni081_warehouse_depot/005_time_body.sql"]=body
 out["db/migrations/2026-10-11_ni081_warehouse_depot/rollback.sql"]="@@004_before_time_body.sql\n"+Path("db/migrations/2026-10-11_ni081_warehouse_depot/rollback.sql").read_text(encoding="utf-8")
print(json.dumps(out,ensure_ascii=True))
