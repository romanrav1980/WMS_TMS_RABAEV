"""Build a bounded command around the existing native wave launch."""
import sys
import json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"db/migrations/2026-10-08_stock_posting_core"
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
    with c.cursor() as q:
        q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if q.fetchone()[0]!="PREPARED": raise RuntimeError("Requires dormant release")
        parts=[]
        for t in ("PACKAGE","PACKAGE BODY"):
            q.execute("select TEXT from USER_SOURCE where NAME='RRL_PICK_WAVE_API' and TYPE=:t order by LINE",t=t)
            text="create or replace "+"".join(r[0] for r in q).rstrip()+"\n/\n"
            parts.append(text)
old="\n".join(parts).replace("RRL_PICK_WAVE_API","RRL_PICK_WAVE_META")
old=old.replace("authid definer as","authid definer accessible by(package RRL_STOCK_WAVE_LAUNCH_CMD,package RRL_PICK_WAVE_API) as",1)
# Keep launch body as the fixed metadata implementation, without any public callback.
a=old.lower().index("  procedure launch_wave(",old.lower().index("package body"))
b=old.lower().index("  begin",a)
old=old[:b]+old[b:].replace("  begin","  begin\n    if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null then raise_application_error(-20863,'WAVE_LAUNCH_REQUIRES_POSTING_CONTEXT');end if;",1)

public="\n".join(parts)
a=public.lower().index("  procedure launch_wave(",public.lower().index("package body"))
b=public.lower().index("  begin",a)
public=public[:b]+public[b:].replace("  begin",'''  begin
    declare
      st varchar2(20);j json_object_t:=json_object_t();src json_object_t:=json_object_t();result clob;
    begin
      select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
      if st='ACTIVE' then
        j.put('contract_version',2);j.put('operation_id','WAVE.LAUNCH:'||to_char(p_pick_wave_id,'TM9'));
        j.put('command_type','WAVE_LAUNCH');j.put('actor',p_launched_by);
        src.put('wave_id',p_pick_wave_id);j.put('source',src);j.put('lines',json_array_t());
        j.put('units',json_array_t());j.put('metadata',json_object_t());
        RRL_STOCK_NATIVE_API.post(j.to_clob,p_launched_by,result);return;
      end if;
    end;
''',1)
print(json.dumps({"db/migrations/2026-10-08_stock_posting_core/105_wave_metadata.sql":old,"db/migrations/2026-10-08_stock_posting_core/107_native_wave_api.sql":public}, ensure_ascii=True))
