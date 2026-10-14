exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};root="db/migrations/2026-10-11_ni022_multi_st/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 pieces=[]
 for kind in ("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_API'and TYPE=:kind order by LINE",kind=kind)
  pieces.append("create or replace "+"".join(row[0]for row in q)+"\n/\n")
 original="\n".join(pieces).replace("\r\n","\n")
old="""v_requested_number:=v_requested.get_string(i);select CONDITION into v_requested_state from RRL_SBORKA_PALLETS where ST_NUMBER=v_requested_number;
    if nvl(v_requested_state,0)!=2 then v_writable.append(v_requested.get_string(i));end if;"""
assert old in original,"Current native body drift, do not replace other revisions"
new="""v_requested_number:=v_requested.get_string(i);
    select count(case when CONDITION=2 then 1 end),
           count(case when nvl(TRANSTASK_ID,0)!=p_tt then 1 end)
     into v_requested_state,v_requested_unassigned from RRL_SBORKA_PALLETS where ST_NUMBER=v_requested_number;
    if v_requested_state>0 then
     if v_requested_unassigned>0 then raise_application_error(-20886,'PLAN_PARTIALLY_LOADED_ST_FROZEN');end if;
     -- Keep every already assigned row of a partly loaded ST intact. The legacy writer addresses the whole ST.
    else v_writable.append(v_requested_number);end if;"""
updated=original.replace("v_requested_state number;","v_requested_state number;v_requested_unassigned number;",1).replace(old,new,1)
out[root+"000_before.sql"]=original;out[root+"001_assignment.sql"]=updated
out[root+"apply.sql"]="@001_assignment.sql\n"
out[root+"rollback.sql"]="@000_before.sql\n"
print(json.dumps(out,ensure_ascii=True))
