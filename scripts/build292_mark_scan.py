exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};base="db/migrations/2026-10-11_ni061_marked_partial/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_INTERWARE_MARK_SCAN'and TYPE='PACKAGE BODY'order by LINE")
 old="create or replace "+"".join(r[0]for r in q)+"\n/\n";out[base+"000_before_mark_scan.sql"]=old
 body=old.replace("scans_clob clob;v_key","scans_clob clob;selected_clob clob;v_key")
 needle="   v_uid:=l.get_string('uid');"
 assert needle in body;body=body.replace(needle,"   selected_clob:=null;if l.has('selected_unit_keys')then selected_clob:=l.get_array('selected_unit_keys').to_clob;end if;\n"+needle,1)
 needle="u.STOCK_STATUS='ISSUED' and u.BASE_UOM=v_base"
 assert body.count(needle)==1
 filter=" and(selected_clob is null or exists(select 1 from json_table(selected_clob,'$[*]'columns(K varchar2(64)path '$'))chosen where chosen.K=u.PHYSICAL_UNIT_KEY))"
 body=body.replace(needle,needle+filter,1)
 needle="where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS='ISSUED' and BASE_UOM=v_base;"
 assert needle in body
 body=body.replace(needle,"where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS='ISSUED' and BASE_UOM=v_base and(selected_clob is null or exists(select 1 from json_table(selected_clob,'$[*]'columns(K varchar2(64)path '$'))chosen where chosen.K=PHYSICAL_UNIT_KEY));",1)
 out[base+"004_mark_scan.sql"]=body
print(json.dumps(out,ensure_ascii=True))
