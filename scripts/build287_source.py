exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};base="db/migrations/2026-10-11_ni081_delivery_windows/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY','RRL_TT_TIME_API',user)from dual")
 raw=q.fetchone()[0].read().replace("\r\n","\n").replace("\r","\n").strip()+"\n/\n"
 body=raw.replace("put('source_contract_version',4)","put('source_contract_version',5)")
 body=body.replace("PALLET_UID,ADDR,STDATE,ORD from RRL_SBORKA_PALLETS","PALLET_UID,ADDR,STDATE,ORD,ZONE_TIME_PLAN_IN,ZONE_TIME_PLAN_OUT from RRL_SBORKA_PALLETS")
 needle="o.put('route_ordinal',member.ORD);a.append(o);"
 assert needle in body
 body=body.replace(needle,"o.put('route_ordinal',member.ORD);o.put('delivery_window_from',to_char(member.ZONE_TIME_PLAN_IN,'YYYY-MM-DD HH24:MI:SS'));o.put('delivery_window_to',to_char(member.ZONE_TIME_PLAN_OUT,'YYYY-MM-DD HH24:MI:SS'));a.append(o);")
 needle="  b.put('warehouse_origins',a);a:=json_array_t();"
 assert needle in body
 body=body.replace(needle,needle+"""
  n:=0;
  for destination in(select ADDR,count(*) ADDRESS_COUNT,min(UNLOAD_NORM_MIN) UNLOAD_NORM_MIN,min(TW_STRICT) TW_STRICT,min(SHIROTA) LATITUDE,min(DOLGOTA) LONGITUDE
    from RRL_ADDR where nvl(DELETED3,0)=0 and ADDR in(select ADDR from RRL_SBORKA_PALLETS where TRANSTASK_ID=p_trip)
    group by ADDR order by ADDR fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'TT_TIME_DESTINATION_BOUND_200');end if;
   o:=json_object_t();o.put('address',destination.ADDR);o.put('address_count',destination.ADDRESS_COUNT);
   o.put('unload_norm_min',destination.UNLOAD_NORM_MIN);o.put('window_strict',destination.TW_STRICT);
   o.put('latitude',destination.LATITUDE);o.put('longitude',destination.LONGITUDE);a.append(o);
  end loop;
  b.put('destination_rules',a);a:=json_array_t();n:=0;
""")
 out[base+"000_before_body.sql"]=raw;out[base+"001_body.sql"]=body;out[base+"rollback.sql"]="@@000_before_body.sql\n"
print(json.dumps(out,ensure_ascii=True))
