import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni043_aggregation_lifecycle")
p=d/"001_lifecycle.sql";s=p.read_text(encoding="utf-8")
s=s.replace(" procedure assert_write;\nend;"," procedure assert_write;\n procedure assert_scan(p_system varchar2,p_profile varchar2,p_hash varchar2);\nend;")
s=s.replace(" function invalidate(p_operation varchar2,p_request clob,p_actor varchar2)return clob is",""" procedure assert_scan(p_system varchar2,p_profile varchar2,p_hash varchar2)is n number;begin
 select count(*)into n from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=p_system and PROFILE_CODE=p_profile and CODE_HASH=p_hash;
 if n!=0 then raise_application_error(-20886,'INTERWARE_LOCAL_AGGREGATION_INVALIDATED');end if;
 end;
 function invalidate(p_operation varchar2,p_request clob,p_actor varchar2)return clob is""")
p2=d/"002_scan_guard.sql";scan=p2.read_text(encoding="utf-8")
old="""select count(*)into n from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=v_system_code and PROFILE_CODE=v_profile_code and CODE_HASH=v_digest;
 if n!=0 then raise_application_error(-20886,'INTERWARE_LOCAL_AGGREGATION_INVALIDATED');end if;"""
assert scan.count(old)==1;scan=scan.replace(old,"RRL_TRACE_AGG_LIFECYCLE.assert_scan(v_system_code,v_profile_code,v_digest);")
print(json.dumps({str(p):s,str(p2):scan}))
