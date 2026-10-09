"""Checkpoint the three terminal inventory functions and prepare fixed adapters."""
import json
import re
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment

ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings(); files={}; old_sources=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
    q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
    if q.fetchone()!=("RABAEV","orcl"): raise RuntimeError("Unexpected target")
    q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if q.fetchone()!=("PREPARED",):raise RuntimeError("Preparation requires PREPARED")
    for number in (2,3,4):
        name=f"RRL_INV_CREATE_LINE{number}"
        q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='FUNCTION' order by LINE",n=name)
        source="".join(row[0] for row in q)
        if not source or "RRL_STOCK_INV_ENTRY" in source:raise RuntimeError("Expected original "+name)
        files[f"137_inventory_{number}_rollback.sql"]="create or replace "+source.rstrip()+"\n/\n"
        old=re.sub(r"\b"+name+r"\b",name+"_SP_OLD",source,flags=re.I)
        old=re.sub(r"RETURN\s+varchar2\s+IS",f"RETURN varchar2 accessible by(function {name}) IS",old,count=1,flags=re.I)
        if "accessible by" not in old:raise RuntimeError("Restricted declaration not located")
        old=re.sub(r"--[^\r\n]*","",old)
        old_sources.append("create or replace "+old.rstrip()+"\n/\n")
        if number==2:
            args="cell1 varchar2,shk_art varchar2,articul_part varchar2,count1 number,p_revision_id number default null,p_expiry date default null,p_actor varchar2 default null,p_operation_id varchar2 default null"
            legacy_args="cell1,shk_art,articul_part,count1"
            doc="p_revision_id";expiry="p_expiry"
        elif number==3:
            args="cell1 varchar2,shk_art varchar2,articul_part varchar2,count1 number,UID_DOC int,p_expiry date default null,p_actor varchar2 default null,p_operation_id varchar2 default null"
            legacy_args="cell1,shk_art,articul_part,count1,UID_DOC"
            doc="UID_DOC";expiry="p_expiry"
        else:
            args="cell1 varchar2,shk_art varchar2,articul_part varchar2,count1 number,UID_DOC int,expiury_date date,p_actor varchar2 default null,p_operation_id varchar2 default null"
            legacy_args="cell1,shk_art,articul_part,count1,UID_DOC,expiury_date"
            doc="UID_DOC";expiry="expiury_date"
        files[f"137_inventory_{number}_entrypoint.sql"]=f"""create or replace function {name}({args}) return varchar2 authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return {name}_SP_OLD({legacy_args});end if;
 return RRL_STOCK_INV_ENTRY.register_line(cell1,shk_art,articul_part,count1,{doc},{expiry},p_actor,p_operation_id);
end;
/
"""
files["137_inventory_legacy.sql"]="\n".join(old_sources)
print(json.dumps(files,ensure_ascii=True))
