"""Checkpoint live article package; preserve pack versions and remove implicit moves."""
import json,re,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment();sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();sources={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as conn:
 cur=conn.cursor();cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if cur.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if cur.fetchone()!=("PREPARED",):raise RuntimeError("Dormant preparation only")
 for kind in ("PACKAGE","PACKAGE BODY"):
  cur.execute("select TEXT from USER_SOURCE where NAME='ARTICULS' and TYPE=:t order by LINE",t=kind)
  sources[kind]="".join(row[0] for row in cur)
cp=ROOT/"runtime/stock_posting_20261008/174_article-original-checkpoint";cp.mkdir(parents=True,exist_ok=False)
for kind,source in sources.items():
 (cp/(kind.replace(" ","_")+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
def ascii_source(source):
 source=re.sub(r"--[^\r\n]*","",source)
 def string(m):
  literal=m.group()
  if all(ord(c)<128 for c in literal):return literal
  value=literal[1:-1].replace("''","'")
  value="".join(c if ord(c)<128 and c!="\\" else "\\"+format(ord(c),"04x") for c in value)
  return "unistr('"+value.replace("'","''")+"')"
 return re.sub(r"'(?:[^']|'')*'",string,source)
spec=ascii_source(sources["PACKAGE"]);body=ascii_source(sources["PACKAGE BODY"])
oldspec=re.sub(r"\bARTICULS\b","ARTICULS_SP_OLD",spec,flags=re.I)
oldspec=re.sub(r"(package\s+ARTICULS_SP_OLD\s+)(is\b)",r"\1accessible by(package ARTICULS) \2",oldspec,count=1,flags=re.I)
oldbody=re.sub(r"\bARTICULS\b","ARTICULS_SP_OLD",body,flags=re.I)
matches=list(re.finditer(r"(?im)^\s*function\s+(\w+)\s*\(",body))
methods={m.group(1).upper():body[m.start():matches[i+1].start() if i+1<len(matches) else body.lower().rfind("end articuls;")] for i,m in enumerate(matches)}
method=methods["EVENT_ON_CHANGE_PICKING_CELL"]
head=re.match(r"\s*function\s+\w+\s*\((.*?)\)\s*return\s+int\s*is",method,re.I|re.S)
assert head
replacement="function event_on_change_picking_cell("+head.group(1)+""") return int is
begin
 if articul1 is null or new_cell is null or current_cell is null or iser_id1 is null then
  raise_application_error(-20886,'ARTICLE_MOVE_FACTS_REQUIRED');
 end if;
 raise_application_error(-20886,'ARTICLE_CELL_CHANGE_REQUIRES_PHYSICAL_MOVE_TASK: use existing warehouse tasks');
end;
"""
body=body.replace(method,replacement,1)
method=methods["UPDATE_MOD"];head=re.match(r"\s*function\s+\w+\s*\((.*?)\)\s*return\s+int\s*is",method,re.I|re.S)
assert head
args=head.group(1).strip()
spec,n=re.subn(r"(function\s+UPDATE_MOD\s*\()(.*?)(\)\s*return\s+int\s*;)",lambda m:m.group(1)+m.group(2)+",p_actor varchar2 default null"+m.group(3),spec,count=1,flags=re.I|re.S)
assert n==1
calls=",".join(part.strip().split()[0] for part in args.split(","))
replacement="function UPDATE_MOD("+args+",p_actor varchar2 default null) return int is"+"""
 v_state varchar2(20);v_id number;v_article varchar2(160);v_brutto number;v_n number;
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' and p_actor is null then return ARTICULS_SP_OLD.UPDATE_MOD("""+calls+""");end if;
 if ARTICUL1 is null or NAME1 is null or SHT_IN_KOR1 is null or SHT_IN_KOR1<1
  or SHT_IN_KOR1!=trunc(SHT_IN_KOR1) or SHT_IN_KOR1>1000000000
  or nvl(SHT_WEIGHT1,0)<0 or nvl(KARTON_WEIGHT1,0)<0 or nvl(BRT_KOR,0)<0
  or nvl(X,0)<0 or nvl(Y,0)<0 or nvl(Z,0)<0 or DELETED1 is null or DELETED1 not in(0,1) then
  raise_application_error(-20887,'ARTICLE_PACK_FACTS_INVALID');
 end if;
 RRL_STOCK_CONFIG_API.begin_change(p_actor,'warehouse_settings_edit');
 select count(*) into v_n from RRL_ARTICULS where ACTICUL=ARTICUL1;
 if v_n!=1 then raise_application_error(-20887,'ARTICLE_NOT_FOUND');end if;
 if nvl(ID1,0)>0 then
  select ARTICUL into v_article from RRL_ARTICUL_MODS where ID=ID1 for update;
  if v_article!=ARTICUL1 then raise_application_error(-20887,'ARTICLE_MOD_IDENTITY_CONFLICT');end if;
  -- Existing pallets keep their immutable packaging factor and dimensions.
  update RRL_ARTICUL_MODS set DELETED=1 where ID=ID1;
 end if;
 v_brutto:=case when nvl(BRT_KOR,0)>0 then BRT_KOR else nvl(KARTON_WEIGHT1,0)+nvl(SHT_WEIGHT1,0)*SHT_IN_KOR1 end;
 select MODS_SEQ.nextval into v_id from dual;
 insert into RRL_ARTICUL_MODS(ID,ARTICUL,NAME,SHT_IN_KOR,SHT_WEIGHT,KARTON_WEIGHT,DELETED,SHK_SHT,SHK_KOR,DIMK_X,DIMK_Y,DIMK_Z,BRT_WEIGHT_OF_KOR)
 values(v_id,ARTICUL1,NAME1,SHT_IN_KOR1,SHT_WEIGHT1,KARTON_WEIGHT1,DELETED1,SHK_SHT1,SHK_KOR1,X,Y,Z,v_brutto);
 RRL_STOCK_CONFIG_API.end_change;
 return v_id;
exception when others then RRL_STOCK_CONFIG_API.end_change;raise;
end;
"""
body=body.replace(method,replacement,1)
base="db/migrations/2026-10-08_stock_posting_core/"
print(json.dumps({base+"174_article_legacy.sql":"create or replace "+oldspec+"\n/\ncreate or replace "+oldbody+"\n/\n",
 base+"174_article_adapter.sql":"create or replace "+spec+"\n/\ncreate or replace "+body+"\n/\n"},ensure_ascii=True))
